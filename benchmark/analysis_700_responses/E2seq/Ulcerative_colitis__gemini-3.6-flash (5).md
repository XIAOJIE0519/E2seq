# ulcerative colitis (UC) - gemini-3.6-flash

- Benchmark system: E2seq + Agent RAG
- Repeat: 7
- Task type: DISEASE-STATE
- Tissue / sample source: colonic mucosal tissue
- Comparison or endpoint: ulcerative colitis versus healthy control
- Answer input cohort: Discovery/Core only
- Selected items: 100
- Input fields: gene name, effect size (log2FC/HR), P value, FDR
- E2seq Agent RAG: enabled
- Conversation memory: disabled
- Thinking mode: disabled
- Held-out validation data in prompt/RAG: no
- Model API: Google Gemini / gemini-3.6-flash
- Message SHA-256: 478acec7ab00f0e9bda085b6ecab7aa16a2bc8aa5cde3f2ba8fb71b2af94f79a
- Response HTTP status: 200
- Prompt tokens: 43953
- Completion tokens: 38906
- Reasoning tokens: 11526
- Total tokens: 82859
- API requests reported: 3
- Elapsed seconds: 47.069
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 1095.213
- Question handoff seconds: 1109.559
- Final benchmark system: E2seq; file rank 5/5; original repeat 7; model vendor: Google Gemini

---
### 1. Overall Biological Interpretation

The transcriptomic profile of colonic mucosal tissue from patients with active ulcerative colitis (UC) compared to healthy controls demonstrates a marked functional divergence: robust induction of inflammatory, tissue-destructive, and oxidative programs alongside extensive repression of mature enterocyte transport, metabolic, and digestive functions. 

Upregulated transcripts are concentrated in pro-inflammatory neutrophil-attracting chemokines (*CXCL1*, *CXCL2*, *CXCL3*), antimicrobial alarmins and defense proteins (*S100A8*, *LCN2*, *S100P*, *PI3*), extracellular matrix remodeling enzymes (*MMP3*, *TIMP1*, *CHI3L1*), epithelial hydrogen peroxide production machinery (*DUOX2*, *DUOXA2*), and immune feedback regulators (*SOCS3*, *CTLA4*, *IRAK3*). 

In contrast, downregulated transcripts reveal a widespread shutdown of physiological colonocyte processes. This includes severe suppression of apical water channels (*AQP8*, *AQP7*), amino acid and vitamin transporters (*SLC38A4*, *SLC23A1*), short-chain fatty acid and solute transporters (*SLC16A1*, *SLC51A*, *ABCG2*), mitochondrial ketogenesis (*HMGCS2*), and mucosal barrier digestive enzymes (*MEP1B*, *DEFB1*). 

Collectively, these transcriptomic alterations depict an inflamed mucosa characterized by leukocyte recruitment, oxidative stress, and matrix turnover, coupled with functional metabolic collapse and crypt epithelial transport failure.

---

### 2. Core Biological Programs

#### Program 1: Neutrophil Chemotaxis and Pro-Inflammatory Chemokine Signaling
* **Direction:** Upregulated in UC
* **Major Supporting Genes:** *CXCL1* ($\log_2\text{FC} = 3.46, \text{FDR} = 1.15 \times 10^{-15}$), *CXCL2* ($\log_2\text{FC} = 2.80, \text{FDR} = 1.73 \times 10^{-11}$), *CXCL3* ($\log_2\text{FC} = 2.33, \text{FDR} = 2.51 \times 10^{-11}$), *S100A8* ($\log_2\text{FC} = 3.80, \text{FDR} = 4.43 \times 10^{-11}$), *LCN2* ($\log_2\text{FC} = 2.67, \text{FDR} = 1.37 \times 10^{-21}$)
* **Standardized Pathway:** KEGG: IL-17 signaling pathway (`hsa04657`) / GO: Neutrophil Chemotaxis (`GO:0030593`)
* **Biological Rationale:** *CXCL1*, *CXCL2*, and *CXCL3* act as potent chemoattractants operating through the CXCR2 receptor to drive neutrophil extravasation into the colonic lamina propria and crypt epithelium (crypt abscesses). *S100A8* (calprotectin subunit) and *LCN2* (lipocalin-2) are abundant neutrophil secondary granule proteins released upon activation into the mucosa and lumen.
* **Evidence Strength & Limitations:** High statistical significance ($\text{FDR} < 10^{-10}$) across multiple co-regulated chemokines. *Limitation:* Whole mucosal biopsy profiling blends single-cell expression changes with cell-composition shifts caused by dense neutrophil infiltration.

#### Program 2: Mucosal Oxidative Stress and Reactive Oxygen Species (ROS) Generation
* **Direction:** Upregulated in UC
* **Major Supporting Genes:** *DUOX2* ($\log_2\text{FC} = 4.67, \text{FDR} = 4.45 \times 10^{-26}$), *DUOXA2* ($\log_2\text{FC} = 2.89, \text{FDR} = 1.12 \times 10^{-10}$), *VNN1* ($\log_2\text{FC} = 3.20, \text{FDR} = 1.54 \times 10^{-15}$)
* **Standardized Pathway:** Reactome: ROS and RNS production in phagocytes (`R-HSA-1221632`) / GO: Reactive Oxygen Species Metabolic Process (`GO:0072593`)
* **Biological Rationale:** *DUOX2* (dual oxidase 2) and its essential maturation factor *DUOXA2* form a functional apical membrane complex in mucosal epithelial cells, generating hydrogen peroxide for mucosal host defense. *VNN1* (vanin-1) regulates pantetheine cleavage and tissue oxidative sensitivity.
* **Evidence Strength & Limitations:** Highly concordant stoichiometric upregulation of both subunit and maturation factor with large effect sizes ($\log_2\text{FC} > 2.8$). *Limitation:* RNA levels do not directly measure local hydrogen peroxide fluxes or distinguish bactericidal defense from host tissue oxidative injury.

#### Program 3: Extracellular Matrix (ECM) Remodeling and Tissue Repair
* **Direction:** Upregulated in UC
* **Major Supporting Genes:** *MMP3* ($\log_2\text{FC} = 4.64, \text{FDR} = 5.40 \times 10^{-14}$), *TIMP1* ($\log_2\text{FC} = 1.97, \text{FDR} = 1.81 \times 10^{-17}$), *CHI3L1* ($\log_2\text{FC} = 4.59, \text{FDR} = 3.20 \times 10^{-11}$), *TNC* ($\log_2\text{FC} = 2.58, \text{FDR} = 2.51 \times 10^{-11}$), *PRRX1* ($\log_2\text{FC} = 2.91, \text{FDR} = 4.35 \times 10^{-16}$), *PDPN* ($\log_2\text{FC} = 2.54, \text{FDR} = 1.75 \times 10^{-10}$)
* **Standardized Pathway:** Reactome: Extracellular matrix organization (`R-HSA-1474244`) / GO: Collagen Catabolic Process (`GO:0030574`)
* **Biological Rationale:** *MMP3* (stromelysin-1) degrades structural ECM proteins during active mucosal ulceration, counterbalanced by *TIMP1*. *CHI3L1* (chitinase-3-like 1), *TNC* (tenascin C), *PDPN* (podoplanin), and *PRRX1* reflect stromal fibroblast activation, wound healing, and tissue remodeling in response to mucosal barrier breach.
* **Evidence Strength & Limitations:** Strong effect sizes ($\log_2\text{FC} > 4.5$ for *MMP3* and *CHI3L1*). *Limitation:* Transcriptional upregulation of matrix modifiers cannot distinguish effective mucosal restitution from chronic fibrotic tissue remodeling.

#### Program 4: Epithelial Solute and Water Transport Suppression
* **Direction:** Downregulated in UC
* **Major Supporting Genes:** *AQP8* ($\log_2\text{FC} = -4.42, \text{FDR} = 1.60 \times 10^{-13}$), *AQP7* ($\log_2\text{FC} = -2.32, \text{FDR} = 4.04 \times 10^{-20}$), *SLC38A4* ($\log_2\text{FC} = -3.07, \text{FDR} = 4.70 \times 10^{-37}$), *SLC23A1* ($\log_2\text{FC} = -2.40, \text{FDR} = 8.89 \times 10^{-29}$), *SLC16A1* ($\log_2\text{FC} = -2.38, \text{FDR} = 5.83 \times 10^{-21}$), *SLC51A* ($\log_2\text{FC} = -3.71, \text{FDR} = 1.54 \times 10^{-20}$)
* **Standardized Pathway:** GO: Fluid Transport (`GO:0042044`) / KEGG: Bile secretion (`hsa04976`)
* **Biological Rationale:** Differentiated colonocytes absorb water, electrolytes, and microbial metabolites. *AQP8* and *AQP7* govern mucosal water transport; *SLC16A1* (MCT1) mediates short-chain fatty acid (butyrate) uptake; *SLC51A* (OST-alpha) mediates basolateral bile acid export; *SLC38A4* and *SLC23A1* transport amino acids and ascorbic acid. Coordinated suppression accounts for mucosal malabsorption and diarrhea in UC.
* **Evidence Strength & Limitations:** Extensive co-downregulation across distinct transporter gene families with extremely low FDR values. *Limitation:* Loss of transport expression is confounded by mucosal denudation and loss of mature surface colonocytes.

#### Program 5: Colonocyte Epithelial Metabolism and Digestive Enzyme Loss
* **Direction:** Downregulated in UC
* **Major Supporting Genes:** *HMGCS2* ($\log_2\text{FC} = -3.45, \text{FDR} = 1.10 \times 10^{-16}$), *MEP1B* ($\log_2\text{FC} = -2.99, \text{FDR} = 1.11 \times 10^{-22}$), *GBA3* ($\log_2\text{FC} = -3.00, \text{FDR} = 4.12 \times 10^{-17}$), *ABCG2* ($\log_2\text{FC} = -2.92, \text{FDR} = 1.11 \times 10^{-10}$), *DEFB1* ($\log_2\text{FC} = -2.31, \text{FDR} = 1.25 \times 10^{-10}$), *HSD3B2* ($\log_2\text{FC} = -2.77, \text{FDR} = 4.62 \times 10^{-16}$)
* **Standardized Pathway:** KEGG: Butanoate metabolism (`hsa00650`) / GO: Carboxylic Acid Metabolic Process (`GO:0190161`)
* **Biological Rationale:** *HMGCS2* is the rate-limiting mitochondrial enzyme for colonocyte ketogenesis from microbial butyrate. *MEP1B* (meprin A subunit beta) and *DEFB1* (beta-defensin 1) maintain mucosal barrier processing and antimicrobial homeostasis. *GBA3* and *ABCG2* mediate epithelial xenobiotic clearance and lipid handling.
* **Evidence Strength & Limitations:** Consistent suppression of key brush-border and mitochondrial enzymes. *Limitation:* Cannot separate cell-intrinsic transcriptional repression from crypt architecture disruption and enterocyte loss.

---

### 3. Key Genes and Interaction Modules

1. **SLC6A14**
   * **Direction:** Upregulated ($\log_2\text{FC} = 4.85, \text{FDR} = 8.07 \times 10^{-39}$)
   * **Role:** Na+/Cl--coupled concentrative amino acid transporter induced at mucosal surfaces during severe inflammation and nutrient stress.
   * **Relationship Type:** *Indirect / Putative relationship* (co-expressed with inflammatory signaling networks; functional transporter).

2. **DUOX2 / DUOXA2 Module**
   * **Direction:** Upregulated (*DUOX2*: $\log_2\text{FC} = 4.67, \text{FDR} = 4.45 \times 10^{-26}$; *DUOXA2*: $\log_2\text{FC} = 2.89, \text{FDR} = 1.12 \times 10^{-10}$)
   * **Role:** Apical hydrogen peroxide-generating system providing mucosal antimicrobial ROS defense.
   * **Relationship Type:** *Direct physical interaction* (DUOX2 forms an obligate protein complex with DUOXA2 for membrane trafficking and enzyme maturation) and *Pathway co-membership*.

3. **CXCL1 / CXCL2 / CXCL3 Chemokine Cluster**
   * **Direction:** Upregulated (*CXCL1*: $\log_2\text{FC} = 3.46$; *CXCL2*: $\log_2\text{FC} = 2.80$; *CXCL3*: $\log_2\text{FC} = 2.33$; all $\text{FDR} < 10^{-10}$)
   * **Role:** Paracrine signaling cluster recruiting neutrophils to inflamed colonic tissue.
   * **Relationship Type:** *Pathway co-membership* and *Regulatory interaction* (all three ligands bind directly to the cell-surface receptor CXCR2; highly co-expressed).

4. **AQP8**
   * **Direction:** Downregulated ($\log_2\text{FC} = -4.42, \text{FDR} = 1.60 \times 10^{-13}$)
   * **Role:** Apical colonocyte water channel essential for luminal fluid absorption.
   * **Relationship Type:** *Pathway co-membership* and *Co-expression* with mucosal solute transport networks (*AQP7*, *SLC16A1*, *SLC51A*).

5. **MMP3 / TIMP1 Remodeling Pair**
   * **Direction:** Upregulated (*MMP3*: $\log_2\text{FC} = 4.64, \text{FDR} = 5.40 \times 10^{-14}$; *TIMP1*: $\log_2\text{FC} = 1.97, \text{FDR} = 1.81 \times 10^{-17}$)
   * **Role:** Counter-balanced enzymatic system controlling stromal breakdown and tissue remodeling in ulcerated mucosa.
   * **Relationship Type:** *Direct physical interaction* (TIMP1 protein binds and inhibits active MMP3 enzyme) and *Pathway co-membership*.

6. **HMGCS2**
   * **Direction:** Downregulated ($\log_2\text{FC} = -3.45, \text{FDR} = 1.10 \times 10^{-16}$)
   * **Role:** Rate-limiting enzyme for mitochondrial ketogenesis from short-chain fatty acids (butyrate) in mature colonocytes.
   * **Relationship Type:** *Pathway co-membership* with *SLC16A1* (butyrate uptake transporter) and *GBA3*.

7. **S100A8 / LCN2 Alarming Axis**
   * **Direction:** Upregulated (*S100A8*: $\log_2\text{FC} = 3.80, \text{FDR} = 4.43 \times 10^{-11}$; *LCN2*: $\log_2\text{FC} = 2.67, \text{FDR} = 1.37 \times 10^{-21}$)
   * **Role:** Neutrophil-derived antimicrobial proteins and inflammatory alarmins released into the mucosal microenvironment.
   * **Relationship Type:** *Co-expression* (co-released by activated mucosal granulocytes) and *Pathway co-membership* (neutrophil degranulation); S100A8 also forms a *direct physical interaction* with S100A9 to form calprotectin.

8. **MEP1B**
   * **Direction:** Downregulated ($\log_2\text{FC} = -2.99, \text{FDR} = 1.11 \times 10^{-22}$)
   * **Role:** Brush-border metalloprotease regulating mucosal peptide digestion and barrier protection.
   * **Relationship Type:** *Pathway co-membership* and *Co-expression* with enterocyte differentiation programs.

9. **CTLA4 / SOCS3 Immunoregulatory Module**
   * **Direction:** Upregulated (*CTLA4*: $\log_2\text{FC} = 2.62, \text{FDR} = 1.11 \times 10^{-10}$; *SOCS3*: $\log_2\text{FC} = 2.79, \text{FDR} = 8.13 \times 10^{-12}$)
   * **Role:** Downstream negative feedback regulators suppressing T-cell co-stimulation (*CTLA4*) and cytokine/STAT3 signaling (*SOCS3*).
   * **Relationship Type:** *Regulatory interaction* and *Pathway co-membership* in immune receptor negative feedback cascades.

10. **SLC51A (OST-alpha)**
    * **Direction:** Downregulated ($\log_2\text{FC} = -3.71, \text{FDR} = 1.54 \times 10^{-20}$)
    * **Role:** Subunit of the heteromeric basolateral organic solute transporter required for intestinal bile acid recycling.
    * **Relationship Type:** *Direct physical interaction* (forms a obligate heterodimer with SLC51B/OST-beta) and *Pathway co-membership*.

---

### 4. Validation Priorities

#### Priority 1: Epithelial DUOX2/DUOXA2 Hydrogen Peroxide Generation Engine
* **Classification:** Mechanistic hypothesis
* **Prioritization Rationale:** *DUOX2* exhibits one of the largest upregulation values ($\log_2\text{FC} = 4.67$) alongside stoichiometric induction of *DUOXA2*, placing epithelial oxidative burst at the center of mucosal host-microbial interactions.
* **Dataset Evidence:** Robust upregulation of *DUOX2* ($\text{FDR} = 4.45 \times 10^{-26}$) and *DUOXA2* ($\text{FDR} = 1.12 \times 10^{-10}$).
* **External Evidence:** Reactome records confirm the DUOX2-DUOXA2 enzymatic complex; published literature implicates DUOX2 activation in mucosal defense and IBD pathogenesis.
* **Next Steps:** Evaluate patient-derived colonic organoids co-cultured with gut anaerobes under DUOX2 shRNA knockdown or pharmacological inhibition to measure apical H2O2 flux, barrier integrity, and oxidative DNA damage.
* **Evidence Level:** Supported hypothesis.

#### Priority 2: Restoration of Colonocyte Butyrate Oxidation via HMGCS2 / SLC16A1 Resuscitation
* **Classification:** Therapeutic target
* **Prioritization Rationale:** Loss of *HMGCS2* ($\log_2\text{FC} = -3.45$) and *SLC16A1* ($\log_2\text{FC} = -2.38$) points to colonocyte energy starvation, contributing to epithelial atrophy and impaired mucosal healing.
* **Dataset Evidence:** Highly significant downregulation of both butyrate uptake (*SLC16A1*) and mitochondrial utilization (*HMGCS2*) genes.
* **External Evidence:** Literature confirms deficient butyrate oxidation in active UC mucosa. Note: The presence of PPAR-gamma agonists or metabolic modulators in chemical databases does not prove clinical therapeutic efficacy in UC.
* **Next Steps:** Ex vivo metabolic flux analysis using $^{13}\text{C}$-labeled butyrate on human colonic mucosal biopsies exposed to metabolic enhancers (e.g., PPAR-gamma agonists) to evaluate restoration of ketogenesis and oxygen consumption.
* **Evidence Level:** Supported hypothesis.

#### Priority 3: Non-Invasive Mucosal Remodeling Biomarker Panel (MMP3, CHI3L1, CXCL1, S100A8)
* **Classification:** Biomarker
* **Prioritization Rationale:** These factors encode secreted proteins with marked upregulation ($\log_2\text{FC} > 3.4$), suitable for serial non-invasive tracking of mucosal ulceration and healing.
* **Dataset Evidence:** Concordant elevation of matrix-degrading (*MMP3*, *CHI3L1*) and leukocyte-recruiting (*CXCL1*, *S100A8*) transcripts.
* **External Evidence:** S100A8/A9 (fecal calprotectin) is an established clinical biomarker. Published studies report serum MMP3 and CHI3L1 correlation with endoscopic Mayo subscores [PMID: 41029776].
* **Next Steps:** Prospective clinical validation measuring serum and stool protein levels via ELISA across longitudinal UC cohorts before and after anti-TNF/anti-integrin therapy, correlated with endoscopic mucosal healing.
* **Evidence Level:** Supported hypothesis.

#### Priority 4: CXCR2-Mediated Paracrine Neutrophil Recruitment Network
* **Classification:** Interaction / network hypothesis
* **Prioritization Rationale:** Redundant activation of *CXCL1*, *CXCL2*, and *CXCL3* converges on the CXCR2 receptor to drive granulocyte infiltration.
* **Dataset Evidence:** Synchronous upregulation of all three CXCR2 ligands ($\text{FDR} < 10^{-10}$).
* **External Evidence:** STRING and OmniPath confirm physical receptor-ligand interaction between CXCL chemokines and CXCR2; small-molecule CXCR2 antagonists demonstrate anti-inflammatory effects in animal colitis models.
* **Next Steps:** Microfluidic migration assays measuring primary human neutrophil chemotaxis toward UC mucosal explant supernatants in the presence of selective CXCR2 inhibitors.
* **Evidence Level:** Supported hypothesis.

#### Priority 5: Distinguishing Crypt Cell-Intrinsic Repression from Epithelial Denudation
* **Classification:** Confounding or composition check
* **Prioritization Rationale:** Bulk mucosal biopsies mix epithelial loss, stromal expansion, and leukocyte infiltration, which can mimic cell-intrinsic gene suppression.
* **Dataset Evidence:** Severe downregulation of enterocyte markers (*AQP8*, *MEP1B*, *SLC51A*).
* **External Evidence:** Single-cell RNA sequencing of UC mucosa demonstrates both mature enterocyte depletion and intrinsic downregulation of transport programs.
* **Next Steps:** Single-cell RNA sequencing or spatial transcriptomics paired with quantitative RNA in situ hybridization (FISH) on UC mucosal sections to measure per-cell transcript density in remaining epithelial cells versus total enterocyte population counts.
* **Evidence Level:** Exploratory hypothesis.

---

### 5. Evidence Grounding

* **Direct Evidence (Input Dataset):** Preserved statistical values from the primary dataset represent direct evidence for all 100 differentially expressed genes. Note that external statistical validation was not performed on an independent cohort in this dataset context.
* **Pathway / Ontology Evidence:** Standardized GO and KEGG pathways (e.g., IL-17 signaling, fluid transport, ROS production) provide functional grouping of co-regulated genes.
* **Protein Interaction / Regulatory Evidence:** Databases (STRING, IntAct) document physical protein complexes (*DUOX2*–*DUOXA2*, *MMP3*–*TIMP1*, *SLC51A*–*SLC51B*, *S100A8*–*S100A9*) and receptor-ligand pairings (*CXCL1/2/3* with CXCR2).
* **Tissue / Expression Evidence:** HPA and GTEx confirm that *AQP8*, *HMGCS2*, *MEP1B*, and *SLC51A* are physiologically enriched in colonic mucosal epithelium, whereas *CXCL1/2/3* and *S100A8* are predominant in activated immune cells.
* **Drug / Therapeutic Evidence:** ChEMBL and OpenTargets list agents targeting *CTLA4*, *MMP3*, and CXCR2. However, the presence of a drug target record does not establish therapeutic efficacy for UC.
* **Published Literature Evidence:** Literature context (e.g., *BRINP3* downregulation in UC mucosal transcriptomes [PMID: 25171508]; *IRAK3* immune regulation [PMID: 40918148]; WGCNA biomarker studies in UC [PMID: 41029776]) provides external functional framing.
* **Conflicting Evidence & Ambiguity:** While *CTLA4* is upregulated ($\log_2\text{FC} = 2.62$), whole-tissue transcriptomics cannot resolve whether elevated *CTLA4* reflects active immunosuppression by regulatory T cells or compensatory elevation secondary to dense T-effector cell infiltration.

---

### 6. Limitations and Alternative Explanations

1. **Tissue Heterogeneity and Cell-Composition Confounding:** Active UC biopsies suffer from mucosal erosion and crypt loss alongside immune infiltration. Downregulation of *AQP8* or *HMGCS2* and upregulation of *S100A8* or *CXCL1* may primarily reflect changes in cell type proportions rather than intrinsic per-cell transcriptional changes. This can be resolved using spatial transcriptomics or single-cell deconvolution algorithms.
2. **Absence of External Independent Cohort Validation:** External statistical validation was not performed on an independent validation cohort in this study context. Effect sizes and FDR values rely on a single input dataset, requiring caution until reproduced in independent public datasets (e.g., GEO cohorts).
3. **Association versus Causation Ambiguity:** Induction of *DUOX2* and *MMP3* may represent secondary reactive responses to mucosal tissue injury rather than primary pathogenic drivers. Mendelian Randomization (MR) using GWAS risk variants is required to test causality.
4. **Unmeasured Medication Exposure and Severity:** Baseline transcriptomic profiles can be modified by patient exposure to 5-ASAs, corticosteroids, or biologic therapies, which may suppress inflammatory genes or induce regulatory factors (*SOCS3*, *IL1RN*). Stratification by treatment status and Mayo endoscopic score is necessary.
5. **Broad Pathway Enriched Features:** High-level ontology terms (e.g., "protein binding" or "cellular process") encompass heterogeneous biological functions. Functional interpretations must rely on specific physical complexes (*DUOX2*–*DUOXA2*) and direct pathway nodes rather than generic ontology broadness.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=0, external claims checked=0, external mismatches=0, status=passed.

Answer model API: Google Gemini / gemini-3.6-flash

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 94/100 selected items (records returned); cbioportal 87/100 selected items (records returned); chembl 40/100 selected items (partially returned; some queries failed); civic 7/100 selected items (records returned); clinicaltrials 51/100 selected items (records returned); clinvar 90/100 selected items (records returned); ensembl 55/100 selected items (partially returned; some queries failed); europepmc 936 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 91/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 85/100 selected items (records returned); humanbase 87/100 selected items (records returned); intact 85/100 selected items (records returned); mygene 93/100 selected items (records returned); omnipath 45/100 selected items (records returned); opentargets 92/100 selected items (records returned); pubmed 750 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 87/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 88/100 selected items (records returned)
Local databases: gutmgene 8/100 selected items (records returned); hmdb 46/100 selected items (records returned); string 85/100 selected items (records returned); trrust 31/100 selected items (records returned)
