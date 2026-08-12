"""Enhanced API client integrating standalone API modules."""

import asyncio
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp
import requests

# Add api folder to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "api"))

from e2seq.utils import get_config, get_logger

logger = get_logger(__name__)

# Import standalone API modules
try:
    from uniprot_api import UniProtAPI
    from string_api import STRING_API as STRINGAPI
    from quickgo_api import QuickGO_API as QuickGOAPI
    from mygene_api import MyGene_API as MyGeneAPI
    from pubmed_api import PubMed_API as PubMedAPI
    from pubchem_api import PubChem_API as PubChemAPI
    from chembl_api import ChEMBL_API as ChEMBLAPI
    from ensembl_api import Ensembl_API as EnsemblAPI
    from europepmc_api import EuropePMC_API as EuropePMCAPI
    from gtex_api import GTExAPI
    from humanbase_api import HumanBaseAPI
    from gwas_catalog_api import GWASCatalogAPI
    from biogrid_api import BioGRIDAPI
    from civic_api import CIViCAPI
    from alliance_api import AllianceAPI
    STANDALONE_APIS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Standalone API modules not available: {e}")
    STANDALONE_APIS_AVAILABLE = False


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


class EnhancedUniProtClient(APIClient):
    """Enhanced UniProt API client."""

    def __init__(self):
        super().__init__("https://rest.uniprot.org/uniprotkb")
        self.standalone = None
        if STANDALONE_APIS_AVAILABLE:
            try:
                self.standalone = UniProtAPI()
            except Exception:
                pass

    def get_protein_info(self, gene: str) -> Dict[str, Any]:
        """Get protein information for a gene - always use REST for full data."""
        import requests as _req
        try:
            r = _req.get(
                "https://rest.uniprot.org/uniprotkb/search",
                params={"query": f"gene:{gene} AND organism_id:9606", "format": "json"},
                timeout=15
            )
            rest_result = r.json()
            if rest_result.get("results"):
                return rest_result
        except Exception as e:
            logger.warning(f"UniProt REST failed for {gene}: {e}")
        # Fallback: standalone simplified structure
        if self.standalone:
            try:
                result = self.standalone.search_by_gene(gene, organism="human")
                if result and result.get("results"):
                    converted = []
                    for entry in result["results"]:
                        fn = entry.get("function", "")
                        converted.append({
                            "primaryAccession": entry.get("accession"),
                            "proteinDescription": {"recommendedName": {"fullName": {"value": entry.get("protein_name", "")}}},
                            "comments": [{"commentType": "FUNCTION", "textes": [{"value": fn}]}] if fn else []
                        })
                    return {"results": converted}
            except Exception as e:
                logger.warning(f"Standalone UniProt failed for {gene}: {e}")
        return {"results": []}


class EnhancedSTRINGAPIClient(APIClient):
    """Enhanced STRING API client — uses LOCAL SQLite DB exclusively."""

    def __init__(self):
        super().__init__("https://string-db.org/api/json")
        try:
            from e2seq.data.local_db import STRINGDatabase
            self._local_db = STRINGDatabase()
        except Exception as e:
            logger.warning(f"Could not init local STRING DB: {e}")
            self._local_db = None

    def get_interactions(self, genes: List[str], species: int = 9606) -> Dict[str, Any]:
        """Get protein interactions from LOCAL STRING SQLite DB."""
        if self._local_db is not None:
            try:
                all_interactions = []
                seen = set()
                for g in genes:
                    rows = self._local_db.get_interactions(g, min_score=0.4)
                    for row in rows:
                        a = row.get('source_gene', '')
                        b = row.get('target_gene', '')
                        key = (min(a, b), max(a, b))
                        if key not in seen:
                            seen.add(key)
                            all_interactions.append({
                                'preferredName_A': a,
                                'preferredName_B': b,
                                'score': row.get('weight', row.get('score', row.get('combined_score', 0))),
                            })
                # sort by score desc, limit 20 per gene
                all_interactions.sort(key=lambda x: x.get('score', 0), reverse=True)
                return all_interactions[:20 * len(genes)]
            except Exception as e:
                logger.warning(f"Local STRING DB failed, using online fallback: {e}")

        # Online fallback only if local DB unavailable
        params = {"identifiers": "%0d".join(genes), "species": species}
        return self.get("network", params)


class EnhancedMyGeneClient(APIClient):
    """Enhanced MyGene.info API client."""

    def __init__(self):
        super().__init__("https://mygene.info/v3")
        if STANDALONE_APIS_AVAILABLE:
            self.standalone = MyGeneAPI()

    def get_gene_info(self, gene: str) -> Dict[str, Any]:
        """Get gene information."""
        if STANDALONE_APIS_AVAILABLE and hasattr(self, 'standalone'):
            try:
                return self.standalone.query_gene(gene, species="human")
            except Exception as e:
                logger.warning(f"Standalone API failed, using fallback: {e}")

        return self.get(f"query?q={gene}&species=human")


class EnhancedQuickGOClient(APIClient):
    """Enhanced QuickGO API client."""

    def __init__(self):
        super().__init__("https://www.ebi.ac.uk/QuickGO/services")
        if STANDALONE_APIS_AVAILABLE:
            self.standalone = QuickGOAPI()

    def get_go_terms(self, gene: str) -> Dict[str, Any]:
        """Get GO terms for a gene (resolves gene symbol to UniProt ID first)."""
        import requests as _req
        # Step 1: resolve gene symbol -> UniProt accession via MyGene
        uniprot_id = gene
        try:
            r = _req.get(
                "https://mygene.info/v3/query",
                params={"q": gene, "species": "human", "fields": "uniprot"},
                timeout=10
            )
            if r.status_code == 200:
                hits = r.json().get("hits", [])
                if hits:
                    up = hits[0].get("uniprot", {})
                    sp = up.get("Swiss-Prot", "")
                    if sp:
                        uniprot_id = sp if isinstance(sp, str) else sp[0]
        except Exception:
            pass

        if STANDALONE_APIS_AVAILABLE and hasattr(self, 'standalone'):
            try:
                return self.standalone.get_go_annotations(uniprot_id)
            except Exception as e:
                logger.warning(f"Standalone API failed, using fallback: {e}")

        params = {"geneProductId": uniprot_id, "limit": 50, "taxonId": 9606}
        return self.get("annotation/search", params)


class EnhancedPubMedClient(APIClient):
    """Enhanced PubMed API client with rate limiting and retry logic."""

    def __init__(self):
        super().__init__("https://eutils.ncbi.nlm.nih.gov/entrez/eutils")
        self._standalone = None
        if STANDALONE_APIS_AVAILABLE:
            try:
                self._standalone = PubMedAPI()
                logger.info("[PubMed] Using standalone API with rate limiting and retry")
            except Exception as e:
                logger.warning(f"[PubMed] Failed to init standalone API: {e}")

    def search(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search PubMed."""
        if self._standalone:
            try:
                return self._standalone.search_articles(query, max_results=max_results)
            except Exception as e:
                logger.warning(f"[PubMed] Standalone search failed, using fallback: {e}")

        params = {"db": "pubmed", "term": query, "retmax": max_results, "retmode": "json"}
        return self.get("esearch.fcgi", params)

    def search_and_get_details(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Search PubMed and fetch article details with rate limiting and retry."""
        # Use standalone API which has proper rate limiting and retry logic
        if self._standalone:
            try:
                return self._standalone.search_and_get_details(query, max_results=max_results)
            except Exception as e:
                logger.warning(f"[PubMed] Standalone failed, using fallback: {e}")

        # Fallback: direct requests WITHOUT rate limiting (for backward compatibility)
        import requests as _req
        try:
            # Step 1: search
            search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            r = _req.get(search_url, params={
                "db": "pubmed", "term": query,
                "retmax": max_results, "retmode": "json"
            }, timeout=15)
            ids = r.json().get("esearchresult", {}).get("idlist", [])
            if not ids:
                return {"articles": []}

            # Step 2: fetch summaries
            summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            r2 = _req.get(summary_url, params={
                "db": "pubmed", "id": ",".join(ids), "retmode": "json"
            }, timeout=15)
            result = r2.json().get("result", {})

            articles = []
            for pmid in ids:
                doc = result.get(pmid, {})
                if not doc:
                    continue
                articles.append({
                    "pmid": pmid,
                    "title": doc.get("title", ""),
                    "journal": doc.get("source", ""),
                    "pub_date": doc.get("pubdate", ""),
                    "authors": ", ".join([a.get("name","") for a in doc.get("authors", [])[:3]]),
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                })
            return {"articles": articles}
        except Exception as e:
            logger.warning(f"[PubMed] search_and_get_details failed: {e}")
            return {"articles": []}


class EnhancedPubChemClient(APIClient):
    """Enhanced PubChem API client."""

    def __init__(self):
        super().__init__("https://pubchem.ncbi.nlm.nih.gov/rest/pug")
        if STANDALONE_APIS_AVAILABLE:
            self.standalone = PubChemAPI()

    def get_compound_info(self, compound_name: str) -> Dict[str, Any]:
        """Get compound information."""
        if STANDALONE_APIS_AVAILABLE and hasattr(self, 'standalone'):
            try:
                return self.standalone.search_by_name(compound_name)
            except Exception as e:
                logger.warning(f"Standalone API failed, using fallback: {e}")

        return self.get(f"compound/name/{compound_name}/JSON")


class EnhancedChEMBLClient(APIClient):
    """Enhanced ChEMBL API client."""

    def __init__(self):
        super().__init__("https://www.ebi.ac.uk/chembl/api/data")
        if STANDALONE_APIS_AVAILABLE:
            self.standalone = ChEMBLAPI()

    def search_target(self, target_name: str) -> Dict[str, Any]:
        """Search for drug targets."""
        # Note: ChEMBL_API standalone only has search_compound, not search_target
        # Use REST API directly for target search
        params = {"q": target_name, "format": "json"}
        return self.get("target/search", params)


class EnhancedEnsemblClient(APIClient):
    """Enhanced Ensembl API client."""

    def __init__(self):
        super().__init__("https://rest.ensembl.org")
        if STANDALONE_APIS_AVAILABLE:
            self.standalone = EnsemblAPI()

    def get_gene_info(self, gene_id: str) -> Dict[str, Any]:
        """Get gene information from Ensembl."""
        if STANDALONE_APIS_AVAILABLE and hasattr(self, 'standalone'):
            try:
                return self.standalone.lookup_gene(gene_id)
            except Exception as e:
                logger.warning(f"Standalone API failed, using fallback: {e}")

        return self.get(f"lookup/symbol/homo_sapiens/{gene_id}?content-type=application/json")


class EnhancedEuropePMCClient(APIClient):
    """Enhanced Europe PMC API client."""

    def __init__(self):
        super().__init__("https://www.ebi.ac.uk/europepmc/webservices/rest")
        if STANDALONE_APIS_AVAILABLE:
            self.standalone = EuropePMCAPI()

    def search(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search Europe PMC."""
        if STANDALONE_APIS_AVAILABLE and hasattr(self, 'standalone'):
            try:
                return self.standalone.search_articles(query, page_size=max_results)
            except Exception as e:
                logger.warning(f"Standalone API failed, using fallback: {e}")

        params = {"query": query, "pageSize": max_results, "format": "json"}
        return self.get("search", params)


class EnhancedGTExClient:
    """Enhanced GTEx API client - 基因在各组织的表达数据"""

    def __init__(self):
        if STANDALONE_APIS_AVAILABLE:
            self.standalone = GTExAPI()

    def get_gene_expression(self, gene: str, max_results: int = 50) -> Dict[str, Any]:
        """获取基因在各组织的表达数据"""
        if STANDALONE_APIS_AVAILABLE and hasattr(self, 'standalone'):
            try:
                return self.standalone.get_gene_expression(gene, max_results)
            except Exception as e:
                logger.warning(f"GTEx standalone failed for {gene}: {e}")
        # Fallback: two-step GTEx v2 lookup
        try:
            import requests as _req
            base = "https://gtexportal.org/api/v2"
            h = {"Accept": "application/json"}
            # Step 1: resolve gencodeId
            ref = _req.get(base+"/reference/gene", params={"geneId": gene}, headers=h, timeout=15)
            gencode_id = None
            if ref.status_code == 200:
                data = ref.json().get("data", [])
                if data:
                    gencode_id = data[0].get("gencodeId", "")
            if not gencode_id:
                return {"status": "success", "gene": gene, "total": 0, "records": [], "note": "Gene not found in GTEx"}
            # Step 2: get expression
            r = _req.get(base+"/expression/medianGeneExpression",
                params={"gencodeId": gencode_id, "datasetId": "gtex_v8"}, headers=h, timeout=20)
            if r.status_code == 200:
                raw = r.json().get("data", [])
                records = [{"gene": gene, "tissue": x.get("tissueSiteDetailId",""),
                            "median_expression": x.get("median"), "unit": "TPM"} for x in raw[:max_results]]
                records.sort(key=lambda x: x.get("median_expression") or 0, reverse=True)
                return {"status": "success", "gene": gene, "gencodeId": gencode_id,
                        "total": len(records), "records": records}
        except Exception as e:
            logger.warning(f"GTEx REST fallback failed for {gene}: {e}")
        return {"status": "error", "error": "GTEx API unavailable"}


class EnhancedHumanBaseClient:
    """Enhanced HumanBase API client - 基因组织特异性表达和功能网络"""

    def __init__(self):
        if STANDALONE_APIS_AVAILABLE:
            self.standalone = HumanBaseAPI()

    def get_gene_expression(self, gene: str, max_results: int = 50) -> Dict[str, Any]:
        """获取基因在各组织的表达特异性"""
        if STANDALONE_APIS_AVAILABLE and hasattr(self, 'standalone'):
            try:
                return self.standalone.get_gene_expression(gene, max_results)
            except Exception as e:
                logger.warning(f"HumanBase standalone failed for {gene}: {e}")
        return {"status": "error", "error": "HumanBase API unavailable"}

    def get_tissue_network(self, gene: str, tissue: str = "brain") -> Dict[str, Any]:
        """获取特定组织的基因功能网络"""
        if STANDALONE_APIS_AVAILABLE and hasattr(self, 'standalone'):
            try:
                return self.standalone.get_tissue_network(gene, tissue)
            except Exception as e:
                logger.warning(f"HumanBase get_tissue_network failed: {e}")
        return {"status": "error", "error": "HumanBase API unavailable"}

    def search_genes(self, query: str, max_results: int = 20) -> Dict[str, Any]:
        """搜索基因"""
        if STANDALONE_APIS_AVAILABLE and hasattr(self, 'standalone'):
            try:
                return self.standalone.search_genes(query, max_results)
            except Exception as e:
                logger.warning(f"HumanBase search failed: {e}")
        return {"status": "error", "error": "HumanBase API unavailable"}


class EnhancedGWASCatalogClient:
    """Enhanced GWAS Catalog API client - 基因/SNP 与性状/疾病的大规模 GWAS 证据"""

    def __init__(self):
        if STANDALONE_APIS_AVAILABLE:
            self.standalone = GWASCatalogAPI()

    def get_gene_trait_associations(self, gene: str, max_results: int = 20) -> Dict[str, Any]:
        """获取某基因相关的疾病/表型 GWAS 证据"""
        if STANDALONE_APIS_AVAILABLE and hasattr(self, 'standalone'):
            try:
                return self.standalone.get_gene_trait_associations(gene, max_results)
            except Exception as e:
                logger.warning(f"GWASCatalog standalone failed for {gene}: {e}")
        # Fallback: 直接 REST
        try:
            import requests as _req
            r = _req.get(
                "https://www.ebi.ac.uk/gwas/rest/api/v2/associations",
                params={"geneSymbol": gene, "size": min(max_results, 100)},
                headers={"Accept": "application/json", "User-Agent": "Python/E2seq"},
                timeout=30
            )
            if r.status_code == 200:
                data = r.json()
                associations = data.get("_embedded", {}).get("associations", [])
                return {"status": "success", "gene": gene, "total": len(associations), "associations": associations}
        except Exception as e:
            logger.warning(f"GWASCatalog REST failed for {gene}: {e}")
        return {"status": "error", "error": "GWAS Catalog API unavailable"}


class EnhancedBioGRIDClient:
    """Enhanced BioGRID API client - 实验验证的蛋白互作"""

    def __init__(self):
        if STANDALONE_APIS_AVAILABLE:
            self.standalone = BioGRIDAPI()

    def get_interactions(self, genes: List[str], max_results: int = 100) -> Dict[str, Any]:
        """获取蛋白互作网络"""
        if STANDALONE_APIS_AVAILABLE and hasattr(self, 'standalone'):
            try:
                return self.standalone.get_interactions(genes, max_results)
            except Exception as e:
                logger.warning(f"BioGRID standalone failed: {e}")
        # Fallback: 直接 REST
        try:
            import requests as _req
            r = _req.get(
                "https://webservice.thebiogrid.org/interactions",
                params={
                    "accessKey": "1647cceb86ebd3fb64caf6e20048e6bc",
                    "geneList": "|".join(genes),
                    "organism": "9606",
                    "max": min(max_results, 10000),
                    "format": "json"
                },
                timeout=60
            )
            if r.status_code == 200:
                data = r.json()
                interactions = []
                for interaction_id, hit in list(data.items())[:max_results]:
                    if isinstance(hit, dict):
                        interactions.append({
                            "gene_a": hit.get("OFFICIAL_SYMBOL_A", ""),
                            "gene_b": hit.get("OFFICIAL_SYMBOL_B", ""),
                            "experimental_system": hit.get("EXPERIMENTAL_SYSTEM", ""),
                            "pmid": hit.get("PUBMED_ID", ""),
                        })
                return {"status": "success", "genes": genes, "total": len(interactions), "interactions": interactions}
        except Exception as e:
            logger.warning(f"BioGRID REST failed: {e}")
        return {"status": "error", "error": "BioGRID API unavailable"}


class EnhancedCIViCClient:
    """Enhanced CIViC API client - 癌症变异临床解释知识库"""

    def __init__(self):
        if STANDALONE_APIS_AVAILABLE:
            self.standalone = CIViCAPI()

    def search_variants(self, gene: str, max_results: int = 20) -> Dict[str, Any]:
        """搜索基因相关的变异"""
        if STANDALONE_APIS_AVAILABLE and hasattr(self, 'standalone'):
            try:
                return self.standalone.search_variants(gene, max_results)
            except Exception as e:
                logger.warning(f"CIViC standalone failed for {gene}: {e}")
        return {"status": "error", "error": "CIViC API unavailable"}


class EnhancedAllianceClient:
    """Enhanced Alliance of Genome Resources API client - 模式生物、同源基因、跨物种证据"""

    def __init__(self):
        if STANDALONE_APIS_AVAILABLE:
            self.standalone = AllianceAPI()

    def search_cross_species(self, query: str) -> Dict[str, Any]:
        """跨物种搜索"""
        if STANDALONE_APIS_AVAILABLE and hasattr(self, 'standalone'):
            try:
                return self.standalone.search_cross_species(query)
            except Exception as e:
                logger.warning(f"Alliance search_cross_species failed: {e}")
        return {"status": "error", "error": "Alliance API unavailable"}

    def get_homologs(self, gene: str, species: str = "human") -> Dict[str, Any]:
        """获取基因的同源基因"""
        if STANDALONE_APIS_AVAILABLE and hasattr(self, 'standalone'):
            try:
                return self.standalone.get_homologs(gene, species)
            except Exception as e:
                logger.warning(f"Alliance get_homologs failed: {e}")
        return {"status": "error", "error": "Alliance API unavailable"}


class EnhancedVerifiedSourceClient:
    """Status-aware adapter for a maintained public knowledge source."""

    def __init__(self, source: str):
        from e2seq.data.knowledge_sources import KnowledgeSourceClient
        self.source = str(source).lower()
        self.client = KnowledgeSourceClient(timeout=20)

    def query(self, gene: str, max_results: int = 20) -> Dict[str, Any]:
        return self.client.query(self.source, gene, max_results=max_results)


def create_api_clients() -> Dict[str, APIClient]:
    """Create all API clients with enhanced functionality.

    Returns:
        Dictionary of API clients
    """
    logger.info(f"Creating API clients (standalone APIs available: {STANDALONE_APIS_AVAILABLE})")

    clients = {
        # 核心基因/蛋白 API
        "uniprot": EnhancedUniProtClient(),
        "mygene": EnhancedMyGeneClient(),
        "ensembl": EnhancedEnsemblClient(),

        # 蛋白互作网络
        "string": EnhancedSTRINGAPIClient(),

        # GO 功能注释
        "quickgo": EnhancedQuickGOClient(),

        # 文献检索
        "pubmed": EnhancedPubMedClient(),
        "europepmc": EnhancedEuropePMCClient(),

        # 化合物/药物
        "pubchem": EnhancedPubChemClient(),
        "chembl": EnhancedChEMBLClient(),

        # GWAS
        "gwas": EnhancedGWASCatalogClient(),

        # 癌症变异
        "civic": EnhancedCIViCClient(),

        # 跨物种
        "alliance": EnhancedAllianceClient(),
    }
    # These sources share one status-aware implementation so an HTTP error,
    # missing credential, and gene-level no-record result remain distinguishable.
    clients.update({
        source: EnhancedVerifiedSourceClient(source)
        for source in (
            "gtex", "hpa", "opentargets", "alliance",
            "cbioportal", "omnipath", "intact",
            "humanbase", "clinicaltrials",
        )
    })
    # Replace the legacy Alliance wrapper with the verified endpoint too.
    clients["alliance"] = EnhancedVerifiedSourceClient("alliance")
    return clients
