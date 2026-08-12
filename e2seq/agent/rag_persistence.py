"""Durable per-chat RAG knowledge snapshots.

The vector database already persists its collection on disk, but the
source-aware records and source-coverage audit also need a durable snapshot.
Keeping both lets a reopened chat reuse the completed retrieval instead of
calling the external annotation services again.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
import threading
from pathlib import Path
from typing import Any, Dict, Optional


def _safe_session_id(session_id: str) -> str:
    safe = "".join(c for c in str(session_id or "default") if c.isalnum() or c in "-_")
    return safe or "default"


def _storage_root() -> Path:
    project_root = Path(__file__).resolve().parents[2]
    return Path(os.environ.get("E2SEQ_DATA_DIR") or (project_root / ".e2seq" / "user_data")).expanduser().resolve()


def rag_knowledge_path(session_id: str) -> Path:
    """Return the JSON snapshot path for one chat session."""
    return _storage_root() / "datasets" / f"{_safe_session_id(session_id)}_rag_knowledge.json"


def _session_deleted(session_id: str) -> bool:
    """Check the server's deletion tombstone before writing a RAG snapshot."""
    root = _storage_root() / "datasets"
    return (root / f".{_safe_session_id(session_id)}.deleted").is_file()


def _json_safe(value: Any) -> Any:
    """Recursively convert numpy/set-like values into JSON-safe values."""
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, set):
        return sorted((_json_safe(v) for v in value), key=str)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    try:
        return value.item()
    except Exception:
        return str(value)


def _snapshot_payload(knowledge: Dict[str, Any]) -> Dict[str, Any]:
    """Keep the reusable evidence, not the query-specific formatted context."""
    return {
        "genes": _json_safe(knowledge.get("genes", {})),
        "pubmed": _json_safe(knowledge.get("pubmed", [])),
        "europepmc": _json_safe(knowledge.get("europepmc", [])),
        "_selected_gene_count": int(knowledge.get("_selected_gene_count") or 0),
        "_rag_core_gene_count": int(knowledge.get("_rag_core_gene_count") or len(knowledge.get("genes", {}))),
        "_rag_queried_gene_count": int(
            knowledge.get("_rag_queried_gene_count")
            or knowledge.get("_rag_core_gene_count")
            or len(knowledge.get("genes", {}))
        ),
        "_source_stats": _json_safe(knowledge.get("_source_stats", {})),
    }


def save_rag_knowledge(session_id: str, knowledge: Dict[str, Any]) -> Optional[Path]:
    """Atomically persist a source-aware RAG snapshot for a chat."""
    if _session_deleted(session_id):
        return None
    if not isinstance(knowledge, dict) or not knowledge.get("genes"):
        return None
    path = rag_knowledge_path(session_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "knowledge": _snapshot_payload(knowledge),
    }
    # Include the process/thread in the temporary name.  Two uvicorn workers
    # can finish a retrieval for the same chat close together; sharing one
    # fixed ``.tmp`` file makes Windows ``replace`` fail intermittently and
    # leaves the previous snapshot in place.
    temp_path = path.with_name(
        f"{path.name}.{os.getpid()}.{threading.get_ident()}.tmp"
    )
    temp_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    temp_path.replace(path)
    return path


def load_rag_knowledge(session_id: str) -> Optional[Dict[str, Any]]:
    """Load a previously completed RAG snapshot, if one exists."""
    path = rag_knowledge_path(session_id)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        knowledge = payload.get("knowledge") if isinstance(payload, dict) else None
        if not isinstance(knowledge, dict) or not isinstance(knowledge.get("genes"), dict):
            return None
        return knowledge
    except Exception:
        return None
