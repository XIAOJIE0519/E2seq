# breast cancer - gemini-3.6-flash

- Benchmark system: E2seq + Agent RAG
- Repeat: 4
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
- Model API: Google Gemini / gemini-3.6-flash
- Message SHA-256: 2eef237c25053f55d87c73e963368cae88b5c698447f11e7e98ebc594d62e5bb
- Response HTTP status: 200
- Prompt tokens: 83372
- Completion tokens: 97402
- Reasoning tokens: 44230
- Total tokens: 180774
- API requests reported: 6
- Elapsed seconds: 72.48
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 685.605
- Question handoff seconds: 699.996
- Final benchmark system: E2seq; file rank 3/5; original repeat 4; model vendor: Google Gemini

---
### 1. Overall Biological Interpretation

This prognostic transcriptomic dataset from breast tumor tissue comprises 100 statistically significant genes (FDR $\le 1.74 \times 10^{-6}$), divided into 52 risk-associated genes ($\text{HR} > 1$, higher expression associated with shorter overall survival [OS]) and 48 protective-associated genes ($\text{HR} < 1$, higher expression associated with longer OS). 

Integrated analysis reveals four dominant biological themes driving patient survival:
1. **Mitotic Spindle Assembly and G2/M Progression (Risk Driver):** Synchronous upregulation of mitotic kinesins, kinetochore proteins, and cell-cycle kinases (e.g., `PKMYT1`, `AURKA`, `TPX2`, `CDC20`, `KIF20A`) forms a prominent pro-proliferative risk axis ($\text{HR} \approx 1.18\text{--}1.24$).
2. **Proteostasis, RNA Processing, and Translational Stress Response (Risk Driver):** Key regulators of 5' TOP mRNA translation (`LARP1`, the top risk gene, $\text{HR} = 1.261$), protein folding co-chaperones (`STIP1`, $\text{HR} = 1.237$), and m6A RNA modification (`YTHDF1`, $\text{HR} = 1.192$) indicate that enhanced translational capacity and stress tolerance favor aggressive tumor behavior.
3. **Tumor-Infiltrating Adaptive and Innate Immune Signaling (Protective Driver):** Co-expression of plasma cell immunoglobulin elements (`JCHAIN`, $\text{HR} = 0.803$), dendritic cell surface molecules (`CD1C`, `CD1E`), natural killer cell receptors (`KLRB1`), and STAT family transcription factors (`STAT5A`, `STAT5B`) outlines a microenvironmental immune infiltrate associated with favorable long-term survival.
4. **Extracellular Matrix (ECM) Architecture and Stromal Homeostasis (Protective Driver):** Basement membrane collagens (`COL17A1`, $\text{HR} = 0.798$; `COL14A1`), laminins (`LAMA2`), proteoglycans (`OGN`, `OMD`), and matrix metalloproteinase regulators (`ADAMTS8`) indicate that preserved matrix structure and stromal compartmentalization constrain disease progression.

*Note on Validation Status:* Direct transcriptomic findings are derived solely from the provided primary cohort statistics. External statistical validation on an independent cohort was not performed in this analysis.

---

### 2. Core Biological Programs

```
                       ┌─────────────────────────────────────────────────────────┐
                       │          TRANSCRIPTOMIC PROGNOSTIC PROGRAM MAP          │
                       └────────────────────────────┬────────────────────────────┘
                                                    │
                 ┌──────────────────────────────────┴──────────────────────────────────┐
                 ▼                                                                     ▼
      RISK-ASSOCIATED PROGRAMS                                              PROTECTIVE-ASSOCIATED PROGRAMS
             (HR > 1.0)                                                                (HR < 1.0)
 ┌───────────────────────────────────────┐                             ┌───────────────────────────────────────┐
 │ 1. Mitotic Spindle & Cell Cycle       │                             │ 2. Immune Response & Presentation     │
 │    AURKA, TPX2, CDC20, PKMYT1, UBE2C   │                             │    JCHAIN, FCER1A, CD1C, STAT5A, KLRB1 │
 ├───────────────────────────────────────┤                             ├───────────────────────────────────────┤
 │ 4. RNA Processing & Proteostasis      │                             │ 3. ECM Architecture & Cell Adhesion   │
 │    LARP1, STIP1, DDX41, YTHDF1, UTP23  │                             │    COL17A1, OGN, LAMA2, ADAMTS8, RELN │
 └───────────────────────────────────────┘                             ├───────────────────────────────────────┤
                                                                       │ 5. Homeostatic Paracrine Signaling   │
                                                                       │    IGF1, PDGFRA, PROS1, SPRY2, LEPR    │
                                                                       └───────────────────────────────────────┘
```

#### Program 1: Mitotic Spindle Assembly & G2/M Cell Cycle Progression
* **Direction:** Risk-associated ($\text{HR} > 1$)
* **Major Supporting Genes:** `PKMYT1` ($\text{HR} = 1.244, P = 1.36 \times 10^{-13}$), `KIF20A` ($\text{HR} = 1.218, P = 1.74 \times 10^{-11}$), `CDCA5` ($\text{HR} = 1.218$), `RACGAP1` ($\text{HR} = 1.224$), `TPX2` ($\text{HR} = 1.202$), `AURKA` ($\text{HR} = 1.189$), `CDC20` ($\text{HR} = 1.191$), `UBE2C` ($\text{HR} = 1.210$), `PTTG1` ($\text{HR} = 1.197$), `PRC1` ($\text{HR} = 1.186$).
* **Standardized Pathway:** KEGG: Cell cycle (`hsa04110`) / GO: Positive Regulation Of Mitotic Nuclear Division (`GO:0045840`).
* **Biological Rationale:** The concerted upregulation of mitotic spindle organizers (`TPX2`, `AURKA`), kinesin motor proteins (`KIF20A`, `KIF4A`), anaphase-promoting complex co-factors (`CDC20`, `UBE2C`, `UBE2S`), and G2/M regulators (`PKMYT1`) directly reflects high mitotic activity and chromosomal instability in aggressive tumor phenotypes.
* **Evidence Strength & Limitations:** High direct statistical significance in the input cohort ($\text{FDR} < 1.7 \times 10^{-7}$). Main limitation: Proliferation signatures strongly correlate with histological grade and molecular subtypes (e.g., Triple-Negative vs. Luminal A), representing potential subtype-driven confounding rather than an independent mechanistic vulnerability.

#### Program 2: Adaptive & Innate Immune Microenvironment
* **Direction:** Protective-associated ($\text{HR} < 1$)
* **Major Supporting Genes:** `FCER1A` ($\text{HR} = 0.793, P = 6.52 \times 10^{-13}$), `JCHAIN` ($\text{HR} = 0.803, P = 7.43 \times 10^{-13}$), `STAT5A` ($\text{HR} = 0.806$), `STAT5B` ($\text{HR} = 0.837$), `CD1C` ($\text{HR} = 0.814$), `CD1E` ($\text{HR} = 0.824$), `KLRB1` ($\text{HR} = 0.822$), `IL27RA` ($\text{HR} = 0.825$), `FLT3` ($\text{HR} = 0.817$).
* **Standardized Pathway:** Reactome: Immunoregulatory interactions between a Lymphoid and a non-Lymphoid cell (`R-HSA-198933`) / GO: Immune Response (`GO:0006955`).
* **Biological Rationale:** Simultaneous protective associations of B-cell/plasma cell components (`JCHAIN`), dendritic cell markers (`CD1C`, `CD1E`), NK cell markers (`KLRB1`), and STAT5 transcriptional mediators highlight an active immune infiltrate capable of restricting tumor outgrowth.
* **Evidence Strength & Limitations:** Strong internal consistency ($\text{FDR} < 1.3 \times 10^{-6}$). Main limitation: Bulk tissue expression reflects immune cell abundance rather than tumor-intrinsic activation; results are sensitive to variation in leukocyte filtration during sample procurement.

#### Program 3: Extracellular Matrix Architecture & Basement Membrane Homeostasis
* **Direction:** Protective-associated ($\text{HR} < 1$)
* **Major Supporting Genes:** `COL17A1` ($\text{HR} = 0.798, P = 2.77 \times 10^{-12}$), `ADAMTS8` ($\text{HR} = 0.793, P = 1.04 \times 10^{-9}$), `RELN` ($\text{HR} = 0.796$), `OGN` ($\text{HR} = 0.807$), `LAMA2` ($\text{HR} = 0.830$), `MFAP4` ($\text{HR} = 0.834$), `OMD` ($\text{HR} = 0.829$), `COL14A1` ($\text{HR} = 0.824$).
* **Standardized Pathway:** Reactome: Extracellular matrix organization (`R-HSA-1474244`) / GO: Extracellular Region (`GO:0005576`).
* **Biological Rationale:** Structurally intact basement membranes (`COL17A1`, `LAMA2`) and pericellular matrix proteoglycans (`OGN`, `OMD`, `MFAP4`) act as physical barriers against local stromal invasion, epithelial-to-mesenchymal transition, and early metastatic intravasation.
* **Evidence Strength & Limitations:** Consistent protective HRs ($\text{HR} \approx 0.79\text{--}0.83, \text{FDR} < 1.1 \times 10^{-6}$). Main limitation: Signals may partially capture variations in normal breast tissue contamination or fibrous tumor stroma content.

#### Program 4: RNA Processing, Translation Control & Proteostasis Stress Response
* **Direction:** Risk-associated ($\text{HR} > 1$)
* **Major Supporting Genes:** `LARP1` ($\text{HR} = 1.261, P = 2.09 \times 10^{-14}$), `STIP1` ($\text{HR} = 1.237, P = 1.33 \times 10^{-13}$), `UTP23` ($\text{HR} = 1.203$), `YTHDF1` ($\text{HR} = 1.192$), `DDX41` ($\text{HR} = 1.191$), `PSMD3` ($\text{HR} = 1.183$), `FAF2` ($\text{HR} = 1.200$).
* **Standardized Pathway:** Reactome: Metabolism of RNA (`R-HSA-8953863`) / GO: RNA Binding (`GO:0003723`).
* **Biological Rationale:** `LARP1` regulates 5' TOP mRNA translation downstream of mTORC1, while `STIP1` serves as an essential co-chaperone linking HSP70 and HSP90 complexes. `YTHDF1` enhances m6A-modified mRNA translation efficiency. Together, they enable cancer cells to maintain high protein turnover and withstand metabolic stress.
* **Evidence Strength & Limitations:** Contains the single most statistically significant gene in the dataset (`LARP1`, $\text{FDR} = 4.48 \times 10^{-10}$). Main limitation: RNA processing proteins have broad baseline functional redundancy across non-malignant tissues.

#### Program 5: Growth Factor Receptor & Paracrine Homeostatic Signaling
* **Direction:** Protective-associated ($\text{HR} < 1$)
* **Major Supporting Genes:** `IGF1` ($\text{HR} = 0.803, P = 6.29 \times 10^{-10}$), `SPRY2` ($\text{HR} = 0.806, P = 4.14 \times 10^{-11}$), `LEPR` ($\text{HR} = 0.821$), `IGFBP6` ($\text{HR} = 0.828$), `PDGFRA` ($\text{HR} = 0.838$), `PROS1` ($\text{HR} = 0.836$).
* **Standardized Pathway:** KEGG: Signaling pathways regulating pluripotency of stem cells (`hsa04550`) / Reactome: Signaling by Receptor Tyrosine Kinases (`R-HSA-9006934`).
* **Biological Rationale:** Expression of paracrine growth factors (`IGF1`), matrix-binding proteins (`IGFBP6`), receptors (`PDGFRA`, `LEPR`), and receptor tyrosine kinase (RTK) feedback inhibitors (`SPRY2`) reflects differentiated tissue cross-talk and suppression of uncontrolled RTK signaling cascades.
* **Evidence Strength & Limitations:** Coherent protective direction ($\text{FDR} < 1.8 \times 10^{-6}$). Main limitation: Growth factor signaling pathways possess context-dependent roles, occasionally acting as pro-tumorigenic drivers in specific mutated backgrounds.

---

### 3. Key Genes and Interaction Modules

| Gene | Direction (HR, P-value) | Core Program | Proposed Gene-Gene / Module Relationship | Relationship Classification |
| :--- | :--- | :--- | :--- | :--- |
| **`AURKA`** | Risk ($\text{HR} = 1.189, P = 2.85 \times 10^{-9}$) | Mitotic Spindle | Binds `TPX2` directly on spindle poles; regulates APC/C via `CDC20` | **Direct physical interaction** (`TPX2`); **Regulatory interaction** (`CDC20`) |
| **`TPX2`** | Risk ($\text{HR} = 1.202, P = 1.90 \times 10^{-10}$) | Mitotic Spindle | Co-localizes with mitotic kinesins (`KIF20A`, `KIF4A`, `NUSAP1`, `PRC1`) | **Direct physical interaction** (`AURKA`); **Pathway co-membership / Co-expression** (`KIF20A`, `PRC1`) |
| **`CDC20`** | Risk ($\text{HR} = 1.191, P = 2.79 \times 10^{-9}$) | Mitotic Spindle | Co-activates APC/C complex alongside `UBE2C` and `UBE2S`; targets `PTTG1` | **Direct physical / Regulatory interaction** (`UBE2C`, `UBE2S`, `PTTG1`) |
| **`PKMYT1`** | Risk ($\text{HR} = 1.244, P = 1.36 \times 10^{-13}$) | Mitotic Spindle | Phosphorylates CDK1 to control G2/M transition alongside `CCNE2` and `TPX2` | **Regulatory interaction** (CDK1); **Pathway co-membership** (`CCNE2`, `TPX2`) |
| **`LARP1`** | Risk ($\text{HR} = 1.261, P = 2.09 \times 10^{-14}$) | RNA Processing | Binds 5' TOP motif mRNAs; functions alongside translational reader `YTHDF1` | **Regulatory interaction** (RNA binding); **Pathway co-membership** (`YTHDF1`) |
| **`STIP1`** | Risk ($\text{HR} = 1.237, P = 1.33 \times 10^{-13}$) | Proteostasis Stress | Acts as scaffold protein bridging HSP70 and HSP90 (PMID: 37488801) | **Direct physical interaction** (HSP70/HSP90); **Co-expression** (`PPIL3`) |
| **`JCHAIN`** | Protective ($\text{HR} = 0.803, P = 7.43 \times 10^{-13}$) | Immune Response | Links IgA/IgM monomers; co-expressed with immune markers (`CD1C`, `FCER1A`) | **Direct physical interaction** (IgA/IgM); **Co-expression** (`CD1C`, `FCER1A`) |
| **`STAT5A` / `STAT5B`** | Protective ($\text{STAT5A}: 0.806; \text{STAT5B}: 0.837$) | Immune Response | Dimerizes upon activation; mediates signaling for `IL27RA` and `FLT3` | **Direct physical interaction** (homo/heterodimers); **Regulatory interaction** (`IL27RA`) |
| **`COL17A1`** | Protective ($\text{HR} = 0.798, P = 2.77 \times 10^{-12}$) | ECM Architecture | Anchors epithelial hemidesmosomes; operates alongside `LAMA2` and `COL14A1` | **Direct physical interaction** (laminin-integrin complex); **Pathway co-membership** (`LAMA2`) |
| **`PROS1`** | Protective ($\text{HR} = 0.836, P = 4.79 \times 10^{-9}$) | Homeostatic Signaling | Ligand for TAM receptors (TYRO3/AXL/MERTK); linked to immune infiltration (PMID: 37827342) | **Direct physical interaction** (TAM receptors); **Pathway co-membership** (`IGF1`) |

---

### 4. Validation Priorities

#### 1. Therapeutic Targeting of Mitotic Kinases (`AURKA` and `PKMYT1`)
* **Category:** Therapeutic target
* **Prioritization Rationale:** Both `PKMYT1` ($\text{HR} = 1.244$) and `AURKA` ($\text{HR} = 1.189$) represent druggable mitotic enzymes with high statistical significance in this dataset ($\text{FDR} < 10^{-6}$).
* **Current Dataset Evidence:** Synchronous risk association ($\text{HR} > 1$) across 19 mitotic and G2/M cell-cycle regulators.
* **External Context:** Inhibitors of AURKA (e.g., alisertib) and PKMYT1 (e.g., RP-6306) are under clinical investigation for solid tumors. However, independent cohort statistical validation was not provided in this input context.
* **Next Step:** Evaluate dual inhibition of AURKA and PKMYT1 in ER+ and Triple-Negative breast cancer cell lines, followed by survival stratification in independent patient cohorts.
* **Classification:** Supported hypothesis.

#### 2. Spatial and Cellular Deconvolution of Immune Biomarkers (`JCHAIN`, `CD1C`, `FCER1A`)
* **Category:** Biomarker
* **Prioritization Rationale:** Clarifies whether protective effects ($\text{HR} \approx 0.79\text{--}0.81$) stem from specific tumor-infiltrating immune subsets (plasma cells, dendritic cells).
* **Current Dataset Evidence:** Robust protective HRs for `FCER1A` ($\text{HR} = 0.793$), `JCHAIN` ($\text{HR} = 0.803$), and `CD1C` ($\text{HR} = 0.814$).
* **External Context:** External literature confirms immune cell infiltration correlates with extended survival in breast cancer (PMID: 37827342, 37488801).
* **Next Step:** Perform multiplex immunohistochemistry and spatial transcriptomics on tissue microarrays to quantify plasma cell density relative to clinical OS.
* **Classification:** Supported hypothesis.

#### 3. Characterization of `LARP1`-Mediated 5' TOP mRNA Translation in Aggressive Tumors
* **Category:** Mechanistic hypothesis
* **Prioritization Rationale:** `LARP1` exhibits the strongest statistical association in the input dataset ($\text{HR} = 1.261, P = 2.09 \times 10^{-14}$).
* **Current Dataset Evidence:** Highest single-gene risk contribution among all 100 features.
* **External Context:** Published functional studies show LARP1 binds 5' TOP motifs downstream of mTORC1 to regulate ribosomal protein translation.
* **Next Step:** Conduct ribosome profiling (Ribo-seq) and RNA immunoprecipitation (RIP-seq) following LARP1 knockdown in breast cancer models.
* **Classification:** Supported hypothesis.

#### 4. Role of Structural Collagen and Basement Membrane Integrity (`COL17A1`, `OGN`, `LAMA2`)
* **Category:** Interaction / network hypothesis
* **Prioritization Rationale:** Structural matrix proteins consistently demonstrate strong protective HRs ($\text{HR} \approx 0.79\text{--}0.83$).
* **Current Dataset Evidence:** Multi-gene concordance across collagens, laminins, and proteoglycans ($\text{FDR} < 1.1 \times 10^{-6}$).
* **External Context:** ECM physical integrity acts as a mechanical barrier preventing cell invasion and metastatic dissemination.
* **Next Step:** Assess 3D organoid invasion and second-harmonic generation microscopy of matrix density in patient biopsies.
* **Classification:** Exploratory hypothesis.

#### 5. Confounding Assessment of Molecular Subtypes and Tumor Purity
* **Category:** Confounding or composition check
* **Prioritization Rationale:** Proliferation and stromal signals in bulk tumor RNA are heavily influenced by tumor cell purity and intrinsic subtypes (PAM50).
* **Current Dataset Evidence:** Concurrent presence of proliferation risk signatures and stromal/immune protective signatures.
* **External Context:** PAM50 subtypes (Luminal A vs. Basal-like) represent major unadjusted drivers of overall survival statistics.
* **Next Step:** Perform multivariate Cox proportional hazards regression adjusting for ER/PR/HER2 status, PAM50 subtype, tumor purity, and histological stage.
* **Classification:** Exploratory hypothesis.

---

### 5. Evidence Grounding

```
                     ┌─────────────────────────────────────────────────────────┐
                     │              EVIDENCE GROUNDING HIERARCHY               │
                     └────────────────────────────┬────────────────────────────┘
                                                  │
 ┌───────────────────────────────┬────────────────┴───────────────┬───────────────────────────────┐
 │ DIRECT INPUT EVIDENCE         │ PATHWAY & ONTOLOGY EVIDENCE    │ PROTEIN & NETWORK EVIDENCE    │
 │ • 100 features (FDR <= 1.74e-6)│ • KEGG: Cell cycle (hsa04110)  │ • STRING PPIs: AURKA-TPX2,    │
 │ • 52 Risk genes (HR 1.18-1.26)│ • Reactome: ECM (R-HSA-1474244)│   CDC20-UBE2C, STAT5A-STAT5B  │
 │ • 48 Protective (HR 0.79-0.84)│ • GO: RNA Binding (GO:0003723) │ • TRRUST regulatory networks  │
 └──────────────┬────────────────┴────────────────┬───────────────┴────────────────┬──────────────┘
                │                                 │                                │
 ┌──────────────┴────────────────┐ ┌──────────────┴────────────────┐ ┌──────────────┴───────────────┐
 │ DISEASE & LITERATURE EVIDENCE │ │ DRUG & TARGET EVIDENCE       │ │ EXTERNAL STATISTICAL REPL.   │
 │ • PROS1 immune link (37827342)│ │ • ChEMBL: AURKA, PKMYT1,     │ │ • Status: NOT AVAILABLE       │
 │ • STIP1 pan-cancer (37488801) │ │   PDGFRA, FLT3, ABCB1        │ │ • No external cohort statistic│
 │ • PPIL3 signature (40642086)  │ │ • Drug presence != Efficacy  │ │   was supplied in this input  │
 └───────────────────────────────┘ └───────────────────────────────┘ └───────────────────────────────┘
```

* **Direct Evidence from Input Dataset:** Primary statistical values ($\text{HR}$, $P$-value, $\text{FDR}$) establish feature selection across 100 genes ($\text{FDR} \le 1.74 \times 10^{-6}$). Effect directions are clearly divided into 52 risk-associated ($\text{HR} > 1$) and 48 protective-associated ($\text{HR} < 1$) genes.
* **Pathway & Ontology Evidence:** Standardized database mappings (KEGG, Reactome, QuickGO) reveal functional convergence in cell cycle regulation, immune signaling, ECM organization, and RNA translation. These enrichment records explain potential mechanism but do not replace direct cohort statistics.
* **Protein Interaction & Regulatory Evidence:** STRING network records confirm direct physical binding (e.g., `AURKA`–`TPX2`, `CDC20`–`UBE2C`, `STAT5A`–`STAT5B`). Databases may draw from overlapping primary publications and experimental databases, so high record counts must not be interpreted as independent replication.
* **Published Literature Evidence:** Question-specific PubMed records corroborate functional links, such as `PROS1` in immune infiltration (PMID: 37827342), `STIP1` in tumor immune microenvironments (PMID: 37488801), `PPIL3` in therapeutic responses (PMID: 40642086), `CENPO` in diagnostic pathways (PMID: 36187159), and `GPRC5A` in malignant subpopulations (PMID: 40865843).
* **Drug & Therapeutic Evidence:** ChEMBL and OpenTargets document targeted compounds against `AURKA`, `PKMYT1`, `PDGFRA`, `FLT3`, and `ABCB1`. Pharmacological target status does not prove therapeutic efficacy in this clinical disease context.
* **External Independent Statistical Validation:** *Not Available.* Independent cohort statistical validation was not performed. External dataset statistics were not provided in the input file.

---

### 6. Limitations and Alternative Explanations

1. **Absence of Independent Cohort Replication:**
   * *Limitation:* Findings rely strictly on internal statistical significance from a single cohort. Without external replication (e.g., METABRIC or GEO datasets), overfitting to sample-specific features remains possible.
   * *Investigation Strategy:* Perform validation of the 100-gene prognostic model in independent public transcriptomic datasets with matched clinical OS endpoints.

2. **Cellular Composition and Tumor Purity Confounding:**
   * *Limitation:* Protective signals (e.g., `JCHAIN`, `CD1C`, `COL17A1`, `OGN`) may reflect higher normal tissue contamination or dense immune infiltration rather than intrinsic tumor cell suppression.
   * *Investigation Strategy:* Apply in silico cell-type deconvolution algorithms (e.g., CIBERSORTx) and align bulk data with single-cell RNA-sequencing reference panels.

3. **Unadjusted Breast Cancer Subtype Heterogeneity:**
   * *Limitation:* High proliferation gene expression (e.g., `AURKA`, `CDC20`, `PKMYT1`) is characteristic of Triple-Negative and HER2-enriched subtypes, which carry distinct baseline hazard functions compared to ER-positive Luminal A tumors.
   * *Investigation Strategy:* Execute subtype-stratified Cox proportional hazards analyses within defined PAM50 molecular subgroups.

4. **Adjuvant Treatment Exposure Confounding:**
   * *Limitation:* Overall survival outcomes in breast cancer are influenced by systemic treatments (chemotherapy, endocrine therapy, anti-HER2 targeted agents). Genes like `ABCB1` ($\text{HR} = 0.815$) may reflect chemo-resistance mechanisms rather than untreated natural disease progression.
   * *Investigation Strategy:* Incorporate systemic therapy status as interaction terms or covariates in multivariate survival models.

5. **Association vs. Causality Ambiguity:**
   * *Limitation:* Statistical association between gene expression levels and overall survival does not prove that candidate genes functionally alter tumor growth or patient lifespan.
   * *Investigation Strategy:* Conduct loss-of-function (CRISPR/Cas9) and gain-of-function experiments in patient-derived organoids and xenograft models to demonstrate causal survival mechanisms.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=20, external claims checked=0, external mismatches=0, status=needs review.

Answer model API: Google Gemini / gemini-3.6-flash

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 100/100 selected items (records returned); cbioportal 100/100 selected items (records returned); chembl 52/100 selected items (records returned); civic 12/100 selected items (records returned); clinicaltrials 57/100 selected items (records returned); clinvar 100/100 selected items (records returned); ensembl 100/100 selected items (records returned); europepmc 990 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 98/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 99/100 selected items (records returned); humanbase 100/100 selected items (records returned); intact 99/100 selected items (partially returned; some queries failed); mygene 100/100 selected items (records returned); omnipath 65/100 selected items (records returned); opentargets 100/100 selected items (records returned); pubmed 791 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 99/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 100/100 selected items (records returned)
Local databases: gutmgene 4/100 selected items (records returned); hmdb 31/100 selected items (records returned); string 100/100 selected items (records returned); trrust 40/100 selected items (records returned)
