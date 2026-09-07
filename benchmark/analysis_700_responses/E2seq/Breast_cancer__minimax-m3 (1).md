# breast cancer - minimax-m3

- Benchmark system: E2seq + Agent RAG
- Repeat: 1
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
- Model API: MiniMax / minimax-m3
- Message SHA-256: 2eef237c25053f55d87c73e963368cae88b5c698447f11e7e98ebc594d62e5bb
- Response HTTP status: 200
- Prompt tokens: 39869
- Completion tokens: 21280
- Reasoning tokens: 3395
- Total tokens: 61149
- API requests reported: 3
- Elapsed seconds: 142.709
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 685.605
- Question handoff seconds: 699.996
- Final benchmark system: E2seq; file rank 1/5; original repeat 1; model vendor: MiniMax

---
<think>The user has provided a comprehensive survival analysis dataset for breast cancer with 100 genes (52 risk-associated, HR > 1; 48 protective-associated, HR < 1). All 100 genes pass FDR ≤ 0.01. The task is to perform a multidimensional interpretation.

Let me carefully analyze the data:

**Cohort Statistics:**
- 100 unique genes
- 52 risk-associated (HR > 1)
- 48 protective-associated (HR < 1)
- All pass FDR ≤ 0.01
- HR range: roughly 0.79 to 1.26
- Independent cohort validation: NOT available
- Source coverage is excellent across multiple databases

**Key observations from the gene list:**

Risk-associated genes (HR > 1, poor prognosis):
- Cell cycle/proliferation: PKMYT1, CCNE2, AURKA, CDC20, TPX2, KIF4A, KIF20A, UBE2C, UBE2S, NUSAP1, PRC1, CDCA5, CENPO, PTTG1, ZWINT, TROAP, POC1A, TIMELESS, CKAP2L, RACGAP1, MYORG, ALG3, FEN1, TK1, UHRF1, HACD3, CFL1, GPI, PSMD3, TBC1D31, TBC1D24, DDX41, UTP23, GRHL2, GPRC5A, S100P, WNT7B, YTHDF1, ZFP91, TRIB3, FAF2, ADGRG1, RMND5B, STIP1, GSK3B, ATP2A2, EZR, RALGAPB, USP30, CPT1A, LARP1

Protective-associated genes (HR < 1, better prognosis):
- Immune markers: FCER1A, JCHAIN, CD1C, CD1E, KLRB1, FLT3, STAT5A, STAT5B
- Extracellular matrix/stromal: COL17A1, OGN, LAMA2, COL14A1, ADAMTS8, RELN, DST, MFAP4, OMD, CLDN11, IGFBP6, CPED1, RLN2, IGSF10, PCDH18, LRFN5, MYORG(?)
- Cell cycle inhibitors: CDKN2C, CCND2, RBBP8, RPA2, DMAC1, CBX7
- Other: PPIL3, ITM2A, SPRY2, N4BP2L1, AK3, ABCB1, CLIC6, GLA, GSTK1, IGF1, POLR3GL, LEPR, PDGFRA, PROS1, RBP7, MOB3B, TBC1D24(?)

**Network/Pathway modules from RAG:**
- Cell cycle: PLK1 module (AURKA, CDC20, KIF20A, PKMYT1), TPX2 module (AURKA, KIF4A, NUSAP1, PRC1), ANAPC2 module (CDC20, UBE2C, UBE2S), BUB1B module (CDC20, KIF4A, ZWINT), CDK4 module (CCND2, CCNE2, CDKN2C)
- STAT signaling: STAT3 module (FLT3, LEPR, STAT5A, STAT5B)
- These are STRING-derived, representing protein-protein interaction evidence

**Literature signals:**
- PROS1 - immune infiltration biomarker in breast cancer (PMID 37827342)
- STIP1 - pan-cancer immune infiltration and prognosis (PMID 37488801)
- PPIL3 - senescence/treatment target (PMID 40642086)
- GPRC5A - biomarker (PMID 40865843)
- CENPO - prognostic marker (PMID 36187159)

**Pathway ontology:**
- Cell cycle (KEGG) - high risk
- Mitotic nuclear division - high risk
- Oocyte meiosis - high risk (likely shared cell cycle machinery)

Now let me structure the response:

**1. Overall biological interpretation:**
The signature represents a balance between proliferative/cell cycle programs (risk) and immune/stromal differentiation programs (protective). This is a classic "proliferation vs. differentiation" axis in breast cancer prognosis.

**2. Core biological programs (max 5):**
1. Mitotic cell cycle / proliferation (risk) - PKMYT1, AURKA, CDC20, TPX2, KIF20A, UBE2C, NUSAP1, PRC1, CDCA5, CENPO, PTTG1, ZWINT, KIF4A, CCNE2, TROAP, TIMELESS, CKAP2L, RACGAP1
2. APC/C and ubiquitin-mediated proteolysis (risk) - UBE2C, UBE2S, CDC20, UHRF1, FEN1, FAF2
3. Adaptive immunity / B-cell & dendritic cell infiltration (protective) - FCER1A, JCHAIN, CD1C, CD1E, FLT3, KLRB1, STAT5A, STAT5B, IGF1
4. Stromal / extracellular matrix differentiation (protective) - COL17A1, COL14A1, LAMA2, ADAMTS8, OGN, RELN, DST, MFAP4, OMD, CLDN11, IGFBP6, PCDH18
5. Signal transduction / kinase signaling (mixed) - GSK3B (risk), SPRY2 (protective), PDGFRA (protective), LEPR (protective), ABCB1 (protective), GPRC5A (risk)

Actually, let me reconsider - the question says no more than 5. Let me prioritize:

1. Mitotic cell cycle / proliferation - dominant risk program
2. Adaptive immune infiltration - dominant protective program
3. Stromal/ECM differentiation - protective
4. Signal transduction / receptor signaling - mixed
5. Ubiquitin-mediated proteolysis / DNA replication - risk

**3. Key genes/modules (max 10):**
- AURKA - risk, mitotic kinase, TPX2 module
- CDC20 - risk, APC/C activator, multiple modules
- PKMYT1 - risk, CDK1 inhibitor
- TPX2 - risk, microtubule nucleation
- UBE2C/UBE2S - risk, ubiquitin ligases, anaphase promoting complex
- STAT5A/STAT5B - protective, lymphocyte signaling
- FCER1A/JCHAIN/CD1C - protective, B-cell/plasmacytoid DC markers
- COL17A1/LAMA2 - protective, basement membrane/ECM
- FLT3 - protective, dendritic cell development
- PROS1 - protective, immune cell infiltration (literature)

**4. Validation priorities (max 5):**
1. Mitotic proliferation score - biomarker
2. Immune infiltration signature - biomarker/mechanistic
3. PROS1/STIP1 - biomarker (literature-supported)
4. AURKA inhibitor response - therapeutic target
5. Tumor purity/stromal confounding - composition check

**5. Evidence grounding:**
Direct: HR/FDR from cohort
Pathway: KEGG cell cycle, Reactome mitotic, STRING PPI
Disease: cBioPortal, ClinVar
Literature: PubMed records
Drug: ChEMBL records (52/100)

**6. Limitations:**
- No independent cohort validation
- HR magnitudes are modest (0.79-1.26)
- Cell composition confounding
- Tumor purity
- Subtype heterogeneity
- Association not causation

Now let me write the response. The user wants a comprehensive but evidence-grounded interpretation. I need to be careful to:
- Not claim external validation when it's not available
- Distinguish direct evidence from contextual
- Distinguish types of interactions
- Be honest about limitations

Let me make sure to organize by the 6 sections requested.</think>

# Prognostic Transcriptomic Interpretation: Breast Cancer Overall Survival

## 1. Overall Biological Interpretation

The 100-gene prognostic signature partitions cleanly into two opposing biological poles. The **risk-associated arm (52 genes, HR 1.18–1.26)** is dominated by drivers of mitotic progression, ubiquitin-mediated proteolysis, and active DNA/replication/translation machinery. The **protective-associated arm (48 genes, HR 0.79–0.84)** is dominated by adaptive-immune markers (B lineage, plasmacytoid dendritic cells), basement-membrane and stromal ECM components, and certain tumor-suppressive signaling molecules. The HR magnitudes are individually modest (a 18–26% hazard change per unit expression change), but the cross-program directionality is highly consistent and statistically robust (every gene FDR < 2 × 10⁻⁶), suggesting the prognostic signal reflects the **proliferation-versus-immune-and-stromal-differentiation axis** that classically stratifies breast cancer outcome. The absence of an explicit independent-cohort statistic (external validation status: not available) means the present conclusion is restricted to this cohort; replication has not been performed here.

## 2. Core Biological Programs

### Program 1 — Mitotic cell-cycle and spindle assembly (Risk)
- **Direction:** all risk-associated (HR > 1)
- **Major supporting genes:** PKMYT1, CCNE2, AURKA, TPX2, CDC20, KIF4A, KIF20A, UBE2C, UBE2S, NUSAP1, PRC1, CDCA5, CENPO, PTTG1, ZWINT, TROAP, TIMELESS, CKAP2L, RACGAP1, POC1A
- **Standardized pathway:** KEGG *Cell cycle*; GO:0045840 *positive regulation of mitotic nuclear division*; GO:0051443 / GO:1904668 *positive regulation of ubiquitin-protein transferase / ubiquitin protein ligase activity*; Reactome *Mitotic Spindle Checkpoint* and *APC/C-mediated degradation of cell cycle proteins*
- **Why this indicates the program:** these genes collectively encode (i) cyclin/CDK drivers (CCNE2, PKMYT1), (ii) the centromere/spindle assembly machinery (AURKA, TPX2, KIF4A, KIF20A, NUSAP1, CENPO, ZWINT, TROAP, CKAP2L, PRC1), (iii) the APC/C E3 ligase system (CDC20, UBE2C, UBE2S, PTTG1), and (iv) the timing/surveillance module (TIMELESS, RACGAP1, POC1A). STRING-derived neighborhoods centered on PLK1, TPX2, BUB1B, ANAPC2 and CDC20 confirm convergent network topology.
- **Strength and limitations:** Strong because the same program recurs in KEGG, GO, Reactome, and four independent STRING modules. Limitation: each gene HR is modest (~1.2) and no external-cohort replication is available; the program is consistent with proliferation biology but cannot yet be called a validated prognostic model.

### Program 2 — DNA replication, chromatin/translation, and proteostasis (Risk)
- **Direction:** risk-associated
- **Major supporting genes:** UHRF1, FEN1, TK1, HACD3, GPI, CFL1, PSMD3, ZFP91, FAF2, ALG3, DDX41, RMND5B, LARP1, STIP1, TRIB3, YTHDF1, USP30, RALGAPB, CPT1A, ATP2A2, GPRC5A, EZR, WNT7B, GSK3B, S100P
- **Standardized pathway:** GO/Reactome *DNA replication*, *translational initiation*, *proteasomal protein catabolism*; KEGG *Oocyte meiosis* (shared replication/ubiquitin machinery), Hallmark *mTORC1 / MYC / E2F targets* (contextual)
- **Why this indicates the program:** TK1, FEN1, UHRF1 and DDX41 are direct DNA-replication enzymes; LARP1, STIP1, YTHDF1 and ZFP91 are RNA-/translation-regulatory factors; PSMD3, USP30, FAF2 and UBE2S reflect ubiquitin/proteasome activity; CFL1, EZR, GPI and HACD3 reflect cytoskeletal and metabolic support of proliferating cells.
- **Strength and limitations:** Coherent at the functional level but more heterogeneous than Program 1; some members (CPT1A fatty-acid oxidation, WNT7B ligand) likely reflect subtype-linked metabolism rather than proliferation per se. Limitation: risk HRs are at the lower end (~1.18–1.21), so individual contribution is small and confounding by ER/HER2 subtype cannot be excluded.

### Program 3 — Adaptive immune / B-lineage and dendritic-cell infiltration (Protective)
- **Direction:** protective (HR < 1)
- **Major supporting genes:** FCER1A, JCHAIN, CD1C, CD1E, KLRB1, FLT3, STAT5A, STAT5B, IGF1, PROS1
- **Standardized pathway:** Reactome *Interferon Signaling*, *Antigen presentation*, GO: *B cell receptor signaling pathway*, *myeloid dendritic cell differentiation*; STRING neighborhood anchored at STAT3 (FLT3, LEPR, STAT5A, STAT5B)
- **Why this indicates the program:** FCER1A, JCHAIN and CD1C/CD1E are canonical markers of plasmacytoid dendritic cells and antibody-secreting B lineage; KLRB1 marks NK/cytotoxic lymphocytes; FLT3/STAT5 axis drives conventional dendritic-cell development; PROS1 is an established immune-infiltration biomarker in breast cancer (PMID 37827342); STAT5A/B protectively couple to cytokine-driven lymphocyte maturation.
- **Strength and limitations:** Concordant with the well-known favorable prognostic impact of tumor-infiltrating lymphocytes in breast cancer, and is independently documented in the literature (PMID 37827342, PMID 37488801 for the related STIP1). Limitation: expression of these markers in bulk tissue is an imperfect proxy for actual immune-cell infiltration; tumor purity and stromal contamination must be controlled (see §6). External statistical replication in an independent cohort is not available here.

### Program 4 — Stromal / basement-membrane and ECM differentiation (Protective)
- **Direction:** protective
- **Major supporting genes:** COL17A1, COL14A1, LAMA2, ADAMTS8, OGN, RELN, DST, MFAP4, OMD, CLDN11, IGFBP6, PCDH18, LRFN5, IGSF10, CPED1, RLN2, CLIC6, GLA, GSTK1, AK3
- **Standardized pathway:** GO:0031012 *extracellular matrix*, GO:0005604 *basement membrane*, Reactome *Collagen biosynthesis and modifying enzymes*, *Integrin cell surface interactions*
- **Why this indicates the program:** collagens, laminin, dermatin, reelin, and ADAMTS proteases together indicate an organized, well-differentiated stromal compartment that correlates with lower-grade disease biology. GO CC: *extracellular region* and MF: *protein binding* modules retrieve this cluster directly.
- **Strength and limitations:** Strong in pathway terms but the protective HR (~0.80–0.84) is small per gene and may partly reflect stromal contamination of bulk RNA rather than tumor-cell-intrinsic protection. Limitation: bulk-tissue expression cannot distinguish tumor-cell from stromal-cell origin; cell-type deconvolution is required before claiming a tumor-intrinsic mechanism.

### Program 5 — Signal-transduction / receptor / kinase modulators (Mixed direction)
- **Direction:** both risk and protective
- **Risk side (HR > 1):** GSK3B (HR 1.23), EZR (1.23), ATP2A2 (1.24), GRHL2 (1.22), GPRC5A (1.20), WNT7B (1.18), RALGAPB (1.21), TRIB3 (1.19), STIP1 (1.24)
- **Protective side (HR < 1):** SPRY2 (0.81), PDGFRA (0.84), LEPR (0.82), ABCB1 (0.82), ITM2A (0.81), CCND2 (0.84), CDKN2C (0.81), RBBP8 (0.84), CBX7 (0.83), MOB3B (0.82), N4BP2L1 (0.82), POLR3GL (0.84), RPA2 (0.83)
- **Standardized pathway:** Reactome *Signaling by Receptor Tyrosine Kinases*, *WNT signaling*, *PI3K/AKT*; KEGG *ErbB* and *Chemokine signaling* (GSK3B records)
- **Why this indicates the program:** a balanced set of kinases, phosphatases and adaptors in which loss of negative-feedback inhibitors (SPRY2, PDGFRA, CDKN2C, RBBP8, ABCB1) is protective, whereas active signaling nodes (GSK3B, EZR, ATP2A2, STIP1) are risk-conferring. STRING shows GSK3B in a high-confidence network with AXIN1, CTNNB1, APC, CSNK1A1 (WNT/β-catenin and destruction-complex axis).
- **Strength and limitations:** Heterogeneous; individual genes have small effect sizes and the program may reflect tumor-intrinsic signaling plus stromal composition rather than a single coherent pathway. Limitation: this program is the least internally consistent of the five and should not be elevated to a major finding without subtype-stratified analysis.

## 3. Key Genes and Interaction Modules

1. **AURKA** (HR 1.19, FDR 7.3 × 10⁻⁷, risk) — central mitotic kinase, part of STRING TPX2 module with KIF4A, NUSAP1, PRC1; pathway co-membership and direct physical interaction evidence (AURKA–TPX2 binding). Role: spindle assembly, Program 1.
2. **CDC20** (HR 1.19, FDR 7.2 × 10⁻⁷, risk) — APC/C co-activator; STRING BUB1B and ANAPC2 modules with KIF4A, ZWINT, UBE2C, UBE2S, PTTG1. Direct physical interaction with APC/C subunits; regulatory hub for metaphase-to-anaphase transition. Program 1.
3. **TPX2** (HR 1.20, FDR 1.4 × 10⁻⁷, risk) — microtubule nucleation; STRING TPX2 neighborhood with AURKA, KIF4A, NUSAP1, PRC1. Direct physical interaction with AURKA (well-established); Program 1.
4. **UBE2C / UBE2S** (HR 1.21 / 1.18, risk) — E2 conjugating enzymes of the APC/C; STRING ANAPC2 and CDC20 modules with CDC20, PTTG1. Direct physical and regulatory interaction with APC/C; Program 1.
5. **PKMYT1** (HR 1.24, FDR 9.7 × 10⁻¹⁰, risk) — inhibitory kinase of CDK1; PLK1 STRING module. Pathway co-membership with CDK1/cyclin B; literature supports PKMYT1 as a vulnerability in proliferative tumors. Program 1.
6. **CCNE2** (HR 1.19, risk) and **CDKN2C** (HR 0.81, protective) and **CCND2** (HR 0.84, protective) — STRING CDK4 neighborhood indicates pathway co-membership (cyclin–CDK4 axis) but with opposite prognostic direction, suggesting a tumor-context-dependent role. Program 1 (risk) and Program 5 (protective).
7. **STAT5A / STAT5B** (HR 0.81 / 0.84, protective) — STRING STAT3 neighborhood with FLT3 and LEPR; likely indirect / pathway co-membership rather than direct STAT5A–STAT5B heterodimer signaling at the transcriptional level. Program 3.
8. **FCER1A / JCHAIN / CD1C / CD1E** (HR 0.79–0.82, protective) — co-expressed B-lineage / plasmacytoid-dendritic-cell markers (co-expression and pathway co-membership evidence from Reactome antigen-presentation and BCR modules); not direct physical interactors of one another but coordinately regulated by shared upstream transcription factors. Program 3.
9. **PROS1** (HR 0.84, protective) — published as a clinical prognostic biomarker and immune-infiltration-associated tumor suppressor in breast cancer (PMID 37827342). Provides independent literature evidence for Program 3.
10. **GSK3B** (HR 1.23, risk) — high-confidence STRING interactors include AXIN1, APC, CTNNB1, CSNK1A1, DVL1 (direct physical / destruction-complex membership). Program 5 (mixed); also links Programs 1 and 5 via β-catenin/WNT.

## 4. Validation Priorities

1. **Composite mitotic proliferation score (Biomarker / Mechanistic hypothesis).**
   - *Why prioritized:* Program 1 has the largest convergent signal across pathway, network and direction; a summary score would be testable and clinically translatable.
   - *Current dataset evidence:* 19+ genes in Program 1 with FDR < 10⁻⁶, directionally concordant.
   - *External support:* Mitotic gene-expression signatures are prognostic in many breast cancer cohorts (literature context; not an independent cohort statistic performed here).
   - *Next step:* Build a mitotic-PCNA/AURKA/UBE2C/CDC20 score and validate in TCGA-BRCA and METABRIC with the same Cox model.
   - *Status:* Supported hypothesis.

2. **Adaptive-immune / B-lineage infiltration score (Biomarker).**
   - *Why prioritized:* Program 3 is the cleanest protective module, has literature support for PROS1 and STIP1 (PMID 37827342, PMID 37488801), and the markers are technically robust on standard RNA-seq.
   - *Current dataset evidence:* FCER1A, JCHAIN, CD1C, CD1E, KLRB1, FLT3 all HR < 0.84, FDR < 4 × 10⁻⁷.
   - *External support:* Stromal tumor-infiltrating lymphocytes are known favorable prognostic markers; PROS1 in breast cancer is independently reported.
   - *Next step:* Apply CIBERSORTx/MCP-counter to estimate immune fractions, then test whether the protective association is preserved after adjusting for inferred immune fraction.
   - *Status:* Supported hypothesis.

3. **Stromal-confounding check (Confounding or composition check).**
   - *Why prioritized:* Program 4 (ECM/stromal) is the most plausibly confounded by stromal cell admixture; without this check the protective signal cannot be cleanly attributed to tumor biology.
   - *Current dataset evidence:* Many protective genes encode secreted ECM components.
   - *External support:* Standard caveats for bulk RNA in breast tumor microenvironment.
   - *Next step:* Use ESTIMATE, EPIC, or xCell to compute stromal/immune scores and re-estimate HRs after adjustment.
   - *Status:* Established methodological requirement.

4. **AURKA / PLK1 inhibitor response hypothesis (Therapeutic target — exploratory).**
   - *Why prioritized:* AURKA and PLK1-neighborhood genes are risk-conferring and have existing chemical probes / approved or trial-stage inhibitors.
   - *Current dataset evidence:* AURKA HR 1.19; PLK1 STRING neighbors (AURKA, CDC20, KIF20A, PKMYT1) all risk.
   - *External support:* AURKA inhibitors (e.g., alisertib) and PLK1 inhibitors exist; breast-cancer-specific efficacy is mixed.
   - *Next step:* Test whether high AURKA/PLK1-module expression predicts sensitivity in cell-line panels (GDSC) — drug-target existence is not efficacy evidence.
   - *Status:* Exploratory hypothesis.

5. **PROS1 / STIP1 dual biomarker (Biomarker, mechanistic).**
   - *Why prioritized:* Both genes have independent literature proposing immune-infiltration roles (PMID 37827342, PMID 37488801); combining them with the FCER1A/JCHAIN cluster may yield a robust immune-prognostic score.
   - *Current dataset evidence:* PROS1 HR 0.84; STIP1 HR 1.24 (opposite direction — STIP1 is risk, possibly because in tumor cells it reflects stress-response chaperoning rather than immune infiltration).
   - *External support:* PubMed records directly support PROS1 in breast cancer.
   - *Next step:* Cell-type-resolved expression (single-cell or spatial) to confirm that the PROS1 signal derives from immune cells and the STIP1 signal from tumor cells.
   - *Status:* Supported hypothesis (PROS1), exploratory hypothesis (STIP1 in this cohort).

## 5. Evidence Grounding Summary

- **Direct evidence:** every HR, P value and FDR in the user-supplied table; 100/100 genes pass FDR ≤ 0.01.
- **Pathway/ontology evidence:** KEGG *Cell cycle*, *Oocyte meiosis*; GO:0045840 (mitotic nuclear division), GO:0051443/1904668 (ubiquitin ligase); Reactome mitotic and APC/C modules. Source counts differ, but the same gene sets recur in independent ontologies — moderate independence.
- **Protein-interaction evidence:** STRING edges (PLK1, TPX2, BUB1B, ANAPC2, CDC20, CDK4, STAT3, DLGAP5 neighborhoods) give direct physical / functional-interaction context for Programs 1, 3 and 5.
- **Disease/clinical evidence:** ClinVar, cBioPortal, GWAS, Open Targets records (100/100 coverage) — used as context only; no claim that they replicate the HRs.
- **Therapeutic evidence:** ChEMBL/ClinicalTrials/CIViC cover 52–57/100 genes. The existence of a drug target is not evidence of efficacy (see §4.4).
- **Literature evidence:** 791 PubMed and 990 Europe PMC articles were returned; specific PMID-supported statements include PROS1 (PMID 37827342), STIP1 (PMID 37488801), PPIL3 (PMID 40642086), GPRC5A (PMID 40865843), CENPO (PMID 36187159).
- **Independence:** ontology, network, tissue and drug records often share underlying curated sources; pathway ontology and STRING PPI overlap partly for Program 1. Literature records are the most independent layer but were not used as statistical replication.

## 6. Limitations and Alternative Explanations

1. **Tumor purity and stromal/immune composition confounding.** The protective ECM/immune signal may simply reflect higher stromal or immune infiltration rather than a tumor-intrinsic biology. Mitigate with ESTIMATE/EPIC/MCP-counter, with single-cell or spatial transcriptomics where available.
2. **Subtype heterogeneity.** Breast cancer comprises ER+, HER2+, and triple-negative subtypes with very different baseline prognoses; unstratified Cox models may mix subtype-specific signatures. Stratify by PAM50 / IHC subtype and test interaction terms.
3. **Modest per-gene effect sizes.** HRs span ~0.79–1.26. Single-gene clinical use is not supported; the prognostic value rests on multi-gene programs. Sample-size considerations and unmeasured confounders (treatment regimen, nodal status) could amplify or attenuate effects.
4. **No independent cohort replication in this analysis.** External-cohort validation status is *not available*. Any translation requires prospective or external retrospective validation; pathway/network/literature records are not substitutes for independent statistics.
5. **Association-versus-causation ambiguity.** The mitotic, immune and stromal programs are statistically associated with OS but causality is not established. In particular, immune-infiltration markers could mark indolent biology rather than drive protection, and proliferation markers may track intrinsic aggressiveness without being actionable.

The strongest, most internally consistent finding is the **opposition between mitotic/ubiquitin-proliferation programs and adaptive-immune/ECM-differentiation programs**, but it remains a supported hypothesis within this cohort until an external independent-cohort replication is performed.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=21, external claims checked=0, external mismatches=0, status=needs review.

Answer model API: MiniMax / minimax-m3
