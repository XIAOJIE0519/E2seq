# idiopathic pulmonary fibrosis (IPF) - gpt-5.6-luna

- Benchmark system: E2seq + Agent RAG
- Repeat: 1
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
- Prompt tokens: 15463
- Completion tokens: 6284
- Reasoning tokens: 0
- Total tokens: 21747
- API requests reported: 1
- Elapsed seconds: 164.437
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 1387.824
- Question handoff seconds: 1401.194
- Final benchmark system: E2seq; file rank 1/5; original repeat 1; model vendor: OpenAI

---
# Data-quality warning

The survival results are technically suspicious and should **not be interpreted as calibrated effect estimates without reanalysis**. The ledger contains 100 unique genes represented by 137 retained rows, including 29 duplicated/group rows, and reports:

- 93 risk-associated genes and 7 protective-associated genes.
- Every selected gene has P ≤ 0.05 and FDR ≤ 0.05.
- Several rows have exactly `P=0`, `FDR=0`, or extremely saturated HRs such as `1.9287498e-22` and `5.1847055e+21`.
- Control probes and poorly annotated transcripts occur among the strongest results.
- `XLOC_003303` has a direction conflict across retained rows.

This pattern is compatible with numerical underflow, separation, probe-mapping problems, duplicated measurements, or an overly flexible/saturated survival model. Therefore, the reported HRs and P values are the direct input evidence, but their magnitudes and apparent universal significance are unreliable. The biological interpretation below is consequently **exploratory**, not a validated prognostic signature. No independent-cohort survival statistic was supplied; **external statistical validation was not performed**.

## 1. Overall biological interpretation

After setting aside the most suspicious control, uncharacterized, and saturated rows, the interpretable risk-associated genes converge on a lung injury and poor-outcome phenotype involving:

1. **Neutrophil and inflammatory chemokine activity**, represented by `S100A12`, `CXCL1`, `CCL7`, `CXCR1`, `CD177`, `MMP25`, and `SELL`.
2. **Abnormal epithelial-cell state and barrier/surfactant remodeling**, represented by `MUC1`, `SLC34A2`, `SFTPB`, `SFTA2`, `CEACAM6`, `CEACAM7`, `AGR3`, `KRT17`, `KRT23`, `SPRR1A`, and `MUC21`.
3. **Extracellular-matrix remodeling, stromal activation, and altered tissue architecture**, including `HTRA1`, `EFEMP1`, `CHST15`, `F5`, `TM4SF1`, `CXCL14`, `STAB1`, and `SPP1`.
4. **Stress, redox, and metabolic adaptation**, including `SLC7A11`, `SOD3`, `ACOX2`, `ALDH1A3`, `STEAP4`, `ANKRD22`, and `CYP4F3`.
5. **Growth-factor and cytoskeletal signaling**, involving `HGF`, `MET`, `NRG1`, `FHL2`, `MARCKS`, `MRVI1`, `RGL1`, `ENAH`, and `KANK1`.

The most defensible model is that higher expression of several coordinated inflammatory, epithelial-remodeling, and stromal/repair programs marks more advanced or biologically active IPF and is associated with higher all-cause mortality. However, bulk lung expression cannot establish whether these genes drive disease, reflect disease severity, or primarily measure changes in cell composition.

The one conventional protective-associated result is `LOC100128226` with HR `0.0070320732`, P `1.2409004e-38`, FDR `4.7992385e-35`. Several other protective-associated rows have implausibly extreme HRs, including `MIR221`, `IHH`, `FAM75A2`, and `OR2M2`; these should be treated as potential technical or annotation artifacts until independently reproduced.

## 2. Core biological programs

The supplied GO/KEGG/STRING results were retrieved before synthesis and were **not newly recomputed here**. Their recurrence is contextual evidence, not a new enrichment P value.

### Program 1: Neutrophil recruitment and innate inflammatory signaling

- **Direction:** Risk-associated.
- **Major genes:** `S100A12` HR `2.5346746`, `CXCL1` HR `2.9896541`, `CCL7` HR `3.0162564`, `CXCR1` HR `3.2808305`, `CD177` HR `2.7158374`, `MMP25` HR `3.2556305`, `SELL` HR `2.3747997`, and `SPP1` HR `3.3988408`.
- **Relevant standardized terms:** GO:1990266, *neutrophil migration*; GO:0061844, *antimicrobial humoral immune response mediated by antimicrobial peptide*; KEGG *chemokine signaling pathway*.
- **Interpretation:** Multiple chemokines, a chemokine receptor, neutrophil-associated markers, and an inflammatory S100 protein point to an inflammatory microenvironment with potential neutrophil recruitment and activation. The supplied Reactome record links `S100A12` to neutrophil degranulation, advanced glycation end-product receptor signaling, and NF-κB-related pathways. STRING records report interactions of `S100A12` with `AGER`, `TLR4`, `S100A8`, and `S100A9`; these are database-supported interaction records, not interactions demonstrated in this cohort.
- **Evidence strength:** **Supported hypothesis** from a multi-gene risk-associated pattern plus ontology, Reactome, and network annotations.
- **Limitations:** In bulk lung, this may reflect increased neutrophil or monocyte abundance rather than activation within resident lung cells. The retrieved KEGG terms include broad inflammatory or infection-related pathways and are not specific to IPF. No independent IPF survival statistic was supplied.

### Program 2: Injured or aberrantly remodeled alveolar epithelial state

- **Direction:** Risk-associated.
- **Major genes:** `MUC1` HR `2.324446`, `SLC34A2` HR `2.2735087`, `SFTPB` HR `2.6648273`, `SFTA2` HR `2.2481876`, `CEACAM6` HR `2.6583866`, `CEACAM7` HR `2.3129975`, `AGR3` HR `2.4049488`, `KRT17` HR `2.1878884`, `KRT23` HR `2.5853444`, `SPRR1A` HR `2.2771352`, and `MUC21` HR `2.1034589`.
- **Relevant standardized terms:** Epithelial-cell differentiation and epithelial structural programs; surfactant and secretory epithelial biology. A single exact pathway assignment is not sufficiently specific from the supplied evidence.
- **Interpretation:** The coordinated presence of epithelial mucins, surfactant-associated genes, epithelial junction/secretory markers, and keratinization-associated genes is consistent with epithelial injury, altered differentiation, and remodeling of the alveolar or distal-airway compartment. `SFTA2` has published lung genetic-association evidence in a lung-cancer context, but that is not evidence of IPF prognosis; see PMID [37471639](https://pubmed.ncbi.nlm.nih.gov/37471639/).
- **Evidence strength:** **Supported hypothesis** based on convergence of several epithelial genes in the uploaded risk-associated results and tissue/pathway annotations.
- **Limitations:** Some markers may indicate airway epithelial contamination, metaplastic epithelium, or altered cell proportions rather than a common disease mechanism. The literature records supplied for `SFTA2`, `KRT23`, and related genes are largely from cancer or other diseases, so disease-specific extrapolation is limited.

### Program 3: Matrix remodeling, vascular/stromal activation, and tissue architecture

- **Direction:** Risk-associated.
- **Major genes:** `HTRA1` HR `4.3017004`, `EFEMP1` HR `2.3286851`, `CHST15` HR `2.9905364`, `F5` HR `2.5492222`, `TM4SF1` HR `2.5703046`, `CXCL14` HR `2.3752098`, `STAB1` HR `3.2915925`, `SPP1` HR `3.3988408`, and `HGF` HR `2.926959`.
- **Relevant standardized terms:** Extracellular-region and extracellular-matrix organization terms; cell–matrix adhesion and tissue-remodeling processes. The supplied annotations also include extracellular-region representation and membrane-associated components.
- **Interpretation:** The simultaneous risk association of matrix-associated, endothelial/stromal, macrophage-associated, and protease-related genes is compatible with active remodeling of the fibrotic lung. `SPP1`, `STAB1`, and `EFEMP1` may reflect macrophage, stromal, or vascular compartments, while `HTRA1`, `CHST15`, and `TM4SF1` are consistent with altered matrix or tissue architecture. This is a program-level interpretation rather than evidence that any one of these genes causes fibrosis.
- **Evidence strength:** **Supported hypothesis**, with direct multi-gene statistical support and pathway/tissue context.
- **Limitations:** Formal pathway enrichment was not rerun for this answer, and the retrieved recurrent annotations do not provide an independent P value. Matrix and vascular signals are strongly sensitive to fibrosis extent, vascular remodeling, and cell composition.

### Program 4: Oxidative, metabolic, and epithelial stress adaptation

- **Direction:** Risk-associated.
- **Major genes:** `SLC7A11` HR `3.5163423`, `SOD3` HR `2.3705165`, `ACOX2` HR `3.1831737`, `ALDH1A3` HR `2.2709533`, `STEAP4` HR `3.0269152`, `ANKRD22` HR `2.5550238`, and `CYP4F3` HR `3.7794741`.
- **Relevant standardized terms:** Oxidative-stress response, lipid and peroxisomal metabolism, cellular redox homeostasis, and xenobiotic/metabolic processes; no single standardized pathway is sufficiently established from the supplied records.
- **Interpretation:** This combination suggests that poor-outcome tissue may contain cells adapting to oxidative, lipid, inflammatory, or metabolic stress. `SLC7A11` is particularly compatible with altered cystine uptake and redox buffering, whereas `SOD3` and `ACOX2` point toward extracellular antioxidant and lipid/peroxisomal biology. `CYP4F3` may also reflect myeloid or inflammatory-cell composition.
- **Evidence strength:** **Exploratory to supported hypothesis**, because the genes are statistically coherent in direction but their shared IPF-specific mechanism is not established by the supplied evidence.
- **Limitations:** The program combines genes from different cell types and metabolic processes. Published evidence for `CYP4F3` in the supplied literature includes a lung-cancer GWAS pathway analysis rather than IPF prognosis (PMID [28150878](https://pubmed.ncbi.nlm.nih.gov/28150878/)). It should not be interpreted as disease-specific validation.

### Program 5: Growth-factor, Ras/ERK, and cytoskeletal remodeling

- **Direction:** Risk-associated.
- **Major genes:** `HGF` HR `2.926959`, `MET` HR `2.5264463`, `NRG1` HR `2.7571185`, `FHL2` HR `2.7639514`, `MRVI1` HR `3.8541091`, `MARCKS` HR `3.99821`, `RGL1` HR `3.2649702`, `ENAH` HR `2.0330546`, and `KANK1` HR `3.5878891`.
- **Relevant standardized terms:** Growth-factor receptor signaling, Ras/ERK signaling, cell motility, actin organization, and cell–matrix interaction.
- **Interpretation:** The pattern is compatible with activated repair, migration, contractility, or survival signaling. STRING records connect selected genes around EGFR, including `HGF`, `MET`, `MUC1`, `NRG1`, and `EFEMP1`, and around the Ras-family signaling gene `RGL1`. These records indicate pathway/network relationships; they do not prove direct physical interactions among every listed gene.
- **Evidence strength:** **Supported hypothesis** at the network and pathway level.
- **Limitations:** Growth-factor signaling can be reparative as well as pathogenic, and bulk expression cannot determine the responding cell type. The supplied literature record for `FAM198B` concerns lung adenocarcinoma survival and ERK-mediated MMP-1 expression, not IPF survival (PMID [29217529](https://pubmed.ncbi.nlm.nih.gov/29217529/)); therefore cancer literature should not be treated as IPF replication.

## 3. Key genes and interaction modules

The candidates below are prioritized for biological interpretability and program convergence, not solely by HR magnitude.

| Candidate | Current result | Potential role | Relationship type and evidence |
|---|---:|---|---|
| **S100A12-centered inflammatory module** | `S100A12` HR `2.5346746`, P `2.5789837e-09`, FDR `5.4858851e-06` | Neutrophil/monocyte inflammatory signaling and possible RAGE/TLR4 activation | STRING reports interactions with `AGER`, `TLR4`, `S100A8`, and `S100A9`; these are database-supported protein/network relationships, not cohort-demonstrated physical interactions. |
| **CXCL1–CXCR1–CCL7 axis** | `CXCL1` HR `2.9896541`; `CXCR1` HR `3.2808305`; `CCL7` HR `3.0162564` | Leukocyte recruitment and inflammatory amplification | Chemokine signaling and pathway co-membership; receptor–ligand relationships are biologically plausible, but direct binding or functional signaling was not measured here. |
| **SPP1–CD44-associated module** | `SPP1` HR `3.3988408` | Macrophage/stromal activation, matrix interaction, and inflammatory remodeling | STRING links selected genes around `CD44`, including `SPP1`; this is network evidence. A functional `SPP1`–`CD44` signaling relationship is plausible, but causality is untested. |
| **Epithelial mucin/surfactant module** | `MUC1` HR `2.324446`; `SLC34A2` HR `2.2735087`; `SFTPB` HR `2.6648273`; `SFTA2` HR `2.2481876` | Distal epithelial injury, altered epithelial differentiation, and surfactant/barrier remodeling | Epithelial pathway co-membership and tissue-expression evidence; not evidence of direct protein interactions among these genes. |
| **CEACAM6–CEACAM7/AGR3 epithelial secretory module** | `CEACAM6` HR `2.6583866`; `CEACAM7` HR `2.3129975`; `AGR3` HR `2.4049488` | Secretory epithelial remodeling and possibly abnormal epithelial state | Co-expression or shared epithelial-cell program is the most defensible relationship; direct physical interaction is insufficiently supported here. |
| **HGF–MET growth-factor module** | `HGF` HR `2.926959`; `MET` HR `2.5264463` | Repair, migration, survival, and stromal–epithelial signaling | HGF–MET is a biologically established ligand–receptor relationship, but the uploaded data show association only. The STRING EGFR-centered record is additional network context. |
| **NRG1/EGFR-related signaling module** | `NRG1` HR `2.7571185`; `MUC1`, `MET`, and `EFEMP1` also risk-associated | Growth-factor signaling and epithelial/stromal response | Pathway/network co-membership; direct physical interaction should not be inferred for all members. |
| **HTRA1–EFEMP1–CHST15 remodeling module** | `HTRA1` HR `4.3017004`; `EFEMP1` HR `2.3286851`; `CHST15` HR `2.9905364` | Matrix turnover, extracellular organization, and fibrotic tissue remodeling | Functional/pathway co-membership and indirect extracellular relationships; direct protein interaction is not established by the supplied evidence. |
| **SLC7A11–SOD3 redox module** | `SLC7A11` HR `3.5163423`; `SOD3` HR `2.3705165` | Oxidative-stress handling and altered redox balance | Shared redox biology and indirect functional relationship; no direct interaction is demonstrated. |
| **LOC100128226** | HR `0.0070320732`, P `1.2409004e-38`, FDR `4.7992385e-35`; protective-associated | Potential protective marker requiring annotation and replication | The statistical association is direct input evidence, but biological interpretation is **insufficient evidence** because the transcript is poorly characterized and no independent survival statistic is available. |

`MIR221`, `IHH`, `FAM75A2`, `OR2M2`, and other extreme protective rows should not be promoted as biological key genes until probe identity, normalization, event coding, and model stability are checked.

## 4. Validation priorities

### 1. Resolve inflammatory-cell composition versus inflammatory activation  
**Classification:** Confounding or composition check

- **Why prioritize:** The `S100A12`, `CXCL1`, `CCL7`, `CXCR1`, `CD177`, `SELL`, and `MMP25` pattern could reflect neutrophil/monocyte abundance in bulk lung.
- **Current evidence:** Multiple risk-associated genes and the retrieved neutrophil-migration/chemokine annotations.
- **External evidence:** `S100A12` has GO, Reactome, and STRING support for inflammatory, neutrophil, RAGE, and TLR4-related biology. These sources may overlap in literature and database curation and are not independent survival validation.
- **Next step:** Apply cell deconvolution and immune-cell marker adjustment; confirm with single-cell or spatial RNA-seq and immunohistochemistry for S100A12, CD177, CXCR1, and SPP1.
- **Status:** **Supported hypothesis**, not established causality.

### 2. Test a multigene prognostic program in an independent IPF cohort  
**Classification:** Biomarker

- **Why prioritize:** The risk-associated genes form a more coherent candidate biomarker than any single extreme HR.
- **Current evidence:** 93 of 100 selected genes are risk-associated, with representative conventional HRs approximately 2–4 and FDR values below 0.001 for many genes.
- **External evidence:** The evidence pack reports no independent cohort, endpoint, model, or survival statistic; thus there is no external statistical validation. Literature on individual genes is often from cancer or other diseases.
- **Next step:** Refit a penalized Cox model or prespecified pathway score in an independent IPF lung cohort, report calibration, discrimination, proportional-hazards checks, and incremental value beyond age, sex, lung function, disease stage, and treatment.
- **Status:** **Exploratory hypothesis** until independently validated.

### 3. Determine whether epithelial remodeling is linked to fibrotic severity  
**Classification:** Mechanistic hypothesis

- **Why prioritize:** The epithelial mucin/surfactant and keratin-associated genes occur together with matrix and growth-factor signals.
- **Current evidence:** Risk association of `MUC1`, `SLC34A2`, `SFTPB`, `SFTA2`, `CEACAM6`, `KRT17`, and related genes.
- **External evidence:** Tissue and pathway annotations support epithelial identity. The supplied `SFTA2` and `KRT23` literature is not IPF-specific; therefore it supports plausibility but not disease-specific mechanism.
- **Next step:** Use spatial transcriptomics or single-cell data to map these genes to alveolar type II, airway, metaplastic, or stromal compartments, followed by organoid or precision-cut lung experiments.
- **Status:** **Supported hypothesis**.

### 4. Test the HGF–MET/EGFR growth-factor network experimentally  
**Classification:** Interaction / network hypothesis

- **Why prioritize:** `HGF`, `MET`, `NRG1`, `MUC1`, and `EFEMP1` are jointly risk-associated and occur in the supplied EGFR-centered STRING network.
- **Current evidence:** `HGF` HR `2.926959` and `MET` HR `2.5264463`, together with risk-associated `NRG1`.
- **External evidence:** Ligand–receptor and network annotations support a plausible signaling relationship, but the STRING record does not establish that these genes physically interact in IPF lung. No independent IPF functional or prognostic experiment was supplied.
- **Next step:** Measure ligand/receptor protein localization, phospho-MET/EGFR/ERK activity, and perturb the pathway in relevant epithelial–fibroblast co-cultures or lung organoids.
- **Status:** **Exploratory to supported hypothesis**, depending on the specific interaction tested.

### 5. Evaluate redox and matrix pathways as therapeutic hypotheses, not established targets  
**Classification:** Therapeutic target

- **Why prioritize:** `SLC7A11`, `SOD3`, `HTRA1`, `EFEMP1`, `CHST15`, and `SPP1` connect stress adaptation with tissue remodeling and are risk-associated.
- **Current evidence:** Multiple genes in these programs have FDR values below `4e-05`, but the global saturation raises concern about model validity.
- **External evidence:** Pathway, disease, and therapeutic records are present for some genes, but the evidence pack does not provide an independent IPF treatment-effect statistic. The existence of drugs or inhibitors for a target does not establish efficacy in IPF.
- **Next step:** Prioritize perturbation experiments that distinguish whether altering each pathway changes fibroblast activation, epithelial survival, matrix deposition, or inflammatory recruitment, followed by toxicity and in vivo validation.
- **Status:** **Exploratory hypothesis**.

## 5. Evidence grounding and conflicts

- **Direct input evidence:** The uploaded survival table and authoritative ledger provide the only cohort-level statistical evidence. The strongest conventional interpretable risk signals include `HTRA1` HR `4.3017004`, `MARCKS` HR `3.99821`, `MRVI1` HR `3.8541091`, `RAB3IL1` HR `3.840031`, `CYP4F3` HR `3.7794741`, `BASP1` HR `3.7716028`, `MERTK` HR `3.7021145`, and `SPP1` HR `3.3988408`.
- **Pathway/ontology evidence:** The supplied GO and KEGG batch supports neutrophil migration, antimicrobial/inflammatory response, chemokine signaling, epithelial signaling, and cytoskeletal organization. These were not recomputed and should not be described as statistically enriched in this analysis.
- **Network evidence:** STRING and other network records support relationships around `S100A12`, `CXCL1/CXCR1`, `SPP1/CD44`, and EGFR/MET-related signaling. Relationship types are source-dependent and may include curated, predicted, or literature-derived associations.
- **Tissue and disease evidence:** Tissue-expression and disease/genetic annotations support that many candidates are biologically relevant to lung or inflammatory biology, but source coverage and annotation presence do not establish prognostic replication.
- **Literature evidence:** The question-specific search retrieved 658 PubMed and 860 Europe PMC records, but the highlighted records mainly concern lung cancer, metabolic disease, neurological disease, or other conditions. For example, `CYP4F3` is discussed in a lung-cancer GWAS context (PMID [28150878](https://pubmed.ncbi.nlm.nih.gov/28150878/)), and `FAM198B` in lung adenocarcinoma survival (PMID [29217529](https://pubmed.ncbi.nlm.nih.gov/29217529/)). These records provide plausibility, not IPF mortality replication.
- **Independent validation:** Not available. Pathway recurrence, interaction records, tissue annotations, literature counts, and therapeutic records are not substitutes for an independent-cohort HR, P value, or FDR.

## 6. Major limitations and alternative explanations

1. **Model saturation and numerical instability:** Exact zero P values, extreme HRs, universal significance, and control probes suggest separation, underflow, or preprocessing/model problems. Recheck event coding, censoring, normalization, expression scaling, covariate specification, confidence intervals, and proportional-hazards assumptions.
2. **Probe and annotation quality:** Controls, obsolete identifiers, lincRNAs, and duplicated probes may inflate apparent significance. Re-map probes to current genome builds, remove controls, collapse duplicate probes transparently, and rerun the survival model.
3. **Bulk tissue composition:** Neutrophil, macrophage, epithelial, endothelial, and fibroblast abundance may drive the signal. Use histologic fibrosis scores, cell deconvolution, single-cell/spatial data, and cell-type-adjusted models.
4. **Clinical confounding:** Mortality-associated expression may proxy age, sex, baseline FVC/DLCO, oxygen requirement, acute exacerbation, disease stage, treatment exposure, smoking, infection, or transplant status. These variables should be included in multivariable and sensitivity analyses.
5. **Association-versus-causation and endpoint specificity:** The endpoint is all-cause mortality, not necessarily IPF-specific progression. Genes may mark severe disease or comorbidity rather than a causal IPF mechanism. External validation should use prespecified IPF outcomes and evaluate whether the signature adds prognostic value beyond established clinical predictors.

Overall, the most credible exploratory interpretation is a high-risk lung-tissue state combining inflammatory-cell recruitment, epithelial remodeling, extracellular-matrix disturbance, and stress/growth-factor signaling, but the current numerical results require technical reanalysis and independent IPF-cohort validation before any gene or pathway is considered a reliable prognostic biomarker or therapeutic target.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=0, external claims checked=0, external mismatches=0, status=passed.

Answer model API: OpenAI / gpt-5.6-luna

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 77/100 selected items (partially returned; some queries failed); cbioportal 78/100 selected items (records returned); chembl 13/100 selected items (partially returned; some queries failed); civic 8/100 selected items (records returned); clinicaltrials 48/100 selected items (records returned); clinvar 78/100 selected items (records returned); ensembl 25/100 selected items (partially returned; some queries failed); europepmc 860 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 83/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 78/100 selected items (records returned); humanbase 78/100 selected items (records returned); intact 81/100 selected items (partially returned; some queries failed); mygene 91/100 selected items (records returned); omnipath 47/100 selected items (records returned); opentargets 80/100 selected items (partially returned; some queries failed); pubmed 658 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 83/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 84/100 selected items (records returned)
Local databases: gutmgene 3/100 selected items (records returned); hmdb 32/100 selected items (records returned); string 79/100 selected items (records returned); trrust 25/100 selected items (records returned)
