import json
import time
import requests

BASE = "http://127.0.0.1:8000"

ALL_APIS = [
    "uniprot","mygene","quickgo","ensembl","chembl","pubmed","europepmc",
    "reactome","gtex","humanbase","gwas","biogrid","civic","alliance",
    "opentargets","clinvar",
]
ALL_DBS = ["string","hmdb","trrust","gutmgene"]

SESSIONS = ["livetest-s1", "livetest-s4", "livetest-s11"]
PROMPTS = [
    "最有可能的药物靶点是什么",
    "最有可能的互作是什么",
    "综合解读一下",
]


def configure_csv(session_id: str):
    payload = {
        "session_id": session_id,
        "group_col": "group",
        "gene_col": "name",
        "expr_type": "log2FC",
        "expr_col": "log2FC",
        "sig_col": "FDR",
        "sig_thresh": 1.0,
        "n_top_genes": 66,
        "enabled_apis": ALL_APIS,
        "enabled_dbs": ALL_DBS,
        "dataset_description": f"Reference subset {session_id} from reference.h5ad",
    }
    r = requests.post(f"{BASE}/api/configure-csv", json=payload, timeout=120)
    return r.status_code, r.text


def do_chat(session_id: str, message: str):
    payload = {"chat_id": session_id, "message": message}
    t0 = time.time()
    r = requests.post(f"{BASE}/api/chat", json=payload, timeout=600)
    dt = time.time() - t0
    return r.status_code, r.json() if r.headers.get("content-type", "").startswith("application/json") else {"raw": r.text}, dt


def get_progress(session_id: str):
    try:
        r = requests.get(f"{BASE}/api/progress/{session_id}", timeout=20)
        if r.status_code == 200:
            return r.json().get("messages", [])
    except Exception:
        pass
    return []


def main():
    print("== Health ==")
    print(requests.get(f"{BASE}/api/health", timeout=10).text)

    summary = []

    for sid in SESSIONS:
        print(f"\n=== CONFIGURE {sid} ===")
        code, txt = configure_csv(sid)
        print(code, txt[:500])
        if code != 200:
            summary.append({"session": sid, "error": f"configure failed: {code}"})
            continue

        for q in PROMPTS:
            print(f"\n--- CHAT [{sid}] {q} ---")
            code, data, dt = do_chat(sid, q)
            print("status:", code, "time_s:", round(dt, 1))
            if code != 200:
                print(str(data)[:800])
                summary.append({"session": sid, "q": q, "ok": False, "error": str(data)[:500]})
                continue

            thinking = data.get("thinking", [])
            think_steps = [f"{x.get('step')}={x.get('content')}" for x in thinking[:8]]
            print("thinking_steps:")
            for s in think_steps:
                print("  -", s[:220])

            resp = data.get("response", "")
            print("response_preview:", resp[:260].replace("\n", " "))

            prog = get_progress(sid)
            prog_tail = prog[-12:] if prog else []
            print("progress_tail:")
            for p in prog_tail:
                print("  *", p[:220])

            summary.append({
                "session": sid,
                "q": q,
                "ok": True,
                "time_s": round(dt, 2),
                "thinking": think_steps,
                "response_preview": resp[:320],
                "progress_tail": prog_tail,
            })

    print("\n=== SUMMARY JSON ===")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
