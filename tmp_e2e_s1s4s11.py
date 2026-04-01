import requests
from collections import Counter

BASE = "http://127.0.0.1:8000"
ALL_APIS = [
    "uniprot","mygene","quickgo","ensembl","chembl","pubmed","europepmc","reactome",
    "gtex","humanbase","gwas","biogrid","civic","alliance","opentargets","clinvar"
]
ALL_DBS = ["string","hmdb","trrust","gutmgene"]
SESSIONS = ["livetest-s1", "livetest-s4", "livetest-s11"]
QUESTIONS = ["最有可能的药物靶点是什么", "最有可能的互作是什么", "综合解读一下"]


def count_sources(progress_lines):
    ok = Counter()
    fail = Counter()
    for ln in progress_lines:
        up = ln.upper()
        for src in ALL_APIS + ALL_DBS:
            k = src.upper()
            if f"[{k}] [OK]" in up:
                ok[src] += 1
            if f"[{k}] [FAIL]" in up:
                fail[src] += 1
    return ok, fail


def configure(session_id):
    payload = {
        "session_id": session_id,
        "group_col": "group",
        "gene_col": "name",
        "expr_type": "log2FC",
        "expr_col": "log2FC",
        "sig_col": "FDR",
        "sig_thresh": 0.05,
        "n_top_genes": 30,
        "enabled_apis": ALL_APIS,
        "enabled_dbs": ALL_DBS,
        "dataset_description": f"reference.h5ad-derived table: {session_id}",
    }
    return requests.post(f"{BASE}/api/configure-csv", json=payload, timeout=120)


def ask(session_id, q):
    return requests.post(f"{BASE}/api/chat", json={"chat_id": session_id, "message": q}, timeout=900)


if __name__ == "__main__":
    print("HEALTH", requests.get(f"{BASE}/api/health", timeout=10).text)

    for sid in SESSIONS:
        print("\n" + "="*80)
        print("SESSION", sid)
        cfg = configure(sid)
        print("configure", cfg.status_code, cfg.text[:200])

        for q in QUESTIONS:
            print("\nQ:", q)
            rr = ask(sid, q)
            print("chat", rr.status_code)
            data = rr.json() if rr.headers.get("content-type", "").startswith("application/json") else {"response": rr.text}
            print("response:", (data.get("response", "") or "")[:320].replace("\n", " "))
            thinking = data.get("thinking", [])
            if thinking:
                print("thinking_tail:", thinking[-3:])

            pg = requests.get(f"{BASE}/api/progress/{sid}", timeout=20).json().get("messages", [])
            ok, fail = count_sources(pg)
            active = sorted([s for s in (ALL_APIS + ALL_DBS) if ok.get(s, 0) > 0])
            print("active_sources", len(active), active)
            f2 = {k: v for k, v in fail.items() if v > 0}
            if f2:
                print("fail_counts", f2)
