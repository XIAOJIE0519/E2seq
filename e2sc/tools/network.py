"""Network analysis tools using NetworkX."""

from typing import Any, Dict, List, Optional, Tuple

import networkx as nx
import pandas as pd

from e2sc.data.local_db import STRINGDatabase
from e2sc.utils import get_logger

logger = get_logger(__name__)


class NetworkAnalyzer:
    """Network analysis tools."""
    
    def __init__(self):
        """Initialize network analyzer."""
        self.string_db = STRINGDatabase()
    
    def build_ppi_network(
        self,
        genes: List[str],
        min_score: float = 0.4,
        include_neighbors: bool = False
    ) -> nx.Graph:
        """Build protein-protein interaction network.
        
        Args:
            genes: List of gene symbols
            min_score: Minimum interaction confidence score
            include_neighbors: Whether to include first neighbors
            
        Returns:
            NetworkX graph
        """
        logger.info(f"Building PPI network for {len(genes)} genes")
        
        # Get interactions from STRING database
        interactions = self.string_db.get_network(genes, min_score)
        
        # Build graph
        G = nx.Graph()
        
        for interaction in interactions:
            source = interaction["source_gene"]
            target = interaction["target_gene"]
            score = interaction.get("score", 0.5)
            
            G.add_edge(source, target, weight=score)
        
        logger.info(f"Built network with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
        
        return G
    
    def identify_hub_genes(
        self,
        G: nx.Graph,
        top_n: int = 10,
        method: str = "degree"
    ) -> List[Tuple[str, float]]:
        """Identify hub genes in network.
        
        Args:
            G: NetworkX graph
            top_n: Number of top hubs to return
            method: Centrality method (degree, betweenness, closeness, eigenvector)
            
        Returns:
            List of (gene, centrality_score) tuples
        """
        logger.info(f"Identifying hub genes using {method} centrality")
        
        if method == "degree":
            centrality = nx.degree_centrality(G)
        elif method == "betweenness":
            centrality = nx.betweenness_centrality(G)
        elif method == "closeness":
            centrality = nx.closeness_centrality(G)
        elif method == "eigenvector":
            try:
                centrality = nx.eigenvector_centrality(G, max_iter=1000)
            except (nx.NetworkXError, RuntimeError, ConvergenceWarning) as e:
                logger.warning(f"Eigenvector centrality failed ({type(e).__name__}), using degree instead: {e}")
                centrality = nx.degree_centrality(G)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Sort by centrality
        sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        hubs = sorted_nodes[:top_n]
        
        logger.info(f"Identified {len(hubs)} hub genes")
        return hubs
    
    def detect_communities(self, G: nx.Graph) -> Dict[int, List[str]]:
        """Detect communities in network.
        
        Args:
            G: NetworkX graph
            
        Returns:
            Dictionary mapping community ID to list of genes
        """
        logger.info("Detecting communities")
        
        # Use Louvain algorithm
        from networkx.algorithms import community
        
        communities = community.louvain_communities(G)
        
        # Convert to dictionary
        community_dict = {}
        for i, comm in enumerate(communities):
            community_dict[i] = list(comm)
        
        logger.info(f"Detected {len(community_dict)} communities")
        return community_dict
    
    def get_network_statistics(self, G: nx.Graph) -> Dict[str, Any]:
        """Calculate network statistics.
        
        Args:
            G: NetworkX graph
            
        Returns:
            Dictionary of network statistics
        """
        stats = {
            "n_nodes": G.number_of_nodes(),
            "n_edges": G.number_of_edges(),
            "density": nx.density(G),
            "avg_degree": sum(dict(G.degree()).values()) / G.number_of_nodes() if G.number_of_nodes() > 0 else 0,
        }
        
        # Connected components
        if G.number_of_nodes() > 0:
            components = list(nx.connected_components(G))
            stats["n_components"] = len(components)
            stats["largest_component_size"] = len(max(components, key=len)) if components else 0
        
        # Clustering coefficient
        if G.number_of_nodes() > 0:
            stats["avg_clustering"] = nx.average_clustering(G)
        
        return stats
    
    def find_shortest_path(
        self,
        G: nx.Graph,
        source: str,
        target: str
    ) -> Optional[List[str]]:
        """Find shortest path between two genes.
        
        Args:
            G: NetworkX graph
            source: Source gene
            target: Target gene
            
        Returns:
            List of genes in path, or None if no path exists
        """
        try:
            path = nx.shortest_path(G, source, target)
            logger.info(f"Found path of length {len(path)} from {source} to {target}")
            return path
        except nx.NetworkXNoPath:
            logger.warning(f"No path found from {source} to {target}")
            return None
    
    def export_network(self, G: nx.Graph, format: str = "edgelist") -> pd.DataFrame:
        """Export network to DataFrame.
        
        Args:
            G: NetworkX graph
            format: Export format (edgelist, adjacency)
            
        Returns:
            DataFrame with network data
        """
        if format == "edgelist":
            edges = []
            for u, v, data in G.edges(data=True):
                edges.append({
                    "source": u,
                    "target": v,
                    "weight": data.get("weight", 1.0)
                })
            return pd.DataFrame(edges)
        
        elif format == "adjacency":
            return nx.to_pandas_adjacency(G)
        
        else:
            raise ValueError(f"Unknown format: {format}")
