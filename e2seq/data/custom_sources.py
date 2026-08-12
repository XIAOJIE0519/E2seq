"""Persistence and validation for user-defined answer-time API sources.

Custom sources are deliberately kept outside ``config.yaml``.  The main
configuration file is shared by model/runtime settings, while this file is a
small source registry that can be replaced or audited independently.  Header
values are encrypted with the existing local security manager before they are
written to disk; the browser only receives source metadata, never credentials.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import urlparse

from e2seq.utils import get_config, get_security_manager


_SOURCE_ID_RE = re.compile(r"^[a-z][a-z0-9_-]{1,48}$")
_ENCRYPTED_PREFIX = "e2seq-encrypted:"
_SENSITIVE_HEADER_RE = re.compile(r"(authorization|api[-_]?key|token|secret|password|credential)", re.I)


def custom_sources_path() -> Path:
    """Return the registry path, with an explicit deployment override."""
    configured = os.environ.get("E2SEQ_CUSTOM_SOURCES_PATH", "").strip()
    path = Path(configured) if configured else get_config().config_dir / "answer_sources.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", str(value or "").strip().lower()).strip("-")
    return value or "source"


def _as_bool(value: Any, default: bool = True) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _renderable_text(value: Any, limit: int = 20000) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False)
    return str(value)[:limit]


def _validate_headers(value: Any) -> Dict[str, str]:
    if value in (None, ""):
        return {}
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ValueError("headers must be a JSON object") from exc
    if not isinstance(value, dict):
        raise ValueError("headers must be a JSON object")
    result: Dict[str, str] = {}
    for key, item in value.items():
        key = str(key).strip()
        if not key or len(key) > 120:
            raise ValueError("header names must be non-empty and <= 120 characters")
        result[key] = _renderable_text(item, 2000)
    return result


def validate_custom_source(raw: Dict[str, Any], reserved_ids: Iterable[str] = ()) -> Dict[str, Any]:
    """Validate and normalize one source definition.

    URL and body templates may contain ``{gene}``, ``{gene_raw}``,
    ``{query}``, ``{query_raw}``, ``{context}``, and ``{context_raw}``.
    Without placeholders the adapter adds the configured query parameters.
    """
    if not isinstance(raw, dict):
        raise ValueError("custom source must be an object")

    name = str(raw.get("name") or raw.get("label") or "").strip()
    if not name or len(name) > 100:
        raise ValueError("custom source name is required and must be <= 100 characters")

    source_id = str(raw.get("id") or _slug(name)).strip().lower()
    if not _SOURCE_ID_RE.fullmatch(source_id):
        raise ValueError("custom source id must match [a-z][a-z0-9_-]{1,48}")
    reserved = {str(item).strip().lower() for item in reserved_ids}
    if source_id in reserved:
        raise ValueError(f"custom source id conflicts with a built-in source: {source_id}")

    url = str(raw.get("url_template") or raw.get("url") or "").strip()
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("custom source URL must be an absolute http(s) URL")
    if len(url) > 4000:
        raise ValueError("custom source URL is too long")

    method = str(raw.get("method") or "GET").strip().upper()
    if method not in {"GET", "POST"}:
        raise ValueError("custom source method must be GET or POST")

    records_path = str(raw.get("records_path") or "").strip()
    if len(records_path) > 300:
        raise ValueError("records_path is too long")
    body_template = raw.get("body_template", raw.get("body", ""))
    if isinstance(body_template, str) and len(body_template) > 20000:
        raise ValueError("body_template is too long")
    if isinstance(body_template, (dict, list)):
        body_template = json.loads(json.dumps(body_template, ensure_ascii=False))
    elif body_template not in (None, ""):
        body_template = str(body_template)
    else:
        body_template = ""

    return {
        "id": source_id,
        "name": name,
        "description": str(raw.get("description") or "").strip()[:300],
        "url_template": url,
        "method": method,
        "headers": _validate_headers(raw.get("headers")),
        "body_template": body_template,
        "records_path": records_path,
        "gene_param": str(raw.get("gene_param") or "gene").strip()[:80],
        "query_param": str(raw.get("query_param") or "query").strip()[:80],
        "context_param": str(raw.get("context_param") or "context").strip()[:80],
        "enabled": _as_bool(raw.get("enabled"), True),
        "max_records": max(1, min(int(raw.get("max_records") or 20), 100)),
        "timeout": max(5, min(int(raw.get("timeout") or 20), 60)),
    }


def _encrypt_headers(headers: Dict[str, str]) -> Dict[str, str]:
    security = get_security_manager()
    encrypted: Dict[str, str] = {}
    for key, value in headers.items():
        text = str(value or "")
        if not text:
            encrypted[key] = ""
            continue
        # Encrypt all non-empty values.  This also protects custom headers
        # whose names do not happen to contain a standard secret keyword.
        try:
            encrypted[key] = _ENCRYPTED_PREFIX + security.encrypt(text)
        except Exception:
            # A source must not be silently destroyed if the local key store
            # is temporarily unavailable.  The runtime will report the
            # configuration error instead of claiming biological no-records.
            encrypted[key] = text
    return encrypted


def _decrypt_headers(headers: Any) -> Dict[str, str]:
    if not isinstance(headers, dict):
        return {}
    security = get_security_manager()
    result: Dict[str, str] = {}
    for key, value in headers.items():
        text = str(value or "")
        if text.startswith(_ENCRYPTED_PREFIX):
            try:
                text = security.decrypt(text[len(_ENCRYPTED_PREFIX):])
            except Exception:
                text = ""
        result[str(key)] = text
    return result


def _read_raw() -> List[Dict[str, Any]]:
    path = custom_sources_path()
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError):
        return []
    if isinstance(payload, dict):
        payload = payload.get("sources", [])
    return [item for item in payload if isinstance(item, dict)] if isinstance(payload, list) else []


def load_custom_sources(include_secrets: bool = True) -> List[Dict[str, Any]]:
    """Load validated sources; secrets are only returned to server-side code."""
    result = []
    for raw in _read_raw():
        try:
            item = validate_custom_source(raw)
        except (TypeError, ValueError):
            continue
        item["headers"] = _decrypt_headers(raw.get("headers", {})) if include_secrets else {}
        item["has_headers"] = bool(raw.get("headers"))
        result.append(item)
    return result


def save_custom_sources(items: Any, reserved_ids: Iterable[str] = ()) -> List[Dict[str, Any]]:
    """Validate and atomically save the registry, preserving omitted secrets.

    The browser intentionally receives metadata without header values.  When
    it saves an unchanged source, an absent ``headers`` field therefore means
    “keep the existing encrypted headers”, not “delete authentication”.
    """
    if items is None:
        return load_custom_sources(include_secrets=True)
    if not isinstance(items, list):
        raise ValueError("custom_sources must be a list")

    existing = {item["id"]: item for item in load_custom_sources(include_secrets=True)}
    normalized: List[Dict[str, Any]] = []
    seen = set()
    for raw in items:
        if not isinstance(raw, dict):
            raise ValueError("each custom source must be an object")
        raw_copy = dict(raw)
        source_id = str(raw_copy.get("id") or _slug(raw_copy.get("name"))).strip().lower()
        if "headers" not in raw_copy and source_id in existing:
            raw_copy["headers"] = existing[source_id].get("headers", {})
        if "body_template" not in raw_copy and source_id in existing:
            raw_copy["body_template"] = existing[source_id].get("body_template", "")
        item = validate_custom_source(raw_copy, reserved_ids=reserved_ids)
        if item["id"] in seen:
            raise ValueError(f"duplicate custom source id: {item['id']}")
        seen.add(item["id"])
        item["headers"] = _encrypt_headers(item.get("headers", {}))
        normalized.append(item)

    path = custom_sources_path()
    payload = json.dumps({"version": 1, "sources": normalized}, ensure_ascii=False, indent=2)
    temp_name = ""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=str(path.parent),
            prefix=f".{path.name}.", suffix=".tmp", delete=False,
        ) as handle:
            handle.write(payload)
            temp_name = handle.name
        os.replace(temp_name, path)
    finally:
        if temp_name and os.path.exists(temp_name):
            try:
                os.unlink(temp_name)
            except OSError:
                pass
    return load_custom_sources(include_secrets=True)


def public_custom_sources(items: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """Return safe metadata for the browser and source catalog."""
    items = load_custom_sources(include_secrets=False) if items is None else items
    public = []
    for item in items:
        public.append({
            "id": item.get("id", ""),
            "name": item.get("name", item.get("id", "")),
            "description": item.get("description", ""),
            "url_template": item.get("url_template", ""),
            "method": item.get("method", "GET"),
            "records_path": item.get("records_path", ""),
            "gene_param": item.get("gene_param", "gene"),
            "query_param": item.get("query_param", "query"),
            "context_param": item.get("context_param", "context"),
            "enabled": bool(item.get("enabled", True)),
            "has_headers": bool(item.get("has_headers") or item.get("headers")),
            "has_body_template": bool(item.get("body_template")),
            "max_records": item.get("max_records", 20),
            "timeout": item.get("timeout", 20),
        })
    return public


def custom_source_catalog(items: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """Build the answer-settings catalog entries for custom API sources."""
    return [
        {
            "id": item.get("id", ""),
            "kind": "api",
            "custom": True,
            "name": item.get("name", item.get("id", "")),
            "description": item.get("description", ""),
        }
        for item in (items if items is not None else load_custom_sources(include_secrets=False))
        if item.get("id")
    ]
