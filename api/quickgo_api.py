"""
QuickGO API 调用示例
Gene Ontology (GO) 注释数据库
"""

import requests
import json
from typing import Dict, Any

class QuickGO_API:
    """QuickGO数据库API接口"""
    
    def __init__(self):
        self.base_url = "https://www.ebi.ac.uk/QuickGO/services"
        
    def get_go_annotations(self, uniprot_id: str, taxon_id: int = 9606) -> Dict[str, Any]:
        """
        获取基因的GO注释
        
        参数:
            uniprot_id: UniProt ID（如 P04637）
            taxon_id: 物种ID，9606=人类
            
        返回:
            GO注释列表
        """
        annotation_url = f"{self.base_url}/annotation/search"
        
        params = {
            'geneProductId': uniprot_id,
            'taxonId': taxon_id,
            'limit': 100
        }
        
        headers = {
            'Accept': 'application/json'
        }
        
        try:
            response = requests.get(annotation_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            annotations = []
            for result in data.get('results', []):
                annotations.append({
                    'go_id': result.get('goId'),
                    'go_name': result.get('goName'),
                    'go_aspect': result.get('goAspect'),
                    'evidence_code': result.get('goEvidence')
                })
            
            return {
                'status': 'success',
                'query': uniprot_id,
                'total_annotations': len(annotations),
                'annotations': annotations[:20]  # 只返回前20个
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'query': uniprot_id,
                'error': str(e)
            }
    
    def get_go_term(self, go_id: str) -> Dict[str, Any]:
        """
        获取GO term详细信息
        
        参数:
            go_id: GO ID，如 "GO:0006915"
            
        返回:
            GO term详细信息
        """
        term_url = f"{self.base_url}/ontology/go/terms/{go_id}"
        
        headers = {
            'Accept': 'application/json'
        }
        
        try:
            response = requests.get(term_url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            result = data.get('results', [{}])[0]
            return {
                'status': 'success',
                'go_id': go_id,
                'name': result.get('name'),
                'definition': result.get('definition', {}).get('text'),
                'aspect': result.get('aspect')
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'go_id': go_id,
                'error': str(e)
            }


# 测试示例
if __name__ == "__main__":
    api = QuickGO_API()
    
    print("=" * 60)
    print("测试1: 获取TP53的GO注释（使用UniProt ID: P04637）")
    print("=" * 60)
    result1 = api.get_go_annotations("P04637")
    print(json.dumps(result1, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("测试2: 获取GO term详细信息 - GO:0006915 (apoptosis)")
    print("=" * 60)
    result2 = api.get_go_term("GO:0006915")
    print(json.dumps(result2, indent=2, ensure_ascii=False))
