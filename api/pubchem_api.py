"""
PubChem API 调用示例
PubChem是一个免费的化学数据库，可以作为HMDB的替代方案
支持通过化合物名称、CID、InChI等多种方式查询
"""

import requests
import json
from typing import Dict, Any, List
import time

class PubChem_API:
    """PubChem数据库API接口"""
    
    def __init__(self):
        self.base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
        
    def search_by_name(self, compound_name: str, max_results: int = 5) -> Dict[str, Any]:
        """
        通过化合物名称搜索
        
        参数:
            compound_name: 化合物名称，如 "glucose", "caffeine"
            max_results: 最大返回结果数
            
        返回:
            包含化合物CID列表的字典
        """
        search_url = f"{self.base_url}/compound/name/{compound_name}/cids/JSON"
        
        try:
            response = requests.get(search_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            cid_list = data.get('IdentifierList', {}).get('CID', [])[:max_results]
            
            return {
                'status': 'success',
                'query': compound_name,
                'total_results': len(cid_list),
                'cid_list': cid_list
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'query': compound_name,
                'error': str(e)
            }
    
    def get_compound_by_cid(self, cid: str) -> Dict[str, Any]:
        """
        通过CID获取化合物详细信息
        
        参数:
            cid: PubChem Compound ID
            
        返回:
            化合物详细信息
        """
        compound_url = f"{self.base_url}/compound/cid/{cid}/JSON"
        
        try:
            response = requests.get(compound_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # 提取关键信息
            pc_compounds = data.get('PC_Compounds', [])
            if pc_compounds:
                compound = pc_compounds[0]
                
                # 提取属性
                props = {}
                for prop in compound.get('props', []):
                    urn = prop.get('urn', {})
                    label = urn.get('label', '')
                    value = prop.get('value', {})
                    
                    if 'sval' in value:
                        props[label] = value['sval']
                    elif 'fval' in value:
                        props[label] = value['fval']
                    elif 'ival' in value:
                        props[label] = value['ival']
                
                return {
                    'status': 'success',
                    'cid': cid,
                    'molecular_formula': props.get('Molecular Formula', 'N/A'),
                    'molecular_weight': props.get('Molecular Weight', 'N/A'),
                    'iupac_name': props.get('IUPAC Name', 'N/A'),
                    'canonical_smiles': props.get('Canonical SMILES', 'N/A'),
                    'inchi': props.get('InChI', 'N/A'),
                    'inchikey': props.get('InChIKey', 'N/A'),
                    'url': f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}",
                    'full_data': compound
                }
            else:
                return {
                    'status': 'error',
                    'cid': cid,
                    'error': 'No compound data found'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'cid': cid,
                'error': str(e)
            }
    
    def get_compound_properties(self, cid: str, properties: List[str] = None) -> Dict[str, Any]:
        """
        获取化合物的特定属性
        
        参数:
            cid: PubChem Compound ID
            properties: 要获取的属性列表，如 ['MolecularFormula', 'MolecularWeight', 'IUPACName']
            
        返回:
            化合物属性信息
        """
        if properties is None:
            properties = ['MolecularFormula', 'MolecularWeight', 'IUPACName', 
                         'CanonicalSMILES', 'InChI', 'InChIKey']
        
        props_str = ','.join(properties)
        props_url = f"{self.base_url}/compound/cid/{cid}/property/{props_str}/JSON"
        
        try:
            response = requests.get(props_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            properties_data = data.get('PropertyTable', {}).get('Properties', [])
            if properties_data:
                return {
                    'status': 'success',
                    'cid': cid,
                    'properties': properties_data[0],
                    'url': f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}"
                }
            else:
                return {
                    'status': 'error',
                    'cid': cid,
                    'error': 'No properties found'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'cid': cid,
                'error': str(e)
            }
    
    def search_and_get_details(self, compound_name: str, top_n: int = 1) -> Dict[str, Any]:
        """
        一步完成：搜索并获取化合物详细信息
        
        参数:
            compound_name: 化合物名称
            top_n: 返回前N个结果的详细信息
            
        返回:
            完整的化合物信息
        """
        # 第一步：搜索CID
        search_result = self.search_by_name(compound_name, max_results=top_n)
        
        if search_result['status'] != 'success' or not search_result['cid_list']:
            return search_result
        
        # 第二步：获取详细信息
        compounds = []
        for cid in search_result['cid_list']:
            time.sleep(0.2)  # 避免请求过快
            details = self.get_compound_properties(str(cid))
            if details['status'] == 'success':
                compounds.append(details)
        
        return {
            'status': 'success',
            'query': compound_name,
            'total_results': len(compounds),
            'compounds': compounds
        }
    
    def get_synonyms(self, cid: str) -> Dict[str, Any]:
        """
        获取化合物的同义词
        
        参数:
            cid: PubChem Compound ID
            
        返回:
            同义词列表
        """
        synonyms_url = f"{self.base_url}/compound/cid/{cid}/synonyms/JSON"
        
        try:
            response = requests.get(synonyms_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            synonyms = data.get('InformationList', {}).get('Information', [])
            if synonyms:
                return {
                    'status': 'success',
                    'cid': cid,
                    'synonyms': synonyms[0].get('Synonym', [])[:20]  # 只返回前20个
                }
            else:
                return {
                    'status': 'error',
                    'cid': cid,
                    'error': 'No synonyms found'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'cid': cid,
                'error': str(e)
            }


# 测试示例
if __name__ == "__main__":
    api = PubChem_API()
    
    print("=" * 60)
    print("测试1: 通过名称搜索化合物 - Glucose")
    print("=" * 60)
    result1 = api.search_by_name("glucose", max_results=3)
    print(json.dumps(result1, indent=2, ensure_ascii=False))
    
    if result1['status'] == 'success' and result1['cid_list']:
        cid = result1['cid_list'][0]
        
        print("\n" + "=" * 60)
        print(f"测试2: 获取化合物详细信息 - CID {cid}")
        print("=" * 60)
        result2 = api.get_compound_by_cid(str(cid))
        print(json.dumps({k: v for k, v in result2.items() if k != 'full_data'}, 
                        indent=2, ensure_ascii=False))
        
        print("\n" + "=" * 60)
        print(f"测试3: 获取化合物属性 - CID {cid}")
        print("=" * 60)
        result3 = api.get_compound_properties(str(cid))
        print(json.dumps(result3, indent=2, ensure_ascii=False))
        
        print("\n" + "=" * 60)
        print(f"测试4: 获取化合物同义词 - CID {cid}")
        print("=" * 60)
        result4 = api.get_synonyms(str(cid))
        print(json.dumps(result4, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("测试5: 一步完成 - 搜索Caffeine并获取详情")
    print("=" * 60)
    result5 = api.search_and_get_details("caffeine", top_n=1)
    print(json.dumps(result5, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("测试6: 搜索代谢物 - ATP")
    print("=" * 60)
    result6 = api.search_and_get_details("ATP", top_n=1)
    print(json.dumps(result6, indent=2, ensure_ascii=False))
