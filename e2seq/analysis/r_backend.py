"""Native R/Bioconductor bridge for expression-profile statistics.

The upload layer keeps source tables untouched.  This module receives the
analysis-time copies prepared by ``BulkRNAAnalyzer`` and runs the selected
method in the user's R installation.  Python remains an explicit fallback
when R or a required package is unavailable.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from textwrap import dedent
from typing import Any, Mapping

import pandas as pd


class RBackendError(RuntimeError):
    """Raised when the configured R/Bioconductor backend cannot run."""


_R_SCRIPT = dedent(r'''
    suppressPackageStartupMessages(library(jsonlite))

    args <- commandArgs(trailingOnly = TRUE)
    if (length(args) < 1) stop("missing bridge configuration")
    cfg <- fromJSON(args[[1]], simplifyVector = FALSE)
    `%||%` <- function(x, y) if (is.null(x)) y else x

    fail <- function(message) {
      write_json(list(error = as.character(message)), cfg$meta_path,
                 auto_unbox = TRUE, na = "null", digits = NA)
      quit(save = "no", status = 1)
    }

    tryCatch({
      counts_df <- read.csv(cfg$counts_path, check.names = FALSE,
                            stringsAsFactors = FALSE, na.strings = c("", "NA"))
      clinical_df <- read.csv(cfg$clinical_path, check.names = FALSE,
                              stringsAsFactors = FALSE, na.strings = c("", "NA"))
      if (ncol(counts_df) < 2) stop("count matrix has no sample columns")
      if (ncol(clinical_df) < 2) stop("clinical table has no variables")

      gene_ids <- trimws(as.character(counts_df[[1]]))
      count_matrix <- as.matrix(counts_df[, -1, drop = FALSE])
      storage.mode(count_matrix) <- "numeric"
      rownames(count_matrix) <- make.unique(gene_ids)
      sample_ids <- trimws(as.character(clinical_df[[1]]))
      rownames(clinical_df) <- sample_ids
      clinical <- clinical_df[, -1, drop = FALSE]
      common <- intersect(colnames(count_matrix), rownames(clinical))
      if (length(common) < 3) stop("count and clinical tables have fewer than 3 matched samples")
      count_matrix <- count_matrix[, common, drop = FALSE]
      clinical <- clinical[common, , drop = FALSE]

      as_char <- function(x) trimws(as.character(x))
      cfg_value <- function(name, default = "") {
        value <- cfg[[name]]
        if (is.null(value) || length(value) == 0 || is.na(value[[1]])) default else as.character(value[[1]])
      }
      as_int <- function(name, default) {
        value <- suppressWarnings(as.integer(cfg_value(name, as.character(default))))
        if (is.na(value)) default else value
      }
      as_bool <- function(name, default = FALSE) {
        value <- tolower(cfg_value(name, if (default) "true" else "false"))
        value %in% c("1", "true", "yes", "y", "on")
      }
      covariates <- unlist(cfg$covariates %||% list(), use.names = FALSE)
      covariates <- as.character(covariates[nzchar(as.character(covariates))])

      if (cfg$analysis_type == "differential") {
        group_col <- cfg_value("group_col")
        control <- cfg_value("control_level")
        case <- cfg_value("case_level")
        if (!group_col %in% colnames(clinical)) stop("group column not found")
        group_values <- as_char(clinical[[group_col]])
        clinical$group <- factor(group_values, levels = c(control, case))
        keep_samples <- !is.na(clinical$group)
        clinical <- clinical[keep_samples, , drop = FALSE]
        count_matrix <- count_matrix[, rownames(clinical), drop = FALSE]
        if (nlevels(droplevels(clinical$group)) < 2) stop("both control and case groups are required")

        cov_names <- character(0)
        for (cv in covariates) {
          if (!cv %in% colnames(clinical)) next
          nm <- make.names(cv)
          raw <- clinical[[cv]]
          numeric_value <- suppressWarnings(as.numeric(as.character(raw)))
          if (mean(!is.na(numeric_value)) >= 0.95 && length(unique(numeric_value[!is.na(numeric_value)])) > 1) {
            numeric_value[is.na(numeric_value)] <- median(numeric_value, na.rm = TRUE)
            clinical[[nm]] <- numeric_value
          } else {
            text_value <- as_char(raw)
            text_value[is.na(text_value) | !nzchar(text_value)] <- "NA"
            clinical[[nm]] <- factor(text_value)
          }
          cov_names <- c(cov_names, nm)
        }
        design_rhs <- paste(c(cov_names, "group"), collapse = " + ")
        de_formula <- as.formula(paste("~", design_rhs))
        design_formula <- as.formula(paste("~ 0 + group", if (length(cov_names)) paste("+", paste(cov_names, collapse = " + ")) else ""))
        design <- model.matrix(design_formula, data = clinical)
        group_columns <- grep("^group", colnames(design), value = TRUE)
        if (length(group_columns) < 2) stop("could not construct group contrast")
        control_column <- group_columns[[1]]
        case_column <- group_columns[[2]]
        contrast <- rep(0, ncol(design))
        names(contrast) <- colnames(design)
        contrast[[case_column]] <- 1
        contrast[[control_column]] <- -1

        method <- tolower(gsub("-", "_", cfg_value("method", "deseq2")))
        min_count <- as_int("min_count", 10)
        min_samples <- as_int("min_samples", 2)
        pipeline <- character(0)
        normalization_factors <- numeric(0)
        filtered_n <- 0L

        if (method == "deseq2") {
          if (!requireNamespace("DESeq2", quietly = TRUE)) stop("R package DESeq2 is not installed")
          keep <- rowSums(count_matrix >= min_count) >= min_samples
          filtered <- round(count_matrix[keep, , drop = FALSE])
          if (!nrow(filtered)) stop("low-expression filtering removed every gene")
          dds <- DESeq2::DESeqDataSetFromMatrix(countData = filtered,
                                                colData = clinical,
                                                design = de_formula)
          dds <- DESeq2::estimateSizeFactors(dds)
          dds <- tryCatch(
            DESeq2::DESeq(dds, test = "Wald", quiet = TRUE,
                          fitType = "parametric", minReplicatesForReplace = Inf),
            error = function(e) {
              # Small validation cohorts can make the parametric dispersion
              # curve non-identifiable.  Keep the native DESeq2 Wald model,
              # but use its gene-wise dispersion estimates in that case.
              dds_gene <- DESeq2::estimateDispersionsGeneEst(dds)
              gene_disp <- S4Vectors::mcols(dds_gene)$dispGeneEst
              gene_disp[!is.finite(gene_disp) | gene_disp <= 0] <- 1e-8
              DESeq2::dispersions(dds_gene) <- gene_disp
              DESeq2::nbinomWaldTest(dds_gene)
            })
          rr <- DESeq2::results(dds, contrast = c("group", case, control),
                                independentFiltering = FALSE, cooksCutoff = FALSE)
          out <- data.frame(gene = rownames(rr),
                            baseMean = rr$baseMean,
                            log2FoldChange = rr$log2FoldChange,
                            statistic = rr$stat,
                            pvalue = rr$pvalue,
                            padj = rr$padj,
                            dispersion = as.numeric(S4Vectors::mcols(dds)$dispersion[match(rownames(rr), rownames(dds))]),
                            stringsAsFactors = FALSE)
          normalization_factors <- DESeq2::sizeFactors(dds)
          pipeline <- c("raw integer count", "统一低表达过滤", "DESeq2 size-factor normalization", "negative-binomial GLM", "Wald test")
        } else {
          if (!requireNamespace("edgeR", quietly = TRUE)) stop("R package edgeR is not installed")
          y0 <- edgeR::DGEList(counts = count_matrix)
          keep <- edgeR::filterByExpr(y0, design = design, min.count = min_count)
          filtered <- y0$counts[keep, , drop = FALSE]
          if (!nrow(filtered)) stop("filterByExpr removed every gene")
          y <- edgeR::DGEList(counts = filtered)
          y <- edgeR::calcNormFactors(y, method = "TMM")
          normalization_factors <- y$samples$norm.factors
          names(normalization_factors) <- rownames(y$samples)
          if (method == "edger") {
            y <- edgeR::estimateDisp(y, design)
            fit <- edgeR::glmQLFit(y, design, robust = TRUE)
            qlf <- edgeR::glmQLFTest(fit, contrast = contrast)
            tab <- edgeR::topTags(qlf, n = Inf, sort.by = "none")$table
            out <- data.frame(gene = rownames(tab),
                              baseMean = tab$logCPM,
                              log2FoldChange = tab$logFC,
                              statistic = tab$F,
                              pvalue = tab$PValue,
                              padj = tab$FDR,
                              stringsAsFactors = FALSE)
            pipeline <- c("raw integer count", "filterByExpr", "TMM normalization", "estimateDisp", "glmQLFit", "glmQLFTest")
          } else if (method == "limma_voom") {
            if (!requireNamespace("limma", quietly = TRUE)) stop("R package limma is not installed")
            voom_fit <- limma::voom(y, design, plot = FALSE)
            fit <- limma::lmFit(voom_fit, design)
            fit <- limma::contrasts.fit(fit, contrasts = matrix(contrast, ncol = 1,
                                                                  dimnames = list(colnames(design), "case_vs_control")))
            fit <- limma::eBayes(fit)
            tab <- limma::topTable(fit, number = Inf, sort.by = "none")
            out <- data.frame(gene = rownames(tab),
                              baseMean = tab$AveExpr,
                              log2FoldChange = tab$logFC,
                              statistic = tab$t,
                              pvalue = tab$P.Value,
                              padj = tab$adj.P.Val,
                              stringsAsFactors = FALSE)
            pipeline <- c("raw integer count", "filterByExpr", "TMM normalization", "voom", "lmFit", "contrasts.fit", "eBayes")
          } else stop("unsupported differential method")
        }
        filtered_n <- nrow(out)
        meta <- list(backend = "R/Bioconductor", pipeline = pipeline,
                     n_genes_input = nrow(count_matrix),
                     n_genes_after_filter = filtered_n,
                     n_samples = nrow(clinical),
                     normalization_factors = as.list(normalization_factors),
                     covariates = covariates)
        write.csv(out, cfg$result_path, row.names = FALSE, na = "")
        write_json(meta, cfg$meta_path, auto_unbox = TRUE, na = "null", digits = NA)
      } else {
        if (!requireNamespace("survival", quietly = TRUE)) stop("R package survival is not installed")
        time_type <- tolower(gsub("-", "_", cfg_value("time_type", "duration")))
        event_col <- cfg_value("event_col")
        if (!event_col %in% colnames(clinical)) stop("event column not found")
        if (time_type %in% c("date", "date_ymd", "ymd", "calendar_date")) {
          start_col <- cfg_value("start_date_col")
          end_col <- cfg_value("end_date_col")
          if (!start_col %in% colnames(clinical) || !end_col %in% colnames(clinical)) stop("date columns not found")
          start_date <- as.Date(as_char(clinical[[start_col]]))
          end_date <- as.Date(as_char(clinical[[end_col]]))
          follow_time <- as.numeric(end_date - start_date)
          time_type <- "date_ymd"
          time_unit <- "days"
        } else {
          time_col <- cfg_value("time_col")
          if (!time_col %in% colnames(clinical)) stop("survival time column not found")
          follow_time <- suppressWarnings(as.numeric(as_char(clinical[[time_col]])))
          time_unit <- "as_provided"
          time_type <- "duration"
        }
        positive <- tolower(cfg_value("event_positive", "1"))
        event_text <- tolower(as_char(clinical[[event_col]]))
        event_status <- as.integer(event_text == positive)
        valid <- !is.na(follow_time) & follow_time > 0 & !is.na(event_status)
        if (sum(valid) < 5 || sum(event_status[valid]) < 2) stop("survival data has too few valid samples or events")
        clinical <- clinical[valid, , drop = FALSE]
        count_matrix <- count_matrix[, rownames(clinical), drop = FALSE]
        follow_time <- follow_time[valid]
        event_status <- event_status[valid]

        transform <- tolower(gsub(" ", "_", cfg_value("expression_transform", "vst")))
        transform_warning <- character(0)
        if (transform %in% c("vst", "variance_stabilizing", "variance_stabilizing_transform")) {
          if (!requireNamespace("DESeq2", quietly = TRUE)) stop("R package DESeq2 is not installed for VST")
          dds <- DESeq2::DESeqDataSetFromMatrix(countData = round(count_matrix),
                                                colData = clinical,
                                                design = ~ 1)
          dds <- DESeq2::estimateSizeFactors(dds)
          vst_obj <- tryCatch(
            DESeq2::varianceStabilizingTransformation(dds, blind = TRUE),
            error = function(e) {
              DESeq2::varianceStabilizingTransformation(dds, blind = TRUE, fitType = "mean")
            })
          expr_matrix <- SummarizedExperiment::assay(vst_obj)
        } else if (transform %in% c("logcpm", "log_cpm")) {
          if (!requireNamespace("edgeR", quietly = TRUE)) stop("R package edgeR is not installed for logCPM")
          y <- edgeR::DGEList(counts = count_matrix)
          y <- edgeR::calcNormFactors(y, method = "TMM")
          expr_matrix <- edgeR::cpm(y, log = TRUE, prior.count = 1)
        } else if (transform %in% c("log2_tpm_1", "log2tpm1", "tpm")) {
          stop("log2(TPM+1) requires a gene-length vector; choose VST or logCPM when no length table is supplied")
        } else stop("unsupported survival expression transform")

        all_genes <- as_bool("all_genes", TRUE)
        if (all_genes) {
          requested_genes <- rownames(expr_matrix)
        } else {
          requested_genes <- unlist(cfg$genes %||% list(), use.names = FALSE)
          requested_genes <- as.character(requested_genes[nzchar(as.character(requested_genes))])
          requested_genes <- intersect(requested_genes, rownames(expr_matrix))
          if (!length(requested_genes)) {
            max_genes <- as_int("max_genes", 1000)
            variances <- apply(expr_matrix, 1, var, na.rm = TRUE)
            requested_genes <- names(sort(variances, decreasing = TRUE))[seq_len(min(max_genes, length(variances)))]
          }
        }

        cov_names <- character(0)
        for (cv in covariates) {
          if (!cv %in% colnames(clinical)) next
          nm <- make.names(cv)
          raw <- clinical[[cv]]
          numeric_value <- suppressWarnings(as.numeric(as.character(raw)))
          if (mean(!is.na(numeric_value)) >= 0.95 && length(unique(numeric_value[!is.na(numeric_value)])) > 1) {
            numeric_value[is.na(numeric_value)] <- median(numeric_value, na.rm = TRUE)
            clinical[[nm]] <- numeric_value
          } else {
            text_value <- as_char(raw)
            text_value[is.na(text_value) | !nzchar(text_value)] <- "NA"
            clinical[[nm]] <- factor(text_value)
          }
          cov_names <- c(cov_names, nm)
        }
        formula_text <- paste("survival::Surv(time, status) ~ expression",
                              if (length(cov_names)) paste("+", paste(cov_names, collapse = " + ")) else "")
        model_formula <- as.formula(formula_text)
        rows <- list()
        skipped <- 0L
        for (gene in requested_genes) {
          dat <- data.frame(time = follow_time, status = event_status,
                            expression = as.numeric(expr_matrix[gene, rownames(clinical)]),
                            clinical, check.names = FALSE)
          fit <- tryCatch(survival::coxph(model_formula, data = dat, ties = "efron", na.action = na.omit), error = function(e) NULL)
          if (is.null(fit)) { skipped <- skipped + 1L; next }
          co <- summary(fit)$coefficients
          if (!"expression" %in% rownames(co)) { skipped <- skipped + 1L; next }
          coef_value <- as.numeric(co["expression", "coef"])
          rows[[length(rows) + 1L]] <- data.frame(gene = gene,
                                                   coef = coef_value,
                                                   HR = as.numeric(exp(coef_value)),
                                                   z = as.numeric(co["expression", "z"]),
                                                   pvalue = as.numeric(co["expression", "Pr(>|z|)"]),
                                                   n = as.integer(fit$n[[1]]),
                                                   stringsAsFactors = FALSE)
        }
        if (!length(rows)) stop("no gene could be fitted by Cox regression")
        out <- do.call(rbind, rows)
        meta <- list(backend = "R survival::coxph",
                     pipeline = c(transform, "Cox proportional hazards regression", "Benjamini-Hochberg FDR"),
                     n_genes_input = nrow(count_matrix), n_samples = nrow(clinical),
                     all_genes_mode = all_genes, n_genes_modeled = length(requested_genes),
                     time_type = time_type, time_unit = time_unit,
                     covariates = covariates, skipped_genes = skipped,
                     warnings = transform_warning)
        write.csv(out, cfg$result_path, row.names = FALSE, na = "")
        write_json(meta, cfg$meta_path, auto_unbox = TRUE, na = "null", digits = NA)
      }
    }, error = function(e) fail(conditionMessage(e)))
''')


def _r_executable(config: Mapping[str, Any]) -> str | None:
    candidates = [
        config.get("r_path"),
        config.get("r_executable"),
        os.environ.get("E2SEQ_R_EXE"),
        os.environ.get("E2SEQ_R_PATH"),
        os.environ.get("R_HOME"),
        shutil.which("Rterm.exe"),
        shutil.which("R.exe"),
        shutil.which("Rscript.exe"),
        shutil.which("R"),
        shutil.which("Rscript"),
    ]
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(str(candidate)).expanduser()
        if path.is_file():
            return str(path)
        if path.is_dir():
            for folder in (path, path / "bin", path / "bin" / "x64"):
                for name in ("Rterm.exe", "R.exe", "Rscript.exe", "R", "Rscript"):
                    executable = folder / name
                    if executable.is_file():
                        return str(executable)
    return None


def _run_r(kind: str, counts: pd.DataFrame, clinical: pd.DataFrame,
           config: Mapping[str, Any], method: str = "") -> dict[str, Any]:
    executable = _r_executable(config)
    if not executable:
        raise RBackendError(
            "R executable not found / 未找到 R 解释器；"
            "set E2SEQ_R_EXE or provide r_path / 请设置 E2SEQ_R_EXE 或配置 r_path"
        )
    with tempfile.TemporaryDirectory(prefix="e2seq_r_") as temp_dir:
        root = Path(temp_dir)
        counts_path = root / "counts.csv"
        clinical_path = root / "clinical.csv"
        result_path = root / "result.csv"
        meta_path = root / "meta.json"
        script_path = root / "bridge.R"
        config_path = root / "config.json"
        counts.to_csv(counts_path, index=True, index_label="gene")
        clinical.to_csv(clinical_path, index=True, index_label="__sample_id__")
        payload = dict(config)
        payload.update({
            "analysis_type": kind,
            "method": method,
            "counts_path": str(counts_path),
            "clinical_path": str(clinical_path),
            "result_path": str(result_path),
            "meta_path": str(meta_path),
        })
        config_path.write_text(json.dumps(payload, ensure_ascii=False, default=str), encoding="utf-8")
        script_path.write_text(_R_SCRIPT, encoding="utf-8")
        try:
            completed = subprocess.run(
                [executable, "--vanilla", "--slave", "-f", str(script_path), "--args", str(config_path)],
                capture_output=True,
                timeout=int(config.get("r_timeout_seconds", 1800)),
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise RBackendError(f"R 分析超过 {config.get('r_timeout_seconds', 1800)} 秒") from exc
        stdout = (completed.stdout or b"").decode("utf-8", errors="replace")
        stderr = (completed.stderr or b"").decode("utf-8", errors="replace")
        if completed.returncode != 0 or not result_path.exists():
            error = ""
            if meta_path.exists():
                try:
                    error = str(json.loads(meta_path.read_text(encoding="utf-8")).get("error") or "")
                except Exception:
                    pass
            detail = error or stderr.strip() or stdout.strip() or f"R exit code {completed.returncode}"
            raise RBackendError(detail[-2000:])
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
            result = pd.read_csv(result_path)
        except Exception as exc:
            raise RBackendError(f"R 输出结果无法读取：{exc}") from exc
        if result.empty:
            raise RBackendError("R 输出结果为空")
        return {"result": result, "metadata": meta, "stdout": stdout, "stderr": stderr}


def run_r_differential(counts: pd.DataFrame, clinical: pd.DataFrame,
                       config: Mapping[str, Any], method: str) -> dict[str, Any]:
    """Run native DESeq2, edgeR QL, or limma-voom."""
    return _run_r("differential", counts, clinical, config, method=method)


def run_r_survival(counts: pd.DataFrame, clinical: pd.DataFrame,
                   config: Mapping[str, Any]) -> dict[str, Any]:
    """Run native survival::coxph on the requested transformed expression."""
    return _run_r("survival", counts, clinical, config)
