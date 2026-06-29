"""Agent orchestrator for E2sc with streaming support."""

from typing import Any, Dict, Generator, List, Optional

from anndata import AnnData

from e2sc.agent.enhanced_planner import EnhancedPlannerAgent
from e2sc.agent.memory import get_memory_manager
from e2sc.agent.planner import PlannerAgent
from e2sc.agent.retriever import RetrieverAgent
from e2sc.agent.synthesizer import SynthesizerAgent
from e2sc.data.api_client import create_api_clients
from e2sc.data.local_db import GUTMGENEDatabase, HMDBDatabase, STRINGDatabase, TRRUSTDatabase
from e2sc.llm import create_llm_provider
from e2sc.tools import EnrichmentAnalyzer, NetworkAnalyzer, ScancpyTools, Visualizer
from e2sc.utils import get_config, get_logger, get_security_manager

logger = get_logger(__name__)


class E2scAgent:
    """Main agent orchestrator for E2sc with streaming support."""
    
    def __init__(
        self,
        adata: Optional[AnnData] = None,
        llm_provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        """Initialize E2sc agent."""
        logger.info("Initializing E2sc Agent")
        
        self.config = get_config()
        self.security = get_security_manager()

        provider = llm_provider or self.config.llm.provider

        # key 优先用调用方传入的明文，否则从配置读取并解密
        if api_key:
            key = api_key  # 调用方（server.py）已传入明文，无需再解密
        elif self.config.llm.api_key:
            key = self.security.decrypt(self.config.llm.api_key)  # 从配置读取时需要解密
        else:
            key = ""
        
        self.llm = create_llm_provider(
            provider=provider,
            api_key=key,
            model=model or self.config.llm.model,
            temperature=self.config.llm.temperature,
            max_tokens=self.config.llm.max_tokens,
            thinking_enabled=self.config.llm.thinking_enabled,
            thinking_effort=self.config.llm.thinking_effort or "high",
        )
        
        self.adata = adata
        self.scanpy_tools = ScancpyTools(adata) if adata else None
        self.enrichment = EnrichmentAnalyzer()
        self.network = NetworkAnalyzer()
        self.visualizer = Visualizer()
        
        self.string_db = STRINGDatabase()
        self.hmdb_db = HMDBDatabase()
        self.trrust_db = TRRUSTDatabase()
        self.gutmgene_db = GUTMGENEDatabase()
        
        self.api_clients = create_api_clients()
        
        self.planner = PlannerAgent(self.llm)
        self.retriever = RetrieverAgent(
            self.llm, self.string_db, self.hmdb_db,
            self.trrust_db, self.gutmgene_db, self.api_clients
        )
        self.synthesizer = SynthesizerAgent(self.llm)
        
        self.history: List[Dict[str, str]] = []
        
        logger.info("E2sc Agent initialized successfully")
    
    def load_data(self, adata: AnnData) -> None:
        """Load single-cell data."""
        logger.info(f"Loading data: {adata.n_obs} cells, {adata.n_vars} genes")
        self.adata = adata
        self.scanpy_tools = ScancpyTools(adata)
    
    def chat(self, message: str, stream: bool = False):
        """Chat with the agent.
        
        Args:
            message: User message
            stream: Whether to stream the response
            
        Returns:
            Response dictionary or generator
        """
        logger.info(f"User message: {message}")
        self.history.append({"role": "user", "content": message})
        
        if self.adata is None:
            # 没有数据时，先查询本地数据库，将检索结果注入 system prompt
            rag_context = ""
            try:
                if hasattr(self, 'retriever') and self.retriever:
                    db_results = self.retriever.retrieve(message, dataset_info={})
                    if db_results:
                        rag_lines = [f"[{r.get('source','db')}] {r.get('content', r.get('text', str(r)))}" for r in db_results[:8]]
                        rag_context = "\n".join(rag_lines)
            except Exception as re:
                logger.warning(f"RAG context retrieval failed: {re}")

            system_prompt = (
                "You are E2sc, an AI assistant specialized in single-cell RNA sequencing (scRNA-seq) analysis. "
                "You have access to local bioinformatics databases including STRING (protein interactions), "
                "HMDB (metabolites), TRRUST (transcription factors), and GUTMGENE (gut microbiome). "
                "Currently no h5ad dataset is loaded."
            )
            if rag_context:
                system_prompt += f"\n\n=== Local Database Context ===\n{rag_context}\n=== End Context ==="

            messages = [{"role": "system", "content": system_prompt}]
            for h in self.history[-6:]:
                if h.get("role") != "system":
                    messages.append(h)
            messages.append({"role": "user", "content": message})

            try:
                reply = self.llm.chat(messages)
            except Exception as e:
                reply = f"LLM 调用失败: {str(e)}"
            response = {
                "text": reply,
                "plots": [],
                "data": {},
                "thinking": [{"step": "RAG", "content": f"Retrieved context: {len(rag_context)} chars"}]
            }
            self.history.append({"role": "assistant", "content": response["text"]})
            return response
        
        if stream:
            return self._chat_stream(message)
        else:
            return self._chat_complete(message)
    
    def _chat_complete(self, message: str) -> Dict[str, Any]:
        """Complete chat response."""
        try:
            dataset_info = self.scanpy_tools.get_dataset_info()
            plan = self.planner.create_plan(message, dataset_info)
            
            thinking_steps = [
                {"step": "Planning", "content": f"Created {len(plan.get('steps', []))} analysis steps"}
            ]
            
            results = self._execute_plan(plan)
            thinking_steps.append({"step": "Execution", "content": "Completed analysis"})
            
            # CRITICAL: Retrieve knowledge from RAG databases BEFORE synthesis
            knowledge = self.retriever.retrieve(message, results)
            retrieval_stats = knowledge.get("retrieval_stats", {})
            thinking_steps.append({
                "step": "Retrieval", 
                "content": f"Retrieved info for {retrieval_stats.get('genes_with_info', 0)}/{retrieval_stats.get('genes_queried', 0)} genes. Vector DB: {'✓' if retrieval_stats.get('vector_db_success') else '✗'}"
            })
            
            # Synthesize with retrieved knowledge
            response = self.synthesizer.synthesize(message, results, knowledge)
            response["thinking"] = thinking_steps
            
            # Validate response has grounding in retrieved knowledge
            if not knowledge.get("genes") and not knowledge.get("similar_cases"):
                logger.warning("No knowledge retrieved - response may lack grounding")
                response["warning"] = "知识库检索结果有限，回答可能不够全面 (Limited knowledge retrieved, response may be incomplete)"
            
            self.history.append({"role": "assistant", "content": response["text"]})
            return response
            
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            return {
                "text": f"Error: {str(e)}",
                "plots": [],
                "data": {},
                "thinking": [{"step": "Error", "content": str(e)}]
            }
    
    def _chat_stream(self, message: str) -> Generator[Dict[str, Any], None, None]:
        """Stream chat response."""
        try:
            yield {"type": "thinking", "content": "Planning analysis..."}
            
            dataset_info = self.scanpy_tools.get_dataset_info()
            plan = self.planner.create_plan(message, dataset_info)
            
            yield {"type": "thinking", "content": f"Created plan with {len(plan.get('steps', []))} steps"}
            
            yield {"type": "thinking", "content": "Executing analysis..."}
            results = self._execute_plan(plan)
            
            yield {"type": "thinking", "content": "Retrieving knowledge from databases..."}
            knowledge = self.retriever.retrieve(message, results)
            
            retrieval_stats = knowledge.get("retrieval_stats", {})
            yield {"type": "thinking", "content": f"Retrieved {retrieval_stats.get('genes_with_info', 0)} genes with information"}
            
            yield {"type": "thinking", "content": "Synthesizing response..."}
            response = self.synthesizer.synthesize(message, results, knowledge)
            
            # Stream text in chunks
            text = response["text"]
            for i in range(0, len(text), 50):
                yield {"type": "text", "content": text[i:i+50]}
            
            if response.get("plots"):
                yield {"type": "plots", "content": response["plots"]}
            
            yield {"type": "data", "content": response.get("data", {})}
            
        except Exception as e:
            yield {"type": "error", "content": str(e)}
    
    def _execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute analysis plan."""
        results = {
            "deg": None,
            "enrichment": None,
            "network": None,
            "plots": [],
            "statistics": {}
        }
        
        for step in plan.get("steps", []):
            action = step.get("action", "")
            params = step.get("params", {})
            
            try:
                if "differential" in action.lower() or "deg" in action.lower():
                    results["deg"] = self._run_deg_analysis(params)
                elif "enrichment" in action.lower():
                    results["enrichment"] = self._run_enrichment_analysis(params, results.get("deg"))
                elif "network" in action.lower():
                    results["network"] = self._run_network_analysis(params, results.get("deg"))
                elif "visualize" in action.lower():
                    plots = self._create_visualizations(params, results)
                    results["plots"].extend(plots)
            except Exception as e:
                logger.error(f"Error in step {action}: {e}")
        
        return results
    
    def _run_deg_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run differential expression analysis."""
        cell_type = params.get("cell_type")
        if cell_type:
            deg_results = self.scanpy_tools.find_marker_genes(cell_type)
        else:
            group1 = params.get("group1")
            group2 = params.get("group2")
            deg_results = self.scanpy_tools.differential_expression(group1, group2)
        return {"results": deg_results, "params": params}
    
    def _run_enrichment_analysis(self, params: Dict[str, Any], deg_data: Optional[Dict]) -> Dict[str, Any]:
        """Run enrichment analysis."""
        if deg_data:
            gene_list = deg_data["results"]["names"].head(200).tolist()
        else:
            gene_list = params.get("genes", [])
        
        analysis_type = params.get("type", "go")
        if analysis_type == "go":
            results = self.enrichment.go_enrichment(gene_list)
        elif analysis_type == "kegg":
            results = self.enrichment.kegg_enrichment(gene_list)
        else:
            results = self.enrichment.enrichr_analysis(gene_list)
        
        return {"results": results, "gene_list": gene_list}
    
    def _run_network_analysis(self, params: Dict[str, Any], deg_data: Optional[Dict]) -> Dict[str, Any]:
        """Run network analysis."""
        if deg_data:
            genes = deg_data["results"]["names"].head(100).tolist()
        else:
            genes = params.get("genes", [])
        
        G = self.network.build_ppi_network(genes)
        hubs = self.network.identify_hub_genes(G, top_n=10)
        stats = self.network.get_network_statistics(G)
        
        return {"graph": G, "hubs": hubs, "statistics": stats, "genes": genes}
    
    def _create_visualizations(self, params: Dict[str, Any], results: Dict[str, Any]) -> List[Any]:
        """Create visualizations."""
        plots = []
        
        if params.get("umap", True):
            try:
                fig = self.visualizer.plot_umap(self.adata)
                plots.append(("umap", fig))
            except Exception as e:
                logger.warning(f"UMAP plot failed: {e}")
        
        if results.get("deg") and params.get("volcano", True):
            try:
                fig = self.visualizer.plot_volcano(results["deg"]["results"])
                plots.append(("volcano", fig))
            except Exception as e:
                logger.warning(f"Volcano plot failed: {e}")
        
        if results.get("enrichment") and params.get("enrichment", True):
            try:
                enr_results = results["enrichment"]["results"]
                if isinstance(enr_results, dict):
                    enr_results = list(enr_results.values())[0]
                fig = self.visualizer.plot_enrichment(enr_results)
                plots.append(("enrichment", fig))
            except Exception as e:
                logger.warning(f"Enrichment plot failed: {e}")
        
        if results.get("network") and params.get("network", True):
            try:
                hub_genes = [h[0] for h in results["network"]["hubs"]]
                fig = self.visualizer.plot_network(results["network"]["graph"], hub_genes)
                plots.append(("network", fig))
            except Exception as e:
                logger.warning(f"Network plot failed: {e}")
        
        return plots
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.history
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self.history = []
        logger.info("Conversation history cleared")
    
    def __del__(self):
        """Cleanup: ensure database connections are closed."""
        try:
            if hasattr(self, 'string_db'):
                self.string_db.close()
            if hasattr(self, 'hmdb_db'):
                self.hmdb_db.close()
            if hasattr(self, 'trrust_db'):
                self.trrust_db.close()
            if hasattr(self, 'gutmgene_db'):
                self.gutmgene_db.close()
        except Exception as e:
            logger.debug(f"Cleanup error: {e}")
