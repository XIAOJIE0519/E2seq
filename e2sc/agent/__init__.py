"""Agent modules for E2sc - Optimized version."""

# Optimized components (default)
from e2sc.agent.orchestrator_optimized import E2scAgentOptimized as E2scAgent
from e2sc.agent.enhanced_planner import EnhancedPlannerAgent as PlannerAgent
from e2sc.agent.retriever import RetrieverAgent
from e2sc.agent.synthesizer import SynthesizerAgent

# Additional optimized modules
from e2sc.agent.memory import MemoryManager, get_memory_manager
from e2sc.agent.state_manager import StateManager, get_state_manager
from e2sc.agent.error_recovery import ErrorRecovery, get_error_recovery
from e2sc.agent.tool_registry import ToolRegistry, create_tool_registry

# Legacy components (for backward compatibility)
from e2sc.agent.orchestrator import E2scAgent as E2scAgentLegacy
from e2sc.agent.planner import PlannerAgent as PlannerAgentLegacy

__all__ = [
    # Main components (optimized)
    "E2scAgent",
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
    "E2scAgentLegacy",
    "PlannerAgentLegacy",
]
