"""
PubMed API 调用示例
通过关键词搜索文献
使用NCBI E-utilities API
"""

import requests
import json
from typing import List, Dict, Any
import time

class PubMed_API:
    """PubMed数据库API接口"""
    
    def __init__(self, email: str = "your_email@example.com"):
        """
        初始化PubMed API
        
        参数:
            email: 你的邮箱（NCBI要求提供，用于追踪API使用）
        """
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.email = email
        
    def search_articles(self, keywords: str, max_results: int = 10, 
                       sort: str = "relevance") -> Dict[str, Any]:
        """
        通过关键词搜索PubMed文献
        
        参数:
            keywords: 搜索关键词，如 "cancer AND TP53"
            max_results: 最大返回结果数，默认10
            sort: 排序方式，可选 "relevance"(相关性), "pub_date"(发表日期)
            
        返回:
            包含文献ID列表的字典
        """
        search_url = f"{self.base_url}/esearch.fcgi"
        
        params = {
            'db': 'pubmed',
            'term': keywords,
            'retmax': max_results,
            'retmode': 'json',
            'sort': sort,
            'email': self.email
        }
        
        try:
            response = requests.get(search_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            pmid_list = data.get('esearchresult', {}).get('idlist', [])
            count = data.get('esearchresult', {}).get('count', 0)
            
            return {
                'status': 'success',
                'query': keywords,
                'total_count': int(count),
                'returned_count': len(pmid_list),
                'pmid_list': pmid_list
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'query': keywords,
                'error': str(e)
            }
    
    def get_article_details(self, pmid_list: List[str]) -> Dict[str, Any]:
        """
        获取文献详细信息
        
        参数:
            pmid_list: PubMed ID列表
            
        返回:
            文献详细信息
        """
        if not pmid_list:
            return {'status': 'error', 'error': 'Empty PMID list'}
        
        fetch_url = f"{self.base_url}/efetch.fcgi"
        
        params = {
            'db': 'pubmed',
            'id': ','.join(pmid_list),
            'retmode': 'xml',
            'email': self.email
        }
        
        try:
            response = requests.get(fetch_url, params=params, timeout=15)
            response.raise_for_status()
            
            return {
                'status': 'success',
                'pmid_count': len(pmid_list),
                'data': response.text
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def get_article_summary(self, pmid_list: List[str]) -> Dict[str, Any]:
        """
        获取文献摘要信息（JSON格式，更易解析）
        
        参数:
            pmid_list: PubMed ID列表
            
        返回:
            文献摘要信息
        """
        if not pmid_list:
            return {'status': 'error', 'error': 'Empty PMID list'}
        
        summary_url = f"{self.base_url}/esummary.fcgi"
        
        params = {
            'db': 'pubmed',
            'id': ','.join(pmid_list),
            'retmode': 'json',
            'email': self.email
        }
        
        try:
            response = requests.get(summary_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # 提取关键信息
            articles = []
            for pmid in pmid_list:
                if pmid in data.get('result', {}):
                    article_data = data['result'][pmid]
                    article_info = {
                        'pmid': pmid,
                        'title': article_data.get('title', 'N/A'),
                        'authors': [author.get('name') for author in article_data.get('authors', [])],
                        'journal': article_data.get('fulljournalname', 'N/A'),
                        'pub_date': article_data.get('pubdate', 'N/A'),
                        'doi': article_data.get('elocationid', 'N/A'),
                        'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                    }
                    articles.append(article_info)
            
            return {
                'status': 'success',
                'pmid_count': len(pmid_list),
                'articles': articles
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def search_and_get_details(self, keywords: str, max_results: int = 10) -> Dict[str, Any]:
        """
        一步完成：搜索并获取文献详细信息
        
        参数:
            keywords: 搜索关键词
            max_results: 最大返回结果数
            
        返回:
            完整的文献信息
        """
        # 第一步：搜索
        search_result = self.search_articles(keywords, max_results)
        
        if search_result['status'] != 'success' or not search_result['pmid_list']:
            return search_result
        
        # 等待一下，避免请求过快
        time.sleep(0.5)
        
        # 第二步：获取详细信息
        details = self.get_article_summary(search_result['pmid_list'])
        
        return {
            'status': 'success',
            'query': keywords,
            'total_count': search_result['total_count'],
            'returned_count': search_result['returned_count'],
            'articles': details.get('articles', [])
        }


# 测试示例
if __name__ == "__main__":
    # 注意：请替换为你的真实邮箱
    api = PubMed_API(email="your_email@example.com")
    
    print("=" * 60)
    print("测试1: 搜索关键词 'cancer AND TP53' - 返回前5篇")
    print("=" * 60)
    result1 = api.search_articles("cancer AND TP53", max_results=5)
    print(json.dumps(result1, indent=2, ensure_ascii=False))
    
    if result1['status'] == 'success' and result1['pmid_list']:
        print("\n" + "=" * 60)
        print("测试2: 获取上述文献的摘要信息")
        print("=" * 60)
        result2 = api.get_article_summary(result1['pmid_list'])
        print(json.dumps(result2, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("测试3: 一步完成 - 搜索'apoptosis ferroptosis'并获取详情")
    print("=" * 60)
    result3 = api.search_and_get_details("apoptosis ferroptosis", max_results=3)
    print(json.dumps(result3, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("测试4: 搜索中文相关主题（用英文关键词）")
    print("=" * 60)
    result4 = api.search_and_get_details("single cell RNA sequencing intestinal", max_results=3)
    print(json.dumps(result4, indent=2, ensure_ascii=False))
