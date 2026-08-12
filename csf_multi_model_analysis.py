# -*- coding: utf-8 -*-
r"""
CSF Proteomics Multi-Model Analysis Pipeline
=============================================
Cross-model comparison of LLM conclusions for CSF proteomics data
(EOAD vs LOAD) via SiliconFlow API.

Questions:
  Q1. EOAD & LOAD protein-protein interaction pairs (top-3 each)
  Q2. EOAD & LOAD drug target proteins & corresponding drugs (top-3 each)

Datasets (S1, S4, S11) and Models (DeepSeek, GLM, Qwen):
  2 questions × 3 datasets × 3 models = 18 total results

API: SiliconFlow (https://api.siliconflow.cn)
  Models:
    DeepSeek: deepseek-ai/DeepSeek-V3-0324
    GLM:      THUDM/GLM-4-Flash
    Qwen:     Qwen/Qwen2.5-7B-Instruct

Output:
  - CSF_Proteomics_Q1_PPI.csv
  - CSF_Proteomics_Q2_Drug.csv

Python: the selected environment / 使用当前选择的 Python 环境
"""

import os
import sys
import csv
import json
import time
import requests
import traceback
import concurrent.futures
from pathlib import Path

# ── UTF-8 ─────────────────────────────────────────────────────────────────────
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

# ── PATHS ─────────────────────────────────────────────────────────────────────
BASE_DIR  = Path(os.environ.get("E2SEQ_PROJECT_ROOT", Path(__file__).resolve().parent)).resolve()
OUT_DIR   = BASE_DIR / "analysis_output"
OUT_DIR.mkdir(exist_ok=True)

S1_PATH   = BASE_DIR / "S1.csv"
S4_PATH   = BASE_DIR / "S4.csv"
S11_PATH  = BASE_DIR / "S11.csv"

API_KEY   = os.environ.get("SILICONFLOW_API_KEY", "")
API_BASE  = "https://api.siliconflow.cn/v1"

LOG_FC_THR = 0.2
FDR_THR    = 0.05

# ── MODEL CONFIG ─────────────────────────────────────────────────────────────
MODELS = {
    "DeepSeek": "deepseek-ai/DeepSeek-V3-0324",
    "GLM":      "THUDM/GLM-4-Flash",
    "Qwen":     "Qwen/Qwen2.5-7B-Instruct",
}

# DATA LOADING / 数据读取
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


# ── PREPARE PROTEIN TABLE FOR PROMPTS ─────────────────────────────────────────
def build_protein_table(sig_list, max_rows=20):
    """Build a markdown table of significant proteins."""
    lines = [
        "| Rank | Protein | log2FC | FDR |",
        "|------|---------|--------|-----|"
    ]
    for i, p in enumerate(sig_list[:max_rows], 1):
        fdr_str = f"{p['FDR']:.2e}" if p['FDR'] < 0.001 else f"{p['FDR']:.4f}"
        fc_str  = f"{p['log2FC']:+.4f}"
        lines.append(f"| {i} | **{p['name']}** | {fc_str} | {fdr_str} |")
    total = len(sig_list)
    if total > max_rows:
        lines.append(f"| ... | (showing top {max_rows} of {total} significant proteins) | | |")
    return "\n".join(lines)


# ── SYSTEM PROMPTS ─────────────────────────────────────────────────────────────
SYS_PROMPT_Q1 = """You are an expert in Alzheimer's disease proteomics and protein-protein interaction (PPI) network biology.

TASK: From the differential expression table provided below, identify the most likely strong protein-protein interaction (PPI) pairs for EOAD (Early-Onset Alzheimer's Disease) and LOAD (Late-Onset Alzheimer's Disease).

METHODOLOGY:
1. Focus on proteins with |log2FC| > 0.2 AND FDR < 0.05 (already pre-filtered in the table).
2. Prioritize protein pairs where BOTH partners are significantly changed and in the SAME direction (both up- or both down-regulated), as these are more likely to form functional co-regulated modules.
3. Prefer known AD-relevant proteins: glycolytic enzymes (ALDOA, ENO2, LDHB, PGK1, GPI, PKM), 14-3-3 proteins (YWHAZ, YWHAG), synaptic proteins (NRXN1, NRXN2, CNTN2, NFASC, NCAM1, NRCAM), complement proteins (C1S, CFB, C1QA), apolipoproteins (APOA1, APOC1, APOC3, APOE), ECM proteins (COL1A1, COL3A1, LAMB1, SPARC, DCN), neuroinflammatory markers (CHI3L1, A2M, VTN), and neurodegenerative markers (MAPT, GAP43, UCHL1, NEFL).
4. Rank by absolute log2FC magnitude. For STRING-db-known interactors, prefer those with higher confidence.
5. Output exactly 3 EOAD pairs and 3 LOAD pairs.

OUTPUT FORMAT (strict JSON array, no extra text):
[
  {
    "dataset": "<S1/S4/S11>",
    "model": "<model_name>",
    "cohort": "EOAD",
    "pairs": [
      {"rank": 1, "protein_A": "GENE_NAME", "protein_B": "GENE_NAME", "log2FC_A": +X.XXXX, "log2FC_B": +X.XXXX, "rationale": "1-2 sentence biological rationale"},
      {"rank": 2, "protein_A": "...", "protein_B": "...", "log2FC_A": +X.XXXX, "log2FC_B": +X.XXXX, "rationale": "..."},
      {"rank": 3, "protein_A": "...", "protein_B": "...", "log2FC_A": +X.XXXX, "log2FC_B": +X.XXXX, "rationale": "..."}
    ]
  },
  {
    "dataset": "<S1/S4/S11>",
    "model": "<model_name>",
    "cohort": "LOAD",
    "pairs": [
      {"rank": 1, "protein_A": "GENE_NAME", "protein_B": "GENE_NAME", "log2FC_A": +X.XXXX, "log2FC_B": +X.XXXX, "rationale": "..."},
      {"rank": 2, "protein_A": "...", "protein_B": "...", "log2FC_A": +X.XXXX, "log2FC_B": +X.XXXX, "rationale": "..."},
      {"rank": 3, "protein_A": "...", "protein_B": "...", "log2FC_A": +X.XXXX, "log2FC_B": +X.XXXX, "rationale": "..."}
    ]
  }
]
"""


SYS_PROMPT_Q2 = """You are an expert in Alzheimer's disease pharmacology and drug target prioritization.

TASK: From the differential expression table provided below, identify the most promising drug target proteins for EOAD (Early-Onset Alzheimer's Disease) and LOAD (Late-Onset Alzheimer's Disease), and name the corresponding drugs acting on those targets.

METHODOLOGY:
1. Focus on proteins with |log2FC| > 0.2 AND FDR < 0.05 (already pre-filtered in the table).
2. Prioritize proteins that are established AD drug targets with drugs in clinical development (Phase 1-4). Preferred target families include: secretases (BACE1, BACE2, PSEN1, PSEN2, ACHE), kinases (GSK3B, CDK5, CDK5R1, MAPT, MAP2), neurotrophic factors (BDNF, NTRK2, GFRA2), neuroinflammation targets (IL6, IL1B, TNF, CXCL8, CHI3L1, A2M, C1S), amyloid-related (APP, APOE, CLU, PSEN1, PSEN2), lipid metabolism (APOA1, APOC1, APOC3, APOE, CETP, PON1), synaptic (ACHE, CAMK2A, GRIN2B, BDNF, NTRK2), and metabolic enzymes with available inhibitors (ALDOA, ENO2, LDHB, PGK1, HSP90AA1, HDAC6).
3. For each selected target, name at least one drug (generic name preferred; brand name acceptable) that acts on that target. Include the clinical development phase if known.
4. Prefer targets with drugs that have reached at least Phase 2 (or have strong preclinical validation).
5. Output exactly 3 EOAD targets and 3 LOAD targets.

OUTPUT FORMAT (strict JSON array, no extra text):
[
  {
    "dataset": "<S1/S4/S11>",
    "model": "<model_name>",
    "cohort": "EOAD",
    "targets": [
      {"rank": 1, "protein": "GENE_NAME", "log2FC": +X.XXXX, "FDR": X.XXe-XX, "target_name": "Full target protein name", "drug_name": "Drug generic name", "phase": "Phase X or Preclinical", "rationale": "1-2 sentence biological and therapeutic rationale"},
      {"rank": 2, "protein": "...", "log2FC": +X.XXXX, "FDR": X.XXe-XX, "target_name": "...", "drug_name": "...", "phase": "...", "rationale": "..."},
      {"rank": 3, "protein": "...", "log2FC": +X.XXXX, "FDR": X.XXe-XX, "target_name": "...", "drug_name": "...", "phase": "...", "rationale": "..."}
    ]
  },
  {
    "dataset": "<S1/S4/S11>",
    "model": "<model_name>",
    "cohort": "LOAD",
    "targets": [
      {"rank": 1, "protein": "GENE_NAME", "log2FC": +X.XXXX, "FDR": X.XXe-XX, "target_name": "Full target protein name", "drug_name": "Drug generic name", "phase": "Phase X or Preclinical", "rationale": "..."},
      {"rank": 2, "protein": "...", "log2FC": +X.XXXX, "FDR": X.XXe-XX, "target_name": "...", "drug_name": "...", "phase": "...", "rationale": "..."},
      {"rank": 3, "protein": "...", "log2FC": +X.XXXX, "FDR": X.XXe-XX, "target_name": "...", "drug_name": "...", "phase": "...", "rationale": "..."}
    ]
  }
]
"""


# ── SILICONFLOW API CALL ───────────────────────────────────────────────────────
def call_siliconflow(model_id: str, system_prompt: str, user_prompt: str,
                     max_tokens: int = 2048) -> str:
    """Call SiliconFlow chat API and return the assistant's message."""
    url = f"{API_BASE}/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        "temperature": 0.3,
        "max_tokens":  max_tokens,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    if resp.status_code != 200:
        raise RuntimeError(
            f"SiliconFlow API error {resp.status_code}: {resp.text[:500]}"
        )
    data = resp.json()
    return data["choices"][0]["message"]["content"]


# ── USER PROMPTS BUILDER ────────────────────────────────────────────────────────
def build_user_prompt_q1(sig_eoad, sig_load, dataset):
    return f"""DIFFERENTIAL EXPRESSION DATA — Dataset {dataset}
===========================================================
Filtering: |log2FC| > {LOG_FC_THR} AND FDR < {FDR_THR}
Direction: positive log2FC = upregulated in disease vs control; negative = downregulated

--- EOAD Significant Proteins ---
{sig_eoad}

--- LOAD Significant Proteins ---
{sig_load}

TASK: Identify 3 top EOAD PPI pairs and 3 top LOAD PPI pairs.
Return ONLY a JSON array following the system format. No markdown fences, no extra text.
"""


def build_user_prompt_q2(sig_eoad, sig_load, dataset):
    return f"""DIFFERENTIAL EXPRESSION DATA — Dataset {dataset}
===========================================================
Filtering: |log2FC| > {LOG_FC_THR} AND FDR < {FDR_THR}
Direction: positive log2FC = upregulated in disease vs control; negative = downregulated

--- EOAD Significant Proteins ---
{sig_eoad}

--- LOAD Significant Proteins ---
{sig_load}

TASK: Identify 3 top EOAD drug targets and 3 top LOAD drug targets with drug names.
Return ONLY a JSON array following the system format. No markdown fences, no extra text.
"""


# ── RESULT PARSING ─────────────────────────────────────────────────────────────
def extract_json(text: str):
    """Extract JSON array from LLM response, stripping markdown fences if present."""
    text = text.strip()
    if text.startswith("```"):
        # Strip markdown code fences
        for line in text.splitlines():
            stripped = line.strip().strip("`")
            if stripped.startswith("json"):
                continue
            if stripped.startswith("["):
                text = stripped
                break
            if stripped.startswith("{"):
                text = stripped
                break
    # Find the first [ or {
    start = next((i for i, c in enumerate(text) if c in "[{"), None)
    end   = next((len(text) - 1 - i for i, c in enumerate(reversed(text)) if c in "]}"), None)
    if start is not None and end is not None:
        text = text[start:end + 1]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find the array manually
        start = text.find("[")
        if start != -1:
            depth = 0
            for i, c in enumerate(text[start:], start):
                if c == "[": depth += 1
                elif c == "]": depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i + 1])
                    except json.JSONDecodeError:
                        pass
        raise ValueError(f"Cannot parse JSON from response:\n{text[:1000]}")


# ── WORKER: single dataset × model ─────────────────────────────────────────────
def worker(q_num, dataset, model_name, model_id, sig_eoad, sig_load):
    """Run one model on one dataset for one question. Returns parsed JSON."""
    label = f"{dataset}/{model_name}/Q{q_num}"
    print(f"  ▶ {label}")
    t0 = time.time()

    if q_num == 1:
        sys_p  = SYS_PROMPT_Q1
        build  = lambda: build_user_prompt_q1(sig_eoad, sig_load, dataset)
    else:
        sys_p  = SYS_PROMPT_Q2
        build  = lambda: build_user_prompt_q2(sig_eoad, sig_load, dataset)

    user_p = build()
    raw    = call_siliconflow(model_id, sys_p, user_p)
    parsed = extract_json(raw)
    elapsed = time.time() - t0
    print(f"  ✓ {label} ({elapsed:.1f}s)")
    return q_num, dataset, model_name, parsed, raw


# ── MAIN PIPELINE ───────────────────────────────────────────────────────────────
def main():
    print("=" * 65)
    print("CSF Proteomics Multi-Model Analysis Pipeline")
    print("Questions: Q1 (PPI) | Q2 (Drug Targets)")
    print("Models:    DeepSeek | GLM | Qwen")
    print("Datasets:  S1 | S4 | S11")
    print("=" * 65)
    print()

    # ── Step 1: Load data ─────────────────────────────────────────────────────
    print("[Step 1] Loading CSV datasets ...")
    datasets = {}
    for label, path in [("S1", S1_PATH), ("S4", S4_PATH), ("S11", S11_PATH)]:
        rows      = load_csv(path)
        sig_eoad  = rank_proteins(sig_proteins(rows, "EOAD"))
        sig_load  = rank_proteins(sig_proteins(rows, "LOAD"))
        datasets[label] = {
            "EOAD": sig_eoad,
            "LOAD": sig_load,
            "table_EOAD": build_protein_table(sig_eoad, max_rows=20),
            "table_LOAD": build_protein_table(sig_load, max_rows=20),
        }
        print(f"  [{label}] EOAD: {len(sig_eoad)} sig. | LOAD: {len(sig_load)} sig.")
    print()

    # ── Step 2: Collect all tasks ─────────────────────────────────────────────
    print("[Step 2] Building task queue ...")
    tasks = []
    for label, data in datasets.items():
        for model_name, model_id in MODELS.items():
            for q_num in (1, 2):
                tasks.append((q_num, label, model_name, model_id,
                              data["table_EOAD"], data["table_LOAD"]))
    print(f"  Total tasks: {len(tasks)}")
    print()

    # ── Step 3: Execute in parallel ──────────────────────────────────────────
    print("[Step 3] Executing model queries ...")
    t0 = time.time()
    results_raw = {}  # (q_num, dataset, model_name) -> (parsed, raw)
    results_err = []

    def safe_worker(args):
        q_num, dataset, model_name, model_id, table_eoad, table_load = args
        try:
            return worker(q_num, dataset, model_name, model_id, table_eoad, table_load)
        except Exception as exc:
            print(f"  ✗ {dataset}/{model_name}/Q{q_num} FAILED: {exc}")
            return (q_num, dataset, model_name, None, str(exc))

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        futures = [ex.submit(safe_worker, t) for t in tasks]
        for fut in concurrent.futures.as_completed(futures):
            q_num, dataset, model_name, parsed, raw = fut.result()
            key = (q_num, dataset, model_name)
            results_raw[key] = (parsed, raw)

    print(f"  All queries completed in {time.time()-t0:.1f}s")
    print()

    # ── Step 4: Write Q1 CSV (PPI) ────────────────────────────────────────────
    print("[Step 4] Writing output CSV files ...")
    q1_rows = [
        ["Dataset", "Model", "Cohort", "Rank",
         "Protein_A", "log2FC_A",
         "Protein_B", "log2FC_B",
         "Rationale"]
    ]
    q2_rows = [
        ["Dataset", "Model", "Cohort", "Rank",
         "Protein", "log2FC", "FDR",
         "Target_Name", "Drug_Name", "Phase", "Rationale"]
    ]

    for (q_num, dataset, model_name), (parsed, raw) in results_raw.items():
        if parsed is None:
            continue
        try:
            # Find the right entry in the parsed list
            for entry in parsed:
                if entry.get("dataset") == dataset and entry.get("model") == model_name:
                    cohort = entry.get("cohort", "")
                    if q_num == 1:
                        for p in entry.get("pairs", []):
                            q1_rows.append([
                                dataset, model_name, cohort,
                                p.get("rank", ""),
                                p.get("protein_A", ""),
                                str(p.get("log2FC_A", "")),
                                p.get("protein_B", ""),
                                str(p.get("log2FC_B", "")),
                                p.get("rationale", ""),
                            ])
                    else:
                        for t in entry.get("targets", []):
                            q2_rows.append([
                                dataset, model_name, cohort,
                                t.get("rank", ""),
                                t.get("protein", ""),
                                str(t.get("log2FC", "")),
                                str(t.get("FDR", "")),
                                t.get("target_name", ""),
                                t.get("drug_name", ""),
                                t.get("phase", ""),
                                t.get("rationale", ""),
                            ])
                    break
        except Exception as exc:
            print(f"  Warning: error processing {dataset}/{model_name}/Q{q_num}: {exc}")

    # ── Write CSV files ───────────────────────────────────────────────────────
    def write_csv(path, rows):
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            for row in rows:
                writer.writerow(row)
        print(f"  ✓ {path.name}: {len(rows)-1} result rows")

    q1_path = OUT_DIR / "CSF_Proteomics_Q1_PPI.csv"
    q2_path = OUT_DIR / "CSF_Proteomics_Q2_Drug.csv"

    write_csv(q1_path, q1_rows)
    write_csv(q2_path, q2_rows)

    # ── Write raw JSON log for reproducibility ─────────────────────────────────
    raw_log_path = OUT_DIR / "model_raw_responses.json"
    raw_log = {}
    for key, (parsed, raw) in results_raw.items():
        k = f"Q{key[0]}_{key[1]}_{key[2]}"
        raw_log[k] = {"parsed": parsed, "raw": raw[:2000] if isinstance(raw, str) else raw}
    with open(raw_log_path, "w", encoding="utf-8") as f:
        json.dump(raw_log, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Raw response log: {raw_log_path.name}")

    print()
    print("=" * 65)
    print("Pipeline complete!")
    print(f"  Q1 PPI CSV:     {q1_path}")
    print(f"  Q2 Drug CSV:    {q2_path}")
    print(f"  Raw log:        {raw_log_path}")
    print("=" * 65)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
