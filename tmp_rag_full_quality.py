import sys
from collections import defaultdict
sys.path.insert(0, '.')

from e2sc.data.vector_store import reset_vector_store

# -------------------------
# Build full 20-source demo
# -------------------------
knowledge = {
    "genes": {
        "MAPT": {
            "function": "Microtubule-associated protein tau; drives neurofibrillary tangle pathology in Alzheimer disease.",
            "uniprot_accession": "P10636",
            "gene_name": "MAPT",
            "gene_summary": "Tau stabilizes microtubules; hyperphosphorylation causes aggregation.",
            "gene_aliases": ["TAU", "FTDP-17"],
            "pathways": ["Tau pathology", "Neurodegeneration"],
            "go_terms": ["microtubule binding", "axon"],
            "ensembl_id": "ENSG00000186868",
            "description": "Microtubule associated protein tau",
            "chromosome": "17",
            "biotype": "protein_coding",
            "drug_targets": ["GSK3B pathway modulation (CHEMBL210) [drugs: lithium, tideglusib]"],
            "ot_diseases": ["Alzheimer disease (score=0.92, id=EFO_0000249)", "Frontotemporal dementia (score=0.87, id=MONDO_0018076)"],
            "clinvar_variants": ["MAPT p.P301L (Pathogenic)", "MAPT p.R406W (Pathogenic)"],
            "reactome_pathways": ["Axonal growth stimulation (R-HSA-422475)", "Tau protein binding (R-HSA-956581)"],
            "interactions": [{"partner": "GSK3B", "score": 1.0}, {"partner": "CDK5", "score": 0.998}],
            "metabolites": [{"name": "ATP", "protein_type": "substrate"}],
            "tf_targets": [],
            "regulators": [{"tf": "SP1", "effect": "Activation"}],
            "gut_microbes": [{"microbe": "Lactobacillus reuteri", "Alteration": "decreased", "Condition": "Alzheimer disease", "PMID": "11111111"}],
            "gtex_tissues": [{"tissue": "Brain_Hippocampus", "median_expression": 42.3}],
            "humanbase_tissues": [{"tissue": "brain", "score": 0.94}],
            "gwas_snps": [{"trait": "Alzheimer disease", "rsid": "rs63750264", "pvalue": "1.2e-15"}],
            "biogrid_interactions": [{"gene_a": "MAPT", "gene_b": "GSK3B", "experimental_system": "Co-IP", "pmid": "9852110"}],
            "civic_variants": ["MAPT P301L (Pathogenic)"],
            "alliance_homologs": "Mouse: Mapt; Fly: tau; Worm: ptl-1",
        },
        "APOE": {
            "function": "Apolipoprotein E mediates lipid transport and cholesterol metabolism.",
            "uniprot_accession": "P02649",
            "gene_name": "APOE",
            "gene_summary": "APOE epsilon4 is a key risk allele for late-onset Alzheimer disease.",
            "gene_aliases": ["Apo-E"],
            "pathways": ["Lipoprotein metabolism"],
            "go_terms": ["cholesterol transport", "lipoprotein particle binding"],
            "ensembl_id": "ENSG00000130203",
            "description": "Apolipoprotein E",
            "chromosome": "19",
            "biotype": "protein_coding",
            "drug_targets": ["LDLR pathway target class (CHEMBLXXXX) [drugs: statins]"],
            "ot_diseases": ["Alzheimer disease (score=0.683, id=EFO_0000249)"],
            "clinvar_variants": ["APOE e4/e4 (Risk factor)"],
            "reactome_pathways": ["HDL-mediated lipid transport (R-HSA-983705)"],
            "interactions": [{"partner": "LDLR", "score": 0.998}, {"partner": "APOC3", "score": 1.0}],
            "metabolites": [{"name": "Cholesterol", "protein_type": "transport"}],
            "tf_targets": [],
            "regulators": [{"tf": "PPARG", "effect": "Activation"}],
            "gut_microbes": [{"microbe": "Bacteroides", "Alteration": "increased", "Condition": "LOAD", "PMID": "22222222"}],
            "gtex_tissues": [{"tissue": "Liver", "median_expression": 60.1}],
            "humanbase_tissues": [{"tissue": "liver", "score": 0.95}],
            "gwas_snps": [{"trait": "Late-onset AD", "rsid": "rs429358", "pvalue": "2.0e-50"}],
            "biogrid_interactions": [{"gene_a": "APOE", "gene_b": "LDLR", "experimental_system": "Co-IP", "pmid": "19706383"}],
            "civic_variants": ["APOE e4 (Risk biomarker)"],
            "alliance_homologs": "Mouse: Apoe; Zebrafish: apoea",
        },
        "FABP3": {
            "function": "Fatty acid-binding protein 3 transports long-chain fatty acids and acyl-CoA esters.",
            "uniprot_accession": "P05413",
            "gene_name": "FABP3",
            "gene_summary": "Heart-type FABP; associated with lipid metabolism and neuronal energy dysregulation.",
            "gene_aliases": ["H-FABP"],
            "pathways": ["Fatty acid beta-oxidation"],
            "go_terms": ["fatty acid binding"],
            "ensembl_id": "ENSG00000121769",
            "description": "Fatty acid binding protein 3",
            "chromosome": "1",
            "biotype": "protein_coding",
            "drug_targets": ["PPAR signaling modulators (CHEMBL999) [drugs: fenofibrate]"],
            "ot_diseases": ["Myocardial infarction (score=0.54)"],
            "clinvar_variants": ["FABP3 variant of uncertain significance"],
            "reactome_pathways": ["Triglyceride catabolism (R-HSA-75109)", "Fatty acid beta-oxidation (R-HSA-77289)"],
            "interactions": [{"partner": "GOT2", "score": 0.949}],
            "metabolites": [{"name": "Butyryl-CoA", "protein_type": "ligand"}],
            "tf_targets": [],
            "regulators": [{"tf": "PPARA", "effect": "Activation"}],
            "gut_microbes": [{"microbe": "Akkermansia", "Alteration": "decreased", "Condition": "Metabolic syndrome", "PMID": "33333333"}],
            "gtex_tissues": [{"tissue": "Heart_Left_Ventricle", "median_expression": 71.2}],
            "humanbase_tissues": [{"tissue": "heart", "score": 0.91}],
            "gwas_snps": [{"trait": "Coronary artery disease", "rsid": "rs123456", "pvalue": "3.1e-9"}],
            "biogrid_interactions": [{"gene_a": "FABP3", "gene_b": "GOT2", "experimental_system": "Biochemical Activity", "pmid": "15240858"}],
            "civic_variants": ["FABP3 expression biomarker"],
            "alliance_homologs": "Mouse: Fabp3; Rat: Fabp3",
        },
    },
    "pubmed": [
        {"pmid": "38260284", "title": "APOE-dependent AD signatures in serum proteomics", "abstract": "Cross-biofluid evidence for APOE-linked Alzheimer features."},
        {"pmid": "31452104", "title": "Tau phosphorylation and neuroinflammation in AD", "abstract": "Tau kinases and microglia activation cooperate in disease progression."},
    ],
    "europepmc": [
        {"id": "EPMC123456", "title": "Tau and lipid pathways in AD subtypes", "abstractText": "EOAD and LOAD share core neurodegenerative mechanisms."},
    ],
}

EXPECTED_SOURCES = [
    "uniprot", "mygene", "quickgo", "ensembl", "chembl", "opentargets", "clinvar", "reactome", "string",
    "hmdb", "trrust", "gutmgene", "gtex", "humanbase", "gwas", "biogrid", "civic", "alliance", "pubmed", "europepmc"
]

# One probe query per source
probe_queries = {
    "uniprot": "protein function uniprot accession MAPT microtubule associated",
    "mygene": "gene summary alias APOE epsilon4 risk",
    "quickgo": "go annotations microtubule binding axon",
    "ensembl": "ensembl id ENSG00000186868 chromosome biotype",
    "chembl": "chembl drug targets mechanism GSK3B inhibitor",
    "opentargets": "open targets disease association score EFO",
    "clinvar": "clinvar pathogenic variant P301L R406W",
    "reactome": "reactome pathway HDL mediated lipid transport",
    "string": "string interacts with GSK3B confidence",
    "hmdb": "hmdb metabolite cholesterol butyryl coa",
    "trrust": "trrust transcription factor SP1 regulates",
    "gutmgene": "gutmgene microbiota Lactobacillus alteration",
    "gtex": "gtex tissue expression brain hippocampus median TPM",
    "humanbase": "humanbase tissue specific network score",
    "gwas": "gwas trait SNP rs429358 pvalue",
    "biogrid": "biogrid interaction experimental system co-ip",
    "civic": "civic clinical variant biomarker",
    "alliance": "alliance cross species homolog mouse fly worm",
    "pubmed": "pubmed pmid 38260284 APOE dependent",
    "europepmc": "europepmc tau and lipid pathways",
}

vs = reset_vector_store("demo_rag_full_quality")
num_docs = vs.reset_and_build(knowledge)
print(f"Built docs: {num_docs}")

# Coverage check from collection metadata
all_hits = vs.search("alzheimer tau apoe fabp3 pathways interactions lipids", n_results=min(300, vs.count()))
present_sources = sorted(set((h.get('metadata') or {}).get('source', '?') for h in all_hits))
print(f"Active sources in index ({len(present_sources)}/20): {present_sources}")

missing = [s for s in EXPECTED_SOURCES if s not in present_sources]
if missing:
    print(f"MISSING SOURCES: {missing}")

# Retrieval quality evaluation
print("\n=== Retrieval quality per source ===")
summary = []
for src in EXPECTED_SOURCES:
    q = probe_queries[src]
    hits = vs.search(q, n_results=10)
    top_sources = [((h.get('metadata') or {}).get('source', '?')) for h in hits]
    # rank of first correct source hit
    rr = 0.0
    first_rank = None
    for idx, s in enumerate(top_sources, start=1):
        if s == src:
            rr = 1.0 / idx
            first_rank = idx
            break
    top1_ok = (top_sources[0] == src) if top_sources else False
    src_hits = sum(1 for s in top_sources if s == src)
    summary.append((src, top1_ok, first_rank, rr, src_hits, top_sources[:5]))

for src, top1_ok, first_rank, rr, src_hits, top5 in summary:
    print(f"{src:10s} | top1={str(top1_ok):5s} | first_rank={str(first_rank):>2s} | MRR={rr:.3f} | hits@10={src_hits} | top5={top5}")

mean_mrr = sum(x[3] for x in summary) / len(summary)
top1_acc = sum(1 for x in summary if x[1]) / len(summary)
covered = sum(1 for x in summary if x[2] is not None)
print("\n=== Overall ===")
print(f"Top1 accuracy: {top1_acc:.2%}")
print(f"Mean MRR:      {mean_mrr:.3f}")
print(f"Sources retrievable in top10: {covered}/{len(summary)}")
