"""Tests for network analysis."""

import pytest
import networkx as nx

from e2sc.tools.network import NetworkAnalyzer


@pytest.fixture
def sample_graph():
    """Create sample graph."""
    G = nx.Graph()
    G.add_edges_from([
        ("A", "B", {"weight": 0.8}),
        ("B", "C", {"weight": 0.6}),
        ("C", "D", {"weight": 0.7}),
        ("D", "A", {"weight": 0.5}),
        ("A", "C", {"weight": 0.9}),
    ])
    return G


def test_identify_hub_genes(sample_graph):
    """Test hub gene identification."""
    analyzer = NetworkAnalyzer()
    hubs = analyzer.identify_hub_genes(sample_graph, top_n=2)
    
    assert len(hubs) == 2
    assert all(isinstance(h, tuple) for h in hubs)
    assert all(len(h) == 2 for h in hubs)


def test_get_network_statistics(sample_graph):
    """Test network statistics."""
    analyzer = NetworkAnalyzer()
    stats = analyzer.get_network_statistics(sample_graph)
    
    assert stats["n_nodes"] == 4
    assert stats["n_edges"] == 5
    assert "density" in stats
    assert "avg_degree" in stats


def test_find_shortest_path(sample_graph):
    """Test shortest path finding."""
    analyzer = NetworkAnalyzer()
    path = analyzer.find_shortest_path(sample_graph, "A", "D")
    
    assert path is not None
    assert path[0] == "A"
    assert path[-1] == "D"
