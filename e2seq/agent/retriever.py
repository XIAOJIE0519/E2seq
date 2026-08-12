"""Retriever agent for knowledge retrieval."""

from typing import Any, Dict, List

from e2seq.data.vector_store import get_vector_store
from e2seq.llm import RETRIEVER_PROMPT
from e2seq.utils import get_logger

logger = get_logger(__name__)


class RetrieverAgent:
    """Agent for retrieving knowledge from databases and APIs."""

    def __init__(self, llm, string_db, hmdb_db, trrust_db, gutmgene_db, api_clients):
        """Initialize retriever agent.

        Args:
            llm: LLM provider instance
            string_db: STRING database instance
            hmdb_db: HMDB database instance
            trrust_db: TRRUST database instance
            gutmgene_db: GUTMGENE database instance
            api_clients: Dictionary of API clients
        """
        self.llm = llm
        self.string_db = string_db
        self.hmdb_db = hmdb_db
        self.trrust_db = trrust_db
        self.gutmgene_db = gutmgene_db
        self.api_clients = api_clients

        # Initialize vector store for RAG
        try:
            self.vector_store = get_vector_store()
            logger.info("Vector store initialized for RAG")
        except Exception as e:
            logger.warning(f"Vector store initialization failed: {e}")
            self.vector_store = None

    def retrieve(self, question: str, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve relevant knowledge.

        Args:
            question: User's question
            analysis_results: Results from analysis

        Returns:
            Dictionary with retrieved knowledge
        """
        logger.info("Retrieving knowledge from databases and APIs")

        knowledge = {
            "genes": {},
            "pathways": [],
            "interactions": [],
            "metabolites": [],
            "transcription_factors": [],
            "microbiome": [],
            "similar_cases": [],
            "retrieval_stats": {
                "vector_db_success": False,
                "genes_queried": 0,
                "genes_with_info": 0,
                "databases_queried": []
            }
        }

        # RAG: Search for similar analysis cases from vector database (PRIORITY)
        if self.vector_store:
            try:
                similar_cases = self.vector_store.search_similar_cases(
                    query=question,
                    n_results=3
                )
                knowledge["similar_cases"] = similar_cases
                knowledge["retrieval_stats"]["vector_db_success"] = True
                logger.info(f"[OK / 成功]Vector DB: Found {len(similar_cases)} similar cases")
            except Exception as e:
                logger.warning(f"[WARN / 警告]Vector DB: Search failed - {e}")
        else:
            logger.warning("[WARN / 警告]Vector DB: Not initialized")

        # Extract key genes from results
        key_genes = self._extract_key_genes(analysis_results)

        if not key_genes:
            logger.warning("No key genes found in results")
            return knowledge

        logger.info(f"Retrieving knowledge for {len(key_genes)} key genes")
        knowledge["retrieval_stats"]["genes_queried"] = len(key_genes)

        # Query databases for each key gene with proper connection management
        for gene in key_genes:
            try:
                gene_info = self._retrieve_gene_info(gene)
                if gene_info and self._has_useful_info(gene_info):
                    knowledge["genes"][gene] = gene_info
                    knowledge["retrieval_stats"]["genes_with_info"] += 1
                else:
                    # Still add gene but mark as no info found
                    knowledge["genes"][gene] = {
                        "gene": gene,
                        "status": "no_information_found"
                    }
            except Exception as e:
                logger.error(f"Error retrieving info for {gene}: {e}")
                knowledge["genes"][gene] = {
                    "gene": gene,
                    "status": "retrieval_error",
                    "error": str(e)
                }

        logger.info(f"Knowledge retrieval completed: {knowledge['retrieval_stats']['genes_with_info']}/{knowledge['retrieval_stats']['genes_queried']} genes with information")
        return knowledge

    def _has_useful_info(self, gene_info: Dict[str, Any]) -> bool:
        """Check if gene info contains useful data.

        Args:
            gene_info: Gene information dictionary

        Returns:
            True if has useful information
        """
        return bool(
            gene_info.get("interactions") or
            gene_info.get("metabolites") or
            gene_info.get("regulators") or
            gene_info.get("targets") or
            gene_info.get("microbiome") or
            gene_info.get("uniprot")
        )

    def _extract_key_genes(self, results: Dict[str, Any]) -> List[str]:
        """Extract key genes from analysis results.

        Args:
            results: Analysis results

        Returns:
            List of gene names
        """
        genes = []

        # From DEG results
        if results.get("deg"):
            deg_df = results["deg"]["results"]
            if "names" in deg_df.columns:
                genes.extend(deg_df["names"].head(20).tolist())

        # From network hubs
        if results.get("network"):
            hubs = results["network"].get("hubs", [])
            genes.extend([h[0] for h in hubs])

        # Remove duplicates
        genes = list(set(genes))

        return genes

    def _retrieve_gene_info(self, gene: str) -> Dict[str, Any]:
        """Retrieve comprehensive information for a gene.

        Args:
            gene: Gene symbol

        Returns:
            Dictionary with gene information
        """
        info = {
            "gene": gene,
            "interactions": [],
            "metabolites": [],
            "regulators": [],
            "targets": [],
            "microbiome": [],
            "uniprot": None
        }

        # STRING interactions - use context manager for proper connection handling
        try:
            with self.string_db as db:
                interactions = db.get_interactions(gene, min_score=0.5)
                info["interactions"] = [
                    {
                        "partner": i.get("target_gene") if i.get("source_gene") == gene else i.get("source_gene"),
                        "score": i.get("score", 0)
                    }
                    for i in interactions[:10]
                ]
                if interactions:
                    logger.debug(f"[OK / 成功]STRING: {len(interactions)} interactions for {gene}")
        except Exception as e:
            logger.debug(f"[WARN / 警告]STRING query failed for {gene}: {e}")

        # HMDB metabolites
        try:
            with self.hmdb_db as db:
                metabolites = db.get_metabolites(gene)
                info["metabolites"] = [
                    {
                        "id": m.get("metabolite_id"),
                        "name": m.get("metabolite_name", "Unknown")
                    }
                    for m in metabolites[:5]
                ]
                if metabolites:
                    logger.debug(f"[OK / 成功]HMDB: {len(metabolites)} metabolites for {gene}")
        except Exception as e:
            logger.debug(f"[WARN / 警告]HMDB query failed for {gene}: {e}")

        # TRRUST regulators
        try:
            with self.trrust_db as db:
                regulators = db.get_regulators(gene)
                info["regulators"] = [
                    {
                        "tf": r.get("tf"),
                        "mode": r.get("mode", "Unknown")
                    }
                    for r in regulators[:5]
                ]
                if regulators:
                    logger.debug(f"[OK / 成功]TRRUST: {len(regulators)} regulators for {gene}")
        except Exception as e:
            logger.debug(f"[WARN / 警告]TRRUST regulator query failed for {gene}: {e}")

        # TRRUST targets (if gene is a TF)
        try:
            with self.trrust_db as db:
                targets = db.get_targets(gene)
                info["targets"] = [
                    {
                        "gene": t.get("target_gene"),
                        "mode": t.get("mode", "Unknown")
                    }
                    for t in targets[:5]
                ]
                if targets:
                    logger.debug(f"[OK / 成功]TRRUST: {len(targets)} targets for {gene}")
        except Exception as e:
            logger.debug(f"[WARN / 警告]TRRUST target query failed for {gene}: {e}")

        # GUTMGENE microbiome
        try:
            with self.gutmgene_db as db:
                microbes = db.get_microbes(gene)
                info["microbiome"] = [
                    {
                        "microbe": m.get("gut_microbiota"),
                        "condition": m.get("condition", "Unknown")
                    }
                    for m in microbes[:3]
                ]
                if microbes:
                    logger.debug(f"[OK / 成功]GUTMGENE: {len(microbes)} microbes for {gene}")
        except Exception as e:
            logger.debug(f"[WARN / 警告]GUTMGENE query failed for {gene}: {e}")

        # UniProt API
        try:
            uniprot_data = self.api_clients["uniprot"].get_protein_info(gene)
            if uniprot_data and "results" in uniprot_data and len(uniprot_data["results"]) > 0:
                entry = uniprot_data["results"][0]
                comments = entry.get("comments", [])
                function_text = ""
                for comment in comments:
                    if comment.get("commentType") == "FUNCTION":
                        texts = comment.get("texts", [])
                        if texts:
                            function_text = texts[0].get("value", "")[:300]
                            break
                info["uniprot"] = {
                    "accession": entry.get("primaryAccession"),
                    "protein_name": entry.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value", ""),
                    "function": function_text
                }
                logger.debug(f"[OK / 成功]UniProt: retrieved for {gene}")
        except Exception as e:
            logger.debug(f"[WARN / 警告]UniProt query failed for {gene}: {e}")

        # MyGene —gene summary, type, genomic pos
        try:
            mg = self.api_clients["mygene"].get_gene_info(gene)
            if mg and mg.get("status") == "success":
                info["mygene"] = {"symbol": mg.get("symbol"), "name": mg.get("name"),
                                   "entrez_id": mg.get("entrez_id"), "type": mg.get("type_of_gene")}
                logger.debug(f"[OK / 成功]MyGene: retrieved for {gene}")
        except Exception as e:
            logger.debug(f"[WARN / 警告]MyGene query failed for {gene}: {e}")

        # Ensembl —gene ID, biotype
        try:
            ens = self.api_clients["ensembl"].get_gene_info(gene)
            if ens and ens.get("status") == "success":
                info["ensembl"] = {"ensembl_id": ens.get("ensembl_id"),
                                    "description": ens.get("description", "")[:200],
                                    "biotype": ens.get("biotype")}
                logger.debug(f"[OK / 成功]Ensembl: retrieved for {gene}")
        except Exception as e:
            logger.debug(f"[WARN / 警告]Ensembl query failed for {gene}: {e}")

        # QuickGO —GO terms
        try:
            go = self.api_clients["quickgo"].get_go_terms(gene)
            if go and go.get("status") == "success" and go.get("total_annotations", 0) > 0:
                anns = go.get("annotations", [])
                info["go_terms"] = [{"go_id": a.get("go_id"), "aspect": a.get("go_aspect")} for a in anns[:8]]
                logger.debug(f"[OK / 成功]QuickGO: {len(info['go_terms'])} GO terms for {gene}")
        except Exception as e:
            logger.debug(f"[WARN / 警告]QuickGO query failed for {gene}: {e}")

        # ChEMBL —drug targets
        try:
            ch = self.api_clients["chembl"].search_target(gene)
            targets = ch.get("targets", []) if isinstance(ch, dict) else []
            if targets:
                info["chembl_targets"] = [{"chembl_id": t.get("target_chembl_id"),
                                            "name": t.get("pref_name", "")[:100]} for t in targets[:5]]
                logger.debug(f"[OK / 成功]ChEMBL: {len(targets)} targets for {gene}")
        except Exception as e:
            logger.debug(f"[WARN / 警告]ChEMBL query failed for {gene}: {e}")

        # GTEx —tissue expression
        try:
            gtex = self.api_clients["gtex"].query(gene, max_results=5)
            if gtex and gtex.get("status") in {"ok", "success"} and (gtex.get("count", 0) or gtex.get("total", 0)) > 0:
                info["gtex"] = {"total_tissues": gtex.get("count", gtex.get("total", 0)),
                                 "top_tissues": [{"tissue": r.get("tissue"), "median": r.get("median_expression")}
                                                  for r in gtex.get("records", [])[:5]]}
                logger.debug(f"[OK / 成功]GTEx: {gtex.get('total')} tissues for {gene}")
        except Exception as e:
            logger.debug(f"[WARN / 警告]GTEx query failed for {gene}: {e}")

        # HumanBase —tissue network
        try:
            hb = None  # HumanBase public REST endpoint was removed; do not use fallbacks under its name.
            if hb and hb.get("status") == "success" and hb.get("total", 0) > 0:
                info["humanbase"] = {"tissue": "brain", "network_genes": [g.get("gene") for g in hb.get("network_genes", [])[:10]]}
                logger.debug(f"[OK / 成功]HumanBase: {hb.get('total')} network genes for {gene}")
        except Exception as e:
            logger.debug(f"[WARN / 警告]HumanBase query failed for {gene}: {e}")

        # GWAS —trait associations
        try:
            gw = self.api_clients["gwas"].get_gene_trait_associations(gene)
            if gw and gw.get("status") == "success" and gw.get("total", 0) > 0:
                assocs = gw.get("associations", [])
                info["gwas"] = [{"trait": a.get("trait"), "pvalue": a.get("p_value")} for a in assocs[:5]]
                logger.debug(f"[OK / 成功]GWAS: {gw.get('total')} associations for {gene}")
        except Exception as e:
            logger.debug(f"[WARN / 警告]GWAS query failed for {gene}: {e}")

        # PubMed —literature
        try:
            pm = self.api_clients["pubmed"].search(gene + " disease", max_results=3)
            if pm and pm.get("status") == "success" and pm.get("total_count", 0) > 0:
                info["pubmed"] = {"total": pm.get("total_count"), "pmids": pm.get("pmid_list", [])[:3]}
                logger.debug(f"[OK / 成功]PubMed: {pm.get('total_count')} articles for {gene}")
        except Exception as e:
            logger.debug(f"[WARN / 警告]PubMed query failed for {gene}: {e}")

        # EuropePMC —literature
        try:
            ep = self.api_clients["europepmc"].search(gene + " disease", max_results=3)
            if ep and ep.get("status") == "success" and ep.get("total_hits", 0) > 0:
                info["europepmc"] = {"total": ep.get("total_hits"),
                                      "articles": [{"pmid": a.get("pmid"), "title": a.get("title", "")[:100]}
                                                   for a in ep.get("articles", [])[:3]]}
                logger.debug(f"[OK / 成功]EuropePMC: {ep.get('total_hits')} articles for {gene}")
        except Exception as e:
            logger.debug(f"[WARN / 警告]EuropePMC query failed for {gene}: {e}")

        # CIViC —clinical variants
        try:
            cv = self.api_clients["civic"].search_variants(gene)
            if cv and cv.get("status") == "success" and cv.get("total", 0) > 0:
                info["civic"] = {"total_variants": cv.get("total"),
                                  "variants": [{"name": v.get("name"), "disease": v.get("disease", "")} for v in cv.get("variants", [])[:5]]}
                logger.debug(f"[OK / 成功]CIViC: {cv.get('total')} variants for {gene}")
        except Exception as e:
            logger.debug(f"[WARN / 警告]CIViC query failed for {gene}: {e}")

        # Alliance —homologs
        try:
            al = self.api_clients["alliance"].get_homologs(gene)
            if al and al.get("status") == "success" and al.get("total", 0) > 0:
                info["alliance"] = {"total_homologs": al.get("total"),
                                     "homologs": [{"species": h.get("species"), "symbol": h.get("symbol")} for h in al.get("homologs", [])[:5]]}
                logger.debug(f"[OK / 成功]Alliance: {al.get('total')} homologs for {gene}")
        except Exception as e:
            logger.debug(f"[WARN / 警告]Alliance query failed for {gene}: {e}")

        return info
