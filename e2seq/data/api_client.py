"""API client for external bioinformatics databases."""

import asyncio
import time
from typing import Any, Dict, List, Optional

import aiohttp
import requests

from e2seq.utils import get_config, get_logger

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
    """PubMed API client."""

    def __init__(self):
        super().__init__("https://eutils.ncbi.nlm.nih.gov/entrez/eutils")
        self.email = "e2seq@example.com"

    def search(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search PubMed."""
        params = {"db": "pubmed", "term": query, "retmax": max_results, "retmode": "json", "email": self.email}
        return self.get("esearch.fcgi", params)

    def search_and_get_details(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search PubMed and return article summaries."""
        try:
            search_result = self.search(query, max_results)
            pmid_list = search_result.get("esearchresult", {}).get("idlist", [])
            if not pmid_list:
                return {"status": "success", "query": query, "articles": []}

            time.sleep(0.3)  # be polite to NCBI
            params = {
                "db": "pubmed",
                "id": ",".join(pmid_list),
                "retmode": "json",
                "email": self.email,
            }
            summary = self.get("esummary.fcgi", params)
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
        except Exception as e:
            logger.error(f"PubMed search_and_get_details failed: {e}")
            return {"status": "error", "query": query, "articles": [], "error": str(e)}


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
