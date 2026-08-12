"""FastAPI backend for E2seq - Modern REST API."""

import os

# Use a custom Hugging Face endpoint only when explicitly configured.
# 仅在用户显式配置时使用自定义 Hugging Face 端点。
if not os.environ.get("HF_ENDPOINT") and os.environ.get("E2SEQ_HF_ENDPOINT"):
    os.environ["HF_ENDPOINT"] = os.environ["E2SEQ_HF_ENDPOINT"]
# 禁用 symlink 警告（Windows 非管理员模式）
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import asyncio
import json
import datetime as _datetime_module
import tempfile
import base64
import shutil
import uuid
from pathlib import Path
import scanpy as sc
import logging
import anyio
import threading as _threading

# Client disconnect exception types for SSE streaming
# These exceptions are raised when the client disconnects during streaming
try:
    from starlette.requests import ClientDisconnect
except ImportError:
    class ClientDisconnect(Exception):
        """Fallback when starlette.requests.ClientDisconnect is not available."""
        pass

# Tuple of exception types that indicate client disconnection
# Used to gracefully handle cases where client closes connection mid-stream
CLIENT_DISCONNECT_EXCEPTIONS = (asyncio.CancelledError, ClientDisconnect, OSError, ConnectionError)

from e2seq import E2seqAgent
from e2seq.analysis import BulkRNAAnalyzer, inspect_bulk_files, load_bulk_tables
from e2seq.analysis.bulk_rnaseq import (
    BulkAnalysisError,
    build_user_bulk_result,
    inspect_bulk_result_file,
    run_batch_enrichment,
    validate_bulk_configuration,
)
from e2seq.utils import get_config, get_security_manager
from e2seq.utils.config import DEFAULT_ANSWER_APIS, DEFAULT_ANSWER_DBS
from e2seq.utils.gene_intersection import normalize_gene_list
from e2seq.data.knowledge_sources import KnowledgeSourceClient
from e2seq.data.local_db import (
    GUTMGENEDatabase,
    HMDBDatabase,
    STRINGDatabase,
    TRRUSTDatabase,
)
from e2seq.data.custom_sources import (
    custom_source_catalog,
    load_custom_sources,
    public_custom_sources,
    save_custom_sources,
)
from e2seq.data.custom_annotations import parse_annotation_text, load_annotation_catalog

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="E2seq API - Easy to Chat with Sequencing", version="2.0.0")

# Answer-time source catalog.  The identifiers are also persisted in the
# user's configuration and passed to the agent, so keep them stable.
ANSWER_SOURCE_CATALOG = [
    {"id": "uniprot", "kind": "api"},
    {"id": "mygene", "kind": "api"},
    {"id": "quickgo", "kind": "api"},
    {"id": "ensembl", "kind": "api"},
    {"id": "chembl", "kind": "api"},
    {"id": "pubmed", "kind": "api"},
    {"id": "europepmc", "kind": "api"},
    {"id": "reactome", "kind": "api"},
    {"id": "gtex", "kind": "api"},
    {"id": "hpa", "kind": "api"},
    {"id": "gwas", "kind": "api"},
    {"id": "civic", "kind": "api"},
    {"id": "alliance", "kind": "api"},
    {"id": "opentargets", "kind": "api"},
    {"id": "clinvar", "kind": "api"},
    {"id": "cbioportal", "kind": "api"},
    {"id": "omnipath", "kind": "api"},
    {"id": "intact", "kind": "api"},
    {"id": "humanbase", "kind": "api"},
    {"id": "clinicaltrials", "kind": "api"},
    {"id": "string", "kind": "db"},
    {"id": "hmdb", "kind": "db"},
    {"id": "trrust", "kind": "db"},
    {"id": "gutmgene", "kind": "db"},
]
_ANSWER_API_IDS = {item["id"] for item in ANSWER_SOURCE_CATALOG if item["kind"] == "api"}
_ANSWER_DB_IDS = {item["id"] for item in ANSWER_SOURCE_CATALOG if item["kind"] == "db"}

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Timeout middleware: limit ONLY the streaming chat endpoint so a hung LLM
# call cannot leave the frontend stuck on "thinking" forever. The non-streaming
# /api/chat endpoint is intentionally uncapped — it is the fallback when the
# user does NOT want streaming (e.g. agent mode, batch analyses), and it must
# be allowed to wait as long as the LLM needs (large GLM/DeepSeek synthesis
# routinely takes 3-5 minutes). The SSE stream's per-chunk keepalive pings
# already prevent the browser from hanging on it.
_STREAM_TIMEOUT = 480  # seconds — only applied to /api/chat/stream


@app.middleware("http")
async def _chat_timeout_middleware(request: Request, call_next):
    if request.url.path in ("/api/chat/stream",):
        try:
            response = await asyncio.wait_for(call_next(request), timeout=_STREAM_TIMEOUT)
            return response
        except asyncio.TimeoutError:
            logger.error(f"[Timeout] {request.url.path} exceeded {_STREAM_TIMEOUT}s — returning error response")
            return JSONResponse(
                status_code=504,
                content={"detail": f"请求超时（超过{_STREAM_TIMEOUT // 60}分钟），可能是 LLM 接口响应过慢，请点击「中止」并重试，或更换为更快的模型。"}
            )
    return await call_next(request)

# Mount static files
static_path = Path(__file__).parent.parent / "web" / "static"
templates_path = Path(__file__).parent.parent / "web" / "templates"

if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Global state (in production, use Redis or database)
agents = {}
datasets = {}
# Bulk RNA-seq sessions deliberately stay separate from the legacy h5ad/table
# path until the user starts an analysis.  This lets the upload dialog preview
# and map columns without silently filtering or normalizing raw counts.
bulk_sessions: dict[str, dict[str, Any]] = {}
bulk_jobs: dict[str, asyncio.Task] = {}
_BULK_RAG_GENE_WORKERS = 4
_BULK_RAG_SESSION_LIMIT = 2
_bulk_rag_jobs: dict[str, dict[str, Any]] = {}
_bulk_rag_jobs_lock = _threading.Lock()
_bulk_rag_session_gate = _threading.BoundedSemaphore(_BULK_RAG_SESSION_LIMIT)
# A full-cohort R/Bioconductor model is deliberately single-slotted.  This
# keeps two browser chats independent while preventing concurrent DESeq2/Cox
# processes from starving each other and falling into the slow Python fallback.
_bulk_model_session_gate = _threading.BoundedSemaphore(1)
# Per-chat-id abort events — set by /api/chat/abort, checked by _stream_agent_chat
_abort_events: dict[str, asyncio.Event] = {}
# Chats deleted by the user are kept as a short-lived in-process tombstone so
# an already-running background task cannot write its dataset/RAG back after
# the delete request has completed.
_deleted_session_ids: set[str] = set()
# Shared exception raised inside agent thread when user aborts
class AbortChat(Exception):
    """Raised when the user clicks the abort button during agent execution."""
    pass

# Project-scoped user data. Override with E2SEQ_DATA_DIR when a different
# drive is preferred. Secrets remain in the user's encrypted config directory.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_STORAGE_ROOT = Path(
    os.environ.get("E2SEQ_DATA_DIR") or (_PROJECT_ROOT / ".e2seq" / "user_data")
).expanduser().resolve()
_DATASET_DIR = _STORAGE_ROOT / "datasets"
_CHAT_DIR = _STORAGE_ROOT / "chats"
_CUSTOM_DATABASE_DIR = _STORAGE_ROOT / "uploads" / "knowledge_bases"
for _storage_dir in (_DATASET_DIR, _CHAT_DIR, _CUSTOM_DATABASE_DIR):
    _storage_dir.mkdir(parents=True, exist_ok=True)

_LEGACY_DATASET_DIR = _PROJECT_ROOT / "_datasets"
_LEGACY_CHAT_DB_PATH = _PROJECT_ROOT / ".e2sc" / "chat_history.db"

def _dataset_path(session_id: str) -> Path:
    """Return the path where a session's h5ad is persisted."""
    # Sanitise session_id for use as filename
    safe = "".join(c for c in session_id if c.isalnum() or c in "-_")
    return _DATASET_DIR / f"{safe}.h5ad"

def _config_path(session_id: str) -> Path:
    """Return the path where a session's uns config is persisted."""
    safe = "".join(c for c in session_id if c.isalnum() or c in "-_")
    return _DATASET_DIR / f"{safe}_config.json"


def _bulk_file_path(session_id: str, kind: str, suffix: str) -> Path:
    safe = "".join(c for c in session_id if c.isalnum() or c in "-_") or "default"
    return _DATASET_DIR / f"{safe}_bulk_{kind}{suffix}"


def _bulk_json_safe(value: Any) -> Any:
    """Convert numpy/pandas values for API responses and persisted manifests."""
    return json.loads(json.dumps(value, default=str))


def _bulk_state_path(session_id: str) -> Path:
    """Return the durable manifest path for one expression-profile session."""
    safe = "".join(c for c in str(session_id or "default") if c.isalnum() or c in "-_") or "default"
    return _DATASET_DIR / f"{safe}_bulk_state.json"


def _answer_usage_path(session_id: str) -> Path:
    """Return the durable, credential-free model-usage path for one chat."""
    safe = "".join(c for c in str(session_id or "default") if c.isalnum() or c in "-_") or "default"
    return _DATASET_DIR / f"{safe}_answer_usage.json"


def _session_is_deleted(session_id: str) -> bool:
    """Return whether a session is currently being purged."""
    key = str(session_id or "default")
    if key in _deleted_session_ids:
        return True
    safe = "".join(c for c in key if c.isalnum() or c in "-_") or "default"
    return (_DATASET_DIR / f".{safe}.deleted").is_file()


_ANSWER_USAGE_LOCK = _threading.Lock()


def _persist_answer_usage(
    session_id: str,
    usage: Optional[dict],
    source_stats: Optional[dict] = None,
    bulk_state: Optional[dict] = None,
) -> None:
    """Persist measured provider usage without storing prompts or credentials."""
    if _session_is_deleted(session_id):
        return
    if not isinstance(usage, dict):
        return

    def _int_value(value: Any) -> int:
        try:
            return max(0, int(value or 0))
        except (TypeError, ValueError):
            return 0

    source_stats = source_stats if isinstance(source_stats, dict) else {}
    bulk_state = bulk_state if isinstance(bulk_state, dict) else {}
    timing = bulk_state.get("timing") or {}
    selected_items = _int_value(source_stats.get("selected_gene_count"))
    if not selected_items:
        selected_items = len({
            str(gene).strip()
            for gene in (bulk_state.get("selected_genes") or [])
            if str(gene).strip()
        })
    rag_items = _int_value(source_stats.get("total_genes_queried")) or selected_items
    record = {
        "timestamp": _datetime_module.datetime.now(_datetime_module.timezone.utc).isoformat(),
        "session_id": str(session_id),
        "provider": str(usage.get("provider") or "unknown"),
        "model": str(usage.get("model") or "unknown"),
        "selected_items": selected_items,
        "rag_items": rag_items,
        "prompt_tokens": _int_value(usage.get("prompt_tokens")),
        "completion_tokens": _int_value(usage.get("completion_tokens")),
        "total_tokens": _int_value(usage.get("total_tokens")),
        "reasoning_tokens": _int_value(usage.get("reasoning_tokens")),
        "requests": _int_value(usage.get("requests")),
        "token_usage_available": bool(usage.get("token_usage_available")),
        "elapsed_seconds": float(usage.get("elapsed_seconds") or 0.0),
        "rag_elapsed_seconds": float(
            timing.get("question_handoff_seconds")
            or timing.get("rag_elapsed_seconds")
            or timing.get("rag_rebuild_seconds")
            or source_stats.get("rag_elapsed_seconds")
            or usage.get("rag_elapsed_seconds")
            or 0.0
        ),
    }
    path = _answer_usage_path(session_id)
    try:
        with _ANSWER_USAGE_LOCK:
            payload = {}
            if path.exists():
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, TypeError, ValueError, json.JSONDecodeError):
                    payload = {}
            records = payload.get("records", []) if isinstance(payload, dict) else []
            if not isinstance(records, list):
                records = []
            records.append(record)
            payload = {"schema_version": 1, "session_id": str(session_id), "records": records[-100:]}
            temp_path = path.with_suffix(path.suffix + ".tmp")
            temp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            temp_path.replace(path)
    except Exception as exc:
        logger.warning("Failed to persist answer usage for %s: %s", session_id, exc)


def _load_answer_usage_records() -> list[dict]:
    """Load measured model-usage records from saved chats."""
    records = []
    try:
        paths = sorted(
            _DATASET_DIR.glob("*_answer_usage.json"),
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )[:100]
        for path in paths:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, TypeError, ValueError, json.JSONDecodeError):
                continue
            items = payload.get("records", []) if isinstance(payload, dict) else []
            if isinstance(items, list):
                records.extend(item for item in items if isinstance(item, dict))
    except OSError:
        return []
    return records[-1000:]


def _persist_bulk_state(session_id: str, state: Optional[dict] = None) -> None:
    """Persist bulk files, configuration, result and RAG status atomically."""
    state = state if state is not None else bulk_sessions.get(session_id)
    if not state or state.get("_deleted") or _session_is_deleted(session_id):
        return
    path = _bulk_state_path(session_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        payload = _bulk_json_safe(dict(state))
        payload["session_id"] = str(session_id)
        temp_path = path.with_suffix(path.suffix + ".tmp")
        temp_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        temp_path.replace(path)
    except Exception as exc:
        logger.warning("Failed to persist bulk state for %s: %s", session_id, exc)


def _load_bulk_state(session_id: str) -> Optional[dict]:
    """Load a durable bulk manifest without starting analysis or RAG."""
    path = _bulk_state_path(session_id)
    if not path.exists():
        return None
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(state, dict):
            return None
        state.pop("session_id", None)
        # A process restart cannot resume an in-flight thread. Preserve all
        # completed data but make the next safe UI state explicit.
        if state.get("status") in {"queued", "analyzing", "enriching", "rag_building"}:
            state["status"] = (
                "ready_for_filter" if state.get("result")
                else "configured" if state.get("config")
                else "uploaded"
            )
            state["progress_phase"] = "会话已恢复；已保存的数据无需重新上传或重新查询"
        state.setdefault("progress", [])
        state.setdefault("config", None)
        state.setdefault("result", None)
        state.setdefault("rag", None)
        state.setdefault("gene_intersection", [])
        return state
    except Exception as exc:
        logger.warning("Failed to load bulk state for %s: %s", session_id, exc)
        return None

def _save_dataset(session_id: str, adata) -> None:
    """Persist adata to disk so it survives server restarts."""
    if _session_is_deleted(session_id):
        return
    try:
        import anndata
        p = _dataset_path(session_id)
        adata.write_h5ad(str(p))
        # Also save uns config separately (faster to reload just config)
        import json as _json
        cfg = {k: v for k, v in adata.uns.items() if k.startswith("e2sc_") and isinstance(v, (str, int, float, bool, list, dict))}
        _config_path(session_id).write_text(_json.dumps(cfg), encoding="utf-8")
        logger.info(f"Dataset persisted for session {session_id} ({adata.n_obs} cells)")
    except Exception as _e:
        logger.warning(f"Failed to persist dataset: {_e}")

def _reload_datasets() -> None:
    """On startup, scan persisted datasets but do NOT auto-load into memory.
    Data is only loaded when the user explicitly uploads or opens a previous session.

    Note: Aggregated log only (one INFO line) to keep startup output clean,
    since users with many saved sessions would otherwise see 30+ lines of
    "Found persisted dataset..." noise. Enable verbose mode by passing
    verbose=True to log each dataset individually.
    """
    import anndata
    h5_files = list(_DATASET_DIR.glob("*.h5ad"))
    legacy_h5_files = list(_LEGACY_DATASET_DIR.glob("*.h5ad")) if _LEGACY_DATASET_DIR.exists() else []
    for h5 in h5_files:
        sid = h5.stem
        try:
            # Only log existence; do not load into datasets dict
            logger.debug(f"Found persisted dataset for session {sid} (not auto-loaded)")
        except Exception as _e:
            logger.warning(f"Failed to scan {h5}: {_e}")
    if h5_files or legacy_h5_files:
        logger.info(
            "Found %s persisted dataset(s) in active storage and %s in legacy storage "
            "(not auto-loaded)",
            len(h5_files),
            len(legacy_h5_files),
        )

# Scan persisted datasets at import time (do NOT load into memory)
_reload_datasets()


def _restore_session_state(session_id: str) -> tuple[Any, Optional[dict]]:
    """Restore one chat's dataset and bulk manifest on first access.

    Chat history is already durable in SQLite.  This companion restore path
    makes the data plane follow the same session ID, so switching back to a
    historical chat does not require another upload or another RAG build.
    """
    session_id = str(session_id or "default")

    if _session_is_deleted(session_id):
        return None, None

    if session_id not in bulk_sessions:
        state = _load_bulk_state(session_id)
        if state is None:
            # Backward-compatible recovery for files written before manifests
            # were introduced. This recovers the upload stage; completed
            # result/RAG state is recovered from new manifests going forward.
            safe = "".join(c for c in session_id if c.isalnum() or c in "-_") or "default"
            count_files = sorted(_DATASET_DIR.glob(f"{safe}_bulk_counts.*"), key=lambda p: p.stat().st_mtime, reverse=True)
            clinical_files = sorted(_DATASET_DIR.glob(f"{safe}_bulk_clinical.*"), key=lambda p: p.stat().st_mtime, reverse=True)
            result_files = sorted(_DATASET_DIR.glob(f"{safe}_bulk_result.*"), key=lambda p: p.stat().st_mtime, reverse=True)
            if count_files and clinical_files:
                try:
                    preview = inspect_bulk_files(count_files[0], clinical_files[0])
                    state = {
                        "status": "uploaded",
                        "input_type": "raw_counts_clinical",
                        "counts_path": str(count_files[0]),
                        "clinical_path": str(clinical_files[0]),
                        "counts_filename": count_files[0].name,
                        "clinical_filename": clinical_files[0].name,
                        "preview": preview,
                        "progress": ["已恢复历史原始文件；尚未重新执行统计分析"],
                        "progress_percent": 100,
                        "progress_phase": "历史原始文件已恢复",
                        "config": None,
                        "result": None,
                        "rag": None,
                        "gene_intersection": [],
                    }
                except Exception as exc:
                    logger.warning("Failed to inspect legacy bulk files for %s: %s", session_id, exc)
            elif result_files:
                try:
                    preview = inspect_bulk_result_file(result_files[0])
                    state = {
                        "status": "result_uploaded",
                        "input_type": "user_precomputed_result",
                        "result_path": str(result_files[0]),
                        "result_filename": result_files[0].name,
                        "preview": {"result": preview},
                        "progress": ["已恢复历史结果表；未重新计算统计量"],
                        "progress_percent": 100,
                        "progress_phase": "历史结果表已恢复",
                        "config": None,
                        "result": None,
                        "rag": None,
                        "gene_intersection": [],
                    }
                except Exception as exc:
                    logger.warning("Failed to inspect legacy bulk result for %s: %s", session_id, exc)
        if state is not None:
            bulk_sessions[session_id] = state

    if session_id not in datasets:
        dataset_path = _dataset_path(session_id)
        if dataset_path.exists():
            try:
                datasets[session_id] = sc.read_h5ad(str(dataset_path))
                logger.info("Restored dataset for session %s from %s", session_id, dataset_path)
            except Exception as exc:
                logger.warning("Failed to restore dataset for %s: %s", session_id, exc)

    return datasets.get(session_id), bulk_sessions.get(session_id)

# Per-session progress log (last N messages for polling)
import collections as _collections
import threading as _threading
_progress_lock = _threading.Lock()
_progress: dict[str, list] = _collections.defaultdict(list)
_MAX_PROGRESS = 60  # keep last 60 messages per session

# Track KB build state per session: None=not started, False=building, True=done
_kb_build_state: dict[str, Any] = {}  # session_id -> {ready, n_docs, n_genes}


def _push_progress(session_id: str, msg: str) -> None:
    """Append a progress message for a session (thread-safe)."""
    with _progress_lock:
        buf = _progress[session_id]
        # The same progress event can arrive through the durable bulk updater
        # and the per-chat logging bridge.  Keep one visible copy so the chat
        # progress log does not repeat identical status lines.
        if buf and buf[-1] == msg:
            return
        buf.append(msg)
        if len(buf) > _MAX_PROGRESS:
            del buf[:-_MAX_PROGRESS]


class _ProgressHandler(logging.Handler):
    """Logging handler that mirrors INFO records to the progress buffer."""

    def __init__(self, session_id: str, bind_current_thread: bool = True):
        super().__init__(level=logging.INFO)
        self.session_id = session_id
        self.thread_id = _threading.get_ident() if bind_current_thread else None

    def bind_to_current_thread(self) -> None:
        """Restrict captured records to the Agent worker for this session."""
        self.thread_id = _threading.get_ident()

    def emit(self, record: logging.LogRecord) -> None:
        try:
            if self.thread_id is None or record.thread != self.thread_id:
                return
            msg = record.getMessage()
            if msg.startswith("["):
                _push_progress(self.session_id, msg)
                logger.info(f"[_ProgressHandler] captured: {msg[:80]}")
        except Exception as _eh_e:
            logger.warning(f"[_ProgressHandler] emit failed: {_eh_e}")


import sqlite3 as _sqlite3
import uuid as _uuid
from datetime import datetime as _datetime

def _get_project_root_for_server() -> Path:
    """Get project root directory for server module."""
    current = Path(__file__).resolve().parent  # api/
    current = current.parent  # e2seq/
    current = current.parent  # project root
    return current

# Use the centralized project storage directory for chat history.
_project_root_server = _get_project_root_for_server()
_CHAT_DB_PATH = _CHAT_DIR / "chat_history.db"

# One-time, non-destructive migration of the small legacy chat database.
if not _CHAT_DB_PATH.exists() and _LEGACY_CHAT_DB_PATH.exists():
    try:
        shutil.copy2(_LEGACY_CHAT_DB_PATH, _CHAT_DB_PATH)
        logger.info("Migrated chat history to %s", _CHAT_DB_PATH)
    except Exception as migration_error:
        logger.warning("Could not migrate legacy chat history: %s", migration_error)


def _init_chat_db():
    """Initialize chat history SQLite database."""
    _CHAT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = _sqlite3.connect(str(_CHAT_DB_PATH))
    conn.execute("""CREATE TABLE IF NOT EXISTS chats (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (chat_id) REFERENCES chats(id)
    )""")
    conn.commit()
    conn.close()


def _save_chat_message(chat_id: str, role: str, content: str, title: str = ""):
    """Save a message and ensure chat record exists."""
    now = _datetime.utcnow().isoformat()
    conn = _sqlite3.connect(str(_CHAT_DB_PATH))
    # Upsert chat record
    existing = conn.execute("SELECT id FROM chats WHERE id=?", (chat_id,)).fetchone()
    if not existing:
        chat_title = title or (content[:40] + "..." if len(content) > 40 else content)
        conn.execute("INSERT INTO chats (id,title,created_at,updated_at) VALUES (?,?,?,?)",
                     (chat_id, chat_title, now, now))
    else:
        conn.execute("UPDATE chats SET updated_at=? WHERE id=?", (now, chat_id))
    # Insert message
    conn.execute("INSERT INTO messages (chat_id,role,content,created_at) VALUES (?,?,?,?)",
                 (chat_id, role, content, now))
    conn.commit()
    conn.close()


def _get_all_chats():
    """Get all chats ordered by updated_at desc."""
    if not _CHAT_DB_PATH.exists():
        return []
    conn = _sqlite3.connect(str(_CHAT_DB_PATH))
    rows = conn.execute("SELECT id,title,created_at,updated_at FROM chats ORDER BY updated_at DESC").fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1], "created_at": r[2], "updated_at": r[3]} for r in rows]


def _get_chat_messages(chat_id: str):
    """Get all messages for a chat."""
    if not _CHAT_DB_PATH.exists():
        return []
    conn = _sqlite3.connect(str(_CHAT_DB_PATH))
    rows = conn.execute(
        "SELECT role,content,created_at FROM messages WHERE chat_id=? ORDER BY id ASC",
        (chat_id,)
    ).fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1], "created_at": r[2]} for r in rows]


def _delete_chat(chat_id: str):
    """Delete a chat and its messages."""
    if not _CHAT_DB_PATH.exists():
        return
    conn = _sqlite3.connect(str(_CHAT_DB_PATH))
    conn.execute("DELETE FROM messages WHERE chat_id=?", (chat_id,))
    conn.execute("DELETE FROM chats WHERE id=?", (chat_id,))
    conn.commit()
    conn.close()


def _purge_session_artifacts(session_id: str, *, mark_deleted: bool = False) -> list[str]:
    """Cascade-delete all data owned by one chat/session ID.

    Chat history and uploaded analysis data are separate persistence layers.
    This function is the single cleanup path used by chat deletion, the
    history bulk-delete route, and the UI's "clear current data" action.  It
    intentionally matches only the exact sanitized session prefix, so one
    chat can never delete another chat's files.
    """
    key = str(session_id or "default")
    safe = "".join(c for c in key if c.isalnum() or c in "-_") or "default"
    cleared: list[str] = []

    if mark_deleted:
        _deleted_session_ids.add(key)
        try:
            _DATASET_DIR.mkdir(parents=True, exist_ok=True)
            (_DATASET_DIR / f".{safe}.deleted").write_text("deleted\n", encoding="utf-8")
        except OSError as exc:
            logger.warning("Failed to write deletion tombstone for %s: %s", key, exc)

    # Mark the existing manifest before removing it.  A background worker may
    # still hold the same dict object and must not persist it again.
    state = bulk_sessions.get(key)
    if isinstance(state, dict):
        state["_deleted"] = True

    if key in datasets:
        datasets.pop(key, None)
        cleared.append("dataset-memory")
    if key in agents:
        agents.pop(key, None)
        cleared.append("agent-memory")
    if key in bulk_sessions:
        bulk_sessions.pop(key, None)
        cleared.append("bulk-state-memory")

    job = bulk_jobs.pop(key, None)
    if job is not None:
        if not job.done():
            job.cancel()
        cleared.append("bulk-job")

    with _bulk_rag_jobs_lock:
        rag_job = _bulk_rag_jobs.pop(key, None)
        if rag_job is not None:
            cancel_event = rag_job.get("cancel_event")
            if cancel_event is not None:
                cancel_event.set()
            task = rag_job.get("task")
            if task is not None and hasattr(task, "cancel") and not task.done():
                task.cancel()
            cleared.append("bulk-rag-job")

    abort_event = _abort_events.pop(key, None)
    if abort_event is not None:
        abort_event.set()
        cleared.append("chat-job")
    with _progress_lock:
        if _progress.pop(key, None) is not None:
            cleared.append("progress")
    if _kb_build_state.pop(key, None) is not None:
        cleared.append("kb-build-state")

    # Drop process-local scientific execution and state-manager instances.
    try:
        from e2seq.agent.code_executor import _executors
        if _executors.pop(key, None) is not None:
            cleared.append("code-executor")
    except Exception as exc:
        logger.debug("Code executor cleanup skipped for %s: %s", key, exc)
    try:
        from e2seq.agent.state_manager import delete_session_state
        cleared.extend(delete_session_state(key))
    except Exception as exc:
        logger.debug("State-manager cleanup skipped for %s: %s", key, exc)
    try:
        from e2seq.agent.memory import delete_session_memory
        memory_result = delete_session_memory(key)
        if any(int(value or 0) for value in memory_result.values()):
            cleared.append("long-term-memory")
    except Exception as exc:
        logger.debug("Long-term-memory cleanup skipped for %s: %s", key, exc)
    try:
        from e2seq.data.vector_store import delete_vector_store
        if delete_vector_store(key):
            cleared.append("vector-store")
    except Exception as exc:
        logger.debug("Vector-store cleanup skipped for %s: %s", key, exc)

    # Delete every session-prefixed artifact, including future per-session
    # files, rather than maintaining another brittle filename allow-list.
    for data_dir in (_DATASET_DIR, _LEGACY_DATASET_DIR):
        if not data_dir.is_dir():
            continue
        try:
            paths = list(data_dir.iterdir())
        except OSError:
            continue
        for path in paths:
            if not path.is_file():
                continue
            name = path.name
            if (
                name != safe
                and not name.startswith(f"{safe}_")
                and not name.startswith(f"{safe}.")
            ):
                continue
            try:
                path.unlink()
                cleared.append(f"file:{name}")
            except OSError as exc:
                logger.warning("Failed to delete session artifact %s: %s", path, exc)

    logger.info("Purged session %s: %s", key, cleared)
    return cleared


def _rename_chat(chat_id: str, new_title: str) -> bool:
    """Rename a chat session. Returns True if updated, False if not found."""
    if not _CHAT_DB_PATH.exists():
        return False
    conn = _sqlite3.connect(str(_CHAT_DB_PATH))
    cur = conn.execute("UPDATE chats SET title=?, updated_at=? WHERE id=?",
                       (new_title, _datetime.utcnow().isoformat(), chat_id))
    conn.commit()
    updated = cur.rowcount > 0
    conn.close()
    return updated


@app.on_event("startup")
async def startup_event():
    """Initialize databases on server startup."""
    import os
    from e2seq.data.local_db import initialize_databases
    # 优先尝试项目目录下的 database/ 目录
    candidates = [
        Path(__file__).parent.parent.parent / "database",
        Path(os.getcwd()) / "database",
    ]
    for data_dir in candidates:
        if data_dir.exists():
            logger.info(f"Initializing databases from {data_dir}")
            try:
                initialize_databases(data_dir)
                logger.info("Local databases initialized successfully")
            except Exception as e:
                logger.warning(f"Database initialization warning: {e}")
            break
    else:
        logger.warning("database/ directory not found, skipping DB initialization")

    # Initialize chat history database
    _init_chat_db()
    logger.info("Chat history database initialized")


@app.post("/api/execute")
async def execute_code(request: Request):
    """Execute Python code in the AI sandbox and return results."""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    code = body.get("code", "").strip()
    chat_id = body.get("chat_id", "default")

    if not code:
        raise HTTPException(status_code=400, detail="code is required")

    from e2seq.agent.code_executor import get_executor

    adata = datasets.get(chat_id, None)
    executor = get_executor(session_id=chat_id, adata=adata)

    result = executor.execute(code, timeout=30)

    # Serialize plots to plotly JSON if any
    plots_data = []
    for fig in result.plots:
        try:
            import plotly
            fig_json = plotly.io.to_json(fig)
            plots_data.append({"type": "matplotlib", "figure": fig_json})
        except Exception:
            pass

    return {
        "success": result.success,
        "stdout": result.stdout,
        "result": str(result.result) if result.result is not None else None,
        "error": result.error,
        "plots": plots_data,
        "dataframes": result.dataframes,
        "context_text": result.as_context_text(),
    }


@app.get("/api/matrix/groups")
async def get_available_groups(session_id: str = "default"):
    """Return all categorical obs columns and their unique values."""
    adata = datasets.get(session_id)
    if adata is None:
        raise HTTPException(status_code=400, detail="请先上传 h5ad 数据文件")
    try:
        from e2seq.tools.scanpy_tools import ScancpyTools
        tools = ScancpyTools(adata)
        return tools.get_available_groups()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/matrix/by-group")
async def get_matrix_by_group(session_id: str = "default", group_col: str = "group", n_top_genes: int = 20, method: str = "mean"):
    """Return top-expressed genes × disease-group matrix."""
    if session_id not in datasets:
        raise HTTPException(status_code=400, detail="请先上传 h5ad 数据文件")
    try:
        from e2seq.tools.scanpy_tools import ScancpyTools
        adata = datasets[session_id]
        tools = ScancpyTools(adata)
        result = tools.get_top_genes_by_group(group_col=group_col, n_top_genes=n_top_genes, method=method)
        from e2seq.utils.gene_intersection import apply_gene_intersection
        return apply_gene_intersection(result, adata.uns.get("e2sc_gene_intersection", []))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/matrix")
async def get_expression_matrix(session_id: str = "default", n_top_genes: int = 20, method: str = "mean", celltype_col: str = ""):
    """Return top-expressed genes × cell-type matrix from the loaded dataset."""
    if session_id not in datasets:
        raise HTTPException(status_code=400, detail="请先上传 h5ad 数据文件")
    try:
        from e2seq.tools.scanpy_tools import ScancpyTools
        adata = datasets[session_id]
        tools = ScancpyTools(adata)
        # Prefer user-specified column, fall back to adata.uns config, then auto-detect
        col = celltype_col or adata.uns.get("e2sc_celltype_col", None)
        result = tools.get_top_genes_matrix(n_top_genes=n_top_genes, method=method, celltype_col=col or None)
        from e2seq.utils.gene_intersection import apply_gene_intersection
        return apply_gene_intersection(result, adata.uns.get("e2sc_gene_intersection", []))
    except Exception as e:
        logger.error(f"Matrix generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/db/status")
async def db_status():
    """Return local database files, table counts, and a real query probe.

    A populated SQLite file only proves that the file exists.  The probe also
    exercises each public query method, while keeping ``probe_records=0`` as a
    valid gene-level result rather than labelling the database broken.
    """
    from e2seq.data.local_db import STRINGDatabase, HMDBDatabase, TRRUSTDatabase, GUTMGENEDatabase
    from e2seq.utils import get_config
    config = get_config()
    db_base = Path(config.database.db_path).expanduser()
    result = {}
    probe_genes = {
        "string": "TP53",
        "hmdb": "EGFR",
        "trrust": "TP53",
        "gutmgene": "IL6",
    }
    for name, cls in [("string", STRINGDatabase), ("hmdb", HMDBDatabase),
                      ("trrust", TRRUSTDatabase), ("gutmgene", GUTMGENEDatabase)]:
        db_file = db_base / f"{name}.db"
        if db_file.exists():
            try:
                db = cls()
                db.connect()
                cursor = db.conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [r[0] for r in cursor.fetchall()]
                counts = {}
                for t in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {t}")
                    counts[t] = cursor.fetchone()[0]
                db.close()
                probe_gene = probe_genes[name]
                probe_count = 0
                with cls() as probe_db:
                    if name == "string":
                        probe_count = len(probe_db.get_interactions(probe_gene, min_score=0.4))
                    elif name == "hmdb":
                        probe_count = len(probe_db.get_metabolites(probe_gene))
                    elif name == "trrust":
                        probe_count = len(probe_db.get_targets(probe_gene)) + len(probe_db.get_regulators(probe_gene))
                    else:
                        probe_count = len(probe_db.get_microbes(probe_gene))
                result[name] = {
                    "status": "ok",
                    "queryable": True,
                    "tables": counts,
                    "path": str(db_file),
                    "probe_gene": probe_gene,
                    "probe_records": probe_count,
                    "probe_note": "0 means this probe gene has no record; it does not mean the database is unreadable.",
                }
            except Exception as e:
                result[name] = {"status": "error", "queryable": False, "error": str(e)}
        else:
            result[name] = {"status": "not_initialized", "queryable": False, "path": str(db_file)}
    return result


@app.get("/api/source-health")
async def source_health(gene: str = "TP53"):
    """Probe every enabled online source and the local databases.

    This endpoint is intentionally a diagnostic endpoint.  It reports
    ``ok``, ``no_records``, ``needs_configuration`` and ``error`` separately,
    so a source cannot silently become a misleading zero in the UI.
    """
    probe_gene = str(gene or "TP53").strip()[:80] or "TP53"
    online_sources = list(DEFAULT_ANSWER_APIS)

    def _probe_online() -> dict:
        """Run the same all-source Agent RAG query used for a new answer.

        A health check that only probes the small verified-adapter subset can
        report a reassuring partial picture while the production fan-out is
        failing elsewhere.  This diagnostic deliberately exercises every
        remaining configured API once, including the literature pass, and
        preserves no_records separately from transport errors.
        """
        agent = E2seqAgent(
            adata=None,
            session_id=f"source-health-{uuid.uuid4()}",
        )
        knowledge = agent._build_group_knowledge(
            "source-health",
            [probe_gene],
            context_hint="",
            enabled_apis=set(online_sources),
            enabled_dbs=set(),
        )
        return knowledge.get("_source_stats", {}) or {}

    try:
        audit = await asyncio.to_thread(_probe_online)
    except Exception as exc:
        audit = {
            "apis": {
                source: {
                    "status_counts": {"error": 1},
                    "errors": [str(exc)],
                    "hit_count": 0,
                    "total_genes": 1,
                }
                for source in online_sources
            }
        }

    online = {}
    for source in online_sources:
        item = (audit.get("apis") or {}).get(source, {})
        status_counts = dict(item.get("status_counts") or {})
        if status_counts.get("ok") or item.get("hit_count", 0):
            status = "ok"
        elif status_counts.get("error"):
            status = "error"
        elif status_counts.get("no_records"):
            status = "no_records"
        else:
            status = "unqueried"
        online[source] = {
            "status": status,
            "count": item.get("hit_count", 0),
            "queried_genes": item.get("total_genes", 1),
            "query_attempts": sum(status_counts.values()),
            "status_counts": status_counts,
            "error": "; ".join(item.get("errors") or []),
            "fields": {},
        }
    local_status = await db_status()
    return {
        "gene": probe_gene,
        "online": online,
        "local": local_status,
        "agent_rag": True,
        "note": "每个剩余在线 API 均按生产 Agent RAG 路径实际查询一次；no_records 表示接口可达但该基因无记录。",
    }




# Pydantic models
class ConfigRequest(BaseModel):
    provider: str
    api_key: str
    model: str


class ChatRequest(BaseModel):
    message: str
    session_id: str


class ChatResponse(BaseModel):
    text: str
    plots: List[Dict[str, Any]]
    thinking: List[Dict[str, str]]


class StatusResponse(BaseModel):
    configured: bool
    data_loaded: bool
    # Dataset-level setup is separate from LLM/API configuration. The UI
    # keeps the question box locked until the user confirms the setup dialog.
    analysis_configured: bool = True
    data_mode: Optional[str] = None  # singlecell | table | bulk (bulk is exposed as table-compatible UI mode)
    cells: Optional[int] = None
    genes: Optional[int] = None
    bulk_status: Optional[str] = None
    bulk_analysis_type: Optional[str] = None
    selected_genes: List[str] = []
    gene_intersection: List[str] = []


class KnowledgeBase(BaseModel):
    name: str
    type: str
    records: str


# API Endpoints

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Serve favicon."""
    favicon_path = static_path / "favicon.png"
    if favicon_path.exists():
        return FileResponse(str(favicon_path), media_type="image/png")
    legacy_favicon_path = static_path / "favicon.ico"
    if legacy_favicon_path.exists():
        return FileResponse(str(legacy_favicon_path), media_type="image/x-icon")
    return HTMLResponse(status_code=204)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface."""
    try:
        index_path = templates_path / "index.html"
        if index_path.exists():
            import time as _time
            import re as _re
            _ts = int(_time.time())
            content = index_path.read_text(encoding='utf-8')
            # Replace static version strings with a live timestamp so the
            # browser never serves a cached copy of JS/CSS after a redeploy.
            content = _re.sub(r'\?v=[^"\']+', f'?v={_ts}', content)
            return HTMLResponse(
                content=content,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache"}
            )
        else:
            return HTMLResponse(content="<h1>E2seq Web Interface</h1><p>Template not found. Please check installation.</p>")
    except Exception as e:
        logger.error(f"Failed to load index.html: {e}")
        return HTMLResponse(content=f"<h1>Error</h1><p>{str(e)}</p>", status_code=500)


@app.get("/knowledge-base", response_class=HTMLResponse)
async def knowledge_base_page():
    """Serve the knowledge base management page."""
    try:
        kb_path = templates_path / "knowledge_base.html"
        if kb_path.exists():
            return kb_path.read_text(encoding='utf-8')
        else:
            return HTMLResponse(content="<h1>Knowledge Base</h1><p>Template not found.</p>", status_code=404)
    except Exception as e:
        logger.error(f"Failed to load knowledge_base.html: {e}")
        return HTMLResponse(content=f"<h1>Error</h1><p>{str(e)}</p>", status_code=500)


@app.get("/api/status")
async def get_status(session_id: str = "default"):
    """Get system status."""
    _restore_session_state(session_id)
    config = get_config()
    # Only use session-specific data (no fallback to "default" — that would
    # resurrect stale data after a session switch or clear-data operation).
    adata = datasets.get(session_id)
    has_data = adata is not None

    cells = None
    genes = None
    data_mode = None
    analysis_configured = True
    bulk_status = None
    bulk_analysis_type = None
    selected_genes: list[str] = []
    gene_intersection: list[str] = []
    if has_data:
        if adata.uns.get("e2sc_data_mode") == "csv":
            data_mode = "table"
            cells = adata.uns.get("e2sc_display_rows", adata.n_obs)   # 过滤后行数（记录数）
            genes = adata.uns.get("e2sc_display_genes", adata.n_vars)  # 唯一基因/蛋白数
        else:
            data_mode = "singlecell"
            cells = adata.n_obs
            genes = adata.n_vars
        # New uploads explicitly start in an unconfigured state. Older
        # persisted sessions did not have this marker, so infer readiness
        # from their stored column settings for backward compatibility.
        if "e2sc_configured" in adata.uns:
            analysis_configured = bool(adata.uns.get("e2sc_configured"))
        else:
            analysis_configured = bool(
                adata.uns.get("e2sc_celltype_col")
                or adata.uns.get("e2sc_group_col")
            )
        gene_intersection = normalize_gene_list(adata.uns.get("e2sc_gene_intersection", []))
    bulk = bulk_sessions.get(session_id)
    if bulk is not None:
        has_data = True
        # Keep the legacy panel compatible while exposing the more precise
        # bulk state to the new dialog and polling UI.
        data_mode = "table"
        bulk_status = bulk.get("status", "uploaded")
        analysis_configured = bulk_status in _BULK_CHAT_READY_STATUSES
        bulk_analysis_type = (bulk.get("config") or {}).get("analysis_type")
        selected_genes = [str(gene) for gene in (bulk.get("selected_genes") or []) if str(gene).strip()]
        gene_intersection = normalize_gene_list(bulk.get("gene_intersection", []))
        preview = bulk.get("preview") or {}
        if bulk.get("input_type") == "user_precomputed_result":
            result_preview = preview.get("result") or {}
            cells = int(result_preview.get("n_rows", 0)) or cells
            completed_result = bulk.get("result") or {}
            genes = int(completed_result.get("n_genes_tested", 0)) or int(result_preview.get("n_genes_guess", 0)) or genes
        else:
            cells = int((preview.get("clinical") or {}).get("n_rows", 0)) or cells
            genes = int((preview.get("counts") or {}).get("n_genes", 0)) or genes

    return StatusResponse(
        configured=bool(config.llm.api_key),
        data_loaded=has_data,
        analysis_configured=analysis_configured,
        data_mode=data_mode,
        cells=cells,
        genes=genes,
        bulk_status=bulk_status,
        bulk_analysis_type=bulk_analysis_type,
        selected_genes=selected_genes,
        gene_intersection=gene_intersection,
    )


@app.post("/api/config")
async def save_config(config_req: ConfigRequest):
    """Save LLM configuration."""
    try:
        logger.info(f"Saving configuration for provider: {config_req.provider}")
        config = get_config()
        security = get_security_manager()

        # Encrypt API key
        encrypted_key = security.encrypt(config_req.api_key)

        # Update config
        config.update_llm(
            config_req.provider,
            encrypted_key,
            config_req.model
        )

        # Re-initialize all existing agents with new configuration
        for session_id, adata in datasets.items():
            try:
                logger.info(f"Reinitializing agent for session: {session_id}")
                agents[session_id] = E2seqAgent(
                    adata=adata,
                    llm_provider=config_req.provider,
                    api_key=config_req.api_key,
                    model=config_req.model
                )
            except Exception as e:
                # Log error but don't fail the config save
                logger.warning(f"Failed to reinitialize agent for session {session_id}: {e}")

        logger.info("Configuration saved successfully")
        return {"success": True, "message": "Configuration saved and agents updated"}
    except Exception as e:
        logger.error(f"Failed to save configuration: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save configuration: {str(e)}")


@app.get("/api/config")
async def get_config_info():
    """Get current configuration."""
    config = get_config()
    return {
        "provider": config.llm.provider,
        "model": config.llm.model,
        "configured": bool(config.llm.api_key)
    }


@app.get("/api/storage")
async def get_storage_info():
    """Return the exact persistent storage locations used by the web app."""
    config = get_config()
    return {
        "root": str(_STORAGE_ROOT),
        "datasets": str(_DATASET_DIR),
        "chat_history": str(_CHAT_DB_PATH),
        "knowledge_bases": str(_CUSTOM_DATABASE_DIR),
        "vector_database": str(Path(config.database.db_path).expanduser().resolve()),
        "config": str(config.config_path.expanduser().resolve()),
        "legacy_datasets": str(_LEGACY_DATASET_DIR.resolve()) if _LEGACY_DATASET_DIR.exists() else "",
        "override_env": "E2SEQ_DATA_DIR",
    }


@app.post("/api/upload")
async def upload_data(request: Request, file: UploadFile = File(...)):
    """Upload single-cell dataset file (.h5ad/.csv/.rds)."""
    import pandas as pd
    import numpy as np
    import anndata
    import io

    filename = file.filename or ""
    ext = Path(filename).suffix.lower()
    if ext not in {".h5ad", ".csv", ".rds"}:
        raise HTTPException(status_code=400, detail="单细胞数据仅支持 .h5ad / .csv / .rds")

    form = await request.form()
    session_id = form.get("session_id") or "default"

    _restore_session_state(session_id)

    # 已有数据时不允许覆盖上传，必须先清除
    if session_id in datasets:
        raise HTTPException(status_code=400, detail="当前会话已有数据，请先点击“清除数据”后再上传")

    logger.info(f"Uploading file: {filename}")
    tmp_path = None
    try:
        content = await file.read()

        if ext == ".h5ad":
            with tempfile.NamedTemporaryFile(delete=False, suffix='.h5ad') as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            logger.info(f"Reading h5ad file from: {tmp_path}")
            adata = sc.read_h5ad(tmp_path)
        elif ext == ".csv":
            # Treat CSV as expression matrix for single-cell mode
            df = pd.read_csv(io.BytesIO(content), encoding="utf-8")
            if df.shape[1] > 1 and not pd.api.types.is_numeric_dtype(df.iloc[:, 0]):
                df = df.set_index(df.columns[0])
            numeric_df = df.select_dtypes(include=[np.number])
            if numeric_df.empty:
                raise HTTPException(status_code=400, detail="CSV 中未找到数值表达矩阵")
            matrix = numeric_df.to_numpy(dtype=np.float32)
            # Heuristic: genes are usually much more than cells -> transpose
            if matrix.shape[0] > matrix.shape[1] * 3:
                matrix = matrix.T
                obs_index = [f"cell_{i+1}" for i in range(matrix.shape[0])]
                var_index = list(numeric_df.index.astype(str))[:matrix.shape[1]]
            else:
                obs_index = list(numeric_df.index.astype(str))[:matrix.shape[0]]
                var_index = list(numeric_df.columns.astype(str))[:matrix.shape[1]]
            adata = anndata.AnnData(
                X=matrix,
                obs=pd.DataFrame(index=obs_index),
                var=pd.DataFrame(index=var_index),
            )
            adata.obs["cell_type"] = "all_cells"
            adata.obs["group"] = "group1"
            adata.uns["e2sc_source_format"] = "csv"
        else:
            # .rds support: try to read with pyreadr and convert first table
            try:
                import pyreadr
            except Exception:
                raise HTTPException(status_code=400, detail=".rds 需要安装 pyreadr 后才能解析")
            with tempfile.NamedTemporaryFile(delete=False, suffix='.rds') as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            r_obj = pyreadr.read_r(tmp_path)
            if not r_obj:
                raise HTTPException(status_code=400, detail=".rds 文件为空或不可解析")
            first = next(iter(r_obj.values()))
            if not hasattr(first, "select_dtypes"):
                raise HTTPException(status_code=400, detail=".rds 暂不支持该对象类型，请先转换为 h5ad/csv")
            df = first.copy()
            numeric_df = df.select_dtypes(include=[np.number])
            if numeric_df.empty:
                raise HTTPException(status_code=400, detail=".rds 中未找到数值表达矩阵")
            matrix = numeric_df.to_numpy(dtype=np.float32)
            if matrix.shape[0] > matrix.shape[1] * 3:
                matrix = matrix.T
            adata = anndata.AnnData(
                X=matrix,
                obs=pd.DataFrame(index=[f"cell_{i+1}" for i in range(matrix.shape[0])]),
                var=pd.DataFrame(index=[f"gene_{j+1}" for j in range(matrix.shape[1])]),
            )
            adata.obs["cell_type"] = "all_cells"
            adata.obs["group"] = "group1"
            adata.uns["e2sc_source_format"] = "rds"

        datasets[session_id] = adata
        # Uploading is not analysis configuration. Keep data-backed questions
        # locked until /api/configure-dataset succeeds.
        adata.uns["e2sc_configured"] = False
        logger.info(f"Data loaded: {adata.n_obs} cells, {adata.n_vars} genes")
        _save_dataset(session_id, adata)

        obs_cols = list(adata.obs.columns)
        _ct_exact = ['cell_type', 'celltype', 'cell type', 'final_annotation', 'annotation', 'auto_annotation']
        _ct_partial = ['louvain', 'leiden', 'cluster']
        ct_guess = next((c for c in obs_cols if c.lower() in _ct_exact), None) or \
                   next((c for c in obs_cols if any(k in c.lower() for k in _ct_partial)), obs_cols[0] if obs_cols else "")
        _grp_exact = ['group', 'condition', 'disease', 'status', 'phenotype']
        _grp_partial = ['batch', 'sample']
        grp_guess = next((c for c in obs_cols if c.lower() in _grp_exact), None) or \
                    next((c for c in obs_cols if any(k in c.lower() for k in _grp_partial)), "")

        return {
            "success": True,
            "cells": adata.n_obs,
            "genes": adata.n_vars,
            "session_id": session_id,
            "obs_columns": obs_cols,
            "celltype_col_guess": ct_guess,
            "group_col_guess": grp_guess,
        }
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Invalid file format: {e}")
        raise HTTPException(status_code=400, detail="无效文件格式")
    except Exception as e:
        logger.error(f"Failed to process file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")
    finally:
        if tmp_path and Path(tmp_path).exists():
            try:
                Path(tmp_path).unlink()
                logger.info(f"Cleaned up temp file: {tmp_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temp file {tmp_path}: {e}")


@app.post("/api/configure-dataset")
async def configure_dataset(request: Request):
    """Apply user-selected column names and API/DB settings, then initialise agent.
    Called once after the user confirms the post-upload configuration dialog.
    """
    body = await request.json()
    session_id = body.get("session_id", "default")
    _restore_session_state(session_id)
    celltype_col = body.get("celltype_col", "cell_type")
    group_col = body.get("group_col", "group")
    enabled_apis = body.get("enabled_apis", list(DEFAULT_ANSWER_APIS))
    enabled_dbs = body.get("enabled_dbs", ["string","hmdb","trrust","gutmgene"])
    n_top_genes = int(body.get("n_top_genes", 50))  # 默认50，可在5-2000间调整
    # Validate n_top_genes range
    n_top_genes = max(5, min(2000, n_top_genes))
    min_cells = int(body.get("min_cells", 10))
    # User-defined display name mappings {original_value: display_name}
    celltype_labels = body.get("celltype_labels", {})  # e.g. {"B cells": "B lymphocytes"}
    group_labels = body.get("group_labels", {})        # e.g. {"HC": "Healthy control"}

    if session_id not in datasets:
        if "default" not in datasets:
            raise HTTPException(status_code=400, detail="请先上传 h5ad 数据文件")
        # Only copy default if it was explicitly uploaded in this session context
        # Do NOT auto-inherit across sessions
        raise HTTPException(status_code=400, detail="请先上传 h5ad 数据文件")

    adata = datasets[session_id]

    # Validate columns
    obs_cols = list(adata.obs.columns)
    if celltype_col and celltype_col not in obs_cols:
        raise HTTPException(status_code=400, detail=f"列 '{celltype_col}' 不存在于 obs 中")
    if group_col and group_col not in obs_cols:
        group_col = ""

    # Store config on adata for orchestrator to read
    adata.uns["e2sc_session_id"] = session_id
    adata.uns["e2sc_celltype_col"] = celltype_col
    adata.uns["e2sc_group_col"] = group_col
    adata.uns["e2sc_enabled_apis"] = enabled_apis
    adata.uns["e2sc_enabled_dbs"] = enabled_dbs
    adata.uns["e2sc_n_top_genes"] = n_top_genes
    adata.uns["e2sc_min_cells"] = min_cells
    # A gene-list intersection is a post-ranking selection constraint.  Keep
    # it with the session so returning to this chat does not require re-entry.
    gene_intersection = (
        normalize_gene_list(body.get("gene_intersection"))
        if "gene_intersection" in body
        else normalize_gene_list(adata.uns.get("e2sc_gene_intersection", []))
    )
    adata.uns["e2sc_gene_intersection"] = gene_intersection
    # User-supplied free-text description of this dataset (helps LLM avoid misinterpretation)
    dataset_description = body.get("dataset_description", "").strip()
    adata.uns["e2sc_dataset_description"] = dataset_description
    dataset_prompt = str(body.get("dataset_prompt", "") or "").strip()
    if len(dataset_prompt) > 10000:
        raise HTTPException(status_code=400, detail="Dataset prompt must be at most 10000 characters")
    adata.uns["e2sc_dataset_prompt"] = dataset_prompt
    # Persist label mappings — orchestrator will use these for queries and reports
    adata.uns["e2sc_celltype_labels"] = celltype_labels
    adata.uns["e2sc_group_labels"] = group_labels
    # Output mode: "simple" or "detailed" (default detailed)
    output_mode = body.get("output_mode", "detailed")
    adata.uns["e2sc_output_mode"] = output_mode
    # Max tokens for LLM response
    max_tokens = int(body.get("max_tokens", 0)) or None
    if max_tokens:
        adata.uns["e2sc_max_tokens"] = max_tokens
    # Reasoner mode (DeepSeek-R1 / o3 etc.)
    reasoner_mode = bool(body.get("reasoner_mode", False))
    adata.uns["e2sc_reasoner_mode"] = reasoner_mode

    # Now initialise (or re-use) the agent, preserving conversation memory.
    # IMPORTANT: label mappings are already stored on adata.uns above.
    # We only (re-)initialise when there is no existing agent for this session,
    # or when the existing agent does not yet have data loaded.  This ensures
    # that calling /api/configure-dataset again (e.g. from the debounced label
    # persist) does NOT wipe conversation history or reset the agent state.
    config = get_config()
    if not config.llm.api_key:
        raise HTTPException(status_code=400, detail="请先在设置页面配置 API Key")
    security = get_security_manager()
    decrypted_key = security.decrypt(config.llm.api_key)
    existing = agents.get(session_id)
    if existing is not None:
        # Agent already exists — just update its adata reference and uns config
        try:
            existing.load_data(adata)
            existing._session_id = session_id
            logger.info(f"Agent config updated for session {session_id} (labels preserved, memory intact)")
        except Exception as e:
            logger.warning(f"Failed to reload data on existing agent: {e}")
    else:
        try:
            agents[session_id] = E2seqAgent(
                adata=adata,
                llm_provider=config.llm.provider,
                api_key=decrypted_key,
                model=config.llm.model,
                session_id=session_id,
            )
            agents[session_id]._session_id = session_id
            logger.info(f"Agent initialised for session {session_id} (celltype={celltype_col}, group={group_col}, top_genes={n_top_genes}, min_cells={min_cells})")
        except Exception as e:
            logger.error(f"Agent init failed: {e}")
            raise HTTPException(status_code=500, detail=f"Agent 初始化失败: {str(e)}")

    # Mark the dataset ready only after validation and agent initialisation
    # have both succeeded. This is persisted and enforced by the chat
    # endpoints, so a stale frontend cannot bypass the setup dialog.
    adata.uns["e2sc_configured"] = True
    # Persist dataset with updated uns config so it survives restarts
    _save_dataset(session_id, adata)

    return {
        "success": True,
        "session_id": session_id,
        "celltype_col": celltype_col,
        "group_col": group_col,
        "enabled_apis": enabled_apis,
        "enabled_dbs": enabled_dbs,
        "n_top_genes": n_top_genes,
        "min_cells": min_cells,
        "gene_intersection": gene_intersection,
        "celltype_labels": celltype_labels,
        "group_labels": group_labels,
    }


@app.post("/api/gene-intersection")
async def set_gene_intersection(request: Request):
    """Persist the current chat's expression-item intersection selection."""
    body = await request.json()
    session_id = str(body.get("session_id") or "default")
    _restore_session_state(session_id)
    gene_intersection = normalize_gene_list(body.get("genes", body.get("gene_intersection", [])))

    state = bulk_sessions.get(session_id)
    if state is not None:
        state["gene_intersection"] = gene_intersection
        # A changed list invalidates question-time enrichment/RAG, but never
        # invalidates the completed statistical result itself.
        if state.get("result"):
            result = dict(state["result"])
            result.pop("enrichment", None)
            result.pop("core_enrichment", None)
            state["result"] = result
            state["rag"] = None
            state["status"] = "ready_for_filter"
            state["selected_genes"] = []
        _persist_bulk_state(session_id, state)
        return {
            "success": True,
            "session_id": session_id,
            "gene_intersection": gene_intersection,
            "matched": len(gene_intersection),
        }

    adata = datasets.get(session_id)
    if adata is None:
        raise HTTPException(status_code=400, detail="请先上传数据")
    adata.uns["e2sc_gene_intersection"] = gene_intersection
    _save_dataset(session_id, adata)
    existing = agents.get(session_id)
    if existing is not None:
        try:
            existing.load_data(adata)
            existing._session_id = session_id
        except Exception as exc:
            logger.warning("Failed to refresh agent after gene intersection update: %s", exc)
    return {
        "success": True,
        "session_id": session_id,
        "gene_intersection": gene_intersection,
        "matched": len(gene_intersection),
    }


def _bulk_progress(session_id: str, message: str, percent: int | None = None) -> None:
    """Store a bulk progress message and an optional determinate percentage."""
    state = bulk_sessions.get(session_id)
    if state is not None:
        progress = state.setdefault("progress", [])
        if not progress or progress[-1] != message:
            progress.append(message)
            state["progress"] = progress[-80:]
        if percent is not None:
            state["progress_percent"] = max(0, min(100, int(percent)))
            state["progress_phase"] = message
    suffix = f" [{max(0, min(100, int(percent)))}%]" if percent is not None else ""
    _push_progress(session_id, f"[bulk]{suffix} {message}")


_BULK_CHAT_READY_STATUSES = frozenset({"ready_for_filter", "ready", "ready_without_rag"})


def _ensure_bulk_chat_ready(session_id: str) -> None:
    """Block questions until a bulk session has passed configuration and statistics."""
    state = bulk_sessions.get(session_id)
    if state is None:
        return
    status = str(state.get("status") or "uploaded")
    if status not in _BULK_CHAT_READY_STATUSES:
        raise HTTPException(status_code=409, detail="bulk_analysis_not_ready")


def _ensure_dataset_chat_ready(session_id: str) -> None:
    """Block data-backed questions until the dataset setup is confirmed.

    Bulk expression-profile sessions are guarded by
    ``_ensure_bulk_chat_ready`` and may temporarily materialise an AnnData
    object for the agent, so they are intentionally excluded here. Single-cell
    uploads use the explicit ``e2sc_configured`` marker; legacy persisted
    sessions fall back to their stored column settings.
    """
    if session_id in bulk_sessions:
        return
    adata = datasets.get(session_id)
    if adata is None:
        return
    if "e2sc_configured" in adata.uns:
        ready = bool(adata.uns.get("e2sc_configured"))
    else:
        ready = bool(
            adata.uns.get("e2sc_celltype_col")
            or adata.uns.get("e2sc_group_col")
            or adata.uns.get("e2sc_bulk_selected_genes")
        )
    if not ready:
        raise HTTPException(status_code=409, detail="dataset_configuration_required")


def _bulk_enrichment_summary(enrichment: dict) -> str:
    """Create a short, auditable summary that can be supplied to the RAG prompt."""
    lines = []
    for set_name, data in (enrichment.get("core") or {}).items():
        bits = []
        for label in ("go", "kegg", "gsea"):
            entries = data.get(label) if isinstance(data, dict) else None
            if isinstance(entries, list):
                names = []
                for item in entries[:3]:
                    if isinstance(item, dict):
                        names.append(str(item.get("Term") or item.get("Name") or item.get("term") or ""))
                names = [n for n in names if n]
                if names:
                    bits.append(f"{label.upper()}: {', '.join(names)}")
        string_edges = data.get("string", []) if isinstance(data, dict) else []
        if isinstance(string_edges, list) and string_edges:
            bits.append(f"STRING edges: {len(string_edges)}")
        if bits:
            lines.append(f"{set_name}: " + "; ".join(bits))
    return "\n".join(lines[:12])


def _prepare_bulk_rag(session_id: str, result: dict, abort_flag=None) -> dict:
    """Expose the complete selected cohort to the existing Agentic RAG path."""
    import anndata
    import numpy as np
    import pandas as pd

    state = bulk_sessions.get(session_id)
    if state is None:
        return {"success": False, "error": "bulk session not found"}
    if abort_flag is not None and abort_flag.is_set():
        raise AbortChat("Bulk RAG cancelled before retrieval")
    # Submit the complete selected cohort to RAG. Question-time
    # GO/KEGG/GSEA/STRING and the source audit must describe the same set;
    # concurrency is controlled by the worker pool, not by dropping genes or
    # API sources. The legacy rag_core_gene_sets field is retained only as a
    # fallback for sessions created by older versions.
    selected_gene_sets = (
        result.get("rag_gene_sets")
        or result.get("gene_sets")
        or result.get("rag_core_gene_sets")
        or {}
    )
    if not isinstance(selected_gene_sets, dict):
        selected_gene_sets = {}
    gene_sets = selected_gene_sets
    full_selected_genes = []
    for _set_name, values in selected_gene_sets.items():
        if isinstance(values, (list, tuple, set)):
            full_selected_genes.extend(str(gene).strip() for gene in values if str(gene).strip())
    full_selected_genes = list(dict.fromkeys(full_selected_genes))
    rag_sets = {}
    for set_name, values in gene_sets.items():
        if not isinstance(values, (list, tuple, set)):
            continue
        normalized = list(dict.fromkeys(
            str(gene).strip() for gene in values if str(gene).strip()
        ))
        if normalized:
            rag_sets[str(set_name)] = normalized
    genes = list(dict.fromkeys(g for values in rag_sets.values() for g in values))
    if not genes:
        return {"success": False, "error": "no selected genes available"}

    rows = []
    result_rows_by_gene = {}
    analysis_type = str(result.get("analysis_type", "")).lower()
    effect_col = "log2FoldChange" if analysis_type == "differential" else "HR" if analysis_type == "survival" else "score"
    effect_label = effect_col
    for row in result.get("result", []):
        gene = str(row.get("gene", ""))
        if gene:
            result_rows_by_gene.setdefault(gene, []).append(dict(row))
    for set_name, set_genes in rag_sets.items():
        for gene in set_genes:
            source_rows = result_rows_by_gene.get(gene) or [{}]
            # A pre-computed table may contain one row per gene and group. Do
            # not overwrite those rows by indexing only on gene: the complete
            # group-level record must remain available to the agent and to the
            # answer-time synthesis context.
            for source in source_rows:
                effect = source.get(effect_col)
                if effect is None:
                    effect = source.get("coef", 0)
                row = {"analysis_set": set_name, "gene": gene, "score": effect}
                if source.get("group") not in (None, ""):
                    row["input_group"] = source.get("group")
                # Preserve the actual statistical columns in the RAG handoff
                # so the LLM can distinguish HR/log2FC/expression from
                # external annotations and compare multiple input groups.
                for key in ("log2FoldChange", "HR", "coef", "z", "statistic", "pvalue", "padj", "direction", "n", "baseMean"):
                    if key in source:
                        row[key] = source[key]
                rows.append(row)

    adata = anndata.AnnData(
        X=np.ones((1, len(genes)), dtype=np.float32),
        obs=pd.DataFrame(index=["bulk_core"]),
        var=pd.DataFrame(index=genes),
    )
    adata.uns["e2sc_data_mode"] = "csv"
    adata.uns["e2sc_session_id"] = session_id
    adata.uns["e2sc_group_col"] = "analysis_set"
    adata.uns["e2sc_gene_col"] = "gene"
    adata.uns["e2sc_expr_col"] = effect_col if effect_col != "score" else "score"
    adata.uns["e2sc_expr_type"] = effect_label
    adata.uns["e2sc_groups"] = list(rag_sets)
    adata.uns["e2sc_all_genes"] = genes
    adata.uns["e2sc_n_top_genes"] = len(genes)
    adata.uns["e2sc_bulk_selected_genes"] = full_selected_genes
    adata.uns["e2sc_bulk_selected_count"] = len(full_selected_genes)
    adata.uns["e2sc_bulk_rag_core_count"] = len(genes)
    adata.uns["e2sc_bulk_rag_queried_count"] = len(genes)
    adata.uns["e2sc_enabled_apis"] = list(DEFAULT_ANSWER_APIS)
    adata.uns["e2sc_enabled_dbs"] = list(DEFAULT_ANSWER_DBS)
    adata.uns["e2sc_csv_records"] = json.dumps(rows, ensure_ascii=False)
    enrich_summary = _bulk_enrichment_summary(result.get("enrichment") or {})
    adata.uns["e2sc_bulk_result_summary"] = enrich_summary
    user_dataset_description = str((state.get("config") or {}).get("dataset_description") or "").strip()
    auto_dataset_description = (
        "Expression-profile analysis completed. Statistical outputs are computed from the uploaded raw count matrix.\n"
        f"Analysis type: {result.get('analysis_type')}; method: {result.get('method')}; backend: {result.get('backend')}.\n"
        f"Statistical effect column: {effect_col}; p-value/FDR columns are preserved when available.\n"
        f"Selected cohort: {len(full_selected_genes)} expression items. The question-time GO/KEGG/GSEA/STRING batch and durable per-gene RAG retrieval used all selected items. Each enabled source was queried in parallel subject to its request timeout.\n"
        "The complete selected cohort and statistical table remain available in the structured result, together with source-labelled RAG records.\n"
        "Core GO/KEGG/GSEA/STRING results (top terms only):\n" + (enrich_summary or "No significant enrichment summary available.")
    )
    adata.uns["e2sc_dataset_description"] = (
        (f"User-provided dataset description: {user_dataset_description}\n" if user_dataset_description else "")
        + auto_dataset_description
    )
    adata.uns["e2sc_dataset_prompt"] = str((state.get("config") or {}).get("dataset_prompt") or "").strip()
    datasets[session_id] = adata
    _save_dataset(session_id, adata)

    config = get_config()
    if not config.llm.api_key:
        return {"success": True, "rag_status": "skipped_no_api_key", "gene_count": len(genes)}
    try:
        security = get_security_manager()
        decrypted_key = security.decrypt(config.llm.api_key)
        existing = agents.get(session_id)
        if existing is not None:
            existing.load_data(adata)
            existing._session_id = session_id
        else:
            agents[session_id] = E2seqAgent(
                adata=adata,
                llm_provider=config.llm.provider,
                api_key=decrypted_key,
                model=config.llm.model,
                session_id=session_id,
            )
            agents[session_id]._session_id = session_id
        _bulk_progress(session_id, f"开始并行 RAG 检索选定表达项目（{len(genes)} 个）", 72)
        if session_id in bulk_sessions:
            bulk_sessions[session_id]["rag_progress_max"] = 72
        # The first question has a strict completeness contract: every
        # selected expression item is queried against every enabled API and
        # local database before question-specific retrieval begins.  Do not
        # silently remove PubMed/Europe PMC for large cohorts; those sources
        # are part of the durable first-question RAG snapshot.  Use the
        # agent's batch coordinator so the cohort is processed in several
        # disjoint gene batches instead of creating one task per gene in the
        # API layer.  This preserves every selected gene while keeping
        # network concurrency bounded and CPU usage stable.
        answer_config = get_config().answer_settings
        configured_sources = bool(getattr(answer_config, "configured", False))
        custom_source_defs = load_custom_sources(include_secrets=True)
        custom_source_ids = {
            str(item.get("id")).lower()
            for item in custom_source_defs
            if item.get("id") and item.get("enabled", True)
        }
        if configured_sources:
            gene_enabled_apis = {
                str(source).lower()
                for source in (answer_config.enabled_apis or [])
                if str(source).lower() in (_ANSWER_API_IDS | custom_source_ids)
            }
            enabled_dbs = {
                str(source).lower()
                for source in (answer_config.enabled_dbs or [])
                if str(source).lower() in _ANSWER_DB_IDS
            }
        else:
            gene_enabled_apis = set(DEFAULT_ANSWER_APIS) | custom_source_ids
            enabled_dbs = set(DEFAULT_ANSWER_DBS)
        enabled_apis = set(gene_enabled_apis)
        total_genes = len(genes)
        _core_enrichment = result.get("core_enrichment") or (result.get("enrichment") or {}).get("core")

        def _rag_progress(message: str) -> None:
            # Map the bounded gene-batch progress into the 72--96% RAG
            # interval.  The previous callback forwarded every message with
            # a fixed 72%, which made a live, progressing RAG retrieval look
            # frozen in the browser.
            text = str(message)
            percentage = 72
            try:
                import re as _re
                batch_match = _re.search(r"gene batch\s+(\d+)/(\d+)", text, flags=_re.IGNORECASE)
                inner_match = _re.findall(r"(\d{1,3})%", text)
                if batch_match and inner_match:
                    batch_index = max(1, int(batch_match.group(1)))
                    batch_total = max(1, int(batch_match.group(2)))
                    inner_pct = min(100, max(0, int(inner_match[-1]))) / 100.0
                    percentage = 72 + int(round(((batch_index - 1 + inner_pct) / batch_total) * 24))
            except Exception:
                percentage = 72
            # Multiple gene batches report concurrently. Keep the visible
            # percentage monotonic so a late message from an earlier batch
            # cannot make the browser appear to move backwards.
            state = bulk_sessions.get(session_id)
            if state is not None:
                previous = float(state.get("rag_progress_max", 72) or 72)
                percentage = max(previous, percentage)
                state["rag_progress_max"] = percentage
            _bulk_progress(session_id, text, min(96, max(72, percentage)))

        knowledge = agents[session_id]._build_group_knowledge_parallel(
            "bulk/{}".format(session_id[:12]),
            genes,
            context_hint="expression profile " + ",".join(sorted(rag_sets)),
            enabled_apis=gene_enabled_apis,
            enabled_dbs=enabled_dbs,
            progress_callback=_rag_progress,
            abort_flag=abort_flag,
            max_gene_workers=_BULK_RAG_GENE_WORKERS + 2,
        )
        knowledge["_selected_gene_count"] = len(full_selected_genes)
        knowledge["_rag_core_gene_count"] = total_genes
        knowledge["_rag_queried_gene_count"] = len(knowledge.get("genes", {}))
        if _core_enrichment:
            knowledge.setdefault("_source_stats", {})["question_time_enrichment"] = _core_enrichment
            knowledge.setdefault("_source_stats", {})["question_time_enrichment_status"] = "completed"
        _bulk_progress(session_id, "整理 RAG 知识上下文", 98)
        # Each worker queried one gene, so its child source stats naturally
        # carry total_genes=1.  The durable bulk snapshot must report the
        # cohort denominator and recompute hit counts after all workers merge;
        # otherwise a correct 498/500 result is rendered misleadingly as 498/1.
        source_stats = knowledge.setdefault("_source_stats", {})
        source_stats["total_genes_queried"] = total_genes
        for category in ("apis", "dbs"):
            for source, info in (source_stats.get(category, {}) or {}).items():
                if not isinstance(info, dict):
                    continue
                hit_genes = sorted({str(gene) for gene in (info.get("hit_genes") or []) if str(gene).strip()})
                info["hit_genes"] = hit_genes
                info["hit_count"] = len(hit_genes)
                info["total_genes"] = total_genes
                info["pct"] = round(len(hit_genes) / total_genes * 100) if total_genes else 0
        source_stats["pubmed_articles"] = len(knowledge.get("pubmed", []))
        source_stats["europepmc_articles"] = len(knowledge.get("europepmc", []))
        source_stats["stats_version"] = 3
        source_stats["rag_policy"] = "all-selected-genes; one initial literature query per gene; question-time literature retrieval remains enabled"
        from e2seq.data.vector_store import reset_vector_store
        store = reset_vector_store(session_id, llm=agents[session_id].llm)
        n_docs = store.reset_and_build(knowledge)
        agents[session_id]._vector_store = store
        knowledge.setdefault("_source_stats", {})["vector_chunks"] = n_docs
        knowledge.setdefault("_source_stats", {})["vector_retrieval_mode"] = "hybrid dense + BM25"
        from e2seq.agent.rag_persistence import save_rag_knowledge
        save_rag_knowledge(session_id, knowledge)
        rag_result = {
            "success": True,
            "n_docs": n_docs,
            "n_genes": len(knowledge["genes"]),
            "rag_policy_version": 3,
            "error": None,
        }
        return {"success": bool(rag_result.get("success")), "rag_status": "ready", "gene_count": len(genes), "rag": rag_result}
    except Exception as exc:
        logger.exception("Bulk RAG preparation failed for %s: %s", session_id, exc)
        return {"success": False, "rag_status": "failed", "gene_count": len(genes), "error": str(exc)}


def _run_bulk_question_handoff(
    session_id: str,
    selected_genes: list[str],
    abort_flag=None,
    force_rebuild: bool = False,
) -> dict:
    """Run enrichment/network work only after the user asks a question.

    Bulk statistics stay separate from the question-time knowledge build. The
    right-panel filters decide the gene list; this handoff then runs
    GO/KEGG/GSEA/STRING in parallel and builds the RAG context for the first
    question that uses the selected genes.
    """
    import time as _time

    handoff_started = _time.perf_counter()
    if abort_flag is not None and abort_flag.is_set():
        raise AbortChat("Bulk RAG cancelled before handoff")
    _restore_session_state(session_id)
    state = bulk_sessions.get(session_id)
    if state is None or not state.get("result"):
        return {"success": False, "rag_status": "not_ready", "error": "expression-profile statistics are not ready"}
    # A persisted summary is reusable only when it was built with the
    # current all-selected-gene retrieval policy.  Older sessions may still
    # contain the pre-retry 8-query-per-gene literature snapshot; refresh it
    # once rather than presenting stale transport failures forever.
    existing_rag = state.get("rag")
    if (
        not force_rebuild
        and isinstance(existing_rag, dict)
        and int(existing_rag.get("rag_policy_version") or 0) >= 3
    ):
        return existing_rag
    if existing_rag is not None or force_rebuild:
        state["rag"] = None
        _persist_bulk_state(session_id, state)

    result = dict(state["result"])
    available = {
        str(row.get("gene")).strip()
        for row in (result.get("result") or [])
        if str(row.get("gene") or "").strip()
    }
    full_genes = list(dict.fromkeys(str(g).strip() for g in (selected_genes or []) if str(g).strip()))
    full_genes = [gene for gene in full_genes if gene in available][:2000]
    if not full_genes:
        return {"success": False, "rag_status": "skipped_no_selection", "gene_count": 0,
                "error": "no filtered genes were selected"}

    # Keep the legacy rag_core_* state fields as aliases for compatibility, but
    # query every selected item. The selected-N control is the only cohort
    # limit; there is no hidden 50-item per-gene RAG cap.
    core_genes = list(full_genes)
    genes = full_genes
    state["selected_genes"] = full_genes
    state["rag_core_genes"] = core_genes
    result["rag_gene_sets"] = {"selected_genes": full_genes}
    result["rag_core_gene_sets"] = {"selected_genes": core_genes}
    state["progress_percent"] = 0
    state["progress_phase"] = "准备选定表达项目"
    state["status"] = "enriching"
    _persist_bulk_state(session_id, state)
    _bulk_progress(session_id, f"选定 {len(genes)} 个表达项目，开始并行执行 GO / KEGG / GSEA / STRING", 5)
    ranked = {}
    for row in result.get("result") or []:
        gene = str(row.get("gene") or "").strip()
        score = row.get("statistic", row.get("coef", row.get("log2FoldChange", 0)))
        try:
            ranked[gene] = float(score or 0)
        except (TypeError, ValueError):
            ranked[gene] = 0.0
    completed_tasks = 0
    total_tasks = max(1, 4 * len(result["rag_gene_sets"]))
    progress_lock = _threading.Lock()

    def _enrichment_progress(message: str) -> None:
        nonlocal completed_tasks
        with progress_lock:
            completed_tasks += 1
            completed = completed_tasks
        _bulk_progress(session_id, message, 20 + int(50 * completed / total_tasks))

    _bulk_progress(session_id, "读取选定表达项目的知识来源", 20)
    enrichment_started = _time.perf_counter()
    enrichment = run_batch_enrichment(
        result["rag_gene_sets"],
        ranked_genes=ranked,
        top_terms=int((state.get("config") or {}).get("top_terms", 10)),
        progress=_enrichment_progress,
    )
    if abort_flag is not None and abort_flag.is_set():
        raise AbortChat("Bulk RAG cancelled after enrichment")
    result["enrichment"] = enrichment
    result["core_enrichment"] = enrichment.get("core", {})
    enrichment_elapsed = round(max(0.0, _time.perf_counter() - enrichment_started), 3)
    state["result"] = result
    state.setdefault("timing", {})["enrichment_seconds"] = enrichment_elapsed
    _persist_bulk_state(session_id, state)
    _bulk_progress(session_id, "GO / KEGG / GSEA / STRING 已完成，正在构建 RAG", 70)

    state["status"] = "rag_building"
    rag_started = _time.perf_counter()
    gate_acquired = False
    try:
        while not gate_acquired:
            if abort_flag is not None and abort_flag.is_set():
                raise AbortChat("Bulk RAG cancelled while waiting for a retrieval slot")
            gate_acquired = _bulk_rag_session_gate.acquire(timeout=0.5)
        rag = _prepare_bulk_rag(session_id, result, abort_flag=abort_flag)
    finally:
        if gate_acquired:
            _bulk_rag_session_gate.release()
    state.setdefault("timing", {})["rag_elapsed_seconds"] = round(
        max(0.0, _time.perf_counter() - rag_started), 3
    )
    state["rag"] = rag
    state["status"] = "ready" if rag.get("rag_status") in {"ready", "skipped_no_api_key"} else "ready_without_rag"
    state.setdefault("timing", {})["question_handoff_seconds"] = round(
        max(0.0, _time.perf_counter() - handoff_started), 3
    )
    _bulk_progress(session_id, "选定表达项目的 RAG 上下文已准备完成", 100)
    _persist_bulk_state(session_id, state)
    return rag


async def _await_bulk_question_handoff(
    session_id: str,
    selected_genes: list[str],
    force_rebuild: bool = False,
) -> dict:
    """Run one first-question handoff per chat and cancel it on disconnect.

    ``asyncio.to_thread`` cannot interrupt the underlying synchronous worker by
    itself.  Keeping the cancellation event beside the task lets a closed
    browser request stop submitting new gene/API work instead of leaving an
    orphaned RAG batch consuming CPU in the background.
    """
    with _bulk_rag_jobs_lock:
        current = _bulk_rag_jobs.get(session_id)
        if current and not current["task"].done():
            task = current["task"]
            cancel_event = current["cancel_event"]
            owner = False
        else:
            cancel_event = _threading.Event()
            task = asyncio.create_task(
                asyncio.to_thread(
                    _run_bulk_question_handoff,
                    session_id,
                    selected_genes,
                    cancel_event,
                    force_rebuild,
                )
            )
            _bulk_rag_jobs[session_id] = {"task": task, "cancel_event": cancel_event}
            owner = True
    try:
        return await asyncio.shield(task)
    except AbortChat as exc:
        state = bulk_sessions.get(session_id)
        if state is not None:
            state["status"] = "ready_for_filter"
            state["progress_phase"] = "RAG handoff cancelled; selected data remain available"
            state["error"] = str(exc)
            _persist_bulk_state(session_id, state)
        return {"success": False, "rag_status": "cancelled", "error": str(exc)}
    except asyncio.CancelledError:
        if owner:
            cancel_event.set()
            logger.info("Bulk RAG cancellation requested for disconnected chat %s", session_id)
        raise
    finally:
        if owner:
            with _bulk_rag_jobs_lock:
                current = _bulk_rag_jobs.get(session_id)
                if current and current.get("task") is task:
                    _bulk_rag_jobs.pop(session_id, None)


def _run_bulk_analysis_job(session_id: str) -> None:
    state = bulk_sessions.get(session_id)
    if state is None:
        return
    import time as _time

    analysis_started = _time.perf_counter()
    try:
        state["status"] = "analyzing"
        state["progress_percent"] = 0
        state["progress_phase"] = "准备读取原始数据"
        _persist_bulk_state(session_id, state)
        _bulk_progress(session_id, "读取原始 count 与临床表；上传阶段未做过滤或归一化", 8)
        counts, clinical = load_bulk_tables(
            state["counts_path"], state["clinical_path"], gene_col=(state.get("config") or {}).get("gene_col") or None
        )
        _bulk_progress(session_id, "原始 count 与临床变量已读取，开始统计建模", 22)
        # R/DESeq2/edgeR/limma/cox runs are synchronous and may legitimately
        # take minutes.  Run the model in a worker while this thread emits a
        # bounded heartbeat, so the UI never mistakes an active model for a
        # frozen 22% upload stage.  The estimate is deliberately asymptotic:
        # it communicates liveness without pretending to know R's exact ETA.
        import math as _math
        from concurrent.futures import ThreadPoolExecutor as _ThreadPoolExecutor

        config = state.get("config") or {}
        analysis_type = str(config.get("analysis_type") or "differential").lower()
        if analysis_type == "differential":
            method_key = str(config.get("method") or "deseq2").lower()
            model_label = {
                "deseq2": "DESeq2",
                "edger": "edgeR",
                "limma_voom": "limma-voom",
            }.get(method_key, method_key)
        else:
            transform = str(config.get("expression_transform") or "vst")
            model_label = f"Cox / {transform}"
        estimated_seconds = max(
            30.0,
            min(1800.0, 0.01 * max(1, len(counts)) + 0.08 * max(1, len(counts.columns))),
        )
        model_slot_wait_started = _time.monotonic()
        while not _bulk_model_session_gate.acquire(blocking=False):
            waited = int(_time.monotonic() - model_slot_wait_started)
            _bulk_progress(
                session_id,
                f"统计资源排队中（{model_label}；已等待 {waited} 秒）",
                22,
            )
            _time.sleep(2)
        try:
            with _ThreadPoolExecutor(max_workers=1, thread_name_prefix="e2seq-bulk-model") as executor:
                future = executor.submit(BulkRNAAnalyzer(counts, clinical).run, config)
                started = _time.monotonic()
                while not future.done():
                    elapsed = int(_time.monotonic() - started)
                    # This is a liveness indicator, not a false exact ETA.  The
                    # old curve used 60% of a conservative estimate as its time
                    # constant, leaving a BRCA-sized job visually near 25% for
                    # minutes even while R was working normally.
                    fraction = 0.08 + 0.92 * (1.0 - _math.exp(-max(0.0, elapsed) / max(10.0, estimated_seconds * 0.25)))
                    progress = min(94, 22 + int(72 * fraction))
                    _bulk_progress(
                        session_id,
                        f"统计建模进行中（{model_label}，已运行 {elapsed} 秒）",
                        progress,
                    )
                    _time.sleep(2)
                result = future.result()
        finally:
            _bulk_model_session_gate.release()
        result_dict = result.as_dict()
        state["result"] = result_dict
        state.setdefault("timing", {})["statistical_model_seconds"] = round(
            max(0.0, _time.perf_counter() - analysis_started), 3
        )
        state["timing"]["analysis_elapsed_seconds"] = state["timing"]["statistical_model_seconds"]
        state["status"] = "ready_for_filter"
        state["rag"] = None
        _bulk_progress(session_id, f"统计分析完成：{result.n_genes_tested} 个表达项目；右侧筛选已就绪", 100)
        _persist_bulk_state(session_id, state)
    except (BulkAnalysisError, ValueError) as exc:
        state["status"] = "error"
        state["error"] = str(exc)
        _bulk_progress(session_id, f"表达谱分析失败：{exc}")
        _persist_bulk_state(session_id, state)
    except Exception as exc:
        logger.exception("Bulk analysis job failed for %s", session_id)
        state["status"] = "error"
        state["error"] = str(exc)
        _bulk_progress(session_id, f"表达谱分析失败：{exc}")
        _persist_bulk_state(session_id, state)


@app.post("/api/bulk/upload")
async def upload_bulk_data(
    request: Request,
    counts_file: UploadFile = File(...),
    clinical_file: UploadFile = File(...),
):
    """Stage raw integer counts and clinical variables as two separate files."""
    import time as _time

    upload_started = _time.perf_counter()
    session_id = "default"
    try:
        form = await request.form()
        session_id = str(form.get("session_id") or "default")
    except Exception:
        pass
    _restore_session_state(session_id)
    if session_id in datasets or session_id in bulk_sessions:
        raise HTTPException(status_code=400, detail="当前会话已有数据，请先清除后再上传表达谱文件")
    count_name = counts_file.filename or "counts.csv"
    clinical_name = clinical_file.filename or "clinical.csv"
    allowed = {".csv", ".tsv", ".txt", ".xlsx", ".xls"}
    if Path(count_name).suffix.lower() not in allowed or Path(clinical_name).suffix.lower() not in allowed:
        raise HTTPException(status_code=400, detail="表达谱文件仅支持 CSV、TSV 或 XLSX")
    count_path = _bulk_file_path(session_id, "counts", Path(count_name).suffix.lower() or ".csv")
    clinical_path = _bulk_file_path(session_id, "clinical", Path(clinical_name).suffix.lower() or ".csv")
    try:
        count_path.write_bytes(await counts_file.read())
        clinical_path.write_bytes(await clinical_file.read())
        preview = inspect_bulk_files(count_path, clinical_path)
    except Exception as exc:
        for path in (count_path, clinical_path):
            if path.exists():
                path.unlink()
        raise HTTPException(status_code=400, detail=f"表达谱文件读取失败：{exc}") from exc
    bulk_sessions[session_id] = {
        "status": "uploaded",
        "input_type": "raw_counts_clinical",
        "counts_path": str(count_path),
        "clinical_path": str(clinical_path),
        "counts_filename": count_name,
        "clinical_filename": clinical_name,
        "preview": preview,
        "progress": ["两份原始文件已上传；尚未执行过滤、归一化或建模"],
        "progress_percent": 100,
        "progress_phase": "文件上传与结构读取完成",
        "timing": {
            "upload_elapsed_seconds": round(max(0.0, _time.perf_counter() - upload_started), 3),
        },
        "config": None,
        "result": None,
        "rag": None,
        "gene_intersection": [],
    }
    _persist_bulk_state(session_id)
    return {
        "success": True,
        "session_id": session_id,
        "counts_filename": count_name,
        "clinical_filename": clinical_name,
        "preview": preview,
        "analysis_options": ["differential", "survival"],
        "differential_methods": ["deseq2", "edger", "limma_voom"],
        "survival_transforms": ["vst", "logcpm", "log2_tpm_1"],
    }


@app.post("/api/bulk/result-upload")
async def upload_bulk_result(request: Request, result_file: UploadFile = File(...)):
    """Stage a user-computed differential/prognostic result table."""
    session_id = "default"
    try:
        form = await request.form()
        session_id = str(form.get("session_id") or "default")
    except Exception:
        pass
    _restore_session_state(session_id)
    if session_id in datasets:
        raise HTTPException(status_code=400, detail="当前会话已有数据，请先清除后再上传结果表")
    existing = bulk_sessions.get(session_id)
    if existing and existing.get("input_type") != "user_precomputed_result":
        raise HTTPException(status_code=400, detail="当前会话已有原始 count/临床数据，请先清除后再上传结果表")
    if existing and existing.get("status") not in {"result_uploaded", "uploaded"}:
        raise HTTPException(status_code=400, detail="结果表已经载入，请先清除当前数据后再重新上传")
    filename = result_file.filename or "analysis_result.csv"
    allowed = {".csv", ".tsv", ".txt", ".xlsx", ".xls"}
    suffix = Path(filename).suffix.lower() or ".csv"
    if suffix not in allowed:
        raise HTTPException(status_code=400, detail="结果表仅支持 CSV、TSV 或 XLSX")
    result_path = _bulk_file_path(session_id, "result", suffix)
    try:
        result_path.write_bytes(await result_file.read())
        preview = inspect_bulk_result_file(result_path)
    except Exception as exc:
        if result_path.exists():
            result_path.unlink()
        raise HTTPException(status_code=400, detail=f"结果表读取失败：{exc}") from exc
    bulk_sessions[session_id] = {
        "status": "result_uploaded",
        "input_type": "user_precomputed_result",
        "result_path": str(result_path),
        "result_filename": filename,
        "preview": {"result": preview},
        "progress": ["用户结果表已上传；尚未执行重新分析"],
        "progress_percent": 100,
        "progress_phase": "用户结果表结构读取完成",
        "config": None,
        "result": None,
        "rag": None,
        "gene_intersection": [],
    }
    _persist_bulk_state(session_id)
    return {
        "success": True,
        "session_id": session_id,
        "result_filename": filename,
        "result_preview": preview,
        "analysis_options": ["differential", "survival"],
    }


@app.post("/api/bulk/result-configure")
async def configure_bulk_result(request: Request):
    """Map columns in a user result table without recomputing its statistics."""
    body = await request.json()
    session_id = str(body.get("session_id") or "default")
    _restore_session_state(session_id)
    state = bulk_sessions.get(session_id)
    if state is None or state.get("input_type") != "user_precomputed_result" or not state.get("result_path"):
        raise HTTPException(status_code=400, detail="请先上传用户自己的差异/预后结果表")
    try:
        analysis_type = str(body.get("analysis_type") or "").lower()
        config = {
            "analysis_type": analysis_type,
            "gene_col": str(body.get("gene_col") or ""),
            "effect_col": str(body.get("effect_col") or ""),
            "effect_metric": str(body.get("effect_metric") or ("log2fc" if analysis_type == "differential" else "HR")),
            "pvalue_col": str(body.get("pvalue_col") or ""),
            "padj_col": str(body.get("padj_col") or ""),
            "direction_col": str(body.get("direction_col") or ""),
            "group_col": str(body.get("group_col") or ""),
            "group_values": body.get("group_values") or [],
            "result_file": state.get("result_filename", ""),
            "input_type": "user_precomputed_result",
            "dataset_description": str(body.get("dataset_description") or "").strip(),
            "dataset_prompt": str(body.get("dataset_prompt") or "").strip(),
        }
        if len(config["dataset_prompt"]) > 10000:
            raise BulkAnalysisError("Dataset prompt must be at most 10000 characters")
        result = build_user_bulk_result(state["result_path"], config)
        state["config"] = config
        state["status"] = "ready_for_filter"
        state["error"] = None
        state["result"] = result.as_dict()
        state["rag"] = None
        state["progress"] = ["用户结果表已载入；未重新计算统计量；右侧筛选已就绪"]
        state["progress_percent"] = 100
        state["progress_phase"] = f"用户结果表已载入：{result.n_genes_tested} 个表达项目；右侧筛选已就绪"
        _persist_bulk_state(session_id, state)
        return {
            "success": True,
            "session_id": session_id,
            "status": state["status"],
            "analysis_type": analysis_type,
            "n_genes": result.n_genes_tested,
            "n_rows": len(result.result),
            "group_col": config.get("group_col", ""),
            "group_values": config.get("group_values", []),
            "result": result.as_dict(),
            "raw_result_unchanged": True,
        }
    except (BulkAnalysisError, ValueError) as exc:
        state["error"] = str(exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/bulk/configure")
async def configure_bulk(request: Request):
    """Store user-selected columns and contrast/survival settings without running analysis."""
    session_id = "default"
    body = await request.json()
    session_id = str(body.get("session_id") or "default")
    _restore_session_state(session_id)
    state = bulk_sessions.get(session_id)
    if state is None:
        raise HTTPException(status_code=400, detail="请先上传原始 count 和临床变量两份文件")
    try:
        counts, clinical = load_bulk_tables(
            state["counts_path"], state["clinical_path"], gene_col=body.get("gene_col") or None
        )
        sample_col = str(body.get("sample_col") or "")
        if sample_col not in clinical.columns:
            raise BulkAnalysisError(f"临床样本 ID 列 '{sample_col}' 不存在")
        analysis_type = str(body.get("analysis_type") or "").lower()
        if analysis_type not in {"differential", "survival"}:
            raise BulkAnalysisError("请选择差异分析或预后分析")
        if analysis_type == "differential":
            for key in ("group_col", "control_level", "case_level"):
                if not str(body.get(key) or ""):
                    raise BulkAnalysisError(f"差异分析必须选择 {key}")
            if str(body.get("group_col")) not in clinical.columns:
                raise BulkAnalysisError("分组列不存在")
        else:
            time_type = str(body.get("time_type") or "duration").lower().replace("-", "_")
            if time_type in {"date", "date_ymd", "ymd", "calendar_date"}:
                time_type = "date_ymd"
                required = ("start_date_col", "end_date_col", "event_col")
            else:
                time_type = "duration"
                required = ("time_col", "event_col")
            for key in required:
                if not str(body.get(key) or ""):
                    raise BulkAnalysisError(f"预后分析必须选择 {key}")
                if str(body.get(key)) not in clinical.columns:
                    raise BulkAnalysisError(f"临床列 '{body.get(key)}' 不存在")
            body["time_type"] = time_type
        body["analysis_type"] = analysis_type
        validation = validate_bulk_configuration(counts, clinical, body)
        config = dict(body)
        config["analysis_type"] = analysis_type
        config["sample_col"] = sample_col
        config["covariates"] = [c for c in config.get("covariates", []) if c in clinical.columns]
        config["dataset_description"] = str(config.get("dataset_description") or "").strip()
        config["dataset_prompt"] = str(config.get("dataset_prompt") or "").strip()
        if len(config["dataset_prompt"]) > 10000:
            raise BulkAnalysisError("Dataset prompt must be at most 10000 characters")
        state["config"] = config
        state["status"] = "configured"
        state["error"] = None
        state["result"] = None
        _bulk_progress(session_id, "配置已保存；仍未对原始 count 做任何处理")
        _persist_bulk_state(session_id, state)
        return {"success": True, "session_id": session_id, "analysis_type": analysis_type,
                "counts_genes": len(counts), "clinical_rows": len(clinical),
                "validation": validation,
                "raw_counts_unchanged": True}
    except (BulkAnalysisError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/bulk/analyze")
async def analyze_bulk(request: Request):
    """Queue statistics; enrichment/network/RAG starts later with a question."""
    body = await request.json()
    session_id = str(body.get("session_id") or "default")
    _restore_session_state(session_id)
    state = bulk_sessions.get(session_id)
    if state is None or not state.get("config"):
        raise HTTPException(status_code=400, detail="请先上传并完成表达谱分析配置")
    if state.get("status") in {"analyzing", "enriching", "rag_building"}:
        return {"success": True, "status": state.get("status"), "queued": False}
    state["status"] = "queued"
    state["progress"] = []
    state["progress_percent"] = 0
    state["progress_phase"] = "准备统计分析"
    _persist_bulk_state(session_id, state)
    job = asyncio.create_task(asyncio.to_thread(_run_bulk_analysis_job, session_id))
    bulk_jobs[session_id] = job
    return {"success": True, "status": "queued", "queued": True, "session_id": session_id}


@app.get("/api/bulk/status/{session_id}")
async def get_bulk_status(session_id: str):
    _restore_session_state(session_id)
    state = bulk_sessions.get(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="bulk session not found")
    return {"session_id": session_id, "status": state.get("status"), "error": state.get("error"),
            "progress": list(state.get("progress", [])),
            "progress_percent": state.get("progress_percent", 0),
            "progress_phase": state.get("progress_phase", ""),
            "rag": state.get("rag"),
            "timing": dict(state.get("timing") or {}),
            "preview": state.get("preview"), "config": state.get("config"),
            "selected_genes": list(state.get("selected_genes") or [])}


@app.get("/api/bulk/result/{session_id}")
async def get_bulk_result(session_id: str, include_rows: bool = False):
    _restore_session_state(session_id)
    state = bulk_sessions.get(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="bulk session not found")
    if not state.get("result"):
        return {"session_id": session_id, "status": state.get("status"), "result": None}
    result = dict(state["result"])
    if not include_rows:
        result.pop("result", None)
    return {"session_id": session_id, "status": state.get("status"), "result": _bulk_json_safe(result)}


@app.post("/api/bulk/rag")
async def select_bulk_rag(request: Request):
    """Compatibility endpoint for an explicit selected-gene handoff."""
    body = await request.json()
    session_id = str(body.get("session_id") or "default")
    _restore_session_state(session_id)
    state = bulk_sessions.get(session_id)
    if state is None or not state.get("result"):
        raise HTTPException(status_code=400, detail="请先完成表达谱统计分析")
    explicit_genes = [
        str(gene).strip()
        for gene in (body.get("selected_genes") or [])
        if str(gene).strip()
    ]
    selected = [str(name) for name in (body.get("gene_sets") or [])]
    all_sets = {}
    # Older result tables expose ``gene_sets`` (the display groups), while a
    # filtered bulk cohort is persisted under ``rag_gene_sets``.  Merge both
    # namespaces so an explicit repair cannot silently fall back to 50 genes.
    for source_sets in (
        state["result"].get("gene_sets") or {},
        state["result"].get("rag_gene_sets") or {},
    ):
        if isinstance(source_sets, dict):
            all_sets.update(source_sets)
    selected_sets = {name: all_sets[name] for name in selected if name in all_sets}
    if explicit_genes:
        selected_genes = list(dict.fromkeys(explicit_genes))
        selected_set_names = ["selected_genes"]
    else:
        if not selected_sets:
            raise HTTPException(status_code=400, detail="至少选择一个核心基因集合")
        selected_genes = list(dict.fromkeys(gene for genes in selected_sets.values() for gene in genes))
        selected_set_names = list(selected_sets)
    # ``force_rebuild`` is intentionally explicit and is used for repairing a
    # persisted RAG snapshot after an adapter/rate-limit fix.  Normal user
    # questions continue to reuse a policy-compatible snapshot.
    force_rebuild = bool(body.get("force_rebuild") or body.get("force"))
    rag = await _await_bulk_question_handoff(
        session_id,
        selected_genes,
        force_rebuild=force_rebuild,
    )
    _bulk_progress(session_id, f"已按显式选择提交 {len(selected_genes)} 个表达项目到富集与 RAG")
    return {
        "success": True,
        "status": state["status"],
        "rag": rag,
        "gene_sets": selected_set_names,
        "force_rebuild": force_rebuild,
    }


@app.post("/api/upload-csv")
async def upload_csv(request: Request, file: UploadFile = File(...)):
    """Upload CSV/TSV/XLSX for table analysis and return detected columns."""
    import pandas as pd, io
    form = await request.form()
    session_id = form.get("session_id") or "default"

    _restore_session_state(session_id)

    if session_id in datasets:
        raise HTTPException(status_code=400, detail="当前会话已有数据，请先点击“清除数据”后再上传")

    content = await file.read()
    filename = file.filename or ""
    ext = Path(filename).suffix.lower()

    try:
        if ext == ".xlsx":
            df = pd.read_excel(io.BytesIO(content))
        elif ext == ".tsv":
            df = pd.read_csv(io.BytesIO(content), sep="\t", encoding="utf-8")
        else:
            # default csv fallback
            try:
                df = pd.read_csv(io.BytesIO(content), encoding="utf-8")
            except Exception:
                df = pd.read_csv(io.BytesIO(content), sep="\t", encoding="utf-8")

        columns = list(df.columns)
        n_rows = len(df)

        # Persist normalized CSV for configure-csv
        safe = "".join(c for c in session_id if c.isalnum() or c in "-_")
        csv_path = _DATASET_DIR / f"{safe}_csv.csv"
        df.to_csv(csv_path, index=False, encoding="utf-8")

        logger.info(f"Table uploaded for {session_id}: {n_rows} rows, columns: {columns}, ext={ext}")
        return {"success": True, "session_id": session_id, "columns": columns, "n_rows": n_rows, "filename": filename}
    except Exception as e:
        logger.error(f"Table upload failed: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to parse table file: {e}")


@app.post("/api/configure-csv")
async def configure_csv(request: Request):
    """Configure CSV analysis: map columns and apply filters, then initialise agent.
    Stores a synthetic AnnData-like object in datasets so the orchestrator can use
    the same agentic RAG pipeline.
    """
    import pandas as pd, io
    import anndata
    import numpy as np

    # Support both JSON and FormData
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        body = await request.json()
        session_id = body.get("session_id", "default")
        group_col = body.get("group_col", "")
        gene_col = body.get("gene_col", "name")
        expr_type = body.get("expr_type", "log2FC")
        expr_col = body.get("expr_col", "")
        expr_thresh = body.get("expr_thresh", None)
        sig_col = body.get("sig_col", "")
        sig_thresh = body.get("sig_thresh", 0.05)
        try:
            n_top_genes = max(0, int(body.get("n_top_genes", 30)))
        except (TypeError, ValueError):
            n_top_genes = 0
        dataset_description = (body.get("dataset_description", "") or "").strip()
        dataset_prompt = (body.get("dataset_prompt", "") or "").strip()
        if len(dataset_prompt) > 10000:
            raise HTTPException(status_code=400, detail="Dataset prompt must be at most 10000 characters")
        # Parse enabled APIs and DBs from JSON body
        enabled_apis = body.get("enabled_apis", list(DEFAULT_ANSWER_APIS))
        enabled_dbs = body.get("enabled_dbs", ["string","hmdb","trrust","gutmgene"])
    else:
        form = await request.form()
        session_id = form.get("session_id", "default")
        group_col = form.get("group_col", "")
        gene_col = form.get("gene_col", "name")
        expr_type = form.get("expr_type", "log2FC")
        expr_col = form.get("expr_col", "")
        expr_thresh = form.get("expr_thresh")
        sig_col = form.get("sig_col", "")
        sig_thresh = form.get("sig_thresh", "0.05")
        try:
            n_top_genes = max(0, int(form.get("n_top_genes", "30")))
        except (TypeError, ValueError):
            n_top_genes = 0
        dataset_description = (form.get("dataset_description", "") or "").strip()
        dataset_prompt = (form.get("dataset_prompt", "") or "").strip()
        if len(dataset_prompt) > 10000:
            raise HTTPException(status_code=400, detail="Dataset prompt must be at most 10000 characters")

        # Parse enabled APIs and DBs from JSON strings
        try:
            enabled_apis = json.loads(form.get("enabled_apis", json.dumps(DEFAULT_ANSWER_APIS)))
        except Exception:
            enabled_apis = list(DEFAULT_ANSWER_APIS)
        try:
            enabled_dbs = json.loads(form.get("enabled_dbs", '["string","hmdb","trrust","gutmgene"]'))
        except Exception:
            enabled_dbs = ["string","hmdb","trrust","gutmgene"]

    _restore_session_state(session_id)

    safe = "".join(c for c in session_id if c.isalnum() or c in "-_")
    csv_path = _DATASET_DIR / f"{safe}_csv.csv"
    if not csv_path.exists():
        raise HTTPException(status_code=400, detail="请先上传 CSV 文件")

    try:
        try:
            df = pd.read_csv(csv_path, encoding="utf-8")
        except Exception:
            df = pd.read_csv(csv_path, sep="\t", encoding="utf-8")

        # Prefer user-selected expression value column; fallback to expr_type when it is an actual column name
        actual_expr_col = expr_col or (expr_type if expr_type in df.columns else "")

        # Validate gene column
        if gene_col not in df.columns:
            raise HTTPException(status_code=400, detail=f"基因列 '{gene_col}' 不存在。可用列: {list(df.columns)}")

        # Group col is optional - if not provided, use a single group
        if group_col and group_col in df.columns:
            groups = sorted(df[group_col].astype(str).unique().tolist())
        else:
            # Create synthetic group
            df["_default_group_"] = "Data"
            groups = ["Data"]
            group_col = "_default_group_"

        # Compute original unique gene count BEFORE filtering (for display)
        n_genes_total = len(df[gene_col].astype(str).unique())

        # Apply significance filter
        if sig_col and sig_col in df.columns and sig_thresh is not None:
            try:
                df = df[df[sig_col].astype(float) <= float(sig_thresh)]
            except Exception:
                pass

        # Apply expression threshold (on absolute value)
        if expr_thresh is not None and actual_expr_col in df.columns:
            try:
                df = df[df[actual_expr_col].abs() >= float(expr_thresh)]
            except Exception:
                pass

        # Keep the uploaded result order: after applying the current filters,
        # "top N" means the first N unique expression items in that order.
        conditioned_gene_values = df[gene_col].astype(str)
        conditioned_genes = list(dict.fromkeys(conditioned_gene_values.tolist()))
        n_genes_conditioned = len(conditioned_genes)
        n_rows_conditioned = len(df)
        if n_top_genes > 0:
            selected_genes = set(conditioned_genes[:n_top_genes])
            df = df[conditioned_gene_values.isin(selected_genes)].copy()
            all_genes = conditioned_genes[:n_top_genes]
        else:
            all_genes = conditioned_genes
        n_genes = len(all_genes)
        n_filtered = len(df)
        logger.info(f"CSV configured for {session_id}: {n_filtered} rows after top-N selection, {n_genes} unique genes ({n_genes_conditioned} after filters), {len(groups)} groups")

        # Build a minimal AnnData so the orchestrator can be initialised normally
        # Rows = genes, Cols = groups, values = mean expr per group
        gene_index = {g: i for i, g in enumerate(all_genes)}
        group_index = {g: i for i, g in enumerate(groups)}
        expr_matrix = np.zeros((n_genes, len(groups)), dtype=np.float32)
        for _, row in df.iterrows():
            gi = gene_index.get(str(row[gene_col]))
            gri = group_index.get(str(row[group_col]))
            if gi is not None and gri is not None:
                try:
                    val = row[actual_expr_col] if actual_expr_col in df.columns else 0
                    expr_matrix[gi, gri] = float(val)
                except Exception:
                    pass

        adata = anndata.AnnData(
            X=expr_matrix,
            obs=pd.DataFrame(index=all_genes),
            var=pd.DataFrame(index=groups),
        )
        # Store CSV-specific metadata in uns
        adata.uns["e2sc_data_mode"] = "csv"
        adata.uns["e2sc_session_id"] = session_id
        adata.uns["e2sc_dataset_description"] = dataset_description
        adata.uns["e2sc_dataset_prompt"] = dataset_prompt
        adata.uns["e2sc_display_genes"] = n_genes       # 唯一基因数（展示用）
        adata.uns["e2sc_display_rows"] = n_filtered     # 过滤后行数（展示用）
        adata.uns["e2sc_conditioned_genes"] = n_genes_conditioned
        adata.uns["e2sc_conditioned_rows"] = n_rows_conditioned
        adata.uns["e2sc_group_col"] = group_col
        adata.uns["e2sc_celltype_col"] = ""
        adata.uns["e2sc_gene_col"] = gene_col
        adata.uns["e2sc_expr_col"] = actual_expr_col
        adata.uns["e2sc_expr_type"] = expr_type
        adata.uns["e2sc_sig_col"] = sig_col
        adata.uns["e2sc_sig_thresh"] = sig_thresh
        adata.uns["e2sc_expr_thresh"] = expr_thresh
        adata.uns["e2sc_enabled_apis"] = enabled_apis
        adata.uns["e2sc_enabled_dbs"] = enabled_dbs
        adata.uns["e2sc_n_top_genes"] = n_top_genes
        adata.uns["e2sc_celltype_labels"] = {}
        adata.uns["e2sc_group_labels"] = {}
        adata.uns["e2sc_groups"] = groups
        adata.uns["e2sc_all_genes"] = all_genes
        record_cols = [group_col, gene_col]
        if actual_expr_col and actual_expr_col in df.columns:
            record_cols.append(actual_expr_col)
        if sig_col and sig_col in df.columns:
            record_cols.append(sig_col)
        adata.uns["e2sc_csv_records"] = df[record_cols].to_json(orient="records")

        datasets[session_id] = adata

        # Initialise agent
        config = get_config()
        if not config.llm.api_key:
            raise HTTPException(status_code=400, detail="请先在设置页面配置 API Key")
        security = get_security_manager()
        decrypted_key = security.decrypt(config.llm.api_key)
        existing = agents.get(session_id)
        if existing is not None:
            try:
                existing.load_data(adata)
                existing._session_id = session_id
            except Exception as e:
                logger.warning(f"Failed to reload data on existing agent: {e}")
        else:
            from e2seq import E2seqAgent
            agents[session_id] = E2seqAgent(
                adata=adata,
                llm_provider=config.llm.provider,
                api_key=decrypted_key,
                model=config.llm.model,
                session_id=session_id,
            )
            agents[session_id]._session_id = session_id

        # Persist the configured table-backed AnnData so a reopened chat can
        # restore its analysis context without asking for the CSV again.
        _save_dataset(session_id, adata)

        return {
            "success": True,
            "session_id": session_id,
            "n_genes": n_genes,
            "n_genes_total": n_genes_total,  # original count before filtering
            "n_genes_conditioned": n_genes_conditioned,
            "n_rows_filtered": n_filtered,
            "n_rows_conditioned": n_rows_conditioned,
            "groups": groups,
            "expr_type": expr_type,
            # cells=过滤后行数（display only），genes=原始唯一基因数（display only）
            "cells": n_filtered,
            "genes": n_genes_total,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"configure-csv failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/csv-gene-count")
async def csv_gene_count(request: Request):
    """Return filtered unique gene count for current uploaded CSV settings."""
    import pandas as pd

    form = await request.form()
    session_id = form.get("session_id", "default")
    gene_col = form.get("gene_col", "")
    expr_col = form.get("expr_col", "")
    expr_thresh = form.get("expr_thresh")
    sig_col = form.get("sig_col", "")
    sig_thresh = form.get("sig_thresh")
    top_n_raw = form.get("n_top_genes", "0")
    try:
        top_n = max(0, int(top_n_raw))
    except (TypeError, ValueError):
        top_n = 0

    safe = "".join(c for c in session_id if c.isalnum() or c in "-_")
    csv_path = _DATASET_DIR / f"{safe}_csv.csv"
    if not csv_path.exists():
        raise HTTPException(status_code=400, detail="请先上传 CSV 文件")

    try:
        try:
            df = pd.read_csv(csv_path, encoding="utf-8")
        except Exception:
            df = pd.read_csv(csv_path, sep="\t", encoding="utf-8")

        if not gene_col or gene_col not in df.columns:
            return {"n_genes": 0, "n_rows_filtered": 0}

        if sig_col and sig_col in df.columns and sig_thresh not in (None, ""):
            try:
                df = df[df[sig_col].astype(float) <= float(sig_thresh)]
            except Exception:
                pass

        if expr_col and expr_col in df.columns and expr_thresh not in (None, ""):
            try:
                df = df[df[expr_col].astype(float).abs() >= float(expr_thresh)]
            except Exception:
                pass

        conditioned_gene_values = df[gene_col].astype(str)
        conditioned_genes = list(dict.fromkeys(conditioned_gene_values.tolist()))
        n_genes_conditioned = len(conditioned_genes)
        n_rows_conditioned = len(df)
        if top_n > 0:
            selected_genes = set(conditioned_genes[:top_n])
            df = df[conditioned_gene_values.isin(selected_genes)]
        n_genes = int(df[gene_col].astype(str).nunique())
        return {
            "n_genes": n_genes,
            "n_genes_conditioned": n_genes_conditioned,
            "n_rows_filtered": int(len(df)),
            "n_rows_conditioned": int(n_rows_conditioned),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/clear-data")
async def clear_data(body: Dict[str, Any]):
    """Clear uploaded dataset and agent for a session, resetting to no-data state.

    IMPORTANT: This must clear BOTH in-memory state AND persisted disk files,
    otherwise data reappears on page reload when session_id (UUID) happens to match
    a previously persisted h5ad file.
    """
    session_id = str(body.get("session_id") or "default")
    # This action clears the data/RAG plane but intentionally keeps the chat
    # transcript.  Deleting the chat itself uses the same cascade with
    # mark_deleted=True and also removes the transcript below.
    cleared = _purge_session_artifacts(session_id, mark_deleted=False)
    return {"success": True, "cleared": cleared, "session_id": session_id}


@app.get("/api/group-values")
async def get_group_values(session_id: str = "default", col: str = ""):
    """Return unique values of a given obs column for group alias configuration."""
    adata = datasets.get(session_id)
    if adata is None:
        return {"values": []}
    if not col or col not in adata.obs.columns:
        return {"values": []}
    values = sorted(adata.obs[col].astype(str).unique().tolist())
    return {"values": values}


@app.get("/api/progress/{session_id}")
async def get_progress(session_id: str):
    """Return recent progress messages for a running analysis session."""
    with _progress_lock:
        msgs = list(_progress.get(session_id, []))
    return {"session_id": session_id, "messages": msgs}


async def _stream_agent_chat(chat_id: str, message: str):
    """Generator that yields SSE events for agent chat.

    NON-STREAMING design: progress events (`event: thinking`) are streamed in
    real-time so the UI can show what backend is doing, but the LLM text
    itself is delivered in a single `event: done` event after the agent
    finishes. This used to stream per-token chunks too, but that path was
    fragile (text-queue drainer tasks, "dictionary changed size during
    iteration" errors, run-time interleaving bugs). The user explicitly
    asked to stop experimenting with streaming — only progress events stream,
    final response is delivered in one shot.

    Supports cancellation via _abort_events[chat_id].set().
    """
    import asyncio
    import plotly
    from e2seq.utils import get_config, get_security_manager
    from e2seq import E2seqAgent

    # Register abort event for this chat session
    abort_event = asyncio.Event()
    _abort_events[chat_id] = abort_event

    # threading.Event checked inside the agent thread for fast abort
    abort_flag = _threading.Event()

    try:
        if abort_event.is_set():
            yield "event: aborted\ndata: {}\n\n"
            return

        _restore_session_state(chat_id)
        _ensure_bulk_chat_ready(chat_id)
        _ensure_dataset_chat_ready(chat_id)

        # Persist user message immediately so it's never lost even if agent crashes
        _save_chat_message(chat_id, "user", message)

        _push_progress(chat_id, f"[进度] 开始处理请求: {message[:60]}")

        # Initialize agent if needed
        config = get_config()
        if not config.llm.api_key:
            yield "event: error\ndata: \u8bf7\u5148\u5728\u8bbe\u7f6e\u9875\u9762\u914d\u7f6e API Key\n\n"
            return

        security = get_security_manager()
        try:
            decrypted_key = security.decrypt(config.llm.api_key)
        except Exception as e:
            yield f"event: error\ndata: API Key\u89e3\u5bc6\u5931\u8d25: {str(e)}\n\n"
            return
        adata = datasets.get(chat_id)
        agent = agents.get(chat_id)
        if agent is None:
            try:
                agent = E2seqAgent(
                    adata=adata,
                    llm_provider=config.llm.provider,
                    api_key=decrypted_key,
                    model=config.llm.model,
                    session_id=chat_id,
                )
                agents[chat_id] = agent
            except Exception as e:
                yield f"event: error\ndata: Agent\u521d\u59cb\u5316\u5931\u8d25: {str(e)}\n\n"
                return

        # Install progress handler that mirrors orchestrator INFO logs to the
        # progress_queue (and via _push_progress to /api/progress/{chat_id}).
        _prog_handler = _ProgressHandler(chat_id, bind_current_thread=False)
        _orch_logger = logging.getLogger("e2seq.agent.orchestrator_optimized")
        _orch_logger.addHandler(_prog_handler)
        logger.info(f"[SSE] Handler added for chat_id={chat_id}")

        # Progress queue for real-time progress streaming
        progress_queue: asyncio.Queue = asyncio.Queue()
        _running_loop = asyncio.get_running_loop()
        _loop_closed = False

        def progress_callback(msg: str):
            """Thread-safe callback: schedule a put_nowait on the event loop."""
            if _loop_closed:
                return
            try:
                _running_loop.call_soon_threadsafe(progress_queue.put_nowait, msg)
            except RuntimeError:
                # Event loop closed (client disconnected)
                pass
            except Exception as _pcb_e:
                logger.debug(f"[SSE] progress_callback failed: {_pcb_e}")

        # Run agent in executor — text_queue=None forces the synthesizer down
        # the non-streaming LLM branch (a single blocking call) so the full
        # response is available in agent_result_holder["result"] when the
        # executor_future completes.
        loop = asyncio.get_running_loop()
        agent_result_holder: dict = {}

        def run_agent():
            try:
                _prog_handler.bind_to_current_thread()
                agent_result_holder["result"] = agent.chat(
                    message,
                    progress_callback=progress_callback,
                    text_queue=None,    # non-streaming path on purpose
                    abort_flag=abort_flag,
                )
            except AbortChat as e:
                agent_result_holder["aborted"] = True
                agent_result_holder["abort_reason"] = str(e) if str(e) else "User requested abort"
            except Exception as e:
                agent_result_holder["error"] = e

        executor_future = loop.run_in_executor(None, run_agent)

        # Stream progress events until agent finishes. Emit a keepalive ping
        # every 2s so the browser's fetch doesn't time out during long LLM
        # calls (GLM-5 / DeepSeek on 60k-char prompts can take 3-5 minutes).
        _PING_INTERVAL = 2
        try:
            while True:
                if executor_future.done():
                    # Drain any final progress messages the agent emitted in
                    # the last few hundred ms before finishing.
                    while not progress_queue.empty():
                        try:
                            msg = progress_queue.get_nowait()
                            _push_progress(chat_id, msg)
                            payload = json.dumps({"step": "progress", "content": msg})
                            yield f"event: thinking\ndata: {payload}\n\n"
                        except Exception:
                            break
                    break

                try:
                    msg = await asyncio.wait_for(progress_queue.get(), timeout=_PING_INTERVAL)
                    _push_progress(chat_id, msg)
                    payload = json.dumps({"step": "progress", "content": msg})
                    logger.info(f"[SSE] yield thinking: {msg[:80]}")
                    yield f"event: thinking\ndata: {payload}\n\n"
                except asyncio.TimeoutError:
                    # No progress in 2s — emit keepalive so browser keeps the
                    # connection alive. yield is fine inside an async-for;
                    # StreamingResponse forwards each yielded str.
                    yield ": keepalive\n\n"
        except asyncio.CancelledError:
            # Client disconnected. Signal the agent thread to abort and let
            # the executor_future be cleaned up by the outer finally.
            abort_flag.set()
            try:
                executor_future.cancel()
            except Exception:
                pass
            raise

        # Block until agent actually finishes (executor_future.done() can be
        # momentarily true while result() is still being set). We don't need
        # to .result() here because the agent has already populated
        # agent_result_holder by this point.

        _orch_logger.removeHandler(_prog_handler)

        # ── Emit terminal SSE events ────────────────────────────────────
        if agent_result_holder.get("aborted"):
            try:
                yield f"event: aborted\ndata: {json.dumps({'reason': agent_result_holder.get('abort_reason', 'User requested abort')})}\n\n"
            except CLIENT_DISCONNECT_EXCEPTIONS:
                raise
            return

        if abort_event.is_set():
            try:
                yield f"event: aborted\ndata: {json.dumps({'reason': 'User requested abort'})}\n\n"
            except CLIENT_DISCONNECT_EXCEPTIONS:
                raise
            return

        _push_progress(chat_id, "[进度] 解读完成")

        if "error" in agent_result_holder:
            _stream_err = agent_result_holder["error"]
            _stream_err_msg = str(_stream_err)
            try:
                _save_chat_message(chat_id, "assistant", f"[Error] {_stream_err_msg}")
            except Exception as _pe:
                logger.warning(f"Failed to persist stream error: {_pe}")
            try:
                yield f"event: error\ndata: {_stream_err_msg}\n\n"
            except CLIENT_DISCONNECT_EXCEPTIONS:
                raise
            return

        response = agent_result_holder.get("result", {})
        if not isinstance(response, dict):
            response = {"text": str(response) if response else "", "plots": [], "data": {}, "thinking": []}
        _stream_data = response.get("data") if isinstance(response.get("data"), dict) else {}
        _persist_answer_usage(
            chat_id,
            _stream_data.get("llm_usage"),
            _stream_data.get("source_stats"),
            bulk_sessions.get(chat_id),
        )

        # Yield recorded thinking steps (these are steps the agent accumulated
        # and the frontend uses to render the collapsible "thinking" sections).
        for step in response.get("thinking", []):
            content = json.dumps({"step": step.get("step", ""), "content": step.get("content", "")})
            try:
                yield f"event: thinking\ndata: {content}\n\n"
            except CLIENT_DISCONNECT_EXCEPTIONS:
                raise

        # Serialize plotly figures into JSON strings the frontend can render.
        plots_data = []
        for item in response.get("plots") or []:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                plot_name, fig = item
            else:
                continue
            try:
                fig_json = plotly.io.to_json(fig)
                plots_data.append({"title": plot_name, "figure": fig_json})
            except Exception:
                pass
        if plots_data:
            try:
                yield f"event: plots\ndata: {json.dumps(plots_data)}\n\n"
            except CLIENT_DISCONNECT_EXCEPTIONS:
                raise

        src_stats = response.get("data", {}).get("source_stats", {})
        if src_stats:
            try:
                yield f"event: source_stats\ndata: {json.dumps(src_stats)}\n\n"
            except CLIENT_DISCONNECT_EXCEPTIONS:
                raise

        # Persist assistant text for the chat history sidebar.
        try:
            _save_chat_message(chat_id, "assistant", response.get("text", ""))
        except Exception as _pe:
            logger.warning(f"Failed to persist chat message: {_pe}")

        # Single `done` event with the full response. Use default=str so any
        # numpy arrays / sets / bytes inside response.data don't crash the
        # serializer and silently kill the stream.
        resp_body = {
            "response": response.get("text", ""),
            "plots": plots_data,
            "chat_id": chat_id,
            "data": response.get("data", {}),
        }
        try:
            done_payload = json.dumps(resp_body, default=str, ensure_ascii=False)
        except Exception as _je:
            logger.error(f"[SSE] Failed to serialize done payload: {_je}")
            done_payload = json.dumps({
                "response": response.get("text", ""),
                "plots": plots_data,
                "chat_id": chat_id,
                "data": {},
            }, ensure_ascii=False)
        logger.info(f"[SSE] Yielding done event for chat_id={chat_id}, response_len={len(resp_body.get('response', ''))}, plots={len(plots_data)}")
        try:
            yield f"event: done\ndata: {done_payload}\n\n"
        except CLIENT_DISCONNECT_EXCEPTIONS:
            raise
        logger.info(f"[SSE] Done event sent for chat_id={chat_id}")

    except asyncio.CancelledError:
        # Client disconnected or abort triggered — this is normal cleanup
        logger.info(f"[SSE] Client disconnected for chat_id={chat_id}, stopping stream")
        _abort_events.pop(chat_id, None)
        raise
    except Exception as e:
        logger.error(f"SSE stream error: {e}")
        try:
            yield f"event: error\ndata: {str(e)}\n\n"
        except CLIENT_DISCONNECT_EXCEPTIONS:
            raise
    finally:
        _abort_events.pop(chat_id, None)


@app.post("/api/chat/abort")
async def chat_abort(request: Request):
    """Abort an ongoing chat streaming session by chat_id."""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")
    chat_id = body.get("chat_id")
    if not chat_id:
        raise HTTPException(status_code=400, detail="chat_id is required")
    abort_event = _abort_events.get(chat_id)
    if abort_event is None:
        return {"ok": False, "reason": "No active stream for this chat_id"}
    abort_event.set()
    logger.info(f"Abort signal sent for chat_id={chat_id}")
    return {"ok": True, "chat_id": chat_id}


@app.post("/api/chat/stream")
async def chat_stream(request: Request):
    """Streaming chat with agent via Server-Sent Events."""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    message = body.get("message", "").strip()
    chat_id = body.get("chat_id") or None
    if not chat_id:
        import uuid as _uuid_mod
        chat_id = str(_uuid_mod.uuid4())
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    _restore_session_state(chat_id)
    _ensure_bulk_chat_ready(chat_id)
    _ensure_dataset_chat_ready(chat_id)

    return StreamingResponse(
        _stream_agent_chat(chat_id, message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@app.post("/api/chat")
async def chat(request: Request):
    """Chat with agent."""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    message = body.get("message", "").strip()
    chat_id = body.get("chat_id") or None
    # If frontend sends null/empty, generate a fresh UUID so every new chat is isolated
    if not chat_id:
        import uuid as _uuid_mod
        chat_id = str(_uuid_mod.uuid4())

    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    # Restore the session's durable dataset/bulk manifest before deciding
    # whether this first question needs the selected-gene handoff.
    _restore_session_state(chat_id)
    _ensure_bulk_chat_ready(chat_id)
    _ensure_dataset_chat_ready(chat_id)

    # Bulk statistics stop at the right-panel filters.  Only the first chat
    # question carrying the user's selected genes starts enrichment/network
    # work and the RAG handoff.
    bulk_selected_genes = [
        str(g).strip() for g in (body.get("bulk_selected_genes") or [])
        if str(g).strip()
    ][:2000]
    bulk_state = bulk_sessions.get(chat_id)
    if bulk_state and bulk_state.get("result") and bulk_state.get("rag") is None and bulk_selected_genes:
        try:
            await _await_bulk_question_handoff(chat_id, bulk_selected_genes)
        except Exception as _bulk_handoff_error:
            bulk_state["status"] = "ready_for_filter"
            _push_progress(chat_id, f"[进度] 选定基因的批量知识分析暂时失败，将继续回答：{_bulk_handoff_error}")
            logger.exception("Bulk question handoff failed for %s", chat_id)

    # 若 agent 尚未初始化，尝试用当前配置自动创建；已存在则直接复用（保留记忆）
    if chat_id not in agents:
        config = get_config()
        if not config.llm.api_key:
            raise HTTPException(
                status_code=400,
                detail="请先在设置页面配置 API Key，然后重试。"
            )
        security = get_security_manager()
        decrypted_key = security.decrypt(config.llm.api_key)
        # 只使用当前 session 的数据，绝不跨 session 继承
        adata = datasets.get(chat_id)  # None if not uploaded yet
        try:
            agents[chat_id] = E2seqAgent(
                adata=adata,
                llm_provider=config.llm.provider,
                api_key=decrypted_key,
                model=config.llm.model,
                session_id=chat_id,
                base_url=config.get_provider_base_url(config.llm.provider),
            )
            if adata is not None:
                logger.info(f"Auto-initialized agent with data for session: {chat_id}")
            else:
                logger.info(f"Auto-initialized agent (no data) for session: {chat_id}")
        except Exception as e:
            logger.error(f"Failed to auto-initialize agent: {e}")
            raise HTTPException(status_code=500, detail=f"Agent 初始化失败: {str(e)}")
    else:
        logger.info(f"Reusing existing agent for session: {chat_id} (memory preserved)")

    # P0 FIX: Restore SQLite conversation history into agent's WorkingMemory
    # This fixes the critical断层 where switching to an existing chat left the
    # LLM with empty conversation_history even though the frontend showed messages.
    try:
        _sqlite_msgs = _get_chat_messages(chat_id)
        if _sqlite_msgs:
            agent = agents[chat_id]
            if hasattr(agent, "memory") and hasattr(agent.memory, "restore_session"):
                agent.memory.restore_session(chat_id, _sqlite_msgs)
                logger.info(f"[Memory] Restored {len(_sqlite_msgs)} messages from SQLite for session {chat_id}")
    except Exception as _mem_e:
        logger.warning(f"[Memory] Failed to restore session history: {_mem_e}")

    try:
        agent = agents[chat_id]

        # Apply max_tokens and reasoner_mode from adata.uns if user configured it
        _adata_chat = datasets.get(chat_id)
        if _adata_chat is not None:
            _reasoner = _adata_chat.uns.get("e2sc_reasoner_mode", False)
            if _reasoner and hasattr(agent, "llm") and hasattr(agent.llm, "set_thinking"):
                agent.llm.set_thinking(True, agent.llm.thinking_effort or "high")
                if hasattr(agent.llm, "max_tokens"):
                    agent.llm.max_tokens = 65536
            else:
                _max_tok = _adata_chat.uns.get("e2sc_max_tokens")
                if _max_tok and hasattr(agent, "llm") and hasattr(agent.llm, "max_tokens"):
                    agent.llm.max_tokens = int(_max_tok)

        # Install per-session progress handler so orchestrator logger.info
        # calls are captured and exposed via /api/progress/{chat_id}
        _push_progress(chat_id, f"[进度] 开始处理请求: {message[:60]}")
        _prog_handler = _ProgressHandler(chat_id, bind_current_thread=False)
        _orch_logger = logging.getLogger("e2seq.agent.orchestrator_optimized")
        _orch_logger.addHandler(_prog_handler)

        # Create a progress_callback that pushes messages to the progress buffer
        # This runs in the thread pool alongside agent.chat
        def _progress_callback(msg: str):
            _push_progress(chat_id, msg)

        try:
            # Run blocking agent.chat in a thread pool to avoid blocking the
            # async event loop (agent makes many synchronous HTTP + DB calls)
            loop = asyncio.get_running_loop()
            def _run_agent_chat():
                _prog_handler.bind_to_current_thread()
                return agent.chat(
                    message,
                    progress_callback=_progress_callback,
                    text_queue=None,
                )

            response = await loop.run_in_executor(None, _run_agent_chat)
        finally:
            _orch_logger.removeHandler(_prog_handler)
            _push_progress(chat_id, "[进度] 分析完成")

        if not isinstance(response, dict):
            response = {"text": str(response) if response else "", "plots": [], "data": {}, "thinking": []}
        plots_data = []
        if response.get("plots"):
            for item in response["plots"]:
                if isinstance(item, (list, tuple)) and len(item) == 2:
                    plot_name, fig = item
                else:
                    continue
                try:
                    import plotly
                    fig_json = plotly.io.to_json(fig)
                    plots_data.append({
                        "title": plot_name,
                        "figure": fig_json,
                    })
                except Exception as pe:
                    logger.warning(f"Failed to serialize plot '{plot_name}': {pe}")

        # Persist messages to SQLite
        try:
            _save_chat_message(chat_id, "user", message)
            _save_chat_message(chat_id, "assistant", response.get("text", ""))
        except Exception as pe:
            logger.warning(f"Failed to persist chat message: {pe}")

        response_data = dict(response.get("data") or {})
        bulk_state = bulk_sessions.get(chat_id)
        if bulk_state and bulk_state.get("timing"):
            response_data["bulk_timing"] = dict(bulk_state.get("timing") or {})
        _persist_answer_usage(
            chat_id,
            response_data.get("llm_usage"),
            response_data.get("source_stats"),
            bulk_state,
        )

        return {
            "response": response.get("text", ""),
            "plots": plots_data,
            "chat_id": chat_id,
            "thinking": response.get("thinking", []),
            "data": response_data,
        }
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Invalid response format from agent: {str(e)}")
    except Exception as e:
        logger.error(f"Chat processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


# Provider-to-key mapping and model defaults
PROVIDER_KEY_MAP = {
    "openai": ("openai_key", "gpt-5.4"),
    "anthropic": ("anthropic_key", "claude-opus-4-5"),
    "gemini": ("gemini_key", "gemini-2.5-pro-preview-06-05"),
    "deepseek": ("deepseek_key", "deepseek-reasoner"),
    "siliconflow": ("siliconflow_key", "deepseek-ai/DeepSeek-V3"),
    "glm": ("glm_key", "glm-5.1"),
    "kimi": ("kimi_key", "moonshot-v2.6-250415"),
    "sdu": ("sdu_key", "SDU-AI/DeepSeek-V4-Flash"),
    "custom": ("custom_key", ""),
}


def _normalise_answer_sources(value: Any, allowed: set[str], fallback: list[str]) -> list[str]:
    """Normalise a source list while preserving an intentional empty list."""
    if value is None:
        value = fallback
    if isinstance(value, str):
        value = [part.strip() for part in value.split(",") if part.strip()]
    if not isinstance(value, (list, tuple, set)):
        value = fallback
    return list(dict.fromkeys(str(item).strip() for item in value if str(item).strip() in allowed))


@app.get("/api/answer-settings")
async def get_answer_settings():
    """Return answer-time knowledge-source policy only.

    Dataset prompts are stored with the uploaded dataset/session and are not
    part of this knowledge-base source settings endpoint.
    """
    config = get_config()
    settings = config.answer_settings
    custom_sources = load_custom_sources(include_secrets=False)
    custom_ids = {str(item.get("id")).lower() for item in custom_sources if item.get("id")}
    allowed_apis = _ANSWER_API_IDS | custom_ids
    default_apis = list(DEFAULT_ANSWER_APIS) + [
        source_id for source_id in sorted(custom_ids)
        if next((item for item in custom_sources if item.get("id") == source_id), {}).get("enabled", True)
    ]
    # Older config files predate the newer verified sources.  Until the user
    # explicitly saves a source selection, expose the current defaults rather
    # than silently keeping a stale list from a previous release.
    configured = bool(settings.configured)
    enabled_apis = _normalise_answer_sources(
        settings.enabled_apis if configured else None,
        allowed_apis,
        default_apis,
    )
    enabled_dbs = _normalise_answer_sources(
        settings.enabled_dbs if configured else None,
        _ANSWER_DB_IDS,
        DEFAULT_ANSWER_DBS,
    )
    return {
        "enabled_apis": enabled_apis,
        "enabled_dbs": enabled_dbs,
        "configured": configured,
        "applies_to": "new_answers_sources_only",
        "sources": ANSWER_SOURCE_CATALOG + custom_source_catalog(custom_sources),
        "custom_sources": public_custom_sources(custom_sources),
    }


@app.post("/api/answer-settings")
async def save_answer_settings(settings: Dict[str, Any]):
    """Persist answer-time sources; existing answers and RAG snapshots are untouched."""
    try:
        config = get_config()
        if "custom_sources" in settings:
            custom_sources = save_custom_sources(
                settings.get("custom_sources"),
                reserved_ids=_ANSWER_API_IDS | _ANSWER_DB_IDS,
            )
        else:
            custom_sources = load_custom_sources(include_secrets=True)
        custom_ids = {str(item.get("id")).lower() for item in custom_sources if item.get("id")}
        allowed_apis = _ANSWER_API_IDS | custom_ids
        default_apis = list(DEFAULT_ANSWER_APIS) + [
            source_id for source_id in sorted(custom_ids)
            if next((item for item in custom_sources if item.get("id") == source_id), {}).get("enabled", True)
        ]
        enabled_apis = _normalise_answer_sources(
            settings.get("enabled_apis"), allowed_apis, default_apis
        )
        enabled_dbs = _normalise_answer_sources(
            settings.get("enabled_dbs"), _ANSWER_DB_IDS, DEFAULT_ANSWER_DBS
        )
        config.answer_settings.enabled_apis = enabled_apis
        config.answer_settings.enabled_dbs = enabled_dbs
        config.answer_settings.configured = True
        config.save()
        logger.info(
            "[AnswerSettings] saved for new answers: apis=%s, dbs=%s",
            enabled_apis,
            enabled_dbs,
        )
        return {
            "success": True,
            "enabled_apis": enabled_apis,
            "enabled_dbs": enabled_dbs,
            "configured": True,
            "applies_to": "new_answers_sources_only",
            "sources": ANSWER_SOURCE_CATALOG + custom_source_catalog(custom_sources),
            "custom_sources": public_custom_sources(custom_sources),
        }
    except HTTPException:
        raise
    except (TypeError, ValueError) as e:
        logger.warning(f"Invalid answer source settings: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to save answer settings: {e}")
        raise HTTPException(status_code=500, detail=f"保存回答设置失败: {e}")


@app.get("/api/rag-cost-estimate")
async def get_rag_cost_estimate():
    """Return a transparent time/query estimate for full selected-item Agent RAG.

    Source retrieval itself does not consume answer-model tokens.  The table
    uses exact provider usage for a matching completed cohort when available;
    otherwise it marks a range as an estimate based on completed answers and
    never fabricates missing provider usage.  Completed durable bulk manifests
    provide the time calibration when available; otherwise the conservative
    3--8 seconds per selected item baseline is used.
    """
    config = get_config()
    settings = config.answer_settings
    custom_sources = load_custom_sources(include_secrets=False)
    custom_ids = {
        str(item.get("id")).lower()
        for item in custom_sources
        if item.get("id") and item.get("enabled", True)
    }
    if bool(settings.configured):
        enabled_apis = _normalise_answer_sources(
            settings.enabled_apis,
            _ANSWER_API_IDS | custom_ids,
            list(DEFAULT_ANSWER_APIS) + sorted(custom_ids),
        )
        enabled_dbs = _normalise_answer_sources(
            settings.enabled_dbs,
            _ANSWER_DB_IDS,
            DEFAULT_ANSWER_DBS,
        )
    else:
        enabled_apis = list(DEFAULT_ANSWER_APIS) + sorted(custom_ids)
        enabled_dbs = list(DEFAULT_ANSWER_DBS)
    if load_annotation_catalog() and "custom_gene_annotations" not in enabled_dbs:
        enabled_dbs.append("custom_gene_annotations")

    measurements = []
    for manifest in sorted(
        _DATASET_DIR.glob("*_bulk_state.json"),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )[:20]:
        try:
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            selected = len({
                str(gene).strip()
                for gene in (payload.get("selected_genes") or [])
                if str(gene).strip()
            })
            timing = payload.get("timing") or {}
            elapsed = float(
                timing.get("rag_elapsed_seconds")
                or timing.get("rag_rebuild_seconds")
                or 0
            )
            if selected > 0 and elapsed > 0:
                measurements.append({
                    "selected_items": selected,
                    "rag_seconds": round(elapsed, 3),
                    "seconds_per_item": round(elapsed / selected, 3),
                })
        except (OSError, TypeError, ValueError, json.JSONDecodeError):
            continue

    per_item_values = [float(item["seconds_per_item"]) for item in measurements]
    if per_item_values:
        low_per_item = max(3.0, min(per_item_values))
        high_per_item = max(8.0, max(per_item_values))
        calibration = "completed bulk RAG manifests"
    else:
        low_per_item, high_per_item = 3.0, 8.0
        calibration = "conservative baseline; no completed bulk RAG manifest yet"

    answer_records = []
    for record in _load_answer_usage_records():
        try:
            rag_items = int(record.get("rag_items") or record.get("selected_items") or 0)
            total_tokens = int(record.get("total_tokens") or 0)
        except (TypeError, ValueError):
            continue
        if rag_items > 0 and bool(record.get("token_usage_available")) and total_tokens > 0:
            answer_records.append(record)

    def _token_range(values: list[int]) -> Optional[dict]:
        clean = sorted(max(0, int(value or 0)) for value in values)
        if not clean:
            return None
        middle = len(clean) // 2
        median = clean[middle] if len(clean) % 2 else round((clean[middle - 1] + clean[middle]) / 2)
        return {"low": clean[0], "high": clean[-1], "median": median}

    def _token_estimate(selected: int) -> dict:
        exact = [
            item for item in answer_records
            if int(item.get("rag_items") or item.get("selected_items") or 0) == selected
        ]
        if exact:
            prompt = _token_range([int(item.get("prompt_tokens") or 0) for item in exact])
            completion = _token_range([int(item.get("completion_tokens") or 0) for item in exact])
            total = _token_range([int(item.get("total_tokens") or 0) for item in exact])
            return {
                "status": "measured",
                "sample_count": len(exact),
                "prompt_tokens": prompt,
                "completion_tokens": completion,
                "total_tokens": total,
            }

        if not answer_records:
            return {"status": "not_measured", "sample_count": 0}

        prompt_per_item = [
            int(item.get("prompt_tokens") or 0) / max(1, int(item.get("rag_items") or item.get("selected_items") or 1))
            for item in answer_records
        ]
        completion_values = [int(item.get("completion_tokens") or 0) for item in answer_records]
        prompt_low = round(min(prompt_per_item) * selected)
        prompt_high = round(max(prompt_per_item) * selected)
        completion_range = _token_range(completion_values)
        total_range = {
            "low": prompt_low + int((completion_range or {}).get("low", 0)),
            "high": prompt_high + int((completion_range or {}).get("high", 0)),
            "median": round((prompt_low + prompt_high) / 2) + int((completion_range or {}).get("median", 0)),
        }
        return {
            "status": "estimated_from_completed_answers",
            "sample_count": len(answer_records),
            "prompt_tokens": {"low": prompt_low, "high": prompt_high, "median": round((prompt_low + prompt_high) / 2)},
            "completion_tokens": completion_range,
            "total_tokens": total_range,
        }

    source_count = len(enabled_apis) + len(enabled_dbs)
    literature_sources = sum(
        source in enabled_apis for source in ("pubmed", "europepmc")
    )
    estimates = []
    for selected in (1, 10, 100, 1000):
        source_queries = selected * source_count
        literature_queries = selected * literature_sources
        estimates.append({
            "selected_items": selected,
            "low_seconds": round(selected * low_per_item),
            "high_seconds": round(selected * high_per_item),
            "source_query_units": source_queries,
            "literature_queries": literature_queries,
            "answer_model_tokens": _token_estimate(selected),
        })

    return {
        "online_apis": enabled_apis,
        "local_databases": enabled_dbs,
        "online_api_count": len(enabled_apis),
        "local_database_count": len(enabled_dbs),
        "source_query_units_per_item": source_count,
        "literature_queries_per_item": literature_sources,
        "selected_item_limit": 2000,
        "gene_workers": _BULK_RAG_GENE_WORKERS + 2,
        "cpu_policy": "bounded network workers; no hidden top-gene retrieval cap",
        "calibration": calibration,
        "seconds_per_item": {
            "low": round(low_per_item, 3),
            "high": round(high_per_item, 3),
        },
        "estimates": estimates,
        "answer_token_samples": len(answer_records),
        "last_answer_measurement": answer_records[-1] if answer_records else None,
        "token_note": (
            "Source/API retrieval does not consume answer-model tokens. "
            "Exact rows use completed provider usage; other rows are explicitly "
            "estimated from completed answers. If the provider omits usage, the "
            "value remains unavailable rather than being invented."
        ),
        "last_measured": measurements[0] if measurements else None,
    }


@app.get("/api/settings")
async def get_settings():
    """Get current settings (masked API keys)."""
    config = get_config()
    security = get_security_manager()

    def mask(encrypted: str) -> str:
        """Return masked placeholder if a key is stored."""
        if not encrypted:
            return ""
        try:
            decrypted = security.decrypt(encrypted)
            if decrypted and len(decrypted) > 8:
                return decrypted[:4] + "****" + decrypted[-4:]
            return "****"
        except Exception:
            return ""

    # Current provider/model plus all encrypted provider profiles.
    current_provider = config.llm.provider
    current_model = config.llm.model
    current_base_url = config.llm.base_url or ""
    provider_profiles = {}
    configured_providers = []
    for provider in PROVIDER_KEY_MAP:
        profile = config.get_provider_profile(provider)
        encrypted_key = profile.get("api_key", "")
        if encrypted_key:
            configured_providers.append(provider)
        provider_profiles[provider] = {
            "key": mask(encrypted_key),
            "model": profile.get("model", ""),
            "base_url": profile.get("base_url", ""),
            "configured": bool(encrypted_key),
        }

    # 获取 Embedding 模型列表
    from e2seq.data.vector_store import get_embedding_models as _get_embed_models
    embed_models = _get_embed_models()

    return {
        "provider": current_provider,
        "model": current_model,
        "configured_providers": configured_providers,
        "provider_profiles": provider_profiles,
        **{
            f"{provider}_key": profile["key"]
            for provider, profile in provider_profiles.items()
        },
        **{
            f"{provider}_model": profile["model"]
            for provider, profile in provider_profiles.items()
        },
        "custom_base_url": provider_profiles.get("custom", {}).get("base_url", current_base_url),
        # Thinking / chain-of-thought settings
        "thinking_enabled": bool(getattr(config.llm, "thinking_enabled", False)),
        "thinking_effort": getattr(config.llm, "thinking_effort", "") or "high",
        # Embedding 配置
        "embedding_model": config.embedding.model_name,
        "embedding_models": embed_models,
    }


@app.get("/api/settings/thinking")
async def get_thinking_capabilities(provider: str = "", model: str = ""):
    """Return thinking-mode capability info for the active provider/model.

    Used by the settings UI to decide whether to show the Thinking toggle
    and which effort levels to put in the dropdown. Returns:
      {
        "provider": ...,  "model": ...,
        "supports_thinking": bool,  "always_on": bool, "model_supported": bool,
        "capability_state": "supported|unsupported|unknown|always_on",
        "thinking_parameter": "provider-specific dialect",
        "thinking_enabled": bool,  "thinking_effort": str,
        "effort_levels": [...],
      }
    """
    try:
        from e2seq.llm.provider import provider_supports_thinking
        config = get_config()
        selected_provider = (provider or config.llm.provider).strip().lower()
        selected_model = (model or config.llm.model).strip()
        caps = provider_supports_thinking(selected_provider, selected_model)
        return {
            "provider": selected_provider,
            "model": selected_model,
            **caps,
            "thinking_enabled": bool(config.llm.thinking_enabled),
            "thinking_effort": config.llm.thinking_effort or "high",
        }
    except Exception as e:
        logger.error(f"get_thinking_capabilities failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/settings/thinking")
async def save_thinking(body: Dict[str, Any]):
    """Persist thinking_enabled + thinking_effort and re-init active agents.

    Body: { "enabled": bool, "effort": "high"|"medium"|"low"|... }
    Reuses the encrypted API key from config so we don't ask for it again.
    """
    try:
        raw_enabled = body.get("enabled", False)
        if isinstance(raw_enabled, str):
            requested_enabled = raw_enabled.strip().lower() in {"1", "true", "yes", "on"}
        else:
            requested_enabled = bool(raw_enabled)
        effort = (body.get("effort", "") or "high").strip().lower()

        config = get_config()
        security = get_security_manager()
        from e2seq.llm.provider import thinking_enabled_for_model
        enabled = thinking_enabled_for_model(
            config.llm.provider,
            config.llm.model,
            requested_enabled,
        )

        if not config.llm.api_key:
            raise HTTPException(status_code=400, detail="请先配置 API Key")

        # Persist to config
        config.update_llm(
            provider=config.llm.provider,
            api_key=config.llm.api_key,
            model=config.llm.model,
            thinking_enabled=enabled,
            thinking_effort=effort,
        )

        # Reinitialize all active agents so the new thinking setting takes
        # effect immediately for the next chat request.
        decrypted_key = security.decrypt(config.llm.api_key)
        reinitialized = 0
        for session_id, adata in datasets.items():
            try:
                agents[session_id] = E2seqAgent(
                    adata=adata,
                    llm_provider=config.llm.provider,
                    api_key=decrypted_key,
                    model=config.llm.model,
                )
                reinitialized += 1
            except Exception as e:
                logger.warning(f"Failed to reinitialize agent for {session_id}: {e}")

        logger.info(
            f"[Settings] thinking updated: enabled={enabled}, effort={effort}, "
            f"reinitialized={reinitialized} agents"
        )
        return {
            "success": True,
            "thinking_enabled": enabled,
            "thinking_effort": effort,
            "agents_reinitialized": reinitialized,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"save_thinking failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/settings")
async def save_settings(settings: Dict[str, Any]):
    """Save provider profiles and explicitly activate the selected provider."""
    try:
        logger.info("Saving settings")
        config = get_config()
        security = get_security_manager()
        selected_provider = (settings.get("provider", "") or "").strip().lower()
        if not selected_provider:
            selected_provider = config.llm.provider
        if selected_provider not in PROVIDER_KEY_MAP:
            raise HTTPException(status_code=400, detail="Please select a supported API provider.")

        # Save every newly entered key as an encrypted, reusable provider
        # profile. This does not change the active provider until below.
        for provider, (field, default_model) in PROVIDER_KEY_MAP.items():
            raw_key = (settings.get(field, "") or "").strip()
            if not raw_key:
                continue
            existing_profile = config.get_provider_profile(provider)
            user_model = (settings.get(f"{provider}_model", "") or "").strip()
            profile_model = user_model or existing_profile.get("model") or default_model
            profile_base_url = existing_profile.get("base_url", "")
            if provider == "custom":
                profile_base_url = (settings.get("custom_base_url", "") or "").strip()
            config.set_provider_profile(
                provider,
                security.encrypt(raw_key),
                profile_model,
                base_url=profile_base_url,
            )

        chosen_profile = config.get_provider_profile(selected_provider)
        if not chosen_profile.get("api_key"):
            raise HTTPException(
                status_code=400,
                detail=f"No API key configured for {selected_provider}. Enter and save its key first.",
            )

        _, default_model = PROVIDER_KEY_MAP[selected_provider]
        chosen_model = (
            (settings.get(f"{selected_provider}_model", "") or "").strip()
            or chosen_profile.get("model")
            or default_model
        )
        chosen_base_url = chosen_profile.get("base_url", "") or None
        if selected_provider == "custom":
            chosen_base_url = (
                (settings.get("custom_base_url", "") or "").strip()
                or chosen_profile.get("base_url", "")
                or None
            )
        encrypted_key = chosen_profile["api_key"]
        chosen_raw_key = security.decrypt(encrypted_key)
        raw_thinking = settings.get("thinking_enabled", config.llm.thinking_enabled)
        if isinstance(raw_thinking, str):
            requested_thinking = raw_thinking.strip().lower() in {"1", "true", "yes", "on"}
        else:
            requested_thinking = bool(raw_thinking)
        from e2seq.llm.provider import thinking_enabled_for_model
        thinking_enabled = thinking_enabled_for_model(
            selected_provider,
            chosen_model,
            requested_thinking,
        )
        thinking_effort = (
            str(settings.get("thinking_effort") or config.llm.thinking_effort or "high")
            .strip()
            .lower()
        )
        config.update_llm(
            selected_provider,
            encrypted_key,
            chosen_model,
            base_url=chosen_base_url,
            thinking_enabled=thinking_enabled,
            thinking_effort=thinking_effort,
        )

        # Re-read the canonical base URL we just stored (covers the case
        # where the user cleared the field — update_llm should already have
        # wiped it but we want the value the actual LLM will use).
        from e2seq.utils.config import get_config as _gc_after
        effective_base_url = (
            _gc_after().llm.base_url
            if selected_provider == "custom"
            else _gc_after().get_provider_base_url(selected_provider)
        )

        # Reinitialize agents for all sessions that already have data loaded
        reinitialized = 0
        for session_id, adata in datasets.items():
            try:
                logger.info(f"Reinitializing agent for session: {session_id}")
                agents[session_id] = E2seqAgent(
                    adata=adata,
                    llm_provider=selected_provider,
                    api_key=chosen_raw_key,  # 传明文，agent 内部不再解密
                    model=chosen_model,
                    base_url=effective_base_url,
                )
                reinitialized += 1
            except Exception as e:
                logger.warning(f"Failed to reinitialize agent for session {session_id}: {e}")

        logger.info(f"Settings saved; {reinitialized} agent(s) reinitialized")

        # 保存后自动测试连接
        connection_result = {"success": False, "message": "未测试"}
        try:
            from e2seq.llm.provider import create_llm_provider
            test_llm = create_llm_provider(
                provider=selected_provider,
                api_key=chosen_raw_key,
                model=chosen_model,
                max_tokens=16,
                base_url=effective_base_url,
            )
            connection_result = test_llm.test_connection()
            logger.info(f"保存后连接测试: {connection_result}")
        except Exception as ce:
            connection_result = {"success": False, "message": str(ce)}
            logger.warning(f"保存后连接测试失败: {ce}")

        return {

            "success": True,
            "message": f"Settings saved successfully. Provider: {selected_provider}, model: {chosen_model}.",
            "provider": selected_provider,
            "model": chosen_model,
            "base_url": effective_base_url or "",
            "connection_test": connection_result,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save settings: {str(e)}")


@app.post("/api/settings/switch-model")
async def switch_model(body: Dict[str, Any]):
    """Switch active provider/model without requiring an API key (uses already-configured key).

    Use this when the user:
    - Already has an API key configured
    - Just wants to switch to a different model from the dropdown

    The chat endpoint re-reads config.llm.model each time, so we just update the YAML.
    """
    try:
        provider = (body.get("provider", "") or "").strip().lower()
        model = (body.get("model", "") or "").strip()

        if not provider:
            raise HTTPException(status_code=400, detail="provider is required")
        config = get_config()
        security = get_security_manager()

        # Retrieve the encrypted key and last model for any saved provider.
        profile = config.get_provider_profile(provider)
        if not profile.get("api_key"):
            raise HTTPException(
                status_code=400,
                detail=f"No API key configured for {provider}. Please save the API key first."
            )

        encrypted_key = profile["api_key"]
        decrypted_key = security.decrypt(encrypted_key)
        model = model or profile.get("model") or PROVIDER_KEY_MAP.get(provider, ("", ""))[1]
        if not model:
            raise HTTPException(status_code=400, detail="model is required")
        base_url = profile.get("base_url") or None

        raw_thinking = body.get("thinking_enabled", config.llm.thinking_enabled)
        if isinstance(raw_thinking, str):
            requested_thinking = raw_thinking.strip().lower() in {"1", "true", "yes", "on"}
        else:
            requested_thinking = bool(raw_thinking)
        from e2seq.llm.provider import thinking_enabled_for_model
        thinking_enabled = thinking_enabled_for_model(
            provider,
            model,
            requested_thinking,
        )
        thinking_effort = (
            str(body.get("thinking_effort") or config.llm.thinking_effort or "high")
            .strip()
            .lower()
        )

        # Update config with new provider + model (keep existing encrypted key)
        config.update_llm(
            provider,
            encrypted_key,
            model,
            base_url=base_url,
            thinking_enabled=thinking_enabled,
            thinking_effort=thinking_effort,
        )

        # Reinitialize all active agents with new provider + model
        reinitialized = 0
        for session_id, adata in datasets.items():
            try:
                agents[session_id] = E2seqAgent(
                    adata=adata,
                    llm_provider=provider,
                    api_key=decrypted_key,
                    model=model,
                    base_url=base_url,
                )
                reinitialized += 1
            except Exception as e:
                logger.warning(f"Failed to reinitialize agent for session {session_id}: {e}")

        # Test connection with new model
        connection_result = {"success": False, "message": "未测试"}
        try:
            from e2seq.llm.provider import create_llm_provider
            test_llm = create_llm_provider(
                provider=provider,
                api_key=decrypted_key,
                model=model,
                max_tokens=16,
                base_url=base_url,
            )
            connection_result = test_llm.test_connection()
        except Exception as ce:
            connection_result = {"success": False, "message": str(ce)}

        logger.info(f"Model switched to {provider}/{model}; {reinitialized} agent(s) reinitialized")
        return {
            "success": True,
            "provider": provider,
            "model": model,
            "thinking_enabled": thinking_enabled,
            "thinking_effort": thinking_effort,
            "agents_reinitialized": reinitialized,
            "connection_test": connection_result,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to switch model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/settings/clear")
async def clear_api_key(body: Dict[str, Any]):
    """Clear the API key for a specific provider and disconnect."""
    try:
        provider = (body.get("provider", "") or "").strip().lower()
        if not provider:
            raise HTTPException(status_code=400, detail="provider is required")

        config = get_config()
        security = get_security_manager()

        was_active = config.llm.provider == provider
        config.clear_provider_profile(provider)
        if not was_active:
            return {"success": True, "message": f"Stored profile removed for {provider}."}

        # Activate another configured provider when possible; otherwise fall
        # back to the local Ollama profile.
        fallback_provider = "ollama"
        fallback_key = ""
        fallback_model = "llama3.2"
        fallback_base_url = None
        for candidate in PROVIDER_KEY_MAP:
            profile = config.get_provider_profile(candidate)
            if profile.get("api_key"):
                fallback_provider = candidate
                fallback_key = profile["api_key"]
                fallback_model = profile.get("model") or PROVIDER_KEY_MAP[candidate][1]
                fallback_base_url = profile.get("base_url") or None
                break
        config.update_llm(
            fallback_provider,
            fallback_key,
            fallback_model,
            base_url=fallback_base_url,
        )

        # Clear all active agents (they will be reinitialized with ollama on next chat)
        cleared = 0
        for session_id in list(agents.keys()):
            del agents[session_id]
            cleared += 1

        logger.info(f"API key cleared for {provider}; {cleared} agent(s) disconnected")
        return {
            "success": True,
            "message": f"{provider} profile removed; active provider is now {fallback_provider}.",
            "provider": fallback_provider,
            "model": fallback_model,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to clear API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chats")
async def get_chats():
    """Get all chat history."""
    return _get_all_chats()


@app.get("/api/chats/{chat_id}")
async def get_chat(chat_id: str):
    """Get messages for a specific chat."""
    _restore_session_state(chat_id)
    messages = _get_chat_messages(chat_id)
    if not messages:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"id": chat_id, "messages": messages}


@app.patch("/api/chats/{chat_id}")
async def rename_chat(chat_id: str, request: Request):
    """Rename a chat session title."""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")
    new_title = body.get("title", "").strip()
    if not new_title:
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    if len(new_title) > 200:
        raise HTTPException(status_code=400, detail="Title too long (max 200 characters)")
    updated = _rename_chat(chat_id, new_title)
    if not updated:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"success": True, "title": new_title}


@app.delete("/api/chats/{chat_id}")
async def delete_chat(chat_id: str):
    """Delete a chat and every data/RAG artifact owned by that chat."""
    _delete_chat(chat_id)
    cleared = _purge_session_artifacts(chat_id, mark_deleted=True)
    return {"success": True, "cleared": cleared, "session_id": chat_id}


@app.delete("/api/chats")
async def clear_all_chats_except_latest():
    """Delete all chat sessions except the most recently updated one."""
    if not _CHAT_DB_PATH.exists():
        return {"success": True, "deleted": 0, "kept": None}
    conn = _sqlite3.connect(str(_CHAT_DB_PATH))
    rows = conn.execute(
        "SELECT id FROM chats ORDER BY updated_at DESC"
    ).fetchall()
    conn.close()
    if not rows:
        return {"success": True, "deleted": 0, "kept": None}
    keep_id = rows[0][0]
    to_delete = [r[0] for r in rows[1:]]
    cleared_artifacts = 0
    for cid in to_delete:
        _delete_chat(cid)
        cleared_artifacts += len(_purge_session_artifacts(cid, mark_deleted=True))
    return {
        "success": True,
        "deleted": len(to_delete),
        "kept": keep_id,
        "cleared_artifacts": cleared_artifacts,
    }


@app.get("/api/knowledge-bases")
async def get_knowledge_bases():
    """Get available knowledge bases."""
    # 动态获取实际行数
    try:
        string_db = STRINGDatabase()
        string_count = string_db.count()
        string_db.close()
    except (_sqlite3.Error, IOError, RuntimeError) as e:
        logger.warning(f"STRING database count failed, using default: {e}")
        string_count = "1,858,946"

    try:
        hmdb_db = HMDBDatabase()
        hmdb_count = hmdb_db.count()
        hmdb_db.close()
    except (_sqlite3.Error, IOError, RuntimeError) as e:
        logger.warning(f"HMDB database count failed, using default: {e}")
        hmdb_count = "858,077"

    try:
        trrust_db = TRRUSTDatabase()
        trrust_count = trrust_db.count()
        trrust_db.close()
    except (_sqlite3.Error, IOError, RuntimeError) as e:
        logger.warning(f"TRRUST database count failed, using default: {e}")
        trrust_count = "9,398"

    try:
        gutmgene_db = GUTMGENEDatabase()
        gutmgene_count = gutmgene_db.count()
        gutmgene_db.close()
    except (_sqlite3.Error, IOError, RuntimeError) as e:
        logger.warning(f"GUTMGENE database count failed, using default: {e}")
        gutmgene_count = "1,334"

    return [
        KnowledgeBase(name="STRING", type="built-in", records=str(string_count)),
        KnowledgeBase(name="HMDB", type="built-in", records=str(hmdb_count)),
        KnowledgeBase(name="TRRUST", type="built-in", records=str(trrust_count)),
        KnowledgeBase(name="GUTMGENE", type="built-in", records=str(gutmgene_count)),
    ]


@app.get("/api/knowledge-bases/custom")
async def get_custom_knowledge_bases():
    """Get custom knowledge bases."""
    from pydantic import BaseModel

    custom_dir = _CUSTOM_DATABASE_DIR
    if not custom_dir.exists():
        return []

    knowledge_bases = []
    for file_path in custom_dir.glob("*"):
        if file_path.suffix.lower() in ['.csv', '.tsv', '.txt']:
            # 统计行数
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = sum(1 for line in f if line.strip())
                    records = max(0, lines - 1)  # 减去表头
            except (IOError, OSError) as e:
                logger.warning(f"Failed to read file {file_path}: {e}")
                records = 0

            gene_column = ""
            annotation_columns = []
            rag_ready = False
            try:
                parsed = parse_annotation_text(file_path.read_text(encoding="utf-8"), file_path.name)
                records = int(parsed["record_count"])
                gene_column = parsed["gene_column"]
                annotation_columns = parsed["annotation_columns"]
                rag_ready = True
            except Exception as exc:
                logger.warning("Custom annotation file %s is invalid: %s", file_path.name, exc)
            knowledge_bases.append({
                "name": file_path.stem,
                "id": file_path.name,
                "type": "gene_annotation",
                "records": str(records),
                "file": str(file_path),
                "gene_column": gene_column,
                "annotation_columns": annotation_columns,
                "rag_ready": rag_ready,
            })

    return knowledge_bases


@app.post("/api/knowledge-bases/upload")
async def upload_knowledge_base(file: UploadFile = File(...)):
    """Upload custom knowledge base CSV file with validation."""
    # 验证文件扩展名
    allowed_extensions = ['.csv', '.tsv', '.txt']
    file_ext = '.' + file.filename.split('.')[-1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Please upload CSV or TSV file."
        )

    logger.info(f"Uploading knowledge base: {file.filename}")

    try:
        # 读取文件内容
        content = await file.read()

        # 检查文件大小（50MB限制）
        max_size = 50 * 1024 * 1024
        if len(content) > max_size:
            raise HTTPException(
                status_code=400,
                detail="File size exceeds 50MB limit"
            )

        # 解码内容
        try:
            text_content = content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="File encoding error. Please ensure the file is UTF-8 encoded."
            )

        # Gene-annotation validation: require a gene-like column plus at
        # least one annotation column.  The same parser is used by Agent RAG,
        # so a file accepted here cannot later disappear from retrieval.
        try:
            parsed = parse_annotation_text(text_content, file.filename or "annotation.csv")
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        header_fields = parsed["headers"]
        record_count = int(parsed["record_count"])
        logger.info(
            "Gene annotation validated: %s records, gene column=%s",
            record_count,
            parsed["gene_column"],
        )

        # 保存到自定义数据库目录
        import os
        custom_dir = _CUSTOM_DATABASE_DIR
        custom_dir.mkdir(exist_ok=True)

        # 生成唯一文件名
        import uuid
        safe_name = file.filename.replace(file_ext, '')
        unique_name = f"{safe_name}_{uuid.uuid4().hex[:8]}{file_ext}"
        save_path = custom_dir / unique_name

        # 保存文件
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(text_content)

        logger.info(f"Knowledge base saved to {save_path}")

        return {
            "success": True,
            "message": f"Gene annotation '{file.filename}' uploaded successfully",
            "id": unique_name,
            "records": record_count,
            "fields": header_fields,
            "gene_column": parsed["gene_column"],
            "annotation_columns": parsed["annotation_columns"],
            "rag_ready": True,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload knowledge base: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload: {str(e)}"
        )


@app.delete("/api/knowledge-bases/{kb_id}")
async def delete_knowledge_base(kb_id: str):
    """Delete custom knowledge base."""
    # Only a basename created by the upload endpoint may be deleted. This
    # keeps the route scoped to the custom annotation directory and prevents
    # path traversal through a user-controlled URL segment.
    requested_name = str(kb_id or "").strip()
    safe_name = Path(requested_name).name
    if not requested_name or safe_name != requested_name or safe_name in {".", ".."}:
        raise HTTPException(status_code=400, detail="Invalid knowledge-base identifier")
    if Path(safe_name).suffix.lower() not in {".csv", ".tsv", ".txt"}:
        raise HTTPException(status_code=400, detail="Only uploaded annotation files can be deleted")

    custom_dir = _CUSTOM_DATABASE_DIR.resolve()
    file_path = (custom_dir / safe_name).resolve()
    if file_path.parent != custom_dir:
        raise HTTPException(status_code=400, detail="Invalid knowledge-base path")
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    try:
        file_path.unlink()
    except OSError as exc:
        logger.error("Failed to delete knowledge base %s: %s", safe_name, exc)
        raise HTTPException(status_code=500, detail="Failed to delete knowledge base") from exc
    logger.info("Deleted knowledge base: %s", safe_name)
    return {"success": True, "id": safe_name, "message": f"Knowledge base '{safe_name}' deleted successfully"}






def _model_capabilities(provider: str, models: list[str]) -> dict[str, dict[str, Any]]:
    """Attach local thinking-capability metadata to a scanned model list.

    The provider's ``/models`` endpoint usually returns IDs only.  Capability
    classification therefore stays local and uses the provider/model registry;
    it never sends a paid probe completion just to render the settings page.
    """
    from e2seq.llm.provider import provider_supports_thinking

    capabilities: dict[str, dict[str, Any]] = {}
    for model in models:
        model_id = str(model or "").strip()
        if not model_id:
            continue
        capabilities[model_id] = provider_supports_thinking(provider, model_id)
    return capabilities


@app.post("/api/settings/models")
async def fetch_models(body: Dict[str, Any]):
    """Get available models from provider API. Honors an optional ``base_url``
    in the body so users can query any OpenAI/Anthropic/Gemini-compatible
    proxy (e.g. a6api, OpenRouter) without changing the saved settings.

    Docs:
    - OpenAI:    GET https://api.openai.com/v1/models
    - DeepSeek:  GET https://api.deepseek.com/v1/models
    - Anthropic: GET https://api.anthropic.com/v1/models
    - Gemini:    GET https://generativelanguage.googleapis.com/v1beta/models
    - GLM:       GET https://open.bigmodel.cn/api/paas/v4/models
    - Kimi:      GET https://api.moonshot.cn/v1/models
    - Ollama:    GET http://localhost:11434/api/tags
    """
    import httpx
    from e2seq.llm.provider import _PROVIDERS  # local import keeps top clean

    provider = body.get("provider", "").lower().strip()
    api_key = body.get("api_key", "").strip()
    custom_base_url = (body.get("base_url", "") or "").strip() or None

    if not provider:
        raise HTTPException(status_code=400, detail="provider is required")
    if provider != "ollama" and not api_key:
        raise HTTPException(status_code=400, detail="api_key is required")

    # Per-provider hard-coded defaults — used when no custom base URL was
    # supplied so the user can still fetch the official model list.
    DEFAULT_BASE_URLS = {
        "openai":      "https://api.openai.com/v1",
        "anthropic":   "https://api.anthropic.com",
        "deepseek":    "https://api.deepseek.com/v1",
        "gemini":      "https://generativelanguage.googleapis.com/v1beta/openai",
        "siliconflow": "https://api.siliconflow.cn/v1",
        "glm":         "https://open.bigmodel.cn/api/paas/v4",
        "kimi":        "https://api.moonshot.cn/v1",
        "sdu":         "https://xplt.sdu.edu.cn:4000/v1",
        "ollama":      "http://localhost:11434",
    }
    base_url = custom_base_url or DEFAULT_BASE_URLS.get(provider, "")
    base_url = base_url.rstrip("/")

    def _bearer_path(path: str) -> str:
        return f"{base_url}{path}"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            if provider == "openai":
                # https://platform.openai.com/docs/api-reference/models/list
                resp = await client.get(
                    _bearer_path("/models"),
                    headers={"Authorization": f"Bearer {api_key}"},
                )
                if resp.status_code != 200:
                    raise HTTPException(status_code=400, detail=f"OpenAI API error ({resp.status_code}): {resp.text[:300]}")
                data = resp.json()
                models = sorted(
                    [m["id"] for m in data.get("data", [])
                     if any(m["id"].startswith(p) for p in ("gpt-", "o1", "o3", "o4", "chatgpt"))],
                    reverse=True,
                )

            elif provider == "anthropic":
                # https://docs.anthropic.com/en/api/models-list
                resp = await client.get(
                    _bearer_path("/v1/models"),
                    headers={"x-api-key": api_key, "anthropic-version": "2023-06-01"},
                )
                if resp.status_code != 200:
                    raise HTTPException(status_code=400, detail=f"Anthropic API error ({resp.status_code}): {resp.text[:300]}")
                data = resp.json()
                models = sorted([m["id"] for m in data.get("data", [])], reverse=True)

            elif provider == "deepseek":
                # https://platform.deepseek.com/api-docs/
                resp = await client.get(
                    _bearer_path("/models"),
                    headers={"Authorization": f"Bearer {api_key}"},
                )
                if resp.status_code != 200:
                    raise HTTPException(status_code=400, detail=f"DeepSeek API error ({resp.status_code}): {resp.text[:300]}")
                data = resp.json()
                models = sorted([m["id"] for m in data.get("data", [])], reverse=True)

            elif provider == "gemini":
                # Gemini has two endpoints. Try the OpenAI-compat /v1/models first
                # (this is what proxies usually expose); fall back to the native
                # /v1beta/models?key=... if the proxy returned an empty list.
                url_openai = _bearer_path("/v1/models")
                resp = await client.get(
                    url_openai,
                    headers={"Authorization": f"Bearer {api_key}"},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    raw = data.get("data", []) or data.get("models", [])
                    ids = [(m.get("id") or m.get("name", "")).replace("models/", "") for m in raw]
                    ids = [i for i in ids if i]
                    if ids:
                        models = sorted(set(ids), reverse=True)
                    else:
                        models = []
                else:
                    # Native Gemini API
                    params = {"key": api_key}
                    resp2 = await client.get(
                        "https://generativelanguage.googleapis.com/v1beta/models",
                        params=params,
                    )
                    if resp2.status_code != 200:
                        raise HTTPException(status_code=400, detail=f"Gemini API error ({resp2.status_code}): {resp2.text[:300]}")
                    data = resp2.json()
                    models = sorted(
                        [m["name"].replace("models/", "")
                         for m in data.get("models", [])
                         if "generateContent" in m.get("supportedGenerationMethods", [])],
                        reverse=True,
                    )

            elif provider == "siliconflow":
                # https://docs.siliconflow.cn/cn/api-reference/models/get-model-list
                resp = await client.get(
                    _bearer_path("/models"),
                    headers={"Authorization": f"Bearer {api_key}"},
                )
                if resp.status_code != 200:
                    raise HTTPException(status_code=400, detail=f"SiliconFlow API error ({resp.status_code}): {resp.text[:300]}")
                data = resp.json()
                # Return ALL models (no filtering), sorted by provider priority
                all_models = [m["id"] for m in data.get("data", []) if m.get("id")]
                # Prefer frontier/large models first
                priority = ["DeepSeek", "deepseek", "Qwen", "Llama", "THUDM", "glm", "MiniMax", "Pro/", "internlm"]
                def _sort_key(m):
                    ml = m.lower()
                    for i, p in enumerate(priority):
                        if p.lower() in ml:
                            return (i, m)
                    return (len(priority), m)
                models = sorted(all_models, key=_sort_key)

            elif provider == "ollama":
                # https://github.com/ollama/ollama/blob/main/docs/api.md
                tags_url = custom_base_url or "http://localhost:11434/api/tags"
                try:
                    resp = await client.get(tags_url)
                    if resp.status_code != 200:
                        raise HTTPException(status_code=400, detail="Ollama not running. Run: ollama serve")
                    data = resp.json()
                    models = [m["name"] for m in data.get("models", [])]
                except httpx.ConnectError:
                    raise HTTPException(status_code=400, detail="Ollama not running. Run: ollama serve")

            elif provider == "glm":
                # https://docs.bigmodel.cn — GLM-5.1 / GLM-5 / GLM-4-Plus / GLM-Z1
                resp = await client.get(
                    _bearer_path("/models"),
                    headers={"Authorization": f"Bearer {api_key}"},
                )
                if resp.status_code != 200:
                    raise HTTPException(status_code=400, detail=f"GLM API error ({resp.status_code}): {resp.text[:300]}")
                data = resp.json()
                all_models = [m["id"] for m in data.get("data", []) if m.get("id")]
                # Prioritize flagship models: GLM-5.1 > GLM-5 > GLM-4-Plus > GLM-4 > GLM-Z1
                priority = ["glm-5.1", "glm-5", "glm-4-plus", "glm-4-0520", "glm-4", "glm-z1", "glm-3"]
                def _glm_sort(m):
                    ml = m.lower()
                    for i, p in enumerate(priority):
                        if ml.startswith(p):
                            return (i, m)
                    return (len(priority), m)
                models = sorted(all_models, key=_glm_sort)

            elif provider == "kimi":
                # https://platform.kimi.com/docs/api/overview — moonshot-v2.6 / moonshot-v2.5
                resp = await client.get(
                    _bearer_path("/models"),
                    headers={"Authorization": f"Bearer {api_key}"},
                )
                if resp.status_code != 200:
                    raise HTTPException(status_code=400, detail=f"Kimi API error ({resp.status_code}): {resp.text[:300]}")
                data = resp.json()
                all_models = [m["id"] for m in data.get("data", []) if m.get("id")]
                # Prioritize moonshot-v2.6 > moonshot-v2.5 > moonshot-v1.5
                priority = ["moonshot-v2.6", "moonshot-v2.5", "moonshot-v1.5", "moonshot-v1"]
                def _kimi_sort(m):
                    ml = m.lower()
                    for i, p in enumerate(priority):
                        if ml.startswith(p):
                            return (i, m)
                    return (len(priority), m)
                models = sorted(all_models, key=_kimi_sort)

            elif provider == "sdu":
                # 山东大学 SDU-AI 平台 - default at https://xplt.sdu.edu.cn:4000/v1/models
                resp = await client.get(
                    _bearer_path("/models"),
                    headers={"Authorization": f"Bearer {api_key}"},
                )
                if resp.status_code != 200:
                    raise HTTPException(status_code=400, detail=f"SDU-AI API error ({resp.status_code}): {resp.text[:300]}")
                data = resp.json()
                all_models = [m["id"] for m in data.get("data", []) if m.get("id")]
                # Prioritize flagship: DeepSeek > GLM > others
                priority = ["deepseek", "glm", "qwen", "kimi", "internlm", "minimax"]
                def _sdu_sort(m):
                    ml = m.lower()
                    for i, p in enumerate(priority):
                        if p in ml:
                            return (i, m)
                    return (len(priority), m)
                models = sorted(all_models, key=_sdu_sort)
                # Fallback: if remote /models returns empty, return curated SDU-AI model list
                if not models:
                    models = [
                        "SDU-AI/DeepSeek-V4-Flash",
                        "SDU-AI/GLM-5",
                        "SDU-AI/Qwen3-235B",
                        "SDU-AI/Kimi-K2",
                    ]

            else:
                raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")

        if not models:
            return {"models": [], "warning": "No models found. Check API key permissions."}

        logger.info(f"Fetched {len(models)} models for {provider}")
        return {
            "models": models,
            "default": models[0] if models else "",
            "model_capabilities": _model_capabilities(provider, models),
        }

    except HTTPException:
        raise
    except httpx.ConnectError:
        raise HTTPException(status_code=400, detail=f"Cannot connect to {provider} API. Check network.")
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail=f"Connection to {provider} API timed out.")
    except Exception as e:
        logger.error(f"fetch_models error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch models: {str(e)}")


@app.post("/api/settings/models-custom")
async def fetch_models_custom(body: Dict[str, Any]):
    """Fetch available models from any OpenAI-compatible endpoint.

    Takes ``base_url`` and ``api_key`` from the request body and queries
    ``{base_url}/models`` using Bearer authentication.
    """
    import httpx
    base_url = (body.get("base_url", "") or "").strip().rstrip("/")
    api_key  = (body.get("api_key", "") or "").strip()

    if not base_url:
        raise HTTPException(status_code=400, detail="base_url is required")
    if not api_key:
        raise HTTPException(status_code=400, detail="api_key is required")

    models_url = f"{base_url}/models"
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(
                models_url,
                headers={"Authorization": f"Bearer {api_key}"},
            )
        if resp.status_code == 401:
            raise HTTPException(status_code=401, detail="Invalid API key")
        if resp.status_code == 403:
            raise HTTPException(status_code=403, detail="API key lacks permissions to list models")
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=f"API error ({resp.status_code}): {resp.text[:200]}")
        data = resp.json()
        models = [m["id"] for m in data.get("data", []) if m.get("id")]
        logger.info(f"Custom endpoint {base_url}: found {len(models)} models")
        return {
            "models": models,
            "default": models[0] if models else "",
            "model_capabilities": _model_capabilities("custom", models),
        }
    except HTTPException:
        raise
    except httpx.ConnectError:
        raise HTTPException(status_code=400, detail=f"Cannot connect to {base_url}. Check URL and network.")
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail=f"Connection to {base_url} timed out.")
    except Exception as e:
        logger.error(f"fetch_models_custom error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch models: {str(e)}")


@app.post("/api/settings/test-connection")
async def test_connection(body: Dict[str, Any] = None):
    """Test LLM connection by sending a real lightweight request.

    可接收 body: {provider, api_key, model, base_url} 直接测试指定参数，
    也可不传 body，使用当前已保存的配置测试。
    """
    from e2seq.llm.provider import create_llm_provider
    try:
        config = get_config()
        security = get_security_manager()

        base_url = (body or {}).get("base_url") if body else None
        if base_url is not None:
            base_url = base_url.strip() or None

        if body and body.get("api_key") and body.get("provider"):
            # 直接用传入的参数测试（保存设置时调用）
            provider_name = body["provider"]
            raw_key = body["api_key"]
            model = body.get("model")
            # base_url may be passed in by the form; fall back to the saved one
            if base_url is None:
                base_url = config.get_provider_base_url(provider_name)
        elif config.llm.api_key:
            # 使用已保存的配置
            provider_name = config.llm.provider
            raw_key = security.decrypt(config.llm.api_key)
            model = config.llm.model
            if base_url is None:
                base_url = config.get_provider_base_url(provider_name)
        else:
            raise HTTPException(status_code=400, detail="未配置 API Key，请先在设置页面保存 API Key")

        logger.info(f"测试连接: provider={provider_name}, model={model}, base_url={base_url or '<default>'}")
        llm = create_llm_provider(
            provider=provider_name,
            api_key=raw_key,
            model=model,
            max_tokens=16,  # 最小 token，节省费用
            base_url=base_url,
        )
        result = llm.test_connection()
        if result["success"]:
            logger.info(f"连接测试成功: {result['message']}")
            return {"success": True, "message": result["message"], "model": result["model"]}
        else:
            logger.warning(f"连接测试失败: {result['message']}")
            raise HTTPException(status_code=400, detail=f"连接失败: {result['message']}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"连接测试异常: {e}")
        raise HTTPException(status_code=500, detail=f"连接测试失败: {str(e)}")


# =============================================================================
# Embedding 模型配置 API
# =============================================================================

def _embedding_hf_token_status() -> Dict[str, Any]:
    """Return non-sensitive HF token status for the settings page."""
    from e2seq.data.vector_store import _get_hf_api_token

    token = _get_hf_api_token()
    if not token:
        return {"configured": False, "masked": ""}
    masked = token[:4] + "****" + token[-4:] if len(token) > 8 else "****"
    return {"configured": True, "masked": masked}


@app.get("/api/embedding/models")
async def get_embedding_models():
    """获取可用的 Embedding 模型列表"""
    from e2seq.data.vector_store import get_embedding_models as _get_models
    return {"models": _get_models()}


@app.get("/api/embedding/config")
async def get_embedding_config():
    """获取当前 Embedding 模型配置"""
    config = get_config()
    provider = getattr(config.embedding, "provider", "local") or "local"
    hf_token_status = _embedding_hf_token_status()
    return {
        "model_name": config.embedding.model_name,
        "model_dimension": config.embedding.model_dimension,
        "normalize": config.embedding.normalize,
        "provider": provider,
        "local_only": config.embedding.local_only,
        "model_paths": config.embedding.model_paths,
        "custom_models": config.embedding.custom_models,
        "hf_token_configured": hf_token_status["configured"],
        "hf_token_masked": hf_token_status["masked"],
    }


@app.post("/api/embedding/config")
async def save_embedding_config(request: Request):
    """保存 Embedding 模型配置并清除缓存"""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    model_name = body.get("model_name", "").strip()
    if not model_name:
        raise HTTPException(status_code=400, detail="model_name is required")

    provider = body.get("provider")
    if provider is None:
        # Older clients only sent local_only.  Keep those requests local and
        # avoid interpreting local_only=False as the new online mode.
        provider = "local"
    provider = str(provider).strip().lower()
    if provider not in {"local", "hf_api"}:
        raise HTTPException(status_code=400, detail="provider must be 'local' or 'hf_api'")

    model_dimension = body.get("model_dimension")
    normalize = body.get("normalize")
    model_paths = body.get("model_paths")
    custom_models = body.get("custom_models")
    hf_token_input = body.get("hf_token")
    clear_hf_token = bool(body.get("clear_hf_token", False))

    hf_api_token = None
    if hf_token_input is not None and str(hf_token_input).strip():
        hf_api_token = get_security_manager().encrypt(str(hf_token_input).strip())
    elif clear_hf_token:
        hf_api_token = ""

    config = get_config()
    try:
        from e2seq.data.vector_store import get_embedding_models as _get_models
        available_models = _get_models()
        model_meta = next((item for item in available_models if item.get("id") == model_name), None)
        effective_custom_models = (
            list(custom_models)
            if isinstance(custom_models, list)
            else list(config.embedding.custom_models or [])
        )
        if model_meta is None and provider == "hf_api":
            # Hugging Face model IDs are intentionally open-ended.  Keep an
            # arbitrary ID as a saved remote model so it appears in the next
            # settings-page load without maintaining a curated allow-list.
            model_meta = {
                "id": model_name,
                "name": model_name,
                "dimension": model_dimension if isinstance(model_dimension, int) else "-",
                "size": "未知",
                "description": "用户配置的 Hugging Face 在线模型",
                "path_required": False,
                "remote": True,
            }
            if not any(
                isinstance(item, dict) and (item.get("id") or "").strip() == model_name
                for item in effective_custom_models
            ):
                effective_custom_models.append({
                    "id": model_name,
                    "name": model_name,
                    "dimension": model_dimension if isinstance(model_dimension, int) else None,
                    "size": "未知",
                    "description": "用户配置的 Hugging Face 在线模型",
                    "provider": "hf_api",
                })
        if model_meta is None:
            raise HTTPException(status_code=400, detail="Unknown embedding model.")

        effective_paths = model_paths if isinstance(model_paths, dict) else config.embedding.model_paths
        configured_path = (effective_paths.get(model_name, "") or "").strip()
        if provider == "local" and configured_path and not Path(configured_path).expanduser().exists():
            raise HTTPException(status_code=400, detail="Configured embedding model path does not exist.")
        if provider == "local" and model_meta.get("path_required") and not configured_path:
            raise HTTPException(
                status_code=400,
                detail="This model requires a valid local path while local-only mode is enabled.",
            )
        if model_dimension is None and isinstance(model_meta.get("dimension"), int):
            model_dimension = model_meta["dimension"]

        # 更新配置
        config.update_embedding(
            model_name=model_name,
            model_dimension=model_dimension,
            normalize=normalize,
            local_only=(provider == "local"),
            model_paths=model_paths,
            custom_models=effective_custom_models,
            provider=provider,
            hf_api_token=hf_api_token,
        )

        # 清除向量存储的 session 缓存
        from e2seq.data.vector_store import clear_embedding_cache, _session_stores
        clear_embedding_cache()
        # 清除现有的 VectorStore 实例，强制重新初始化
        _session_stores.clear()

        logger.info(f"Embedding model changed to: {model_name}")

        hf_token_status = _embedding_hf_token_status()
        return {
            "success": True,
            "message": f"Embedding 模型已切换到 {model_name}",
            "model_name": model_name,
            "model_dimension": model_dimension,
            "provider": provider,
            "hf_token_configured": hf_token_status["configured"],
            "hf_token_masked": hf_token_status["masked"],
            "requires_reindex": True,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save embedding config: {e}")
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")


@app.post("/api/embedding/test")
async def test_embedding_model(request: Request):
    """测试 Embedding 模型是否可用"""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    model_name = body.get("model_name", "").strip()
    local_path = (body.get("local_path", "") or "").strip()
    if not model_name:
        raise HTTPException(status_code=400, detail="model_name is required")

    configured = get_config().embedding
    provider = str(
        body.get("provider")
        or getattr(configured, "provider", "local")
        or "local"
    ).strip().lower()
    if provider not in {"local", "hf_api"}:
        raise HTTPException(status_code=400, detail="provider must be 'local' or 'hf_api'")
    normalize = body.get("normalize")
    if normalize is None:
        normalize = bool(getattr(configured, "normalize", True))

    import threading
    import time

    result_container = {"success": False, "message": "", "time_ms": 0, "provider": provider}

    def _test():
        try:
            start = time.time()
            if provider == "hf_api":
                from e2seq.data.vector_store import HuggingFaceAPIEmbeddingFunction

                embed_fn = HuggingFaceAPIEmbeddingFunction(
                    model_name=model_name,
                    normalize=normalize,
                )
                embeddings = embed_fn(["test embedding"])
                dimension = len(embeddings[0])
            else:
                from sentence_transformers import SentenceTransformer

                model_ref = local_path or model_name
                # 先优先走本地缓存，避免已下载模型因联网波动而“打不开”
                try:
                    model = SentenceTransformer(model_ref, local_files_only=True)
                except Exception:
                    model = SentenceTransformer(model_ref)
                embeddings = model.encode(["test embedding"])
                dimension = int(embeddings.shape[1])
            elapsed = (time.time() - start) * 1000
            result_container["success"] = True
            result_container["dimension"] = int(dimension)
            result_container["message"] = f"Embedding model loaded successfully (dimension: {dimension})"
            result_container["time_ms"] = round(elapsed)
            logger.info(f"Embedding model test passed: {model_name} ({elapsed:.0f}ms)")
        except Exception as e:
            result_container["message"] = f"Embedding model failed to load: {str(e)}"
            logger.warning(f"Embedding model test failed: {model_name} - {e}")

    t = threading.Thread(target=_test, daemon=True)
    t.start()
    t.join(timeout=60)  # 最多等待60秒

    if t.is_alive():
        return {
            "success": False,
            "message": "Embedding model loading timed out after 60 seconds.",
            "time_ms": 60000,
            "provider": provider,
        }

    return result_container


@app.post("/api/embedding/download")
async def download_embedding_model(request: Request):
    """Download a Hugging Face embedding model for local use.

    The download is explicit and opt-in.  If the user leaves the path empty,
    the model is stored below the configured database directory so the web UI
    can immediately reuse it in local mode.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    model_name = str(body.get("model_name") or "").strip()
    requested_path = str(body.get("local_path") or "").strip()
    if not model_name:
        raise HTTPException(status_code=400, detail="model_name is required")

    config = get_config()
    if requested_path:
        target_dir = Path(requested_path).expanduser()
    else:
        safe_model_name = "_".join(
            part for part in model_name.replace("\\", "/").split("/") if part
        ) or "embedding-model"
        target_dir = Path(config.database.db_path).expanduser() / "embedding_models" / safe_model_name

    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        from huggingface_hub import snapshot_download
        from e2seq.data.vector_store import _get_hf_api_token

        token = _get_hf_api_token() or None
        snapshot_path = await asyncio.to_thread(
            snapshot_download,
            repo_id=model_name,
            local_dir=str(target_dir),
            token=token,
        )
        resolved_path = str(Path(snapshot_path or target_dir).expanduser().resolve())

        model_paths = dict(config.embedding.model_paths or {})
        model_paths[model_name] = resolved_path
        custom_models = list(config.embedding.custom_models or [])
        updated = False
        for item in custom_models:
            if isinstance(item, dict) and (item.get("id") or "").strip() == model_name:
                item["path"] = resolved_path
                item["provider"] = "local"
                updated = True
                break
        if not updated and not any(
            isinstance(item, dict) and (item.get("id") or "").strip() == model_name
            for item in custom_models
        ):
            custom_models.append({
                "id": model_name,
                "name": model_name,
                "dimension": None,
                "size": "未知",
                "description": "从 Hugging Face 下载的本地模型",
                "provider": "local",
                "path": resolved_path,
            })

        config.update_embedding(
            model_name=model_name,
            model_dimension=config.embedding.model_dimension,
            normalize=config.embedding.normalize,
            local_only=True,
            model_paths=model_paths,
            custom_models=custom_models,
            provider="local",
        )
        from e2seq.data.vector_store import clear_embedding_cache, _session_stores
        clear_embedding_cache()
        _session_stores.clear()
        return {
            "success": True,
            "model_name": model_name,
            "path": resolved_path,
            "provider": "local",
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to download embedding model %s", model_name)
        raise HTTPException(status_code=500, detail=f"Embedding model download failed: {exc}")


@app.get("/api/plots/{plot_type}")
async def get_plot(plot_type: str):
    """Get visualization plot data."""
    try:
        session_id = "default"

        # Check if data is loaded
        if session_id not in datasets:
            # Return empty plot with message instead of error
            return {
                "data": [],
                "layout": {
                    "title": f"{plot_type.upper()} Visualization",
                    "template": "plotly_dark",
                    "paper_bgcolor": "#0a0e1a",
                    "plot_bgcolor": "#131825",
                    "annotations": [{
                        "text": "No data loaded. Please upload a dataset first.",
                        "xref": "paper",
                        "yref": "paper",
                        "x": 0.5,
                        "y": 0.5,
                        "showarrow": False,
                        "font": {"size": 16, "color": "#8ab4f8"}
                    }]
                }
            }

        adata = datasets[session_id]

        # Generate plot based on type
        plot_data = {
            "data": [],
            "layout": {
                "title": f"{plot_type.upper()} Visualization",
                "template": "plotly_dark",
                "paper_bgcolor": "#0a0e1a",
                "plot_bgcolor": "#131825"
            }
        }

        if plot_type == "umap":
            if "X_umap" in adata.obsm:
                plot_data["data"] = [{
                    "type": "scatter",
                    "mode": "markers",
                    "x": adata.obsm["X_umap"][:, 0].tolist(),
                    "y": adata.obsm["X_umap"][:, 1].tolist(),
                    "marker": {"size": 3, "color": "#8ab4f8"}
                }]
                plot_data["layout"]["xaxis"] = {"title": "UMAP 1"}
                plot_data["layout"]["yaxis"] = {"title": "UMAP 2"}

        elif plot_type == "violin":
            plot_data["data"] = [{
                "type": "violin",
                "y": [1, 2, 3, 4, 5],
                "name": "Sample",
                "marker": {"color": "#8ab4f8"}
            }]

        elif plot_type == "heatmap":
            plot_data["data"] = [{
                "type": "heatmap",
                "z": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                "colorscale": "Viridis"
            }]

        elif plot_type == "volcano":
            plot_data["data"] = [{
                "type": "scatter",
                "mode": "markers",
                "x": [-2, -1, 0, 1, 2],
                "y": [1, 2, 3, 2, 1],
                "marker": {"size": 5, "color": "#8ab4f8"}
            }]
            plot_data["layout"]["xaxis"] = {"title": "Log2 Fold Change"}
            plot_data["layout"]["yaxis"] = {"title": "-Log10 P-value"}

        elif plot_type == "bubble":
            plot_data["data"] = [{
                "type": "scatter",
                "mode": "markers",
                "x": [1, 2, 3, 4, 5],
                "y": [1, 2, 3, 4, 5],
                "marker": {"size": [10, 20, 30, 40, 50], "color": "#8ab4f8"}
            }]

        elif plot_type == "network":
            plot_data["data"] = [{
                "type": "scatter",
                "mode": "markers+lines",
                "x": [0, 1, 2, 1],
                "y": [0, 1, 0, -1],
                "marker": {"size": 20, "color": "#8ab4f8"}
            }]

        elif plot_type == "chord":
            plot_data["data"] = [{
                "type": "scatter",
                "mode": "markers",
                "x": [0, 1, 2, 3],
                "y": [0, 1, 0, -1],
                "marker": {"size": 15, "color": "#8ab4f8"}
            }]

        return plot_data
    except Exception as e:
        logger.error(f"Failed to generate plot: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate plot: {str(e)}")


@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    """Clear one session's data plane, including its persisted RAG."""
    cleared = _purge_session_artifacts(session_id, mark_deleted=False)
    return {"success": True, "message": "Session cleared", "cleared": cleared}


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/kb-status")
async def kb_status(session_id: str = "default"):
    """Return knowledge-base build status for a session.

    Returns:
      building: True while the background thread is running
      ready:    True once the vector store has documents
      n_docs:   Number of documents in the vector store
      n_genes:  Number of genes processed (set after build completes)
    """
    try:
        state = _kb_build_state.get(session_id, {})
        building = state.get("building", False)
        from e2seq.data.vector_store import get_vector_store
        store = get_vector_store(session_id)
        n_docs = store.count()
        ready = n_docs > 0 and not building
        return {
            "session_id": session_id,
            "building": building,
            "ready": ready,
            "n_docs": n_docs,
            "n_genes": state.get("n_genes", 0),
        }
    except Exception as e:
        return {"session_id": session_id, "building": False, "ready": False, "n_docs": 0, "n_genes": 0, "error": str(e)}


@app.post("/api/build-knowledge")
async def build_knowledge(request: Request):
    """Trigger offline knowledge-base build for a session.

    Launches the build in a background thread and returns 202 immediately.
    Frontend polls /api/progress and /api/kb-status to track progress.
    """
    try:
        body = await request.json()
    except Exception:
        body = {}
    # Support both JSON body and query param
    session_id = body.get("session_id") or request.query_params.get("session_id") or "default"

    agent = agents.get(session_id)
    if agent is None:
        raise HTTPException(status_code=400, detail="Agent not initialised — please configure dataset first")

    # Mark session as building (clears any previous ready state)
    _kb_build_state[session_id] = {"building": True, "n_docs": 0, "n_genes": 0}
    _push_progress(session_id, "[离线构建] 开始构建知识库...")

    import threading

    def _run_build():
        _prog_handler = _ProgressHandler(session_id)
        _orch_logger = logging.getLogger("e2seq.agent.orchestrator_optimized")
        _orch_logger.addHandler(_prog_handler)
        try:
            result = agent.build_knowledge_base()
            if result["success"]:
                _kb_build_state[session_id] = {
                    "building": False,
                    "n_docs": result.get("n_docs", 0),
                    "n_genes": result.get("n_genes", 0),
                }
                _push_progress(session_id, f"[离线构建] 知识库构建完成: {result['n_genes']} 基因, {result['n_docs']} 向量文档")
                logger.info(f"KB build done for {session_id}: {result['n_genes']} genes, {result['n_docs']} docs")
            else:
                _kb_build_state[session_id] = {"building": False, "n_docs": 0, "n_genes": 0, "error": result.get("error")}
                _push_progress(session_id, f"[离线构建] 构建失败: {result.get('error', 'unknown error')}")
                logger.error(f"KB build failed for {session_id}: {result.get('error')}")
        except Exception as _e:
            _kb_build_state[session_id] = {"building": False, "n_docs": 0, "n_genes": 0, "error": str(_e)}
            _push_progress(session_id, f"[离线构建] 构建异常: {_e}")
            logger.error(f"KB build exception for {session_id}: {_e}")
        finally:
            _orch_logger.removeHandler(_prog_handler)

    t = threading.Thread(target=_run_build, daemon=True)
    t.start()

    return JSONResponse(status_code=202, content={
        "success": True,
        "session_id": session_id,
        "message": "知识库构建已在后台启动，请轮询 /api/kb-status 获取进度",
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "e2seq.api.server:app",
        host=os.environ.get("E2SEQ_HOST", "127.0.0.1"),
        port=int(os.environ.get("E2SEQ_PORT", "8521")),
        reload=False,
    )
