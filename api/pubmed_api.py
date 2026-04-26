"""
PubMed API 调用示例
通过关键词搜索文献
使用NCBI E-utilities API

支持API Key和重试机制：
- 有API Key时：最多10请求/秒
- 无API Key时：最多3请求/秒
- SSL错误和429限流时会自动重试
"""

import random
import time
from typing import Any, Dict, List, Optional

import requests

import sys as _sys
from pathlib import Path as _Path

# Add project root to path for imports
_proj_root = _Path(__file__).resolve().parent.parent
if str(_proj_root) not in _sys.path:
    _sys.path.insert(0, str(_proj_root))


class PubMed_API:
    """PubMed数据库API接口，支持API Key和重试机制"""
    
    def __init__(self, email: str = "e2sc@example.com", api_key: str = ""):
        """
        初始化PubMed API
        
        参数:
            email: 邮箱（NCBI要求提供，用于追踪API使用）
            api_key: NCBI API Key（可选，提供后可提高速率限制）
        """
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.email = email
        self.api_key = api_key
        self._window_start = time.time()
        self._request_count = 0
    
    def _rate_limit_wait(self) -> None:
        """Enhanced rate limiting with API key support.
        
        With API key: up to 10 req/s
        Without API key: 3 req/s
        """
        max_rate = 10 if self.api_key else 3
        elapsed = time.time() - self._window_start
        interval = 1.0 / max_rate
        if elapsed < interval:
            time.sleep(interval - elapsed)
        self._window_start = time.time()
    
    def _make_request_with_retry(
        self,
        url: str,
        params: Dict,
        max_retries: int = 3,
        timeout: int = 15
    ) -> Optional[requests.Response]:
        """Make HTTP request with exponential backoff retry.
        
        Handles SSL errors, connection errors, and 429 rate limit responses.
        
        参数:
            url: 请求URL
            params: 请求参数
            max_retries: 最大重试次数
            timeout: 超时时间（秒）
            
        返回:
            Response对象或None
        """
        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params, timeout=timeout)
                
                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 5))
                    print(f"[PubMed_API] Rate limited (429), waiting {retry_after}s before retry {attempt + 1}/{max_retries}")
                    time.sleep(retry_after)
                    continue
                
                response.raise_for_status()
                return response
                
            except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    print(f"[PubMed_API] Request failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time:.1f}s: {e}")
                    time.sleep(wait_time)
                else:
                    print(f"[PubMed_API] Request failed after {max_retries} attempts: {e}")
                    return None
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt)
                    print(f"[PubMed_API] Request timeout (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s")
                    time.sleep(wait_time)
                else:
                    print(f"[PubMed_API] Request timeout after {max_retries} attempts")
                    return None
            except Exception as e:
                print(f"[PubMed_API] Request unexpected error: {e}")
                return None
        
        return None
    
    def _build_params(self, base_params: Dict) -> Dict:
        """Build request params with API key if available."""
        params = base_params.copy()
        params["email"] = self.email
        if self.api_key:
            params["api_key"] = self.api_key
        return params
    
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
        
        self._rate_limit_wait()
        params = self._build_params({
            'db': 'pubmed',
            'term': keywords,
            'retmax': max_results,
            'retmode': 'json',
            'sort': sort,
        })
        
        response = self._make_request_with_retry(search_url, params)
        
        if response is None:
            return {
                'status': 'error',
                'query': keywords,
                'error': 'Search failed after retries'
            }
        
        try:
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
        
        self._rate_limit_wait()
        params = self._build_params({
            'db': 'pubmed',
            'id': ','.join(pmid_list),
            'retmode': 'xml',
        })
        
        response = self._make_request_with_retry(fetch_url, params)
        
        if response is None:
            return {
                'status': 'error',
                'error': 'Fetch failed after retries'
            }
        
        return {
            'status': 'success',
            'pmid_count': len(pmid_list),
            'data': response.text
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
        
        self._rate_limit_wait()
        params = self._build_params({
            'db': 'pubmed',
            'id': ','.join(pmid_list),
            'retmode': 'json',
        })
        
        response = self._make_request_with_retry(summary_url, params)
        
        if response is None:
            return {
                'status': 'error',
                'error': 'Summary fetch failed after retries'
            }
        
        try:
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
        
        if search_result['status'] != 'success' or not search_result.get('pmid_list'):
            return search_result
        
        # 等待一下，避免请求过快
        time.sleep(0.3)
        
        # 第二步：获取详细信息
        details = self.get_article_summary(search_result['pmid_list'])
        
        return {
            'status': 'success',
            'query': keywords,
            'total_count': search_result.get('total_count', 0),
            'returned_count': search_result.get('returned_count', 0),
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
