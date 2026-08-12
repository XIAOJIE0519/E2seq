"""Gene-annotation files used as a local Agent RAG source.

The web upload is intentionally narrow: a file must contain one gene-like
column and one or more annotation columns.  Every non-empty row is indexed by
gene symbol/ID and can be retrieved for each selected expression item without
turning the file into an interaction table.
"""

from __future__ import annotations

import csv
import io
import os
import re
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional


_GENE_COLUMN_ALIASES = (
    "gene",
    "gene_symbol",
    "symbol",
    "hgnc_symbol",
    "gene_id",
    "geneid",
    "ensembl_gene_id",
    "feature",
    "feature_id",
    "id",
)
_CACHE_LOCK = threading.RLock()
_CACHE_SIGNATURE: Optional[tuple] = None
_CACHE_CATALOG: List[Dict[str, Any]] = []


def storage_root() -> Path:
    project_root = Path(__file__).resolve().parents[2]
    return Path(
        os.environ.get("E2SEQ_DATA_DIR") or (project_root / ".e2seq" / "user_data")
    ).expanduser().resolve()


def annotation_dir() -> Path:
    path = storage_root() / "uploads" / "knowledge_bases"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _safe_source_id(path: Path) -> str:
    value = re.sub(r"[^a-zA-Z0-9_-]+", "_", path.stem).strip("_").lower()
    return value[:80] or "annotation"


def gene_key(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    text = text.split(".", 1)[0]
    return text.upper()


def _delimiter_for(path: Path, text: str) -> str:
    if path.suffix.lower() in {".tsv", ".txt"}:
        return "\t"
    try:
        return csv.Sniffer().sniff(text[:4096], delimiters=",\t;").delimiter
    except csv.Error:
        return "\t" if "\t" in text.splitlines()[0] else ","


def parse_annotation_text(text: str, filename: str = "annotation.csv") -> Dict[str, Any]:
    """Parse and validate a gene-annotation file without writing it."""
    if not text or not text.strip():
        raise ValueError("The annotation file is empty")
    path = Path(filename)
    delimiter = _delimiter_for(path, text)
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    headers = [str(item or "").strip() for item in (reader.fieldnames or [])]
    if not headers:
        raise ValueError("The annotation file must contain a header row")
    by_lower = {header.lower(): header for header in headers if header}
    gene_column = next((by_lower[name] for name in _GENE_COLUMN_ALIASES if name in by_lower), None)
    if not gene_column:
        raise ValueError(
            "The annotation file must contain a gene column, for example gene, "
            "gene_symbol, symbol, gene_id, or ensembl_gene_id"
        )
    annotation_columns = [header for header in headers if header and header != gene_column]
    if not annotation_columns:
        raise ValueError("The annotation file must contain at least one annotation column")

    rows: List[Dict[str, Any]] = []
    for raw in reader:
        if not raw:
            continue
        gene = str(raw.get(gene_column, "") or "").strip()
        if not gene:
            continue
        row = {
            header: str(raw.get(header, "") or "").strip()
            for header in headers
            if header
        }
        if any(value for key, value in row.items() if key != gene_column):
            rows.append(row)
    if not rows:
        raise ValueError("The annotation file contains no non-empty gene annotation rows")
    return {
        "headers": headers,
        "gene_column": gene_column,
        "annotation_columns": annotation_columns,
        "rows": rows,
        "record_count": len(rows),
        "delimiter": delimiter,
    }


def _file_signature() -> tuple:
    items = []
    for path in sorted(annotation_dir().glob("*")):
        if path.suffix.lower() not in {".csv", ".tsv", ".txt"} or not path.is_file():
            continue
        try:
            stat = path.stat()
            items.append((path.name, stat.st_mtime_ns, stat.st_size))
        except OSError:
            continue
    return tuple(items)


def _load_catalog() -> List[Dict[str, Any]]:
    catalog: List[Dict[str, Any]] = []
    for path in sorted(annotation_dir().glob("*")):
        if path.suffix.lower() not in {".csv", ".tsv", ".txt"} or not path.is_file():
            continue
        try:
            parsed = parse_annotation_text(path.read_text(encoding="utf-8"), path.name)
            index: Dict[str, List[Dict[str, Any]]] = {}
            for row in parsed["rows"]:
                key = gene_key(row.get(parsed["gene_column"]))
                if key:
                    index.setdefault(key, []).append(row)
            catalog.append({
                "id": _safe_source_id(path),
                "name": path.name,
                "path": str(path),
                "gene_column": parsed["gene_column"],
                "headers": parsed["headers"],
                "annotation_columns": parsed["annotation_columns"],
                "record_count": parsed["record_count"],
                "index": index,
            })
        except Exception as exc:
            catalog.append({
                "id": _safe_source_id(path),
                "name": path.name,
                "path": str(path),
                "gene_column": "",
                "headers": [],
                "annotation_columns": [],
                "record_count": 0,
                "error": str(exc),
                "index": {},
            })
    return catalog


def load_annotation_catalog() -> List[Dict[str, Any]]:
    """Return the cached parsed catalog, refreshing after file changes."""
    global _CACHE_SIGNATURE, _CACHE_CATALOG
    signature = _file_signature()
    with _CACHE_LOCK:
        if signature != _CACHE_SIGNATURE:
            _CACHE_CATALOG = _load_catalog()
            _CACHE_SIGNATURE = signature
        return _CACHE_CATALOG


def query_annotations(gene: str, max_results: int = 20) -> List[Dict[str, Any]]:
    """Return annotations for one gene across all uploaded annotation files."""
    key = gene_key(gene)
    if not key:
        return []
    results: List[Dict[str, Any]] = []
    for source in load_annotation_catalog():
        for row in source.get("index", {}).get(key, [])[:max_results]:
            results.append({
                "source": source["name"],
                "gene": row.get(source.get("gene_column", ""), gene),
                "annotation": row,
            })
            if len(results) >= max_results:
                return results
    return results


def public_catalog() -> List[Dict[str, Any]]:
    """Return upload metadata without exposing parsed indexes."""
    return [
        {
            key: value
            for key, value in source.items()
            if key not in {"index", "path"}
        }
        for source in load_annotation_catalog()
    ]
