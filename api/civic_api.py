"""
CIViC API 调用模块
提供癌症变异临床解释知识库
API文档: https://griffithlab.github.io/civic-v2/
GraphQL端点: https://civicdb.org/api/graphql
"""

import requests
from typing import Dict, Any, List, Optional


class CIViCAPI:
    """CIViC (Clinical Interpretations of Variants in Cancer) 数据库 API 接口"""

    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://civicdb.org/api/graphql"
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    def _graphql_query(self, query: str, variables: Dict = None) -> Dict[str, Any]:
        """执行 GraphQL 查询"""
        try:
            payload = {"query": query}
            if variables:
                payload["variables"] = variables

            response = requests.post(
                self.base_url,
                json=payload,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if "errors" in result:
                    return {"status": "error", "error": result["errors"]}
                return {"status": "success", "data": result.get("data", {})}
            else:
                return {"status": "error", "error": f"HTTP {response.status_code}: {response.text[:200]}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def search_variants(self, gene: str, max_results: int = 20) -> Dict[str, Any]:
        """搜索基因相关的变异（使用 genes(entrezSymbols) + variants.nodes）"""
        query = """
        query SearchGeneVariants($geneSymbol: String!) {
          genes(entrezSymbols: [$geneSymbol]) {
            nodes {
              id
              name
              entrezId
              description
              variants {
                totalCount
                nodes {
                  id
                  name
                  variantTypes { name }
                  singleVariantMolecularProfileId
                }
              }
            }
          }
        }
        """

        result = self._graphql_query(query, {"geneSymbol": gene})

        if result.get("status") != "success":
            return result

        genes_data = result.get("data", {}).get("genes", {}).get("nodes", [])
        if not genes_data:
            return {"status": "success", "gene": gene, "total": 0, "variants": []}

        gene_node = genes_data[0]
        variants_data = gene_node.get("variants", {})
        variant_nodes = variants_data.get("nodes", [])

        variants = []
        for v in variant_nodes[:max_results]:
            if not isinstance(v, dict):
                continue
            types = v.get("variantTypes", [])
            if isinstance(types, list):
                type_names = [t.get("name", "") for t in types if isinstance(t, dict)]
            else:
                type_names = []

            variants.append({
                "id": v.get("id"),
                "name": v.get("name", ""),
                "gene": gene,
                "gene_id": gene_node.get("id"),
                "entrez_id": gene_node.get("entrezId"),
                "variant_types": type_names,
                "molecular_profile_id": v.get("singleVariantMolecularProfileId"),
            })

        return {
            "status": "success",
            "gene": gene,
            "total": len(variants),
            "total_in_db": variants_data.get("totalCount", len(variants)),
            "variants": variants
        }

    def get_variant_evidence(self, variant_id: int) -> Dict[str, Any]:
        """获取变异的临床证据"""
        # 先获取变异基本信息
        query_var = """
        query VariantInfo($id: Int!) {
          variant(id: $id) {
            id
            name
            variantTypes { name }
            singleVariantMolecularProfile { id name }
          }
        }
        """
        result_var = self._graphql_query(query_var, {"id": variant_id})

        if result_var.get("status") != "success":
            return result_var

        var_data = result_var.get("data", {}).get("variant", {})
        if not var_data:
            return {"status": "error", "error": f"Variant {variant_id} not found"}

        mp_id = var_data.get("singleVariantMolecularProfile", {})
        mp_id_val = mp_id.get("id") if isinstance(mp_id, dict) else None
        mp_name = mp_id.get("name", "") if isinstance(mp_id, dict) else ""

        # 通过 molecularProfiles 获取 evidence
        query_ev = """
        query VariantEvidence($mpId: Int!) {
          molecularProfile(id: $mpId) {
            id
            name
            evidenceItems {
              nodes {
                id
                evidenceType
                significance
                evidenceLevel
                disease { name }
                therapies { name }
                description
                source { citation }
              }
            }
          }
        }
        """

        evidence = []
        if mp_id_val:
            result_ev = self._graphql_query(query_ev, {"mpId": mp_id_val})
            if result_ev.get("status") == "success":
                ev_data = result_ev.get("data", {}).get("molecularProfile", {}).get("evidenceItems", {}).get("nodes", [])
                for e in ev_data:
                    if not isinstance(e, dict):
                        continue
                    therapies = e.get("therapies", [])
                    if isinstance(therapies, list):
                        drug_names = [d.get("name", "") for d in therapies if isinstance(d, dict)]
                    else:
                        drug_names = []

                    evidence.append({
                        "id": e.get("id"),
                        "type": e.get("evidenceType", ""),
                        "clinical_significance": e.get("significance", ""),
                        "disease": e.get("disease", {}).get("name", "") if isinstance(e.get("disease"), dict) else "",
                        "drugs": drug_names,
                        "evidence_level": e.get("evidenceLevel", ""),
                        "description": e.get("description", ""),
                        "pmid": e.get("source", {}).get("citation", "") if isinstance(e.get("source"), dict) else "",
                    })

        return {
            "status": "success",
            "variant_id": variant_id,
            "variant_name": var_data.get("name", ""),
            "molecular_profile": mp_name,
            "molecular_profile_id": mp_id_val,
            "variant_types": [t.get("name", "") for t in var_data.get("variantTypes", []) if isinstance(t, dict)],
            "total_evidence": len(evidence),
            "evidence": evidence
        }

    def get_gene_variants(self, gene: str) -> Dict[str, Any]:
        """获取基因的所有变异"""
        return self.search_variants(gene, max_results=50)


if __name__ == "__main__":
    api = CIViCAPI()

    print("=== 测试基因变异 (EGFR) ===")
    result = api.search_variants("EGFR", max_results=10)
    print(f"Status: {result.get('status')}, Total: {result.get('total')}")
    if result.get("status") == "success":
        for v in result.get("variants", [])[:5]:
            print(f"  - {v['name']}: {v.get('variant_types', [])}")
    else:
        print(f"Error: {result.get('error')}")

    # 测试变异证据
    print("\n=== 测试变异证据 (EGFR L858R, id=1499) ===")
    result2 = api.get_variant_evidence(1499)
    print(f"Status: {result2.get('status')}, Evidence: {result2.get('total_evidence')}")
    if result2.get("status") == "success":
        for e in result2.get("evidence", [])[:3]:
            print(f"  - {e['type']}: {e['clinical_significance']} | {e['disease']} | Drugs: {e['drugs']}")
