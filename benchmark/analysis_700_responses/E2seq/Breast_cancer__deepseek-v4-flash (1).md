# breast cancer - deepseek-v4-flash

- Benchmark system: E2seq + Agent RAG
- Repeat: 2
- Task type: PROGNOSIS
- Tissue / sample source: breast tumor tissue
- Comparison or endpoint: overall survival (OS)
- Answer input cohort: Discovery/Core only
- Selected items: 100
- Input fields: gene name, effect size (log2FC/HR), P value, FDR
- E2seq Agent RAG: enabled
- Conversation memory: disabled
- Thinking mode: disabled
- Held-out validation data in prompt/RAG: no
- Model API: DeepSeek / deepseek-v4-flash
- Message SHA-256: 2eef237c25053f55d87c73e963368cae88b5c698447f11e7e98ebc594d62e5bb
- Response HTTP status: 200
- Prompt tokens: 30810
- Completion tokens: 12165
- Reasoning tokens: 0
- Total tokens: 42975
- API requests reported: 2
- Elapsed seconds: 90.362
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 685.605
- Question handoff seconds: 699.996
- Final benchmark system: E2seq; file rank 1/5; original repeat 2; model vendor: DeepSeek

---
## 1. Overall Biological Interpretation

The prognostic transcriptomic landscape of this breast cancer cohort is dominated by a **proliferative, cell-cycle-driven risk program**, opposed by a **protective program enriched for immune, stromal, and differentiation-associated genes**.

**Risk-associated genes (HR > 1):** The most striking and statistically robust signal centers on **mitotic and cell-cycle machinery** — TPX2, AURKA, KIF20A, KIF4A, CDC20, CDCA5, UBE2C, UBE2S, PTTG1, PRC1, NUSAP1, CKAP2L, CENPO, ZWINT, TROAP, RACGAP1, PKMYT1, TIMELESS, CCNE2, and TK1. This is a coherent, mechanistically interlocking set of genes that regulate spindle assembly, chromosome segregation, mitotic checkpoint control, and the metaphase-to-anaphase transition. A secondary but notable risk signal involves **RNA biology and translation** (LARP1, YTHDF1, UTP23, DDX41), **proteostasis** (PSMD3, USP30, STIP1), and **signaling/metabolism** (GSK3B, WNT7B, CPT1A, GPI, CFL1, TRIB3, GPRC5A).

**Protective-associated genes (HR < 1):** The protective set is more heterogeneous but clusters around several themes: **immune cell markers** (FCER1A, CD1C, CD1E, KLRB1, JCHAIN, IL27RA, FLT3, STAT5A, STAT5B), **extracellular matrix and stromal components** (LAMA2, COL14A1, COL17A1, OGN, OMD, MFAP4, ADAMTS8, DST, RELN, IGFBP6, PROS1), and **differentiation/developmental regulators** (TP63, SPRY2, IGF1, PDGFRA, LEPR, CCND2, CDKN2C, CBX7).

The overall picture is consistent with a **proliferation-high versus immune/stroma-high dichotomy** in breast cancer prognosis — a pattern repeatedly observed in transcriptomic subtyping of breast tumors.

---

## 2. Core Biological Programs

### Program 1: Mitotic Spindle Assembly and Chromosome Segregation
- **Direction:** Risk-associated (HR > 1)
- **Supporting genes:** TPX2 (HR 1.202), AURKA (1.189), KIF20A (1.218), KIF4A (1.199), PRC1 (1.186), NUSAP1 (1.194), CKAP2L (1.191), RACGAP1 (1.224), TROAP (1.210), PKMYT1 (1.244), CENPO (1.189), ZWINT (1.191), CDCA5 (1.218)
- **Pathway:** KEGG: Cell cycle; Reactome: "Resolution of Sister Chromatid Cohesion", "Mitotic Spindle Checkpoint"; GO: Positive regulation of mitotic nuclear division (GO:0045840)
- **Rationale:** These genes collectively execute the microtubule-dependent steps of mitosis — TPX2 and AURKA form a well-characterized complex required for spindle pole organization; KIF20A and KIF4A are kinesins moving chromosomes and spindle components; PRC1 bundles antiparallel microtubules; RACGAP1 (via the centralspindlin complex) regulates cytokinesis; CDCA5 maintains sister chromatid cohesion; ZWINT is a kinetochore component of the MIS12 complex. The recurrence of this module in the STRING network (PLK1, TPX2, BUB1B, DLGAP5 hubs) supports pathway co-membership.
- **Evidence strength:** Strong — 13+ independent genes, all with FDR < 1.3×10⁻⁶, forming a well-documented protein complex network. **Limitation:** These genes are proliferation markers; their prognostic signal may partly reflect tumor grade or intrinsic subtype rather than a specific driver mechanism.

### Program 2: Ubiquitin-Dependent Cell Cycle Progression (APC/C and Anaphase-Promoting Machinery)
- **Direction:** Risk-associated (HR > 1)
- **Supporting genes:** UBE2C (1.210), UBE2S (1.184), CDC20 (1.191), PTTG1 (1.197), PSMD3 (1.183), USP30 (1.222), FAF2 (1.200), RMND5B (1.198)
- **Pathway:** GO: Positive regulation of ubiquitin-protein transferase activity (GO:0051443); Reactome: "APC/C-mediated degradation of cell cycle proteins"; KEGG: Oocyte meiosis (shares CDC20, PTTG1)
- **Rationale:** UBE2C and UBE2S are the E2 conjugating enzymes that work with the APC/C (anaphase-promoting complex); CDC20 is the APC/C co-activator; PTTG1 (securin) is the classic APC/C substrate whose degradation triggers sister chromatid separation. PSMD3 is a 26S proteasome subunit — the downstream execution arm of ubiquitin-dependent degradation. The STRING module ANAPC2–CDC20–UBE2C–UBE2S captures this pathway co-membership. USP30 (a deubiquitinase) may counterbalance ubiquitination, though its role here is less clearly cell-cycle-specific.
- **Evidence strength:** Moderate-strong — coherent pathway logic with multiple members, but USP30 and FAF2 broaden the program beyond pure APC/C biology. **Limitation:** Ubiquitin-proteasome activity is pleiotropic; the program overlaps heavily with Program 1 (cell cycle) and may not be independently prognostic.

### Program 3: RNA Metabolism, Translation, and Ribosome Biogenesis
- **Direction:** Risk-associated (HR > 1)
- **Supporting genes:** LARP1 (1.261), YTHDF1 (1.192), UTP23 (1.203), DDX41 (1.191), NUSAP1 (1.194, also mitotic), GPI (1.192, also metabolic)
- **Pathway:** Reactome: "Translation", "rRNA processing"; GO: RNA binding (MF, 8 genes in cohort)
- **Rationale:** LARP1 is a well-established regulator of TOP-mRNA translation (ribosomal protein mRNAs, mTORC1-responsive); YTHDF1 is an m⁶A reader that promotes translation of methylated mRNAs; UTP23 is a small-subunit processome component for 18S rRNA maturation; DDX41 is an RNA helicase involved in pre-mRNA splicing. Together these suggest that **enhanced translational capacity** — a hallmark of oncogenic growth — is prognostic. The STRING network shows DDX41 and LARP1 in RNA-binding clusters.
- **Evidence strength:** Moderate — fewer genes than Program 1, but functionally coherent and mechanistically specific. **Limitation:** The RNA-binding annotation (8 genes) is broad; LARP1 and YTHDF1 have distinct mechanisms (mTORC1-dependent translation vs. m⁶A-directed) that may not be a single program.

### Program 4: Immune Cell Infiltration and Humoral Immunity (Protective)
- **Direction:** Protective-associated (HR < 1)
- **Supporting genes:** FCER1A (0.793), CD1C (0.814), CD1E (0.824), KLRB1 (0.822), JCHAIN (0.803), IL27RA (0.825), FLT3 (0.817), STAT5A (0.806), STAT5B (0.837)
- **Pathway:** GO: immune response; KEGG: Hematopoietic cell lineage (FCER1A, CD1C, CD1E, FLT3); Reactome: "Immune System"
- **Rationale:** FCER1A (FcεRIα) marks mast cells/basophils; CD1C/CD1E are lipid-antigen-presenting molecules on dendritic cells; KLRB1 (CD161) marks NK/T cells; JCHAIN (joining chain of IgM/IgA) indicates B-cell/plasma cell infiltration; FLT3 is expressed on dendritic cell progenitors; STAT5A/B mediate cytokine signaling in immune cells. This is a coherent **lymphoid/myeloid infiltration signature** — consistent with the well-established protective effect of tumor-infiltrating lymphocytes in breast cancer. The STRING module STAT3–FLT3–LEPR–STAT5A–STAT5B suggests regulatory connectivity.
- **Evidence strength:** Moderate-strong — 9 genes across multiple immune lineages. **Limitation:** This is a bulk-tissue signal; cell composition (immune infiltration fraction) may drive the association rather than a tumor-intrinsic mechanism.

### Program 5: Stromal / Extracellular Matrix Remodeling and Differentiation (Protective)
- **Direction:** Protective-associated (HR < 1)
- **Supporting genes:** LAMA2 (0.830), COL14A1 (0.824), COL17A1 (0.798), OGN (0.807), OMD (0.829), MFAP4 (0.834), ADAMTS8 (0.793), DST (0.807), RELN (0.796), IGSF10 (0.824), TP63 (0.810), SPRY2 (0.806), IGF1 (0.803), PDGFRA (0.838), LEPR (0.821), CCND2 (0.838), CDKN2C (0.807)
- **Pathway:** GO: extracellular region (CC, 8 genes); Reactome: "ECM organization"; GO: cell differentiation
- **Rationale:** LAMA2, COL14A1, COL17A1, OGN, OMD, and MFAP4 are ECM components or matricellular proteins; ADAMTS8 is a matrix metalloprotease; DST (dystonin) and RELN are cytoskeletal/developmental regulators; TP63 is a basal/differentiation transcription factor; SPRY2 is a negative regulator of receptor tyrosine kinase (RTK) signaling; IGF1 and PDGFRA are growth factor/RTK genes. This is a heterogeneous but consistently protective set, likely reflecting **differentiated, less aggressive tumor biology** or **stromal content** that is associated with better outcomes.
- **Evidence strength:** Moderate — many genes, but functionally heterogeneous (ECM, differentiation, RTK signaling, cell-cycle inhibitors). **Limitation:** This may be a composite of several distinct protective programs (stromal reaction, luminal differentiation, immune microenvironment) rather than one biological process.

---

## 3. Key Genes and Interaction Modules

### Module A: TPX2–AURKA–KIF4A–NUSAP1–PRC1 (Mitotic Spindle Module)
- **Statistics:** TPX2 HR 1.202 (FDR 1.4×10⁻⁷); AURKA HR 1.189 (7.3×10⁻⁷); KIF4A HR 1.199 (1.6×10⁻⁷); NUSAP1 HR 1.194 (1.1×10⁻⁶); PRC1 HR 1.186 (1.2×10⁻⁶)
- **Role:** Core of Program 1 — spindle pole organization, microtubule bundling, chromosome segregation.
- **Relationships:** TPX2 directly binds and activates AURKA (direct physical interaction, well-documented); AURKA and TPX2 co-localize at spindle poles; KIF4A and PRC1 are microtubule-associated proteins that function in the same mitotic spindle apparatus; NUSAP1 binds microtubules and interacts with the chromosomal passenger complex. These are **direct physical interactions** (TPX2–AURKA) and **pathway co-membership** (all in mitotic spindle organization).
- **Why key:** This is the most statistically robust and mechanistically coherent module in the risk set; multiple independent genes converge on the same process.

### Module B: CDC20–UBE2C–UBE2S–PTTG1 (APC/C Module)
- **Statistics:** CDC20 HR 1.191 (7.2×10⁻⁷); UBE2C HR 1.210 (1.7×10⁻⁷); UBE2S HR 1.184 (1.2×10⁻⁶); PTTG1 HR 1.197 (4.7×10⁻⁷)
- **Role:** Program 2 — APC/C-mediated degradation of securin (PTTG1) and cyclins to drive anaphase entry.
- **Relationships:** CDC20 is the APC/C co-activator; UBE2C and UBE2S are the E2 enzymes for APC/C; PTTG1 is the APC/C substrate. This is a **direct functional pathway** (substrate–enzyme–co-activator). STRING confirms ANAPC2–CDC20–UBE2C–UBE2S connectivity.
- **Why key:** Bridges the mitotic spindle program to the protein degradation machinery; the APC/C is a validated therapeutic target concept in oncology.

### Module C: LARP1–YTHDF1–UTP23 (Translational Control Module)
- **Statistics:** LARP1 HR 1.261 (4.5×10⁻¹⁰, strongest HR in cohort); YTHDF1 HR 1.192 (4.6×10⁻⁷); UTP23 HR 1.203 (6.8×10⁻⁸)
- **Role:** Program 3 — enhanced mRNA translation and ribosome production.
- **Relationships:** LARP1 and YTHDF1 both regulate translation but through different mechanisms (TOP-motif vs. m⁶A). Co-expression in the same pathway (translation) is likely, but direct physical interaction is not established. UTP23 is a ribosome biogenesis factor — pathway co-membership via ribosome production.
- **Why key:** LARP1 has the highest HR in the cohort; the m⁶A/translation axis (YTHDF1) is a rapidly emerging cancer target.

### Module D: FCER1A–CD1C–CD1E–KLRB1–JCHAIN (Immune Infiltration Module)
- **Statistics:** FCER1A HR 0.793 (1.8×10⁻⁹); CD1C HR 0.814 (3.1×10⁻⁷); CD1E HR 0.824 (1.3×10⁻⁶); KLRB1 HR 0.822 (3.6×10⁻⁷); JCHAIN HR 0.803 (1.8×10⁻⁹)
- **Role:** Program 4 — immune cell infiltration (dendritic cells, NK/T cells, plasma cells).
- **Relationships:** These are **co-expression markers** of different immune lineages rather than direct interactors. CD1C and CD1E are both expressed by dendritic cells (pathway co-membership in antigen presentation); FCER1A marks mast cells; KLRB1 marks NK/T cells; JCHAIN marks B/plasma cells. STRING shows a STAT3–FLT3–STAT5A/B regulatory cluster that may connect these lineages.
- **Why key:** The protective direction is strong and consistent; this module likely reflects the tumor immune microenvironment, a clinically actionable axis.

### Module E: GSK3B–WNT7B (Wnt/β-Catenin Signaling)
- **Statistics:** GSK3B HR 1.227 (1.2×10⁻⁹); WNT7B HR 1.183 (7.1×10⁻⁷)
- **Role:** Wnt signaling; GSK3B is the kinase that phosphorylates β-catenin for degradation (tumor-suppressive in the canonical pathway) but also has β-catenin-independent, pro-proliferative roles.
- **Relationships:** GSK3B and WNT7B are **pathway co-members** in Wnt signaling (WNT7B activates; GSK3B inhibits canonical signaling). STRING shows GSK3B interacting with AXIN1, APC, CTNNB1 (β-catenin) — direct physical interactions within the destruction complex.
- **Why key:** Both genes are risk-associated in the same pathway, but with opposing predicted functions (GSK3B should be tumor-suppressive in canonical Wnt). This paradox is a validation priority.

### Module F: STAT5A–STAT5B–FLT3–LEPR (Cytokine Signaling, Protective)
- **Statistics:** STAT5A HR 0.806 (4.1×10⁻⁹); STAT5B HR 0.837 (8.9×10⁻⁷); FLT3 HR 0.817 (4.4×10⁻⁷); LEPR HR 0.821 (5.4×10⁻⁷)
- **Role:** Cytokine/JAK-STAT signaling in immune cells and mammary epithelium.
- **Relationships:** STRING shows STAT3–FLT3–LEPR–STAT5A–STAT5B connectivity — likely **regulatory/co-expression** in immune signaling rather than direct physical interaction. STAT5A/B are transcription factors activated downstream of FLT3 and LEPR.
- **Why key:** The protective direction is strong; STAT5 signaling has context-dependent roles in breast cancer (luminal differentiation vs. oncogenic).

---

## 4. Validation Priorities

### Priority 1: Mitotic Spindle Module as a Prognostic Biomarker Panel
- **Classification:** Biomarker
- **Why:** The TPX2–AURKA–KIF4A–NUSAP1–PRC1 module is the most statistically robust and mechanistically coherent signal in the dataset.
- **Current evidence:** 5+ genes with HR > 1.18, all FDR < 1.3×10⁻⁶; pathway co-membership confirmed by STRING and GO/KEGG records.
- **External evidence:** AURKA, TPX2, and KIF20A are established proliferation markers in breast cancer; AURKA inhibitors exist (e.g., alisertib). However, external statistical validation in an independent breast cancer cohort was not performed.
- **Next step:** Test the module as a multigene risk score in an independent breast cancer cohort (e.g., METABRIC, TCGA-BRCA) with OS endpoint; assess whether it adds prognostic value beyond grade, stage, and intrinsic subtype.
- **Status:** Supported hypothesis.

### Priority 2: Functional Dissection of GSK3B's Risk Association
- **Classification:** Mechanistic hypothesis
- **Why:** GSK3B is canonically tumor-suppressive in Wnt signaling (β-catenin degradation) yet is risk-associated here (HR 1.227). This paradox requires mechanistic resolution.
- **Current evidence:** Risk-associated HR with FDR 1.2×10⁻⁹; STRING shows GSK3B in the β-catenin destruction complex (AXIN1, APC, CTNNB1).
- **External evidence:** GSK3B has both pro- and anti-tumor roles depending on cellular context; its role in breast cancer is debated. The risk association may reflect non-canonical GSK3B functions (e.g., NF-κB, cell cycle) or confounding by tumor grade.
- **Next step:** In breast cancer cell lines, test whether GSK3B knockdown affects proliferation in a β-catenin-dependent or -independent manner; examine GSK3B expression across intrinsic subtypes.
- **Status:** Exploratory hypothesis.

### Priority 3: Immune Infiltration Module as a Protective Biomarker
- **Classification:** Biomarker
- **Why:** The protective direction (FCER1A, CD1C, CD1E, KLRB1, JCHAIN) is strong and clinically actionable for immunotherapy stratification.
- **Current evidence:** 5 genes with HR 0.79–0.82, all FDR < 1.3×10⁻⁶.
- **External evidence:** Tumor-infiltrating lymphocytes are well-established as prognostic in triple-negative and HER2+ breast cancer. However, this is a bulk-tissue signal; the genes may simply mark immune cell abundance.
- **Next step:** Validate using multiplex immunohistochemistry or single-cell RNA-seq to confirm which immune cell types express these genes; test the module's prognostic value in an independent cohort with immune cell fraction as a covariate.
- **Status:** Supported hypothesis (for immune infiltration), but the causal relationship between these specific genes and survival is not established.

### Priority 4: LARP1–YTHDF1 Translational Axis as a Therapeutic Target
- **Classification:** Therapeutic target
- **Why:** LARP1 has the highest HR in the cohort (1.261); the m⁶A/translation axis is an emerging therapeutic concept.
- **Current evidence:** LARP1 HR 1.261 (FDR 4.5×10⁻¹⁰); YTHDF1 HR 1.192 (4.6×10⁻⁷). Both are RNA-binding proteins with distinct translational mechanisms.
- **External evidence:** LARP1 is downstream of mTORC1 and regulates ribosomal protein translation; YTHDF1 promotes translation of m⁶A-modified mRNAs. Both have been implicated in cancer. However, drug-target evidence (ChEMBL records) does not establish therapeutic efficacy in breast cancer specifically.
- **Next step:** Test LARP1 and YTHDF1 knockdown effects on proliferation and translation in breast cancer cell lines; assess whether combined inhibition is synergistic. Do not interpret drug-target database presence as clinical efficacy.
- **Status:** Exploratory hypothesis.

### Priority 5: Cell Composition Confounding Check (Immune vs. Stromal vs. Tumor)
- **Classification:** Confounding or composition check
- **Why:** The protective genes (immune and stromal markers) may reflect tissue composition rather than tumor-intrinsic biology. The risk genes (proliferation) may reflect tumor purity.
- **Current evidence:** The protective set includes both immune markers (FCER1A, CD1C) and ECM genes (LAMA2, COL14A1); the risk set includes proliferation genes. These patterns are consistent with composition-driven signals.
- **External evidence:** Bulk RNA-seq in breast tumors is known to be confounded by stromal and immune content; ESTIMATE or CIBERSORT-based deconvolution is standard practice.
- **Next step:** Perform cell-type deconvolution (CIBERSORTx, ESTIMATE) on the cohort; re-run the survival analysis adjusting for immune/stromal scores. Alternatively, validate key genes by spatial transcriptomics or IHC to localize expression to specific cell types.
- **Status:** This is a required quality check before any causal interpretation.

---

## 5. Evidence Grounding

| Claim | Direct Input Evidence | Pathway/Ontology | Interaction/Regulatory | Disease Assoc. | Tissue/Expression | Literature | Independence Assessment |
|---|---|---|---|---|---|---|---|
| Proliferation/cell-cycle risk program | Yes — 13+ genes, HR > 1.18, FDR < 1.3×10⁻⁶ | Yes — KEGG Cell cycle, GO mitotic division | Yes — STRING (PLK1, TPX2, BUB1B hubs) | Yes — proliferation markers in breast cancer | Yes — GTEx/HPA show expression in proliferative tissues | Yes — extensive breast cancer literature | Partially independent — pathway and interaction databases share underlying publications |
| APC/C ubiquitin program | Yes — 5+ genes, HR > 1.18 | Yes — GO ubiquitin transferase, Reactome APC/C | Yes — STRING (ANAPC2–CDC20–UBE2C–UBE2S) | Yes — APC/C in cancer | Yes | Yes | Partially independent — overlaps with cell-cycle program |
| Translational control (LARP1/YTHDF1) | Yes — 3 genes, HR > 1.19 | Yes — Reactome translation | Limited — no direct STRING interaction between LARP1 and YTHDF1 | Yes — m⁶A in cancer | Yes | Yes | Moderate — mechanism-specific literature is accumulating |
| Immune infiltration protective | Yes — 9 genes, HR 0.79–0.84 | Yes — immune response GO | Partial — STAT3–FLT3–STAT5 cluster | Yes — TILs prognostic in breast cancer | Yes — immune cell expression | Yes — extensive | Strongly supported externally, but input is bulk-tissue only |
| Stromal/ECM protective | Yes — 10+ genes, HR 0.79–0.84 | Yes — ECM GO/Reactome | Limited | Mixed — stromal content has context-dependent prognosis | Yes | Yes | Moderate — heterogeneous set; may be multiple programs |

**Important caveat on independence:** The GO/KEGG/STRING records and the literature records are not fully independent evidence sources — they draw on overlapping underlying publications and annotations. The only genuinely independent evidence would be an external cohort survival statistic, which was **not performed** in this analysis.

---

## 6. Limitations and Alternative Explanations

### Limitation 1: Cell Composition and Tumor Purity
The protective genes (immune and stromal markers) and risk genes (proliferation markers) are classic signatures of tissue composition. In bulk tumor RNA-seq, immune infiltration and stromal content vary widely between tumors and can dominate the transcriptomic signal. The observed HRs may reflect **cell-type abundance** rather than tumor-cell-intrinsic biology.
**How to test:** Deconvolution (CIBERSORTx, ESTIMATE), single-cell RNA-seq, or spatial transcriptomics to localize gene expression; adjust survival models for immune/stromal scores.

### Limitation 2: Broad Proliferation Signal May Reflect Grade/Subtype
The mitotic gene program (AURKA, TPX2, CDC20, etc.) is strongly correlated with tumor grade and intrinsic subtype (especially basal-like and HER2-enriched). The prognostic association may be **redundant with grade or Ki-67 index** rather than providing independent information.
**How to test:** Multivariable Cox regression adjusting for grade, stage, subtype, and Ki-67; assess whether the gene module adds independent prognostic value.

### Limitation 3: Association-versus-Causation Ambiguity
All genes are associated with OS in a single cohort. None of these associations are established as causal. The GSK3B paradox (canonical tumor-suppressor with risk-associated HR) illustrates this: the association may reflect confounding, non-canonical functions, or reverse causation.
**How to test:** Functional perturbation studies (knockdown/overexpression) in appropriate models; pathway-specific inhibitors.

### Limitation 4: No External Cohort Validation
The statistical ledger shows **no independent cohort was analyzed** for this task. All 100 genes have FDR ≤ 0.01 in this cohort, but this does not establish replication. The literature records (e.g., PROS1, STIP1, CENPO as prognostic markers) are contextual support, not replication statistics.
**How to test:** Validate the top modules (not just individual genes) in an independent breast cancer cohort with OS endpoint; require concordant direction and FDR significance.

### Limitation 5: Batch/Platform Effects and Subgroup Heterogeneity
The input table provides no information about the cohort's platform, batch structure, treatment exposure, or subtype composition. Breast cancer is heterogeneous (ER+/HER2−, HER2+, TNBC), and prognostic associations can differ dramatically by subtype. The observed signals may be driven by a specific subgroup.
**How to test:** Subgroup analysis by intrinsic subtype and treatment status; assess platform/batch as covariates if raw data are available.

---

## Summary Statement

The current prognostic transcriptomic results in breast cancer support a coherent model in which a **mitotic spindle and APC/C-driven proliferation program (TPX2–AURKA–CDC20–UBE2C, plus translational regulators LARP1/YTHDF1) is associated with worse overall survival**, while a **protective program marked by immune cell infiltration (FCER1A, CD1C, CD1E, KLRB1, JCHAIN) and stromal/differentiation genes (LAMA2, COL14A1, OGN, TP63, IGF1) is associated with better survival**, with the major caveat that these patterns may partly reflect tissue composition rather than tumor-intrinsic mechanisms, and external cohort validation was not performed.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=29, external claims checked=0, external mismatches=0, status=passed.

Answer model API: deepseek / deepseek-v4-flash.

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 100/100 selected items (records returned); cbioportal 100/100 selected items (records returned); chembl 52/100 selected items (records returned); civic 12/100 selected items (records returned); clinicaltrials 57/100 selected items (records returned); clinvar 100/100 selected items (records returned); ensembl 100/100 selected items (records returned); europepmc 990 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 98/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 99/100 selected items (records returned); humanbase 100/100 selected items (records returned); intact 99/100 selected items (partially returned; some queries failed); mygene 100/100 selected items (records returned); omnipath 65/100 selected items (records returned); opentargets 100/100 selected items (records returned); pubmed 791 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 99/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 100/100 selected items (records returned)
Local databases: gutmgene 4/100 selected items (records returned); hmdb 31/100 selected items (records returned); string 100/100 selected items (records returned); trrust 40/100 selected items (records returned)
