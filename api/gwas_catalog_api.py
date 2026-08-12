"""
GWAS Catalog API 调用模块
提供变异-性状关联的大规模 GWAS 证据
API文档: https://www.ebi.ac.uk/gwas/rest/api/v2/docs
v2端点已知: /associations, /studies
"""

import requests
from typing import Dict, Any, List, Optional


class GWASCatalogAPI:
    """GWAS Catalog 数据库 API 接口 (v2)"""

    def __init__(self, email: str = "e2seq@example.com"):
        self.base_url = "https://www.ebi.ac.uk/gwas/rest/api/v2"
        self.email = email
        self.headers = {
            "Accept": "application/json",
            "User-Agent": f"Python/{email}"
        }

    def get_gene_trait_associations(self, gene: str, max_results: int = 20) -> Dict[str, Any]:
        """获取某基因相关的疾病/表型 GWAS 证据"""
        try:
            url = f"{self.base_url}/associations"
            params = {
                "geneSymbol": gene,
                "page": 1,
                "size": min(max_results, 100)
            }

            response = requests.get(url, params=params, headers=self.headers, timeout=30)

            if response.status_code == 200:
                data = response.json()
                assocs = data.get("_embedded", {}).get("associations", [])

                associations = []
                for hit in assocs[:max_results]:
                    if not isinstance(hit, dict):
                        continue

                    efo_traits = hit.get("efo_traits", [])
                    trait_names = []
                    efo_ids = []
                    for t in efo_traits:
                        if isinstance(t, dict):
                            trait_names.append(t.get("efo_trait", ""))
                            efo_ids.append(t.get("efo_id", ""))
                        else:
                            trait_names.append(str(t))

                    associations.append({
                        "gene": gene,
                        "rsID": hit.get("snp_id_current", hit.get("snp_id", "")),
                        "trait": "; ".join(filter(None, trait_names)) or hit.get("reported_trait", ""),
                        "efo_id": "; ".join(filter(None, efo_ids)),
                        "pvalue": hit.get("p_value", None),
                        "beta": hit.get("beta", None),
                        "or_value": hit.get("or_value", None),
                        "ci_lower": hit.get("ci_lower", None),
                        "ci_upper": hit.get("ci_upper", None),
                        "risk_frequency": hit.get("risk_frequency", ""),
                        "study_accession": hit.get("accession_id", ""),
                        "pubmed": hit.get("pubmed_id", ""),
                        "first_author": hit.get("first_author", ""),
                        "snp_allele": f"{hit.get('snp_effect_allele', '')}/{hit.get('snp_allele', '')}",
                    })

                return {
                    "status": "success",
                    "gene": gene,
                    "total": len(associations),
                    "associations": associations,
                    "api_version": "v2"
                }

            return {
                "status": "success",
                "gene": gene,
                "total": 0,
                "associations": [],
                "note": f"GWAS API returned {response.status_code}"
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def search_by_trait(self, trait: str, max_results: int = 20) -> Dict[str, Any]:
        """通过性状/疾病搜索 GWAS 关联"""
        try:
            url = f"{self.base_url}/associations"
            params = {
                "efo_trait": trait,
                "page": 1,
                "size": min(max_results, 100)
            }

            response = requests.get(url, params=params, headers=self.headers, timeout=30)

            if response.status_code == 200:
                data = response.json()
                assocs = data.get("_embedded", {}).get("associations", [])

                associations = []
                for hit in assocs[:max_results]:
                    if not isinstance(hit, dict):
                        continue

                    efo_traits = hit.get("efo_traits", [])
                    mapped_genes = hit.get("mapped_genes", [])

                    associations.append({
                        "rsID": hit.get("snp_id_current", ""),
                        "trait": hit.get("reported_trait", ""),
                        "pvalue": hit.get("p_value", None),
                        "beta": hit.get("beta", None),
                        "or_value": hit.get("or_value", None),
                        "study_accession": hit.get("accession_id", ""),
                        "pubmed": hit.get("pubmed_id", ""),
                        "genes": "; ".join(filter(None, mapped_genes)) if isinstance(mapped_genes, list) else str(mapped_genes),
                    })

                return {
                    "status": "success",
                    "trait": trait,
                    "total": len(associations),
                    "associations": associations,
                    "api_version": "v2"
                }

            return {"status": "success", "trait": trait, "total": 0, "associations": [], "note": f"HTTP {response.status_code}"}

        except Exception as e:
            return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    api = GWASCatalogAPI()

    print("=== Test Gene Search (TP53) ===")
    result = api.get_gene_trait_associations("TP53", max_results=5)
    print(f"Status: {result.get('status')}")
    print(f"API Version: {result.get('api_version', 'unknown')}")
    if result.get("status") == "success":
        print(f"Found {result.get('total')} associations")
        for a in result.get("associations", [])[:3]:
            print(f"  - rsID: {a.get('rsID', 'N/A')}, Trait: {a.get('trait', 'N/A')}, P-value: {a.get('pvalue', 'N/A')}")
    else:
        print(f"Error: {result.get('error')}")
