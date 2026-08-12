"""
GTEx API 调用模块
提供基因在各组织的表达数据
API文档: https://gtexportal.org/api/v2/docs
"""

import requests
from typing import Dict, Any, List, Optional


class GTExAPI:
    """GTEx Portal API v2 接口"""

    def __init__(self):
        self.base_url = "https://gtexportal.org/api/v2"
        self.headers = {"Accept": "application/json"}

    def get_gene_expression(self, gene: str, max_results: int = 50) -> Dict[str, Any]:
        """Get gene tissue expression from GTEx Portal v2 API.

        Uses a two-step process:
        1. Resolve gene symbol -> gencodeId via /reference/gene
        2. Fetch median expression per tissue via /expression/medianGeneExpression

        Falls back to MyGene.info expression data if GTEx API is unavailable.
        Timeout: 10s per step to avoid blocking concurrent requests.
        """
        # Use the verified GTEx-only adapter.  The historical fallback below
        # labelled HPA/MyGene records as GTEx, which made source audits false.
        from e2seq.data.knowledge_sources import KnowledgeSourceClient
        verified = KnowledgeSourceClient(timeout=20).query_gtex(gene, max_results=max_results)
        return {
            "status": "success" if verified.get("status") == "ok" else verified.get("status", "error"),
            "gene": gene,
            "gencodeId": (verified.get("fields") or {}).get("gencode_id", ""),
            "total": verified.get("count", 0),
            "records": verified.get("records", []),
            "error": verified.get("error", ""),
        }
        # ── Primary: GTEx Portal v2 ───────────────────────────────────────────
        try:
            # Step 1: resolve gene symbol -> gencodeId
            ref_url = f"{self.base_url}/reference/gene"
            ref_r = requests.get(
                ref_url,
                params={"geneId": gene},
                headers=self.headers,
                timeout=8
            )
            gencode_id = None
            if ref_r.status_code == 200:
                ref_data = ref_r.json().get("data", [])
                if ref_data:
                    gencode_id = ref_data[0].get("gencodeId", "")

            if not gencode_id:
                raise ValueError(f"No gencodeId for {gene}")

            # Step 2: get median expression per tissue
            expr_url = f"{self.base_url}/expression/medianGeneExpression"
            response = requests.get(
                expr_url,
                params={"gencodeId": gencode_id, "datasetId": "gtex_v8"},
                headers=self.headers,
                timeout=8
            )

            if response.status_code == 200:
                data = response.json()
                raw = data.get("data", [])
                if raw:
                    records = []
                    for hit in raw[:max_results]:
                        if not isinstance(hit, dict):
                            continue
                        records.append({
                            "gene": gene,
                            "tissue": hit.get("tissueSiteDetailId", ""),
                            "median_expression": hit.get("median", None),
                            "unit": hit.get("unit", "TPM")
                        })
                    records.sort(key=lambda x: x.get("median_expression") or 0, reverse=True)
                    return {
                        "status": "success",
                        "gene": gene,
                        "gencodeId": gencode_id,
                        "total": len(records),
                        "records": records
                    }
        except Exception:
            pass  # Fall through to fallbacks

        # ── Fallback 1: Human Protein Atlas ───────────────────────────────────
        try:
            hpa_r = requests.get(
                f"https://www.proteinatlas.org/{gene}/tissue.json",
                timeout=10,
            )
            if hpa_r.status_code == 200:
                data = hpa_r.json()
                tissues = []
                for entry in data.get("tissueExpression", {}).get("data", [])[:max_results]:
                    tissue = entry.get("tissue", "")
                    level = entry.get("level", "")
                    nxp = entry.get("nx", "")
                    if tissue:
                        label = f"{tissue}"
                        if level: label += f" ({level})"
                        if nxp: label += f" [{nxp}]"
                        tissues.append(label)
                if tissues:
                    return {
                        "status": "success",
                        "gene": gene,
                        "source": "Human Protein Atlas",
                        "total": len(tissues),
                        "records": [{"gene": gene, "tissue": t} for t in tissues]
                    }
        except Exception:
            pass

        # ── Fallback 2: MyGene.info expression field ──────────────────────────
        try:
            mg_r = requests.get(
                "https://mygene.info/v3/query",
                params={
                    "q": f"symbol:{gene} AND species:human",
                    "fields": "symbol,summary,go,pathway,expression"
                },
                headers={"Accept": "application/json"},
                timeout=8
            )
            if mg_r.status_code == 200:
                mg_data = mg_r.json()
                hits = mg_data.get("hits", [])
                if hits:
                    hit = hits[0]
                    expr = hit.get("expression", {})
                    tissues = []
                    if isinstance(expr, dict):
                        for src, tissues_list in expr.items():
                            if isinstance(tissues_list, list):
                                for t_item in tissues_list[:3]:
                                    tissue = t_item.get("tissue", src)
                                    val = t_item.get("value", "")
                                    tissues.append(f"{tissue}: {val}" if val else tissue)
                    elif isinstance(expr, list):
                        for t_item in expr[:10]:
                            tissue = t_item.get("tissue", "")
                            val = t_item.get("value", "")
                            tissues.append(f"{tissue}: {val}" if val else tissue)
                    return {
                        "status": "success",
                        "gene": gene,
                        "source": "MyGene.info",
                        "total": len(tissues),
                        "records": [{"gene": gene, "tissue": t} for t in tissues[:max_results]]
                    }
        except Exception:
            pass

        return {
            "status": "success",
            "gene": gene,
            "total": 0,
            "records": [],
            "note": "No expression data available (GTEx + HPA + MyGene all unavailable)"
        }


if __name__ == "__main__":
    api = GTExAPI()

    print("=== Test Gene Expression (TP53) ===")
    result = api.get_gene_expression("TP53")
    print(f"Status: {result.get('status')}")
    if result.get("status") == "success":
        print(f"Found {result.get('total')} tissue records")
        for r in result.get("records", [])[:5]:
            print(f"  - {r.get('tissue', r.get('tissue_id'))}: {r.get('median_expression')} TPM")
    else:
        print(f"Error: {result.get('error')}")
