"""Enhanced Retriever with strategy learning from similar cases.

This module extends the base RetrieverAgent with:
- Strategy extraction from similar cases
- Priority-based retrieval
- Learning from successful patterns
"""

from typing import Any, Dict, List, Optional

from e2seq.agent.retriever import RetrieverAgent
from e2seq.utils import get_logger

logger = get_logger(__name__)


class EnhancedRetrieverAgent(RetrieverAgent):
    """Enhanced retriever with strategy learning capabilities."""

    def retrieve(self, question: str, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced retrieve with strategy learning.

        Args:
            question: User's question
            analysis_results: Results from analysis

        Returns:
            Dictionary with retrieved knowledge and learned strategies
        """
        logger.info("Enhanced retrieval with strategy learning")

        # First, get similar cases from vector database
        similar_cases = []
        if self.vector_store:
            try:
                similar_cases = self.vector_store.search_similar_cases(
                    query=question,
                    n_results=5
                )
                logger.info(f"[OK] Found {len(similar_cases)} similar cases")
            except Exception as e:
                logger.warning(f"[FAIL] Similar case search failed: {e}")

        # Extract successful strategies from similar cases
        strategies = self._extract_strategies(similar_cases)
        logger.info(f"Extracted {len(strategies)} strategies from similar cases")

        # Use base retrieval
        knowledge = super().retrieve(question, analysis_results)

        # Enhance with strategy-based retrieval
        if strategies:
            knowledge = self._apply_strategies(knowledge, strategies, analysis_results)

        # Add strategies to knowledge
        knowledge["learned_strategies"] = strategies
        knowledge["strategy_applied"] = bool(strategies)

        return knowledge

    def _extract_strategies(self, similar_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract successful strategies from similar cases.

        Args:
            similar_cases: List of similar case dictionaries

        Returns:
            List of strategy dictionaries
        """
        strategies = []

        for case in similar_cases:
            metadata = case.get("metadata", {})

            # Only learn from successful cases
            if not metadata.get("success", False):
                continue

            strategy = {
                "case_id": case.get("id"),
                "analysis_type": metadata.get("analysis_type", "unknown"),
                "similarity": 1 - case.get("distance", 1),
                "n_genes": metadata.get("n_genes", 0),
                "has_enrichment": metadata.get("has_enrichment", False),
                "has_network": metadata.get("has_network", False),
                "priority_databases": []
            }

            # Infer which databases were most useful
            if strategy["has_network"]:
                strategy["priority_databases"].append("STRING")
            if strategy["has_enrichment"]:
                strategy["priority_databases"].append("GO")

            # Add to strategies if similarity is high enough
            if strategy["similarity"] > 0.7:
                strategies.append(strategy)
                logger.debug(f"Extracted strategy from case {strategy['case_id']}: {strategy['analysis_type']}")

        return strategies

    def _apply_strategies(
        self,
        knowledge: Dict[str, Any],
        strategies: List[Dict[str, Any]],
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply learned strategies to enhance retrieval.

        Args:
            knowledge: Current knowledge dictionary
            strategies: List of learned strategies
            analysis_results: Analysis results

        Returns:
            Enhanced knowledge dictionary
        """
        logger.info("Applying learned strategies to retrieval")

        # Determine priority databases based on strategies
        priority_dbs = set()
        for strategy in strategies:
            priority_dbs.update(strategy.get("priority_databases", []))

        knowledge["retrieval_stats"]["priority_databases"] = list(priority_dbs)

        # If strategies suggest focusing on network analysis
        if "STRING" in priority_dbs and analysis_results.get("network"):
            logger.info("Strategy: Prioritizing protein interaction data")
            # Already retrieved in base class, but we can add more context
            knowledge["retrieval_stats"]["strategy_hint"] = "Focus on protein-protein interactions"

        # If strategies suggest enrichment is important
        if "GO" in priority_dbs and analysis_results.get("enrichment"):
            logger.info("Strategy: Prioritizing functional enrichment data")
            knowledge["retrieval_stats"]["strategy_hint"] = "Focus on functional annotations"

        # Adjust gene retrieval priority based on strategies
        avg_n_genes = sum(s.get("n_genes", 0) for s in strategies) / max(len(strategies), 1)
        if avg_n_genes > 0:
            knowledge["retrieval_stats"]["suggested_gene_count"] = int(avg_n_genes)
            logger.info(f"Strategy suggests focusing on ~{int(avg_n_genes)} genes")

        return knowledge

    def learn_from_feedback(self, case_id: str, feedback: Dict[str, Any]) -> None:
        """Learn from user feedback on retrieval quality.

        Args:
            case_id: Case identifier
            feedback: Feedback dictionary with ratings
        """
        if not self.vector_store:
            return

        try:
            # Update case metadata with feedback
            # This would require extending vector_store with update capability
            logger.info(f"Received feedback for case {case_id}: {feedback}")

            # In a full implementation, we would:
            # 1. Update the case metadata in vector store
            # 2. Adjust strategy weights based on feedback
            # 3. Store feedback for future strategy refinement

        except Exception as e:
            logger.error(f"Error processing feedback: {e}")


def create_enhanced_retriever(llm, string_db, hmdb_db, trrust_db, gutmgene_db, api_clients) -> EnhancedRetrieverAgent:
    """Factory function to create enhanced retriever.

    Args:
        llm: LLM provider
        string_db: STRING database
        hmdb_db: HMDB database
        trrust_db: TRRUST database
        gutmgene_db: GUTMGENE database
        api_clients: API clients dictionary

    Returns:
        EnhancedRetrieverAgent instance
    """
    return EnhancedRetrieverAgent(llm, string_db, hmdb_db, trrust_db, gutmgene_db, api_clients)
