"""
STRING API 调用示例
蛋白质-蛋白质相互作用网络数据库
"""

import requests
import json
from typing import Dict, Any, List

class STRING_API:
    """STRING数据库API接口"""
    
    def __init__(self):
        self.base_url = "https://string-db.org/api"
        
    def get_interactions(self, protein_name: str, species: int = 9606, limit: int = 10) -> Dict[str, Any]:
        """
        获取蛋白质相互作用
        
        参数:
            protein_name: 蛋白质名称或基因名
            species: 物种ID，9606=人类
            limit: 返回结果数量
            
        返回:
            相互作用列表
        """
        interaction_url = f"{self.base_url}/json/interaction_partners"
        
        params = {
            'identifiers': protein_name,
            'species': species,
            'limit': limit
        }
        
        try:
            response = requests.get(interaction_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            interactions = []
            for item in data:
                interactions.append({
                    'partner': item.get('preferredName_B'),
                    'score': item.get('score'),
                    'nscore': item.get('nscore'),
                    'escore': item.get('escore')
                })
            
            return {
                'status': 'success',
                'query': protein_name,
                'total_interactions': len(interactions),
                'interactions': interactions
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'query': protein_name,
                'error': str(e)
            }
    
    def get_network_image(self, protein_list: List[str], species: int = 9606) -> Dict[str, Any]:
        """
        获取蛋白质网络图像URL
        
        参数:
            protein_list: 蛋白质名称列表
            species: 物种ID
            
        返回:
            网络图像URL
        """
        network_url = f"{self.base_url}/image/network"
        
        params = {
            'identifiers': '%0d'.join(protein_list),
            'species': species
        }
        
        try:
            response = requests.get(network_url, params=params, timeout=10)
            response.raise_for_status()
            
            return {
                'status': 'success',
                'proteins': protein_list,
                'image_url': response.url
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'proteins': protein_list,
                'error': str(e)
            }


# 测试示例
if __name__ == "__main__":
    api = STRING_API()
    
    print("=" * 60)
    print("测试1: 获取TP53的相互作用蛋白")
    print("=" * 60)
    result1 = api.get_interactions("TP53", limit=10)
    print(json.dumps(result1, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("测试2: 获取凋亡通路蛋白网络图")
    print("=" * 60)
    proteins = ["TP53", "BAX", "BCL2", "CASP3", "CASP9"]
    result2 = api.get_network_image(proteins)
    print(json.dumps(result2, indent=2, ensure_ascii=False))
