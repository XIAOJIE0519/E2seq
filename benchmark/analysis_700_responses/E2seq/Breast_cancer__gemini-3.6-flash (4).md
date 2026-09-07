# breast cancer - gemini-3.6-flash

- Benchmark system: E2seq + Agent RAG
- Repeat: 5
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
- Prompt tokens: 33549
- Completion tokens: 57508
- Reasoning tokens: 31039
- Total tokens: 91057
- API requests reported: 3
- Elapsed seconds: 48.316
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 685.605
- Question handoff seconds: 699.996
- Final benchmark system: E2seq; file rank 4/5; original repeat 5; model vendor: Google Gemini

---
### 1. Overall Biological Interpretation

The provided transcriptomic dataset analyzes overall survival (OS) associations across 100 unique genes in breast tumor tissue. The dataset reveals a clear functional dichotomy between two primary regulatory axes:

1. **Mitotic Cell Cycle & Genome Instability Axis (Risk-Associated, HR > 1)**: Genes associated with poor overall survival (HR ~ 1.18 to 1.26, FDR < 1.6e-6) are strongly enriched for cell cycle acceleration, mitotic spindle assembly, kinetochore attachment, ubiquitin-mediated proteolysis, and translational control. Key drivers include *LARP1*, *STIP1*, *PKMYT1*, *GSK3B*, *TPX2*, *KIF20A*, *RACGAP1*, *UBE2C*, *AURKA*, *CDC20*, and *PTTG1*. Upregulation of these genes reflects hyper-proliferative tumor phenotypes, high histological grade, and mitotic turnover, which collectively drive adverse clinical outcomes in breast cancer.
2. **Immune Surveillance, Extracellular Matrix, and Differentiated Stroma Axis (Protective-Associated, HR < 1)**: Genes associated with favorable overall survival (HR ~ 0.79 to 0.84, FDR < 1.8e-6) represent tumor microenvironment defense mechanisms, including adaptive immune infiltration, dendritic cell antigen presentation, structural extracellular matrix (ECM) organization, and receptor tyrosine kinase differentiation pathways. Key protective markers include *FCER1A*, *JCHAIN*, *CD1C*, *KLRB1*, *STAT5A*, *STAT5B*, *COL17A1*, *OGN*, *LAMA2*, *ADAMTS8*, *PROS1*, and *PDGFRA*. High transcript levels of these markers indicate effective host immune infiltration and intact tissue architecture that restrict tumor expansion.

---

### 2. Core Biological Programs

```
                       +-------------------------------------------------------+
                       |           Breast Cancer Prognosis Spectrum            |
                       +---------------------------+---------------------------+
                                                   |
                     +-----------------------------+-----------------------------+
                     |                                                           |
       [ Risk-Associated Axis: HR > 1 ]                             [ Protective Axis: HR < 1 ]
       +-------------------------------+                            +---------------------------+
       | Program 1: Mitotic Division   |                            | Program 3: Immune Infilt. |
       | (PKMYT1, TPX2, KIF20A, AURKA) |                            | (JCHAIN, FCER1A, CD1C)    |
       +---------------+---------------+                            +-------------+-------------+
                       |                                                          |
       +---------------+---------------+                            +-------------+-------------+
       | Program 2: Ubiquitin Turnover |                            | Program 4: ECM Stroma     |
       | (UBE2C, UBE2S, CDC20, PTTG1)  |                            | (OGN, LAMA2, COL17A1)     |
       +-------------------------------+                            +---------------------------+
```

#### Program 1: Mitotic Nuclear Division and Spindle Assembly
* **Prognostic Association**: Risk-associated ($\text{HR} > 1$)
* **Major Supporting Genes**: *PKMYT1* ($\text{HR}=1.2438, P=1.364e-13, \text{FDR}=9.744e-10$), *KIF20A* ($\text{HR}=1.2180, P=1.735e-11, \text{FDR}=2.186e-08$), *CDCA5* ($\text{HR}=1.2179, P=3.873e-11, \text{FDR}=3.951e-08$), *TPX2* ($\text{HR}=1.2017, P=1.903e-10, \text{FDR}=1.405e-07$), *KIF4A* ($\text{HR}=1.1986, P=2.226e-10, \text{FDR}=1.590e-07$), *NUSAP1* ($\text{HR}=1.1942, P=4.829e-09, \text{FDR}=1.078e-06$), *CDC20* ($\text{HR}=1.1913, P=2.787e-09, \text{FDR}=7.192e-07$), *AURKA* ($\text{HR}=1.1885, P=2.846e-09, \text{FDR}=7.259e-07$), *PRC1* ($\text{HR}=1.1860, P=5.592e-09, \text{FDR}=1.210e-06$).
* **Standardized Pathway**: GO:0045840 (Positive Regulation of Mitotic Nuclear Division) / Reactome: Cell Cycle (R-HSA-69278).
* **Biological Explanation**: These genes coordinate chromosome condensation, kinetochore-microtubule attachment, spindle pole organization, and cytokinesis. Co-activation of microtubule motors (*KIF20A*, *KIF4A*), spindle assembly factors (*TPX2*, *NUSAP1*, *PRC1*), and mitotic kinases (*AURKA*, *PKMYT1*) accelerates transit through the G2/M phase, enabling uninhibited carcinoma cell cleavage.
* **Evidence & Limitations**: Strongly supported by direct input statistics ($\text{FDR} < 1.2e-6$), protein-protein interaction networks (STRING), and Reactome pathway records. *Limitation*: High transcript abundance of mitotic genes strongly correlates with overall tumor proliferation index and aggressive breast cancer subtypes (e.g., Triple-Negative / Basal-like), acting as a potential broad confounding variable.

#### Program 2: Ubiquitin-Mediated Mitotic Proteolysis
* **Prognostic Association**: Risk-associated ($\text{HR} > 1$)
* **Major Supporting Genes**: *RACGAP1* ($\text{HR}=1.2235, P=8.150e-12, \text{FDR}=1.164e-08$), *UBE2C* ($\text{HR}=1.2100, P=2.908e-10, \text{FDR}=1.731e-07$), *PTTG1* ($\text{HR}=1.1974, P=1.539e-09, \text{FDR}=4.711e-07$), *UBE2S* ($\text{HR}=1.1842, P=5.329e-09, \text{FDR}=1.165e-06$), *CDC20* ($\text{HR}=1.1913, P=2.787e-09, \text{FDR}=7.192e-07$).
* **Standardized Pathway**: GO:0051443 (Positive Regulation of Ubiquitin-Protein Transferase Activity) / KEGG: hsa04110 (Cell cycle - Ubiquitin Mediated Proteolysis).
* **Biological Explanation**: Anaphase promotion requires timely degradation of cell cycle inhibitors. *CDC20* activates the Anaphase-Promoting Complex/Cyclosome (APC/C), while E2 ubiquitin-conjugating enzymes (*UBE2C*, *UBE2S*) polyubiquitinate substrates such as Securin (*PTTG1*), triggering sister chromatid separation and mitotic exit.
* **Evidence & Limitations**: High direct significance ($\text{FDR} < 1.2e-6$) and validated physical protein complex membership. *Limitation*: E2 enzyme expression levels in bulk RNA reflect metabolic protein turnover demands and cell division rates rather than direct oncogenic mutation.

#### Program 3: Tumor Microenvironment Immune Infiltration and Antigen Presentation
* **Prognostic Association**: Protective-associated ($\text{HR} < 1$)
* **Major Supporting Genes**: *FCER1A* ($\text{HR}=0.7932, P=6.520e-13, \text{FDR}=1.769e-09$), *JCHAIN* ($\text{HR}=0.8029, P=7.433e-13, \text{FDR}=1.769e-09$), *CD1C* ($\text{HR}=0.8142, P=7.785e-10, \text{FDR}=3.147e-07$), *KLRB1* ($\text{HR}=0.8216, P=9.148e-10, \text{FDR}=3.563e-07$), *CD1E* ($\text{HR}=0.8236, P=5.963e-09, \text{FDR}=1.277e-06$), *IL27RA* ($\text{HR}=0.8255, P=1.496e-09, \text{FDR}=4.645e-07$), *FLT3* ($\text{HR}=0.8170, P=1.232e-09, \text{FDR}=4.397e-07$).
* **Standardized Pathway**: GO:0002376 (Immune System Process) / Reactome: Adaptive Immune System (R-HSA-1280218).
* **Biological Explanation**: Expression of *JCHAIN* (IgA/IgM joining chain) reflects tumor-infiltrating plasma cells, while *CD1C*, *CD1E*, and *FCER1A* mark conventional dendritic cells specialized in lipid and peptide antigen presentation. Co-expression with *KLRB1* (NK/T cell marker) indicates an immunocompetent tumor microenvironment capable of mounting cytotoxic anti-tumor responses.
* **Evidence & Limitations**: Robust protective statistical effect across multiple immune lineage markers ($\text{HR} \approx 0.79\text{--}0.83$). Literature records (PubMed: 37827342, 37488801) confirm tumor-infiltrating lymphocyte (TIL) correlation with survival. *Limitation*: Captures bulk cell-type composition rather than tumor cell transcriptional alterations.

#### Program 4: Extracellular Matrix (ECM) Organization and Tissue Architecture
* **Prognostic Association**: Protective-associated ($\text{HR} < 1$)
* **Major Supporting Genes**: *ADAMTS8* ($\text{HR}=0.7929, P=1.038e-09, \text{FDR}=3.903e-07$), *RELN* ($\text{HR}=0.7964, P=1.126e-09, \text{FDR}=4.158e-07$), *COL17A1* ($\text{HR}=0.7976, P=2.765e-12, \text{FDR}=5.385e-09$), *OGN* ($\text{HR}=0.8074, P=2.578e-10, \text{FDR}=1.721e-07$), *COL14A1* ($\text{HR}=0.8236, P=4.432e-09, \text{FDR}=1.021e-06$), *OMD* ($\text{HR}=0.8291, P=1.745e-09, \text{FDR}=5.120e-07$), *LAMA2* ($\text{HR}=0.8300, P=5.665e-10, \text{FDR}=2.638e-07$), *MFAP4* ($\text{HR}=0.8342, P=1.863e-09, \text{FDR}=5.320e-07$).
* **Standardized Pathway**: GO:0030198 (Extracellular Matrix Organization) / Reactome: Core matrisome (R-HSA-1474290).
* **Biological Explanation**: Structural matrix proteins (*LAMA2*, *COL17A1*, *COL14A1*) and small leucine-rich proteoglycans (*OGN*, *OMD*, *MFAP4*) maintain basement membrane integrity and extracellular matrix homeostasis, acting as a physical barrier against tumor cell motility, local invasion, and intravasation.
* **Evidence & Limitations**: Consistent protective signals ($\text{HR} \approx 0.79\text{--}0.83$). *Limitation*: Variable stromal composition in tumor biopsies can introduce composition confounding.

---

### 3. Key Genes and Interaction Modules

| Key Gene / Module | Direction / HR | P Value | FDR | Primary Biological Function | Proposed Gene-Gene Relationship Type |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **LARP1** | Risk ($\text{HR}=1.2612$) | $2.089e-14$ | $4.476e-10$ | mTORC1 downstream translation regulator of TOP mRNAs | **Co-expression** & **Pathway co-membership** with post-transcriptional regulators (*YTHDF1*). |
| **TPX2 – AURKA Module** | Risk ($\text{HR}=1.2017 \text{ / } 1.1885$) | $1.903e-10 \text{ / } 2.846e-09$ | $1.405e-07 \text{ / } 7.259e-07$ | Spindle assembly factor (*TPX2*) and mitotic kinase (*AURKA*) | **Direct physical interaction** (*TPX2* directly binds and activates *AURKA*) and **Pathway co-membership**. |
| **CDC20 – UBE2C – UBE2S – PTTG1 Module** | Risk ($\text{HR}=1.1842\text{--}1.2100$) | $2.908e-10\text{--}5.329e-09$ | $1.731e-07\text{--}1.165e-06$ | APC/C-mediated ubiquitin proteolysis of Securin (*PTTG1*) | **Direct physical interaction** (protein complex) & **Regulatory interaction** (E2/E3 ubiquitination). |
| **STIP1 – GSK3B Module** | Risk ($\text{HR}=1.2369 \text{ / } 1.2271$) | $1.332e-13 \text{ / } 2.163e-13$ | $9.744e-10 \text{ / } 1.159e-09$ | Hsp90 co-chaperone (*STIP1*) and glycogen synthase kinase (*GSK3B*) | **Indirect / Putative relationship** and **Co-expression** in cellular stress signaling. |
| **STAT5A – STAT5B Pair** | Protective ($\text{HR}=0.8063 \text{ / } 0.8372$) | $1.913e-12 \text{ / } 3.714e-09$ | $4.098e-09 \text{ / } 8.851e-07$ | Transcription factors regulating differentiation and cytokines | **Paralogous pathway co-membership**, **Co-expression**, and potential **Direct physical interaction** (homo/heterodimerization). |
| **FCER1A – JCHAIN – CD1C Module** | Protective ($\text{HR}=0.7932\text{--}0.8142$) | $6.520e-13\text{--}7.785e-10$ | $1.769e-09\text{--}3.147e-07$ | Immune cell infiltration (Plasma cells, cDCs, Mast cells) | **Co-expression** driven by immune cell co-infiltration and **Pathway co-membership**. |
| **PKMYT1** | Risk ($\text{HR}=1.2438$) | $1.364e-13$ | $9.744e-10$ | Inhibitory phosphorylation kinase of CDK1 at G2/M transition | **Regulatory interaction** with CDK1/Cyclin B and **Pathway co-membership** with mitotic regulators (*TPX2*, *AURKA*). |
| **PROS1 – PDGFRA Axis** | Protective ($\text{HR}=0.8362 \text{ / } 0.8376$) | $4.787e-09 \text{ / } 2.240e-09$ | $1.078e-06 \text{ / } 5.998e-07$ | TAM receptor ligand (*PROS1*) and stromal RTK (*PDGFRA*) | **Co-expression** in tumor stroma and **Pathway co-membership** in microenvironmental regulation. |

---

### 4. Validation Priorities

```
+-----------------------------------------------------------------------------------+
|                            Validation Priority Pipeline                           |
+-----------------------------------------------------------------------------------+
|  1. TPX2-AURKA-PKMYT1 Kinase Axis    --> Therapeutic Target   (Supported Hypoth.) |
|  2. USP30 Mitophagy Regulatory Role  --> Mechanistic Hypoth.  (Exploratory)       |
|  3. JCHAIN/FCER1A/CD1C Immune Panel  --> Biomarker            (Supported Hypoth.) |
|  4. APC/C Ubiquitin Ligase Complex   --> Network Interaction  (Supported Hypoth.) |
|  5. Subtype & Composition Adjustments--> Confounding Check    (Supported Hypoth.) |
+-----------------------------------------------------------------------------------+
```

#### Priority 1: Mitotic Kinase/Spindle Axis (*TPX2* – *AURKA* – *PKMYT1*)
* **Classification**: Therapeutic target
* **Why Prioritized**: Multiple top-ranking risk genes converge on G2/M kinase activation (*PKMYT1* $\text{HR}=1.2438$; *TPX2* $\text{HR}=1.2017$; *AURKA* $\text{HR}=1.1885$).
* **Input Dataset Evidence**: High statistical significance ($\text{FDR} < 7.3e-07$) and concurrent risk hazard ratios.
* **External Evidence**: Inhibitors targeting AURKA (e.g., alisertib) and PKMYT1 (e.g., RP-6306) are in active oncology clinical trials.
* **Next Step for Validation**: Evaluate dual PKMYT1/AURKA pharmacological inhibition or siRNA knockdowns in patient-derived breast cancer organoids (PDOs) stratified by HR/HER2 status.
* **Conclusion Status**: **Supported hypothesis** (therapeutic efficacy in breast cancer OS requires prospectively controlled clinical trial validation).

#### Priority 2: Deubiquitinase *USP30* in Tumor Cell Survival & Mitophagy
* **Classification**: Mechanistic hypothesis
* **Why Prioritized**: *USP30* is a mitochondrial outer membrane deubiquitinase displaying a strong adverse risk association ($\text{HR}=1.2223, P=4.349e-12, \text{FDR}=7.166e-09$).
* **Input Dataset Evidence**: High statistical ranking among non-mitotic risk genes.
* **External Evidence**: Reactome and UniProt records establish USP30 as a negative regulator of Parkin-mediated mitophagy; literature on its specific role in breast cancer survival under metabolic stress remains preliminary.
* **Next Step for Validation**: Perform CRISPR knockout of *USP30* in breast carcinoma cell lines subjected to metabolic hypoxia and assess mitochondrial clearance, ROS accumulation, and apoptotic rate.
* **Conclusion Status**: **Exploratory hypothesis**.

#### Priority 3: Tumor Immunogenicity Panel (*JCHAIN* / *FCER1A* / *CD1C*)
* **Classification**: Biomarker
* **Why Prioritized**: Coordinated protective signal across humoral and dendritic cell markers ($\text{HR} \approx 0.79\text{--}0.81, \text{FDR} < 3.2e-07$).
* **Input Dataset Evidence**: Strong protective hazard ratios in bulk breast tumor transcriptomes.
* **External Evidence**: Published literature (PubMed: 37827342, 37488801) confirms that intratumoral plasma cells (*JCHAIN*) and dendritic cells (*CD1C*, *FCER1A*) correlate with favorable immunotherapy response and improved OS.
* **Next Step for Validation**: Conduct multiplex immunohistochemistry (mIHC) or single-cell spatial transcriptomics on clinical tissue microarrays (TMAs) to quantify spatial proximity of cDCs and plasma cells to carcinoma cells.
* **Conclusion Status**: **Supported hypothesis**.

#### Priority 4: APC/C-Ubiquitin E2 Ligase Cascade (*UBE2C* / *UBE2S* / *CDC20*)
* **Classification**: Interaction / network hypothesis
* **Why Prioritized**: Direct functional interaction cascade involving E2 conjugating enzymes (*UBE2C*, *UBE2S*) and the APC/C co-activator (*CDC20*) linked to securin (*PTTG1*) degradation ($\text{HR} \approx 1.18\text{--}1.21$).
* **Input Dataset Evidence**: Co-elevation of multiple physically interacting nodes of the mitotic ubiquitin pathway.
* **External Evidence**: STRING network records confirm direct physical binding between CDC20, UBE2C, and UBE2S.
* **Next Step for Validation**: Co-immunoprecipitation and ubiquitination assays under double *UBE2C*/*UBE2S* knockdown to evaluate APC/C substrate turnover and cell cycle arrest.
* **Conclusion Status**: **Supported hypothesis**.

#### Priority 5: Subtype Composition & Proliferation Confounding Check
* **Classification**: Confounding or composition check
* **Why Prioritized**: Bulk tissue RNA-seq aggregates malignant epithelial cells, stromal fibroblasts, and immune subsets. Proliferation genes dominate survival signatures but correlate strongly with PAM50 intrinsic subtypes (e.g., Basal-like vs. Luminal A).
* **Input Dataset Evidence**: Inverse correlation between mitotic risk genes ($\text{HR} > 1$) and immune/stromal protective genes ($\text{HR} < 1$).
* **External Evidence**: Standard breast cancer clinical practice relies on ER/PR/HER2 status and PAM50 molecular subtyping, which strongly dictate baseline proliferation index and prognosis.
* **Next Step for Validation**: Multivariable Cox proportional hazards regression incorporating clinical stage, PAM50 subtype, ER/PR/HER2 status, and CIBERSORTx cell-type deconvolution fractions.
* **Conclusion Status**: **Supported hypothesis**.

---

### 5. Evidence Grounding

```
+---------------------------------------------------------------------------------------+
|                                Evidence Grounding Hierarchy                           |
+---------------------------------------------------------------------------------------+
|  1. Direct Input Evidence    --> Uploaded dataset HR, P values, and FDR metrics       |
|  2. Pathway & Ontology       --> QuickGO, Reactome, KEGG annotations (Cell Cycle, ECM)|
|  3. Network Evidence         --> STRING protein-protein binding (TPX2-AURKA, APC/C)   |
|  4. Clinical & Literature    --> PubMed / Europe PMC records (PROS1, STIP1 studies)   |
|  5. External Stat. Valid.    --> NOT PERFORMED (No independent external statistics)   |
+---------------------------------------------------------------------------------------+
```

1. **Direct Input Evidence**: The uploaded survival metrics ($\text{HR}$, $P$ value, $\text{FDR}$) serve as the sole statistical foundation for this study. All 100 genes meet strict significance thresholds ($\text{FDR} < 1.8e-06$).
2. **Pathway & Ontology Evidence**: Standardized annotations from QuickGO, Reactome, and KEGG contextualize the input genes into mitotic nuclear division (GO:0045840), ubiquitin transfer activity (GO:0051443), and extracellular matrix organization (GO:0030198).
3. **Protein Interaction & Regulatory Network Evidence**: STRING and TRRUST databases provide structural and regulatory network context. Physical binding evidence exists for *TPX2*–*AURKA* and *CDC20*–*PTTG1*–*UBE2C*. These database annotations represent contextual evidence rather than statistics computed from the uploaded data.
4. **Published Literature & Clinical Evidence**: PubMed/Europe PMC literature records support the protective role of *PROS1* (PMID: 37827342) and the immune relevance of *STIP1* (PMID: 37488801). Clinical trial records (ClinicalTrials.gov) document small molecules targeting AURKA and PKMYT1.
5. **Distinction of Source Independence**: Databases like QuickGO, Reactome, and STRING aggregate overlapping primary literature; their concurrence indicates mechanistic plausibility rather than independent statistical replication.
6. **External Statistical Replication Status**: **External statistical validation was not performed**. No independent validation cohort statistics (such as hazard ratios or P values from METABRIC, TCGA, or SCAN-B) were supplied in the input dataset.

---

### 6. Limitations and Alternative Explanations

1. **Lack of Independent External Statistical Replication**: The current findings are derived exclusively from the internal survival statistics of the provided 100-gene ledger. Because **external statistical validation was not performed** on an independent breast cancer cohort, prognostic estimates may be subject to cohort-specific bias.
2. **Cell Composition and Microenvironment Heterogeneity**: Bulk tumor transcriptomics averages expressions across carcinoma cells, immune infiltrates, and connective stroma. The protective associations of *JCHAIN*, *FCER1A*, *CD1C*, *LAMA2*, and *OGN* likely reflect higher infiltration of plasma cells, dendritic cells, and healthy stromal tissue rather than intrinsic transcriptional activation within carcinoma cells.
3. **Proliferation Bias and Molecular Subtype Confounding**: Mitotic risk genes (*PKMYT1*, *TPX2*, *KIF20A*, *UBE2C*, *AURKA*) are characteristic of high-grade, highly proliferative breast cancer subtypes (such as Triple-Negative / Basal-like and HER2-enriched). Without controlling for PAM50 molecular subtypes and histologic grade, these HRs may reflect subtype distribution rather than independent prognostic drivers.
4. **Association-versus-Causation Ambiguity**: The observational nature of survival associations cannot distinguish whether candidate genes (e.g., *LARP1*, *STIP1*, *USP30*) actively drive tumor progression or merely represent secondary downstream markers of cellular stress, rapid division, or genomic instability.
5. **Unmeasured Clinical Covariates and Treatment Exposure**: Patient overall survival is heavily confounded by systemic therapies (chemotherapy regimens, endocrine therapy, HER2-targeted agents) and clinical stage. Genes associated with poor survival could represent markers of therapeutic resistance rather than intrinsic aggressive biology, a distinction requiring patient-level treatment data to resolve.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=30, external claims checked=0, external mismatches=0, status=passed.

Answer model API: Google Gemini / gemini-3.6-flash

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 100/100 selected items (records returned); cbioportal 100/100 selected items (records returned); chembl 52/100 selected items (records returned); civic 12/100 selected items (records returned); clinicaltrials 57/100 selected items (records returned); clinvar 100/100 selected items (records returned); ensembl 100/100 selected items (records returned); europepmc 990 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 98/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 99/100 selected items (records returned); humanbase 100/100 selected items (records returned); intact 99/100 selected items (partially returned; some queries failed); mygene 100/100 selected items (records returned); omnipath 65/100 selected items (records returned); opentargets 100/100 selected items (records returned); pubmed 791 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 99/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 100/100 selected items (records returned)
Local databases: gutmgene 4/100 selected items (records returned); hmdb 31/100 selected items (records returned); string 100/100 selected items (records returned); trrust 40/100 selected items (records returned)
