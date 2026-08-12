"""Visualization tools using Plotly."""

from typing import Any, Dict, List, Optional

import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from anndata import AnnData

from e2seq.utils import get_logger

logger = get_logger(__name__)


class Visualizer:
    """Visualization tools for single-cell analysis."""

    def __init__(self):
        """Initialize visualizer."""
        self.default_colors = px.colors.qualitative.Set2

    def plot_umap(
        self,
        adata: AnnData,
        color_by: str = "cell_type",
        title: str = "UMAP Visualization"
    ) -> go.Figure:
        """Create UMAP scatter plot.

        Args:
            adata: AnnData object
            color_by: Column to color by
            title: Plot title

        Returns:
            Plotly figure
        """
        logger.info(f"Creating UMAP plot colored by {color_by}")

        # Get UMAP coordinates
        if "X_umap" not in adata.obsm:
            raise ValueError("UMAP coordinates not found. Run sc.tl.umap first.")

        umap_coords = adata.obsm["X_umap"]

        # Create DataFrame
        df = pd.DataFrame({
            "UMAP1": umap_coords[:, 0],
            "UMAP2": umap_coords[:, 1],
            color_by: adata.obs[color_by] if color_by in adata.obs else "Unknown"
        })

        # Create plot
        fig = px.scatter(
            df,
            x="UMAP1",
            y="UMAP2",
            color=color_by,
            title=title,
            template="plotly_white"
        )

        fig.update_traces(marker=dict(size=3, opacity=0.7))
        fig.update_layout(width=800, height=600)

        return fig

    def plot_volcano(
        self,
        deg_results: pd.DataFrame,
        log2fc_col: str = "log2fc",
        pval_col: str = "pvals_adj",
        gene_col: str = "names",
        log2fc_threshold: float = 1.0,
        pval_threshold: float = 0.05
    ) -> go.Figure:
        """Create volcano plot for DEG results.

        Args:
            deg_results: DataFrame with DEG results
            log2fc_col: Column name for log2 fold change
            pval_col: Column name for adjusted p-value
            gene_col: Column name for gene names
            log2fc_threshold: Log2FC threshold for significance
            pval_threshold: P-value threshold

        Returns:
            Plotly figure
        """
        logger.info("Creating volcano plot")

        import numpy as np

        df = deg_results.copy()
        df["-log10(pval)"] = -np.log10(df[pval_col] + 1e-300)

        # Classify genes
        df["significance"] = "Not significant"
        df.loc[(df[log2fc_col] > log2fc_threshold) & (df[pval_col] < pval_threshold), "significance"] = "Up"
        df.loc[(df[log2fc_col] < -log2fc_threshold) & (df[pval_col] < pval_threshold), "significance"] = "Down"

        # Create plot
        fig = px.scatter(
            df,
            x=log2fc_col,
            y="-log10(pval)",
            color="significance",
            hover_data=[gene_col],
            title="Volcano Plot",
            color_discrete_map={"Up": "red", "Down": "blue", "Not significant": "gray"},
            template="plotly_white"
        )

        # Add threshold lines
        fig.add_hline(y=-np.log10(pval_threshold), line_dash="dash", line_color="gray")
        fig.add_vline(x=log2fc_threshold, line_dash="dash", line_color="gray")
        fig.add_vline(x=-log2fc_threshold, line_dash="dash", line_color="gray")

        fig.update_layout(width=800, height=600)

        return fig

    def plot_enrichment(
        self,
        enrichment_results: pd.DataFrame,
        top_n: int = 20,
        title: str = "Enrichment Analysis"
    ) -> go.Figure:
        """Create bubble plot for enrichment results.

        Args:
            enrichment_results: DataFrame with enrichment results
            top_n: Number of top terms to show
            title: Plot title

        Returns:
            Plotly figure
        """
        logger.info("Creating enrichment bubble plot")

        import numpy as np

        df = enrichment_results.head(top_n).copy()

        # Get p-value column
        pval_col = "Adjusted P-value" if "Adjusted P-value" in df.columns else "P-value"
        df["-log10(pval)"] = -np.log10(df[pval_col] + 1e-300)

        # Get gene ratio
        if "Overlap" in df.columns:
            df["gene_ratio"] = df["Overlap"].apply(lambda x: eval(x.split("/")[0]) / eval(x.split("/")[1]) if "/" in str(x) else 0)
        else:
            df["gene_ratio"] = 0.1

        # Create plot
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df["-log10(pval)"],
            y=df["Term"],
            mode="markers",
            marker=dict(
                size=df["gene_ratio"] * 100,
                color=df["-log10(pval)"],
                colorscale="Reds",
                showscale=True,
                colorbar=dict(title="-log10(p-value)")
            ),
            text=df["Term"],
            hovertemplate="<b>%{text}</b><br>-log10(p-value): %{x:.2f}<extra></extra>"
        ))

        fig.update_layout(
            title=title,
            xaxis_title="-log10(p-value)",
            yaxis_title="",
            template="plotly_white",
            width=900,
            height=max(400, top_n * 25)
        )

        return fig

    def plot_network(
        self,
        G: nx.Graph,
        hub_genes: Optional[List[str]] = None,
        title: str = "Protein-Protein Interaction Network"
    ) -> go.Figure:
        """Create network visualization.

        Args:
            G: NetworkX graph
            hub_genes: List of hub genes to highlight
            title: Plot title

        Returns:
            Plotly figure
        """
        logger.info(f"Creating network plot with {G.number_of_nodes()} nodes")

        # Get layout
        pos = nx.spring_layout(G, k=0.5, iterations=50)

        # Create edge traces
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color="#888"),
            hoverinfo="none",
            mode="lines"
        )

        # Create node traces
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        node_size = []

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)

            # Color hub genes differently
            if hub_genes and node in hub_genes:
                node_color.append("red")
                node_size.append(20)
            else:
                node_color.append("lightblue")
                node_size.append(10)

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode="markers+text",
            text=node_text,
            textposition="top center",
            marker=dict(
                size=node_size,
                color=node_color,
                line=dict(width=1, color="white")
            ),
            hoverinfo="text"
        )

        # Create figure
        fig = go.Figure(data=[edge_trace, node_trace])

        fig.update_layout(
            title=title,
            showlegend=False,
            hovermode="closest",
            template="plotly_white",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            width=900,
            height=700
        )

        return fig

    def plot_heatmap(
        self,
        expr_matrix: pd.DataFrame,
        title: str = "Gene Expression Heatmap"
    ) -> go.Figure:
        """Create heatmap of gene expression.

        Args:
            expr_matrix: Expression matrix (genes x cells)
            title: Plot title

        Returns:
            Plotly figure
        """
        logger.info("Creating expression heatmap")

        fig = go.Figure(data=go.Heatmap(
            z=expr_matrix.values,
            x=expr_matrix.columns,
            y=expr_matrix.index,
            colorscale="RdBu_r",
            zmid=0
        ))

        fig.update_layout(
            title=title,
            template="plotly_white",
            width=900,
            height=max(400, len(expr_matrix) * 20)
        )

        return fig
