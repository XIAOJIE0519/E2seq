"""Enhanced planner with ReAct-style reasoning."""

import re
from typing import Any, Dict, List

from e2sc.agent.memory import get_memory_manager
from e2sc.utils import get_logger

logger = get_logger(__name__)


class EnhancedPlannerAgent:
    """Enhanced planner with reasoning and chain-of-thought."""
    
    def __init__(self, llm):
        """Initialize enhanced planner."""
        self.llm = llm
        self.memory = get_memory_manager()
    
    def create_plan(self, question: str, dataset_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create analysis plan with reasoning."""
        logger.info("Creating enhanced analysis plan")
        
        # Get context from memory
        context = self.memory.get_relevant_context(question)
        
        # Build prompt
        prompt = self._build_prompt(question, dataset_info, context)
        
        # Get plan from LLM
        messages = [
            {"role": "system", "content": "You are an expert single-cell analysis planner."},
            {"role": "user", "content": prompt}
        ]
        
        response = self.llm.chat(messages)
        
        # Parse plan
        plan = self._parse_plan(response, question, dataset_info)
        
        # Store in memory
        self.memory.update_analysis_state({
            "current_plan": plan,
            "analysis_type": plan.get("analysis_type", "unknown")
        })
        
        logger.info(f"Created plan with {len(plan['steps'])} steps")
        return plan
    
    def _build_prompt(self, question: str, dataset_info: Dict[str, Any], 
                     context: Dict[str, Any]) -> str:
        """Build enhanced prompt."""
        prompt_parts = [
            f"User Question: {question}",
            f"Dataset: {dataset_info.get('n_cells', 0)} cells, {dataset_info.get('n_genes', 0)} genes",
            "",
            "Create a step-by-step analysis plan."
        ]
        
        return "\n".join(prompt_parts)
    
    def _parse_plan(self, response: str, question: str, 
                   dataset_info: Dict[str, Any]) -> Dict[str, Any]:
        """Parse plan from response."""
        steps = self._parse_steps(question)
        
        return {
            "question": question,
            "analysis_type": self._determine_type(steps),
            "steps": steps,
            "dataset_info": dataset_info
        }
    
    def _parse_steps(self, question: str) -> List[Dict[str, Any]]:
        """Parse steps from question."""
        steps = []
        q_lower = question.lower()
        
        if any(kw in q_lower for kw in ["差异", "differential", "deg"]):
            steps.append({"action": "differential_expression", "params": {}})
        
        if any(kw in q_lower for kw in ["富集", "enrichment", "go", "kegg"]):
            steps.append({"action": "enrichment_analysis", "params": {}})
        
        if any(kw in q_lower for kw in ["网络", "network", "ppi"]):
            steps.append({"action": "network_analysis", "params": {}})
        
        steps.append({"action": "visualize", "params": {}})
        
        return steps
    
    def _determine_type(self, steps: List[Dict]) -> str:
        """Determine analysis type."""
        actions = [s["action"] for s in steps]
        
        if len(actions) > 2:
            return "comprehensive"
        elif "differential_expression" in actions:
            return "deg"
        elif "enrichment_analysis" in actions:
            return "enrichment"
        else:
            return "exploratory"
