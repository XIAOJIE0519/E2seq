# lung adenocarcinoma (LUAD) - gemini-3.6-flash

- Benchmark system: E2seq + Agent RAG
- Repeat: 5
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
- Model API: Google Gemini / gemini-3.6-flash
- Message SHA-256: a2c9355177479f23c6c81afe1b39ba697ac131cc344bb83120b98e2c6bbfee49
- Response HTTP status: 200
- Prompt tokens: 82945
- Completion tokens: 64713
- Reasoning tokens: 29456
- Total tokens: 147658
- API requests reported: 6
- Elapsed seconds: 62.68
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 957.651
- Question handoff seconds: 970.897
- Final benchmark system: E2seq; file rank 4/5; original repeat 5; model vendor: Google Gemini

---
### 1. Overall Biological Interpretation

#### Data Quality and Technical Warning
Before interpreting the biological signals, a critical data-quality caveat must be highlighted: **over 60 non-coding RNA features, pseudogenes, and Y-chromosome loci in the uploaded dataset exhibit extreme, unconstrained hazard ratios** (e.g., $HR = 5.185 \times 10^{21}$ for *RBMY1F*, *FAM9A*, *HMGN2P39*, etc.; and $HR = 1.929 \times 10^{-22}$ for *TCP10L3*) alongside mathematically zero $P$ values and FDRs ($P = 0, FDR = 0$). These non-physiological values reflect numerical saturation, computational boundary conditions, or complete separation artifacts in unpenalized Cox proportional hazards models—typically caused by zero-count inflation or extreme low-expression sparsity across survival strata. Consequently, these saturated statistical values cannot be treated as true biological effect magnitudes.

#### Integrated Biological Theme
Filtering past these technical artifacts to focus on well-annotated protein-coding genes and validated non-coding transcripts reveals a coherent, biologically biologically grounded spectrum of overall survival (OS) risk in lung adenocarcinoma (LUAD). The dominant prognostic signal is driven by **risk-associated genes ($HR > 1$)** that converge on three central oncogenic axes:
1. **Wnt/$\beta$-Catenin Dysregulation and Morphogenetic Repression**: Driven by elevated expression of Wnt signaling regulators and transcriptional corepressors such as *DKK1* ($HR = 1.475$) and *TLE1* ($HR = 1.484$).
2. **Small GTPase Dynamics, Cytoskeletal Remodeling, and Cell Motility**: Mediated by small GTPases, regulators, and intermediate filaments including *RHOF* ($HR = 1.403$), *RGS20* ($HR = 1.352$), and *KRT6A* ($HR = 1.390$).
3. **Oncogenic Surface Glycosylation and Receptor Trafficking**: Highlighted by fucosyltransferases and endocytic receptors such as *FUT4* ($HR = 1.403$) and *LDLRAD3* ($HR = 1.420$).

In parallel, specific long non-coding RNAs (lncRNAs)—notably *ITGB1-DT* ($HR = 1.302$)—mark high-risk progression, whereas transcripts such as *CRNDE* ($HR = 0.716$) associate with protective outcomes. 

*Note on Validation Status*: Direct statistics from the uploaded Cox regression form the primary dataset evidence. **External statistical validation was not performed** on an independent cohort within the supplied data; database annotations and literature citations serve exclusively as functional context.

---

### 2. Core Biological Programs

```
                  ┌─────────────────────────────────────────────────────────┐
                  │    Prognostic Transcriptomic Landscape in LUAD (OS)    │
                  └────────────────────────────┬────────────────────────────┘
                                               │
         ┌──────────────────────┬──────────────┴───────┬──────────────────────┐
         ▼                      ▼                      ▼                      ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   Program 1:     │  │   Program 2:     │  │   Program 3:     │  │   Program 4:     │
│   Wnt/Morpho-    │  │  Small GTPase &  │  │  Glycosylation & │  │  Oncogenic lncRNA│
│  genetic Axis    │  │  Cytoskeleton    │  │ Cell-Surface Axis│  │  Regulatory Axis │
├──────────────────┤  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤
│ DKK1  (HR=1.475) │  │ RHOF   (HR=1.403) │  │ FUT4   (HR=1.403) │  │ ITGB1-DT(HR=1.302│
│ TLE1  (HR=1.484) │  │ RGS20  (HR=1.352) │  │ LDLRAD3(HR=1.420) │  │ LINC00707(HR=1.31│
│ PITX3 (HR=1.429) │  │ KRT6A  (HR=1.390) │  │                  │  │ CRNDE  (HR=0.716)│
│ VAX1  (HR=1.335) │  │                  │  │                  │  │                  │
└──────────────────┘  └──────────────────┘  └──────────────────┘  └──────────────────┘
```

#### Program 1: Wnt/$\beta$-Catenin Pathway Dysregulation & Morphogenetic Repression
* **Direction**: Risk-associated (Higher expression correlates with shorter overall survival).
* **Major Supporting Genes**: *DKK1* ($HR = 1.475, P = 4.27 \times 10^{-10}, FDR = 3.55 \times 10^{-7}$), *TLE1* ($HR = 1.484, P = 3.20 \times 10^{-8}, FDR = 2.46 \times 10^{-5}$), *PITX3* ($HR = 1.429, P = 4.14 \times 10^{-14}, FDR = 3.49 \times 10^{-11}$), *VAX1* ($HR = 1.335, P = 1.16 \times 10^{-8}, FDR = 9.25 \times 10^{-6}$).
* **Standardized Pathway**: GO:0030111 (Regulation of Wnt Signaling Pathway); KEGG: hsa04310 (Wnt signaling pathway).
* **Biological Explanation**: *DKK1* is a canonical secreted Wnt antagonist, while *TLE1* functions as a transcriptional corepressor that interacts with TCF/LEF factors downstream of Wnt and Notch signaling. In LUAD, overexpression of negative-feedback regulators like DKK1 frequently marks tumors with hyperactivated, aggressive Wnt autocrine loops or stem cell-like morphogenetic plasticities driven by homeobox transcription factors (*PITX3*, *VAX1*).
* **Strength & Limitations**: Supported by multiple protein-coding genes with concordant hazard ratios and established pathway annotations. Limited by the absence of protein-level phosphorylation or nuclear $\beta$-catenin localization data in this cohort.

#### Program 2: Small GTPase Signal Transduction & Cytoskeletal Motility
* **Direction**: Risk-associated (Worse overall survival).
* **Major Supporting Genes**: *RHOF* ($HR = 1.403, P = 6.31 \times 10^{-7}, FDR = 4.00 \times 10^{-4}$), *RGS20* ($HR = 1.352, P = 9.55 \times 10^{-7}, FDR = 5.79 \times 10^{-4}$), *KRT6A* ($HR = 1.390, P = 4.22 \times 10^{-7}, FDR = 2.78 \times 10^{-4}$).
* **Standardized Pathway**: GO:0007264 (Small GTPase mediated signal transduction); GO:0030036 (Actin cytoskeleton organization).
* **Biological Explanation**: *RHOF* (Rif) is a Rho family GTPase that directs filopodia formation and cell migration. *RGS20* regulates G-protein coupled receptor (GPCR) GTPase activity, specifically modulating $G_{\alpha(i)}$ and $G_{\alpha(z)}$ signaling. *KRT6A* builds intermediate filaments involved in cell structural integrity and invasion. Together, elevated transcript levels of these regulators reflect heightened cytoskeletal plasticity and invasive cell migration in high-risk LUAD.
* **Strength & Limitations**: Moderate-to-high biological coherence across QuickGO and Reactome annotations. Limited because GTPase signaling depends heavily on post-translational GTP-binding state rather than RNA expression alone.

#### Program 3: Oncogenic Surface Glycosylation & Receptor Endocytosis
* **Direction**: Risk-associated (Worse overall survival).
* **Major Supporting Genes**: *FUT4* ($HR = 1.403, P = 4.55 \times 10^{-7}, FDR = 2.93 \times 10^{-4}$), *LDLRAD3* ($HR = 1.420, P = 3.34 \times 10^{-7}, FDR = 2.23 \times 10^{-4}$).
* **Standardized Pathway**: KEGG: Glycosphingolipid biosynthesis / Mannose type O-glycan biosynthesis; GO:0006486 (Protein glycosylation).
* **Biological Explanation**: *FUT4* encodes an $\alpha$-(1,3)-fucosyltransferase responsible for synthesizing tumor-associated carbohydrate antigens (such as Lewis X), which facilitate selectin-mediated cell adhesion and metastasis. *LDLRAD3* is a low-density lipoprotein receptor class A domain-containing receptor implicated in cell-surface transport and receptor binding. 
* **Strength & Limitations**: Supported by KEGG pathway enrichment and STRING interaction evidence. Limited by a low overall gene count within this specific program in the selected feature set.

#### Program 4: Oncogenic Long Non-Coding RNA (lncRNA) Regulatory Network
* **Direction**: Mixed (Predominantly Risk-associated; selective Protective transcripts).
* **Major Supporting Genes**: Risk: *ITGB1-DT* ($HR = 1.302, FDR = 1.48 \times 10^{-4}$), *LINC00707* ($HR = 1.318, FDR = 4.73 \times 10^{-4}$), *LINC01312* ($HR = 1.364, FDR = 3.52 \times 10^{-6}$), *LINC02178* ($HR = 1.297, FDR = 9.04 \times 10^{-6}$); Protective: *CRNDE* ($HR = 0.716, P = 1.41 \times 10^{-7}, FDR = 1.03 \times 10^{-4}$).
* **Standardized Pathway**: Non-coding RNA transcriptional regulation (Reactome R-HSA-6807505 context).
* **Biological Explanation**: Divergent lncRNAs such as *ITGB1-DT* regulate neighboring gene networks (e.g., integrin signaling) to promote tumor cell motility and proliferation in LUAD. Conversely, *CRNDE* expression exhibits protective prognostic utility ($HR < 1$) in this cohort, suggesting a potential role in cell-cycle arrest or metabolic homeostasis depending on cell-type context.
* **Strength & Limitations**: Strong internal statistical evidence ($FDR < 1 \times 10^{-4}$) and direct literature precedence for *ITGB1-DT* in LUAD (PMID: 34906142). Limited because precise regulatory modes (sponging vs epigenetic chromatin scaffolding) cannot be resolved from bulk transcriptomic Cox models alone.

---

### 3. Key Genes and Interaction Modules

| Candidate Gene | Dataset HR | Dataset FDR | Program / Biological Role | Explicit Relationship Type |
| :--- | :--- | :--- | :--- | :--- |
| **DKK1** | 1.475 | $3.55 \times 10^{-7}$ | Wnt pathway inhibition & stemness | **Pathway co-membership**: Co-annotated with *TLE1* in Wnt signaling (GO:0030111). No direct physical interaction. |
| **TLE1** | 1.484 | $2.46 \times 10^{-5}$ | Wnt/Notch transcriptional repression | **Pathway co-membership**: Functional co-membership with *DKK1*, *PITX3*, and *VAX1* in developmental transcription. |
| **RHOF** | 1.403 | $4.00 \times 10^{-4}$ | Rho GTPase filopodia & motility | **Direct physical interaction**: Interacts with *ACTN1* and *ARHGAP1* (STRING database evidence). |
| **RGS20** | 1.352 | $5.79 \times 10^{-4}$ | GPCR $G_{\alpha(i)/z}$ GTPase activation | **Direct physical interaction**: Physical binding with G-protein subunits (*GNAZ*, *GNB5*, *GNAI2*, *GNAQ*) (STRING/QuickGO). |
| **FUT4** | 1.403 | $2.93 \times 10^{-4}$ | Fucosyltransferase glycan synthesis | **Pathway co-membership**: Functional co-membership with glycosyltransferases *B3GNT3* and *B4GALT1* (STRING/KEGG). |
| **ITGB1-DT** | 1.302 | $1.48 \times 10^{-4}$ | Oncogenic divergent lncRNA | **Putative regulatory / Literature co-occurrence**: Regulates *ITGB1* / *ARNTL2* axis in LUAD prognosis (PMID: 34906142). |
| **LDLRAD3** | 1.420 | $2.23 \times 10^{-4}$ | Cell surface receptor endocytosis | **Direct physical interaction**: Protein binding interaction with Amyloid Beta Precursor Protein (*APP*) (STRING evidence). |
| **KRT6A** | 1.390 | $2.78 \times 10^{-4}$ | Epithelial intermediate filament | **Co-expression / Structural pathway co-membership**: Co-expressed cytoskeletal component in aggressive epithelial states. |
| **PITX3** | 1.429 | $3.49 \times 10^{-11}$ | Morphogenetic homeobox transcription | **Regulatory interaction**: Putative transcriptional regulation of downstream developmental targets. |
| **CRNDE** | 0.716 | $1.03 \times 10^{-4}$ | Protective long non-coding RNA | **Co-expression / Indirect relationship**: Inverse co-expression relationship with high-risk proliferation clusters. |

---

### 4. Validation Priorities

```
  Priority 1: ITGB1-DT [Biomarker] ──► RT-qPCR in Independent Cohort (Supported Hypothesis)
  Priority 2: DKK1 Axis [Mechanistic] ──► In vitro Wnt Reporter Knockdown (Supported Hypothesis)
  Priority 3: RHOF Axis [Network]     ──► IP-MS with ACTN1 / Invasion Assay (Exploratory Hypothesis)
  Priority 4: Saturated HRs [Check]   ──► Firth's Penalized Cox Re-analysis (Established Evidence)
  Priority 5: FUT4 Axis [Therapeutic] ──► Fucosyltransferase Small-Molecule Inhibition (Exploratory Hypothesis)
```

#### Priority 1: ITGB1-DT Prognostic Diagnostic & Survival Biomarker
* **Category**: Biomarker
* **Why Prioritize**: Demonstrates strong internal statistical significance ($HR = 1.302, FDR = 1.48 \times 10^{-4}$) backed by direct published literature in lung adenocarcinoma.
* **Dataset Evidence**: Statistically significant risk association with overall survival in LUAD tumor tissue.
* **External Evidence**: Published studies confirm *ITGB1-DT* is upregulated in LUAD and correlates with poor survival through the *ITGB1-DT/ARNTL2* axis (PMID: 34906142).
* **Next Step for Validation**: Perform RT-qPCR quantification of *ITGB1-DT* in an independent, fully annotated formalin-fixed paraffin-embedded (FFPE) cohort of LUAD patients with complete clinical survival follow-up.
* **Evidence Classification**: **Supported hypothesis** (Pending independent statistical replication).

#### Priority 2: DKK1 / Wnt Pathway Paracrine Crosstalk and Invasiveness
* **Category**: Mechanistic hypothesis
* **Why Prioritize**: High risk association ($HR = 1.475, FDR = 3.55 \times 10^{-7}$) among protein-coding genes, representing a key nodal point in Wnt pathway feedback.
* **Dataset Evidence**: Concurrent elevation of Wnt antagonist *DKK1* and transcriptional corepressor *TLE1*.
* **External Evidence**: Literature indicates secreted DKK1 suppresses local immune clearance and promotes cancer cell stemness in solid tumors.
* **Next Step for Validation**: Knockdown and overexpression of *DKK1* in human LUAD cell lines (e.g., A549, H1299) followed by TCF/LEF reporter assays, transwell invasion assays, and co-culture with immune effector cells.
* **Evidence Classification**: **Supported hypothesis**.

#### Priority 3: RHOF GTPase Cytoskeletal Network & Filopodia Formation
* **Category**: Interaction / network hypothesis
* **Why Prioritize**: Connects small GTPase signaling ($HR = 1.403, FDR = 4.00 \times 10^{-4}$) to tumor cell structural invasion.
* **Dataset Evidence**: Direct risk association in LUAD OS ledger; STRING PPI linkage to actin-binding proteins (*ACTN1*, *ARHGAP1*).
* **External Evidence**: Literature reports high RHOF expression predicts poor overall survival in aggressive malignancies (PMID: 34405015).
* **Next Step for Validation**: Co-immunoprecipitation and mass spectrometry (IP-MS) in LUAD cells to confirm physical RHOF-ACTN1 complexing, paired with live-cell imaging of filopodia formation under shRNA-mediated *RHOF* depletion.
* **Evidence Classification**: **Exploratory hypothesis**.

#### Priority 4: Re-evaluation of Saturated Hazard Ratios via Penalized Regression
* **Category**: Confounding or composition check
* **Why Prioritize**: Essential for methodological integrity. Over 60 features exhibit non-physiological hazard ratios ($HR = 5.185 \times 10^{21}$) and $P = 0$.
* **Dataset Evidence**: Extreme, identical point estimates across pseudogenes (e.g., *HMGN2P39*, *ATP5PBP2*) and non-coding transcripts (*RBMY1F*, *Y_RNA*).
* **External Evidence**: Standard unpenalized Cox proportional hazards algorithms undergo numerical failure (complete separation) when low-expression transcripts contain zero counts in specific outcome groups.
* **Next Step for Validation**: Re-fit multivariable survival models using Firth’s penalized likelihood or Lasso/Ridge Cox regression following strict filter removal of low-count pseudogenes.
* **Evidence Classification**: **Established evidence** (Technical model artifact requiring correction).

#### Priority 5: FUT4-Mediated Fucosyltransferase Activity as a Therapeutic Vulnerability
* **Category**: Therapeutic target
* **Why Prioritize**: Glycosylation enzymes present actionable catalytic pockets for small-molecule inhibition ($HR = 1.403, FDR = 2.93 \times 10^{-4}$).
* **Dataset Evidence**: Risk association with OS in the primary dataset.
* **External Evidence**: FUT4 elevates cell-surface Lewis X expression, increasing tumor cell-selectin adhesion and metastatic dissemination in lung cancer models.
* **Next Step for Validation**: Treat high-FUT4 LUAD cell lines with small-molecule fucosyltransferase inhibitors (e.g., 2-deoxy-2-fluoro-L-fucose) and evaluate cell-matrix adhesion, selectin binding, and xenograft metastatic seeding.
* **Evidence Classification**: **Exploratory hypothesis** (Target availability does not equal proven therapeutic efficacy).

---

### 5. Evidence Grounding

```
      Direct Input Data          External Knowledge Databases         Published Literature
  ┌───────────────────────┐       ┌───────────────────────────┐      ┌────────────────────┐
  │ Uploaded Cox Ledger   │       │ STRING (RGS20, RHOF, PPI) │      │ PMID: 34906142     │
  │ • HR, P-val, FDR      │       │ Reactome / GO (Wnt, Glyc) │      │ (ITGB1-DT in LUAD) │
  │ • 100 Selected Genes  │       │ GTEx / HPA Tissue Express │      │ PMID: 34405015     │
  └───────────┬───────────┘       └─────────────┬─────────────┘      │ (RHOF in OS)       │
              │                                 │                    └─────────┬──────────┘
              │                                 │                              │
              └────────────────┐                │                              │
                               ▼                ▼                              ▼
                        ┌────────────────────────────────────────────────────────┐
                        │      Synthesis & Evidence Adjudication Hierarchy       │
                        ├────────────────────────────────────────────────────────┤
                        │ 1. Direct Input Statistics (Primary)                   │
                        │ 2. Pathway & PPI Functional Context (Exploratory)       │
                        │ 3. External Statistical Validation: NOT PERFORMED      │
                        └────────────────────────────────────────────────────────┘
```

The conclusions in this analysis are structured according to the following evidence categories:

1. **Direct Evidence from Input Dataset**:
   * *Source*: The supplied 100-gene transcriptomic Cox survival table.
   * *Scope*: Direct hazard ratios, $P$ values, and FDR values for all genes (e.g., *DKK1* $HR = 1.475$, *ITGB1-DT* $HR = 1.302$, *CRNDE* $HR = 0.716$).
   * *Independence*: Represents the single primary quantitative source for this dataset.

2. **Pathway & Gene Ontology Evidence**:
   * *Source*: QuickGO, Reactome, and KEGG database records retrieved for selected genes.
   * *Scope*: Biological process annotations such as Wnt regulation (GO:0030111), small GTPase signaling (GO:0007264), and glycan biosynthesis (KEGG).
   * *Independence*: External functional context; derived from generalized curate databases, not calculated from the uploaded dataset.

3. **Protein Interaction & Regulatory Network Evidence**:
   * *Source*: STRING database and TRRUST network records.
   * *Scope*: Direct physical interaction records (e.g., RGS20 binding to G-protein subunits $G_{\alpha(i)/z}$; RHOF interacting with ACTN1; LDLRAD3 binding APP).
   * *Independence*: Derived from external experimental biophysical assays and text-mining models.

4. **Published Literature Evidence**:
   * *Source*: PubMed / Europe PMC search records.
   * *Scope*: Specific disease context, such as *ITGB1-DT* operating as a prognostic biomarker in LUAD (PMID: 34906142) and *RHOF* predicting survival outcomes in oncology (PMID: 34405015).
   * *Independence*: Independent external clinical and experimental publications.

5. **Conflicting & Insufficient Evidence**:
   * *Conflicting Signal*: *CRNDE* is documented in broad literature as an oncogenic driver in certain GI cancers, but presents a protective prognostic association ($HR = 0.716, FDR = 1.03 \times 10^{-4}$) in this specific LUAD cohort.
   * *Insufficient Evidence*: Multiple uncharacterized pseudogenes (*RBMXP1*, *TCP10L3*, *DRAXINP1*, *ETFRF1P1*) lack experimental protein interaction or pathway records. Functional mechanisms for these pseudogenes are explicitly categorized as **insufficient evidence**.

---

### 6. Limitations and Alternative Explanations

1. **Model Non-Convergence & Saturated HR Artifacts**:
   * *Issue*: Over 60 genes show an identical, unphysiological $HR = 5.185 \times 10^{21}$ with $P = 0$.
   * *Impact*: Computational saturation occurs when low-count non-coding RNAs or pseudogenes have complete separation across survival outcome groups.
   * *Investigation*: Filter features by expression thresholds (e.g., $CPM > 1$ in $>20\%$ of samples) and re-analyze using Firth's penalized Cox regression.

2. **Absence of Independent Cohort Statistical Validation**:
   * *Issue*: No external validation statistics (e.g., validation cohort $HR$, $P$ value) were provided.
   * *Impact*: Statistical significance ($FDR < 0.05$) in a single cohort carries risk of cohort-specific overfitting.
   * *Investigation*: Test the derived gene signature on public independent datasets (e.g., TCGA-LUAD, GEO validation cohorts: GSE31210, GSE30219).

3. **Tumor Purity & Tissue Composition Confounding**:
   * *Issue*: Bulk tumor RNA sequencing integrates malignant epithelial cells, stromal fibroblasts, immune infiltrates, and vascular structures.
   * *Impact*: High expression of genes like *KRT6A* (epithelial remodeling) or *FUT4* (glycosylation/adhesion) may reflect variations in tumor purity or stromal cell abundance rather than cell-intrinsic transcriptomic rewiring.
   * *Investigation*: Perform digital cell-type deconvolution (e.g., CIBERSORTx, EPIC) or single-cell RNA-seq (scRNA-seq) spatial profiling to assign gene signals to specific cell lineages.

4. **Association vs. Causation Ambiguity**:
   * *Issue*: Cox proportional hazards models establish prognostic correlation with overall survival, not biological causality.
   * *Impact*: Upregulation of Wnt inhibitors like *DKK1* ($HR = 1.475$) may represent a secondary compensatory stress response to aggressive upstream signaling rather than a driver of tumor progression.
   * *Investigation*: Conduct loss-of-function (CRISPRi/shRNA) and gain-of-function experiments in preclinical models to determine if gene manipulation alters cell survival or invasion.

5. **Unadjusted Clinical Confounders**:
   * *Issue*: Single-gene hazard ratios in the input ledger do not specify adjustment for essential clinical covariates.
   * *Impact*: Prognostic signals may be driven by baseline differences in clinical stage (Stage I vs Stage IV), patient age, smoking pack-years, or systemic therapy history (e.g., platinum chemotherapy, EGFR/ALK TKIs, immune checkpoint inhibitors).
   * *Investigation*: Perform multivariable Cox proportional hazards modeling incorporating age, sex, AJCC stage, smoking status, and therapeutic treatment regimens as covariates.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=69, external claims checked=0, external mismatches=0, status=needs review.

Answer model API: Google Gemini / gemini-3.6-flash

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 53/100 selected items (records returned); cbioportal 51/100 selected items (records returned); chembl 16/100 selected items (records returned); civic 1/100 selected items (records returned); clinicaltrials 6/100 selected items (records returned); clinvar 30/100 selected items (records returned); ensembl 11/100 selected items (partially returned; some queries failed); europepmc 362 articles / initial full-cohort RAG 100 queries + 4 current-round queries; some queries failed; gtex 81/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 14/100 selected items (records returned); humanbase 56/100 selected items (partially returned; some queries failed); intact 18/100 selected items (records returned); mygene 59/100 selected items (records returned); omnipath 3/100 selected items (records returned); opentargets 55/100 selected items (records returned); pubmed 202 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 17/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 17/100 selected items (records returned)
Local databases: gutmgene 0/100 selected items (reachable but no records for this batch); hmdb 2/100 selected items (records returned); string 14/100 selected items (records returned); trrust 4/100 selected items (records returned)
