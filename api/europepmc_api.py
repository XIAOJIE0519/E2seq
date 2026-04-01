"""
Europe PMC API 调用示例
欧洲PubMed中心文献检索
"""

import requests
import json
from typing import Dict, Any

class EuropePMC_API:
    """Europe PMC数据库API接口"""
    
    def __init__(self):
        self.base_url = "https://www.ebi.ac.uk/europepmc/webservices/rest"
        
    def search_articles(self, query: str, page_size: int = 10) -> Dict[str, Any]:
        """
        搜索文献
        
        参数:
            query: 搜索关键词
            page_size: 返回结果数量
            
        返回:
            文献列表
        """
        search_url = f"{self.base_url}/search"
        
        params = {
            'query': query,
            'format': 'json',
            'pageSize': page_size
        }
        
        try:
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for result in data.get('resultList', {}).get('result', []):
                articles.append({
                    'pmid': result.get('pmid'),
                    'title': result.get('title'),
                    'authors': result.get('authorString'),
                    'journal': result.get('journalTitle'),
                    'pub_year': result.get('pubYear'),
                    'doi': result.get('doi'),
                    'citation_count': result.get('citedByCount', 0)
                })
            
            return {
                'status': 'success',
                'query': query,
                'total_hits': data.get('hitCount', 0),
                'returned_count': len(articles),
                'articles': articles
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'query': query,
                'error': str(e)
            }


# 测试示例
if __name__ == "__main__":
    api = EuropePMC_API()
    
    print("=" * 60)
    print("测试1: 搜索TP53相关文献")
    print("=" * 60)
    result1 = api.search_articles("TP53 AND cancer", page_size=5)
    print(json.dumps(result1, indent=2, ensure_ascii=False))
