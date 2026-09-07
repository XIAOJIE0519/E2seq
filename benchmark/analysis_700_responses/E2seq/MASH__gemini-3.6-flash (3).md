# metabolic dysfunction-associated steatohepatitis (MASH) - gemini-3.6-flash

- Benchmark system: E2seq + Agent RAG
- Repeat: 5
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
- Prompt tokens: 60005
- Completion tokens: 39897
- Reasoning tokens: 19915
- Total tokens: 99902
- API requests reported: 3
- Elapsed seconds: 51.364
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 1019.869
- Question handoff seconds: 1032.938
- Final benchmark system: E2seq; file rank 3/5; original repeat 5; model vendor: Google Gemini

---
### 1. Overall Biological Interpretation

The transcriptomic dataset comparing metabolic dysfunction-associated steatohepatitis (MASH) liver tissue against healthy controls reveals a profound, multi-compartmental remodeling of hepatic cellular composition, immune signaling, non-coding RNA expression, and metabolic homeostasis. 

Rather than isolated single-gene alterations, the results reflect coordinated shifts across four primary biological axes:
1. **Macrophage Identity Reprogramming:** A striking loss of embryonic tissue-resident Kupffer cell homeostatic markers (e.g., `TIMD4`, `MARCO`, `CD163`, `MRC1`, `CD5L`, `SPIC`, `FOLR2`) juxtaposed with robust induction of lipid-associated macrophage (LAM) and pro-inflammatory signaling programs (`TREM2`, `FABP5`, `CXCL10`, `TNFRSF12A`).
2. **Sinusoidal Endothelial Dysfunction:** Downregulation of key liver sinusoidal endothelial cell (LSEC) structural and cell-adhesion determinants (`LYVE1`, `CDH5`, `VCAM1`, `LDB2`, `PCDH20`), reflecting sinusoidal capillarization and loss of fenestration integrity.
3. **Mitochondrial Stress & Proteostasis Perturbation:** Marked upregulation of mitochondrial electron transport/translocation components (`UQCRBP1`, `CYCS`, `TIMM17A`) and proteotoxic/ER stress responders (`UBD`, `MANF`), alongside downregulation of core hepatic metabolic regulators (`CETP`, `CBS`, `SCLY`).
4. **Translational Machinery & NcRNA Activation:** Induction of multiple transfer RNA transcripts (`TRNK`, `TRNS1`, `TRNC`, `TRNL2`, `TRNY`) and small nucleolar/microRNAs (`SNORD140`, `MIR4647`, `MIR12136`), paired with downregulation of regulatory long non-coding RNAs (`CD81-AS1`, `DIO3OS`).

*Note:* External statistical validation was not performed on an independent cohort in this analysis context; all effect sizes and significance metrics derive directly from the uploaded differential transcriptomic dataset.

---

### 2. Core Biological Programs

```
+---------------------------------------------------------------------------------------------------+
| CORE BIOLOGICAL PROGRAM OVERVIEW                                                                  |
+------------------------------------+---------------+----------------------------------------------+
| Program Name                       | Direction     | Key Genes                                    |
+------------------------------------+---------------+----------------------------------------------+
| 1. Lipid-Associated Macrophage     | Upregulated   | TREM2, FABP5, CXCL10, TNFRSF12A, CAPG        |
|    Activation & Inflammation       |               |                                              |
| 2. Depletion of Resident Kupffer   | Downregulated | TIMD4, MARCO, CD163, MRC1, CD5L, SPIC, FOLR2 |
|    Cell Identity                   |               |                                              |
| 3. Sinusoidal Endothelial &        | Downregulated | LYVE1, CDH5, VCAM1, LDB2, PCDH20, TINAGL1    |
|    Vascular Integrity              |               |                                              |
| 4. Mitochondrial Stress &          | Mixed /       | UBD, UQCRBP1, CYCS, MANF (Up);               |
|    Proteostasis Perturbation       | Upregulated   | CETP, CBS, SCLY (Down)                       |
| 5. NcRNA & Translational           | Upregulated   | TRNC, TRNL2, TRNY, TRNK, TRNS1, SNORD140     |
|    Machinery Alterations           | tRNAs         |                                              |
+------------------------------------+---------------+----------------------------------------------+
```

#### Program 1: Lipid-Associated Macrophage (LAM) Activation & Pro-Inflammatory Signaling
* **Direction:** Upregulated in MASH
* **Major Supporting Genes:** `TREM2` (log2FC = 4.911, FDR = 3.899e-09), `FABP5` (log2FC = 2.849, FDR = 4.938e-08), `CXCL10` (log2FC = 3.463, FDR = 1.183e-07), `TNFRSF12A` (log2FC = 3.271, FDR = 1.334e-07), `CAPG` (log2FC = 2.567, FDR = 3.116e-07).
* **Standardized Pathway:** GO: Immune Response (`GO:0006954`); Reactome: Innate Immune System (`R-HSA-168249`); KEGG: Cytokine-cytokine receptor interaction (`hsa04060`).
* **Biological Rationale:** `TREM2` and `FABP5` are canonical markers of lipid-associated macrophages that expand in steatotic liver tissue to process lipid overload and apoptotic debris. `CXCL10` and `TNFRSF12A` (Fn14) recruit peripheral immune cells and drive inflammatory remodeling, indicating active immune cell infiltration and activation.
* **Evidence Strength & Limitations:** Extremely high effect size and statistical significance in the direct input dataset (`TREM2` log2FC = 4.911). A major limitation is that bulk RNA-seq cannot distinguish whether elevated transcript levels stem from cell-intrinsic transcriptional upregulation or an increased proportion of infiltrating macrophages.

#### Program 2: Depletion / Downregulation of Resident Kupffer Cell Identity
* **Direction:** Downregulated in MASH
* **Major Supporting Genes:** `TIMD4` (log2FC = -4.282, FDR = 1.502e-08), `MARCO` (log2FC = -2.844, FDR = 3.464e-10), `CD163` (log2FC = -2.517, FDR = 3.117e-09), `MRC1` (log2FC = -2.102, FDR = 1.877e-08), `CD5L` (log2FC = -2.899, FDR = 8.311e-08), `SPIC` (log2FC = -2.616, FDR = 1.341e-08), `FOLR2` (log2FC = -2.040, FDR = 4.299e-07), `CSF1R` (log2FC = -1.985, FDR = 3.844e-07).
* **Standardized Pathway:** GO: Regulation Of Complement Activation, Classical Pathway (`GO:0030450`); Reactome: Scavenger Receptors (`R-HSA-3000480`); KEGG: Phagosome (`hsa04145`).
* **Biological Rationale:** `TIMD4`, `MARCO`, `CD163`, `MRC1`, `CD5L`, and `SPIC` define the lineage identity of self-renewing, tissue-resident Kupffer cells responsible for immune tolerance and efferocytosis. Their broad downregulation indicates either severe loss/displacement of resident Kupffer cells or epigenetic silencing of homeostatic scavenger programs during chronic steatohepatitis.
* **Evidence Strength & Limitations:** High statistical concordance across 8 independent cell-surface receptor genes (all FDR < 5e-07). Limited by the ambiguity between true cellular cell death versus phenotypic downregulation of surface markers in chronic inflammation.

#### Program 3: Sinusoidal Endothelial Dysfunction & Microvascular Disruption
* **Direction:** Downregulated in MASH
* **Major Supporting Genes:** `LYVE1` (log2FC = -2.730, FDR = 5.223e-09), `CDH5` (log2FC = -1.376, FDR = 5.561e-07), `VCAM1` (log2FC = -2.378, FDR = 4.971e-10), `LDB2` (log2FC = -1.531, FDR = 3.844e-07), `PCDH20` (log2FC = -4.593, FDR = 1.474e-08), `TINAGL1` (log2FC = -1.777, FDR = 4.721e-08).
* **Standardized Pathway:** GO: Cell-Cell Adhesion Via Plasma-Membrane Adhesion Molecules (`GO:0098742`); Reactome: Cell surface interactions at the vascular wall (`R-HSA-202733`).
* **Biological Rationale:** `LYVE1` is a specific marker of healthy liver sinusoidal endothelial cells (LSECs). Downregulation of `LYVE1` alongside junctional cadherin `CDH5` and matrix/adhesion molecules (`VCAM1`, `PCDH20`, `TINAGL1`) reflects LSEC capillarization, basement membrane deposition, and loss of normal microvascular architecture in MASH.
* **Evidence Strength & Limitations:** Biologically consistent with known pathological capillarization in steatohepatitis. Bulk transcriptomics lacks spatial context to determine whether endothelial loss is pan-lobular or localized to pericentral zones.

#### Program 4: Mitochondrial Stress, Metabolic Dysregulation & Proteostasis Response
* **Direction:** Mixed (Upregulated stress/chaperones; Downregulated lipid/amino acid metabolic enzymes)
* **Major Supporting Genes:** Upregulated: `UBD` (log2FC = 4.151, FDR = 1.325e-10), `UQCRBP1` (log2FC = 3.733, FDR = 1.139e-14), `CYCS` (log2FC = 1.565, FDR = 1.124e-08), `MANF` (log2FC = 1.854, FDR = 6.054e-07); Downregulated: `CETP` (log2FC = -2.487, FDR = 2.037e-08), `CBS` (log2FC = -1.254, FDR = 1.804e-07), `SCLY` (log2FC = -1.282, FDR = 5.208e-07).
* **Standardized Pathway:** Reactome: Respiratory electron transport (`R-HSA-611105`); GO: Negative Regulation Of Amyloid Fibril Formation (`GO:1905907`); KEGG: Metabolic pathways (`hsa01100`).
* **Biological Rationale:** Induction of `UBD` (FAT10) and ER chaperone `MANF` highlights proteotoxic and ubiquitin-proteasome system stress. Simultaneous elevation of electron transport components (`UQCRBP1`, `CYCS`) combined with suppression of essential metabolic machinery (`CETP` cholesterol transfer, `CBS` transsulfuration) demonstrates severe metabolic cofactor and lipid processing dysfunction.
* **Evidence Strength & Limitations:** Strong direct statistical signal (`UBD` log2FC = 4.151, `UQCRBP1` log2FC = 3.733). However, enzymatic activity and metabolic flux cannot be inferred solely from steady-state mRNA levels.

#### Program 5: Non-Coding RNA & Protein Translation Machinery Alterations
* **Direction:** Upregulated tRNAs and specific ncRNAs; Downregulated regulatory lncRNAs
* **Major Supporting Genes:** `TRNC` (log2FC = 4.066, FDR = 6.480e-08), `TRNL2` (log2FC = 3.865, FDR = 2.695e-07), `TRNY` (log2FC = 3.571, FDR = 3.844e-07), `TRNS1` (log2FC = 3.047, FDR = 1.165e-08), `TRNK` (log2FC = 2.726, FDR = 4.073e-09), `SNORD140` (log2FC = 3.061, FDR = 8.273e-14), `CD81-AS1` (log2FC = -2.961, FDR = 8.273e-14), `DIO3OS` (log2FC = -3.876, FDR = 3.915e-08).
* **Standardized Pathway:** KEGG: Aminoacyl-tRNA biosynthesis (`hsa00970`); GO: Translation (`GO:0006412`).
* **Biological Rationale:** Robust upregulation of nuclear and mitochondrial tRNA transcripts indicates heightened translational demand or altered tRNA processing under chronic inflammatory stress. Concurrently, dysregulation of non-coding regulatory RNAs (`CD81-AS1`, `DIO3OS`) suggests epigenetic remodeling.
* **Evidence Strength & Limitations:** High statistical significance across tRNA species (FDR < 3e-07). A major limitation is that standard poly(A)-selection or total RNA-seq library protocols exhibit variable capture efficiency for small structured tRNAs, introducing potential technical variation.

---

### 3. Key Genes and Interaction Modules

1. **`TREM2` (Upregulated, log2FC = 4.911, P = 5.661e-12, FDR = 3.899e-09)**
   * *Role:* Key cell-surface receptor driving the survival and phagocytic activity of lipid-associated macrophages.
   * *Interaction Nature:* Regulatory interaction and pathway co-membership with `CSF1R` (OmniPath record) and signaling crosstalk with scavenger receptors (`CD36`, `MARCO`).

2. **`TIMD4` (Downregulated, log2FC = -4.282, P = 3.570e-11, FDR = 1.502e-08)**
   * *Role:* Phosphatidylserine receptor essential for apoptotic cell clearance (efferocytosis) by resident Kupffer cells.
   * *Interaction Nature:* Co-expression module with resident Kupffer cell markers (`CD163`, `MRC1`, `MARCO`, `CD5L`).

3. **`UBD` / FAT10 (Upregulated, log2FC = 4.151, P = 5.248e-14, FDR = 1.325e-10)**
   * *Role:* Ubiquitin-like modifier induced by pro-inflammatory cytokines (TNF-alpha, IFN-gamma) targeting proteins for proteasomal degradation and modulating NF-kB signaling.
   * *Interaction Nature:* Direct protein conjugation and pathway co-membership in proteasomal response networks.

4. **`LYVE1` (Downregulated, log2FC = -2.730, P = 8.275e-12, FDR = 5.223e-09)**
   * *Role:* Hyaluronan receptor maintaining normal liver sinusoidal endothelial cell fenestration and identity.
   * *Interaction Nature:* Co-expression and pathway co-membership with vascular endothelial markers (`CDH5`, `VCAM1`).

5. **`UQCRBP1` (Upregulated, log2FC = 3.733, P = 7.520e-19, FDR = 1.139e-14)**
   * *Role:* Ubiquinol-cytochrome c reductase complex subunit pseudogene/gene candidate, representing the most statistically significant transcript in the dataset.
   * *Interaction Nature:* Pathway co-membership with mitochondrial respiratory component `CYCS` and mitochondrial translocator `TIMM17A`.

6. **`CXCL10` (Upregulated, log2FC = 3.463, P = 4.686e-10, FDR = 1.183e-07)**
   * *Role:* Major CXCR3-binding chemokine driving hepatic recruitment of activated T lymphocytes and monocytes.
   * *Interaction Nature:* Regulatory ligand-receptor interaction with `CXCR3` and pathway co-membership with cytokine receptor networks.

7. **`CD163` - `MRC1` - `MARCO` Scavenger Receptor Module**
   * *Statistical Status:* `CD163` (log2FC = -2.517, FDR = 3.117e-09), `MRC1` (log2FC = -2.102, FDR = 1.877e-08), `MARCO` (log2FC = -2.844, FDR = 3.464e-10).
   * *Role:* Multi-receptor complex maintaining hemoglobin clearance, endocytosis, and pathogen recognition in tolerogenic macrophages.
   * *Interaction Nature:* Direct physical interaction (STRING records: `CD163`-`MRC1`-`SIGLEC1`; `CD36`-`CD163`-`MARCO`) and functional co-expression.

8. **`CTNNB1` / Wnt Signaling Regulatory Axis (`FOXM1`, `TCF7L1`, `CDH5`)**
   * *Statistical Status:* `FOXM1` (log2FC = 2.144, FDR = 4.232e-07), `TCF7L1` (log2FC = -1.535, FDR = 1.987e-07), `CDH5` (log2FC = -1.376, FDR = 5.561e-07).
   * *Role:* Regulates endothelial-to-mesenchymal transition, cell cycle progression, and vascular junction stability.
   * *Interaction Nature:* Regulatory interaction and direct physical interaction via central network hub `CTNNB1` (STRING record).

9. **`FABP5` (Upregulated, log2FC = 2.849, P = 1.630e-10, FDR = 4.938e-08)**
   * *Role:* Fatty acid binding protein facilitating intracellular lipophilic ligand transport and lipid mediator signaling.
   * *Interaction Nature:* Co-expression with `TREM2` in lipid-loaded foam cell-like macrophages.

10. **`CETP` (Downregulated, log2FC = -2.487, P = 5.651e-11, FDR = 2.037e-08)**
    * *Role:* Cholesteryl ester transfer protein mediating neutral lipid exchange between high-density lipoproteins (HDL) and apoB-containing lipoproteins.
    * *Interaction Nature:* Pathway co-membership in systemic and hepatic lipid transport.

---

### 4. Validation Priorities

#### Priority 1: Shift from Resident Kupffer Cells (`TIMD4`/`CD163`) to Lipid-Associated Macrophages (`TREM2`/`FABP5`)
* **Category:** Confounding or composition check / Mechanistic hypothesis
* **Why Prioritize:** Resolves whether observed expression shifts represent true intracellular transcriptional reprogramming or a cell population shift (loss of resident cells vs. infiltration of monocyte-derived LAMs).
* **Dataset Evidence:** Concurrent deep downregulation of `TIMD4` (log2FC = -4.282) and `MARCO` (log2FC = -2.844) alongside strong upregulation of `TREM2` (log2FC = 4.911) and `FABP5` (log2FC = 2.849).
* **External Evidence:** Single-cell transcriptomic literature (PMID: 39497821, 29503738) confirms subset-restricted expression of `TIMD4` to Kupffer cells and `TREM2` to LAMs.
* **Next Validation Step:** Single-cell RNA sequencing (scRNA-seq) or spatial transcriptomics combined with multiplex immunofluorescence (`TIMD4` vs. `TREM2` staining) on human MASH liver biopsies.
* **Status:** Supported hypothesis.

#### Priority 2: Loss of Sinusoidal Endothelial Identity and Capillarization (`LYVE1`, `CDH5`)
* **Category:** Mechanistic hypothesis / Biomarker
* **Why Prioritize:** LSEC capillarization precedes overt hepatic fibrosis and exacerbates parenchymal hypoxia and steatosis.
* **Dataset Evidence:** Significant downregulation of LSEC fenestration marker `LYVE1` (log2FC = -2.730, FDR = 5.223e-09) and junctional `CDH5` (log2FC = -1.376, FDR = 5.561e-07).
* **External Evidence:** HPA tissue records confirm selective expression of `LYVE1` in hepatic sinusoidal endothelium.
* **Next Validation Step:** Transmission electron microscopy (TEM) for fenestration count paired with immunohistochemical co-staining of `LYVE1` and `CDH5` across MASH fibrosis stages (F0-F4).
* **Status:** Supported hypothesis.

#### Priority 3: Inflammatory Proteotoxic Stress Driven by `UBD` (FAT10)
* **Category:** Therapeutic target / Mechanistic hypothesis
* **Why Prioritize:** `UBD` is one of the highest upregulated protein-coding transcripts (log2FC = 4.151, FDR = 1.325e-10) and regulates NF-kB activation and protein degradation under inflammatory stress.
* **Dataset Evidence:** `UBD` log2FC = 4.151 with P = 5.248e-14.
* **External Evidence:** Literature links `UBD` induction to TNF-alpha/IFN-gamma stimulation in steatotic hepatocytes.
* **Next Validation Step:** In vitro siRNA knock-down of `UBD` in primary human hepatocytes subjected to palmitate lipid loading, measuring NF-kB promoter activity, protein aggregation, and apoptosis.
* **Status:** Exploratory hypothesis.

#### Priority 4: Chemokine-Mediated Leukocyte Recruitment via `CXCL10` - `TNFRSF12A` Axis
* **Category:** Therapeutic target / Biomarker
* **Why Prioritize:** Pro-inflammatory recruitment vectors are actionable targets for mitigating hepatic lobular inflammation.
* **Dataset Evidence:** Upregulation of `CXCL10` (log2FC = 3.463, FDR = 1.183e-07) and `TNFRSF12A` (log2FC = 3.271, FDR = 1.334e-07).
* **External Evidence:** Clinical trial records document CXCR3/CXCL10 pathway inhibitors in chronic inflammatory conditions.
* **Next Validation Step:** Enzyme-linked immunosorbent assay (ELISA) measuring circulating CXCL10 protein levels in MASH patient serum, correlated with histopathology NAS scores.
* **Status:** Supported hypothesis.

#### Priority 5: External Statistical Validation in Independent MASH Cohorts
* **Category:** Confounding or composition check
* **Why Prioritize:** Essential for confirming cohort-independent reproducibility and ruling out platform-specific or small sample size artifacts.
* **Dataset Evidence:** 100 differentially expressed genes (all FDR <= 0.01).
* **External Evidence:** External statistical validation was not performed in the provided evidence pack.
* **Next Validation Step:** Cross-validation and meta-analysis across independent public RNA-seq datasets (e.g., GEO datasets GSE130970, GSE135251).
* **Status:** Exploratory hypothesis.

---

### 5. Evidence Grounding

```
+----------------------------------------------------------------------------------------------------+
| EVIDENCE GROUNDING MATRIX                                                                          |
+--------------------------+-----------------------+-----------------------+-------------------------+
| Biological Program       | Direct Input Evidence | Pathway / Interaction | Tissue & Literature     |
+--------------------------+-----------------------+-----------------------+-------------------------+
| 1. LAM Activation        | TREM2 (log2FC=4.911), | Reactome: Innate      | Single-cell MASH lit    |
|                          | FABP5 (log2FC=2.849)  | Immune System         | (PMID:39497821)         |
| 2. Kupffer Cell Loss     | TIMD4 (log2FC=-4.282),| STRING interaction:   | HPA liver macrophage    |
|                          | MARCO (log2FC=-2.844) | CD163-MRC1-SIGLEC1    | records; PMID:29503738  |
| 3. LSEC Dysfunction      | LYVE1 (log2FC=-2.730),| GO: Cell-Cell         | HPA endothelial tissue  |
|                          | CDH5 (log2FC=-1.376)  | Adhesion (GO:0098742) | expression records      |
| 4. Proteostasis & Stress | UBD (log2FC=4.151),   | Reactome: Respiratory | Literature: FAT10 &     |
|                          | UQCRBP1 (log2FC=3.733)| electron transport    | ER stress in liver      |
| 5. NcRNA & Translation   | TRNC (log2FC=4.066),  | KEGG: Aminoacyl-tRNA  | PubMed non-coding RNA   |
|                          | SNORD140 (log2FC=3.061)| biosynthesis          | records (PMID:35581633) |
+--------------------------+-----------------------+-----------------------+-------------------------+
```

* **Direct Evidence:** Up/downregulated log2FC, P values, and FDR from the provided statistical ledger (`TREM2`, `UBD`, `TIMD4`, `LYVE1`, `UQCRBP1`).
* **Pathway & Ontology Evidence:** Standardized GO terms (`GO:0006954`, `GO:0030450`, `GO:0098742`), Reactome pathways (`R-HSA-168249`, `R-HSA-3000480`), and KEGG modules (`hsa00970`, `hsa04060`).
* **Protein Interaction Evidence:** STRING network physical/functional interactions (`CD163`-`MRC1`-`SIGLEC1`, `CD36`-`CD163`-`MARCO`, `CTNNB1`-`CDH5`-`FOXM1`-`TCF7L1`) and OmniPath receptor-ligand records (`CSF1R`-`TREM2`).
* **Tissue Expression Evidence:** HPA and GTEx tissue-specific records verifying cellular localization of `LYVE1` (LSECs) and `TIMD4`/`CD163` (hepatic macrophages).
* **Literature Evidence:** PubMed/Europe PMC articles validating `TREM2`/`TIMD4` dynamics in steatohepatitis (PMID: 39497821) and tissue-resident cell homeostasis (PMID: 29503738).
* **Independent External Validation:** External statistical validation was not performed; database cross-references provide mechanistic context rather than statistical replication.

---

### 6. Limitations and Alternative Explanations

1. **Bulk Tissue Cell-Composition Confounding:** Bulk RNA sequencing averages transcript abundance across all hepatic cell types. The marked downregulation of Kupffer cell markers (`TIMD4`, `MARCO`, `CD163`) alongside upregulation of LAM markers (`TREM2`, `FABP5`) likely reflects shifts in cell-type proportions (loss of Kupffer cells and infiltration of monocyte-derived macrophages) rather than purely cell-intrinsic gene suppression.
2. **Correlation vs. Causal Ambiguity:** Differential expression establishes statistical association with the MASH disease state but cannot prove functional causality. Highly upregulated genes like `UBD` or `TREM2` may represent compensatory protective responses to lipid toxic stress rather than pathogenic disease drivers.
3. **Disease Stage & Severity Heterogeneity:** The dataset compares MASH against healthy controls without stratification by NAFLD Activity Score (NAS) or fibrosis stage (F0–F4). Transcriptomic signals associated with LSEC dysfunction (`LYVE1`, `CDH5`) may be concentrated in advanced fibrotic samples.
4. **RNA Isolation & Sequencing Capture Biases for Non-Coding RNAs:** Small non-coding transcripts, tRNAs (`TRNC`, `TRNL2`, `TRNY`), and pseudogenes (`UQCRBP1`, `GLUD1P2`) can be subject to alignment multi-mapping artifacts and variable enrichment efficiency depending on whether poly(A) selection or total RNA ribo-depletion protocols were utilized.
5. **Unmeasured Clinical Confounders:** Patient-level variables such as body mass index (BMI), type 2 diabetes status, concurrent medications (e.g., statins, GLP-1 receptor agonists), biological sex, and fasting state could account for a portion of the variance in lipid metabolic gene expression (`CETP`, `FABP5`, `CBS`).

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=133, external claims checked=0, external mismatches=0, status=passed.

Answer model API: Google Gemini / gemini-3.6-flash

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 93/100 selected items (records returned); cbioportal 85/100 selected items (records returned); chembl 33/100 selected items (partially returned; some queries failed); civic 4/100 selected items (records returned); clinicaltrials 40/100 selected items (records returned); clinvar 82/100 selected items (records returned); ensembl 42/100 selected items (partially returned; some queries failed); europepmc 897 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 75/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 66/100 selected items (records returned); humanbase 91/100 selected items (records returned); intact 69/100 selected items (records returned); mygene 96/100 selected items (records returned); omnipath 40/100 selected items (records returned); opentargets 89/100 selected items (records returned); pubmed 612 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 69/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 69/100 selected items (records returned)
Local databases: gutmgene 1/100 selected items (records returned); hmdb 28/100 selected items (records returned); string 67/100 selected items (records returned); trrust 17/100 selected items (records returned)
