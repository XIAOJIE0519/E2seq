"""
E2seq: Easy to Chat with Sequencing via Agentic RAG

An Agent RAG interpreter for uploaded sequencing gene-value results.
"""

__version__ = "0.2.0"
__author__ = "E2seq Team"
__email__ = "team@e2seq.dev"

# Import optimized version as default
from e2sc.agent.orchestrator_optimized import E2scAgentOptimized as E2scAgent

# Backward compatibility: also expose original version
from e2sc.agent.orchestrator import E2scAgent as E2scAgentLegacy

__all__ = [
    "E2scAgent",           # Optimized version (default)
    "E2scAgentLegacy",     # Original version (for compatibility)
    "__version__"
]
