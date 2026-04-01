"""
ChEMBL API 调用示例
药物和化合物数据库
"""

import requests
import json
from typing import Dict, Any

class ChEMBL_API:
    """ChEMBL数据库API接口"""
    
    def __init__(self):
        self.base_url = "https://www.ebi.ac.uk/chembl/api/data"
        
    def search_compound(self, compound_name: str) -> Dict[str, Any]:
        """
        搜索化合物
        
        参数:
            compound_name: 化合物名称
            
        返回:
            化合物信息
        """
        search_url = f"{self.base_url}/molecule/search.json"
        
        params = {
            'q': compound_name,
            'limit': 5
        }
        
        try:
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            compounds = []
            for molecule in data.get('molecules', []):
                compounds.append({
                    'chembl_id': molecule.get('molecule_chembl_id'),
                    'pref_name': molecule.get('pref_name'),
                    'molecule_type': molecule.get('molecule_type'),
                    'max_phase': molecule.get('max_phase')
                })
            
            return {
                'status': 'success',
                'query': compound_name,
                'total_results': len(compounds),
                'compounds': compounds
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'query': compound_name,
                'error': str(e)
            }
    
    def get_compound_by_id(self, chembl_id: str) -> Dict[str, Any]:
        """
        通过ChEMBL ID获取化合物详细信息
        
        参数:
            chembl_id: ChEMBL ID
            
        返回:
            化合物详细信息
        """
        compound_url = f"{self.base_url}/molecule/{chembl_id}.json"
        
        try:
            response = requests.get(compound_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                'status': 'success',
                'chembl_id': chembl_id,
                'data': data
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'chembl_id': chembl_id,
                'error': str(e)
            }


# 测试示例
if __name__ == "__main__":
    api = ChEMBL_API()
    
    print("=" * 60)
    print("测试1: 搜索化合物 - Aspirin")
    print("=" * 60)
    result1 = api.search_compound("aspirin")
    print(json.dumps(result1, indent=2, ensure_ascii=False))
    
    if result1['status'] == 'success' and result1['compounds']:
        chembl_id = result1['compounds'][0]['chembl_id']
        print("\n" + "=" * 60)
        print(f"测试2: 获取化合物详细信息 - {chembl_id}")
        print("=" * 60)
        result2 = api.get_compound_by_id(chembl_id)
        print(f"状态: {result2['status']}")
