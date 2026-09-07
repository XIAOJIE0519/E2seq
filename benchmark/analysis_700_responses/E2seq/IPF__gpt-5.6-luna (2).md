# idiopathic pulmonary fibrosis (IPF) - gpt-5.6-luna

- Benchmark system: E2seq + Agent RAG
- Repeat: 2
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
- Model API: OpenAI / gpt-5.6-luna
- Message SHA-256: d9fe74e971569d03f1ace047ce334e08d788b93d2057913b4d42b34da6d57d2f
- Response HTTP status: 200
- Prompt tokens: 30908
- Completion tokens: 12784
- Reasoning tokens: 0
- Total tokens: 43692
- API requests reported: 2
- Elapsed seconds: 164.899
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 1387.824
- Question handoff seconds: 1401.194
- Final benchmark system: E2seq; file rank 2/5; original repeat 2; model vendor: OpenAI

---
## Data-quality warning

The statistical output is technically suspicious and should not be interpreted as a conventional, well-calibrated survival analysis without reprocessing. All 100 selected genes have \(P \le 0.05\) and FDR \(\le 0.05\), 93/100 are classified as risk-associated, several HRs are exactly or effectively extreme (\(1.93\times10^{-22}\) or \(5.18\times10^{21}\)), and many P values/FDRs are reported as 0. The table also retains 137 input rows for 100 unique genes, including 29 duplicated genes/probes, control-probe identifiers, uncharacterized loci, and at least one direction-conflicting duplicate for `XLOC_003303`.

These patterns may indicate complete or quasi-complete separation, probe or coding problems, an improperly scaled expression variable, duplicated predictors, or a computational failure in the Cox-model statistics. The HRs therefore should not be treated as reliable quantitative effect estimates until the model, event counts, censoring, normalization, duplicate handling, and numerical precision have been audited. The interpretation below is consequently **exploratory**, although it uses the supplied HR directions and the available external annotations.

## 1. Overall biological interpretation

The interpretable risk-associated genes form a coherent but potentially composition-sensitive signal involving:

- **Neutrophil and myeloid inflammation**, represented by `S100A12`, `CXCL1`, `CXCR1`, `CCL7`, `CD177`, `MMP25`, `SELL`, and `SPP1`.
- **Damaged or aberrantly activated lung epithelium**, represented by `MUC1`, `SLC34A2`, `SFTPB`, `SFTA2`, `CEACAM6`, `CEACAM7`, `KRT17`, `KRT23`, `AGR3`, and `PRSS8`.
- **Extracellular-matrix remodeling, adhesion, and cell motility**, represented by `HTRA1`, `EFEMP1`, `CHST15`, `FBLIM1`, `ENAH`, `MARCKS`, `MTSS1`, `KANK1`, and `PRSS23`.
- **Growth-factor and receptor signaling**, including the `HGF–MET`, `NRG1–EGFR`, and related signaling context.
- **Oxidative, metabolic, and stress-adaptation biology**, including `SLC7A11`, `SOD3`, `CYP4F3`, `ACOX2`, `ALDH1A3`, `STEAP4`, and `SLC39A8`.

The strongest disease-relevant interpretation is not that one gene independently causes mortality, but that higher-risk lung samples may contain a combination of inflammatory-cell recruitment, epithelial injury or remodeling, matrix reorganization, and growth-factor activation. However, the same bulk-lung pattern could partly reflect differences in immune, epithelial, endothelial, or fibroblast composition rather than altered transcription within a single cell type.

The seven protective-associated entries are difficult to interpret biologically. They include `MIR221`, `IHH`, `FAM75A2`, `OR2M2`, `DYDC2`, and the poorly annotated `LOC100128226` (HR \(=0.0070320732\), FDR \(=4.7992385\times10^{-35}\)), alongside probe-like or uncharacterized entries. Their extreme HRs and the absence of a coherent protective program make them insufficient evidence for a true protective mechanism. `IHH` and `MIR221` should not be called protective without technical and independent validation.

**External statistical validation was not performed.** Pathway, network, tissue, and literature records provide biological plausibility but do not replicate the survival associations.

## 2. Core biological programs

### Program 1: Neutrophil–myeloid inflammatory recruitment

- **Association:** Exploratory risk-associated program.
- **Supporting genes:** `S100A12` (HR \(=2.5346746\), FDR \(=5.4858851\times10^{-6}\)), `CXCL1` (HR \(=2.9896541\), FDR \(=3.7334116\times10^{-5}\)), `CXCR1` (HR \(=3.2808305\), FDR \(=1.6046748\times10^{-5}\)), `CCL7` (HR \(=3.0162564\), FDR \(=2.6037418\times10^{-5}\)), `CD177` (HR \(=2.7158374\), FDR \(=3.9005539\times10^{-5}\)), `MMP25`, `SELL`, and `SPP1`.
- **Relevant standardized pathways:** GO **Neutrophil Migration** (GO:1990266), GO chemotaxis, KEGG **Chemokine signaling pathway**, and Reactome **Neutrophil degranulation**.
- **Interpretation:** These genes collectively indicate chemokine production or response, leukocyte adhesion/migration, neutrophil-associated biology, and inflammatory matrix or phagocyte activity. QuickGO annotates `S100A12` and `CCL7` to inflammatory response and monocyte chemotaxis; Reactome links `S100A12` to neutrophil degranulation and NF-κB-related signaling.
- **Evidence strength:** **Moderate for biological plausibility, weak-to-moderate for prognosis because the direct statistics are technically suspect.** The dataset contains multiple genes from the same inflammatory axis, and the retrieved GO/Reactome/STRING records are concordant in function. These sources may nevertheless overlap in their underlying literature and annotation models.
- **Limitation:** Bulk lung expression cannot distinguish activated resident cells from increased neutrophil or monocyte abundance. The retrieved `S100A12` interactions with `AGER`, `TLR4`, `S100A8`, and `S100A9` are database-supported functional or physical-association records, but they do not demonstrate that these interactions occur in the studied lungs or cause mortality.

### Program 2: Injured or remodeled epithelial state

- **Association:** Risk-associated.
- **Supporting genes:** `MUC1` (HR \(=2.324446\), FDR \(=1.0892619\times10^{-5}\)), `SLC34A2` (HR \(=2.2735087\), FDR \(=1.1386793\times10^{-5}\)), `SFTPB` (HR \(=2.6648273\), FDR \(=3.3741902\times10^{-5}\)), `SFTA2` (HR \(=2.2481876\), FDR \(=2.9216189\times10^{-5}\)), `CEACAM6`, `CEACAM7`, `KRT17`, `KRT23`, `AGR3`, `PRSS8`, and `MAL2`.
- **Relevant standardized pathways:** GO epithelial cell differentiation, epithelial cell development, and cell–cell junction organization; relevant epithelial-signaling annotations include KEGG **Epithelial cell signaling in Helicobacter pylori infection**, although this KEGG label is not specific to IPF and should not be interpreted as infection in these patients.
- **Interpretation:** The combination of surfactant-associated genes, epithelial membrane and junction genes, mucins, and keratins is consistent with altered alveolar or airway epithelial identity, epithelial stress, and remodeling. It may reflect reparative metaplasia or expansion of particular epithelial populations rather than a uniform increase in epithelial injury.
- **Evidence strength:** **Moderate exploratory evidence.** Multiple epithelial genes show risk association, and tissue/pathway annotations support epithelial localization or function. The literature record for `SFTA2` concerns lung-cancer risk rather than IPF (PMID: **37471639**), so it is contextual rather than disease-specific validation.
- **Limitation:** Cell-composition and sampling effects are major alternatives. In particular, `KRT17`, `KRT23`, mucins, and CEACAM genes may reflect airway contamination, bronchiolization, or altered epithelial proportions.

### Program 3: Matrix remodeling, adhesion, and motility

- **Association:** Risk-associated.
- **Supporting genes:** `HTRA1` (HR \(=4.3017004\), FDR \(=2.5707761\times10^{-6}\)), `EFEMP1` (HR \(=2.3286851\), FDR \(=2.7318548\times10^{-5}\)), `CHST15` (HR \(=2.9905364\), FDR \(=2.0944132\times10^{-5}\)), `FBLIM1`, `ENAH`, `MARCKS` (HR \(=3.99821\), FDR \(=2.1170634\times10^{-5}\)), `MTSS1`, `KANK1`, `PRSS23`, `TM4SF1`, and `F5`.
- **Relevant standardized pathways:** GO **extracellular matrix organization**, cell-substrate adhesion, actin cytoskeleton organization, and focal-adhesion-related processes.
- **Interpretation:** These genes collectively support altered extracellular-matrix turnover, cytoskeletal organization, adhesion, and cell movement. `HTRA1` is compatible with extracellular protease activity, while `EFEMP1`, `FBLIM1`, `ENAH`, `MARCKS`, and `MTSS1` connect matrix or membrane signaling with cellular morphology and motility.
- **Evidence strength:** **Moderate exploratory evidence.** The program is supported by several functionally related genes and recurrent extracellular-region, plasma-membrane, and Golgi annotations. These annotations are broad and do not establish increased fibrosis or demonstrate a causal fibroblast program.
- **Limitation:** Matrix genes can arise from fibroblast abundance, vascular remodeling, epithelial migration, or inflammatory-cell infiltration. Histology, hydroxyproline or collagen measurements, and cell-resolved expression are needed to identify the source.

### Program 4: Growth-factor receptor signaling involving EGFR/MET

- **Association:** Risk-associated.
- **Supporting genes:** `HGF` (HR \(=2.926959\), FDR \(=1.0892619\times10^{-5}\)), `MET` (HR \(=2.5264463\), FDR \(=1.4677765\times10^{-5}\)), `NRG1` (HR \(=2.7571185\), FDR \(=6.852395\times10^{-6}\)), `MUC1`, `SPRY2`, `EFEMP1`, and `TM4SF1`.
- **Relevant standardized pathways:** Reactome/GO receptor tyrosine kinase signaling, EGFR signaling, MAPK signaling, and PI3K–AKT-related processes, where supported by the gene annotations.
- **Interpretation:** The co-occurrence of ligand, receptor, and pathway-modulator genes suggests an activated epithelial–stromal growth-factor signaling environment. The retrieved STRING network places `HGF`, `MET`, `MUC1`, `NRG1`, and `EFEMP1` in an EGFR-centered functional neighborhood, while `MET` and `SPRY2` form another reported network relationship.
- **Evidence strength:** **Weak-to-moderate, hypothesis-generating evidence.** The pattern is biologically plausible, but the supplied network record does not establish a single active receptor complex, ligand–receptor direction, or causal signaling route in IPF lung.
- **Limitation:** Growth-factor signaling may be a secondary response to tissue injury or a marker of epithelial/stromal composition. A therapeutic opportunity cannot be inferred from the presence of druggable receptors.

### Program 5: Redox, lipid, and metabolic stress adaptation

- **Association:** Risk-associated, but more exploratory than the programs above.
- **Supporting genes:** `SLC7A11` (HR \(=3.5163423\), FDR \(=1.0940918\times10^{-5}\)), `SOD3` (HR \(=2.3705165\), FDR \(=2.7318548\times10^{-5}\)), `CYP4F3` (HR \(=3.7794741\), FDR \(=9.470129\times10^{-8}\)), `ACOX2`, `ALDH1A3`, `STEAP4`, and `SLC39A8`.
- **Relevant standardized pathways:** Hallmark **Reactive Oxygen Species Pathway** and **Fatty Acid Metabolism**, plus GO redox and lipid-metabolic processes, subject to confirmation by formal enrichment.
- **Interpretation:** `SLC7A11` is consistent with cellular adaptation to oxidative or ferroptotic stress, `SOD3` with extracellular antioxidant defense, and `CYP4F3`/`ACOX2` with lipid oxidation or eicosanoid-related metabolism. The coordinated risk direction suggests that metabolic stress may accompany severe remodeling or inflammation.
- **Evidence strength:** **Exploratory.** The genes have plausible functional annotations, but no new enrichment statistic was computed, and the program is less internally specific than the inflammatory and epithelial programs.
- **Limitation:** These genes can reflect cell type, medication exposure, nutritional state, smoking history, or general disease severity rather than an IPF-specific metabolic mechanism.

## 3. Key genes and interaction modules

The following are priorities for investigation, not validated causal drivers.

1. **`S100A12` inflammatory node** — risk-associated, HR \(=2.5346746\), FDR \(=5.4858851\times10^{-6}\). It is relevant to neutrophil and monocyte recruitment. Its reported relationships with `AGER`, `TLR4`, and S100-family proteins are **database-supported interaction or functional-association records**, not proof of direct interaction in this cohort. The relationship to `CXCL1`, `CCL7`, and `CXCR1` is best described as **pathway co-membership or indirect inflammatory coupling**.

2. **`CXCL1–CXCR1` chemokine module** — both risk-associated: `CXCL1` HR \(=2.9896541\), FDR \(=3.7334118\times10^{-5}\); `CXCR1` HR \(=3.2808305\), FDR \(=1.6046748\times10^{-5}\). This supports a chemokine ligand–receptor hypothesis and is consistent with GO chemotaxis and KEGG chemokine signaling. It is a **putative regulatory/signaling relationship**, not demonstrated receptor activation in the samples.

3. **`CCL7` monocyte-recruitment signal** — risk-associated, HR \(=3.0162564\), FDR \(=2.6037418\times10^{-5}\). Its annotated CCR1/CCR2/CCR3/CCR5 binding and monocyte chemotaxis support an inflammatory recruitment role. Relationships to `S100A12` and `CXCL1` are **parallel or indirect chemokine-network relationships**, not direct physical interactions.

4. **`SPP1–STAB1–MERTK` phagocyte/remodeling context** — all are risk-associated: `SPP1` HR \(=3.3988408\), `STAB1` HR \(=3.2915921\), and `MERTK` HR \(=3.7021145\). This may represent a macrophage-associated remodeling state. The relationship is primarily **cell-type co-expression and pathway/network association**; the supplied evidence does not establish a direct physical complex or causal macrophage program.

5. **Epithelial injury/remodeling module** — `MUC1`, `SLC34A2`, `SFTPB`, `SFTA2`, `CEACAM6`, and `KRT17` are all risk-associated, with HRs from 2.1878884 to 2.6648273 in the supplied rows. These genes are related by **epithelial identity and pathway co-membership**, not necessarily by direct protein interaction.

6. **`HTRA1–EFEMP1–CHST15` matrix module** — risk-associated, with HRs 4.3017004, 2.3286851, and 2.9905364, respectively. The proposed relationship is **extracellular-matrix co-membership and indirect remodeling**, not a demonstrated physical complex. This module is relevant to fibrosis biology but remains confounded by fibroblast and vascular abundance.

7. **`HGF–MET` signaling pair** — both risk-associated, `HGF` HR \(=2.926959\) and `MET` HR \(=2.5264463\). This is a **putative ligand–receptor regulatory relationship**. The current data do not show ligand binding, receptor phosphorylation, or causation.

8. **`NRG1` with EGFR-centered signaling context** — `NRG1` is risk-associated, HR \(=2.7571185\), and the network digest places `NRG1`, `MUC1`, `HGF`, `MET`, and `EFEMP1` near EGFR. This is **network functional association and pathway co-membership**; direct physical interaction should not be inferred from STRING neighborhood evidence.

9. **`SLC7A11–SOD3` redox module** — both risk-associated, HR \(=3.5163423\) and 2.3705165. The relationship is **complementary redox biology**, not a direct interaction. It may indicate oxidative stress adaptation or altered cell composition.

10. **`LOC100128226` protective-associated signal** — HR \(=0.0070320732\), P \(=1.2409004\times10^{-38}\), FDR \(=4.7992385\times10^{-35}\). This is a statistically striking but biologically uncharacterized observation. Because it lacks a coherent annotated program and has an implausibly extreme HR, it should be treated as an **exploratory candidate requiring probe-level and independent-cohort verification**, not as an established protective biomarker.

## 4. Validation priorities

### 1. Audit the survival model and probe identities  
**Classification:** Confounding or composition check

- **Why prioritize:** Extreme reciprocal HRs, zero P values, universal significance, duplicated probes, controls, and direction conflicts could invalidate the quantitative results.
- **Current evidence:** The ledger reports 100 unique genes but 137 retained rows, 29 duplicated genes/probes, 93 risk-associated genes, and seven protective-associated genes.
- **External support or conflict:** No external statistical validation is available; database annotations cannot resolve a modeling failure.
- **Next step:** Refit a prespecified Cox model after removing control probes and ambiguous loci, collapsing or selecting duplicate probes, checking expression scaling and event counts, examining Schoenfeld residuals, testing penalized Cox/Firth methods where appropriate, and reporting confidence intervals rather than only HRs and zero-valued P values.
- **Conclusion level:** **Established evidence that a technical/statistical audit is necessary; biological conclusions remain exploratory.**

### 2. Test whether the inflammatory signal reflects immune-cell composition  
**Classification:** Confounding or composition check

- **Why prioritize:** `S100A12`, `CXCL1`, `CXCR1`, `CCL7`, `CD177`, `SELL`, and `SPP1` form the clearest risk-associated program, but these genes can be driven by neutrophil or monocyte abundance.
- **Current evidence:** Direct risk associations plus GO Neutrophil Migration, chemokine signaling, and Reactome neutrophil-degranulation annotations.
- **External support or conflict:** QuickGO, Reactome, and STRING support inflammatory functions, but they do not provide independent survival replication.
- **Next step:** Apply validated bulk deconvolution, compare with histologic immune-cell counts, and confirm spatially or by flow cytometry/single-cell RNA sequencing. Test whether gene–mortality associations persist after adjustment for estimated cell fractions.
- **Conclusion level:** **Supported hypothesis**, not causal evidence.

### 3. Resolve epithelial remodeling versus airway-composition effects  
**Classification:** Biomarker

- **Why prioritize:** The epithelial cluster is broad and includes multiple membrane, surfactant, mucin, and keratin genes, making it a possible composite biomarker of severe epithelial remodeling.
- **Current evidence:** Risk associations for `MUC1`, `SLC34A2`, `SFTPB`, `SFTA2`, `CEACAM6`, `CEACAM7`, and `KRT17`.
- **External support or conflict:** Lung expression and pathway annotations support epithelial relevance; PMID **37471639** links `SFTA2` to lung-related genetic analysis, but this is not IPF survival validation.
- **Next step:** Validate a prespecified multi-gene score in an independent IPF lung cohort and, if possible, in blood or bronchoalveolar lavage; use spatial transcriptomics or immunohistochemistry to distinguish alveolar epithelial injury from bronchiolar expansion.
- **Conclusion level:** **Supported hypothesis** for an epithelial-state biomarker; clinical utility is unestablished.

### 4. Test the matrix-remodeling and growth-factor hypothesis experimentally  
**Classification:** Mechanistic hypothesis

- **Why prioritize:** Matrix genes and growth-factor signaling provide a plausible link between tissue injury, remodeling, and poor outcome.
- **Current evidence:** Risk-associated `HTRA1`, `EFEMP1`, `CHST15`, `HGF`, `MET`, `NRG1`, and `TM4SF1`, together with extracellular-region and receptor-signaling annotations.
- **External support or conflict:** STRING and pathway records support functional connectivity; literature retrieved for `FAM198B` concerns lung adenocarcinoma survival and ERK/MMP biology (PMID **29217529**), which is not evidence that the same mechanism operates in IPF.
- **Next step:** Use IPF epithelial–fibroblast co-cultures or precision-cut lung slices, measure ligand/receptor activation and matrix deposition, and perturb the pathway genetically or pharmacologically. A drug response alone should not be interpreted as proof of therapeutic efficacy.
- **Conclusion level:** **Exploratory-to-supported hypothesis**, depending on experimental confirmation.

### 5. Establish external prognostic reproducibility of a compact signature  
**Classification:** Biomarker

- **Why prioritize:** The current table cannot establish a clinically useful signature because independent-cohort statistics are absent and the apparent effect distribution is degenerate.
- **Current evidence:** Many genes show nominally strong risk associations, including `HTRA1`, `CYP4F3`, `S100A12`, `SPP1`, `HGF`, and `SLC7A11`.
- **External support or conflict:** The evidence pack explicitly reports independent-cohort validation as unavailable; literature and pathway recurrence are not replication.
- **Next step:** Lock a small biologically motivated signature after model correction, validate it in an independent IPF cohort with all-cause mortality, adjust for age, sex, baseline lung function, disease stage, treatment, and batch, and assess calibration, discrimination, and incremental value over clinical variables.
- **Conclusion level:** **Insufficient evidence** for a validated prognostic biomarker at present.

## 5. Evidence grounding

- **Direct dataset evidence:** The supplied survival table is the only cohort-level statistical evidence. It reports 93 risk-associated and seven protective-associated genes, but the numerical pattern is technically abnormal.
- **Pathway and ontology evidence:** GO, Reactome, KEGG, and QuickGO records support chemotaxis, neutrophil degranulation, inflammatory signaling, epithelial biology, extracellular localization, and membrane/adhesion functions. The reported pathway recurrence was not accompanied by a newly calculated enrichment P value and should not be called formal enrichment.
- **Network evidence:** STRING reports 50 edges in the selected-gene batch and identifies EGFR-, CD44-, CXCL5/CXCL6-, and FN1-centered neighborhoods. These are generally **functional association or network-context records**; they do not by themselves prove direct physical binding, co-expression in the cohort, or causal signaling.
- **Tissue and disease evidence:** GTEx, HPA, GWAS, ClinVar, OpenTargets, and related records provide gene annotation, tissue, genetic, or disease context for many genes. They do not demonstrate that the observed HRs replicate in IPF.
- **Literature evidence:** The supplied PubMed/Europe PMC records include lung-cancer or other-disease studies such as CYP4F3 and lung cancer (PMID **28150878**), FAM198B and lung adenocarcinoma (PMID **29217529**), and SFTA2 and lung cancer risk (PMID **37471639**). These support plausibility for selected genes but are not independent IPF mortality studies.
- **Therapeutic evidence:** Drug or clinical-trial records exist for some genes, but druggability is not evidence that targeting the gene improves IPF or survival. No therapeutic conclusion is established here.
- **Independence:** Database sources within a category may reuse the same publications, pathway curation, or prediction models. Their agreement should therefore be treated as convergent annotation, not automatically independent confirmation.

## 6. Major limitations and alternative explanations

1. **Statistical degeneracy and possible separation:** The extreme HRs, zero P values, universal FDR significance, and duplicated rows may reflect model or numerical artifacts. Reanalysis is required before ranking genes quantitatively.

2. **Bulk-lung cell composition:** Inflammatory, epithelial, endothelial, and fibroblast proportions can strongly influence lung transcriptomes. Deconvolution, histology, single-cell or spatial profiling, and cell-fraction-adjusted survival models are needed.

3. **Disease severity and clinical confounding:** Mortality-associated expression may simply mark advanced fibrosis, reduced lung function, acute exacerbation, oxygen requirement, treatment exposure, age, or comorbidity. Multivariable adjustment and stratified analyses are necessary.

4. **Broad and nonspecific pathway labels:** Chemokine signaling, epithelial signaling, protein binding, plasma membrane, and extracellular-region annotations are biologically broad. They support plausibility but do not identify a unique IPF mechanism.

5. **Association-versus-causation and generalizability:** A risk-associated transcript may be a consequence, marker, or mediator of severe disease. The absence of an independent cohort, model specification, confidence intervals, and clinical covariates means that no gene, pathway, interaction, or therapeutic target can yet be considered validated for mortality prediction or IPF treatment.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=0, external claims checked=0, external mismatches=0, status=passed.

Answer model API: OpenAI / gpt-5.6-luna

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 77/100 selected items (partially returned; some queries failed); cbioportal 78/100 selected items (records returned); chembl 13/100 selected items (partially returned; some queries failed); civic 8/100 selected items (records returned); clinicaltrials 48/100 selected items (records returned); clinvar 78/100 selected items (records returned); ensembl 25/100 selected items (partially returned; some queries failed); europepmc 860 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 83/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 78/100 selected items (records returned); humanbase 78/100 selected items (records returned); intact 81/100 selected items (partially returned; some queries failed); mygene 91/100 selected items (records returned); omnipath 47/100 selected items (records returned); opentargets 80/100 selected items (partially returned; some queries failed); pubmed 658 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 83/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 84/100 selected items (records returned)
Local databases: gutmgene 3/100 selected items (records returned); hmdb 32/100 selected items (records returned); string 79/100 selected items (records returned); trrust 25/100 selected items (records returned)
