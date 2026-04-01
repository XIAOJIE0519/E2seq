"""LangGraph-based Agent Executor for E2sc.

Uses langgraph.prebuilt.create_react_agent for autonomous tool calling,
compatible with LangChain 1.x / LangGraph.
"""

from typing import Any, Dict, List, Optional

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import StructuredTool, Tool
from langgraph.prebuilt import create_react_agent

from e2sc.agent.tool_registry import ToolRegistry
from e2sc.utils import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are E2sc, an expert AI assistant specialized in single-cell RNA sequencing (scRNA-seq) data analysis.

You have direct access to pre-built bioinformatics API tools. Call them directly to answer questions.

## Available API Tools (call directly)

### Gene & Protein
- `mygene_query_gene(gene)` — Gene info: Entrez ID, UniProt, Ensembl, location
- `mygene_get_by_id(entrez_id)` — Gene details by Entrez ID
- `uniprot_search_gene(gene)` — UniProt protein info, function, domains
- `uniprot_get_protein(accession)` — Protein details by UniProt accession
- `ensembl_lookup_gene(gene)` — Ensembl ID, chromosome position
- `ensembl_get_sequence(ensembl_id)` — DNA sequence

### Interactions & Function
- `string_get_interactions(gene, limit)` — Protein-protein interaction network
- `string_get_network_image(proteins)` — PPI network image URL
- `quickgo_get_annotations(uniprot_id)` — GO functional annotations
- `quickgo_get_term(go_id)` — GO term definition

### Compounds & Drugs
- `chembl_search_compound(name)` — Drug/compound, clinical phase
- `chembl_get_compound(chembl_id)` — Compound details
- `pubchem_search_compound(name)` — Chemical info: formula, MW, SMILES

### Literature
- `pubmed_search(query, max_results)` — PubMed articles, abstracts
- `europepmc_search(query, page_size)` — Europe PMC, citation counts

### Local Databases
- `query_local_db(db_name, sql)` — SQL query on STRING/HMDB/TRRUST/GUTMGENE
- `list_available_databases()` — List available local databases

## Rules
1. Always call the appropriate tool(s) to get real data before answering
2. Synthesize tool results into a clear scientific answer
3. Cite which tool/database provided each piece of information
4. Do NOT say you cannot execute tools — you CAN and MUST use them
"""


class E2scAgentExecutor:
    """LangGraph ReAct agent executor with autonomous tool calling."""

    def __init__(self, llm, tool_registry: ToolRegistry):
        self.llm = llm
        self.tool_registry = tool_registry
        self.langchain_tools = self._build_langchain_tools()
        self.agent = create_react_agent(
            model=self.llm,
            tools=self.langchain_tools,
            prompt=SYSTEM_PROMPT,
        )
        logger.info(f"LangGraph ReAct agent initialized with {len(self.langchain_tools)} tools")

    def _build_langchain_tools(self) -> list:
        """Convert ToolRegistry entries to LangChain tool objects."""
        import inspect
        lc_tools = []
        for name, tool in self.tool_registry.tools.items():
            try:
                sig = inspect.signature(tool.func)
                non_default_params = [
                    p for p in sig.parameters.values()
                    if p.name != "self" and p.default is inspect.Parameter.empty
                ]
                if len(non_default_params) <= 1:
                    lc_tool = Tool(
                        name=name,
                        func=tool.func,
                        description=tool.description,
                    )
                else:
                    lc_tool = StructuredTool.from_function(
                        func=tool.func,
                        name=name,
                        description=tool.description,
                    )
                lc_tools.append(lc_tool)
                logger.debug(f"Registered tool: {name}")
            except Exception as e:
                logger.warning(f"Skipped tool {name}: {e}")
        return lc_tools

    def execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute agent with autonomous tool calling.

        Args:
            query: User query
            context: Optional context with chat_history

        Returns:
            Dict with answer, tools_used, intermediate_steps, success
        """
        logger.info(f"Agent executing: {query[:100]}...")
        try:
            messages = [HumanMessage(content=query)]

            # Add recent chat history if provided
            history = context.get("chat_history", []) if context else []
            if history:
                hist_msgs = []
                for h in history[-6:]:
                    role = h.get("role", "")
                    content = h.get("content", "")
                    if role == "user":
                        hist_msgs.append(HumanMessage(content=content))
                    elif role == "assistant":
                        hist_msgs.append(AIMessage(content=content))
                messages = hist_msgs + messages

            result = self.agent.invoke({"messages": messages})

            # Extract final answer from last AI message
            answer = ""
            tools_used = []
            intermediate_steps = []

            for msg in result.get("messages", []):
                if isinstance(msg, AIMessage):
                    if msg.content:
                        answer = msg.content
                    # Collect tool calls
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        for tc in msg.tool_calls:
                            tools_used.append(tc.get("name", ""))
                            intermediate_steps.append({
                                "tool": tc.get("name"),
                                "input": tc.get("args"),
                            })

            tools_used = list(set(tools_used))
            logger.info(f"Agent done. Tools used: {tools_used}")
            return {
                "answer": answer,
                "tools_used": tools_used,
                "intermediate_steps": intermediate_steps,
                "success": True,
            }

        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            return {
                "answer": f"Agent execution error: {str(e)}",
                "tools_used": [],
                "intermediate_steps": [],
                "success": False,
                "error": str(e),
            }


def create_agent_executor(llm, tool_registry: ToolRegistry) -> E2scAgentExecutor:
    """Factory function."""
    return E2scAgentExecutor(llm, tool_registry)
