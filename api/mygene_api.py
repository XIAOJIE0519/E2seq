"""
MyGene.info API 调用示例
提供基因注释信息，可以替代多个API
"""

import requests
import json
from typing import Dict, Any, List

class MyGene_API:
    """MyGene.info数据库API接口"""
    
    def __init__(self):
        self.base_url = "https://mygene.info/v3"
        
    def query_gene(self, gene_symbol: str, species: str = "human") -> Dict[str, Any]:
        """
        查询基因信息
        
        参数:
            gene_symbol: 基因符号，如 "TP53"
            species: 物种，默认 "human"
            
        返回:
            基因详细信息
        """
        query_url = f"{self.base_url}/query"
        
        params = {
            'q': f'symbol:{gene_symbol} AND taxid:9606' if species == "human" else f'symbol:{gene_symbol}',
            'fields': 'all',
            'size': 1
        }
        
        try:
            response = requests.get(query_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('hits'):
                hit = data['hits'][0]
                return {
                    'status': 'success',
                    'query': gene_symbol,
                    'entrez_id': hit.get('_id'),
                    'symbol': hit.get('symbol'),
                    'name': hit.get('name'),
                    'taxid': hit.get('taxid'),
                    'type_of_gene': hit.get('type_of_gene'),
                    'genomic_pos': hit.get('genomic_pos'),
                    'ensembl': hit.get('ensembl'),
                    'uniprot': hit.get('uniprot'),
                    'full_data': hit
                }
            else:
                return {
                    'status': 'error',
                    'query': gene_symbol,
                    'error': 'No results found'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'query': gene_symbol,
                'error': str(e)
            }
    
    def get_gene_by_id(self, gene_id: str) -> Dict[str, Any]:
        """
        通过Entrez Gene ID获取基因信息
        
        参数:
            gene_id: Entrez Gene ID
            
        返回:
            基因详细信息
        """
        gene_url = f"{self.base_url}/gene/{gene_id}"
        
        try:
            response = requests.get(gene_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                'status': 'success',
                'gene_id': gene_id,
                'data': data
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'gene_id': gene_id,
                'error': str(e)
            }


# 测试示例
if __name__ == "__main__":
    api = MyGene_API()
    
    print("=" * 60)
    print("测试1: 查询TP53基因")
    print("=" * 60)
    result1 = api.query_gene("TP53")
    print(json.dumps({k: v for k, v in result1.items() if k != 'full_data'}, 
                     indent=2, ensure_ascii=False))
    
    if result1['status'] == 'success':
        print("\n" + "=" * 60)
        print(f"测试2: 通过Entrez ID获取详细信息 - {result1['entrez_id']}")
        print("=" * 60)
        result2 = api.get_gene_by_id(result1['entrez_id'])
        print(f"状态: {result2['status']}")
        if result2['status'] == 'success':
            print(f"基因符号: {result2['data'].get('symbol')}")
            print(f"基因名称: {result2['data'].get('name')}")
