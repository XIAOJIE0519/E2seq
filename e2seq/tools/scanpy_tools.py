"""Scanpy-based single-cell analysis tools."""

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import scanpy as sc
from anndata import AnnData

from e2seq.utils import get_logger

logger = get_logger(__name__)


class ScancpyTools:
    """Scanpy-based single-cell analysis tools."""

    def __init__(self, adata: AnnData):
        """Initialize with AnnData object.

        Args:
            adata: AnnData object containing single-cell data
        """
        self.adata = adata
        logger.info(f"Initialized with {adata.n_obs} cells and {adata.n_vars} genes")

    def get_cell_types(self) -> List[str]:
        """Get list of cell types in the dataset."""
        cell_type_col = self._find_cell_type_column()
        if cell_type_col:
            return list(self.adata.obs[cell_type_col].unique())
        return []

    def _find_cell_type_column(self, preferred: Optional[str] = None) -> Optional[str]:
        """Find cell type annotation column.

        Args:
            preferred: User-specified column name (from adata.uns['e2sc_celltype_col'])
        """
        # 1. Honour user-configured column stored in adata.uns
        uns_col = self.adata.uns.get("e2sc_celltype_col", None)
        if uns_col and uns_col in self.adata.obs.columns:
            return uns_col
        # 2. Caller-supplied preferred column
        if preferred and preferred in self.adata.obs.columns:
            return preferred
        # 3. Heuristic fallback
        candidates = ["cell_type", "final_annotation", "celltype", "annotation",
                      "leiden", "louvain", "cluster"]
        for col in candidates:
            if col in self.adata.obs.columns:
                return col
        return None

    def subset_cells(self, cell_type: str) -> AnnData:
        """Subset cells by cell type.

        Args:
            cell_type: Cell type to subset

        Returns:
            Subsetted AnnData object
        """
        cell_type_col = self._find_cell_type_column()
        if not cell_type_col:
            raise ValueError("No cell type column found in adata.obs")

        mask = self.adata.obs[cell_type_col] == cell_type
        subset = self.adata[mask].copy()
        logger.info(f"Subsetted {subset.n_obs} cells of type {cell_type}")
        return subset

    def find_marker_genes(
        self,
        cell_type: str,
        n_genes: int = 50,
        method: str = "wilcoxon"
    ) -> pd.DataFrame:
        """Find marker genes for a cell type.

        Args:
            cell_type: Cell type to find markers for
            n_genes: Number of top genes to return
            method: Statistical test method

        Returns:
            DataFrame with marker genes and statistics
        """
        cell_type_col = self._find_cell_type_column()
        if not cell_type_col:
            raise ValueError("No cell type column found")

        logger.info(f"Finding marker genes for {cell_type}")

        # Run differential expression
        sc.tl.rank_genes_groups(
            self.adata,
            groupby=cell_type_col,
            groups=[cell_type],
            method=method,
            use_raw=False
        )

        # Extract results
        result = sc.get.rank_genes_groups_df(self.adata, group=cell_type)
        result = result.head(n_genes)

        logger.info(f"Found {len(result)} marker genes")
        return result

    def differential_expression(
        self,
        group1: str,
        group2: str,
        groupby: Optional[str] = None,
        method: str = "wilcoxon"
    ) -> pd.DataFrame:
        """Perform differential expression analysis between two groups.

        Args:
            group1: First group name
            group2: Second group name
            groupby: Column to group by (default: cell_type column)
            method: Statistical test method

        Returns:
            DataFrame with DEG results
        """
        if groupby is None:
            groupby = self._find_cell_type_column()

        logger.info(f"Comparing {group1} vs {group2}")

        # Run differential expression
        sc.tl.rank_genes_groups(
            self.adata,
            groupby=groupby,
            groups=[group1],
            reference=group2,
            method=method,
            use_raw=False
        )

        # Extract results
        result = sc.get.rank_genes_groups_df(self.adata, group=group1)

        # Add log2 fold change
        if "logfoldchanges" in result.columns:
            result["log2fc"] = result["logfoldchanges"] / np.log(2)

        logger.info(f"Found {len(result)} genes")
        return result

    def get_highly_variable_genes(self, n_top_genes: int = 2000) -> List[str]:
        """Identify highly variable genes.

        Args:
            n_top_genes: Number of top variable genes

        Returns:
            List of gene names
        """
        if "highly_variable" not in self.adata.var.columns:
            sc.pp.highly_variable_genes(self.adata, n_top_genes=n_top_genes)

        hvg = self.adata.var[self.adata.var["highly_variable"]].index.tolist()
        logger.info(f"Identified {len(hvg)} highly variable genes")
        return hvg

    def get_gene_expression(self, genes: List[str], cell_type: Optional[str] = None) -> pd.DataFrame:
        """Get expression matrix for specific genes.

        Args:
            genes: List of gene names
            cell_type: Optional cell type to filter

        Returns:
            DataFrame with expression values
        """
        adata = self.adata
        if cell_type:
            adata = self.subset_cells(cell_type)

        # Filter genes that exist
        genes = [g for g in genes if g in adata.var_names]

        if len(genes) == 0:
            logger.warning("No genes found in dataset")
            return pd.DataFrame()

        # Extract expression
        expr = adata[:, genes].to_df()
        return expr

    def get_top_genes_by_group(
        self,
        group_col: str = "group",
        n_top_genes: int = 20,
        method: str = "mean"
    ) -> Dict[str, Any]:
        """Generate top-expressed genes × disease-group matrix.

        Args:
            group_col: obs column containing group labels (e.g. 'group' with HC/UC/CD).
            n_top_genes: Number of top genes per group.
            method: 'mean' or 'median'.

        Returns:
            Same structure as get_top_genes_matrix but keyed by group label.
        """
        import numpy as np
        import scipy.sparse as sp

        if group_col not in self.adata.obs.columns:
            raise ValueError(f"Column '{group_col}' not found in adata.obs. Available: {list(self.adata.obs.columns)}")

        groups = list(self.adata.obs[group_col].unique())
        logger.info(f"Building gene×group matrix for {len(groups)} groups in '{group_col}'")

        X = self.adata.X
        if sp.issparse(X):
            X = X.toarray()
        gene_names = list(self.adata.var_names)

        matrix: Dict[str, Dict[str, float]] = {}
        top_genes_per_group: Dict[str, List[str]] = {}

        for grp in groups:
            mask = (self.adata.obs[group_col] == grp).values
            if mask.sum() == 0:
                continue
            grp_X = X[mask, :]
            expr = np.median(grp_X, axis=0) if method == "median" else np.mean(grp_X, axis=0)
            gene_expr = {g: float(expr[i]) for i, g in enumerate(gene_names)}
            top_genes = sorted(gene_expr, key=lambda g: gene_expr[g], reverse=True)[:n_top_genes]
            top_genes_per_group[grp] = top_genes
            matrix[grp] = {g: round(gene_expr[g], 4) for g in top_genes}

        all_top_genes = sorted(set(g for gs in top_genes_per_group.values() for g in gs))
        # Re-sort by mean expression across groups (highest first), not alphabetically
        gene_mean_expr = {}
        for grp, gdict in matrix.items():
            for g, val in gdict.items():
                gene_mean_expr[g] = gene_mean_expr.get(g, 0) + val
        all_top_genes = sorted(gene_mean_expr, key=lambda g: gene_mean_expr[g], reverse=True)
        logger.info(f"Group matrix built: {len(groups)} groups, {len(all_top_genes)} unique top genes")
        return {
            "matrix": matrix,
            "top_genes_per_group": top_genes_per_group,
            "all_top_genes": all_top_genes,
            "groups": groups,
            "group_col": group_col,
            "n_genes_total": self.adata.n_vars,
            "method": method,
        }

    def get_available_groups(self) -> Dict[str, List[str]]:
        """Return all categorical obs columns and their unique values for UI selection."""
        result = {}
        for col in self.adata.obs.columns:
            if self.adata.obs[col].dtype.name in ("category", "object"):
                uniq = [str(v) for v in self.adata.obs[col].unique() if str(v) != "nan"]
                if 1 < len(uniq) <= 50:  # skip columns with too few or too many values
                    result[col] = sorted(uniq)
        return result

    def get_top_genes_matrix(
        self,
        n_top_genes: int = 20,
        method: str = "mean",
        celltype_col: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a top-expressed genes × cell type matrix.

        For each cell type, compute the mean (or median) expression of every gene,
        then return the top-N genes per cell type AND the full ranked matrix.

        Args:
            n_top_genes: Number of top genes to return per cell type.
            method: Aggregation method — 'mean' or 'median'.

        Returns:
            {
              'matrix': {cell_type: {gene: mean_expr, ...}, ...},
              'top_genes_per_celltype': {cell_type: [gene1, gene2, ...], ...},
              'all_top_genes': [gene, ...],   # union across all cell types
              'cell_types': [...],
              'n_genes_total': int,
              'method': str
            }
        """
        import numpy as np

        cell_type_col = self._find_cell_type_column(preferred=celltype_col)
        if not cell_type_col:
            raise ValueError("No cell type column found in adata.obs")

        cell_types = list(self.adata.obs[cell_type_col].unique())
        logger.info(f"Building gene×cell-type matrix for {len(cell_types)} cell types")

        matrix: Dict[str, Dict[str, float]] = {}
        top_genes_per_ct: Dict[str, List[str]] = {}

        # Use dense expression matrix (works for both sparse and dense)
        import scipy.sparse as sp
        X = self.adata.X
        if sp.issparse(X):
            X = X.toarray()

        gene_names = list(self.adata.var_names)

        for ct in cell_types:
            mask = (self.adata.obs[cell_type_col] == ct).values
            if mask.sum() == 0:
                continue
            ct_X = X[mask, :]  # cells × genes
            if method == "median":
                expr = np.median(ct_X, axis=0)
            else:
                expr = np.mean(ct_X, axis=0)

            # Build the gene-to-expression map for this cell type.
            gene_expr = {gene: float(expr[i]) for i, gene in enumerate(gene_names)}

            # Top N genes by expression
            top_genes = sorted(gene_expr, key=lambda g: gene_expr[g], reverse=True)[:n_top_genes]
            top_genes_per_ct[ct] = top_genes
            # Store only top genes in matrix to keep response lean
            matrix[ct] = {g: round(gene_expr[g], 4) for g in top_genes}

        # Union of all top genes across cell types, sorted by mean expression
        # (highest first), not alphabetically.
        gene_mean_expr: dict = {}
        for ct_genes in top_genes_per_ct.values():
            for g in ct_genes:
                gene_mean_expr[g] = gene_mean_expr.get(g, 0) + matrix.get(list(top_genes_per_ct.keys())[0], {}).get(g, 0)
        # Use per-gene sum of expression across all cell types
        gene_sum_expr: dict = {}
        for ct, gdict in matrix.items():
            for g, val in gdict.items():
                gene_sum_expr[g] = gene_sum_expr.get(g, 0) + val
        all_top_genes = sorted(
            set(g for genes in top_genes_per_ct.values() for g in genes),
            key=lambda g: gene_sum_expr.get(g, 0),
            reverse=True
        )

        logger.info(f"Matrix built: {len(cell_types)} cell types, {len(all_top_genes)} unique top genes")
        return {
            "matrix": matrix,
            "top_genes_per_celltype": top_genes_per_ct,
            "all_top_genes": all_top_genes,
            "cell_types": cell_types,
            "n_genes_total": self.adata.n_vars,
            "method": method,
        }

    def get_dataset_info(self) -> Dict[str, Any]:
        """Get dataset information.

        Returns:
            Dictionary with dataset statistics
        """
        cell_type_col = self._find_cell_type_column()

        info = {
            "n_cells": self.adata.n_obs,
            "n_genes": self.adata.n_vars,
            "cell_types": self.get_cell_types() if cell_type_col else [],
            "obs_columns": list(self.adata.obs.columns),
            "var_columns": list(self.adata.var.columns),
        }

        if cell_type_col:
            info["cell_type_counts"] = self.adata.obs[cell_type_col].value_counts().to_dict()

        return info
