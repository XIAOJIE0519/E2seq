"""
BioGRID API 调用模块
提供实验验证的蛋白互作、遗传互作、化学互作和 PTM 数据
API文档: https://wiki.thebiogrid.org/
注意: BioGRID WebService 需要注册获取 accessKey，免费 Demo 用 "biological"
      API Key 优先级: 参数 > 环境变量 E2SC_BIOGRID_API_KEY > 内置 key
"""

import os
import requests
from typing import Dict, Any, List, Optional


class BioGRIDAPI:
    """BioGRID 数据库 API 接口"""

    # 保留项目原 key 作为 fallback 默认值（用户可通过 E2SC_BIOGRID_API_KEY 替换）
    _DEFAULT_KEY = "1647cceb86ebd3fb64caf6e20048e6bc"

    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://webservice.thebiogrid.org"
        env_key = os.environ.get("E2SC_BIOGRID_API_KEY", "")
        if api_key is not None:
            self.api_key = api_key
        elif env_key:
            self.api_key = env_key
        else:
            self.api_key = self._DEFAULT_KEY

    def get_interactions(
        self,
        genes: List[str],
        max_results: int = 100,
        interactor_type: str = "all"
    ) -> Dict[str, Any]:
        """获取蛋白互作网络"""
        try:
            url = f"{self.base_url}/interactions"
            
            params = {
                "accessKey": self.api_key,
                "geneList": "|".join(genes),
                "organism": "9606",  # Human
                "max": min(max_results, 10000),
                "format": "json",
                "interSpeciesExclusion": "false",
                "showInteractors": "true"
            }
            
            if interactor_type == "protein":
                params["interactorType"] = "protein"
            elif interactor_type == "genetic":
                params["interactorType"] = "genetic"
            
            response = requests.get(url, params=params, timeout=60)
            
            if response.status_code == 401:
                return {
                    "status": "error",
                    "error": "BioGRID requires a valid API key. Register at: https://webservice.thebiogrid.org/support/api_keys"
                }
            
            if response.status_code == 200:
                data = response.json()

                interactions = []
                # BioGRID 返回的格式是 {"interaction_id": {...}}，字段名是大写的
                for interaction_id, hit in list(data.items())[:max_results]:
                    if not isinstance(hit, dict):
                        continue
                    interactions.append({
                        "interaction_id": hit.get("BIOGRID_INTERACTION_ID", ""),
                        "gene_a": hit.get("OFFICIAL_SYMBOL_A", ""),
                        "gene_b": hit.get("OFFICIAL_SYMBOL_B", ""),
                        "entrez_a": hit.get("ENTREZ_GENE_A", ""),
                        "entrez_b": hit.get("ENTREZ_GENE_B", ""),
                        "experimental_system": hit.get("EXPERIMENTAL_SYSTEM", ""),
                        "experimental_system_type": hit.get("EXPERIMENTAL_SYSTEM_TYPE", ""),
                        "pmid": hit.get("PUBMED_ID", ""),
                        "pubmed_author": hit.get("PUBMED_AUTHOR", ""),
                        "throughput": hit.get("THROUGHPUT", ""),
                        "organism_a": hit.get("ORGANISM_A", ""),
                        "organism_b": hit.get("ORGANISM_B", ""),
                        "source_db": hit.get("SOURCEDB", ""),
                    })
                
                return {
                    "status": "success",
                    "genes": genes,
                    "total": len(interactions),
                    "interactions": interactions
                }
            
            return {"status": "error", "message": f"API returned status {response.status_code}"}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def search_interactions_by_gene(
        self,
        gene: str,
        max_results: int = 50
    ) -> Dict[str, Any]:
        """通过基因搜索互作"""
        return self.get_interactions([gene], max_results=max_results)

    def get_network_for_genes(
        self,
        genes: List[str],
        max_results: int = 200
    ) -> Dict[str, Any]:
        """获取基因组的互作网络"""
        return self.get_interactions(genes, max_results=max_results)


if __name__ == "__main__":
    api = BioGRIDAPI()
    
    print("=== 测试蛋白互作 (TP53) ===")
    result = api.search_interactions_by_gene("TP53", max_results=10)
    print(f"Status: {result.get('status')}")
    if result.get("status") == "success":
        print(f"找到 {result.get('total')} 个互作")
        for i in result.get("interactions", [])[:5]:
            print(f"  - {i.get('gene_a')} <-> {i.get('gene_b')}: {i.get('experimental_system')}")
    else:
        print(f"Error: {result.get('error', result.get('message'))}")
