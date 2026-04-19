"""Enhanced Vector Store for E2sc — P0/P1/P2/P3 optimizations.

Architecture improvements applied:
  P0  — Chunking by data source + sliding window (vs. one giant doc per gene)
  P0  — BGE-Large embedding (all-MiniLM → BAAI/bge-large-en-v1.5, 1024d)
  P1  — Hybrid BM25 + Dense retrieval with Reciprocal Rank Fusion
  P1  — Reranker (flashrank / BAAI/bge-reranker-v2-m3) for precision boost
  P2  — Query expansion via LLM sub-query generation
  P2  — Metadata pre-filtering (intent detection by keyword)
  P3  — Structured context with provenance labels
  P3  — LRU cache + diagnostic logging
  P3  — Fix dead-code: search_similar_cases / add_case now implemented
"""

from __future__ import annotations

import hashlib
import os
import re
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

# Use HuggingFace mirror for China/低网络延迟环境
if not os.environ.get("HF_ENDPOINT"):
    os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
# 禁用 symlink 警告（Windows 非管理员模式）
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from e2sc.utils import get_config, get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_COLL_PREFIX = "e2sc_"

# --- Chunking parameters ---------------------------------------------------
CHUNK_SIZE_TOKENS = 400   # target tokens per chunk (model max 512)
CHUNK_OVERLAP_TOKENS = 50  # overlap to prevent semantic breaks
BYTES_PER_TOKEN = 4        # rough estimate for character-based splitting

# --- Retrieval parameters --------------------------------------------------
DEFAULT_N_RESULTS = 20          # retrieve this many after BM25+dense fusion
RECALL_MULTIPLIER = 3          # fetch 3x for reranker (top 30 → rerank → top 10)
BM25_ALPHA = 0.45              # weight for BM25; (1-alpha) for dense
RERANKER_TOP_K = 5             # final top-K after reranking
RERANK_THRESHOLD_RATIO = 0.25  # drop docs below max_score × this ratio

# --- Embedding model ------------------------------------------------------
# 默认值（与 EmbeddingConfig 保持一致）
_EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
_EMBED_DIM = 384             # output dimension of MiniLM
_EMBED_NORM = True             # normalize embeddings (required for cosine)

# ---------------------------------------------------------------------------
# Collection naming helpers
# ---------------------------------------------------------------------------

def _sanitize(session_id: str) -> str:
    """Convert an arbitrary session_id into a valid ChromaDB collection name."""
    name = re.sub(r"[^a-zA-Z0-9_-]", "_", session_id)
    name = _COLL_PREFIX + name
    return name[:63] if len(name) >= 3 else (name + "_kb")


# ---------------------------------------------------------------------------
# Text chunking utilities
# ---------------------------------------------------------------------------

def _token_estimate(text: str) -> int:
    """Rough character-based token estimate (4 chars ≈ 1 token)."""
    return len(text) // BYTES_PER_TOKEN


def _sliding_window(text: str, chunk_size: int, overlap: int) -> List[str]:
    """Split text into overlapping chunks of ~chunk_size tokens.

    Splits on sentence boundaries (``.``, ``!``, ``?``) when possible,
    then falls back to clause boundaries (``;``, ``,``) and finally
    hard boundaries to ensure we never return an empty chunk.
    """
    if _token_estimate(text) <= chunk_size:
        return [text]

    chunks: List[str] = []
    # Try splitting on sentences first
    sentence_ends = [m.end() for m in re.finditer(r"[.!?]\s+", text)]
    if len(sentence_ends) < 2:
        # Fall back to semicolons / commas
        sentence_ends = [m.end() for m in re.finditer(r"[;,]\s+", text)]
    sentence_ends.insert(0, 0)

    start = 0
    target_chars = chunk_size * BYTES_PER_TOKEN
    while start < len(text):
        end = start + target_chars
        if end >= len(text):
            chunks.append(text[start:].strip())
            break

        # Walk back to nearest sentence/comma boundary
        boundary = end
        for b in sentence_ends:
            if b <= end and b > end - target_chars // 3:
                boundary = b
                break
        else:
            # Walk back up to 30% of target to find a space
            for b in range(end - 1, max(start, end - target_chars // 3), -1):
                if text[b] in " \t\n":
                    boundary = b + 1
                    break

        chunk_text = text[start:boundary].strip()
        if chunk_text:
            chunks.append(chunk_text)

        # Advance with overlap
        start = boundary - overlap * BYTES_PER_TOKEN
        start = max(start, chunks[-1].find(" ") + 1) if " " in chunks[-1] else start
        if start <= 0:
            start = boundary
        if start >= len(text):
            break

    return [c for c in chunks if c.strip()]


# ---------------------------------------------------------------------------
# Source → data-type taxonomy
# ---------------------------------------------------------------------------

_SOURCE_TO_TYPE: Dict[str, str] = {
    "uniprot":    "protein_function",
    "mygene":     "annotation",
    "quickgo":    "go_annotations",
    "ensembl":    "genomics",
    "opentargets": "disease",
    "clinvar":    "clinical",
    "chembl":     "drug",
    "reactome":   "pathway",
    "string":     "interaction",
    "hmdb":       "metabolite",
    "trrust":     "transcription_factor",
    "gutmgene":   "microbiome",
    "pubmed":     "literature",
    "europepmc":  "literature",
    "gtex":       "expression",
    "humanbase":  "expression",
    "gwas":       "clinical",
    "biogrid":    "interaction",
    "civic":      "clinical",
    "alliance":   "annotation",
}


# ---------------------------------------------------------------------------
# Per-source document formatters (return plain-text snippets)
# ---------------------------------------------------------------------------

def _fmt_uniprot(info: Dict) -> List[str]:
    parts = []
    fn = info.get("function", "")
    if fn:
        parts.append(f"[UniProt] Protein function: {fn}")
    acc = info.get("uniprot_accession", "")
    if acc:
        parts.append(f"[UniProt] Accession: {acc}")
    name = info.get("gene_name", "")
    if name:
        parts.append(f"[UniProt] Gene name: {name}")
    return parts


def _fmt_mygene(info: Dict) -> List[str]:
    parts = []
    summary = info.get("gene_summary", "")
    if summary:
        parts.append(f"[MyGene] Summary: {summary}")
    aliases = info.get("gene_aliases", [])
    if aliases:
        parts.append(f"[MyGene] Aliases: {', '.join(aliases)}")
    pathways = info.get("pathways", [])
    if pathways:
        parts.append(f"[MyGene] Pathways (KEGG/Reactome): {'; '.join(pathways)}")
    return parts


def _fmt_quickgo(info: Dict) -> List[str]:
    terms = info.get("go_terms", [])
    if not terms:
        return []
    return [f"[QuickGO] GO annotations: {'; '.join(terms)}"]


def _fmt_ensembl(info: Dict) -> List[str]:
    parts = []
    eid = info.get("ensembl_id", "")
    desc = info.get("description", "")
    chrom = info.get("chromosome", "")
    biotype = info.get("biotype", "")
    if eid:
        parts.append(f"[Ensembl] ID: {eid}; Chromosome: {chrom}; Biotype: {biotype}")
    if desc:
        parts.append(f"[Ensembl] Description: {desc}")
    return parts


def _fmt_opentargets(info: Dict) -> List[str]:
    diseases = info.get("ot_diseases", [])
    if not diseases:
        return []
    return [f"[Open Targets] Disease associations: {'; '.join(diseases)}"]


def _fmt_clinvar(info: Dict) -> List[str]:
    variants = info.get("clinvar_variants", [])
    if not variants:
        return []
    parts = []
    for v in variants:
        if isinstance(v, dict):
            name = v.get("variant", v.get("name", ""))
            sig = v.get("significance", v.get("clinical_significance", ""))
            cond = v.get("condition", "")
            if name:
                entry = f"[ClinVar] {name}"
                if sig:
                    entry += f" — {sig}"
                if cond:
                    entry += f" ({cond})"
                parts.append(entry)
        elif isinstance(v, str) and v.strip():
            parts.append(f"[ClinVar] {v}")
    return parts if parts else [f"[ClinVar] Pathogenic variants: {len(variants)} entries"]


def _fmt_chembl(info: Dict) -> List[str]:
    targets = info.get("drug_targets", [])
    if not targets:
        return []
    return [f"[ChEMBL] Drug targets / molecules: {'; '.join(targets)}"]


def _fmt_reactome(info: Dict) -> List[str]:
    paths = info.get("reactome_pathways", [])
    if not paths:
        return []
    return [f"[Reactome] Pathways: {'; '.join(paths)}"]


def _fmt_string(info: Dict) -> List[str]:
    interactions = info.get("interactions", [])
    if not interactions:
        return []
    lines = []
    for ix in interactions[:10]:
        partner = ix.get("partner", "")
        score = ix.get("score", 0)
        if partner:
            lines.append(f"[STRING] Interacts with {partner} (confidence={score:.3f})")
    return lines


def _fmt_hmdb(info: Dict) -> List[str]:
    metabolites = info.get("metabolites", [])
    if not metabolites:
        return []
    parts = []
    for m in metabolites[:8]:
        name = m.get("name", "")
        ptype = m.get("protein_type", "")
        if name:
            entry = f"[HMDB] Metabolite: {name}"
            if ptype:
                entry += f" (protein role: {ptype})"
            parts.append(entry)
    return parts


def _fmt_trrust(info: Dict) -> List[str]:
    lines = []
    gene_name = info.get("gene", info.get("gene_symbol", "?"))
    tf_targets = info.get("tf_targets", [])
    for t in tf_targets[:8]:
        tg = t.get("target_gene", "")
        effect = t.get("effect", t.get("mode", "Unknown"))
        if tg:
            lines.append(f"[TRRUST] {gene_name} regulates {tg} ({effect})")
    regulators = info.get("regulators", [])
    for r in regulators[:8]:
        tf = r.get("tf", "")
        effect = r.get("effect", r.get("mode", "Unknown"))
        if tf:
            lines.append(f"[TRRUST] {tf} regulates {gene_name} ({effect})")
    return lines


def _fmt_gutmgene(info: Dict) -> List[str]:
    microbes = info.get("gut_microbes", [])
    if not microbes:
        return []
    parts = []
    for gm in microbes[:5]:
            microbe = gm.get("microbe", gm.get("gut_microbiota", ""))
            alteration = gm.get("alteration", gm.get("Alteration", ""))
            condition = gm.get("condition", gm.get("Condition", ""))
            pmid = gm.get("pmid", gm.get("PMID", ""))
            if microbe:
                entry = f"[GUTMGENE] {microbe}"
                if alteration:
                    entry += f" [{alteration}]"
                if condition:
                    entry += f" in {condition}"
                if pmid:
                    entry += f" (PMID:{pmid})"
                parts.append(entry)
    return parts


def _fmt_gtex(info: Dict) -> List[str]:
    tissues = info.get("gtex_tissues", [])
    if not tissues:
        return []
    parts = []
    for t in tissues[:10]:
        if isinstance(t, dict):
            tissue = t.get("tissue", t.get("tissueSiteDetailId", ""))
            expr = t.get("median_expression", t.get("median", ""))
            if tissue:
                parts.append(f"[GTEx] Tissue expression: {tissue} — median TPM={expr}")
        elif isinstance(t, str) and t.strip():
            parts.append(f"[GTEx] {t}")
    return parts


def _fmt_humanbase(info: Dict) -> List[str]:
    tissues = info.get("humanbase_tissues", [])
    if not tissues:
        return []
    parts = []
    for t in tissues[:8]:
        if isinstance(t, dict):
            tissue = t.get("tissue", "")
            score = t.get("score", t.get("specificity", ""))
            if tissue:
                parts.append(f"[HumanBase] Tissue-specific network: {tissue} (specificity={score})")
        elif isinstance(t, str) and t.strip():
            parts.append(f"[HumanBase] {t}")
    return parts


def _fmt_gwas(info: Dict) -> List[str]:
    snps = info.get("gwas_snps", [])
    if not snps:
        return []
    parts = []
    for s in snps[:8]:
        if isinstance(s, dict):
            trait = s.get("trait", s.get("mappedTrait", s.get("disease_trait", "")))
            rsid = s.get("rsid", s.get("snp", ""))
            pval = s.get("pvalue", s.get("p_value", ""))
            if trait:
                entry = f"[GWAS] Trait: {trait}"
                if rsid:
                    entry += f" — SNP: {rsid}"
                if pval:
                    entry += f" (p={pval})"
                parts.append(entry)
        elif isinstance(s, str) and s.strip():
            parts.append(f"[GWAS] {s}")
    return parts


def _fmt_biogrid(info: Dict) -> List[str]:
    interactions = info.get("biogrid_interactions", [])
    if not interactions:
        return []
    parts = []
    for ix in interactions[:10]:
        if isinstance(ix, dict):
            gene_a = ix.get("gene_a", "")
            gene_b = ix.get("gene_b", "")
            system = ix.get("experimental_system", "")
            pmid = ix.get("pmid", "")
            if gene_a and gene_b:
                entry = f"[BioGRID] {gene_a} — {gene_b}"
                if system:
                    entry += f" ({system})"
                if pmid:
                    entry += f" PMID:{pmid}"
                parts.append(entry)
        elif isinstance(ix, str) and ix.strip():
            parts.append(f"[BioGRID] {ix}")
    return parts


def _fmt_civic(info: Dict) -> List[str]:
    variants = info.get("civic_variants", [])
    if not variants:
        return []
    parts = []
    for v in variants[:8]:
        if isinstance(v, str) and v.strip():
            parts.append(f"[CIViC] Clinical variant: {v}")
        elif isinstance(v, dict):
            name = v.get("name", "")
            sig = v.get("clinical_significance", "")
            if name:
                entry = f"[CIViC] Variant: {name}"
                if sig:
                    entry += f" — {sig}"
                parts.append(entry)
    return parts


def _fmt_alliance(info: Dict) -> List[str]:
    homologs = info.get("alliance_homologs", "")
    if not homologs:
        return []
    if isinstance(homologs, str) and homologs.strip():
        return [f"[Alliance] Cross-species homologs: {homologs}"]
    if isinstance(homologs, list):
        parts = []
        for h in homologs[:8]:
            if isinstance(h, str) and h.strip():
                parts.append(f"[Alliance] Homolog: {h}")
            elif isinstance(h, dict):
                species = h.get("species", "")
                symbol = h.get("symbol", h.get("gene", ""))
                if symbol:
                    parts.append(f"[Alliance] Homolog: {symbol} ({species})")
        return parts
    return []


def _fmt_pubmed(article: Dict) -> str:
    pmid = article.get("pmid", "")
    title = article.get("title", "")
    abstract = article.get("abstract", "") or article.get("summary", "")
    text = f"[PubMed PMID:{pmid}] {title}\n.Abstract: {abstract}".strip()
    return text


def _fmt_europepmc(article: Dict) -> str:
    eid = article.get("id", "")
    title = article.get("title", "")
    abstract = article.get("abstractText", "") or article.get("abstract", "")
    text = f"[EuropePMC {eid}] {title}\n.Abstract: {abstract}".strip()
    return text


# ---------------------------------------------------------------------------
# P0: Source-aware chunk builder
# ---------------------------------------------------------------------------

def _build_chunks_for_gene(gene: str, info: Dict) -> List[Dict]:
    """Split a gene's knowledge into semantically coherent chunks.

    Returns a list of dicts with keys: ``id``, ``document``, ``metadata``.
    """
    chunks: List[Dict] = []
    doc_type = "gene"

    # --- UniProt -----------------------------------------------------------
    uniprot_snippets = _fmt_uniprot(info)
    if uniprot_snippets:
        joined = "\n".join(uniprot_snippets)
        for i, chunk_text in enumerate(_sliding_window(joined, CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS)):
            chunks.append({
                "id": f"{gene}::uniprot::{i}",
                "document": f"Gene: {gene}\n{chunk_text}",
                "metadata": {
                    "gene": gene,
                    "source": "uniprot",
                    "data_type": _SOURCE_TO_TYPE.get("uniprot", "annotation"),
                    "chunk_index": i,
                },
            })

    # --- MyGene -----------------------------------------------------------
    mygene_snippets = _fmt_mygene(info)
    if mygene_snippets:
        joined = "\n".join(mygene_snippets)
        for i, chunk_text in enumerate(_sliding_window(joined, CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS)):
            chunks.append({
                "id": f"{gene}::mygene::{i}",
                "document": f"Gene: {gene}\n{chunk_text}",
                "metadata": {
                    "gene": gene,
                    "source": "mygene",
                    "data_type": _SOURCE_TO_TYPE.get("mygene", "annotation"),
                    "chunk_index": i,
                },
            })

    # --- QuickGO ----------------------------------------------------------
    quickgo_snippets = _fmt_quickgo(info)
    if quickgo_snippets:
        joined = "\n".join(quickgo_snippets)
        for i, chunk_text in enumerate(_sliding_window(joined, CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS)):
            chunks.append({
                "id": f"{gene}::quickgo::{i}",
                "document": f"Gene: {gene}\n{chunk_text}",
                "metadata": {
                    "gene": gene,
                    "source": "quickgo",
                    "data_type": _SOURCE_TO_TYPE.get("quickgo", "annotation"),
                    "chunk_index": i,
                },
            })

    # --- Ensembl ----------------------------------------------------------
    ensembl_snippets = _fmt_ensembl(info)
    if ensembl_snippets:
        joined = "\n".join(ensembl_snippets)
        for i, chunk_text in enumerate(_sliding_window(joined, CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS)):
            chunks.append({
                "id": f"{gene}::ensembl::{i}",
                "document": f"Gene: {gene}\n{chunk_text}",
                "metadata": {
                    "gene": gene,
                    "source": "ensembl",
                    "data_type": _SOURCE_TO_TYPE.get("ensembl", "genomics"),
                    "chunk_index": i,
                },
            })

    # --- Open Targets ------------------------------------------------------
    ot_snippets = _fmt_opentargets(info)
    if ot_snippets:
        joined = "\n".join(ot_snippets)
        for i, chunk_text in enumerate(_sliding_window(joined, CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS)):
            chunks.append({
                "id": f"{gene}::opentargets::{i}",
                "document": f"Gene: {gene}\n{chunk_text}",
                "metadata": {
                    "gene": gene,
                    "source": "opentargets",
                    "data_type": _SOURCE_TO_TYPE.get("opentargets", "disease"),
                    "chunk_index": i,
                },
            })

    # --- ClinVar ----------------------------------------------------------
    clinvar_snippets = _fmt_clinvar(info)
    if clinvar_snippets:
        joined = "\n".join(clinvar_snippets)
        for i, chunk_text in enumerate(_sliding_window(joined, CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS)):
            chunks.append({
                "id": f"{gene}::clinvar::{i}",
                "document": f"Gene: {gene}\n{chunk_text}",
                "metadata": {
                    "gene": gene,
                    "source": "clinvar",
                    "data_type": _SOURCE_TO_TYPE.get("clinvar", "clinical"),
                    "chunk_index": i,
                },
            })

    # --- ChEMBL -----------------------------------------------------------
    chembl_snippets = _fmt_chembl(info)
    if chembl_snippets:
        joined = "\n".join(chembl_snippets)
        for i, chunk_text in enumerate(_sliding_window(joined, CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS)):
            chunks.append({
                "id": f"{gene}::chembl::{i}",
                "document": f"Gene: {gene}\n{chunk_text}",
                "metadata": {
                    "gene": gene,
                    "source": "chembl",
                    "data_type": _SOURCE_TO_TYPE.get("chembl", "drug"),
                    "chunk_index": i,
                },
            })

    # --- Reactome ---------------------------------------------------------
    reactome_snippets = _fmt_reactome(info)
    if reactome_snippets:
        joined = "\n".join(reactome_snippets)
        for i, chunk_text in enumerate(_sliding_window(joined, CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS)):
            chunks.append({
                "id": f"{gene}::reactome::{i}",
                "document": f"Gene: {gene}\n{chunk_text}",
                "metadata": {
                    "gene": gene,
                    "source": "reactome",
                    "data_type": _SOURCE_TO_TYPE.get("reactome", "pathway"),
                    "chunk_index": i,
                },
            })

    # --- STRING -----------------------------------------------------------
    string_snippets = _fmt_string(info)
    if string_snippets:
        joined = "\n".join(string_snippets)
        for i, chunk_text in enumerate(_sliding_window(joined, CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS)):
            chunks.append({
                "id": f"{gene}::string::{i}",
                "document": f"Gene: {gene}\n{chunk_text}",
                "metadata": {
                    "gene": gene,
                    "source": "string",
                    "data_type": _SOURCE_TO_TYPE.get("string", "interaction"),
                    "chunk_index": i,
                },
            })

    # --- HMDB ------------------------------------------------------------
    hmdb_snippets = _fmt_hmdb(info)
    if hmdb_snippets:
        joined = "\n".join(hmdb_snippets)
        for i, chunk_text in enumerate(_sliding_window(joined, CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS)):
            chunks.append({
                "id": f"{gene}::hmdb::{i}",
                "document": f"Gene: {gene}\n{chunk_text}",
                "metadata": {
                    "gene": gene,
                    "source": "hmdb",
                    "data_type": _SOURCE_TO_TYPE.get("hmdb", "metabolite"),
                    "chunk_index": i,
                },
            })

    # --- TRRUST ----------------------------------------------------------
    trrust_snippets = _fmt_trrust(info)
    if trrust_snippets:
        joined = "\n".join(trrust_snippets)
        for i, chunk_text in enumerate(_sliding_window(joined, CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS)):
            chunks.append({
                "id": f"{gene}::trrust::{i}",
                "document": f"Gene: {gene}\n{chunk_text}",
                "metadata": {
                    "gene": gene,
                    "source": "trrust",
                    "data_type": _SOURCE_TO_TYPE.get("trrust", "transcription_factor"),
                    "chunk_index": i,
                },
            })

    # --- GUTMGENE --------------------------------------------------------
    gutmgene_snippets = _fmt_gutmgene(info)
    if gutmgene_snippets:
        joined = "\n".join(gutmgene_snippets)
        for i, chunk_text in enumerate(_sliding_window(joined, CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS)):
            chunks.append({
                "id": f"{gene}::gutmgene::{i}",
                "document": f"Gene: {gene}\n{chunk_text}",
                "metadata": {
                    "gene": gene,
                    "source": "gutmgene",
                    "data_type": _SOURCE_TO_TYPE.get("gutmgene", "microbiome"),
                    "chunk_index": i,
                },
            })

    # --- GTEX ------------------------------------------------------------
    gtex_snippets = _fmt_gtex(info)
    if gtex_snippets:
        joined = "\n".join(gtex_snippets)
        for i, chunk_text in enumerate(_sliding_window(joined, CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS)):
            chunks.append({
                "id": f"{gene}::gtex::{i}",
                "document": f"Gene: {gene}\n{chunk_text}",
                "metadata": {
                    "gene": gene,
                    "source": "gtex",
                    "data_type": _SOURCE_TO_TYPE.get("gtex", "expression"),
                    "chunk_index": i,
                },
            })

    # --- HUMANBASE -------------------------------------------------------
    humanbase_snippets = _fmt_humanbase(info)
    if humanbase_snippets:
        joined = "\n".join(humanbase_snippets)
        for i, chunk_text in enumerate(_sliding_window(joined, CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS)):
            chunks.append({
                "id": f"{gene}::humanbase::{i}",
                "document": f"Gene: {gene}\n{chunk_text}",
                "metadata": {
                    "gene": gene,
                    "source": "humanbase",
                    "data_type": _SOURCE_TO_TYPE.get("humanbase", "expression"),
                    "chunk_index": i,
                },
            })

    # --- GWAS ------------------------------------------------------------
    gwas_snippets = _fmt_gwas(info)
    if gwas_snippets:
        joined = "\n".join(gwas_snippets)
        for i, chunk_text in enumerate(_sliding_window(joined, CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS)):
            chunks.append({
                "id": f"{gene}::gwas::{i}",
                "document": f"Gene: {gene}\n{chunk_text}",
                "metadata": {
                    "gene": gene,
                    "source": "gwas",
                    "data_type": _SOURCE_TO_TYPE.get("gwas", "clinical"),
                    "chunk_index": i,
                },
            })

    # --- BIOGRID ---------------------------------------------------------
    biogrid_snippets = _fmt_biogrid(info)
    if biogrid_snippets:
        joined = "\n".join(biogrid_snippets)
        for i, chunk_text in enumerate(_sliding_window(joined, CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS)):
            chunks.append({
                "id": f"{gene}::biogrid::{i}",
                "document": f"Gene: {gene}\n{chunk_text}",
                "metadata": {
                    "gene": gene,
                    "source": "biogrid",
                    "data_type": _SOURCE_TO_TYPE.get("biogrid", "interaction"),
                    "chunk_index": i,
                },
            })

    # --- CIVIC -----------------------------------------------------------
    civic_snippets = _fmt_civic(info)
    if civic_snippets:
        joined = "\n".join(civic_snippets)
        for i, chunk_text in enumerate(_sliding_window(joined, CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS)):
            chunks.append({
                "id": f"{gene}::civic::{i}",
                "document": f"Gene: {gene}\n{chunk_text}",
                "metadata": {
                    "gene": gene,
                    "source": "civic",
                    "data_type": _SOURCE_TO_TYPE.get("civic", "clinical"),
                    "chunk_index": i,
                },
            })

    # --- ALLIANCE --------------------------------------------------------
    alliance_snippets = _fmt_alliance(info)
    if alliance_snippets:
        joined = "\n".join(alliance_snippets)
        for i, chunk_text in enumerate(_sliding_window(joined, CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS)):
            chunks.append({
                "id": f"{gene}::alliance::{i}",
                "document": f"Gene: {gene}\n{chunk_text}",
                "metadata": {
                    "gene": gene,
                    "source": "alliance",
                    "data_type": _SOURCE_TO_TYPE.get("alliance", "annotation"),
                    "chunk_index": i,
                },
            })

    # --- Fallback: gene-level doc if nothing matched ---------------------
    if not chunks:
        fallback = f"Gene: {gene}\n"
        # grab any non-empty string field
        for k, v in info.items():
            if isinstance(v, str) and v.strip():
                fallback += f"[{k}] {v.strip()}\n"
            elif isinstance(v, list) and v:
                fallback += f"[{k}] {v[0]}\n"
        if fallback.strip() != f"Gene: {gene}":
            chunks.append({
                "id": f"{gene}::fallback::0",
                "document": fallback,
                "metadata": {"gene": gene, "source": "unknown", "data_type": "annotation", "chunk_index": 0},
            })

    return chunks


# ---------------------------------------------------------------------------
# P0: BGE-Large embedding function
# ---------------------------------------------------------------------------

# --- Embedding model (loaded from config or defaults) -------------------------
_EMBED_CFG: Optional[Dict[str, Any]] = None  # {model_name, dimension, normalize, local_only}

# 可用的 Embedding 模型列表
# 需求：默认 4 个，其中最小 80~90MB 模型内置可直接使用；其余支持用户填写本地路径
AVAILABLE_EMBEDDING_MODELS = [
    {
        "id": "sentence-transformers/all-MiniLM-L6-v2",
        "name": "MiniLM-L6 (内置 ~90MB)",
        "dimension": 384,
        "size": "~90MB",
        "description": "最小内置模型，开箱可用（无需额外路径）",
        "default": True,
        "builtin": True,
        "path_required": False,
        "path": "",
    },
    {
        "id": "BAAI/bge-base-en-v1.5",
        "name": "BGE-Base",
        "dimension": 768,
        "size": "~410MB",
        "description": "推荐填写本地目录路径后加载",
        "default": False,
        "builtin": False,
        "path_required": True,
        "path": "",
    },
    {
        "id": "BAAI/bge-large-en-v1.5",
        "name": "BGE-Large",
        "dimension": 1024,
        "size": "~1.3GB",
        "description": "高精度模型，建议本地路径加载",
        "default": False,
        "builtin": False,
        "path_required": True,
        "path": "",
    },
    {
        "id": "sentence-transformers/all-mpnet-base-v2",
        "name": "MPNet-Base",
        "dimension": 768,
        "size": "~420MB",
        "description": "平衡型模型，可配置本地路径",
        "default": False,
        "builtin": False,
        "path_required": True,
        "path": "",
    },
]


def _load_embed_config() -> Dict[str, Any]:
    """Load embedding config from E2scConfig (lazy, cached)."""
    global _EMBED_CFG
    if _EMBED_CFG is None:
        try:
            cfg = get_config()
            _EMBED_CFG = {
                "model_name": cfg.embedding.model_name,
                "dimension": cfg.embedding.model_dimension,
                "normalize": cfg.embedding.normalize,
                "local_only": cfg.embedding.local_only,
                "model_paths": cfg.embedding.model_paths,
                "custom_models": cfg.embedding.custom_models,
            }
        except Exception:
            _EMBED_CFG = {
                "model_name": _EMBED_MODEL,
                "dimension": _EMBED_DIM,
                "normalize": _EMBED_NORM,
                "local_only": False,
                "model_paths": {},
                "custom_models": [],
            }
    return _EMBED_CFG


@lru_cache(maxsize=8)
def _get_embed_fn_for_model(model_name: str, normalize: bool, local_path: str = "") -> embedding_functions.SentenceTransformerEmbeddingFunction:
    """Get embedding function for a specific model (cached per model/path)."""
    kwargs = {
        "model_name": local_path or model_name,
        "normalize_embeddings": normalize,
    }
    if local_path:
        kwargs["trust_remote_code"] = True
    return embedding_functions.SentenceTransformerEmbeddingFunction(**kwargs)


@lru_cache(maxsize=4)
def _get_bge_embed_fn() -> embedding_functions.SentenceTransformerEmbeddingFunction:
    """Get (or create) a cached embedding function.

    Tries BGE-Large first (medical-domain, 1024d). Falls back to the
    built-in DefaultEmbeddingFunction (all-MiniLM-L6-v2, 384d) if the
    model cannot be downloaded (SSL / network / disk errors) or if
    HuggingFace is unreachable.

    A network-reachability probe is done first so the fallback fires
    immediately when HuggingFace is unreachable, without waiting for
    retry delays.
    """
    import os as _os

    # 从配置加载
    cfg = _load_embed_config()
    model_to_load = cfg["model_name"]
    normalize = cfg["normalize"]
    local_only = cfg["local_only"]
    model_paths = cfg.get("model_paths") or {}
    local_path = (model_paths.get(model_to_load) or "").strip()

    # local_only 时：若该模型需要路径但未配置，立即回退到内置模型
    _model_meta = next((m for m in AVAILABLE_EMBEDDING_MODELS if m.get("id") == model_to_load), None)
    if local_only and _model_meta and _model_meta.get("path_required") and not local_path:
        logger.warning(f"Embedding model '{model_to_load}' requires local path, fallback to builtin MiniLM")
        return _get_embed_fn_for_model("sentence-transformers/all-MiniLM-L6-v2", True, "")

    # ── 1. Quick network-reachability probe ───────────────────────────────
    # 仅在非 local_only 且未提供本地路径时才探测网络
    if not local_only and not local_path:
        try:
            import urllib.request
            req = urllib.request.Request(
                "https://huggingface.co",
                headers={"User-Agent": "Mozilla/5.0"},
                method="HEAD",
            )
            _os.environ.setdefault("HF_HUB_TIMEOUT", "8")
            _os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "8")
            urllib.request.urlopen(req, timeout=5)
        except Exception:
            logger.warning(
                "HuggingFace CDN unreachable — falling back to DefaultEmbeddingFunction. "
                "Set local_only=True in embedding config to skip network check."
            )
            return embedding_functions.DefaultEmbeddingFunction()

    # ── 2. Try to load specified model with a hard 20-second wall-clock budget ─
    def _try_load():
        return _get_embed_fn_for_model(model_to_load, normalize, local_path)

    import threading as _thr
    result: dict = {}

    def _worker():
        try:
            result["fn"] = _try_load()
            result["fn"](["test"])   # smoke-test — forces download
        except Exception as _e:
            result["exc"] = _e

    t = _thr.Thread(target=_worker, daemon=True)
    t.start()
    t.join(timeout=20)   # 20 s hard budget

    if t.is_alive() or result.get("exc"):
        logger.warning(
            f"Embedding model '{model_to_load}' load timed out or failed ({result.get('exc')}), "
            "falling back to DefaultEmbeddingFunction (all-MiniLM-L6-v2). "
            "RAG quality slightly lower but pipeline stays functional."
        )
        return embedding_functions.DefaultEmbeddingFunction()

    logger.info(f"Embedding model loaded: {model_to_load}")
    return result["fn"]


# ---------------------------------------------------------------------------
# P1: Reranker (flashrank — BAAI/bge-reranker-v2-m3)
# ---------------------------------------------------------------------------

_reranker_instance: Optional[Any] = None   # lazily initialised


def _get_reranker():
    """Lazily initialise and return the flashrank reranker.

    Falls back to None if flashrank is unavailable or if the
    BAAI/bge-reranker-v2-m3 model cannot be downloaded (SSL / network errors).
    """
    global _reranker_instance
    if _reranker_instance is None:
        try:
            from flashrank import Ranker
            _reranker_instance = Ranker.model_name("BAAI/bge-reranker-v2-m3")
            logger.info("Reranker ready: BAAI/bge-reranker-v2-m3 (flashrank)")
        except Exception as _e:
            logger.warning(
                f"Reranker unavailable ({_e}), skipping cross-encoder reranking. "
                "Dense + BM25 hybrid retrieval will still work."
            )
            _reranker_instance = False   # sentinel: not available
    return _reranker_instance if _reranker_instance else None


def _rerank(query: str, hits: List[Dict], top_k: int = RERANKER_TOP_K) -> List[Dict]:
    """Re-rank hits using BAAI/bge-reranker-v2-m3 (flashrank).

    Returns the top-K re-ranked hits with reranker scores attached.
    Falls back to original ordering if reranker is unavailable.
    """
    ranker = _get_reranker()
    if not ranker:
        return hits[:top_k]

    try:
        import flashrank
        passages = [
            {"id": i, "text": h["document"]}
            for i, h in enumerate(hits)
        ]
        results = ranker.rerank(query=query, passages=passages)
        # Map back to original hits preserving reranker metadata
        id_to_hit = {h["id"]: h for h in hits}
        reranked = []
        max_score = results[0]["score"] if results and len(results) > 0 else 1.0
        threshold = max_score * RERANK_THRESHOLD_RATIO
        for item in results:
            idx = int(item["id"])
            if idx in id_to_hit and item["score"] >= threshold:
                reranked.append({**id_to_hit[idx], "reranker_score": item["score"]})
        return reranked[:top_k]
    except Exception as e:
        logger.warning(f"Reranker failed ({e}), returning dense-only ordering")
        return hits[:top_k]


# ---------------------------------------------------------------------------
# P1: BM25 helper
# ---------------------------------------------------------------------------

_bm25_cache: Dict[str, Any] = {}   # session_id → (tokenized_corpus, bm25_index)


def _build_bm25_index(documents: List[Dict]) -> Any:
    """Build and return a BM25Okapi index over the document list."""
    try:
        from rank_bm25 import BM25Okapi
        tokenized = [doc["document"].lower().split() for doc in documents]
        return BM25Okapi(tokenized)
    except ImportError:
        logger.warning(
            "rank_bm25 not installed — BM25 disabled. "
            "Install with: pip install rank_bm25"
        )
        return None


def _bm25_search(bm25_index, documents: List[Dict], query: str, top_n: int) -> List[Dict]:
    """Run BM25 query and return (doc, score) pairs sorted descending."""
    if bm25_index is None:
        return []
    tokens = query.lower().split()
    scores = bm25_index.get_scores(tokens)
    scored = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
    result = []
    for idx, score in scored[:top_n]:
        if score > 0:
            result.append({**documents[idx], "bm25_score": float(score)})
    return result


# ---------------------------------------------------------------------------
# P1: Reciprocal Rank Fusion
# ---------------------------------------------------------------------------

def _reciprocal_rank_fusion(
    dense_hits: List[Dict],
    bm25_hits: List[Dict],
    alpha: float = BM25_ALPHA,
    k: int = 60,
) -> List[Dict]:
    """Fuse ranked lists from dense and BM25 retrieval using RRF.

    Score(d) = alpha * (1/(rank_d + k)) + (1-alpha) * (1/(rank_bm25 + k))
    """
    fused: Dict[str, Dict] = {}
    for rank, hit in enumerate(dense_hits):
        key = hit["id"]
        fused[key] = {**hit}
        fused[key]["_rrf_score"] = alpha / (rank + k)

    for rank, hit in enumerate(bm25_hits):
        key = hit["id"]
        if key in fused:
            fused[key]["_rrf_score"] += (1 - alpha) / (rank + k)
        else:
            fused[key] = {**hit}
            fused[key]["_rrf_score"] = (1 - alpha) / (rank + k)

    sorted_fused = sorted(fused.values(), key=lambda x: x["_rrf_score"], reverse=True)
    for h in sorted_fused:
        h.pop("_rrf_score", None)
    return sorted_fused


# ---------------------------------------------------------------------------
# P2: Query intent detection → metadata pre-filter
# ---------------------------------------------------------------------------

# Keyword → source mapping (order matters: more specific first)
_INTENT_KEYWORDS: List[tuple] = [
    (["drug", "target", "inhibitor", "compound", "agonist", "antagonist", "chembl"], ["chembl", "opentargets"]),
    (["variant", "mutation", "pathogenic", "clinvar", "rs", "snv", "cadd"], ["clinvar", "uniprot"]),
    (["pathway", "reactome", "kegg"], ["reactome", "quickgo", "mygene"]),
    (["interact", "ppi", "protein.network", "string"], ["string"]),
    (["tf.", "transcription.factor", "regulates", "trrust"], ["trrust"]),
    (["metabolite", "hmdb", "metabolic"], ["hmdb"]),
    (["microbiome", "gut", "bacteria", "gutmgene"], ["gutmgene"]),
    (["expression", "gtex", "tissue", "tpm", "fpkm"], ["gtex"]),
    (["go.", "gene.ontology", "go term"], ["quickgo"]),
    (["disease", "phenotype", "opentargets"], ["opentargets"]),
    (["pubmed", "literature", "article", "pmid", "abstract"], ["pubmed", "europepmc"]),
]


def detect_source_filter(query: str) -> Optional[Dict[str, Any]]:
    """Detect likely data source(s) from query keywords and return a ChromaDB where clause."""
    q = query.lower()
    matched_sources: set = set()
    for keywords, sources in _INTENT_KEYWORDS:
        if any(kw in q for kw in keywords):
            matched_sources.update(sources)

    if not matched_sources:
        return None

    if len(matched_sources) == 1:
        return {"source": list(matched_sources)[0]}
    return {"source": {"$in": list(matched_sources)}}


# ---------------------------------------------------------------------------
# P2: Gene name extraction → metadata filter
# ---------------------------------------------------------------------------

_GENE_PATTERN = re.compile(r"\b([A-Z]{2,}[A-Z0-9]{0,10})\b")


def extract_gene_names(query: str) -> List[str]:
    """Extract potential gene symbols (2+ uppercase letters) from query."""
    candidates = _GENE_PATTERN.findall(query)
    # Filter common false positives (all-caps English words)
    FALSE_POSITIVES = {
        "THE", "AND", "FOR", "ARE", "BUT", "WITH", "FROM", "THIS", "THAT",
        "THESE", "THOSE", "HAVE", "HAS", "HAD", "VERY", "MORE", "MOST",
        "INTO", "ONLY", "SOME", "SUCH", "WHEN", "WHAT", "WHERE", "WHICH",
        "WHILE", "ABOUT", "AFTER", "ALSO", "BEFORE", "BETWEEN", "CASE",
        "CAUSE", "CELL", "GENE", "DATA", "HIGH", "LOW", "TYPE", "PMID",
        "GTEX", "HMDB", "GO", "KEGG", "PATHWAY", "RISK", "FOLD", "RANK",
    }
    return [g for g in candidates if g not in FALSE_POSITIVES]


# ---------------------------------------------------------------------------
# P2: Query expansion via LLM (optional — called only if llm is provided)
# ---------------------------------------------------------------------------

def expand_query_via_llm(query: str, llm: Any) -> List[str]:
    """Generate 2-3 diverse sub-queries using the LLM to improve recall."""
    prompt = (
        "Given this biomedical research question, generate exactly 2 additional "
        "alternative phrasings that would help find relevant scientific information.\n"
        "Output each phrasing on its own line, nothing else:\n\n"
        f"Question: {query}\n\n"
        "Alternative phrasings:"
    )
    try:
        response = llm.chat([{"role": "user", "content": prompt}])
        sub_queries = [
            line.strip()
            for line in response.strip().split("\n")
            if line.strip() and len(line.strip()) > 10
        ]
        return [query] + sub_queries[:2]
    except Exception as e:
        logger.debug(f"Query expansion failed: {e}")
        return [query]


# ---------------------------------------------------------------------------
# P3: LRU cache for retrieval results
# ---------------------------------------------------------------------------

_RETRIEVAL_CACHE: Dict[str, List[Dict]] = {}
_CACHE_MAX_SIZE = 200


def _cache_key(query: str, n: int, where_hash: str) -> str:
    return hashlib.md5(f"{query}::{n}::{where_hash}".encode()).hexdigest()


# ---------------------------------------------------------------------------
# P3: Diagnostic logging helpers
# ---------------------------------------------------------------------------

def _log_retrieval_diagnostics(
    query: str,
    hits: List[Dict],
    method: str,
    n_dense: int = 0,
    n_bm25: int = 0,
) -> None:
    """Emit structured debug logs for retrieval quality monitoring."""
    if not hits:
        logger.info(f"[RAG-{method}] Query='{query[:80]}' → 0 hits (KB may lack relevant content)")
        return

    distances = [h.get("distance", 1.0) for h in hits]
    sources = [h.get("metadata", {}).get("source", "?") for h in hits]
    logger.info(
        f"[RAG-{method}] query='{query[:60]}' | "
        f"dense={n_dense} bm25={n_bm25} → final={len(hits)} | "
        f"top_dist={distances[0]:.4f} | spread={distances[-1] - distances[0]:.4f} | "
        f"sources={sources[:5]}"
    )
    # Warn if best match is distant (KB may not have relevant content)
    if distances[0] > 1.4:
        logger.warning(f"[RAG-WARN] Low relevance — best distance={distances[0]:.4f} for query: '{query[:60]}'")


# ---------------------------------------------------------------------------
# P2: Structured context formatter
# ---------------------------------------------------------------------------

def format_structured_context(hits: List[Dict]) -> str:
    """Build a structured context string with provenance labels.

    Groups chunks by (gene, source) and labels each with confidence tier.
    """
    if not hits:
        return ""

    # Group by gene
    by_gene: Dict[str, List[Dict]] = {}
    for h in hits:
        gene = h.get("metadata", {}).get("gene", "unknown")
        by_gene.setdefault(gene, []).append(h)

    lines = []
    for gene, gene_hits in sorted(by_gene.items(), key=lambda x: -len(x[1])):
        lines.append(f"\n{'='*60}")
        lines.append(f"## Gene: {gene} ({len(gene_hits)} relevant chunk(s))")
        lines.append(f"{'='*60}")

        # Group by source within this gene
        by_source: Dict[str, List[Dict]] = {}
        for h in gene_hits:
            src = h.get("metadata", {}).get("source", "unknown")
            by_source.setdefault(src, []).append(h)

        for src, src_hits in sorted(by_source.items(), key=lambda x: -len(x[1])):
            for i, h in enumerate(src_hits[:3]):  # max 3 chunks per source per gene
                label = f"[{gene}::{src.upper()}::{i+1}]"
                lines.append(f"\n{label}\n{h['document']}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# VectorStore — main class
# ---------------------------------------------------------------------------

class VectorStore:
    """Enhanced per-session ChromaDB vector store for RAG.

    Optimisations applied:
      P0  — BGE-Large embeddings (1024d, bio-medical domain)
      P0  — Source-aware chunking with sliding window
      P1  — Hybrid BM25 + Dense retrieval with RRF fusion
      P1  — Cross-encoder reranker (BAAI/bge-reranker-v2-m3)
      P2  — Query intent detection + metadata pre-filter
      P2  — Structured context with provenance labels
      P3  — LRU retrieval cache
      P3  — Diagnostic logging + dead-code fix
    """

    def __init__(self, session_id: str = "default", llm: Any = None):
        config = get_config()
        self.session_id = session_id
        self.collection_name = _sanitize(session_id)
        self.db_path = Path(config.database.db_path).expanduser() / "chroma"
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.llm = llm   # optional; used for query expansion

        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False, allow_reset=True),
        )

        # P0: Upgrade embedding to BGE-Large
        self.embedding_function = _get_bge_embed_fn()

        self._ensure_collection(create_fresh=False)

        # P1: Lazy BM25 index (built once per session, reused)
        self._bm25_index: Optional[Any] = None
        self._bm25_documents: List[Dict] = []

        logger.info(
            f"VectorStore ready: collection='{self.collection_name}' "
            f"embed_model={_EMBED_MODEL}({_EMBED_DIM}d)"
        )

    # ------------------------------------------------------------------
    # Collection management
    # ------------------------------------------------------------------

    def _ensure_collection(self, create_fresh: bool = False) -> None:
        if create_fresh:
            try:
                self.client.delete_collection(self.collection_name)
                logger.info(f"Deleted existing collection '{self.collection_name}'")
            except Exception:
                pass

        try:
            self.collection = self.client.get_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
            )
        except Exception:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
                metadata={
                    "description": f"E2sc KB — session {self.session_id}",
                    "embed_model": _EMBED_MODEL,
                    "embed_dim": _EMBED_DIM,
                },
            )

    # ------------------------------------------------------------------
    # P3 fix: implement previously missing methods
    # ------------------------------------------------------------------

    def search_similar_cases(self, query: str, n_results: int = 5) -> List[Dict]:
        """P3 fix: implement the method that retriever.py / memory.py call."""
        return self.search(query, n_results=n_results)

    def add_case(self, case_id: str, case_text: str, metadata: Optional[Dict] = None) -> None:
        """P3 fix: persist a historical case to the vector store."""
        self.collection.upsert(
            ids=[case_id],
            documents=[case_text],
            metadatas=[metadata or {}],
        )

    # ------------------------------------------------------------------
    # P0: Offline build phase
    # ------------------------------------------------------------------

    def reset_and_build(self, knowledge: Dict[str, Any]) -> int:
        """Rebuild the collection with source-aware chunking.

        P0 change: one giant gene doc → multiple source-specific chunks.
        Also builds the session BM25 index for hybrid retrieval.

        Args:
            knowledge: Dict with keys ``genes``, ``pubmed``, ``europepmc``.

        Returns:
            Total number of chunks stored.
        """
        self._ensure_collection(create_fresh=True)
        self._bm25_index = None
        self._bm25_documents = []

        ids, docs, metas = [], [], []
        source_counter: Dict[str, int] = {}

        # --- Per-gene source-aware chunks ---------------------------------
        genes_dict = knowledge.get("genes", {})
        total_genes = len(genes_dict)
        for gene, info in genes_dict.items():
            if not info:
                continue
            chunks = _build_chunks_for_gene(gene, info)
            for chunk in chunks:
                ids.append(chunk["id"])
                docs.append(chunk["document"])
                metas.append(chunk["metadata"])
                _src = chunk.get("metadata", {}).get("source", "unknown")
                source_counter[_src] = source_counter.get(_src, 0) + 1

        # --- PubMed articles (treat as single doc each) -------------------
        for i, article in enumerate(knowledge.get("pubmed", [])):
            text = _fmt_pubmed(article)
            if len(text) > 40:
                ids.append(f"pubmed::{article.get('pmid', str(i))}")
                docs.append(text)
                metas.append({"type": "pubmed", "source": "pubmed", "data_type": "literature"})
                source_counter["pubmed"] = source_counter.get("pubmed", 0) + 1

        # --- EuropePMC articles --------------------------------------------
        for i, article in enumerate(knowledge.get("europepmc", [])):
            text = _fmt_europepmc(article)
            if len(text) > 40:
                ids.append(f"epmc::{article.get('id', str(i))}")
                docs.append(text)
                metas.append({"type": "europepmc", "source": "europepmc", "data_type": "literature"})
                source_counter["europepmc"] = source_counter.get("europepmc", 0) + 1

        if not ids:
            logger.warning("reset_and_build: no documents to add")
            return 0

        # Batch upsert
        batch = 100
        for start in range(0, len(ids), batch):
            self.collection.upsert(
                ids=ids[start:start + batch],
                documents=docs[start:start + batch],
                metadatas=metas[start:start + batch],
            )

        # Build BM25 index over all documents for hybrid retrieval
        self._bm25_documents = [
            {"id": ids[i], "document": docs[i], "metadata": metas[i]}
            for i in range(len(ids))
        ]
        self._bm25_index = _build_bm25_index(self._bm25_documents)

        logger.info(
            f"VectorStore built: {len(ids)} chunks / {total_genes} genes "
            f"(session='{self.session_id}') | BM25 index: {'OK' if self._bm25_index else 'N/A'}"
        )
        try:
            _active_sources = sorted([s for s, c in source_counter.items() if c > 0])
            logger.info(
                "[RAG-SOURCES] active={}/20 | {}".format(
                    len(_active_sources), ", ".join(_active_sources)
                )
            )
            logger.info(
                "[RAG-SOURCE-CHUNKS] {}".format(
                    ", ".join(f"{k}:{source_counter[k]}" for k in sorted(source_counter.keys()))
                )
            )
        except Exception:
            pass
        return len(ids)

    # ------------------------------------------------------------------
    # P1: Hybrid dense + BM25 search
    # ------------------------------------------------------------------

    def _dense_search(
        self,
        query: str,
        n: int,
        where: Optional[Dict] = None,
    ) -> List[Dict]:
        """Pure vector similarity search."""
        count = self.collection.count()
        if count == 0:
            return []
        n = min(n, count)
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n,
                where=where,
                include=["documents", "metadatas", "distances"],
            )
            hits = []
            # Safely access ChromaDB results with fallback
            ids_list = results.get("ids", [[]])
            docs_list = results.get("documents", [[]])
            metas_list = results.get("metadatas", [[]])
            dists_list = results.get("distances", [[]])

            # Ensure first dimension exists
            if ids_list and docs_list and metas_list and dists_list:
                ids = ids_list[0]
                docs = docs_list[0]
                metas = metas_list[0]
                dists = dists_list[0]
                for i in range(len(ids)):
                    hits.append({
                        "id": ids[i],
                        "document": docs[i] if i < len(docs) else "",
                        "metadata": metas[i] if i < len(metas) else {},
                        "distance": dists[i] if i < len(dists) else 0.0,
                    })
            return hits
        except Exception as e:
            logger.error(f"Dense search failed: {e}")
            return []

    def _hybrid_search(
        self,
        query: str,
        n: int,
        where: Optional[Dict] = None,
    ) -> List[Dict]:
        """Hybrid retrieval: BM25 + dense (RRF fusion).

        Fetches 3x candidates from each arm, fuses with RRF,
        then returns top-n fused results.
        """
        recall_k = n * RECALL_MULTIPLIER

        # Dense arm
        dense_hits = self._dense_search(query, recall_k, where)

        # BM25 arm
        bm25_hits = []
        if self._bm25_index is not None:
            # Build a filtered corpus if we have a metadata filter on 'source'
            corpus = self._bm25_documents
            if where and "source" in where:
                src_filter = where["source"]
                if isinstance(src_filter, dict) and "$in" in src_filter:
                    corpus = [d for d in corpus if d["metadata"].get("source") in src_filter["$in"]]
                else:
                    corpus = [d for d in corpus if d["metadata"].get("source") == src_filter]
            filtered_bm25 = _build_bm25_index(corpus) if corpus else None
            bm25_hits = _bm25_search(filtered_bm25 or self._bm25_index, corpus, query, recall_k)

        if not dense_hits and not bm25_hits:
            return []
        if not bm25_hits:
            return dense_hits[:n]
        if not dense_hits:
            return bm25_hits[:n]

        fused = _reciprocal_rank_fusion(dense_hits, bm25_hits, alpha=BM25_ALPHA)
        return fused[:n]

    # ------------------------------------------------------------------
    # P1: Reranking + P2: query expansion
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        n_results: int = 8,
        doc_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """P1/P2 entry point: hybrid search + optional reranking.

        P2: if self.llm is available, expands the query first.
        P1: reranks results if the reranker is available.
        P2: detects intent and applies source pre-filter.

        Args:
            query:     User question.
            n_results: Number of final chunks to return.
            doc_type:  Optional legacy filter (maps to metadata source).

        Returns:
            List of dicts with keys ``id``, ``document``, ``metadata``, ``distance``.
        """
        # P2: query expansion
        queries = [query]
        if self.llm is not None:
            expanded = expand_query_via_llm(query, self.llm)
            if len(expanded) > 1:
                queries = expanded
                logger.debug(f"Query expanded to {len(queries)} sub-queries")

        # P2: intent-based source filter
        where = None
        if doc_type:
            where = {"source": doc_type}
        else:
            intent_filter = detect_source_filter(query)
            if intent_filter:
                where = intent_filter

        # P2: gene name pre-filter (if gene names detected, boost relevance)
        detected_genes = extract_gene_names(query)

        # P1: multi-query hybrid search → merge results
        all_hits: Dict[str, Dict] = {}
        for q in queries:
            hits = self._hybrid_search(q, n_results * RECALL_MULTIPLIER, where)
            for h in hits:
                key = h["id"]
                if key not in all_hits:
                    all_hits[key] = {**h, "_query_count": 1}
                else:
                    all_hits[key]["_query_count"] += 1

        # Merge: deduplicated, sort by distance
        merged = sorted(
            all_hits.values(),
            key=lambda x: (x.get("distance", 999), -x.get("_query_count", 0)),
        )
        for h in merged:
            h.pop("_query_count", None)

        # P1: rerank
        reranked = _rerank(query, merged, top_k=n_results)

        # P3: diagnostic logging
        _log_retrieval_diagnostics(
            query,
            reranked,
            method="HYBRID+RERANK" if _get_reranker() else "HYBRID",
            n_dense=len(queries) * n_results * RECALL_MULTIPLIER,
            n_bm25=len(queries) * n_results * RECALL_MULTIPLIER,
        )

        return reranked

    def retrieve_context(
        self,
        query: str,
        n_results: int = 8,
        structured: bool = True,
    ) -> str:
        """P2/P3 main entry point: retrieve and format context for LLM injection.

        Args:
            query:     User question.
            n_results: Number of chunks to include.
            structured: If True, use structured context with provenance labels.

        Returns:
            Formatted context string ready for LLM prompt injection.
        """
        hits = self.search(query, n_results=n_results)
        if not hits:
            return ""

        if structured:
            return format_structured_context(hits)

        parts = [f"[Context chunk {i+1}]\n{h['document']}" for i, h in enumerate(hits)]
        return "\n\n".join(parts)

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def count(self) -> int:
        try:
            return self.collection.count()
        except Exception:
            return 0

    def clear(self) -> None:
        self._ensure_collection(create_fresh=True)
        self._bm25_index = None
        self._bm25_documents = []
        logger.info(f"VectorStore cleared for session '{self.session_id}'")


# ---------------------------------------------------------------------------
# Per-session factory
# ---------------------------------------------------------------------------

_session_stores: Dict[str, VectorStore] = {}

# Global embedding cache — must be cleared when model changes
_EMBED_CACHE: Dict[str, Any] = {}


def clear_embedding_cache() -> None:
    """Clear all embedding function caches so a new model takes effect."""
    global _EMBED_CACHE
    _EMBED_CACHE.clear()
    # Also clear the LRU cache on the factory functions
    try:
        _get_bge_embed_fn.cache_clear()
        _get_embed_fn_for_model.cache_clear()
    except NameError:
        pass
    # Reset global embed config so it reloads from disk
    global _EMBED_CFG
    _EMBED_CFG = None
    logger.info("Embedding cache cleared — new model will be loaded on next use")


def get_embedding_models() -> List[Dict[str, Any]]:
    """Return available embedding models with metadata (defaults + user custom)."""
    cfg = _load_embed_config()
    model_paths = cfg.get("model_paths") or {}
    custom_models = cfg.get("custom_models") or []

    models = []
    for m in AVAILABLE_EMBEDDING_MODELS:
        item = dict(m)
        item["path"] = model_paths.get(item["id"], item.get("path", ""))
        # local 字段兼容前端旧逻辑：有路径或内置视为本地可用
        item["local"] = bool(item.get("builtin") or item.get("path"))
        models.append(item)

    # 用户新增模型
    for cm in custom_models:
        cid = (cm.get("id") or "").strip()
        if not cid:
            continue
        item = {
            "id": cid,
            "name": cm.get("name") or cid,
            "dimension": cm.get("dimension") or "-",
            "size": cm.get("size") or "未知",
            "description": cm.get("description") or "用户自定义模型",
            "default": False,
            "builtin": False,
            "path_required": True,
            "path": cm.get("path") or model_paths.get(cid, ""),
            "local": bool(cm.get("path") or model_paths.get(cid, "")),
            "custom": True,
        }
        models.append(item)

    return models


def get_vector_store(session_id: str = "default", llm: Any = None) -> VectorStore:
    """Get (or create) the VectorStore for a specific session.

    Args:
        session_id: Chat session identifier.
        llm:        Optional LLM instance for query expansion.

    Returns:
        VectorStore instance.
    """
    if session_id not in _session_stores:
        _session_stores[session_id] = VectorStore(session_id=session_id, llm=llm)
    return _session_stores[session_id]


def reset_vector_store(session_id: str, llm: Any = None) -> VectorStore:
    """Force-create a fresh VectorStore for the session, discarding existing data.

    Called when the user uploads new data or reconfigures an existing session.
    """
    store = VectorStore(session_id=session_id, llm=llm)
    _session_stores[session_id] = store
    return store
