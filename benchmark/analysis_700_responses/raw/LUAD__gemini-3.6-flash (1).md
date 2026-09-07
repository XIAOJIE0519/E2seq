# lung adenocarcinoma (LUAD) - gemini-3.6-flash

- Benchmark system: raw
- Repeat: 2
- Task type: PROGNOSIS
- Tissue / sample source: lung adenocarcinoma tumor tissue
- Comparison or endpoint: overall survival (OS)
- Answer input cohort: Discovery/Core only
- Selected items: 100
- Input fields: gene name, effect size (log2FC/HR), P value, FDR
- E2seq Agent RAG: disabled
- Conversation memory: disabled
- Thinking mode: disabled
- Held-out validation data in prompt/RAG: no
- Model API: Google Gemini / gemini-3.6-flash
- Message SHA-256: a2c9355177479f23c6c81afe1b39ba697ac131cc344bb83120b98e2c6bbfee49
- Response HTTP status: 200
- Prompt tokens: 4353
- Completion tokens: 14084
- Reasoning tokens: 
- Total tokens: 18437
- API requests reported: 
- Elapsed seconds: 25.814
- Final benchmark system: raw; file rank 1/5; original repeat 2; model vendor: Google Gemini

---
### 1. Overall Biological Interpretation

The survival analysis dataset for lung adenocarcinoma (LUAD) demonstrates a dual-layer transcriptomic profile:

1. **Biologically Plausible Prognostic Program**: A set of protein-coding genes and long non-coding RNAs (lncRNAs) displays moderate, statistically robust hazard ratios (HR ~ 1.25–1.48 for risk; HR ~ 0.71 for protective). These signals center on key pathways in aggressive LUAD:
   * **Wnt signaling modulation and transcriptional corepression** (`DKK1`, `TLE1`, `PITX3`, `VAX1`)
   * **Cytoskeletal dynamics and cell adhesion/plasticity** (`RHOF`, `KRT6A`, `FUT4`)
   * **G-protein and receptor signaling regulation** (`RGS20`, `LDLRAD3`)
   * **Non-coding RNA dysregulation** (`LINC00707`, `ITGB1-DT`, `LINC01312`, `LINC02178`, `CRNDE`)

2. **Computational / Statistical Artifacts (Quasi-Complete Separation)**: A large cluster of features exhibits non-physiological hazard ratios (e.g., $HR = 5.18 \times 10^{21}$ or $1.93 \times 10^{-22}$ with $P = 0$). This group contains Y-chromosome genes (`RBMY1F`, `TTTY4C`, `USP9YP3`, `RBMY2AP`), pseudogenes, snRNAs (`RNU6-78P`, `RNU7-99P`), and unmapped Ensembl transcripts. 

In single-variable Cox proportional hazards models, genes with near-zero expression across a major subset of samples (such as male-specific Y-linked genes absent in females, or ultra-lowly expressed non-coding transcripts) cause complete or quasi-complete numerical separation. As a result, the partial likelihood maximization algorithm hits ceiling or floor parameter caps ($5.18 \times 10^{21}$). These extreme values represent mathematical boundary convergence rather than a true $10^{21}$-fold increase in patient mortality risk.

Focusing on the realistic parameter space, the biological landscape of LUAD mortality is driven by enhanced tumor cell invasion (actin motility via `RHOF` and squamous/plasticity markers via `KRT6A`), dysregulated extracellular signaling/Wnt modulation (`DKK1`, `TLE1`), and oncogenic lncRNA transcriptional networks.

---

### 2. Core Biological Programs

```
                  +-------------------------------------------------------+
                  |         LUAD Overall Survival Architecture            |
                  +-------------------------------------------------------+
                                      |
         +----------------------------+----------------------------+
         |                                                         |
         v                                                         v
+-----------------------------------+                 +-----------------------------------+
|  Biological Programs (Valid HRs)  |                 | Technical Separation Artifacts    |
+-----------------------------------+                 +-----------------------------------+
| 1. Wnt & Transcriptional Control  |                 | 5. Low-Expression / Sex-Chrom.    |
|    (DKK1, TLE1, PITX3, VAX1)      |                 |    Separation (RBMY1F, TTTY4C,    |
| 2. Cytoskeleton & Adhesion        |                 |    USP9YP3, Y_RNA, TCP10L3)       |
|    (RHOF, KRT6A, FUT4)            |                 +-----------------------------------+
| 3. GPCR & Receptor Dynamics       |
|    (RGS20, LDLRAD3)               |
| 4. Regulatory lncRNA Network      |
|    (ITGB1-DT, LINC00707, CRNDE)   |
+-----------------------------------+
```

#### Program 1: Wnt Signal Modulation and Transcriptional Corepression
* **Direction / Prognostic Association**: Risk-associated (Adverse survival, HRs ~ 1.33–1.48)
* **Major Supporting Genes**: `TLE1` (HR = 1.484, $P = 3.20 \times 10^{-8}$), `DKK1` (HR = 1.475, $P = 4.27 \times 10^{-10}$), `PITX3` (HR = 1.429, $P = 4.14 \times 10^{-14}$), `VAX1` (HR = 1.335, $P = 1.16 \times 10^{-8}$)
* **Standardized Pathway**: Reactome: *Deactivation of the Signaling State of Wnt Planar Cell Polarity Pathway* (R-HSA-195721) / KEGG: *Wnt Signaling Pathway* (hsa04310)
* **Collective Evidence Rationale**: `DKK1` is a secreted Wnt antagonist elevated in aggressive LUAD that modulates non-canonical Wnt pathways and tumor-stroma crosstalk. `TLE1` acts as a transcriptional corepressor interacting with TCF/LEF and Hes family factors to regulate cell lineage determination and stemness. The co-elevation of homeobox transcription factors (`PITX3`, `VAX1`) further points to developmental transcriptional reprogramming that supports an aggressive cellular phenotype.
* **Evidence Strength & Limitations**: High statistical significance ($FDR < 10^{-5}$) across multiple coding genes. However, direct protein-level activity and pathway activation states (canonical vs. non-canonical Wnt signaling) cannot be confirmed by transcript abundance alone.

#### Program 2: Actin Cytoskeletal Dynamics, Cell Adhesion, and Phenotypic Plasticity
* **Direction / Prognostic Association**: Risk-associated (Adverse survival, HRs ~ 1.39–1.40)
* **Major Supporting Genes**: `RHOF` (HR = 1.403, $P = 6.31 \times 10^{-7}$), `FUT4` (HR = 1.403, $P = 4.55 \times 10^{-7}$), `KRT6A` (HR = 1.390, $P = 4.22 \times 10^{-7}$)
* **Standardized Pathway**: KEGG: *Regulation of Actin Cytoskeleton* (hsa04810) / GO: *Cell-Matrix Adhesion* (GO:0007160)
* **Collective Evidence Rationale**: `RHOF` (Rif) is a Rho GTPase involved in actin remodeling and filopodia formation, which drives cell migration. `KRT6A` is a cytokeratin associated with epithelial plasticity, stress response, and aggressive subtype transdifferentiation in lung adenocarcinoma. `FUT4` synthesizes fucosylated glycans (such as Lewis X epitopes) that mediate cell adhesion, extracellular interactions, and metastatic dissemination.
* **Evidence Strength & Limitations**: Biologically coherent across intracellular structural (cytoskeletal) and extracellular functional (glycan modification) levels. A main limitation is that bulk RNA expression does not reflect post-translational GTPase activation (RHOF GTP-binding state).

#### Program 3: GPCR and Transmembrane Receptor Signaling Dynamics
* **Direction / Prognostic Association**: Risk-associated (Adverse survival, HRs ~ 1.35–1.42)
* **Major Supporting Genes**: `LDLRAD3` (HR = 1.420, $P = 3.34 \times 10^{-7}$), `RGS20` (HR = 1.352, $P = 9.55 \times 10^{-7}$)
* **Standardized Pathway**: Reactome: *Signaling by GPCR* (R-HSA-372790) / GO: *G-protein Coupled Receptor Signaling Pathway* (GO:0007186)
* **Collective Evidence Rationale**: `RGS20` (Regulator of G Protein Signaling 20) acts as a GTPase-activating protein for $\text{G}_{\alpha}$ subunits, modulating GPCR signal duration, chemokine receptor signaling, and cell survival. `LDLRAD3` is a single-pass transmembrane receptor linked to endocytic trafficking and intracellular signaling cascades. Elevated levels of both genes indicate altered cell surface signal processing.
* **Evidence Strength & Limitations**: Supported by high-confidence FDR values ($FDR < 6 \times 10^{-4}$). However, this program includes relatively few genes in the current top list, making pathway-level conclusions less robust than those for Programs 1 and 2.

#### Program 4: Regulatory Long Non-Coding RNA (lncRNA) Network
* **Direction / Prognostic Association**: Bidirectional (predominantly Risk-associated; one Protective)
* **Major Supporting Genes**: Risk: `LINC02323` (HR = 1.373), `LINC01312` (HR = 1.364), `LINC02802` (HR = 1.333), `LINC00707` (HR = 1.318), `LINC01910` (HR = 1.312), `ITGB1-DT` (HR = 1.302), `LINC02178` (HR = 1.297); Protective: `CRNDE` (HR = 0.716, $P = 1.41 \times 10^{-7}$)
* **Standardized Pathway**: Non-coding RNA Mediated Gene Regulation / Epigenetic Transcriptional Networks
* **Collective Evidence Rationale**: Multiple non-coding RNAs demonstrate consistent statistical associations with overall survival. `ITGB1-DT` (ITGB1 divergent transcript) regulates the expression of its neighbor gene `ITGB1` (Integrin $\beta1$), promoting cell-matrix adhesion. `LINC00707` acts as a competitive endogenous RNA (ceRNA) sponge, facilitating oncogenic signaling. Conversely, high `CRNDE` expression is associated with reduced hazard in this dataset (HR = 0.716).
* **Evidence Strength & Limitations**: Highly significant association within this dataset ($FDR < 5 \times 10^{-4}$). The primary limitation is that many novel lncRNAs (`LINC02323`, `LINC01312`, `LINC02802`) lack established biological mechanisms in lung tissue, so their functions remain speculative.

#### Program 5: Low-Expression / Sex-Chromosome Separation Artifact (Technical & Methodological Signal)
* **Direction / Prognostic Association**: Pathological Extreme Association ($HR = 5.18 \times 10^{21}$ and $HR = 1.93 \times 10^{-22}$, $P = 0$, $FDR = 0$)
* **Major Supporting Genes**: `RBMY1F`, `TTTY4C`, `USP9YP3`, `Y_RNA`, `RBMY2AP`, `TCP10L3`, `RNU6-78P`, `HMGN2P39`, `ATP5PBP2`, `MTND1P1`
* **Standardized Pathway**: Computational/Methodological Artifact (Unadjusted Cox Proportional Hazards Boundary Overflow)
* **Collective Evidence Rationale**: These genes map predominantly to the Y chromosome (e.g., `RBMY1F`, `TTTY4C`, `USP9YP3`), small nuclear/non-coding RNAs (`Y_RNA`, `RNU6-78P`), or non-functional pseudogenes. In standard univariable Cox models applied to mixed-sex cohorts, Y-linked genes have zero expression in female samples. If sample subgroup balances or survival events correlate with patient sex or near-zero expression cutoffs, complete or quasi-complete separation occurs. This causes optimizer convergence failure, resulting in artificial hazard ratios at algorithm boundary limits ($5.18 \times 10^{21}$).
* **Evidence Strength & Limitations**: This is a analytical artifact caused by unadjusted regression modeling on unfiltered, sparse, or sex-chromosome-linked expression matrices. These genes should not be interpreted as functional driver mutations or genuine $10^{21}$-fold clinical risk factors.

---

### 3. Key Genes and Interaction Modules

```
         +------------------------------------------------------------+
         |        Key Biological & Functional Interaction Modules     |
         +------------------------------------------------------------+
                                        |
      +---------------------------------+---------------------------------+
      |                                 |                                 |
      v                                 v                                 v
+--------------------------+  +--------------------------+  +--------------------------+
|   Module A: Wnt/Fate     |  |  Module B: Cytoskeleton  |  |   Module C: Non-Coding   |
|  DKK1 (HR=1.48, Risk)    |  |  RHOF  (HR=1.40, Risk)   |  | ITGB1-DT (HR=1.30, Risk) |
|  TLE1 (HR=1.48, Risk)    |  |  KRT6A (HR=1.39, Risk)   |  | LINC00707(HR=1.32, Risk) |
|  PITX3(HR=1.43, Risk)    |  |  FUT4  (HR=1.40, Risk)   |  | CRNDE    (HR=0.72, Prot) |
+--------------------------+  +--------------------------+  +--------------------------+
```

1. **`TLE1` (HR = 1.484, $P = 3.20 \times 10^{-8}$, FDR = $2.46 \times 10^{-5}$)**
   * **Prognostic Association**: Risk-associated. High expression correlates with shorter overall survival.
   * **Program Role**: Central corepressor in Program 1 (Wnt & Transcriptional Control).
   * **Gene Interaction Type**: **Regulatory interaction** (acts as a transcriptional corepressor binding to TCF/LEF transcription factor complexes) and **Pathway co-membership** with `DKK1`.

2. **`DKK1` (HR = 1.475, $P = 4.27 \times 10^{-10}$, FDR = $3.55 \times 10^{-7}$)**
   * **Prognostic Association**: Risk-associated.
   * **Program Role**: Upstream secreted ligand inhibitor in Program 1.
   * **Gene Interaction Type**: **Pathway co-membership** with `TLE1` in Wnt signaling pathways. Direct receptor interaction with LRP5/6 and KREMEN cell-surface proteins.

3. **`PITX3` (HR = 1.429, $P = 4.14 \times 10^{-14}$, FDR = $3.49 \times 10^{-11}$)**
   * **Prognostic Association**: Risk-associated. Statistically robust coding-gene signal.
   * **Program Role**: Transcriptional mediator in Program 1.
   * **Gene Interaction Type**: **Regulatory interaction** (transcription factor binding target promoters) and **Co-expression** with developmental transcriptional regulators.

4. **`LDLRAD3` (HR = 1.420, $P = 3.34 \times 10^{-7}$, FDR = $2.23 \times 10^{-4}$)**
   * **Prognostic Association**: Risk-associated.
   * **Program Role**: Transmembrane receptor component in Program 3.
   * **Gene Interaction Type**: **Co-expression** with receptor endocytosis and membrane trafficking machinery.

5. **`RHOF` (HR = 1.403, $P = 6.31 \times 10^{-7}$, FDR = $4.00 \times 10^{-4}$)**
   * **Prognostic Association**: Risk-associated.
   * **Program Role**: Key small GTPase regulator in Program 2 (Cytoskeletal Dynamics).
   * **Gene Interaction Type**: **Pathway co-membership** with actin polymerization dynamics; **Indirect regulatory interaction** with cellular motility machinery.

6. **`FUT4` (HR = 1.403, $P = 4.55 \times 10^{-7}$, FDR = $2.93 \times 10^{-4}$)**
   * **Prognostic Association**: Risk-associated.
   * **Program Role**: Glycan modification driver in Program 2.
   * **Gene Interaction Type**: **Regulatory (enzymatic) interaction** via post-translational fucosylation of cell-surface adhesion proteins (e.g., CD15/Lewis X) and receptor tyrosine kinases.

7. **`KRT6A` (HR = 1.390, $P = 4.22 \times 10^{-7}$, FDR = $2.78 \times 10^{-4}$)**
   * **Prognostic Association**: Risk-associated.
   * **Program Role**: Epithelial plasticity and structural filament marker in Program 2.
   * **Gene Interaction Type**: **Direct physical interaction** (heterodimerization with cytokeratin partners) and **Co-expression** with markers of aggressive or squamous-like LUAD transdifferentiation.

8. **`RGS20` (HR = 1.352, $P = 9.55 \times 10^{-7}$, FDR = $5.79 \times 10^{-4}$)**
   * **Prognostic Association**: Risk-associated.
   * **Program Role**: Signal transduction regulator in Program 3.
   * **Gene Interaction Type**: **Direct physical / regulatory interaction** (GTPase activator binding directly to $\text{G}_{\alpha i/o}$ sub-units to accelerate GTP hydrolysis).

9. **`ITGB1-DT` (HR = 1.302, $P = 2.07 \times 10^{-7}$, FDR = $1.48 \times 10^{-4}$)**
   * **Prognostic Association**: Risk-associated.
   * **Program Role**: Non-coding RNA regulator in Program 4.
   * **Gene Interaction Type**: **Regulatory interaction** (cis-acting epigenetic/transcriptional regulator of the neighboring *ITGB1* gene encoding Integrin subunit $\beta1$).

10. **`RBMY1F` / `TTTY4C` Chromosome Y Cluster (HR = $5.18 \times 10^{21}$, $P = 0$, FDR = $0$)**
    * **Prognostic Association**: Computational Risk Artifact.
    * **Program Role**: Non-physiological extreme statistical separation (Program 5).
    * **Gene Interaction Type**: **Co-expression artifact** (linked by male-specific chromosomal localization on Chr Y; no direct protein-protein or functional interaction implied by the numerical ceiling).

---

### 4. Validation Priorities

| Priority | Hypothesis / Priority Type | Target Gene(s) / Pathways | Evidence Base (Dataset vs. External) | Recommended Next Step | Evidence Level |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Confounding / Composition Check** | Chr Y genes (`RBMY1F`, `TTTY4C`), pseudogenes, low-expression transcripts | **Dataset**: HRs at numerical caps ($10^{21}$ and $10^{-22}$), $P=0$.<br>**External**: Known Cox regression behavior when handling sex-stratified zero-inflated RNA-seq counts. | Perform sex-stratified multivariate Cox regression; apply Firth's penalized likelihood and minimum expression filtering ($CPM > 1$). | **Established Evidence** (Methodological artifact) |
| **2** | **Mechanistic Hypothesis** | `DKK1` & `TLE1` Wnt Corepression Axis | **Dataset**: Statistically robust risk association (HR ~ 1.48, $FDR < 10^{-4}$).<br>**External**: `DKK1` drives osteolytic metastasis and immunosuppression; `TLE1` mediates stemness in lung tumors. | siRNA/CRISPR knockdown of `TLE1` and `DKK1` in LUAD lines; measure Wnt reporter activity, invasion, and TCF/LEF binding. | **Supported Hypothesis** |
| **3** | **Therapeutic Target** | `RHOF` Cytoskeletal Motility Axis | **Dataset**: Risk association (HR = 1.403, $P = 6.31 \times 10^{-7}$).<br>**External**: Rho GTPases mediate filopodia formation, cell migration, and metastatic spread. | Evaluate small-molecule GTPase inhibition or RHOF knockdown on invadopodia formation and transwell invasion assays. | **Exploratory Hypothesis** |
| **4** | **Biomarker Validation** | Non-Coding RNA Signature (`ITGB1-DT`, `LINC00707`, `CRNDE`) | **Dataset**: Strong statistical associations ($FDR < 5 \times 10^{-4}$).<br>**External**: `LINC00707` sponge function reported in solid tumors; `ITGB1-DT` linked to cell adhesion. | qRT-PCR validation in independent frozen clinical LUAD tissue cohorts; construct a multivariable risk score index. | **Supported Hypothesis** |
| **5** | **Interaction / Network Hypothesis** | `ITGB1-DT` to `ITGB1` Cis-Regulation | **Dataset**: `ITGB1-DT` elevated in high-risk patients (HR = 1.302).<br>**External**: Divergent transcripts often regulate adjacent host coding genes in cis. | Perform Antisense Oligonucleotide (ASO) knockdown of `ITGB1-DT` and measure `ITGB1` mRNA, surface integrin protein levels, and cell adhesion. | **Exploratory Hypothesis** |

---

### 5. Evidence Grounding

```
+-----------------------------------------------------------------------------------+
|                            Evidence Integration Framework                         |
+-----------------------------------------------------------------------------------+
|  Direct Input Evidence  |  Pathological HRs ($10^21$) vs Moderate HRs (1.25-1.48)  |
|  Pathway & Ontology     |  Reactome Wnt, KEGG Cytoskeleton, Reactome GPCR           |
|  Protein & Regulatory   |  TLE1-TCF/LEF corepression, RGS20-Galpha GAP activity     |
|  Literature / Clinical  |  DKK1 immuno-suppression, KRT6A plasticity in LUAD        |
+-----------------------------------------------------------------------------------+
```

#### Independent vs. Overlapping Evidence Sources
* **Direct Input Dataset Evidence**: Provides statistical associations (HR, P-value, FDR) linking mRNA/lncRNA transcript levels to overall survival in LUAD tissue. This evidence is correlative, not causal.
* **Pathway & Ontology Evidence**: Standardized annotations (KEGG, Reactome, GO) link individual genes (`RHOF`, `KRT6A`, `DKK1`, `TLE1`) to biological processes like cytoskeletal remodeling and Wnt signaling. These annotations represent **independent, external biological knowledge** built from functional literature, not from this dataset.
* **Protein Interaction and Regulatory Evidence**: Databases (STRING, BioGRID) document physical binding between TLE1 and TCF/LEF factors, as well as RGS20 and $\text{G}_{\alpha}$ subunits. This provides direct structural and biochemical support that reinforces the transcriptional correlations observed in the dataset.
* **Literature Evidence Conflict**:
  * *Conflict observed in lncRNAs*: `CRNDE` acts as a protective marker in this LUAD overall survival dataset (HR = 0.716, $P = 1.41 \times 10^{-7}$). In contrast, several published studies report `CRNDE` as an oncogenic driver in colorectal cancer and specific lung cancer cell lines. This conflict likely stems from tissue-specific expression differences, varying tumor microenvironments, or distinct isoform splice variants.

#### Insufficient Evidence Identification
* **Direct Physical Interactions among Top Prognostic Markers**: There is **insufficient evidence** to claim direct physical protein-protein interactions between `DKK1` and `RHOF`, or between `KRT6A` and `RGS20`. Their co-occurrence in high-risk patients reflects parallel activation of distinct oncogenic programs (cytoskeletal remodeling, signal transduction, transcriptional corepression) rather than direct physical coupling.
* **Causal Therapeutic Efficacy**: The correlation of `DKK1` or `RHOF` expression with shorter overall survival is **insufficient evidence** to claim that pharmacologically targeting these proteins will improve patient survival.

---

### 6. Limitations and Alternative Explanations

1. **Numerical Instability and Optimizer Ceiling Artifacts (Separation)**
   * *Mechanism*: Unadjusted single-variable Cox proportional hazards algorithms hit upper boundary limits ($HR = 5.18 \times 10^{21}$) when evaluating zero-inflated transcripts or male-specific Y-chromosome genes (`RBMY1F`, `TTTY4C`, `USP9YP3`) across a mixed-sex cohort.
   * *Investigation / Resolution*: Filter out low-count genes ($CPM < 1$ in > 50% of samples), run sex-stratified Cox models, and use Firth's penalized likelihood Cox regression to correct for complete separation.

2. **Confounding by Clinical and Demographic Factors**
   * *Mechanism*: Clinical variables—such as patient sex, smoking history, tumor stage (Stage I vs. Stage IV), and driver mutations (*EGFR*, *KRAS*, *TP53*, *ALK*)—were not controlled for in single-variable regressions. For example, `KRT6A` elevation may simply track higher tumor stage or poorly differentiated histopathology.
   * *Investigation / Resolution*: Construct multivariable Cox proportional hazards models incorporating age, sex, pack-years, pathological TNM stage, and mutational status as covariates.

3. **Tumor Purity and Cell Composition Heterogeneity**
   * *Mechanism*: Whole-tissue bulk RNA sequencing measures combined signals from cancer cells, stromal fibroblasts, vascular endothelial cells, and infiltrating immune populations. Elevated `DKK1` or `RGS20` levels might reflect differences in stromal density or immune cell infiltration rather than changes in tumor cell transcription.
   * *Investigation / Resolution*: Apply computational deconvolution algorithms (e.g., CIBERSORTx, ESTIMATE) to estimate tumor purity and cell-type fractions, or validate expression using single-cell RNA sequencing (scRNA-seq) and spatial transcriptomics.

4. **Association vs. Causation Ambiguity**
   * *Mechanism*: Increased expression of risk-associated genes (`RHOF`, `FUT4`, `PITX3`) may be a downstream reactive marker of cellular stress, genomic instability, or subclonal evolution, rather than a functional driver of mortality.
   * *Investigation / Resolution*: Perform functional loss-of-function (CRISPR/RNAi) and gain-of-function experiments in patient-derived organoids or xenograft models to test causality directly.

5. **Cross-Hybridization and Pseudogene Mapping Ambiguities**
   * *Mechanism*: Non-coding features and pseudogenes (e.g., `RBMXP1`, `HMGN2P39`, `ATP5PBP2`, `RNU6-78P`) share high sequence homology with parent genes. Alignment tools may misassign short RNA-seq reads, creating artificial expression estimates.
   * *Investigation / Resolution*: Re-evaluate read alignments using stringent sequence mapping parameters (e.g., long-read RNA sequencing, unique molecular identifier [UMI] counts, and strict multi-mapping filtering).
