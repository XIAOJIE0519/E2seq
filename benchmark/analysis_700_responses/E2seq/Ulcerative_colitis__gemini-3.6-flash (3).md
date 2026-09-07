# ulcerative colitis (UC) - gemini-3.6-flash

- Benchmark system: E2seq + Agent RAG
- Repeat: 3
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
- Prompt tokens: 56021
- Completion tokens: 40744
- Reasoning tokens: 18445
- Total tokens: 96765
- API requests reported: 3
- Elapsed seconds: 46.64
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 1095.213
- Question handoff seconds: 1109.559
- Final benchmark system: E2seq; file rank 3/5; original repeat 3; model vendor: Google Gemini

---
### 1. Overall Biological Interpretation

The transcriptomic profile comparing colonic mucosal tissue from ulcerative colitis (UC) patients against healthy controls reveals a marked dysregulation characterized by reciprocal cellular and physiological shifts:

1. **Upregulation of Mucosal Inflammation and Innate/Adaptive Immune Activation**: Upregulated genes are dominated by neutrophil-recruiting chemokines (*CXCL1*, *CXCL2*, *CXCL3*), inflammatory alarmins (*S100A8*, *S100P*, *LCN2*), immune checkpoint markers (*CTLA4*), and mucosal hydrogen peroxide-generating complexes (*DUOX2*, *DUOXA2*). In addition, robust upregulation of tissue-remodeling enzymes (*MMP3*) and extracellular matrix (ECM) components (*TNC*, *PDPN*) reflects active tissue injury and stromal remodeling within the inflamed mucosal niche.
2. **Downregulation of Mature Epithelial Transport and Energy Metabolism**: Downregulated genes reflect loss or functional suppression of mature intestinal epithelial cell processes. This includes marked reduction of transcellular water channels (*AQP8*, *AQP7*), solute and organic anion/cation transporters (*SLC51A*, *SLC38A4*, *SLC23A1*, *SLC16A1*), mitochondrial ketogenesis (*HMGCS2*), brush-border peptidases (*MEP1B*), and drug/xenobiotic detoxification pathways (*ABCG2*, *CYP2B6*, *UGT2A3*, *GBA3*).

A notable exception to the general down-regulation of solute transporters is the nutrient transporter *SLC6A14* ($\text{log}_2\text{FC} = 4.85$, $\text{FDR} = 8.07 \times 10^{-39}$), which is markedly upregulated. This reflects an adaptive or inflammatory upregulation of specific amino acid transport under mucosal stress. Overall, these transcriptomic changes illustrate a functional collapse of normal epithelial transport and barrier metabolism alongside immune cell infiltration and matrix destruction.

---

### 2. Core Biological Programs

```
                       +-------------------------------------------------------+
                       |        Ulcerative Colitis Mucosal Transcriptome        |
                       +-------------------------------------------------------+
                                                   |
                     +-----------------------------+-----------------------------+
                     |                                                           |
        [ Upregulated Pathogenic Programs ]                         [ Downregulated Homeostatic Programs ]
                     |                                                           |
   +-----------------+-----------------+                         +---------------+---------------+
   |                                   |                         |                               |
Program 1:                          Program 2:                Program 3:                      Program 4:
Innate Immune & Chemokine           Mucosal ROS &             Epithelial Water &              Epithelial Xenobiotic &
Recruitment                         Antimicrobial Defense     Solute Transport Loss           Metabolic Dysfunction
(CXCL1, CXCL2, S100A8)              (DUOX2, DUOXA2, PI3)      (AQP8, AQP7, SLC51A)            (HMGCS2, ABCG2, MEP1B)
   |                                   |                         |                               |
   +-----------------+-----------------+                         +---------------+---------------+
                     |                                                           |
                     +-----------------------------+-----------------------------+
                                                   |
                                              Program 5:
                                      ECM Remodeling & Fibrosis
                                        (MMP3, TNC, PDPN)
```

#### Program 1: Inflammatory Chemokine Recruitment & Innate Immune Response
* **Direction**: Upregulated
* **Major Supporting Genes**: *CXCL1* ($\text{log}_2\text{FC} = 3.46$, $\text{FDR} = 1.15 \times 10^{-15}$), *CXCL2* ($\text{log}_2\text{FC} = 2.80$, $\text{FDR} = 1.73 \times 10^{-11}$), *CXCL3* ($\text{log}_2\text{FC} = 2.33$, $\text{FDR} = 2.51 \times 10^{-11}$), *S100A8* ($\text{log}_2\text{FC} = 3.80$, $\text{FDR} = 4.43 \times 10^{-11}$), *LCN2* ($\text{log}_2\text{FC} = 2.67$, $\text{FDR} = 1.37 \times 10^{-21}$), *SOCS3* ($\text{log}_2\text{FC} = 2.79$, $\text{FDR} = 8.13 \times 10^{-12}$).
* **Standardized Pathway**: KEGG: IL-17 signaling pathway (hsa04657) / GO: Inflammatory Response (GO:0006954).
* **Biological Rationale**: Co-upregulation of ELR+ CXC chemokines (*CXCL1/2/3*) alongside neutrophil granule components (*S100A8*, *LCN2*) indicates intense neutrophil attraction and activation in the colonic mucosa during active UC flare.
* **Evidence Strength & Limitations**: High direct statistical significance in the dataset. However, because external statistical validation was not performed on an independent cohort, these values represent single-cohort differential expressions.

#### Program 2: Mucosal Epithelial ROS Generation & Antimicrobial Defense
* **Direction**: Upregulated
* **Major Supporting Genes**: *DUOX2* ($\text{log}_2\text{FC} = 4.67$, $\text{FDR} = 4.45 \times 10^{-26}$), *DUOXA2* ($\text{log}_2\text{FC} = 2.89$, $\text{FDR} = 1.12 \times 10^{-10}$), *PI3* ($\text{log}_2\text{FC} = 2.21$, $\text{FDR} = 3.97 \times 10^{-19}$), *SERPINB5* ($\text{log}_2\text{FC} = 3.29$, $\text{FDR} = 2.58 \times 10^{-17}$), *VNN1* ($\text{log}_2\text{FC} = 3.20$, $\text{FDR} = 1.54 \times 10^{-15}$).
* **Standardized Pathway**: Reactome: ROS and RNS production in phagocytes (R-HSA-1221633) / GO: Antimicrobial Humoral Response (GO:0019730).
* **Biological Rationale**: Dual oxidase 2 (*DUOX2*) and its maturation factor *DUOXA2* form a functional complex on epithelial surfaces that produces reactive oxygen species ($\text{H}_2\text{O}_2$) for mucosal host defense. Their co-induction alongside anti-proteases (*PI3*, *SERPINB5*) highlights an activated epithelial antimicrobial barrier response.
* **Evidence Strength & Limitations**: Robust concordant upregulation of both enzyme subunits. External statistical validation was not performed.

#### Program 3: Epithelial Water and Solute Transport Breakdown
* **Direction**: Downregulated
* **Major Supporting Genes**: *AQP8* ($\text{log}_2\text{FC} = -4.42$, $\text{FDR} = 1.60 \times 10^{-13}$), *AQP7* ($\text{log}_2\text{FC} = -2.32$, $\text{FDR} = 4.04 \times 10^{-20}$), *SLC51A* ($\text{log}_2\text{FC} = -3.71$, $\text{FDR} = 1.54 \times 10^{-20}$), *SLC38A4* ($\text{log}_2\text{FC} = -3.07$, $\text{FDR} = 4.70 \times 10^{-37}$), *SLC23A1* ($\text{log}_2\text{FC} = -2.40$, $\text{FDR} = 8.89 \times 10^{-29}$), *SLC16A1* ($\text{log}_2\text{FC} = -2.38$, $\text{FDR} = 5.83 \times 10^{-21}$).
* **Standardized Pathway**: GO: Fluid Transport (GO:0042044) / GO: Water Transport (GO:0006833) / GO: Carboxylic Acid Transport (GO:0046942).
* **Biological Rationale**: The loss of apical and basolateral channels responsible for water absorption (*AQP8*, *AQP7*), bile salt transport (*SLC51A*), short-chain fatty acid transport (*SLC16A1*), and vitamin C uptake (*SLC23A1*) directly accounts for mucosal malabsorption and secretory diarrhea symptoms in UC.
* **Evidence Strength & Limitations**: Multiple independent solute carriers demonstrate uniform downregulation. External statistical validation was not performed.

#### Program 4: Epithelial Xenobiotic Clearance & Metabolic Dysfunction
* **Direction**: Downregulated
* **Major Supporting Genes**: *HMGCS2* ($\text{log}_2\text{FC} = -3.45$, $\text{FDR} = 1.10 \times 10^{-16}$), *ABCG2* ($\text{log}_2\text{FC} = -2.92$, $\text{FDR} = 1.11 \times 10^{-10}$), *MEP1B* ($\text{log}_2\text{FC} = -2.99$, $\text{FDR} = 1.11 \times 10^{-22}$), *GBA3* ($\text{log}_2\text{FC} = -3.00$, $\text{FDR} = 4.12 \times 10^{-17}$), *CYP2B6* ($\text{log}_2\text{FC} = -2.78$, $\text{FDR} = 4.18 \times 10^{-13}$), *UGT2A3* ($\text{log}_2\text{FC} = -2.68$, $\text{FDR} = 7.16 \times 10^{-11}$).
* **Standardized Pathway**: KEGG: Bile secretion (hsa04976) / KEGG: Metabolism of xenobiotics by cytochrome P450 (hsa00980).
* **Biological Rationale**: Decreased expression of rate-limiting ketogenesis enzymes (*HMGCS2*), efflux transporters (*ABCG2*), brush-border metalloproteases (*MEP1B*), and phase I/II detoxification enzymes indicates widespread metabolic failure of enterocytes due to tissue damage.
* **Evidence Strength & Limitations**: Highly consistent down-regulation across enzymatic families. External statistical validation was not performed.

#### Program 5: Extracellular Matrix Remodeling & Stromal Tissue Response
* **Direction**: Upregulated
* **Major Supporting Genes**: *MMP3* ($\text{log}_2\text{FC} = 4.64$, $\text{FDR} = 5.40 \times 10^{-14}$), *PRRX1* ($\text{log}_2\text{FC} = 2.91$, $\text{FDR} = 4.35 \times 10^{-16}$), *TNC* ($\text{log}_2\text{FC} = 2.58$, $\text{FDR} = 2.51 \times 10^{-11}$), *PDPN* ($\text{log}_2\text{FC} = 2.54$, $\text{FDR} = 1.75 \times 10^{-10}$), *TIMP1* ($\text{log}_2\text{FC} = 1.97$, $\text{FDR} = 1.81 \times 10^{-17}$).
* **Standardized Pathway**: Reactome: Degradation of the extracellular matrix (R-HSA-1474228) / GO: Extracellular Matrix Organization (GO:0030198).
* **Biological Rationale**: Marked induction of stromal and matrix metalloproteinases (*MMP3*), tenascin-C (*TNC*), podoplanin (*PDPN*), and fibroblast transcription factors (*PRRX1*) reflects active connective tissue degradation, mucosal ulceration, and wound repair responses in inflamed lesions.
* **Evidence Strength & Limitations**: Multi-gene matrix degradation module upregulation. External statistical validation was not performed.

---

### 3. Key Genes and Interaction Modules

| Key Gene / Module | Direction in Dataset | Core Program Association | Proposed Relationship Type | Biological & Interaction Context |
| :--- | :--- | :--- | :--- | :--- |
| **CXCL1 – CXCL2 – CXCL3** | Upregulated ($\text{log}_2\text{FC} = 2.33\text{ to }3.46$) | Program 1 (Innate Immune) | **Pathway co-membership & Receptor shared binding** | All three chemokines bind the CXCR2 receptor on neutrophils (OmniPath/STRING records). They are co-expressed in response to pro-inflammatory cytokines like IL-17 and TNF. |
| **DUOX2 – DUOXA2** | Upregulated ($\text{log}_2\text{FC} = 4.67\text{ and }2.89$) | Program 2 (ROS Defense) | **Direct physical interaction & Functional complex** | DUOXA2 acts as an essential ER-to-plasma membrane maturation factor and protein chaperone that heterodimerizes with DUOX2 to form functional hydrogen peroxide-producing complexes. |
| **AQP8 – AQP7** | Downregulated ($\text{log}_2\text{FC} = -4.42\text{ and }-2.32$) | Program 3 (Fluid Transport) | **Pathway co-membership** | Both belong to the aquaporin family (GO: Water Transport). They exhibit co-regulated depletion due to epithelial cell injury; no direct protein-protein physical binding is implied. |
| **SLC6A14** | Upregulated ($\text{log}_2\text{FC} = 4.85$, $\text{FDR} = 8.07 \times 10^{-39}$) | Program 1 & 3 (Transporter Adaptivity) | **Co-expression / Functional shift** | Concentrative amino acid transporter ($\text{Na}^+/\text{Cl}^-$-dependent). Unlike other solute carriers, it is dramatically induced during mucosal inflammation to supply amino acids to proliferating cells. |
| **HMGCS2** | Downregulated ($\text{log}_2\text{FC} = -3.45$, $\text{FDR} = 1.10 \times 10^{-16}$) | Program 4 (Metabolism) | **Pathway co-membership** | Rate-limiting enzyme in mitochondrial ketogenesis. Key marker of functional, differentiated colonocyte bioenergetics; lost upon mucosal erosion. |
| **MMP3 – TIMP1** | Upregulated ($\text{log}_2\text{FC} = 4.64\text{ and }1.97$) | Program 5 (ECM Remodeling) | **Regulatory interaction & Enzyme-inhibitor binding** | MMP3 degrades collagen and matrix components; TIMP1 is an endogenous inhibitor that physically binds MMP3 to regulate proteolytic tissue turnover. |
| **S100A8 – LCN2** | Upregulated ($\text{log}_2\text{FC} = 3.80\text{ and }2.67$) | Program 1 (Innate Immunity) | **Co-expression** | Highly induced antimicrobial proteins originating from infiltrating neutrophils and activated epithelial cells; co-regulated under NF-$\kappa$B and STAT3 signaling. |
| **CTLA4** | Upregulated ($\text{log}_2\text{FC} = 2.62$, $\text{FDR} = 1.11 \times 10^{-10}$) | Program 1 (Adaptive Immunity) | **Co-expression** | Inhibitory receptor expressed on activated T lymphocytes and regulatory T cells (Tregs). Reflects dense infiltration of adaptive immune cells into the mucosal lamina propria. |
| **BRINP3** | Downregulated ($\text{log}_2\text{FC} = -2.13$, $\text{FDR} = 6.95 \times 10^{-12}$) | Program 3 & 4 (Epithelial Homeostasis) | **Indirect / Putative relationship** | Downregulated in mucosal biopsies from active UC patients (literature support: PMID 25171508); implicated in mucosal growth regulation and homeostatic signaling. |
| **SLC51A** | Downregulated ($\text{log}_2\text{FC} = -3.71$, $\text{FDR} = 1.54 \times 10^{-20}$) | Program 3 (Bile Transport) | **Pathway co-membership** | Heterodimeric organic solute transporter alpha subunit (OST$\alpha$) involved in basolateral transport of bile acids and steroids in mucosal epithelial cells. |

---

### 4. Validation Priorities

```
+-----------------------------------------------------------------------------------+
|                            Targeted Validation Plan                               |
+-----------------------------------------------------------------------------------+
                                          |
    +-------------------+-----------------+-------------------+-------------------+
    |                   |                 |                   |                   |
[ Priority 1 ]      [ Priority 2 ]    [ Priority 3 ]      [ Priority 4 ]      [ Priority 5 ]
Mechanistic         Therapeutic       Biomarker           Interaction Net     Composition
DUOX2/DUOXA2        SLC6A14 Blockade  AQP8 Loss           CXCL-CXCR2 Axis     Epithelial/Leukocyte
ROS Axis            Inhibitor         Mucosal Secretion   Neutrophil Chemotax Single-Cell Deconv
    |                   |                 |                   |                   |
    v                   v                 v                   v                   v
Organoid ROS        In vitro Transport Immunohistochem.     Transwell Migration Single-cell RNA-seq
Assay & Knockout    Inhibition        Biopsy Staining     Receptor Assay      & Flow Cytometry
```

#### Priority 1: DUOX2 / DUOXA2 Epithelial Oxidative Stress Axis
* **Classification**: Mechanistic hypothesis
* **Prioritization Rationale**: *DUOX2* and *DUOXA2* are among the most strongly induced genes in the entire dataset ($\text{log}_2\text{FC} = 4.67$ and $2.89$). Uncontrolled epithelial ROS production may contribute directly to mucosal double-strand DNA damage and barrier disruption.
* **Input Dataset Evidence**: Strong co-upregulation of enzyme and maturation accessory subunit ($P < 2 \times 10^{-13}$).
* **External Evidence**: Literature and pathway records confirm DUOX2/DUOXA2 form a heterodimeric complex in mucosal enterocytes responsible for luminal $\text{H}_2\text{O}_2$ synthesis in IBD.
* **Next Validation Step**: Perform dual-immunofluorescence and hydrogen peroxide quantification in patient-derived colonic organoids under IL-17/TNF-$\alpha$ stimulation with CRISPR knockout of *DUOX2*.
* **Current Conclusion Status**: Supported hypothesis.

#### Priority 2: SLC6A14 Amino Acid Transporter Upregulation
* **Classification**: Therapeutic target
* **Prioritization Rationale**: *SLC6A14* shows the largest positive fold-change in the dataset ($\text{log}_2\text{FC} = 4.85$, $\text{FDR} = 8.07 \times 10^{-39}$). As a broad-spectrum amino acid transporter, its upregulation may nourish infiltrating immune cells or hyper-metabolic inflamed epithelium.
* **Input Dataset Evidence**: Top-ranked upregulated gene by statistical significance and effect size.
* **External Evidence**: Literature confirms SLC6A14 is upregulated in inflamed gut mucosa and solid tumors; small-molecule inhibitors exist (e.g., $\alpha$-methyl-DL-tryptophan). However, drug availability alone does not establish therapeutic efficacy in UC.
* **Next Validation Step**: Test whether pharmacological blockade of SLC6A14 reduces inflammatory cytokine output or cell viability in human mucosal explants.
* **Current Conclusion Status**: Exploratory hypothesis.

#### Priority 3: AQP8 Transcellular Fluid Transport Suppression
* **Classification**: Biomarker
* **Prioritization Rationale**: *AQP8* shows the largest negative fold-change in the dataset ($\text{log}_2\text{FC} = -4.42$, $\text{FDR} = 1.60 \times 10^{-13}$). Loss of apical water channels directly correlates with mucosal diarrhea severity.
* **Input Dataset Evidence**: Marked downregulation alongside *AQP7* ($\text{log}_2\text{FC} = -2.32$).
* **External Evidence**: Reactome and QuickGO classify AQP8 in passive water transport; literature reports loss of AQP8 transcript and protein in active UC mucosal biopsies (PMID 41029776).
* **Next Validation Step**: Evaluate AQP8 protein loss by quantitative immunohistochemistry in endoscopic mucosal biopsies across mild, moderate, and severe UC cohorts to evaluate diagnostic concordance.
* **Current Conclusion Status**: Supported hypothesis.

#### Priority 4: CXCL1 / CXCL2 / CXCL3 – CXCR2 Chemokine Signaling Axis
* **Classification**: Interaction / network hypothesis
* **Prioritization Rationale**: The ELR+ CXC chemokine cluster (*CXCL1*, *CXCL2*, *CXCL3*) is uniformly upregulated ($\text{log}_2\text{FC} > 2.3$), driving neutrophil recruitment into mucosal crypts (crypt abscesses).
* **Input Dataset Evidence**: Synchronous upregulation of three tandem CXCR2 ligands ($P < 3.5 \times 10^{-14}$).
* **External Evidence**: STRING and OmniPath interaction records validate direct chemokine receptor binding; published literature (PMID 41029776) identifies neutrophil chemokine networks in active colitis.
* **Next Validation Step**: Transwell neutrophil migration assays utilizing mucosal supernatant from UC biopsies with and without selective CXCR2 antagonists.
* **Current Conclusion Status**: Supported hypothesis.

#### Priority 5: Epithelial Cell Attrition vs. Immune Infiltration Compositional Deconvolution
* **Classification**: Confounding or composition check
* **Prioritization Rationale**: Massive downregulation of epithelial-specific transporters (*SLC51A*, *HMGCS2*, *MEP1B*) combined with upregulation of leukocyte markers (*CTLA4*, *S100A8*) may reflect shifts in cell type proportions rather than gene expression changes per cell.
* **Input Dataset Evidence**: Reciprocal expression pattern between enterocyte-specific and leukocyte-specific marker genes.
* **External Evidence**: Single-cell RNA-seq studies of human IBD mucosa show marked loss of mature colonocytes and expansion of inflammatory fibroblasts and immune subsets.
* **Next Validation Step**: Apply single-cell RNA-sequencing or digital deconvolution algorithms (e.g., CIBERSORTx) using matched tissue samples to isolate cell-type-specific transcriptional alterations from cell-frequency shifts.
* **Current Conclusion Status**: Supported hypothesis.

---

### 5. Evidence Grounding

To ensure scientific rigor, evidence sources supporting the main conclusions are explicit:

1. **Direct Evidence from Input Dataset**: All primary effect sizes ($\text{log}_2\text{FC}$), raw $P$ values, and FDR values cited throughout this report derive strictly from the user-provided analysis table (100 genes total: 40 upregulated, 60 downregulated).
2. **Pathway & Network Evidence**: GO terms (e.g., *Fluid Transport* [GO:0042044], *Water Transport* [GO:0006833]), KEGG pathways (e.g., *IL-17 signaling pathway*, *Bile secretion*), and STRING interaction networks (50 edge connections) provide functional context.
3. **Database & Literature Cross-referencing**: Tissue expression patterns (GTEx, HPA), regulatory networks (TRRUST), and published literature (e.g., PMID 41029776 for UC biomarkers, PMID 25171508 for mucosal *BRINP3* downregulation) support the disease relevance of key targets.
4. **Source Overlap Note**: Databases such as GO, KEGG, Reactome, and STRING share common underlying literature and primary protein annotations. Therefore, concurrence across these databases represents cross-annotation agreement rather than independent cohort replication.
5. **Statistical Validation Status**: **External statistical validation was not performed** on an independent cohort within this dataset. All findings must be interpreted as single-cohort differential expression discovery signals requiring independent validation.

---

### 6. Limitations and Alternative Explanations

1. **Cellular Composition Confounding**: Colonic biopsies from active UC patients suffer from severe erosion of surface epithelial cells and dense infiltration of neutrophils, plasma cells, and lymphocytes. Downregulation of *HMGCS2*, *AQP8*, and *MEP1B* may primarily reflect enterocyte loss rather than transcriptional repression within intact enterocytes.
2. **Lack of Clinical Metadata & Treatment Exposure**: The dataset lacks annotation for patient treatment history (e.g., 5-ASA, corticosteroids, anti-TNF, anti-IL12/23, or JAK inhibitors) and disease severity scores (Mayo score). Therapeutic agents alter gene expression profiles and can introduce unmeasured subgroup confounding.
3. **Absence of External Cohort Replication**: Because independent cohort statistical validation was not performed, dataset-specific batch effects or platform idiosyncrasies cannot be ruled out.
4. **Bulk Tissue Spatial Ambiguity**: Bulk tissue transcriptomics averages signal across mucosal crypts, lamina propria, submucosa, and luminal debris. Localized paracrine signals (such as focal matrix degradation by *MMP3* at ulcer margins) cannot be resolved spatially without spatial transcriptomics or single-cell approaches.
5. **Association vs. Causation Ambiguity**: Differential expression identifies correlations with the disease state but cannot establish whether individual gene alterations (such as high *SLC6A14* or low *BRINP3*) drive disease pathogenesis, protect against further damage, or act as secondary bystander consequences of mucosal inflammation.

---

### Final Summary

The transcriptomic landscape of ulcerative colitis colonic mucosa demonstrates a dual-pathology state marked by active innate immune activation, ROS production, and matrix degradation (*CXCL1/2/3*, *S100A8*, *DUOX2*, *MMP3*) alongside a breakdown of mature epithelial transport, water reabsorption, and xenobiotic metabolism (*AQP8*, *SLC51A*, *HMGCS2*, *ABCG2*). High-priority validation targets include the *DUOX2/DUOXA2* oxidative stress complex, the upregulated *SLC6A14* transporter, and cell-composition deconvolution to isolate true intracellular regulatory changes from mucosal cell-type shifts.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=0, external claims checked=0, external mismatches=0, status=passed.

Answer model API: Google Gemini / gemini-3.6-flash

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 94/100 selected items (records returned); cbioportal 87/100 selected items (records returned); chembl 40/100 selected items (partially returned; some queries failed); civic 7/100 selected items (records returned); clinicaltrials 51/100 selected items (records returned); clinvar 90/100 selected items (records returned); ensembl 55/100 selected items (partially returned; some queries failed); europepmc 936 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 91/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 85/100 selected items (records returned); humanbase 87/100 selected items (records returned); intact 85/100 selected items (records returned); mygene 93/100 selected items (records returned); omnipath 45/100 selected items (records returned); opentargets 92/100 selected items (records returned); pubmed 750 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 87/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 88/100 selected items (records returned)
Local databases: gutmgene 8/100 selected items (records returned); hmdb 46/100 selected items (records returned); string 85/100 selected items (records returned); trrust 31/100 selected items (records returned)
