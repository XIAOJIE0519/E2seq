# lung adenocarcinoma (LUAD) - minimax-m3

- Benchmark system: E2seq + Agent RAG
- Repeat: 7
- Task type: PROGNOSIS
- Tissue / sample source: lung adenocarcinoma tumor tissue
- Comparison or endpoint: overall survival (OS)
- Answer input cohort: Discovery/Core only
- Selected items: 100
- Input fields: gene name, effect size (log2FC/HR), P value, FDR
- E2seq Agent RAG: enabled
- Conversation memory: disabled
- Thinking mode: disabled
- Held-out validation data in prompt/RAG: no
- Model API: MiniMax / minimax-m3
- Message SHA-256: a2c9355177479f23c6c81afe1b39ba697ac131cc344bb83120b98e2c6bbfee49
- Response HTTP status: 200
- Prompt tokens: 42786
- Completion tokens: 21935
- Reasoning tokens: 4920
- Total tokens: 64721
- API requests reported: 3
- Elapsed seconds: 78.245
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 957.651
- Question handoff seconds: 970.897
- Final benchmark system: E2seq; file rank 5/5; original repeat 7; model vendor: MiniMax

---
<think>Let me carefully analyze this dataset. The user has provided a prognostic analysis (overall survival in lung adenocarcinoma) with HR values, P values, and FDR values for 100 selected genes.

**Critical observations about the data quality:**

1. **Extreme HR values**: Many genes have HR values of ~5.18e+21 (which is effectively infinity in Cox regression), or other astronomically large numbers (10^9, 10^11, etc.). These are clearly degenerate Cox model estimates, almost certainly from complete separation - where a gene's expression perfectly predicts survival outcomes (all events in one group, none in the other). P=0 and FDR=0 for nearly all of these.

2. **One outlier with a sensible HR**: TCP10L3 has HR=1.929e-22, which is essentially HR≈0, meaning it is strongly protective. This is also a degenerate estimate.

4. **Y_RNA has direction-conflict rows=163**: This means the gene has 163 rows with conflicting direction annotations, suggesting it's a multi-mapped or ambiguous probe/transcript.

5. **Bulk of "realistic" HRs**: Only about 30 genes have HRs in a plausible range (0.2-1.5):
- RBMXP1: HR=0.21 (protective)
- PITX3: HR=1.43 (risk)
- DKK1: HR=1.48 (risk)
- LINC01312: HR=1.36 (risk)
- LINC02178: HR=1.30 (risk)
- VAX1: HR=1.33 (risk)
- CTD-2066L21.1/.2: HR~1.23-1.27 (risk)
- TLE1: HR=1.48 (risk)
- LINC01910: HR=1.31 (risk)
- LINC02323: HR=1.37 (risk)
- CRNDE: HR=0.72 (protective)
- LINC02802: HR=1.33 (risk)
- ITGB1-DT: HR=1.30 (risk)
- CREG2: HR=1.33 (risk)
- OR10J6P: HR=1.29 (risk)
- RP11-1057N3.2: HR=1.17 (risk)
- LOC105375754: HR=1.31 (risk)
- RP11-96B2.1: HR=1.29 (risk)
- LDLRAD3: HR=1.42 (risk)
- KRT6A: HR=1.39 (risk)
- RP11-438B23.2: HR=1.31 (risk)
- FUT4: HR=1.40 (risk)
- RHOF: HR=1.40 (risk)
- RP11-58O9.2: HR=1.35 (risk)
- LINC00707: HR=1.32 (risk)
- RHCG: HR=1.29 (risk)
- CMAHP: HR=0.71 (protective)
- RGS20: HR=1.35 (risk)

6. **Gene composition**: The majority of genes are:
- lncRNAs/pseudogenes (LINC*, RP11-*, LOC*, CTD-*)
- Y-chromosome or testis-specific genes (RBMY1F, FAM9A, TCP10L3, TEX13A, TTTY4C, CDY10P, RBMY2AP, USP9YP3, VENTXP7)
- Mitochondrial pseudogenes (MTND1P1, ATP5PBP2)
- RNA-related (Y_RNA, RNY1P3, RNU6-78P, RNU7-99P, MIR509-1, MIR3924, MIR8065, MIR6862-1)
- Processed pseudogenes (HMGN2P39, RAP1BP2, DRAXINP1, ATG4AP1, AMMECR1LP1, RBMXP1, DIMT1P1, DNM1P49)

This is a strong signal of biological noise / artifact. Y-chromosome genes are likely artifacts from male samples, and many lncRNAs/pseudogenes may be passenger signals or noise.

**The pathway annotation**: GO and KEGG annotations point to Wnt signaling pathway (DKK1 is a Wnt antagonist, TLE1 is a Wnt/TLE repressor). This suggests a genuine Wnt-related signal in the more realistic HR genes.

Let me build the interpretation:

1. **Data quality warning**: The vast majority of "top hits" have degenerate HR estimates (HR ≈ 10^21) due to complete separation in Cox regression, P=0, FDR=0. These are not biologically meaningful effect sizes. Only ~30 genes have plausible HR estimates.

2. **The biologically interpretable signal**: Looking at genes with HR in the 0.2-1.5 range:
   - Risk-associated: PITX3, DKK1, TLE1, KRT6A, FUT4, RHOF, RGS20, LDLRAD3, VAX1, several lncRNAs
   - Protective: RBMXP1, CRNDE, CMAHP

3. **Core programs I can identify**:
   - Wnt signaling / developmental transcription factors (DKK1, TLE1, PITX3, VAX1) - risk-associated
   - Cell migration / Rho GTPase signaling (RHOF, RGS20)
   - Glycosylation (FUT4, KRT6A keratin-related)
   - Most of the remaining signal is noise/artifacts (Y-chromosome genes, pseudogenes, lncRNAs)

4. **Key genes**: DKK1, TLE1, PITX3, RHOF, RGS20, FUT4, KRT6A, ITGB1-DT, CRNDE, RBMXP1

5. **Validation priorities**: DKK1/TLE1/PITX3 as Wnt axis markers; RHOF as Rho GTPase target; lncRNA ITGB1-DT/CRNDE as biomarkers; and most importantly, **the need for external validation and filtering of degenerate estimates**.

Let me structure the response.</think>

# Prognostic Transcriptomic Interpretation: LUAD Overall Survival

## Data-Quality Warning (must be read first)

The uploaded survival table is **statistically degenerate**. Of the 100 "selected" genes, ~70 have HR values around 5.18 × 10²¹ and many others have HR values of 10⁶–10¹⁶; all carry P = 0 and FDR = 0. These are not biologically plausible effect sizes. They are the canonical signature of **complete/quasi-complete separation in a Cox model**: in at least one expression stratum, every patient experiences the same event pattern (e.g., 0 events in one group), so the partial-likelihood coefficient diverges to ±∞. The Cox Wald statistic then rounds P to machine zero. These rows are *artefacts of model fitting*, not evidence of effect magnitude, and they cannot be interpreted as hazard ratios in any clinically meaningful sense.

A second large block consists of Y-chromosome / testis-restricted transcripts (RBMY1F, FAM9A, TEX13A, TTY4C, USP9YP3, VENTXP7, CDY10P, RBMY2AP), unprocessed-locus lncRNAs (LINC00448, RP11-*, CTD-*), short-RNA pseudogenes (Y_RNA with 163 conflicting-direction rows, RNY1P3, RNU6-78P, RNU7-99P, MIR509-1/3924/8065/6862-1), and nuclear/mitochondrial pseudogenes (HMGN2P39, RAP1BP2, DRAXINP1, ATG4AP1, AMMECR1LP1, MTND1P1, DIMT1P1, DNM1P49, ATP5PBP2, RBMXP1). In a Cox model of bulk RNA from a tumour with mixed sex/genotype background, such features are dominated by **technical and composition noise** rather than tumour biology. They should not be promoted to prognostic mechanisms.

**Only the ~30 genes with HRs in the 0.2–1.5 range carry interpretable effect estimates**, and even those should be treated as hypothesis-generating because **no independent cohort replication statistic is provided** (external summary: 0/0 concordant, 0/0 significant). The literature context below is used to assess plausibility, not as replication.

---

## 1. Overall Biological Interpretation

Within the subset of genes that have well-defined Cox estimates, the prognostic signal in LUAD converges on three coherent themes:

- A **Wnt-pathway / developmental-transcription-factor axis** that leans *unfavourable* (DKK1 ↑HR, TLE1 ↑HR, PITX3 ↑HR, VAX1 ↑HR).
- A **Rho-GTPase / cytoskeletal migration module** that also trends *unfavourable* (RHOF ↑HR, RGS20 ↑HR).
- A **glycosylation / epithelial-keratin module** that is *unfavourable* (FUT4 ↑HR, KRT6A ↑HR), with one *favourable* protective candidate (CMAHP, related to the ABO/Sda antigen).

The vast majority of the remaining "top" features are degenerate HRs from pseudogenes, Y-linked transcripts, and uncharacterised lncRNAs. They swamp the analysis numerically (96 of 100 genes nominally "risk-associated") but contribute essentially no verifiable biology.

Net interpretation: the current dataset's *interpretable* prognostic biology is dominated by a developmental-Wnt signature with secondary cytoskeletal and glycosylation contributions; the rest is artefactual and should be filtered before any downstream use.

---

## 2. Core Biological Programs (≤5)

### Program 1 — Wnt / developmental transcription-factor axis (direction: **risk / unfavourable**)
- Supporting genes: **DKK1** (HR = 1.475, FDR = 3.55 × 10⁻⁷), **TLE1** (HR = 1.484, FDR = 2.46 × 10⁻⁵), **PITX3** (HR = 1.429, FDR = 3.49 × 10⁻¹¹), **VAX1** (HR = 1.335, FDR = 9.25 × 10⁻⁶).
- Pathway mapping: GO Regulation of Wnt signalling (GO:0030111), Planar Cell Polarity Pathway (GO:2000096), Cell Junction Disassembly (GO:0150146); KEGG Wnt signalling pathway.
- Why these genes fit: DKK1 is a secreted Wnt antagonist whose overexpression has been linked to β-catenin-independent/non-canonical Wnt activity and poor outcome in several solid tumours (question-specific PMID 40124684 notes DKK1-family Wnt context in NSCLC prognosis). TLE1 is a Groucho/TLE co-repressor that restrains canonical Wnt/TCF targets and is itself regulated by Wnt; its prognostic role in LUAD is plausible but not equivalent to canonical pathway activation. PITX3 and VAX1 are paired-like homeodomain transcription factors with established roles in tissue specification rather than direct Wnt readout, but recurrent GO/Reactome mapping groups them with Wnt/planar-cell-polarity terms in the retrieved annotations.
- Evidence: Direct HR in dataset (all four pass FDR < 10⁻⁴); pathway/ontology annotation (Reactome, QuickGO); one concordant NSCLC-ferritinophagy context reference (PMID 40124684) for DKK1-related Wnt axis in NSCLC.
- Strength: only four genes, but the signal is internally consistent (HR ~1.3–1.5, all FDR < 10⁻⁴) and matches a known LUAD-relevant pathway.
- Limitations: TLE1 and DKK1 can move in opposite biological directions depending on cellular context; "Wnt signalling" here is inferred from annotation overlap, not from a unified transcriptional programme; no independent cohort statistic.

### Program 2 — Rho-GTPase / actin-driven migration (direction: **risk / unfavourable**)
- Supporting genes: **RHOF** (HR = 1.403, FDR = 4.00 × 10⁻⁴), **RGS20** (HR = 1.352, FDR = 5.79 × 10⁻⁴), with **ITGB1-DT** (HR = 1.302) and **CREG2** (HR = 1.332) as ancillary support (the latter two are context-linked rather than canonical members).
- Pathway mapping: GO actin filament organisation, regulation of small GTPase-mediated signal transduction; Reactome Gα(i)/(z) signalling events.
- Why these genes fit: RHOF is an atypical Rho-family GTPase tied to filopodia formation and migration. STRING interactions connect RHOF with ACTN1 and ARHGAP family proteins, and the QuickGO annotation bundle lists actin-cytoskeleton and small-GTPase regulation as the dominant terms. RGS20 is a GTPase-activator for Gα(i)/Gα(z); Reactome maps it directly onto G-protein signalling. RHOF overexpression has previously been associated with worse survival in AML (PMID 34405015), which is mechanistically transferable to invasive phenotypes.
- Evidence: Direct HR (both genes, FDR < 10⁻³); Reactome/QuickGO annotation; STRING protein-interaction evidence; one disease-context literature record (PMID 34405015, AML).
- Limitations: only two core genes; literature evidence is from a different tumour type; "migration" is inferred, not measured.

### Program 3 — Glycosylation / epithelial-keratin module (direction: **risk / unfavourable** for FUT4, KRT6A; CMAHP is protective)
- Supporting genes: **FUT4** (HR = 1.403, FDR = 2.93 × 10⁻⁴), **KRT6A** (HR = 1.390, FDR = 2.78 × 10⁻⁴), **CMAHP** (HR = 0.706, FDR = 5.77 × 10⁻⁴, *protective*).
- Pathway mapping: Mannose-type O-glycan biosynthesis (KEGG); Glycosphingolipid biosynthesis (KEGG); protein-binding molecular function.
- Why these genes fit: FUT4 is an α-1,3-fucosyltransferase; STRING shows it interacts with B3GNT3 and B4GALT1, two glycosylation enzymes, consistent with altered cell-surface glycan signatures in LUAD. KRT6A is a stress/regeneration keratin whose upregulation is associated with squamous/squamoid features. CMAHP is a pseudogenised version of a CMP-N-acetylneuraminate hydroxylase; its protective HR (0.71) is opposite in direction to FUT4/KRT6A, but its mechanism here is ambiguous because the locus is normally non-coding in humans.
- Evidence: Direct HR in dataset; STRING protein-interaction partners; KEGG glycosylation pathway recurrence; one mesenchymal-stem-cell KRT6A literature record (PMID 42216026) in a non-pulmonary context.
- Limitations: FUT4 and KRT6A association with LUAD prognosis is supportable but small-N; CMAHP protective signal is mechanistically unclear because the gene is generally a non-functional relic; KEGG recurrence is "retrieved" rather than enrichment-tested.

### Program 4 — Pseudogene / repetitive-element signal (direction: **apparent risk; mostly artefactual**)
- Supporting "genes": the ~70 entries with HR ≈ 10²¹ and many lncRNAs/pseudogenes (e.g., HMGN2P39, RAP1BP2, DRAXINP1, ATG4AP1, AMMECR1LP1, MTND1P1, MT-ND1 pseudogenes, RBMXP1, DIMT1P1, DNM1P49, RBMY2AP, and 60+ uncharacterised RP11-* / LINC* / CTD-* transcripts).
- Pathway mapping: none biologically coherent; Reactome maps several CTD-* entries into "RNA Pol II CTD phosphorylation and snRNA transcription" purely because the gene symbol begins with "CTD".
- Why these are listed together: they are not a biological programme. Their HRs reflect complete-separation artefacts and the appearance of an enormous risk signature is **driven by fitting instability, not biology**. The protective counter-examples (TCP10L3 HR ≈ 0, RBMXP1 HR = 0.21, CMAHP HR = 0.71) are also best explained by the same numerical pathology in the opposite tail.
- Evidence: Direct numerical evidence (degenerate HRs); Y_RNA appears with 163 direction-conflicting rows, confirming that the underlying transcripts map ambiguously.
- Strength / limitations: This is included as an explicit **negative** programme — i.e., it should *not* be promoted to a finding. Reproducibility and any clinical use requires re-fitting with Firth penalisation, exact logistic regression for sparse strata, or Bayesian shrinkage before claiming prognostic relevance for these loci.

### Program 5 — Sex-chromosome / testis-restricted expression (direction: **artefactual, not prognostic**)
- Supporting "genes": RBMY1F, FAM9A, TEX13A, TTY4C, USP9YP3, VENTXP7, CDY10P, RBMY2AP, plus several Y_RNA-derived entries.
- Pathway mapping: not biologically meaningful; STRING maps FAM9A to ANOS1 and ARSF, two X-linked partners, suggesting these are residual Y-pseudogene alignments.
- Why they are listed: their appearance as "HR ≈ 10²¹" almost certainly reflects complete separation driven by patient sex (any male-only or female-only expression stratum produces a divergent Cox coefficient in sex-imbalanced cohorts). In an unadjusted survival model, these are confounders, not prognostic biomarkers.
- Evidence: Y-chromosome localisation; complete-separation numerics; STRING partner mapping; absence of Reactome pathway membership.
- Limitations: this programme is a **confounding artefact**; it must be controlled for sex at the modelling stage, not interpreted as biology.

---

## 3. Key Genes and Interaction Modules (≤10)

| # | Gene | HR (direction) | Programme | Relationship type |
|---|------|----------------|-----------|--------------------|
| 1 | **DKK1** | 1.475 (risk) | Wnt axis | Functional (secreted Wnt antagonist); not a direct physical interactor with TLE1/PITX3 — pathway co-membership. |
| 2 | **TLE1** | 1.484 (risk) | Wnt axis | Co-repressor of TCF/LEF; pathway co-membership with DKK1; STRING / Reactome co-occurrence, not direct binding. |
| 3 | **PITX3** | 1.429 (risk) | Wnt / developmental TF | Paired-like homeodomain TF; *no* direct interaction evidence with DKK1/TLE1 in the retrieved pack; relationship is putative / pathway co-membership. |
| 4 | **VAX1** | 1.335 (risk) | Wnt / developmental TF | STRING partner ASXL2; otherwise indirect. |
| 5 | **RHOF** | 1.403 (risk) | Rho/migration | STRING interactors ACTN1, ARHGAP1 — *direct physical* (high-confidence STRING, ≥0.7) interaction candidates; QuickGO lists actin/cytoskeleton regulation directly. |
| 6 | **RGS20** | 1.352 (risk) | G-protein signalling | STRING direct interactors: GNAZ (0.95), GNB5 (0.95), SUCLG2 (0.85), GNAI2 (0.82), GNAQ (0.80) — high-confidence direct interactions. |
| 7 | **FUT4** | 1.403 (risk) | Glycosylation | STRING partners B3GNT3, B4GALT1 — direct protein-protein interaction candidates; co-membership in mannose-type O-glycan / glycosphingolipid biosynthesis. |
| 8 | **KRT6A** | 1.390 (risk) | Epithelial/keratin | Independent cytoskeletal role; no strong direct interactors among selected genes; literature support (PMID 42216026) is from a non-pulmonary context. |
| 9 | **ITGB1-DT** | 1.302 (risk) | lncRNA near ITGB1 | Published biomarker candidate in LUAD (PMID 34906142, ITGB1-DT/ARNTL2 axis) and in breast cancer (PMID 37690573); co-expression with ITGB1, not direct interaction. |
| 10 | **CRNDE** | 0.716 (protective) | lncRNA | Not mapped to a coherent programme in the retrieved pack; included because it is one of only four true protective candidates with a non-degenerate HR. Relationship to other selected genes is indirect/literature co-occurrence only. |

**Caveat on the protective side**: only four genes in the entire table have HR < 1 — RBMXP1 (0.21), TCP10L3 (≈0, degenerate), CRNDE (0.72), CMAHP (0.71). RBMXP1 is a processed pseudogene of RBMX; its "protective" HR in a male-skewed sample is again consistent with sex-linked artefact, and CMAHP is a known pseudogene relic. Of the four, **CRNDE is the most defensible protective candidate**, but its independent prognostic value in LUAD has not been demonstrated here (external-cohort statistics not supplied).

---

## 4. Validation Priorities (≤5)

### V1 — **DKK1 / TLE1 / PITX3 axis as a LUAD Wnt prognostic signature** *(Biomarker / Supported hypothesis)*
- **Why prioritise**: four genes, all risk-associated with HR ≈ 1.3–1.5 and FDR ≤ 10⁻⁴, converging on a known LUAD-relevant pathway; one concordant external NSCLC prognostic reference (PMID 40124684).
- **Dataset evidence**: HRs listed above; pathway annotation overlap (GO:0030111, GO:2000096, KEGG Wnt signalling).
- **External support / conflict**: DKK1 has published NSCLC prognostic association (PMID 40124684); TLE1/PITX3/VAX1 LUAD-specific evidence is weaker. The four may not act in a single coherent biological axis.
- **Next step**: Re-fit Cox models in TCGA-LUAD with Firth penalisation, then test the 4-gene score in an independent cohort (e.g., CPTAC-LUAD, MSK-IMPACT, or a published microarray cohort with OS); assess IHC for DKK1 and TLE1 on a TMA.
- **Status**: **Supported hypothesis** — internally consistent within the dataset but not externally replicated here.

### V2 — **RHOF / RGS20 as a migration-and-G-protein prognostic pair** *(Mechanistic hypothesis / Therapeutic target — exploratory)*
- **Why prioritise**: RHOF and RGS20 sit at different nodes (cytoskeletal vs G-protein) of the same motility signalling network, both carry clean HRs and FDR ≤ 5 × 10⁻⁴, and both have high-confidence STRING partners.
- **Dataset evidence**: HRs as listed; Reactome Gα(i)/(z) signalling events for RGS20; QuickGO cytoskeleton/Rho annotations for RHOF; direct STRING interactions with GNAZ, GNB5, GNAI2, GNAQ, ACTN1, ARHGAP1.
- **External support / conflict**: RHOF prognostic evidence exists in AML (PMID 34405015); no LUAD-specific replication in the pack. No existing LUAD-validated drug target.
- **Next step**: qPCR / IHC for RHOF and RGS20 in a LUAD TMA with outcome annotation; functional assays (3D invasion, G-actin/F-actin ratios, RGS-domain inhibition) in LUAD cell lines.
- **Status**: **Exploratory hypothesis**. Drug-target status is *not* implied by the dataset.

### V3 — **ITGB1-DT as a published LUAD lncRNA biomarker** *(Biomarker / Supported hypothesis)*
- **Why prioritise**: ITGB1-DT appears as a risk gene (HR = 1.302, FDR = 1.48 × 10⁻⁴) and there is independent published work (PMID 34906142) proposing an ITGB1-DT/ARNTL2 axis in LUAD, plus a breast-cancer bioinformatics/biomarker paper (PMID 37690573).
- **Dataset evidence**: HR above; selection as one of the non-degenerate risk lncRNAs.
- **External support**: directly aligned with PMID 34906142 (LUAD) and PMID 37690573 (breast cancer).
- **Next step**: Confirm in an external OS cohort; test whether the ARNTL2 link holds; perform loss-of-function experiments in LUAD lines.
- **Status**: **Supported hypothesis** at the biomarker level; mechanistic directionality remains open.

### V4 — **Filter and re-fit the Cox model with Firth penalisation** *(Confounding / composition check — high priority)*
- **Why prioritise**: The dominant signal in the table (HR ≈ 10²¹, P = 0) is not biology — it is model-fitting pathology. Until this is addressed, none of the candidate biomarkers above can be cleanly interpreted.
- **Dataset evidence**: 67 of 100 rows with HR = 5.18 × 10²¹ and FDR = 0; Y_RNA with 163 direction-conflicting rows; Y-chromosome and pseudogene enrichment in the "top" hits.
- **External support**: standard practice for small-effect / sparse-stratum Cox regressions; not addressed here.
- **Next step**: Re-run survival analysis with (a) Firth penalised Cox, (b) sex as a covariate, (c) filtering of Y-linked and pseudogene loci, (d) removal of features with zero or near-zero variance in event strata; report the resulting HRs and concordance index.
- **Status**: **Methodological priority** — without this, downstream biomarker conclusions are unsupported.

### V5 — **CMAHP / RBMXP1 / CRNDE as the small protective set** *(Biomarker / Exploratory)*
- **Why prioritise**: only four genes are protective; CRNDE is the most defensible as a real expressed lncRNA. CMAHP and RBMXP1 are pseudogene loci and may be sex/confounder artefacts.
- **Dataset evidence**: HR = 0.71 (CMAHP), 0.21 (RBMXP1), 0.72 (CRNDE); all FDR < 6 × 10⁻⁴.
- **External support / conflict**: CRNDE has been reported in various cancers, including as an oncogenic lncRNA in some contexts — direction is therefore context-dependent; LUAD-specific protective evidence is not present here.
- **Next step**: Re-test after sex adjustment and pseudogene filtering; validate CRNDE expression by qPCR in LUAD vs. adjacent normal and assess OS in an independent cohort.
- **Status**: **Exploratory hypothesis**.

---

## 5. Evidence Grounding (per item)

| Item | Direct dataset | Pathway/ontology | Protein/regulatory | Disease / expression | Literature |
|------|----------------|------------------|--------------------|----------------------|------------|
| DKK1 | HR = 1.475, FDR = 3.55 × 10⁻⁷ | GO Wnt regulation | — | NSCLC prognostic context | PMID 40124684 (NSCLC ferritinophagy/Wnt) |
| TLE1 | HR = 1.484, FDR = 2.46 × 10⁻⁵ | GO Wnt regulation | — | LUAD recurrent in TCGA | — |
| PITX3 | HR = 1.429, FDR = 3.49 × 10⁻¹¹ | GO Wnt / planar cell polarity | — | Brain-restricted in GTEx | — |
| VAX1 | HR = 1.335, FDR = 9.25 × 10⁻⁶ | GO Wnt / PCP | STRING partner ASXL2 | Developmental TF | — |
| RHOF | HR = 1.403, FDR = 4.00 × 10⁻⁴ | GO actin / small GTPase | STRING: ACTN1, ARHGAP1 | AML poor OS | PMID 34405015 |
| RGS20 | HR = 1.352, FDR = 5.79 × 10⁻⁴ | Reactome Gα(i)/(z) | STRING: GNAZ, GNB5, GNAI2, GNAQ, SUCLG2 | Brain-enriched in GTEx | — |
| FUT4 | HR = 1.403, FDR = 2.93 × 10⁻⁴ | KEGG O-glycan / glycosphingolipid | STRING: B3GNT3, B4GALT1 | Tissue-specific expression | — |
| KRT6A | HR = 1.390, FDR = 2.78 × 10⁻⁴ | MF protein binding | — | Alopecia areata (off-target) | PMID 42216026 |
| ITGB1-DT | HR = 1.302, FDR = 1.48 × 10⁻⁴ | — | Co-expression with ITGB1 | LUAD, breast | PMID 34906142, PMID 37690573 |
| CRNDE | HR = 0.716, FDR = 1.03 × 10⁻⁴ | — | — | Multi-cancer lncRNA | — |
| CMAHP | HR = 0.706, FDR = 5.77 × 10⁻⁴ | MF protein binding | — | Pseudogene relic | — |
| RBMXP1 | HR = 0.212, FDR = 1.60 × 10⁻¹⁷ | MF protein binding | — | Likely sex artefact | — |
| Y_RNA / RNY1P3 / RNU6-78P / RNU7-99P | HR ≈ 10²¹, FDR = 0 | RNA Pol II CTD (Reactome, mis-mapped via "CTD" string) | — | Direction-conflict rows for Y_RNA | — |
| Y-chromosome cluster | HR ≈ 10²¹, FDR = 0 | — | STRING: FAM9A–ANOS1/ARSF | Confounded by sex | — |

**Independence note**: Reactome hits for "CTD-*" genes arise from Reactome's own naming conventions and therefore are *not* independent of the gene-symbol text; they do not constitute biological replication. Several Reactome/QuickGO terms recur across the same set of genes, so apparent "module recurrence" overstates independence.

**Conflicts**: CRNDE is reported as oncogenic in some tumours and protective here — directionality is context-dependent and not resolvable from this dataset alone. RGS20 interacts with GNAI2/GNAQ in STRING but the Reactome "Gα(i)/(z) signalling" mapping omits those partners — different sources, consistent biology, not a true conflict.

---

## 6. Limitations and Alternative Explanations

1. **Complete/quasi-complete separation in Cox regression** — the dominant technical issue. Causes the ~10²¹ HRs and P = 0 / FDR = 0 in most rows; cannot be solved by more data of the same kind, only by Firth-style penalisation, exact methods, or Bayesian shrinkage.

2. **Sex / genotype confounding** — Y-linked (RBMY1F, FAM9A, TEX13A, TTTY4C, USP9YP3, VENTXP7, CDY10P, RBMY2AP) and X-pseudogene artefacts (RBMXP1) are likely driving separation simply because the cohort is not sex-balanced. Adjustment for sex is the obvious next step.

3. **Tumour purity / stromal contamination** — many of the lncRNAs (LINC01312, LINC02178, LINC01910, LINC02323, LINC02802, LINC00707, ITGB1-DT, CRNDE) have low expression and are sensitive to stromal/immune admixture. The "risk" HRs of these may reflect stromal fraction rather than tumour-intrinsic biology. Investigate by ESTIMATE / xCell deconvolution and by paired tumour/stroma microdissection.

4. **Pseudogene / repetitive-element mapping artefacts** — Y_RNA with 163 conflicting rows; MTND1P1 and similar mitochondrial pseudogenes; RBMXP1 and other processed pseudogenes. These should be filtered or remapped before survival modelling.

5. **Association-versus-causation** — even the well-behaved HRs (1.3–1.5) are observational; Wnt-pathway genes (DKK1, TLE1) and developmental TFs (PITX3, VAX1) may mark aggressive histologic subtypes rather than drive them. Stage, grade, and driver-mutation status (EGFR, KRAS, TP53, STK11) should be co-modelled to test whether the prognostic signal is independent.

6. **Lack of independent-cohort replication** — external summary explicitly states 0/0 concordant and 0/0 significant. None of the "programmes" above has been independently validated in the supplied evidence pack; pathway recurrence, drug-target presence, or literature support are not a substitute for replication.

---

## Bottom line

- The dataset's **actionable prognostic signal** is small and concentrated in **DKK1, TLE1, PITX3, VAX1, RHOF, RGS20, FUT4, KRT6A, ITGB1-DT, CRNDE**, with most of those having HRs in the 1.3–1.5 range and FDR < 10⁻³.
- The dominant numerical signature (HR ≈ 10²¹, P = 0) is a **Cox-model fitting artefact**, not biology. Sex-linked and pseudogene loci should be filtered, and survival models re-fit with penalised or Bayesian methods before any biomarker claim is made.
- **Wnt / developmental-TF and Rho-GTPase migration** are the two most defensible programmes; the glycosylation/keratin programme is plausible but smaller. None has been independently replicated here.
- ITGB1-DT is the single biomarker candidate with **published independent support** in LUAD (PMID 34906142) and is the most immediately actionable.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=77, external claims checked=0, external mismatches=0, status=passed.

Answer model API: MiniMax / minimax-m3

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 53/100 selected items (records returned); cbioportal 51/100 selected items (records returned); chembl 16/100 selected items (records returned); civic 1/100 selected items (records returned); clinicaltrials 6/100 selected items (records returned); clinvar 30/100 selected items (records returned); ensembl 11/100 selected items (partially returned; some queries failed); europepmc 362 articles / initial full-cohort RAG 100 queries + 4 current-round queries; some queries failed; gtex 81/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 14/100 selected items (records returned); humanbase 56/100 selected items (partially returned; some queries failed); intact 18/100 selected items (records returned); mygene 59/100 selected items (records returned); omnipath 3/100 selected items (records returned); opentargets 55/100 selected items (records returned); pubmed 202 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 17/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 17/100 selected items (records returned)
Local databases: gutmgene 0/100 selected items (reachable but no records for this batch); hmdb 2/100 selected items (records returned); string 14/100 selected items (records returned); trrust 4/100 selected items (records returned)
