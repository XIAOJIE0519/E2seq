"""Helpers for applying a user-supplied expression-item intersection.

The intersection is a selection constraint, not a statistical transformation.
It is therefore applied after an existing ranking/filtering step has produced
its candidate genes, while the original numerical values remain unchanged.
"""

from collections.abc import Mapping
from typing import Any, Iterable


def gene_key(value: Any) -> str:
    """Return a stable, case-insensitive key for an expression-item ID."""
    return str(value or "").strip().casefold()


def normalize_gene_list(value: Any) -> list[str]:
    """Normalize newline-delimited or list-like expression-item IDs.

    Blank lines are ignored and duplicate IDs are removed while preserving the
    first spelling supplied by the user.  Newlines are the documented
    separator; accepting a list of already separated values keeps the helper
    safe for JSON requests and persisted session state.
    """
    if isinstance(value, str):
        values: Iterable[Any] = value.splitlines()
    elif isinstance(value, (list, tuple, set)):
        values = value
    else:
        values = []

    normalized: list[str] = []
    seen: set[str] = set()
    for item in values:
        for line in str(item or "").splitlines():
            name = line.strip()
            key = gene_key(name)
            if not key or key in seen:
                continue
            seen.add(key)
            normalized.append(name)
    return normalized


def apply_gene_intersection(result: Mapping[str, Any], requested: Any) -> dict[str, Any]:
    """Filter an already ranked matrix result by the requested IDs.

    ``result`` is copied and the recognized matrix/list fields are filtered in
    place on that copy.  Ranking, expression values, and the original AnnData
    object are not changed.  This implements the intended semantics:
    existing top-N/filter candidates ∩ user list.
    """
    genes = normalize_gene_list(requested)
    keys = {gene_key(gene) for gene in genes}
    copied = dict(result or {})
    if not keys:
        return copied

    def keep(value: Any) -> bool:
        return gene_key(value) in keys

    matrix = copied.get("matrix")
    if isinstance(matrix, Mapping):
        copied["matrix"] = {
            group: {
                gene: value
                for gene, value in (values.items() if isinstance(values, Mapping) else [])
                if keep(gene)
            }
            for group, values in matrix.items()
        }

    for field in ("top_genes_per_celltype", "top_genes_per_group"):
        groups = copied.get(field)
        if isinstance(groups, Mapping):
            copied[field] = {
                group: [gene for gene in values if keep(gene)]
                for group, values in groups.items()
                if isinstance(values, (list, tuple))
            }

    all_top_genes = copied.get("all_top_genes")
    if isinstance(all_top_genes, (list, tuple)):
        copied["all_top_genes"] = [gene for gene in all_top_genes if keep(gene)]

    matched = []
    for field in ("top_genes_per_celltype", "top_genes_per_group"):
        groups = copied.get(field, {})
        if isinstance(groups, Mapping):
            matched.extend(gene for values in groups.values() for gene in values)
    copied["gene_intersection_requested"] = len(genes)
    copied["gene_intersection_matched"] = len({gene_key(gene) for gene in matched})
    return copied
