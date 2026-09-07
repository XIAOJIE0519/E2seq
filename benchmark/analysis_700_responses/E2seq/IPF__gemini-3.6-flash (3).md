# idiopathic pulmonary fibrosis (IPF) - gemini-3.6-flash

- Benchmark system: E2seq + Agent RAG
- Repeat: 5
- Task type: PROGNOSIS
- Tissue / sample source: lung tissue
- Comparison or endpoint: all-cause mortality
- Answer input cohort: Discovery/Core only
- Selected items: 100
- Input fields: gene name, effect size (log2FC/HR), P value, FDR
- E2seq Agent RAG: enabled
- Conversation memory: disabled
- Thinking mode: disabled
- Held-out validation data in prompt/RAG: no
- Model API: Google Gemini / gemini-3.6-flash
- Message SHA-256: d9fe74e971569d03f1ace047ce334e08d788b93d2057913b4d42b34da6d57d2f
- Response HTTP status: 200
- Prompt tokens: 69237
- Completion tokens: 51446
- Reasoning tokens: 20839
- Total tokens: 120683
- API requests reported: 4
- Elapsed seconds: 81.115
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 1387.824
- Question handoff seconds: 1401.194
- Final benchmark system: E2seq; file rank 3/5; original repeat 5; model vendor: Google Gemini

---
### Data-Quality Warning & Validation Disclaimer

* **Data-Quality Warning**: The primary statistical ledger contains severe numerical anomalies and technical saturation among a subset of features. Specifically, 10 features display extreme, identical hazard ratios (e.g., $\text{HR} = 1.93 \times 10^{-22}$ for *MIR221*, *IHH*, *FAM75A2*, *OR2M2*, *XLOC_003303*, *DYDC2*; $\text{HR} = 5.18 \times 10^{21}$ for *CONTROL_A_33_P3222196*, *CONTROL_A_33_P3345409*, *DKFZP434L187*; $\text{HR} = 1.93 \times 10^{21}$ for *HCN4*) accompanied by saturated $P = 0$ and $\text{FDR} = 0$. These include non-gene microarray control probes. Such extreme values indicate numerical non-convergence, complete separation, or statistical artifact in the underlying Cox regression model. Direct quantitative effect sizes for these saturated features must be treated as unreliable and exploratory.
* **External Validation Disclaimer**: **External statistical validation was not performed** because no independent cohort survival dataset or external validation statistics were supplied. External database annotations (Reactome, STRING, QuickGO, PubMed records) provide contextual biological plausibility but do not constitute statistical replication.

---

### 1. Overall Biological Interpretation

The provided transcriptomic dataset evaluates lung tissue gene expression in relation to all-cause mortality in patients with idiopathic pulmonary fibrosis (IPF). Out of 100 unique features, 93 display a risk-associated direction ($\text{HR} > 1$), while 7 display a protective-associated direction ($\text{HR} < 1$, predominantly compromised by technical saturation or unannotated non-coding regions). 

Rather than isolated gene changes, the risk profile reflects a coordinated multi-lineage pathomechanistic cascade driving progressive end-stage lung failure:

1. **Innate Immune Recruitment & Neutrophilic Inflammation**: Co-elevation of chemokine ligands (*CXCL1*, *CXCL14*, *CCL7*), chemokine receptors (*CXCR1*), granulocyte activation markers (*CD177*, *S100A12*), and pro-inflammatory signaling molecules (*PROK2*) indicates that persistent innate immune cell infiltration and microvascular inflammation strongly correlate with poor overall survival.
2. **Extracellular Matrix (ECM) Disruption & Pericellular Remodeling**: Elevated levels of matrix degradation enzymes (*HTRA1*, *MMP25*), matricellular adhesive proteins (*SPP1* / osteopontin), basement membrane modifiers (*EFEMP1*), and proteoglycan synthetic enzymes (*CHST15*) reflect active architectural breakdown and aberrant fibrous matrix deposition.
3. **Aberrant Alveolar Epithelial Stress & Growth Factor Crosstalk**: Heightened expression of type II alveolar epithelial markers (*SFTPB*, *SFTA2*, *MUC1*) alongside growth factor pathways (*MET*, *HGF*, *NRG1*, *SPRY2*) highlights unresolving epithelial injury, defective alveolar repair, and hyperplastic epithelial-mesenchymal crosstalk.
4. **Membrane Organization & Cytoskeletal Dynamics**: Upregulation of PKC substrates governing membrane-actin dynamics (*MARCKS*, *BASP1*), vesicular trafficking GTPases (*RAB3D*, *RAB3IL1*), and transmembrane solute transporters (*SLC7A11*, *SLC6A8*) indicates high cellular motility, metabolic adaptation to oxidative stress, and active secretory functions across fibrotic tissue compartments.

---

### 2. Core Biological Programs

#### Program 1: Neutrophil Chemotaxis and Innate Inflammatory Signaling
* **Prognostic Association**: Risk-associated ($\text{HR} > 1$)
* **Major Supporting Genes**: *CXCL1* ($\text{HR} = 2.99$, $\text{FDR} = 3.73 \times 10^{-5}$), *CXCL14* ($\text{HR} = 2.38$, $\text{FDR} = 1.89 \times 10^{-5}$), *CCL7* ($\text{HR} = 3.02$, $\text{FDR} = 2.60 \times 10^{-5}$), *CXCR1* ($\text{HR} = 3.28$, $\text{FDR} = 1.60 \times 10^{-5}$), *CD177* ($\text{HR} = 2.72$, $\text{FDR} = 3.90 \times 10^{-5}$), *S100A12* ($\text{HR} = 2.53$, $\text{FDR} = 5.49 \times 10^{-6}$), *PROK2* ($\text{HR} = 3.65$, $\text{FDR} = 9.91 \times 10^{-6}$)
* **Standardized Pathway**: GO: Neutrophil Migration (GO:1990266) / KEGG: Chemokine signaling pathway (hsa04062)
* **Biological Rationale**: Chemokines (*CXCL1*, *CCL7*, *CXCL14*) bind G-protein-coupled receptors like *CXCR1* to recruit neutrophils and monocytes to damaged lung tissue. *S100A12* (calgranulin C) and *CD177* facilitate neutrophil transmigration and activation, driving proteolytic release and tissue injury.
* **Evidence Strength & Limitations**: High pathway recurrence and strong co-expression signals across multiple independent chemoattractants. *Limitation*: Bulk transcriptomics cannot distinguish whether higher transcript abundance stems from increased cell-intrinsic expression or higher local neutrophil density.

#### Program 2: Extracellular Matrix (ECM) Proteolysis and Structuring
* **Prognostic Association**: Risk-associated ($\text{HR} > 1$)
* **Major Supporting Genes**: *HTRA1* ($\text{HR} = 4.30$, $\text{FDR} = 2.57 \times 10^{-6}$), *SPP1* ($\text{HR} = 3.40$, $\text{FDR} = 3.99 \times 10^{-5}$), *MMP25* ($\text{HR} = 3.26$, $\text{FDR} = 1.28 \times 10^{-5}$), *EFEMP1* ($\text{HR} = 2.33$, $\text{FDR} = 2.73 \times 10^{-5}$), *CHST15* ($\text{HR} = 2.99$, $\text{FDR} = 2.09 \times 10^{-5}$), *FHL2* ($\text{HR} = 2.76$, $\text{FDR} = 2.76 \times 10^{-6}$)
* **Standardized Pathway**: Reactome: Degradation of the extracellular matrix (R-HSA-1474228) / GO: Extracellular matrix organization (GO:0030198)
* **Biological Rationale**: *SPP1* (osteopontin) acts as a central matricellular mediator driving fibroblast activation and macrophage polarization. Proteases like *HTRA1* and *MMP25* remodel fibrotic matrix architecture, while *EFEMP1* (fibulin-3) and *CHST15* (sulfotransferase) alter matrix stiffness and glycosaminoglycan composition.
* **Evidence Strength & Limitations**: Strongly supported by single-cell literature identifying *SPP1*+ macrophages in fibrotic lung niches. *Limitation*: RNA levels do not directly measure zymogen activation, enzymatic cleavage, or physical matrix cross-linking.

#### Program 3: Receptor Tyrosine Kinase (RTK) Axis & Alveolar Epithelial Stress
* **Prognostic Association**: Risk-associated ($\text{HR} > 1$)
* **Major Supporting Genes**: *HGF* ($\text{HR} = 2.93$, $\text{FDR} = 1.09 \times 10^{-5}$), *MET* ($\text{HR} = 2.53$, $\text{FDR} = 1.47 \times 10^{-5}$), *NRG1* ($\text{HR} = 2.76$, $\text{FDR} = 6.85 \times 10^{-6}$), *SPRY2* ($\text{HR} = 3.26$, $\text{FDR} = 1.69 \times 10^{-5}$), *MUC1* ($\text{HR} = 2.32$, $\text{FDR} = 1.09 \times 10^{-5}$), *SFTPB* ($\text{HR} = 2.66$, $\text{FDR} = 3.37 \times 10^{-5}$), *SFTA2* ($\text{HR} = 2.25$, $\text{FDR} = 2.92 \times 10^{-5}$)
* **Standardized Pathway**: Reactome: Signaling by Receptor Tyrosine Kinases (R-HSA-9006934) / KEGG: Epithelial cell signaling
* **Biological Rationale**: Concurrent risk associations for hepatocyte growth factor (*HGF*), its receptor (*MET*), Neuregulin-1 (*NRG1*), and RTK inhibitor Sprouty-2 (*SPRY2*) suggest hyperactive or dysregulated RTK repair cascades in damaged alveolar epithelium. Elevated *MUC1*, *SFTPB*, and *SFTA2* reflect hyperplastic or stressed type II alveolar epithelial cells (AECII) undergoing repetitive damage.
* **Evidence Strength & Limitations**: Direct protein-protein interaction networks exist between HGF-MET and regulatory feedback loops (SPRY2). *Limitation*: HGF/MET signaling has dual regenerative and pro-invasive roles, making net pathomechanistic direction difficult to infer without cell-type-specific functional assays.

#### Program 4: Cytoskeletal Membrane Organization, Vesicular Transport, and Metabolic Adaptation
* **Prognostic Association**: Risk-associated ($\text{HR} > 1$)
* **Major Supporting Genes**: *MARCKS* ($\text{HR} = 4.00$, $\text{FDR} = 2.12 \times 10^{-5}$), *BASP1* ($\text{HR} = 3.77$, $\text{FDR} = 1.89 \times 10^{-5}$), *RAB3D* ($\text{HR} = 3.08$, $\text{FDR} = 2.11 \times 10^{-5}$), *RAB3IL1* ($\text{HR} = 3.84$, $\text{FDR} = 5.73 \times 10^{-6}$), *SLC7A11* ($\text{HR} = 3.52$, $\text{FDR} = 1.09 \times 10^{-5}$), *SLC6A8* ($\text{HR} = 3.21$, $\text{FDR} = 8.66 \times 10^{-6}$)
* **Standardized Pathway**: GO: Plasma membrane organization (GO:0007009) / GO: Vesicle-mediated transport (GO:0016192)
* **Biological Rationale**: *MARCKS* and *BASP1* regulate actin filament cross-linking, membrane fluidity, and exocytosis. *RAB3D* and *RAB3IL1* orchestrate secretory vesicle docking, facilitating pro-inflammatory cytokine and collagen secretion. *SLC7A11* (cystine/glutamate antiporter xCT) manages intracellular glutathione synthesis to counteract oxidative stress in expanding fibrotic cells.
* **Evidence Strength & Limitations**: STRING interaction networks confirm physical and functional binding between MARCKS, BASP1, and calmodulin-like proteins. *Limitation*: These metabolic and structural programs are broadly expressed across multiple lung cell types.

---

### 3. Key Genes and Interaction Modules

| Key Gene / Module | Dataset Association | Potential Role in Biological Programs | Nature of Proposed Gene-Gene Relationship |
| :--- | :--- | :--- | :--- |
| **HTRA1** | Risk-associated ($\text{HR} = 4.30$, $\text{FDR} = 2.57 \times 10^{-6}$) | Extracellular serine protease; drives pericellular ECM degradation and releases matrix-bound growth factors (e.g., TGF-$\beta$). | **Pathway co-membership**: Shares matrix degradation pathways with *MMP25* and *EFEMP1*. |
| **MARCKS** | Risk-associated ($\text{HR} = 4.00$, $\text{FDR} = 2.12 \times 10^{-5}$) | PKC substrate anchoring actin to plasma membrane; promotes cellular motility and exocytosis. | **Co-expression & Pathway co-membership**: Co-expressed with *BASP1*; shared binding to calmodulin-like proteins (*CALML4*/*CALML6*). |
| **SPP1** (Osteopontin) | Risk-associated ($\text{HR} = 3.40$, $\text{FDR} = 3.99 \times 10^{-5}$) | Profibrotic cytokine secreted by pathogenic macrophages; stimulates fibroblast migration and ECM secretion. | **Direct physical & Receptor-ligand interaction**: Binds integrin receptors and *CD44*; STRING interaction with *FN1*. |
| **MET & HGF Axis** | Both Risk-associated (*HGF*: $\text{HR} = 2.93$; *MET*: $\text{HR} = 2.53$) | Growth factor-receptor pair governing epithelial repair, survival, and motility. | **Direct physical ligand-receptor interaction**: *HGF* binds *MET*; forms network module with *SPRY2*, *CBL*, and *MUC1*. |
| **CXCL1 & CXCR1 Module** | Both Risk-associated (*CXCL1*: $\text{HR} = 2.99$; *CXCR1*: $\text{HR} = 3.28$) | Chemokine-receptor pair driving neutrophil chemotaxis into alveolar airspaces. | **Direct physical ligand-receptor interaction**: *CXCL1* binds *CXCR1*; pathway co-membership with *CXCL14* and *CCL7*. |
| **SLC7A11** (xCT) | Risk-associated ($\text{HR} = 3.52$, $\text{FDR} = 1.09 \times 10^{-5}$) | Cystine/glutamate antiporter managing oxidative stress and ferroptosis resistance in remodeling tissue. | **Functional / Regulatory interaction**: STRING interaction with *CD44*; co-expression with metabolic stress markers (*STEAP4*, *ACOX2*). |
| **S100A12** | Risk-associated ($\text{HR} = 2.53$, $\text{FDR} = 5.49 \times 10^{-6}$) | Pro-inflammatory alarmin / DAMP promoting innate immune activation via RAGE and TLR4 signaling. | **Direct physical interaction**: Interacts with *AGER* (RAGE), *S100A8*, *S100A9*, and *TLR4* (STRING confidence > 0.95). |
| **MERTK** | Risk-associated ($\text{HR} = 3.70$, $\text{FDR} = 1.05 \times 10^{-5}$) | Receptor tyrosine kinase expressed by macrophages involved in efferocytosis and pro-resolving signaling. | **Co-expression**: Co-expressed with macrophage scavenger receptors (*STAB1*) and myeloid signaling markers. |
| **MUC1** | Risk-associated ($\text{HR} = 2.32$, $\text{FDR} = 1.09 \times 10^{-5}$) | Transmembrane mucin on alveolar epithelial cells; precursor to clinical serum biomarker KL-6. | **Co-expression & Pathway co-membership**: Co-expressed with alveolar epithelial markers (*SFTPB*, *SFTA2*, *PRSS8*). |
| **STAB1** (Stabilin-1) | Risk-associated ($\text{HR} = 3.29$, $\text{FDR} = 3.15 \times 10^{-5}$) | Scavenger receptor mediating endocytosis and cell trafficking in tissue macrophages. | **Co-expression**: Co-expressed with myeloid regulators *MERTK*, *PROK2*, and *CD177*. |

---

### 4. Validation Priorities

1. **SPP1+ Macrophage Pro-Fibrotic Axis**
   * **Category**: Mechanistic hypothesis
   * **Prioritization Rationale**: *SPP1* is a strong statistical predictor ($\text{HR} = 3.40$) and a validated hallmark of expanding pro-fibrotic macrophages in human lung fibrosis.
   * **Dataset Evidence**: $\text{HR} = 3.40$, $\text{FDR} = 3.99 \times 10^{-5}$; co-elevated with matrix modifiers (*HTRA1*, *MMP25*, *CHST15*).
   * **External Evidence**: Independent scRNA-seq studies (e.g., IPF Cell Atlas) consistently identify *SPP1*-high macrophages in diseased alveolar spaces.
   * **Next Steps**: Spatial transcriptomics and multiplex immunofluorescence on IPF lung biopsies to map *SPP1*+ macrophage interactions with *COL1A1*+ myofibroblasts.
   * **Conclusion Status**: **Supported hypothesis** (supported by extensive single-cell literature, though independent cohort statistical survival validation was not performed).

2. **CXCL1 / CXCL14 / S100A12 Neutrophil Activation Cascade**
   * **Category**: Biomarker
   * **Prioritization Rationale**: Neutrophil-driven airway inflammation correlates with rapid lung function decline in clinical IPF cohorts.
   * **Dataset Evidence**: Concurrent elevation of neutrophil chemokines (*CXCL1*, *CXCL14*, *CCL7*), receptors (*CXCR1*), and neutrophil markers (*CD177*, *S100A12*).
   * **External Evidence**: Published literature demonstrates elevated BAL fluid and serum S100A12 and CXCL1 levels in progressive IPF.
   * **Next Steps**: ELISA quantification of circulating S100A12, CXCL1, and CXCL14 proteins in plasma from prospective IPF patient cohorts.
   * **Conclusion Status**: **Supported hypothesis**.

3. **HTRA1 Matrix Proteolysis Inhibitory Validation**
   * **Category**: Therapeutic target
   * **Prioritization Rationale**: *HTRA1* demonstrates the highest robust statistical hazard ratio among annotated enzymes in this dataset ($\text{HR} = 4.30$).
   * **Dataset Evidence**: $\text{HR} = 4.30$, $P = 7.86 \times 10^{-10}$, $\text{FDR} = 2.57 \times 10^{-6}$.
   * **External Evidence**: HTRA1 cleaves pericellular matrix components and regulates TGF-$\beta$ bioavailability.
   * **Next Steps**: Genetic knockdown (siRNA/CRISPR) or small-molecule HTRA1 inhibition in patient-derived precision-cut lung slices (PCLS) to assess collagen deposition.
   * **Conclusion Status**: **Exploratory hypothesis** (therapeutic efficacy in lung fibrosis has not been established).

4. **SLC7A11-Mediated Redox Management in Fibrotic Remodeling**
   * **Category**: Mechanistic hypothesis
   * **Prioritization Rationale**: *SLC7A11* ($\text{HR} = 3.52$) protects fibrotic cells from ferroptosis and oxidative stress during rapid tissue remodeling.
   * **Dataset Evidence**: $\text{HR} = 3.52$, $\text{FDR} = 1.09 \times 10^{-5}$; co-expressed with stress response enzymes (*STEAP4*, *ACOX2*).
   * **External Evidence**: xCT inhibition sensitizes activated myofibroblasts to oxidative stress-induced apoptosis in non-pulmonary tissue models.
   * **Next Steps**: Evaluate ferroptosis sensitivity under SLC7A11 pharmacological blockade in primary human IPF lung fibroblasts.
   * **Conclusion Status**: **Exploratory hypothesis**.

5. **Cell-Composition Deconvolution and Tissue Heterogeneity Control**
   * **Category**: Confounding or composition check
   * **Prioritization Rationale**: Bulk transcriptomic survival signatures can reflect shifts in tissue cell composition (e.g., macrophage expansion, loss of healthy AECI cells) rather than cell-intrinsic transcriptional changes.
   * **Dataset Evidence**: Multi-lineage signatures (epithelial: *SFTPB*/*MUC1*; macrophage: *SPP1*/*MERTK*; neutrophil: *CD177*/*S100A12*) elevated simultaneously.
   * **External Evidence**: IPF histopathology shows dense cellular heterogeneity ranging from fibrotic foci to honeycomb cysts.
   * **Next Steps**: Perform single-cell reference bulk deconvolution (e.g., CIBERSORTx) to re-estimate hazard ratios after adjusting for cell-type proportions.
   * **Conclusion Status**: **Exploratory hypothesis** (methodological verification requirement).

---

### 5. Evidence Grounding

* **Direct Dataset Evidence**: Hazard ratios, P values, and FDR values from the primary survival analysis provide direct support for candidate prognostic associations (e.g., *HTRA1* $\text{HR} = 4.30$; *MARCKS* $\text{HR} = 4.00$; *SPP1* $\text{HR} = 3.40$). Saturation artifacts in features like *MIR221* and *IHH* are recognized as model non-convergence.
* **Pathway & Ontology Evidence**: Standardized functional annotations from GO (GO:1990266, GO:0030198) and Reactome (R-HSA-1474228, R-HSA-9006934) substantiate the enrichment of chemokine signaling, matrix degradation, and RTK activation.
* **Protein Interaction & Regulatory Evidence**: STRING records confirm direct physical binding between HGF–MET, CXCL1–CXCR1, and S100A12–AGER/TLR4, as well as shared complex membership for MARCKS–BASP1.
* **Disease & Literature Evidence**: Published studies link *SPP1*, *MUC1* (KL-6), *S100A12*, and *HGF* to IPF pathobiology and clinical mortality.
* **Evidence Independence vs. Overlap**: Databases such as QuickGO, Reactome, STRING, and MyGene draw from overlapping PubMed curation records and high-throughput experimental databases. Their concordance represents cross-database curation alignment rather than independent statistical validation.
* **Conflicting Evidence**: *HGF* and *MET* show risk-associated prognostic directions (*HGF*: $\text{HR} = 2.93$; *MET*: $\text{HR} = 2.53$) in bulk tissue survival analysis. However, literature classically describes HGF/MET signaling as protective/antifibrotic in epithelial damage models. This conflict likely indicates that elevated bulk *HGF*/*MET* reflects reactive, compensatory upregulation in response to severe structural tissue destruction rather than a primary pro-fibrotic driver.
* **Explicit Insufficient Evidence Labels**:
  - Direct causal role of candidate genes in driving patient death: **Insufficient evidence** (observational survival correlation cannot prove causality).
  - Independent statistical cohort validation: **Insufficient evidence** (external statistical validation was not performed).
  - Clinical efficacy of targeting HTRA1 or SLC7A11 in human IPF: **Insufficient evidence**.

---

### 6. Limitations and Alternative Explanations

1. **Model Non-Convergence and Technical Artifacts**: Extreme, identical hazard ratios (e.g., $1.93 \times 10^{-22}$ and $5.18 \times 10^{21}$) and zero P values for multiple non-coding RNAs, developmental genes (*IHH*), and microarray control probes (*CONTROL_A_33_P3222196*) demonstrate severe numerical instability or sparse event distribution in the primary survival regression. *Mitigation*: Perform penalized Cox proportional hazards regression (Ridge/Lasso) or non-parametric log-rank testing.
2. **Bulk Tissue Cell-Composition Shifts**: Increased expression of cell-type-specific markers (e.g., *CD177* for neutrophils, *SPP1* for macrophages, *SFTPB* for type II epithelial cells) may reflect altered cellular composition in end-stage fibrotic lungs rather than transcriptomic induction within specific cells. *Mitigation*: Apply single-cell deconvolution algorithms paired with single-cell RNA sequencing validation.
3. **Disease Stage and Tissue Harvesting Bias**: Lung tissue samples from IPF mortality studies often derive from surgical biopsies or explanted lungs at organ transplantation. These samples disproportionately capture end-stage structural destruction, tissue hypoxia, and terminal inflammatory cascades. *Mitigation*: Stratify survival models by baseline clinical severity metrics (FVC % predicted, DLCO % predicted).
4. **Confounding by Antifibrotic and Immunosuppressive Therapy**: Patient treatment histories (e.g., nintedanib, pirfenidone, or historical corticosteroid exposure) can significantly suppress or induce inflammatory and growth factor genes. *Mitigation*: Incorporate medication history as time-varying covariates in multivariate survival analysis.
5. **Association vs. Causation Ambiguity**: Genes strongly associated with all-cause mortality may serve as passive biomarkers of extensive tissue destruction rather than active driver genes of disease progression. *Mitigation*: Perform Mendelian randomization studies utilizing pulmonary cis-eQTLs or functional loss-of-function studies in human precision-cut lung slices.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=1, external claims checked=0, external mismatches=0, status=passed.

Answer model API: Google Gemini / gemini-3.6-flash

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 77/100 selected items (partially returned; some queries failed); cbioportal 78/100 selected items (records returned); chembl 13/100 selected items (partially returned; some queries failed); civic 8/100 selected items (records returned); clinicaltrials 48/100 selected items (records returned); clinvar 78/100 selected items (records returned); ensembl 25/100 selected items (partially returned; some queries failed); europepmc 860 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 83/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 78/100 selected items (records returned); humanbase 78/100 selected items (records returned); intact 81/100 selected items (partially returned; some queries failed); mygene 91/100 selected items (records returned); omnipath 47/100 selected items (records returned); opentargets 80/100 selected items (partially returned; some queries failed); pubmed 658 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 83/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 84/100 selected items (records returned)
Local databases: gutmgene 3/100 selected items (records returned); hmdb 32/100 selected items (records returned); string 79/100 selected items (records returned); trrust 25/100 selected items (records returned)
