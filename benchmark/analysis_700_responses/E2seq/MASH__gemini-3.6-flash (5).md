# metabolic dysfunction-associated steatohepatitis (MASH) - gemini-3.6-flash

- Benchmark system: E2seq + Agent RAG
- Repeat: 7
- Task type: DISEASE-STATE
- Tissue / sample source: liver tissue
- Comparison or endpoint: MASH/NASH versus healthy control
- Answer input cohort: Discovery/Core only
- Selected items: 100
- Input fields: gene name, effect size (log2FC/HR), P value, FDR
- E2seq Agent RAG: enabled
- Conversation memory: disabled
- Thinking mode: disabled
- Held-out validation data in prompt/RAG: no
- Model API: Google Gemini / gemini-3.6-flash
- Message SHA-256: f634f84e95c290ce4195eb13604b114b4c86ce8adb76238e59c436c955ac43b9
- Response HTTP status: 200
- Prompt tokens: 60043
- Completion tokens: 42815
- Reasoning tokens: 15651
- Total tokens: 102858
- API requests reported: 3
- Elapsed seconds: 101.938
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 1019.869
- Question handoff seconds: 1032.938
- Final benchmark system: E2seq; file rank 5/5; original repeat 7; model vendor: Google Gemini

---
### 1. Overall Biological Interpretation

The transcriptomic landscape comparing metabolic dysfunction-associated steatohepatitis (MASH) liver tissue to healthy controls reveals a profound shift in immune cell composition, microvascular remodeling, cellular stress responses, and metabolic pathway adaptation:

1. **Hepatic Myeloid Niche Remodeling**: A major feature is the replacement of homeostatic resident Kupffer cells with recruited lipid-associated macrophages (LAMs). Highly induced myeloid and lipid-handling markers (e.g., **TREM2**, **FABP5**, **CXCL10**) contrast with the downregulation of homeostatic resident Kupffer cell surface receptors (e.g., **TIMD4**, **MARCO**, **CD163**, **MRC1**, **FOLR2**, **CD5L**).
2. **Proteostasis, Ubiquitin System, and ER Stress Response**: Marked induction of ubiquitin-like modifier **UBD** (FAT10), chaperone precursor **PFDN6**, and ER cytoprotective factor **MANF** indicates activation of the ubiquitin-proteasome system and unfolded protein response under lipotoxic hepatic stress.
3. **Sinusoidal Endothelial and Structural Remodeling**: Downregulation of endothelial and vascular markers (**LYVE1**, **CDH5**, **VCAM1**, **TINAGL1**, **PCDH20**) reflects liver sinusoidal endothelial cell (LSEC) capillarization and disruption of healthy vascular architecture.
4. **Metabolic Reprogramming**: Significant alterations in lipid transport (**CETP** downregulated, **FABP5** upregulated) and one-carbon / transsulfuration pathways (**MTHFD1L** upregulated, **CBS** downregulated) highlight metabolic adaptations to persistent lipid accumulation and oxidative stress.

---

### 2. Core Biological Programs

```
+----------------------------------------------------------------------------------------------------+
| CORE BIOLOGICAL PROGRAM OVERVIEW                                                                   |
+------------------------------------+---------------+---------------------+-------------------------+
| Program Name                       | Direction     | Key Genes           | Primary Pathway         |
+------------------------------------+---------------+---------------------+-------------------------+
| 1. Lipid-Associated Macrophages    | Upregulated   | TREM2, FABP5, CXCL10| GO:0002250 / KEGG:04657 |
| 2. Homeostatic Kupffer Cell Loss   | Downregulated | TIMD4, MARCO, CD163 | GO:0006954 / Reactome   |
| 3. ER Stress & Proteostasis        | Upregulated   | UBD, MANF, PFDN6    | KEGG:hsa04141           |
| 4. Sinusoidal Microvascular Loss   | Downregulated | LYVE1, CDH5, VCAM1  | GO:0098742              |
| 5. One-Carbon / Sulfur Metabolism  | Shifted       | MTHFD1L, GGTLC1, CBS| KEGG:hsa00270           |
+------------------------------------+---------------+---------------------+-------------------------+
```

#### Program 1: Lipid-Associated Macrophage (LAM) Activation & Chemokine Signaling
* **Direction**: Upregulated in MASH
* **Major Supporting Genes**: **TREM2** ($\log_2\text{FC} = +4.91$, $\text{FDR} = 3.90 \times 10^{-9}$), **FABP5** ($\log_2\text{FC} = +2.85$, $\text{FDR} = 4.94 \times 10^{-8}$), **CXCL10** ($\log_2\text{FC} = +3.46$, $\text{FDR} = 1.18 \times 10^{-7}$), **TNFRSF12A** ($\log_2\text{FC} = +3.27$, $\text{FDR} = 1.33 \times 10^{-7}$), **CAPG** ($\log_2\text{FC} = +2.57$, $\text{FDR} = 3.12 \times 10^{-7}$).
* **Standardized Pathway**: GO:0002250 (Adaptive Immune Response) / KEGG: hsa04657 (IL-17 signaling pathway) / Reactome: R-HSA-6798695 (Neutrophil degranulation).
* **Biological Explanation**: TREM2 and FABP5 define recruited lipid-associated macrophages that aggregate around lipid-laden hepatocytes. Chemokine CXCL10 and TWEAK receptor TNFRSF12A coordinate monocyte recruitment and pro-inflammatory signaling during liver injury.
* **Evidence Strength & Limitations**: Strong input statistical signal ($\text{FDR} < 1 \times 10^{-6}$). *Limitation*: Bulk RNA sequencing cannot differentiate increased expression per cell from increased proportional cell abundance; external statistical validation was not performed on an independent cohort.

#### Program 2: Loss of Homeostatic Resident Kupffer Cell Signature
* **Direction**: Downregulated in MASH
* **Major Supporting Genes**: **TIMD4** ($\log_2\text{FC} = -4.28$, $\text{FDR} = 1.50 \times 10^{-8}$), **MARCO** ($\log_2\text{FC} = -2.84$, $\text{FDR} = 3.46 \times 10^{-10}$), **CD163** ($\log_2\text{FC} = -2.52$, $\text{FDR} = 3.12 \times 10^{-9}$), **MRC1** ($\log_2\text{FC} = -2.10$, $\text{FDR} = 1.88 \times 10^{-8}$), **FOLR2** ($\log_2\text{FC} = -2.04$, $\text{FDR} = 4.30 \times 10^{-7}$), **CD5L** ($\log_2\text{FC} = -2.90$, $\text{FDR} = 8.31 \times 10^{-8}$), **SPIC** ($\log_2\text{FC} = -2.62$, $\text{FDR} = 1.34 \times 10^{-8}$).
* **Standardized Pathway**: GO:0006954 (Inflammatory Response) / GO:0030450 (Regulation of complement activation) / QuickGO: BP:immune complex clearance.
* **Biological Explanation**: TIMD4, MARCO, CD163, MRC1, and CD5L represent core cell-surface markers of healthy embryonic-derived resident Kupffer cells. SPIC is a lineage-determining transcription factor for tissue-resident macrophages. Concurrent downregulation across these markers indicates depletion or displacement of resident Kupffer cells by infiltrative monocyte-derived cells.
* **Evidence Strength & Limitations**: Coherent negative fold-changes across multiple lineage surface markers. *Limitation*: Reflects tissue cell-type composition shifts rather than direct transcriptional suppression within individual resident cells; external statistical validation was not performed on an independent cohort.

#### Program 3: Proteostasis, Ubiquitin Proteasome System, and ER Stress
* **Direction**: Upregulated in MASH
* **Major Supporting Genes**: **UBD** ($\log_2\text{FC} = +4.15$, $\text{FDR} = 1.33 \times 10^{-10}$), **MANF** ($\log_2\text{FC} = +1.85$, $\text{FDR} = 6.05 \times 10^{-7}$), **TP53I3** ($\log_2\text{FC} = +3.26$, $\text{FDR} = 2.69 \times 10^{-10}$), **PFDN6** ($\log_2\text{FC} = +1.49$, $\text{FDR} = 8.31 \times 10^{-8}$), **CAST** ($\log_2\text{FC} = +4.02$, $\text{FDR} = 7.02 \times 10^{-8}$).
* **Standardized Pathway**: KEGG: hsa04141 (Protein processing in endoplasmic reticulum) / Reactome: R-HSA-8951664 (Neddylation) / GO:0031072 (Heat shock protein binding).
* **Biological Explanation**: UBD (FAT10) targets proteins for proteasomal degradation under inflammatory and oxidative stress. MANF and PFDN6 assist chaperone-mediated folding in the ER lumen. Upregulation of these factors indicates an ongoing response to lipotoxic protein misfolding.
* **Evidence Strength & Limitations**: Pronounced induction of key proteostatic markers. *Limitation*: Protein-level turnover and enzymatic degradation kinetics require functional biochemical assays; external statistical validation was not performed on an independent cohort.

#### Program 4: Sinusoidal Endothelial Microvascular Architecture Disruption
* **Direction**: Downregulated in MASH
* **Major Supporting Genes**: **LYVE1** ($\log_2\text{FC} = -2.73$, $\text{FDR} = 5.22 \times 10^{-9}$), **CDH5** ($\log_2\text{FC} = -1.38$, $\text{FDR} = 5.56 \times 10^{-7}$), **VCAM1** ($\log_2\text{FC} = -2.38$, $\text{FDR} = 4.97 \times 10^{-10}$), **TINAGL1** ($\log_2\text{FC} = -1.78$, $\text{FDR} = 4.72 \times 10^{-8}$), **PCDH20** ($\log_2\text{FC} = -4.59$, $\text{FDR} = 1.47 \times 10^{-8}$).
* **Standardized Pathway**: GO:0098742 (Cell-Cell Adhesion Via Plasma-Membrane Adhesion Molecules) / Reactome: R-HSA-216083 (Integrin cell surface interactions).
* **Biological Explanation**: LYVE1 and CDH5 (VE-cadherin) maintain the specialized fenestrated phenotype of liver sinusoidal endothelial cells (LSECs). Downregulation of these junctional and extracellular matrix factors aligns with LSEC capillarization and microvascular remodeling.
* **Evidence Strength & Limitations**: Consistent downregulation across structural endothelial molecules. *Limitation*: Cannot distinguish physical loss of sinusoids from loss of fenestrations without structural imaging; external statistical validation was not performed on an independent cohort.

#### Program 5: One-Carbon and Transsulfuration Metabolic Reprogramming
* **Direction**: Shifted (MTHFD1L & GGTLC1 Upregulated; CBS Downregulated)
* **Major Supporting Genes**: **MTHFD1L** ($\log_2\text{FC} = +1.72$, $\text{FDR} = 1.93 \times 10^{-7}$), **GGTLC1** ($\log_2\text{FC} = +2.33$, $\text{FDR} = 2.04 \times 10^{-8}$), **CBS** ($\log_2\text{FC} = -1.25$, $\text{FDR} = 1.80 \times 10^{-7}$), **SCLY** ($\log_2\text{FC} = -1.28$, $\text{FDR} = 5.21 \times 10^{-7}$).
* **Standardized Pathway**: KEGG: hsa00270 (Cysteine and methionine metabolism) / Reactome: R-HSA-161463 (One-carbon metabolism).
* **Biological Explanation**: Mitochondrial MTHFD1L supplies one-carbon units for NADPH synthesis and redox balance. Downregulation of cystathionine beta-synthase (CBS) indicates reduced transsulfuration capacity, while GGTLC1 upregulation reflects glutathione cleavage and recycling under oxidative stress.
* **Evidence Strength & Limitations**: High statistical significance across primary metabolic enzymes. *Limitation*: Gene expression changes do not directly measure metabolite pool sizes or enzyme activity; external statistical validation was not performed on an independent cohort.

---

### 3. Key Genes and Interaction Modules

1. **TREM2**
   * **Statistical Direction**: Upregulated ($\log_2\text{FC} = +4.91$, $\text{FDR} = 3.90 \times 10^{-9}$).
   * **Role in Core Program**: Primary driver of Program 1 (LAM Activation).
   * **Relationship Nature**: **Co-expression & Pathway Co-membership** with FABP5 and CSF1R (OmniPath/ConnectomeDB2025 link). *Note*: This is shared expression in infiltrative myeloid cells, not demonstrated direct physical interaction.
2. **TIMD4**
   * **Statistical Direction**: Downregulated ($\log_2\text{FC} = -4.28$, $\text{FDR} = 1.50 \times 10^{-8}$).
   * **Role in Core Program**: Core receptor in Program 2 (Kupffer Cell Homeostasis).
   * **Relationship Nature**: **Co-expression & Pathway Co-membership** with MARCO and CD163 in resident phagocytes.
3. **UBD (FAT10)**
   * **Statistical Direction**: Upregulated ($\log_2\text{FC} = +4.15$, $\text{FDR} = 1.33 \times 10^{-10}$).
   * **Role in Core Program**: Effector in Program 3 (Proteostasis and ER Stress).
   * **Relationship Nature**: **Regulatory Interaction & Pathway Co-membership** within ubiquitin-proteasome processing pathways.
4. **MARCO**
   * **Statistical Direction**: Downregulated ($\log_2\text{FC} = -2.84$, $\text{FDR} = 3.46 \times 10^{-10}$).
   * **Role in Core Program**: Scavenger receptor in Program 2 (Kupffer Cell Homeostasis).
   * **Relationship Nature**: **STRING Network Association & Pathway Co-membership** with CD36 and CD163 in lipid uptake and clearance.
5. **LYVE1**
   * **Statistical Direction**: Downregulated ($\log_2\text{FC} = -2.73$, $\text{FDR} = 5.22 \times 10^{-9}$).
   * **Role in Core Program**: Marker in Program 4 (Sinusoidal Microvascular Loss).
   * **Relationship Nature**: **Co-expression** with CDH5 in liver sinusoidal endothelial cell lining.
6. **CXCL10**
   * **Statistical Direction**: Upregulated ($\log_2\text{FC} = +3.46$, $\text{FDR} = 1.18 \times 10^{-7}$).
   * **Role in Core Program**: Pro-inflammatory mediator in Program 1 (LAM Activation).
   * **Relationship Nature**: **Indirect Regulatory Interaction** via CXCR3 receptor axis driving immune recruitment.
7. **MANF**
   * **Statistical Direction**: Upregulated ($\log_2\text{FC} = +1.85$, $\text{FDR} = 6.05 \times 10^{-7}$).
   * **Role in Core Program**: Cytoprotective factor in Program 3 (ER Stress Response).
   * **Relationship Nature**: **Direct Physical Interaction / Chaperone Association** (STRING network link) with HSPA5 (BiP) in the ER lumen.
8. **MTHFD1L**
   * **Statistical Direction**: Upregulated ($\log_2\text{FC} = +1.72$, $\text{FDR} = 1.93 \times 10^{-7}$).
   * **Role in Core Program**: Rate-limiting mitochondrial enzyme in Program 5 (One-Carbon Metabolism).
   * **Relationship Nature**: **Pathway Co-membership** with folate cycle enzymes and indirect metabolic linkage to CBS.
9. **CD163**
   * **Statistical Direction**: Downregulated ($\log_2\text{FC} = -2.52$, $\text{FDR} = 3.12 \times 10^{-9}$).
   * **Role in Core Program**: Scavenger receptor in Program 2 (Kupffer Cell Homeostasis).
   * **Relationship Nature**: **Direct Physical Interaction / Network Edge** (STRING database record) with MRC1 and SIGLEC1.
10. **TCF7L1**
    * **Statistical Direction**: Downregulated ($\log_2\text{FC} = -1.53$, $\text{FDR} = 1.99 \times 10^{-7}$).
    * **Role in Core Program**: Transcriptional regulator of homeostatic Wnt signaling.
    * **Relationship Nature**: **Direct Physical / Regulatory Interaction** (STRING network record) with CTNNB1 (beta-catenin) and FOXM1 ($\log_2\text{FC} = +2.14$).

---

### 4. Validation Priorities

```
+----------------------------------------------------------------------------------------------------+
| VALIDATION PRIORITIES                                                                              |
+-------------------+---------------------+-----------------------------------+----------------------+
| Target Axis       | Classification      | Primary Method                    | Status               |
+-------------------+---------------------+-----------------------------------+----------------------+
| 1. Kupffer/LAM    | Mechanistic         | Single-cell RNA-seq / Spatial IF  | Supported Hypothesis |
| 2. LSEC Remodel   | Confounding Check   | CD31/LYVE1 EM Fenestration Staining| Supported Hypothesis |
| 3. UBD (FAT10)    | Therapeutic Target  | Hepatocyte siRNA lipotoxicity test| Exploratory Hypoth.  |
| 4. CBS / Folate   | Biomarker           | Targeted GSH/SAMe metabolomics    | Exploratory Hypoth.  |
| 5. TCF7L1/FOXM1   | Interaction Network | Co-IP & Wnt Luciferase reporter   | Exploratory Hypoth.  |
+-------------------+---------------------+-----------------------------------+----------------------+
```

1. **Shift from Resident Kupffer Cells to TREM2+ Lipid-Associated Macrophages**
   * **Classification**: Mechanistic hypothesis
   * **Why Prioritize**: Explains the reciprocal contrast between TREM2/FABP5 upregulation and TIMD4/MARCO downregulation in bulk tissue.
   * **Dataset Evidence**: TREM2 ($\log_2\text{FC} = +4.91$) vs. TIMD4 ($\log_2\text{FC} = -4.28$) and MARCO ($\log_2\text{FC} = -2.84$).
   * **External Evidence**: Single-cell studies in human MASH (PMID: 39497821) confirm TREM2+ LAM accumulation.
   * **Next Validation Step**: Single-cell RNA-seq or multiplex spatial immunofluorescence on human MASH liver biopsies.
   * **Status**: **Supported hypothesis** (*Note: external statistical validation was not performed on an independent cohort*).

2. **Sinusoidal Endothelial Capillarization and Fenestration Loss**
   * **Classification**: Confounding or composition check
   * **Why Prioritize**: Clarifies whether endothelial gene downregulation represents loss of endothelial cells or phenotypic capillarization.
   * **Dataset Evidence**: Concurrent decrease in LYVE1 ($\log_2\text{FC} = -2.73$), CDH5 ($\log_2\text{FC} = -1.38$), and TINAGL1 ($\log_2\text{FC} = -1.78$).
   * **External Evidence**: LSEC capillarization is a recognized feature of progressive liver fibrosis.
   * **Next Validation Step**: Transmission electron microscopy of sinusoidal fenestrations and CD31/LYVE1 co-staining.
   * **Status**: **Supported hypothesis** (*Note: external statistical validation was not performed on an independent cohort*).

3. **Targeting UBD (FAT10) and ER Stress Pathways for Hepatoprotection**
   * **Classification**: Therapeutic target
   * **Why Prioritize**: UBD induction ($\log_2\text{FC} = +4.15$) reflects lipotoxic proteasomal strain and inflammatory activation.
   * **Dataset Evidence**: UBD upregulation coupled with cytoprotective MANF induction ($\log_2\text{FC} = +1.85$).
   * **External Evidence**: Literature connects FAT10 to NF-$\kappa$B stabilization and protein aggregate clearance in liver disease.
   * **Next Validation Step**: siRNA knockdown or CRISPR knockout of UBD in human primary hepatocytes exposed to palmitate/oleate.
   * **Status**: **Exploratory hypothesis** (*Note: drug presence or gene induction does not automatically confer therapeutic efficacy; external statistical validation was not performed on an independent cohort*).

4. **Transsulfuration and One-Carbon Metabolite Ratios as Metabolic Biomarkers**
   * **Classification**: Biomarker
   * **Why Prioritize**: Decreased CBS ($\log_2\text{FC} = -1.25$) paired with elevated MTHFD1L ($\log_2\text{FC} = +1.72$) points to altered glutathione and S-adenosylmethionine (SAMe) flux.
   * **Dataset Evidence**: Reciprocal expression shifts in one-carbon/transsulfuration enzymes.
   * **External Evidence**: CBS deficiency impairs hepatic transsulfuration and lowers liver glutathione reserves.
   * **Next Validation Step**: Targeted LC-MS/MS measurement of serum SAMe, homocysteine, and GSH/GSSG ratios in MASH patient cohorts.
   * **Status**: **Exploratory hypothesis** (*Note: external statistical validation was not performed on an independent cohort*).

5. **Wnt/Beta-Catenin Axis Modulation via TCF7L1 and FOXM1**
   * **Classification**: Interaction / network hypothesis
   * **Why Prioritize**: Both TCF7L1 (downregulated) and FOXM1 (upregulated) connect to CTNNB1, regulating liver zonation and hepatocyte proliferation.
   * **Dataset Evidence**: TCF7L1 ($\log_2\text{FC} = -1.53$) and FOXM1 ($\log_2\text{FC} = +2.14$).
   * **External Evidence**: STRING network interactions bind both factors to CTNNB1 signaling.
   * **Next Validation Step**: Co-immunoprecipitation and TOPFlash Wnt reporter assays in steatotic hepatocyte models.
   * **Status**: **Exploratory hypothesis** (*Note: external statistical validation was not performed on an independent cohort*).

---

### 5. Evidence Grounding

* **Direct Input Dataset Evidence**: UBD ($\log_2\text{FC} = +4.15$), TREM2 ($\log_2\text{FC} = +4.91$), TIMD4 ($\log_2\text{FC} = -4.28$), PCDH20 ($\log_2\text{FC} = -4.59$), FABP5 ($\log_2\text{FC} = +2.85$), CXCL10 ($\log_2\text{FC} = +3.46$), MARCO ($\log_2\text{FC} = -2.84$), LYVE1 ($\log_2\text{FC} = -2.73$), MTHFD1L ($\log_2\text{FC} = +1.72$), CBS ($\log_2\text{FC} = -1.25$). All ledger genes satisfy $\text{FDR} \le 0.01$.
* **Pathway / Ontology Evidence**: GO:0098742 (Cell-cell adhesion), GO:0030450 (Complement activation), KEGG: hsa00270 (Cysteine and methionine metabolism), Reactome: R-HSA-8951664 (Neddylation), Reactome: R-HSA-6798695 (Neutrophil degranulation).
* **Protein Interaction / Regulatory Evidence**: STRING network links CTNNB1 with CDH5, FOXM1, and TCF7L1; C3 with CFP and CR1; CD163 with MRC1 and SIGLEC1; CD36 with CD163 and MARCO; HSPA5 with CD5L and MANF; OmniPath/ConnectomeDB2025 links CSF1R and TREM2.
* **Disease & Tissue-Specific Evidence**: GTEx and HPA expression records confirm baseline liver tissue expression for CBS, CD5L, and MARCO. GWAS records associate TREM2, FABP5, and CETP with metabolic lipid traits.
* **Published Literature Evidence**: Europe PMC and PubMed literature records (e.g., PMID: 39497821, 38323273) support efferocytosis pathways, MTHFD1L metabolic activity, and TREM2+ macrophage emergence in MASH.
* **Evidence Overlap & Conflicts**: Database records (such as STRING and QuickGO) share underlying PubMed source literature for protein annotations (e.g., CD163-MRC1 co-citation). No internal direction conflicts exist in the statistical ledger except for CAST, which was represented by two concordant upregulated rows ($\log_2\text{FC} = +4.02$).
* **External Statistical Replication Status**: *External statistical validation was not performed on an independent cohort in this analysis.*

---

### 6. Limitations and Alternative Explanations

1. **Cell Composition Shifts vs. Cell-Intrinsic Transcriptional Repression**:
   * Bulk liver tissue transcriptomics captures signals from hepatocytes, Kupffer cells, endothelial cells, stellate cells, and infiltrating immune cells.
   * *Impact*: Reduced expression of Kupffer cell markers (TIMD4, MARCO) and elevated expression of LAM markers (TREM2, FABP5) likely reflects changes in cell-type proportions rather than transcriptional repression within intact resident cells.
   * *Investigation*: Validate using single-cell RNA sequencing or flow cytometry on isolated non-parenchymal cell fractions.

2. **Absence of Independent Cohort Statistical Replication**:
   * *Impact*: Although internal statistical significance is strong ($\text{FDR} < 1 \times 10^{-6}$), external statistical validation on an independent clinical dataset was not provided.
   * *Investigation*: Perform cross-cohort validation using public MASH microarrays or RNA-seq cohorts (e.g., GEO datasets GSE130970 or GSE135251).

3. **Association vs. Causation Ambiguity**:
   * *Impact*: Upregulation of stress-response genes (UBD, MANF) may represent a protective compensatory mechanism to limit tissue injury rather than a pathogenic driver of MASH.
   * *Investigation*: Conduct functional gain- and loss-of-function experiments in primary hepatocyte organoid cultures under lipotoxic strain.

4. **Confounding by Fibrosis Stage and Disease Severity**:
   * *Impact*: Tissue samples from MASH patients often span diverse stages of fibrosis (F0–F4). Vascular markers (LYVE1, CDH5) and chemokines (CXCL10) strongly correlate with sinusoidal capillarization and stage of fibrosis.
   * *Investigation*: Stratify patient cohorts by NAFLD Activity Score (NAS) and histological fibrosis stage.

5. **Functional Significance of Non-Coding Features**:
   * *Impact*: Top-ranking features include non-coding RNAs and pseudogenes (e.g., SNORD140, MIR4647, GLUD1P2, CES1P2).
   * *Investigation*: Perform targeted qPCR validation, subcellular fractionation, and microRNA target-reporter assays to establish functional relevance.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=0, external claims checked=0, external mismatches=0, status=passed.

Answer model API: Google Gemini / gemini-3.6-flash

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 93/100 selected items (records returned); cbioportal 85/100 selected items (records returned); chembl 33/100 selected items (partially returned; some queries failed); civic 4/100 selected items (records returned); clinicaltrials 40/100 selected items (records returned); clinvar 82/100 selected items (records returned); ensembl 42/100 selected items (partially returned; some queries failed); europepmc 897 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 75/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 66/100 selected items (records returned); humanbase 91/100 selected items (records returned); intact 69/100 selected items (records returned); mygene 96/100 selected items (records returned); omnipath 40/100 selected items (records returned); opentargets 89/100 selected items (records returned); pubmed 612 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 69/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 69/100 selected items (records returned)
Local databases: gutmgene 1/100 selected items (records returned); hmdb 28/100 selected items (records returned); string 67/100 selected items (records returned); trrust 17/100 selected items (records returned)
