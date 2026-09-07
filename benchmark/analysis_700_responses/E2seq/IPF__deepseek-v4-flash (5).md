# idiopathic pulmonary fibrosis (IPF) - deepseek-v4-flash

- Benchmark system: E2seq + Agent RAG
- Repeat: 7
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
- Prompt tokens: 15446
- Completion tokens: 5723
- Reasoning tokens: 0
- Total tokens: 21169
- API requests reported: 1
- Elapsed seconds: 80.973
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 1387.824
- Question handoff seconds: 1401.194
- Final benchmark system: E2seq; file rank 5/5; original repeat 7; model vendor: DeepSeek

---
# Multidimensional Interpretation of Prognostic Transcriptomic Results in Idiopathic Pulmonary Fibrosis (IPF) Lung Tissue

## Data Quality Warning (Read First)

The uploaded statistical ledger contains multiple extreme and implausible values that require immediate flagging before any biological interpretation:

- **Degenerate HR values**: Several genes show HR = 1.93e-22 (protective) or HR = 5.18e+21 (risk) with P = 0 and FDR = 0. These include MIR221, IHH, HCN4, FAM75A2, OR2M2, DYDC2, XLOC_003303 (protective) and CONTROL_A_33_P3222196, CONTROL_A_33_P3345409, DKFZP434L187 (risk). These are statistically degenerate and likely reflect separation, quasi-complete separation, or zero-event strata in the survival model rather than biologically meaningful effect sizes.
- **Non-annotated probes**: CONTROL_A_33_* and DKFZP434L187 are control or uncharacterized probes, not bona fide genes.
- **Duplicate rows**: The ledger notes 29 duplicated genes/probes; several genes (e.g., FHL2, S100A12, NRG1, LOC388210) have multiple rows, and XLOC_003303 shows a direction conflict across rows.
- **Extreme imbalance**: 93 risk-associated vs. 7 protective-associated genes, with all 100 genes passing FDR ≤ 0.01.

Despite these warnings, the bulk of the cohort (the ~90 genes with HR between ~2.0 and ~4.3) shows internally consistent, highly significant risk associations and can support an exploratory biological interpretation. The degenerate rows should be excluded from any quantitative claim about effect magnitude.

---

## 1. Overall Biological Interpretation

The dominant signal in this cohort is a **broad, coordinated upregulation of genes associated with innate immune activation, neutrophil biology, epithelial injury/repair, and matrix remodeling**, all of which are risk-associated (HR > 1) for all-cause mortality in IPF. This is biologically coherent: IPF mortality is driven by progressive fibrotic remodeling and acute exacerbations, both of which involve innate immune amplification and aberrant epithelial–mesenchymal crosstalk.

The most striking pattern is the **co-occurrence of neutrophil/monocyte chemokine and alarmin genes** (CXCL1, CXCL14, CCL7, CXCR1, S100A12, S100A14, SPP1, CD177, SELL) with **epithelial injury/repair and protease genes** (MUC1, MUC21, KRT17, KRT23, SPRR1A, SFTPB, SFTA2, PRSS8, PRSS23, MMP25, HTRA1). This combination suggests that mortality risk is associated with a **pro-inflammatory, neutrophil-rich microenvironment coupled with aberrant epithelial regeneration and extracellular matrix turnover**—a profile consistent with the "accelerated aging + aberrant wound healing" model of IPF.

A second theme is the **growth factor/receptor signaling axis** (HGF, MET, NRG1, EGFR-ligand network, BMP6, SPRY2), indicating that receptor tyrosine kinase signaling and its negative regulators are co-upregulated, consistent with a compensatory but ineffective repair response.

A third theme is **metabolic and redox stress adaptation** (SLC7A11, STEAP4, SLC39A8, ACOX2, ALDH1A3, SOD3, SLC6A8), suggesting that cells under oxidative and metabolic stress are overrepresented in high-risk patients.

**Caveat**: This is an exploratory interpretation. The uploaded statistics are internally consistent but the extreme HR values and the absence of independent-cohort validation mean that the biological conclusions below should be treated as **supported hypotheses** rather than established findings.

---

## 2. Core Biological Programs

### Program 1: Neutrophil Recruitment and Innate Immune Amplification
- **Direction**: Risk-associated (HR > 1)
- **Supporting genes**: CXCL1 (HR=2.99), CXCL14 (HR=2.38), CCL7 (HR=3.02), CXCR1 (HR=3.28), S100A12 (HR=2.53), S100A14 (HR=2.57), SPP1 (HR=3.40), CD177 (HR=2.72), SELL (HR=2.37), STAB1 (HR=3.29)
- **Pathway**: GO:1990266 Neutrophil Migration; KEGG Chemokine signaling pathway; Reactome Neutrophil degranulation (R-HSA-6798695)
- **Explanation**: The simultaneous presence of neutrophil chemoattractants (CXCL1, CXCL14, CCL7), a neutrophil receptor (CXCR1), neutrophil markers (CD177, SELL), and alarmins (S100A12, S100A14) indicates coordinated neutrophil trafficking and activation. S100A12 is a damage-associated molecular pattern (DAMP) that signals through RAGE/AGER and TLR4 (STRING confidence 0.999 and 0.970, respectively), linking innate immune activation to NF-κB signaling (Reactome: TAK1-dependent IKK and NF-κB activation).
- **Evidence strength**: Strong internal consistency (multiple independent genes in the same program, all with FDR < 4e-5). The retrieved GO/KEGG annotations support chemokine and neutrophil biology. **Limitation**: No independent-cohort statistic; neutrophil infiltration could be a consequence of disease severity rather than a driver.

### Program 2: Epithelial Injury, Aberrant Repair, and Mucin Production
- **Direction**: Risk-associated (HR > 1)
- **Supporting genes**: MUC1 (HR=2.32), MUC21 (HR=2.10), KRT17 (HR=2.19), KRT23 (HR=2.59), SPRR1A (HR=2.28), SFTPB (HR=2.66), SFTA2 (HR=2.25), CEACAM6 (HR=2.66), CEACAM7 (HR=2.31), AGR3 (HR=2.40), MAL2 (HR=2.44)
- **Pathway**: Hallmark Epithelial Mesenchymal Transition (partial); GO:0030855 Epithelial cell differentiation; KEGG Epithelial cell signaling in Helicobacter pylori infection (retrieved, though this KEGG term is not lung-specific)
- **Explanation**: Mucins (MUC1, MUC21), keratins (KRT17, KRT23), cornified envelope proteins (SPRR1A), and surfactant proteins (SFTPB, SFTA2) together indicate an activated or aberrant epithelial state—consistent with the bronchiolization and metaplastic epithelium seen in IPF honeycombing. CEACAM6/7 are epithelial adhesion molecules often upregulated in injured epithelium.
- **Evidence strength**: Moderate-to-strong internal consistency. **Limitation**: Epithelial metaplasia is a hallmark of IPF; these genes may reflect disease extent rather than a distinct mortality mechanism.

### Program 3: Extracellular Matrix Remodeling and Protease Activity
- **Direction**: Risk-associated (HR > 1)
- **Supporting genes**: HTRA1 (HR=4.30), MMP25 (HR=3.26), PRSS8 (HR=2.57), PRSS23 (HR=2.25), DYSF (HR=3.47), EFEMP1 (HR=2.33), FBLIM1 (HR=2.59), CHST15 (HR=2.99), HS3ST1 (HR=3.24), F5 (HR=2.55)
- **Pathway**: GO:0030574 Collagen catabolic process (partial); Reactome Extracellular matrix organization (R-HSA-1474244); KEGG ECM-receptor interaction (partial)
- **Explanation**: Multiple proteases (HTRA1, MMP25, PRSS8, PRSS23) and matrix-modifying enzymes (CHST15, HS3ST1) are co-upregulated, indicating active extracellular matrix degradation and remodeling. EFEMP1 (fibulin-3) and FBLIM1 are matrix-associated proteins. This program is consistent with the protease–antiprotease imbalance implicated in IPF progression.
- **Evidence strength**: Moderate. **Limitation**: Protease upregulation could reflect infiltrating inflammatory cells rather than fibroblast-derived remodeling.

### Program 4: Growth Factor Signaling and Receptor Tyrosine Kinase Activation
- **Direction**: Risk-associated (HR > 1)
- **Supporting genes**: HGF (HR=2.93), MET (HR=2.53), NRG1 (HR=2.76), SPRY2 (HR=3.26), BMP6 (HR=3.04), GALNT14 (HR=3.11), RGL1 (HR=3.26)
- **Pathway**: Reactome Signaling by Receptor Tyrosine Kinases (R-HSA-9006934); KEGG Pathways in cancer (partial)
- **Explanation**: HGF/MET and NRG1/ERBB signaling are classic epithelial repair pathways. SPRY2 is a negative regulator of RTK signaling, suggesting a feedback attempt that is insufficient. BMP6 is a TGF-β superfamily member. STRING network evidence places HGF, MET, NRG1, and MUC1 in an EGFR-centered interaction module (6 selected genes), and SPRY2 with MET via CBL.
- **Evidence strength**: Moderate. STRING co-membership is pathway/network evidence, not direct physical interaction. **Limitation**: RTK signaling upregulation is common in injured lung and may be a generic repair response.

### Program 5: Metabolic Stress, Redox Adaptation, and Lipid Metabolism
- **Direction**: Risk-associated (HR > 1)
- **Supporting genes**: SLC7A11 (HR=3.52), STEAP4 (HR=3.03), SLC39A8 (HR=3.22), ACOX2 (HR=3.18), ALDH1A3 (HR=2.27), SOD3 (HR=2.37), SLC6A8 (HR=3.21), CYP4F3 (HR=3.78)
- **Pathway**: GO:0006979 Response to oxidative stress; KEGG Ferroptosis (partial, via SLC7A11); Reactome Metabolism (R-HSA-1430728)
- **Explanation**: SLC7A11 (cystine/glutamate antiporter) is a key ferroptosis regulator; STEAP4 is a metalloreductase induced by inflammatory cytokines; SLC39A8 imports zinc/manganese; ACOX2 and ALDH1A3 are lipid-metabolism enzymes; CYP4F3 is a fatty-acid hydroxylase. This combination suggests that high-risk patients have lungs under oxidative and metabolic stress, possibly reflecting senescent or dysfunctional epithelium and macrophages.
- **Evidence strength**: Moderate. **Limitation**: These genes are expressed in multiple cell types; bulk tissue cannot localize the signal.

---

## 3. Key Genes and Interaction Modules

The following candidates are prioritized based on statistical strength (HR and FDR), biological coherence, and network evidence. The extreme-HR degenerate rows (MIR221, IHH, HCN4, etc.) are **excluded** from this list because their HR values are not biologically interpretable.

### Module A: S100A12–AGER/TLR4–NF-κB Axis
- **Statistics**: S100A12 HR=2.53, FDR=5.49e-06
- **Role**: DAMP-mediated innate immune amplification; neutrophil chemotaxis
- **Interaction nature**: STRING records indicate direct physical interaction with AGER (confidence 0.999) and TLR4 (0.970); Reactome places S100A12 in NF-κB activation pathways. These are direct interaction/regulatory records, not co-expression.
- **Interpretation**: S100A12 is a neutrophil-derived alarmin that can propagate inflammation via RAGE and TLR4. In IPF, this could amplify fibrotic signaling.

### Module B: CXCL1/CXCL14/CXCR1 Chemokine Module
- **Statistics**: CXCL1 HR=2.99, CXCL14 HR=2.38, CXCR1 HR=3.28
- **Role**: Neutrophil chemoattraction; CXCL14 is also antimicrobial and chemotactic for monocytes
- **Interaction nature**: STRING places CXCL1, CXCL14, and CXCR1 in a module with CXCL5/CXCL6 (pathway co-membership and predicted interactions; direct binding of CXCL1 to CXCR1 is established in the chemokine literature).
- **Interpretation**: A coordinated chemokine program recruiting neutrophils to the fibrotic lung.

### Module C: HGF–MET–SPRY2–CBL Regulatory Node
- **Statistics**: HGF HR=2.93, MET HR=2.53, SPRY2 HR=3.26
- **Role**: Epithelial repair signaling with negative-feedback dysregulation
- **Interaction nature**: HGF binds MET (direct ligand–receptor); SPRY2 is a feedback inhibitor of RTK signaling; STRING links MET and SPRY2 via CBL (regulatory). These are direct physical/regulatory interactions in the literature.
- **Interpretation**: Co-upregulation of the ligand, receptor, and its inhibitor suggests a stalled or ineffective repair response.

### Module D: MUC1–CEACAM6/7 Epithelial Module
- **Statistics**: MUC1 HR=2.32, CEACAM6 HR=2.66, CEACAM7 HR=2.31
- **Role**: Epithelial injury/metaplasia markers
- **Interaction nature**: Co-expression in injured epithelium; CEACAM6/7 are GPI-anchored adhesion molecules; no direct physical interaction with MUC1 is established in the retrieved records.
- **Interpretation**: These mark aberrant epithelial differentiation, likely reflecting honeycombing and bronchiolization extent.

### Module E: SPP1–CD44–SLC7A11 Module
- **Statistics**: SPP1 HR=3.40, SLC7A11 HR=3.52
- **Role**: Macrophage–epithelial crosstalk; osteopontin (SPP1) signaling; ferroptosis regulation
- **Interaction nature**: STRING links SPP1, SLC7A11, and SELL to CD44 (pathway co-membership/predicted interactions). SPP1 is a CD44 ligand (direct binding in the literature), and SLC7A11 is a CD44-associated ferroptosis suppressor.
- **Interpretation**: SPP1+ macrophages are increasingly recognized in IPF; SLC7A11 upregulation may protect stressed epithelium from ferroptosis.

### Module F: HTRA1–Protease Module
- **Statistics**: HTRA1 HR=4.30 (highest interpretable HR in the cohort)
- **Role**: Serine protease with roles in TGF-β regulation and ECM degradation
- **Interaction nature**: No direct interaction records retrieved; pathway co-membership with MMP25, PRSS8, PRSS23 in protease/ECM terms.
- **Interpretation**: HTRA1 is a strong single-gene risk marker but its role in IPF mortality is not established.

### Module G: NRG1–EGFR Network
- **Statistics**: NRG1 HR=2.76
- **Role**: ERBB ligand; epithelial proliferation/differentiation
- **Interaction nature**: STRING places NRG1 in an EGFR-centered module with HGF, MET, MUC1, EFEMP1 (pathway co-membership). NRG1 binds ERBB3/ERBB4 (direct ligand–receptor).
- **Interpretation**: Part of the broader RTK repair program.

### Module H: KRT17/KRT23–SPRR1A Epithelial Stress Module
- **Statistics**: KRT17 HR=2.19, KRT23 HR=2.59, SPRR1A HR=2.28
- **Role**: Stress keratin and cornified envelope induction
- **Interaction nature**: Co-expression in metaplastic epithelium; no direct interaction evidence.
- **Interpretation**: Markers of aberrant squamous/basal epithelial differentiation.

### Module I: SLC7A11–STEAP4–SLC39A8 Metabolic Stress Module
- **Statistics**: SLC7A11 HR=3.52, STEAP4 HR=3.03, SLC39A8 HR=3.22
- **Role**: Metal/redox homeostasis; ferroptosis regulation
- **Interaction nature**: No direct interaction; pathway co-membership in oxidative stress responses.
- **Interpretation**: A coordinated metabolic adaptation to oxidative stress.

### Module J: BMP6–GALNT14 Signaling Module
- **Statistics**: BMP6 HR=3.04, GALNT14 HR=3.11
- **Role**: TGF-β superfamily signaling; O-glycosylation
- **Interaction nature**: No direct interaction; GALNT14 could glycosylate BMP receptors (putative regulatory relationship).
- **Interpretation**: BMP6 may modulate fibrotic signaling; GALNT14-mediated glycosylation is an underexplored modifier.

---

## 4. Validation Priorities

### Priority 1: Neutrophil Infiltration as a Mortality Driver
- **Classification**: Mechanistic hypothesis
- **Why**: The chemokine/alarmin module (CXCL1, CXCL14, CXCR1, S100A12, CD177, SELL) is the most internally consistent program in the cohort and is directly actionable.
- **Dataset evidence**: Multiple risk-associated genes with FDR < 4e-5; retrieved GO/KEGG/Reactome annotations support neutrophil biology.
- **External evidence**: Neutrophilia and NETosis are implicated in IPF exacerbations in the literature; S100A12–AGER signaling is established in inflammatory disease. **External statistical validation was not performed.**
- **Next step**: Multiplex immunohistochemistry or flow cytometry on IPF lung tissue to quantify neutrophils (CD177+, SELL+) and S100A12+ cells; correlate with mortality in an independent cohort.
- **Status**: **Supported hypothesis**

### Priority 2: S100A12–AGER/TLR4 Axis as a Therapeutic Target
- **Classification**: Therapeutic target
- **Why**: S100A12 is a druggable DAMP–receptor axis with strong network evidence (direct AGER and TLR4 interactions).
- **Dataset evidence**: S100A12 HR=2.53, FDR=5.49e-06; GO annotations for RAGE receptor binding and inflammatory response.
- **External evidence**: RAGE antagonists and anti-S100A12 antibodies exist in preclinical development; however, **drug-target existence is not evidence of efficacy in IPF**. Literature supports S100A12 in neutrophilic inflammation.
- **Next step**: Test S100A12 neutralization or RAGE blockade in a bleomycin or adoptive-transfer IPF model; measure neutrophil influx and fibrosis.
- **Status**: **Exploratory hypothesis**

### Priority 3: HTRA1 as a Prognostic Biomarker
- **Classification**: Biomarker
- **Why**: HTRA1 has the highest interpretable HR (4.30) in the cohort and is a secreted protease measurable in plasma.
- **Dataset evidence**: HR=4.30, FDR=2.57e-06.
- **External evidence**: HTRA1 is implicated in ECM remodeling and TGF-β regulation; its role in IPF specifically is not established. **External statistical validation was not performed.**
- **Next step**: Measure plasma or BAL HTRA1 in an independent IPF cohort; test association with mortality and FVC decline.
- **Status**: **Exploratory hypothesis**

### Priority 4: Cell-Composition Confounding Check
- **Classification**: Confounding or composition check
- **Why**: Bulk lung tissue gene expression is dominated by cell composition. The neutrophil and epithelial programs could reflect the extent of inflammation and honeycombing rather than cell-intrinsic risk.
- **Dataset evidence**: Many risk genes (CD177, SELL, CXCR1, MUC1, KRT17) are cell-type markers.
- **External evidence**: Single-cell RNA-seq of IPF lungs shows expanded neutrophil, macrophage, and aberrant epithelial populations.
- **Next step**: Deconvolve the bulk data using reference signatures (e.g., CIBERSORTx, BisqueRNA) or validate in public scRNA-seq IPF datasets; adjust survival models for cell fractions.
- **Status**: **Supported hypothesis** (that composition contributes); the question of whether composition is the *sole* driver remains open.

### Priority 5: SPP1+ Macrophage–Epithelial Crosstalk Hypothesis
- **Classification**: Interaction / network hypothesis
- **Why**: SPP1 (HR=3.40) is a top risk gene and the SPP1–CD44–SLC7A11 module links macrophage signaling to epithelial ferroptosis protection.
- **Dataset evidence**: SPP1 and SLC7A11 both risk-associated; STRING places them in a CD44-centered module.
- **External evidence**: SPP1+ macrophages are a well-described profibrotic population in IPF scRNA-seq studies; SLC7A11-mediated ferroptosis resistance is an emerging theme.
- **Next step**: Co-staining for SPP1 and SLC7A11 in IPF tissue; functional assays of macrophage–epithelial co-culture under oxidative stress.
- **Status**: **Supported hypothesis**

---

## 5. Evidence Grounding Summary

| Claim | Direct dataset evidence | Pathway/ontology | Interaction/regulatory | Disease-association | Tissue/expression | Independent cohort |
|---|---|---|---|---|---|---|
| Neutrophil chemokine program is risk-associated | Yes (CXCL1, CXCL14, CXCR1, CCL7, FDR<4e-5) | Yes (GO:1990266, KEGG chemokine) | Yes (S100A12–AGER/TLR4 direct) | Yes (literature; IPF exacerbations) | Yes (bulk lung; cell-type markers) | **Not performed** |
| Epithelial metaplasia program is risk-associated | Yes (MUC1, KRT17, SPRR1A, SFTPB) | Partial (GO epithelial differentiation) | No direct interaction | Yes (IPF honeycombing) | Yes | **Not performed** |
| ECM/protease program is risk-associated | Yes (HTRA1, MMP25, PRSS8) | Partial (GO ECM) | No direct interaction | Yes (fibrosis literature) | Yes | **Not performed** |
| RTK signaling is risk-associated | Yes (HGF, MET, NRG1, SPRY2) | Yes (Reactome RTK) | Yes (HGF–MET direct; SPRY2–CBL regulatory) | Yes (repair literature) | Yes | **Not performed** |
| Metabolic/redox stress is risk-associated | Yes (SLC7A11, STEAP4, SLC39A8) | Partial (GO oxidative stress) | No direct interaction | Emerging (ferroptosis in fibrosis) | Yes | **Not performed** |

**Independence caveat**: The pathway/ontology, interaction, and literature records are contextual. Many QuickGO, STRING, and Reactome annotations derive from overlapping underlying publications or shared databases and are **not independent** of one another. The only direct statistical evidence is the uploaded survival table.

---

## 6. Limitations and Alternative Explanations

### Limitation 1: Cell-Composition Confounding
Bulk lung tissue in IPF contains variable proportions of fibroblasts, myofibroblasts, macrophages, neutrophils, epithelium, and endothelium. Many risk genes are lineage markers (CD177/SELL = neutrophils; MUC1/KRT17 = epithelium; SPP1 = macrophages). The observed HRs may reflect the **extent of inflammation and remodeling** rather than cell-intrinsic risk. **Investigation**: Cell-type deconvolution, spatial transcriptomics, or validation in sorted populations.

### Limitation 2: Degenerate and Non-Annotated Rows
The extreme HR values (1.93e-22, 5.18e+21) and control probes (CONTROL_A_33_*) are statistically degenerate and biologically uninterpretable. They inflate the apparent number of "significant" genes and should be excluded from any downstream analysis. The direction conflict for XLOC_003303 further complicates interpretation. **Investigation**: Re-run the survival model with Firth's penalized likelihood or exclude near-zero-variance genes.

### Limitation 3: Disease Severity and Treatment Confounding
IPF patients vary in baseline FVC, DLCO, and GAP stage, and may be on antifibrotics (pirfenidone, nintedanib) that alter gene expression. The HRs are unadjusted for these covariates in the uploaded table. **Investigation**: Multivariable Cox models adjusting for GAP stage, FVC%, and treatment.

### Limitation 4: Broad, Nonspecific Pathway Enrichment
The identified programs (innate immunity, epithelial injury, ECM remodeling) are broad and overlap with generic tissue-injury responses. They may not be IPF-specific or mortality-specific. **Investigation**: Compare against non-IPF interstitial lung disease and stable IPF cohorts; test whether the gene set discriminates rapid vs. slow progressors.

### Limitation 5: Association-Versus-Causation Ambiguity
All genes are risk-associated in a survival model; none are demonstrated to drive mortality. The co-upregulation of HGF/MET and SPRY2 could indicate a protective repair attempt that is overwhelmed, or a maladaptive feedback loop. **Investigation**: Functional perturbation studies (e.g., SPP1 knockout, S100A12 neutralization) in IPF models.

---

## Concluding Statement

The uploaded survival statistics support an exploratory model in which IPF mortality risk is associated with a coordinated risk-associated program of neutrophil chemokine/alarmin signaling (CXCL1, CXCL14, CXCR1, S100A12), aberrant epithelial repair and mucin production (MUC1, KRT17, SPRR1A), extracellular matrix protease activity (HTRA1, MMP25), growth factor signaling (HGF, MET, NRG1), and metabolic/redox stress adaptation (SLC7A11, STEAP4), but the degenerate extreme-HR rows, the absence of independent-cohort statistics, and the likely cell-composition confounding mean these conclusions should be treated as supported hypotheses requiring external validation rather than established findings.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=72, external claims checked=0, external mismatches=0, status=passed.

Answer model API: deepseek / deepseek-v4-flash.

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 77/100 selected items (partially returned; some queries failed); cbioportal 78/100 selected items (records returned); chembl 13/100 selected items (partially returned; some queries failed); civic 8/100 selected items (records returned); clinicaltrials 48/100 selected items (records returned); clinvar 78/100 selected items (records returned); ensembl 25/100 selected items (partially returned; some queries failed); europepmc 860 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 83/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 78/100 selected items (records returned); humanbase 78/100 selected items (records returned); intact 81/100 selected items (partially returned; some queries failed); mygene 91/100 selected items (records returned); omnipath 47/100 selected items (records returned); opentargets 80/100 selected items (partially returned; some queries failed); pubmed 658 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 83/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 84/100 selected items (records returned)
Local databases: gutmgene 3/100 selected items (records returned); hmdb 32/100 selected items (records returned); string 79/100 selected items (records returned); trrust 25/100 selected items (records returned)
