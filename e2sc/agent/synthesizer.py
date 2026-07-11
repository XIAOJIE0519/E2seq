"""Synthesizer for source-backed interpretation of uploaded gene values."""

import json
import re as _re
import threading as _threading
from typing import Any, Dict, List

from e2sc.llm import SYNTHESIZER_PROMPT
from e2sc.utils import get_logger

# AbortChat is defined in e2sc.api.server to avoid circular import.
# Import it lazily inside synthesize() so that the synthesizer module
# remains importable in non-server contexts (e.g. tests).
try:
    from e2sc.api.server import AbortChat
except Exception:
    class AbortChat(Exception):
        pass

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
    """Interpret user-supplied gene values with source-backed Agent RAG evidence."""

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
        progress_callback=None,
        abort_flag=None,
    ) -> Dict[str, Any]:
        """Synthesize input gene values and retrieved evidence into plain text.

        Args:
            text_queue: a thread-safe queue (e.g. queue.Queue or asyncio.Queue)
                        that receives streamed text chunks in real-time.
                        Uses put_nowait() so works from any thread.
                        If None, no streaming occurs.
        """
        import time as _time
        _t0 = _time.time()
        logger.info(f"[Synthesizer] Starting synthesis. question={question[:80]!r}, has_knowledge={'genes' in knowledge}, text_queue={text_queue is not None}")

        def _maybe_report(msg: str):
            """Send progress message if a callback is registered."""
            if progress_callback:
                try:
                    progress_callback(msg)
                except Exception:
                    pass

        _maybe_report("[进度] 正在调用大模型生成综合报告...")

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
            _last_progress = _time.time()
            try:
                for chunk in self.llm.stream_chat(messages):
                    # Periodic progress + abort check (LLM may take several minutes)
                    if abort_flag is not None and abort_flag.is_set():
                        logger.info("[Synthesizer] Abort detected during streaming")
                        raise AbortChat("User requested abort during synthesizer streaming")
                    if progress_callback and (_time.time() - _last_progress) >= 10.0:
                        _maybe_report(f"[进度] 大模型综合解读中...已生成 {_chunk_count} 个文本块")
                        _last_progress = _time.time()
                    full_text_parts.append(chunk)
                    _chunk_count += 1
                    # Send chunk to SSE stream
                    try:
                        text_queue.put_nowait(chunk)
                    except Exception as _qe:
                        logger.debug(f"[Synthesizer] text_queue.put_nowait failed: {_qe}")
                response_text = "".join(full_text_parts)
                logger.info(f"[Synthesizer] Streaming done: {_chunk_count} chunks, total_len={len(response_text)}")
            except AbortChat:
                raise
            except Exception as stream_err:
                logger.warning(f"[Synthesizer] Streaming failed, falling back to non-streaming: {stream_err}")
                if abort_flag is not None and abort_flag.is_set():
                    raise AbortChat("User requested abort")
                _maybe_report("[进度] 流式失败，切换非流式重试...")
                # Use the same daemon-thread + abort-poll pattern as the
                # non-streaming path so abort works during the fallback too.
                _result_holder = {}
                _llm_done = _threading.Event()
                def _llm_call():
                    try:
                        _result_holder["text"] = self.llm.chat(messages)
                        _result_holder["error"] = None
                    except Exception as _e:
                        _result_holder["error"] = _e
                    finally:
                        _llm_done.set()
                _llm_thread = _threading.Thread(target=_llm_call, daemon=True)
                _llm_thread.start()
                while not _llm_done.is_set():
                    if abort_flag is not None and abort_flag.is_set():
                        raise AbortChat("User requested abort during fallback")
                    _llm_done.wait(timeout=1.0)
                if _result_holder.get("error"):
                    raise _result_holder["error"]
                response_text = _result_holder.get("text", "")
                logger.info(f"[Synthesizer] Non-streaming fallback response_len={len(response_text)}")
        else:
            # Non-streaming LLM call — run in a daemon thread so we can poll
            # abort_flag every second and abandon the call when the user aborts.
            # We CANNOT interrupt a blocking httpx call in Python, so when abort
            # fires we detach from the LLM thread (it will finish in the
            # background and its result will be discarded). This is the only
            # way to honour abort when the LLM is hung in a long blocking call.
            _maybe_report("[进度] 大模型综合解读中（首次响应可能需要 2-5 分钟）...")
            _result_holder: dict = {}
            _llm_done = _threading.Event()

            def _llm_call():
                try:
                    _result_holder["text"] = self.llm.chat(messages)
                    _result_holder["error"] = None
                except Exception as _e:
                    _result_holder["error"] = _e
                finally:
                    _llm_done.set()

            _llm_thread = _threading.Thread(target=_llm_call, daemon=True)
            _llm_thread.start()

            # Poll abort and progress while LLM is running
            _last_progress = _time.time()
            try:
                while not _llm_done.is_set():
                    # Check abort every 1s — exit immediately on user request
                    if abort_flag is not None and abort_flag.is_set():
                        logger.info("[Synthesizer] Abort detected during non-streaming LLM call — abandoning")
                        _maybe_report("[进度] 已收到中止请求，正在中断...")
                        # Don't wait for the daemon thread; just abandon it.
                        # Daemon thread will die with the interpreter.
                        raise AbortChat("User requested abort during non-streaming LLM call")
                    # Periodic progress (every 10s)
                    if progress_callback and (_time.time() - _last_progress) >= 10.0:
                        _maybe_report(f"[进度] 大模型综合解读中...（已等待 {int(_time.time() - _t0)} 秒）")
                        _last_progress = _time.time()
                    _llm_done.wait(timeout=1.0)
            except AbortChat:
                raise

            if _result_holder.get("error"):
                raise _result_holder["error"]
            response_text = _result_holder.get("text", "")
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
                "input_context": results,
                "knowledge": knowledge,
                "retrieval_status": retrieval_status,
            },
        }
        logger.info(
            f"Interpretation synthesis completed. "
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
        """Build strict interpretation-only instructions for the LLM."""
        import re

        comprehensive = is_comprehensive or bool(re.search(
            r"\b(综合|全面|整体|概括|总结|overview|comprehensive|overall|summary|summarize)\b",
            question.lower(),
        ))
        rules = (
            "You are E2sc, an expert interpreter of user-provided bulk and single-cell "
            "sequencing gene-value results.\n"
            "The input values came from the user's CSV/H5AD/RDS/XLSX file. "
            "Database content was retrieved by Agent RAG.\n\n"
            "MANDATORY RULES:\n"
            "1. Preserve every quoted input gene name, label, sign, and numeric value.\n"
            "2. Explain the input through retrieved annotations and literature only.\n"
            "3. Do NOT perform, simulate, or claim marker detection, DEG testing, "
            "fold-change calculation, p-value calculation, enrichment, clustering, "
            "trajectory inference, dimensionality reduction, network/module/hub analysis, "
            "or any new statistical computation.\n"
            "4. STRING/Reactome/QuickGO/TRRUST and similar records are external annotations, "
            "not results computed from the uploaded file.\n"
            "5. Cite each biological claim with its retrieved source label.\n"
            "6. Do not turn associations into causality. State missing evidence explicitly.\n"
            "7. Return normal Markdown text suitable for direct API/SSE delivery.\n"
        )
        if comprehensive:
            rules += (
                "\nCOMPREHENSIVE INTERPRETATION means cover more of the supplied genes and "
                "retrieved sources. It never authorizes additional analysis or invented values.\n"
            )
        return rules

    def _format_results(self, results: Dict[str, Any], knowledge: Dict[str, Any] = None) -> str:
        """Format only values present in the uploaded sequencing result."""
        sections = [
            "=== USER-PROVIDED SEQUENCING GENE VALUES ===",
            "No marker, DEG, enrichment, clustering, or network analysis was run by E2sc.",
        ]

        if results.get("gene_context"):
            sections.append(results["gene_context"])
            return "\n".join(sections)

        context = results.get("matrix_context")
        if not context:
            return "No input gene-value context available."

        genes = context.get("genes_queried", [])
        if genes:
            sections.append(f"Genes selected for RAG ({len(genes)}): {', '.join(genes[:100])}")

        def append_value_map(title: str, value_map: Dict[str, Any], limit: int) -> None:
            if not value_map:
                return
            sections.append(f"\n=== {title} ===")
            for label, values in value_map.items():
                if isinstance(values, dict):
                    rendered = ", ".join(
                        f"{gene}:{float(value):.4g}"
                        for gene, value in list(values.items())[:limit]
                    )
                else:
                    rendered = ", ".join(str(gene) for gene in list(values)[:limit])
                sections.append(f"  {label}: {rendered}")

        overall = context.get("overall_gene_values", {})
        if overall:
            rendered = ", ".join(
                f"{gene}:{float(value):.4g}"
                for gene, value in list(overall.items())[:100]
            )
            sections.append(f"\nOverall input mean values: {rendered}")

        append_value_map(
            "INPUT MEAN VALUES BY USER-SUPPLIED GROUP",
            context.get("top_genes_per_group", {}),
            50,
        )
        append_value_map(
            "INPUT MEAN VALUES BY USER-SUPPLIED CELL TYPE",
            context.get("top_genes_per_celltype", {}),
            50,
        )
        sections.append(
            "\nThese are direct summaries of the uploaded matrix values. "
            "Use them only as context for RAG interpretation."
        )
        return "\n".join(sections)

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

        # Prioritize evidence-rich records when compacting retrieved context.
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
