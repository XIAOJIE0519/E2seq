"""Integration tests for optimized E2sc Agent.

Tests all optimization features:
- MemoryManager
- StateManager
- ErrorRecovery
- ToolRegistry
- EnhancedPlanner
- Agent Executor
"""

import pytest
from unittest.mock import Mock, MagicMock
import pandas as pd
import numpy as np
from anndata import AnnData

from e2sc.agent.orchestrator_optimized import E2scAgentOptimized
from e2sc.agent.memory import get_memory_manager
from e2sc.agent.state_manager import get_state_manager, AgentState
from e2sc.agent.error_recovery import get_error_recovery
from e2sc.agent.tool_registry import create_tool_registry
from e2sc.data.vector_store import get_vector_store


@pytest.fixture
def mock_adata():
    """Create mock AnnData object."""
    n_obs = 100
    n_vars = 50
    
    X = np.random.randn(n_obs, n_vars)
    obs = pd.DataFrame({
        'cell_type': ['TypeA'] * 50 + ['TypeB'] * 50,
        'group': ['Control'] * 50 + ['Treatment'] * 50
    })
    var = pd.DataFrame({
        'gene_ids': [f'GENE{i}' for i in range(n_vars)]
    }, index=[f'GENE{i}' for i in range(n_vars)])
    
    adata = AnnData(X=X, obs=obs, var=var)
    adata.obsm['X_umap'] = np.random.randn(n_obs, 2)
    
    return adata


@pytest.fixture
def mock_llm():
    """Create mock LLM."""
    llm = Mock()
    llm.chat = Mock(return_value="Mock response")
    llm.stream_chat = Mock(return_value=iter(["Mock ", "stream ", "response"]))
    llm.llm = Mock()  # For LangChain compatibility
    return llm


class TestMemoryManager:
    """Test MemoryManager integration."""
    
    def test_memory_initialization(self):
        """Test memory manager initializes correctly."""
        memory = get_memory_manager()
        assert memory is not None
        assert hasattr(memory, 'working_memory')
        assert hasattr(memory, 'long_term_memory')
    
    def test_add_interaction(self):
        """Test adding interactions to memory."""
        memory = get_memory_manager()
        memory.clear_working_memory()
        
        memory.add_interaction("Test question", "Test answer", {"test": True})
        
        history = memory.working_memory.conversation_history
        assert len(history) >= 2
        assert any("Test question" in str(msg) for msg in history)
    
    def test_memory_stats(self):
        """Test memory statistics."""
        memory = get_memory_manager()
        stats = memory.get_memory_stats()
        
        assert 'current_session' in stats
        assert 'long_term' in stats
        assert 'messages' in stats['current_session']


class TestStateManager:
    """Test StateManager integration."""
    
    def test_state_initialization(self):
        """Test state manager initializes correctly."""
        state_mgr = get_state_manager()
        assert state_mgr is not None
        assert state_mgr.current_state == AgentState.IDLE
    
    def test_state_transitions(self):
        """Test state transitions."""
        state_mgr = get_state_manager()
        
        state_mgr.set_state(AgentState.PLANNING)
        assert state_mgr.current_state == AgentState.PLANNING
        
        state_mgr.set_state(AgentState.EXECUTING)
        assert state_mgr.current_state == AgentState.EXECUTING
        
        state_mgr.set_state(AgentState.COMPLETED)
        assert state_mgr.current_state == AgentState.COMPLETED
    
    def test_task_management(self):
        """Test task queue management."""
        state_mgr = get_state_manager()
        state_mgr.reset()
        
        task = {"action": "test_action", "params": {}}
        state_mgr.add_task(task)
        
        next_task = state_mgr.get_next_task()
        assert next_task is not None
        assert next_task["action"] == "test_action"
    
    def test_checkpoint_creation(self):
        """Test checkpoint creation and restoration."""
        state_mgr = get_state_manager()
        
        checkpoint_name = state_mgr.create_checkpoint("test_checkpoint")
        assert checkpoint_name is not None
        
        checkpoints = state_mgr.list_checkpoints()
        assert "test_checkpoint" in checkpoints


class TestErrorRecovery:
    """Test ErrorRecovery integration."""
    
    def test_error_recovery_initialization(self):
        """Test error recovery initializes correctly."""
        error_recovery = get_error_recovery()
        assert error_recovery is not None
        assert error_recovery.max_retries == 3
    
    def test_successful_execution(self):
        """Test successful execution without errors."""
        error_recovery = get_error_recovery()
        
        def success_func():
            return "success"
        
        success, result, error = error_recovery.execute_with_retry(success_func)
        
        assert success is True
        assert result == "success"
        assert error is None
    
    def test_retry_on_failure(self):
        """Test retry mechanism on failure."""
        error_recovery = get_error_recovery()
        
        call_count = [0]
        
        def failing_func():
            call_count[0] += 1
            if call_count[0] < 2:
                raise Exception("Temporary failure")
            return "success"
        
        success, result, error = error_recovery.execute_with_retry(
            failing_func,
            max_retries=3
        )
        
        assert success is True
        assert result == "success"
        assert call_count[0] == 2  # Failed once, succeeded on retry
    
    def test_fallback_mechanism(self):
        """Test fallback function execution."""
        error_recovery = get_error_recovery()
        
        def always_fails():
            raise Exception("Always fails")
        
        def fallback():
            return "fallback_result"
        
        success, result, error = error_recovery.execute_with_retry(
            always_fails,
            max_retries=1,
            fallback_func=fallback
        )
        
        assert success is True
        assert result == "fallback_result"


class TestToolRegistry:
    """Test ToolRegistry integration."""
    
    def test_tool_registry_creation(self):
        """Test tool registry creation."""
        mock_clients = {
            "uniprot": Mock(),
            "string": Mock(),
            "mygene": Mock(),
            "quickgo": Mock(),
            "pubmed": Mock(),
            "pubchem": Mock(),
            "chembl": Mock(),
            "ensembl": Mock(),
            "europepmc": Mock(),
        }
        
        registry = create_tool_registry(mock_clients)
        assert registry is not None
        assert len(registry.tools) == 9
    
    def test_tool_names(self):
        """Test getting tool names."""
        mock_clients = {name: Mock() for name in [
            "uniprot", "string", "mygene", "quickgo", "pubmed",
            "pubchem", "chembl", "ensembl", "europepmc"
        ]}
        
        registry = create_tool_registry(mock_clients)
        tool_names = registry.get_tool_names()
        
        assert "query_uniprot" in tool_names
        assert "query_string_interactions" in tool_names
        assert len(tool_names) == 9
    
    def test_tool_execution(self):
        """Test tool execution."""
        mock_client = Mock()
        mock_client.get_protein_info = Mock(return_value={"result": "test"})
        
        mock_clients = {
            "uniprot": mock_client,
            "string": Mock(),
            "mygene": Mock(),
            "quickgo": Mock(),
            "pubmed": Mock(),
            "pubchem": Mock(),
            "chembl": Mock(),
            "ensembl": Mock(),
            "europepmc": Mock(),
        }
        
        registry = create_tool_registry(mock_clients)
        result = registry.execute_tool("query_uniprot", gene="TP53")
        
        assert result == {"result": "test"}
        mock_client.get_protein_info.assert_called_once_with("TP53")


class TestVectorStore:
    """Test VectorStore integration."""
    
    def test_vector_store_initialization(self):
        """Test vector store initializes correctly."""
        vector_store = get_vector_store()
        assert vector_store is not None
    
    def test_add_and_search_case(self):
        """Test adding and searching cases."""
        vector_store = get_vector_store()
        
        # Add a test case
        vector_store.add_case(
            case_id="test_case_1",
            question="Test question about genes",
            analysis_type="deg",
            results={"deg": {"n_genes": 100}},
            metadata={"test": True}
        )
        
        # Search for similar cases
        results = vector_store.search_similar_cases("genes analysis", n_results=1)
        
        assert len(results) > 0
    
    def test_collection_stats(self):
        """Test getting collection statistics."""
        vector_store = get_vector_store()
        stats = vector_store.get_collection_stats()
        
        assert 'name' in stats
        assert 'count' in stats


class TestOptimizedAgent:
    """Test E2scAgentOptimized integration."""
    
    def test_agent_initialization(self, mock_adata, mock_llm, monkeypatch):
        """Test agent initializes with all optimizations."""
        # Mock LLM creation
        monkeypatch.setattr(
            'e2sc.agent.orchestrator_optimized.create_llm_provider',
            lambda **kwargs: mock_llm
        )
        
        agent = E2scAgentOptimized(adata=mock_adata)
        
        assert agent is not None
        assert hasattr(agent, 'memory')
        assert hasattr(agent, 'state_manager')
        assert hasattr(agent, 'error_recovery')
        assert hasattr(agent, 'tool_registry')
    
    def test_agent_has_optimization_methods(self, mock_adata, mock_llm, monkeypatch):
        """Test agent has all optimization methods."""
        monkeypatch.setattr(
            'e2sc.agent.orchestrator_optimized.create_llm_provider',
            lambda **kwargs: mock_llm
        )
        
        agent = E2scAgentOptimized(adata=mock_adata)
        
        assert hasattr(agent, 'get_memory_stats')
        assert hasattr(agent, 'get_state_summary')
        assert hasattr(agent, 'get_error_stats')
        assert hasattr(agent, 'restore_from_checkpoint')
        assert hasattr(agent, 'list_checkpoints')
    
    def test_memory_stats_accessible(self, mock_adata, mock_llm, monkeypatch):
        """Test memory statistics are accessible."""
        monkeypatch.setattr(
            'e2sc.agent.orchestrator_optimized.create_llm_provider',
            lambda **kwargs: mock_llm
        )
        
        agent = E2scAgentOptimized(adata=mock_adata)
        stats = agent.get_memory_stats()
        
        assert stats is not None
        assert 'current_session' in stats
        assert 'long_term' in stats
    
    def test_state_summary_accessible(self, mock_adata, mock_llm, monkeypatch):
        """Test state summary is accessible."""
        monkeypatch.setattr(
            'e2sc.agent.orchestrator_optimized.create_llm_provider',
            lambda **kwargs: mock_llm
        )
        
        agent = E2scAgentOptimized(adata=mock_adata)
        summary = agent.get_state_summary()
        
        assert summary is not None
        assert 'current_state' in summary
        assert 'total_tasks' in summary
    
    def test_error_stats_accessible(self, mock_adata, mock_llm, monkeypatch):
        """Test error statistics are accessible."""
        monkeypatch.setattr(
            'e2sc.agent.orchestrator_optimized.create_llm_provider',
            lambda **kwargs: mock_llm
        )
        
        agent = E2scAgentOptimized(adata=mock_adata)
        stats = agent.get_error_stats()
        
        assert stats is not None
        assert 'stats' in stats
        assert 'recovery_rate' in stats


def test_all_optimizations_integrated():
    """Integration test: verify all optimizations are present."""
    # Test that all optimization modules can be imported
    from e2sc.agent.memory import MemoryManager
    from e2sc.agent.state_manager import StateManager
    from e2sc.agent.error_recovery import ErrorRecovery
    from e2sc.agent.tool_registry import ToolRegistry
    from e2sc.agent.enhanced_planner import EnhancedPlannerAgent
    from e2sc.agent.agent_executor import E2scAgentExecutor
    from e2sc.agent.retriever_enhanced import EnhancedRetrieverAgent
    
    # All imports successful
    assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
