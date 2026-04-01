"""
Ensembl API 调用示例
基因组信息数据库
"""

import requests
import json
from typing import Dict, Any

class Ensembl_API:
    """Ensembl数据库API接口"""
    
    def __init__(self):
        self.base_url = "https://rest.ensembl.org"
        
    def lookup_gene(self, gene_symbol: str, species: str = "human") -> Dict[str, Any]:
        """
        查询基因信息
        
        参数:
            gene_symbol: 基因符号
            species: 物种
            
        返回:
            基因信息
        """
        lookup_url = f"{self.base_url}/lookup/symbol/{species}/{gene_symbol}"
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(lookup_url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                'status': 'success',
                'query': gene_symbol,
                'ensembl_id': data.get('id'),
                'display_name': data.get('display_name'),
                'description': data.get('description'),
                'biotype': data.get('biotype'),
                'chromosome': data.get('seq_region_name'),
                'start': data.get('start'),
                'end': data.get('end'),
                'strand': data.get('strand')
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'query': gene_symbol,
                'error': str(e)
            }
    
    def get_sequence(self, ensembl_id: str) -> Dict[str, Any]:
        """
        获取基因序列
        
        参数:
            ensembl_id: Ensembl ID
            
        返回:
            基因序列
        """
        sequence_url = f"{self.base_url}/sequence/id/{ensembl_id}"
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(sequence_url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                'status': 'success',
                'ensembl_id': ensembl_id,
                'sequence_length': len(data.get('seq', '')),
                'sequence': data.get('seq', '')[:100] + '...'  # 只显示前100个碱基
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'ensembl_id': ensembl_id,
                'error': str(e)
            }


# 测试示例
if __name__ == "__main__":
    api = Ensembl_API()
    
    print("=" * 60)
    print("测试1: 查询TP53基因信息")
    print("=" * 60)
    result1 = api.lookup_gene("TP53")
    print(json.dumps(result1, indent=2, ensure_ascii=False))
    
    if result1['status'] == 'success':
        print("\n" + "=" * 60)
        print(f"测试2: 获取基因序列 - {result1['ensembl_id']}")
        print("=" * 60)
        result2 = api.get_sequence(result1['ensembl_id'])
        print(json.dumps(result2, indent=2, ensure_ascii=False))
