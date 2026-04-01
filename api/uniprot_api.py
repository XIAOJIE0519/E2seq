"""
UniProt API 调用示例
支持通过基因名搜索蛋白质信息，返回前5个结果并按评分排序
"""

import requests
import json
from typing import List, Dict, Any

class UniProtAPI:
    """UniProt数据库API接口"""
    
    def __init__(self):
        self.base_url = "https://rest.uniprot.org"
        
    def search_by_gene(self, gene_name: str, organism: str = "human", top_n: int = 1) -> Dict[str, Any]:
        """
        通过基因名搜索蛋白质信息
        
        参数:
            gene_name: 基因名称，如 "TP53", "BRCA1"
            organism: 物种，默认 "human"
            top_n: 返回前N个结果，默认1个
            
        返回:
            包含蛋白质信息的字典，按annotation score降序排列
        """
        search_url = f"{self.base_url}/uniprotkb/search"
        
        # 构建查询参数
        if organism.lower() == "human":
            query = f"(gene:{gene_name}) AND (organism_id:9606)"
        else:
            query = f"(gene:{gene_name}) AND (organism_name:{organism})"
        
        params = {
            'query': query,
            'format': 'json',
            'size': top_n,
            'sort': 'annotation_score desc'  # 按注释评分降序排列
        }
        
        try:
            response = requests.get(search_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # 提取关键信息
            results = []
            for entry in data.get('results', []):
                protein_info = {
                    'accession': entry.get('primaryAccession'),
                    'protein_name': entry.get('proteinDescription', {}).get('recommendedName', {}).get('fullName', {}).get('value', 'N/A'),
                    'gene_names': [g.get('geneName', {}).get('value') for g in entry.get('genes', [])],
                    'organism': entry.get('organism', {}).get('scientificName'),
                    'annotation_score': entry.get('annotationScore'),
                    'reviewed': entry.get('entryType') == 'UniProtKB reviewed (Swiss-Prot)',
                    'sequence_length': entry.get('sequence', {}).get('length'),
                    'url': f"https://www.uniprot.org/uniprotkb/{entry.get('primaryAccession')}"
                }
                results.append(protein_info)
            
            return {
                'status': 'success',
                'query': gene_name,
                'organism': organism,
                'total_results': len(results),
                'results': results
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'query': gene_name,
                'error': str(e)
            }
    
    def get_protein_by_accession(self, accession: str) -> Dict[str, Any]:
        """
        通过UniProt Accession获取详细蛋白质信息
        
        参数:
            accession: UniProt登录号，如 "P04637" (TP53)
            
        返回:
            蛋白质详细信息
        """
        protein_url = f"{self.base_url}/uniprotkb/{accession}.json"
        
        try:
            response = requests.get(protein_url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            return {
                'status': 'success',
                'accession': accession,
                'data': data,
                'url': f"https://www.uniprot.org/uniprotkb/{accession}"
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'accession': accession,
                'error': str(e)
            }
    
    def search_multiple_genes(self, gene_list: List[str], organism: str = "human", top_n: int = 5) -> Dict[str, Any]:
        """
        批量搜索多个基因
        
        参数:
            gene_list: 基因名称列表
            organism: 物种
            top_n: 每个基因返回前N个结果
            
        返回:
            所有基因的搜索结果
        """
        results = {}
        for gene in gene_list:
            results[gene] = self.search_by_gene(gene, organism, top_n)
        
        return {
            'status': 'success',
            'total_genes': len(gene_list),
            'results': results
        }


# 测试示例
if __name__ == "__main__":
    api = UniProt_API()
    
    print("=" * 60)
    print("测试1: 搜索TP53基因（人类）- 返回第1个结果")
    print("=" * 60)
    result1 = api.search_by_gene("TP53", organism="human", top_n=1)
    print(json.dumps(result1, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("测试2: 通过Accession获取TP53详细信息 - P04637")
    print("=" * 60)
    result2 = api.get_protein_by_accession("P04637")
    if result2['status'] == 'success':
        print(f"状态: {result2['status']}")
        print(f"Accession: {result2['accession']}")
        print(f"URL: {result2['url']}")
        print(f"蛋白名称: {result2['data'].get('proteinDescription', {}).get('recommendedName', {}).get('fullName', {}).get('value')}")
        print(f"基因名: {[g.get('geneName', {}).get('value') for g in result2['data'].get('genes', [])]}")
    else:
        print(json.dumps(result2, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("测试3: 批量搜索多个基因")
    print("=" * 60)
    result3 = api.search_multiple_genes(["BRCA1", "EGFR", "MYC"], top_n=3)
    print(json.dumps(result3, indent=2, ensure_ascii=False))
