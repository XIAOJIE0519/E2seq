# colorectal cancer - gemini-3.6-flash

- Benchmark system: raw
- Repeat: 3
- Task type: PROGNOSIS
- Tissue / sample source: colorectal tumor tissue
- Comparison or endpoint: overall survival (OS)
- Answer input cohort: Discovery/Core only
- Selected items: 100
- Input fields: gene name, effect size (log2FC/HR), P value, FDR
- E2seq Agent RAG: disabled
- Conversation memory: disabled
- Thinking mode: disabled
- Held-out validation data in prompt/RAG: no
- Model API: Google Gemini / gemini-3.6-flash
- Message SHA-256: dfb8fe82357dbea353d34030380d74028b528c91505f5793c7261ee9e4376675
- Response HTTP status: 200
- Prompt tokens: 5297
- Completion tokens: 10177
- Reasoning tokens: 
- Total tokens: 15474
- API requests reported: 
- Elapsed seconds: 23.635
- Final benchmark system: raw; file rank 2/5; original repeat 3; model vendor: Google Gemini

---
### 1. Overall Biological Interpretation

The prognostic transcriptomic profile of colorectal tumor tissue in relation to overall survival (OS) reveals a clear functional dichotomy between pathways associated with adverse clinical outcomes (HR > 1) and those associated with favorable prognosis (HR < 1). 

**Adverse prognostic signals (Risk program)** are dominated by transcriptomic features characteristic of:
1. Epithelial-mesenchymal transition (EMT) and stromal extracellular matrix (ECM) remodeling (e.g., *ZEB1-AS1*, *INHBB*, *ITGBL1*, *TPM4*, *ADAMTS18*).
2. Pro-survival kinase signaling and stress adaptation pathways (e.g., *AKT3*, *DCBLD2*, *ABL2*, *GADD45B*).
3. Microenvironmental immunosuppression and metabolic rewiring (e.g., *NT5E*, *MIR31HG*, *SLC2A3*).

**Favorable prognostic signals (Protective program)** are characterized by features that mark:
1. High enterocyte differentiation and intestinal lineage retention (e.g., *CDX2*, *CDX1*, *MYO5B*, *LGALS4*).
2. Intact mitochondrial bioenergetics and oxidative phosphorylation (OXPHOS) machinery (e.g., *NDUFA9*, *ATP23*, *ATP5B*, *ATP5G1*, *COA3*, *TIMM13*, *CS*, *OGDHL*).
3. Effective antigen presentation and immune surveillance (e.g., *TAPBPL*, *LGALS9*).

Taken together, these results reflect the well-established clinical and biological spectrum of colorectal cancer (CRC), echoing the Consensus Molecular Subtypes (CMS). Specifically, tumors exhibiting loss of master intestinal transcription factors (*CDX2*/*CDX1*) and diminished mitochondrial metabolic capacity, coupled with increased stromal invasion, EMT non-coding/coding expression, and immune-evasive ecto-nucleotidase activity (*NT5E*), demonstrate significantly compromised overall survival.

---

### 2. Core Biological Programs

```
                  +-------------------------------------------------------+
                  |           COLORECTAL CANCER OVERALL SURVIVAL          |
                  +-------------------------------------------------------+
                                              |
                     +------------------------+------------------------+
                     |                                                 |
         [ RISK PROGRAM (HR > 1) ]                        [ PROTECTIVE PROGRAM (HR < 1) ]
                     |                                                 |
   +-----------------+-----------------+             +-----------------+-----------------+
   |                                   |             |                                   |
Program 1:                          Program 2:     Program 3:                          Program 4:
EMT, Stromal & ECM                  RTK/Akt        Intestinal Epithelial               Mitochondrial OXPHOS
Remodeling                          Signaling      Differentiation                     & TCA Metabolism
(INHBB, ZEB1-AS1,                   (DCBLD2, AKT3, (CDX2, CDX1, MYO5B,                 (NDUFA9, ATP23, ATP5B,
 ITGBL1, TPM4)                       ABL2, GADD45B) LGALS4)                             CS, OGDHL)
                                                     |
                                                     +--- Program 5: Immune Surveillance & Presentation
                                                          (TAPBPL, LGALS9 [Protective] vs NT5E [Risk])
```

#### Program 1: Mesenchymal Stroma, EMT, and Extracellular Matrix Remodeling
* **Direction / Prognostic Association:** Risk-associated (HR > 1; associated with decreased overall survival).
* **Major Supporting Genes:** *INHBB* (HR = 1.43, FDR = 0.0011), *ZEB1-AS1* (HR = 1.37, FDR = 0.0086), *ITGBL1* (HR = 1.30, FDR = 0.0306), *TPM4* (HR = 1.36, FDR = 0.0089), *ADAMTS18* (HR = 1.26, FDR = 0.0468), *MAP1B* (HR = 1.33, FDR = 0.0472).
* **Standardized Pathway:** Reactome: Extracellular Matrix Organization (R-HSA-1474244) / Hallmark: Epithelial-Mesenchymal Transition.
* **Biological Explanation:** High expression of *ZEB1-AS1* (a key non-coding epigenetic regulator of EMT) together with *INHBB* (Activin B subunit, TGF-β superfamily member), *ITGBL1* (integrin-like protein associated with myofibroblast activation), and structural/remodeling factors (*TPM4*, *ADAMTS18*) indicates an active mesenchymal program, stromal reaction, and tissue remodeling. This collective expression reflects enhanced invasive potential and stromal abundance (e.g., CMS4 subtype CRC).
* **Evidence Strength and Limitations:** **Strong statistical evidence** from multiple independent matrix and EMT regulators. *Limitation:* Transcriptomic signals derived from bulk tissue cannot definitively isolate whether these transcripts originate from malignant epithelial cells undergoing EMT or infiltrating cancer-associated fibroblasts (CAFs).

#### Program 2: Intestinal Epithelial Lineage Identity and Mucosal Differentiation
* **Direction / Prognostic Association:** Protective-associated (HR < 1; associated with increased overall survival).
* **Major Supporting Genes:** *CDX2* (HR = 0.75, FDR = 0.0355), *CDX1* (HR = 0.78, FDR = 0.0573), *MYO5B* (HR = 0.75, FDR = 0.0282), *LGALS4* (HR = 0.77, FDR = 0.0512).
* **Standardized Pathway:** GO: Intestinal Epithelial Cell Differentiation (GO:0030030).
* **Biological Explanation:** *CDX2* and *CDX1* are homeobox transcription factors essential for maintaining intestinal lineage commitment. *MYO5B* mediates apical membrane polar transport in differentiated enterocytes, and *LGALS4* (Galectin-4) is expressed selectively in alimentary tract epithelium. Higher expression of these genes marks well-differentiated, lineage-anchored epithelial tumor cells, which follow a less aggressive clinical course.
* **Evidence Strength and Limitations:** **High evidence strength**, grounded in established colonic biology. *Limitation:* Lower expression in bulk tissue may indicate either true transcriptional dedifferentiation of epithelial cells or lower overall tumor epithelial purity relative to stroma.

#### Program 3: Mitochondrial Bioenergetics and Oxidative Phosphorylation
* **Direction / Prognostic Association:** Protective-associated (HR < 1; associated with increased overall survival).
* **Major Supporting Genes:** *NDUFA9* (HR = 0.69, FDR = 0.0086), *ATP23* (HR = 0.69, FDR = 0.0066), *ATP5B* (HR = 0.75, FDR = 0.0593), *ATP5G1* (HR = 0.75, FDR = 0.0519), *COA3* (HR = 0.74, FDR = 0.0434), *TIMM13* (HR = 0.75, FDR = 0.0394), *CS* (HR = 0.75, FDR = 0.0388), *OGDHL* (HR = 0.69, FDR = 0.0744).
* **Standardized Pathway:** KEGG: Oxidative Phosphorylation (hsa00190) / Reactome: Citric Acid (TCA) Cycle and Respiratory Electron Transport (R-HSA-1428517).
* **Biological Explanation:** Multiple structural subunits and assembly factors of Complex I (*NDUFA9*), Complex V (*ATP5B*, *ATP5G1*, *ATP23*), mitochondrial import components (*TIMM13*), Complex IV assembly (*COA3*), and TCA cycle enzymes (*CS*, *OGDHL*) exhibit consistent protective associations. Preserved mitochondrial respiration correlates with differentiated cellular states, whereas metabolic suppression (Warburg effect shift) correlates with aggressive disease.
* **Evidence Strength and Limitations:** **Very high cross-gene consistency** with low individual hazard ratios (~0.69–0.75). *Limitation:* Decreased mitochondrial gene expression can be a non-specific downstream marker of tissue hypoxia, necrosis, or low epithelial cell content.

#### Program 4: Pro-Survival RTK Signaling and Stress Response Networks
* **Direction / Prognostic Association:** Risk-associated (HR > 1; associated with decreased overall survival).
* **Major Supporting Genes:** *DCBLD2* (HR = 1.41, FDR = 0.0086), *AKT3* (HR = 1.32, FDR = 0.0388), *ABL2* (HR = 1.30, FDR = 0.0276), *PTPN14* (HR = 1.36, FDR = 0.0250), *GADD45B* (HR = 1.32, FDR = 0.0630).
* **Standardized Pathway:** KEGG: PI3K-Akt Signaling Pathway (hsa04151) / Reactome: Signaling by Receptor Tyrosine Kinases (R-HSA-9006934).
* **Biological Explanation:** *DCBLD2* acts as a transmembrane co-receptor that amplifies receptor tyrosine kinase signaling (such as EGFR and VEGFR). Coupled with the downstream effector kinase *AKT3*, non-receptor kinase *ABL2*, and stress-response regulator *GADD45B*, this signaling node promotes cell survival, motility, and microenvironmental stress tolerance.
* **Evidence Strength and Limitations:** **Moderate-to-high strength** based on clear hazard ratio directions across complementary intracellular signaling nodes. *Limitation:* Phosphorylation and kinase activity states are not directly measured by transcriptomic profiling.

#### Program 5: Immune Antigen Processing vs. Microenvironmental Immunosuppression
* **Direction / Prognostic Association:** Dual / Mixed (Protective antigen loading vs. Risk immunosuppressive adenosine axis).
* **Major Supporting Genes:** *TAPBPL* (HR = 0.71, FDR = 0.0192; Protective), *LGALS9* (HR = 0.75, FDR = 0.0420; Protective), *NT5E* / CD73 (HR = 1.31, FDR = 0.0394; Risk), *MIR31HG* (HR = 1.31, FDR = 0.0066; Risk).
* **Standardized Pathway:** Reactome: Antigen Processing-Cross Presentation (R-HSA-983168) / Immunosuppressive Adenosinergic Signaling.
* **Biological Explanation:** *TAPBPL* (tapasin-like protein) facilitates MHC class I antigen assembly, promoting immune recognition. In contrast, *NT5E* (CD73) converts extracellular AMP to immunosuppressive adenosine, facilitating T-cell exhaustion and immune evasion. *MIR31HG* is a lncRNA implicated in suppressing anti-tumor immune responses and promoting oncogenic inflammation.
* **Evidence Strength and Limitations:** **Moderate strength.** *Limitation:* Immune cellular subsets (e.g., CD8+ T cells vs. regulatory T cells vs. myeloid-derived suppressor cells) cannot be fully quantified without deconvolution algorithms or spatial multiplexing.

---

### 3. Key Genes and Interaction Modules

| Gene / Module | Direction in Data | HR (FDR) | Role in Core Programs | Proposed Biological Interaction & Relationship Type |
| :--- | :--- | :--- | :--- | :--- |
| **CDX2** | Protective | 0.748 (0.0355) | Lineage identity | **Regulatory interaction / Pathway co-membership**: Master transcription factor regulating epithelial genes (*CDX1*, *MYO5B*, *LGALS4*). Direct transcriptional regulator of intestinal differentiation. |
| **INHBB** | Risk | 1.433 (0.0011) | EMT & Stroma | **Pathway co-membership**: Secreted TGF-β family ligand involved in paracrine signaling to stromal fibroblasts; operates co-operatively (co-expression) with *ITGBL1*. |
| **ZEB1-AS1** | Risk | 1.372 (0.0086) | EMT & Stroma | **Regulatory interaction**: Long non-coding RNA that epigenetically enhances *ZEB1* expression, repressing epithelial markers (e.g., *CDX2*) and driving EMT. |
| **NDUFA9** | Protective | 0.689 (0.0086) | Mitochondrial OXPHOS | **Direct physical interaction / Pathway co-membership**: Core subunit of mitochondrial Complex I. Assembles physically into the respiratory chain alongside *ATP5B*, *ATP5G1*, and *COA3*. |
| **DCBLD2** | Risk | 1.408 (0.0086) | RTK / Akt Signaling | **Direct physical / Regulatory interaction**: Transmembrane scaffold protein that interacts physically with RTKs (EGFR, VEGFR) to facilitate downstream activation of *AKT3*. |
| **ITGBL1** | Risk | 1.299 (0.0306) | EMT & Stroma | **Co-expression / Indirect relationship**: Integrin-like protein co-expressed with extracellular matrix remodelers (*ADAMTS18*, *TPM4*) in activated myofibroblasts. |
| **TAPBPL** | Protective | 0.711 (0.0192) | Immune Presentation | **Direct physical interaction / Pathway co-membership**: Interacts physically with MHC Class I molecules in the endoplasmic reticulum to edit peptide loading. |
| **NT5E (CD73)**| Risk | 1.313 (0.0394) | Immunosuppression | **Pathway co-membership / Enzymatic relationship**: Ecto-enzyme generating extracellular adenosine, creating an immunosuppressive cascade opposing *TAPBPL*-mediated surveillance. |
| **MYO5B** | Protective | 0.748 (0.0282) | Lineage identity | **Pathway co-membership / Functional cooperation**: Actin-based motor protein participating in apical recycling; co-expressed with intestinal lineage marker *CDX2*. |
| **AKT3** | Risk | 1.318 (0.0388) | RTK / Survival Signaling | **Regulatory / Kinase-substrate interaction**: Downstream effector kinase of the PI3K pathway, activated secondary to RTK co-factor signals such as *DCBLD2*. |

---

### 4. Validation Priorities

```
+-----------------------------------------------------------------------------------+
|                            PRIORITY VALIDATION PIPELINE                           |
+-----------------------------------------------------------------------------------+
  |
  +---> 1. CONFOUNDING CHECK: Single-Cell / Spatial Deconvolution
  |        [Target: INHBB, ITGBL1, CDX2, NDUFA9]
  |
  +---> 2. MECHANISTIC HYPOTHESIS: ZEB1-AS1 / INHBB EMT Axis
  |        [Target: ZEB1-AS1 knock-down & cell motility assays]
  |
  +---> 3. BIOMARKER: Differentiation / OXPHOS Composite Risk Score
  |        [Target: CDX2 + NDUFA9 + ATP5B vs INHBB + DCBLD2 in independent cohorts]
  |
  +---> 4. INTERACTION HYPOTHESIS: DCBLD2 - AKT3 RTK Signaling Axis
  |        [Target: Co-IP & Phospho-AKT Western blots in CRC cell models]
  |
  +---> 5. THERAPEUTIC TARGET: NT5E (CD73) Adenosinergic Immunosuppression
           [Target: CD73 enzymatic inhibition + Immune co-culture assays]
```

#### Priority 1: Cell-Composition Deconvolution and Spatial Mapping
* **Classification:** Confounding or composition check.
* **Prioritization Rationale:** Resolves whether risk genes (*INHBB*, *ITGBL1*) represent cell-intrinsic epithelial transdifferentiation versus cancer-associated fibroblast (CAF) infiltration, and whether protective OXPHOS signals are tied to epithelial tumor purity.
* **Current Dataset Evidence:** Strong, opposing prognostic directions between epithelial lineage/OXPHOS genes (HR < 0.75) and stromal/EMT genes (HR > 1.30).
* **External Evidence:** Single-cell RNA sequencing (scRNA-seq) of CRC indicates *ITGBL1* and *INHBB* are prominently expressed in CAFs, while *CDX2* and *NDUFA9* are restricted to epithelial compartments.
* **Next Step:** Perform digital cell-type deconvolution (e.g., CIBERSORTx) on bulk profiles and validate spatial expression via multiplex immunohistochemistry (mIHC) or spatial transcriptomics on CRC tissue microarrays (TMAs).
* **Status:** **Supported hypothesis**.

#### Priority 2: Characterization of the ZEB1-AS1 / INHBB EMT Axis
* **Classification:** Mechanistic hypothesis.
* **Prioritization Rationale:** *ZEB1-AS1* (HR = 1.37, FDR = 0.0086) and *INHBB* (HR = 1.43, FDR = 0.0011) are among the most statistically significant adverse prognostic risk factors in the dataset.
* **Current Dataset Evidence:** Highly significant elevated hazard ratios for non-coding and TGF-β superfamily regulators of EMT.
* **External Evidence:** *ZEB1-AS1* acts as a molecular sponge for miRNAs that repress *ZEB1*, a master driver of tumor cell invasion and chemoresistance.
* **Next Step:** CRISPR-Cas9 knock-down or antisense oligonucleotide (ASO) inhibition of *ZEB1-AS1* in patient-derived organoids (PDOs) followed by Transwell invasion, EMT marker profiling, and RNA-seq.
* **Status:** **Supported hypothesis**.

#### Priority 3: Clinical Validation of an Epithelial-Mitochondrial Prognostic Index
* **Classification:** Biomarker.
* **Prioritization Rationale:** High-throughput translation requires concise gene signatures to stratify patients for post-surgical relapse risk.
* **Current Dataset Evidence:** Consistent hazard reduction across *CDX2*, *CDX1*, *NDUFA9*, *ATP23*, and *ATP5B* (HRs 0.68–0.78, FDR < 0.06).
* **External Evidence:** Loss of CDX2 expression is an established adverse prognostic marker in Stage II/III colon cancer; combining it with metabolic/mitochondrial readouts may increase predictive accuracy.
* **Next Step:** Develop a multivariable Cox proportional hazards model using a reduced panel (*CDX2*, *NDUFA9*, *INHBB*, *DCBLD2*) and validate performance (C-index, ROC-AUC) in external cohorts (e.g., TCGA-COAD, GEO datasets GSE39582, GSE14333).
* **Status:** **Supported hypothesis**.

#### Priority 4: Functional Dissection of DCBLD2-Mediated RTK / AKT3 Activation
* **Classification:** Interaction / network hypothesis.
* **Prioritization Rationale:** *DCBLD2* (HR = 1.41, FDR = 0.0086) is a membrane protein capable of linking extracellular signals to intracellular survival kinases like *AKT3* (HR = 1.32, FDR = 0.0388).
* **Current Dataset Evidence:** Both *DCBLD2* and *AKT3* show strong, congruent risk associations with low FDR values.
* **External Evidence:** DCBLD2 undergoes tyrosine phosphorylation upon growth factor stimulation, serving as a docking site for TRAF6 or CRK, which enhances AKT signaling.
* **Next Step:** Co-immunoprecipitation assays to verify physical complex formation or functional signaling dependence in CRC cell lines, combined with Western blotting for phospho-AKT (Ser473/Thr308) following *DCBLD2* knockdown.
* **Status:** **Exploratory hypothesis**.

#### Priority 5: Targeting NT5E (CD73) in Immune-Evasive Colorectal Tumors
* **Classification:** Therapeutic target.
* **Prioritization Rationale:** *NT5E* / CD73 (HR = 1.31, FDR = 0.0394) is an enzymatically actionable surface target involved in extracellular adenosine generation and T-cell suppression.
* **Current Dataset Evidence:** Adverse survival association linked with higher *NT5E* transcript levels.
* **External Evidence:** Monoclonal antibodies targeting CD73 (e.g., oleclumab) are undergoing clinical evaluation in combination with immune checkpoint inhibitors in solid tumors.
* **Next Step:** Ex vivo functional assays using tumor-infiltrating lymphocytes (TILs) and CRC organoids co-cultured with anti-CD73 antibodies to assess CD8+ T-cell reactivation and cytotoxicity.
* **Status:** **Exploratory hypothesis** (the presence of a targetable enzyme does not yet prove clinical therapeutic efficacy in this specific setting).

---

### 5. Evidence Grounding

| Concept / Program | Direct Dataset Evidence | External / Literature Evidence | Interaction / Regulatory Status | Evidence Synthesis & Conflicts |
| :--- | :--- | :--- | :--- | :--- |
| **Epithelial Lineage Preservation (*CDX2*, *CDX1*)** | HR = 0.75 (*CDX2*), HR = 0.78 (*CDX1*); FDR < 0.058. | Well-documented master intestinal transcription factors. Loss of CDX2 correlates with high tumor grade and poor survival. | Direct transcriptional regulation of colonic epithelial identity genes (*MYO5B*, *LGALS4*). | **Genuinely Independent Evidence:** Transcriptomic data directly align with extensive clinical immunohistochemical literature. No conflicting signals observed. |
| **Mitochondrial OXPHOS (*NDUFA9*, *ATP5B*, *ATP23*)** | Multiple genes with HR = 0.68–0.75; FDR < 0.06. | Mitochondrial dysregulation and metabolic shift (Warburg effect) are established hallmarks of cancer progression. | Physical co-membership within mitochondrial Complexes I and V inner membrane assemblies. | **Overlapping Underlying Source:** Genes reflect a single biological organelle unit; co-expression is largely driven by total mitochondrial mass and epithelial content. |
| **Stromal / EMT Axis (*INHBB*, *ZEB1-AS1*, *ITGBL1*)** | HR = 1.30–1.43; FDR < 0.03. | *ZEB1-AS1* drives *ZEB1* expression; *INHBB* and *ITGBL1* are linked to TGF-β driven stroma and CMS4 subtype. | Regulatory (lncRNA-mRNA) and paracrine matrix signaling. | **Potential Compositional Overlap:** Elevated expression likely reflects high cancer-associated fibroblast (CAF) content in bulk tissue rather than pure epithelial EMT. |
| **DCBLD2 / AKT3 Signaling Axis** | HR = 1.41 (*DCBLD2*), HR = 1.32 (*AKT3*); FDR < 0.039. | DCBLD2 is upregulated in colorectal and gastric cancers, modulating RTK trafficking and AKT pathways. | Putative signal transduction network link (RTK co-receptor to intracellular kinase). | **Exploratory / Indirect:** mRNA co-association in bulk tissue does not guarantee active protein phosphorylation or direct binding in target cells. |
| **Immunosuppressive Adenosine Axis (*NT5E*)** | HR = 1.31; FDR = 0.0394. | CD73 generates adenosine; linked to immune evasion and poor anti-PD-1 responses in cold tumors. | Enzymatic regulation of microenvironmental nucleotide metabolite pools. | **Sufficient Direct Evidence for Association, Insufficient for Treatment Efficacy:** High transcript level correlates with poor survival, but therapeutic targeting requires functional confirmation. |

---

### 6. Limitations and Alternative Explanations

1. **Bulk Tissue Cell-Composition Heterogeneity (CAF Infiltration vs. Epithelial EMT):**
   * *Issue:* Risk genes such as *INHBB*, *ITGBL1*, and *TPM4* are strongly expressed in cancer-associated fibroblasts (CAFs). Their association with poor survival may reflect an abundance of tumor stroma (CMS4 phenotype) rather than cell-intrinsic epithelial transdifferentiation.
   * *Resolution:* Perform single-cell RNA sequencing or spatial transcriptomic deconvolution to separate stromal fibroblast signatures from malignant epithelial cells.

2. **Tumor Purity and Epithelial Depletion Bias:**
   * *Issue:* The protective signal observed for *CDX2*, *CDX1*, and mitochondrial genes (*NDUFA9*, *ATP5B*) could be driven by sample tumor purity. Samples rich in intact, non-necrotic epithelial cells naturally exhibit higher baseline expression of these markers compared to stroma-rich or highly necrotic tumors.
   * *Resolution:* Re-evaluate multivariable Cox models adjusting for histopathologically assessed tumor purity or computationally derived stromal scores (e.g., ESTIMATE algorithm).

3. **Confounding by Clinical Covariates and Treatment Heterogeneity:**
   * *Issue:* Unadjusted clinical variables—such as pathological stage (TNM Stage I–IV), anatomical location (left vs. right colon), microsatellite instability (MSI vs. MSS), and adjuvant chemotherapy exposure (e.g., 5-FU/FOLFOX)—can introduce substantial confounding.
   * *Resolution:* Conduct stratified survival analyses within defined clinical subgroups (e.g., Stage II/III MSS colorectal cancers) using multivariable regression.

4. **Broad, Non-Specific Metabolic Gene Enrichment:**
   * *Issue:* Decreased expression of mitochondrial OXPHOS genes (*NDUFA9*, *ATP23*, *CS*) may be a non-specific byproduct of localized tissue hypoxia, ischemia, or tumor necrosis, rather than a primary driver of aggressive tumor biology.
   * *Resolution:* Assess cellular metabolic flux and oxygen consumption rates (OCR) in functional models (e.g., primary organoids) under controlled normoxic and hypoxic environments.

5. **Correlation vs. Causation Ambiguity in Non-Coding Transcripts:**
   * *Issue:* Association of lncRNAs (*ZEB1-AS1*, *MIR31HG*, *RUNX1-IT1*) with overall survival does not establish functional necessity in tumor progression; these transcripts may represent downstream passenger markers of altered chromatin states.
   * *Resolution:* Perform genetic loss- and gain-of-function experiments (CRISPRi/CRISPRa) in vitro and in vivo to directly evaluate causality regarding cell proliferation, invasion, and drug resistance.
