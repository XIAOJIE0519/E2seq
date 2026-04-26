"""API client for external bioinformatics databases."""

import asyncio
import random
import time
from typing import Any, Dict, List, Optional

import aiohttp
import requests

from e2sc.utils import get_config, get_logger

logger = get_logger(__name__)


class APIClient:
    """Base class for API clients with rate limiting."""
    
    def __init__(self, base_url: str, rate_limit: Optional[int] = None):
        self.base_url = base_url
        config = get_config()
        self.rate_limit = rate_limit or config.database.cache_ttl
        self.timeout = 30
        self.last_request_time = 0
    
    def _rate_limit_wait(self) -> None:
        """Wait if necessary to respect rate limit."""
        if self.rate_limit:
            elapsed = time.time() - self.last_request_time
            wait_time = 1.0 / self.rate_limit - elapsed
            if wait_time > 0:
                time.sleep(wait_time)
        self.last_request_time = time.time()
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request."""
        self._rate_limit_wait()
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"API request failed: {url}, error: {e}")
            return {}
    
    async def async_get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make async GET request."""
        url = f"{self.base_url}/{endpoint}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=self.timeout) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            logger.error(f"Async API request failed: {url}, error: {e}")
            return {}


class UniProtClient(APIClient):
    """UniProt API client."""
    
    def __init__(self):
        super().__init__("https://rest.uniprot.org/uniprotkb")
    
    def get_protein_info(self, gene: str) -> Dict[str, Any]:
        """Get protein information for a gene."""
        params = {"query": f"gene:{gene} AND organism_id:9606", "format": "json"}
        return self.get("search", params)


class STRINGAPIClient(APIClient):
    """STRING API client."""
    
    def __init__(self):
        super().__init__("https://string-db.org/api/json")
    
    def get_interactions(self, genes: List[str], species: int = 9606) -> Dict[str, Any]:
        """Get protein interactions."""
        params = {"identifiers": "%0d".join(genes), "species": species}
        return self.get("network", params)


class MyGeneClient(APIClient):
    """MyGene.info API client."""
    
    def __init__(self):
        super().__init__("https://mygene.info/v3")
    
    def get_gene_info(self, gene: str) -> Dict[str, Any]:
        """Get gene information."""
        return self.get(f"query?q={gene}&species=human")


class QuickGOClient(APIClient):
    """QuickGO API client."""
    
    def __init__(self):
        super().__init__("https://www.ebi.ac.uk/QuickGO/services")
    
    def get_go_terms(self, gene: str) -> Dict[str, Any]:
        """Get GO terms for a gene."""
        return self.get(f"annotation/search?geneProductId={gene}")


class PubMedClient(APIClient):
    """PubMed API client with API key support and retry logic."""
    
    def __init__(self):
        super().__init__("https://eutils.ncbi.nlm.nih.gov/entrez/eutils")
        from e2sc.utils import get_config
        config = get_config()
        self.api_key = config.api.pubmed_api_key or ""
        self.email = config.api.pubmed_email or "e2sc@example.com"
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
    
    def _make_request_with_retry(self, url: str, params: Dict, max_retries: int = 3) -> Optional[requests.Response]:
        """Make HTTP request with exponential backoff retry.
        
        Handles SSL errors, connection errors, and 429 rate limit responses.
        """
        import requests as _req
        import ssl as _ssl
        
        for attempt in range(max_retries):
            try:
                response = _req.get(url, params=params, timeout=15)
                
                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 5))
                    logger.warning(f"PubMed rate limited (429), waiting {retry_after}s before retry {attempt + 1}/{max_retries}")
                    time.sleep(retry_after)
                    continue
                
                response.raise_for_status()
                return response
                
            except (_req.exceptions.SSLError, _req.exceptions.ConnectionError) as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"PubMed request failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time:.1f}s: {e}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"PubMed request failed after {max_retries} attempts: {e}")
                    return None
            except Exception as e:
                logger.error(f"PubMed request unexpected error: {e}")
                return None
        
        return None
    
    def search(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search PubMed with retry logic."""
        self._rate_limit_wait()
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "email": self.email,
        }
        if self.api_key:
            params["api_key"] = self.api_key
        
        response = self._make_request_with_retry(
            f"{self.base_url}/esearch.fcgi",
            params
        )
        
        if response is None:
            return {"esearchresult": {"idlist": []}}
        
        try:
            return response.json()
        except Exception as e:
            logger.error(f"PubMed search JSON parse error: {e}")
            return {"esearchresult": {"idlist": []}}

    def search_and_get_details(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search PubMed and return article summaries with retry logic."""
        import requests as _req
        
        # Step 1: Search for PMIDs
        self._rate_limit_wait()
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "email": self.email,
        }
        if self.api_key:
            search_params["api_key"] = self.api_key
        
        search_response = self._make_request_with_retry(
            f"{self.base_url}/esearch.fcgi",
            search_params
        )
        
        if search_response is None:
            return {"status": "error", "query": query, "articles": [], "error": "Search failed after retries"}
        
        try:
            search_data = search_response.json()
        except Exception as e:
            logger.error(f"PubMed search JSON parse error: {e}")
            return {"status": "error", "query": query, "articles": [], "error": str(e)}
        
        pmid_list = search_data.get("esearchresult", {}).get("idlist", [])
        if not pmid_list:
            return {"status": "success", "query": query, "articles": []}
        
        # Step 2: Fetch article details
        time.sleep(0.3)  # be polite to NCBI
        self._rate_limit_wait()
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(pmid_list),
            "retmode": "json",
            "email": self.email,
        }
        if self.api_key:
            fetch_params["api_key"] = self.api_key
        
        fetch_response = self._make_request_with_retry(
            f"{self.base_url}/esummary.fcgi",
            fetch_params
        )
        
        if fetch_response is None:
            return {"status": "error", "query": query, "articles": [], "error": "Fetch failed after retries"}
        
        try:
            summary = fetch_response.json()
        except Exception as e:
            logger.error(f"PubMed summary JSON parse error: {e}")
            return {"status": "error", "query": query, "articles": [], "error": str(e)}
        
        result_map = summary.get("result", {})
        articles = []
        for pmid in pmid_list:
            art = result_map.get(pmid, {})
            if not art:
                continue
            articles.append({
                "pmid": pmid,
                "title": art.get("title", "N/A"),
                "authors": [a.get("name") for a in art.get("authors", [])][:5],
                "journal": art.get("fulljournalname", "N/A"),
                "pub_date": art.get("pubdate", "N/A"),
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            })
        
        return {"status": "success", "query": query, "total": len(pmid_list), "articles": articles}


def create_api_clients() -> Dict[str, APIClient]:
    """Create all API clients.
    
    Returns:
        Dictionary of API clients
    """
    return {
        "uniprot": UniProtClient(),
        "string": STRINGAPIClient(),
        "mygene": MyGeneClient(),
        "quickgo": QuickGOClient(),
        "pubmed": PubMedClient(),
    }
