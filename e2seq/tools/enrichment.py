"""Enrichment analysis tools using GSEApy."""

from typing import Any, Dict, List, Optional

import gseapy as gp
import pandas as pd

from e2seq.utils import get_logger

logger = get_logger(__name__)


class EnrichmentAnalyzer:
    """Enrichment analysis using GSEApy."""

    def __init__(self):
        """Initialize enrichment analyzer."""
        self.supported_libraries = [
            "GO_Biological_Process_2023",
            "GO_Molecular_Function_2023",
            "GO_Cellular_Component_2023",
            "KEGG_2021_Human",
            "Reactome_2022",
            "WikiPathway_2023_Human",
        ]

    def enrichr_analysis(
        self,
        gene_list: List[str],
        gene_sets: str = "GO_Biological_Process_2023",
        organism: str = "human",
        cutoff: float = 0.05
    ) -> pd.DataFrame:
        """Perform Enrichr analysis.

        Args:
            gene_list: List of gene symbols
            gene_sets: Gene set library name
            organism: Organism name
            cutoff: P-value cutoff

        Returns:
            DataFrame with enrichment results
        """
        logger.info(f"Running Enrichr analysis with {len(gene_list)} genes")

        try:
            enr = gp.enrichr(
                gene_list=gene_list,
                gene_sets=gene_sets,
                organism=organism,
                cutoff=cutoff,
                no_plot=True
            )

            results = enr.results
            logger.info(f"Found {len(results)} enriched terms")
            return results

        except Exception as e:
            logger.error(f"Enrichr analysis failed: {e}")
            return pd.DataFrame()

    def go_enrichment(
        self,
        gene_list: List[str],
        category: str = "BP",
        cutoff: float = 0.05
    ) -> Dict[str, pd.DataFrame]:
        """Perform GO enrichment analysis.

        Args:
            gene_list: List of gene symbols
            category: GO category (BP, MF, CC, or all)
            cutoff: P-value cutoff

        Returns:
            Dictionary of DataFrames with results for each category
        """
        categories = {
            "BP": "GO_Biological_Process_2023",
            "MF": "GO_Molecular_Function_2023",
            "CC": "GO_Cellular_Component_2023",
        }

        if category.upper() == "ALL":
            selected = categories
        else:
            selected = {category.upper(): categories.get(category.upper())}

        results = {}
        for cat, gene_set in selected.items():
            logger.info(f"Running GO {cat} enrichment")
            df = self.enrichr_analysis(gene_list, gene_set, cutoff=cutoff)
            if not df.empty:
                results[cat] = df

        return results

    def kegg_enrichment(
        self,
        gene_list: List[str],
        cutoff: float = 0.05
    ) -> pd.DataFrame:
        """Perform KEGG pathway enrichment.

        Args:
            gene_list: List of gene symbols
            cutoff: P-value cutoff

        Returns:
            DataFrame with KEGG enrichment results
        """
        logger.info("Running KEGG enrichment")
        return self.enrichr_analysis(gene_list, "KEGG_2021_Human", cutoff=cutoff)

    def reactome_enrichment(
        self,
        gene_list: List[str],
        cutoff: float = 0.05
    ) -> pd.DataFrame:
        """Perform Reactome pathway enrichment.

        Args:
            gene_list: List of gene symbols
            cutoff: P-value cutoff

        Returns:
            DataFrame with Reactome enrichment results
        """
        logger.info("Running Reactome enrichment")
        return self.enrichr_analysis(gene_list, "Reactome_2022", cutoff=cutoff)

    def gsea_analysis(
        self,
        gene_expr: pd.DataFrame,
        gene_sets: str = "KEGG_2021_Human",
        cls: Optional[List[str]] = None,
        permutation_num: int = 1000
    ) -> Any:
        """Perform GSEA analysis.

        Args:
            gene_expr: Gene expression DataFrame (genes x samples)
            gene_sets: Gene set library
            cls: Class labels for samples
            permutation_num: Number of permutations

        Returns:
            GSEA results object
        """
        logger.info("Running GSEA analysis")

        try:
            gs_res = gp.gsea(
                data=gene_expr,
                gene_sets=gene_sets,
                cls=cls,
                permutation_num=permutation_num,
                no_plot=True
            )

            logger.info("GSEA analysis completed")
            return gs_res

        except Exception as e:
            logger.error(f"GSEA analysis failed: {e}")
            return None

    def format_results(self, results: pd.DataFrame, top_n: int = 20) -> Dict[str, Any]:
        """Format enrichment results for display.

        Args:
            results: Enrichment results DataFrame
            top_n: Number of top terms to include

        Returns:
            Formatted results dictionary
        """
        if results.empty:
            return {"terms": [], "summary": "No significant enrichment found"}

        top_results = results.head(top_n)

        formatted = {
            "n_total": len(results),
            "n_shown": len(top_results),
            "terms": [],
        }

        for _, row in top_results.iterrows():
            term = {
                "name": row.get("Term", ""),
                "p_value": row.get("P-value", row.get("Adjusted P-value", 1.0)),
                "genes": row.get("Genes", "").split(";") if "Genes" in row else [],
                "overlap": row.get("Overlap", ""),
            }
            formatted["terms"].append(term)

        # Generate summary
        top_terms = [t["name"] for t in formatted["terms"][:5]]
        formatted["summary"] = f"Found {len(results)} enriched terms. Top pathways: {', '.join(top_terms)}"

        return formatted
