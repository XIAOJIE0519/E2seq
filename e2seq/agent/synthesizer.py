"""Synthesizer for source-backed interpretation of uploaded gene values."""

import json
import re as _re
import threading as _threading
from typing import Any, Dict, List

from e2seq.llm import SYNTHESIZER_PROMPT
from e2seq.utils import get_logger

# AbortChat is defined in e2seq.api.server to avoid circular import.
# Import it lazily inside synthesize() so that the synthesizer module
# remains importable in non-server contexts (e.g. tests).
try:
    from e2seq.api.server import AbortChat
except Exception:
    class AbortChat(Exception):
        pass

logger = get_logger(__name__)

# Patterns to strip from LLM output — any "no data" / empty-result language
_NO_DATA_PATTERNS = [
    r'\[Open Targets\] No data for [^.\n]+[.\n]?',
    r'\[ClinVar\] No data for [^.\n]+[.\n]?',
    r'\[GTEx\] No data for [^.\n]+[.\n]?',
    r'\[HPA\] No data for [^.\n]+[.\n]?',
    r'\[cBioPortal\] No data for [^.\n]+[.\n]?',
    r'\[OmniPath\] No data for [^.\n]+[.\n]?',
    r'\[IntAct\] No data for [^.\n]+[.\n]?',
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
    "[HPA] No", "[cBioPortal] No", "[OmniPath] No", "[IntAct] No",
    "[Reactome] No", "[STRING] No", "[TRRUST] No",
    "[GUTMGENE] No", "[HMDB] No", "[QuickGO] No",
    "[UniProt] No", "[MyGene] No", "[Ensembl] No",
    "[ChEMBL] No", "[PubMed] No", "[EuropePMC] No",
]


_RAG_SOURCE_FIELDS = {
    "uniprot": ("uniprot_accession", "function"),
    "mygene": ("gene_name", "gene_aliases", "pathways", "gene_summary"),
    "quickgo": ("go_terms", "go_aspects"),
    "ensembl": ("ensembl_id", "biotype", "chromosome", "description"),
    "chembl": ("drug_targets",),
    "opentargets": ("ot_diseases", "ot_ensembl"),
    "clinvar": ("clinvar_variants",),
    "reactome": ("reactome_pathways",),
    "gtex": ("gtex_tissues",),
    "hpa": ("hpa_tissues",),
    "gwas": ("gwas_snps",),
    "civic": ("civic_variants",),
    "alliance": ("alliance_homologs",),
    "cbioportal": ("cbioportal_gene",),
    "omnipath": ("omnipath_interactions",),
    "intact": ("intact_interactions",),
    "humanbase": ("humanbase_networks", "humanbase_terms"),
    "clinicaltrials": ("clinicaltrials_studies",),
    "custom_gene_annotations": ("custom_gene_annotations_records",),
    "string": ("interactions",),
    "hmdb": ("metabolites",),
    "trrust": ("tf_targets", "regulators"),
    "gutmgene": ("gut_microbes",),
}


def _normalise_source_stats(knowledge: Dict[str, Any]) -> Dict[str, Any]:
    """Repair and standardise source coverage before it reaches the answer.

    Bulk RAG workers query one gene at a time and older persisted snapshots
    therefore contain child totals such as ``total_genes=1``.  Coverage is a
    cohort statistic, so derive the denominator from the actual merged gene
    records and recompute hit counts/pct from the stored hit-gene sets.
    """
    stats = knowledge.setdefault("_source_stats", {})
    genes = knowledge.get("genes", {}) or {}
    requested_total = int(knowledge.get("_rag_queried_gene_count") or 0)
    gene_total = len(genes)
    total = max(requested_total, gene_total)
    if total <= 0:
        total = int(stats.get("total_genes_queried") or 0)
    if total > 0:
        stats["total_genes_queried"] = total
    def _as_nonnegative_int(value: Any) -> int:
        try:
            return max(0, int(value or 0))
        except (TypeError, ValueError):
            return 0

    def _has_record(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, (list, tuple, set, dict)):
            return bool(value)
        try:
            return bool(value.size) if hasattr(value, "size") else True
        except Exception:
            return True

    def _infer_hit_genes(source: str) -> list[str]:
        fields = _RAG_SOURCE_FIELDS.get(source, ())
        if not fields:
            return []
        inferred = []
        for gene, record in genes.items():
            if isinstance(record, dict) and any(
                _has_record(record.get(field)) for field in fields
            ):
                name = str(gene).strip()
                if name:
                    inferred.append(name)
        return sorted(set(inferred))

    for category in ("apis", "dbs"):
        for source, info in (stats.get(category, {}) or {}).items():
            if not isinstance(info, dict):
                continue
            raw_hit_genes = info.get("hit_genes")
            preserved_hit_count = _as_nonnegative_int(info.get("hit_count"))
            hit_genes = sorted({str(gene).strip() for gene in (raw_hit_genes or []) if str(gene).strip()})
            # A few older/merged snapshots retained ``hit_count`` but lost the
            # per-gene set during JSON serialization.  Rebuild that set from
            # the actual merged records when possible.  If the records were
            # intentionally compacted, preserve the measured count instead of
            # turning a real hit into 0 and then labelling it an API error.
            if not hit_genes:
                inferred = _infer_hit_genes(str(source))
                if inferred:
                    hit_genes = inferred
            measured_hit_count = max(len(hit_genes), preserved_hit_count)
            info["hit_genes"] = hit_genes
            info["hit_count"] = min(measured_hit_count, total) if total else measured_hit_count
            info["total_genes"] = total
            info["pct"] = round(info["hit_count"] / total * 100) if total else 0
    stats["pubmed_articles"] = len(knowledge.get("pubmed", []) or [])
    stats["europepmc_articles"] = len(knowledge.get("europepmc", []) or [])
    stats["stats_version"] = max(2, int(stats.get("stats_version") or 0))
    return stats


def _answer_language(question: str) -> str:
    """Infer the response language from the user's current question."""
    text = str(question or "")
    cjk = len(_re.findall(r"[\u3400-\u9fff]", text))
    latin = len(_re.findall(r"[A-Za-z]", text))
    return "en" if latin > cjk else "zh"


def _format_rag_source_audit(knowledge: Dict[str, Any], question: str = "") -> str:
    """Create a compact, user-facing coverage line for the concrete sources.

    The detailed source records stay in the structured response payload.  The
    answer itself only needs the source names and returned/target counts; a
    long audit block made otherwise useful scientific interpretations look like
    an internal debug dump.
    """
    stats = _normalise_source_stats(knowledge)
    language = _answer_language(question)
    english = language == "en"
    api_stats = stats.get("apis", {}) or {}
    db_stats = stats.get("dbs", {}) or {}
    enabled_apis = list(stats.get("enabled_apis") or api_stats.keys())
    enabled_dbs = list(stats.get("enabled_dbs") or db_stats.keys())
    rag_queried_genes = int(
        knowledge.get("_rag_queried_gene_count")
        or knowledge.get("_rag_core_gene_count")
        or len(knowledge.get("genes", {}))
    )
    selected_genes = int(knowledge.get("_selected_gene_count") or rag_queried_genes)
    pubmed_n = int(stats.get("pubmed_articles") or len(knowledge.get("pubmed", [])))
    europepmc_n = int(stats.get("europepmc_articles") or len(knowledge.get("europepmc", [])))

    def _gene_coverage(source: str, category: str) -> str:
        info = (api_stats if category == "apis" else db_stats).get(source, {}) or {}
        hit = int(info.get("hit_count") or len(info.get("hit_genes", [])))
        total = int(
            info.get("total_genes")
            or stats.get("total_genes_queried")
            or rag_queried_genes
        )
        states = info.get("status_counts", {}) or {}
        has_transport_error = bool(states.get("error") or states.get("unavailable"))
        if hit > 0:
            if has_transport_error:
                state = "partially returned; some queries failed" if english else "已返回记录；部分查询失败"
            else:
                state = "records returned" if english else "已返回记录"
        elif states.get("needs_configuration"):
            state = "needs configuration" if english else "需要配置"
        elif has_transport_error:
            state = (
                "interface error/unavailable; zero does not mean no biological record"
                if english else "接口错误/不可用；0 不代表生物学无记录"
            )
        elif states:
            state = "reachable but no records for this batch" if english else "接口可达但本批无记录"
        else:
            state = "query not completed" if english else "未完成查询"
        if english:
            return f"{source} {hit}/{total} selected items ({state})"
        return f"{source} {hit}/{total} 个表达项目（{state}）"

    literature_queries = stats.get("literature_queries", {}) or {}
    initial_literature_queries = stats.get("initial_literature_queries", {}) or {}
    literature_errors = stats.get("literature_errors", {}) or {}

    def _literature_coverage(source: str, count: int) -> str:
        queries = int(literature_queries.get(source, 0) or 0)
        initial = int(initial_literature_queries.get(source, 0) or 0)
        info = api_stats.get(source, {}) or {}
        states = info.get("status_counts", {}) or {}
        has_transport_error = bool(
            states.get("error") or states.get("unavailable") or literature_errors.get(source)
        )
        # A literature source can return useful articles while one of several
        # parallel queries fails.  Never label that non-zero result as an
        # unavailable interface; make the partial nature explicit instead.
        if count > 0:
            status = "; some queries failed" if english and has_transport_error else (
                "；部分查询失败" if has_transport_error else ""
            )
        else:
            status = (
                "; interface error/unavailable; zero does not mean no biological record"
                if english and has_transport_error
                else ("；接口错误/不可用；0 不代表生物学无记录" if has_transport_error else "")
            )
        if initial:
            if english:
                return f"{source} {count} articles / initial full-cohort RAG {initial} queries + {queries} current-round queries{status}"
            return f"{source} {count} 篇 / 初始全量 RAG {initial} 次 + 本轮 {queries} 次查询{status}"
        if english:
            return f"{source} {count} articles / {queries} current-round queries{status}"
        return f"{source} {count} 篇 / 本轮 {queries} 次查询{status}"

    api_returns = []
    for source in enabled_apis:
        if source == "pubmed":
            api_returns.append(_literature_coverage(source, pubmed_n))
        elif source == "europepmc":
            api_returns.append(_literature_coverage(source, europepmc_n))
        else:
            api_returns.append(_gene_coverage(source, "apis"))
    db_returns = [_gene_coverage(source, "dbs") for source in enabled_dbs]

    if english:
        lines = [
            "Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)",
        ]
        lines.append("Online APIs: " + ("; ".join(api_returns) if api_returns else "none"))
        lines.append("Local databases: " + ("; ".join(db_returns) if db_returns else "none"))
    else:
        lines = [
            "本次来源与覆盖率（基因来源=有记录的选定表达项目/选定 RAG 项目；文献来源=文章数/查询次数）",
        ]
        lines.append("在线 API：" + ("；".join(api_returns) if api_returns else "无"))
        lines.append("本地数据库：" + ("；".join(db_returns) if db_returns else "无"))
    return "\n".join(lines)


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
        selected_count = int(knowledge.get("_selected_gene_count") or 0)
        rag_gene_count = len(knowledge.get("genes", {}) or {})
        large_cohort = selected_count > 30 or rag_gene_count > 30
        # A persisted bulk/RAG snapshot already contains source-aware records
        # and a deterministic literature fallback. Avoid two additional
        # remote triage calls before the actual answer, which is important for
        # OpenAI-compatible gateways with strict request timeouts.
        if large_cohort:
            knowledge.setdefault("_source_stats", {})["skip_llm_literature_selection"] = True
            _maybe_report("大规模表达项目使用检索排序选择核心文献，跳过额外的模型文献筛选")
        elif not (knowledge.get("_source_stats", {}) or {}).get("skip_llm_literature_selection"):
            knowledge = self._select_final_literature(
                question,
                results_summary,
                knowledge,
                progress_callback=progress_callback,
                abort_flag=abort_flag,
            )
        else:
            _maybe_report("Using persisted source-aware literature ranking")
        source_audit = _format_rag_source_audit(knowledge, question=question)
        knowledge_summary = self._format_knowledge(knowledge, question=question)
        knowledge_summary = source_audit + "\n\n" + knowledge_summary
        knowledge_summary = self._truncate_to_token_budget(knowledge_summary, max_chars=40000)
        # P3: Use enriched similar_cases from cross_session_context
        similar_cases_summary = self._format_similar_cases(similar_sessions, relevant_patterns)
        similar_cases_summary = self._truncate_to_token_budget(similar_cases_summary, max_chars=3000)
        # P3: Format current context summary
        ctx_summary = self._format_current_context(current_context)
        logger.info(f"[Synthesizer] Formatting done in {_time.time()-_t1:.1f}s. results_len={len(results_summary)}, knowledge_len={len(knowledge_summary)}, history_len={len(history) if history else 0}, similar_cases={len(similar_sessions)}")
        has_knowledge = bool(knowledge.get("genes")) or bool(
            knowledge.get("rag_context")
            or knowledge.get("pubmed")
            or knowledge.get("europepmc")
            or (knowledge.get("_source_stats") or {}).get("question_time_enrichment")
        ) or bool(similar_sessions)

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

        # Large cohorts are intentionally summarized to modules and
        # representative items.  Keep the completion budget bounded as well;
        # an OpenAI-compatible gateway may otherwise spend several minutes on
        # a needlessly large response and return a proxy-level 502.
        synthesis_kwargs = {"max_tokens": 12000} if large_cohort else {}

        def _is_gateway_error(error: Exception) -> bool:
            text = str(error).lower()
            return any(marker in text for marker in (
                "502", "bad gateway", "503", "service unavailable",
                "upstream_unavailable", "504", "gateway timeout", "upstream",
                "connecterror", "connection error", "connection reset",
                "broken pipe", "remoteprotocol", "readtimeout", "read timeout",
                "network is unreachable", "temporarily unavailable", "eof",
            ))

        def _deterministic_fallback(error: Exception) -> str:
            """Return an evidence-preserving report when the answer model is down."""
            selected = int(knowledge.get("_selected_gene_count") or rag_gene_count)
            queried = int(
                knowledge.get("_rag_queried_gene_count")
                or knowledge.get("_rag_core_gene_count")
                or rag_gene_count
            )
            error_hint = " ".join(str(error).split())[:240]
            provider = str(getattr(self.llm, "provider", "") or "").strip()
            if not provider:
                provider = {
                    "DeepSeekProvider": "deepseek",
                    "OpenAIProvider": "openai-compatible",
                    "AnthropicProvider": "anthropic",
                    "GeminiProvider": "gemini",
                    "SiliconFlowProvider": "siliconflow",
                    "OllamaProvider": "ollama",
                    "GLMProvider": "glm",
                    "KimiProvider": "kimi",
                    "SDUProvider": "sdu",
                    "CustomProvider": "custom/openai-compatible",
                }.get(type(self.llm).__name__, type(self.llm).__name__ or "unknown")
            model = str(getattr(self.llm, "model", "unknown") or "unknown")
            if _answer_language(question) == "en":
                _maybe_report("[progress] Answer synthesis is unavailable; returning the completed deterministic evidence report")
                return (
                    "## Answer generation status\n"
                    f"Question: {question}\n"
                    f"Answer model API: {provider} / {model}. The model synthesis request was unavailable, "
                    "so this response contains completed statistics and source-backed Agent RAG evidence only. "
                    "It does not force interactions, targets, modules, or pathways into the answer.\n\n"
                    f"- Selected expression items: {selected}; Agent RAG queried: {queried}\n"
                    f"- PubMed: {len(knowledge.get('pubmed', []) or [])} articles; "
                    f"Europe PMC: {len(knowledge.get('europepmc', []) or [])} articles\n\n"
                    "### Completed statistical and data evidence\n"
                    f"{results_summary[:5000]}\n\n"
                    "### Agent RAG evidence and source coverage\n"
                    f"{knowledge_summary[:8000]}\n\n"
                    f"Gateway error summary: {error_hint}"
                )
            _maybe_report("[进度] 精简合成仍不可用，已切换为本地确定性报告")
            return (
                "## 回答生成状态\n"
                f"当前问题：{question}\n"
                f"回答模型 API：{provider} / {model}。本次大模型合成暂时不可用，"
                "因此返回已完成的统计结果与基于来源的 Agent RAG 证据；没有把互作、靶点、模块或通路强行设为回答主题。\n\n"
                f"- 当前数据集合：{selected} 个表达项目；Agent RAG 实际检索：{queried} 个\n"
                f"- PubMed：{len(knowledge.get('pubmed', []) or [])} 篇；"
                f"Europe PMC：{len(knowledge.get('europepmc', []) or [])} 篇\n\n"
                "### 已完成的统计与数据证据\n"
                f"{results_summary[:5000]}\n\n"
                "### Agent RAG 证据与来源覆盖\n"
                f"{knowledge_summary[:8000]}\n\n"
                f"网关错误摘要：{error_hint}"
            )
            _maybe_report("[进度] 精简合成仍不可用，已切换为本地确定性报告")
            return (
                "## 回答生成状态\n"
                f"当前问题：{question}\n"
                f"回答模型 API：{provider} / {model}。该次大模型合成暂时不可用，"
                "所以这里返回已完成的统计结果与问题中立的 RAG 证据摘要；没有把互作、靶点、模块或通路强行设为回答主题。\n\n"
                f"- 当前数据集合：{selected} 个表达项目；RAG 实际检索 {queried} 个\n"
                f"- PubMed：{len(knowledge.get('pubmed', []) or [])} 篇；"
                f"Europe PMC：{len(knowledge.get('europepmc', []) or [])} 篇\n\n"
                "### 已完成的统计与数据证据\n"
                f"{results_summary[:5000]}\n\n"
                "### RAG 证据摘要与来源审计\n"
                f"{knowledge_summary[:8000]}\n\n"
                "以上摘要是可复用的证据材料，不是固定回答结构；恢复模型网关后，下一次回答会再次按用户问题选择相关证据。\n\n"
                f"网关错误摘要：{error_hint}"
            )
            _maybe_report("[进度] 精简合成仍不可用，已切换为本地确定性报告")
            return (
                "## 综合解读（本地确定性兜底）\n"
                "统计建模、首问 GO/KEGG/GSEA/STRING 批量结果以及选定表达项目的 RAG 检索已经完成。"
                "本次回答模型网关暂时不可用，因此以下内容只使用已完成的结构化结果和来源审计，"
                "不新增统计推断，也不列出完整基因清单。\n\n"
                f"- 当前数据集合：{selected} 个表达项目；RAG 实际检索 {queried} 个\n"
                f"- 已返回的 PubMed 文献：{len(knowledge.get('pubmed', []) or [])}；"
                f"Europe PMC 文献：{len(knowledge.get('europepmc', []) or [])}\n"
                "- 结果解释：优先依据统计效应方向、显著性筛选、富集/网络模块的重复出现，"
                "再结合多来源注释判断候选互作与靶点；这不是因果证明。\n\n"
                "### 已完成的统计与数据证据\n"
                f"{results_summary[:5000]}\n\n"
                "### RAG 核心摘要与来源审计\n"
                f"{knowledge_summary[:8000]}\n\n"
                "### 网关状态\n"
                "a6api 上游综合生成请求返回暂时性服务错误；请稍后重试，或切换到可用的固定模型。"
                f"记录摘要：{error_hint}"
            )

        def _compact_messages() -> list[dict[str, str]]:
            compact_system = system_message + (
                "\nRETRY MODE: The upstream gateway rejected the first large-cohort request. "
                "Answer in a compact cohort-level report (no more than 1,800 Chinese characters), "
                "using only the deterministic evidence digest, source audit, representative items, and "
                "selected literature below. Do not enumerate the full cohort."
            )
            compact_prompt = (
                f"=== USER QUESTION ===\n{question[:2000]}\n\n"
                "=== UPLOADED-DATA SUMMARY ===\n"
                f"{results_summary[:6000]}\n\n"
                "=== COMPACT SOURCE-BACKED COHORT RAG ===\n"
                f"{self._truncate_to_token_budget(knowledge_summary, 18000)}"
            )
            return [
                {"role": "system", "content": compact_system},
                {"role": "user", "content": compact_prompt},
            ]

        def _chat_with_rescue() -> str:
            try:
                return self.llm.chat(messages, **synthesis_kwargs)
            except Exception as error:
                if not large_cohort or not _is_gateway_error(error):
                    raise
                _maybe_report("[进度] 上游模型网关暂时不可用，正在切换精简合成请求")
                try:
                    return self.llm.chat(_compact_messages(), max_tokens=6000)
                except Exception as compact_error:
                    if not _is_gateway_error(compact_error):
                        raise
                    return _deterministic_fallback(compact_error)

        # Stream text chunks in real-time if a callback queue is provided
        if text_queue is not None:
            full_text_parts = []
            _chunk_count = 0
            _last_progress = _time.time()
            try:
                for chunk in self.llm.stream_chat(messages, **synthesis_kwargs):
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
                        _result_holder["text"] = _chat_with_rescue()
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
                    _result_holder["text"] = _chat_with_rescue()
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

        # An OpenAI-compatible gateway may return an empty content field even
        # after a nominally successful HTTP response.  A RAG snapshot must
        # never disappear in that case: return the same deterministic,
        # source-audited cohort digest used by the gateway rescue path.
        if not str(response_text or "").strip():
            response_text = _deterministic_fallback(RuntimeError("empty LLM response"))

        # Strip forbidden "No data" / outlook phrases the LLM may have emitted
        for pat in _NO_DATA_PATTERNS:
            response_text = _re.sub(pat, "", response_text)
        response_text = _re.sub(r"\n{3}", "\n\n", response_text).strip()
        _answer_provider = str(getattr(self.llm, "provider", "") or "").strip()
        if not _answer_provider:
            _answer_provider = {
                "DeepSeekProvider": "deepseek",
                "OpenAIProvider": "openai-compatible",
                "AnthropicProvider": "anthropic",
                "GeminiProvider": "gemini",
                "SiliconFlowProvider": "siliconflow",
                "OllamaProvider": "ollama",
                "GLMProvider": "glm",
                "KimiProvider": "kimi",
                "SDUProvider": "sdu",
                "CustomProvider": "custom/openai-compatible",
            }.get(type(self.llm).__name__, type(self.llm).__name__ or "unknown")
        if "回答模型 API：" not in response_text and "Answer model API:" not in response_text:
            if _answer_language(question) == "en":
                response_text = (
                    response_text.rstrip()
                    + f"\n\nAnswer model API: {_answer_provider} / {getattr(self.llm, 'model', 'unknown')}."
                )
            else:
                response_text = (
                    response_text.rstrip()
                    + f"\n\n回答模型 API：{_answer_provider} / {getattr(self.llm, 'model', 'unknown')}."
                )
        if source_audit and not any(
            marker in response_text
            for marker in ("本次来源与覆盖率", "Source coverage", "API coverage", "RAG SOURCE AUDIT")
        ):
            # Keep the scientific interpretation first.  The source line is a
            # compact provenance footer, not the main body of the answer.
            response_text = response_text.rstrip() + "\n\n" + source_audit

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
                "source_audit": source_audit,
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
    @staticmethod
    def _literature_terms(value: Any) -> set:
        """Extract stable scientific terms for deterministic literature recall."""
        stopwords = {
            "about", "after", "against", "among", "also", "and", "are", "based",
            "been", "being", "between", "both", "could", "from", "have", "into",
            "more", "most", "other", "over", "such", "than", "that", "their",
            "these", "this", "those", "through", "using", "what", "when", "where",
            "which", "with", "within", "would",
            "\u7684", "\u4e86", "\u548c", "\u4e0e", "\u5728", "\u5bf9",
            "\u53ca", "\u6216", "\u662f", "\u6709", "\u4e2d", "\u5982\u4f55",
            "\u54ea\u4e9b", "\u4ec0\u4e48",
        }
        tokens = _re.findall(
            r"[a-z][a-z0-9_-]{1,}|[\u4e00-\u9fff]{2,}",
            str(value or "").lower(),
            flags=_re.IGNORECASE,
        )
        return {token for token in tokens if token not in stopwords}

    def _rank_literature_records(
        self,
        items: list,
        question: str = "",
        evidence_text: str = "",
        limit: int = 8,
    ) -> list:
        """Deterministic recall fallback using question/RAG overlap, never citations."""
        if not items:
            return []
        question_terms = self._literature_terms(question)
        evidence_terms = self._literature_terms(evidence_text)
        ranked = []
        for index, article in enumerate(items):
            title = article.get("title", "")
            abstract = article.get("abstract", "") or article.get("abstractText", "")
            query_layer = article.get("query", "") or article.get("query_layer", "")
            body = " ".join((title, abstract, query_layer))
            title_terms = self._literature_terms(title)
            body_terms = self._literature_terms(body)
            score = (
                len(question_terms & title_terms) * 8
                + len(question_terms & body_terms) * 3
                + len(evidence_terms & title_terms) * 5
                + len(evidence_terms & body_terms)
            )
            ranked.append((score, -index, article))
        ranked.sort(key=lambda row: (row[0], row[1]), reverse=True)
        return [row[2] for row in ranked[:limit]]

    def _select_final_literature(
        self,
        question: str,
        results_summary: str,
        knowledge: Dict[str, Any],
        progress_callback=None,
        abort_flag=None,
    ) -> Dict[str, Any]:
        """Use the LLM to select literature against the question and current RAG evidence."""
        pubmed_all = list(knowledge.get("pubmed", []) or [])
        europepmc_all = list(knowledge.get("europepmc", []) or [])
        if not pubmed_all and not europepmc_all:
            return knowledge

        rag_context = str(knowledge.get("rag_context", "") or "")
        gene_evidence = []
        for gene, info in list((knowledge.get("genes", {}) or {}).items())[:80]:
            if not isinstance(info, dict):
                continue
            fragments = []
            for field in (
                "function", "gene_summary", "pathways", "reactome_pathways",
                "go_terms", "ot_diseases", "drug_targets", "regulators",
            ):
                value = info.get(field)
                if value:
                    fragments.append(f"{field}={str(value)[:240]}")
            if fragments:
                gene_evidence.append(f"{gene}: " + " | ".join(fragments))
        evidence_text = (
            results_summary[:8000]
            + "\n=== CURRENT GENE-LEVEL RAG RECORDS ===\n"
            + "\n".join(gene_evidence)[:10000]
            + "\n=== CURRENT VECTOR RAG CONTEXT ===\n"
            + rag_context[:10000]
        ).strip()
        pubmed_candidates = self._rank_literature_records(
            pubmed_all, question=question, evidence_text=evidence_text, limit=48
        )
        europepmc_candidates = self._rank_literature_records(
            europepmc_all, question=question, evidence_text=evidence_text, limit=48
        )

        def _candidate_lines(source: str, records: list, include_abstract: bool = False) -> str:
            lines = [f"=== {source} candidates (1-based index) ==="]
            for index, article in enumerate(records, 1):
                identifier = article.get("pmid", "") or article.get("id", "") or "N/A"
                title = str(article.get("title", "") or "")[:320]
                abstract = str(
                    article.get("abstract", "") or article.get("abstractText", "")
                    or article.get("summary", "") or ""
                )[:700]
                query = str(article.get("query", "") or article.get("query_layer", ""))[:180]
                year = article.get("pub_year", "") or article.get("year", "") or article.get("pub_date", "")
                line = f"[{index}] id={identifier} year={year} title={title} query={query}"
                if include_abstract:
                    line += f" abstract={abstract}"
                lines.append(line)
            return "\n".join(lines)

        title_prompt = (
            "You are a biomedical literature triage specialist. This is pass 1 of 2. "
            "Using ONLY title and metadata, shortlist papers that could directly help "
            "answer the user's question using the uploaded data and CURRENT RAG evidence. "
            "Consider phenotype, cell type/context, mechanisms, interventions, and "
            "evidence gaps. A gene-name match alone is insufficient. Do not use citation "
            "counts, popularity, or publication age. Do not infer findings that are not "
            "visible in the title/metadata.\n\n"
            "Return STRICT JSON only, with 1-based candidate indices:\n"
            '{{"pubmed": [1, 2], "europepmc": [3, 4]}}\n'
            "Shortlist at most 16 from each source for pass 2. Do not invent indices "
            "or papers.\n\n"
            "=== USER QUESTION ===\n{question}\n\n"
            "=== UPLOADED-DATA SUMMARY ===\n{results}\n\n"
            "=== CURRENT RAG EVIDENCE ===\n{evidence}\n\n"
            "{pubmed}\n\n{europepmc}"
        ).format(
            question=question[:4000],
            results=results_summary[:8000],
            evidence=evidence_text[:12000],
            pubmed=_candidate_lines("PubMed", pubmed_candidates),
            europepmc=_candidate_lines("Europe PMC", europepmc_candidates),
        )

        def _fallback() -> Dict[str, list]:
            return {
                "pubmed": self._rank_literature_records(
                    pubmed_all, question=question, evidence_text=evidence_text, limit=8
                ),
                "europepmc": self._rank_literature_records(
                    europepmc_all, question=question, evidence_text=evidence_text, limit=8
                ),
            }

        def _parse_json(raw: Any) -> dict:
            if isinstance(raw, dict):
                return raw
            match = _re.search(r"\{[\s\S]*\}", str(raw or ""))
            if not match:
                return {}
            try:
                parsed = json.loads(match.group())
                return parsed if isinstance(parsed, dict) else {}
            except (TypeError, ValueError, json.JSONDecodeError):
                return {}

        def _resolve(parsed: dict, source: str, candidates: list, limit: int) -> list:
            values = parsed.get(source, []) if isinstance(parsed, dict) else []
            if isinstance(values, dict):
                values = values.get("indices", values.get("selected", []))
            if not isinstance(values, list):
                return []
            resolved = []
            seen = set()
            for value in values:
                try:
                    index = int(value.get("index") if isinstance(value, dict) else value)
                except (TypeError, ValueError):
                    continue
                if not 1 <= index <= len(candidates):
                    continue
                article = candidates[index - 1]
                key = str(
                    article.get("pmid", "")
                    or article.get("id", "")
                    or article.get("title", "")
                    or f"index:{index}"
                ).strip().lower()
                if key in seen:
                    continue
                seen.add(key)
                resolved.append(article)
                if len(resolved) >= limit:
                    break
            return resolved

        def _fetch_abstracts(source: str, records: list) -> list:
            """Enrich only the pass-1 shortlist; raw knowledge remains unchanged."""
            enriched = [dict(record) for record in records]
            missing = [
                record for record in enriched
                if not (record.get("abstract") or record.get("abstractText") or record.get("summary"))
            ]
            identifiers = [
                str(record.get("pmid", "") or record.get("id", "")).strip()
                for record in missing
            ]
            identifiers = [identifier for identifier in identifiers if identifier]
            if not identifiers:
                return enriched
            try:
                import requests as _abstract_requests
                abstract_by_id = {}
                if source == "pubmed":
                    import xml.etree.ElementTree as _et
                    response = _abstract_requests.get(
                        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
                        params={
                            "db": "pubmed",
                            "id": ",".join(identifiers),
                            "rettype": "abstract",
                            "retmode": "xml",
                        },
                        timeout=12,
                    )
                    if response.ok:
                        root = _et.fromstring(response.content)
                        for article in root.findall(".//PubmedArticle"):
                            pmid_node = article.find(".//PMID")
                            pmid = pmid_node.text.strip() if pmid_node is not None and pmid_node.text else ""
                            abstract_nodes = article.findall(".//AbstractText")
                            abstract = " ".join(
                                "".join(node.itertext()).strip()
                                for node in abstract_nodes
                                if "".join(node.itertext()).strip()
                            )
                            if pmid and abstract:
                                abstract_by_id[pmid] = abstract
                else:
                    query = " OR ".join(f"EXT_ID:{identifier}" for identifier in identifiers)
                    response = _abstract_requests.get(
                        "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                        params={
                            "query": query,
                            "resultType": "core",
                            "pageSize": len(identifiers),
                            "format": "json",
                        },
                        timeout=12,
                    )
                    if response.ok:
                        records_json = response.json().get("resultList", {}).get("result", [])
                        for record in records_json:
                            identifier = str(record.get("pmid", "") or record.get("id", "")).strip()
                            abstract = str(record.get("abstractText", "") or "").strip()
                            if identifier and abstract:
                                abstract_by_id[identifier] = abstract

                for record in enriched:
                    identifier = str(record.get("pmid", "") or record.get("id", "")).strip()
                    abstract = abstract_by_id.get(identifier, "")
                    if abstract:
                        record["abstract"] = abstract
            except Exception as error:
                logger.warning(f"[Synthesizer] Abstract enrichment failed for {source}: {error}")
            return enriched

        selected = None
        if self.llm is not None:
            try:
                if abort_flag is not None and abort_flag.is_set():
                    raise AbortChat("User requested abort before literature title triage")
                if progress_callback:
                    progress_callback("Literature pass 1/2: title triage")
                title_raw = self.llm.chat(
                    [{"role": "user", "content": title_prompt}],
                    max_tokens=1000,
                )
                title_parsed = _parse_json(title_raw)
                shortlist = {
                    "pubmed": _resolve(title_parsed, "pubmed", pubmed_candidates, limit=16),
                    "europepmc": _resolve(title_parsed, "europepmc", europepmc_candidates, limit=16),
                }
                if not shortlist["pubmed"] and pubmed_all:
                    shortlist["pubmed"] = self._rank_literature_records(
                        pubmed_all, question=question, evidence_text=evidence_text, limit=16
                    )
                if not shortlist["europepmc"] and europepmc_all:
                    shortlist["europepmc"] = self._rank_literature_records(
                        europepmc_all, question=question, evidence_text=evidence_text, limit=16
                    )

                if abort_flag is not None and abort_flag.is_set():
                    raise AbortChat("User requested abort before literature abstract triage")
                shortlist["pubmed"] = _fetch_abstracts("PubMed", shortlist["pubmed"])
                shortlist["europepmc"] = _fetch_abstracts("EuropePMC", shortlist["europepmc"])
                abstract_prompt = (
                    "You are a biomedical literature triage specialist. This is pass 2 of 2. "
                    "Now use the abstracts of the title-shortlisted papers to choose the "
                    "papers most directly useful for answering the question with the current "
                    "RAG evidence. Evaluate direct biological relevance, study context, "
                    "mechanism/intervention fit, and evidence quality. Do not use citation "
                    "counts, popularity, or publication age. Return STRICT JSON only:\n"
                    '{{"pubmed": [1, 2], "europepmc": [3, 4]}}\n'
                    "Choose at most 8 from each source, and do not invent indices.\n\n"
                    "=== USER QUESTION ===\n{question}\n\n"
                    "=== CURRENT RAG EVIDENCE ===\n{evidence}\n\n"
                    "{pubmed}\n\n{europepmc}"
                ).format(
                    question=question[:4000],
                    evidence=evidence_text[:12000],
                    pubmed=_candidate_lines("PubMed", shortlist["pubmed"], include_abstract=True),
                    europepmc=_candidate_lines("Europe PMC", shortlist["europepmc"], include_abstract=True),
                )
                if progress_callback:
                    progress_callback("Literature pass 2/2: abstract triage")
                abstract_raw = self.llm.chat(
                    [{"role": "user", "content": abstract_prompt}],
                    max_tokens=1000,
                )
                abstract_parsed = _parse_json(abstract_raw)
                selected = {
                    "pubmed": _resolve(abstract_parsed, "pubmed", shortlist["pubmed"], limit=8),
                    "europepmc": _resolve(abstract_parsed, "europepmc", shortlist["europepmc"], limit=8),
                }
                if not selected["pubmed"] and shortlist["pubmed"]:
                    selected["pubmed"] = shortlist["pubmed"][:8]
                if not selected["europepmc"] and shortlist["europepmc"]:
                    selected["europepmc"] = shortlist["europepmc"][:8]
                logger.info(
                    f"[Synthesizer] Two-pass literature selection: "
                    f"PubMed={len(selected['pubmed'])}, "
                    f"EuropePMC={len(selected['europepmc'])}"
                )
            except AbortChat:
                raise
            except Exception as error:
                logger.warning(f"[Synthesizer] Two-pass literature selection failed: {error}")

        if selected is None:
            selected = _fallback()

        if abort_flag is not None and abort_flag.is_set():
            raise AbortChat("User requested abort after literature selection")
        enriched = dict(knowledge)
        enriched["_final_literature"] = selected
        return enriched

    def _build_system_message(
        self, question: str, is_comprehensive: bool, output_mode: str,
        knowledge: Dict[str, Any] = None
    ) -> str:
        """Build a question-led answer policy without a hidden report template."""
        del is_comprehensive, output_mode
        selected_count = int(knowledge.get("_selected_gene_count") or 0) if knowledge else 0
        retrieved_count = len(knowledge.get("genes", {}) or {}) if knowledge else 0
        scale_note = ""
        if selected_count > 30 or retrieved_count > 30:
            scale_note = (
                "When the supplied cohort is large and the user did not ask for a full list. Do not enumerate all genes; "
                "synthesize the dominant patterns and representative examples rather than copying every row. "
                "If the user asks for a list or table, provide the requested rows.\n"
            )
        return (
            "You are E2seq, a scientific assistant for user-provided expression and sequencing results.\n"
            "Answer the user's actual question directly. Follow the user's requested language, format, "
            "scope, and level of detail; do not impose a fixed report structure or add unrelated sections.\n"
            "Use the uploaded values and the retrieved evidence supplied in the context. Preserve labels, "
            "signs, and numeric values when quoting them, and never invent a result or source.\n"
            "Do not silently claim a computation that was not performed or supplied. If the user asks for "
            "something that cannot be supported by the available data or tools, say exactly what is missing.\n"
            "Treat STRING, Reactome, QuickGO, TRRUST, literature, and other database records as external "
            "annotations or evidence, not as statistics calculated from the uploaded file. Distinguish "
            "association from causality and state important uncertainty.\n"
            "The retrieved digest is evidence, not an answer template. Do not reproduce its headings or "
            "automatically discuss modules, interactions, targets, or pathways unless the user's question "
            "calls for them. For a broad question, integrate the evidence across relevant sources; for a "
            "focused question, omit unrelated evidence.\n"
            "When retrieved sources support a biological claim, cite the source label or record naturally. "
            "Use the question-specific PubMed/Europe PMC search record supplied in the context whenever it "
            "is present, and cite PMID or Europe PMC identifiers/links for literature-backed claims. "
            "The user's question controls the answer: do not default to modules, interactions, targets, or "
            "a fixed report outline unless they answer the question or the user requests them. A literature "
            "search may be skipped only when the retrieval plan explicitly judged the existing evidence "
            "sufficient; otherwise report the search attempt and use the relevant records.\n"
            "End with a complete sentence. If the response is getting long, stop before starting an unfinished clause; "
            "do not leave a sentence fragment at the end.\n"
            + scale_note
            + "Return normal Markdown suitable for the web chat.\n"
            + ("The user's current question is: " + str(question or "") + "\n" if question else "")
        )

    def _format_results(self, results: Dict[str, Any], knowledge: Dict[str, Any] = None) -> str:
        """Format only values present in the uploaded sequencing result."""
        sections = [
            "=== USER-PROVIDED SEQUENCING GENE VALUES ===",
            "No new marker, DEG, enrichment, clustering, or network analysis was run during answer synthesis.",
        ]

        # Some workflows execute a compact GO/KEGG/GSEA/STRING batch at the
        # user's first question, before RAG synthesis. Report those stored
        # outputs as upstream results without implying that synthesis reran
        # any statistics.
        enrichment = results.get("question_time_enrichment")
        enrichment_summary = results.get("question_time_enrichment_summary")
        if enrichment or enrichment_summary:
            sections.append("\n=== QUESTION-TIME GO/KEGG/GSEA/STRING BATCH ===")
            sections.append(
                "This batch was completed before RAG synthesis; it was not recomputed while writing the answer."
            )
            if enrichment_summary:
                sections.append(str(enrichment_summary))
            if isinstance(enrichment, dict):
                for set_name, payload in enrichment.items():
                    if not isinstance(payload, dict):
                        continue
                    bits = []
                    for label in ("go", "kegg", "gsea"):
                        entries = payload.get(label)
                        if isinstance(entries, list):
                            terms = [
                                str(item.get("Term") or item.get("Name") or item.get("term") or "")
                                for item in entries[:3]
                                if isinstance(item, dict)
                            ]
                            terms = [term for term in terms if term]
                            if terms:
                                bits.append(f"{label.upper()}: {', '.join(terms)}")
                        elif isinstance(entries, dict) and entries.get("error"):
                            bits.append(f"{label.upper()}: unavailable ({entries['error']})")
                    string_edges = payload.get("string")
                    if isinstance(string_edges, list) and string_edges:
                        bits.append(f"STRING edges: {len(string_edges)}")
                    if bits:
                        sections.append(f"{set_name}: " + "; ".join(bits))

        if results.get("gene_context"):
            sections.append(results["gene_context"])
            return "\n".join(sections)

        context = results.get("matrix_context")
        if not context:
            return "No input gene-value context available."

        genes = context.get("genes_queried", [])
        if genes:
            if len(genes) > 30:
                sections.append(
                    f"Genes selected for RAG: {len(genes)} expression items. "
                    "The complete set remains available in the structured result/table; "
                    "only representative items are shown here so the interpretation is cohort-level."
                )
                sections.append(f"Representative input items (first 12 only): {', '.join(map(str, genes[:12]))}")
            else:
                sections.append(f"Genes selected for RAG ({len(genes)}): {', '.join(map(str, genes))}")

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
                for gene, value in list(overall.items())[:12 if len(genes) > 30 else 100]
            )
            suffix = " (representative subset; full values remain in the table)" if len(genes) > 30 else ""
            sections.append(f"\nOverall input mean values{suffix}: {rendered}")

        append_value_map(
            "INPUT MEAN VALUES BY USER-SUPPLIED GROUP",
            context.get("top_genes_per_group", {}),
            12 if len(genes) > 30 else 50,
        )
        append_value_map(
            "INPUT MEAN VALUES BY USER-SUPPLIED CELL TYPE",
            context.get("top_genes_per_celltype", {}),
            12 if len(genes) > 30 else 50,
        )
        sections.append(
            "\nThese are direct summaries of the uploaded matrix values. "
            "Use them only as context for RAG interpretation."
        )
        return "\n".join(sections)

    def _format_large_cohort_knowledge(self, knowledge: Dict[str, Any], question: str = "") -> str:
        """Aggregate large RAG cohorts into modules instead of gene-by-gene prose.

        This is a deterministic reduction of already retrieved annotations. It
        does not calculate new expression statistics, enrichment p-values, or
        causal effects. The complete gene-level records stay in ``knowledge``
        and the downloadable result; this text is deliberately a synthesis
        context for the LLM rather than a second gene list.
        """
        from collections import Counter, defaultdict

        genes_info = knowledge.get("genes", {}) or {}
        rag_queried_genes = len(genes_info)
        selected_genes = int(knowledge.get("_selected_gene_count") or rag_queried_genes)
        if not rag_queried_genes:
            return "No gene information retrieved."

        def _items(value: Any) -> list:
            if value is None:
                return []
            if isinstance(value, list):
                return value
            if isinstance(value, tuple):
                return list(value)
            return [value]

        def _label(value: Any) -> str:
            if isinstance(value, dict):
                for key in (
                    "name", "term", "Term", "Name", "pathway", "displayName",
                    "description", "field", "value",
                ):
                    if value.get(key) not in (None, ""):
                        return str(value[key])
            return str(value or "")

        def _clean(text: str, limit: int = 90) -> str:
            return " ".join(str(text).split())[:limit]

        term_counts = Counter()
        term_genes = defaultdict(set)
        for gene, info in genes_info.items():
            if not isinstance(info, dict):
                continue
            for field in ("pathways", "reactome_pathways", "go_terms", "go_aspects"):
                for value in _items(info.get(field)):
                    term = _clean(_label(value))
                    if term:
                        term_counts[term] += 1
                        term_genes[term].add(str(gene))

        source_gene_counts = Counter()
        for source, fields in _RAG_SOURCE_FIELDS.items():
            for info in genes_info.values():
                if isinstance(info, dict) and any(info.get(field) for field in fields):
                    source_gene_counts[source] += 1
        for info in genes_info.values():
            if not isinstance(info, dict):
                continue
            for field, value in info.items():
                if str(field).startswith("custom_") and str(field).endswith("_records") and value:
                    source_gene_counts[str(field)[len("custom_"):-len("_records")]] += 1

        partner_counts = Counter()
        partner_sources = defaultdict(set)

        def _add_partner(gene: str, raw: Any, source: str) -> None:
            partner = ""
            if isinstance(raw, dict):
                partner = str(
                    raw.get("partner") or raw.get("target") or raw.get("target_gene")
                    or raw.get("source") or raw.get("interactor_b") or ""
                )
            else:
                text = str(raw or "")
                for separator in ("->", "--", "—", "–"):
                    if separator in text:
                        parts = [part.strip() for part in text.split(separator) if part.strip()]
                        if len(parts) >= 2:
                            partner = parts[-1] if parts[0].upper() == str(gene).upper() else parts[0]
                            break
                if not partner:
                    partner = text.split()[0] if text.split() else ""
            partner = partner.strip(" []():;,.")
            # IntAct may return stable database identifiers instead of symbols;
            # preserve them only when they look like a compact node label.
            if not partner or partner.upper() == str(gene).upper() or len(partner) > 80:
                return
            if partner.lower().startswith(("uniprotkb", "intact:")):
                return
            partner_counts[partner] += 1
            partner_sources[partner].add(source)

        for gene, info in genes_info.items():
            if not isinstance(info, dict):
                continue
            for raw in _items(info.get("interactions")):
                _add_partner(str(gene), raw, "STRING")
            for raw in _items(info.get("omnipath_interactions")):
                _add_partner(str(gene), raw, "OmniPath")
            for raw in _items(info.get("intact_interactions")):
                _add_partner(str(gene), raw, "IntAct/PSICQUIC")

        regulator_counts = Counter()
        for gene, info in genes_info.items():
            if not isinstance(info, dict):
                continue
            for raw in _items(info.get("regulators")):
                if isinstance(raw, dict):
                    name = raw.get("tf") or raw.get("source")
                else:
                    name = raw
                if name:
                    regulator_counts[_clean(name, 50)] += 1
            for raw in _items(info.get("tf_targets")):
                if isinstance(raw, dict):
                    name = raw.get("target_gene") or raw.get("target")
                else:
                    name = raw
                if name:
                    regulator_counts[_clean(name, 50)] += 1

        # Aggregate metabolite and microbiome records explicitly.  These
        # fields used to remain buried in per-gene records, which made a
        # question about microbial metabolites look like a missing-data case
        # even when HMDB/GutMGene had returned usable annotations.
        metabolite_counts = Counter()
        metabolite_genes = defaultdict(set)
        metabolite_types = defaultdict(set)
        microbe_counts = Counter()
        microbe_genes = defaultdict(set)
        microbe_context = defaultdict(set)
        for gene, info in genes_info.items():
            if not isinstance(info, dict):
                continue
            for raw in _items(info.get("metabolites")):
                if isinstance(raw, dict):
                    name = raw.get("name") or raw.get("metabolite_name") or raw.get("metabolite")
                    protein_type = raw.get("protein_type") or raw.get("type") or ""
                else:
                    name, protein_type = raw, ""
                name = _clean(name, 120)
                if not name:
                    continue
                metabolite_counts[name] += 1
                metabolite_genes[name].add(str(gene))
                if protein_type:
                    metabolite_types[name].add(_clean(protein_type, 60))
            for raw in _items(info.get("gut_microbes")):
                if isinstance(raw, dict):
                    microbe = raw.get("microbe") or raw.get("gut_microbiota") or raw.get("name")
                    context = " | ".join(
                        str(value).strip()
                        for value in (raw.get("Alteration"), raw.get("Condition"), raw.get("PMID"))
                        if str(value or "").strip()
                    )
                else:
                    microbe, context = raw, ""
                microbe = _clean(microbe, 120)
                if not microbe:
                    continue
                microbe_counts[microbe] += 1
                microbe_genes[microbe].add(str(gene))
                if context:
                    microbe_context[microbe].add(_clean(context, 120))

        def _gene_score(gene: str, info: dict) -> int:
            evidence_fields = (
                "function", "gene_summary", "pathways", "reactome_pathways", "go_terms",
                "ot_diseases", "drug_targets", "interactions", "regulators", "tf_targets",
                "metabolites", "gtex_tissues", "hpa_tissues", "gwas_snps", "civic_variants",
                "alliance_homologs", "cbioportal_gene", "omnipath_interactions", "intact_interactions",
                "humanbase_networks", "humanbase_terms", "clinicaltrials_studies",
            )
            score = sum(1 for field in evidence_fields if info.get(field))
            score += min(4, len(_items(info.get("interactions"))))
            score += 3 if info.get("drug_targets") else 0
            score += 2 if info.get("ot_diseases") else 0
            score += 1 if info.get("civic_variants") or info.get("clinvar_variants") else 0
            score += sum(
                1 for key, value in info.items()
                if str(key).startswith("custom_") and str(key).endswith("_records") and value
            )
            return score

        scored = sorted(
            ((str(gene), info, _gene_score(str(gene), info)) for gene, info in genes_info.items() if isinstance(info, dict)),
            key=lambda item: (-item[2], list(genes_info).index(item[0])),
        )
        representatives = scored[:12]

        stats = knowledge.get("_source_stats", {}) or {}
        status_lines = []
        for category in ("apis", "dbs"):
            for source, info in (stats.get(category, {}) or {}).items():
                hit = int(info.get("hit_count") or len(info.get("hit_genes", []) or []))
                states = info.get("status_counts", {}) or {}
                if states.get("needs_configuration"):
                    state = "需要配置"
                elif states.get("error") or states.get("unavailable"):
                    state = "接口错误"
                elif hit == 0 and states.get("no_records"):
                    state = "接口可用但本批基因无记录"
                else:
                    state = "接口可用"
                status_lines.append(f"{source}: {hit}/{rag_queried_genes} 个 RAG 表达项目有记录（{state}）")

        lines = [
            f"=== COHORT-LEVEL RAG SYNTHESIS ({selected_genes} selected expression items; {rag_queried_genes} RAG items queried) ===",
            "This is a question-neutral evidence digest, not a required answer outline. The complete selected cohort remains in the structured statistical result. It integrates batch enrichment/network evidence and source-specific RAG evidence for the full selected cohort; it intentionally does not enumerate the full gene list.",
        ]
        if status_lines:
            lines.append("\nSOURCE AVAILABILITY AND COVERAGE:")
            lines.extend(f"- {line}" for line in status_lines)

        if term_counts:
            lines.append("\nDOMINANT ANNOTATION MODULES (retrieved-term recurrence, not new enrichment statistics):")
            for term, count in term_counts.most_common(12):
                lines.append(f"- {_clean(term)} — present in {len(term_genes[term])} expression items")
        else:
            lines.append("\nDOMINANT ANNOTATION MODULES: no recurrent pathway/GO labels were returned by the enabled sources.")

        if partner_counts:
            lines.append("\nINTERACTION HUBS AND NETWORK EVIDENCE:")
            for partner, count in partner_counts.most_common(12):
                sources = ", ".join(sorted(partner_sources[partner]))
                lines.append(f"- {partner} — connected to {count} selected items; evidence: {sources}")
        else:
            lines.append("\nINTERACTION HUBS: no symbol-resolvable partner hubs were returned; database availability is reported above.")

        if regulator_counts:
            lines.append("\nREGULATORY BRIDGES:")
            lines.extend(f"- {name} — linked to {count} selected items" for name, count in regulator_counts.most_common(10))

        lines.append("\nREPRESENTATIVE ITEMS (8–12 only; selected by multi-source evidence richness):")
        for gene, info, score in representatives:
            evidence = []
            if info.get("drug_targets"):
                evidence.append("drug/target")
            if info.get("ot_diseases"):
                evidence.append("Open Targets disease")
            if info.get("civic_variants") or info.get("clinvar_variants"):
                evidence.append("clinical variant")
            if info.get("interactions") or info.get("omnipath_interactions") or info.get("intact_interactions"):
                evidence.append("interaction")
            if info.get("pathways") or info.get("reactome_pathways") or info.get("go_terms"):
                evidence.append("pathway/GO")
            if info.get("humanbase_networks") or info.get("humanbase_terms"):
                evidence.append("HumanBase")
            if info.get("clinicaltrials_studies"):
                evidence.append("ClinicalTrials.gov")
            if any(str(key).startswith("custom_") and str(key).endswith("_records") and value for key, value in info.items()):
                evidence.append("custom API")
            lines.append(f"- {gene} — evidence richness {score}; {', '.join(evidence[:4]) or 'annotation'}")

        pubmed_all = knowledge.get("pubmed", []) or []
        europepmc_all = knowledge.get("europepmc", []) or []
        literature_stats = knowledge.get("_source_stats", {}) or {}
        literature_queries = literature_stats.get("literature_queries", {}) or {}
        literature_details = literature_stats.get("literature_query_details", {}) or {}
        if metabolite_counts or microbe_counts:
            lines.append("\nMICROBIAL-METABOLITE AND GUT-MICROBE EVIDENCE (retrieved annotations, not causal proof):")
            if metabolite_counts:
                lines.append("- HMDB metabolite-gene records:")
                for name, count in metabolite_counts.most_common(12):
                    type_note = "; ".join(sorted(metabolite_types[name]))
                    type_note = f"; type={type_note}" if type_note else ""
                    genes_preview = ", ".join(sorted(metabolite_genes[name])[:8])
                    lines.append(f"  - {name} — linked to {len(metabolite_genes[name])} selected items ({genes_preview}){type_note}")
            if microbe_counts:
                lines.append("- GutMGene microorganism-gene records:")
                for microbe, count in microbe_counts.most_common(12):
                    genes_preview = ", ".join(sorted(microbe_genes[microbe])[:8])
                    context_preview = "; ".join(sorted(microbe_context[microbe])[:2])
                    context_preview = f"; context={context_preview}" if context_preview else ""
                    lines.append(f"  - {microbe} — linked to {len(microbe_genes[microbe])} selected items ({genes_preview}){context_preview}")
            lines.append("- These records identify candidate associations only; they do not establish that the metabolite is produced by the listed microbe in this cohort or that it drives cancer.")
        elif literature_queries or pubmed_all or europepmc_all:
            lines.append("\nMICROBIAL-METABOLITE EVIDENCE: no HMDB/GutMGene metabolite record was returned for the queried cohort.")

        if literature_queries or literature_details or pubmed_all or europepmc_all:
            lines.append("\nQUESTION-SPECIFIC LITERATURE SEARCH:")
            lines.append(
                f"- This question used {int(literature_queries.get('pubmed', 0) or 0)} PubMed queries and "
                f"{int(literature_queries.get('europepmc', 0) or 0)} Europe PMC queries; "
                f"the retrieved pools contain {len(pubmed_all)} and {len(europepmc_all)} records respectively."
            )
            for source in ("pubmed", "europepmc"):
                queries = literature_details.get(source, []) if isinstance(literature_details, dict) else []
                if queries:
                    lines.append(f"- {source} query strings actually sent: " + " || ".join(str(query)[:140] for query in queries[:8]))

        final_literature = knowledge.get("_final_literature", {})
        pubmed = (
            final_literature.get("pubmed")
            if isinstance(final_literature, dict) and "pubmed" in final_literature
            else self._rank_literature_records(pubmed_all, question=question, limit=12)
        )
        europepmc = (
            final_literature.get("europepmc")
            if isinstance(final_literature, dict) and "europepmc" in final_literature
            else self._rank_literature_records(europepmc_all, question=question, limit=12)
        )
        if pubmed:
            lines.append(f"\nPUBMED SELECTED EVIDENCE ({len(pubmed)} of {len(pubmed_all)}):")
            for article in pubmed:
                lines.append(f"- [{article.get('pmid', 'N/A')}] {_clean(article.get('title', ''), 140)}")
        if europepmc:
            lines.append(f"\nEUROPE PMC SELECTED EVIDENCE ({len(europepmc)} of {len(europepmc_all)}):")
            for article in europepmc:
                lines.append(f"- [{article.get('pmid', 'N/A')}] {_clean(article.get('title', ''), 140)}")
        return "\n".join(lines)

    def _format_knowledge(self, knowledge: Dict[str, Any], question: str = "") -> str:
        """Compact, high-density gene knowledge formatting to fit within token budget.

        Small cohorts retain compact representative-level evidence. Large cohorts
        are reduced to cohort modules, hubs, target tiers, and 8–12 representatives;
        the full structured records are never expanded into the prompt.
        """
        genes_info = knowledge.get("genes", {})
        if not genes_info:
            evidence_parts = []
            if knowledge.get("rag_context"):
                evidence_parts.append(
                    "RAG retrieved context is available for this question:\n"
                    + self._truncate_to_token_budget(str(knowledge["rag_context"]), max_chars=8000)
                )
            for label, key in (("PubMed", "pubmed"), ("Europe PMC", "europepmc")):
                records = knowledge.get(key, []) or []
                if records:
                    evidence_parts.append(
                        f"{label} returned {len(records)} question-specific records; "
                        "use the titles/identifiers below as literature evidence.\n"
                        + "\n".join(
                            f"- [{item.get('pmid') or item.get('id') or 'N/A'}] {item.get('title', '')}"
                            for item in records[:12] if isinstance(item, dict)
                        )
                    )
            return "\n\n".join(evidence_parts) or "No RAG or literature record was retrieved."
        selected_count = int(knowledge.get("_selected_gene_count") or 0)
        if selected_count > 30 or len(genes_info) > 30:
            return self._format_large_cohort_knowledge(knowledge, question=question)

        # Score genes by data richness (more non-empty fields = more important)
        def gene_score(gene: str, info: dict) -> int:
            score = 0
            for field in ["function", "pathways", "go_terms", "ot_diseases", "drug_targets",
                           "interactions", "regulators", "tf_targets", "gut_microbes",
                           "metabolites", "reactome_pathways", "gene_summary",
                           "clinvar_variants", "gtex_tissues", "hpa_tissues",
                           "gwas_snps", "civic_variants",
                           "alliance_homologs", "cbioportal_gene", "omnipath_interactions",
                           "intact_interactions", "humanbase_networks",
                           "humanbase_terms", "clinicaltrials_studies"]:
                val = info.get(field)
                if val and (isinstance(val, list) and val or isinstance(val, str) and val):
                    score += 1
            score += sum(
                1 for key, value in info.items()
                if str(key).startswith("custom_") and str(key).endswith("_records") and value
            )
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

        lines = [f"=== GENE KNOWLEDGE (compact evidence for {len(top_genes)} of {len(genes_info)} retrieved genes) ===\n"]

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

            # 6. PPI — representative partners with scores
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

            # 11. Human Protein Atlas
            hpa = info.get("hpa_tissues") or []
            if hpa:
                parts.append(f"HPA:{','.join(str(t)[:40] for t in hpa[:5])}")

            # 12. GWAS trait associations
            gwas = info.get("gwas_snps") or []
            if gwas:
                parts.append(f"GWAS:{';'.join(str(s)[:60] for s in gwas[:5])}")

            # 13. CIViC cancer variants
            civic = info.get("civic_variants") or []
            if civic:
                parts.append(f"CIViC:{','.join(str(v)[:35] for v in civic[:5])}")

            # 15. Alliance cross-species homologs
            alliance = info.get("alliance_homologs") or []
            if alliance:
                parts.append(f"Alliance:{','.join(str(h)[:35] for h in alliance[:5])}")

            # 16b. Cancer genomics and interaction services
            cbio = info.get("cbioportal_gene") or []
            if cbio:
                parts.append(f"cBioPortal:{','.join(str(v)[:45] for v in cbio[:3])}")
            omnipath = info.get("omnipath_interactions") or []
            if omnipath:
                parts.append(f"OmniPath:{';'.join(str(v)[:55] for v in omnipath[:4])}")
            intact = info.get("intact_interactions") or []
            if intact:
                parts.append(f"IntAct:{';'.join(str(v)[:55] for v in intact[:4])}")

            humanbase = list(info.get("humanbase_networks") or []) + list(info.get("humanbase_terms") or [])
            if humanbase:
                parts.append(f"HumanBase:{';'.join(str(v)[:60] for v in humanbase[:4])}")
            trials = info.get("clinicaltrials_studies") or []
            if trials:
                parts.append(f"ClinicalTrials:{';'.join(str(v)[:70] for v in trials[:3])}")
            custom_records = [
                (str(key)[len("custom_"):-len("_records")], value)
                for key, value in info.items()
                if str(key).startswith("custom_") and str(key).endswith("_records") and value
            ]
            for source_id, values in custom_records[:2]:
                rendered = values if isinstance(values, list) else [values]
                parts.append(f"Custom[{source_id}]:{';'.join(str(v)[:70] for v in rendered[:3])}")

            # 16. ClinVar pathogenic variants
            clinvar = info.get("clinvar_variants") or []
            if clinvar:
                parts.append(f"ClinVar:{';'.join(str(v)[:50] for v in clinvar[:5])}")

            # 17. Open Targets disease associations
            ot = info.get("ot_diseases") or []
            if ot:
                parts.append(f"OT:{';'.join(str(d)[:60] for d in ot[:5])}")

            lines.append(f"{gene}: " + " | ".join(parts) if parts else gene)

        # Graph-linked edges — compact representative context
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
            lines.append("\n=== REPRESENTATIVE INTERACTION EDGES ===")
            lines.extend(graph_edges[:60])

        # PubMed — selected records with source links
        # Keep the full raw lists in ``knowledge`` for auditability. The final
        # lists are chosen by the LLM against the question and current RAG context;
        # direct formatting calls use the deterministic overlap fallback.
        pubmed_all = knowledge.get("pubmed", [])
        europepmc_all = knowledge.get("europepmc", [])
        final_literature = knowledge.get("_final_literature", {})
        pubmed = (
            final_literature.get("pubmed")
            if isinstance(final_literature, dict) and "pubmed" in final_literature
            else self._rank_literature_records(pubmed_all, question=question, limit=8)
        )
        if pubmed:
            lines.append(
                f"\n=== PUBMED (relevant {len(pubmed)} of {len(pubmed_all)}) ==="
            )
            for art in pubmed:
                pmid = art.get("pmid", "N/A")
                title = art.get("title", "")[:120]
                journal = art.get("journal", "")[:40]
                date = art.get("pub_date", "") or art.get("year", "")
                authors = art.get("authors", "")
                url = art.get("url", "")
                lines.append(f"  [{pmid}] {title} | {journal} {date} | {authors}")
                if url:
                    lines.append(f"    URL: {url}")

        # EuropePMC — selected records with source links
        europepmc = (
            final_literature.get("europepmc")
            if isinstance(final_literature, dict) and "europepmc" in final_literature
            else self._rank_literature_records(europepmc_all, question=question, limit=8)
        )
        if europepmc:
            lines.append(
                f"\n=== EUROPEPMC (relevant {len(europepmc)} of {len(europepmc_all)}) ==="
            )
            for art in europepmc:
                pmid = art.get("pmid", "N/A")
                year = art.get("pub_year", art.get("year", ""))
                title = art.get("title", "")[:120]
                journal = art.get("journal", "")[:40]
                url = art.get("url", "")
                lines.append(f"  [{pmid}] {year} | {title} | {journal}")
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
