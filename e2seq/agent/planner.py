"""Planner agent for task planning."""

from typing import Any, Dict, List

from e2seq.llm import PLANNER_PROMPT
from e2seq.utils import get_logger

logger = get_logger(__name__)


class PlannerAgent:
    """Agent for planning analysis tasks."""

    def __init__(self, llm):
        """Initialize planner agent.

        Args:
            llm: LLM provider instance
        """
        self.llm = llm

    def create_plan(self, question: str, dataset_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create analysis plan based on user question.

        Args:
            question: User's question
            dataset_info: Information about the dataset

        Returns:
            Dictionary with analysis plan
        """
        logger.info("Creating analysis plan")

        # Prepare prompt
        prompt = PLANNER_PROMPT.format(
            question=question,
            tools=self._get_available_tools(),
            dataset_info=dataset_info.get("n_cells", "Unknown"),
            cell_types=", ".join(dataset_info.get("cell_types", [])),
            n_cells=dataset_info.get("n_cells", 0),
            n_genes=dataset_info.get("n_genes", 0)
        )

        # Get plan from LLM
        messages = [
            {"role": "system", "content": "You are an expert in expression-profile and single-cell analysis planning."},
            {"role": "user", "content": prompt}
        ]

        response = self.llm.chat(messages)

        # Parse plan
        plan = self._parse_plan(response, question)

        logger.info(f"Created plan with {len(plan['steps'])} steps")
        return plan

    def _get_available_tools(self) -> str:
        """Get description of available tools."""
        tools = """
        1. Differential Expression Analysis (DEG)
           - Find marker genes for cell types
           - Compare gene expression between groups

        2. Enrichment Analysis
           - GO enrichment (BP, MF, CC)
           - KEGG pathway enrichment
           - Reactome pathway enrichment

        3. Network Analysis
           - Build PPI networks from STRING database
           - Identify hub genes
           - Detect communities

        4. Visualization
           - UMAP/tSNE plots
           - Volcano plots
           - Enrichment bubble plots
           - Network graphs
           - Heatmaps

        5. Knowledge Retrieval
           - Query local databases (STRING, HMDB, TRRUST, GUTMGENE)
           - Query online APIs (UniProt, QuickGO, PubMed)
        """
        return tools

    def _parse_plan(self, response: str, question: str) -> Dict[str, Any]:
        """Parse LLM response into structured plan.

        Args:
            response: LLM response text
            question: Original question

        Returns:
            Structured plan dictionary
        """
        # Simple parsing - extract key actions
        steps = []

        # Detect analysis types from question
        question_lower = question.lower()

        # Check for differential expression
        if any(kw in question_lower for kw in ["差异", "differential", "deg", "marker", "高表达", "低表达"]):
            cell_type = self._extract_cell_type(question)
            steps.append({
                "action": "differential_expression",
                "params": {"cell_type": cell_type} if cell_type else {}
            })

        # Check for enrichment analysis
        if any(kw in question_lower for kw in ["富集", "enrichment", "go", "kegg", "pathway", "通路"]):
            enr_type = "go"
            if "kegg" in question_lower:
                enr_type = "kegg"
            steps.append({
                "action": "enrichment_analysis",
                "params": {"type": enr_type}
            })

        # Check for network analysis
        if any(kw in question_lower for kw in ["网络", "network", "互作", "interaction", "ppi", "hub"]):
            steps.append({
                "action": "network_analysis",
                "params": {}
            })

        # Always add visualization
        steps.append({
            "action": "visualize",
            "params": {
                "umap": True,
                "volcano": "differential" in [s["action"] for s in steps],
                "enrichment": "enrichment" in [s["action"] for s in steps],
                "network": "network" in [s["action"] for s in steps]
            }
        })

        return {
            "question": question,
            "steps": steps,
            "raw_response": response
        }

    def _extract_cell_type(self, question: str) -> str:
        """Extract cell type from question.

        Args:
            question: User question

        Returns:
            Cell type name or empty string
        """
        # Simple extraction - look for common patterns
        import re

        # Pattern: "XXX细胞" or "XXX cells"
        patterns = [
            r"([A-Za-z]+)\s*细胞",
            r"([A-Za-z]+)\s+cells?",
        ]

        for pattern in patterns:
            match = re.search(pattern, question)
            if match:
                return match.group(1)

        return ""
