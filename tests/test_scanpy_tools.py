"""Tests for Scanpy tools."""

import pytest
import numpy as np
import pandas as pd
from anndata import AnnData

from e2sc.tools.scanpy_tools import ScancpyTools


@pytest.fixture
def sample_adata():
    """Create sample AnnData object."""
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


def test_initialization(sample_adata):
    """Test ScancpyTools initialization."""
    tools = ScancpyTools(sample_adata)
    assert tools.adata is not None


def test_get_cell_types(sample_adata):
    """Test getting cell types."""
    tools = ScancpyTools(sample_adata)
    cell_types = tools.get_cell_types()
    
    assert len(cell_types) == 2
    assert "TypeA" in cell_types
    assert "TypeB" in cell_types


def test_subset_cells(sample_adata):
    """Test subsetting cells."""
    tools = ScancpyTools(sample_adata)
    subset = tools.subset_cells("TypeA")
    
    assert subset.n_obs == 50
    assert all(subset.obs["cell_type"] == "TypeA")


def test_get_dataset_info(sample_adata):
    """Test getting dataset info."""
    tools = ScancpyTools(sample_adata)
    info = tools.get_dataset_info()
    
    assert info["n_cells"] == 100
    assert info["n_genes"] == 50
    assert len(info["cell_types"]) == 2
