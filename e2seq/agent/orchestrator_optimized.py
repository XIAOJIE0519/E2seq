"""Final optimized Agent orchestrator with full integration of all modules."""

import time
import threading
import uuid
import json
from io import StringIO
from typing import Any, Dict, List, Optional

from anndata import AnnData

from e2seq.agent.error_recovery import ErrorRecovery
from e2seq.agent.memory import MemoryManager
from e2seq.agent.state_manager import AgentState, StateManager
from e2seq.agent.synthesizer import SynthesizerAgent
from e2seq.agent.tool_registry import create_tool_registry
from e2seq.data.api_client_enhanced import create_api_clients
from e2seq.llm import create_llm_provider
from e2seq.tools import ScancpyTools
from e2seq.utils import get_config, get_logger, get_security_manager
from e2seq.utils.config import DEFAULT_ANSWER_APIS, DEFAULT_ANSWER_DBS
from e2seq.utils.gene_intersection import apply_gene_intersection, gene_key, normalize_gene_list

logger = get_logger(__name__)

# A single expression item fans out to many source adapters.  Keep the
# per-item API fan-out bounded so large selected cohorts remain responsive
# without creating one thread per enabled source for every gene worker.
_MAX_SOURCE_WORKERS = 4

# These are the sources that have a maintained adapter or a local query
# implementation.  Deprecated BioGRID/DepMap adapters remain only for
# backward-compatible imports; neither is in the active source policy.
VERIFIED_RAG_APIS = frozenset(DEFAULT_ANSWER_APIS)
VERIFIED_RAG_DBS = frozenset(DEFAULT_ANSWER_DBS)
OPTIONAL_RAG_APIS = frozenset()


class E2seqAgentOptimized:
    """Final optimized agent with full integration of all optimization modules.

    Features:
    - [OK] MemoryManager integration (short-term + long-term memory)
    - [OK] StateManager integration (state tracking + checkpoints)
    - [OK] ErrorRecovery integration (auto-retry + fallback)
    - [OK] ToolRegistry (API, local-database, and code-execution tools)
    - [OK] EnhancedAPIClient (multi-layer fallback)
    - [OK] Auto-save to vector database
    - [OK] Per-session memory, state, cache, and recovery isolation
    """

    def __init__(
        self,
        adata: Optional[AnnData] = None,
        llm_provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        session_id: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """Initialize fully optimized E2seq agent."""
        logger.info("=" * 60)
        logger.info("Initializing E2seq Agent v0.2.0 (Fully Optimized)")
        logger.info("=" * 60)

        self.config = get_config()
        self.security = get_security_manager()
        data_session_id = adata.uns.get("e2sc_session_id") if adata is not None else None
        self._session_id = str(session_id or data_session_id or uuid.uuid4())

        provider = llm_provider or self.config.llm.provider

        # key 优先用调用方传入的明文，否则从配置读取并解密
        if api_key:
            key = api_key  # 调用方（server.py）已传入明文，无需再解密
        elif self.config.llm.api_key:
            key = self.security.decrypt(self.config.llm.api_key)  # 从配置读取时需要解密
        else:
            key = ""

        # base_url: for "custom" provider it lives in llm.base_url directly;
        # for other providers it is looked up from the per-provider base_urls dict.
        if provider == "custom":
            effective_base_url = base_url or self.config.llm.base_url
        else:
            effective_base_url = base_url or self.config.get_provider_base_url(provider)

        self.llm = create_llm_provider(
            provider=provider,
            api_key=key,
            model=model or self.config.llm.model,
            temperature=self.config.llm.temperature,
            max_tokens=self.config.llm.max_tokens,
            thinking_enabled=self.config.llm.thinking_enabled,
            thinking_effort=self.config.llm.thinking_effort or "high",
            base_url=effective_base_url,
        )

        self.adata = adata
        self.scanpy_tools = ScancpyTools(adata) if adata else None

        # OPTIMIZATION 1: Use enhanced API clients with fallback
        logger.info("[OK] Loading enhanced API clients with fallback mechanisms")
        self.api_clients = create_api_clients()

        # OPTIMIZATION 2: Register all API tools + code execution tools
        logger.info("\u2713 Registering bioinformatics API tools + code execution tools")
        from e2seq.agent.code_executor import get_executor
        from e2seq.agent.api_tools import register_api_tools
        self.code_executor = get_executor(
            session_id=self._session_id,
            adata=adata,
        )
        self.tool_registry = create_tool_registry(self.api_clients, code_executor=self.code_executor)
        # Register api/ folder tools (pre-built, no code writing needed)
        register_api_tools(self.tool_registry)
        logger.info(f"  - Registered tools: {', '.join(self.tool_registry.get_tool_names())}")

        self.synthesizer = SynthesizerAgent(self.llm)

        # Per-session vector store for RAG (populated during offline knowledge build)
        self._vector_store = None

        # Per-instance cache: API results and its lock must never be shared by chats.
        self._gene_cache: dict = {}
        self._gene_cache_lock: threading.Lock = threading.Lock()

        # OPTIMIZATION 4: Integrate MemoryManager
        logger.info("[OK] Integrating MemoryManager (short-term + long-term)")
        self.memory = MemoryManager()
        if hasattr(self.memory, 'session_id'):
            self.memory.session_id = self._session_id
        # P0/P1: inject LLM so MemoryManager can run auto-summarization
        if hasattr(self.memory, 'set_llm'):
            self.memory.set_llm(self.llm)

        # OPTIMIZATION 5: Integrate StateManager
        logger.info("[OK] Integrating StateManager (state tracking + checkpoints)")
        self.state_manager = StateManager(session_id=self._session_id)
        if hasattr(self.state_manager, 'set_state'):
            self.state_manager.set_state(AgentState.IDLE)

        # OPTIMIZATION 6: Integrate ErrorRecovery
        logger.info("[OK] Integrating ErrorRecovery (auto-retry + fallback)")
        self.error_recovery = ErrorRecovery()

        logger.info("=" * 60)
        logger.info("[OK] E2seq Agent fully initialized with all optimizations")
        logger.info("=" * 60)

    def _effective_answer_sources(self) -> tuple[set[str], set[str]]:
        """Return the source policy for the next answer.

        Before the knowledge-base answer settings were introduced, each
        dataset stored its own source choices.  Keep that behaviour until the
        user explicitly saves the new global answer policy; after that, the
        policy is applied only when a new answer starts.
        """
        def _items(value):
            if value is None:
                return []
            if isinstance(value, (str, bytes)):
                return [value]
            try:
                return list(value)
            except TypeError:
                return [value]

        configured = getattr(getattr(self.config, "answer_settings", None), "configured", False)
        if configured:
            settings = self.config.answer_settings
            return (
                set(str(item) for item in _items(settings.enabled_apis) if str(item).strip()),
                set(str(item) for item in _items(settings.enabled_dbs) if str(item).strip()),
            )

        if self.adata is not None:
            # Older bulk handoff snapshots did not write the source policy to
            # AnnData even though the RAG snapshot was queried with the full
            # verified source catalog.  Treat a missing key as the effective
            # default; preserve an explicit empty list if a user deliberately
            # disabled every source.
            apis = self.adata.uns.get("e2sc_enabled_apis")
            dbs = self.adata.uns.get("e2sc_enabled_dbs")
            if apis is None:
                apis = DEFAULT_ANSWER_APIS
            if dbs is None:
                dbs = DEFAULT_ANSWER_DBS
            return set(str(item) for item in _items(apis) if str(item).strip()), set(
                str(item) for item in _items(dbs) if str(item).strip()
            )
        return set(), set()

    def _apply_answer_policy(self) -> None:
        """Apply the saved answer-time source policy to this in-memory chat."""
        if self.adata is None:
            return
        enabled_apis, enabled_dbs = self._effective_answer_sources()
        signature = (tuple(sorted(enabled_apis)), tuple(sorted(enabled_dbs)))
        previous_signature = getattr(self, "_answer_source_policy_signature", None)
        self._answer_source_policy_changed = (
            previous_signature is not None and previous_signature != signature
        )
        self._answer_source_policy_signature = signature
        if self._answer_source_policy_changed:
            # Do not let a vector collection built under the previous source
            # policy leak into a new answer.
            self._persisted_rag_loaded = False
            self._persisted_rag_knowledge = None
            self._vector_store = None
            self._skip_persisted_vector_store = True
        if getattr(getattr(self.config, "answer_settings", None), "configured", False):
            self.adata.uns["e2sc_enabled_apis"] = sorted(enabled_apis)
            self.adata.uns["e2sc_enabled_dbs"] = sorted(enabled_dbs)

    def _apply_default_answer_prompt(self, message: str) -> str:
        """Apply only the optional prompt stored with the active dataset."""
        dataset_prompt = ""
        try:
            dataset_prompt = str(self.adata.uns.get("e2sc_dataset_prompt", "") or "").strip()
        except Exception:
            dataset_prompt = ""
        if not dataset_prompt:
            return message
        return (
            "Optional context supplied for this dataset:\n"
            f"{dataset_prompt}\n\n"
            "User question:\n"
            f"{message}"
        )

    @staticmethod
    def _select_agent_sources(
        plan: Dict[str, Any],
        enabled_apis: set,
        enabled_dbs: set,
    ) -> tuple[set, set]:
        """Resolve the LLM source plan against the user's allow-list.

        The answer settings are an allow-list: a planner can narrow the
        retrieval scope, but it can never enable a source that the user
        disabled.  Older code discarded ``apis_to_use``/``dbs_to_use`` and
        always queried every enabled source, which made the planner output
        cosmetic rather than operational.

        PubMed and Europe PMC remain automatic literature sources when the
        user has enabled them, matching the planner contract.  An invalid or
        empty planner response falls back to the complete user allow-list so
        a malformed LLM response cannot silently produce an empty RAG.
        """
        _all_apis = set(VERIFIED_RAG_APIS | OPTIONAL_RAG_APIS)
        try:
            from e2seq.data.custom_sources import load_custom_sources
            _all_apis.update(
                str(item.get("id")).lower()
                for item in load_custom_sources(include_secrets=False)
                if item.get("id")
            )
        except Exception:
            # A malformed optional registry must not disable built-in RAG.
            pass
        _all_dbs = set(VERIFIED_RAG_DBS)
        if "custom_gene_annotations" in {str(value).strip().lower() for value in (enabled_dbs or set())}:
            _all_dbs.add("custom_gene_annotations")

        def _normalise(values: Any) -> list[str]:
            if values is None:
                return []
            if isinstance(values, (str, bytes)):
                values = [values]
            try:
                return [str(value).strip().lower() for value in values if str(value).strip()]
            except TypeError:
                return [str(values).strip().lower()] if str(values).strip() else []

        allowed_apis = {str(value).strip().lower() for value in (enabled_apis or set())} & _all_apis
        allowed_dbs = {str(value).strip().lower() for value in (enabled_dbs or set())} & _all_dbs

        planned_apis = set(_normalise(plan.get("apis_to_use"))) if isinstance(plan, dict) else set()
        planned_dbs = set(_normalise(plan.get("dbs_to_use"))) if isinstance(plan, dict) else set()
        selected_apis = (planned_apis & allowed_apis) or set(allowed_apis)
        selected_dbs = (planned_dbs & allowed_dbs) or set(allowed_dbs)

        # Literature is part of the Agent RAG contract, but still obeys the
        # user's source settings.
        selected_apis.update(allowed_apis & {"pubmed", "europepmc"})
        return selected_apis, selected_dbs

    def load_data(self, adata: AnnData) -> None:
        """Load an expression-profile or single-cell dataset."""
        logger.info(f"Loading data: {adata.n_obs} cells, {adata.n_vars} genes")
        self.adata = adata
        self.scanpy_tools = ScancpyTools(adata)
        # Update code executor with new adata
        self.code_executor.adata = adata

        # Update memory and state
        dataset_info = {
            "n_cells": adata.n_obs,
            "n_genes": adata.n_vars,
            "cell_types": list(adata.obs.get("cell_type", []).unique()) if "cell_type" in adata.obs else []
        }
        self.memory.working_memory.update_context("dataset", dataset_info)
        self.state_manager.update_context({"dataset_loaded": True, "dataset_info": dataset_info})

    def _get_persisted_rag_knowledge(
        self,
        genes: list,
        required_apis: Optional[set] = None,
        required_dbs: Optional[set] = None,
    ) -> tuple[Optional[dict], list, bool]:
        """Return reusable local RAG evidence and any genes still missing.

        The snapshot is deliberately consulted before external retrieval.  A
        reopened chat therefore reuses completed per-gene evidence and its
        literature records; only genuinely new genes or source records can
        trigger new API work.
        """
        requested = list(dict.fromkeys(str(g).strip() for g in (genes or []) if str(g).strip()))
        if not requested:
            return None, [], False
        if not getattr(self, "_persisted_rag_loaded", False):
            try:
                from e2seq.agent.rag_persistence import load_rag_knowledge
                self._persisted_rag_knowledge = load_rag_knowledge(self._session_id)
            except Exception:
                self._persisted_rag_knowledge = None
            self._persisted_rag_loaded = True
        persisted = getattr(self, "_persisted_rag_knowledge", None)
        available = persisted.get("genes", {}) if isinstance(persisted, dict) else {}
        persisted_stats = persisted.get("_source_stats", {}) if isinstance(persisted, dict) else {}
        persisted_apis = set(str(item) for item in (persisted_stats.get("enabled_apis") or []) if str(item).strip())
        persisted_dbs = set(str(item) for item in (persisted_stats.get("enabled_dbs") or []) if str(item).strip())
        current_apis, current_dbs = self._effective_answer_sources()
        # A source disabled by the user must not leak into a new answer.  A
        # snapshot containing only a subset of the current allow-list remains
        # reusable; the missing sources are fetched below when the planner
        # requests them.
        if not persisted_apis.issubset(current_apis) or not persisted_dbs.issubset(current_dbs):
            return None, requested, False

        required_apis = set(required_apis) if required_apis is not None else set(current_apis)
        required_dbs = set(required_dbs) if required_dbs is not None else set(current_dbs)
        missing_sources = (
            not required_apis.issubset(persisted_apis)
            or not required_dbs.issubset(persisted_dbs)
        )
        reusable = [gene for gene in requested if gene in available]
        if not reusable:
            return None, requested, False
        import copy
        knowledge = {
            "genes": {gene: copy.deepcopy(available[gene]) for gene in reusable},
            "pubmed": copy.deepcopy((persisted or {}).get("pubmed", [])),
            "europepmc": copy.deepcopy((persisted or {}).get("europepmc", [])),
            "_source_stats": copy.deepcopy((persisted or {}).get("_source_stats", {})),
        }
        persisted_selected = int((persisted or {}).get("_selected_gene_count") or 0)
        persisted_total = int(
            (knowledge["_source_stats"] or {}).get("total_genes_queried") or 0
        )
        knowledge["_selected_gene_count"] = persisted_selected or persisted_total or len(available) or len(requested)
        knowledge["_rag_core_gene_count"] = int(
            (persisted or {}).get("_rag_core_gene_count") or len(available)
        )
        knowledge["_rag_queried_gene_count"] = len(reusable)
        knowledge["_source_stats"]["reused_from_disk"] = True
        missing = [gene for gene in requested if gene not in reusable]
        if missing_sources:
            # Reuse the existing records and ask the caller to augment all
            # requested genes with the planner-selected source subset.  This
            # avoids re-uploading data while preventing a partial snapshot
            # from being treated as complete.
            missing = list(dict.fromkeys(missing + reusable))
        return knowledge, missing, not missing and not missing_sources

    def _restore_persisted_vector_store(self) -> None:
        """Attach an existing on-disk vector collection without rebuilding it."""
        if getattr(self, "_skip_persisted_vector_store", False):
            return
        if self._vector_store is not None:
            return
        try:
            from e2seq.data.vector_store import get_vector_store
            store = get_vector_store(self._session_id, llm=self.llm)
            if store.count() > 0:
                self._vector_store = store
                logger.info("[RAG] Reused persisted vector store for session %s (%s chunks)", self._session_id, store.count())
        except Exception as exc:
            logger.warning(f"[RAG] Persisted vector store unavailable for {self._session_id}: {exc}")

    def _persist_rag_knowledge(self, knowledge: dict) -> None:
        """Save source-aware evidence after a completed retrieval pass."""
        try:
            from e2seq.agent.rag_persistence import save_rag_knowledge
            save_rag_knowledge(self._session_id, knowledge)
            self._persisted_rag_knowledge = knowledge
            self._persisted_rag_loaded = True
        except Exception as exc:
            logger.warning(f"[RAG] Failed to persist knowledge for {self._session_id}: {exc}")

    def build_knowledge_base(self) -> dict:
        """Offline phase: query all APIs/DBs for selected genes and build the session vector store.

        Called once after the user clicks Run Analysis.  Runs in a background thread
        and must complete before the user is allowed to ask questions.

        Returns:
            dict: success, n_docs, n_genes, error
        """
        if self.adata is None:
            return {"success": False, "n_docs": 0, "n_genes": 0, "error": "No data loaded"}
        try:
            # Clear gene cache at start of each fresh KB build
            self._gene_cache = {}
            self._gene_cache_lock = None  # reset lock too
            n_top = int(self.adata.uns.get("e2sc_n_top_genes", 50))
            # Use the user-configured n_top for both display AND KB build,
            # so the LLM answers are always based on the full gene set the user selected.
            KB_TOP = n_top
            enabled_apis = set(self.adata.uns.get("e2sc_enabled_apis", DEFAULT_ANSWER_APIS))
            enabled_dbs = set(self.adata.uns.get("e2sc_enabled_dbs", DEFAULT_ANSWER_DBS))
            celltype_labels = dict(self.adata.uns.get("e2sc_celltype_labels", {}))
            group_labels    = dict(self.adata.uns.get("e2sc_group_labels", {}))
            gene_intersection = normalize_gene_list(self.adata.uns.get("e2sc_gene_intersection", []))
            intersection_keys = {gene_key(gene) for gene in gene_intersection}

            ct_knowledge  = {}
            grp_knowledge = {}

            # ── CSV mode: build knowledge directly from pre-filtered CSV records ──
            if self.adata.uns.get("e2sc_data_mode") == "csv":
                uns = self.adata.uns
                grp_col    = uns.get("e2sc_group_col", "")
                groups     = uns.get("e2sc_groups", [])
                all_genes  = uns.get("e2sc_all_genes", [])

                logger.info(f"[离线构建] CSV模式知识库: {len(groups)} 个分组, {len(all_genes)} 个基因")

                # Build per-group gene lists from CSV records (no n_top cap)
                import pandas as pd
                records_json = uns.get("e2sc_csv_records", "[]")
                _df = pd.read_json(records_json, orient="records")
                _gene_col = uns.get("e2sc_gene_col", "name")
                _grp_col = uns.get("e2sc_group_col", "")
                _expr_col = uns.get("e2sc_expr_col", "log2FC")

                _grp_genes_map = {}  # {group: [genes sorted by |expr|]}
                for _grp in groups:
                    _sub = _df[_df[_grp_col].astype(str) == str(_grp)].copy()
                    _sub = _sub.sort_values(_expr_col, key=abs, ascending=False)
                    _genes = list(_sub[_gene_col].astype(str).unique())
                    if intersection_keys:
                        _genes = [gene for gene in _genes if gene_key(gene) in intersection_keys]
                    _grp_genes_map[_grp] = _genes

                # Build KB for each group concurrently
                from concurrent.futures import ThreadPoolExecutor as _TPE, as_completed as _asc
                def _build_csv_grp(args):
                    idx, grp, genes = args
                    _preview = ", ".join(genes[:5])
                    logger.info(f"[进度] [离线构建] 分组 {idx}/{len(groups)}: {grp} | {len(genes)} 个基因 | 前5: {_preview}...")
                    return grp, self._build_group_knowledge(
                        grp, genes, context_hint=grp,
                        enabled_apis=enabled_apis, enabled_dbs=enabled_dbs)

                grp_map = {
                    group_labels.get(_grp, _grp): _grp_genes_map.get(_grp, [])
                    for _grp in groups
                    if _grp_genes_map.get(_grp, [])
                }

                if grp_map:
                    with _TPE(max_workers=min(len(grp_map), 4)) as _pool:
                        _grp_futs = {_pool.submit(_build_csv_grp, (i, grp, genes)): grp
                                     for i, (grp, genes) in enumerate(grp_map.items(), 1)}
                        for _fut in _asc(_grp_futs):
                            _grp, _kb = _fut.result()
                            grp_knowledge[_grp] = _kb

                # Cache for follow-up questions
                self.memory.working_memory.update_context("comprehensive_knowledge", {
                    "ct_knowledge": {},
                    "grp_knowledge": grp_knowledge,
                })

                # Merge all knowledge into unified dict for vector store
                merged_genes, merged_pubmed, merged_epmc = {}, [], []
                seen_pmids = set()
                for kb in grp_knowledge.values():
                    merged_genes.update(kb.get("genes", {}))
                    for a in kb.get("pubmed", []):
                        pid = a.get("pmid", "")
                        if pid not in seen_pmids:
                            seen_pmids.add(pid); merged_pubmed.append(a)
                    for a in kb.get("europepmc", []):
                        pid = a.get("pmid", "") or a.get("id", "")
                        if pid not in seen_pmids:
                            seen_pmids.add(pid); merged_epmc.append(a)

                merged_knowledge = {"genes": merged_genes, "pubmed": merged_pubmed, "europepmc": merged_epmc}

                # Build vector store
                n_docs = 0
                if self._session_id:
                    from e2seq.data.vector_store import reset_vector_store
                    store = reset_vector_store(self._session_id, llm=self.llm)
                    n_docs = store.reset_and_build(merged_knowledge)
                    self._vector_store = store
                    logger.info(f"[离线构建] 向量库构建完成: {n_docs} 文档")

                n_genes = len(merged_genes)
                logger.info(f"[离线构建] 知识库构建完成: {n_genes} 基因, {n_docs} 向量文档")
                return {"success": True, "n_docs": n_docs, "n_genes": n_genes, "error": None}

            ct_col  = self.adata.uns.get("e2sc_celltype_col", None)
            grp_col = self.adata.uns.get("e2sc_group_col", "")

            if ct_col and self.scanpy_tools is not None:
                # Build display + KB matrix with user-configured n_top
                matrix = self.scanpy_tools.get_top_genes_matrix(n_top_genes=n_top, celltype_col=ct_col)
                matrix = apply_gene_intersection(matrix, gene_intersection)
                self.memory.working_memory.update_context("gene_matrix", matrix)
                ct_map = {
                    celltype_labels.get(k, k): v
                    for k, v in matrix.get("top_genes_per_celltype", {}).items()
                    if v
                }
                ct_total = len(ct_map)
                logger.info(f"[离线构建] 细胞类型知识库: {ct_total} 种细胞类型, 每种取 TOP{KB_TOP} 基因")
                # Process all cell types CONCURRENTLY to reduce total build time
                from concurrent.futures import ThreadPoolExecutor as _TPE, as_completed as _asc
                def _build_ct(args):
                    idx, ct, genes = args
                    logger.info(f"[进度] [离线构建] 细胞类型 {idx}/{ct_total}: {ct} | TOP{KB_TOP}: {', '.join(genes)}")
                    return ct, self._build_group_knowledge(
                        ct, genes, context_hint=ct,
                        enabled_apis=enabled_apis, enabled_dbs=enabled_dbs)
                if ct_total:
                    with _TPE(max_workers=min(ct_total, 8)) as _pool:
                        _ct_futs = {_pool.submit(_build_ct, (i, ct, genes)): ct
                                    for i, (ct, genes) in enumerate(ct_map.items(), 1)}
                        for _fut in _asc(_ct_futs):
                            _ct, _kb = _fut.result()
                            ct_knowledge[_ct] = _kb

            if grp_col and self.scanpy_tools is not None:
                # Build display + KB matrix with user-configured n_top
                grp_matrix = self.scanpy_tools.get_top_genes_by_group(group_col=grp_col, n_top_genes=n_top)
                grp_matrix = apply_gene_intersection(grp_matrix, gene_intersection)
                self.memory.working_memory.update_context("group_matrix", grp_matrix)
                grp_map = {
                    group_labels.get(k, k): v
                    for k, v in grp_matrix.get("top_genes_per_group", {}).items()
                    if v
                }
                grp_total = len(grp_map)
                logger.info(f"[离线构建] 疾病分组知识库: {grp_total} 个分组, 每组取 TOP{KB_TOP} 基因")
                # Process all disease groups CONCURRENTLY
                def _build_grp(args):
                    idx, grp, genes = args
                    logger.info(f"[进度] [离线构建] 疾病分组 {idx}/{grp_total}: {grp} | TOP{KB_TOP}: {', '.join(genes)}")
                    return grp, self._build_group_knowledge(
                        grp, genes, context_hint=grp,
                        enabled_apis=enabled_apis, enabled_dbs=enabled_dbs)
                if grp_total:
                    with _TPE(max_workers=min(grp_total, 4)) as _pool:
                        _grp_futs = {_pool.submit(_build_grp, (i, grp, genes)): grp
                                     for i, (grp, genes) in enumerate(grp_map.items(), 1)}
                        for _fut in _asc(_grp_futs):
                            _grp, _kb = _fut.result()
                            grp_knowledge[_grp] = _kb

            # Cache for follow-up questions (skip re-query)
            self.memory.working_memory.update_context("comprehensive_knowledge", {
                "ct_knowledge": ct_knowledge,
                "grp_knowledge": grp_knowledge,
            })

            # Merge all knowledge into unified dict for vector store
            merged_genes, merged_pubmed, merged_epmc = {}, [], []
            seen_pmids = set()
            for kb in list(ct_knowledge.values()) + list(grp_knowledge.values()):
                merged_genes.update(kb.get("genes", {}))
                for a in kb.get("pubmed", []):
                    pid = a.get("pmid", "")
                    if pid not in seen_pmids:
                        seen_pmids.add(pid); merged_pubmed.append(a)
                for a in kb.get("europepmc", []):
                    pid = a.get("pmid", "") or a.get("id", "")
                    if pid not in seen_pmids:
                        seen_pmids.add(pid); merged_epmc.append(a)

            merged_knowledge = {"genes": merged_genes, "pubmed": merged_pubmed, "europepmc": merged_epmc}

            # Build/rebuild vector store from merged knowledge
            n_docs = 0
            if self._session_id:
                from e2seq.data.vector_store import reset_vector_store
                store = reset_vector_store(self._session_id, llm=self.llm)
                n_docs = store.reset_and_build(merged_knowledge)
                self._vector_store = store
                logger.info(f"[离线构建] 向量库构建完成: {n_docs} 文档 (session={self._session_id})")

            n_genes = len(merged_genes)
            logger.info(f"[离线构建] 知识库构建完成: {n_genes} 基因, {n_docs} 向量文档")
            return {"success": True, "n_docs": n_docs, "n_genes": n_genes, "error": None}

        except Exception as e:
            logger.error(f"build_knowledge_base failed: {e}")
            return {"success": False, "n_docs": 0, "n_genes": 0, "error": str(e)}

    def chat(self, message: str, stream: bool = False, use_agent_mode: bool = False,
             progress_callback=None, text_queue=None, abort_flag=None):
        """Agentic RAG chat: Agent thinks -> RAG retrieves -> Agent evaluates -> re-retrieves -> LLM answers.

        Args:
            text_queue: if provided, synthesizer streams LLM text chunks through this queue
                        which is consumed by the SSE handler for real-time text display.
            abort_flag: threading.Event set by the server when the user clicks abort.
        """
        import time as _time

        started = _time.perf_counter()
        usage_before = self.llm.usage_snapshot() if hasattr(self.llm, "usage_snapshot") else {}
        self._apply_answer_policy()
        message = self._apply_default_answer_prompt(str(message or ""))
        logger.info(f"User message: {message}")
        self.state_manager.set_state(AgentState.PLANNING)
        self.memory.working_memory.add_message("user", message)
        thinking_steps = []

        # ── Pure conversational mode (no data uploaded) ──────────────────
        if self.adata is None:
            resp = self._chat_no_data(message, thinking_steps)
        else:
            # ── Agentic RAG loop (LLM auto-detects intent and data structure) ──
            resp = self._chat_agentic_rag(message, thinking_steps,
                                          progress_callback=progress_callback,
                                          text_queue=text_queue,
                                          abort_flag=abort_flag)
        # P1: auto-summarize after each exchange (checks threshold internally)
        if hasattr(self.memory, 'maybe_summarize'):
            self.memory.maybe_summarize()
        if not isinstance(resp, dict):
            resp = {"text": str(resp or ""), "plots": [], "data": {}, "thinking": []}
        usage = (
            self.llm.usage_delta(usage_before)
            if hasattr(self.llm, "usage_delta")
            else {"requests": 0, "prompt_tokens": 0, "completion_tokens": 0,
                  "total_tokens": 0, "reasoning_tokens": 0,
                  "token_usage_available": False, "latency_seconds": 0.0}
        )
        usage["provider"] = str(getattr(self.config.llm, "provider", "unknown"))
        usage["model"] = str(getattr(self.llm, "model", getattr(self.config.llm, "model", "unknown")))
        usage["elapsed_seconds"] = round(max(0.0, _time.perf_counter() - started), 3)
        resp.setdefault("data", {})["llm_usage"] = usage
        return resp

    def _chat_csv_rag(self, message: str, thinking_steps: list,
                      abort_flag=None, text_queue=None,
                      progress_callback=None) -> dict:
        """Interpret gene/value rows from an uploaded CSV/TSV through RAG.

        Existing values such as log2FC or p-values are preserved as input fields;
        this path does not calculate new markers, DEGs, enrichment, or networks.
        """

        def _check_abort():
            """Raise AbortChat if the user has clicked the abort button."""
            from e2seq.api import AbortChat as _AbortChat
            if abort_flag is not None and abort_flag.is_set():
                raise _AbortChat("User requested abort")

        import json
        import re as _re_ar

        uns = self.adata.uns
        group_col  = uns.get("e2sc_group_col", "group")
        gene_col   = uns.get("e2sc_gene_col", "name")
        expr_col   = uns.get("e2sc_expr_col", "log2FC")
        expr_type  = uns.get("e2sc_expr_type", "log2FC")
        sig_col    = uns.get("e2sc_sig_col", "")
        sig_thresh = uns.get("e2sc_sig_thresh", 0.05)
        # AnnData serializes list-like ``uns`` values as NumPy arrays on
        # reload.  Normalize them before any truth-value check or set/list
        # operation so a reopened CSV-backed chat follows the same path as a
        # freshly configured session.
        def _persisted_list(value):
            if value is None:
                return []
            if isinstance(value, (str, bytes)):
                return [value]
            try:
                return list(value)
            except TypeError:
                return [value]

        groups     = _persisted_list(uns.get("e2sc_groups", []))
        all_genes  = [str(g) for g in _persisted_list(uns.get("e2sc_all_genes", [])) if str(g).strip()]
        gene_intersection = normalize_gene_list(uns.get("e2sc_gene_intersection", []))
        intersection_keys = {gene_key(gene) for gene in gene_intersection}
        if intersection_keys:
            all_genes = [gene for gene in all_genes if gene_key(gene) in intersection_keys]
        enabled_apis = set(uns.get("e2sc_enabled_apis", DEFAULT_ANSWER_APIS))
        enabled_dbs  = set(uns.get("e2sc_enabled_dbs", DEFAULT_ANSWER_DBS))
        # Large uploaded result tables follow a strict first-question
        # contract: the question must not decide which sources are built.
        # The complete selected cohort is sent to every enabled API/database;
        # only synthesis and question-time literature selection remain
        # question-led.  Requiring the full source set on later turns is
        # inexpensive when the durable snapshot is complete and repairs an
        # older partial snapshot when necessary.
        _full_csv_rag_contract = (
            str(uns.get("e2sc_data_mode", "")).lower() == "csv"
            and len(all_genes) > 30
        )

        # Load filtered CSV records
        import pandas as pd
        records_json = uns.get("e2sc_csv_records", "[]")
        df = pd.read_json(StringIO(records_json), orient="records")
        if intersection_keys and gene_col in df.columns:
            df = df[df[gene_col].astype(str).map(gene_key).isin(intersection_keys)].copy()

        # --- Step 1: Build GeneContext from CSV ---
        # Per-group genes by |expr| — no cap, include ALL genes
        # Keep effect and statistical columns together so the model can
        # interpret HR/log2FC alongside p-value/FDR and direction.
        def _csv_row_summary(row):
            gene = str(row[gene_col])
            try:
                effect = float(row[expr_col])
                bits = [f"{gene}({expr_type}={effect:.4g}"]
            except (TypeError, ValueError):
                bits = [f"{gene}({expr_type}={row[expr_col]}"]
            for key, label in (("log2FoldChange", "log2FC"), ("HR", "HR"),
                               ("coef", "coef"), ("pvalue", "p"), ("padj", "FDR"),
                               ("direction", "direction"), ("input_group", "input group"),
                               ("n", "n")):
                if key == expr_col or key not in row.index:
                    continue
                value = row[key]
                if pd.isna(value):
                    continue
                if isinstance(value, (int, float)):
                    bits.append(f"{label}={value:.4g}")
                else:
                    bits.append(f"{label}={value}")
            return ", ".join(bits) + ")"

        grp_summary = {}   # {group: [(gene, effect, p/FDR, ...), ...]}
        grp_all_genes = {} # {group: set of genes}
        for grp in groups:
            sub = df[df[group_col].astype(str) == str(grp)].copy()
            sub = sub.sort_values(expr_col, key=abs, ascending=False)
            # Keep a compact per-group preview for LLM readability; retrieval
            # still receives every selected row/gene below.
            grp_summary[grp] = [_csv_row_summary(row) for _, row in sub.head(50).iterrows()]
            grp_all_genes[grp] = set(sub[gene_col].astype(str).tolist())

        # Sig filter summary per group
        sig_note = ""
        if sig_col:
            sig_note = f" (filtered: {sig_col} ≤ {sig_thresh})"

        grp_str = "; ".join(
            "{}: [{}]".format(g, ", ".join(grp_summary.get(g, [])))
            for g in groups
        )

        # Union of ALL genes across all groups — no cap, from all_dataset_genes
        top_ranked_genes = all_genes  # already the full unique gene set from filtered CSV

        gctx = (
            "{desc_line}"
            "Data type: CSV differential expression / expression table{sig_note}\n"
            "Expression metric: {expr_type} (column: {expr_col})\n"
            "Groups ({n_gr}): {grp_names}\n"
            "Total genes in dataset: {n_genes}\n"
            "Compact per-group preview (ranked by |{expr_type}| for readability; all rows remain available for retrieval):\n  {grp_str}\n"
            "All selected genes are sent to per-gene retrieval ({n_top} total); compact name preview: {top}\n"
            "IMPORTANT: All values are actual {expr_type} from the uploaded table.\n"
            "Genes not present in a group have no entry in that group's comparison."
        ).format(
            desc_line=("Dataset description (provided by user): {}\n".format(uns.get("e2sc_dataset_description", "")) if uns.get("e2sc_dataset_description", "") else ""),
            sig_note=sig_note,
            expr_type=expr_type,
            expr_col=expr_col,
            n_gr=len(groups),
            grp_names=", ".join(groups),
            n_genes=len(all_genes),
            grp_str=grp_str,
            n_top=len(top_ranked_genes),
            top=", ".join(top_ranked_genes[:100]),  # 展示更多基因给LLM
        )
        thinking_steps.append({"step": "GeneContext", "content": "{} groups, {} genes{}".format(
            len(groups), len(all_genes), sig_note)})

        # --- Step 2: AgentPlan ---
        all_dataset_genes = all_genes
        _all_apis = sorted(enabled_apis)
        _all_dbs  = sorted(enabled_dbs)
        planning_prompt = (
            "You interpret gene/value rows from a SPECIFIC uploaded dataset.\n"
            "User question: {q}\n\n"
            "=== DATA FROM THIS DATASET ===\n"
            "{ctx}\n"
            "=== END OF DATA ===\n\n"
            "=== AVAILABLE DATA SOURCES ===\n"
            "Online APIs (select based on the question and your own judgment):\n"
            "  {apis}\n"
            "Local databases (select based on the question and your own judgment):\n"
            "  {dbs}\n"
            "API descriptions:\n"
            "  uniprot     : Protein function, domains, subcellular location, PTMs, disease associations. USE FOR: protein biology.\n"
            "  mygene      : Gene summary, aliases, Entrez/Ensembl IDs, GO terms, KEGG/Reactome pathways. USE FOR: gene annotation.\n"
            "  quickgo     : Detailed GO annotations with evidence codes (biological process/molecular function/cellular component). USE FOR: functional classification.\n"
            "  ensembl     : Genomic coordinates, biotype (protein-coding/lncRNA/etc), exon structure. USE FOR: genomics context.\n"
            "  chembl      : Approved/investigational drugs, drug-target binding affinities, clinical phases, mechanism of action. USE FOR: drug targets, therapeutics.\n"
            "  opentargets : Gene-disease association scores (GWAS+somatic+expression+literature integrated). USE FOR: disease relevance, target prioritisation.\n"
            "  clinvar     : Pathogenic/benign variant classifications, disease associations, inheritance. USE FOR: clinical variant significance.\n"
            "  civic       : Clinical evidence for cancer variants, therapy response/resistance, diagnostic significance. USE FOR: cancer driver genes.\n"
            "  gwas        : GWAS Catalog — trait/disease SNP associations with p-values. USE FOR: genetic risk loci.\n"
            "  reactome    : Curated pathway membership and hierarchy. USE FOR: external pathway annotation only.\n"
            "  gtex        : GTEx Portal v2 median RNA expression by tissue. USE FOR: tissue expression atlas.\n"
            "  hpa         : Human Protein Atlas RNA/protein class and subcellular annotations. USE FOR: tissue/protein context.\n"
            "  alliance    : Alliance maintained cross-species gene search and orthology context. USE FOR: model-organism evidence.\n"
            "  cbioportal  : Public cBioPortal gene catalog and cancer genomics identifiers. USE FOR: cancer cohort context.\n"
            "  omnipath    : OmniPath signalling and regulatory interactions. USE FOR: directed mechanism hypotheses.\n"
            "  intact      : IntAct/PSICQUIC PSI-MITAB molecular interaction evidence. USE FOR: physical interaction evidence.\n"
            "  pubmed      : PubMed literature — use when the question needs primary research or clinical evidence.\n"
            "  europepmc   : Europe PMC — use when the question needs broader literature or preprints.\n"
            "  string      : STRING known interaction evidence (local). USE FOR: external annotation only.\n"
            "  hmdb        : Human Metabolome Database — metabolite-gene associations, biochemical pathways (local). USE FOR: metabolomics.\n"
            "  trrust      : Transcription factor - target gene regulatory relationships activation/repression (local). USE FOR: transcriptional regulation.\n"
            "  gutmgene    : Gut microbiome-gene associations — microorganism-gene edges in gut disease context (local). USE FOR: microbiome/gut disease.\n"
            "Choose only sources that help answer the user's question; do not add a source merely because it is available.\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. Select only genes present in the uploaded rows, preserving their supplied {expr_type} values.\n"
            "2. Mention the actual group names ({grp_names}) in your focus sentence.\n"
            "3. Select APIs and databases based solely on what the user question requires and your own judgment.\n"
            "4. Do not invent a computation. If the requested information is already present, retrieve and synthesize it; otherwise make the limitation explicit.\n"
            "5. Output STRICT JSON only - no markdown, no explanation.\n"
            "Output exactly this JSON structure:\n"
            "{{\n"
            "  \"genes_to_retrieve\": [gene symbols with highest |{expr_type}| — as many as needed],\n"
            "  \"apis_to_use\": [subset of {apis} — choose based on the question and your own judgment],\n"
            "  \"dbs_to_use\": [subset of {dbs} — choose based on the question and your own judgment],\n"
            "  \"pubmed_keywords\": [keyword strings combining gene names + group names],\n"
            "  \"europepmc_keywords\": [keyword strings, different angle from pubmed],\n"
            "  \"literature_search\": true or false (set false only when existing evidence is sufficient),\n"
            "  \"focus\": \"one sentence about the groups and representative genes\"\n"
            "}}\n"
        ).format(q=message, ctx=gctx, expr_type=expr_type, grp_names=", ".join(groups),
                 apis=_all_apis, dbs=_all_dbs)
        try:
            plan_raw = "" if _full_csv_rag_contract else self.llm.chat(
                [{"role": "user", "content": planning_prompt}]
            )
            _check_abort()  # abort check after planning LLM call
            _jm = _re_ar.search(r"\{[\s\S]*\}", plan_raw)
            plan = json.loads(_jm.group()) if _jm else {}
            _gene_set = set(all_dataset_genes)
            to_ret = [g for g in plan.get("genes_to_retrieve", []) if g in _gene_set]  # no cap
            # Union with all filtered genes so every gene in the dataset gets retrieved
            _seen = set(to_ret)
            to_ret.extend([g for g in all_dataset_genes if g not in _seen])
            # Agent narrows retrieval to its planned sources inside the
            # user's enabled-source allow-list.
            _csv_agent_apis, _csv_agent_dbs = self._select_agent_sources(
                plan, enabled_apis, enabled_dbs
            )
            kws_pm = plan.get("pubmed_keywords", [])
            kws_em = plan.get("europepmc_keywords", [])
            focus  = plan.get("focus", message[:80])
        except Exception as _pe:
            logger.warning("[CsvRAG] Planning fallback: {}".format(_pe))
            plan = {}
            to_ret = top_ranked_genes[:]
            _csv_agent_apis = enabled_apis
            _csv_agent_dbs  = enabled_dbs
            kws_pm = [message[:60]]
            kws_em = []
            focus  = message[:80]
        # Literature is attempted for every question by default.  The planner
        # may explicitly mark existing evidence as sufficient; only that
        # explicit boolean false is allowed to skip PubMed/Europe PMC.
        literature_search_requested = not (
            isinstance(plan, dict) and plan.get("literature_search") is False
        )
        if not literature_search_requested:
            _csv_agent_apis = set(_csv_agent_apis) - {"pubmed", "europepmc"}
        else:
            # Literature is a required question-time evidence check by
            # default.  A planner may select additional sources, but it must
            # not silently remove PubMed/Europe PMC when the user has enabled
            # them and the planner did not explicitly declare the evidence
            # sufficient.
            _csv_agent_apis.update({"pubmed", "europepmc"} & set(enabled_apis))
        if not to_ret:
            to_ret = top_ranked_genes[:]
        # Per-gene records are reused across turns, but literature is
        # question-specific and must be searched again for every question.
        # A deterministic fallback query keeps this contract even when the
        # planner returns no keywords; it does not cap the gene cohort.
        _lit_seed_genes = list(dict.fromkeys(str(g) for g in to_ret if str(g).strip()))[:8]
        _lit_context = str(uns.get("e2sc_dataset_description") or focus or "").strip()
        _lit_query = " ".join(
            part for part in (message.strip()[:180], _lit_context[:120], " ".join(_lit_seed_genes))
            if part
        )[:420] or "expression profile"
        kws_pm = [str(k).strip() for k in (kws_pm or []) if str(k).strip()] or [_lit_query]
        kws_em = [str(k).strip() for k in (kws_em or []) if str(k).strip()] or [f"{_lit_query} omics"]
        if literature_search_requested:
            # Keep planner-provided keywords and add question-specific
            # fallbacks so a generic/short planner response cannot silently
            # turn literature retrieval into a no-op.
            _pubmed_fallbacks = [
                _lit_query,
                f"{_lit_query} cancer mechanism",
                f"{_lit_query} clinical evidence",
            ]
            _europepmc_fallbacks = [
                f"{_lit_query} microbiome metabolism",
                f"{_lit_query} pathway mechanism",
                f"{_lit_query} cancer omics",
            ]
            kws_pm = list(dict.fromkeys(kws_pm + _pubmed_fallbacks))
            kws_em = list(dict.fromkeys(kws_em + _europepmc_fallbacks))
        if _full_csv_rag_contract:
            _csv_agent_apis = set(enabled_apis)
            _csv_agent_dbs = set(enabled_dbs)
            thinking_steps.append({
                "step": "AgentPlan",
                "content": "First-question full RAG contract: all selected expression items and all enabled sources are required before synthesis",
            })
        thinking_steps.append({"step": "AgentPlan", "content": "Focus: {} | {} genes | APIs: {} | kws: {}".format(
            focus, len(to_ret), sorted(_csv_agent_apis), kws_pm[:3])})

        # --- Step 3: RAG Retrieve (reuse existing pipeline) ---
        self.state_manager.set_state(AgentState.RETRIEVING)
        knowledge, missing_genes, reused_complete = self._get_persisted_rag_knowledge(
            to_ret, required_apis=_csv_agent_apis, required_dbs=_csv_agent_dbs
        )
        if knowledge is None:
            knowledge = self._build_group_knowledge_parallel(
                "csv/{}".format(focus[:30]), to_ret,
                context_hint=focus, enabled_apis=_csv_agent_apis, enabled_dbs=_csv_agent_dbs,
                progress_callback=progress_callback, abort_flag=abort_flag)
            self._rag_needs_vector_rebuild = True
        elif missing_genes:
            fetched = self._build_group_knowledge_parallel(
                "csv/{}/new".format(focus[:24]), missing_genes,
                context_hint=focus, enabled_apis=_csv_agent_apis, enabled_dbs=_csv_agent_dbs,
                progress_callback=progress_callback, abort_flag=abort_flag)
            self._merge_rag_knowledge(knowledge, fetched)
            self._rag_needs_vector_rebuild = True
        else:
            thinking_steps.append({"step": "RAGReuse", "content": "Reused per-gene source records; this question will run fresh literature searches"})
        # The persisted source records are complete for this question. Keep
        # the deterministic literature fallback and reserve the remote LLM
        # call for the final synthesis instead of repeating two triage calls.
        if reused_complete:
            knowledge.setdefault("_source_stats", {})["skip_llm_literature_selection"] = True
        _check_abort()  # abort check after knowledge retrieval

        # Literature augmentation — no keyword count caps
        try:
            import requests as _kw_req
            def _literature_key(record):
                if not isinstance(record, dict):
                    return ""
                return str(record.get("pmid") or record.get("id") or "").strip()

            _sp  = {_literature_key(a) for a in knowledge.get("pubmed", []) if _literature_key(a)}
            _sep = {_literature_key(a) for a in knowledge.get("europepmc", []) if _literature_key(a)}
            _literature_queries = {"pubmed": 0, "europepmc": 0}
            _literature_query_details = {"pubmed": [], "europepmc": []}
            _literature_errors = {"pubmed": [], "europepmc": []}
            _pubmed_before = len(knowledge.get("pubmed", []) or [])
            _europepmc_before = len(knowledge.get("europepmc", []) or [])
            if progress_callback and ("pubmed" in _csv_agent_apis or "europepmc" in _csv_agent_apis):
                progress_callback("[进度] 本次提问：查询 PubMed 与 EuropePMC")
            if "pubmed" in _csv_agent_apis:
                pm_client = self.api_clients.get("pubmed")
                if pm_client:
                    for kw in kws_pm:  # no count cap
                        try:
                            _kw = str(kw).strip()
                            if not _kw:
                                continue
                            _literature_queries["pubmed"] += 1
                            _literature_query_details["pubmed"].append(_kw)
                            pm = pm_client.search_and_get_details(_kw, max_results=10)
                            if isinstance(pm, dict) and (
                                str(pm.get("status", "")).lower() in {"error", "unavailable"}
                                or pm.get("error")
                            ):
                                _literature_errors["pubmed"].append(
                                    str(pm.get("error") or pm.get("status") or "PubMed query failed")[:240]
                                )
                                continue
                            for art in pm.get("articles", []):
                                pmid = _literature_key(art)
                                if pmid and pmid not in _sp:
                                    _sp.add(pmid); knowledge.setdefault("pubmed", []).append(art)
                        except Exception as e:
                            _literature_errors["pubmed"].append(str(e)[:240])
                            logger.warning(f"PubMed search failed: {e}")
                else:
                    _literature_query_details["pubmed"].extend(
                        str(kw).strip() for kw in kws_pm if str(kw).strip()
                    )
                    _literature_queries["pubmed"] = len(_literature_query_details["pubmed"])
                    _literature_errors["pubmed"].append("PubMed client is not configured")
            if "europepmc" in _csv_agent_apis:
                for kw in kws_em:  # no count cap
                    try:
                        _kw = str(kw).strip()
                        if not _kw:
                            continue
                        _literature_queries["europepmc"] += 1
                        _literature_query_details["europepmc"].append(_kw)
                        r = _kw_req.get("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                            params={"query": _kw, "resultType": "lite", "pageSize": 10, "format": "json"}, timeout=8)
                        if not r.ok:
                            _literature_errors["europepmc"].append(
                                f"HTTP {r.status_code}: Europe PMC query failed"
                            )
                            continue
                        for rec in r.json().get("resultList", {}).get("result", []):
                            pmid = str(rec.get("pmid") or rec.get("id") or "").strip()
                            if pmid and pmid not in _sep:
                                _sep.add(pmid)
                                knowledge.setdefault("europepmc", []).append({
                                    "pmid": pmid, "title": rec.get("title", ""),
                                    "abstract": rec.get("abstractText", ""),
                                    "journal": rec.get("journalTitle", ""),
                                    "year": rec.get("pubYear", "")})
                    except Exception as e:
                        _literature_errors["europepmc"].append(str(e)[:240])
                        logger.warning(f"EuropePMC search failed: {e}")
            _stats = knowledge.setdefault("_source_stats", {})
            _stats["literature_queries"] = _literature_queries
            _stats["literature_query_details"] = _literature_query_details
            _stats["literature_errors"] = {
                source: list(dict.fromkeys(errors))[:3]
                for source, errors in _literature_errors.items() if errors
            }
            _stats["literature_search_attempted"] = bool(
                _literature_query_details["pubmed"] or _literature_query_details["europepmc"]
            )
            _stats["literature_search_question"] = message[:500]
            _stats["literature_search_decision"] = (
                "explicitly_skipped_existing_evidence_sufficient"
                if not literature_search_requested else "attempted"
            )
            _stats["literature_new_records"] = {
                "pubmed": max(0, len(knowledge.get("pubmed", []) or []) - _pubmed_before),
                "europepmc": max(0, len(knowledge.get("europepmc", []) or []) - _europepmc_before),
            }
        except Exception as e:
            logger.warning(f"CSV literature augmentation failed: {e}")

        _check_abort()  # abort check after literature augmentation

        # Keep the current question's retrieval target and the persisted
        # source audit aligned.  Older snapshots stored child-worker totals
        # (one gene) and later answers could therefore display 498/1 even
        # though the merged RAG contained hundreds of genes.
        knowledge["_selected_gene_count"] = int(
            knowledge.get("_selected_gene_count") or len(all_genes) or len(to_ret)
        )
        knowledge["_rag_core_gene_count"] = len(to_ret)
        knowledge["_rag_queried_gene_count"] = len(knowledge.get("genes", {}) or {})
        try:
            from e2seq.agent.synthesizer import _normalise_source_stats
            _normalise_source_stats(knowledge)
        except Exception as _stats_error:
            logger.warning("[CsvRAG] Source coverage normalisation failed: %s", _stats_error)

        # Count retrieved genes, not top-level knowledge fields.  The latter
        # made a 500-gene RAG run appear as only five retrieved genes.
        n_ret = len(knowledge.get("genes", {}) or {})
        n_arts = len(knowledge.get("pubmed", [])) + len(knowledge.get("europepmc", []))
        thinking_steps.append({"step": "RAGRetrieve", "content": "{} genes retrieved, {} articles".format(n_ret, n_arts)})

        # --- Step 3b: Build vector store from retrieved knowledge ---
        # Only rebuild if not already built for this session (reuse across questions)
        try:
            _force_vector_rebuild = bool(getattr(self, "_rag_needs_vector_rebuild", False))
            if _force_vector_rebuild:
                # Newly fetched genes/source records are not in the persisted
                # collection, so do not reattach it before rebuilding.
                self._vector_store = None
            else:
                self._restore_persisted_vector_store()
            if self._vector_store is None or self._vector_store.count() == 0:
                from e2seq.data.vector_store import reset_vector_store
                _vs = reset_vector_store(self._session_id, llm=self.llm)
                n_vs_docs = _vs.reset_and_build(knowledge)
                self._vector_store = _vs
                knowledge.setdefault("_source_stats", {})["vector_chunks"] = n_vs_docs
                knowledge.setdefault("_source_stats", {})["vector_retrieval_mode"] = "hybrid dense + BM25"
                thinking_steps.append({"step": "VectorStoreBuild",
                    "content": "{} docs embedded (session={})".format(n_vs_docs, self._session_id)})
                logger.info("[CsvRAG] Vector store built: {} docs".format(n_vs_docs))
                if progress_callback:
                    progress_callback(f"[进度] [向量库] 构建完成，{n_vs_docs} 文档已嵌入")
            else:
                knowledge.setdefault("_source_stats", {})["vector_chunks"] = self._vector_store.count()
                knowledge.setdefault("_source_stats", {})["vector_retrieval_mode"] = "hybrid dense + BM25 (reused)"
                # Update with new knowledge (add without resetting)
                thinking_steps.append({"step": "VectorStoreBuild",
                    "content": "Reusing existing store: {} docs".format(self._vector_store.count())})
                logger.info("[CsvRAG] Reusing vector store: {} docs".format(self._vector_store.count()))
                if progress_callback:
                    progress_callback(f"[进度] [向量库] 复用现有向量库，{self._vector_store.count()} 文档")
            self._rag_needs_vector_rebuild = False
        except Exception as _vse:
            logger.warning("[CsvRAG] Vector store build failed: {}".format(_vse))
        _check_abort()  # abort check after vector store build

        # --- Step 3c: RAG retrieval from vector store ---
        if self._vector_store is not None and self._vector_store.count() > 0:
            try:
                # Use focus (agent-generated semantic description) as RAG query
                # when original message is too short/vague to match knowledge chunks
                _rag_query = focus if (len(message.strip()) < 20 or any(
                    kw in message for kw in ["综合", "解读", "全面", "整体", "comprehensive", "overall"]
                )) else message
                _rag_top_k = min(50, max(20, self._vector_store.count() // 10))
                knowledge.setdefault("_source_stats", {})["vector_retrieval_top_k"] = _rag_top_k
                _rag_ctx = self._vector_store.retrieve_context(_rag_query, n_results=_rag_top_k)
                if _rag_ctx:
                    knowledge["rag_context"] = _rag_ctx
                    thinking_steps.append({"step": "VectorRAG",
                        "content": "{} docs; ranked context chunks for: {}".format(
                            self._vector_store.count(), _rag_query[:60])})
            except Exception as _re:
                logger.warning("[CsvRAG] RAG retrieval failed: {}".format(_re))

        self._persist_rag_knowledge(knowledge)

        # --- Step 4: Synthesise ---
        input_results = {
            "gene_context": gctx,
            "groups": groups,
            "expr_type": expr_type,
            "n_genes": len(all_genes),
            "interpretation_focus": focus,
            "interpretation_only": True,
            "question_time_enrichment_summary": uns.get("e2sc_bulk_result_summary", ""),
            "question_time_enrichment": (
                (knowledge.get("_source_stats") or {}).get("question_time_enrichment")
            ),
        }
        # Keep only this session's conversation history. Do not mix knowledge
        # from another uploaded dataset into the current interpretation.
        history = self.memory.get_conversation_history_for_llm(max_messages=20, max_total_chars=8000)
        self.state_manager.set_state(AgentState.SYNTHESIZING)
        logger.info("[CsvRAG] Starting synthesizer.synthesize... text_queue={}".format(text_queue is not None))
        if progress_callback:
            progress_callback("[进度] 正在根据输入基因数值和检索证据生成解读...")
        ok, resp, err = self.error_recovery.execute_with_retry(
            self.synthesizer.synthesize,
            message, input_results, knowledge, history,
            error_context="synthesize_csv_rag", is_comprehensive=False,
            text_queue=text_queue,
            progress_callback=progress_callback,
            abort_flag=abort_flag,
        )
        if not ok:
            if err and "abort" in err.lower():
                from e2seq.api.server import AbortChat as _AbortChat
                raise _AbortChat(err)
            # Retrieval is still a valid result when the answer gateway fails.
            # Preserve the structured RAG evidence and return a deterministic
            # digest instead of replacing it with an empty synthesis error.
            try:
                from e2seq.agent.synthesizer import _format_rag_source_audit
                fallback_digest = self.synthesizer._format_knowledge(knowledge, question=message)
                fallback_audit = _format_rag_source_audit(knowledge, question=message)
                _provider = str(getattr(self.llm, "provider", "") or "").strip()
                if not _provider:
                    _provider = {
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
                _model = str(getattr(self.llm, "model", "unknown") or "unknown")
                resp = {
                    "text": f"回答模型 API：{_provider} / {_model}。\n\n"
                    "本次大模型综合合成暂时不可用，以下返回已完成的 RAG 证据与来源审计。\n\n"
                    + fallback_digest + "\n\n" + fallback_audit,
                    "plots": [],
                    "data": {
                        "knowledge": knowledge,
                        "source_audit": fallback_audit,
                        "retrieval_status": {
                            "genes_retrieved": len(knowledge.get("genes", {}) or {}),
                            "has_sufficient_knowledge": bool(knowledge),
                        },
                    },
                }
            except Exception:
                resp = {"text": "Synthesis failed: {}".format(err), "plots": [], "data": {"knowledge": knowledge}}
        if not isinstance(resp, dict):
            resp = {"text": str(resp), "plots": [], "data": {}}
        # Synthesis normalises source coverage and attaches the question-
        # specific literature ranking. Persist that mutated snapshot so a
        # later turn can reuse the same dataset without re-uploading or
        # losing the provenance audit.
        try:
            _response_data = resp.get("data") or {}
            _response_knowledge = _response_data.get("knowledge")
            if isinstance(_response_knowledge, dict):
                self._persist_rag_knowledge(_response_knowledge)
        except Exception as _persist_err:
            logger.warning("[CsvRAG] Persisting post-synthesis knowledge failed: {}".format(_persist_err))
        response_text = resp.get("text", "")
        logger.info(f"[CsvRAG] Synthesize OK: response_len={len(response_text)}")
        thinking_steps.append({"step": "Synthesize", "content": "Interpretation generated"})

        self.memory.working_memory.add_message("assistant", response_text)
        self.memory.save_current_session(success=True)
        self.state_manager.set_state(AgentState.COMPLETED)
        resp["thinking"] = thinking_steps
        return resp

    def _chat_no_data(self, message: str, thinking_steps: list) -> dict:
        """Answer ordinary questions freely while refusing fabricated data results."""
        history = self.memory.get_conversation_history()
        messages = [{"role": "system", "content": (
            "You are E2seq, a scientific assistant. Answer the user's actual question directly and follow "
            "their requested language, format, and level of detail. Do not fabricate results for an absent "
            "dataset and do not pretend a computation was performed; if the question needs uploaded data, "
            "say what data or configuration is missing. General biology, bioinformatics, coding, and usage "
            "questions can be answered normally. Do not impose a fixed report template or an arbitrary length."
        )}]
        for h in history[-8:]:
            messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": message})
        try:
            response_text = self.llm.chat(messages)
        except Exception as e:
            response_text = "回答生成失败: {}".format(e)
        thinking_steps.append({"step": "ConversationalMode", "content": "No data — guide user to upload"})
        self.memory.working_memory.add_message("assistant", response_text)
        self.memory.save_current_session(success=True)
        return {"text": response_text, "plots": [], "data": {}, "thinking": thinking_steps}
    def _chat_agentic_rag(self, message: str, thinking_steps: list,
                          progress_callback=None, text_queue=None, abort_flag=None) -> dict:
        """Extract uploaded gene/value context, retrieve evidence, and interpret it.

        The default path does not run marker, differential-expression,
        enrichment, clustering, or network/module analysis.

        Args:
            abort_flag: threading.Event; if set, raises AbortChat to stop execution.
        """
        def _check_abort():
            """Raise AbortChat if the user has clicked the abort button."""
            from e2seq.api import AbortChat as _AbortChat
            if abort_flag is not None and abort_flag.is_set():
                raise _AbortChat("User requested abort")

        import json
        import re as _re_ar
        import time as _time
        from collections import OrderedDict
        _rag_started = _time.perf_counter()

        # ── CSV mode: data is a pre-filtered differential/expression table ──
        if self.adata.uns.get("e2sc_data_mode") == "csv":
            return self._chat_csv_rag(message, thinking_steps,
                abort_flag=abort_flag, text_queue=text_queue,
                progress_callback=progress_callback)

        # ── Meta-questions about the AI model: answer directly without any RAG ──
        _quick_keywords = [
            "什么模型", "是哪家", "哪个模型", "who are you", "what are you",
            "what model", "which model", "who built", "你的名字", "叫什么",
            "怎么用", "how to use", "how do i", "如何使用", "有什么功能",
            "支持什么", "can you", "could you", "你基于", "你的能力",
        ]
        # The first question after a dataset is loaded must still traverse
        # the complete Agent RAG contract, even when it is short or asks
        # about the model. Later meta-questions may use the lightweight path.
        _history_before_current = self.memory.working_memory.conversation_history[:-1]
        _has_prior_answer = any(
            isinstance(item, dict) and item.get("role") == "assistant"
            for item in _history_before_current
        )
        if _has_prior_answer and any(kw in message for kw in _quick_keywords):
            thinking_steps.append({"step": "MetaMode", "content": "Direct meta-answer without RAG"})
            _provider_info = {
                "openai": ("OpenAI", "gpt-5.4"),
                "anthropic": ("Anthropic", "claude-opus-4-7"),
                "deepseek": ("DeepSeek", "deepseek-chat / deepseek-reasoner"),
                "gemini": ("Google Gemini", "gemini-3.1-pro-preview"),
                "siliconflow": ("SiliconFlow", "deepseek-ai/DeepSeek-V3"),
                "glm": ("Zhipu AI (GLM)", "glm-5.1"),
                "kimi": ("Moonshot AI (Kimi)", "kimi-k2.6"),
                "sdu": ("山东大学 SDU-AI 平台", "SDU-AI/DeepSeek-V4-Flash"),
                "ollama": ("Ollama (本地)", "llama3.2"),
            }
            _p = self.config.llm.provider.lower()
            _m = self.config.llm.model or "default"
            _company, _default_model = _provider_info.get(_p, ("Unknown", _p))
            _response_text = (
                "我是 E2seq（Easy to Chat with Sequencing），一个用于解读表达谱和单细胞测序结果的 AI 助手。\n\n"
                f"**当前配置**:\n"
                f"- 底层模型: {_m}\n"
                f"- 模型提供商: {_company}\n\n"
                f"**我的能力**:\n"
                f"- 读取 CSV/TSV/H5AD 中已有的基因、数值、分组和细胞类型标签\n"
                f"- 将输入基因直接送入 Agent RAG，检索功能、通路、相互作用和文献证据\n"
                f"- 只做基于输入值和外部证据的文字解读，不计算 marker、差异表达、富集或网络模块\n"
                f"- 通过 Web API 流式返回可直接阅读的 Markdown 文字\n"
                f"- 支持后续追问，系统会从缓存中快速回答\n\n"
                f"请上传表达谱或单细胞测序结果开始解读！"
            )
            self.memory.working_memory.add_message("assistant", _response_text)
            self.memory.save_current_session(success=True)
            self.state_manager.set_state(AgentState.COMPLETED)
            return {"text": _response_text, "plots": [], "data": {}, "thinking": thinking_steps}

        ct_col  = self.adata.uns.get("e2sc_celltype_col") or ""
        grp_col = self.adata.uns.get("e2sc_group_col") or ""
        celltype_labels = dict(self.adata.uns.get("e2sc_celltype_labels", {}))
        group_labels    = dict(self.adata.uns.get("e2sc_group_labels", {}))
        # The saved answer policy is an allow-list.  Selecting HumanBase (or
        # any other source) must not implicitly re-enable every API.
        enabled_apis = {
            str(source).lower()
            for source in self.adata.uns.get("e2sc_enabled_apis", DEFAULT_ANSWER_APIS)
        }
        enabled_dbs = set(self.adata.uns.get("e2sc_enabled_dbs", DEFAULT_ANSWER_DBS))
        gene_intersection = normalize_gene_list(self.adata.uns.get("e2sc_gene_intersection", []))
        intersection_keys = {gene_key(gene) for gene in gene_intersection}

        # Step 1: extract gene/value context from the uploaded matrix only.
        # No marker, differential, enrichment, or network computation runs here.
        import numpy as np
        import scipy.sparse as sp
        # User-configurable N — stored during configure-dataset, default 30
        _n_ctx = int(self.adata.uns.get("e2sc_n_top_genes", 30))
        logger.info(f"[AgenticRAG] START. message={message[:60]!r}, data_mode={self.adata.uns.get('e2sc_data_mode','h5ad')}, n_top_genes={_n_ctx}, apis={sorted(enabled_apis)}, dbs={sorted(enabled_dbs)}, text_queue={text_queue is not None}")
        # Keep the planner, retrieval, and synthesis candidate set aligned with
        # the user's requested gene cap.  Expanding this to 200 here makes a
        # "只分析 N 个基因" request silently query many more genes and can turn
        # a small validation run into a long, unrelated live-API crawl.
        _n_ctx_planner = max(1, _n_ctx)
        ct_matrix = {}   # {display_label: {gene: input mean value}}
        grp_matrix = {}  # {display_label: {gene: input mean value}}
        if self.scanpy_tools:
            if ct_col:
                _m = self.scanpy_tools.get_top_genes_matrix(n_top_genes=_n_ctx_planner, celltype_col=ct_col)
                _m = apply_gene_intersection(_m, gene_intersection)
                ct_matrix = {
                    celltype_labels.get(k, k): dict(v)
                    for k, v in _m.get("matrix", {}).items()
                }
                self.memory.working_memory.update_context("gene_matrix", _m)
            if grp_col:
                _g = self.scanpy_tools.get_top_genes_by_group(group_col=grp_col, n_top_genes=_n_ctx_planner)
                _g = apply_gene_intersection(_g, gene_intersection)
                grp_matrix = {
                    group_labels.get(k, k): dict(v)
                    for k, v in _g.get("matrix", {}).items()
                }
                self.memory.working_memory.update_context("group_matrix", _g)

        # Convert the uploaded cells-by-genes matrix to gene/value pairs. This
        # deterministic mean is input summarisation, not statistical analysis.
        all_dataset_genes = list(self.adata.var_names)
        candidate_genes = (
            [gene for gene in all_dataset_genes if gene_key(gene) in intersection_keys]
            if intersection_keys else all_dataset_genes
        )
        X = self.adata.X
        if sp.issparse(X):
            overall_vector = np.asarray(X.mean(axis=0)).ravel()
        else:
            overall_vector = np.asarray(X).mean(axis=0)
        overall_gene_values = dict(sorted(
            ((str(gene), float(overall_vector[i]))
             for i, gene in enumerate(all_dataset_genes)
             if not intersection_keys or gene_key(gene) in intersection_keys),
            key=lambda item: abs(item[1]),
            reverse=True,
        )[:_n_ctx_planner])

        top_ranked_genes = list(OrderedDict.fromkeys(
            gene
            for values in list(ct_matrix.values()) + list(grp_matrix.values())
            for gene in values.keys()
        ))
        # The matrix preview is intentionally per cell type/group, but the
        # user's N control is the cohort sent to Agent RAG.  Keep that RAG
        # cohort globally bounded so “Top 50” means 50 queried genes rather
        # than 50 multiplied by every displayed category.
        top_ranked_genes = list(OrderedDict.fromkeys(
            list(overall_gene_values.keys()) + top_ranked_genes
        ))[:_n_ctx_planner]

        # Fallback to the uploaded gene order if the matrix has no usable values.
        if not top_ranked_genes:
            top_ranked_genes = list(candidate_genes[:_n_ctx_planner])
            logger.info(f"[AgenticRAG] No ct/grp cols — using {len(top_ranked_genes)} fallback genes from var_names")

        def _format_value_map(values):
            return ",".join(
                "{}(value={:.4g})".format(gene, float(value))
                for gene, value in list(values.items())[:_n_ctx_planner]
            )

        overall_summary = _format_value_map(overall_gene_values)
        grp_sum = "; ".join(
            "{}:[{}]".format(label, _format_value_map(values))
            for label, values in grp_matrix.items()
        ) or "(no group column configured)"
        ct_sum = "; ".join(
            "{}:[{}]".format(label, _format_value_map(values))
            for label, values in ct_matrix.items()
        ) or "(no cell-type column configured)"

        gctx = (
            "{desc_line}"
            "Dataset: {n_obs} cells, {n_vars} total genes\n"
            "Overall input gene values (deterministic mean across uploaded rows/cells): {overall}\n"
            "Input values by user-provided group ({n_gr}): {gr}\n"
            "Input values by user-provided cell type ({n_ct}): {ct}\n"
            "User-selected candidate genes sent to retrieval ({n_top}); compact name preview: {top}\n"
            "IMPORTANT: These values only summarise the uploaded matrix. No marker detection, "
            "differential expression, fold-change, p-value, enrichment, clustering, network, "
            "or module analysis was performed. RAG may retrieve external annotations only."
        ).format(
            desc_line=("Dataset description (provided by user): {}\n".format(self.adata.uns.get("e2sc_dataset_description", "")) if self.adata.uns.get("e2sc_dataset_description", "") else ""),
            n_obs=self.adata.n_obs, n_vars=self.adata.n_vars,
            n_gr=len(grp_matrix), gr=grp_sum,
            n_ct=len(ct_matrix), ct=ct_sum,
            n_top=len(top_ranked_genes),
            top=", ".join(top_ranked_genes[:300]),
            overall=overall_summary,
        )
        thinking_steps.append({"step":"InputGeneValues","content":"{} cell types, {} groups, {} input genes, {} total; no derived differential or enrichment analysis".format(
            len(ct_matrix), len(grp_matrix), len(top_ranked_genes), len(all_dataset_genes))})

        # Step 2: Agent planning — data-anchored, question-driven, API-aware
        _all_apis = sorted(enabled_apis)
        _all_dbs  = sorted(enabled_dbs)
        planning_prompt = (
            "You interpret gene/value pairs from a SPECIFIC uploaded expression-profile or single-cell dataset.\n"
            "User question: {q}\n\n"
            "=== ACTUAL DATA FROM THIS DATASET ===\n"
            "{ctx}\n"
            "=== END OF DATA ===\n\n"
            "=== AVAILABLE DATA SOURCES (select based on question type) ===\n"
            "ONLINE APIs\n"
            "  uniprot     : Protein function, domains, subcellular location, PTMs, disease associations. USE FOR: protein biology.\n"
            "  mygene      : Gene summary, aliases, Entrez/Ensembl IDs, GO terms, KEGG/Reactome pathways. USE FOR: gene annotation.\n"
            "  quickgo     : Detailed GO annotations with evidence codes (biological process/molecular function/cellular component). USE FOR: functional classification.\n"
            "  ensembl     : Genomic coordinates, biotype (protein-coding/lncRNA/etc), exon structure. USE FOR: genomics context.\n"
            "  chembl      : Approved/investigational drugs, drug-target binding affinities, clinical phases, mechanism of action. USE FOR: drug targets, therapeutics.\n"
            "  opentargets : Gene-disease association scores (GWAS+somatic+expression+literature integrated). USE FOR: disease relevance, target prioritisation.\n"
            "  clinvar     : Pathogenic/benign variant classifications, disease associations, inheritance. USE FOR: clinical variant significance.\n"
            "  civic       : Clinical evidence for cancer variants, therapy response/resistance, diagnostic significance. USE FOR: cancer driver genes.\n"
            "  gwas        : GWAS Catalog — trait/disease SNP associations with p-values. USE FOR: genetic risk loci.\n"
            "  reactome    : Curated pathway membership and hierarchy. USE FOR: external pathway annotation only.\n"
            "  gtex        : GTEx Portal v2 median RNA expression by tissue. USE FOR: tissue expression atlas.\n"
            "  hpa         : Human Protein Atlas RNA/protein class and subcellular annotations. USE FOR: tissue/protein context.\n"
            "  alliance    : Alliance maintained cross-species gene search and orthology context. USE FOR: model-organism evidence.\n"
            "  cbioportal  : Public cBioPortal gene catalog and cancer genomics identifiers. USE FOR: cancer cohort context.\n"
            "  omnipath    : OmniPath signalling and regulatory interactions. USE FOR: directed mechanism hypotheses.\n"
            "  intact      : IntAct/PSICQUIC PSI-MITAB molecular interaction evidence. USE FOR: physical interaction evidence.\n"
            "  pubmed      : PubMed literature — use when the question needs primary research or clinical evidence.\n"
            "  europepmc   : Europe PMC — use when the question needs broader literature or preprints.\n"
            "LOCAL DATABASES\n"
            "  string      : STRING known interaction evidence. USE FOR: external annotation only.\n"
            "  hmdb        : Human Metabolome Database — metabolite-gene associations, biochemical pathways. USE FOR: metabolomics questions.\n"
            "  trrust      : Transcription factor - target gene regulatory relationships (activation/repression). USE FOR: transcriptional regulation.\n"
            "  gutmgene    : Gut microbiome-gene associations — microorganism-gene edges in gut disease context. USE FOR: microbiome/gut disease.\n"
            "=== END OF SOURCES ===\n\n"
            "Choose only sources that help answer the user's question; do not add a source merely because it is available.\n\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. Use only gene symbols and numeric values present in the input context above.\n"
            "2. Preserve the actual group and cell-type labels exactly when they exist.\n"
            "3. Select genes for RAG retrieval from the candidate input genes only.\n"
            "4. Do not invent a computation. If the requested information is already present, retrieve and synthesize it; otherwise make the limitation explicit.\n"
            "5. Retrieved pathway or interaction records are external annotations, never computed dataset results.\n"
            "6. Select APIs/databases only to interpret the user's question, then output STRICT JSON.\n"
            "JSON format:\n"
            "{{\n"
            "  \"genes_to_retrieve\": [gene symbols selected only from the uploaded input context],\n"
            "  \"apis_to_use\": [subset of {apis} — choose based on the question and your own judgment],\n"
            "  \"dbs_to_use\": [subset of {dbs} — choose based on the question and your own judgment],\n"
            "  \"pubmed_keywords\": [keyword strings combining gene names + actual disease group names + cell types],\n"
            "  \"europepmc_keywords\": [keyword strings, different angle from pubmed],\n"
            "  \"focus\": \"one sentence mentioning the specific disease groups and cell types in this dataset\"\n"
            "}}"
        ).format(q=message, ctx=gctx, apis=_all_apis, dbs=_all_dbs, _n_ctx_planner=_n_ctx_planner)
        # Constrain planner to top_ranked_genes only (user's filtered/prioritized gene range)
        _gene_set = set(top_ranked_genes)
        _is_precomputed_bulk = (
            str(self.adata.uns.get("e2sc_data_mode", "")).lower() == "csv"
            and int(self.adata.uns.get("e2sc_bulk_selected_count") or 0) > 30
        )
        if _is_precomputed_bulk:
            thinking_steps.append({
                "step": "AgentPlan",
                "content": "Reused persisted bulk RAG plan; skipped planner LLM for the large cohort",
            })
        try:
            # The bulk handoff has already selected and queried this cohort;
            # avoid a second upstream planner request containing hundreds of
            # gene names.  The empty plan intentionally falls through to the
            # deterministic full candidate list below.
            plan_raw = "" if _is_precomputed_bulk else self.llm.chat([{"role":"user","content":planning_prompt}])
            _check_abort()  # abort check after planning LLM call
            _jm = _re_ar.search(r"\{[\s\S]*\}", plan_raw)
            plan = json.loads(_jm.group()) if _jm else {}
            # The planner may choose APIs, literature angles, and synthesis
            # focus, but it must never reduce the user's selected cohort.
            # Every gene in the current cell-type/group selection therefore
            # enters Agent RAG, even when the planner names only a few
            # representative genes in its JSON.
            _gene_set = set(top_ranked_genes)
            _planned_genes = [g for g in plan.get("genes_to_retrieve", []) if g in _gene_set]
            to_ret = top_ranked_genes[:]
            if len(_planned_genes) != len(to_ret):
                thinking_steps.append({
                    "step": "AgentRAGCoverage",
                    "content": f"Planner named {len(_planned_genes)} representative genes; retrieval retained all {len(to_ret)} selected genes",
                })
            # Agent narrows retrieval to its planned sources inside the
            # user's enabled-source allow-list.
            _agent_apis, _agent_dbs = self._select_agent_sources(
                plan, enabled_apis, enabled_dbs
            )
            kws_pm = plan.get("pubmed_keywords", [])
            kws_em = plan.get("europepmc_keywords", [])
            focus  = plan.get("focus", message[:80])
        except Exception as _pe:
            logger.warning("[AgenticRAG] Planning fallback: {}".format(_pe))
            # Fallback: retain the complete user-selected candidate set; the
            # configured gene count, not an internal top-k constant, controls
            # the cohort sent to source retrieval.
            to_ret = top_ranked_genes[:]
            _agent_apis = enabled_apis
            _agent_dbs  = enabled_dbs
            kws_pm = [message[:60]]
            kws_em = []
            focus  = message[:80]

        literature_search_requested = not (
            isinstance(plan, dict) and plan.get("literature_search") is False
        )
        if not literature_search_requested:
            _agent_apis = set(_agent_apis) - {"pubmed", "europepmc"}

        # Fallback: ensure we always have genes to retrieve
        if not to_ret:
            to_ret = top_ranked_genes[:]

        # The selected cohort is the RAG contract, not just a planner hint:
        # build/reuse records for every enabled source for every selected
        # gene.  The agent still decides the question-specific focus and
        # literature expansion below, but it must not silently turn the
        # first single-cell RAG pass into a partial source crawl.
        _agent_apis = set(enabled_apis)
        _agent_dbs = set(enabled_dbs)

        # Literature is question-specific.  Reuse the per-gene evidence, but
        # always issue a fresh PubMed/EuropePMC query for the current wording.
        _lit_seed_genes = list(dict.fromkeys(str(g) for g in to_ret if str(g).strip()))[:8]
        _lit_context = str(self.adata.uns.get("e2sc_dataset_description") or focus or "").strip()
        _lit_query = " ".join(
            part for part in (message.strip()[:180], _lit_context[:120], " ".join(_lit_seed_genes))
            if part
        )[:420] or "expression profile"
        kws_pm = [str(k).strip() for k in (kws_pm or []) if str(k).strip()] or [_lit_query]
        kws_em = [str(k).strip() for k in (kws_em or []) if str(k).strip()] or [f"{_lit_query} omics"]
        kws = list(OrderedDict.fromkeys(kws_pm + kws_em))  # merged, deduped

        # Step 2b: Intelligent keyword expansion — generate multi-angle keywords if few provided
        # This ensures rich literature coverage across biological, clinical, and methodological angles
        _EXPANSION_PROMPT = (
            "You are a biomedical literature search expert. Generate diverse search keywords.\n"
            "Genes: {genes}\n"
            "Disease/Context: {context}\n"
            "Existing keywords: {existing}\n\n"
            "Generate only the additional search angles needed by the user's question. "
            "Do not add generic methodology, survival, drug, pathway, or interaction searches unless relevant.\n"
            "Return JSON: {{\"pubmed_keywords\": [...], \"europepmc_keywords\": [...]}}\n"
            "Use PubMed for primary research when appropriate and Europe PMC for complementary records when appropriate.\n"
            "Max 10 total per list. Use actual gene names from the list."
        )
        if not _is_precomputed_bulk and len(kws) < 3 and to_ret:
            try:
                _exp_genes = to_ret[:8]  # cap for prompt length
                _exp_ctx = focus or message[:120]
                _exp_prompt = _EXPANSION_PROMPT.format(
                    genes=", ".join(_exp_genes),
                    context=_exp_ctx,
                    existing=", ".join(kws) if kws else "(none)"
                )
                _exp_raw = self.llm.chat([{"role": "user", "content": _exp_prompt}])
                _jm = _re_ar.search(r"\{[\s\S]*\}", _exp_raw)
                if _jm:
                    _exp = json.loads(_jm.group())
                    _extra_pm = [str(k).strip() for k in _exp.get("pubmed_keywords", []) if str(k).strip()]
                    _extra_em = [str(k).strip() for k in _exp.get("europepmc_keywords", []) if str(k).strip()]
                    kws_pm = list(OrderedDict.fromkeys(kws_pm + _extra_pm))
                    kws_em = list(OrderedDict.fromkeys(kws_em + _extra_em))
                    kws = list(OrderedDict.fromkeys(kws_pm + kws_em))
                    logger.info(f"[AgenticRAG] Keyword expansion: +{len(_extra_pm)} PM, +{len(_extra_em)} EPMC keywords")
            except Exception as _ke:
                logger.warning(f"Keyword expansion failed: {_ke}")
        _check_abort()  # abort check after keyword expansion

        thinking_steps.append({"step":"AgentPlan","content":"Focus: {} | {} genes selected | APIs: {} | DBs: {} | kws: {}".format(
            focus, len(to_ret), sorted(_agent_apis), sorted(_agent_dbs), kws[:3])})
        logger.info("[AgenticRAG] Plan: {} genes, {} keywords, APIs={}, DBs={}".format(
            len(to_ret), len(kws), sorted(_agent_apis), sorted(_agent_dbs)))

        # Step 3: RAG retrieval — agent-selected genes + agent-selected APIs/DBs
        self.state_manager.set_state(AgentState.RETRIEVING)
        knowledge, missing_genes, reused_complete = self._get_persisted_rag_knowledge(
            to_ret, required_apis=_agent_apis, required_dbs=_agent_dbs
        )
        if knowledge is None:
            knowledge = self._build_group_knowledge_parallel(
                "agentic/{}".format(focus[:30]), to_ret,
                context_hint=focus, enabled_apis=_agent_apis, enabled_dbs=_agent_dbs,
                progress_callback=progress_callback, abort_flag=abort_flag)
            self._rag_needs_vector_rebuild = True
        elif missing_genes:
            fetched = self._build_group_knowledge_parallel(
                "agentic/{}/new".format(focus[:24]), missing_genes,
                context_hint=focus, enabled_apis=_agent_apis, enabled_dbs=_agent_dbs,
                progress_callback=progress_callback, abort_flag=abort_flag)
            self._merge_rag_knowledge(knowledge, fetched)
        else:
            thinking_steps.append({"step": "RAGReuse", "content": "Reused per-gene source records; this question will run fresh literature searches"})
        _check_abort()  # abort check after retrieval step

        # Keep the first-answer audit and durable usage record aligned with the
        # actual single-cell cohort.  A fresh session has no persisted count
        # yet, so relying only on the cache would report selected_items=0 even
        # though every gene in ``to_ret`` was sent through Agent RAG.
        knowledge["_selected_gene_count"] = len(to_ret)
        knowledge.setdefault("_source_stats", {})["selected_gene_count"] = len(to_ret)

        # Single-cell questions use the same first-question enrichment contract
        # as expression-profile analyses.  Run the compact GO/KEGG/GSEA/STRING
        # batch once for the selected genes, persist only its core output inside
        # the source audit, and reuse it on later questions.
        _question_enrichment = (knowledge.get("_source_stats", {}) or {}).get("question_time_enrichment")
        if _is_precomputed_bulk and not _question_enrichment:
            # Older bulk snapshots predate persistence of the structured
            # enrichment payload. Their compact summary is already embedded
            # in the dataset description, so do not rerun the whole batch.
            _question_enrichment = {"selected_genes": []}
            knowledge.setdefault("_source_stats", {})["question_time_enrichment_status"] = "reused_from_bulk_handoff"
        if not _question_enrichment and to_ret:
            try:
                from e2seq.analysis.bulk_rnaseq import run_batch_enrichment
                _ranked_for_enrichment = {
                    str(gene): float(overall_gene_values.get(gene, 0.0) or 0.0)
                    for gene in to_ret
                }
                if progress_callback:
                    progress_callback("[进度] 首次提问：并行执行 GO / KEGG / GSEA / STRING")
                _enrichment = run_batch_enrichment(
                    {"selected_genes": list(dict.fromkeys(to_ret))},
                    ranked_genes=_ranked_for_enrichment,
                    top_terms=10,
                    progress=progress_callback,
                )
                _question_enrichment = _enrichment.get("core", {})
                knowledge.setdefault("_source_stats", {})["question_time_enrichment"] = _question_enrichment
                knowledge["_source_stats"]["question_time_enrichment_status"] = "completed"
                thinking_steps.append({"step": "QuestionEnrichment", "content": "GO / KEGG / GSEA / STRING batch completed before synthesis"})
            except Exception as _enrichment_error:
                logger.warning(f"[AgenticRAG] Question-time enrichment failed: {_enrichment_error}")
                knowledge.setdefault("_source_stats", {})["question_time_enrichment_status"] = "failed"
                knowledge["_source_stats"]["question_time_enrichment_error"] = str(_enrichment_error)
        _check_abort()  # abort check after question-time enrichment

        # Step 3b: Agent-directed literature augmentation using direct API calls
        # PubMed and EuropePMC use SEPARATE keyword sets from the agent plan — no count cap
        try:
            import requests as _kw_req
            _sp  = {a.get("pmid") for a in knowledge.get("pubmed", [])}
            _sep = {a.get("pmid") for a in knowledge.get("europepmc", [])}
            _literature_queries = {"pubmed": 0, "europepmc": 0}
            _literature_errors = {"pubmed": [], "europepmc": []}
            if literature_search_requested and progress_callback and ("pubmed" in _agent_apis or "europepmc" in _agent_apis):
                progress_callback("[进度] 本次提问：查询 PubMed 与 EuropePMC")
            if literature_search_requested and "pubmed" in _agent_apis:
                pm_client = self.api_clients.get("pubmed")
                if pm_client:
                    for kw_idx, kw in enumerate(kws_pm, 1):
                        try:
                            _kw = str(kw).strip()
                            if not _kw:
                                continue
                            _literature_queries["pubmed"] += 1
                            if progress_callback:
                                progress_callback(f"[进度] 查询 PubMed ({kw_idx}/{len(kws_pm)}): {_kw[:50]}")
                            pm = pm_client.search_and_get_details(_kw, max_results=10)
                            if isinstance(pm, dict) and (
                                str(pm.get("status", "")).lower() in {"error", "unavailable"}
                                or pm.get("error")
                            ):
                                _literature_errors["pubmed"].append(
                                    str(pm.get("error") or pm.get("status") or "PubMed query failed")[:240]
                                )
                                continue
                            for art in pm.get("articles", []):
                                pmid = art.get("pmid", "")
                                if pmid and pmid not in _sp:
                                    _sp.add(pmid); knowledge.setdefault("pubmed", []).append(art)
                        except Exception as e:
                            _literature_errors["pubmed"].append(str(e)[:240])
                            logger.warning(f"PubMed search failed: {e}")
            if literature_search_requested and "europepmc" in _agent_apis:
                for kw_idx, kw in enumerate(kws_em, 1):
                    try:
                        _kw = str(kw).strip()
                        if not _kw:
                            continue
                        _literature_queries["europepmc"] += 1
                        if progress_callback:
                            progress_callback(f"[进度] 查询 EuropePMC ({kw_idx}/{len(kws_em)}): {_kw[:50]}")
                        r = _kw_req.get("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                            params={"query": _kw, "resultType": "lite",
                                    "pageSize": 10, "format": "json"},
                            timeout=12)
                        if not r.ok:
                            _literature_errors["europepmc"].append(
                                f"HTTP {r.status_code}: Europe PMC query failed"
                            )
                            continue
                        for art in r.json().get("resultList", {}).get("result", []):
                            pmid = art.get("pmid", "") or art.get("id", "")
                            if pmid and pmid not in _sep:
                                _sep.add(pmid)
                                knowledge.setdefault("europepmc", []).append({
                                    "pmid": pmid, "title": art.get("title", ""),
                                    "journal": art.get("journalTitle", ""),
                                    "citations": art.get("citedByCount", 0),
                                    "pub_year": art.get("pubYear", ""),
                                    "query_layer": kw[:60],
                                    "url": "https://europepmc.org/article/MED/{}".format(pmid)
                                })
                    except Exception as e:
                        _literature_errors["europepmc"].append(str(e)[:240])
                        logger.warning(f"EuropePMC search failed: {e}")
            knowledge.setdefault("_source_stats", {})["literature_queries"] = _literature_queries
            knowledge["_source_stats"]["literature_errors"] = {
                source: list(dict.fromkeys(errors))[:3]
                for source, errors in _literature_errors.items() if errors
            }
            knowledge["_source_stats"]["literature_search_attempted"] = bool(literature_search_requested)
            knowledge["_source_stats"]["literature_search_decision"] = (
                "explicitly_skipped_existing_evidence_sufficient"
                if not literature_search_requested else "attempted"
            )
        except Exception as _le:
            logger.warning(f"[AgenticRAG] Lit augmentation failed: {_le}")

        _check_abort()  # abort check after literature augmentation

        n_ret  = len(knowledge.get("genes", {}))
        n_arts = len(knowledge.get("pubmed", [])) + len(knowledge.get("europepmc", []))
        thinking_steps.append({"step": "RAGRetrieve", "content": "{} genes retrieved, {} articles".format(n_ret, n_arts)})
        logger.info("[AgenticRAG] Retrieved: {} genes, {} articles".format(n_ret, n_arts))

        # Step 4: Agent evaluation loop — iterate until sufficient or max rounds
        # Required flow: question -> source-aware retrieval -> embed/rag -> sufficiency check -> repeat
        _max_refine_rounds = 0 if reused_complete else 3
        for _round in range(1, _max_refine_rounds + 1):
            _check_abort()  # abort check at start of each refine round
            n_ret_now = len(knowledge.get("genes", {}))
            n_arts_now = len(knowledge.get("pubmed", [])) + len(knowledge.get("europepmc", []))
            eval_prompt = (
                "User question: {}\n"
                "Retrieved data: {} genes, {} articles.\n"
                "Current genes: {}\n"
                "You MUST decide if evidence is sufficient for a high-confidence answer.\n"
                "If insufficient, return extra genes and extra literature keywords for PubMed/EuropePMC.\n"
                "Output STRICT JSON only: "
                "{{\"sufficient\": true/false, "
                "\"extra_genes\": [up to 10 dataset genes], "
                "\"pubmed_keywords\": [strings], "
                "\"europepmc_keywords\": [strings], "
                "\"reason\": \"short reason\"}}"
            ).format(
                message, n_ret_now, n_arts_now,
                list(knowledge.get("genes", {}).keys())[:80]
            )
            try:
                ev_raw = self.llm.chat([{"role": "user", "content": eval_prompt}])
                _em = _re_ar.search(r"\{[\s\S]*?\}", ev_raw)
                ev = json.loads(_em.group()) if _em else {"sufficient": True}
            except Exception:
                ev = {"sufficient": True}

            if ev.get("sufficient", True):
                thinking_steps.append({"step": "AgentEval",
                    "content": "Round {}/{} sufficient | genes={}, articles={}".format(
                        _round, _max_refine_rounds, n_ret_now, n_arts_now)})
                break

            extra_genes = [g for g in ev.get("extra_genes", []) if g in _gene_set][:10]
            extra_pm = [str(k).strip() for k in ev.get("pubmed_keywords", []) if str(k).strip()]
            extra_em = [str(k).strip() for k in ev.get("europepmc_keywords", []) if str(k).strip()]
            thinking_steps.append({"step": "AgentEval",
                "content": "Round {}/{} insufficient | +genes={} | +pm_kw={} | +epmc_kw={} | {}".format(
                    _round, _max_refine_rounds, extra_genes[:5], extra_pm[:3], extra_em[:3], ev.get("reason", ""))})

            if not extra_genes and not extra_pm and not extra_em:
                break

            # Re-retrieve extra genes using the same Agent-selected source policy
            if extra_genes:
                logger.info("[AgenticRAG] Re-retrieve round {} genes: {}".format(_round, extra_genes))
                ekb = self._build_group_knowledge_parallel(
                    "agentic/refine/{}".format(_round),
                    extra_genes,
                    context_hint=focus,
                    enabled_apis=_agent_apis,
                    enabled_dbs=_agent_dbs,
                    progress_callback=progress_callback,
                    abort_flag=abort_flag,
                )
                knowledge.setdefault("genes", {}).update(ekb.get("genes", {}))
                _sp2 = {a.get("pmid") for a in knowledge.get("pubmed", [])}
                for a in ekb.get("pubmed", []):
                    if a.get("pmid") not in _sp2:
                        knowledge.setdefault("pubmed", []).append(a)
                _se2 = {a.get("pmid") or a.get("id") for a in knowledge.get("europepmc", [])}
                for a in ekb.get("europepmc", []):
                    _id = a.get("pmid") or a.get("id")
                    if _id not in _se2:
                        knowledge.setdefault("europepmc", []).append(a)
                # Merge _source_stats from refinement round into accumulated stats
                self._merge_source_stats(knowledge, ekb)

            # Re-query literature with extra keywords
            try:
                import requests as _kw_req
                if "pubmed" in _agent_apis and extra_pm:
                    pm_client = self.api_clients.get("pubmed")
                    if pm_client:
                        _sp = {a.get("pmid") for a in knowledge.get("pubmed", [])}
                        for kw_idx, kw in enumerate(extra_pm, 1):
                            try:
                                if progress_callback:
                                    progress_callback(f"[进度] 查询 PubMed ({kw_idx}/{len(extra_pm)}): {kw[:50]}")
                                pm = pm_client.search_and_get_details(kw, max_results=10)
                                for art in pm.get("articles", []):
                                    pmid = art.get("pmid", "")
                                    if pmid and pmid not in _sp:
                                        _sp.add(pmid)
                                        knowledge.setdefault("pubmed", []).append(art)
                            except Exception as _pe:
                                logger.warning(f"PubMed extra search failed: {_pe}")
                if "europepmc" in _agent_apis and extra_em:
                    _sep = {a.get("pmid") or a.get("id") for a in knowledge.get("europepmc", [])}
                    for kw_idx, kw in enumerate(extra_em, 1):
                        try:
                            if progress_callback:
                                progress_callback(f"[进度] 查询 EuropePMC ({kw_idx}/{len(extra_em)}): {kw[:50]}")
                            r = _kw_req.get(
                                "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                                params={"query": kw, "resultType": "lite", "pageSize": 10, "format": "json"},
                                timeout=12,
                            )
                            for art in r.json().get("resultList", {}).get("result", []):
                                pmid = art.get("pmid", "") or art.get("id", "")
                                if pmid and pmid not in _sep:
                                    _sep.add(pmid)
                                    knowledge.setdefault("europepmc", []).append({
                                        "pmid": pmid,
                                        "title": art.get("title", ""),
                                        "journal": art.get("journalTitle", ""),
                                        "citations": art.get("citedByCount", 0),
                                        "pub_year": art.get("pubYear", ""),
                                        "query_layer": kw[:60],
                                        "url": "https://europepmc.org/article/MED/{}".format(pmid),
                                    })
                        except Exception as _ee:
                            logger.warning(f"EuropePMC extra search failed: {_ee}")
            except Exception as _le2:
                logger.warning(f"Extra literature failed: {_le2}")

        # --- Step 4c: Build vector store from retrieved knowledge ---
        try:
            _force_vector_rebuild = bool(getattr(self, "_rag_needs_vector_rebuild", False))
            if _force_vector_rebuild:
                # Newly fetched genes/source records are not in the persisted
                # collection, so do not reattach it before rebuilding.
                self._vector_store = None
            else:
                self._restore_persisted_vector_store()
            if self._vector_store is None or self._vector_store.count() == 0:
                from e2seq.data.vector_store import reset_vector_store
                _vs = reset_vector_store(self._session_id, llm=self.llm)
                n_vs_docs = _vs.reset_and_build(knowledge)
                self._vector_store = _vs
                knowledge.setdefault("_source_stats", {})["vector_chunks"] = n_vs_docs
                knowledge.setdefault("_source_stats", {})["vector_retrieval_mode"] = "hybrid dense + BM25"
                thinking_steps.append({"step": "VectorStoreBuild",
                    "content": "{} docs embedded".format(n_vs_docs)})
                logger.info("[AgenticRAG] Vector store built: {} docs".format(n_vs_docs))
                if progress_callback:
                    progress_callback(f"[进度] [向量库] 构建完成，{n_vs_docs} 文档已嵌入")
            else:
                knowledge.setdefault("_source_stats", {})["vector_chunks"] = self._vector_store.count()
                knowledge.setdefault("_source_stats", {})["vector_retrieval_mode"] = "hybrid dense + BM25 (reused)"
                thinking_steps.append({"step": "VectorStoreBuild",
                    "content": "Reusing existing store: {} docs".format(self._vector_store.count())})
                logger.info("[AgenticRAG] Reusing vector store: {} docs".format(self._vector_store.count()))
            self._rag_needs_vector_rebuild = False
        except Exception as _vse:
            logger.warning("[AgenticRAG] Vector store build failed: {}".format(_vse))

        # --- Step 4d: RAG retrieval from vector store ---
        if self._vector_store is not None and self._vector_store.count() > 0:
            try:
                # Use focus as RAG query when message is too short/vague
                _rag_query = focus if (len(message.strip()) < 20 or any(
                    kw in message for kw in ["综合", "解读", "全面", "整体", "comprehensive", "overall"]
                )) else message
                _rag_top_k = min(50, max(20, self._vector_store.count() // 10))
                knowledge.setdefault("_source_stats", {})["vector_retrieval_top_k"] = _rag_top_k
                _rag_ctx = self._vector_store.retrieve_context(_rag_query, n_results=_rag_top_k)
                if _rag_ctx:
                    knowledge["rag_context"] = _rag_ctx
                    thinking_steps.append({"step": "VectorRAG",
                        "content": "{} docs; ranked context chunks retrieved for: {}".format(
                            self._vector_store.count(), _rag_query[:60])})
            except Exception as _re:
                logger.warning("[AgenticRAG] RAG retrieval failed: {}".format(_re))

        knowledge.setdefault("_source_stats", {})["rag_elapsed_seconds"] = round(
            max(0.0, _time.perf_counter() - _rag_started), 3
        )
        self._persist_rag_knowledge(knowledge)

        # Step 5: Synthesize
        all_q = list(knowledge.get("genes", {}).keys())[:100]
        input_results = {
            "plots": [],
            "interpretation_only": True,
            "matrix_context": {
                "genes_queried": all_q,
                "overall_gene_values": overall_gene_values,
                "top_genes_per_celltype": ct_matrix,
                "top_genes_per_group": grp_matrix,
                "priority_genes": to_ret,
                "interpretation_focus": focus,
            },
            "question_time_enrichment": (knowledge.get("_source_stats", {}) or {}).get("question_time_enrichment")
        }
        # Keep only this session's conversation history. Do not mix knowledge
        # from another uploaded dataset into the current interpretation.
        history = self.memory.get_conversation_history_for_llm(max_messages=20, max_total_chars=8000)
        self.state_manager.set_state(AgentState.SYNTHESIZING)
        logger.info(f"[AgenticRAG] Starting synthesize. has_knowledge={bool(knowledge.get('genes'))}, text_queue={text_queue is not None}")
        if progress_callback:
            progress_callback("[进度] 正在根据输入基因数值和检索证据生成解读...")
        _selected_for_synthesis = int(knowledge.get("_selected_gene_count") or 0)
        _rag_genes_for_synthesis = len(knowledge.get("genes", {}) or {})
        _synthesis_max_retries = (
            1 if _selected_for_synthesis > 30 or _rag_genes_for_synthesis > 30 else None
        )
        ok, resp, err = self.error_recovery.execute_with_retry(
            self.synthesizer.synthesize,
            message, input_results, knowledge, history,
            error_context="synthesize_agentic_rag", is_comprehensive=False,
            max_retries=_synthesis_max_retries,
            text_queue=text_queue,
            progress_callback=progress_callback,
            abort_flag=abort_flag,
        )
        if not ok:
            logger.error(f"[AgenticRAG] Synthesize failed: {err}")
            if err and "abort" in err.lower():
                from e2seq.api.server import AbortChat as _AbortChat
                raise _AbortChat(err)
            try:
                from e2seq.agent.synthesizer import _format_rag_source_audit
                fallback_digest = self.synthesizer._format_knowledge(knowledge, question=message)
                fallback_audit = _format_rag_source_audit(knowledge, question=message)
                _provider = str(getattr(self.llm, "provider", "") or "").strip()
                if not _provider:
                    _provider = {
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
                _model = str(getattr(self.llm, "model", "unknown") or "unknown")
                resp = {
                    "text": f"回答模型 API：{_provider} / {_model}。\n\n"
                    "本次大模型综合合成暂时不可用，以下返回已完成的 RAG 证据与来源审计。\n\n"
                    + fallback_digest + "\n\n" + fallback_audit,
                    "plots": [],
                    "data": {
                        "knowledge": knowledge,
                        "source_audit": fallback_audit,
                        "retrieval_status": {
                            "genes_retrieved": len(knowledge.get("genes", {}) or {}),
                            "has_sufficient_knowledge": bool(knowledge),
                        },
                    },
                }
            except Exception:
                resp = {"text":"Synthesis failed: {}".format(err),"plots":[],"data":{"knowledge": knowledge}}
        else:
            logger.info(f"[AgenticRAG] Synthesize OK: response_len={len(resp.get('text',''))}")
        if not isinstance(resp, dict):
            resp = {"text":str(resp),"plots":[],"data":{}}
        resp["thinking"] = thinking_steps

        # Append source statistics to response data (frontend renders as styled HTML panel)
        knowledge["_rag_queried_gene_count"] = len(knowledge.get("genes", {}) or {})
        try:
            from e2seq.agent.synthesizer import _normalise_source_stats
            _normalise_source_stats(knowledge)
        except Exception as _stats_error:
            logger.warning("[AgenticRAG] Source coverage normalisation failed: %s", _stats_error)
        src_stats = knowledge.get("_source_stats", {})
        if src_stats:
            # Serialize sets -> lists for JSON response
            _ss: dict = dict(src_stats)
            for _cat in ("apis", "dbs"):
                if _cat in _ss and isinstance(_ss[_cat], dict):
                    for _sn, _si in _ss[_cat].items():
                        if isinstance(_si, dict) and isinstance(_si.get("hit_genes"), set):
                            _si["hit_genes"] = list(_si["hit_genes"])
            # Ensure consistent key names for frontend
            if "total_genes" in _ss:
                _ss["total_genes_queried"] = _ss.pop("total_genes")
            _ss["selected_gene_count"] = int(knowledge.get("_selected_gene_count") or 0)
            _ss["rag_queried_gene_count"] = int(knowledge.get("_rag_queried_gene_count") or 0)
            resp.setdefault("data", {})["source_stats"] = _ss

        self.memory.working_memory.add_message("assistant", resp.get("text",""))
        self.memory.save_current_session(success=True)
        self.state_manager.set_state(AgentState.COMPLETED)
        return resp

    def _get_gene_cache_lock(self):
        import threading
        if self._gene_cache_lock is None:
            self._gene_cache_lock = threading.Lock()
        return self._gene_cache_lock

    def _build_group_knowledge(self, label: str, genes: list, context_hint: str = "",
                                    enabled_apis: set = None, enabled_dbs: set = None,
                                    progress_callback=None, abort_flag=None) -> dict:
        """Query the Agent-selected APIs and local DBs for a gene group.

        Enabled online APIs are executed concurrently via ThreadPoolExecutor.
        Enabled local DB lookups
        (STRING, HMDB, TRRUST, GUTMGENE) are fast and run serially.
        Per-gene results are cached in self._gene_cache to avoid redundant
        cross-group queries.

        Args:
            abort_flag: threading.Event; if set, raises AbortChat to stop execution.
        """
        from e2seq.api import AbortChat as _AbortChat

        def _check_abort():
            """Raise AbortChat if the user has clicked the abort button."""
            if abort_flag is not None and abort_flag.is_set():
                raise _AbortChat("User requested abort")

        import requests as _requests
        from concurrent.futures import ThreadPoolExecutor, as_completed
        from e2seq.data.local_db import HMDBDatabase, TRRUSTDatabase, GUTMGENEDatabase, STRINGDatabase
        from e2seq.data.knowledge_sources import KnowledgeSourceClient
        from e2seq.data.custom_sources import load_custom_sources
        from e2seq.data.custom_annotations import load_annotation_catalog, query_annotations

        # Reuse one bounded connection pool for this group.  The previous
        # implementation called the module-level ``requests.get`` for every
        # source/gene pair, which created thousands of short-lived sockets in
        # a 1,000-item cohort and made the process look CPU-bound while it was
        # mostly churning connections.
        _req = _requests.Session()
        _req.headers.update({"User-Agent": "E2seq/2.1 (agentic-rag)"})
        try:
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            _retry = Retry(
                total=4,
                connect=4,
                read=4,
                status=4,
                backoff_factor=0.35,
                status_forcelist=(408, 425, 429, 500, 502, 503, 504),
                allowed_methods=frozenset({"GET", "POST"}),
                respect_retry_after_header=True,
                raise_on_status=False,
            )
            _adapter = HTTPAdapter(
                pool_connections=max(8, _MAX_SOURCE_WORKERS * 4),
                pool_maxsize=max(8, _MAX_SOURCE_WORKERS * 4),
                max_retries=_retry,
            )
            _req.mount("https://", _adapter)
            _req.mount("http://", _adapter)
        except Exception:
            pass

        knowledge = {"genes": {}, "pubmed": [], "europepmc": [], "_source_stats": {}}
        seen_pmids = set()
        _dataset_context = ""
        try:
            _dataset_context = str(
                self.adata.uns.get("e2sc_dataset_description")
                or self.adata.uns.get("e2sc_project_name")
                or ""
            ).strip()
        except Exception:
            _dataset_context = ""
        _source_context_hint = " ".join(
            part for part in (str(context_hint or "").strip(), _dataset_context) if part
        )[:500]
        # 已确认可用的API列表（含reactome/opentargets/clinvar）
        _custom_sources = {
            str(item.get("id")).lower(): item
            for item in load_custom_sources(include_secrets=True)
            if item.get("id")
        }
        _ALL_APIS = set(VERIFIED_RAG_APIS | OPTIONAL_RAG_APIS) | set(_custom_sources)
        _annotation_catalog = load_annotation_catalog()
        _ALL_DBS  = {"string","hmdb","trrust","gutmgene"}
        if _annotation_catalog:
            _ALL_DBS.add("custom_gene_annotations")
        # Per-source hit tracking: {source_name: {"hit": set of genes with data, "total": int}}
        if enabled_apis is None:
            enabled_apis = set(VERIFIED_RAG_APIS | OPTIONAL_RAG_APIS)
            enabled_apis.update(
                source for source, definition in _custom_sources.items()
                if definition.get("enabled", True)
            )
        else:
            _raw_enabled_apis = {str(source).lower() for source in enabled_apis}
            enabled_apis = _raw_enabled_apis & _ALL_APIS
        if enabled_dbs is None:
            enabled_dbs = set(_ALL_DBS)
        else:
            enabled_dbs = {str(source).lower() for source in enabled_dbs} & _ALL_DBS
            # Uploaded gene-annotation files are a local RAG source, not an
            # interaction database checkbox.  They are always included when
            # present so a selected gene cannot lose user-provided evidence.
            if _annotation_catalog:
                enabled_dbs.add("custom_gene_annotations")

        # Track only sources that were enabled for this retrieval.  Keeping
        # disabled sources out of the audit prevents a response from implying
        # that every possible API was queried when the user selected a subset.
        _src_stats: dict = {
            "apis": {s: {"hit_genes": set(), "total_genes": len(genes), "status_counts": {}} for s in enabled_apis},
            "dbs":  {s: {"hit_genes": set(), "total_genes": len(genes), "status_counts": {}} for s in enabled_dbs},
            "total_genes": len(genes),
            "enabled_apis": sorted(enabled_apis),
            "enabled_dbs": sorted(enabled_dbs),
        }
        # Keep initial full-cohort literature work separate from the
        # question-time literature pass.  The answer audit must be able to
        # show both counts instead of replacing the expensive first pass with
        # the much smaller number of queries for the current question.
        _initial_literature_queries = {"pubmed": 0, "europepmc": 0}
        _source_client = KnowledgeSourceClient(timeout=20)
        # ClinVar and PubMed both use NCBI E-utilities.  Route ClinVar through
        # the shared rate-limited/retrying client so a 1,000-gene cohort does
        # not create a second uncoordinated NCBI request stream that triggers
        # 429 responses for the literature pass.
        from api.pubmed_api import PubMed_API as _PubMedAPI
        _ncbi_client = _PubMedAPI()
        _source_status_lock = threading.Lock()
        _source_failures: set[tuple[str, str]] = set()

        def _record_source_status(source: str, status: str, error: str = "") -> None:
            """Keep endpoint state separate from gene-level hit coverage."""
            category = "apis" if source in _ALL_APIS else "dbs"
            if source not in _src_stats.get(category, {}):
                return
            with _source_status_lock:
                stats = _src_stats[category][source]
                counts = stats.setdefault("status_counts", {})
                counts[status] = int(counts.get(status, 0)) + 1
                # A resolver can legitimately explain a ``no_records`` result
                # (for example, no exact Entrez mapping or no UniProt
                # accession). Keep that explanation out of the transport
                # error list; otherwise the UI reports a healthy, queried
                # endpoint as an interface error.
                if error and status in {"error", "unavailable", "needs_configuration"}:
                    errors = stats.setdefault("errors", [])
                    if error not in errors and len(errors) < 3:
                        errors.append(error[:240])

        def _mark_source_failure(source: str, gene: str, error: str) -> None:
            """Record transport failures separately from biological no-records."""
            with _source_status_lock:
                _source_failures.add((str(source).lower(), str(gene)))
            _record_source_status(source, "error", error)

        def _source_failed(source: str, gene: str) -> bool:
            with _source_status_lock:
                return (str(source).lower(), str(gene)) in _source_failures

        _source_fields = {
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
        for source in _custom_sources:
            _source_fields[source] = (f"custom_{source}_records",)

        def _record_cached_source_hits(gene: str, info: dict) -> None:
            """Count source records reused from the per-agent gene cache."""
            for source, fields in _source_fields.items():
                category = "apis" if source in _ALL_APIS else "dbs"
                if source not in _src_stats.get(category, {}):
                    continue
                if any(info.get(field) for field in fields):
                    _src_stats[category][source]["hit_genes"].add(gene)

        def _fetch_verified_source(source: str, gene: str) -> tuple:
            """Fetch one source through the status-aware public adapter."""
            try:
                result = _source_client.query(
                    source,
                    gene,
                    max_results=20,
                    context_hint=_source_context_hint,
                    custom_source=_custom_sources.get(source),
                )
                status = str(result.get("status") or "error")
                _record_source_status(source, status, str(result.get("error") or ""))
                records = result.get("records") or []
                fields = result.get("fields") or {}

                if source == "gtex":
                    values = [
                        f"{row.get('tissue')}: {row.get('median_expression')} {row.get('unit', 'TPM')}"
                        for row in records if isinstance(row, dict) and row.get("tissue")
                    ]
                    if values:
                        fields = {**fields, "gtex_tissues": values[:12]}
                elif source == "hpa":
                    values = [
                        f"{row.get('field')}: {row.get('value')}"
                        for row in records if isinstance(row, dict) and row.get("field")
                    ]
                    if values:
                        fields = {**fields, "hpa_tissues": values[:12]}
                elif source == "opentargets":
                    values = [
                        f"{row.get('name')} (score={row.get('score')}, id={row.get('id', '')})"
                        for row in records if isinstance(row, dict) and row.get("name")
                    ]
                    if values:
                        fields = {**fields, "ot_diseases": values[:8]}
                elif source == "alliance":
                    values = [
                        f"{row.get('symbol')} ({row.get('species')})"
                        + (f": {row.get('name')}" if row.get("name") else "")
                        for row in records if isinstance(row, dict) and row.get("symbol")
                    ]
                    if values:
                        fields = {**fields, "alliance_homologs": values[:12]}
                elif source == "cbioportal":
                    values = []
                    for row in records:
                        if isinstance(row, dict):
                            symbol = row.get("hugoGeneSymbol") or row.get("symbol") or fields.get("hugo_symbol")
                            gene_id = row.get("entrezGeneId") or row.get("geneId")
                            if symbol or gene_id:
                                values.append(f"{symbol or gene} (gene_id={gene_id or 'NA'})")
                    if values:
                        fields = {**fields, "cbioportal_gene": values[:4]}
                elif source == "omnipath":
                    values = [
                        f"{row.get('source')} -> {row.get('target')}"
                        + (f" [sources={row.get('sources')}]" if row.get("sources") else "")
                        for row in records if isinstance(row, dict) and (row.get("source") or row.get("target"))
                    ]
                    if values:
                        fields = {**fields, "omnipath_interactions": values[:20]}
                elif source == "intact":
                    values = [
                        f"{row.get('interactor_a')} -- {row.get('interactor_b')}"
                        + (f" [{row.get('interaction')}]" if row.get("interaction") else "")
                        for row in records if isinstance(row, dict) and (row.get("interactor_a") or row.get("interactor_b"))
                    ]
                    if values:
                        fields = {**fields, "intact_interactions": values[:20]}
                elif source == "humanbase":
                    values = list(fields.get("humanbase_networks") or []) + list(fields.get("humanbase_terms") or [])
                    if not values:
                        values = [
                            f"{row.get('type')}: {row.get('partner') or row.get('term') or row.get('standard_name')}"
                            for row in records
                            if isinstance(row, dict) and (row.get("partner") or row.get("term") or row.get("standard_name"))
                        ]
                    if values:
                        fields = {**fields, "humanbase_networks": values[:20]}
                elif source == "clinicaltrials":
                    values = [
                        f"{row.get('nct_id')}: {row.get('title')} [{row.get('status') or 'status unavailable'}]"
                        + (f" | {', '.join(row.get('conditions') or [])}" if row.get("conditions") else "")
                        for row in records if isinstance(row, dict) and (row.get("nct_id") or row.get("title"))
                    ]
                    if values:
                        fields = {**fields, "clinicaltrials_studies": values[:20]}
                elif source in _custom_sources:
                    values = []
                    for row in records:
                        if isinstance(row, (dict, list)):
                            values.append(json.dumps(row, ensure_ascii=False, separators=(",", ":"))[:1200])
                        elif row not in (None, ""):
                            values.append(str(row)[:1200])
                    if values:
                        fields = {**fields, f"custom_{source}_records": values[:20]}

                # Only evidence fields count as a gene-level hit.  Query
                # strings, resolved IDs, and empty containers must not turn a
                # successful transport into a false biological record.
                allowed_fields = set(_source_fields.get(source, ()))
                fields = {
                    key: value for key, value in fields.items()
                    if key in allowed_fields and value not in (None, "", [], {}, ())
                }

                return (source, fields)
            except Exception as exc:
                _record_source_status(source, "error", str(exc))
                logger.warning(f"{source} {gene}: {exc}")
                return (source, {})

        # NOTE: gene cache is NOT cleared here — it is shared across concurrent
        # group builds and cleared once at the start of build_knowledge_base().

        # ------------------------------------------------------------------ #
        # Helper: fetch a single gene from one online API
        # ------------------------------------------------------------------ #
        def _fetch_uniprot(gene: str) -> tuple:
            try:
                r = _req.get("https://rest.uniprot.org/uniprotkb/search",
                    params={"query": f"gene:{gene} AND organism_id:9606", "format": "json"}, timeout=10)
                results = r.json().get("results", [])
                if results:
                    entry = results[0]
                    acc = entry.get("primaryAccession", "")
                    fn = ""
                    for c in entry.get("comments", []):
                        if c.get("commentType") == "FUNCTION":
                            fn = c.get("texts", [{}])[0].get("value", "")[:300]
                            break
                    return ("uniprot", {"uniprot_accession": acc, "function": fn})
            except Exception as e:
                _mark_source_failure("uniprot", gene, str(e))
                logger.warning(f"UniProt {gene}: {e}")
            return ("uniprot", {})

        def _fetch_mygene(gene: str) -> tuple:
            """Query MyGene.info for gene name, aliases and pathway info."""
            try:
                r = _req.get("https://mygene.info/v3/query",
                    params={"q": gene, "species": "human",
                            "fields": "name,alias,pathway.kegg,pathway.reactome,summary"},
                    timeout=10)
                hits = r.json().get("hits", [])
                if hits:
                    h = hits[0]
                    official = h.get("name", "")
                    aliases = h.get("alias", [])
                    if isinstance(aliases, str): aliases = [aliases]
                    pathways = []
                    for db in ("kegg", "reactome"):
                        pw = h.get("pathway", {}).get(db, [])
                        if isinstance(pw, dict): pw = [pw]
                        pathways += [p.get("name", "") for p in (pw or []) if p.get("name")][:3]
                    summary = h.get("summary", "")[:200]
                    return ("mygene", {
                        "gene_name": official,
                        "gene_aliases": aliases[:3],
                        "pathways": pathways[:5],
                        "gene_summary": summary,
                    })
            except Exception as e:
                _mark_source_failure("mygene", gene, str(e))
                logger.warning(f"MyGene {gene}: {e}")
            return ("mygene", {})

        def _fetch_quickgo(gene: str, accession: str) -> tuple:
            """Query QuickGO for GO annotations using UniProt accession."""
            try:
                if accession:
                    r = _req.get("https://www.ebi.ac.uk/QuickGO/services/annotation/search",
                        params={"geneProductId": accession, "limit": 25, "includeFields": "goName"},
                        headers={"Accept": "application/json"}, timeout=15)
                    data = r.json()
                    annotations = data.get("results", [])
                    if annotations:
                        # Collect unique GO IDs; goName is often None in this endpoint
                        go_map = {}
                        for a in annotations:
                            goid = a.get("goId", "")
                            goname = a.get("goName") or a.get("name")
                            aspect = a.get("goAspect", "")
                            if goid and goid not in go_map:
                                go_map[goid] = {"name": goname, "aspect": aspect}
                        # # goName already populated via includeFields=goName -- no batch fetch needed
                        # Format with aspect prefix
                        aspect_prefix = {"biological_process": "BP", "molecular_function": "MF", "cellular_component": "CC"}
                        go_terms = []
                        for goid, info in list(go_map.items())[:12]:
                            name = info.get("name") or goid
                            prefix = aspect_prefix.get(info.get("aspect", ""), "")
                            go_terms.append(f"{prefix}:{name}" if prefix else name)
                        go_aspects = list({v.get("aspect", "") for v in go_map.values() if v.get("aspect")})
                        return ("quickgo", {
                            "go_terms": [t for t in go_terms if t][:10],
                            "go_aspects": go_aspects,
                        })
            except Exception as e:
                _mark_source_failure("quickgo", gene, str(e))
                logger.warning(f"QuickGO {gene}: {e}")
            return ("quickgo", {})

        def _fetch_ensembl(gene: str) -> tuple:
            """Query Ensembl REST API for gene description and location."""
            try:
                r = _req.get(f"https://rest.ensembl.org/lookup/symbol/homo_sapiens/{gene}",
                    headers={"Content-Type": "application/json"}, timeout=10)
                data = r.json()
                if "id" in data:
                    return ("ensembl", {
                        "chromosome": data.get("seq_region_name", ""),
                        "description": data.get("description", "")[:200],
                        "ensembl_id": data.get("id", ""),
                        "biotype": data.get("biotype", ""),
                    })
            except Exception as e:
                _mark_source_failure("ensembl", gene, str(e))
                logger.warning(f"Ensembl {gene}: {e}")
            return ("ensembl", {})

        def _fetch_chembl(gene: str) -> tuple:
            """Query ChEMBL for drug targets and approved molecules."""
            try:
                r = _req.get("https://www.ebi.ac.uk/chembl/api/data/target/search.json",
                    params={"q": gene, "limit": 5}, timeout=10)
                data = r.json()
                targets = data.get("targets", [])
                if targets:
                    drug_targets = []
                    for t in targets[:3]:
                        name = t.get("pref_name", "")
                        tid = t.get("target_chembl_id", "")
                        if not name:
                            continue
                        # Try to get approved drugs via mechanism endpoint
                        drugs = []
                        try:
                            r2 = _req.get("https://www.ebi.ac.uk/chembl/api/data/mechanism.json",
                                params={"target_chembl_id": tid, "limit": 5}, timeout=6)
                            mechs = r2.json().get("mechanisms", [])
                            drugs = [m.get("molecule_name", "") for m in mechs if m.get("molecule_name")]
                        except Exception as _ee:
                            logger.warning(f"EuropePMC extra search failed: {_ee}")
                        # Fall back to activity molecules if no mechanism drugs
                        if not drugs:
                            try:
                                r3 = _req.get("https://www.ebi.ac.uk/chembl/api/data/activity.json",
                                    params={"target_chembl_id": tid, "limit": 3, "assay_type": "B"}, timeout=6)
                                acts = r3.json().get("activities", [])
                                drugs = list(set(a.get("molecule_chembl_id", "") for a in acts if a.get("molecule_chembl_id")))[:3]
                            except Exception as _pe:
                                logger.warning(f"PubMed extra search failed: {_pe}")
                        entry = f"{name} ({tid})"
                        if drugs:
                            entry += f" [drugs: {', '.join(str(d) for d in drugs[:3])}]"
                        drug_targets.append(entry)
                    if drug_targets:
                        return ("chembl", {"drug_targets": drug_targets})
            except Exception as e:
                _mark_source_failure("chembl", gene, str(e))
                logger.warning(f"ChEMBL {gene}: {e}")
            return ("chembl", {})


        def _fetch_opentargets(gene: str) -> tuple:
            """Query Open Targets Platform for gene-disease associations."""
            return _fetch_verified_source("opentargets", gene)
            try:
                query = """
                query ($gene: String!) {
                  target(ensemblId: $gene) {
                    id
                    approvedSymbol
                    associatedDiseases(page: {index: 0, size: 5}) {
                      rows {
                        disease { name id }
                        score
                      }
                    }
                  }
                }
                """
                # First get Ensembl ID via MyGene
                r_id = _req.get("https://mygene.info/v3/query",
                    params={"q": gene, "species": "human", "fields": "ensembl.gene"},
                    timeout=8)
                hits = r_id.json().get("hits", [])
                ensembl_id = ""
                if hits:
                    eg = hits[0].get("ensembl", {})
                    if isinstance(eg, dict):
                        ensembl_id = eg.get("gene", "")
                    elif isinstance(eg, list) and eg:
                        ensembl_id = eg[0].get("gene", "")
                if not ensembl_id:
                    return ("opentargets", {})
                r = _req.post("https://api.platform.opentargets.org/api/v4/graphql",
                    json={"query": query, "variables": {"gene": ensembl_id}},
                    timeout=12)
                data = r.json().get("data", {}).get("target", {}) or {}
                if not data:
                    return ("opentargets", {})
                diseases = []
                ad = data.get("associatedDiseases") or {}
                for row in (ad.get("rows") or []):
                    d = row.get("disease") or {}
                    score = round(row.get("score", 0), 3)
                    if d.get("name"):
                        diseases.append(f"{d['name']} (score={score}, id={d.get('id','')})")
                return ("opentargets", {"ot_diseases": diseases[:5], "ot_ensembl": ensembl_id})
            except Exception as e:
                _mark_source_failure("opentargets", gene, str(e))
                logger.warning(f"OpenTargets {gene}: {e}")
            return ("opentargets", {})

        def _fetch_clinvar(gene: str) -> tuple:
            """Query NCBI ClinVar for gene-disease variant associations."""
            try:
                # Search ClinVar - use broad query to get pathogenic/likely pathogenic variants
                r = _ncbi_client._request("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                    params={"db": "clinvar",
                            "term": f"{gene}[gene] AND (pathogenic[clinical significance] OR likely pathogenic[clinical significance])",
                            "retmax": 5, "retmode": "json", "sort": "relevance"},
                )
                ids = r.json().get("esearchresult", {}).get("idlist", [])
                if not ids:
                    return ("clinvar", {})
                # Fetch summaries
                r2 = _ncbi_client._request("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                    params={"db": "clinvar", "id": ",".join(ids[:5]), "retmode": "json"},
                )
                result = r2.json().get("result", {})
                variants = []
                for vid in ids[:5]:
                    rec = result.get(str(vid), {})
                    title = rec.get("title", "")
                    clin_sig = rec.get("clinical_significance", {}).get("description", "")
                    condition = rec.get("trait_set", [{"trait_name": ""}])
                    cond_name = condition[0].get("trait_name", "") if condition else ""
                    # Build a useful summary: prefer condition name, fall back to title
                    display = cond_name.strip() if cond_name.strip() else title[:60]
                    if clin_sig: display = f"{display} ({clin_sig})"
                    if display.strip():
                        variants.append(display)
                return ("clinvar", {"clinvar_variants": variants[:5]})
            except Exception as e:
                _mark_source_failure("clinvar", gene, str(e))
                logger.warning(f"ClinVar {gene}: {e}")
            return ("clinvar", {})

        def _fetch_gtex(gene: str) -> tuple:
            """Query tissue expression data via Human Protein Atlas (primary) + NCBI Gene (fallback)."""
            return _fetch_verified_source("gtex", gene)
            import requests as _gtex_req
            # Primary: Human Protein Atlas — rich tissue/organ RNA expression
            try:
                r = _gtex_req.get(
                    f"https://www.proteinatlas.org/api/search_download.php",
                    params={"search": gene, "format": "json", "columns": "g,eg,rnats", "compress": "no"},
                    timeout=10,
                )
                if r.status_code == 200:
                    rows = r.json()
                    if rows:
                        row = rows[0]
                        rna_ts = row.get("RNA tissue specificity", "") or row.get("rnats", "")
                        ensg = row.get("Ensembl", "") or row.get("eg", "")
                        if rna_ts:
                            return ("gtex", {"gtex_tissues": [f"HPA RNA specificity: {rna_ts}", f"Ensembl: {ensg}"]})
            except Exception as _le2:
                logger.warning(f"Extra literature failed: {_le2}")
            # Fallback 1: Human Protein Atlas tissue page JSON
            try:
                r2 = _gtex_req.get(
                    f"https://www.proteinatlas.org/{gene}/tissue.json",
                    timeout=10,
                )
                if r2.status_code == 200:
                    data = r2.json()
                    tissues = []
                    for entry in data.get("tissueExpression", {}).get("data", [])[:10]:
                        tissue = entry.get("tissue", "")
                        level = entry.get("level", "")
                        if tissue:
                            tissues.append(f"{tissue}: {level}" if level else tissue)
                    if tissues:
                        return ("gtex", {"gtex_tissues": tissues[:8]})
            except Exception as _le2:
                logger.warning(f"Extra literature failed: {_le2}")
            # Fallback 2: NCBI Gene + MyGene expression field
            try:
                r1 = _gtex_req.get(
                    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                    params={"db": "gene", "term": f"{gene}[gene] AND Homo sapiens[organism]",
                            "retmode": "json", "retmax": 1},
                    timeout=8,
                )
                gene_ids = r1.json().get("esearchresult", {}).get("idlist", [])
                if gene_ids:
                    r3 = _gtex_req.get(
                        "https://mygene.info/v3/gene/" + gene_ids[0],
                        params={"fields": "expression,genomic_pos"},
                        timeout=8,
                    )
                    gdata = r3.json()
                    expr = gdata.get("expression", {})
                    if isinstance(expr, dict) and expr:
                        sorted_tissues = sorted(
                            [(k, v) for k, v in expr.items() if isinstance(v, (int, float))],
                            key=lambda x: float(x[1]), reverse=True
                        )
                        tissues = [f"{t} (expr={v:.2f})" for t, v in sorted_tissues[:8]]
                        if tissues:
                            return ("gtex", {"gtex_tissues": tissues})
                    # Last resort: return genomic location as tissue context
                    r2b = _gtex_req.get(
                        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                        params={"db": "gene", "id": gene_ids[0], "retmode": "json"},
                        timeout=8,
                    )
                    result = r2b.json().get("result", {}).get(str(gene_ids[0]), {})
                    chrom = result.get("chromosome", "")
                    loc = result.get("maplocation", "")
                    summary = result.get("summary", "")[:150]
                    if chrom or summary:
                        tissues = []
                        if chrom: tissues.append(f"chr{chrom} {loc}")
                        if summary: tissues.append(f"NCBI summary: {summary}")
                        return ("gtex", {"gtex_tissues": tissues})
            except Exception as e:
                logger.warning(f"GTEx/NCBI {gene}: {e}")
            return ("gtex", {})

        def _fetch_reactome(gene: str) -> tuple:
            """Query Reactome for pathway membership."""
            try:
                # ContentService: find pathways by gene symbol
                r = _req.get(f"https://reactome.org/ContentService/data/mapping/UniProt/{gene}/pathways",
                    headers={"Accept": "application/json"}, timeout=10)
                if r.status_code != 200:
                    # Try by gene name
                    r = _req.get("https://reactome.org/ContentService/search/query",
                        params={"query": gene, "species": "Homo sapiens",
                                "types": "Pathway", "cluster": "true"},
                        headers={"Accept": "application/json"}, timeout=10)
                    hits = r.json().get("results", [])
                    pathways = []
                    for h in hits[:1]:
                        for e in h.get("entries", [])[:5]:
                            name = e.get("name", "")
                            pid = e.get("stId", "")
                            if name:
                                pathways.append(f"{name} ({pid})")
                    return ("reactome", {"reactome_pathways": pathways[:5]})
                data = r.json()
                pathways = []
                for p in data[:6]:
                    name = p.get("displayName", "") or p.get("name", "")
                    pid = p.get("stId", "")
                    if name:
                        pathways.append(f"{name} ({pid})")
                import re as _re
                pathways = [_re.sub(r'<[^>]+>', '', p) for p in pathways]
                return ("reactome", {"reactome_pathways": [p for p in pathways if p.strip()][:5]})
            except Exception as e:
                _mark_source_failure("reactome", gene, str(e))
                logger.warning(f"Reactome {gene}: {e}")
            return ("reactome", {})

        def _fetch_gwas(gene: str) -> tuple:
            """Query GWAS Catalog for gene-associated SNPs and disease traits."""
            # Primary: V2 API with geneSymbol
            try:
                r = _req.get(
                    "https://www.ebi.ac.uk/gwas/rest/api/v2/associations",
                    params={"geneSymbol": gene, "size": 10},
                    headers={"Accept": "application/json", "User-Agent": "E2seq/1.0"},
                    timeout=15,
                )
                if r.status_code == 200:
                    data = r.json()
                    associations = data.get("_embedded", {}).get("associations", [])
                    if associations:
                        snps = []
                        for s in associations[:8]:
                            pval = s.get("p_value", "")
                            or_val = s.get("or_value", "")
                            efo = s.get("efo_traits", [])
                            trait = efo[0].get("efo_trait", "") if efo else ""
                            pubmed = s.get("pubmed_id", "")
                            parts = []
                            if trait: parts.append(trait)
                            if pval: parts.append(f"p={pval}")
                            if or_val and or_val != "-": parts.append(f"OR={or_val}")
                            if pubmed: parts.append(f"[PubMed:{pubmed}]")
                            if parts: snps.append(" | ".join(parts))
                        if snps:
                            return ("gwas", {"gwas_snps": snps[:8]})
            except Exception as e:
                _mark_source_failure("gwas", gene, str(e))
                logger.warning(f"GWAS V2 {gene}: {e}")
            # Fallback: V1 REST API — search by reported gene
            try:
                r2 = _req.get(
                    "https://www.ebi.ac.uk/gwas/rest/api/singleNucleotidePolymorphisms/search/findByGene",
                    params={"geneName": gene, "size": 10},
                    headers={"Accept": "application/json"},
                    timeout=15,
                )
                if r2.status_code == 200:
                    snp_list = r2.json().get("_embedded", {}).get("singleNucleotidePolymorphisms", [])
                    snps = []
                    for snp in snp_list[:8]:
                        rsid = snp.get("rsId", "")
                        func = snp.get("functionalClass", "")
                        chrom = snp.get("chromosomeName", "")
                        pos = snp.get("chromosomePosition", "")
                        if rsid:
                            snps.append(f"{rsid} ({func}) chr{chrom}:{pos}")
                    if snps:
                        return ("gwas", {"gwas_snps": snps[:8]})
            except Exception as e:
                _mark_source_failure("gwas", gene, str(e))
                logger.warning(f"GWAS V1 {gene}: {e}")
            return ("gwas", {})

        def _fetch_humanbase(gene: str) -> tuple:
            """Query tissue-specific expression.
            Strategy: resolve Ensembl ID via MyGene -> fetch HPA JSON with Ensembl ID.
            Falls back to Jensen TISSUES and MyGene expression field.
            """
            # Retained only as a compatibility stub for old in-memory callers;
            # HumanBase is no longer in the source allow-list and must never
            # receive HPA/Jensen fallback data under its name.
            return ("humanbase", {})
            # Primary: MyGene (resolve Ensembl) -> HPA JSON (Ensembl URL)
            try:
                # Resolve symbol -> Ensembl ID
                r_mg = _req.get(
                    "https://mygene.info/v3/query",
                    params={"q": gene, "species": "human",
                            "fields": "ensembl.gene,HGNC,symbol"},
                    timeout=10,
                )
                ensembl_id = None
                if r_mg.status_code == 200:
                    mg_data = r_mg.json()
                    hits = mg_data.get("hits", [])
                    if hits:
                        h = hits[0]
                        ensembl_list = h.get("ensembl", [])
                        if isinstance(ensembl_list, dict):
                            ensembl_list = [ensembl_list]
                        for e in ensembl_list:
                            eid = e.get("gene", "") if isinstance(e, dict) else str(e)
                            if eid and eid.startswith("ENSG"):
                                ensembl_id = eid
                                break
                if ensembl_id:
                    # Fetch HPA JSON using Ensembl ID (not gene symbol)
                    r_hpa = _req.get(
                        f"https://www.proteinatlas.org/{ensembl_id}.json",
                        timeout=10,
                    )
                    if r_hpa.status_code == 200:
                        hpa = r_hpa.json()
                        tissues = []
                        # RNA tissue distribution
                        rna_data = hpa.get("rna_tissue_distribution", {})
                        if isinstance(rna_data, dict):
                            for entry in rna_data.get("tissue", [])[:8]:
                                tissue = entry.get("tissue", "")
                                level = entry.get("level", "")
                                if tissue:
                                    tissues.append(f"{tissue} (RNA: {level})")
                        # Single cell type expression
                        sc_data = hpa.get("cell_type_expression", {})
                        if isinstance(sc_data, dict) and not tissues:
                            for entry in sc_data.get("cellType", [])[:6]:
                                cell = entry.get("cellType", "")
                                tcells = entry.get("tissueCellType", "")
                                level = entry.get("level", "")
                                label = entry.get("enrichedIn", "")
                                if cell:
                                    src = f"{tcells} {cell}" if tcells else cell
                                    tissues.append(f"{src} (SC: {level})")
                        if tissues:
                            return ("humanbase", {"humanbase_tissues": tissues[:8]})
                    else:
                        logger.warning(f"HPA JSON for {ensembl_id}: HTTP {r_hpa.status_code}")
            except Exception as e:
                logger.warning(f"HumanBase HPA route {gene}: {e}")

            # Fallback 1: Jensen Lab TISSUES
            try:
                r = _req.get(
                    "https://tissues.jensenlab.org/api/entity",
                    params={"format": "json", "type": "9606", "term": gene, "limit": 10},
                    timeout=10,
                )
                if r.status_code == 200:
                    data = r.json()
                    tissues = []
                    for item in data[:10]:
                        tissue = item.get("tissue", item.get("name", ""))
                        score = item.get("score", item.get("confidence", ""))
                        source = item.get("source", "")
                        if tissue:
                            entry = tissue
                            if score:
                                entry += f" (score={score})"
                            if source:
                                entry += f" [{source}]"
                            tissues.append(entry)
                    if tissues:
                        return ("humanbase", {"humanbase_tissues": tissues[:8]})
            except Exception as _le2:
                logger.warning(f"Extra literature failed: {_le2}")

            # Fallback 2: MyGene expression field
            try:
                r3 = _req.get(
                    "https://mygene.info/v3/query",
                    params={"q": gene, "species": "human", "fields": "expression"},
                    timeout=10,
                )
                hits = r3.json().get("hits", [])
                if hits:
                    expr = hits[0].get("expression", {})
                    if isinstance(expr, dict) and expr:
                        tissues = [
                            f"{t} (expr={v})"
                            for t, v in sorted(
                                expr.items(),
                                key=lambda x: float(x[1]) if isinstance(x[1], (int, float)) else 0,
                                reverse=True
                            )[:8]
                        ]
                        if tissues:
                            return ("humanbase", {"humanbase_tissues": tissues})
            except Exception as e:
                logger.warning(f"HumanBase MyGene fallback {gene}: {e}")
            return ("humanbase", {})

        def _fetch_civic(gene: str) -> tuple:
            """Query CIViC for cancer variant clinical evidence using POST GraphQL."""
            try:
                r = _req.post(
                    "https://civicdb.org/api/graphql",
                    json={
                        "query": """
                            query SearchGene($geneSymbol: String!) {
                              genes(entrezSymbols: [$geneSymbol]) {
                                nodes {
                                  id
                                  name
                                  variants {
                                    totalCount
                                    nodes {
                                      id
                                      name
                                      variantTypes { name }
                                    }
                                  }
                                }
                              }
                            }
                        """,
                        "variables": {"geneSymbol": gene}
                    },
                    headers={"Content-Type": "application/json", "Accept": "application/json"},
                    timeout=15,
                )
                if r.status_code == 200:
                    data = r.json()
                    if "errors" in data:
                        logger.warning(f"CIViC GraphQL errors for {gene}: {data['errors']}")
                    genes_data = data.get("data", {}).get("genes", {}).get("nodes", [])
                    if genes_data:
                        variants = genes_data[0].get("variants", {}).get("nodes", [])[:10]
                        variant_names = [v.get("name", "") for v in variants if v.get("name")]
                        if variant_names:
                            return ("civic", {"civic_variants": variant_names[:8]})
                else:
                    logger.warning(f"CIViC {gene}: HTTP {r.status_code} {r.text[:200]}")
            except Exception as e:
                _mark_source_failure("civic", gene, str(e))
                logger.warning(f"CIViC {gene}: {e}")
            return ("civic", {})

        def _fetch_alliance(gene: str) -> tuple:
            """Query Alliance of Genome Resources for cross-species homologs.
            Uses search_autocomplete endpoint which returns multi-species hits directly.
            """
            return _fetch_verified_source("alliance", gene)
            try:
                r = _req.get(
                    "https://www.alliancegenome.org/api/search_autocomplete",
                    params={"q": gene, "category": "gene"},
                    headers={"Accept": "application/json"},
                    timeout=12,
                )
                if r.status_code == 200:
                    hits = r.json().get("results", [])
                    _sp_map = {
                        "Hsa": "Homo sapiens", "Mmu": "Mus musculus",
                        "Rno": "Rattus norvegicus", "Dre": "Danio rerio",
                        "Dme": "Drosophila melanogaster", "Cel": "C. elegans",
                        "Sce": "S. cerevisiae", "Xla": "Xenopus laevis",
                    }
                    species_map = {}
                    for h in hits[:20]:
                        if h.get("category") != "gene":
                            continue
                        symbol = h.get("symbol", "") or h.get("name", "")
                        name_key = h.get("name_key", "")
                        primary_key = h.get("primaryKey", "")
                        sp_abbrev = ""
                        if name_key and "(" in name_key:
                            sp_abbrev = name_key.split("(")[-1].rstrip(")")
                        species = _sp_map.get(sp_abbrev, sp_abbrev) if sp_abbrev else primary_key.split(":")[0]
                        if symbol and species and species != "Homo sapiens":
                            if species not in species_map:
                                species_map[species] = []
                            if symbol not in species_map[species]:
                                species_map[species].append(symbol)
                    homolog_summary = [
                        f"{sp}: {', '.join(syms[:3])}"
                        for sp, syms in list(species_map.items())[:6]
                    ]
                    if homolog_summary:
                        return ("alliance", {"alliance_homologs": homolog_summary})
            except Exception as e:
                logger.warning(f"Alliance {gene}: {e}")
            return ("alliance", {})

        def _fetch_hpa(gene: str) -> tuple:
            """Query the Human Protein Atlas, kept separate from GTEx."""
            return _fetch_verified_source("hpa", gene)

        def _fetch_cbioportal(gene: str) -> tuple:
            """Query the public cBioPortal gene catalog."""
            return _fetch_verified_source("cbioportal", gene)

        def _fetch_omnipath(gene: str) -> tuple:
            """Query OmniPath directed and physical/signalling evidence."""
            return _fetch_verified_source("omnipath", gene)

        def _fetch_intact(gene: str) -> tuple:
            """Query IntAct through the PSI-MITAB/PSICQUIC service."""
            return _fetch_verified_source("intact", gene)

        # ------------------------------------------------------------------ #
        # Phase 1: query each gene -- online APIs in parallel, local DBs serial
        # ------------------------------------------------------------------ #
        genes_to_query = genes  # No upper cap — agent/caller decides how many genes to pass
        total_genes = len(genes_to_query)
        # Calculate total steps for percentage: each gene has online APIs + local DBs
        # Phase 1 (gene queries): 1-80%, Phase 2 (pubmed): 81-100%
        for gene_idx, gene in enumerate(genes_to_query, 1):
            _check_abort()  # Check abort at start of each gene
            pct = int((gene_idx - 1) / total_genes * 80)
            # Return cached result immediately
            _cache_lock = self._get_gene_cache_lock()
            with _cache_lock:
                _cached = self._gene_cache.get(gene)
            if _cached is not None:
                _cached_info = dict(_cached)
                _custom_records = query_annotations(gene, max_results=20)
                if _custom_records:
                    _cached_info["custom_gene_annotations_records"] = _custom_records
                knowledge["genes"][gene] = _cached_info
                _record_cached_source_hits(gene, _cached)
                if _custom_records:
                    _src_stats["dbs"].setdefault(
                        "custom_gene_annotations",
                        {"hit_genes": set(), "total_genes": len(genes), "status_counts": {}},
                    )["hit_genes"].add(gene)
                logger.info(f"[进度] [{label}] [{gene}] {pct}% ({gene_idx}/{total_genes}) [OK] 使用缓存结果")
                if progress_callback:
                    progress_callback(f"[进度] [{label}] [{gene}] {pct}% [{gene_idx}/{total_genes}] 使用缓存结果")
                continue
            gk: dict = {}
            _custom_records = query_annotations(gene, max_results=20)
            if _custom_records:
                gk["custom_gene_annotations_records"] = _custom_records
                _src_stats["dbs"].setdefault(
                    "custom_gene_annotations",
                    {"hit_genes": set(), "total_genes": len(genes), "status_counts": {}},
                )["hit_genes"].add(gene)
                _record_source_status("custom_gene_annotations", "ok")
            elif "custom_gene_annotations" in _src_stats.get("dbs", {}):
                _record_source_status("custom_gene_annotations", "no_records")
            active_apis = [a.upper() for a in ["uniprot","mygene","ensembl","chembl"] if a in enabled_apis]
            _start_msg = f"[进度] [{label}] [{gene}] {pct}% ({gene_idx}/{total_genes}) 正在查询 {' / '.join(active_apis) if active_apis else '(无在线 API)'} ..."
            logger.info(_start_msg)
            if progress_callback:
                progress_callback(_start_msg)

            # Submit every enabled online API for this gene at once.  The
            # worker count follows the enabled source count; sources are not
            # silently dropped.  Each task still has its own HTTP timeout.
            futures_map = {}
            logger.info(f"[进度] [{label}] [{gene}] 开始提交 {len(enabled_apis)} 个API查询...")
            if progress_callback:
                progress_callback(f"[进度] [{label}] [{gene}] 开始提交API查询...")
            _BATCH_TIMEOUT = 45  # Safety timeout for entire batch of API calls per gene (seconds)
            _batch_deadline = time.time() + _BATCH_TIMEOUT

            with ThreadPoolExecutor(max_workers=max(1, min(_MAX_SOURCE_WORKERS, len(enabled_apis)))) as pool:
                if "uniprot"      in enabled_apis: futures_map[pool.submit(_fetch_uniprot,      gene)] = "uniprot"
                if "mygene"       in enabled_apis: futures_map[pool.submit(_fetch_mygene,       gene)] = "mygene"
                if "ensembl"      in enabled_apis: futures_map[pool.submit(_fetch_ensembl,      gene)] = "ensembl"
                if "chembl"       in enabled_apis: futures_map[pool.submit(_fetch_chembl,       gene)] = "chembl"
                if "gtex"        in enabled_apis: futures_map[pool.submit(_fetch_gtex,         gene)] = "gtex"
                if "hpa"         in enabled_apis: futures_map[pool.submit(_fetch_hpa,          gene)] = "hpa"
                if "gwas"        in enabled_apis: futures_map[pool.submit(_fetch_gwas,         gene)] = "gwas"
                if "civic"       in enabled_apis: futures_map[pool.submit(_fetch_civic,        gene)] = "civic"
                if "alliance"    in enabled_apis: futures_map[pool.submit(_fetch_alliance,    gene)] = "alliance"
                if "reactome"    in enabled_apis: futures_map[pool.submit(_fetch_reactome,     gene)] = "reactome"
                if "opentargets" in enabled_apis: futures_map[pool.submit(_fetch_opentargets,  gene)] = "opentargets"
                if "cbioportal"  in enabled_apis: futures_map[pool.submit(_fetch_cbioportal,   gene)] = "cbioportal"
                if "omnipath"    in enabled_apis: futures_map[pool.submit(_fetch_omnipath,     gene)] = "omnipath"
                if "intact"      in enabled_apis: futures_map[pool.submit(_fetch_intact,       gene)] = "intact"
                if "clinvar"    in enabled_apis: futures_map[pool.submit(_fetch_clinvar,      gene)] = "clinvar"
                if "humanbase"  in enabled_apis: futures_map[pool.submit(_fetch_verified_source, "humanbase", gene)] = "humanbase"
                if "clinicaltrials" in enabled_apis: futures_map[pool.submit(_fetch_verified_source, "clinicaltrials", gene)] = "clinicaltrials"
                for _custom_id in sorted(set(enabled_apis) & set(_custom_sources)):
                    futures_map[pool.submit(_fetch_verified_source, _custom_id, gene)] = _custom_id
                logger.info(f"[进度] [{label}] [{gene}] 已提交 {len(futures_map)} 个查询任务，等待完成...")
                if progress_callback:
                    progress_callback(f"[进度] [{label}] [{gene}] 已提交 {len(futures_map)} 个查询，等待完成...")
                for fut in as_completed(futures_map):
                    _check_abort()  # Check abort after each completion
                    api_name = futures_map[fut].lower()
                    try:
                        _, data = fut.result()
                        gk.update(data)
                        if data:
                            _src_stats["apis"].setdefault(api_name, {"hit_genes": set(), "total_genes": len(genes)})
                            _src_stats["apis"][api_name]["hit_genes"].add(gene)
                        if api_name not in {
                            "gtex", "hpa", "opentargets", "alliance", "cbioportal",
                            "omnipath", "intact", "humanbase", "clinicaltrials",
                            *set(_custom_sources),
                        }:
                            _record_source_status(
                                api_name,
                                "ok" if data else ("error" if _source_failed(api_name, gene) else "no_records"),
                            )
                        logger.info(f"[进度] [{label}] [{gene}] {pct}% ({gene_idx}/{total_genes}) [{api_name.upper()}] [OK]")
                        if progress_callback:
                            progress_callback(f"[进度] [{label}] [{gene}] {pct}% [{api_name.upper()}] OK")
                    except Exception as _api_e:
                        _record_source_status(api_name, "error", str(_api_e))
                        logger.info(f"[进度] [{label}] [{gene}] {pct}% ({gene_idx}/{total_genes}) [{api_name.upper()}] [FAIL]")
                        if progress_callback:
                            progress_callback(f"[进度] [{label}] [{gene}] {pct}% [{api_name.upper()}] FAIL")
            _completed = sum(1 for _ in futures_map.values())  # Count total submitted
            logger.info(f"[进度] [{label}] [{gene}] API查询完成，共{_completed}/{len(futures_map)}个")
            if progress_callback:
                progress_callback(f"[进度] [{label}] [{gene}] API查询完成，{_completed}/{len(futures_map)}个")

            # QuickGO needs accession from UniProt (sequential dependency)
            accession = gk.get("uniprot_accession", "")
            if accession and "quickgo" in enabled_apis:
                _qg_msg = f"[进度] [{label}] [{gene}] {pct}% ({gene_idx}/{total_genes}) 正在查询 [QuickGO] GO注释 ..."
                logger.info(_qg_msg)
                if progress_callback:
                    progress_callback(_qg_msg)
                _, qg_data = _fetch_quickgo(gene, accession)
                gk.update(qg_data)
                if qg_data:
                    _src_stats["apis"].setdefault("quickgo", {"hit_genes": set(), "total_genes": len(genes)})
                    _src_stats["apis"]["quickgo"]["hit_genes"].add(gene)
                _record_source_status("quickgo", "ok" if qg_data else "no_records")
                logger.info(f"[进度] [{label}] [{gene}] {pct}% ({gene_idx}/{total_genes}) [QuickGO] [OK]")
                if progress_callback:
                    progress_callback(f"[进度] [{label}] [{gene}] {pct}% [QuickGO] GO注释 OK")
            elif "quickgo" in enabled_apis:
                # QuickGO requires a UniProt accession.  A missing accession
                # after a transport failure must not be presented as a real
                # biological zero or as an unqueried source.
                _record_source_status(
                    "quickgo",
                    "error" if _source_failed("uniprot", gene) else "no_records",
                    "UniProt accession unavailable; QuickGO query was not possible"
                    if _source_failed("uniprot", gene) else "",
                )

            # Local DBs (fast, serial) -- only those enabled by user
            active_dbs = [d.upper() for d in ["string","hmdb","trrust","gutmgene"] if d in enabled_dbs]
            if active_dbs:
                _db_msg = f"[进度] [{label}] [{gene}] {pct}% ({gene_idx}/{total_genes}) 正在查询本地数据库 [{' / '.join(active_dbs)}] ..."
                logger.info(_db_msg)
                if progress_callback:
                    progress_callback(_db_msg)
            if "string" in enabled_dbs:
                try:
                    with STRINGDatabase() as db:
                        interactions = db.get_interactions(gene, min_score=0.4)
                        partners = []
                        for iact in interactions[:10]:
                            src = iact.get("source_gene", "")
                            tgt = iact.get("target_gene", "")
                            p = tgt if src == gene else src
                            # STRING CSV uses 'weight' column (0-1 range); fall back to combined_score (0-1000)
                            raw_score = iact.get("weight") or iact.get("combined_score") or iact.get("score") or 0
                            try:
                                raw_score = float(raw_score)
                            except (ValueError, TypeError):
                                raw_score = 0.0
                            score = round(raw_score / 1000.0, 3) if raw_score > 1 else round(raw_score, 3)
                            if p and p != gene and p not in (None, ""):
                                partners.append({"partner": p, "score": score})
                        if partners:
                            gk["interactions"] = partners
                            _src_stats["dbs"].setdefault("string", {"hit_genes": set(), "total_genes": len(genes)})
                            _src_stats["dbs"]["string"]["hit_genes"].add(gene)
                        _record_source_status("string", "ok" if partners else "no_records")
                    logger.info(f"[进度] [{label}] [{gene}] {pct}% ({gene_idx}/{total_genes}) [STRING] [OK] {len(partners)} 互作")
                except Exception as e:
                    logger.info(f"[进度] [{label}] [{gene}] {pct}% ({gene_idx}/{total_genes}) [STRING] [FAIL]")
                    _mark_source_failure("string", gene, str(e))
                    logger.warning(f"STRING {gene}: {e}")

            if "hmdb" in enabled_dbs:
                try:
                    with HMDBDatabase() as db:
                        metabolites = db.get_metabolites(gene)
                        if metabolites:
                            # metabolite_name is the primary column in new HMDB CSV format
                            gk["metabolites"] = [
                                {"name": m.get("metabolite_name", ""),
                                 "protein_type": m.get("protein_type", "")}
                                for m in metabolites[:5]
                                if m.get("metabolite_name")
                            ]
                    n_met = len(gk.get("metabolites", []))
                    if n_met > 0:
                        _src_stats["dbs"].setdefault("hmdb", {"hit_genes": set(), "total_genes": len(genes)})
                        _src_stats["dbs"]["hmdb"]["hit_genes"].add(gene)
                    _record_source_status("hmdb", "ok" if n_met > 0 else "no_records")
                    logger.info(f"[进度] [{label}] [{gene}] {pct}% ({gene_idx}/{total_genes}) [HMDB] [OK] {n_met} 代谢物")
                except Exception as e:
                    logger.info(f"[进度] [{label}] [{gene}] {pct}% ({gene_idx}/{total_genes}) [HMDB] [FAIL]")
                    _mark_source_failure("hmdb", gene, str(e))
                    logger.warning(f"HMDB {gene}: {e}")

            if "trrust" in enabled_dbs:
                try:
                    with TRRUSTDatabase() as db:
                        tf_targets = db.get_targets(gene)
                        regulators = db.get_regulators(gene)
                        has_trrust_data = False
                        if tf_targets:
                            gk["tf_targets"] = [
                                {"target_gene": t.get("target_gene", ""),
                                 "effect": t.get("function", t.get("mode", ""))}
                                for t in tf_targets[:5] if t.get("target_gene")
                            ]
                            has_trrust_data = True
                        if regulators:
                            gk["regulators"] = [
                                {"tf": r.get("tf", ""),
                                 "effect": r.get("function", r.get("mode", ""))}
                                for r in regulators[:5] if r.get("tf")
                            ]
                            has_trrust_data = True
                        if has_trrust_data:
                            _src_stats["dbs"].setdefault("trrust", {"hit_genes": set(), "total_genes": len(genes)})
                            _src_stats["dbs"]["trrust"]["hit_genes"].add(gene)
                        _record_source_status("trrust", "ok" if has_trrust_data else "no_records")
                    logger.info(f"[进度] [{label}] [{gene}] ({gene_idx}/{total_genes}) [TRRUST] [OK]")
                except Exception as e:
                    _mark_source_failure("trrust", gene, str(e))
                    logger.warning(f"TRRUST {gene}: {e}")
                    logger.info(f"[进度] [{label}] [{gene}] ({gene_idx}/{total_genes}) [TRRUST] [FAIL]")

            if "gutmgene" in enabled_dbs:
                try:
                    with GUTMGENEDatabase() as db:
                        microbes = db.get_microbes(gene)
                        if microbes:
                            gk["gut_microbes"] = [
                                {
                                    "microbe": m.get("gut_microbiota", m.get("microbe", "")),
                                    "Alteration": m.get("Alteration", ""),
                                    "Condition": m.get("Condition", ""),
                                    "PMID": m.get("PMID", ""),
                                }
                                for m in microbes[:5]
                                if m.get("gut_microbiota") or m.get("microbe")
                            ]
                            if gk.get("gut_microbes"):
                                _src_stats["dbs"].setdefault("gutmgene", {"hit_genes": set(), "total_genes": len(genes)})
                                _src_stats["dbs"]["gutmgene"]["hit_genes"].add(gene)
                        _record_source_status("gutmgene", "ok" if gk.get("gut_microbes") else "no_records")
                    logger.info(f"[进度] [{label}] [{gene}] ({gene_idx}/{total_genes}) [GUTMGENE] [OK]")
                except Exception as e:
                    _mark_source_failure("gutmgene", gene, str(e))
                    logger.warning(f"GUTMGENE {gene}: {e}")

            # Cache and store
            with _cache_lock:
                self._gene_cache[gene] = dict(gk)
                knowledge["genes"][gene] = gk

        _check_abort()  # Check abort before starting PubMed queries

        # ------------------------------------------------------------------ #
        # Phase 2: PubMed + EuropePMC -- queries across four biological layers
        #   Layer 1: Function  (UniProt/MyGene/QuickGO/Ensembl level)
        #   Layer 2: Target    (ChEMBL level)
        #   Layer 3: Interaction (STRING/TRRUST level)
        #   Layer 4: Microbiome  (GUTMGENE level)
        # ------------------------------------------------------------------ #
        def _build_lit_queries(gene: str) -> list:
            """Return one reliable gene-level query for the durable first pass.

            The question-time literature planner performs richer,
            question-specific searches.  The initial selected-gene pass only
            needs one query per selected gene; issuing generic variants for
            every gene creates redundant NCBI requests and makes a transport
            failure look like a biological coverage failure.
            """
            return [str(gene).strip()] if str(gene).strip() else []

        def _fetch_pubmed(gene: str) -> list:
            """Fetch one gene-level PubMed result with failure aggregation."""
            arts = []
            seen = set()
            query_failures = 0
            last_error = ""
            try:
                pm_client = self.api_clients.get("pubmed")
                if not pm_client:
                    _mark_source_failure("pubmed", gene, "PubMed client is not configured")
                    return arts
                for q in _build_lit_queries(gene):
                    try:
                        pm = pm_client.search_and_get_details(q.strip(), max_results=10)
                        # Enhanced/standalone PubMed clients return a
                        # structured error for a transport failure.  Do not
                        # turn that failure into a biological "no records"
                        # result in the coverage audit.
                        if isinstance(pm, dict) and (
                            str(pm.get("status", "")).lower() in {"error", "unavailable"}
                            or pm.get("error")
                        ):
                            query_failures += 1
                            last_error = str(pm.get("error") or pm.get("status") or "PubMed query failed")
                            continue
                        if not isinstance(pm, dict):
                            query_failures += 1
                            last_error = "PubMed client returned a non-object response"
                            continue
                        for art in pm.get("articles", []):
                            pmid = art.get("pmid", "")
                            if pmid and pmid not in seen:
                                seen.add(pmid)
                                art["gene"] = gene
                                art["query"] = q
                                arts.append(art)
                    except Exception as query_error:
                        query_failures += 1
                        last_error = str(query_error)
            except Exception as e:
                query_failures += 1
                last_error = str(e)
                logger.warning(f"PubMed {gene}: {e}")
            query_count = len(_build_lit_queries(gene))
            if query_failures and not arts and query_failures >= query_count:
                _mark_source_failure("pubmed", gene, last_error or "PubMed query failed")
            return arts[:8]  # cap per gene

        if "pubmed" in enabled_apis:
            _check_abort()  # Check abort before starting PubMed queries
            _pm_genes = genes_to_query  # no cap — query all selected genes
            _initial_literature_queries["pubmed"] = sum(
                len(_build_lit_queries(gene)) for gene in _pm_genes
            )
            logger.info(f"[进度] [{label}] 81% 并发查询 PubMed 文献 ({len(_pm_genes)} genes, 1 query/gene) ...")
            if progress_callback:
                progress_callback(f"[进度] 开始查询 PubMed ({len(_pm_genes)} genes) ...")
            with ThreadPoolExecutor(max_workers=max(1, min(_MAX_SOURCE_WORKERS, len(_pm_genes)))) as pool:
                pubmed_futures = {pool.submit(_fetch_pubmed, g): g for g in _pm_genes}
                done_count = 0
                for fut in as_completed(pubmed_futures):
                    _check_abort()  # Check abort after each completion
                    done_count += 1
                    pct = 81 + int(done_count / len(pubmed_futures) * 9)
                    g = pubmed_futures[fut]
                    arts = fut.result()
                    _record_source_status(
                        "pubmed",
                        "ok" if arts else ("error" if _source_failed("pubmed", g) else "no_records"),
                    )
                    if arts and "pubmed" in _src_stats.get("apis", {}):
                        _src_stats["apis"]["pubmed"]["hit_genes"].add(g)
                    logger.info(f"[进度] [{label}] {pct}% [PubMed] [{g}] {str(len(arts)) + ' articles' if arts else 'no results'}")
                    if progress_callback:
                        progress_callback(f"[进度] PubMed [{g}] {pct}% {str(len(arts)) + ' articles' if arts else 'no results'}")
                    for art in arts:
                        if art.get("pmid") not in seen_pmids:
                            seen_pmids.add(art.get("pmid"))
                            knowledge["pubmed"].append(art)

            # Log final PubMed summary
            logger.info(f"[进度] [{label}] PubMed 查询完成: {len(knowledge['pubmed'])} 篇文献")
            if progress_callback:
                progress_callback(f"[进度] PubMed 查询完成: {len(knowledge['pubmed'])} 篇文献")

        if "europepmc" in enabled_apis:
            _check_abort()  # Check abort before starting EuropePMC queries
            _epmc_genes = genes_to_query  # no cap — query every selected gene
            logger.info(f"[进度] [{label}] 92% 并发查询 Europe PMC 文献 ({len(_epmc_genes)} genes, 1 query/gene) ...")
            if progress_callback:
                progress_callback(f"[进度] 开始查询 EuropePMC ({len(_epmc_genes)} genes) ...")

            def _fetch_europepmc_gene(gene: str) -> tuple[list, int]:
                """Run one gene-level Europe PMC search for the durable pass."""
                epmc_queries = [str(gene).strip()] if str(gene).strip() else []
                records, seen = [], set()
                query_failures = 0
                for eq in epmc_queries:
                    try:
                        r = _req.get(
                            "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                            params={"query": eq, "resultType": "lite", "pageSize": 10, "format": "json"},
                            timeout=12,
                        )
                        r.raise_for_status()
                        hits = r.json().get("resultList", {}).get("result", [])
                        for art in hits:
                            pmid = art.get("pmid", "") or art.get("id", "")
                            if pmid and pmid not in seen:
                                seen.add(pmid)
                                records.append({
                                    "pmid": pmid,
                                    "gene": gene,
                                    "title": art.get("title", ""),
                                    "abstract": art.get("abstractText", ""),
                                    "journal": art.get("journalTitle", ""),
                                    "citations": art.get("citedByCount", 0),
                                    "pub_year": art.get("pubYear", ""),
                                    "query_layer": eq[:120],
                                    "url": f"https://europepmc.org/article/MED/{pmid}",
                                })
                    except Exception as _eq_e:
                        query_failures += 1
                        logger.warning(f"EuropePMC query '{eq[:40]}': {_eq_e}")
                if query_failures == len(epmc_queries) and epmc_queries:
                    _mark_source_failure(
                        "europepmc", gene,
                        "all Europe PMC queries failed for this expression item",
                    )
                return records[:20], len(epmc_queries)

            epmc_workers = max(1, min(_MAX_SOURCE_WORKERS, len(_epmc_genes)))
            epmc_futures = {}
            with ThreadPoolExecutor(max_workers=epmc_workers) as pool:
                epmc_futures = {pool.submit(_fetch_europepmc_gene, gene): gene for gene in _epmc_genes}
                epmc_seen = set()
                for fut in as_completed(epmc_futures):
                    _check_abort()
                    gene = epmc_futures[fut]
                    try:
                        records, n_queries = fut.result()
                        _initial_literature_queries["europepmc"] += n_queries
                        _record_source_status(
                            "europepmc",
                            "ok" if records else ("error" if _source_failed("europepmc", gene) else "no_records"),
                        )
                        if records and "europepmc" in _src_stats.get("apis", {}):
                            _src_stats["apis"]["europepmc"]["hit_genes"].add(gene)
                        for record in records:
                            pmid = record.get("pmid")
                            if pmid and pmid not in epmc_seen:
                                epmc_seen.add(pmid)
                                knowledge["europepmc"].append(record)
                    except Exception as _epmc_error:
                        _initial_literature_queries["europepmc"] += 1
                        _record_source_status("europepmc", "error", str(_epmc_error))
                        logger.warning(f"EuropePMC {gene}: {_epmc_error}")
            logger.info(f"[进度] [{label}] 96% [EuropePMC] {len(knowledge['europepmc'])} articles")
            if progress_callback:
                progress_callback(f"[进度] EuropePMC 完成: {len(knowledge['europepmc'])} articles")

        logger.info(f"[进度] [{label}] 100% 知识查询完成: {len(knowledge['genes'])} 基因, {len(knowledge['pubmed'])} 篇文献")
        if progress_callback:
            progress_callback(f"[进度] 100% 知识查询完成: {len(knowledge['genes'])} 基因, {len(knowledge['pubmed'])} 篇文献")

        # Build source stats report from tracked data
        total_genes = _src_stats["total_genes"]
        apis_hit = sum(1 for s in _src_stats["apis"].values() if s["hit_genes"])
        dbs_hit = sum(1 for s in _src_stats["dbs"].values() if s["hit_genes"])

        # Serialize sets to lists for JSON transport
        _final_stats = {
            "total_genes_queried": total_genes,
            "apis_hit_count": apis_hit,
            "dbs_hit_count": dbs_hit,
            "total_sources_hit": apis_hit + dbs_hit,
            "total_sources_enabled": len(_src_stats["apis"]) + len(_src_stats["dbs"]),
            "enabled_apis": sorted(enabled_apis),
            "enabled_dbs": sorted(enabled_dbs),
            "apis": {
                name: {
                    "hit_count": len(st["hit_genes"]),
                    "total_genes": st["total_genes"],
                    "pct": round(len(st["hit_genes"]) / st["total_genes"] * 100) if st["total_genes"] > 0 else 0,
                    "hit_genes": list(st["hit_genes"]),
                    "status_counts": dict(st.get("status_counts", {})),
                    "errors": list(st.get("errors", []) or []),
                }
                for name, st in _src_stats["apis"].items()
            },
            "dbs": {
                name: {
                    "hit_count": len(st["hit_genes"]),
                    "total_genes": st["total_genes"],
                    "pct": round(len(st["hit_genes"]) / st["total_genes"] * 100) if st["total_genes"] > 0 else 0,
                    "hit_genes": list(st["hit_genes"]),
                    "status_counts": dict(st.get("status_counts", {})),
                    "errors": list(st.get("errors", []) or []),
                }
                for name, st in _src_stats["dbs"].items()
            },
            "pubmed_articles": len(knowledge.get("pubmed", [])),
            "europepmc_articles": len(knowledge.get("europepmc", [])),
            "initial_literature_queries": dict(_initial_literature_queries),
        }
        knowledge["_source_stats"] = _final_stats

        # NOTE: Per-group vector store build is intentionally removed here.
        # The unified reset_and_build is called once at the end of build_knowledge_base()
        # so that all groups' knowledge is merged into a single collection.
        return knowledge


    def _build_group_knowledge_parallel(
        self,
        label: str,
        genes: list,
        context_hint: str = "",
        enabled_apis=None,
        enabled_dbs=None,
        progress_callback=None,
        abort_flag: Optional[threading.Event] = None,
        max_gene_workers: int = 6,
    ) -> dict:
        """Retrieve every selected gene with bounded gene-level concurrency.

        ``_build_group_knowledge`` already fans out the enabled sources for one
        gene.  Calling it once for a 1,000-gene cohort used to leave the genes
        themselves serial, so a first-question Agent RAG run could take hours.
        This wrapper keeps the source fan-out bounded while processing several
        disjoint gene batches concurrently.  It is network-bound concurrency;
        it does not create a CPU worker per gene and it preserves the complete
        per-gene source records before synthesis.
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        from e2seq.api import AbortChat as _AbortChat

        unique_genes = list(dict.fromkeys(
            str(g).strip() for g in (genes or []) if str(g).strip()
        ))
        if not unique_genes:
            return {
                "genes": {},
                "pubmed": [],
                "europepmc": [],
                "_source_stats": {
                    "total_genes": 0,
                    "total_genes_queried": 0,
                    "enabled_apis": sorted(set(enabled_apis or [])),
                    "enabled_dbs": sorted(set(enabled_dbs or [])),
                    "apis": {},
                    "dbs": {},
                },
            }

        if abort_flag is not None and abort_flag.is_set():
            raise _AbortChat("User requested abort")

        worker_count = max(1, min(int(max_gene_workers or 6), len(unique_genes)))
        if len(unique_genes) <= worker_count:
            return self._build_group_knowledge(
                label,
                unique_genes,
                context_hint=context_hint,
                enabled_apis=set(enabled_apis or []),
                enabled_dbs=set(enabled_dbs or []),
                progress_callback=progress_callback,
                abort_flag=abort_flag,
            )

        chunk_size = max(1, (len(unique_genes) + worker_count - 1) // worker_count)
        batches = [
            unique_genes[start:start + chunk_size]
            for start in range(0, len(unique_genes), chunk_size)
        ]
        source_apis = set(enabled_apis or [])
        source_dbs = set(enabled_dbs or [])
        accumulated = {
            "genes": {},
            "pubmed": [],
            "europepmc": [],
            "_source_stats": {
                "total_genes": len(unique_genes),
                "total_genes_queried": len(unique_genes),
                "enabled_apis": sorted(source_apis),
                "enabled_dbs": sorted(source_dbs),
                "apis": {},
                "dbs": {},
            },
        }

        def _run_batch(batch_index: int, batch_genes: list) -> dict:
            if abort_flag is not None and abort_flag.is_set():
                raise _AbortChat("User requested abort")

            def _batch_progress(message: str) -> None:
                if progress_callback:
                    progress_callback(
                        "[gene batch {}/{}] {}".format(
                            batch_index, len(batches), message
                        )
                    )

            logger.info(
                "[AgenticRAG] Gene batch {}/{} started: {} genes (workers={})".format(
                    batch_index, len(batches), len(batch_genes), worker_count
                )
            )
            result = self._build_group_knowledge(
                "{}/genes-{}".format(label, batch_index),
                batch_genes,
                context_hint=context_hint,
                enabled_apis=set(source_apis),
                enabled_dbs=set(source_dbs),
                progress_callback=_batch_progress,
                abort_flag=abort_flag,
            )
            logger.info(
                "[AgenticRAG] Gene batch {}/{} complete: {} genes".format(
                    batch_index, len(batches), len(batch_genes)
                )
            )
            return result

        with ThreadPoolExecutor(max_workers=worker_count) as pool:
            futures = {
                pool.submit(_run_batch, index, batch): index
                for index, batch in enumerate(batches, 1)
            }
            try:
                for future in as_completed(futures):
                    if abort_flag is not None and abort_flag.is_set():
                        for pending in futures:
                            pending.cancel()
                        raise _AbortChat("User requested abort")
                    self._merge_rag_knowledge(accumulated, future.result())
            except Exception:
                for pending in futures:
                    pending.cancel()
                raise

        stats = accumulated.setdefault("_source_stats", {})
        stats["total_genes"] = len(unique_genes)
        stats["total_genes_queried"] = len(unique_genes)
        for category in ("apis", "dbs"):
            for source_info in stats.get(category, {}).values():
                source_info["total_genes"] = len(unique_genes)
                source_info["pct"] = round(
                    len(source_info.get("hit_genes", [])) / len(unique_genes) * 100
                ) if unique_genes else 0

        logger.info(
            "[AgenticRAG] Parallel retrieval complete: {} genes, {} batches, {} APIs, {} DBs".format(
                len(unique_genes), len(batches), len(source_apis), len(source_dbs)
            )
        )
        return accumulated


    def _merge_rag_knowledge(self, accum: dict, new_kb: dict) -> None:
        """Merge newly retrieved records without overwriting existing evidence.

        This is used both for new genes and for a reopened session where the
        planner asks for a source that was not present in the persisted
        snapshot.  The previous ``dict.update`` behaviour replaced a gene's
        complete record with only the newly fetched source fields.
        """
        if not isinstance(accum, dict) or not isinstance(new_kb, dict):
            return
        target_genes = accum.setdefault("genes", {})
        for gene, info in (new_kb.get("genes", {}) or {}).items():
            if isinstance(target_genes.get(gene), dict) and isinstance(info, dict):
                target_genes[gene].update(info)
            else:
                target_genes[gene] = info

        for key in ("pubmed", "europepmc"):
            target = accum.setdefault(key, [])
            seen = {
                str(item.get("pmid") or item.get("id"))
                for item in target
                if isinstance(item, dict) and (item.get("pmid") or item.get("id"))
            }
            for item in new_kb.get(key, []) or []:
                if not isinstance(item, dict):
                    continue
                item_id = item.get("pmid") or item.get("id")
                dedupe_key = str(item_id) if item_id else repr(item)
                if dedupe_key not in seen:
                    seen.add(dedupe_key)
                    target.append(item)

        self._merge_source_stats(accum, new_kb)

    def _merge_source_stats(self, accum: dict, new_kb: dict) -> None:
        """Merge _source_stats from a refinement KB round into the accumulated knowledge dict."""
        ns = new_kb.get("_source_stats", {})
        if not ns:
            return
        acc_stats = accum.get("_source_stats")
        if acc_stats is None:
            accum["_source_stats"] = dict(ns)
            return
        for cat in ("apis", "dbs"):
            for name, info in ns.get(cat, {}).items():
                if name not in acc_stats.get(cat, {}):
                    acc_stats.setdefault(cat, {})[name] = {
                        "hit_genes": set(info.get("hit_genes", []) or []),
                        "hit_count": int(info.get("hit_count") or len(info.get("hit_genes", []) or [])),
                        "total_genes": info.get("total_genes", acc_stats.get("total_genes_queried", 0)),
                        "status_counts": dict(info.get("status_counts", {}) or {}),
                        "errors": list(info.get("errors", []) or []),
                    }
                else:
                    existing_hits = set(acc_stats[cat][name].get("hit_genes", []) or [])
                    existing_hits.update(info.get("hit_genes", []) or [])
                    acc_stats[cat][name]["hit_genes"] = existing_hits
                    acc_stats[cat][name]["hit_count"] = max(
                        int(acc_stats[cat][name].get("hit_count") or 0),
                        int(info.get("hit_count") or 0),
                        len(existing_hits),
                    )
                    existing_status = acc_stats[cat][name].setdefault("status_counts", {})
                    for status, count in (info.get("status_counts", {}) or {}).items():
                        existing_status[status] = int(existing_status.get(status, 0)) + int(count or 0)
                    existing_errors = acc_stats[cat][name].setdefault("errors", [])
                    for error in info.get("errors", []) or []:
                        if error not in existing_errors and len(existing_errors) < 3:
                            existing_errors.append(error)
        for key in ("enabled_apis", "enabled_dbs"):
            merged = set(acc_stats.get(key, []) or [])
            merged.update(ns.get(key, []) or [])
            acc_stats[key] = sorted(merged)
        acc_stats["total_genes_queried"] = max(
            int(acc_stats.get("total_genes_queried", 0) or 0),
            int(ns.get("total_genes_queried", 0) or 0),
        )
        acc_lit = acc_stats.setdefault("initial_literature_queries", {})
        for source in ("pubmed", "europepmc"):
            acc_lit[source] = int(acc_lit.get(source, 0) or 0) + int(
                (ns.get("initial_literature_queries", {}) or {}).get(source, 0) or 0
            )

    def _generate_source_report(self, stats: dict) -> str:
        """Format source stats as a readable markdown report."""
        total_genes = stats.get("total_genes_queried", 0)
        apis = stats.get("apis", {})
        dbs = stats.get("dbs", {})
        pubmed_n = stats.get("pubmed_articles", 0)
        europepmc_n = stats.get("europepmc_articles", 0)

        apis_hit = sum(1 for s in apis.values() if int(s.get("hit_count") or len(s.get("hit_genes", []) or [])) > 0)
        dbs_hit = sum(1 for s in dbs.values() if int(s.get("hit_count") or len(s.get("hit_genes", []) or [])) > 0)
        total_enabled = len(apis) + len(dbs)
        total_hit = apis_hit + dbs_hit

        lines = []
        lines.append("")
        lines.append("---")
        lines.append("**数据来源统计 | Data Source Coverage**")
        lines.append("")
        lines.append(f"**分析基因总数 (Total genes queried): {total_genes}**")
        lines.append(f"**文献检索 (Literature): PubMed {pubmed_n} 篇 + Europe PMC {europepmc_n} 篇**")
        lines.append("")
        lines.append("**在线 API | Online APIs**")
        lines.append("")

        api_order = ["uniprot","mygene","quickgo","ensembl","chembl","opentargets",
                     "clinvar","reactome","gtex","hpa","gwas","civic",
                     "alliance","cbioportal","omnipath","intact","humanbase",
                     "clinicaltrials","pubmed","europepmc"]
        api_order.extend(name for name in apis if name not in api_order)
        for name in api_order:
            if name not in apis:
                continue
            info = apis[name]
            hit = int(info.get("hit_count") or len(info.get("hit_genes", []) or []))
            pct = info.get("pct", 0)
            filled = int(pct / 5)
            bar = "[" + "\u2588" * filled + "\u2591" * (20 - filled) + "]"
            label = name.upper().replace("OPENTARGETS", "Open Targets").replace("CBIOPORTAL", "cBioPortal").replace("OMNIPATH", "OmniPath").replace("INTACT", "IntAct")
            status_counts = info.get("status_counts", {}) or {}
            if hit > 0 and (status_counts.get("error") or status_counts.get("unavailable") or status_counts.get("needs_configuration")):
                state = "partial; some queries failed"
            elif status_counts.get("needs_configuration"):
                state = "needs key"
            elif status_counts.get("error") or status_counts.get("unavailable"):
                state = "endpoint error"
            elif hit == 0 and status_counts.get("no_records"):
                state = "reachable; no records"
            else:
                state = "reachable"
            lines.append(f"  {label:16s} {bar:s} {hit:3d} / {total_genes:3d} ({pct:3d}%) — {state}")

        lines.append("")
        lines.append("**本地数据库 | Local Databases**")
        lines.append("")
        db_order = ["string", "hmdb", "trrust", "gutmgene"]
        db_order.extend(name for name in dbs if name not in db_order)
        for name in db_order:
            if name not in dbs:
                continue
            info = dbs[name]
            hit = int(info.get("hit_count") or len(info.get("hit_genes", []) or []))
            pct = info.get("pct", 0)
            filled = int(pct / 5)
            bar = "[" + "\u2588" * filled + "\u2591" * (20 - filled) + "]"
            label = name.upper()
            status_counts = info.get("status_counts", {}) or {}
            state = "reachable; no records" if hit == 0 and status_counts.get("no_records") else "reachable"
            lines.append(f"  {label:16s} {bar:s} {hit:3d} / {total_genes:3d} ({pct:3d}%) — {state}")

        lines.append("")
        lines.append(f"**汇总 | Summary: 有数据的数据源 {total_hit}/{total_enabled}**")
        lines.append("---")
        lines.append("")
        return "\n".join(lines)

    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history from memory system."""
        return self.memory.working_memory.conversation_history

    def clear_history(self) -> None:
        """Clear conversation history and start new session."""
        self.memory.clear_working_memory()
        self.state_manager.reset()
        logger.info("Conversation history cleared and new session started")

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return self.memory.get_memory_stats()

    def get_state_summary(self) -> Dict[str, Any]:
        """Get state manager summary."""
        return self.state_manager.get_execution_summary()

    def get_error_stats(self) -> Dict[str, Any]:
        """Get error recovery statistics."""
        return self.error_recovery.get_error_summary()

    def restore_from_checkpoint(self, checkpoint_name: str) -> bool:
        """Restore state from checkpoint."""
        return self.state_manager.restore_checkpoint(checkpoint_name)

    def list_checkpoints(self) -> List[str]:
        """List available checkpoints."""
        return self.state_manager.list_checkpoints()

