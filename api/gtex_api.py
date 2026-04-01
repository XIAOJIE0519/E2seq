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
        """获取基因在各组织的表达数据"""
        try:
            # Step 1: resolve gene symbol -> gencodeId
            ref_url = f"{self.base_url}/reference/gene"
            ref_r = requests.get(ref_url, params={"geneId": gene}, headers=self.headers, timeout=20)
            gencode_id = None
            if ref_r.status_code == 200:
                ref_data = ref_r.json().get("data", [])
                if ref_data:
                    gencode_id = ref_data[0].get("gencodeId", "")

            if not gencode_id:
                return {"status": "success", "gene": gene, "total": 0, "records": [], "note": "Gene not found in GTEx reference"}

            # Step 2: get median expression per tissue
            expr_url = f"{self.base_url}/expression/medianGeneExpression"
            response = requests.get(
                expr_url,
                params={"gencodeId": gencode_id, "datasetId": "gtex_v8"},
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                raw = data.get("data", [])
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
                # sort by expression descending
                records.sort(key=lambda x: x.get("median_expression") or 0, reverse=True)
                return {
                    "status": "success",
                    "gene": gene,
                    "gencodeId": gencode_id,
                    "total": len(records),
                    "records": records
                }

            return {
                "status": "success",
                "gene": gene,
                "total": 0,
                "records": [],
                "note": f"GTEx returned {response.status_code}"
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}


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
