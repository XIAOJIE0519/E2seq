"""Verified public knowledge-source adapters used by Agentic RAG.

The adapters in this module deliberately return a small, source-labelled
record rather than silently converting an unavailable service into an empty
result.  This lets the caller distinguish three different states:

* ``ok``: the endpoint was reachable and returned source records;
* ``no_records``: the endpoint was reachable but this gene has no record;
* ``needs_configuration`` / ``unavailable``: the source could not be queried.

The distinction is important for coverage reports.  A zero for HMDB, for
example, can be a real gene-level coverage result; an unavailable adapter is
never reported as a biological zero.
"""

from __future__ import annotations

import csv
import io
import json
import os
import re
import threading
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import quote

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class KnowledgeSourceClient:
    """Small, dependency-light clients for the verified public endpoints."""

    _USER_AGENT = "E2seq/2.1 (source-audit; +https://github.com/)"
    # ClinicalTrials.gov is public but rate-limits bursts more aggressively
    # than the gene annotation endpoints.  Keep a small global gate so that
    # parallel RAG batches do not turn transient 429/5xx responses into false
    # source failures.
    _clinicaltrials_gate = threading.BoundedSemaphore(4)

    def __init__(self, timeout: int = 20):
        self.timeout = timeout
        self._last_resolution_error = ""
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self._USER_AGENT,
            "Accept": "application/json",
        })
        retry = Retry(
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
        adapter = HTTPAdapter(
            pool_connections=16,
            pool_maxsize=16,
            max_retries=retry,
        )
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _get(self, url: str, **kwargs) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        return self.session.get(url, **kwargs)

    def _post(self, url: str, **kwargs) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        return self.session.post(url, **kwargs)

    @staticmethod
    def _result(source: str, status: str, records: Optional[list] = None,
                fields: Optional[dict] = None, error: str = "") -> dict:
        records = list(records or [])
        return {
            "source": source,
            "status": status,
            "records": records,
            "count": len(records),
            "fields": dict(fields or {}),
            "error": error,
        }

    @staticmethod
    def _payload_rows(payload: Any, max_results: int = 30) -> List[Any]:
        """Extract common list containers without treating empty data as an error."""
        if isinstance(payload, list):
            return payload[:max_results]
        if not isinstance(payload, dict):
            return [payload] if payload not in (None, "") else []
        for key in ("results", "data", "records", "items", "hits", "studies", "models", "edges"):
            value = payload.get(key)
            if isinstance(value, list):
                return value[:max_results]
            if isinstance(value, dict):
                nested = KnowledgeSourceClient._payload_rows(value, max_results=max_results)
                if nested:
                    return nested
        return [payload]

    @staticmethod
    def _extract_path(payload: Any, path: str) -> Any:
        current = payload
        for part in [item for item in str(path or "").split(".") if item]:
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
                current = current[int(part)]
            else:
                return None
        return current

    @staticmethod
    def _template_value(value: Any, gene: str, query: str, context_hint: str) -> Any:
        replacements = {
            "{gene}": quote(str(gene), safe=""),
            "{gene_raw}": str(gene),
            "{query}": quote(str(query), safe=""),
            "{query_raw}": str(query),
            "{context}": quote(str(context_hint or ""), safe=""),
            "{context_raw}": str(context_hint or ""),
        }
        if isinstance(value, dict):
            return {str(key): KnowledgeSourceClient._template_value(item, gene, query, context_hint)
                    for key, item in value.items()}
        if isinstance(value, list):
            return [KnowledgeSourceClient._template_value(item, gene, query, context_hint) for item in value]
        text = str(value) if value is not None else ""
        for marker, replacement in replacements.items():
            text = text.replace(marker, replacement)
        return text

    @staticmethod
    def _disease_context_terms(context_hint: str) -> List[str]:
        """Map common disease labels to terms used by source metadata.

        The uploaded project label is often ``TCGA-BRCA`` or Chinese text
        rather than the exact OncoTree/ClinicalTrials.gov wording.  Only
        recognised disease aliases are returned; generic question words must
        not accidentally filter a source to zero rows.
        """
        raw = str(context_hint or "").strip().lower()
        if not raw:
            return []
        aliases = (
            (("brca", "breast", "mammary", "乳腺", "乳房"),
             ("brca", "breast", "mammary")),
            (("ovarian", "ovary", "卵巢"), ("ovarian", "ovary")),
            (("lung", "nsclc", "luad", "lusc", "肺"), ("lung", "pulmonary", "nsclc", "luad", "lusc")),
            (("colorectal", "colon", "rectal", "结直肠", "结肠", "直肠"), ("colorectal", "colon", "rectal")),
            (("prostate", "前列腺"), ("prostate",)),
            (("pancreatic", "pancreas", "胰腺"), ("pancreatic", "pancreas")),
            (("glioma", "brain", "cns", "脑", "胶质瘤"), ("glioma", "brain", "cns")),
            (("melanoma", "skin", "黑色素瘤"), ("melanoma", "skin")),
            (("gastric", "stomach", "胃"), ("gastric", "stomach")),
            (("liver", "hepatocellular", "hepatic", "肝"), ("liver", "hepatocellular", "hepatic")),
            (("kidney", "renal", "肾"), ("kidney", "renal")),
            (("leukemia", "白血病"), ("leukemia",)),
            (("lymphoma", "淋巴瘤"), ("lymphoma",)),
        )
        terms = set()
        for markers, mapped in aliases:
            if any(marker in raw for marker in markers):
                terms.update(mapped)
        return sorted(terms)

    @staticmethod
    def _first_ensembl(payload: dict, gene: str = "") -> str:
        hits = payload.get("hits", []) if isinstance(payload, dict) else []
        if not isinstance(hits, list):
            return ""
        preferred = []
        for hit in hits:
            if not isinstance(hit, dict):
                continue
            if gene and str(hit.get("symbol", "")).upper() == gene.upper():
                preferred.append(hit)
        ordered = preferred + [hit for hit in hits if hit not in preferred]
        for hit in ordered:
            values = hit.get("ensembl", [])
            if isinstance(values, dict):
                values = [values]
            for value in values if isinstance(values, list) else []:
                if isinstance(value, dict):
                    value = value.get("gene", "")
                value = str(value or "")
                if value.startswith("ENSG"):
                    return value
        return ""

    def resolve_ensembl(self, gene: str) -> str:
        """Resolve an HGNC symbol through MyGene.info without guessing IDs."""
        self._last_resolution_error = ""
        try:
            # MyGene's query parser does not consistently support combining
            # the ``symbol:`` and ``species:`` clauses.  Query the symbol,
            # then select the exact human-symbol hit below; otherwise valid
            # symbols silently looked like an absent Ensembl mapping.
            response = self._get(
                "https://mygene.info/v3/query",
                params={
                    "q": gene,
                    "species": "human",
                    "size": 10,
                    "fields": "symbol,ensembl.gene",
                },
            )
            if response.status_code == 200:
                return self._first_ensembl(response.json(), gene)
            if response.status_code == 404:
                self._last_resolution_error = ""
                return ""
            self._last_resolution_error = f"MyGene resolution HTTP {response.status_code}"
        except Exception as exc:
            self._last_resolution_error = str(exc)
        return ""

    def resolve_entrez(self, gene: str) -> str:
        """Resolve an exact human symbol to Entrez for HumanBase."""
        try:
            response = self._get(
                "https://mygene.info/v3/query",
                params={
                    "q": gene,
                    "species": "human",
                    "size": 10,
                    "fields": "symbol,entrezgene",
                },
            )
            if response.status_code != 200:
                return ""
            payload = response.json() or {}
            hits = payload.get("hits", []) if isinstance(payload, dict) else []
            for hit in hits if isinstance(hits, list) else []:
                if not isinstance(hit, dict):
                    continue
                symbol = str(hit.get("symbol") or "").upper()
                entrez = hit.get("entrezgene") or hit.get("_id")
                if symbol == str(gene).upper() and str(entrez or "").isdigit():
                    return str(entrez)
            return ""
        except Exception:
            return ""

    def query_gtex(self, gene: str, max_results: int = 12) -> dict:
        """Query the current GTEx Portal v2 reference and median-expression API."""
        try:
            ref = self._get(
                "https://gtexportal.org/api/v2/reference/gene",
                params={"geneId": gene},
            )
            if ref.status_code != 200:
                return self._result("gtex", "error", error=f"reference HTTP {ref.status_code}")
            rows = ref.json().get("data", [])
            if not rows:
                return self._result("gtex", "no_records")
            gencode = str(rows[0].get("gencodeId", ""))
            if not gencode:
                return self._result("gtex", "no_records")
            response = self._get(
                "https://gtexportal.org/api/v2/expression/medianGeneExpression",
                params={"gencodeId": gencode, "datasetId": "gtex_v8"},
            )
            if response.status_code != 200:
                return self._result("gtex", "error", error=f"expression HTTP {response.status_code}")
            records = []
            for row in (response.json().get("data", []) or [])[:max_results]:
                if not isinstance(row, dict):
                    continue
                tissue = row.get("tissueSiteDetailId", "")
                if tissue:
                    records.append({
                        "gene": gene,
                        "tissue": tissue,
                        "median_expression": row.get("median"),
                        "unit": row.get("unit", "TPM"),
                    })
            return self._result(
                "gtex",
                "ok" if records else "no_records",
                records,
                {"gencode_id": gencode, "dataset": "gtex_v8"},
            )
        except Exception as exc:
            return self._result("gtex", "error", error=str(exc))

    def query_hpa(self, gene: str, max_results: int = 12) -> dict:
        """Query the Human Protein Atlas single-entry JSON endpoint."""
        try:
            ensembl = self.resolve_ensembl(gene)
            if not ensembl:
                if self._last_resolution_error:
                    return self._result("hpa", "error", error=self._last_resolution_error)
                return self._result("hpa", "no_records")
            response = self._get(f"https://www.proteinatlas.org/{ensembl}.json")
            if response.status_code == 404:
                return self._result("hpa", "no_records")
            if response.status_code != 200:
                return self._result("hpa", "error", error=f"HTTP {response.status_code}")
            payload = response.json()
            records = []
            for key in (
                "Gene", "Gene description", "Protein class", "RNA tissue specificity",
                "Protein expression", "Subcellular location",
            ):
                value = payload.get(key)
                if isinstance(value, list):
                    value = "; ".join(str(item) for item in value[:max_results])
                if value not in (None, "", [], {}):
                    records.append({"field": key, "value": value})
            return self._result(
                "hpa",
                "ok" if records else "no_records",
                records,
                {"ensembl_id": ensembl, "gene": payload.get("Gene", gene)},
            )
        except Exception as exc:
            return self._result("hpa", "error", error=str(exc))

    def query_opentargets(self, gene: str, max_results: int = 8) -> dict:
        """Query Open Targets Platform v4 GraphQL by a resolved Ensembl ID."""
        try:
            ensembl = self.resolve_ensembl(gene)
            if not ensembl:
                if self._last_resolution_error:
                    return self._result("opentargets", "error", error=self._last_resolution_error)
                return self._result("opentargets", "no_records")
            query = """
            query ($gene: String!) {
              target(ensemblId: $gene) {
                id
                approvedSymbol
                associatedDiseases(page: {index: 0, size: 8}) {
                  rows { disease { name id } score }
                }
              }
            }
            """
            response = self._post(
                "https://api.platform.opentargets.org/api/v4/graphql",
                json={"query": query, "variables": {"gene": ensembl}},
            )
            if response.status_code != 200:
                return self._result("opentargets", "error", error=f"HTTP {response.status_code}")
            payload = response.json()
            if payload.get("errors"):
                return self._result("opentargets", "error", error=str(payload["errors"][:2]))
            target = (payload.get("data", {}) or {}).get("target") or {}
            if not target:
                return self._result("opentargets", "no_records", fields={"ot_ensembl": ensembl})
            records = []
            for row in ((target.get("associatedDiseases") or {}).get("rows") or [])[:max_results]:
                disease = row.get("disease") or {}
                if disease.get("name"):
                    records.append({
                        "name": disease.get("name"),
                        "id": disease.get("id", ""),
                        "score": round(float(row.get("score") or 0), 4),
                    })
            return self._result(
                "opentargets",
                "ok" if records else "no_records",
                records,
                {"ot_ensembl": ensembl, "approved_symbol": target.get("approvedSymbol", gene)},
            )
        except Exception as exc:
            return self._result("opentargets", "error", error=str(exc))

    def query_alliance(self, gene: str, max_results: int = 12) -> dict:
        """Query Alliance's maintained cross-species search endpoint."""
        try:
            response = self._get(
                "https://www.alliancegenome.org/api/search",
                params={"q": gene},
            )
            if response.status_code != 200:
                return self._result("alliance", "error", error=f"HTTP {response.status_code}")
            hits = response.json().get("results", [])
            records = []
            for hit in hits if isinstance(hits, list) else []:
                if not isinstance(hit, dict):
                    continue
                symbol = str(hit.get("symbol", ""))
                species = str(hit.get("species", ""))
                if symbol and species:
                    records.append({
                        "symbol": symbol,
                        "species": species,
                        "name": hit.get("name", ""),
                        "id": hit.get("id", ""),
                        "category": hit.get("category", ""),
                    })
            return self._result("alliance", "ok" if records else "no_records", records[:max_results])
        except Exception as exc:
            return self._result("alliance", "error", error=str(exc))

    def query_humanbase(self, gene: str, context_hint: str = "", max_results: int = 20) -> dict:
        """Query HumanBase's current documented REST API.

        HumanBase uses Entrez IDs in its gene and tissue-network endpoints.  A
        breast/BRCA context is mapped to the maintained mammary-gland network;
        other contexts still receive the current gene prediction endpoint.
        """
        entrez = self.resolve_entrez(gene)
        if not entrez:
            return self._result("humanbase", "no_records", error="No exact human Entrez mapping")
        base = "https://humanbase.io/api"
        try:
            gene_response = self._get(f"{base}/genes/{quote(entrez, safe='')}/")
            if gene_response.status_code != 200:
                return self._result("humanbase", "error", error=f"gene HTTP {gene_response.status_code}")
            gene_payload = gene_response.json() or {}
            records = [{"type": "gene", **gene_payload}] if isinstance(gene_payload, dict) else []
            term_records = []
            prediction_response = self._get(
                f"{base}/genes/{quote(entrez, safe='')}/predictions/",
                params={"database": "gene-ontology-bp", "score_cutoff": 0.75},
            )
            if prediction_response.status_code == 200:
                predictions = self._payload_rows(prediction_response.json(), max_results=max_results)
                for item in predictions[:max_results]:
                    if not isinstance(item, dict):
                        continue
                    term = item.get("term") or {}
                    term_records.append({
                        "type": "predicted_term",
                        "term": term.get("title") or term.get("identifier", ""),
                        "score": item.get("score", ""),
                        "database": (term.get("database") or {}).get("name", "Gene Ontology (BP)"),
                    })
            records.extend(term_records)

            context = str(context_hint or "").strip().lower()
            network_slugs = []
            if any(term in context for term in ("breast", "brca", "mammary")):
                # The current v3 endpoint is attempted first; the v1 slug is
                # a maintained fallback because some deployments do not yet
                # serve every v3 context through the network worker.
                network_slugs = ["mammary-gland-v3", "mammary-gland"]
            network_payload = None
            network_slug = ""
            for slug in network_slugs:
                network_response = self._get(
                    f"{base}/integrations/{slug}/network/",
                    params={"entrez": entrez, "node_size": min(12, max_results)},
                )
                if network_response.status_code == 200:
                    try:
                        network_payload = network_response.json() or {}
                        network_slug = slug
                        break
                    except ValueError:
                        continue
            network_records = []
            if isinstance(network_payload, dict):
                for row in self._payload_rows(network_payload.get("genes", []), max_results=max_results):
                    if isinstance(row, dict):
                        symbol = row.get("standard_name") or row.get("systematic_name") or row.get("entrez")
                        if symbol and str(row.get("entrez")) != entrez:
                            network_records.append({
                                "type": "tissue_network_neighbor",
                                "context": network_slug,
                                "partner": symbol,
                                "entrez": row.get("entrez"),
                            })
                edges = network_payload.get("edges", [])
                for edge in edges[:max_results] if isinstance(edges, list) else []:
                    if isinstance(edge, dict):
                        network_records.append({"type": "tissue_network_edge", "context": network_slug, **edge})
            records.extend(network_records[:max_results])

            fields = {
                "humanbase_entrez": entrez,
                "humanbase_context": network_slug or context or "gene-level predictions",
                "humanbase_networks": [
                    f"{item.get('partner')} ({item.get('context')})"
                    for item in network_records
                    if item.get("partner")
                ][:max_results],
                "humanbase_terms": [
                    f"{item.get('term')} (score={item.get('score')})"
                    for item in term_records if item.get("term")
                ][:max_results],
            }
            return self._result("humanbase", "ok" if records else "no_records", records, fields)
        except Exception as exc:
            return self._result("humanbase", "error", error=str(exc))

    def query_clinicaltrials(self, gene: str, context_hint: str = "", max_results: int = 12) -> dict:
        """Query ClinicalTrials.gov API v2 for gene- and disease-relevant studies."""
        context_terms = self._disease_context_terms(context_hint)
        # Only pass recognised disease aliases to ClinicalTrials.gov.  A
        # generic dataset description (for example, "expression profile /
        # selected_genes / statistical outputs ...") is not a valid clinical
        # query and can make the API reject an otherwise valid gene query as
        # "Too complicated query" (HTTP 400).  An empty disease context must
        # therefore remain a gene-only query.
        query_context = " ".join(context_terms[:3])
        query = " ".join(part for part in (str(gene).strip(), query_context) if part)
        try:
            with self._clinicaltrials_gate:
                response = self._get(
                    "https://clinicaltrials.gov/api/v2/studies",
                    params={
                        "query.term": query,
                        "pageSize": max(1, min(int(max_results), 100)),
                    },
                )
                # A disease alias can still be rejected for an unusual gene
                # token.  Retry the same endpoint with the gene alone before
                # reporting a transport/query error; a valid no-hit response
                # is biological absence, not endpoint failure.
                if response.status_code in {400, 414} and query != str(gene).strip():
                    response = self._get(
                        "https://clinicaltrials.gov/api/v2/studies",
                        params={
                            "query.term": str(gene).strip(),
                            "pageSize": max(1, min(int(max_results), 100)),
                        },
                    )
                    query = str(gene).strip()
            if response.status_code != 200:
                return self._result("clinicaltrials", "error", error=f"HTTP {response.status_code}")
            payload = response.json() or {}
            records = []
            for study in (payload.get("studies", []) if isinstance(payload, dict) else [])[:max_results]:
                protocol = study.get("protocolSection", {}) if isinstance(study, dict) else {}
                ident = protocol.get("identificationModule", {}) or {}
                status = protocol.get("statusModule", {}) or {}
                conditions = protocol.get("conditionsModule", {}) or {}
                design = protocol.get("designModule", {}) or {}
                sponsor = protocol.get("sponsorCollaboratorsModule", {}) or {}
                nct = ident.get("nctId", "")
                title = ident.get("briefTitle", "")
                if not nct and not title:
                    continue
                records.append({
                    "nct_id": nct,
                    "title": title,
                    "status": status.get("overallStatus", ""),
                    "conditions": conditions.get("conditions", [])[:8],
                    "phases": design.get("phases", []),
                    "sponsor": (sponsor.get("leadSponsor") or {}).get("name", ""),
                    "url": f"https://clinicaltrials.gov/study/{nct}" if nct else "",
                })
            fields = {
                "clinicaltrials_query": query,
                "clinicaltrials_studies": [
                    f"{item.get('nct_id')}: {item.get('title')} [{item.get('status') or 'status unavailable'}]"
                    + (f" | {', '.join(item.get('conditions') or [])}" if item.get("conditions") else "")
                    for item in records
                ],
            }
            if context_terms:
                matched = []
                for record in records:
                    haystack = " ".join(
                        [str(record.get("title") or "")]
                        + [str(item) for item in (record.get("conditions") or [])]
                    ).lower()
                    if any(term in haystack for term in context_terms):
                        matched.append(record)
                records = matched
                fields["clinicaltrials_studies"] = [
                    f"{item.get('nct_id')}: {item.get('title')} [{item.get('status') or 'status unavailable'}]"
                    + (f" | {', '.join(item.get('conditions') or [])}" if item.get("conditions") else "")
                    for item in records
                ]
            return self._result("clinicaltrials", "ok" if records else "no_records", records, fields)
        except Exception as exc:
            return self._result("clinicaltrials", "error", error=str(exc))

    def query_clinvar(self, gene: str, max_results: int = 12) -> dict:
        """Query NCBI ClinVar through the shared, rate-limited E-utilities client.

        ClinVar is an NCBI endpoint rather than a generic JSON annotation
        endpoint.  Keep the adapter here as well as in the production
        orchestrator so diagnostics, direct source probes, and Agent RAG all
        exercise the same verified query path.
        """
        gene = str(gene or "").strip()
        if not gene:
            return self._result("clinvar", "no_records")
        try:
            from api.pubmed_api import PubMed_API

            client = PubMed_API()
            retmax = max(1, min(int(max_results), 20))
            search = client._request(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                params={
                    "db": "clinvar",
                    "term": (
                        f"{gene}[gene] AND (pathogenic[clinical significance] "
                        "OR likely pathogenic[clinical significance])"
                    ),
                    "retmax": retmax,
                    "retmode": "json",
                    "sort": "relevance",
                },
            )
            ids = (search.json() or {}).get("esearchresult", {}).get("idlist", [])
            ids = [str(item) for item in ids[:retmax] if str(item).strip()]
            if not ids:
                return self._result("clinvar", "no_records", fields={"clinvar_variants": []})

            summary = client._request(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                params={
                    "db": "clinvar",
                    "id": ",".join(ids),
                    "retmode": "json",
                },
            )
            payload = summary.json() or {}
            result = payload.get("result", {}) if isinstance(payload, dict) else {}
            records = []
            variants = []
            for variant_id in ids:
                item = result.get(str(variant_id), {}) or {}
                clinical = item.get("clinical_significance", {}) or {}
                significance = str(clinical.get("description") or "").strip()
                traits = item.get("trait_set") or []
                condition = ""
                if traits and isinstance(traits[0], dict):
                    condition = str(traits[0].get("trait_name") or "").strip()
                title = str(item.get("title") or "").strip()
                display = condition or title[:160]
                if significance:
                    display = f"{display} ({significance})" if display else significance
                if not display:
                    continue
                record = {
                    "variant_id": variant_id,
                    "title": title,
                    "condition": condition,
                    "clinical_significance": significance,
                    "summary": display,
                }
                records.append(record)
                variants.append(display)
            fields = {
                "clinvar_query": gene,
                "clinvar_variants": variants[:retmax],
            }
            return self._result(
                "clinvar",
                "ok" if records else "no_records",
                records,
                fields,
            )
        except Exception as exc:
            return self._result("clinvar", "error", error=str(exc))

    def query_custom(self, source: str, gene: str, definition: Dict[str, Any],
                     context_hint: str = "", max_results: int = 20) -> dict:
        """Query a user-defined HTTP JSON source using a bounded adapter."""
        source = str(source or "").strip().lower()
        if not isinstance(definition, dict):
            return self._result(source, "needs_configuration", error="Custom source definition is missing")
        query = " ".join(part for part in (str(gene).strip(), str(context_hint or "").strip()) if part)
        try:
            url = self._template_value(definition.get("url_template", ""), gene, query, context_hint)
            headers = dict(definition.get("headers") or {})
            method = str(definition.get("method") or "GET").upper()
            has_placeholder = any(marker in str(definition.get("url_template", "")) for marker in ("{gene", "{query", "{context"))
            params = {}
            if not has_placeholder:
                gene_param = str(definition.get("gene_param") or "gene")
                query_param = str(definition.get("query_param") or "query")
                context_param = str(definition.get("context_param") or "context")
                if gene_param:
                    params[gene_param] = gene
                if query_param and query_param != gene_param:
                    params[query_param] = query
                if context_hint and context_param not in params:
                    params[context_param] = context_hint
            if method == "POST":
                body = definition.get("body_template") or {
                    str(definition.get("gene_param") or "gene"): gene,
                    str(definition.get("query_param") or "query"): query,
                }
                body = self._template_value(body, gene, query, context_hint)
                response = self._post(url, json=body, headers=headers, timeout=int(definition.get("timeout") or self.timeout))
            else:
                response = self._get(url, params=params, headers=headers, timeout=int(definition.get("timeout") or self.timeout))
            if response.status_code in {401, 403}:
                return self._result(source, "needs_configuration", error=f"HTTP {response.status_code}")
            if response.status_code != 200:
                return self._result(source, "error", error=f"HTTP {response.status_code}")
            try:
                payload = response.json()
            except ValueError as exc:
                return self._result(source, "error", error=f"response is not JSON: {exc}")
            extracted = self._extract_path(payload, str(definition.get("records_path") or ""))
            if extracted is None:
                extracted = payload
            records = self._payload_rows(extracted, max_results=max_results)
            fields = {"records": records[:max_results], "query": query}
            return self._result(source, "ok" if records else "no_records", records, fields)
        except Exception as exc:
            return self._result(source, "error", error=str(exc))

    def query_biogrid(self, gene: str, max_results: int = 30) -> dict:
        """Return disabled state; BioGRID is no longer an active source."""
        return self._result(
            "biogrid",
            "unavailable",
            error="BioGRID has been removed from the active source policy.",
        )

        # Kept below only for backwards-compatible source snapshots; it is
        # unreachable and must not be used by the active RAG path.
        api_key = os.environ.get("E2SEQ_BIOGRID_API_KEY", "").strip()
        if not api_key:
            try:
                from e2seq.utils import get_config
                api_key = str(get_config().api.biogrid_api_key or "").strip()
            except Exception:
                api_key = ""
        if not api_key or api_key in {"biological", "demo", "1647cceb86ebd3fb64caf6e20048e6bc"}:
            return self._result("biogrid", "needs_configuration", error="A valid BioGRID access key is required")
        try:
            response = self._get(
                "https://webservice.thebiogrid.org/interactions",
                params={
                    "accessKey": api_key,
                    "geneList": gene,
                    "organism": "9606",
                    "max": max_results,
                    "format": "json",
                },
            )
            if response.status_code in {401, 403}:
                return self._result("biogrid", "needs_configuration", error=f"HTTP {response.status_code}")
            if response.status_code != 200:
                return self._result("biogrid", "error", error=f"HTTP {response.status_code}")
            records = []
            payload = response.json()
            for hit in list(payload.values())[:max_results] if isinstance(payload, dict) else []:
                if not isinstance(hit, dict):
                    continue
                a = hit.get("OFFICIAL_SYMBOL_A", "")
                b = hit.get("OFFICIAL_SYMBOL_B", "")
                partner = b if a.upper() == gene.upper() else a
                if partner and partner.upper() != gene.upper():
                    records.append({
                        "partner": partner,
                        "experimental_system": hit.get("EXPERIMENTAL_SYSTEM", ""),
                        "pmid": hit.get("PUBMED_ID", ""),
                        "interaction_id": hit.get("BIOGRID_INTERACTION_ID", ""),
                    })
            return self._result("biogrid", "ok" if records else "no_records", records)
        except Exception as exc:
            return self._result("biogrid", "error", error=str(exc))

    def query_cbioportal(self, gene: str, max_results: int = 1) -> dict:
        """Query cBioPortal's public gene endpoint."""
        try:
            response = self._get(f"https://www.cbioportal.org/api/genes/{quote(gene, safe='')}")
            if response.status_code == 404:
                return self._result("cbioportal", "no_records")
            if response.status_code != 200:
                return self._result("cbioportal", "error", error=f"HTTP {response.status_code}")
            payload = response.json()
            if not payload:
                return self._result("cbioportal", "no_records")
            return self._result("cbioportal", "ok", [payload], {"hugo_symbol": payload.get("hugoGeneSymbol", gene)})
        except Exception as exc:
            return self._result("cbioportal", "error", error=str(exc))

    @staticmethod
    def _parse_tsv(text: str) -> List[dict]:
        lines = [line for line in text.splitlines() if line and not line.startswith("#")]
        if not lines:
            return []
        reader = csv.reader(io.StringIO("\n".join(lines)), delimiter="\t")
        rows = list(reader)
        if not rows:
            return []
        header = rows[0]
        has_header = any("source" in str(item).lower() for item in header)
        if has_header:
            return [dict(zip(header, row)) for row in rows[1:] if row]
        return [{"field_0": row[0], "field_1": row[1], "field_2": row[2] if len(row) > 2 else ""} for row in rows]

    def query_omnipath(self, gene: str, max_results: int = 30) -> dict:
        """Query OmniPath's gene-symbol-aware interaction endpoint."""
        try:
            response = self._get(
                "https://omnipathdb.org/interactions",
                params={
                    "genesymbols": "yes",
                    "partners": gene,
                    "fields": "sources,references",
                    "limit": max_results,
                },
                headers={"Accept": "text/plain"},
            )
            if response.status_code != 200:
                return self._result("omnipath", "error", error=f"HTTP {response.status_code}")
            rows = self._parse_tsv(response.text)[:max_results]
            records = []
            for row in rows:
                source_symbol = row.get("source_genesymbol", "")
                target_symbol = row.get("target_genesymbol", "")
                if source_symbol or target_symbol:
                    records.append({
                        "source": source_symbol or row.get("source", ""),
                        "target": target_symbol or row.get("target", ""),
                        "is_directed": row.get("is_directed", ""),
                        "is_stimulation": row.get("is_stimulation", ""),
                        "is_inhibition": row.get("is_inhibition", ""),
                        "sources": row.get("sources", ""),
                        "references": row.get("references", ""),
                    })
            return self._result("omnipath", "ok" if records else "no_records", records)
        except Exception as exc:
            return self._result("omnipath", "error", error=str(exc))

    def query_intact(self, gene: str, max_results: int = 30) -> dict:
        """Query IntAct through PSICQUIC with the EBI Search fallback.

        EMBL-EBI currently redirects the legacy HTTPS PSICQUIC route to an
        HTTP URL that is unavailable from many networks.  The EBI Search
        ``intact`` domain is the maintained HTTPS route and still returns
        IntAct interaction entries, so a redirect/transport failure is not
        reported as a false biological zero.
        """
        try:
            url = (
                "https://www.ebi.ac.uk/Tools/webservices/psicquic/intact/"
                f"webservices/current/search/query/{quote(gene, safe='')}"
            )
            response = self._get(
                url,
                params={"format": "tab25", "firstResult": 0, "maxResults": max_results},
                headers={"Accept": "text/plain"},
                # EBI's legacy route currently redirects HTTPS -> HTTP.  Stop
                # at the redirect and use the maintained HTTPS fallback below.
                allow_redirects=False,
            )
            if response.status_code != 200:
                raise RuntimeError(f"PSICQUIC HTTP {response.status_code}")
            rows = self._parse_tsv(response.text)[:max_results]
            records = []
            for row in rows:
                a = row.get("field_0", "") or row.get("#ID(s) interactor A", "")
                b = row.get("field_1", "") or row.get("Alt. ID(s) interactor B", "")
                if a or b:
                    records.append({
                        "interactor_a": a,
                        "interactor_b": b,
                        "interaction": row.get("field_2", ""),
                        "source": "IntAct/PSICQUIC",
                    })
            return self._result("intact", "ok" if records else "no_records", records)
        except Exception as exc:
            # Maintained HTTPS fallback: EBI Search's IntAct domain returns
            # interaction entries as JSON and remains usable when PSICQUIC is
            # redirected or temporarily unavailable.
            try:
                fallback = self._get(
                    "https://www.ebi.ac.uk/ebisearch/ws/rest/intact",
                    params={
                        "query": str(gene),
                        "format": "json",
                        # A small ID-only page is substantially more stable
                        # than asking the EBI Search service to materialize a
                        # large description page during a parallel cohort
                        # query.  The returned interaction ID is an auditable
                        # IntAct record and can be followed in the portal.
                        "size": 1,
                    },
                    headers={"Accept": "application/json"},
                    timeout=min(int(self.timeout), 15),
                )
                if fallback.status_code != 200:
                    return self._result(
                        "intact",
                        "error",
                        error=f"PSICQUIC: {exc}; EBI Search HTTP {fallback.status_code}",
                    )
                payload = fallback.json() if fallback.text else {}
                records = []
                for entry in (payload.get("entries") or [])[:max_results]:
                    if not isinstance(entry, dict):
                        continue
                    fields = entry.get("fields") or {}
                    names = fields.get("name") or []
                    descriptions = fields.get("description") or []
                    name = str(names[0] if names else entry.get("id") or "").strip()
                    description = "; ".join(str(item).strip() for item in descriptions if str(item).strip())
                    interaction_id = str(entry.get("id") or "").strip()
                    if not name and not description:
                        continue
                    if not names and not descriptions:
                        participants = [str(gene).strip(), interaction_id]
                    else:
                        participants = [part.strip() for part in name.split("-", 1)]
                    records.append({
                        "interactor_a": participants[0] if participants else name,
                        "interactor_b": participants[1] if len(participants) > 1 else interaction_id,
                        "interaction": description or (name if name != interaction_id else f"IntAct interaction entry {interaction_id}"),
                        "interaction_id": interaction_id,
                        "source": "IntAct via EBI Search",
                    })
                return self._result("intact", "ok" if records else "no_records", records)
            except Exception as fallback_exc:
                return self._result(
                    "intact",
                    "error",
                    error=f"PSICQUIC: {exc}; EBI Search: {fallback_exc}",
                )

    def query(self, source: str, gene: str, max_results: int = 20,
              context_hint: str = "", custom_source: Optional[Dict[str, Any]] = None) -> dict:
        """Dispatch a source query by its stable source identifier."""
        source = str(source).lower()
        if custom_source is not None:
            return self.query_custom(
                source, gene, custom_source,
                context_hint=context_hint,
                max_results=max_results,
            )
        handlers = {
            "gtex": self.query_gtex,
            "hpa": self.query_hpa,
            "opentargets": self.query_opentargets,
            "alliance": self.query_alliance,
            "humanbase": self.query_humanbase,
            "clinicaltrials": self.query_clinicaltrials,
            "clinvar": self.query_clinvar,
            "cbioportal": self.query_cbioportal,
            "omnipath": self.query_omnipath,
            "intact": self.query_intact,
        }
        handler = handlers.get(source)
        if handler is None:
            return self._result(source, "unavailable", error="No verified adapter")
        if source in {"humanbase", "clinicaltrials"}:
            return handler(gene, context_hint=context_hint, max_results=max_results)
        return handler(gene, max_results=max_results)
