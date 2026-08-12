"""Bilingual API examples / 双语 API 示例.

This file is an optional standalone demonstration.  The web application uses
the Agent + RAG pipeline in ``e2seq/``; this script only shows direct API calls.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

try:  # Works both as ``python api/example_usage.py`` and as a package import.
    from .uniprot_api import UniProt_API
    from .pubchem_api import PubChem_API
    from .pubmed_api import PubMed_API
except ImportError:  # pragma: no cover - convenience for direct execution.
    from uniprot_api import UniProt_API
    from pubchem_api import PubChem_API
    from pubmed_api import PubMed_API


class BioInfoSearch:
    """Small direct-query helper / 直接查询示例工具。"""

    def __init__(self, email: str = "your_email@example.com") -> None:
        self.uniprot = UniProt_API()
        self.pubchem = PubChem_API()
        self.pubmed = PubMed_API(email=email)

    def search_gene_comprehensive(self, gene_name: str) -> dict:
        """Query protein annotations and literature / 查询蛋白注释与文献。"""
        print(f"\n{'=' * 60}\nQuerying gene / 正在查询基因: {gene_name}\n{'=' * 60}")

        protein_result = self.uniprot.search_by_gene(gene_name, top_n=5)
        if protein_result.get("status") == "success" and protein_result.get("results"):
            print(f"[OK / 完成] Protein records / 蛋白记录: {len(protein_result['results'])}")
            top = protein_result["results"][0]
            print(f"  Name / 名称: {top.get('protein_name', '')}")
            print(f"  Accession / 登录号: {top.get('accession', '')}")
            print(f"  Score / 评分: {top.get('annotation_score', '')}")
        else:
            print("[WARN / 提示] No protein annotation found / 未找到蛋白注释")

        time.sleep(0.5)
        literature = self.pubmed.search_and_get_details(
            f"{gene_name}[Gene] AND human", max_results=5
        )
        if literature.get("status") == "success" and literature.get("articles"):
            print(f"[OK / 完成] Literature / 文献: {literature.get('total_count', 0)}")
            for number, article in enumerate(literature["articles"][:3], 1):
                print(f"  {number}. {article.get('title', '')[:80]}...")
        else:
            print("[WARN / 提示] No literature found / 未找到相关文献")

        return {"gene": gene_name, "protein_info": protein_result, "literature": literature}

    def search_metabolite_comprehensive(self, metabolite_name: str) -> dict:
        """Query a compound and literature / 查询化合物与相关文献。"""
        print(f"\n{'=' * 60}\nQuerying metabolite / 正在查询代谢物: {metabolite_name}\n{'=' * 60}")

        compound_result = self.pubchem.search_and_get_details(metabolite_name, top_n=1)
        compounds = compound_result.get("compounds") or []
        if compound_result.get("status") == "success" and compounds:
            props = compounds[0].get("properties", {})
            print(f"[OK / 完成] Compound found / 找到化合物: CID {props.get('CID', '')}")
            print(f"  Formula / 分子式: {props.get('MolecularFormula', '')}")
            print(f"  Weight / 分子量: {props.get('MolecularWeight', '')}")
        else:
            print("[WARN / 提示] No compound found / 未找到化合物")

        time.sleep(0.5)
        literature = self.pubmed.search_and_get_details(
            f"{metabolite_name} AND metabolism", max_results=5
        )
        if literature.get("status") == "success" and literature.get("articles"):
            print(f"[OK / 完成] Literature / 文献: {literature.get('total_count', 0)}")
        else:
            print("[WARN / 提示] No literature found / 未找到相关文献")

        return {
            "metabolite": metabolite_name,
            "compound_info": compound_result,
            "literature": literature,
        }

    def search_pathway_genes(self, gene_list: list[str]) -> dict[str, dict | None]:
        """Query one UniProt record per gene / 批量查询每个基因的 UniProt 记录。"""
        print(f"\nBatch query / 正在批量查询: {len(gene_list)} genes / 个基因")
        results: dict[str, dict | None] = {}
        for number, gene in enumerate(gene_list, 1):
            print(f"[{number}/{len(gene_list)}] {gene}")
            result = self.uniprot.search_by_gene(gene, top_n=1)
            records = result.get("results") or []
            results[gene] = records[0] if result.get("status") == "success" and records else None
            time.sleep(0.3)
        return results


if __name__ == "__main__":
    searcher = BioInfoSearch(email="your_email@example.com")
    gene_result = searcher.search_gene_comprehensive("TP53")
    metabolite_result = searcher.search_metabolite_comprehensive("glucose")
    genes = ["TP53", "BAX", "BCL2", "CASP3", "CASP9"]
    pathway_result = searcher.search_pathway_genes(genes)

    output = {
        "gene_query": {
            "gene": gene_result["gene"],
            "protein_count": len(gene_result["protein_info"].get("results", [])),
            "literature_count": gene_result["literature"].get("total_count", 0),
        },
        "metabolite_query": {
            "metabolite": metabolite_result["metabolite"],
            "compound_found": metabolite_result["compound_info"].get("status") == "success",
            "literature_count": metabolite_result["literature"].get("total_count", 0),
        },
        "pathway_genes": {
            "total": len(genes),
            "found": sum(value is not None for value in pathway_result.values()),
            "genes": list(pathway_result),
        },
    }
    output_path = Path(__file__).resolve().parent / "query_results.json"
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved query summary / 查询结果摘要已保存到: {output_path}")
