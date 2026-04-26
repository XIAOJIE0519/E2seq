"""FastAPI backend for E2sc - Modern REST API."""

import os

# Use HuggingFace mirror for China/低网络延迟环境
if not os.environ.get("HF_ENDPOINT"):
    os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
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
import tempfile
import base64
from pathlib import Path
import scanpy as sc
import logging

from e2sc import E2scAgent
from e2sc.utils import get_config, get_security_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="E2seq API - Easy to Chat with Sequencing", version="2.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path(__file__).parent.parent / "web" / "static"
templates_path = Path(__file__).parent.parent / "web" / "templates"

if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Global state (in production, use Redis or database)
agents = {}
datasets = {}
# Per-chat-id abort events — set by /api/chat/abort, checked by _stream_agent_chat
_abort_events: dict[str, asyncio.Event] = {}
# Shared exception raised inside agent thread when user aborts
class AbortChat(Exception):
    """Raised when the user clicks the abort button during agent execution."""
    pass

# Persistent dataset storage directory
_DATASET_DIR = Path(__file__).parent.parent.parent / "_datasets"
_DATASET_DIR.mkdir(exist_ok=True)

def _dataset_path(session_id: str) -> Path:
    """Return the path where a session's h5ad is persisted."""
    # Sanitise session_id for use as filename
    safe = "".join(c for c in session_id if c.isalnum() or c in "-_")
    return _DATASET_DIR / f"{safe}.h5ad"

def _config_path(session_id: str) -> Path:
    """Return the path where a session's uns config is persisted."""
    safe = "".join(c for c in session_id if c.isalnum() or c in "-_")
    return _DATASET_DIR / f"{safe}_config.json"

def _save_dataset(session_id: str, adata) -> None:
    """Persist adata to disk so it survives server restarts."""
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
    """
    import anndata
    for h5 in _DATASET_DIR.glob("*.h5ad"):
        sid = h5.stem
        try:
            # Only log existence; do not load into datasets dict
            logger.info(f"Found persisted dataset for session {sid} (not auto-loaded)")
        except Exception as _e:
            logger.warning(f"Failed to scan {h5}: {_e}")

# Scan persisted datasets at import time (do NOT load into memory)
_reload_datasets()

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
        buf.append(msg)
        if len(buf) > _MAX_PROGRESS:
            del buf[:-_MAX_PROGRESS]


class _ProgressHandler(logging.Handler):
    """Logging handler that mirrors INFO records to the progress buffer."""

    def __init__(self, session_id: str):
        super().__init__(level=logging.INFO)
        self.session_id = session_id

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = record.getMessage()
            if msg.startswith("["):
                _push_progress(self.session_id, msg)
        except Exception:
            pass


import sqlite3 as _sqlite3
import uuid as _uuid
from datetime import datetime as _datetime

def _get_project_root_for_server() -> Path:
    """Get project root directory for server module."""
    current = Path(__file__).resolve().parent  # api/
    current = current.parent  # e2sc/
    current = current.parent  # project root
    return current

# Use project-local .e2sc directory for chat history
_project_root_server = _get_project_root_for_server()
_CHAT_DB_PATH = _project_root_server / ".e2sc" / "chat_history.db"


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
    from e2sc.data.local_db import initialize_databases
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

    from e2sc.agent.code_executor import get_executor

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
        from e2sc.tools.scanpy_tools import ScancpyTools
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
        from e2sc.tools.scanpy_tools import ScancpyTools
        tools = ScancpyTools(datasets[session_id])
        return tools.get_top_genes_by_group(group_col=group_col, n_top_genes=n_top_genes, method=method)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/matrix")
async def get_expression_matrix(session_id: str = "default", n_top_genes: int = 20, method: str = "mean", celltype_col: str = ""):
    """Return top-expressed genes × cell-type matrix from the loaded dataset."""
    if session_id not in datasets:
        raise HTTPException(status_code=400, detail="请先上传 h5ad 数据文件")
    try:
        from e2sc.tools.scanpy_tools import ScancpyTools
        adata = datasets[session_id]
        tools = ScancpyTools(adata)
        # Prefer user-specified column, fall back to adata.uns config, then auto-detect
        col = celltype_col or adata.uns.get("e2sc_celltype_col", None)
        result = tools.get_top_genes_matrix(n_top_genes=n_top_genes, method=method, celltype_col=col or None)
        return result
    except Exception as e:
        logger.error(f"Matrix generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/db/status")
async def db_status():
    """Return status of all local databases."""
    from e2sc.data.local_db import STRINGDatabase, HMDBDatabase, TRRUSTDatabase, GUTMGENEDatabase
    from e2sc.utils import get_config
    config = get_config()
    db_base = Path(config.database.db_path).expanduser()
    result = {}
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
                result[name] = {"status": "ok", "tables": counts, "path": str(db_file)}
            except Exception as e:
                result[name] = {"status": "error", "error": str(e)}
        else:
            result[name] = {"status": "not_initialized", "path": str(db_file)}
    return result




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
    data_mode: Optional[str] = None  # singlecell | table
    cells: Optional[int] = None
    genes: Optional[int] = None


class KnowledgeBase(BaseModel):
    name: str
    type: str
    records: str


# API Endpoints

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Serve favicon."""
    favicon_path = static_path / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(str(favicon_path), media_type="image/x-icon")
    return HTMLResponse(status_code=204)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface."""
    try:
        index_path = templates_path / "index.html"
        if index_path.exists():
            import time as _time
            _ts = int(_time.time())
            content = index_path.read_text(encoding='utf-8')
            # Replace static version strings with a live timestamp so the
            # browser never serves a cached copy of JS/CSS after a redeploy.
            content = content.replace('?v=20260317e', f'?v={_ts}')
            content = content.replace('?v=20260315b', f'?v={_ts}')
            return HTMLResponse(
                content=content,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache"}
            )
        else:
            return HTMLResponse(content="<h1>E2sc Web Interface</h1><p>Template not found. Please check installation.</p>")
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
    config = get_config()
    # Only use session-specific data (no fallback to "default" — that would
    # resurrect stale data after a session switch or clear-data operation).
    adata = datasets.get(session_id)
    has_data = adata is not None

    cells = None
    genes = None
    data_mode = None
    if has_data:
        if adata.uns.get("e2sc_data_mode") == "csv":
            data_mode = "table"
            cells = adata.uns.get("e2sc_display_rows", adata.n_obs)   # 过滤后行数（记录数）
            genes = adata.uns.get("e2sc_display_genes", adata.n_vars)  # 唯一基因/蛋白数
        else:
            data_mode = "singlecell"
            cells = adata.n_obs
            genes = adata.n_vars

    return StatusResponse(
        configured=bool(config.llm.api_key),
        data_loaded=has_data,
        data_mode=data_mode,
        cells=cells,
        genes=genes
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
                agents[session_id] = E2scAgent(
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
        datasets["default"] = adata
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
    celltype_col = body.get("celltype_col", "cell_type")
    group_col = body.get("group_col", "group")
    enabled_apis = body.get("enabled_apis", ["uniprot","mygene","quickgo","ensembl","chembl","pubmed","europepmc","opentargets","clinvar","gtex","humanbase","gwas","biogrid","civic","alliance"])
    enabled_dbs = body.get("enabled_dbs", ["string","hmdb","trrust","gutmgene"])
    n_top_genes = int(body.get("n_top_genes", 50))  # 默认50，可在5-100间调整
    # Validate n_top_genes range
    n_top_genes = max(5, min(100, n_top_genes))
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
    adata.uns["e2sc_celltype_col"] = celltype_col
    adata.uns["e2sc_group_col"] = group_col
    adata.uns["e2sc_enabled_apis"] = enabled_apis
    adata.uns["e2sc_enabled_dbs"] = enabled_dbs
    adata.uns["e2sc_n_top_genes"] = n_top_genes
    adata.uns["e2sc_min_cells"] = min_cells
    # User-supplied free-text description of this dataset (helps LLM avoid misinterpretation)
    dataset_description = body.get("dataset_description", "").strip()
    adata.uns["e2sc_dataset_description"] = dataset_description
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
            agents[session_id] = E2scAgent(
                adata=adata,
                llm_provider=config.llm.provider,
                api_key=decrypted_key,
                model=config.llm.model,
            )
            agents[session_id]._session_id = session_id
            logger.info(f"Agent initialised for session {session_id} (celltype={celltype_col}, group={group_col}, top_genes={n_top_genes}, min_cells={min_cells})")
        except Exception as e:
            logger.error(f"Agent init failed: {e}")
            raise HTTPException(status_code=500, detail=f"Agent 初始化失败: {str(e)}")

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
        "celltype_labels": celltype_labels,
        "group_labels": group_labels,
    }


@app.post("/api/upload-csv")
async def upload_csv(request: Request, file: UploadFile = File(...)):
    """Upload CSV/TSV/XLSX for table analysis and return detected columns."""
    import pandas as pd, io
    form = await request.form()
    session_id = form.get("session_id") or "default"

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
        n_top_genes = int(body.get("n_top_genes", 30))
        dataset_description = (body.get("dataset_description", "") or "").strip()
        # Parse enabled APIs and DBs from JSON body
        enabled_apis = body.get("enabled_apis", ["uniprot","mygene","quickgo","ensembl","chembl","pubmed","europepmc","reactome","gtex","humanbase","gwas","biogrid","civic","alliance","opentargets","clinvar"])
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
        n_top_genes = int(form.get("n_top_genes", "30"))
        dataset_description = (form.get("dataset_description", "") or "").strip()

        # Parse enabled APIs and DBs from JSON strings
        try:
            enabled_apis = json.loads(form.get("enabled_apis", '["uniprot","mygene","quickgo","ensembl","chembl","pubmed","europepmc","reactome","gtex","humanbase","gwas","biogrid","civic","alliance","opentargets","clinvar"]'))
        except Exception:
            enabled_apis = ["uniprot","mygene","quickgo","ensembl","chembl","pubmed","europepmc","reactome","gtex","humanbase","gwas","biogrid","civic","alliance","opentargets","clinvar"]
        try:
            enabled_dbs = json.loads(form.get("enabled_dbs", '["string","hmdb","trrust","gutmgene"]'))
        except Exception:
            enabled_dbs = ["string","hmdb","trrust","gutmgene"]

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

        all_genes = sorted(df[gene_col].astype(str).unique().tolist())
        n_genes = len(all_genes)
        if n_top_genes <= 0:
            n_top_genes = n_genes
        n_filtered = len(df)
        logger.info(f"CSV configured for {session_id}: {n_filtered} rows after filter, {n_genes} unique genes, {len(groups)} groups")

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
        adata.uns["e2sc_dataset_description"] = dataset_description
        adata.uns["e2sc_display_genes"] = n_genes       # 唯一基因数（展示用）
        adata.uns["e2sc_display_rows"] = n_filtered     # 过滤后行数（展示用）
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
        datasets["default"] = adata

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
            from e2sc import E2scAgent
            agents[session_id] = E2scAgent(
                adata=adata,
                llm_provider=config.llm.provider,
                api_key=decrypted_key,
                model=config.llm.model,
            )
            agents[session_id]._session_id = session_id

        return {
            "success": True,
            "session_id": session_id,
            "n_genes": n_genes,
            "n_genes_total": n_genes_total,  # original count before filtering
            "n_rows_filtered": n_filtered,
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

        n_genes = int(df[gene_col].astype(str).nunique())
        return {"n_genes": n_genes, "n_rows_filtered": int(len(df))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/clear-data")
async def clear_data(body: Dict[str, Any]):
    """Clear uploaded dataset and agent for a session, resetting to no-data state.
    
    IMPORTANT: This must clear BOTH in-memory state AND persisted disk files,
    otherwise data reappears on page reload when session_id (UUID) happens to match
    a previously persisted h5ad file.
    """
    session_id = body.get("session_id", "default")
    cleared = []

    # 1. Delete from in-memory dict — both session-specific AND default
    if session_id in datasets:
        del datasets[session_id]
        cleared.append("dataset-session")
    if "default" in datasets:
        del datasets["default"]
        cleared.append("dataset-default")

    # 2. Delete agent from in-memory dict
    if session_id in agents:
        del agents[session_id]
        cleared.append("agent")

    # 3. Delete ALL persisted files for this session (UUID may repeat on page reload)
    import pathlib
    _ds_dir = pathlib.Path(__file__).parent.parent.parent / "_datasets"
    _ds_dir.mkdir(exist_ok=True)
    for _pat in [f"{session_id}.h5ad", f"{session_id}_config.json", f"{session_id}_csv.csv",
                 "default.h5ad", "default_config.json", "default_csv.csv"]:
        _fp = _ds_dir / _pat
        if _fp.exists():
            try:
                _fp.unlink()
                cleared.append(f"file:{_pat}")
            except Exception as _e:
                logger.warning(f"Failed to delete {_fp}: {_e}")

    logger.info(f"Cleared data for session {session_id}: {cleared}")
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
    """Generator that yields SSE events for streaming agent chat.

    Runs the agent in a thread executor and streams progress events via an async
    queue as they are produced, so the frontend sees real-time updates instead of
    waiting for the full response.

    Supports cancellation via _abort_events[chat_id].set().
    """
    import asyncio
    import plotly
    from e2sc.utils import get_config, get_security_manager
    from e2sc import E2scAgent

    # Register abort event for this chat session
    abort_event = asyncio.Event()
    _abort_events[chat_id] = abort_event

    # threading.Event checked inside the agent thread for fast abort
    abort_flag = _threading.Event()

    try:
        # Yield abort check at start
        if abort_event.is_set():
            yield "event: aborted\ndata: {}\n\n"
            return


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
                agent = E2scAgent(
                    adata=adata,
                    llm_provider=config.llm.provider,
                    api_key=decrypted_key,
                    model=config.llm.model,
                )
                agents[chat_id] = agent
            except Exception as e:
                yield f"event: error\ndata: Agent\u521d\u59cb\u5316\u5931\u8d25: {str(e)}\n\n"
                return

        # Install progress handler
        _prog_handler = _ProgressHandler(chat_id)
        _orch_logger = logging.getLogger("e2sc.agent.orchestrator_optimized")
        _orch_logger.addHandler(_prog_handler)

        # Progress queue for real-time streaming (async-safe via call_soon_threadsafe)
        progress_queue = asyncio.Queue()
        # Text chunk queue for streaming LLM response in real-time (thread-safe)
        import queue
        text_queue = queue.Queue()

        # Capture the running loop for thread-safe access from the executor thread
        _running_loop = asyncio.get_running_loop()

        def progress_callback(msg: str):
            """Thread-safe callback: put progress message into the async queue."""
            try:
                _running_loop.call_soon_threadsafe(
                    progress_queue.put_nowait, msg
                )
            except Exception:
                pass

        async def drain_queue():
            """Drain all queued progress messages as SSE events."""
            while not progress_queue.empty():
                try:
                    msg = await asyncio.wait_for(progress_queue.get(), timeout=0.05)
                    _push_progress(chat_id, msg)
                    payload = json.dumps({"step": "progress", "content": msg})
                    yield f"event: thinking\ndata: {payload}\n\n"
                except asyncio.TimeoutError:
                    break

        # Run agent in executor so we can interleave SSE yields with progress
        loop = asyncio.get_event_loop()
        agent_result_holder = {}

        def run_agent():
            try:
                agent_result_holder["result"] = agent.chat(
                    message,
                    progress_callback=progress_callback,
                    text_queue=text_queue,
                    abort_flag=abort_flag,
                )
            except AbortChat as e:
                agent_result_holder["aborted"] = True
                agent_result_holder["abort_reason"] = str(e) if str(e) else "User requested abort"
            except Exception as e:
                agent_result_holder["error"] = e

        # Kick off agent in thread pool
        executor_future = loop.run_in_executor(None, run_agent)

        # Interleave progress streaming with agent execution.
        # Also check abort_event periodically to support cancellation.
        progress_gen = None
        cancelled = False
        try:
            async def stream_progress():
                while not executor_future.done():
                    # Build task list: progress queue + abort event
                    tasks = [asyncio.create_task(progress_queue.get())]
                    done, _ = await asyncio.wait(
                        tasks + [asyncio.create_task(abort_event.wait())],
                        return_when=asyncio.FIRST_COMPLETED,
                    )
                    if abort_event.is_set():
                        # Signal the agent thread to abort and cancel the executor
                        abort_flag.set()
                        nonlocal cancelled
                        cancelled = True
                        executor_future.cancel()
                        logger.info(f"[SSE] Abort triggered for chat_id={chat_id}")
                        return

                    # Check which task completed
                    for d in done:
                        if d == tasks[0]:
                            # Progress message
                            try:
                                msg = d.result()
                                _push_progress(chat_id, msg)
                                payload = json.dumps({"step": "progress", "content": msg})
                                logger.debug(f"[SSE] progress: {msg[:100]}")
                                yield f"event: thinking\ndata: {payload}\n\n"
                            except Exception:
                                pass

                    # Drain LLM text chunks from queue while executor is running
                    _drained = 0
                    while True:
                        try:
                            chunk = text_queue.get_nowait()
                            text_payload = json.dumps({"content": chunk})
                            logger.debug(f"[SSE] text chunk ({len(chunk)} chars)")
                            yield f"event: text\ndata: {text_payload}\n\n"
                            _drained += 1
                        except Exception:
                            break
                    if _drained > 0:
                        logger.info(f"[SSE] Drained {_drained} text chunks from queue")

            progress_gen = stream_progress()
            async for ev in progress_gen:
                yield ev
        finally:
            # Properly await aclose() per Python cpython issue #117536
            if progress_gen is not None:
                try:
                    await progress_gen.aclose()
                except Exception:
                    pass

        # Drain any remaining LLM text chunks AND progress messages from queues
        # (chunks may have been queued right before/during executor completion)
        while True:
            try:
                chunk = text_queue.get_nowait()
                text_payload = json.dumps({"content": chunk})
                yield f"event: text\ndata: {text_payload}\n\n"
            except Exception:
                break
        while not progress_queue.empty():
            try:
                msg = progress_queue.get_nowait()
                _push_progress(chat_id, msg)
                payload = json.dumps({"step": "progress", "content": msg})
                yield f"event: thinking\ndata: {payload}\n\n"
            except asyncio.QueueEmpty:
                break
            except Exception:
                break

        # Wait for agent to complete (or be cancelled after abort)
        try:
            await loop.run_in_executor(None, lambda: executor_future.result())
        except (asyncio.CancelledError, asyncio.InvalidStateError):
            # CancelledError means abort was triggered and executor was cancelled
            _orch_logger.removeHandler(_prog_handler)
            yield f"event: aborted\ndata: {json.dumps({'reason': 'User requested abort'})}\n\n"
            return

        _orch_logger.removeHandler(_prog_handler)

        # Check if agent raised AbortChat internally (caught in run_agent)
        if agent_result_holder.get("aborted"):
            yield f"event: aborted\ndata: {json.dumps({'reason': agent_result_holder.get('abort_reason', 'User requested abort')})}\n\n"
            return

        # Check if abort was requested while we were draining queues
        if abort_event.is_set():
            yield f"event: aborted\ndata: {json.dumps({'reason': 'User requested abort'})}\n\n"
            return

        _push_progress(chat_id, "[进度] 分析完成")

        if "error" in agent_result_holder:
            _stream_err = agent_result_holder["error"]
            _stream_err_msg = str(_stream_err)
            # Ensure assistant error message is persisted even when agent raises
            try:
                _save_chat_message(chat_id, "assistant", f"[Error] {_stream_err_msg}")
            except Exception as _pe:
                logger.warning(f"Failed to persist stream error: {_pe}")
            yield f"event: error\ndata: {_stream_err_msg}\n\n"
            return

        response = agent_result_holder.get("result", {})
        if not isinstance(response, dict):
            response = {"text": str(response) if response else "", "plots": [], "data": {}, "thinking": []}

        # Yield thinking steps accumulated during execution
        for step in response.get("thinking", []):
            content = json.dumps({"step": step.get("step", ""), "content": step.get("content", "")})
            yield f"event: thinking\ndata: {content}\n\n"

        # Yield plot data
        plots_data = []
        if response.get("plots"):
            for item in response["plots"]:
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
            yield f"event: plots\ndata: {json.dumps(plots_data)}\n\n"

        # Yield source_stats
        src_stats = response.get("data", {}).get("source_stats", {})
        if src_stats:
            yield f"event: source_stats\ndata: {json.dumps(src_stats)}\n\n"

        # Persist assistant response after completion
        try:
            _save_chat_message(chat_id, "assistant", response.get("text", ""))
        except Exception as _pe:
            logger.warning(f"Failed to persist chat message: {_pe}")

        # Yield the full response text
        resp_body = {
            "response": response.get("text", ""),
            "plots": plots_data,
            "chat_id": chat_id,
            "data": response.get("data", {}),
        }
        yield f"event: done\ndata: {json.dumps(resp_body)}\n\n"

    except Exception as e:
        logger.error(f"SSE stream error: {e}")
        yield f"event: error\ndata: {str(e)}\n\n"
    finally:
        # Clean up abort event registration
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
            agents[chat_id] = E2scAgent(
                adata=adata,
                llm_provider=config.llm.provider,
                api_key=decrypted_key,
                model=config.llm.model,
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
        # Do NOT auto-inject data — only load data when user explicitly uploads
    try:
        agent = agents[chat_id]

        # Apply max_tokens and reasoner_mode from adata.uns if user configured it
        _adata_chat = datasets.get(chat_id)
        if _adata_chat is not None:
            _reasoner = _adata_chat.uns.get("e2sc_reasoner_mode", False)
            if _reasoner and hasattr(agent, "llm") and hasattr(agent.llm, "reasoner_mode"):
                agent.llm.reasoner_mode = True
                # Reasoner models have no output token limit - remove max_tokens constraint
                if hasattr(agent.llm, "max_tokens"):
                    agent.llm.max_tokens = 65536
            else:
                _max_tok = _adata_chat.uns.get("e2sc_max_tokens")
                if _max_tok and hasattr(agent, "llm") and hasattr(agent.llm, "max_tokens"):
                    agent.llm.max_tokens = int(_max_tok)

        # Install per-session progress handler so orchestrator logger.info
        # calls are captured and exposed via /api/progress/{chat_id}
        _push_progress(chat_id, f"[进度] 开始处理请求: {message[:60]}")
        _prog_handler = _ProgressHandler(chat_id)
        _orch_logger = logging.getLogger("e2sc.agent.orchestrator_optimized")
        _orch_logger.addHandler(_prog_handler)
        try:
            # Run blocking agent.chat in a thread pool to avoid blocking the
            # async event loop (agent makes many synchronous HTTP + DB calls)
            import asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, agent.chat, message)
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

        return {
            "response": response.get("text", ""),
            "plots": plots_data,
            "chat_id": chat_id,
            "thinking": response.get("thinking", []),
            "data": response.get("data", {}),
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

    # 当前模型名称，用于回填到对应 provider 的模型输入框
    current_provider = config.llm.provider
    current_model = config.llm.model

    # 获取 Embedding 模型列表
    from e2sc.data.vector_store import get_embedding_models as _get_embed_models
    embed_models = _get_embed_models()

    return {
        "provider": current_provider,
        "model": current_model,
        "openai_key": mask(config.llm.api_key) if current_provider == "openai" else "",
        "anthropic_key": mask(config.llm.api_key) if current_provider == "anthropic" else "",
        "gemini_key": mask(config.llm.api_key) if current_provider == "gemini" else "",
        "deepseek_key": mask(config.llm.api_key) if current_provider == "deepseek" else "",
        "siliconflow_key": mask(config.llm.api_key) if current_provider == "siliconflow" else "",
        "glm_key": mask(config.llm.api_key) if current_provider == "glm" else "",
        "kimi_key": mask(config.llm.api_key) if current_provider == "kimi" else "",
        "openai_model": current_model if current_provider == "openai" else "",
        "anthropic_model": current_model if current_provider == "anthropic" else "",
        "gemini_model": current_model if current_provider == "gemini" else "",
        "deepseek_model": current_model if current_provider == "deepseek" else "",
        "siliconflow_model": current_model if current_provider == "siliconflow" else "",
        "glm_model": current_model if current_provider == "glm" else "",
        "kimi_model": current_model if current_provider == "kimi" else "",
        # Embedding 配置
        "embedding_model": config.embedding.model_name,
        "embedding_models": embed_models,
    }


@app.post("/api/settings")
async def save_settings(settings: Dict[str, Any]):
    """Save user settings and reinitialize agents if data is loaded."""
    try:
        logger.info("Saving settings")
        config = get_config()
        security = get_security_manager()

        # Determine which provider key was supplied (last one wins if multiple)
        chosen_provider = None
        chosen_raw_key = None
        chosen_model = None

        for provider, (field, default_model) in PROVIDER_KEY_MAP.items():
            raw_key = settings.get(field, "").strip()
            if raw_key:
                chosen_provider = provider
                chosen_raw_key = raw_key
                # 用户如果自定义了模型名称，优先使用；否则用默认模型
                user_model = settings.get(f"{provider}_model", "").strip()
                chosen_model = user_model if user_model else default_model

        if not chosen_provider:
            # No new key supplied — nothing to update
            return {"success": True, "message": "No API keys provided; settings unchanged."}

        # Encrypt and persist
        encrypted_key = security.encrypt(chosen_raw_key)
        config.update_llm(chosen_provider, encrypted_key, chosen_model)

        # Reinitialize agents for all sessions that already have data loaded
        reinitialized = 0
        for session_id, adata in datasets.items():
            try:
                logger.info(f"Reinitializing agent for session: {session_id}")
                agents[session_id] = E2scAgent(
                    adata=adata,
                    llm_provider=chosen_provider,
                    api_key=chosen_raw_key,  # 传明文，agent 内部不再解密
                    model=chosen_model,
                )
                reinitialized += 1
            except Exception as e:
                logger.warning(f"Failed to reinitialize agent for session {session_id}: {e}")

        logger.info(f"Settings saved; {reinitialized} agent(s) reinitialized")

        # 保存后自动测试连接
        connection_result = {"success": False, "message": "未测试"}
        try:
            from e2sc.llm.provider import create_llm_provider
            test_llm = create_llm_provider(
                provider=chosen_provider,
                api_key=chosen_raw_key,
                model=chosen_model,
                max_tokens=16,
            )
            connection_result = test_llm.test_connection()
            logger.info(f"保存后连接测试: {connection_result}")
        except Exception as ce:
            connection_result = {"success": False, "message": str(ce)}
            logger.warning(f"保存后连接测试失败: {ce}")

        return {

            "success": True,
            "message": f"Settings saved successfully. Provider: {chosen_provider}, model: {chosen_model}.",
            "provider": chosen_provider,
            "model": chosen_model,
            "connection_test": connection_result,
        }
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
        key_field = body.get("key_field", "").strip()

        if not provider:
            raise HTTPException(status_code=400, detail="provider is required")
        if not model:
            raise HTTPException(status_code=400, detail="model is required")
        if not key_field:
            raise HTTPException(status_code=400, detail="key_field is required")

        config = get_config()
        security = get_security_manager()

        # Retrieve the already-encrypted key for this provider from config
        if config.llm.provider != provider or not config.llm.api_key:
            raise HTTPException(
                status_code=400,
                detail=f"No API key configured for {provider}. Please save the API key first."
            )

        encrypted_key = config.llm.api_key
        decrypted_key = security.decrypt(encrypted_key)

        # Update config with new provider + model (keep existing encrypted key)
        config.update_llm(provider, encrypted_key, model)

        # Reinitialize all active agents with new provider + model
        reinitialized = 0
        for session_id, adata in datasets.items():
            try:
                agents[session_id] = E2scAgent(
                    adata=adata,
                    llm_provider=provider,
                    api_key=decrypted_key,
                    model=model,
                )
                reinitialized += 1
            except Exception as e:
                logger.warning(f"Failed to reinitialize agent for session {session_id}: {e}")

        # Test connection with new model
        connection_result = {"success": False, "message": "未测试"}
        try:
            from e2sc.llm.provider import create_llm_provider
            test_llm = create_llm_provider(
                provider=provider,
                api_key=decrypted_key,
                model=model,
                max_tokens=16,
            )
            connection_result = test_llm.test_connection()
        except Exception as ce:
            connection_result = {"success": False, "message": str(ce)}

        logger.info(f"Model switched to {provider}/{model}; {reinitialized} agent(s) reinitialized")
        return {
            "success": True,
            "provider": provider,
            "model": model,
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

        # Only clear if this provider is currently active
        if config.llm.provider != provider:
            return {"success": True, "message": f"{provider} is not the active provider; nothing to clear."}

        # Reset to ollama (no key required) as the active provider
        config.update_llm("ollama", "", "llama3.2")

        # Clear all active agents (they will be reinitialized with ollama on next chat)
        cleared = 0
        for session_id in list(agents.keys()):
            del agents[session_id]
            cleared += 1

        logger.info(f"API key cleared for {provider}; {cleared} agent(s) disconnected")
        return {
            "success": True,
            "message": f"{provider} API 已清除并断开，当前切换至 Ollama (本地模型)",
            "provider": "ollama",
            "model": "llama3.2",
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
    """Delete a chat and its messages."""
    _delete_chat(chat_id)
    if chat_id in agents:
        del agents[chat_id]
    if chat_id in datasets:
        del datasets[chat_id]
    return {"success": True}


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
    for cid in to_delete:
        _delete_chat(cid)
        if cid in agents:
            del agents[cid]
        if cid in datasets:
            del datasets[cid]
    return {"success": True, "deleted": len(to_delete), "kept": keep_id}


@app.get("/api/knowledge-bases")
async def get_knowledge_bases():
    """Get available knowledge bases."""
    # 动态获取实际行数
    try:
        string_db = STRINGDatabase()
        string_count = string_db.count()
        string_db.close()
    except (sqlite3.Error, IOError, RuntimeError) as e:
        logger.warning(f"STRING database count failed, using default: {e}")
        string_count = "1,858,946"

    try:
        hmdb_db = HMDBDatabase()
        hmdb_count = hmdb_db.count()
        hmdb_db.close()
    except (sqlite3.Error, IOError, RuntimeError) as e:
        logger.warning(f"HMDB database count failed, using default: {e}")
        hmdb_count = "858,077"

    try:
        trrust_db = TRRUSTDatabase()
        trrust_count = trrust_db.count()
        trrust_db.close()
    except (sqlite3.Error, IOError, RuntimeError) as e:
        logger.warning(f"TRRUST database count failed, using default: {e}")
        trrust_count = "9,398"

    try:
        gutmgene_db = GUTMGENEDatabase()
        gutmgene_count = gutmgene_db.count()
        gutmgene_db.close()
    except (sqlite3.Error, IOError, RuntimeError) as e:
        logger.warning(f"GUTMGENE database count failed, using default: {e}")
        gutmgene_count = "1,334"

    return [
        KnowledgeBase(name="STRING", type="built-in", records=string_count),
        KnowledgeBase(name="HMDB", type="built-in", records=hmdb_count),
        KnowledgeBase(name="TRRUST", type="built-in", records=trrust_count),
        KnowledgeBase(name="GUTMGENE", type="built-in", records=gutmgene_count),
    ]


@app.get("/api/knowledge-bases/custom")
async def get_custom_knowledge_bases():
    """Get custom knowledge bases."""
    from pydantic import BaseModel

    custom_dir = Path("custom_databases")
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

            knowledge_bases.append({
                "name": file_path.stem,
                "id": file_path.name,
                "type": "custom",
                "records": str(records),
                "file": str(file_path)
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
        
        # 解析CSV
        lines = [line.strip() for line in text_content.split('\n') if line.strip()]
        
        if len(lines) < 2:
            raise HTTPException(
                status_code=400,
                detail="File is empty or contains no data rows"
            )
        
        # 验证表头
        header = lines[0].lower()
        required_fields = ['source', 'target']
        
        # 检测分隔符
        if '\t' in header:
            delimiter = '\t'
        else:
            delimiter = ','
        
        header_fields = [field.strip() for field in header.split(delimiter)]
        missing_fields = [field for field in required_fields if field not in header_fields]
        
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required fields: {', '.join(missing_fields)}. Required fields are: source, target"
            )
        
        # 统计记录数
        record_count = len(lines) - 1  # 减去表头
        
        logger.info(f"Knowledge base validated: {record_count} records")

        # 保存到自定义数据库目录
        import os
        custom_dir = Path("custom_databases")
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
            "message": f"Knowledge base '{file.filename}' uploaded successfully",
            "id": unique_name,
            "records": record_count,
            "fields": header_fields
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
    # TODO: Implement custom database deletion
    logger.info(f"Deleting knowledge base: {kb_id}")
    return {"success": True, "message": f"Knowledge base '{kb_id}' deleted successfully"}






@app.post("/api/settings/models")
async def fetch_models(body: Dict[str, Any]):
    """Get available models from provider API.

    Docs:
    - OpenAI:    GET https://api.openai.com/v1/models
    - DeepSeek:  GET https://api.deepseek.com/models
    - Anthropic: GET https://api.anthropic.com/v1/models
    - Gemini:    GET https://generativelanguage.googleapis.com/v1beta/models
    - GLM:       GET https://open.bigmodel.cn/api/paas/v4/models
    - Kimi:      GET https://api.moonshot.cn/v1/models
    - Ollama:    GET http://localhost:11434/api/tags
    """
    import httpx

    provider = body.get("provider", "").lower().strip()
    api_key = body.get("api_key", "").strip()

    if not provider:
        raise HTTPException(status_code=400, detail="provider is required")
    if provider != "ollama" and not api_key:
        raise HTTPException(status_code=400, detail="api_key is required")

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:

            if provider == "openai":
                # https://platform.openai.com/docs/api-reference/models/list
                resp = await client.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"}
                )
                if resp.status_code != 200:
                    raise HTTPException(status_code=400, detail=f"OpenAI API error ({resp.status_code}): {resp.text[:300]}")
                data = resp.json()
                models = sorted(
                    [m["id"] for m in data.get("data", [])
                     if any(m["id"].startswith(p) for p in ("gpt-", "o1", "o3", "o4", "chatgpt"))],
                    reverse=True
                )

            elif provider == "anthropic":
                # https://docs.anthropic.com/en/api/models-list
                resp = await client.get(
                    "https://api.anthropic.com/v1/models",
                    headers={"x-api-key": api_key, "anthropic-version": "2023-06-01"}
                )
                if resp.status_code != 200:
                    raise HTTPException(status_code=400, detail=f"Anthropic API error ({resp.status_code}): {resp.text[:300]}")
                data = resp.json()
                models = sorted([m["id"] for m in data.get("data", [])], reverse=True)

            elif provider == "deepseek":
                # https://platform.deepseek.com/api-docs
                resp = await client.get(
                    "https://api.deepseek.com/models",
                    headers={"Authorization": f"Bearer {api_key}"}
                )
                if resp.status_code != 200:
                    raise HTTPException(status_code=400, detail=f"DeepSeek API error ({resp.status_code}): {resp.text[:300]}")
                data = resp.json()
                models = sorted([m["id"] for m in data.get("data", [])], reverse=True)

            elif provider == "gemini":
                # https://ai.google.dev/api/models#method:-models.list
                resp = await client.get(
                    "https://generativelanguage.googleapis.com/v1beta/models",
                    params={"key": api_key}
                )
                if resp.status_code != 200:
                    raise HTTPException(status_code=400, detail=f"Gemini API error ({resp.status_code}): {resp.text[:300]}")
                data = resp.json()
                models = sorted(
                    [m["name"].replace("models/", "")
                     for m in data.get("models", [])
                     if "generateContent" in m.get("supportedGenerationMethods", [])],
                    reverse=True
                )

            elif provider == "siliconflow":
                # https://docs.siliconflow.cn/cn/api-reference/models/get-model-list
                resp = await client.get(
                    "https://api.siliconflow.cn/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"}
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
                try:
                    resp = await client.get("http://localhost:11434/api/tags")
                    if resp.status_code != 200:
                        raise HTTPException(status_code=400, detail="Ollama not running. Run: ollama serve")
                    data = resp.json()
                    models = [m["name"] for m in data.get("models", [])]
                except httpx.ConnectError:
                    raise HTTPException(status_code=400, detail="Ollama not running. Run: ollama serve")

            elif provider == "glm":
                # https://docs.bigmodel.cn — GLM-5.1 / GLM-5 / GLM-4-Plus / GLM-Z1
                resp = await client.get(
                    "https://open.bigmodel.cn/api/paas/v4/models",
                    headers={"Authorization": f"Bearer {api_key}"}
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
                    "https://api.moonshot.cn/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"}
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

            else:
                raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")

        if not models:
            return {"models": [], "warning": "No models found. Check API key permissions."}

        logger.info(f"Fetched {len(models)} models for {provider}")
        return {"models": models, "default": models[0] if models else ""}

    except HTTPException:
        raise
    except httpx.ConnectError:
        raise HTTPException(status_code=400, detail=f"Cannot connect to {provider} API. Check network.")
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail=f"Connection to {provider} API timed out.")
    except Exception as e:
        logger.error(f"fetch_models error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch models: {str(e)}")

@app.post("/api/settings/test-connection")
async def test_connection(body: Dict[str, Any] = None):
    """Test LLM connection by sending a real lightweight request.
    
    可接收 body: {provider, api_key, model} 直接测试指定参数，
    也可不传 body，使用当前已保存的配置测试。
    """
    from e2sc.llm.provider import create_llm_provider
    try:
        config = get_config()
        security = get_security_manager()

        if body and body.get("api_key") and body.get("provider"):
            # 直接用传入的参数测试（保存设置时调用）
            provider_name = body["provider"]
            raw_key = body["api_key"]
            model = body.get("model")
        elif config.llm.api_key:
            # 使用已保存的配置
            provider_name = config.llm.provider
            raw_key = security.decrypt(config.llm.api_key)
            model = config.llm.model
        else:
            raise HTTPException(status_code=400, detail="未配置 API Key，请先在设置页面保存 API Key")

        logger.info(f"测试连接: provider={provider_name}, model={model}")
        llm = create_llm_provider(
            provider=provider_name,
            api_key=raw_key,
            model=model,
            max_tokens=16,  # 最小 token，节省费用
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

@app.get("/api/embedding/models")
async def get_embedding_models():
    """获取可用的 Embedding 模型列表"""
    from e2sc.data.vector_store import get_embedding_models as _get_models
    return {"models": _get_models()}


@app.get("/api/embedding/config")
async def get_embedding_config():
    """获取当前 Embedding 模型配置"""
    config = get_config()
    return {
        "model_name": config.embedding.model_name,
        "model_dimension": config.embedding.model_dimension,
        "normalize": config.embedding.normalize,
        "local_only": config.embedding.local_only,
        "model_paths": config.embedding.model_paths,
        "custom_models": config.embedding.custom_models,
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

    model_dimension = body.get("model_dimension")
    normalize = body.get("normalize")
    local_only = body.get("local_only")
    model_paths = body.get("model_paths")
    custom_models = body.get("custom_models")

    config = get_config()
    try:
        # 更新配置
        config.update_embedding(
            model_name=model_name,
            model_dimension=model_dimension,
            normalize=normalize,
            local_only=local_only,
            model_paths=model_paths,
            custom_models=custom_models,
        )

        # 清除向量存储的 session 缓存
        from e2sc.data.vector_store import clear_embedding_cache, _session_stores
        clear_embedding_cache()
        # 清除现有的 VectorStore 实例，强制重新初始化
        _session_stores.clear()

        logger.info(f"Embedding model changed to: {model_name}")

        return {
            "success": True,
            "message": f"Embedding 模型已切换到 {model_name}",
            "model_name": model_name,
        }
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

    import threading
    import time

    result_container = {"success": False, "message": "", "time_ms": 0}

    def _test():
        try:
            from sentence_transformers import SentenceTransformer
            start = time.time()
            model_ref = local_path or model_name
            # 先优先走本地缓存，避免已下载模型因联网波动而“打不开”
            try:
                model = SentenceTransformer(model_ref, local_files_only=True)
            except Exception:
                model = SentenceTransformer(model_ref)
            embeddings = model.encode(["test embedding"])
            elapsed = (time.time() - start) * 1000
            result_container["success"] = True
            result_container["message"] = f"模型加载成功，维度: {embeddings.shape[1]}"
            result_container["time_ms"] = round(elapsed)
            logger.info(f"Embedding model test passed: {model_name} ({elapsed:.0f}ms)")
        except Exception as e:
            result_container["message"] = f"模型加载失败: {str(e)}"
            logger.warning(f"Embedding model test failed: {model_name} - {e}")

    t = threading.Thread(target=_test)
    t.start()
    t.join(timeout=60)  # 最多等待60秒

    if t.is_alive():
        return {
            "success": False,
            "message": "模型加载超时（超过60秒），可能网络较慢或模型较大",
            "time_ms": 60000,
        }

    return result_container


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
    """Clear session data."""
    if session_id in agents:
        del agents[session_id]
    if session_id in datasets:
        del datasets[session_id]
    return {"success": True, "message": "Session cleared"}


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
        from e2sc.data.vector_store import get_vector_store
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
        _orch_logger = logging.getLogger("e2sc.agent.orchestrator_optimized")
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
    uvicorn.run("e2sc.api.server:app", host="0.0.0.0", port=8000, reload=False)
