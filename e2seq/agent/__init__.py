"""Agent modules for E2seq - Optimized version."""

# Optimized components (default)
from e2seq.agent.orchestrator_optimized import E2seqAgentOptimized as E2seqAgent
from e2seq.agent.enhanced_planner import EnhancedPlannerAgent as PlannerAgent
from e2seq.agent.retriever import RetrieverAgent
from e2seq.agent.synthesizer import SynthesizerAgent

# Additional optimized modules
from e2seq.agent.memory import MemoryManager, get_memory_manager
from e2seq.agent.state_manager import StateManager, get_state_manager
from e2seq.agent.error_recovery import ErrorRecovery, get_error_recovery
from e2seq.agent.tool_registry import ToolRegistry, create_tool_registry

# Legacy components (for backward compatibility)
from e2seq.agent.orchestrator import E2seqAgent as E2seqLegacyAgent
from e2seq.agent.planner import PlannerAgent as PlannerAgentLegacy

__all__ = [
    # Main components (optimized)
    "E2seqAgent",
    "PlannerAgent",
    "RetrieverAgent",
    "SynthesizerAgent",

    # Memory and state management
    "MemoryManager",
    "get_memory_manager",
    "StateManager",
    "get_state_manager",

    # Error recovery
    "ErrorRecovery",
    "get_error_recovery",

    # Tool registry
    "ToolRegistry",
    "create_tool_registry",

    # Legacy (backward compatibility)
    "E2seqLegacyAgent",
    "PlannerAgentLegacy",
]
