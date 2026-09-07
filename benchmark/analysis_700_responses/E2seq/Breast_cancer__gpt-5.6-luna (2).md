# breast cancer - gpt-5.6-luna

- Benchmark system: E2seq + Agent RAG
- Repeat: 2
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
- Model API: OpenAI / gpt-5.6-luna
- Message SHA-256: 2eef237c25053f55d87c73e963368cae88b5c698447f11e7e98ebc594d62e5bb
- Response HTTP status: 200
- Prompt tokens: 46318
- Completion tokens: 18305
- Reasoning tokens: 0
- Total tokens: 64623
- API requests reported: 3
- Elapsed seconds: 193.883
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 685.605
- Question handoff seconds: 699.996
- Final benchmark system: E2seq; file rank 2/5; original repeat 2; model vendor: OpenAI

---
## 1. Overall biological interpretation

The result is a **prognostic survival signature in breast tumor tissue**, not a differential-expression analysis; therefore, the HRs indicate association with overall-survival hazard and do not establish that the genes are causally altered or therapeutically actionable.

Among 100 unique genes, **52 were risk-associated (HR > 1)** and **48 protective-associated (HR < 1)**. All 100 unique genes passed the supplied thresholds (**P ≤ 0.05 and FDR ≤ 0.05**), with FDR values ranging from **4.4762322e-10** to **1.7414147e-06**. The dominant risk-associated pattern is a coordinated **mitotic/cell-cycle program**, including **PKMYT1, RACGAP1, KIF20A, CDCA5, TPX2, UBE2C, CDC20, AURKA, NUSAP1, UBE2S, and PRC1**. This is biologically consistent with aggressive, highly proliferative tumor states.

The protective-associated genes form two additional broad patterns: an **immune or antigen-presenting-cell-associated program**, represented by **FCER1A, CD1C, CD1E, FLT3, KLRB1, STAT5A, STAT5B, IL27RA, and JCHAIN**, and a **stromal, extracellular-matrix, and differentiated tissue program**, represented by **OGN, COL14A1, MFAP4, LAMA2, ADAMTS8, COL17A1, PDGFRA, and IGF1**. These protective associations may reflect favorable tumor biology, immune infiltration, stromal composition, or combinations of these factors.

### Data-quality warning

The statistical pattern is technically suspicious and requires verification before biological conclusions are treated as robust. Specifically:

- All 100 unique genes are highly significant.
- The direction split is nearly balanced: 52 risk-associated and 48 protective-associated genes.
- The HRs are confined to a relatively narrow range, approximately **1.183–1.261** for risk-associated genes and **0.793–0.839** for protective-associated genes.
- The ledger reports **106 retained input rows, 100 unique genes, and 6 duplicated genes/probes**.
- No independent-cohort survival statistic is supplied.

This pattern could arise from a very large sample size, but it could also reflect model overfitting, feature preselection using the outcome, duplicated probes, unadjusted clinical confounding, or a technical transformation issue. The interpretation below is therefore an **exploratory biological interpretation of a statistically strong but not yet independently validated signature**. External statistical validation was not performed.

---

## 2. Core biological programs

### Program 1 — Mitotic proliferation, chromosome segregation, and cell-cycle progression

**Direction:** Risk-associated with worse OS.

**Major supporting genes:**  
**PKMYT1** HR=1.2437685, **RACGAP1** HR=1.223506, **KIF20A** HR=1.2180492, **CDCA5** HR=1.2179013, **TPX2** HR=1.2017253, **UBE2C** HR=1.2100353, **CDC20** HR=1.1912581, **AURKA** HR=1.1885146, **NUSAP1** HR=1.1942371, **UBE2S** HR=1.1841829, and **PRC1** HR=1.1859845.

**Relevant standardized pathways:**

- **KEGG: Cell cycle**
- **GO: Positive regulation of mitotic nuclear division (GO:0045840)**
- **Hallmark: G2M checkpoint**
- **Hallmark: E2F targets**
- **Reactome: Cell cycle-related processes**, where applicable

**Interpretation:**  
The concentration of risk-associated genes in mitotic kinase, spindle, cytokinesis, sister-chromatid, and ubiquitin-mediated cell-cycle functions is the clearest biological signal in the dataset. **PKMYT1** is associated with cell-cycle checkpoint control; **AURKA, TPX2, KIF20A, KIF4A, NUSAP1, PRC1, RACGAP1, and CKAP2L** relate to spindle organization, chromosome movement, or cytokinesis; and **CDC20, UBE2C, and UBE2S** are associated with anaphase-promoting-complex and ubiquitin-dependent cell-cycle transitions.

The retrieved pathway batch also reported **KEGG Cell cycle** and GO terms related to mitotic nuclear division and ubiquitin-ligase activity. These are **annotation-level contextual signals, not newly calculated enrichment statistics**.

**Evidence strength and limitations:**  
- **Direct dataset evidence:** strong internal convergence across many genes, all with FDR < 1.3e-6 in the supplied ledger.
- **Pathway evidence:** coherent GO/KEGG annotation and retrieved network associations.
- **Network evidence:** STRING-linked relationships involving **PLK1, TPX2, ANAPC2, BUB1B, and DLGAP5**.
- **Independent validation:** absent; external statistical validation was not performed.
- **Main limitation:** this may primarily be a proliferation index or tumor-grade signal rather than a specific mechanism unique to the identified genes.

---

### Program 2 — Translational capacity, proteostasis, and metabolic or cellular stress

**Direction:** Predominantly risk-associated.

**Major supporting genes:**  
**LARP1** HR=1.2611983, **STIP1** HR=1.2368966, **ATP2A2** HR=1.2378678, **GSK3B** HR=1.2271421, **USP30** HR=1.2222583, **CPT1A** HR=1.1962357, **YTHDF1** HR=1.1923944, **GPI** HR=1.1924932, **TRIB3** HR=1.1914433, and **HACD3** HR=1.1970276.

**Relevant standardized pathways, where applicable:**

- **GO: RNA binding**
- **GO: ATP binding**
- **GO: cellular response to stress**
- **Reactome: fatty-acid metabolism and mitochondrial processes**, where supported by gene-specific annotations
- **Hallmark: mTORC1 signaling, glycolysis, or unfolded-protein response** as hypotheses requiring formal testing

**Interpretation:**  
This group suggests that poor survival may be associated with tumor cells capable of sustaining protein synthesis, RNA utilization, energy production, and stress adaptation. **LARP1** and **YTHDF1** are plausible translational/post-transcriptional components; **STIP1** is associated with chaperone and proteostasis biology; **ATP2A2** relates to calcium handling; and **CPT1A, GPI, TRIB3, and HACD3** are compatible with metabolic flexibility or stress responses. **GSK3B** provides a possible signaling link to WNT and other intracellular regulatory systems, but its HR association alone does not establish pathway activation.

**Evidence strength and limitations:**  
- **Direct dataset evidence:** multiple risk-associated genes with highly significant HRs.
- **Ontology evidence:** retrieved annotations include ATP-binding and RNA-binding categories, but these are broad and not equivalent to formal enrichment.
- **Literature evidence:** the supplied literature includes a pan-cancer report linking **STIP1** to prognosis and immune infiltration (PMID **37488801**), but this is not independent statistical validation of the present breast-cancer cohort.
- **Main limitation:** this program is less specific and less tightly connected than the mitotic module; it may partly reflect general tumor proliferation, stress, or tissue composition.

---

### Program 3 — Immune-cell and antigen-presentation-associated biology

**Direction:** Protective-associated with better OS.

**Major supporting genes:**  
**FCER1A** HR=0.7932319, **CD1C** HR=0.81422548, **CD1E** HR=0.82361278, **FLT3** HR=0.81703284, **KLRB1** HR=0.82162453, **STAT5A** HR=0.80627148, **STAT5B** HR=0.83716163, **IL27RA** HR=0.82546531, and **JCHAIN** HR=0.80290118.

**Relevant standardized pathways:**

- **GO: antigen presentation and immune-cell differentiation**
- **GO: receptor signaling and cytokine-response processes**
- **Reactome: immune system**
- **Hallmark: inflammatory response** or **interferon-related programs**, subject to formal testing

**Interpretation:**  
The combination of **FCER1A, CD1C, and CD1E** is compatible with dendritic-cell and antigen-presenting-cell biology. **FLT3** is relevant to dendritic and myeloid-cell development, while **KLRB1** marks an immune-cell population and **STAT5A/STAT5B** are cytokine-responsive transcriptional regulators. **JCHAIN** may reflect antibody-secreting or immunoglobulin-associated cells. Taken together, this pattern is consistent with an immune-infiltrated tumor microenvironment associated with improved survival.

**Evidence strength and limitations:**  
- **Direct dataset evidence:** several immune-associated genes are protective, with HRs approximately 0.79–0.84.
- **Tissue/expression evidence:** external expression and tissue annotations support immune-cell relevance.
- **Pathway evidence:** immune and antigen-presentation annotations are biologically concordant.
- **Main limitation:** the most important alternative explanation is **cellular composition**. The results do not show whether tumor-cell expression, immune-cell abundance, or both drive the associations. Immune infiltration should not be inferred as causally protective from these data alone.

---

### Program 4 — Extracellular matrix, stromal organization, and tissue differentiation

**Direction:** Predominantly protective-associated.

**Major supporting genes:**  
**OGN** HR=0.80743973, **COL14A1** HR=0.82355765, **MFAP4** HR=0.83417958, **LAMA2** HR=0.83003966, **ADAMTS8** HR=0.7928718, **COL17A1** HR=0.79759519, **PDGFRA** HR=0.83760447, **IGF1** HR=0.80347674, **RELN** HR=0.79635886, and **RBP7** HR=0.83174472.

**Relevant standardized pathways:**

- **Reactome: extracellular matrix organization**
- **GO: extracellular region**
- **GO: cell adhesion and tissue development**
- **Hallmark: epithelial–mesenchymal transition**, only as a possible framework rather than a demonstrated enrichment result

**Interpretation:**  
The coordinated protective associations of matrix and stromal genes suggest that a more differentiated or particular stromal context is associated with favorable OS in this cohort. **OGN, COL14A1, MFAP4, LAMA2, and ADAMTS8** are extracellular or matrix-associated; **PDGFRA, IGF1, and RBP7** may reflect fibroblast, adipose, vascular, or stromal compartments. **COL17A1, CLDN11, TP63, and IGF1** also support a tissue-differentiation interpretation, although **GRHL2** is risk-associated in the supplied results, illustrating that this is not a uniformly defined differentiation axis.

**Evidence strength and limitations:**  
- **Direct dataset evidence:** multiple protective-associated extracellular and stromal genes.
- **Ontology evidence:** retrieved annotations include an extracellular-region category.
- **Tissue evidence:** gene functions are compatible with stromal and epithelial compartments.
- **Main limitation:** this program is particularly vulnerable to tumor purity, stromal abundance, and sampling differences. It should not be interpreted as evidence that increasing matrix expression would improve survival.

---

### Program 5 — Cytoskeletal remodeling, membrane signaling, and invasive-cell behavior

**Direction:** Predominantly risk-associated.

**Major supporting genes:**  
**EZR** HR=1.2269146, **RALGAPB** HR=1.2067852, **GPRC5A** HR=1.2018529, **ADGRG1** HR=1.2045524, **WNT7B** HR=1.1834371, **S100P** HR=1.1956391, **CFL1** HR=1.1908915, **TBC1D31** HR=1.1954831, and **GPRC5A**.

**Relevant standardized pathways:**

- **GO: plasma membrane**
- **GO: actin cytoskeleton organization**
- **Reactome: cell–cell communication and Rho-family signaling**, where supported
- **Hallmark: epithelial–mesenchymal transition**, as a hypothesis requiring formal analysis

**Interpretation:**  
The pattern is compatible with altered cell adhesion, membrane signaling, actin dynamics, and motility. **EZR** links membrane proteins to the actin cytoskeleton; **CFL1** is involved in actin remodeling; **RALGAPB** relates to small-GTPase regulation; and **ADGRG1, GPRC5A, WNT7B, and S100P** may represent signaling or epithelial-state features. Their coordinated risk association could indicate an invasive or adaptable tumor phenotype, but the dataset does not demonstrate invasion, metastasis, or pathway activation directly.

**Evidence strength and limitations:**  
- **Direct dataset evidence:** several risk-associated membrane/cytoskeletal genes.
- **Pathway evidence:** retrieved plasma-membrane annotations and gene-specific interaction records.
- **Literature evidence:** a supplied study identifies **GPRC5A** as a candidate cancer biomarker in gastric cancer (PMID **40865843**), which supports general plausibility but not breast-cancer OS replication.
- **Main limitation:** this program may overlap substantially with epithelial subtype, tumor purity, and proliferation.

---

## 3. Key genes and interaction modules

The following candidates are prioritized by program-level coherence rather than by HR magnitude alone.

| Candidate | Current statistical association | Biological interpretation and relationship type |
|---|---|---|
| **Mitotic module: PKMYT1–AURKA–TPX2–KIF20A–PRC1–CDC20/UBE2C/UBE2S** | Risk-associated; representative HRs: PKMYT1 **1.2437685**, TPX2 **1.2017253**, CDC20 **1.1912581**, UBE2C **1.2100353** | Core cell-cycle and chromosome-segregation module. The relationships are primarily **pathway co-membership and functional network association**. Retrieved STRING links include PLK1, TPX2, ANAPC2, BUB1B, and DLGAP5; STRING evidence should not automatically be interpreted as direct physical binding. |
| **LARP1** | Risk-associated, HR **1.2611983**, P **2.0894516e-14**, FDR **4.4762322e-10** | Candidate marker of translational or growth-associated tumor biology. Its relationship to the mitotic module is **indirect/putative**, through shared proliferative state rather than a demonstrated direct interaction in the supplied evidence. |
| **STIP1** | Risk-associated, HR **1.2368966**, FDR **9.7437879e-10** | Proteostasis and chaperone-associated candidate. The supplied literature reports an association with prognosis and immune infiltration in pan-cancer analysis (PMID **37488801**). This is **literature association**, not causal evidence or external replication. |
| **GSK3B–WNT7B signaling context** | GSK3B HR **1.2271421**; WNT7B HR **1.1834371**; both risk-associated | Potential WNT-related signaling context. Retrieved STRING records show GSK3B associations with CTNNB1, APC, AXIN1/2, DVL1, and related proteins. These are **database-supported interaction associations**, with relationship type potentially mixed; they do not prove that WNT signaling is activated in these tumors. |
| **Immune/APC module: FCER1A–CD1C–CD1E–FLT3** | Protective-associated; FCER1A HR **0.7932319**, CD1C HR **0.81422548**, CD1E HR **0.82361278**, FLT3 HR **0.81703284** | Coherent antigen-presenting and myeloid-cell signature. Relationships are **cell-type co-expression and pathway co-membership**, not necessarily direct gene-gene interactions. |
| **STAT5A–STAT5B–IL27RA module** | Protective-associated; STAT5A HR **0.80627148**, STAT5B HR **0.83716163**, IL27RA HR **0.82546531** | Cytokine-response and immune-state context. The retrieved network includes STAT3-related links involving FLT3, LEPR, STAT5A, and STAT5B. This is a **regulatory/signaling-network association**, not proof of direct STAT5A–STAT5B binding or transcriptional causality. |
| **Stromal ECM module: OGN–COL14A1–MFAP4–LAMA2–ADAMTS8** | Protective-associated; OGN HR **0.80743973**, COL14A1 HR **0.82355765**, ADAMTS8 HR **0.7928718** | Extracellular-matrix and stromal-context program. The relationship is **pathway co-membership and likely shared tissue-compartment expression**; direct physical interactions are not established by the supplied records. |
| **EZR–CFL1–RALGAPB cytoskeletal module** | Risk-associated; EZR HR **1.2269146**, CFL1 HR **1.1908915**, RALGAPB HR **1.2067852** | Candidate membrane–actin remodeling axis. Relationships are **functional or indirect signaling relationships** unless specific biochemical interaction data are independently demonstrated. |
| **CPT1A–GPI–TRIB3 metabolic-stress module** | Risk-associated; CPT1A HR **1.1962357**, GPI HR **1.1924932**, TRIB3 HR **1.1914433** | Candidate metabolic flexibility/stress-adaptation program. The relationships are **metabolic pathway co-membership**, not direct physical interaction. |
| **PROS1** | Protective-associated, HR **0.83621827**, FDR **1.0775537e-06** | Candidate immune–vascular or tumor-microenvironment biomarker. A breast-cancer bioinformatics study with experimental verification describes PROS1 as a prognostic biomarker associated with immune infiltration (PMID **37827342**). This is supportive contextual literature, not independent validation of the present HR. |

---

## 4. Validation priorities

### 1. Validate the proliferation signature as an independent OS biomarker  
**Classification:** Biomarker

**Why prioritize:** The mitotic program is the most internally coherent risk-associated signal and includes many genes across spindle, cytokinesis, checkpoint, and ubiquitin-mediated cell-cycle processes.

**Current evidence:** Multiple genes show risk-associated HRs, including PKMYT1 **1.2437685**, RACGAP1 **1.223506**, CDCA5 **1.2179013**, UBE2C **1.2100353**, CDC20 **1.1912581**, and AURKA **1.1885146**.

**External evidence:** GO/KEGG and STRING annotations support cell-cycle relationships. However, **external statistical validation was not performed**.

**Next step:** Test a prespecified proliferation score in an independent breast-cancer cohort using multivariable Cox regression adjusted for stage, grade, molecular subtype, treatment, age, and tumor purity. Confirm calibration, proportional-hazards assumptions, and performance beyond established proliferation measures such as Ki-67 or standard cell-cycle signatures.

**Conclusion level:** **Supported hypothesis**, not established clinical evidence.

---

### 2. Determine whether protective immune genes represent immune infiltration or tumor-cell biology  
**Classification:** Confounding or composition check

**Why prioritize:** The protective APC/immune pattern could be biologically meaningful, but it is highly susceptible to variation in immune-cell abundance.

**Current evidence:** Protective associations of FCER1A, CD1C, CD1E, FLT3, KLRB1, STAT5A, STAT5B, and IL27RA.

**External evidence:** Gene annotations and tissue-expression records support immune-cell relevance. The evidence is partly overlapping because many databases derive annotations from related expression and literature sources.

**Next step:** Apply tumor-purity and deconvolution analyses, then confirm cell localization using single-cell RNA-seq, spatial transcriptomics, multiplex immunohistochemistry, or flow cytometry. Refit survival models after adjustment for immune-cell fractions.

**Conclusion level:** **Supported hypothesis** for an immune-composition association; **insufficient evidence** for a causal protective immune mechanism.

---

### 3. Test whether the ECM/stromal program reflects favorable tumor biology or sampling composition  
**Classification:** Confounding or composition check

**Why prioritize:** OGN, COL14A1, MFAP4, LAMA2, ADAMTS8, and COL17A1 are collectively protective-associated but may originate from stromal, vascular, or differentiated epithelial compartments.

**Current evidence:** Several genes have HRs below 1, including ADAMTS8 **0.7928718**, COL17A1 **0.79759519**, OGN **0.80743973**, and COL14A1 **0.82355765**.

**External evidence:** Extracellular-region and matrix annotations support biological plausibility, but no independent survival statistic is provided.

**Next step:** Relate the signature to histologic stromal content, tumor purity, collagen imaging, fibroblast subtypes, and spatial localization. Perform cell-type-specific survival analyses rather than interpreting bulk expression as tumor-cell expression.

**Conclusion level:** **Exploratory hypothesis** until compartment-specific validation is completed.

---

### 4. Evaluate a metabolic/proteostasis stress axis involving LARP1, STIP1, CPT1A, and TRIB3  
**Classification:** Mechanistic hypothesis

**Why prioritize:** These risk-associated genes could represent tumor adaptation to high biosynthetic demand, altered lipid oxidation, protein-folding stress, or nutrient limitation.

**Current evidence:** LARP1 HR **1.2611983**, STIP1 HR **1.2368966**, CPT1A HR **1.1962357**, and TRIB3 HR **1.1914433**.

**External evidence:** The supplied literature supports STIP1 as a pan-cancer prognostic and immune-associated candidate (PMID **37488801**), but this is not breast-cancer cohort replication. Gene annotations support translational, metabolic, and stress-related plausibility.

**Next step:** Measure pathway activity rather than transcript abundance alone, including protein levels, phosphoproteomics, oxygen and nutrient dependence, lipid oxidation, unfolded-protein-response markers, and functional perturbation of individual genes or combinations.

**Conclusion level:** **Exploratory hypothesis**.

---

### 5. Test whether the mitotic network is functionally coupled to cytoskeletal and WNT-associated signaling  
**Classification:** Interaction / network hypothesis

**Why prioritize:** Risk-associated genes include both mitotic regulators and membrane/cytoskeletal genes such as EZR, CFL1, RALGAPB, ADGRG1, and WNT7B, suggesting a possible link between proliferation and invasive-cell behavior.

**Current evidence:** Mitotic genes and cytoskeletal/membrane genes are independently risk-associated. Retrieved STRING records connect selected genes through network neighborhoods involving PLK1, TPX2, DLGAP5, and GSK3B-related WNT components.

**External evidence:** These are **network or pathway associations**, not evidence of direct physical interactions among all genes. No independent functional or survival statistic is supplied.

**Next step:** Use perturbation experiments, live-cell imaging, proximity-based assays where appropriate, phosphoproteomics, and invasion/migration assays to test whether disrupting the mitotic module changes cytoskeletal behavior or vice versa.

**Conclusion level:** **Exploratory hypothesis**.

---

## 5. Major limitations and alternative explanations

1. **Potential statistical or preprocessing artifact**  
   The universal significance, narrow HR distributions, and six duplicated rows warrant reanalysis. Verify probe-to-gene mapping, expression scaling, event counts, censoring, variance filtering, missing-data handling, and whether outcome information was used during feature selection.

2. **Outcome-driven selection and overfitting**  
   If the 100 genes were selected in the same cohort used for survival testing, the reported P values and FDRs may be optimistic. Use nested cross-validation, bootstrap optimism correction, and a completely independent cohort.

3. **Tumor purity and cell composition**  
   Immune and ECM signals may reflect differing proportions of immune, fibroblast, vascular, epithelial, or malignant cells. Investigate using purity estimates, pathological review, single-cell or spatial data, and adjusted survival models.

4. **Clinical and treatment confounding**  
   OS is influenced by stage, grade, age, molecular subtype, metastatic burden, treatment exposure, and socioeconomic or follow-up factors. The supplied table does not include adjusted HRs or covariates, so the genes may partly act as proxies for disease severity or treatment selection.

5. **Association versus causation and broad pathway interpretation**  
   Pathway recurrence, STRING edges, tissue records, drug records, and literature associations explain plausibility but do not constitute replication or causal evidence. The retrieved pathway batch was not recomputed during synthesis, and no formal enrichment statistics beyond the supplied annotations are available.

Overall, the most defensible interpretation is that the signature captures a **high-proliferation, aggressive tumor state**, accompanied by protective associations reflecting **immune and stromal tissue context**, with additional candidate contributions from **proteostasis, metabolism, and cytoskeletal signaling**. These findings are biologically plausible and internally coherent, but they remain **supported hypotheses pending technical reanalysis and independent, covariate-adjusted survival validation**.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=48, external claims checked=0, external mismatches=0, status=passed.

Answer model API: OpenAI / gpt-5.6-luna

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 100/100 selected items (records returned); cbioportal 100/100 selected items (records returned); chembl 52/100 selected items (records returned); civic 12/100 selected items (records returned); clinicaltrials 57/100 selected items (records returned); clinvar 100/100 selected items (records returned); ensembl 100/100 selected items (records returned); europepmc 990 articles / initial full-cohort RAG 100 queries + 4 current-round queries; some queries failed; gtex 98/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 99/100 selected items (records returned); humanbase 100/100 selected items (records returned); intact 99/100 selected items (partially returned; some queries failed); mygene 100/100 selected items (records returned); omnipath 65/100 selected items (records returned); opentargets 100/100 selected items (records returned); pubmed 791 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 99/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 100/100 selected items (records returned)
Local databases: gutmgene 4/100 selected items (records returned); hmdb 31/100 selected items (records returned); string 100/100 selected items (records returned); trrust 40/100 selected items (records returned)
