"""
综合使用示例：整合所有API进行生物信息学查询
演示如何组合使用UniProt、PubChem和PubMed API
"""

import json
import time
from uniprot_api import UniProt_API
from pubchem_api import PubChem_API
from pubmed_api import PubMed_API


class BioInfoSearch:
    """生物信息学综合查询工具"""
    
    def __init__(self, email="your_email@example.com"):
        self.uniprot = UniProt_API()
        self.pubchem = PubChem_API()
        self.pubmed = PubMed_API(email=email)
    
    def search_gene_comprehensive(self, gene_name: str):
        """
        综合查询基因信息
        
        参数:
            gene_name: 基因名称
            
        返回:
            包含蛋白质信息和相关文献的综合结果
        """
        print(f"\n{'='*60}")
        print(f"正在查询基因: {gene_name}")
        print(f"{'='*60}\n")
        
        # 1. 查询UniProt获取蛋白质信息
        print("步骤1: 从UniProt获取蛋白质信息...")
        protein_result = self.uniprot.search_by_gene(gene_name, top_n=5)
        
        if protein_result['status'] == 'success' and protein_result['results']:
            print(f"[OK] 找到 {len(protein_result['results'])} 个蛋白质条目")
            top_protein = protein_result['results'][0]
            print(f"  - 最佳匹配: {top_protein['protein_name']}")
            print(f"  - Accession: {top_protein['accession']}")
            print(f"  - 评分: {top_protein['annotation_score']}")
            print(f"  - 已审核: {'是' if top_protein['reviewed'] else '否'}")
        else:
            print("[FAIL] 未找到蛋白质信息")
            top_protein = None
        
        time.sleep(0.5)
        
        # 2. 查询PubMed获取相关文献
        print("\n步骤2: 从PubMed搜索相关文献...")
        literature_result = self.pubmed.search_and_get_details(
            f"{gene_name}[Gene] AND human", 
            max_results=5
        )
        
        if literature_result['status'] == 'success' and literature_result.get('articles'):
            print(f"[OK] 找到 {literature_result['total_count']} 篇相关文献（显示前5篇）")
            for i, article in enumerate(literature_result['articles'][:3], 1):
                print(f"  {i}. {article['title'][:80]}...")
                print(f"     期刊: {article['journal']}, {article['pub_date']}")
        else:
            print("[FAIL] 未找到相关文献")
        
        return {
            'gene': gene_name,
            'protein_info': protein_result,
            'literature': literature_result
        }
    
    def search_metabolite_comprehensive(self, metabolite_name: str):
        """
        综合查询代谢物信息
        
        参数:
            metabolite_name: 代谢物名称
            
        返回:
            包含化合物信息和相关文献的综合结果
        """
        print(f"\n{'='*60}")
        print(f"正在查询代谢物: {metabolite_name}")
        print(f"{'='*60}\n")
        
        # 1. 查询PubChem获取化合物信息
        print("步骤1: 从PubChem获取化合物信息...")
        compound_result = self.pubchem.search_and_get_details(metabolite_name, top_n=1)
        
        if compound_result['status'] == 'success' and compound_result.get('compounds'):
            compound = compound_result['compounds'][0]
            props = compound['properties']
            print(f"[OK] 找到化合物")
            print(f"  - CID: {props['CID']}")
            print(f"  - 分子式: {props['MolecularFormula']}")
            print(f"  - 分子量: {props['MolecularWeight']}")
            print(f"  - IUPAC名称: {props['IUPACName'][:80]}...")
            
            # 获取同义词
            time.sleep(0.3)
            synonyms_result = self.pubchem.get_synonyms(str(props['CID']))
            if synonyms_result['status'] == 'success':
                print(f"  - 同义词: {', '.join(synonyms_result['synonyms'][:5])}...")
        else:
            print("[FAIL] 未找到化合物信息")
        
        time.sleep(0.5)
        
        # 2. 查询PubMed获取相关文献
        print("\n步骤2: 从PubMed搜索相关文献...")
        literature_result = self.pubmed.search_and_get_details(
            f"{metabolite_name} AND metabolism", 
            max_results=5
        )
        
        if literature_result['status'] == 'success' and literature_result.get('articles'):
            print(f"[OK] 找到 {literature_result['total_count']} 篇相关文献（显示前5篇）")
            for i, article in enumerate(literature_result['articles'][:3], 1):
                print(f"  {i}. {article['title'][:80]}...")
                print(f"     期刊: {article['journal']}, {article['pub_date']}")
        else:
            print("[FAIL] 未找到相关文献")
        
        return {
            'metabolite': metabolite_name,
            'compound_info': compound_result,
            'literature': literature_result
        }
    
    def search_pathway_genes(self, gene_list: list):
        """
        批量查询通路中的多个基因
        
        参数:
            gene_list: 基因名称列表
            
        返回:
            所有基因的蛋白质信息
        """
        print(f"\n{'='*60}")
        print(f"正在批量查询 {len(gene_list)} 个基因")
        print(f"{'='*60}\n")
        
        results = {}
        for i, gene in enumerate(gene_list, 1):
            print(f"[{i}/{len(gene_list)}] 查询 {gene}...")
            result = self.uniprot.search_by_gene(gene, top_n=1)
            
            if result['status'] == 'success' and result['results']:
                protein = result['results'][0]
                print(f"  [OK] {protein['protein_name']}")
                print(f"    Accession: {protein['accession']}, 评分: {protein['annotation_score']}")
                results[gene] = protein
            else:
                print(f"  [FAIL] 未找到")
                results[gene] = None
            
            time.sleep(0.3)  # 避免请求过快
        
        return results


# 使用示例
if __name__ == "__main__":
    # 初始化综合查询工具
    bio_search = BioInfoSearch(email="your_email@example.com")
    
    print("\n" + "="*60)
    print("示例1: 综合查询基因 TP53")
    print("="*60)
    result1 = bio_search.search_gene_comprehensive("TP53")
    
    print("\n" + "="*60)
    print("示例2: 综合查询代谢物 Glucose")
    print("="*60)
    result2 = bio_search.search_metabolite_comprehensive("glucose")
    
    print("\n" + "="*60)
    print("示例3: 批量查询凋亡通路相关基因")
    print("="*60)
    apoptosis_genes = ["TP53", "BAX", "BCL2", "CASP3", "CASP9"]
    result3 = bio_search.search_pathway_genes(apoptosis_genes)
    
    print("\n" + "="*60)
    print("示例4: 查询铁死亡相关代谢物")
    print("="*60)
    result4 = bio_search.search_metabolite_comprehensive("glutathione")
    
    print("\n" + "="*60)
    print("所有查询完成！")
    print("="*60)
    
    # 保存结果到JSON文件
    output = {
        'gene_query': {
            'gene': result1['gene'],
            'protein_count': len(result1['protein_info'].get('results', [])),
            'literature_count': result1['literature'].get('total_count', 0)
        },
        'metabolite_query': {
            'metabolite': result2['metabolite'],
            'compound_found': result2['compound_info']['status'] == 'success',
            'literature_count': result2['literature'].get('total_count', 0)
        },
        'pathway_genes': {
            'total': len(apoptosis_genes),
            'found': sum(1 for v in result3.values() if v is not None),
            'genes': list(result3.keys())
        }
    }
    
    with open('f:/1a-sc-agent/api/query_results.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print("\n查询结果摘要已保存到: query_results.json")
