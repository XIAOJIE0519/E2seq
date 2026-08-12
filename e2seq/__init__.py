"""
E2seq: Easy to Chat with Sequencing via Agentic RAG

An Agent RAG interpreter for uploaded sequencing gene-value results.
"""

__version__ = "0.2.0"
__author__ = "E2seq Team"
__email__ = "team@e2seq.dev"

# Import optimized version as default
from e2seq.agent.orchestrator_optimized import E2seqAgentOptimized as E2seqAgent

# Backward compatibility: also expose original version
from e2seq.agent.orchestrator import E2seqAgent as E2seqLegacyAgent

__all__ = [
    "E2seqAgent",           # Optimized version (default)
    "E2seqLegacyAgent",    # Original orchestrator (for compatibility)
    "__version__"
]
