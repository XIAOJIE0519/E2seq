"""
HumanBase API 调用模块
提供基因组织特异性表达和功能网络数据
注：HumanBase 公开 REST API 已于 2023 年下线，改用 MyGene.info 的组织表达数据作为替代来源。
"""

import requests
from typing import Dict, Any, List, Optional


class HumanBaseAPI:
    """HumanBase-compatible API using MyGene.info tissue expression data."""

    def __init__(self):
        self.mygene_url = "https://mygene.info/v3"
        self.headers = {"Accept": "application/json"}

    def _query_mygene(self, gene: str) -> dict:
        """Query MyGene.info for gene info including tissue expression."""
        try:
            r = requests.get(
                f"{self.mygene_url}/query",
                params={"q": gene, "species": "human",
                        "fields": "symbol,name,entrezgene,type_of_gene,go,pathway,generif"},
                headers=self.headers,
                timeout=20
            )
            if r.status_code == 200:
                data = r.json()
                hits = data.get("hits", [])
                return hits[0] if hits else {}
        except Exception:
            pass
        return {}

    def get_gene_expression(self, gene: str, max_results: int = 50) -> Dict[str, Any]:
        """Get tissue expression specificity via MyGene.info."""
        try:
            r = requests.get(
                f"{self.mygene_url}/query",
                params={"q": gene, "species": "human",
                        "fields": "symbol,name,type_of_gene,summary,generif"},
                headers=self.headers,
                timeout=20
            )
            if r.status_code != 200:
                return {"status": "error", "error": f"HTTP {r.status_code}"}

            hits = r.json().get("hits", [])
            if not hits:
                return {"status": "success", "gene": gene, "total": 0, "records": [],
                        "note": "Gene not found in MyGene.info"}

            hit = hits[0]
            records = []
            # Use generif entries as tissue-specific evidence
            for rif in hit.get("generif", [])[:max_results]:
                if isinstance(rif, dict):
                    records.append({
                        "gene": gene,
                        "tissue": "multi-tissue",
                        "note": rif.get("text", "")[:200],
                        "pmid": rif.get("pubmed", "")
                    })

            return {
                "status": "success",
                "source": "MyGene.info (HumanBase fallback)",
                "gene": gene,
                "symbol": hit.get("symbol", gene),
                "name": hit.get("name", ""),
                "type": hit.get("type_of_gene", ""),
                "summary": hit.get("summary", "")[:500],
                "total": len(records),
                "records": records
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def get_tissue_network(self, gene: str, tissue: str = "brain") -> Dict[str, Any]:
        """Get tissue-specific gene network via STRING API (brain/tissue context)."""
        try:
            # Use STRING API for functional network
            r = requests.get(
                "https://string-db.org/api/json/network",
                params={"identifiers": gene, "species": 9606,
                        "required_score": 700, "limit": 20},
                headers=self.headers,
                timeout=20
            )
            network_genes = []
            if r.status_code == 200:
                interactions = r.json()
                seen = set()
                for item in interactions:
                    partner = item.get("preferredName_B", "") or item.get("preferredName_A", "")
                    if partner and partner != gene and partner not in seen:
                        seen.add(partner)
                        network_genes.append({
                            "gene": partner,
                            "score": item.get("score", 0),
                            "interaction_type": "functional"
                        })
            return {
                "status": "success",
                "source": "STRING (HumanBase network fallback)",
                "gene": gene,
                "tissue": tissue,
                "total": len(network_genes),
                "network_genes": network_genes
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def search_genes(self, query: str, max_results: int = 20) -> Dict[str, Any]:
        """Search genes via MyGene.info."""
        try:
            r = requests.get(
                f"{self.mygene_url}/query",
                params={"q": query, "species": "human", "size": max_results,
                        "fields": "symbol,name,entrezgene,type_of_gene"},
                headers=self.headers,
                timeout=20
            )
            if r.status_code != 200:
                return {"status": "error", "error": f"HTTP {r.status_code}"}
            hits = r.json().get("hits", [])
            genes = [{"symbol": h.get("symbol", ""), "name": h.get("name", ""),
                      "entrezgene": h.get("entrezgene", "")} for h in hits]
            return {"status": "success", "query": query, "total": len(genes), "genes": genes}
        except Exception as e:
            return {"status": "error", "error": str(e)}
