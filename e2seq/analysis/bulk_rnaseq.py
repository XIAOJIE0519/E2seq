"""Bulk RNA-seq analysis primitives.

The upload layer deliberately keeps the two source tables untouched.  All
filtering, normalization and modelling happens inside ``BulkRNAAnalyzer.run``
after the user has selected an analysis and the relevant clinical columns.

The project uses native Bioconductor through ``r_backend`` when R and the
required packages are available.  A transparent Python compatibility
implementation remains available as a clearly labelled fallback:
DESeq2-style median-ratio + NB GLM/Wald, edgeR-style filterByExpr + TMM + NB
GLM, and limma-voom-style filterByExpr + TMM + logCPM/WLS/eBayes.
"""

from __future__ import annotations

import json
import math
import multiprocessing as mp
import os
import queue
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from scipy import stats


DEFAULT_MIN_COUNT = 10
DEFAULT_MIN_SAMPLES = 2
DEFAULT_TOP_N = 50


class BulkAnalysisError(ValueError):
    """Raised when the uploaded bulk tables cannot support the requested model."""


def _config_bool(config: Mapping[str, Any], key: str, default: bool = False) -> bool:
    value = config.get(key, default)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def _read_table(path: str | Path, *, low_memory: bool = False) -> pd.DataFrame:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        try:
            return pd.read_excel(path)
        except ImportError as exc:
            raise BulkAnalysisError("读取 Excel 需要安装 openpyxl 或相应引擎；请先另存为 CSV/TSV") from exc
    if suffix in {".tsv", ".txt"}:
        return pd.read_csv(path, sep="\t", low_memory=low_memory)
    return pd.read_csv(path, low_memory=low_memory)


def _clean_identifier(value: Any) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return ""
    return str(value).strip()


def _guess_gene_column(columns: Sequence[str]) -> str:
    for col in columns:
        if str(col).lower().startswith("unnamed") or str(col).strip() == "":
            return str(col)
    for col in columns:
        if any(token in str(col).lower() for token in ("gene", "symbol", "ensembl", "feature")):
            return str(col)
    return str(columns[0]) if columns else ""


def _bulk_column_suggestions(clinical: pd.DataFrame) -> Dict[str, Any]:
    """Infer safe column/value defaults from the uploaded clinical table.

    This is metadata inspection only.  It never changes the uploaded table or
    applies a statistical transform.  The suggestions intentionally prefer
    complete follow-up columns over death-only columns, which is important for
    TCGA-style tables where ``days_to_death`` is missing for living patients.
    """
    columns = [str(column) for column in clinical.columns]

    def values(column: str) -> List[str]:
        series = clinical[column].dropna().map(_clean_identifier)
        return sorted({value for value in series if value})

    def numeric_count(column: str) -> int:
        return int(pd.to_numeric(clinical[column], errors="coerce").notna().sum())

    def pick_numeric(priority: Sequence[str], tokens: Sequence[str]) -> str:
        for column in priority:
            if column in columns and numeric_count(column) > 0:
                return column
        candidates: List[Tuple[int, str]] = []
        for column in columns:
            lowered = column.lower()
            if any(token in lowered for token in tokens):
                count = numeric_count(column)
                if count > 0:
                    candidates.append((count, column))
        return max(candidates, key=lambda item: item[0])[1] if candidates else ""

    def pick_value_column(priority: Sequence[str], tokens: Sequence[str], max_unique: int = 20) -> str:
        for column in priority:
            if column in columns:
                current = values(column)
                if 1 < len(current) <= max_unique:
                    return column
        candidates: List[Tuple[int, int, str]] = []
        for column in columns:
            current = values(column)
            lowered = column.lower()
            if 1 < len(current) <= max_unique and any(token in lowered for token in tokens):
                candidates.append((sum(token in lowered for token in tokens), -len(current), column))
        return max(candidates)[2] if candidates else ""

    survival_time = pick_numeric(
        (
            "days_to_last_follow_up",
            "days_to_last_followup",
            "follow_up_days",
            "followup_days",
            "overall_survival",
            "os_time",
            "survival_time",
            "time",
            "days_to_death",
            "death_time",
        ),
        ("follow", "survival", "overall", "os", "time", "days", "death"),
    )
    event_column = pick_value_column(
        ("vital_status", "event", "event_status", "status", "paper_vital_status"),
        ("vital", "event", "status", "death", "outcome"),
    )
    group_column = pick_value_column(
        ("tissue_type", "sample_type", "definition", "shortLetterCode", "group", "condition", "subtype"),
        ("tissue", "sample", "group", "condition", "disease", "phenotype", "subtype", "class"),
    )

    event_values = values(event_column) if event_column else []
    event_positive = next(
        (
            value
            for value in event_values
            if value.casefold() in {"dead", "deceased", "death", "died", "1", "yes", "true", "event", "progressed", "relapsed"}
        ),
        "",
    )
    if not event_positive and "1" in event_values:
        event_positive = "1"

    group_values = values(group_column) if group_column else []
    control_level = next(
        (value for value in group_values if re.search(r"normal|control|healthy|untreated|non[-_ ]?tumou?r", value, re.I)),
        group_values[0] if group_values else "",
    )
    case_level = next(
        (
            value
            for value in group_values
            if value != control_level and re.search(r"tumou?r|case|disease|treated|primary|cancer", value, re.I)
        ),
        next((value for value in group_values if value != control_level), ""),
    )

    date_columns = [
        column
        for column in columns
        if re.search(r"date|_dt$|^dt$", column, re.I)
        and pd.to_datetime(clinical[column], errors="coerce").notna().sum() > 0
    ]
    start_date = next(
        (column for column in date_columns if re.search(r"diagnos|baseline|enroll|start|initial|birth", column, re.I)),
        date_columns[0] if date_columns else "",
    )
    end_date = next(
        (
            column
            for column in date_columns
            if column != start_date and re.search(r"death|last|follow|end|date", column, re.I)
        ),
        next((column for column in date_columns if column != start_date), ""),
    )
    return {
        "survival_time_column_guess": survival_time,
        "event_column_guess": event_column,
        "event_positive_guess": event_positive,
        "event_values_guess": event_values[:20],
        "differential_group_column_guess": group_column,
        "differential_control_level_guess": control_level,
        "differential_case_level_guess": case_level,
        "start_date_column_guess": start_date,
        "end_date_column_guess": end_date,
    }


def _counts_frame(path: str | Path, gene_col: Optional[str] = None) -> Tuple[pd.DataFrame, str]:
    """Read a wide count matrix as genes x samples without transforming values."""
    df = _read_table(path, low_memory=False)
    if df.empty or df.shape[1] < 2:
        raise BulkAnalysisError("表达 count 文件至少需要一列基因标识和两列样本")
    col = gene_col or _guess_gene_column([str(c) for c in df.columns])
    if col not in df.columns:
        raise BulkAnalysisError(f"基因标识列 '{col}' 不存在，可选列：{list(df.columns)}")
    ids = df[col].map(_clean_identifier)
    if ids.eq("").any():
        raise BulkAnalysisError("基因标识列包含空值，请先清理后再上传")
    values = df.drop(columns=[col]).copy()
    # Do not coerce or normalize during upload.  Numeric conversion is only
    # performed on the analysis-time copy in _validate_raw_counts.
    values.index = pd.Index(ids, name=col)
    values.columns = [str(c).strip() for c in values.columns]
    if len(set(values.columns)) != len(values.columns):
        raise BulkAnalysisError("count 文件存在重复样本列名，请保证每个样本列唯一")
    return values, col


def inspect_bulk_files(counts_path: str | Path, clinical_path: str | Path) -> Dict[str, Any]:
    """Return upload-preview metadata; this function performs no analysis."""
    counts, gene_col = _counts_frame(counts_path)
    clinical = _read_table(clinical_path, low_memory=False)
    if clinical.empty:
        raise BulkAnalysisError("临床变量文件为空")
    clinical_cols = [str(c) for c in clinical.columns]
    counts_samples = [str(c) for c in counts.columns]
    sample_col_guess = next(
        (c for c in clinical_cols if any(k in c.lower() for k in ("barcode", "sample", "aliquot"))),
        clinical_cols[0],
    )
    overlap = set(counts_samples) & set(clinical[sample_col_guess].map(_clean_identifier))
    column_values = {}
    for col in clinical_cols:
        series = clinical[col].dropna().map(_clean_identifier)
        if 0 < series.nunique() <= 20:
            column_values[col] = sorted(series.unique().tolist())[:20]
    suggestions = _bulk_column_suggestions(clinical)
    return {
        "counts": {
            "gene_column": gene_col,
            "n_genes": int(counts.shape[0]),
            "n_samples": int(counts.shape[1]),
            "sample_ids": counts_samples[:20],
            "sample_id_count": len(counts_samples),
            "columns": [gene_col] + counts_samples[:50],
        },
        "clinical": {
            "n_rows": int(len(clinical)),
            "columns": clinical_cols,
            "sample_column_guess": sample_col_guess,
            "sample_id_count": int(clinical[sample_col_guess].map(_clean_identifier).nunique()),
            "values": column_values,
            **suggestions,
        },
        "matched_samples": int(len(overlap)),
        "unmatched_counts": int(len(set(counts_samples) - overlap)),
        "unmatched_clinical": int(len(set(clinical[sample_col_guess].map(_clean_identifier)) - overlap)),
    }


def validate_bulk_configuration(
    counts: pd.DataFrame,
    clinical: pd.DataFrame,
    config: Mapping[str, Any],
) -> Dict[str, Any]:
    """Validate selected columns and values before a model worker is queued."""
    sample_col = str(config.get("sample_col") or "")
    if sample_col not in clinical.columns:
        raise BulkAnalysisError(f"临床样本 ID 列 '{sample_col}' 不存在")
    sample_ids = clinical[sample_col].map(_clean_identifier)
    indexed = clinical.copy()
    indexed.index = pd.Index(sample_ids, name=sample_col)
    indexed = indexed[~indexed.index.duplicated(keep="first")]
    overlap = [str(sample) for sample in counts.columns if str(sample) in indexed.index]
    if len(overlap) < 3:
        raise BulkAnalysisError(f"count 与临床文件只匹配到 {len(overlap)} 个样本；请检查样本 ID 列是否选择正确")
    aligned = indexed.loc[overlap].copy()
    analysis_type = str(config.get("analysis_type") or "").lower()
    if analysis_type == "differential":
        group_col = str(config.get("group_col") or "")
        control = _clean_identifier(config.get("control_level"))
        case = _clean_identifier(config.get("case_level"))
        if group_col not in aligned.columns:
            raise BulkAnalysisError(f"差异分析分组列 '{group_col}' 不存在")
        if not control or not case or control == case:
            raise BulkAnalysisError("差异分析必须选择两个不同的分组值（什么 vs 什么）")
        group_values = aligned[group_col].map(_clean_identifier)
        control_n = int((group_values == control).sum())
        case_n = int((group_values == case).sum())
        if control_n < 2 or case_n < 2:
            raise BulkAnalysisError(
                f"差异分析分组样本不足：{control}={control_n}，{case}={case_n}；请检查分组列和对照/实验组是否选错"
            )
        return {"matched_samples": len(overlap), "control_samples": control_n, "case_samples": case_n}
    if analysis_type != "survival":
        raise BulkAnalysisError("请选择差异分析或预后分析")

    time_type = str(config.get("time_type") or "duration").lower().replace("-", "_")
    event_col = str(config.get("event_col") or "")
    if event_col not in aligned.columns:
        raise BulkAnalysisError(f"事件/删失列 '{event_col}' 不存在")
    if time_type in {"date", "date_ymd", "ymd", "calendar_date"}:
        start_col = str(config.get("start_date_col") or "")
        end_col = str(config.get("end_date_col") or "")
        if start_col not in aligned.columns or end_col not in aligned.columns:
            raise BulkAnalysisError("日期型预后分析必须选择起始日期和结束/末次随访日期列")
        start = pd.to_datetime(aligned[start_col], errors="coerce")
        end = pd.to_datetime(aligned[end_col], errors="coerce")
        times = (end - start).dt.total_seconds() / (24 * 60 * 60)
    else:
        time_type = "duration"
        time_col = str(config.get("time_col") or "")
        if time_col not in aligned.columns:
            raise BulkAnalysisError(f"随访时长列 '{time_col}' 不存在")
        times = pd.to_numeric(aligned[time_col], errors="coerce")
    positive = _clean_identifier(config.get("event_positive"))
    if not positive:
        positive = _bulk_column_suggestions(clinical).get("event_positive_guess") or ""
        if isinstance(config, dict):
            config["event_positive"] = positive
    if not positive:
        raise BulkAnalysisError("请填写事件列中代表事件发生的值，例如 Dead、1 或 Yes")
    event_values = aligned[event_col].map(_clean_identifier)
    events = event_values.str.casefold() == positive.casefold()
    keep = times.notna() & times.gt(0) & event_values.ne("")
    valid_samples = int(keep.sum())
    event_count = int(events.loc[keep].sum())
    if valid_samples < 5 or event_count < 2:
        raise BulkAnalysisError(
            f"预后分析列选择无效：有效样本 {valid_samples} 个、事件 {event_count} 个；请检查随访时间列、事件列和事件阳性值"
        )
    return {
        "matched_samples": len(overlap),
        "valid_survival_samples": valid_samples,
        "events": event_count,
        "time_type": time_type,
        "event_positive": positive,
    }


def load_bulk_tables(
    counts_path: str | Path,
    clinical_path: str | Path,
    *,
    gene_col: Optional[str] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load the original wide counts and clinical tables for analysis-time use."""
    counts, _ = _counts_frame(counts_path, gene_col=gene_col)
    clinical = _read_table(clinical_path, low_memory=False)
    return counts, clinical


def _bh_adjust(pvalues: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg FDR adjustment, preserving NaN values."""
    p = np.asarray(pvalues, dtype=float)
    out = np.full(p.shape, np.nan, dtype=float)
    valid = np.isfinite(p)
    if not valid.any():
        return out
    idx = np.flatnonzero(valid)
    order = idx[np.argsort(p[idx])]
    ranked = p[order]
    q = ranked * len(ranked) / np.arange(1, len(ranked) + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    out[order] = np.minimum(q, 1.0)
    return out


def _safe_log2(values: pd.DataFrame | np.ndarray, pseudocount: float = 0.5) -> Any:
    return np.log2(np.asarray(values, dtype=float) + pseudocount)


def _median_ratio_factors(counts: pd.DataFrame) -> pd.Series:
    """DESeq2-style median-of-ratios size factors."""
    matrix = counts.to_numpy(dtype=float)
    positive = matrix > 0
    with np.errstate(divide="ignore", invalid="ignore"):
        log_geo = np.where(positive, np.log(matrix), np.nan).sum(axis=1)
        n_positive = positive.sum(axis=1)
        geo = np.where(n_positive > 0, np.exp(log_geo / np.maximum(n_positive, 1)), np.nan)
        ratios = matrix / geo[:, None]
    factors = np.nanmedian(np.where(np.isfinite(ratios), ratios, np.nan), axis=0)
    factors[~np.isfinite(factors) | (factors <= 0)] = 1.0
    factors = factors / np.exp(np.mean(np.log(factors)))
    return pd.Series(factors, index=counts.columns, name="size_factor")


def _tmm_factors(counts: pd.DataFrame) -> pd.Series:
    """A compact edgeR-style TMM normalization implementation."""
    matrix = counts.to_numpy(dtype=float)
    library = matrix.sum(axis=0)
    library[library <= 0] = 1.0
    ref_idx = int(np.argsort(np.abs(library - np.median(library)))[0])
    factors = np.ones(matrix.shape[1], dtype=float)
    for i in range(matrix.shape[1]):
        if i == ref_idx:
            continue
        y = matrix[:, i]
        r = matrix[:, ref_idx]
        keep = (y > 0) & (r > 0)
        if keep.sum() < 10:
            continue
        m = np.log2((y[keep] / library[i]) / (r[keep] / library[ref_idx]))
        a = 0.5 * np.log2((y[keep] / library[i]) * (r[keep] / library[ref_idx]))
        m_lo, m_hi = np.quantile(m, [0.30, 0.70])
        a_lo, a_hi = np.quantile(a, [0.05, 0.95])
        trimmed = (m >= m_lo) & (m <= m_hi) & (a >= a_lo) & (a <= a_hi)
        if trimmed.any():
            factors[i] = 2.0 ** float(np.mean(m[trimmed]))
    factors = factors / np.exp(np.mean(np.log(np.maximum(factors, 1e-12))))
    return pd.Series(factors, index=counts.columns, name="tmm_factor")


def _filter_by_expr(counts: pd.DataFrame, groups: pd.Series, min_count: int = DEFAULT_MIN_COUNT) -> pd.Series:
    """Approximate edgeR filterByExpr for a two-group contrast."""
    lib = counts.sum(axis=0).replace(0, np.nan)
    cpm = counts.divide(lib, axis=1) * 1_000_000.0
    group_sizes = groups.value_counts()
    min_group_n = int(max(1, group_sizes.min()))
    return (cpm.ge(1.0).sum(axis=1) >= min_group_n) & (counts.ge(min_count).sum(axis=1) >= min_group_n)


def _design_matrix(
    clinical: pd.DataFrame,
    group_col: str,
    control_level: str,
    case_level: str,
    covariates: Sequence[str],
) -> Tuple[pd.DataFrame, pd.Series]:
    if group_col not in clinical.columns:
        raise BulkAnalysisError(f"分组列 '{group_col}' 不存在")
    group_values = clinical[group_col].map(_clean_identifier)
    allowed = {str(control_level), str(case_level)}
    keep = group_values.isin(allowed)
    if keep.sum() < 3:
        raise BulkAnalysisError("对比组匹配到的样本少于 3 个")
    group = (group_values.loc[keep] == str(case_level)).astype(float)
    if group.nunique() < 2:
        raise BulkAnalysisError("对比组必须同时包含 control 和 case")
    design = pd.DataFrame({"Intercept": 1.0, "group": group.to_numpy()}, index=group.index)
    for col in covariates or []:
        if col not in clinical.columns or col in {group_col, ""}:
            continue
        series = clinical.loc[keep, col]
        numeric = pd.to_numeric(series, errors="coerce")
        if numeric.notna().mean() >= 0.95 and numeric.nunique(dropna=True) > 1:
            design[col] = numeric.fillna(numeric.median()).to_numpy(dtype=float)
        else:
            dummies = pd.get_dummies(series.fillna("NA").map(_clean_identifier), prefix=col, drop_first=True, dtype=float)
            for dcol in dummies.columns:
                design[dcol] = dummies[dcol].to_numpy(dtype=float)
    design = design.loc[:, ~design.columns.duplicated()]
    return design, keep


def _frame_records(frame: Any, limit: int = 20) -> List[Dict[str, Any]]:
    if frame is None:
        return []
    if isinstance(frame, pd.DataFrame):
        data = frame.head(limit).replace({np.nan: None}).to_dict(orient="records")
    else:
        data = frame
    return json.loads(json.dumps(data, default=str))


def _guess_user_result_column(columns: Sequence[str], tokens: Sequence[str]) -> str:
    normalized_columns = {
        str(column): re.sub(r"[^a-z0-9]+", "", str(column).lower())
        for column in columns
    }
    # P is a common short header in exported differential-expression tables;
    # handle it explicitly before token matching so a one-letter column is not
    # lost just because it does not contain the longer ``pvalue`` token.
    if any(token in {"p", "pvalue", "pval"} for token in tokens):
        for column, normalized in normalized_columns.items():
            if normalized in {"p", "pvalue", "pval"}:
                return column
    for column in columns:
        normalized = normalized_columns[str(column)]
        if any(token in normalized for token in tokens):
            return str(column)
    return ""


def _guess_user_gene_column(df: pd.DataFrame, columns: Sequence[str]) -> str:
    """Choose the expression-item column without assuming it is column one.

    Result tables often start with a contrast/cohort column, for example
    ``group,name,log2FC,FDR``.  Choosing the first column in that layout turns
    thousands of genes into two groups.  Prefer explicit identifier headers,
    then use identifier-like content (non-numeric and sufficiently unique) as
    a conservative fallback.
    """
    exact_priority = (
        "gene", "geneid", "geneidentifier", "genename", "genesymbol",
        "symbol", "ensembl", "ensemblid", "feature", "featureid",
        "transcript", "transcriptid", "protein", "proteinid", "target",
        "targetid", "accession", "name", "id",
    )
    normalized_columns = {
        str(column): re.sub(r"[^a-z0-9]+", "", str(column).lower())
        for column in columns
    }
    for preferred in exact_priority:
        for column in columns:
            if normalized_columns[str(column)] == preferred:
                return str(column)

    metadata_tokens = (
        "group", "condition", "contrast", "cohort", "sample", "tissue",
        "cell", "cluster", "class", "status", "disease", "patient",
    )
    identifier_tokens = ("gene", "symbol", "ensembl", "feature", "transcript", "protein", "target", "accession")
    scored: list[tuple[float, str]] = []
    for position, column in enumerate(columns):
        name = str(column)
        normalized = normalized_columns[name]
        series = df[name].map(_clean_identifier)
        nonempty = series[series.ne("")]
        unique_count = int(nonempty.nunique())
        unique_ratio = unique_count / max(1, len(nonempty))
        score = unique_ratio * 30.0 + min(unique_count, 100) / 100.0 * 5.0
        if any(token in normalized for token in identifier_tokens):
            score += 60.0
        if any(token in normalized for token in metadata_tokens):
            score -= 60.0
        if pd.api.types.is_numeric_dtype(df[name]):
            score -= 100.0
        if unique_count <= 1:
            score -= 30.0
        # Preserve input order only as a final tie-breaker.
        scored.append((score - position * 1e-6, name))
    return max(scored, default=(0.0, str(columns[0]) if columns else ""))[1]


def inspect_bulk_result_file(path: str | Path) -> Dict[str, Any]:
    """Inspect an existing result or secondary-analysis table without modeling."""
    df = _read_table(path, low_memory=False)
    if df.empty or df.shape[1] < 2:
        raise BulkAnalysisError("用户结果表至少需要两列：表达项目 ID 和统计结果")
    columns = [str(column) for column in df.columns]
    gene_column_guess = _guess_user_gene_column(df, columns)
    n_genes_guess = int(df[gene_column_guess].map(_clean_identifier).replace("", np.nan).dropna().nunique())
    group_column_guess = _guess_user_result_column(
        columns, ("group", "contrast", "cohort", "condition", "cluster", "celltype", "subtype")
    )
    group_values: Dict[str, List[str]] = {}
    for column in columns:
        values = sorted({value for value in df[column].map(_clean_identifier) if value})
        # The UI needs categorical levels, not a copy of a high-cardinality
        # sample/gene column.  Numeric group labels are retained when they are
        # genuinely categorical and remain small enough to select safely.
        if 0 < len(values) <= 100:
            group_values[column] = values
    return {
        "columns": columns,
        "n_rows": int(len(df)),
        "n_genes_guess": n_genes_guess,
        "gene_column_guess": gene_column_guess,
        "group_column_guess": group_column_guess,
        "group_values": group_values,
        "differential": {
            "effect_column_guess": _guess_user_result_column(columns, ("log2fc", "logfc", "foldchange", "effect", "expression", "expr", "count", "mean")),
            "effect_metric": "log2fc",
        },
        "survival": {
            "effect_column_guess": _guess_user_result_column(columns, ("hazardratio", "hr", "coefficient", "coef", "beta")),
            "effect_metric": "HR",
        },
        "pvalue_column_guess": _guess_user_result_column(columns, ("pvalue", "pval")),
        "padj_column_guess": _guess_user_result_column(columns, ("padj", "fdr", "adjp", "adjustedp", "qvalue", "qval")),
        "direction_column_guess": _guess_user_result_column(columns, ("direction", "trend", "risk")),
    }


def _coerce_result_numeric(series: pd.Series) -> pd.Series:
    cleaned = series.astype(str).str.strip().str.replace(",", "", regex=False)
    cleaned = cleaned.str.replace(r"^[<>=]\s*", "", regex=True)
    return pd.to_numeric(cleaned, errors="coerce")


def _normalise_user_direction(value: Any, effect: float, analysis_type: str) -> str:
    text = _clean_identifier(value).lower().replace("-", "_").replace(" ", "_")
    if text in {"up", "upregulated", "positive", "high", "high_risk", "highrisk", "risk_high"}:
        return "high_risk" if analysis_type == "survival" else "up"
    if text in {"down", "downregulated", "negative", "low", "low_risk", "lowrisk", "risk_low"}:
        return "low_risk" if analysis_type == "survival" else "down"
    if analysis_type == "survival":
        return "high_risk" if effect >= 1 else "low_risk"
    return "up" if effect >= 0 else "down"


def build_user_bulk_result(path: str | Path, config: Mapping[str, Any]) -> "BulkResult":
    """Convert a pre-computed result table to the common bulk-result schema.

    No statistical test, filtering, normalization, or recalculation is done
    here; user-provided statistics are copied into the keys consumed by the
    existing right-side filters and question-time enrichment handoff.
    """
    analysis_type = str(config.get("analysis_type", "differential")).lower()
    if analysis_type not in {"differential", "survival"}:
        raise BulkAnalysisError("用户结果类型只能是 differential 或 survival")
    df = _read_table(path, low_memory=False).copy()
    df.columns = [str(column) for column in df.columns]
    gene_col = str(config.get("gene_col", ""))
    effect_col = str(config.get("effect_col", ""))
    pvalue_col = str(config.get("pvalue_col", ""))
    padj_col = str(config.get("padj_col", ""))
    direction_col = str(config.get("direction_col", ""))
    group_col = str(config.get("group_col", ""))
    configured_group_values = config.get("group_values") or []
    if isinstance(configured_group_values, str):
        configured_group_values = re.split(r"[,\n\r]+", configured_group_values)
    group_values = list(dict.fromkeys(
        _clean_identifier(value) for value in configured_group_values if _clean_identifier(value)
    ))
    effect_metric = str(config.get("effect_metric", "log2fc" if analysis_type == "differential" else "HR"))
    for column, label in ((gene_col, "表达项目 ID"), (effect_col, "表达/效应值")):
        if not column or column not in df.columns:
            raise BulkAnalysisError(f"用户结果表必须选择{label}列")
    for column, label in ((pvalue_col, "P 值"), (padj_col, "FDR"), (direction_col, "方向")):
        if column and column not in df.columns:
            raise BulkAnalysisError(f"用户结果表的{label}列不存在")
    if group_col and group_col not in df.columns:
        raise BulkAnalysisError("用户结果表的分组/对比列不存在")
    if group_values and not group_col:
        raise BulkAnalysisError("选择具体组之前必须先选择分组/对比列")

    if group_col and group_values:
        group_series = df[group_col].map(_clean_identifier)
        df = df[group_series.isin(set(group_values))].copy()
        if df.empty:
            raise BulkAnalysisError("选择的组在结果表中没有匹配记录")

    genes = df[gene_col].map(_clean_identifier)
    effects = _coerce_result_numeric(df[effect_col])
    keep = genes.ne("") & effects.notna()
    if not keep.any():
        raise BulkAnalysisError("用户结果表没有可用的表达项目或效应值")
    result = pd.DataFrame({
        "gene": genes.loc[keep].to_numpy(dtype=str),
        "group": df[group_col].map(_clean_identifier).loc[keep].to_numpy(dtype=str) if group_col else "",
        "pvalue": _coerce_result_numeric(df[pvalue_col]).loc[keep].to_numpy(dtype=float) if pvalue_col else np.nan,
        "padj": _coerce_result_numeric(df[padj_col]).loc[keep].to_numpy(dtype=float) if padj_col else np.nan,
    })
    effect_values = effects.loc[keep].to_numpy(dtype=float)
    if analysis_type == "differential":
        result["log2FoldChange"] = effect_values
        result["statistic"] = effect_values
        result["direction"] = [
            _normalise_user_direction(value, effect, analysis_type)
            for value, effect in zip(df[direction_col].loc[keep], effect_values)
        ] if direction_col else [_normalise_user_direction("", effect, analysis_type) for effect in effect_values]
        output_metric = "log2FoldChange"
    else:
        if effect_metric.lower() not in {"coef", "coefficient", "beta", "loghr", "log_hazard"} and (effect_values <= 0).any():
            raise BulkAnalysisError("预后结果的 HR 列必须为正数")
        if effect_metric.lower() in {"coef", "coefficient", "beta", "loghr", "log_hazard"}:
            result["coef"] = effect_values
            result["HR"] = np.exp(np.clip(effect_values, -50, 50))
        else:
            result["HR"] = effect_values
            result["coef"] = np.log(np.maximum(effect_values, 1e-12))
        result["statistic"] = result["coef"]
        result["direction"] = [
            _normalise_user_direction(value, hr, analysis_type)
            for value, hr in zip(df[direction_col].loc[keep], result["HR"])
        ] if direction_col else [_normalise_user_direction("", hr, analysis_type) for hr in result["HR"]]
        output_metric = "HR"

    unique_genes = list(dict.fromkeys(result["gene"].astype(str).tolist()))
    significance_metric = "padj" if padj_col else "pvalue"
    return BulkResult(
        analysis_type=analysis_type,
        method="user_uploaded_result",
        backend="user_provided",
        n_genes_tested=len(unique_genes),
        n_samples=0,
        result=_frame_records(result, limit=max(1, int(config.get("result_limit", 20000)))),
        gene_sets={"user_result": unique_genes},
        warnings=["这是用户上传的既有分析或二次分析结果；系统未重新计算、归一化或校正统计量，仅按所选列和组载入记录。"],
        metadata={
            "input_type": "user_precomputed_result",
            "gene_col": gene_col,
            "effect_col": effect_col,
            "effect_metric": effect_metric,
            "output_metric": output_metric,
            "pvalue_col": pvalue_col,
            "padj_col": padj_col,
            "direction_col": direction_col,
            "group_col": group_col,
            "group_values": group_values,
            "group_count": int(result["group"].replace("", np.nan).dropna().nunique()),
            "significance_metric": significance_metric,
            "significance_available": bool(pvalue_col or padj_col),
            "raw_result_unchanged": True,
        },
    )


@dataclass
class BulkResult:
    analysis_type: str
    method: str
    backend: str
    n_genes_tested: int
    n_samples: int
    result: List[Dict[str, Any]]
    gene_sets: Dict[str, List[str]]
    warnings: List[str]
    metadata: Dict[str, Any]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "analysis_type": self.analysis_type,
            "method": self.method,
            "backend": self.backend,
            "n_genes_tested": self.n_genes_tested,
            "n_samples": self.n_samples,
            "result": self.result,
            "gene_sets": self.gene_sets,
            "warnings": self.warnings,
            "metadata": self.metadata,
        }


class BulkRNAAnalyzer:
    """Run user-selected bulk RNA-seq analyses on raw counts and clinical data."""

    def __init__(self, counts: pd.DataFrame, clinical: pd.DataFrame):
        if not isinstance(counts, pd.DataFrame) or not isinstance(clinical, pd.DataFrame):
            raise BulkAnalysisError("counts 和 clinical 必须是 pandas.DataFrame")
        self.counts_raw = counts.copy(deep=True)
        self.clinical_raw = clinical.copy(deep=True)

    def run(self, config: Mapping[str, Any]) -> BulkResult:
        analysis_type = str(config.get("analysis_type", "differential")).lower()
        if analysis_type in {"differential", "de", "deg"}:
            return self.run_differential(config)
        if analysis_type in {"survival", "prognosis", "cox"}:
            return self.run_survival(config)
        raise BulkAnalysisError("analysis_type 只能是 differential 或 survival")

    def _validate_raw_counts(self, counts: pd.DataFrame) -> pd.DataFrame:
        numeric = counts.apply(pd.to_numeric, errors="coerce")
        if numeric.isna().any().any():
            bad = int(numeric.isna().sum().sum())
            raise BulkAnalysisError(f"raw count 含 {bad} 个非数值/缺失值")
        values = numeric.to_numpy(dtype=float)
        if (values < 0).any():
            raise BulkAnalysisError("raw count 不能为负数")
        if not np.allclose(values, np.round(values), atol=1e-8):
            raise BulkAnalysisError("差异分析要求 raw integer count；检测到非整数值")
        if (numeric.sum(axis=0) <= 0).any():
            raise BulkAnalysisError("存在总 count 为 0 的样本")
        # Duplicate gene IDs are collapsed only on this analysis-time copy.
        return numeric.groupby(level=0, sort=False).sum()

    def _align_samples(self, sample_col: str, group_col: str = "") -> Tuple[pd.DataFrame, pd.DataFrame]:
        if sample_col not in self.clinical_raw.columns:
            raise BulkAnalysisError(f"临床样本 ID 列 '{sample_col}' 不存在")
        clinical = self.clinical_raw.copy()
        sample_ids = clinical[sample_col].map(_clean_identifier)
        clinical.index = pd.Index(sample_ids, name=sample_col)
        clinical = clinical[~clinical.index.duplicated(keep="first")]
        overlap = [sample for sample in self.counts_raw.columns if str(sample) in clinical.index]
        if len(overlap) < 3:
            raise BulkAnalysisError(f"count 与临床文件只匹配到 {len(overlap)} 个样本，至少需要 3 个")
        counts = self.counts_raw.loc[:, overlap]
        aligned = clinical.loc[overlap].copy()
        return counts, aligned

    @staticmethod
    def _core_de_gene_sets(result: pd.DataFrame, top_n: int) -> Dict[str, List[str]]:
        valid = result.dropna(subset=["padj", "log2FoldChange"]).copy()
        sig = valid[valid["padj"] <= 0.05]
        if sig.empty:
            sig = valid
        high = sig[sig["log2FoldChange"] > 0].sort_values(["padj", "log2FoldChange"], ascending=[True, False])
        low = sig[sig["log2FoldChange"] < 0].sort_values(["padj", "log2FoldChange"], ascending=[True, True])
        return {
            "expression_high": high.head(top_n).index.astype(str).tolist(),
            "expression_low": low.head(top_n).index.astype(str).tolist(),
        }

    def run_differential(self, config: Mapping[str, Any]) -> BulkResult:
        method = str(config.get("method", "deseq2")).lower().replace("-", "_")
        method_alias = {"deseq": "deseq2", "limmavoom": "limma_voom", "limma": "limma_voom", "edger": "edger"}
        method = method_alias.get(method, method)
        if method not in {"deseq2", "edger", "limma_voom"}:
            raise BulkAnalysisError("差异分析方法只能是 DESeq2、edgeR 或 limma-voom")
        sample_col = str(config.get("sample_col", ""))
        group_col = str(config.get("group_col", ""))
        control = str(config.get("control_level", ""))
        case = str(config.get("case_level", ""))
        covariates = [str(c) for c in config.get("covariates", []) if str(c)]
        counts_raw, clinical = self._align_samples(sample_col, group_col)
        counts = self._validate_raw_counts(counts_raw)
        design, keep = _design_matrix(clinical, group_col, control, case, covariates)
        counts = counts.loc[:, design.index]
        groups = clinical.loc[design.index, group_col].map(_clean_identifier)
        min_count = int(config.get("min_count", DEFAULT_MIN_COUNT))
        min_samples = int(config.get("min_samples", max(DEFAULT_MIN_SAMPLES, int(groups.value_counts().min()))))
        r_warning = ""
        try:
            from .r_backend import RBackendError, run_r_differential
            r_payload = run_r_differential(counts, clinical, config, method)
        except Exception as exc:
            r_payload = None
            r_warning = str(exc)

        if r_payload is not None:
            r_result = r_payload["result"].copy()
            if "gene" not in r_result.columns:
                raise BulkAnalysisError("R 差异分析输出缺少 gene 列")
            r_result["gene"] = r_result["gene"].astype(str)
            r_result = r_result[r_result["gene"].str.strip() != ""].set_index("gene")
            for column in ("baseMean", "log2FoldChange", "statistic", "pvalue", "padj", "dispersion"):
                if column in r_result.columns:
                    r_result[column] = pd.to_numeric(r_result[column], errors="coerce")
            r_result["direction"] = np.where(r_result["log2FoldChange"] >= 0, "up", "down")
            r_result = r_result.sort_values(["padj", "pvalue"], na_position="last").copy()
            top_n = int(config.get("top_n", DEFAULT_TOP_N))
            gene_sets = self._core_de_gene_sets(r_result, top_n)
            gene_sets.update(self._subgroup_top_genes(counts, clinical, config, top_n))
            r_meta = dict(r_payload.get("metadata") or {})
            r_meta.update({
                "sample_col": sample_col,
                "group_col": group_col,
                "control_level": control,
                "case_level": case,
                "covariates": covariates,
                "n_genes_input": int(len(counts)),
                "n_genes_after_filter": int(r_meta.get("n_genes_after_filter") or len(r_result)),
                "raw_counts_unchanged": True,
            })
            normalization = r_meta.get("normalization_factors") or {}
            if isinstance(normalization, list):
                normalization = {str(i): value for i, value in enumerate(normalization)}
            r_meta["normalization_factors"] = normalization
            result_limit = len(r_result) if _config_bool(config, "all_genes", True) else max(1, int(config.get("result_limit", 20000)))
            return BulkResult(
                analysis_type="differential",
                method=method,
                backend=str(r_meta.get("backend") or "R/Bioconductor"),
                n_genes_tested=int(len(r_result)),
                n_samples=int(r_meta.get("n_samples") or len(design)),
                result=_frame_records(r_result.reset_index(), limit=result_limit),
                gene_sets=gene_sets,
                warnings=list(r_meta.get("warnings") or []),
                metadata=r_meta,
            )

        warnings: List[str] = [
            "R/Bioconductor 原生后端不可用，结果已透明降级为 Python 兼容实现；论文级结果请先安装/修复 R 依赖后重跑。"
            + (f" 原因：{r_warning}" if r_warning else ""),
        ]

        if method == "deseq2":
            keep_mask = (counts >= min_count).sum(axis=1) >= min_samples
            filtered = counts.loc[keep_mask]
            factors = _median_ratio_factors(filtered)
            result = self._nb_glm_table(filtered, design, factors, method="DESeq2", wald=True)
            pipeline = ["raw integer count", "统一低表达过滤", "DESeq2 size-factor normalization", "negative-binomial GLM", "Wald test"]
        elif method == "edger":
            keep_mask = _filter_by_expr(counts, groups, min_count=min_count)
            filtered = counts.loc[keep_mask]
            factors = _tmm_factors(filtered)
            result = self._nb_glm_table(filtered, design, factors, method="edgeR", wald=False)
            pipeline = ["raw integer count", "filterByExpr", "TMM normalization", "estimateDisp", "glmQLFit", "glmQLFTest"]
        else:
            keep_mask = _filter_by_expr(counts, groups, min_count=min_count)
            filtered = counts.loc[keep_mask]
            factors = _tmm_factors(filtered)
            result = self._voom_table(filtered, design, factors)
            pipeline = ["raw integer count", "filterByExpr", "TMM normalization", "voom", "lmFit", "contrasts.fit", "eBayes"]

        result["padj"] = _bh_adjust(result["pvalue"].to_numpy())
        result = result.sort_values(["padj", "pvalue"], na_position="last").copy()
        result["direction"] = np.where(result["log2FoldChange"] >= 0, "up", "down")
        top_n = int(config.get("top_n", DEFAULT_TOP_N))
        gene_sets = self._core_de_gene_sets(result, top_n)
        gene_sets.update(self._subgroup_top_genes(counts, clinical, config, top_n))
        result_limit = len(result) if _config_bool(config, "all_genes", True) else max(1, int(config.get("result_limit", 20000)))
        return BulkResult(
            analysis_type="differential",
            method=method,
            backend="python_fallback",
            n_genes_tested=int(len(result)),
            n_samples=int(len(design)),
            result=_frame_records(result.reset_index(names="gene"), limit=result_limit),
            gene_sets=gene_sets,
            warnings=warnings,
            metadata={
                "pipeline": pipeline,
                "sample_col": sample_col,
                "group_col": group_col,
                "control_level": control,
                "case_level": case,
                "covariates": covariates,
                "n_genes_input": int(len(counts)),
                "n_genes_after_filter": int(len(filtered)),
                "normalization_factors": {str(k): float(v) for k, v in factors.items()},
                "raw_counts_unchanged": True,
            },
        )

    def _nb_glm_table(self, counts: pd.DataFrame, design: pd.DataFrame, factors: pd.Series, *, method: str, wald: bool) -> pd.DataFrame:
        import statsmodels.api as sm

        # The R/Bioconductor bridge is the primary backend.  When it is not
        # available, the old compatibility path fitted one statsmodels GLM
        # per gene.  That is statistically transparent but computationally
        # pathological for a TCGA-sized matrix (tens of thousands of Python
        # model fits).  For the common no-covariate two-group design, the
        # negative-binomial Wald quantities can be evaluated for all genes in
        # one vectorized pass.  This keeps the complete fallback result table
        # while preserving the declared size-factor/NB/Wald contract.
        design_matrix = design.to_numpy(dtype=float)
        factor_values = factors.loc[design.index].to_numpy(dtype=float)
        if (
            design_matrix.shape[1] == 2
            and np.allclose(design_matrix[:, 0], 1.0)
            and np.isfinite(factor_values).all()
        ):
            matrix = counts.loc[:, design.index].to_numpy(dtype=float)
            normalized = matrix / np.maximum(factor_values[None, :], 1e-12)
            group_mask = design_matrix[:, 1] > 0.5
            control_mask = ~group_mask
            n_case = max(1, int(group_mask.sum()))
            n_control = max(1, int(control_mask.sum()))
            mean_case = np.nanmean(normalized[:, group_mask], axis=1)
            mean_control = np.nanmean(normalized[:, control_mask], axis=1)
            variance = np.nanvar(normalized, axis=1, ddof=1)
            mean_all = np.nanmean(normalized, axis=1)
            alpha = (variance - mean_all) / np.maximum(mean_all * mean_all, 1e-8)
            alpha = np.clip(np.nan_to_num(alpha, nan=1e-8, posinf=100.0, neginf=1e-8), 1e-8, 100.0)
            log2_fold_change = np.log2(
                np.maximum(mean_case, 1e-8) / np.maximum(mean_control, 1e-8)
            )
            variance_log = (
                1.0 / np.maximum(n_case * mean_case, 1e-8)
                + alpha / n_case
                + 1.0 / np.maximum(n_control * mean_control, 1e-8)
                + alpha / n_control
            )
            standard_error = np.sqrt(np.maximum(variance_log, 1e-12)) / math.log(2.0)
            statistic = log2_fold_change / standard_error
            if wald:
                pvalue = 2.0 * stats.norm.sf(np.abs(statistic))
            else:
                pvalue = stats.chi2.sf(np.square(statistic), 1)
            return pd.DataFrame({
                "gene": counts.index.astype(str),
                "baseMean": mean_all,
                "log2FoldChange": log2_fold_change,
                "statistic": statistic,
                "pvalue": np.nan_to_num(pvalue, nan=1.0, posinf=1.0, neginf=1.0),
                "dispersion": alpha,
            }).set_index("gene")

        rows: List[Dict[str, Any]] = []
        offset = np.log(factors.loc[design.index].to_numpy(dtype=float))
        for gene, values in counts.iterrows():
            y = values.loc[design.index].to_numpy(dtype=float)
            normalized = y / np.maximum(factors.loc[design.index].to_numpy(dtype=float), 1e-12)
            mean = float(np.mean(normalized))
            variance = float(np.var(normalized, ddof=1)) if len(normalized) > 1 else mean
            alpha = max((variance - mean) / max(mean * mean, 1e-8), 1e-8)
            alpha = min(alpha, 100.0)
            try:
                model = sm.GLM(y, design.to_numpy(dtype=float), offset=offset,
                               family=sm.families.NegativeBinomial(alpha=alpha))
                fit = model.fit(maxiter=100, disp=0)
                coef = float(fit.params[1]) / math.log(2)
                stat = float(fit.params[1] / max(fit.bse[1], 1e-12))
                pvalue = float(2 * stats.norm.sf(abs(stat))) if wald else float(fit.pvalues[1])
                base_mean = mean
            except Exception:
                # A conservative fallback for genes with a singular/degenerate
                # GLM, while keeping the gene in the complete result table.
                group = design["group"].to_numpy(dtype=bool)
                a = _safe_log2(normalized[group] + 0.5)
                b = _safe_log2(normalized[~group] + 0.5)
                test = stats.ttest_ind(a, b, equal_var=False, nan_policy="omit")
                coef = float(np.mean(a) - np.mean(b))
                stat = float(test.statistic) if np.isfinite(test.statistic) else 0.0
                pvalue = float(test.pvalue) if np.isfinite(test.pvalue) else 1.0
                base_mean = mean
            rows.append({"gene": str(gene), "baseMean": base_mean, "log2FoldChange": coef,
                         "statistic": stat, "pvalue": pvalue, "dispersion": alpha})
        return pd.DataFrame(rows).set_index("gene")

    def _voom_table(self, counts: pd.DataFrame, design: pd.DataFrame, factors: pd.Series) -> pd.DataFrame:
        matrix = counts.loc[:, design.index].to_numpy(dtype=float)
        libs = counts.sum(axis=0).replace(0, np.nan)
        cpm = counts.loc[:, design.index].divide(libs.loc[design.index], axis=1) * 1_000_000.0
        logcpm = _safe_log2(cpm.to_numpy(dtype=float) + 0.5)
        # Voom precision weights: a compact lowess-free trend estimate that is
        # stable for both small tests and large uploaded matrices.
        means = np.nanmean(logcpm, axis=1)
        variances = np.nanvar(logcpm, axis=1, ddof=1)
        trend = np.maximum(variances, np.nanmedian(variances[np.isfinite(variances)]) + 1e-6)
        weights = 1.0 / trend
        x = design.to_numpy(dtype=float)
        xtx_inv = np.linalg.pinv(x.T @ x)
        beta = (xtx_inv @ x.T @ (logcpm * weights[:, None]).T).T / np.maximum(weights[:, None], 1e-12)
        fitted = beta @ x.T
        residual = logcpm - fitted
        df_resid = max(1, x.shape[0] - x.shape[1])
        s2 = np.sum(residual * residual, axis=1) / df_resid
        prior = float(np.nanmedian(s2[np.isfinite(s2)])) if np.isfinite(s2).any() else 1.0
        moderated = (4.0 * prior + df_resid * s2) / (4.0 + df_resid)
        se = np.sqrt(np.maximum(moderated * xtx_inv[1, 1], 1e-12))
        statistic = beta[:, 1] / se
        pvalue = 2 * stats.t.sf(np.abs(statistic), df=4 + df_resid)
        return pd.DataFrame({
            "gene": counts.index.astype(str),
            "baseMean": np.nanmean(matrix / np.maximum(factors.loc[design.index].to_numpy(dtype=float), 1e-12), axis=1),
            "log2FoldChange": beta[:, 1],
            "statistic": statistic,
            "pvalue": pvalue,
            "voom_weight": weights,
            "moderated_variance": moderated,
        }).set_index("gene")

    def _subgroup_top_genes(self, counts: pd.DataFrame, clinical: pd.DataFrame, config: Mapping[str, Any], top_n: int) -> Dict[str, List[str]]:
        col = str(config.get("subgroup_col", ""))
        if not col or col not in clinical.columns:
            return {}
        factors = _tmm_factors(counts)
        normalized = counts.divide(factors, axis=1)
        sets: Dict[str, List[str]] = {}
        levels = [level for level in clinical.loc[normalized.columns, col].map(_clean_identifier).dropna().unique() if level]
        for level in levels:
            sample_ids = clinical.index[clinical[col].map(_clean_identifier) == level].intersection(normalized.columns)
            if len(sample_ids) == 0:
                continue
            ranking = normalized.loc[:, sample_ids].mean(axis=1).sort_values(ascending=False)
            sets[f"subgroup_{level}"] = ranking.head(top_n).index.astype(str).tolist()
        return sets

    def _expression_matrix_for_survival(self, counts: pd.DataFrame, transform: str, gene_length_col: str = "") -> Tuple[pd.DataFrame, List[str]]:
        warnings: List[str] = []
        factors = _tmm_factors(counts)
        transform = transform.lower().replace(" ", "_")
        if transform in {"vst", "variance_stabilizing", "variance_stabilizing_transform"}:
            return pd.DataFrame(_safe_log2(counts.divide(factors, axis=1) + 1), index=counts.index, columns=counts.columns), warnings
        if transform in {"logcpm", "log_cpm"}:
            lib = counts.sum(axis=0).replace(0, np.nan)
            return pd.DataFrame(_safe_log2(counts.divide(lib, axis=1) * 1_000_000 + 1), index=counts.index, columns=counts.columns), warnings
        if transform in {"log2_tpm_1", "log2tpm1", "tpm"}:
            if not gene_length_col or gene_length_col not in counts.columns:
                warnings.append("未提供 gene length；log2(TPM+1) 回退为 log2(CPM+1)，请提供长度列后复核。")
                lib = counts.sum(axis=0).replace(0, np.nan)
                return pd.DataFrame(_safe_log2(counts.divide(lib, axis=1) * 1_000_000 + 1), index=counts.index, columns=counts.columns), warnings
        raise BulkAnalysisError("生存分析表达变换只能选择 VST、logCPM 或 log2(TPM+1)")

    def _vectorized_cox_table(
        self,
        expression: pd.DataFrame,
        times: pd.Series,
        events: pd.Series,
        genes: Sequence[str],
        valid_index: pd.Index,
        batch_size: int = 512,
    ) -> pd.DataFrame:
        """Fast no-covariate Cox fallback using batched risk-set Newton steps.

        This is only used when native ``survival::coxph`` is unavailable. It
        evaluates the Breslow partial-likelihood score and information for a
        batch of genes at once, so a complete cohort does not require one
        Python ``PHReg`` object per gene. Native R remains authoritative when
        it completes successfully.
        """
        valid_index = pd.Index(valid_index)
        time_values = pd.to_numeric(times.loc[valid_index], errors="coerce").to_numpy(dtype=float)
        event_values = pd.to_numeric(events.loc[valid_index], errors="coerce").to_numpy(dtype=int)
        order = np.argsort(time_values, kind="mergesort")
        event_rows = np.flatnonzero(event_values[order].astype(bool))
        if len(event_rows) < 2:
            raise BulkAnalysisError("Cox fallback requires at least two observed events")

        sorted_index = valid_index[order]
        outputs: List[pd.DataFrame] = []
        step_size = max(1, int(batch_size))
        for start in range(0, len(genes), step_size):
            batch_genes = [str(gene) for gene in genes[start:start + step_size]]
            matrix = expression.loc[batch_genes, sorted_index].to_numpy(dtype=float).T
            finite = np.isfinite(matrix).all(axis=0)
            if not finite.any():
                continue
            matrix = np.nan_to_num(matrix[:, finite], nan=0.0, posinf=0.0, neginf=0.0)
            kept_genes = [gene for gene, keep_gene in zip(batch_genes, finite) if keep_gene]
            beta = np.zeros(matrix.shape[1], dtype=float)
            information = np.ones(matrix.shape[1], dtype=float)

            for _ in range(8):
                eta = np.clip(matrix * beta[None, :], -30.0, 30.0)
                weights = np.exp(eta)
                risk = np.cumsum(weights[::-1, :], axis=0)[::-1, :]
                risk_x = np.cumsum((weights * matrix)[::-1, :], axis=0)[::-1, :]
                risk_xx = np.cumsum((weights * matrix * matrix)[::-1, :], axis=0)[::-1, :]
                risk_event = np.maximum(risk[event_rows, :], 1e-12)
                mean_event = risk_x[event_rows, :] / risk_event
                variance_event = np.maximum(
                    risk_xx[event_rows, :] / risk_event - mean_event * mean_event,
                    1e-12,
                )
                score = np.sum(matrix[event_rows, :] - mean_event, axis=0)
                information = np.maximum(np.sum(variance_event, axis=0), 1e-12)
                step = np.clip(score / information, -2.0, 2.0)
                beta += step
                if float(np.nanmax(np.abs(step))) < 1e-5:
                    break

            standard_error = 1.0 / np.sqrt(np.maximum(information, 1e-12))
            z_value = beta / standard_error
            pvalue = 2.0 * stats.norm.sf(np.abs(z_value))
            outputs.append(pd.DataFrame({
                "gene": kept_genes,
                "coef": beta,
                "HR": np.exp(np.clip(beta, -50.0, 50.0)),
                "z": z_value,
                "pvalue": np.nan_to_num(pvalue, nan=1.0, posinf=1.0, neginf=1.0),
                "n": int(len(valid_index)),
            }))

        if not outputs:
            raise BulkAnalysisError(
                "No genes could be fitted by the Cox model / 没有基因成功拟合 Cox 模型"
            )
        return pd.concat(outputs, ignore_index=True)

    def run_survival(self, config: Mapping[str, Any]) -> BulkResult:
        sample_col = str(config.get("sample_col", ""))
        time_type = str(config.get("time_type", "duration")).lower().replace("-", "_")
        time_col = str(config.get("time_col", ""))
        start_date_col = str(config.get("start_date_col", ""))
        end_date_col = str(config.get("end_date_col", ""))
        event_col = str(config.get("event_col", ""))
        covariates = [str(c) for c in config.get("covariates", []) if str(c)]
        counts_raw, clinical = self._align_samples(sample_col)
        counts = self._validate_raw_counts(counts_raw)
        r_warning = ""
        try:
            from .r_backend import run_r_survival
            r_payload = run_r_survival(counts, clinical, config)
        except Exception as exc:
            r_payload = None
            r_warning = str(exc)

        if r_payload is not None:
            r_result = r_payload["result"].copy()
            if "gene" not in r_result.columns:
                raise BulkAnalysisError("R Cox 分析输出缺少 gene 列")
            r_result["gene"] = r_result["gene"].astype(str)
            r_result = r_result[r_result["gene"].str.strip() != ""].set_index("gene")
            for column in ("coef", "HR", "z", "pvalue", "n"):
                if column in r_result.columns:
                    r_result[column] = pd.to_numeric(r_result[column], errors="coerce")
            r_result["padj"] = _bh_adjust(r_result["pvalue"].to_numpy(dtype=float))
            r_result["direction"] = np.where(r_result["HR"] >= 1, "high_risk", "low_risk")
            r_result = r_result.sort_values(["padj", "pvalue"], na_position="last").copy()
            top_n = int(config.get("top_n", DEFAULT_TOP_N))
            valid = r_result.dropna(subset=["padj"]).copy()
            sig = valid[valid["padj"] <= 0.05]
            if sig.empty:
                sig = valid
            high = sig[sig["HR"] > 1].sort_values(["padj", "HR"], ascending=[True, False])
            low = sig[sig["HR"] < 1].sort_values(["padj", "HR"], ascending=[True, True])
            gene_sets = {"hr_high": high.head(top_n).index.astype(str).tolist(), "hr_low": low.head(top_n).index.astype(str).tolist()}
            gene_sets.update(self._subgroup_top_genes(counts, clinical, config, top_n))
            r_meta = dict(r_payload.get("metadata") or {})
            r_meta.update({
                "sample_col": sample_col,
                "time_type": r_meta.get("time_type") or time_type,
                "time_col": time_col,
                "start_date_col": start_date_col,
                "end_date_col": end_date_col,
                "event_col": event_col,
                "event_positive": str(config.get("event_positive", "1")).lower(),
                "covariates": covariates,
                "expression_transform": str(config.get("expression_transform", "vst")),
                "raw_counts_unchanged": True,
            })
            result_limit = len(r_result) if _config_bool(config, "all_genes", True) else max(1, int(config.get("result_limit", 5000)))
            return BulkResult(
                analysis_type="survival",
                method="cox_phreg",
                backend=str(r_meta.get("backend") or "R survival::coxph"),
                n_genes_tested=int(len(r_result)),
                n_samples=int(r_meta.get("n_samples") or 0),
                result=_frame_records(r_result.reset_index(), limit=result_limit),
                gene_sets=gene_sets,
                warnings=list(r_meta.get("warnings") or []),
                metadata=r_meta,
            )

        fallback_warning = (
            "R 原生 survival::coxph 后端不可用，结果已透明降级为 statsmodels PHReg；论文级结果请先安装/修复 R 依赖后重跑。"
            + (f" 原因：{r_warning}" if r_warning else "")
        )
        if time_type in {"date", "date_ymd", "ymd", "calendar_date"}:
            time_type = "date_ymd"
            required_time_cols = (start_date_col, end_date_col)
        else:
            time_type = "duration"
            required_time_cols = (time_col,)
        for col in (*required_time_cols, event_col):
            if col not in clinical.columns:
                raise BulkAnalysisError(f"临床列 '{col}' 不存在")
        if time_type == "date_ymd":
            start_dates = pd.to_datetime(clinical[start_date_col], errors="coerce")
            end_dates = pd.to_datetime(clinical[end_date_col], errors="coerce")
            times = (end_dates - start_dates).dt.total_seconds() / (24 * 60 * 60)
        else:
            times = pd.to_numeric(clinical[time_col], errors="coerce")
        event_values = clinical[event_col].map(_clean_identifier).str.lower()
        positive = str(config.get("event_positive", "1")).lower()
        events = (event_values == positive).astype(int)
        keep = times.notna() & times.gt(0)
        if keep.sum() < 5 or events.loc[keep].sum() < 2:
            raise BulkAnalysisError("生存分析至少需要 5 个有效样本和 2 个事件")
        transform = str(config.get("expression_transform", "vst"))
        expr, warnings = self._expression_matrix_for_survival(counts.loc[:, clinical.index], transform, str(config.get("gene_length_col", "")))
        expr = expr.loc[:, clinical.index]
        if _config_bool(config, "all_genes", True):
            genes = expr.index.astype(str).tolist()
        else:
            genes = [g for g in config.get("genes", []) if str(g) in expr.index]
            if not genes:
                n_genes = min(int(config.get("max_genes", 1000)), expr.shape[0])
                genes = expr.var(axis=1).sort_values(ascending=False).head(n_genes).index.astype(str).tolist()
                warnings.append(f"未指定基因列表；按方差选取 top {len(genes)} 个基因进行 Cox 回归。")
        cov = clinical.loc[keep, covariates].copy() if covariates else pd.DataFrame(index=clinical.index[keep])
        x_cov = pd.DataFrame(index=clinical.index[keep])
        for col in cov.columns:
            numeric = pd.to_numeric(cov[col], errors="coerce")
            if numeric.notna().mean() >= 0.95:
                x_cov[col] = numeric.fillna(numeric.median())
            else:
                dummies = pd.get_dummies(cov[col].fillna("NA").map(_clean_identifier), prefix=col, drop_first=True, dtype=float)
                x_cov = pd.concat([x_cov, dummies], axis=1)
        valid_time_index = clinical.index[keep]
        if x_cov.empty:
            # A complete fallback cohort must not instantiate one Python
            # survival model per gene.  The batched implementation evaluates
            # all selected genes together and keeps the full result table.
            result = self._vectorized_cox_table(
                expr,
                times,
                events,
                genes,
                valid_time_index,
            )
            warnings.append(
                "Native R unavailable; used batched vectorized Cox/Breslow fallback for the complete gene set"
            )
        else:
            try:
                from statsmodels.duration.hazard_regression import PHReg
            except ImportError as exc:
                raise BulkAnalysisError("当前 Python 环境缺少 statsmodels.duration.PHReg") from exc
            rows: List[Dict[str, Any]] = []
            for gene in genes:
                # ``keep`` is defined on the full clinical table, while each
                # gene vector is evaluated only on samples with valid follow-up.
                gene_values = pd.to_numeric(expr.loc[gene, valid_time_index], errors="coerce")
                valid = gene_values.notna()
                valid_events = events.loc[gene_values.index[valid]]
                if valid.sum() < 5 or valid_events.sum() < 2 or gene_values.loc[valid].nunique() < 2:
                    continue
                x = pd.DataFrame({"expression": gene_values.loc[valid].to_numpy(dtype=float)}, index=gene_values.index[valid])
                x = pd.concat([x, x_cov.loc[x.index]], axis=1)
                try:
                    fit = PHReg(times.loc[x.index].to_numpy(dtype=float), x.to_numpy(dtype=float),
                                status=events.loc[x.index].to_numpy(dtype=int), ties="efron").fit(disp=0)
                    coef = float(fit.params[0])
                    pvalue = float(fit.pvalues[0])
                    rows.append({"gene": str(gene), "coef": coef, "HR": float(np.exp(coef)),
                                 "z": float(fit.tvalues[0]), "pvalue": pvalue, "n": int(len(x))})
                except Exception:
                    continue
            result = pd.DataFrame(rows)
        if result.empty:
            raise BulkAnalysisError("没有基因成功拟合 Cox 模型；请检查时间、事件和表达列")
        result = result.set_index("gene")
        result["padj"] = _bh_adjust(result["pvalue"].to_numpy())
        result["direction"] = np.where(result["HR"] >= 1, "high_risk", "low_risk")
        top_n = int(config.get("top_n", DEFAULT_TOP_N))
        valid = result.dropna(subset=["padj"]).copy()
        sig = valid[valid["padj"] <= 0.05]
        if sig.empty:
            sig = valid
        high = sig[sig["HR"] > 1].sort_values(["padj", "HR"], ascending=[True, False])
        low = sig[sig["HR"] < 1].sort_values(["padj", "HR"], ascending=[True, True])
        gene_sets = {"hr_high": high.head(top_n).index.astype(str).tolist(), "hr_low": low.head(top_n).index.astype(str).tolist()}
        # Prognostic analyses can still expose subgroup-specific expression sets
        # when the user provides a clinical subtype column.
        gene_sets.update(self._subgroup_top_genes(counts.loc[:, clinical.index], clinical, config, top_n))
        result_limit = len(result) if _config_bool(config, "all_genes", True) else max(1, int(config.get("result_limit", 5000)))
        return BulkResult(
            analysis_type="survival",
            method="cox_phreg",
            backend="python_fallback",
            n_genes_tested=int(len(result)),
            n_samples=int(keep.sum()),
            result=_frame_records(result.reset_index(), limit=result_limit),
            gene_sets=gene_sets,
            warnings=warnings + [fallback_warning],
            metadata={
                "pipeline": [transform, "Cox proportional hazards regression", "Benjamini-Hochberg FDR"],
                "sample_col": sample_col,
                "time_type": time_type,
                "time_col": time_col,
                "start_date_col": start_date_col,
                "end_date_col": end_date_col,
                "time_unit": "days" if time_type == "date_ymd" else "as_provided",
                "event_col": event_col,
                "event_positive": positive,
                "covariates": covariates,
                "expression_transform": transform,
                "raw_counts_unchanged": True,
            },
        )


def _batch_enrichment_worker(
    name: str,
    modality: str,
    genes: Sequence[str],
    ranked_genes: Optional[Mapping[str, float]],
    top_terms: int,
    result_queue: Any,
) -> None:
    """Run one enrichment modality in an isolated worker.

    Enrichr/GSEApy can block indefinitely on an unavailable online library or
    consume excessive CPU during a large permutation run. The parent process
    owns the deadline and can terminate this worker without holding up the
    user's question or the FastAPI event loop.
    """
    try:
        import requests

        request_timeout = max(5.0, float(os.getenv("E2SEQ_ENRICHMENT_REQUEST_TIMEOUT", "20")))
        api_request = requests.api.request
        session_request = requests.sessions.Session.request

        def _bounded_api_request(method, url, **kwargs):
            kwargs.setdefault("timeout", request_timeout)
            return api_request(method, url, **kwargs)

        def _bounded_session_request(self, method, url, **kwargs):
            kwargs.setdefault("timeout", request_timeout)
            return session_request(self, method, url, **kwargs)

        # This process is dedicated to one task, so bounding requests here is
        # isolated from the main application and from sibling tasks.
        requests.api.request = _bounded_api_request
        requests.sessions.Session.request = _bounded_session_request

        genes = list(dict.fromkeys(str(g).strip() for g in genes if str(g).strip()))
        if modality in {"GO", "KEGG"}:
            from gseapy.enrichr import Enrichr

            library = "GO_Biological_Process_2023" if modality == "GO" else "KEGG_2021_Human"
            enr = Enrichr(
                gene_list=genes,
                gene_sets=library,
                organism="human",
                outdir=None,
                cutoff=0.05,
                no_plot=True,
            )
            enr.set_organism()
            enr.run()
            frame = getattr(enr, "results", None)
            if frame is None:
                frame = pd.DataFrame()
            if not isinstance(frame, pd.DataFrame):
                frame = pd.DataFrame(frame)
            sort_col = "Adjusted P-value" if "Adjusted P-value" in frame else "P-value"
            if sort_col in frame:
                frame = frame.sort_values(sort_col)
            payload = _frame_records(frame, limit=top_terms)
        elif modality == "GSEA":
            import gseapy as gp

            rank_map = ranked_genes or {}
            ranked = pd.Series(
                {gene: float(rank_map[gene]) for gene in genes if gene in rank_map},
                dtype=float,
            ).dropna().sort_values(ascending=False)
            if ranked.empty:
                ranked = pd.Series(np.linspace(1.0, 0.1, len(genes)), index=genes)
            # This is a question-time core screen. Keep the calculation
            # bounded and expose the setting in the returned records so the
            # answer can state the uncertainty.
            permutations = max(20, min(50, int(os.getenv("E2SEQ_GSEA_PERMUTATIONS", "25"))))
            res = gp.prerank(
                rnk=ranked,
                gene_sets="KEGG_2021_Human",
                permutation_num=permutations,
                threads=1,
                no_plot=True,
                seed=7,
            )
            frame = getattr(res, "res2d", pd.DataFrame())
            payload = _frame_records(frame, limit=top_terms)
            if isinstance(payload, list):
                for record in payload:
                    if isinstance(record, dict):
                        record.setdefault("_screen_permutations", permutations)
        elif modality == "STRING":
            from e2seq.data.local_db import STRINGDatabase

            with STRINGDatabase() as db:
                edges = db.get_network(genes, min_score=0.4)
            payload = _frame_records(pd.DataFrame(edges), limit=50)
        else:
            payload = {"error": f"unknown enrichment modality: {modality}"}
        result_queue.put({"ok": True, "name": name, "modality": modality, "data": payload})
    except Exception as exc:
        result_queue.put({"ok": False, "name": name, "modality": modality, "error": str(exc)})


def _run_batch_enrichment_isolated(
    normalized: Mapping[str, Sequence[str]],
    ranked_genes: Optional[Mapping[str, float]],
    top_terms: int,
    progress: Optional[Callable[[str], None]],
) -> Dict[str, Any]:
    """Dispatch core enrichment tasks with a hard per-task deadline."""
    tasks = [
        (name, modality, list(genes))
        for name, genes in normalized.items()
        for modality in ("GO", "KEGG", "GSEA", "STRING")
    ]
    output: Dict[str, Dict[str, Any]] = {
        name: {"genes": list(genes)} for name, genes in normalized.items()
    }
    timeout_seconds = max(
        10.0,
        float(os.getenv("E2SEQ_ENRICHMENT_TASK_TIMEOUT_SECONDS", "45")),
    )
    context = mp.get_context("spawn")
    jobs = []
    for name, modality, genes in tasks:
        result_queue = context.Queue()
        process = context.Process(
            target=_batch_enrichment_worker,
            args=(name, modality, genes, ranked_genes, top_terms, result_queue),
        )
        process.daemon = True
        process.start()
        jobs.append({"name": name, "modality": modality, "process": process, "queue": result_queue})

    pending = list(jobs)
    deadline = time.monotonic() + timeout_seconds
    while pending and time.monotonic() < deadline:
        for job in list(pending):
            process = job["process"]
            if process.is_alive():
                continue
            process.join(timeout=0.2)
            try:
                result = job["queue"].get_nowait()
            except queue.Empty:
                result = {
                    "ok": False,
                    "name": job["name"],
                    "modality": job["modality"],
                    "error": f"worker exited with code {process.exitcode}",
                }
            if result.get("ok"):
                output[result["name"]][result["modality"]] = result.get("data")
            else:
                output[result["name"]].setdefault("warnings", []).append(
                    f"{result.get('modality')}: {result.get('error', 'unknown worker error')}"
                )
            if progress:
                progress(f"enrichment complete: {result.get('name')} / {result.get('modality')}")
            try:
                job["queue"].close()
            except Exception:
                pass
            try:
                process.close()
            except Exception:
                pass
            pending.remove(job)
        if pending:
            time.sleep(0.05)

    for job in pending:
        process = job["process"]
        if process.is_alive():
            process.terminate()
        process.join(timeout=2)
        output[job["name"]].setdefault("warnings", []).append(
            f"{job['modality']}: timed out after {timeout_seconds:.0f} seconds"
        )
        if progress:
            progress(f"enrichment timeout: {job['name']} / {job['modality']}")
        try:
            job["queue"].close()
        except Exception:
            pass
        try:
            process.close()
        except Exception:
            pass

    core = {}
    for name, data in output.items():
        core[name] = {
            "genes": data.get("genes", [])[:top_terms * 5],
            "go": data.get("GO", [])[:top_terms] if isinstance(data.get("GO"), list) else data.get("GO", {}),
            "kegg": data.get("KEGG", [])[:top_terms] if isinstance(data.get("KEGG"), list) else data.get("KEGG", {}),
            "gsea": data.get("GSEA", [])[:top_terms] if isinstance(data.get("GSEA"), list) else data.get("GSEA", {}),
            "string": data.get("STRING", [])[:50] if isinstance(data.get("STRING"), list) else data.get("STRING", {}),
        }
    return {"gene_sets": output, "core": core, "warnings": []}


def run_batch_enrichment(
    gene_sets: Mapping[str, Sequence[str]],
    *,
    ranked_genes: Optional[Mapping[str, float]] = None,
    top_terms: int = 10,
    progress: Optional[Callable[[str], None]] = None,
) -> Dict[str, Any]:
    """Run GO, KEGG, GSEA and batch STRING for all core gene sets concurrently."""
    normalized = {str(k): list(dict.fromkeys(str(g) for g in v if str(g).strip())) for k, v in gene_sets.items()}
    normalized = {k: v for k, v in normalized.items() if v}
    if not normalized:
        return {"gene_sets": {}, "core": {}, "warnings": ["没有可用于富集的核心基因集合"]}

    return _run_batch_enrichment_isolated(normalized, ranked_genes, top_terms, progress)
