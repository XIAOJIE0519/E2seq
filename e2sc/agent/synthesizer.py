"""Synthesizer agent for generating final reports."""

import re as _re
from typing import Any, Dict, List

from e2sc.llm import SYNTHESIZER_PROMPT
from e2sc.utils import get_logger

logger = get_logger(__name__)

# Patterns to strip from LLM output — any "no data" / empty-result language
_NO_DATA_PATTERNS = [
    r'\[Open Targets\] No data for [^.\n]+[.\n]?',
    r'\[ClinVar\] No data for [^.\n]+[.\n]?',
    r'\[GTEx\] No data for [^.\n]+[.\n]?',
    r'\[Reactome\] No data for [^.\n]+[.\n]?',
    r'\[STRING\] No data for [^.\n]+[.\n]?',
    r'\[TRRUST\] No data for [^.\n]+[.\n]?',
    r'\[GUTMGENE\] No data for [^.\n]+[.\n]?',
    r'\[HMDB\] No data for [^.\n]+[.\n]?',
    r'\[QuickGO\] No data for [^.\n]+[.\n]?',
    r'\[UniProt\] No data for [^.\n]+[.\n]?',
    r'\[MyGene\] No data for [^.\n]+[.\n]?',
    r'\[Ensembl\] No data for [^.\n]+[.\n]?',
    r'\[ChEMBL\] No data for [^.\n]+[.\n]?',
    r'\[PubMed\] No data for [^.\n]+[.\n]?',
    r'\[EuropePMC\] No data for [^.\n]+[.\n]?',
    r'No data for \w+(?:,\s*\w+)*[.\n]?',
    r'\u5747\u672a\u68c0\u7d22\u5230[^\n]*',
    r'\u672a\u68c0\u7d22\u5230\u76f8\u5173[^\n]*',
    r'\u6570\u636e\u7f3a\u53e3[^\n]*',
    r'\u77e5\u8bc6\u56fe\u8c31\u7f3a\u5931\u8fb9[^\n]*',
    r'\u7814\u7a76\u5c55\u671b[^\n]*',
    r'\u5c1a\u5f85\u7814\u7a76[^\n]*',
    r'\u6709\u5f85\u8fdb\u4e00\u6b65[^\n]*',
    r'\u76ee\u524d\u5c1a\u65e0[^\n]*',
    r'\u76f8\u5173\u6570\u636e\u6709\u9650[^\n]*',
    r'\u4fe1\u606f\u4e0d\u8db3[^\n]*',
    r'\u6682\u65e0\u76f8\u5173\u6570\u636e[^\n]*',
    r'\u5c1a\u65e0\u8bb0\u5f55[^\n]*',
    r'\u672a\u6536\u5f55\u4e8e[^\n]*',
    r'\u6570\u636e\u5e93\u4e2d\u672a\u6536\u5f55[^\n]*',
]

_NO_DATA_CTX_MARKERS = [
    "No data", "no data",
    "\u672a\u68c0\u7d22\u5230", "\u65e0\u8bb0\u5f55", "\u65e0\u6570\u636e",
    "[Open Targets] No", "[ClinVar] No", "[GTEx] No",
    "[Reactome] No", "[STRING] No", "[TRRUST] No",
    "[GUTMGENE] No", "[HMDB] No", "[QuickGO] No",
    "[UniProt] No", "[MyGene] No", "[Ensembl] No",
    "[ChEMBL] No", "[PubMed] No", "[EuropePMC] No",
]


class SynthesizerAgent:
    """Agent for synthesizing analysis results into Nature-level reports."""

    def __init__(self, llm):
        self.llm = llm

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------
    def synthesize(
        self,
        question: str,
        results: Dict[str, Any],
        knowledge: Dict[str, Any],
        history: List[Dict[str, str]] = None,
        output_mode: str = "detailed",
        is_comprehensive: bool = False,
    ) -> Dict[str, Any]:
        """Synthesize Graph-RAG knowledge into a Nature/Cell-level response."""
        logger.info("Synthesizing final report")

        results_summary = self._format_results(results)
        results_summary = self._truncate_to_token_budget(results_summary, max_chars=6000)
        knowledge_summary = self._format_knowledge(knowledge)
        knowledge_summary = self._truncate_to_token_budget(knowledge_summary, max_chars=16000)
        similar_cases_summary = self._format_similar_cases(knowledge.get("similar_cases", []))
        has_knowledge = bool(knowledge.get("genes")) or bool(knowledge.get("similar_cases"))

        prompt = SYNTHESIZER_PROMPT.format(
            question=question,
            results=results_summary,
            knowledge=knowledge_summary,
            similar_cases=similar_cases_summary,
        )

        # Prepend RAG vector-store context chunks (highest evidence priority)
        rag_context = knowledge.get("rag_context", "")
        if rag_context:
            # Cap RAG context to fit within the model's context window (32768 tokens)
            # Total budget: system(~2500) + history(~2000) + template(~800)
            #   + results(4000) + knowledge(6000) + rag(3000) ≈ 18300 chars ≤ 32768 tokens
            rag_context = self._truncate_to_token_budget(rag_context, max_chars=3000)
            prompt = (
                "=== RAG Retrieved Knowledge (highest priority — primary evidence source) ===\n"
                + rag_context
                + "\n\n=== Additional Aggregated Knowledge ===\n"
                + prompt
            )

        system_message = self._build_system_message(question, is_comprehensive, output_mode)

        messages = [{"role": "system", "content": system_message}]
        if history:
            for h in history[-10:]:
                role = h.get("role", "")
                content = h.get("content", "")
                if role in ("user", "assistant") and content:
                    messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": prompt})

        response_text = self.llm.chat(messages)

        # Strip forbidden "No data" / outlook phrases the LLM may have emitted
        for pat in _NO_DATA_PATTERNS:
            response_text = _re.sub(pat, "", response_text)
        response_text = _re.sub(r"\n{3}", "\n\n", response_text).strip()

        retrieval_status = {
            "genes_retrieved": len(knowledge.get("genes", {})),
            "similar_cases_found": len(knowledge.get("similar_cases", [])),
            "has_sufficient_knowledge": has_knowledge,
        }

        response = {
            "text": response_text,
            "plots": results.get("plots", []),
            "data": {
                "deg": results.get("deg"),
                "enrichment": results.get("enrichment"),
                "network": results.get("network"),
                "knowledge": knowledge,
                "retrieval_status": retrieval_status,
            },
        }
        logger.info(
            f"Report synthesis completed. "
            f"{retrieval_status['genes_retrieved']} genes, "
            f"{retrieval_status['similar_cases_found']} similar cases"
        )
        return response

    # ------------------------------------------------------------------
    # System message builder
    # ------------------------------------------------------------------
    def _build_system_message(
        self, question: str, is_comprehensive: bool, output_mode: str
    ) -> str:
        return (
            "You are an expert computational biologist and translational medicine scientist. "
            "You have been given a rich multi-database knowledge base built by querying every gene "
            "against ALL of the following sources: "
            "UniProt, MyGene, QuickGO, Ensembl, ChEMBL, Open Targets, ClinVar, CIViC, GWAS Catalog, "
            "Reactome, GTEx/HPA, HumanBase/TISSUES, BioGRID, Alliance, PubMed, EuropePMC (online); "
            "STRING, HMDB, TRRUST, GUTMGENE (local).\n\n"
            "Your task is to answer the user's question by synthesizing ALL available evidence from this "
            "knowledge base into flowing, rigorous academic Chinese prose.\n\n"
            "RULES:\n"
            "1. ONLY use information explicitly present in the provided knowledge base context."
            " Do NOT fabricate data."
            " Do NOT cite papers not listed in the PubMed/EuropePMC sections.\n"
            "2. Cite the source inline after every biological claim: "
            "[UniProt], [MyGene], [QuickGO], [Ensembl], [ChEMBL], [Open Targets], [ClinVar], [CIViC], "
            "[GWAS], [Reactome], [GTEx], [HumanBase], [BioGRID], [Alliance], [STRING], [HMDB], "
            "[TRRUST], [GUTMGENE], [PubMed:PMID], [EuropePMC:PMID].\n"
            "3. When a source returned no data for a particular gene, simply omit that source-gene "
            "combination — do NOT write phrases like 'No data', '未检索到', '暂无', '相关数据有限', "
            "'数据缺口', '尚无', '未找到', 'Network unavailable', or any similar gap-filler. "
            "Focus entirely on what IS present in the data.\n"
            "4. Use the EXACT disease group names, cell type names, and expression values from the "
            "input context — never substitute generic terms.\n"
            "5. Let the user's question and the actual evidence freely determine the narrative "
            "structure, depth, and emphasis. Do NOT impose any fixed template, section order, "
            "or topic list on the output.\n"
            "6. Never truncate mid-sentence. Complete every thought.\n"
            "7. Write at the level of a Nature / Cell / Nature Medicine research article discussion "
            "or review section — precise, mechanistic, deeply integrated across evidence layers."
        )

    # ------------------------------------------------------------------
    # Formatting helpers
    # ------------------------------------------------------------------
    def _format_results(self, results: Dict[str, Any]) -> str:
        sections = []

        # ── CSV / differential expression table mode ──────────────────────
        if results.get("gene_context"):
            sections.append(results["gene_context"])
            return "\n".join(sections)

        # ── scRNA-seq / h5ad mode with matrix_context ──────────────────
        if results.get("matrix_context"):
            ctx = results["matrix_context"]
            genes = ctx.get("genes_queried", [])
            ct_focus = ctx.get("cell_type_focus", "all cell types")
            sections.append(f"Cell type focus: {ct_focus}")
            # 显示基因（上限50个）
            sections.append(f"ALL genes from this analysis ({len(genes)} total): {', '.join(genes[:50])}")
            if len(genes) > 50:
                sections.append(f"... 以及其他 {len(genes) - 50} 个基因")
            # Disease group expression — 每个组最多10个基因
            grp_map = ctx.get("top_genes_per_group", {})
            if grp_map:
                sections.append("\n=== TOP EXPRESSED GENES PER DISEASE GROUP (gene: mean_expr) ===")
                for grp, gs in grp_map.items():
                    if isinstance(gs, dict):
                        genes_str = ", ".join(f"{g}:{v:.3f}" for g, v in list(gs.items())[:10])
                    else:
                        genes_str = ", ".join(str(g) for g in gs[:10])
                    sections.append(f"  {grp}: {genes_str}")
            # Differential genes — 每组最多8个
            diff_map = ctx.get("diff_genes_per_group", {})
            if diff_map:
                sections.append("\n=== DIFFERENTIALLY HIGH GENES PER GROUP VS OTHERS (gene: fold_change) ===")
                for grp, gene_list in diff_map.items():
                    if gene_list:
                        sections.append(f"  {grp}: {', '.join(gene_list[:8])}")
            # Cell type — 每型最多6个
            ct_map = ctx.get("top_genes_per_celltype", {})
            if ct_map:
                sections.append("\n=== TOP EXPRESSED GENES PER CELL TYPE ===")
                for ct, gs in ct_map.items():
                    g_list = list(gs.keys())[:6] if isinstance(gs, dict) else gs[:6]
                    sections.append(f"  {ct}: {', '.join(g_list)}")
            # Cell type × group joint — 每组最多4个
            ct_grp_joint = ctx.get("ct_grp_joint", {})
            if ct_grp_joint:
                sections.append("\n=== CELL TYPE × DISEASE GROUP JOINT TOP GENES (gene(expr)) ===")
                for ct_lbl, grp_dict in ct_grp_joint.items():
                    parts = []
                    for grp_lbl, genes_list in grp_dict.items():
                        parts.append(f"{grp_lbl}=[{','.join(genes_list[:4])}]")
                    if parts:
                        sections.append(f"  {ct_lbl}: {' | '.join(parts)}")
            sections.append("\nCRITICAL: Base your analysis on the expression values and fold changes above. "
                           "You have access to ALL genes listed — interpret them all, do not limit yourself to only the first few.")
        elif results.get("deg"):
            deg_df = results["deg"]["results"]
            top_genes = deg_df["names"].head(10).tolist() if "names" in deg_df.columns else []
            sections.append(f"DEG top genes: {', '.join(top_genes)}")
        return "\n".join(sections) if sections else "No analysis results available."

    def _format_knowledge(self, knowledge: Dict[str, Any]) -> str:
        """Compact, high-density gene knowledge formatting to fit within token budget.

        Strategy: only include genes with meaningful data, cap each gene ~200 chars,
        show top 30 genes. The LLM already knows what databases were queried.
        """
        genes_info = knowledge.get("genes", {})
        if not genes_info:
            return "No gene information retrieved."

        # Score genes by data richness (more non-empty fields = more important)
        def gene_score(gene: str, info: dict) -> int:
            score = 0
            for field in ["function", "pathways", "go_terms", "ot_diseases", "drug_targets",
                           "interactions", "regulators", "tf_targets", "gut_microbes",
                           "metabolites", "reactome_pathways", "gene_summary",
                           "clinvar_variants", "gtex_tissues", "humanbase_tissues",
                           "gwas_snps", "biogrid_interactions", "civic_variants",
                           "alliance_homologs"]:
                val = info.get(field)
                if val and (isinstance(val, list) and val or isinstance(val, str) and val):
                    score += 1
            return score

        scored = sorted(
            [(g, i, gene_score(g, i)) for g, i in genes_info.items()],
            key=lambda x: x[2], reverse=True
        )

        # Priority: drug targets > disease associations > others (take top 30)
        def has_priority_data(info: dict) -> bool:
            return bool(info.get("drug_targets") or info.get("ot_diseases"))

        priority_genes = [(g, i) for g, i, _ in scored if has_priority_data(i)]
        remaining = [(g, i) for g, i, _ in scored if not has_priority_data(i)]
        top_genes = (priority_genes + remaining)[:60]

        lines = [f"=== GENE KNOWLEDGE (top {len(top_genes)} / {len(genes_info)} genes) ===\n"]

        for gene, info in top_genes:
            parts = []

            # 1. Core function — most compact representation
            fn = info.get("function") or (info.get("uniprot") or {}).get("function", "")
            if fn:
                parts.append(f"Fn:{fn[:200]}")
            elif info.get("gene_summary"):
                parts.append(f"Sum:{info['gene_summary'][:200]}")

            # 2. Pathways (compact comma list)
            pws = info.get("pathways") or info.get("reactome_pathways") or []
            if pws:
                parts.append(f"Pw:{','.join(str(p)[:40] for p in pws[:6])}")

            # 3. GO terms
            gos = info.get("go_terms") or []
            if gos:
                parts.append(f"GO:{','.join(str(g)[:30] for g in gos[:8])}")

            # 4. Disease associations
            dis = info.get("ot_diseases") or []
            if dis:
                parts.append(f"Dis:{','.join(str(d)[:40] for d in dis[:5])}")

            # 5. Drug targets
            drugs = info.get("drug_targets") or []
            if drugs:
                parts.append(f"Drg:{','.join(str(d)[:50] for d in drugs[:5])}")

            # 6. PPI — top 8 partners with scores
            ppi = info.get("interactions") or []
            if ppi:
                ppi_parts = []
                for iact in ppi[:8]:
                    p = iact.get("partner", "") if isinstance(iact, dict) else str(iact)
                    s = iact.get("score", 0) if isinstance(iact, dict) else 0
                    if p:
                        ppi_parts.append(f"{p}({s:.2f})" if isinstance(s, float) else f"{p}")
                if ppi_parts:
                    parts.append(f"PPI:{','.join(ppi_parts)}")

            # 7. TF regulators
            regs = info.get("regulators") or []
            if regs:
                reg_parts = []
                for r in regs[:5]:
                    tf = r.get("tf", "") if isinstance(r, dict) else str(r)
                    eff = r.get("effect", "") if isinstance(r, dict) else ""
                    if tf:
                        reg_parts.append(f"{tf}({eff})" if eff else tf)
                if reg_parts:
                    parts.append(f"TF-reg:{','.join(reg_parts)}")

            # 7b. TF targets (this gene IS the TF)
            tf_targets = info.get("tf_targets") or []
            if tf_targets:
                tgt_parts = []
                for t in tf_targets[:5]:
                    tg = t.get("target_gene", "") if isinstance(t, dict) else str(t)
                    eff = t.get("effect", "") if isinstance(t, dict) else ""
                    if tg:
                        tgt_parts.append(f"{tg}({eff})" if eff else tg)
                if tgt_parts:
                    parts.append(f"TF-targets:{','.join(tgt_parts)}")

            # 8. Microbiome
            microbes = info.get("gut_microbes") or []
            if microbes:
                mnames = []
                for m in microbes[:4]:
                    mn = (m.get("microbe") or m.get("gut_microbiota", "")) if isinstance(m, dict) else str(m)
                    alt = m.get("Alteration", "") if isinstance(m, dict) else ""
                    cond = m.get("Condition", "") if isinstance(m, dict) else ""
                    pmid = m.get("PMID", "") if isinstance(m, dict) else ""
                    entry = mn[:30]
                    if alt: entry += f"({alt})"
                    if cond: entry += f"[{cond[:20]}]"
                    if pmid: entry += f"[PMID:{pmid}]"
                    if mn:
                        mnames.append(entry)
                if mnames:
                    parts.append(f"Mic:{';'.join(mnames)}")

            # 9. Metabolites
            mets = info.get("metabolites") or []
            if mets:
                mnames = []
                for m in mets[:5]:
                    mn = (m.get("name") or m.get("metabolite_name", "")) if isinstance(m, dict) else str(m)
                    pt = m.get("protein_type", "") if isinstance(m, dict) else ""
                    if mn:
                        mnames.append(f"{mn[:30]}({pt})" if pt else mn[:30])
                if mnames:
                    parts.append(f"Met:{','.join(mnames)}")

            # 10. GTEx tissue expression
            gtex = info.get("gtex_tissues") or []
            if gtex:
                parts.append(f"GTEx:{','.join(str(t)[:40] for t in gtex[:6])}")

            # 11. HumanBase tissue specificity
            hb = info.get("humanbase_tissues") or []
            if hb:
                parts.append(f"HumanBase:{','.join(str(t)[:35] for t in hb[:5])}")

            # 12. GWAS trait associations
            gwas = info.get("gwas_snps") or []
            if gwas:
                parts.append(f"GWAS:{';'.join(str(s)[:60] for s in gwas[:5])}")

            # 13. BioGRID experimental interactions
            biogrid = info.get("biogrid_interactions") or []
            if biogrid:
                parts.append(f"BioGRID:{';'.join(str(i)[:50] for i in biogrid[:5])}")

            # 14. CIViC cancer variants
            civic = info.get("civic_variants") or []
            if civic:
                parts.append(f"CIViC:{','.join(str(v)[:35] for v in civic[:5])}")

            # 15. Alliance cross-species homologs
            alliance = info.get("alliance_homologs") or []
            if alliance:
                parts.append(f"Alliance:{','.join(str(h)[:35] for h in alliance[:5])}")

            # 16. ClinVar pathogenic variants
            clinvar = info.get("clinvar_variants") or []
            if clinvar:
                parts.append(f"ClinVar:{';'.join(str(v)[:50] for v in clinvar[:5])}")

            # 17. Open Targets disease associations
            ot = info.get("ot_diseases") or []
            if ot:
                parts.append(f"OT:{';'.join(str(d)[:60] for d in ot[:5])}")

            lines.append(f"{gene}: " + " | ".join(parts) if parts else gene)

        # Graph RAG edges — compact, show top edges
        graph_edges = []
        for gene, info in top_genes:
            ppi = info.get("interactions") or []
            for iact in ppi[:2]:
                p = iact.get("partner", "") if isinstance(iact, dict) else str(iact)
                s = iact.get("score", "") if isinstance(iact, dict) else ""
                if p:
                    s_str = f"{s:.2f}" if isinstance(s, float) else str(s)
                    graph_edges.append(f"  {gene} --[PPI:{s_str}]-> {p}")
            regs = info.get("regulators") or []
            for r in regs[:1]:
                tf = r.get("tf", "") if isinstance(r, dict) else str(r)
                eff = r.get("effect", "") if isinstance(r, dict) else ""
                if tf:
                    graph_edges.append(f"  {tf} --[TF:{eff}]-> {gene}")

        if graph_edges:
            lines.append("\n=== TOP INTERACTION EDGES ===")
            lines.extend(graph_edges[:60])

        # PubMed — full citations with abstract
        pubmed = knowledge.get("pubmed", [])
        if pubmed:
            lines.append(f"\n=== PUBMED ({len(pubmed)} articles) ===")
            for art in pubmed[:15]:
                pmid = art.get("pmid", "N/A")
                title = art.get("title", "")[:120]
                journal = art.get("journal", "")[:40]
                date = art.get("pub_date", "") or art.get("year", "")
                authors = art.get("authors", "")
                url = art.get("url", "")
                lines.append(f"  [{pmid}] {title} | {journal} {date} | {authors}")
                if url:
                    lines.append(f"    URL: {url}")

        # EuropePMC — top by citations
        europepmc = knowledge.get("europepmc", [])
        if europepmc:
            top_epmc = sorted(europepmc, key=lambda x: x.get("citations", x.get("citation_count", 0)), reverse=True)[:15]
            lines.append(f"\n=== EUROPEPMC ({len(europepmc)} articles, top cited) ===")
            for art in top_epmc:
                pmid = art.get("pmid", "N/A")
                cited = art.get("citations", art.get("citation_count", 0))
                year = art.get("pub_year", art.get("year", ""))
                title = art.get("title", "")[:120]
                journal = art.get("journal", "")[:40]
                url = art.get("url", "")
                lines.append(f"  [{pmid}] cited={cited} {year} | {title} | {journal}")
                if url:
                    lines.append(f"    URL: {url}")

        return "\n".join(lines)

    def _truncate_to_token_budget(self, text: str, max_chars: int = 40000) -> str:
        """Hard-truncate knowledge text to stay within LLM context window."""
        if len(text) <= max_chars:
            return text
        truncated = text[:max_chars]
        last_nl = truncated.rfind("\n")
        if last_nl > max_chars * 0.8:
            truncated = truncated[:last_nl]
        return truncated + "\n\n[... knowledge truncated to fit context window ...]"

    def _format_similar_cases(self, similar_cases: list) -> str:
        if not similar_cases:
            return ""   # empty — synthesizer prompt section will be omitted
        lines = [f"Found {len(similar_cases)} similar cases:"]
        for i, case in enumerate(similar_cases, 1):
            meta = case.get("metadata", {})
            lines.append(f"  Case {i}: {meta.get('question','Unknown')} | type={meta.get('analysis_type','Unknown')} | sim={1-case.get('distance',1):.3f}")
        return "\n".join(lines)
