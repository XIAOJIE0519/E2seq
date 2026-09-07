# idiopathic pulmonary fibrosis (IPF) - deepseek-v4-flash

- Benchmark system: E2seq + Agent RAG
- Repeat: 4
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
- Model API: DeepSeek / deepseek-v4-flash
- Message SHA-256: d9fe74e971569d03f1ace047ce334e08d788b93d2057913b4d42b34da6d57d2f
- Response HTTP status: 200
- Prompt tokens: 24138
- Completion tokens: 10935
- Reasoning tokens: 0
- Total tokens: 35073
- API requests reported: 2
- Elapsed seconds: 170.055
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 1387.824
- Question handoff seconds: 1401.194
- Final benchmark system: E2seq; file rank 3/5; original repeat 4; model vendor: DeepSeek

---
## 1. Overall biological interpretation

The uploaded table is a **prognostic (survival) analysis** in IPF lung tissue with all-cause mortality as the endpoint. The statistical ledger shows 100 selected unique genes, of which 93 are risk-associated (HR > 1) and 7 are protective-associated (HR < 1). All 100 genes pass FDR ≤ 0.01, indicating a highly significant, genome-wide-scale survival association at the univariate level.

The overall biology is dominated by an **innate immune / inflammatory program** that is strongly associated with worse survival. The top HR genes include chemokines (CCL7, CXCL1, CXCL14), S100 alarmins (S100A12, S100A14), neutrophil-related markers (CXCR1, CD177, MMP25, SELL), and the profibrotic matricellular protein SPP1 (osteopontin). A second major theme is **epithelial remodeling and aberrant repair**, represented by mucins (MUC1, MUC21), keratins (KRT17, KRT23), surfactant components (SFTPB, SFTA2), and growth factor signaling (HGF, MET, NRG1). A third theme involves **matrix remodeling and protease activity** (HTRA1, MMP25, PRSS23, F5, EFEMP1, DYSF), and a fourth involves **metabolic reprogramming** (SLC7A11, SLC39A8, ACOX2, STEAP4, ALDH1A3, SLC6A8).

The protective-associated genes are few (7/100) and include several with extreme HR values (MIR221, IHH, FAM75A2, OR2M2, DYDC2, XLOC_003303) that are biologically implausible as isolated survival predictors (HR ≈ 1.9×10⁻²²). These likely reflect technical artifacts (near-zero expression, probe issues, or model instability) rather than genuine protective biology; LOC100128226 (HR = 0.007) is the only protective gene with a plausible effect size.

**Data quality warning:** Several genes have extreme HR values (1.9×10⁻²², 5.2×10²¹) with P = 0 exactly, which is statistically degenerate. These likely arise from zero-inflated expression, near-complete separation in the survival model, or probe/annotation artifacts (including CONTROL_A_33 probes and unnamed lincRNA entries). These rows should be interpreted with caution and are not suitable for biological claims about individual genes.

## 2. Core biological programs

### Program 1: Innate immune activation, neutrophil recruitment, and alarmin signaling
- **Direction:** Risk-associated (worse survival)
- **Supporting genes:** CXCL1 (HR=2.99), CCL7 (HR=3.02), CXCL14 (HR=2.38), CXCR1 (HR=3.28), S100A12 (HR=2.53), S100A14 (HR=2.57), CD177 (HR=2.72), MMP25 (HR=3.26), SELL (HR=2.37), SPP1 (HR=3.40)
- **Pathway:** GO: Neutrophil Migration (GO:1990266); KEGG: Chemokine signaling pathway
- **Explanation:** The coordinated upregulation of neutrophil chemoattractants (CXCL1, CXCL14), a neutrophil receptor (CXCR1), neutrophil granule protease (MMP25), neutrophil surface markers (CD177), and S100 calcium-binding alarmins (S100A12, S100A14) indicates an active neutrophilic inflammatory infiltrate. S100A12 binds RAGE (AGER) and TLR4 (STRING confidence 0.999 and 0.970, respectively), amplifying inflammatory signaling. SPP1, a matricellular protein, bridges innate immunity and fibrosis.
- **Evidence strength:** Strong — multiple independent genes with FDR < 4×10⁻⁵, coherent pathway, and consistent with known IPF immunopathology. **Limitations:** The KEGG chemokine pathway annotation is a pathway co-membership, not an enrichment statistic; no formal GSEA was run on this cohort. The neutrophil signal may partly reflect blood contamination or cell-composition differences in lung tissue.

### Program 2: Epithelial injury response and aberrant epithelial repair
- **Direction:** Risk-associated
- **Supporting genes:** MUC1 (HR=2.32), MUC21 (HR=2.10), KRT17 (HR=2.19), KRT23 (HR=2.59), SFTPB (HR=2.66), SFTA2 (HR=2.25), PKP3 (HR=2.50), MAL2 (HR=2.44), SPRR1A (HR=2.28), AGR3 (HR=2.40), IRX2 (HR=2.22)
- **Pathway:** GO: antimicrobial humoral immune response (GO:0061844) for surfactant/mucin components; epithelial cell signaling (KEGG: Epithelial cell signaling in Helicobacter pylori infection) for mucin/keratin dysregulation — both are imperfect matches; no single canonical pathway captures this program well.
- **Explanation:** Mucins (MUC1, MUC21), keratins (KRT17, KRT23), cornified envelope protein (SPRR1A), tight junction component (PKP3), and surfactant proteins (SFTPB, SFTA2) together indicate abnormal epithelial differentiation and metaplasia. In IPF, alveolar type II cell injury leads to aberrant epithelial regeneration with bronchiolization and squamous metaplasia, which this gene set recapitulates.
- **Evidence strength:** Moderate-strong — multiple genes, consistent with IPF histopathology. **Limitations:** These genes are not specific to IPF; similar epithelial programs appear in other fibrotic and neoplastic lung diseases. KRT23's literature support is mainly from MAFLD (PMID 40487984), not IPF.

### Program 3: Growth factor signaling and profibrotic crosstalk (HGF/MET, NRG1/EGFR, BMP)
- **Direction:** Risk-associated
- **Supporting genes:** HGF (HR=2.93), MET (HR=2.53), NRG1 (HR=2.76), BMP6 (HR=3.04), SPRY2 (HR=3.26), EFEMP1 (HR=2.33), STAB1 (HR=3.29)
- **Pathway:** STRING network evidence places HGF, MET, NRG1, MUC1, EFEMP1 in an EGFR-centered module (6 selected genes); SPRY2 is a negative regulator of receptor tyrosine kinase (RTK) signaling that also interacts with CBL (STRING), which regulates MET.
- **Explanation:** HGF/MET signaling is classically associated with epithelial proliferation and repair; its upregulation in IPF lung tissue likely reflects compensatory epithelial regeneration attempts. NRG1 signals through EGFR/ERBB receptors and is implicated in epithelial-mesenchymal plasticity. SPRY2, a feedback inhibitor of RTK signaling, may be induced as a compensatory response. BMP6 (a TGF-β superfamily member) connects to the fibrotic program.
- **Evidence strength:** Moderate — STRING shows pathway co-membership (EGFR module) but not direct physical interaction among all members. The direction is counterintuitive for HGF (usually protective in fibrosis models), so the risk association may reflect disease severity rather than causation. **Limitations:** HGF/MET signaling can be either protective or pathogenic depending on cellular context; bulk tissue cannot resolve this.

### Program 4: Matrix remodeling, protease activity, and fibrosis progression
- **Direction:** Risk-associated
- **Supporting genes:** HTRA1 (HR=4.30), MMP25 (HR=3.26), PRSS23 (HR=2.25), F5 (HR=2.55), DYSF (HR=3.47), EFEMP1 (HR=2.33), FBLIM1 (HR=2.59), CHST15 (HR=2.99), HS3ST1 (HR=3.24), TPST1 (HR=2.92)
- **Pathway:** GO: extracellular region (CC) and extracellular matrix organization (Reactome); no single KEGG pathway cleanly covers this set.
- **Explanation:** HTRA1 (serine protease, HR=4.30, the highest plausible HR in the cohort) degrades extracellular matrix components and regulates TGF-β bioavailability. MMP25 is a neutrophil-derived matrix metalloprotease. PRSS23 is a serine protease induced by TGF-β. CHST15 and HS3ST1 are sulfotransferases that modify glycosaminoglycans, altering growth factor sequestration. DYSF is involved in membrane repair. Together these genes indicate active ECM turnover and remodeling.
- **Evidence strength:** Moderate — multiple genes, coherent function. **Limitations:** Protease expression may reflect inflammatory cell infiltration (MMP25 is neutrophil-specific) rather than fibroblast-driven remodeling per se. The direction is consistent with progressive fibrosis but cannot distinguish cause from consequence.

### Program 5: Metabolic reprogramming and oxidative stress response
- **Direction:** Risk-associated
- **Supporting genes:** SLC7A11 (HR=3.52), SLC39A8 (HR=3.22), SLC6A8 (HR=3.21), ACOX2 (HR=3.18), STEAP4 (HR=3.03), ALDH1A3 (HR=2.27), SOD3 (HR=2.37), SLC34A2 (HR=2.27)
- **Pathway:** GO: molecular_function (metal ion binding, oxidoreductase activity); no single dominant pathway.
- **Explanation:** SLC7A11 (cystine/glutamate antiporter, xCT) is a key mediator of ferroptosis resistance and is induced by oxidative stress. SLC39A8 (zinc transporter) and STEAP4 (metalloreductase) link metal homeostasis to inflammation. ACOX2 (peroxisomal β-oxidation) and ALDH1A3 (aldehyde dehydrogenase) indicate altered lipid and aldehyde metabolism. SOD3 (extracellular superoxide dismutase) is typically protective against oxidative damage, so its risk association is counterintuitive and may reflect compensatory upregulation.
- **Evidence strength:** Moderate — multiple genes but functionally heterogeneous. **Limitations:** This program is the least coherent of the five; the genes span transporters, oxidoreductases, and peroxisomal enzymes without a single unifying pathway. The SLC7A11 association with ferroptosis is a supported hypothesis, not established in this cohort.

**Programs deliberately not included:** (1) A "protective program" was not elevated to a major finding because only 7 genes are protective, several with degenerate HR values; (2) a "chemokine-only" program was merged into Program 1 to avoid redundancy.

## 3. Key genes and interaction modules

### 1. SPP1 (osteopontin) — HR=3.40, FDR=3.99×10⁻⁵
- **Role:** Bridges innate immunity (macrophage/neutrophil recruitment) and fibrosis (matricellular signaling).
- **Interactions:** STRING places SPP1 in a module with CD44 (along with SELL, SLC7A11) and with FN1 (with CEACAM6, HGF). CD44-SPP1 is a **direct physical interaction** with strong literature support; FN1-SPP1 is a **pathway co-membership** (ECM organization).
- **Evidence:** Direct (statistical), disease-association (SPP1 is a well-established IPF biomarker), pathway co-membership. **No independent-cohort statistic was supplied.**

### 2. HTRA1 — HR=4.30, FDR=2.57×10⁻⁶ (highest plausible HR)
- **Role:** Serine protease regulating TGF-β bioavailability and ECM degradation.
- **Interactions:** No strong STRING module identified in this cohort; function is inferred from literature.
- **Evidence:** Direct (statistical), literature (TGF-β regulation). **Interaction evidence: insufficient.**

### 3. MERTK — HR=3.70, FDR=1.05×10⁻⁵
- **Role:** Efferocytosis receptor on macrophages; mediates clearance of apoptotic cells; implicated in fibrosis resolution.
- **Interactions:** No STRING module in this cohort. Its risk association is notable because MERTK is usually considered pro-resolution; the direction may reflect macrophage accumulation.
- **Evidence:** Direct (statistical), disease-association (literature). **Mechanistic direction uncertain.**

### 4. S100A12 / S100A14 module — HR=2.53 / HR=2.57
- **Role:** S100 alarmins signal through RAGE (AGER) and TLR4.
- **Interactions:** STRING shows S100A12 interacts with AGER (confidence=0.999), TLR4 (0.970), S100A8 (0.995), S100A9 (0.940) — **direct physical interactions** by STRING prediction. S100A12-S100A14 relationship is **pathway co-membership** (S100 family, alarmin activity).
- **Evidence:** Direct (statistical), protein-interaction (STRING), disease-association. Note: STRING interactions are predicted/curated, not necessarily experimentally verified physical binding.

### 5. CXCL1 / CXCR1 / CCL7 chemokine module — HR=2.99 / 3.28 / 3.02
- **Role:** Neutrophil and monocyte recruitment.
- **Interactions:** STRING shows CXCL1, CXCL14, CXCR1 in a module with CXCL5; CCL7, CXCL1, CXCR1 in a module with CXCL6. CXCL1-CXCR1 is a **direct ligand-receptor physical interaction** (well-established). CCL7-CXCR1 is a **ligand-receptor interaction** (CCL7 binds CXCR1 with lower affinity than its canonical CCR receptors). CXCL1-CCL7 is **pathway co-membership** (chemokine signaling).
- **Evidence:** Direct (statistical), protein-interaction, pathway co-membership.

### 6. HGF / MET / SPRY2 module — HR=2.93 / 2.53 / 3.26
- **Role:** RTK signaling; HGF-MET is a canonical ligand-receptor pair; SPRY2 is a feedback inhibitor.
- **Interactions:** HGF-MET is a **direct physical interaction** (ligand-receptor). SPRY2-CBL interaction (STRING) is a **regulatory interaction** (CBL-mediated ubiquitination). SPRY2's regulation of MET signaling is a **regulatory interaction** via RTK pathway feedback.
- **Evidence:** Direct (statistical), protein-interaction (STRING), literature. **The risk direction is counterintuitive and requires validation.**

### 7. Mucin/epithelial module: MUC1, MUC21, KRT17, KRT23, PKP3
- **Role:** Epithelial metaplasia and aberrant differentiation.
- **Interactions:** MUC1-PKP3 relationship is **pathway co-membership** (epithelial apical junction); no direct physical interaction evidence in this cohort. KRT17-KRT23 are **co-expressed keratins** (same protein family, likely co-regulated).
- **Evidence:** Direct (statistical), expression/tissue (HPA), disease-association (IPF epithelial remodeling).

### 8. SLC7A11 (xCT) — HR=3.52, FDR=1.09×10⁻⁵
- **Role:** Cystine/glutamate antiporter; ferroptosis regulator; oxidative stress response.
- **Interactions:** STRING places SLC7A11 in a CD44 module (with SPP1, SELL). CD44-SLC7A11 is a **regulatory interaction** (CD44 stabilizes xCT). SLC7A11-SPP1 is **pathway co-membership** (oxidative stress response).
- **Evidence:** Direct (statistical), protein-interaction (STRING), literature (ferroptosis in fibrosis).

### 9. MMP25 / CD177 / CXCR1 neutrophil module — HR=3.26 / 2.72 / 3.28
- **Role:** Neutrophil infiltration and degranulation.
- **Interactions:** MMP25-CD177 are **co-expressed neutrophil granule proteins** (co-expression, not direct physical interaction). CXCR1-CD177 relationship is **pathway co-membership** (neutrophil degranulation).
- **Evidence:** Direct (statistical), expression/tissue (neutrophil-specific). **This module likely reflects neutrophil content, not a causal survival driver.**

### 10. MIR221 / IHH / FAM75A2 / OR2M2 / DYDC2 (protective group) — HR≈1.9×10⁻²²
- **Role:** Unclear; likely technical artifacts.
- **Interactions:** No meaningful interactions.
- **Evidence:** Direct (statistical) but statistically degenerate (P=0, HR at machine precision limits). **These should not be interpreted as genuine protective genes without further validation.**

## 4. Validation priorities

### Priority 1: Cell-composition deconvolution and neutrophil content adjustment
- **Classification:** Confounding or composition check
- **Why:** The neutrophil program (CXCR1, CD177, MMP25, S100A12) may reflect blood contamination or neutrophil infiltration rather than a causal IPF-specific signal. Lung tissue in IPF has variable inflammatory infiltrate.
- **Dataset evidence:** Multiple neutrophil-specific genes with high HRs; the STRING network shows a coherent neutrophil module.
- **External evidence:** Neutrophilia is documented in IPF BAL and tissue; however, blood contamination is a known confounder in bulk lung transcriptomics.
- **Next step:** Run CIBERSORTx or similar deconvolution on the bulk data; adjust survival models for estimated neutrophil fraction; validate in single-cell RNA-seq IPF datasets.
- **Conclusion status:** Supported hypothesis (cell composition is a likely confounder).

### Priority 2: Independent-cohort validation of the SPP1 and HTRA1 survival association
- **Classification:** Biomarker
- **Why:** SPP1 is a well-established IPF biomarker; HTRA1 has the highest plausible HR in the cohort. Both are biologically plausible and measurable in plasma or tissue.
- **Dataset evidence:** SPP1 HR=3.40, HTRA1 HR=4.30, both FDR<4×10⁻⁵ in this cohort.
- **External evidence:** SPP1 is validated in IPF BAL and serum in multiple studies; HTRA1 is less studied in IPF prognosis. **External statistical validation was not performed** — no independent-cohort statistic is supplied.
- **Next step:** Test SPP1 and HTRA1 protein levels (ELISA/IHC) in an independent IPF cohort with survival follow-up; build a multivariable Cox model adjusted for age, sex, FVC, DLCO, and GAP stage.
- **Conclusion status:** Supported hypothesis (SPP1), exploratory hypothesis (HTRA1).

### Priority 3: Functional dissection of the HGF/MET/SPRY2 axis
- **Classification:** Mechanistic hypothesis
- **Why:** HGF/MET is usually considered protective in fibrosis models, yet HGF and MET are risk-associated here. This paradox needs resolution.
- **Dataset evidence:** HGF HR=2.93, MET HR=2.53, SPRY2 HR=3.26 — all risk-associated.
- **External evidence:** HGF is protective in bleomycin models; however, in advanced IPF, compensatory HGF upregulation may mark severe epithelial injury. SPRY2 as an RTK inhibitor being risk-associated supports a compensatory-feedback interpretation.
- **Next step:** In vitro: test HGF/MET signaling in IPF fibroblasts vs. alveolar epithelial cells; examine whether SPRY2 knockdown alters MET-driven proliferation. In vivo: conditional MET knockout in epithelial vs. mesenchymal compartments in bleomycin model.
- **Conclusion status:** Supported hypothesis (compensatory upregulation), not established.

### Priority 4: Ferroptosis/oxidative stress axis (SLC7A11)
- **Classification:** Mechanistic hypothesis / potential therapeutic target
- **Why:** SLC7A11 (xCT) is the master regulator of ferroptosis resistance; its upregulation in IPF tissue suggests oxidative stress and potential ferroptosis vulnerability. This is a druggable axis (e.g., erastin, sulfasalazine).
- **Dataset evidence:** SLC7A11 HR=3.52, FDR=1.09×10⁻⁵; SLC39A8 and STEAP4 support a metal/oxidative stress theme.
- **External evidence:** Ferroptosis is implicated in IPF pathogenesis (alveolar epithelial cell death); SLC7A11 upregulation may be a protective response in surviving cells. **Drug existence (e.g., ferroptosis inducers) is not evidence of therapeutic efficacy in IPF.**
- **Next step:** Measure lipid peroxidation and ferroptosis markers in IPF tissue; test SLC7A11 inhibition in IPF organoids or ex vivo lung slices; assess whether SLC7A11 is epithelial or mesenchymal in origin (IHC).
- **Conclusion status:** Exploratory hypothesis.

### Priority 5: Technical artifact check for extreme-HR genes
- **Classification:** Confounding or composition check
- **Why:** The protective genes (MIR221, IHH, FAM75A2, OR2M2, DYDC2, XLOC_003303) have HR≈1.9×10⁻²² with P=0, which is biologically implausible. These likely reflect near-zero expression in most samples with a few extreme outliers, or probe/annotation errors (including CONTROL_A_33 probes).
- **Dataset evidence:** Degenerate HR values; 7 protective genes vs. 93 risk genes; several unnamed/unannotated probes (CONTROL_A_33_P3222196, CONTROL_A_33_P3345409, XLOC_003303).
- **External evidence:** None needed — the statistics are internally suspicious.
- **Next step:** Examine raw expression distributions; filter by expression threshold (e.g., >1 CPM in >20% of samples); verify probe annotation; rerun survival models after filtering; report sensitivity analyses.
- **Conclusion status:** Established evidence of a technical issue (the extreme HR values are not biologically interpretable).

## 5. Evidence grounding

| Claim | Direct (dataset) | Pathway/ontology | Protein interaction | Disease association | Expression/tissue | Literature | Independent cohort |
|---|---|---|---|---|---|---|---|
| Neutrophil/innate immune program is risk-associated | Yes (93/100 genes risk, FDR<0.01) | GO: Neutrophil Migration; KEGG: Chemokine signaling | STRING: S100A12-AGER/TLR4; CXCL1-CXCR1 | Yes (IPF neutrophilia) | Yes (neutrophil markers) | Yes | **Not performed** |
| Epithelial metaplasia program is risk-associated | Yes | GO: Antimicrobial humoral response | Weak | Yes (IPF histology) | Yes (HPA: epithelial) | Partial | **Not performed** |
| HGF/MET/NRG1/SPRY2 module is risk-associated | Yes | STRING: EGFR module | HGF-MET direct; SPRY2-CBL regulatory | Partial (context-dependent) | Yes | Yes (HGF protective in models — conflict) | **Not performed** |
| Matrix remodeling (HTRA1, MMP25) is risk-associated | Yes | GO: extracellular region | Weak | Yes (fibrosis) | Yes | Partial | **Not performed** |
| SLC7A11/ferroptosis axis is risk-associated | Yes | GO: molecular_function | STRING: CD44 module | Emerging | Yes | Yes (ferroptosis in IPF) | **Not performed** |

**Independence assessment:** The pathway/ontology annotations (GO, KEGG, Reactome) and the protein-interaction records (STRING, IntAct) may share underlying literature and are not fully independent. The disease-association evidence from GWAS/ClinVar/OpenTargets for individual genes is partly overlapping with literature sources. The only genuinely independent evidence class is an external cohort statistic, which is **absent** — external statistical validation was not performed.

**Conflicts:** (1) HGF/MET protective in animal models vs. risk-associated here — likely reflects disease stage or cell-type differences. (2) SOD3 (antioxidant) risk-associated is counterintuitive — may be compensatory. (3) MERTK (pro-resolution) risk-associated — may reflect macrophage burden rather than MERTK function per se.

## 6. Limitations and alternative explanations

### 1. Cell-composition differences (most important)
Bulk lung tissue in IPF contains variable proportions of fibroblasts, myofibroblasts, alveolar epithelium, macrophages, neutrophils, and lymphocytes. The neutrophil program (CXCR1, CD177, MMP25) and macrophage program (MERTK, STAB1, SPP1) may simply reflect the inflammatory infiltrate burden, which itself predicts mortality. **How to test:** Deconvolution (CIBERSORTx, MuSiC), single-cell RNA-seq validation, IHC for cell-type markers, and adjustment of survival models for estimated cell fractions.

### 2. Disease severity confounding
The transcriptomic profile at biopsy may reflect disease severity rather than a causal molecular driver. Patients with more severe disease have more fibrosis, more inflammation, and worse survival — so any gene correlated with severity will appear risk-associated. **How to test:** Adjust for FVC, DLCO, and GAP stage in multivariable models; stratify by early vs. advanced disease; validate in a cohort with serial sampling.

### 3. Technical artifacts and degenerate statistics
The 7 protective genes with HR≈10⁻²² and P=0, plus CONTROL_A_33 probe rows and unnamed lincRNA entries, indicate probe/annotation or zero-inflation issues. The direction-conflict flag on XLOC_003303 (rows=2) and the 29 duplicated genes/probes further complicate interpretation. **How to test:** Filter by expression threshold, verify annotations, rerun with alternative survival models (e.g., penalized Cox), and report sensitivity analyses.

### 4. Association-versus-causation ambiguity
All findings are univariate associations. A gene can be risk-associated because it drives disease progression, because it marks a high-risk cell population, or because it is a bystander correlated with severity. The HGF/MET paradox illustrates this: HGF is protective in animal models yet risk-associated here. **How to test:** Mendelian randomization for genetic instruments, in vitro perturbation studies, and animal models with cell-type-specific knockout.

### 5. Treatment exposure and cohort heterogeneity
IPF patients may be on antifibrotics (pirfenidone, nintedanib), corticosteroids, or oxygen; treatment status is not provided. Treatment can alter gene expression and survival independently of disease biology. Age, sex, and smoking history are also unaccounted for in the univariate analysis. **How to test:** Collect treatment and demographic covariates; perform multivariable adjustment; validate in a treatment-naïve cohort.

## Summary statement

The current dataset provides strong direct statistical evidence (93/100 genes risk-associated, all FDR ≤ 0.01) that a coordinated innate immune/neutrophil program, an epithelial metaplasia program, growth factor signaling (HGF/MET/NRG1), matrix remodeling (HTRA1, MMP25), and metabolic/oxidative stress responses (SLC7A11) are associated with worse all-cause mortality in IPF lung tissue; however, external statistical validation was not performed, several extreme-HR genes are likely technical artifacts, and the risk associations cannot be distinguished from disease-severity or cell-composition confounding without additional multivariable and deconvolution analyses.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=69, external claims checked=0, external mismatches=0, status=needs review.

Answer model API: deepseek / deepseek-v4-flash.

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 77/100 selected items (partially returned; some queries failed); cbioportal 78/100 selected items (records returned); chembl 13/100 selected items (partially returned; some queries failed); civic 8/100 selected items (records returned); clinicaltrials 48/100 selected items (records returned); clinvar 78/100 selected items (records returned); ensembl 25/100 selected items (partially returned; some queries failed); europepmc 860 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 83/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 78/100 selected items (records returned); humanbase 78/100 selected items (records returned); intact 81/100 selected items (partially returned; some queries failed); mygene 91/100 selected items (records returned); omnipath 47/100 selected items (records returned); opentargets 80/100 selected items (partially returned; some queries failed); pubmed 658 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 83/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 84/100 selected items (records returned)
Local databases: gutmgene 3/100 selected items (records returned); hmdb 32/100 selected items (records returned); string 79/100 selected items (records returned); trrust 25/100 selected items (records returned)
