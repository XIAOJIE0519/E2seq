"""Tool registry for automatic API tool registration and invocation."""

from typing import Any, Callable, Dict, List, Optional

from e2seq.utils import get_logger

logger = get_logger(__name__)


class Tool:
    """Represents a callable tool with metadata."""

    def __init__(
        self,
        name: str,
        func: Callable,
        description: str,
        parameters: Optional[Dict[str, Any]] = None
    ):
        """Initialize tool.

        Args:
            name: Tool name
            func: Callable function
            description: Tool description for LLM
            parameters: Parameter schema
        """
        self.name = name
        self.func = func
        self.description = description
        self.parameters = parameters or {}

    def __call__(self, *args, **kwargs):
        """Execute tool."""
        return self.func(*args, **kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for LLM tool calling."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }


class ToolRegistry:
    """Registry for all available API tools."""

    def __init__(self, api_clients: Dict[str, Any]):
        """Initialize tool registry.

        Args:
            api_clients: Dictionary of API client instances
        """
        self.api_clients = api_clients
        self.tools: Dict[str, Tool] = {}
        self._register_all_tools()
        logger.info(f"[OK] Tool registry initialized with {len(self.tools)} tools")

    def _register_all_tools(self) -> None:
        """Register all API tools."""

        # 1. UniProt - Protein information
        self.register_tool(
            name="query_uniprot",
            func=lambda gene: self.api_clients["uniprot"].get_protein_info(gene),
            description="查询UniProt数据库获取蛋白质详细信息，包括功能、结构域、修饰等。输入：基因名称（如TP53）",
            parameters={
                "type": "object",
                "properties": {
                    "gene": {
                        "type": "string",
                        "description": "基因名称，如TP53, BRCA1"
                    }
                },
                "required": ["gene"]
            }
        )

        # 2. STRING - Protein-protein interactions
        self.register_tool(
            name="query_string_interactions",
            func=lambda genes: self.api_clients["string"].get_interactions(
                genes if isinstance(genes, list) else [genes]
            ),
            description="查询STRING数据库获取蛋白质互作网络。输入：基因列表",
            parameters={
                "type": "object",
                "properties": {
                    "genes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "基因名称列表，如['TP53', 'MDM2', 'BAX']"
                    }
                },
                "required": ["genes"]
            }
        )

        # 3. MyGene - Gene annotation
        self.register_tool(
            name="query_mygene",
            func=lambda gene: self.api_clients["mygene"].get_gene_info(gene),
            description="查询MyGene.info获取基因注释信息，包括Entrez ID、Ensembl ID、染色体位置等。输入：基因名称",
            parameters={
                "type": "object",
                "properties": {
                    "gene": {
                        "type": "string",
                        "description": "基因名称"
                    }
                },
                "required": ["gene"]
            }
        )

        # 4. QuickGO - GO annotations
        self.register_tool(
            name="query_quickgo",
            func=lambda gene: self.api_clients["quickgo"].get_go_terms(gene),
            description="查询QuickGO数据库获取基因的GO功能注释。输入：基因名称或UniProt ID",
            parameters={
                "type": "object",
                "properties": {
                    "gene": {
                        "type": "string",
                        "description": "基因名称或UniProt ID"
                    }
                },
                "required": ["gene"]
            }
        )

        # 5. PubMed - Literature search
        self.register_tool(
            name="search_pubmed",
            func=lambda query, max_results=10: self.api_clients["pubmed"].search(query, max_results),
            description="搜索PubMed文献数据库。输入：搜索关键词",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词，如'TP53 AND cancer'"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "最大返回结果数",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        )

        # 6. PubChem - Compound information
        self.register_tool(
            name="query_pubchem",
            func=lambda compound: self.api_clients["pubchem"].get_compound_info(compound),
            description="查询PubChem数据库获取化合物信息。输入：化合物名称",
            parameters={
                "type": "object",
                "properties": {
                    "compound": {
                        "type": "string",
                        "description": "化合物名称，如aspirin, glucose"
                    }
                },
                "required": ["compound"]
            }
        )

        # 7. ChEMBL - Drug target information
        self.register_tool(
            name="query_chembl",
            func=lambda target: self.api_clients["chembl"].search_target(target),
            description="查询ChEMBL数据库获取药物靶点信息。输入：靶点名称",
            parameters={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "靶点名称，如EGFR, TP53"
                    }
                },
                "required": ["target"]
            }
        )

        # 8. Ensembl - Genomic information
        self.register_tool(
            name="query_ensembl",
            func=lambda gene_id: self.api_clients["ensembl"].get_gene_info(gene_id),
            description="查询Ensembl数据库获取基因组信息，包括染色体位置、序列等。输入：基因ID或名称",
            parameters={
                "type": "object",
                "properties": {
                    "gene_id": {
                        "type": "string",
                        "description": "基因ID或名称"
                    }
                },
                "required": ["gene_id"]
            }
        )

        # 9. Europe PMC - Literature with citations
        self.register_tool(
            name="search_europepmc",
            func=lambda query, max_results=10: self.api_clients["europepmc"].search(query, max_results),
            description="搜索Europe PMC文献数据库（包含引用次数）。输入：搜索关键词",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "最大返回结果数",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        )

        # ========== 新增工具 ==========

        # 10. GWAS Catalog - SNP/变异与性状/疾病的大规模GWAS证据
        self.register_tool(
            name="query_gwas_trait_associations",
            func=lambda gene, max_results=20: self.api_clients["gwas"].get_gene_trait_associations(gene, max_results),
            description="查询GWAS Catalog获取基因相关的疾病/表型GWAS证据（SNP、p值、疾病）。输入：基因名称（如TP53）",
            parameters={
                "type": "object",
                "properties": {
                    "gene": {"type": "string", "description": "基因名称，如TP53"},
                    "max_results": {"type": "integer", "description": "最大返回结果数", "default": 20}
                },
                "required": ["gene"]
            }
        )

        # 11. PharmGKB - 药物基因组学：基因变异与药物反应
        self.register_tool(
            name="query_pharmgkb_gene_drug",
            func=lambda gene, max_results=20: self.api_clients["pharmgkb"].get_gene_drug_relationships(gene, max_results),
            description="查询PharmGKB获取基因-药物关系、变异、临床注释、给药指南。输入：基因名称（如CYP2C19）",
            parameters={
                "type": "object",
                "properties": {
                    "gene": {"type": "string", "description": "基因名称，如CYP2C19"},
                    "max_results": {"type": "integer", "description": "最大返回结果数", "default": 20}
                },
                "required": ["gene"]
            }
        )

        self.register_tool(
            name="query_pharmgkb_dosing_guidelines",
            func=lambda gene: self.api_clients["pharmgkb"].get_dosing_guidelines(gene),
            description="查询PharmGKB获取基因相关的给药指南（dosing guideline）。输入：基因名称",
            parameters={
                "type": "object",
                "properties": {
                    "gene": {"type": "string", "description": "基因名称"}
                },
                "required": ["gene"]
            }
        )

        # 12. GTEx - 基因在各组织的表达
        self.register_tool(
            name="query_gtex_expression",
            func=lambda gene, max_results=50: self.api_clients["gtex"].query(gene, max_results),
            description="查询GTEx获取基因在各组织的表达数据（TPM）。输入：基因名称（如TP53）",
            parameters={
                "type": "object",
                "properties": {
                    "gene": {"type": "string", "description": "基因名称"},
                    "max_results": {"type": "integer", "description": "最大返回结果数", "default": 50}
                },
                "required": ["gene"]
            }
        )

        # 14. HumanBase - 基因组织特异性表达和功能网络
        self.register_tool(
            name="query_hpa_expression",
            func=lambda gene, max_results=50: self.api_clients["hpa"].query(gene, max_results),
            description="查询HumanBase获取基因在各组织的表达特异性分数。输入：基因名称（如TP53）",
            parameters={
                "type": "object",
                "properties": {
                    "gene": {"type": "string", "description": "基因名称"},
                    "max_results": {"type": "integer", "description": "最大返回结果数", "default": 50}
                },
                "required": ["gene"]
            }
        )

        self.register_tool(
            name="query_hpa_annotations",
            func=lambda gene, tissue="": self.api_clients["hpa"].query(gene, 20),
            description="查询HumanBase获取特定组织的基因功能网络。输入：基因名称和组织（如brain/liver）",
            parameters={
                "type": "object",
                "properties": {
                    "gene": {"type": "string", "description": "基因名称"},
                    "tissue": {"type": "string", "description": "组织名称", "default": "brain"}
                },
                "required": ["gene"]
            }
        )

        # 15. CIViC - 癌症变异临床解释
        self.register_tool(
            name="query_civic_variants",
            func=lambda gene, max_results=20: self.api_clients["civic"].search_variants(gene, max_results),
            description="查询CIViC获取癌症基因相关的变异及临床证据（therapy/diagnosis/prognosis）。输入：基因名称（如EGFR）",
            parameters={
                "type": "object",
                "properties": {
                    "gene": {"type": "string", "description": "基因名称，如EGFR"},
                    "max_results": {"type": "integer", "description": "最大返回结果数", "default": 20}
                },
                "required": ["gene"]
            }
        )

        # 16. Alliance of Genome Resources - 模式生物、同源基因、跨物种证据
        self.register_tool(
            name="search_alliance_cross_species",
            func=lambda query: self.api_clients["alliance"].query(query, 50),
            description="跨物种搜索Alliance of Genome Resources（人类、小鼠、斑马鱼、果蝇、线虫）。输入：基因/蛋白名称",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索词（基因或蛋白名称）"}
                },
                "required": ["query"]
            }
        )

        self.register_tool(
            name="query_alliance_homologs",
            func=lambda gene, species="human": self.api_clients["alliance"].query(gene, 50),
            description="查询Alliance获取基因的同源基因（mouse/zebrafish/fly/worm）。输入：基因名称和物种",
            parameters={
                "type": "object",
                "properties": {
                    "gene": {"type": "string", "description": "基因名称"},
                    "species": {"type": "string", "description": "物种：human/mouse/zebrafish/fly/worm", "default": "human"}
                },
                "required": ["gene"]
            }
        )

    def register_tool(
        self,
        name: str,
        func: Callable,
        description: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register a new tool.

        Args:
            name: Tool name
            func: Callable function
            description: Tool description
            parameters: Parameter schema
        """
        tool = Tool(name, func, description, parameters)
        self.tools[name] = tool
        logger.debug(f"Registered tool: {name}")

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get tool by name.

        Args:
            name: Tool name

        Returns:
            Tool instance or None
        """
        return self.tools.get(name)

    def execute_tool(self, name: str, **kwargs) -> Any:
        """Execute a tool by name.

        Args:
            name: Tool name
            **kwargs: Tool parameters

        Returns:
            Tool execution result
        """
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool not found: {name}")

        try:
            logger.info(f"Executing tool: {name} with params: {kwargs}")
            result = tool(**kwargs)
            logger.info(f"[OK] Tool {name} executed successfully")
            return result
        except Exception as e:
            logger.error(f"[FAIL] Tool {name} execution failed: {e}")
            raise

    def get_tool_descriptions(self) -> List[Dict[str, Any]]:
        """Get all tool descriptions for LLM.

        Returns:
            List of tool description dictionaries
        """
        return [tool.to_dict() for tool in self.tools.values()]

    def get_tool_names(self) -> List[str]:
        """Get all tool names.

        Returns:
            List of tool names
        """
        return list(self.tools.keys())

    def get_tools_summary(self) -> str:
        """Get human-readable summary of all tools.

        Returns:
            Summary string
        """
        summary = ["Available API Tools:\n"]
        for i, (name, tool) in enumerate(self.tools.items(), 1):
            summary.append(f"{i}. {name}: {tool.description}")
        return "\n".join(summary)


def create_tool_registry(api_clients: Dict[str, Any], code_executor=None) -> ToolRegistry:
    """Factory function to create tool registry.

    Args:
        api_clients: Dictionary of API clients
        code_executor: Optional CodeExecutor instance for AI code execution

    Returns:
        ToolRegistry instance
    """
    registry = ToolRegistry(api_clients)

    if code_executor is not None:
        def _execute_python(code: str) -> str:
            result = code_executor.execute(code)
            return result.as_context_text()

        def _query_local_db(db_name: str, sql: str) -> str:
            try:
                df = code_executor._query_db(db_name, sql)
                return f"Query returned {len(df)} rows:\n{df.head(20).to_string()}"
            except Exception as e:
                return f"Error: {e}"

        def _list_dbs() -> str:
            return "Available databases: " + ", ".join(code_executor._list_dbs())

        registry.register_tool(
            name="execute_python_code",
            func=_execute_python,
            description=(
                "Execute Python code for data analysis. "
                "Pre-injected: adata (AnnData if loaded), pd, np, sc, plt, px, "
                "query_db(db_name, sql) for local DBs. "
                "DBs: string, hmdb, trrust, gutmgene. "
                "Use result=... to return a value."
            ),
            parameters={"type": "object", "properties": {"code": {"type": "string", "description": "Python code to execute"}}, "required": ["code"]}
        )
        registry.register_tool(
            name="query_local_db",
            func=_query_local_db,
            description=(
                "Run SQL against local bioinformatics DB. "
                "db_name: string|hmdb|trrust|gutmgene. "
                "Tables: string_interactions(source_gene,target_gene,weight), "
                "hmdb_associations(gene,metabolite), "
                "trrust_regulations(TF,gene,function,pubmed), "
                "gutmgene_associations(Gene,[Gut Microbiota],Condition,...)"
            ),
            parameters={"type": "object", "properties": {"db_name": {"type": "string"}, "sql": {"type": "string"}}, "required": ["db_name", "sql"]}
        )
        registry.register_tool(
            name="list_available_databases",
            func=lambda: _list_dbs(),
            description="List all available local databases for SQL queries.",
            parameters={"type": "object", "properties": {}, "required": []}
        )
        logger.info("Code execution tools registered")

    return registry
