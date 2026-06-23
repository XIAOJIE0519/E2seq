"""Synthesizer agent for generating final reports."""

import json
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
        text_queue=None,
    ) -> Dict[str, Any]:
        """Synthesize Graph-RAG knowledge into a Nature/Cell-level response.

        Args:
            text_queue: a thread-safe queue (e.g. queue.Queue or asyncio.Queue)
                        that receives streamed text chunks in real-time.
                        Uses put_nowait() so works from any thread.
                        If None, no streaming occurs.
        """
        import time as _time
        _t0 = _time.time()
        logger.info(f"[Synthesizer] Starting synthesis. question={question[:80]!r}, has_knowledge={'genes' in knowledge}, text_queue={text_queue is not None}")

        # P3: Extract cross-session context injected by orchestrator
        cross_session = knowledge.pop("cross_session_context", {})
        similar_sessions = cross_session.get("similar_sessions", [])
        relevant_patterns = cross_session.get("relevant_patterns", {})
        current_context = cross_session.get("current_context", "")
        # P3: Also support legacy direct injection of similar_cases via knowledge dict
        if not similar_sessions:
            similar_sessions = knowledge.get("similar_cases", [])

        # P2: Use dynamic token budgets based on estimated context
        _t1 = _time.time()
        results_summary = self._format_results(results, knowledge=knowledge)
        results_summary = self._truncate_to_token_budget(results_summary, max_chars=15000)
        knowledge_summary = self._format_knowledge(knowledge)
        knowledge_summary = self._truncate_to_token_budget(knowledge_summary, max_chars=40000)
        # P3: Use enriched similar_cases from cross_session_context
        similar_cases_summary = self._format_similar_cases(similar_sessions, relevant_patterns)
        similar_cases_summary = self._truncate_to_token_budget(similar_cases_summary, max_chars=3000)
        # P3: Format current context summary
        ctx_summary = self._format_current_context(current_context)
        logger.info(f"[Synthesizer] Formatting done in {_time.time()-_t1:.1f}s. results_len={len(results_summary)}, knowledge_len={len(knowledge_summary)}, history_len={len(history) if history else 0}, similar_cases={len(similar_sessions)}")
        has_knowledge = bool(knowledge.get("genes")) or bool(similar_sessions)

        prompt = SYNTHESIZER_PROMPT.format(
            question=question,
            results=results_summary,
            knowledge=knowledge_summary,
            similar_cases=similar_cases_summary,
        )

        # Prepend RAG vector-store context chunks (highest evidence priority)
        rag_context = knowledge.get("rag_context", "")
        if rag_context:
            rag_context = self._truncate_to_token_budget(rag_context, max_chars=6000)
            prompt = (
                "=== RAG Retrieved Knowledge (highest priority — primary evidence source) ===\n"
                + rag_context
                + "\n\n=== Additional Aggregated Knowledge ===\n"
                + prompt
            )

        # P3: Prepend cross-session memory context if available
        if ctx_summary or similar_cases_summary:
            cross_parts = []
            if ctx_summary:
                cross_parts.append(ctx_summary)
            if similar_cases_summary:
                cross_parts.append(similar_cases_summary)
            cross_section = "\n".join(cross_parts)
            prompt = cross_section + "\n\n" + prompt

        system_message = self._build_system_message(question, is_comprehensive, output_mode, knowledge=knowledge)

        messages = [{"role": "system", "content": system_message}]
        if history:
            for h in history[-10:]:
                role = h.get("role", "")
                content = h.get("content", "")
                if role in ("user", "assistant") and content:
                    messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": prompt})

        # Stream text chunks in real-time if a callback queue is provided
        if text_queue is not None:
            full_text_parts = []
            _chunk_count = 0
            try:
                for chunk in self.llm.stream_chat(messages):
                    full_text_parts.append(chunk)
                    _chunk_count += 1
                    # Send chunk to SSE stream
                    try:
                        text_queue.put_nowait(chunk)
                    except Exception as _qe:
                        logger.debug(f"[Synthesizer] text_queue.put_nowait failed: {_qe}")
                response_text = "".join(full_text_parts)
                logger.info(f"[Synthesizer] Streaming done: {_chunk_count} chunks, total_len={len(response_text)}")
            except Exception as stream_err:
                logger.warning(f"[Synthesizer] Streaming failed, falling back to non-streaming: {stream_err}")
                response_text = self.llm.chat(messages)
                logger.info(f"[Synthesizer] Non-streaming fallback response_len={len(response_text)}")
        else:
            response_text = self.llm.chat(messages)
            logger.info(f"[Synthesizer] Non-streaming response_len={len(response_text)}")

        # Strip forbidden "No data" / outlook phrases the LLM may have emitted
        for pat in _NO_DATA_PATTERNS:
            response_text = _re.sub(pat, "", response_text)
        response_text = _re.sub(r"\n{3}", "\n\n", response_text).strip()

        retrieval_status = {
            "genes_retrieved": len(knowledge.get("genes", {})),
            "similar_cases_found": len(similar_sessions),
            "relevant_patterns_found": len(relevant_patterns),
            "has_sufficient_knowledge": has_knowledge,
        }

        logger.info(f"[Synthesizer] Done. total_time={_time.time()-_t0:.1f}s, response_len={len(response_text)}")

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
            f"{retrieval_status['similar_cases_found']} similar cases, "
            f"{retrieval_status['relevant_patterns_found']} patterns"
        )
        return response

    # ------------------------------------------------------------------
    # System message builder
    # ------------------------------------------------------------------
    def _build_system_message(
        self, question: str, is_comprehensive: bool, output_mode: str,
        knowledge: Dict[str, Any] = None
    ) -> str:
        """Build system message driven by question type, NOT by is_comprehensive flag.

        Key principle: knowledge retrieval = multi-database breadth,
        but answer writing = question-specific depth.
        """
        import re
        q_lower = question.lower()

        # Detect question type from the user's actual question
        is_targeted = bool(re.search(
            r'\b(找|哪个|哪些|什么|有无|是否|列出|说出|给我看|identify|which|what|find|list|show|any|给我|找一找)\b',
            q_lower
        ))
        is_module_net = bool(re.search(
            r'\b(模块|模块化|网络|互作|相互作用|ppi|通路|调控|module|network|interaction|pathway|regulat|共调控|协同)\b',
            q_lower
        ))
        # Detect comprehensive/overall analysis request
        is_comprehensive_q = bool(re.search(
            r'\b(综合|全面|整体|概括|总结|overview|comprehensive|overall|summary|summarize|综合分析|整体分析|全面解读)\b',
            q_lower
        ))
        has_cross_gene = bool(
            knowledge and (
                (knowledge.get("cross_gene_analysis") or {}).get("modules") or
                (knowledge.get("cross_gene_analysis") or {}).get("all_edges")
            )
        )

        # Always: answer the user's specific question. Never default to comprehensive.
        base_rules = (
            "You are an expert computational biologist and translational medicine scientist.\n"
            "You have been given a knowledge base built by querying genes against: "
            "UniProt, MyGene, QuickGO, Ensembl, ChEMBL, Open Targets, ClinVar, CIViC, "
            "GWAS Catalog, Reactome, GTEx/HPA, HumanBase, BioGRID, Alliance, "
            "PubMed, EuropePMC (online); STRING, HMDB, TRRUST, GUTMGENE (local).\n\n"
            "RULES:\n"
            "1. ONLY use information explicitly present in the provided knowledge base.\n"
            "   Do NOT fabricate data or cite papers not in PubMed/EuropePMC sections.\n"
            "2. Cite every biological claim inline: "
            "[UniProt], [MyGene], [STRING], [PubMed:PMID], etc.\n"
            "3. If no evidence for a claim: write '[No evidence in retrieved data - omitted]'.\n"
            "4. Use EXACT disease group names, cell type names, and expression values "
            "from the input context.\n"
            "5. Focus on answering the USER'S QUESTION directly. "
            "Do NOT default to a template or fixed section order.\n"
            "6. Never truncate mid-sentence.\n"
            "7. Write at Nature/Cell journal level — precise, mechanistic, evidence-driven.\n"
            "8. Do NOT use generic phrases without citing specific values from the data.\n"
            "9. If the question asks about specific targets, biomarkers, drugs, or pathways — "
            "discuss ONLY those. Do NOT force a network/interaction analysis.\n"
        )

        # Comprehensive analysis: MUST integrate ALL data sources
        if is_comprehensive_q or is_comprehensive:
            comprehensive_rules = (
                "\n*** COMPREHENSIVE ANALYSIS MODE ***\n"
                "This is a COMPREHENSIVE/OVERALL analysis request. You MUST:\n"
                "a) INTEGRATE ALL 20 DATA SOURCES — cite evidence from multiple databases for each claim.\n"
                "b) Discuss EVERY gene that has data, not just the top 3-5.\n"
                "c) Structure by BIOLOGICAL THEME (pathways, disease, drugs, tissue specificity).\n"
                "d) Provide QUANTITATIVE data: fold changes, scores, p-values, expression values.\n"
                "e) End with a DATA COVERAGE SUMMARY showing which databases provided data.\n"
                "f) Write a THOROUGH multi-section report — this is NOT a brief summary.\n"
            )
            return base_rules + comprehensive_rules

        # Focused/direct question (找/哪些/列出): answer specifically
        if is_targeted and not is_module_net:
            return base_rules + (
                "\nThis is a DIRECT/FOCUSED question. Answer specifically:\n"
                "- Identify the specific gene(s), drug(s), pathway(s), or biomarker(s) asked about.\n"
                "- Provide the key evidence for each.\n"
                "- Keep it focused — do NOT expand to unrelated genes or modules.\n"
            )

        # Module/network question AND actual cross-gene data exists: module synthesis
        if (is_module_net or has_cross_gene) and has_cross_gene:
            return base_rules + (
                "\nCROSS-GENE MODULE SYNTHESIS (apply when module/network data is present):\n"
                "a. LEAD with gene interaction modules — identify dense PPI clusters, shared TF regulators, "
                "or co-enriched pathways.\n"
                "b. Characterize each module's collective theme "
                "(e.g., 'inflammatory signaling module', 'DNA repair hub').\n"
                "c. Discuss coordinated regulation — shared TF regulators, "
                "same upstream signal, or pathway cascade.\n"
                "d. Cross-validate: how do expression patterns align with network knowledge? "
                "Genes highly expressed AND well-connected are likely key drivers.\n"
                "e. Weave gene descriptions INTO the module narrative — "
                "do not describe genes one-by-one in isolation.\n"
                "f. If modules share pathway enrichment, explain the collective biological process.\n"
            )

        # Default: straightforward knowledge synthesis, question-driven
        return base_rules

    # ------------------------------------------------------------------
    # Formatting helpers
    # ------------------------------------------------------------------
    def _format_results(self, results: Dict[str, Any], knowledge: Dict[str, Any] = None) -> str:
        sections = []

        # ── CSV / differential expression table mode ──────────────────────
        if results.get("gene_context"):
            sections.append(results["gene_context"])
            return "\n".join(sections)

        # ── Cross-gene network analysis (injected by orchestrator into knowledge dict) ──
        # Can be in results (orchestrator injects via fake_results) or knowledge (direct inject)
        cross_gene = results.get("cross_gene_analysis") or (knowledge or {}).get("cross_gene_analysis")
        if cross_gene:
            sections.append(self._format_cross_gene_section(results, knowledge))

        # ── scRNA-seq / h5ad mode with matrix_context ──────────────────
        if results.get("matrix_context"):
            ctx = results["matrix_context"]
            genes = ctx.get("genes_queried", [])
            ct_focus = ctx.get("cell_type_focus", "all cell types")
            sections.append(f"Cell type focus: {ct_focus}")
            sections.append(f"ALL genes from this analysis ({len(genes)} total): {', '.join(genes[:50])}")
            if len(genes) > 50:
                sections.append(f"... 以及其他 {len(genes) - 50} 个基因")
            grp_map = ctx.get("top_genes_per_group", {})
            if grp_map:
                sections.append("\n=== TOP EXPRESSED GENES PER DISEASE GROUP (gene: mean_expr) ===")
                for grp, gs in grp_map.items():
                    if isinstance(gs, dict):
                        genes_str = ", ".join(f"{g}:{v:.3f}" for g, v in list(gs.items())[:10])
                    else:
                        genes_str = ", ".join(str(g) for g in gs[:10])
                    sections.append(f"  {grp}: {genes_str}")
            diff_map = ctx.get("diff_genes_per_group", {})
            if diff_map:
                sections.append("\n=== DIFFERENTIALLY HIGH GENES PER GROUP VS OTHERS (gene: fold_change) ===")
                for grp, gene_list in diff_map.items():
                    if gene_list:
                        sections.append(f"  {grp}: {', '.join(gene_list[:8])}")
            ct_map = ctx.get("top_genes_per_celltype", {})
            if ct_map:
                sections.append("\n=== TOP EXPRESSED GENES PER CELL TYPE ===")
                for ct, gs in ct_map.items():
                    g_list = list(gs.keys())[:6] if isinstance(gs, dict) else gs[:6]
                    sections.append(f"  {ct}: {', '.join(g_list)}")
            ct_grp_joint = ctx.get("ct_grp_joint", {})
            if ct_grp_joint:
                sections.append("\n=== CELL TYPE x DISEASE GROUP JOINT TOP GENES (gene(expr)) ===")
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

    def _format_cross_gene_section(self, results: Dict[str, Any], knowledge: Dict[str, Any] = None) -> str:
        """Format cross-gene network analysis as the leading section.

        Shows PPI/TF/metabolite/microbiome edges and gene modules first,
        so the LLM organizes the entire response around module-level patterns
        rather than describing genes one-by-one in isolation.
        """
        cross = results.get("cross_gene_analysis") or (knowledge or {}).get("cross_gene_analysis")
        if not cross:
            return ""

        lines = ["\n=== CROSS-GENE NETWORK ANALYSIS (ORGANIZE RESPONSE AROUND THESE MODULES) ===\n"]

        all_edges = cross.get("all_edges", [])
        ppi_lines, tf_lines = [], []
        for e in all_edges:
            etype = e.get("type", "")
            a, b = e.get("a", ""), e.get("b", "")
            if etype == "PPI":
                s = e.get("score", 0)
                ppi_lines.append(f"  {a} --[PPI:{s:.2f}]-- {b}")
            elif etype == "TF":
                m = e.get("mode", "")
                tf_lines.append(f"  {a} --[TF:{m}]--> {b}")
        if ppi_lines:
            lines.append("--- PPI NETWORK (protein-protein interactions) ---")
            lines.extend(ppi_lines[:80])
            lines.append("")
        if tf_lines:
            lines.append("--- TF REGULATION (transcription factor -> target) ---")
            lines.extend(tf_lines[:40])
            lines.append("")

        metabolite_edges = cross.get("metabolite_edges", [])
        if metabolite_edges:
            lines.append("--- METABOLITE BRIDGES (shared metabolites link genes) ---")
            seen_met = {}
            for gene, met in metabolite_edges:
                if met not in seen_met:
                    seen_met[met] = []
                seen_met[met].append(gene)
            for met, genes in seen_met.items():
                if len(genes) > 1:
                    lines.append(f"  {', '.join(genes)} <--[{met}]")
            lines.append("")

        microbiome_edges = cross.get("microbiome_edges", [])
        if microbiome_edges:
            lines.append("--- GUT MICROBIOME AXIS ---")
            for gene, microbe, cond in microbiome_edges[:20]:
                cond_str = f" [{cond}]" if cond else ""
                lines.append(f"  {gene} --[{microbe}{cond_str}]")
            lines.append("")

        modules = cross.get("modules", [])
        if modules:
            lines.append("--- GENE MODULES (connected PPI/TF components) ---")
            for i, mod in enumerate(modules):
                lines.append(f"  Module_{i+1} ({len(mod)} genes): {', '.join(mod)}")
            lines.append("")

        shared_pw = cross.get("shared_pathways", {})
        if shared_pw:
            lines.append("--- SHARED PATHWAYS PER MODULE ---")
            for mod_name, pws in shared_pw.items():
                if pws:
                    pw_str = ", ".join(f"{p}({c})" for p, c in pws[:5])
                    lines.append(f"  {mod_name}: {pw_str}")
            lines.append("")

        hubs = cross.get("ppi_hubs", [])
        if hubs:
            hub_str = ", ".join(f"{g}(degree={d})" for g, d in hubs[:10])
            lines.append(f"--- PPI HUB GENES (highest interaction degree) ---\n  {hub_str}\n")

        return "\n".join(lines)

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

        # Priority: drug targets > disease associations > others (take top 100 for comprehensive analysis)
        def has_priority_data(info: dict) -> bool:
            return bool(info.get("drug_targets") or info.get("ot_diseases"))

        priority_genes = [(g, i) for g, i, _ in scored if has_priority_data(i)]
        remaining = [(g, i) for g, i, _ in scored if not has_priority_data(i)]
        top_genes = (priority_genes + remaining)[:100]

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

    def _format_similar_cases(self, similar_cases: list, relevant_patterns: dict = None) -> str:
        """P3: Enhanced to include full cross-session memory context.
        
        Formats similar past sessions and relevant learned patterns as a readable
        context section. Falls back to original knowledge.similar_cases if provided.
        """
        if not similar_cases:
            return ""
        lines = [f"=== SIMILAR PAST SESSIONS ({len(similar_cases)} found) ===\n"]
        for i, case in enumerate(similar_cases, 1):
            meta = case.get("metadata", {})
            q = meta.get("question", case.get("question", "Unknown"))
            at = meta.get("analysis_type", case.get("analysis_type", "Unknown"))
            sim = 1 - case.get("distance", 1)
            sim_str = f"{sim:.2f}" if isinstance(sim, float) else "?"
            conv = case.get("conv_text", "")[:300]
            lines.append(f"[Case {i}] Q: {q} | Type: {at} | Similarity: {sim_str}")
            if conv:
                lines.append(f"  Context: {conv}")
            if i >= 5:
                lines.append(f"  ... and {len(similar_cases) - 5} more")
                break
        
        # P3: Include relevant learned patterns
        if relevant_patterns:
            lines.append(f"\n=== RELEVANT LEARNED PATTERNS ({len(relevant_patterns)}) ===")
            for name, pat in list(relevant_patterns.items())[:5]:
                pat_str = json.dumps(pat.get("data", {}), ensure_ascii=False)[:200]
                lines.append(f"  [{name}]: {pat_str}")
        
        return "\n".join(lines)

    def _format_current_context(self, current_context: str) -> str:
        """P3: Format the current session context (dataset info, analysis state)."""
        if not current_context:
            return ""
        return f"=== CURRENT SESSION CONTEXT ===\n{current_context}\n"
