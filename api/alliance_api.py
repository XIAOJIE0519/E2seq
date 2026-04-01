"""
Alliance of Genome Resources API 调用模块
提供模式生物、同源基因、跨物种证据
API文档: https://www.alliancegenome.org/
"""

import requests
from typing import Dict, Any, List, Optional


class AllianceAPI:
    """Alliance of Genome Resources 数据库 API 接口"""

    def __init__(self):
        self.base_url = "https://www.alliancegenome.org/api"
        self.headers = {"Accept": "application/json"}

    def search_cross_species(self, query: str) -> Dict[str, Any]:
        """跨物种搜索"""
        try:
            url = f"{self.base_url}/search"
            params = {"q": query}
            
            response = requests.get(
                url, 
                params=params, 
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                # 处理不同格式的响应
                raw_results = data if isinstance(data, dict) else {}
                hits = raw_results.get("results", []) if isinstance(raw_results, dict) else raw_results if isinstance(raw_results, list) else []
                
                for hit in hits[:50]:
                    if not isinstance(hit, dict):
                        continue
                    results.append({
                        "id": hit.get("id", ""),
                        "symbol": hit.get("symbol", ""),
                        "name": hit.get("name", ""),
                        "category": hit.get("category", ""),
                        "species": hit.get("species", {}).get("name", "") if isinstance(hit.get("species"), dict) else str(hit.get("species", "")),
                    })
                
                return {
                    "status": "success",
                    "query": query,
                    "total": len(results),
                    "results": results
                }
            
            return {"status": "error", "error": f"HTTP {response.status_code}"}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def get_homologs(self, gene: str, species: str = "human") -> Dict[str, Any]:
        """获取基因的同源基因"""
        try:
            # 先搜索基因获取ID
            search_url = f"{self.base_url}/search"
            search_params = {
                "q": gene,
                "category": "gene",
            }
            search_response = requests.get(
                search_url, 
                params=search_params, 
                headers=self.headers,
                timeout=30
            )
            
            homologs = []
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                hits = search_data.get("results", []) if isinstance(search_data, dict) else search_data if isinstance(search_data, list) else []
                
                if hits:
                    gene_id = hits[0].get("id", "") if isinstance(hits[0], dict) else ""
                    
                    # 获取同源基因
                    homolog_url = f"{self.base_url}/gene/{gene_id}/homologs"
                    homolog_response = requests.get(
                        homolog_url, 
                        headers=self.headers,
                        timeout=30
                    )
                    
                    if homolog_response.status_code == 200:
                        homolog_data = homolog_response.json()
                        homologs_raw = homolog_data if isinstance(homolog_data, list) else homolog_data.get("results", []) if isinstance(homolog_data, dict) else []
                        
                        for h in homologs_raw[:20]:
                            if not isinstance(h, dict):
                                continue
                            homologs.append({
                                "gene": h.get("symbol", ""),
                                "species": h.get("species", {}).get("name", "") if isinstance(h.get("species"), dict) else str(h.get("species", "")),
                                "homology_type": h.get("homologyType", ""),
                            })
                
                return {
                    "status": "success",
                    "gene": gene,
                    "total": len(homologs),
                    "homologs": homologs
                }
            
            return {"status": "error", "error": f"HTTP {search_response.status_code}"}

        except Exception as e:
            return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    api = AllianceAPI()
    
    print("=== 测试跨物种搜索 (BRCA1) ===")
    result = api.search_cross_species("BRCA1")
    print(f"Status: {result.get('status')}")
    if result.get("status") == "success":
        print(f"找到 {result.get('total')} 个结果")
        for r in result.get("results", [])[:3]:
            print(f"  - {r.get('symbol')} ({r.get('species')}): {r.get('category')}")
    else:
        print(f"Error: {result.get('error')}")
