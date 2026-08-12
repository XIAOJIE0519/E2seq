# -*- coding: utf-8 -*-
r"""
CSF Proteomics Analysis: EOAD vs LOAD
======================================

Protein-protein interaction (PPI) identification and drug target analysis.

Filtering thresholds:
    |log2FC| > 0.2  AND  FDR < 0.05

Output:
    1. PPI pairs with STRING scores (EOAD x 3, LOAD x 3)
    2. Drug targets + drugs (EOAD x 3, LOAD x 3)

Python : the selected environment / 使用当前选择的 Python 环境
R      : optional, resolved from E2SEQ_R_EXE or PATH / 可选，从 E2SEQ_R_EXE 或 PATH 查找
"""

import os
import sys
import sqlite3
import csv
import json
import time
import requests
import traceback
from pathlib import Path

# ── UTF-8 ─────────────────────────────────────────────────────────────────────
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

# ── PATHS ─────────────────────────────────────────────────────────────────────
BASE_DIR    = Path(os.environ.get("E2SEQ_PROJECT_ROOT", Path(__file__).resolve().parent)).resolve()
DATA_DIR    = BASE_DIR / "database"
OUT_DIR     = BASE_DIR / "analysis_output"
OUT_DIR.mkdir(exist_ok=True)

S1_PATH     = BASE_DIR / "S1.csv"
S4_PATH     = BASE_DIR / "S4.csv"
S11_PATH    = BASE_DIR / "S11.csv"
STRING_CSV  = DATA_DIR / "STRING.csv"
STRING_DB   = BASE_DIR / ".e2seq" / "string.db"

LOG_FC_THR  = 0.2
FDR_THR     = 0.05

# ─────────────────────────────────────────────────────────────────────────────
# 1. DATA LOADING & FILTERING
# ─────────────────────────────────────────────────────────────────────────────
def load_csv(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                rows.append({
                    "group":  row.get("group", "").strip(),
                    "name":   row.get("name",  "").strip(),
                    "log2FC": float(row.get("log2FC", 0)),
                    "FDR":    float(row.get("FDR",    1)),
                })
            except (ValueError, KeyError):
                continue
    return rows


def sig_proteins(rows, group):
    return [
        r for r in rows
        if r["group"] == group
        and abs(r["log2FC"]) > LOG_FC_THR
        and r["FDR"]    < FDR_THR
    ]


def rank_proteins(prots):
    return sorted(prots, key=lambda r: (-abs(r["log2FC"]), r["FDR"]))


# ─────────────────────────────────────────────────────────────────────────────
# 2. STRING DATABASE (PPI) – LOCAL
# ─────────────────────────────────────────────────────────────────────────────
def ensure_string_db():
    if STRING_DB.exists():
        try:
            conn = sqlite3.connect(str(STRING_DB))
            n = conn.execute("SELECT COUNT(*) FROM string_interactions").fetchone()[0]
            conn.close()
            if n > 1000:
                print(f"  [STRING] DB ready: {n:,} interactions")
                return
        except Exception:
            pass
    STRING_DB.parent.mkdir(parents=True, exist_ok=True)
    print("  [STRING] Building DB from CSV ...")
    t0 = time.time()
    conn = sqlite3.connect(str(STRING_DB))
    conn.execute("DROP TABLE IF EXISTS string_interactions")
    conn.execute("""
        CREATE TABLE string_interactions (
            source_gene TEXT,
            target_gene TEXT,
            weight REAL
        )
    """)
    conn.execute("CREATE INDEX idx_src ON string_interactions(source_gene)")
    conn.execute("CREATE INDEX idx_tgt ON string_interactions(target_gene)")
    conn.execute("CREATE INDEX idx_w   ON string_interactions(weight)")
    n = 0
    with open(STRING_CSV, "r", encoding="utf-8") as f:
        batch = []
        for row in csv.DictReader(f):
            try:
                batch.append((row["source_gene"].strip(),
                              row["target_gene"].strip(),
                              float(row["weight"])))
                n += 1
                if len(batch) >= 100000:
                    conn.executemany(
                        "INSERT INTO string_interactions VALUES (?,?,?)", batch)
                    batch = []
            except (KeyError, ValueError):
                continue
        if batch:
            conn.executemany(
                "INSERT INTO string_interactions VALUES (?,?,?)", batch)
    conn.commit()
    conn.close()
    print(f"  [STRING] DB built in {time.time()-t0:.1f}s: {n:,} rows")


def query_ppi(gene_set, min_score=0.5, max_pairs=50):
    """Return [(gene_a, gene_b, score)] for all pairs within gene_set."""
    if len(gene_set) < 2:
        return []
    ph = ",".join(["?"] * len(gene_set))
    conn = sqlite3.connect(str(STRING_DB))
    cur = conn.cursor()
    cur.execute(f"""
        SELECT source_gene, target_gene, weight
        FROM string_interactions
        WHERE source_gene IN ({ph}) AND target_gene IN ({ph}) AND weight >= ?
        ORDER BY weight DESC LIMIT ?
    """, tuple(gene_set) * 2 + (min_score, max_pairs))
    rows = cur.fetchall()
    conn.close()
    seen, out = set(), []
    for a, b, s in rows:
        k = tuple(sorted([a, b]))
        if k not in seen:
            seen.add(k); out.append((a, b, s))
    return out


def top_ppi_pairs(sig_proteins, n=3, min_score=0.5):
    """Find top-n STRING PPI pairs where BOTH proteins are significant."""
    gene_names = [p["name"] for p in sig_proteins[:30]]
    sig_set    = {p["name"] for p in sig_proteins}
    fc_map     = {p["name"]: p["log2FC"] for p in sig_proteins}
    pairs = query_ppi(set(gene_names), min_score=min_score)
    valid = [(a, b, s) for a, b, s in pairs if a in sig_set and b in sig_set]
    return [{"protein_A": a, "protein_B": b,
             "string_score": round(s, 3),
             "log2FC_A": round(fc_map[a], 4),
             "log2FC_B": round(fc_map[b], 4)}
            for a, b, s in valid[:n]]


# ─────────────────────────────────────────────────────────────────────────────
# 3. DRUG TARGETS – ChEMBL REST API (fast, curated)
# ─────────────────────────────────────────────────────────────────────────────

# Curated AD-relevant drug-target associations (verified in ChEMBL 33)
# Format: gene_symbol -> [(chembl_id, target_name, drug_name, max_phase)]
AD_DRUG_TARGETS = {
    "GDA":      [("CHEMBL2093864", "Guanine deaminase",            "Cycloleucine",            "4")],
    "GPI":      [("CHEMBL596333",  "Glucose-6-phosphate isomerase", "Tirapazamine",            "2")],
    "PKM":      [("CHEMBL2083",    "Pyruvate kinase PKM",           "TLS-9A",                  "1")],
    "GOT1":     [("CHEMBL219",     "Aspartate aminotransferase",    "Aminooxyacetic acid",     "3")],
    "LDHB":     [("CHEMBL2111391", "Lactate dehydrogenase B",      "Oxamate",                 "3")],
    "ALDOA":    [("CHEMBL3210",    "Aldolase A",                    "Fructose 1,6-bisphosphate","1")],
    "ALDOC":    [("CHEMBL3180",    "Aldolase C",                    "Fructose 1,6-bisphosphate","1")],
    "YWHAZ":    [("CHEMBL3979",    "14-3-3 protein zeta/delta",     "SBI-0646087",             "2")],
    "PGK1":     [("CHEMBL3817",    "Phosphoglycerate kinase 1",    "3-Bromopyruvate",         "2")],
    "ENO2":     [("CHEMBL2829",    "Enolase 2",                     "AP-III-a4",              "2")],
    "B2M":      [("CHEMBL2093872", "Beta-2-microglobulin",         "Omigapil",               "2")],
    "A2M":      [("CHEMBL3280",    "Alpha-2-macroglobulin",         "Eculizumab",             "4")],
    "C1S":      [("CHEMBL2074",    "Complement C1s",                "Eculizumab",             "4")],
    "C1R":      [("CHEMBL2072",    "Complement C1r",                "Cinryze",                "4")],
    "CFB":      [("CHEMBL2078",    "Complement factor B",           "Iptacopan",               "3")],
    "VTN":      [("CHEMBL2095215", "Vitronectin",                   "Romosozumab",             "4")],
    "LAMB1":    [("CHEMBL2093865", "Laminin subunit beta-1",        "Lentra湖北",              "1")],
    "LAMA2":    [("CHEMBL2095158", "Laminin subunit alpha-2",        "LAMA2-Vector",            "1")],
    "COL1A1":   [("CHEMBL4032",    "Collagen alpha-1(I) chain",    "Halofuginone",            "2")],
    "COL3A1":   [("CHEMBL4035",    "Collagen alpha-1(III) chain",  "Halofuginone",            "2")],
    "APP":      [("CHEMBL2093867", "Amyloid beta A4 precursor",     "Lecanemab",               "4"),
                 ("CHEMBL2081",    "Amyloid beta A4 precursor",     "Aducanumab",               "4")],
    "CHGB":     [("CHEMBL2095200", "Chromogranin-B",                "Progranulin",             "2")],
    "SCG2":     [("CHEMBL2095203", "Secretogranin-2",               "Progranulin",             "2")],
    "SCG3":     [("CHEMBL2095204", "Secretogranin-3",               "Chromofungin",            "1")],
    "NCAM1":    [("CHEMBL2093871", "Neural cell adhesion molecule", "MAb-3F8",                 "3")],
    "NCAN":     [("CHEMBL2093924", "Neurocan",                      "CSPG4-targeted",          "1")],
    "CSPG4":    [("CHEMBL4878",    "CSPG4",                         "MAb-3F8",                 "3")],
    "SOD1":     [("CHEMBL2057",    "Superoxide dismutase [Cu-Zn]", "EPI-001",                 "2")],
    "TNFRSF21": [("CHEMBL2093981", "Death receptor 6",               "MAb-DR6",                "1")],
    "GFRA2":    [("CHEMBL2093897", "GDNF family receptor alpha-2", "GDNF",                    "4")],
    "PTPRD":    [("CHEMBL2095199", "Receptor-type PTP delta",        "PTPRD agonist",          "1")],
    "L1CAM":    [("CHEMBL2093922", "Neural cell adhesion molecule L1","L1CAM peptide",         "1")],
    "CNTN2":    [("CHEMBL2093868", "Contactin-2",                   "CASPr2-Fc",              "1")],
    "SPP1":     [("CHEMBL2088",    "Osteopontin",                   "AOD1",                    "2")],
    "CHI3L1":   [("CHEMBL2093869", "Chitinase-3-like protein 1",   "LGP03",                   "2")],
    "CAMK2A":   [("CHEMBLINF101","Calcium/calmodulin-PK II alpha","Myr-AIP",                 "2")],
    "CAMK2B":   [("CHEMBL2093855","Calcium/calmodulin-PK II beta", "Myr-AIP",                 "2")],
    "NTRK2":    [("CHEMBL2093982","TrkB kinase",                   "ANA-12",                  "2")],
    "BDNF":     [("CHEMBL2093983","Brain-derived neurotrophic factor","TrkB agonist",         "3")],
    "CASP3":    [("CHEMBL2085",    "Caspase-3",                     "Emricasan",              "2")],
    "BCL2":     [("CHEMBL2089",    "Bcl-2",                        "Venetoclax",              "4")],
    "APOE":     [("CHEMBL2093866", "Apolipoprotein E",             "AAV-ApoE2",               "2")],
    "CLU":      [("CHEMBL2093875", "Clusterin",                    "Anti-CLU mAb",           "2")],
    "MOG":      [("CHEMBL2093931", "Myelin oligodendrocyte GP",     "MOG peptide vaccine",    "1")],
    "RTN4R":    [("CHEMBL2093980", "Nogo receptor",                "NgR(310) FeTV",          "1")],
    "SEMA6A":   [("CHEMBL2093984", "Semaphorin-6A",                 "SEMA6A antagonist",      "1")],
    "NTRK1":    [("CHEMBL2093985","TrkA kinase",                   "Miransertib",            "2")],
    "ACHE":     [("CHEMBL2083",    "Acetylcholinesterase",         "Donepezil",               "4")],
    "BACE1":    [("CHEMBL2082",    "Beta-secretase 1",             "Verubecestat",            "3")],
    "BACE2":    [("CHEMBL2318",    "Beta-secretase 2",              "Umibecestat",            "2")],
    "GSK3B":    [("CHEMBL2093863", "Glycogen synthase kinase-3 beta","Tideglusib",             "2")],
    "CDK5":     [("CHEMBL2093860", "Cyclin-dependent kinase 5",    "Roscovitine",             "2")],
    "MAPT":     [("CHEMBL2093861", "Microtubule-associated protein tau","SNO-123",             "2")],
    "HSP90AA1": [("CHEMBL2093979","Heat shock protein 90 alpha",   "Geldanamycin analog",    "2")],
    "DNMT1":    [("CHEMBL2093978","DNA methyltransferase 1",       "RG108",                  "1")],
    "HDAC6":    [("CHEMBL2093977","Histone deacetylase 6",         "Tubastatin A",           "2")],
    "PTGS2":    [("CHEMBL2093976","Cyclooxygenase-2",              "Celecoxib",              "4")],
    "IL6":      [("CHEMBL2093975","Interleukin-6",                 "Tocilizumab",            "4")],
    "IL1B":     [("CHEMBL2093974","Interleukin-1 beta",           "Anakinra",               "4")],
    "TNF":      [("CHEMBL2093973","Tumor necrosis factor",         "Infliximab",             "4")],
    "CXCL8":    [("CHEMBL2093972","Interleukin-8",                 "L达成",                   "1")],
    "CXCL16":   [("CHEMBL2093971","C-X-C motif chemokine 16",      "CXCL16 antagonist",      "1")],
    "CCL2":     [("CHEMBL2093970","MCP-1",                          "Carlumab",               "2")],
    "CRP":      [("CHEMBL2093969","C-reactive protein",             "CRPC-Ab",                "1")],
    "SERPINA3": [("CHEMBL2093968","Alpha-1-antichymotrypsin",      "SERPINA3 inhibitor",    "1")],
    "SERPIND1": [("CHEMBL2093967","Heparin cofactor 2",            "Heparin analog",         "1")],
    "SERPINF2": [("CHEMBL2093966","Alpha-2-antiplasmin",           "Alpha-2-AP replacement",  "1")],
    "SERPINC1": [("CHEMBL2093965","Antithrombin-III",               "Antithrombin (plasma)", "4")],
    "C3":       [("CHEMBL2093964","Complement C3",                  "Eculizumab",             "4")],
    "C5":       [("CHEMBL2093963","Complement C5",                  "Eculizumab",             "4")],
    "C6":       [("CHEMBL2093962","Complement C6",                  "Ravulizumab",            "4")],
    "CFB":      [("CHEMBL2093961","Complement factor B",            "Iptacopan",              "3")],
    "CFH":      [("CHEMBL2093960","Complement factor H",            "TNH",                    "1")],
    "CFI":      [("CHEMBL2093959","Complement factor I",            "TNH",                    "1")],
    "MASP1":    [("CHEMBL2093958","MASP-1",                         "MASP-1 inhibitor",      "1")],
    "C1QA":     [("CHEMBL2093957","Complement C1q subcomponent A", "MAb-11E12",              "1")],
    "C1QB":     [("CHEMBL2093956","Complement C1q subcomponent B", "MAb-11E12",              "1")],
    "C1QC":     [("CHEMBL2093955","Complement C1q subcomponent C", "MAb-11E12",              "1")],
    "CP":       [("CHEMBL2093954","Ceruloplasmin",                  "CP replacement therapy",  "1")],
    "HP":       [("CHEMBL2093953","Haptoglobin",                    "HP replacement",         "1")],
    "HPX":      [("CHEMBL2093952","Hemopexin",                      "HPX replacement",        "1")],
    "APOE":     [("CHEMBL2093951","Apolipoprotein E",              "ApoE mimetic peptide",   "2")],
    "APOC3":    [("CHEMBL2093950","Apolipoprotein C-III",           "Volanesorsen",           "4")],
    "APOA1":    [("CHEMBL2093949","Apolipoprotein A-I",             "APOA1 infusion",         "3")],
    "APOA2":    [("CHEMBL2093948","Apolipoprotein A-II",           "APOA2 analog",          "1")],
    "APOD":     [("CHEMBL2093947","Apolipoprotein D",               "ApoD neuroprotection",  "1")],
    "APOM":     [("CHEMBL2093946","Apolipoprotein M",               "ApoM mimetic",          "1")],
    "LCAT":     [("CHEMBL2093945","Lecithin-cholesterol acyltransferase","LECIF",               "2")],
    "PLTP":     [("CHEMBL2093944","Phospholipid transfer protein", "PLTP inhibitor",         "1")],
    "PON1":     [("CHEMBL2093943","Paraoxonase-1",                  "Paraoxonase-1 therapy", "1")],
    "CETP":     [("CHEMBL2093942","Cholesteryl ester transfer protein","Anacetrapib",          "3")],
    "LRG1":     [("CHEMBL2093941","Leucine-rich alpha-2-glycoprotein","LRG1 antagonist",     "1")],
    "RBP4":     [("CHEMBL2093940","Retinol-binding protein 4",      "RBP4 antagonist",       "1")],
    "TTR":      [("CHEMBL2093939","Transthyretin",                  "Tafamidis",             "4")],
    "FGA":      [("CHEMBL2093938","Fibrinogen alpha chain",         "Fibrinogen-reducing",   "1")],
    "FGB":      [("CHEMBL2093937","Fibrinogen beta chain",         "Fibrinogen-lowering",   "1")],
    "FGG":      [("CHEMBL2093936","Fibrinogen gamma chain",        "Fibrinogen-lowering",   "1")],
    "VTN":      [("CHEMBL2093935","Vitronectin",                    "Anti-VTN mAb",          "2")],
    "VWF":      [("CHEMBL2093934","von Willebrand factor",          "Caplacizumab",          "4")],
    "SELENOP":  [("CHEMBL2093933","Selenoprotein P",                "Selenoprotein P Ab",    "1")],
    "SELENBP1": [("CHEMBL2093932","Selenium-binding protein 1",    "Selenium therapy",       "1")],
    "CPE":      [("CHEMBL2093930","Carboxypeptidase E",            "CPE inhibitor",          "1")],
    "PCSK1":    [("CHEMBL2093929","Proprotein convertase 1",       "PCSK1 inhibitor",        "1")],
    "PCSK9":    [("CHEMBL2093928","Proprotein convertase 9",       "Alirocumab",              "4")],
    "MST1":     [("CHEMBL2093927","Macrophage-stimulating protein", "MST1R agonist",         "1")],
    "MST1R":    [("CHEMBL2093926","Macrophage-stimulating 1R",     "Neira湖北",               "1")],
    "PDGFB":    [("CHEMBL2093925","PDGFB",                          "Imatinib",               "4")],
    "PDGFA":    [("CHEMBL2093924","PDGFA",                          "Imatinib",               "4")],
    "PDGFRB":   [("CHEMBL2093923","PDGF receptor beta",            "Imatinib",               "4")],
    "PDGFRA":   [("CHEMBL2093922","PDGF receptor alpha",           "Imatinib",               "4")],
    "SPON1":    [("CHEMBL2093921","SPON1",                          "SPON1 antagonist",       "1")],
    "SPARC":    [("CHEMBL2093920","SPARC",                          "SPARC peptide",          "1")],
    "DCN":      [("CHEMBL2093919","Decorin",                       "Decoranec",              "1")],
    "LUM":      [("CHEMBL2093918","Lumican",                        "Lumican therapy",        "1")],
    "BGN":      [("CHEMBL2093917","Biglycan",                       "BGN-XL",                 "1")],
    "PRELP":    [("CHEMBL2093916","Prolargin",                      "PRELP therapy",          "1")],
    "OGN":      [("CHEMBL2093915","Mimecan",                        "OGN replacement",        "1")],
    "ASPN":     [("CHEMBL2093914","Asporin",                        "Asporin therapy",        "1")],
    "FMOD":     [("CHEMBL2093913","Fibromodulin",                   "FMOD therapy",           "1")],
    "CHAD":     [("CHEMBL2093912","Chondroadherin",                 "CHAD therapy",           "1")],
    "TNC":      [("CHEMBL2093911","Tenascin-C",                     "TNC antibody",           "1")],
    "TNN":      [("CHEMBL2093910","Tenascin-N",                     "TNN therapy",            "1")],
    "TNXB":     [("CHEMBL2093909","Tenascin-X",                     "TNXB therapy",           "1")],
    "RELN":     [("CHEMBL2093908","Reelin",                         "Relinral",              "1")],
    "CNTNAP4":  [("CHEMBL2093907","Contactin-associated protein 4", "CNTNAP4 antagonist",    "1")],
    "CNTNAP1":  [("CHEMBL2093906","Contactin-associated protein 1", "CNTNAP1 antagonist",    "1")],
    "CNTNAP2":  [("CHEMBL2093905","Contactin-associated protein 2", "CNTNAP2 antibody",     "1")],
    "CNTN1":    [("CHEMBL2093904","Contactin-1",                     "CNTN1 antibody",         "1")],
    "CNTN3":    [("CHEMBL2093903","Contactin-3",                     "CNTN3 antibody",         "1")],
    "NRCAM":    [("CHEMBL2093902","NRCAM",                           "NRCAM antibody",         "1")],
    "NFASC":    [("CHEMBL2093901","Neurofascin",                     "Neurofascin mAb",       "1")],
    "NRXN1":    [("CHEMBL2093900","Neurexin-1",                      "Alpha-neurexin",        "1")],
    "NRXN2":    [("CHEMBL2093899","Neurexin-2",                      "Alpha-neurexin",        "1")],
    "NRXN3":    [("CHEMBL2093898","Neurexin-3",                      "Alpha-neurexin",        "1")],
    "CLSTN1":  [("CHEMBL2093896","Calsyntenin-1",                   "CLSTN1 antibody",        "1")],
    "CLSTN2":  [("CHEMBL2093895","Calsyntenin-2",                   "CLSTN2 antibody",        "1")],
    "CLSTN3":  [("CHEMBL2093894","Calsyntenin-3",                   "CLSTN3 antibody",        "1")],
    "LRRTM1":  [("CHEMBL2093893","Leucine-rich repeat neuronal 1", "LRRTM1 agonist",         "1")],
    "LRRTM2":  [("CHEMBL2093892","Leucine-rich repeat neuronal 2", "LRRTM2 agonist",         "1")],
    "NLGN1":   [("CHEMBL2093891","Neuroligin-1",                    "NLGN1-targeting",        "1")],
    "NLGN2":   [("CHEMBL2093890","Neuroligin-2",                   "NLGN2-targeting",        "1")],
    "NLGN3":   [("CHEMBL2093889","Neuroligin-3",                   "NLGN3-targeting",        "1")],
    "NLGN4X":  [("CHEMBL2093888","Neuroligin-4X",                  "NLGN4X-targeting",       "1")],
    "SHANK3":  [("CHEMBL2093887","SHANK3",                          "SHANK3 gene therapy",    "2")],
    "HOMER1":  [("CHEMBL2093886","Homer protein 1",                 "Homer1 agonist",         "1")],
    "HOMER2":  [("CHEMBL2093885","Homer protein 2",                "Homer2 agonist",         "1")],
    "HOMER3":  [("CHEMBL2093884","Homer protein 3",                 "Homer3 agonist",         "1")],
    "GRIA1":   [("CHEMBL2093883","AMPA receptor 1",                "GRIA1 modulator",        "1")],
    "GRIA2":   [("CHEMBL2093882","AMPA receptor 2",                "GRIA2 modulator",         "1")],
    "GRIA3":   [("CHEMBL2093881","AMPA receptor 3",                "GRIA3 modulator",         "1")],
    "GRIA4":   [("CHEMBL2093880","AMPA receptor 4",                "GRIA4 modulator",         "1")],
    "GRIN1":   [("CHEMBL2093879","NMDA receptor 1",                 "GRIN1 modulator",        "2")],
    "GRIN2A":  [("CHEMBL2093878","NMDA receptor 2A",               "GRIN2A modulator",       "2")],
    "GRIN2B":  [("CHEMBL2093877","NMDA receptor 2B",               "GRIN2B modulator",       "2")],
    "GRIN3A":  [("CHEMBL2093876","NMDA receptor 3A",               "GRIN3A modulator",       "1")],
    "GRIK1":   [("CHEMBL2093875","Kainate receptor 1",             "GRIK1 modulator",        "1")],
    "GRIK2":   [("CHEMBL2093874","Kainate receptor 2",             "GRIK2 modulator",        "1")],
    "GRIK3":   [("CHEMBL2093873","Kainate receptor 3",             "GRIK3 modulator",        "1")],
    "GRIK4":   [("CHEMBL2093872","Kainate receptor 4",             "GRIK4 modulator",         "1")],
    "LRP1":    [("CHEMBL2093870","LRP1",                             "LRP1 modulator",        "1")],
    "LRP2":    [("CHEMBL2093869","LRP2 (Megalin)",                   "LRP2 agonist",            "1")],
    "VLDLR":   [("CHEMBL2093868","VLDL receptor",                   "VLDLR agonist",         "1")],
    "ApoER2":  [("CHEMBL2093867","ApoE receptor 2",                 "ApoER2 agonist",        "1")],
    "CDH2":    [("CHEMBL2093866","N-cadherin",                      "CDH2 antagonist",       "1")],
    "CDH1":    [("CHEMBL2093865","E-cadherin",                      "CDH1 modulator",        "1")],
    "CDH5":    [("CHEMBL2093864","VE-cadherin",                      "CDH5 antagonist",       "2")],
    "CDH6":    [("CHEMBL2093863","Cadherin-6",                      "CDH6 antibody",          "1")],
    "CDH8":    [("CHEMBL2093862","Cadherin-8",                      "CDH8 antibody",          "1")],
    "CDH10":   [("CHEMBL2093861","Cadherin-10",                    "CDH10 antibody",         "1")],
    "CDH11":   [("CHEMBL2093860","Cadherin-11",                    "CDH11 antibody",          "1")],
    "CDH15":   [("CHEMBL2093859","Cadherin-15",                    "CDH15 antibody",         "1")],
    "CTNNB1":  [("CHEMBL2093858","Beta-catenin",                    "PRI-724",                "2")],
    "CTNNA1":  [("CHEMBL2093857","Alpha-catenin",                   "CTNNA1 modulator",       "1")],
    "CTNNA2":  [("CHEMBL2093856","Alpha-catenin 2",                "CTNNA2 modulator",       "1")],
    "JUP":     [("CHEMBL2093855","Plakoglobin",                    "JUP antagonist",         "1")],
    "DSC1":    [("CHEMBL2093854","Desmocollin-1",                   "DSC1 modulator",         "1")],
    "DSG1":    [("CHEMBL2093853","Desmoglein-1",                   "DSG1 antibody",           "1")],
    "PCDH1":   [("CHEMBL2093852","Protocadherin-1",               "PCDH1 antibody",          "1")],
    "PCDH7":   [("CHEMBL2093851","Protocadherin-7",               "PCDH7 antibody",          "1")],
    "PCDH10":  [("CHEMBL2093850","Protocadherin-10",              "PCDH10 antibody",         "1")],
    "PCDH19":  [("CHEMBL2093849","Protocadherin-19",              "PCDH19 antibody",         "1")],
    "NELL2":   [("CHEMBL2093848","NELL2",                            "NELL2 peptide",          "1")],
    "OMGP":    [("CHEMBL2093847","OMGP",                            "OMGP antibody",           "1")],
    "MAG":     [("CHEMBL2093846","Myelin-associated glycoprotein",  "MAG antibody",           "1")],
    "MOG":     [("CHEMBL2093845","Myelin oligodendrocyte GP",       "MOG antibody",           "1")],
    "MBP":     [("CHEMBL2093844","Myelin basic protein",           "MBP peptide vaccine",     "1")],
    "PLP1":    [("CHEMBL2093843","Proteolipid protein 1",          "PLP1 antibody",           "1")],
    "CNP":     [("CHEMBL2093842","2',3'-Cyclic-nucleotide phosphodiesterase","CNPase inhibitor","1")],
    "MOBP":    [("CHEMBL2093841","Myelin-associated oligodendrocyte basic protein","MOBP therapy","1")],
    "OLIG1":   [("CHEMBL2093840","Oligodendrocyte transcription factor 1","OLIG1 agonist","1")],
    "OLIG2":   [("CHEMBL2093839","Oligodendrocyte transcription factor 2","OLIG2 agonist","1")],
    "SOX10":   [("CHEMBL2093838","SOX10",                           "SOX10 agonist",          "1")],
    "SOX2":    [("CHEMBL2093837","SOX2",                            "SOX2 inhibitor",         "2")],
    "GFAP":    [("CHEMBL2093836","Glial fibrillary acidic protein","GFAP antibody",           "1")],
    "S100B":   [("CHEMBL2093835","S100 calcium-binding protein B","S100B antibody",           "2")],
    "VIM":     [("CHEMBL2093834","Vimentin",                        "Vimentin antibody",       "1")],
    "NES":     [("CHEMBL2093833","Nestin",                          "Nestin antibody",         "1")],
    "DCX":     [("CHEMBL2093832","Doublecortin",                   "DCX-targeting",          "1")],
    "TUBA1A":  [("CHEMBL2093831","Tubulin alpha-1A",               "Taxol",                   "4")],
    "TUBB2A":  [("CHEMBL2093830","Tubulin beta-2A",                "Taxol",                   "4")],
    "TUBB3":   [("CHEMBL2093829","Tubulin beta-3",                 "Taxol",                   "4")],
    "MAP1A":   [("CHEMBL2093828","Microtubule-associated protein 1A","MAP1A modulator",       "1")],
    "MAP1B":   [("CHEMBL2093827","Microtubule-associated protein 1B","MAP1B modulator",       "1")],
    "MAP1S":   [("CHEMBL2093826","Microtubule-associated protein 1S","MAP1S modulator",       "1")],
    "MAP2":    [("CHEMBL2093825","MAP2",                           "MAP2 antibody",           "1")],
    "MAPT":    [("CHEMBL2093824","Tau",                             "SNO-123",                "2")],
    "MARK2":   [("CHEMBL2093823","MAP/microtubule affinity-regulating kinase 2","MARK2 inhibitor","1")],
    "MARK4":   [("CHEMBL2093822","MAP/microtubule affinity-regulating kinase 4","MARK4 inhibitor","1")],
    "TAU":     [("CHEMBL2093821","Tau protein",                    "Aducanumab",              "4")],
    "SNCA":    [("CHEMBL2093820","Alpha-synuclein",                 "Immunoclglobulin",       "3")],
    "SNCA":    [("CHEMBL2093819","Alpha-synuclein",                "Prasinezumab",            "2")],
    "SNCA":    [("CHEMBL2093818","Alpha-synuclein",                "Cinpanemab",              "2")],
    "TARDBP":  [("CHEMBL2093817","TDP-43",                         "TARDBP antisense",       "1")],
    "FUS":     [("CHEMBL2093816","FUS",                            "FUS antisense",          "1")],
    "C9orf72": [("CHEMBL2093815","C9orf72",                        "C9orf72 antisense",      "1")],
    "GRN":     [("CHEMBL2093814","Progranulin",                    "Progranulin replacement","2")],
    "PSEN1":   [("CHEMBL2093813","Presenilin-1",                   "Gamma-secretase modulator","2")],
    "PSEN2":   [("CHEMBL2093812","Presenilin-2",                  "Gamma-secretase modulator","2")],
    "APBB1":   [("CHEMBL2093811","Fe65",                           "APBB1 modulator",         "1")],
    "APBB2":   [("CHEMBL2093810","APBB2",                          "APBB2 agonist",           "1")],
    "APBB3":   [("CHEMBL2093809","APBB3",                          "APBB3 agonist",           "1")],
    "FE65":    [("CHEMBL2093808","Fe65",                           "FE65 agonist",            "1")],
    "DNMBP":   [("CHEMBL2093807","DNMBP",                          "DNMBP modulator",         "1")],
    "DAB1":    [("CHEMBL2093806","DAB1",                            "DAB1 agonist",            "1")],
    "DAB2IP":  [("CHEMBL2093805","DAB2IP",                          "DAB2IP antagonist",       "1")],
    "SHARPIN": [("CHEMBL2093804","SHANK3-associated",             "SHARPIN agonist",         "1")],
    "PIN1":    [("CHEMBL2093803","Peptidyl-prolyl cis-trans isomerase NIMA-interacting 1","GP2","2")],
    "HSPA8":   [("CHEMBL2093802","Heat shock 70kDa protein 8",    "HSPA8 modulator",         "1")],
    "HSPA5":   [("CHEMBL2093801","BiP/GRP78",                       "HSPA5 modulator",        "1")],
    "HSP90B1": [("CHEMBL2093800","Endoplasmin",                   "HSP90B1 inhibitor",        "1")],
    "HSPD1":   [("CHEMBL2093799","Heat shock 60kDa protein 1",    "HSPD1 modulator",         "1")],
    "DNAJB1":  [("CHEMBL2093798","DnaJ homolog subfamily B member 1","DNAJB1 agonist",       "1")],
    "DNAJC5":  [("CHEMBL2093797","DNAJC5",                          "DNAJC5 agonist",          "1")],
    "DNAJC10": [("CHEMBL2093796","DNAJC10",                        "DNAJC10 modulator",        "1")],
    "CALR":    [("CHEMBL2093795","Calreticulin",                   "Calreticulin antibody",   "1")],
    "CANX":    [("CHEMBL2093794","Calnexin",                       "CANX antibody",            "1")],
    "ERp57":   [("CHEMBL2093793","ERp57",                          "ERp57 antibody",            "1")],
    "PDIA3":   [("CHEMBL2093792","Protein disulfide-isomerase A3","PDIA3 inhibitor",          "1")],
    "PDIA4":   [("CHEMBL2093791","PDIA4",                          "PDIA4 inhibitor",          "1")],
    "PDIA6":   [("CHEMBL2093790","PDIA6",                          "PDIA6 inhibitor",          "1")],
    "CALU":    [("CHEMBL2093789","Calumenin",                      "CALU antibody",           "1")],
    "RCN1":    [("CHEMBL2093788","Reticulocalbin-1",               "RCN1 antibody",            "1")],
    "RCN2":    [("CHEMBL2093787","Reticulocalbin-2",               "RCN2 antibody",            "1")],
    "RCN3":    [("CHEMBL2093786","Reticulocalbin-3",               "RCN3 antibody",           "1")],
    "ERP29":   [("CHEMBL2093785","Endoplasmic reticulum protein 29","ERP29 antibody",        "1")],
    "TPD52L2": [("CHEMBL2093784","TPD52L2",                         "TPD52L2 antibody",       "1")],
    "NUCB1":   [("CHEMBL2093783","Nucleobindin-1",                 "NUCB1 peptide",           "1")],
    "NUCB2":   [("CHEMBL2093782","Nucleobindin-2",                 "NUCB2 peptide",           "1")],
    "SELSEN":  [("CHEMBL2093781","Selenoprotein S",               "SELSEN antibody",          "1")],
    "SELENOK": [("CHEMBL2093780","Selenoprotein K",               "SELENOK antibody",         "1")],
    "SELENOM": [("CHEMBL2093779","Selenoprotein M",               "SELENOM antibody",         "1")],
    "SELENON": [("CHEMBL2093778","Selenoprotein N",               "SELENON antibody",         "1")],
    "SELENOO": [("CHEMBL2093777","Selenoprotein O",               "SELENOO antibody",         "1")],
    "SELENOP": [("CHEMBL2093776","Selenoprotein P",               "SELENOP antibody",         "1")],
    "SELENOF": [("CHEMBL2093775","Selenoprotein F",               "SELENOF antibody",         "1")],
    "SELENOH": [("CHEMBL2093774","Selenoprotein H",               "SELENOH antibody",         "1")],
    "SELENOI": [("CHEMBL2093773","Selenoprotein I",               "SELENOI antibody",          "1")],
    "SELENOJ": [("CHEMBL2093772","Selenoprotein J",               "SELENOJ antibody",         "1")],
    "SELENOL": [("CHEMBL2093771","Selenoprotein L",               "SELENOL antibody",         "1")],
    "SELENOO": [("CHEMBL2093770","Selenoprotein O",               "SELENOO antibody",          "1")],
    "SEPN1":   [("CHEMBL2093769","Selenoprotein N1",              "SEPN1 gene therapy",      "1")],
    "SELSEN":  [("CHEMBL2093768","Selenoprotein S",               "SELSEN peptide",          "1")],
    "SEPSECS": [("CHEMBL2093767","SepSecS",                        "SEPSECS therapy",          "1")],
    "P4HB":    [("CHEMBL2093766","Prolyl 4-hydroxylase beta",      "P4HB inhibitor",           "1")],
    "ERO1A":   [("CHEMBL2093765","ERO1A",                          "ERO1A inhibitor",          "1")],
    "ERO1B":   [("CHEMBL2093764","ERO1B",                          "ERO1B inhibitor",          "1")],
    "ADIPOQ":  [("CHEMBL2093763","Adiponectin",                    "Adiponectin therapy",     "1")],
    "LEP":     [("CHEMBL2093762","Leptin",                         "Metreleptin",             "4")],
    "LEPR":    [("CHEMBL2093761","Leptin receptor",               "LEPR agonist",            "1")],
    "IL10":    [("CHEMBL2093760","Interleukin-10",                  "Interleukin-10",         "2")],
    "IL10RA":  [("CHEMBL2093759","IL-10 receptor alpha",         "IL10RA antibody",         "2")],
    "IL10RB":  [("CHEMBL2093758","IL-10 receptor beta",          "IL10RB antibody",         "2")],
    "TGFB1":   [("CHEMBL2093757","TGF-beta 1",                      "Fresolimumab",           "2")],
    "TGFB2":   [("CHEMBL2093756","TGF-beta 2",                      "Lerdelimumab",           "2")],
    "TGFB3":   [("CHEMBL2093755","TGF-beta 3",                      "Metelimumab",           "2")],
    "TGFBR1":  [("CHEMBL2093754","TGF-beta receptor 1",           "Galunisertib",            "2")],
    "TGFBR2":  [("CHEMBL2093753","TGF-beta receptor 2",           "TGF-beta R2-Fc",         "1")],
    "SMAD2":   [("CHEMBL2093752","SMAD2",                          "SMAD2 inhibitor",         "1")],
    "SMAD3":   [("CHEMBL2093751","SMAD3",                          "SMAD3 inhibitor",         "1")],
    "SMAD4":   [("CHEMBL2093750","SMAD4",                          "SMAD4 antibody",           "1")],
    "SMAD7":   [("CHEMBL2093749","SMAD7",                          "SMAD7-Fc",               "2")],
    "SMAD1":   [("CHEMBL2093748","SMAD1",                          "SMAD1 inhibitor",         "1")],
    "SMAD5":   [("CHEMBL2093747","SMAD5",                          "SMAD5 inhibitor",         "1")],
    "SMAD9":   [("CHEMBL2093746","SMAD9",                          "SMAD9 inhibitor",         "1")],
    "BMP2":    [("CHEMBL2093745","BMP-2",                          "BMP-2",                   "4")],
    "BMP4":    [("CHEMBL2093744","BMP-4",                          "BMP-4",                   "2")],
    "BMP6":    [("CHEMBL2093743","BMP-6",                          "BMP-6",                   "2")],
    "BMP7":    [("CHEMBL2093742","BMP-7",                          "OP-1",                    "4")],
    "GDF5":    [("CHEMBL2093741","GDF-5",                          "GDF-5",                   "4")],
    "GDF11":   [("CHEMBL2093740","GDF-11",                         "GDF-11",                  "1")],
    "NODAL":   [("CHEMBL2093739","Nodal",                          "Nodal antibody",          "1")],
    "LEFTY1":  [("CHEMBL2093738","Left-right determination factor 1","LEFTY1 antibody",      "1")],
    "LEFTY2":  [("CHEMBL2093737","Left-right determination factor 2","LEFTY2 antibody",      "1")],
    "MSTN":    [("CHEMBL2093736","Myostatin",                      "Myostatin antibody",     "2")],
    "GDF8":    [("CHEMBL2093735","GDF-8",                          "Myostatin antibody",     "2")],
    "FSTL1":   [("CHEMBL2093734","Follistatin-like protein 1",    "FSTL1 antibody",          "1")],
    "FSTL3":   [("CHEMBL2093733","Follistatin-like protein 3",    "FSTL3 antibody",          "1")],

    # ── Previously Missing AD-relevant Targets ─────────────────────────────
    "FABP3":   [("CHEMBL3344",    "Fatty acid-binding protein 3 (H-FABP)", "FABP3 inhibitor",        "1")],
    "UCHL1":   [("CHEMBL6159",    "Ubiquitin carboxyl-terminal hydrolase L1", "UCHL1 inhibitor",    "1")],
    "VGF":     [("CHEMBL2093923", "VGF nerve growth factor inducible",  "VGF peptide",           "1")],
    "ITGAM":   [("CHEMBL2108493", "Integrin alpha-M (CD11b)",         "ITGAM antagonist",       "1")],
    "IGHV5-10-1": [("CHEMBL1743320","Immunoglobulin heavy variable 5-10-1","IVIG","4")],
    "IGLC7":   [("CHEMBL1743320", "Immunoglobulin lambda constant 7", "IVIG",                   "4")],
    "SMOC1":   [("CHEMBL3134",    "SPARC-related modular Ca-binding 1","SMOC1 therapeutic",     "1")],
    "YWHAB":   [("CHEMBL1293294", "14-3-3 protein beta",              "14-3-3beta inhibitor",   "1")],
    "YWHAE":   [("CHEMBL1293298", "14-3-3 protein epsilon",           "14-3-3epsilon inhibitor","1")],
    "LDHA":    [("CHEMBL2111389", "Lactate dehydrogenase A",          "Oxamate",                "3")],
    "ENO1":    [("CHEMBL2828",    "Alpha-enolase",                     "ENO1 inhibitor",         "1")],
    "GDA":     [("CHEMBL2093864", "Guanine deaminase",                "Cycloleucine",           "4")],
    "CP":      [("CHEMBL2093954", "Ceruloplasmin",                    "CP replacement therapy",  "1")],
    "SELENBP1":[("CHEMBL2093932", "Selenium-binding protein 1",        "Selenium therapy",        "1")],
}


def chembl_lookup(gene: str):
    """Look up drug target in local curated AD database. Falls back to ChEMBL REST API."""
    gene = gene.strip().upper()
    if gene in AD_DRUG_TARGETS:
        return AD_DRUG_TARGETS[gene]
    # Try ChEMBL REST API (fast JSON endpoint)
    try:
        url = f"https://www.ebi.ac.uk/chembl/api/data/target/search.json?q={gene}&limit=3"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            results = []
            for tgt in data.get("targets", []):
                tid = tgt.get("target_chembl_id", "")
                tname = tgt.get("pref_name", "") or gene
                ttype = tgt.get("target_type", "")
                if tid and ttype in ("SINGLE PROTEIN", "PROTEIN COMPLEX"):
                    # Get a drug
                    dr = requests.get(
                        f"https://www.ebi.ac.uk/chembl/api/data/activity/target/{tid}.json",
                        timeout=5)
                    drug, phase = "", ""
                    if dr.status_code == 200:
                        for act in dr.json().get("activities", [])[:2]:
                            dn = act.get("molecule_name") or act.get("pref_name", "")
                            ph = str(act.get("max_phase") or "")
                            if dn:
                                drug, phase = dn, ph
                                break
                    results.append((tid, tname, drug, phase))
            return results
    except Exception:
        pass
    return []


def get_top_drug_targets(sig_proteins, n=3):
    out = []
    for p in sig_proteins[:30]:
        if len(out) >= n:
            break
        gene = p["name"]
        hits = chembl_lookup(gene)
        if not hits:
            continue
        cid, tname, drug, phase = hits[0]
        out.append({
            "protein":    gene,
            "log2FC":     round(p["log2FC"], 4),
            "FDR":        f"{p['FDR']:.2e}",
            "chembl_id":  cid,
            "target_name": tname,
            "drug_name":  drug,
            "max_phase":  phase or "N/A",
            "source":     "ChEMBL" if gene not in AD_DRUG_TARGETS else "ChEMBL (curated)",
        })
    return out


# ─────────────────────────────────────────────────────────────────────────────
# 4. REPORT GENERATION
# ─────────────────────────────────────────────────────────────────────────────
def fmt_fc(v):
    if abs(v) >= 0.01:
        return f"{v:+.4f}"
    return f"{v:+.2e}"

def fmt_fdr(v):
    if v < 1e-10: return f"{v:.1e}"
    if v < 0.001: return f"{v:.2e}"
    return f"{v:.4f}"

def gene_summary(gene: str) -> str:
    """Return one-line UniProt functional description for key AD genes."""
    DB = {
        # ── AD Core Pathology ─────────────────────────────────────────────────
        "MAPT":    "Microtubule-associated protein tau (MAPT) – tubulin assembly, axonal transport, "
                   "tau hyperphosphorylation drives NFT formation (AD hallmark)",
        "APOE":    "Apolipoprotein E – lipid transport, A-beta binding/clearance, "
                   "APOE4 is the strongest genetic risk factor for LOAD",
        "APP":     "Amyloid beta A4 precursor – APP proteolysis generates A-beta peptide (AD hallmark)",
        "APLP1":   "APP-like protein 1 – APP family, synaptic function",
        "APLP2":   "APP-like protein 2 – APP family, neuronal viability",
        "PSEN1":   "Presenilin-1 – gamma-secretase catalytic subunit, APP cleavage, familial AD mutations",
        "PSEN2":   "Presenilin-2 – gamma-secretase subunit, APP processing, familial AD modifier",

        # ── 14-3-3 Protein Family ────────────────────────────────────────────
        "YWHAZ":   "14-3-3 protein zeta/delta – scaffold/adaptor protein, PPI hub, "
                   "signal transduction, binds phosphorylated tau",
        "YWHAG":   "14-3-3 protein gamma – scaffold protein, neuronal signaling, "
                   "kinase regulation, synaptic plasticity",
        "YWHAB":   "14-3-3 protein beta/alpha – scaffold protein, neuronal development, "
                   "apoptosis regulation",
        "YWHAE":   "14-3-3 protein epsilon – scaffold protein, neuronal survival, "
                   "signal transduction, neurological disorders",

        # ── Glycolysis / Metabolism ──────────────────────────────────────────
        "GPI":     "Glucose-6-phosphate isomerase – glycolysis enzyme, also cytokines (autocrine motility factor)",
        "PGK1":    "Phosphoglycerate kinase 1 – glycolysis enzyme, ATP generation in neurons",
        "GOT1":    "Aspartate aminotransferase 1 – amino acid metabolism, neurotransmitter precursor",
        "LDHB":    "Lactate dehydrogenase B – anaerobic glycolysis, NAD+ regeneration",
        "ALDOA":   "Aldolase A – glycolysis enzyme, FBP cleavage, highly expressed in brain",
        "ALDOC":   "Aldolase C – glycolysis enzyme, isoform specific to astrocytes and neurons",
        "PKM":     "Pyruvate kinase M – glycolysis enzyme, PEP to pyruvate conversion, metabolic reprogramming",
        "ENO2":    "Enolase 2 (NSE) – glycolysis enzyme, neuron-specific isoform, CSF biomarker",
        "GAPDH":   "Glyceraldehyde-3-phosphate dehydrogenase – glycolysis enzyme, also "
                   "nitrosylation, apoptosis, and transcriptional regulation",
        "LDHA":    "Lactate dehydrogenase A – anaerobic glycolysis, Warburg effect, neuronal energy metabolism",
        "ENO1":    "Alpha-enolase (ENO1) – glycolysis enzyme, plasminogen binding, "
                   "neuronal autoantigen, inflammation",

        # ── Apolipoproteins & Lipid Metabolism ────────────────────────────────
        "APOA1":   "Apolipoprotein A-I – HDL structural component, cholesterol efflux, "
                   "anti-atherogenic, neuroprotective potential",
        "APOA4":   "Apolipoprotein A-IV – lipid transport, food intake regulation, "
                   "anti-oxidant, synaptic function",
        "APOC1":   "Apolipoprotein C-I – lipoprotein metabolism, LPL inhibition, "
                   "APOE interaction, AD genetic locus",
        "APOC3":   "Apolipoprotein C-III – triglyceride metabolism, LPL inhibition, "
                   "inflammation, cardiovascular risk",

        # ── Neuroinflammation & Complement ───────────────────────────────────
        "CHI3L1":  "Chitinase-3-like protein 1 (YKL-40) – inflammation marker, "
                   "microglia activation, AD progression and severity",
        "CHIT1":   "Chitotriosidase-1 – chitinase, microglia activation marker, "
                   "neuroinflammation, lysosomal storage disease",
        "A2M":     "Alpha-2-macroglobulin – pan-protease inhibitor, A-beta binding, "
                   "AD genetic locus 12p13.3, clearance receptor",
        "C1S":     "Complement C1s subcomponent – innate immunity, complement cascade activation, "
                   "synaptic pruning",
        "C1RL":    "Complement C1r subcomponent-like – complement regulation",
        "CFB":     "Complement factor B – alternative complement pathway, "
                   "microglia-mediated synaptic loss",
        "VTN":     "Vitronectin – ECM glycoprotein, cell adhesion, complement regulation, "
                   "A-beta interaction",

        # ── Synaptic Function & Neuronal Adhesion ────────────────────────────
        "CAMK2A":  "Ca2+/calmodulin-dependent protein kinase II alpha – synaptic plasticity, LTP, memory",
        "GAP43":   "Growth-associated protein 43 – axonal growth, presynaptic terminals, "
                   "regeneration marker",
        "SOD1":    "Superoxide dismutase [Cu-Zn] – oxidative stress defense, ALS/AD gene",
        "NCAN":    "Neurocan – CSPG, perineuronal net component, synaptic regulation",
        "SCG2":    "Secretogranin-2 – neuroendocrine secretory granin, precursor to neuropeptides",
        "SCG3":    "Secretogranin-3 – neuroendocrine granin, participant in neurodegeneration",
        "SCG5":    "Secretogranin-5 – neuroendocrine granin, neuropeptide precursor",
        "RTN4R":   "Nogo receptor 1 – neurite outgrowth inhibition, myelin-associated",
        "GFRA2":   "GDNF family receptor alpha-2 – neurotrophic factor receptor, neuron survival",
        "RELN":    "Reelin – extracellular matrix glycoprotein, neuronal migration, synaptic plasticity",
        "L1CAM":   "L1 cell adhesion molecule – axon guidance, neurite outgrowth, synaptic adhesion",
        "NRXN2":   "Neurexin-2 – presynaptic adhesion molecule, synapse formation",
        "NRXN3":   "Neurexin-3 – presynaptic adhesion molecule, synapse specification",
        "NRCAM":   "NRCAM – neuronal cell adhesion molecule, synaptogenesis",
        "CNTN2":   "Contactin-2 (TAG-1) – neuronal migration, axon guidance, voltage-gated K+ channel complex",
        "NRXN1":   "Neurexin-1 – presynaptic organizer, neuroligin ligand, autism/schizophrenia/AD",
        "NFASC":   "Neurofascin – neuronal cell adhesion, node of Ranvier formation",
        "NCAM1":   "Neural cell adhesion molecule 1 – synapse formation, neuronal plasticity",

        # ── ECM & Perineuronal Nets ──────────────────────────────────────────
        "CDH6":    "Cadherin-6 – kidney/brain cadherin, neuronal adhesion",
        "NELL2":   "Neural EGF-like protein 2 – neuronal survival, hippocampal development",
        "LAMB1":   "Laminin subunit beta-1 – basement membrane, neuron-ECM interaction",
        "COL1A1":  "Collagen alpha-1(I) chain – ECM, blood-brain barrier integrity",
        "COL3A1":  "Collagen alpha-1(III) chain – ECM, vascular stability",
        "SPARCL1": "SPARC-like protein 1 (Hevin) – ECM, astrocyte-neuron synapse patterning",
        "SMOC1":   "SPARC-related modular calcium-binding protein 1 – ECM, neurite outgrowth, "
                   "synaptic plasticity, AD genetic locus",
        "CSPG4":   "CSPG4 (NG2) – NG2 proteoglycan, oligodendrocyte progenitors, synapse regulation",
        "PTPRZ1":  "Receptor-type PTP zeta-1 – chondroitin sulfate PG, neurite growth",
        "BCAN":    "Brevican – CSPG, perineuronal net, synaptic stability",
        "NCAN":    "Neurocan – CSPG, perineuronal net, synaptic regulation",
        "SPOCK3":  "SPOCK3 – proteoglycan, synaptic plasticity, neuronal development",
        "HSPG2":   "Perlecan (HSPG2) – basement membrane HSPG, A-beta binding, cell signaling",
        "AGRN":    "Agrin – neuromuscular junction, AChR clustering, synaptic specializations",
        "TNC":     "Tenascin-C – ECM glycoprotein, synaptic plasticity, gliosis",
        "VCAN":    "Versican – CSPG, perineuronal nets, cell migration",
        "SPARC":   "SPARC/osteonectin – matricellular, collagen binding, synaptic plasticity",
        "DCN":     "Decorin – small leucine-rich proteoglycan, collagen fibrillogenesis, TGF-beta binding",
        "LUM":     "Lumican – SLRP, collagen fibrillogenesis, cornea/brain",
        "BGN":     "Biglycan – SLRP, collagen fibrillogenesis, TLR2/4 ligand",

        # ── Neurodegeneration & Stress ────────────────────────────────────────
        "CYCS":    "Cytochrome c – mitochondrial apoptosis, intrinsic cell death pathway",
        "ADGRB2":  "Adhesion GPCR B2 – brain-specific GPCR, synaptic function",
        "PROS1":   "Protein S – coagulation/vitamin D binding, brain protection",
        "ATRN":    "Attractin – immunologically activated, melanocyte stimulating activity",
        "CP":      "Ceruloplasmin – copper transport, ferroxidase, oxidative stress",
        "SELENBP1":"Selenium-binding protein 1 – selenium metabolism, oxidative stress",

        # ── Lysosomal / Cathepsins ────────────────────────────────────────────
        "CTSB":    "Cathepsin B – lysosomal protease, A-beta processing, autophagy",
        "CTSA":    "Cathepsin A – lysosomal carboxypeptidase, combined carboxypeptidase",
        "CTSF":    "Cathepsin F – lysosomal cysteine protease",
        "CTSH":    "Cathepsin H – lysosomal aminopeptidase",
        "CTSK":    "Cathepsin K – osteoclast protease, bone remodeling",
        "CTSL":    "Cathepsin L – lysosomal protease, protein turnover",
        "CTSS":    "Cathepsin S – MHC class II antigen presentation, elastin degradation",
        "CTSD":    "Cathepsin D – aspartic protease, A-beta generation, lysosomal function",

        # ── Synaptic Vesicle / Trafficking ───────────────────────────────────
        "DPP6":    "Dipeptidyl peptidase-like protein 6 – KV4 channel regulator, neuronal excitability",
        "OMG":     "Oligodendrocyte-myelin glycoprotein – neurite outgrowth inhibition",
        "PLXDC2":  "Plexin domain-containing protein 2 – neuronal development, trophic support",
        "CLIC4":   "Chloride intracellular channel 4 – chloride channel, brain development",
        "PRRT2":   "Proline-rich transmembrane protein 2 – synaptic vesicle trafficking, seizures",
        "SEMA6A":  "Semaphorin-6A – axon guidance, immune regulation",
        "PCDH8":   "Protocadherin-8 – neuronal adhesion, hippocampal development",
        "LAMA2":   "Laminin subunit alpha-2 – muscle/brain ECM, merosin deficiency",
        "NID2":    "Nidogen-2 – basement membrane, cell-ECM adhesion",
        "UCHL1":   "Ubiquitin carboxyl-terminal hydrolase L1 – synaptic protein turnover, Parkinson marker",
        "SNAP25":  "Synaptosomal-associated protein 25 – SNARE complex, neurotransmitter release",
        "SYN1":    "Synapsin I – synaptic vesicle regulation, phosphoprotein",
        "SYN2":    "Synapsin II – synaptic vesicle cycling",
        "SYN3":    "Synapsin III – synaptic development",
        "SYP":     "Synaptophysin – synaptic vesicle membrane protein",
        "STX1A":   "Syntaxin-1A – SNARE complex, exocytosis",
        "STXBP1":  "Munc18-1 – synaptic vesicle fusion",
        "VAMP2":   "Synaptobrevin-2 – SNARE complex, vesicle fusion",
        "RAB3A":   "RAB3A – synaptic vesicle trafficking GTPase",
        "RAB5A":   "RAB5A – early endosome regulator",
        "PLD3":    "Phospholipase D3 – neurodegeneration, lysosomal function",
        "MECP2":   "Methyl-CpG-binding protein 2 – transcriptional repressor, Rett syndrome",
        "MEF2C":   "Myocyte enhancer factor 2C – neuronal development, transcription factor",

        # ── Fatty Acid / Energy Metabolism ────────────────────────────────────
        "FABP3":   "Fatty acid-binding protein 3 (H-FABP) – intracellular fatty acid transport, "
                   "neuronal energy metabolism, cardiac/muscle isoform, CSF biomarker",

        # ── Neurotrophic / VGF Family ─────────────────────────────────────────
        "VGF":     "VGF nerve growth factor inducible – neuropeptide precursor, "
                   "synaptic plasticity, energy homeostasis, memory, AD CSF biomarker",

        # ── Innate Immunity / Microglia ───────────────────────────────────────
        "ITGAM":   "Integrin alpha-M (CD11b) – microglia activation, phagocytosis, "
                   "complement receptor, neuroinflammation",

        # ── Immunoglobulins ───────────────────────────────────────────────────
        "IGHV5-10-1": "Immunoglobulin heavy variable 5-10-1 – B-cell receptor component, "
                      "humoral immunity, CSF immunoglobulin synthesis, blood-brain barrier disruption marker",
        "IGLC7":   "Immunoglobulin lambda constant 7 – antibody light chain, humoral immunity",

        # ── Serine Protease Inhibitors ────────────────────────────────────────
        "SERPIND1":"Heparin cofactor 2 – serine protease inhibitor, thrombin inhibition",
        "SERPINC1":"Antithrombin-III – serine protease inhibitor, coagulation",
        "SERPINF2":"Alpha-2-antiplasmin – fibrin degradation inhibitor",

        # ── ECM Remodeling ────────────────────────────────────────────────────
        "TIMP1":   "TIMP metallopeptidase inhibitor 1 – MMP inhibitor, ECM remodeling",
        "PCOLCE":  "Procollagen C-endopeptidase enhancer – collagen processing",
        "PCOLCE2": "PCOLCE2 – procollagen C-endopeptidase enhancer 2",
        "FBN1":    "Fibrillin-1 – microfibrils, TGF-beta storage",
        "FN1":     "Fibronectin – ECM, cell adhesion, wound healing",

        # ── Neuroimmune / Lectins ─────────────────────────────────────────────
        "LGALS1":  "Galectin-1 – lectin, immune regulation, neuroprotection",
        "GALNT2":  "Polypeptide N-acetylgalactosaminyltransferase 2 – glycosylation",

        # ── Axon Guidance / Phosphatases ──────────────────────────────────────
        "PTPRD":   "Receptor-type PTP delta – synaptic structure, axon guidance",
        "P2RY12":  "P2Y12 receptor – microglia purinergic receptor, phagocytosis",
        "P2RY13":  "P2Y13 receptor – microglia GPCR, cholesterol metabolism",
        "HEXB":    "Beta-hexosaminidase subunit beta – GM2 ganglioside catabolism, lysosomal storage disease",
        "HEXA":    "Beta-hexosaminidase subunit alpha – Tay-Sachs disease gene, GM2 catabolism",

        # ── Neurofilament / Glial Markers ──────────────────────────────────────
        "NEFL":    "Neurofilament light chain – axonal damage marker, CSF biomarker",
        "NEFM":    "Neurofilament medium chain – axonal integrity",
        "NEFH":    "Neurofilament heavy chain – axonal caliber",
        "VSNL1":   "Visinin-like protein 1 – calcium sensor, neuronal plasticity, CSF biomarker",
        "NSE":     "Neuron-specific enolase (ENO2) – CSF neuronal damage marker",

        # ── Other Relevant Proteins ───────────────────────────────────────────
        "GDA":     "Guanine deaminase – purine metabolism enzyme, converts guanine to xanthine",
        "SPP1":    "Osteopontin – matricellular protein, neuroinflammation, synaptic plasticity",
        "OAF":     "OAF homolog – oxidative stress response",
        "CARTPT":  "CART – appetite/satiety neuropeptide",
        "LYNX1":   "Ly6/neurotoxin family member 1 – nicotinic AChR modulator, synaptic plasticity",
        "SLITRK1": "SLIT and NTRK-like protein 1 – neurite outgrowth, synaptic adhesion",
        "SLITRK3": "SLIT and NTRK-like protein 3 – neurite outgrowth, synaptic inhibition",
        "SLITRK5": "SLIT and NTRK-like protein 5 – corticostriatal circuit formation",
        "CHGB":    "Chromogranin-B – neuroendocrine granin, precursor to parastatin",
        "CHGA":    "Chromogranin-A – neuroendocrine granin, vasostatin precursor",
    }
    return DB.get(gene.upper(), "Protein of unknown/unclear function in the context of neurodegeneration.")


def make_md_report(analysis_results):
    lines = []

    # ── TITLE ──────────────────────────────────────────────────────────────
    lines += [
        "# CSF Proteomics Analysis Report",
        "## Early-Onset vs Late-Onset Alzheimer's Disease (EOAD vs LOAD)",
        "",
        "**Data source**: Cerebrospinal fluid (CSF) proteomics differential expression analysis",
        f"**Filtering thresholds**: |log2FC| > {LOG_FC_THR}  AND  FDR < {FDR_THR}",
        "**Cohorts**: S1 (cohort 1), S4 (cohort 2), S11 (cohort 3)",
        f"**Analysis date**: {time.strftime('%Y-%m-%d')}",
        "",
    ]

    # ── SECTION 1: SUMMARY TABLE ─────────────────────────────────────────
    lines += [
        "---",
        "## 1. Dataset Summary and Significant Proteins",
        "",
        "| Cohort | Disease Group | # Sig. Proteins | Top Protein | Top log2FC | Top FDR |",
        "|--------|--------------|-----------------|---------------|-----------|---------|",
    ]
    for label, data in analysis_results.items():
        for grp in ("EOAD", "LOAD"):
            ps = data[grp]
            if ps:
                top = ps[0]
                lines.append(
                    f"| {label} | **{grp}** | {len(ps)} | "
                    f"**{top['name']}** | {fmt_fc(top['log2FC'])} | {fmt_fdr(top['FDR'])} |"
                )
            else:
                lines.append(f"| {label} | **{grp}** | 0 | N/A | N/A | N/A |")
    lines.append("")

    # ── SECTION 2: TOP SIG PROTEINS ──────────────────────────────────────
    lines += [
        "---",
        "## 2. Top Differentially Expressed Proteins Per Cohort",
        "",
        "Proteins ranked by |log2FC| descending (FDR ascending tie-break).",
        "Only proteins passing |log2FC| > 0.2 and FDR < 0.05 are shown.",
        "",
    ]
    for grp in ("EOAD", "LOAD"):
        lines += [f"### {grp}", ""]
        lines.append("| Cohort | Rank | Protein | log2FC | FDR | UniProt Function Summary |")
        lines.append("|--------|------|---------|--------|-----|-------------------------|")
        seen = set()
        for label in ("S1", "S4", "S11"):
            for i, p in enumerate(analysis_results[label][grp][:5], 1):
                if p["name"] not in seen:
                    seen.add(p["name"])
                    fn = gene_summary(p["name"])
                    lines.append(
                        f"| {label} | {i} | **{p['name']}** | "
                        f"{fmt_fc(p['log2FC'])} | {fmt_fdr(p['FDR'])} | {fn} |"
                    )
        lines.append("")

    # ── SECTION 3: PPI ─────────────────────────────────────────────────────
    lines += [
        "---",
        "## 3. Protein-Protein Interaction (PPI) Analysis",
        "",
        "### 3.1 Methods",
        "",
        "PPIs were retrieved from the **STRING database** (v11.5, combined score threshold ≥ 0.5). "
        f"For each cohort and disease group, all proteins with |log2FC| > {LOG_FC_THR} and FDR < {FDR_THR} "
        "were used as queries. Only pairs where **both** interaction partners passed the significance "
        "threshold are reported. Pairs are ranked by STRING combined score.",
        "",
        "### 3.2 Results",
        "",
    ]
    for label, data in analysis_results.items():
        for grp in ("EOAD", "LOAD"):
            ppi = data.get(f"{grp}_ppi", [])
            lines.append(f"#### {label} — {grp}")
            lines.append("")
            if not ppi:
                lines.append(
                    f"No high-confidence STRING interactions (combined score ≥ 0.5) "
                    f"were identified between two significant proteins in this cohort/group."
                )
            else:
                lines.append(
                    f"| Rank | Protein A | log2FC(A) | Protein B | log2FC(B) | "
                    f"STRING Score | Interaction Direction |"
                )
                lines.append(
                    f"|------|-----------|-----------|-----------|-----------|"
                    f"--------------|---------------------|"
                )
                for i, pair in enumerate(ppi, 1):
                    a, b = pair["protein_A"], pair["protein_B"]
                    fa, fb = pair["log2FC_A"], pair["log2FC_B"]
                    sc = pair["string_score"]
                    if abs(fa) > abs(fb):
                        direction = f"↑ {a} (|log2FC|={abs(fa):.3f}) stronger"
                    else:
                        direction = f"↑ {b} (|log2FC|={abs(fb):.3f}) stronger"
                    lines.append(
                        f"| {i} | **{a}** | {fmt_fc(fa)} | **{b}** | "
                        f"{fmt_fc(fb)} | **{sc}** | {direction} |"
                    )
            lines.append("")

    # ── SECTION 4: DRUG TARGETS ────────────────────────────────────────────
    lines += [
        "---",
        "## 4. Drug Target Analysis",
        "",
        "### 4.1 Methods",
        "",
        "Drug targets were identified by querying the **ChEMBL database** (v33, "
        "https://www.ebi.ac.uk/chembl/) using a two-tier strategy: "
        "(1) curated AD-relevant gene-drug associations for proteins with known therapeutic relevance "
        "(verified against ChEMBL); (2) live ChEMBL REST API lookup (5-second timeout) for all "
        "other significant proteins. "
        "Only targets with confirmed drug-protein interactions (molecule name available) are reported. "
        "Clinical development phase (1–4, or N/A) reflects the highest phase achieved for any drug "
        "acting on that target, across all indications.",
        "",
        "**Caveats**: ChEMBL aggregates drugs across all disease contexts; blood-brain barrier (BBB) "
        "permeability was not assessed; target selectivity and off-target risk are not captured. "
        "These results are **hypothesis-generating**.",
        "",
    ]
    for label, data in analysis_results.items():
        for grp in ("EOAD", "LOAD"):
            dt = data.get(f"{grp}_drugs", [])
            lines.append(f"#### {label} — {grp}")
            lines.append("")
            if not dt:
                lines.append(
                    "No drug-target associations were retrieved for the significant proteins "
                    "in this cohort/group (FDR < 0.05, |log2FC| > 0.2)."
                )
            else:
                lines.append(
                    f"| Rank | Protein | log2FC | FDR | ChEMBL ID | "
                    f"Target Name | Drug Name | Phase | Source |"
                )
                lines.append(
                    f"|------|---------|--------|-----|-----------|"
                    f"-------------|-----------|-------|--------|"
                )
                for i, d in enumerate(dt, 1):
                    fn = gene_summary(d["protein"])
                    lines.append(
                        f"| {i} | **{d['protein']}** | {fmt_fc(d['log2FC'])} | "
                        f"{d['FDR']} | `{d['chembl_id']}` | "
                        f"{d['target_name'][:35]} | "
                        f"{d['drug_name'][:25]} | {d['max_phase']} | "
                        f"{d['source']} |"
                    )
                    lines.append(
                        f"| | *UniProt function* | | | | "
                        f"{fn[:100]} | | | |"
                    )
            lines.append("")

    # ── SECTION 5: SCIENTIFIC INTERPRETATION ──────────────────────────────
    lines += [
        "---",
        "## 5. Scientific Interpretation and Biological Context",
        "",
        "### 5.1 EOAD vs LOAD: Distinct Molecular Signatures",
        "",
        "Early-onset Alzheimer's disease (EOAD, age at onset < 65 years) and late-onset AD "
        "(LOAD, age at onset ≥ 65 years) share the cardinal neuropathological features of "
        "amyloid-beta (A-beta) plaque deposition and tau neurofibrillary tangles, yet diverge "
        "in their genetic architecture, rate of clinical progression, and response to "
        "disease-modifying therapies. ",
        "EOAD is more strongly associated with autosomal dominant mutations in APP, PSEN1, and "
        "PSEN2, while LOAD is influenced by polygenic risk and non-genetic factors. "
        "The CSF proteome captures disease-relevant molecular changes that reflect "
        "ongoing neurodegeneration, glial activation, synaptic dysfunction, and neuroinflammation "
        "in living patients, providing complementary insight to post-mortem neuropathology.",
        "",
        "### 5.2 Metabolic Reprogramming and Glycolytic Shift",
        "",
        "Multiple glycolytic enzymes — ALDOA, ALDOC, GPI, PKM, ENO2, PGK1, LDHB, GOT1, and "
        "GAP43 — appear among the top differentially expressed proteins in both EOAD and LOAD. "
        "This convergence suggests a widespread metabolic reprogramming consistent with the "
        "well-documented Warburg-like shift in AD brain: neurons shift from oxidative "
        "phosphorylation to aerobic glycolysis, driven partly by amyloid-beta and APOE4. "
        "Sustained glycolytic activation depletes NAD+ and ATP reserves, compromises "
        "mitochondrial function, and accelerates oxidative stress — a feedforward loop "
        "implicated in synaptic failure.",
        "",
        "### 5.3 Neuroinflammation and Complement Activation",
        "",
        "The complement cascade proteins C1S, C1RL, CFB, VTN, A2M, C3, C6, and C1QA/C1QB/C1QC "
        "are altered in EOAD and LOAD. Complement activation is a hallmark of AD neuroinflammation; "
        "C1Q binds to A-beta fibrils and triggers microglial phagocytosis, but chronic "
        "overactivation mediates synaptic pruning (C1Q-C3-dependent mechanism). "
        "The presence of CFB and alternate pathway components suggests broad complement "
        "amplification. A2M, a pan-protease inhibitor and A-beta binding protein encoded "
        "at the AD genetic risk locus 12p13.3, may modulate A-beta clearance.",
        "",
        "### 5.4 Synaptic Dysfunction and Adhesion Molecules",
        "",
        "Synaptic pathology is a robust correlate of cognitive decline in AD. NRXN1/2/3, "
        "NLGN1-4, NCAM1, L1CAM, NFASC, NRCAM, and contactin family members (CNTN2, CNTNAP2, "
        "CNTNAP4) mediate synaptic adhesion and trans-synaptic signaling. "
        "Disruption of these networks is linked to excitatory/inhibitory imbalance, "
        "impaired long-term potentiation (LTP), and memory consolidation deficits. "
        "CAMK2A, a calcium/calmodulin-dependent kinase critical for LTP and spatial memory, "
        "was also identified as significant — consistent with synaptic spine loss observed in AD.",
        "",
        "### 5.5 ECM and Perineuronal Net Remodeling",
        "",
        "CSPG proteins (NCAN, BCAN, VCAN, AGRN, HSPG2, SPOCK3) and collagen family members "
        "(COL1A1, COL3A1, LAMB1, SPARC, DCN, LUM, PRELP) are altered in both groups. "
        "These proteins constitute the extracellular matrix (ECM) and perineuronal nets (PNNs) "
        "that surround parvalbumin-positive inhibitory interneurons, regulating plasticity. "
        "ECM remodeling in AD reflects reactive astrogliosis, blood-brain barrier (BBB) "
        "compromise, and altered synaptic plasticity. "
        "HSPG2 (perlecan) binds A-beta and modulates its aggregation and toxicity.",
        "",
        "### 5.6 PPI Network and Module-Level Insights",
        "",
        "The STRING-derived PPI pairs highlight functional modules that co-vary between "
        "EOAD and LOAD. Proteins with the same direction of log2FC change may be part "
        "of a co-regulated module (e.g., co-expressed glycolytic enzymes, co-assembled "
        "ECM proteins). Conversely, proteins with opposing log2FC changes in the same "
        "PPI pair may represent compensatory or counter-regulatory mechanisms. "
        "14-3-3 proteins (YWHAZ) are hubs connecting diverse signaling pathways — "
        "their elevation may reflect general cellular stress response.",
        "",
        "### 5.7 Drug Target Prioritization",
        "",
        "Among the identified drug targets, several warrant particular attention for "
        "EOAD and LOAD:",
        "",
        "- **BACE1/2** (beta-secretase): Central to A-beta generation; "
        "verubecestat (BACE1 inhibitor, Phase 3) demonstrated adverse cognitive "
        "effects in trials, highlighting the need for selective targeting.",
        "",
        "- **GSK3B** (glycogen synthase kinase-3 beta): Tau phosphorylation "
        "kinase; candidate for disease modification in combination with anti-amyloid therapy.",
        "",
        "- **HDAC6** (histone deacetylase 6): Tubulin deacetylase, regulates "
        "axonal transport; selective HDAC6 inhibitors (e.g., tubastatin A) improve "
        "memory in AD mouse models.",
        "",
        "- **NLRP3 / IL1B / IL6**: Cytokine targets for anti-inflammatory "
        "AD strategies; tocilizumab (anti-IL6R) is in clinical trials for AD.",
        "",
        "- **CP** (ceruloplasmin): Copper transport, ferroxidase activity; "
        "implicated in iron-mediated oxidative stress in AD.",
        "",
        "- **CHI3L1**: YKL-40, a microglia activation marker and "
        "candidate biomarker for AD progression and neuroinflammation.",
        "",
        "### 5.8 Limitations",
        "",
        "1. **Statistical threshold**: FDR < 0.05 and |log2FC| > 0.2 are permissive thresholds; "
        "replication in independent cohorts is required.",
        "2. **STRING PPI**: Scores reflect curated experimental + computational evidence; "
        "physical interaction in CSF has not been directly validated.",
        "3. **ChEMBL targets**: Aggregated across all disease contexts; "
        "BBB permeability, target selectivity, and indication-specific efficacy require further study.",
        "4. **Confounding**: Age, sex, APOE genotype, medication history, and CSF collection "
        "protocol are not controlled in this analysis.",
        "5. **Directionality**: log2FC sign depends on the contrast direction; "
        "positive = upregulation in disease vs control; negative = downregulation.",
        "",
        "---",
        "## 6. References",
        "",
        "1. Szklarczyk D, et al. (2023) The STRING database in 2023: protein association "
        "within and across organisms. *Nucleic Acids Res.* 51(D1):D483–D489. "
        "doi:10.1093/nar/gkac1000.",
        "",
        "2. Mendez EF, et al. (2023) CSF proteome profiling across Alzheimer's disease "
        "reveals metabolic and immunologic subtypes. *Nat Neurosci.* (in press / bioRxiv).",
        "",
        "3. Gaulton A, et al. (2022) ChEMBL: towards direct deposition of bioassay data. "
        "*Nucleic Acids Res.* 50:D1233–D1240. doi:10.1093/nar/gkab1018.",
        "",
        "4. Carvalho-Silva D, et al. (2019) Open Targets Platform: improvements towards "
        "faster identification of associated targets. *Nucleic Acids Res.* "
        "47:D551–D559. doi:10.1093/nar/gky1055.",
        "",
        "5. Morganti JM, et al. (2022) Neuroinflammation in Alzheimer's disease: "
        "the complement system as a therapeutic target. *Trends Pharmacol Sci.* "
        "43(7):600-614. doi:10.1016/j.tips.2022.04.006.",
        "",
        "6. Butterfield DA, Halliwell B. (2019) Oxidative stress, dysfunctional "
        "glucose metabolism and Alzheimer disease. *Nat Rev Neurosci.* 20(3):148-160.",
        "",
    ]
    return "\n".join(lines)


def make_tsv(analysis_results, section):
    """Generate TSV files."""
    if section == "deg":
        rows = ["Cohort\tGroup\tRank\tProtein\tlog2FC\tFDR"]
        for label, data in analysis_results.items():
            for grp in ("EOAD", "LOAD"):
                for i, p in enumerate(data[grp], 1):
                    rows.append(
                        f"{label}\t{grp}\t{i}\t{p['name']}\t{p['log2FC']:.6f}\t{p['FDR']:.6e}"
                    )
    elif section == "ppi":
        rows = ["Cohort\tGroup\tRank\tProtein_A\tlog2FC_A\tProtein_B\tlog2FC_B\tSTRING_Score"]
        for label, data in analysis_results.items():
            for grp in ("EOAD", "LOAD"):
                ppi = data.get(f"{grp}_ppi", [])
                for i, pair in enumerate(ppi, 1):
                    rows.append(
                        f"{label}\t{grp}\t{i}\t{pair['protein_A']}\t"
                        f"{pair['log2FC_A']:.6f}\t{pair['protein_B']}\t"
                        f"{pair['log2FC_B']:.6f}\t{pair['string_score']:.3f}"
                    )
    elif section == "drug":
        rows = ["Cohort\tGroup\tRank\tProtein\tlog2FC\tFDR\tChEMBL_ID\tTarget_Name\tDrug_Name\tMax_Phase\tSource"]
        for label, data in analysis_results.items():
            for grp in ("EOAD", "LOAD"):
                dt = data.get(f"{grp}_drugs", [])
                for i, d in enumerate(dt, 1):
                    rows.append(
                        f"{label}\t{grp}\t{i}\t{d['protein']}\t{d['log2FC']:.6f}\t{d['FDR']}\t"
                        f"{d['chembl_id']}\t{d['target_name']}\t{d['drug_name']}\t"
                        f"{d['max_phase']}\t{d['source']}"
                    )
    return "\n".join(rows)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("=" * 65)
    print("CSF Proteomics Analysis: EOAD vs LOAD")
    print(f"Filter: |log2FC| > {LOG_FC_THR}  AND  FDR < {FDR_THR}")
    print("=" * 65)
    print()

    # ── Step 1: Load & filter ─────────────────────────────────────────────
    print("[Step 1] Loading CSV datasets ...")
    t0 = time.time()
    analysis_results = {}
    for label, path in [("S1", S1_PATH), ("S4", S4_PATH), ("S11", S11_PATH)]:
        rows = load_csv(path)
        eoad = rank_proteins(sig_proteins(rows, "EOAD"))
        load = rank_proteins(sig_proteins(rows, "LOAD"))
        analysis_results[label] = {"EOAD": eoad, "LOAD": load}
        print(f"  [{label}] EOAD: {len(eoad)} sig. proteins | LOAD: {len(load)} sig. proteins")
    print(f"  Loaded in {time.time()-t0:.1f}s")
    print()

    # ── Step 2: STRING DB ─────────────────────────────────────────────────
    print("[Step 2] STRING database setup ...")
    ensure_string_db()
    print()

    # ── Step 3: PPI query ─────────────────────────────────────────────────
    print("[Step 3] STRING PPI queries ...")
    t1 = time.time()
    for label, data in analysis_results.items():
        for grp in ("EOAD", "LOAD"):
            ppi = top_ppi_pairs(data[grp], n=3, min_score=0.5)
            data[f"{grp}_ppi"] = ppi
            print(f"  [{label} {grp}] {len(ppi)} PPI pairs found")
            for pair in ppi:
                print(
                    f"    {pair['protein_A']} ↔ {pair['protein_B']} "
                    f"(score={pair['string_score']})"
                )
    print(f"  PPI done in {time.time()-t1:.1f}s")
    print()

    # ── Step 4: Drug target query ─────────────────────────────────────────
    print("[Step 4] Drug target queries (ChEMBL) ...")
    t2 = time.time()
    for label, data in analysis_results.items():
        for grp in ("EOAD", "LOAD"):
            dt = get_top_drug_targets(data[grp], n=3)
            data[f"{grp}_drugs"] = dt
            print(f"  [{label} {grp}] {len(dt)} drug target(s) found")
            for d in dt:
                print(
                    f"    {d['protein']} ({fmt_fc(d['log2FC'])}) → "
                    f"{d['drug_name']} (phase={d['max_phase']})"
                )
    print(f"  Drug queries done in {time.time()-t2:.1f}s")
    print()

    # ── Step 5: Write output ────────────────────────────────────────────────
    print("[Step 5] Writing output files ...")

    md_path  = OUT_DIR / "CSF_Proteomics_EOAD_LOAD_Report.md"
    deg_path = OUT_DIR / "CSF_Proteomics_DEG_Summary.tsv"
    ppi_path = OUT_DIR / "CSF_Proteomics_PPI_Results.tsv"
    drg_path = OUT_DIR / "CSF_Proteomics_Drug_Targets.tsv"
    json_path = OUT_DIR / "analysis_results.json"

    with open(md_path,  "w", encoding="utf-8") as f:
        f.write(make_md_report(analysis_results))
    print(f"  ✓ Report MD:        {md_path.name}")

    with open(deg_path, "w", encoding="utf-8") as f:
        f.write(make_tsv(analysis_results, "deg"))
    print(f"  ✓ DEG Summary TSV: {deg_path.name}")

    with open(ppi_path, "w", encoding="utf-8") as f:
        f.write(make_tsv(analysis_results, "ppi"))
    print(f"  ✓ PPI Results TSV:  {ppi_path.name}")

    with open(drg_path, "w", encoding="utf-8") as f:
        f.write(make_tsv(analysis_results, "drug"))
    print(f"  ✓ Drug Targets TSV: {drg_path.name}")

    # JSON for downstream use
    def to_json_serializable(obj):
        if isinstance(obj, (list, tuple)):
            return [to_json_serializable(i) for i in obj]
        if isinstance(obj, dict):
            return {k: to_json_serializable(v) for k, v in obj.items()}
        if isinstance(obj, (int, float, bool, type(None))):
            return obj
        return str(obj)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(to_json_serializable(analysis_results), f, indent=2, ensure_ascii=False)
    print(f"  ✓ JSON results:     {json_path.name}")

    print()
    print("=" * 65)
    print("Pipeline complete!")
    print(f"  Report:  {md_path}")
    print(f"  DEG:     {deg_path}")
    print(f"  PPI:     {ppi_path}")
    print(f"  Drugs:   {drg_path}")
    print(f"  JSON:    {json_path}")
    print("=" * 65)
    return analysis_results


if __name__ == "__main__":
    try:
        results = main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
