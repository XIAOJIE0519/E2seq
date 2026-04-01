"""Tests for E2sc agent."""

import pytest
from unittest.mock import Mock, patch
from anndata import AnnData
import numpy as np
import pandas as pd

from e2sc.agent.orchestrator import E2scAgent


@pytest.fixture
def mock_adata():
    """Create mock AnnData object."""
    n_obs = 100
    n_vars = 50
    
    X = np.random.randn(n_obs, n_vars)
    obs = pd.DataFrame({
        "cell_type": ["TypeA"] * 50 + ["TypeB"] * 50
    })
    var = pd.DataFrame(index=[f"Gene{i}" for i in range(n_vars)])
    
    adata = AnnData(X=X, obs=obs, var=var)
    adata.obsm["X_umap"] = np.random.randn(n_obs, 2)
    
    return adata


@pytest.fixture
def mock_llm():
    """Create mock LLM provider."""
    llm = Mock()
    llm.chat = Mock(return_value="Mock response")
    return llm


def test_agent_initialization(mock_adata):
    """Test agent initialization."""
    with patch("e2sc.agent.orchestrator.create_llm_provider") as mock_create_llm:
        mock_create_llm.return_value = Mock()
        
        agent = E2scAgent(adata=mock_adata, llm_provider="openai", api_key="test-key")
        
        assert agent.adata is not None
        assert agent.scanpy_tools is not None
        assert len(agent.history) == 0


def test_load_data(mock_adata):
    """Test loading data."""
    with patch("e2sc.agent.orchestrator.create_llm_provider") as mock_create_llm:
        mock_create_llm.return_value = Mock()
        
        agent = E2scAgent(llm_provider="openai", api_key="test-key")
        agent.load_data(mock_adata)
        
        assert agent.adata is not None
        assert agent.scanpy_tools is not None


def test_chat_without_data():
    """Test chat without loaded data."""
    with patch("e2sc.agent.orchestrator.create_llm_provider") as mock_create_llm:
        mock_create_llm.return_value = Mock()
        
        agent = E2scAgent(llm_provider="openai", api_key="test-key")
        response = agent.chat("Test question")
        
        assert "load" in response["text"].lower()
        assert len(response["plots"]) == 0


def test_clear_history(mock_adata):
    """Test clearing history."""
    with patch("e2sc.agent.orchestrator.create_llm_provider") as mock_create_llm:
        mock_create_llm.return_value = Mock()
        
        agent = E2scAgent(adata=mock_adata, llm_provider="openai", api_key="test-key")
        agent.history = [{"role": "user", "content": "test"}]
        
        agent.clear_history()
        
        assert len(agent.history) == 0
