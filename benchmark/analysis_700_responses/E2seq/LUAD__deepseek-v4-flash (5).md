# lung adenocarcinoma (LUAD) - deepseek-v4-flash

- Benchmark system: E2seq + Agent RAG
- Repeat: 7
- Task type: PROGNOSIS
- Tissue / sample source: lung adenocarcinoma tumor tissue
- Comparison or endpoint: overall survival (OS)
- Answer input cohort: Discovery/Core only
- Selected items: 100
- Input fields: gene name, effect size (log2FC/HR), P value, FDR
- E2seq Agent RAG: enabled
- Conversation memory: disabled
- Thinking mode: disabled
- Held-out validation data in prompt/RAG: no
- Model API: DeepSeek / deepseek-v4-flash
- Message SHA-256: a2c9355177479f23c6c81afe1b39ba697ac131cc344bb83120b98e2c6bbfee49
- Response HTTP status: 200
- Prompt tokens: 36992
- Completion tokens: 14696
- Reasoning tokens: 0
- Total tokens: 51688
- API requests reported: 3
- Elapsed seconds: 96.958
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 957.651
- Question handoff seconds: 970.897
- Final benchmark system: E2seq; file rank 5/5; original repeat 7; model vendor: DeepSeek

---
# Multidimensional Interpretation of Prognostic Transcriptomic Results in Lung Adenocarcinoma (LUAD)

## 0. Critical Data-Quality Warning (must read first)

Before any biological interpretation, the statistical input itself raises serious technical concerns that materially affect every downstream conclusion:

- **Degenerate HR values at machine precision**: 59 of 100 selected genes have HR = 5.1847055e+21 (identical value, essentially the upper numerical limit of the floating-point representation), with P = 0 and FDR = 0. One gene (TCP10L3) has HR = 1.929e-22 (near the lower limit). These are not biologically meaningful effect sizes; they indicate a **complete separation / quasi-separation problem** in the Cox model — a situation where the predictor perfectly (or near-perfectly) separates events from censoring in the fitted data.
- **Direction conflict flagged**: The ledger marks `Y_RNA` as "direction-conflict; rows=163", meaning multiple rows for the same gene/probe have conflicting HR directions across the 263 input rows. This further supports the interpretation that many extreme values arise from sparse or unstable estimation rather than true effect sizes.
- **High proportion of non-coding / pseudogene / unannotated features**: The overwhelming majority of the 96 "risk-associated" genes are long intergenic non-coding RNAs (RP11-*, CTD-*, LINC*), pseudogenes (e.g., RBMY2AP, RAP1BP2, ATP5PBP2), small RNAs (Y_RNA, RNU6-78P, MIR*), and unmapped Ensembl loci. Only a small number of protein-coding genes with established biology carry moderate HRs (1.2–1.5): PITX3, DKK1, VAX1, TLE1, KRT6A, FUT4, LDLRAD3, RHOF, RGS20, RHCG, CREG2.
- **Protective-associated genes are scarce**: Only 4 of 100 genes are protective (HR < 1): RBMXP1 (HR = 0.212), TCP10L3 (HR = 1.93e-22), CRNDE (HR = 0.716), CMAHP (HR = 0.706).

**Consequence**: The extreme HR values (e+21) should not be interpreted as "very strong risk factors." They are statistical artifacts of model instability. The biologically interpretable signal resides almost entirely in the moderate-HR protein-coding genes (HR ≈ 1.2–1.5) and the four protective genes. All program-level conclusions below are therefore built on the moderate-HR genes, with the extreme values treated as a model-fit problem rather than as evidence of biological effect.

---

## 1. Overall Biological Interpretation

Within the interpretable subset of this cohort, the prognostic signal in LUAD tumor tissue is dominated by **risk-associated (HR > 1) expression of developmental transcription factors, Wnt pathway modulators, and epithelial/keratinization programs**, together with a smaller set of protective (HR < 1) genes. The most coherent biological themes are:

1. **Wnt signaling and developmental transcription-factor programs** — DKK1 (HR = 1.48), TLE1 (HR = 1.48), PITX3 (HR = 1.43), VAX1 (HR = 1.33), and the retrieved GO/KEGG annotations (regulation of Wnt signaling, planar cell polarity, Wnt signaling pathway) point toward aberrant reactivation of developmental signaling as a poor-prognosis feature.
2. **Epithelial differentiation / keratinization and glycosylation** — KRT6A (HR = 1.39) and FUT4 (HR = 1.40) suggest altered epithelial differentiation state and fucosyl-glycan remodeling, both recurrent themes in aggressive LUAD.
3. **Small GTPase / actin-cytoskeleton signaling** — RHOF (HR = 1.40) and RGS20 (HR = 1.35) implicate Rho-family GTPase signaling and G-protein regulation in poor outcome.
4. **Long non-coding RNA and pseudogene-dominated risk signature** — the majority of risk genes are lncRNAs (LINC01312, LINC02178, LINC01910, LINC02323, LINC02802, LINC00707), antisense transcripts (ITGB1-DT, FAS-AS1, MARCHF4-AS1), and pseudogenes. This could reflect genuine lncRNA biology, but more parsimoniously reflects **technical artifacts** (spurious alignments, low-expression features with unstable HR estimates, or contamination), a distinction that must be validated.

The protective genes (RBMXP1, CRNDE, CMAHP) do not form a single coherent program; they are individually interesting but too few to define a protective pathway with confidence.

**Key caveat**: The extreme HRs and the lncRNA/pseudogene enrichment mean that the "risk signature" as a whole is likely dominated by technical or composition effects rather than by a single biological pathway. The protein-coding gene set provides the most defensible biological signal.

---

## 2. Core Biological Programs

Given the data-quality constraints, I restrict program-level interpretation to genes with moderate, biologically interpretable HRs. I identify **five** programs, in decreasing order of confidence:

### Program 1: Wnt Signaling Modulation and Developmental Transcription-Factor Programs
- **Direction**: Risk-associated (HR > 1)
- **Major supporting genes**: DKK1 (HR = 1.48), TLE1 (HR = 1.48), PITX3 (HR = 1.43), VAX1 (HR = 1.33)
- **Pathway**: GO: Regulation of Wnt signaling pathway (GO:0030111); KEGG: Wnt signaling pathway
- **Rationale**: DKK1 is a secreted Wnt antagonist; TLE1 is a corepressor in Wnt/β-catenin and Notch pathways; PITX3 and VAX1 are homeodomain transcription factors with developmental roles. Their co-occurrence with risk suggests that **dysregulated developmental transcription factor networks, potentially interacting with Wnt signaling, mark aggressive LUAD**. The retrieved GO module (regulation of Wnt signaling) directly lists DKK1 and TLE1 among its genes.
- **Evidence strength**: Moderate. Multiple independent protein-coding genes with consistent risk direction and pathway-ontology support (GO/KEGG recurrence). **Limitations**: These genes are not known to act in a single linear pathway; their co-occurrence may reflect broader developmental-program activation rather than a single Wnt axis. DKK1's role is context-dependent (Wnt inhibition can be either tumor-suppressive or pro-metastatic depending on context).

### Program 2: Epithelial Keratinization and Squamous-like Differentiation
- **Direction**: Risk-associated
- **Major supporting genes**: KRT6A (HR = 1.39), FUT4 (HR = 1.40)
- **Pathway**: KEGG: Mannose type O-glycan biosynthesis; Glycosphingolipid biosynthesis (for FUT4); keratinization is a canonical epithelial differentiation program
- **Rationale**: KRT6A is a stress-inducible keratin expressed in activated/proliferating epithelia; FUT4 encodes fucosyltransferase 4, involved in Lewis antigen synthesis and glycan remodeling. Both are associated with epithelial-mesenchymal plasticity and aggressive tumor behavior in multiple cancers.
- **Evidence strength**: Moderate (two independent protein-coding genes, consistent direction, pathway-ontology support). **Limitation**: Two genes are a thin basis for a "program"; the retrieved literature for KRT6A is from an unrelated context (alopecia areata), so disease-specific LUAD support is not established here.

### Program 3: Small GTPase Signaling and Actin-Cytoskeleton Regulation
- **Direction**: Risk-associated
- **Major supporting genes**: RHOF (HR = 1.40), RGS20 (HR = 1.35)
- **Pathway**: GO: regulation of small GTPase mediated signal transduction; actin filament organization (both annotated for RHOF in QuickGO); Reactome: G alpha (i/z) signalling events (for RGS20)
- **Rationale**: RHOF (RhoF) is a Rho-family GTPase involved in actin organization and cell migration; RGS20 is a regulator of G-protein signaling (GAP for Gαz/Gαi). Both are consistent with enhanced migratory/invasive signaling. STRING records show RHOF with predicted interactions to ACTN1 and ARHGAP1 (actin/cytoskeleton nodes), and RGS20 with GNAZ/GNB5/GNAI2 — supporting a coherent G-protein/Rho signaling module at the network level.
- **Evidence strength**: Moderate. Two independent genes, consistent direction, network (STRING) and pathway (Reactome/GO) support. **Limitation**: STRING interactions are predicted/curated, not necessarily direct physical interactions in LUAD; no independent-cohort statistic is available. RHOF's poor-OS association is supported by literature in AML (PMID 34405015), but that is a different disease.

### Program 4: Long Non-Coding RNA / Antisense Transcript Risk Signature
- **Direction**: Risk-associated
- **Major supporting genes**: LINC01312 (HR = 1.36), LINC02178 (HR = 1.30), LINC01910 (HR = 1.31), LINC02323 (HR = 1.37), LINC02802 (HR = 1.33), LINC00707 (HR = 1.32), ITGB1-DT (HR = 1.30), FAS-AS1 (HR = 5.2e+21, extreme/unreliable)
- **Pathway**: No single standardized pathway; this is a feature-class program rather than a pathway program
- **Rationale**: The sheer number of lncRNAs/antisense transcripts with risk direction suggests either (a) a genuine lncRNA-mediated regulatory layer, or (b) a technical artifact (see Limitations). The most defensible biological interpretation is that this represents **transcriptional noise / pervasive transcription** associated with aggressive tumors, or a **cell-composition artifact**. ITGB1-DT has literature support as a LUAD biomarker (PMID 34906142), which lends some credibility to at least this one lncRNA.
- **Evidence strength**: Weak-to-moderate as a biological program; strong as a statistical pattern. **Limitation**: Most of these loci lack functional annotation; the extreme HR values among this class strongly suggest estimation instability.

### Program 5: Protective-Associated Transcripts (Heterogeneous)
- **Direction**: Protective (HR < 1)
- **Major supporting genes**: RBMXP1 (HR = 0.21), CRNDE (HR = 0.72), CMAHP (HR = 0.71)
- **Pathway**: No common pathway; RBMXP1 is an RNA-binding-motif pseudogene, CRNDE is a lncRNA, CMAHP is a complement-regulatory pseudogene
- **Rationale**: These three protective genes do not share a pathway. Their protective direction is statistically significant (FDR ≤ 0.0006 for all three), but biologically they are heterogeneous. CRNDE has been reported as oncogenic in some cancers, so its protective direction here is **directionally conflicting with prior literature** — a point that must be flagged.
- **Evidence strength**: Weak as a coherent program; statistically strong as individual associations. **Limitation**: Too few genes, no shared biology, and CRNDE's direction conflicts with published oncogenic roles in other contexts.

---

## 3. Key Genes and Interaction Modules

I select **eight** candidates (within the limit of ten), prioritizing protein-coding genes with moderate, credible HRs and biological interpretability:

| # | Gene | HR (direction) | Role in programs | Relationship type(s) |
|---|------|----------------|------------------|----------------------|
| 1 | **DKK1** | 1.48 (risk) | Wnt signaling modulator | Pathway co-membership with TLE1 (Wnt pathway); indirect/putative with PITX3/VAX1 (developmental TF network) |
| 2 | **TLE1** | 1.48 (risk) | Wnt/Notch transcriptional corepressor | Pathway co-membership with DKK1 (Wnt); no direct physical interaction evidence in this dataset |
| 3 | **PITX3** | 1.43 (risk) | Developmental homeodomain TF | Co-expression/co-occurrence with VAX1 (both developmental TFs); no direct interaction evidence |
| 4 | **VAX1** | 1.33 (risk) | Developmental TF | Co-expression with PITX3; STRING predicts interaction with ASXL2 (chromatin regulator) — predicted, not direct physical evidence |
| 5 | **KRT6A** | 1.39 (risk) | Epithelial keratinization | Pathway co-membership (keratinization); no interaction evidence with other selected genes |
| 6 | **FUT4** | 1.40 (risk) | Glycan/fucosylation remodeling | STRING predicts interactions with B3GNT3 and B4GALT1 (glycosyltransferases) — predicted network, not direct physical interaction |
| 7 | **RHOF** | 1.40 (risk) | Rho GTPase / actin cytoskeleton | STRING predicts interactions with ACTN1 and ARHGAP1 (cytoskeleton regulators); pathway co-membership with RGS20 in small GTPase signaling |
| 8 | **RGS20** | 1.35 (risk) | G-protein signaling regulation | STRING predicts direct interactions with GNAZ, GNB5, GNAI2, GNAQ (G-protein subunits) — these are predicted/curated physical interactions, not experimentally verified in LUAD |

**Interaction-type clarification**:
- **Direct physical interaction**: Not established for any gene pair in this dataset. STRING records for RHOF-ACTN1, RHOF-ARHGAP1, FUT4-B3GNT3, FUT4-B4GALT1, and RGS20-GNAZ/GNB5/GNAI2/GNAQ are predicted/curated interactions from databases, not direct experimental evidence in LUAD.
- **Regulatory interaction**: None of the selected genes have documented regulatory relationships (e.g., TF-target) in the retrieved records.
- **Co-expression / pathway co-membership**: This is the strongest defensible relationship type for DKK1-TLE1 (Wnt pathway co-membership) and RHOF-RGS20 (small GTPase pathway co-membership).
- **Indirect/putative**: PITX3-VAX1 as co-occurring developmental TFs; lncRNA-protein relationships (e.g., ITGB1-DT) are putative.

**Note on ITGB1-DT**: This lncRNA (HR = 1.30) has the strongest literature support in LUAD specifically (PMID 34906142: ITGB1-DT/ARNTL2 axis as a LUAD biomarker), making it the most credible lncRNA candidate despite the general lncRNA-quality concerns.

---

## 4. Validation Priorities

### Priority 1: Resolve the complete-separation / extreme-HR artifact before any biological claim
- **Classification**: Confounding or composition check
- **Why**: 59/100 genes have HR = 5.18e+21 and 1 gene has HR = 1.9e-22, all with P = 0. These are classic signs of quasi-complete separation in the Cox model, which produces numerically degenerate and biologically meaningless estimates.
- **Current dataset evidence**: The ledger itself (identical extreme HRs, direction conflict for Y_RNA).
- **External evidence**: This is a well-known statistical phenomenon in survival analysis with sparse or perfectly separating predictors.
- **Next step**: Re-fit the model with Firth's penalized likelihood correction, or use exact conditional logistic regression; check for zero-cell counts in stratified analyses; examine whether low-expression genes with many zero counts drive the separation.
- **Conclusion status**: Established evidence (the artifact is statistically evident), but the *biological* interpretation must be deferred.

### Priority 2: Validate the Wnt/developmental TF risk program in an independent LUAD cohort
- **Classification**: Biomarker (prognostic signature)
- **Why**: DKK1, TLE1, PITX3, VAX1 form the most coherent protein-coding risk program.
- **Current dataset evidence**: Four independent genes, consistent risk direction, FDR ≤ 3.5e-7 (DKK1) to ≤ 9.2e-6 (VAX1); GO/KEGG Wnt pathway recurrence.
- **External evidence**: No independent-cohort statistic was supplied — **external statistical validation was not performed**. Literature supports Wnt pathway relevance in LUAD broadly, but this is contextual, not replication.
- **Next step**: Test a combined DKK1/TLE1/PITX3/VAX1 expression index against OS in an independent LUAD RNA-seq cohort (e.g., TCGA-LUAD or a published validation set) with multivariable adjustment for stage, age, sex, and smoking.
- **Conclusion status**: Supported hypothesis (within this dataset); requires external validation before being considered established.

### Priority 3: Mechanistically test DKK1's role in LUAD progression
- **Classification**: Mechanistic hypothesis
- **Why**: DKK1 is a secreted Wnt antagonist with context-dependent tumor biology; its risk association here is strong (HR = 1.48, FDR = 3.5e-7) but its mechanism in LUAD is unresolved.
- **Current dataset evidence**: Risk association only; no expression or functional data.
- **External evidence**: DKK1 has dual roles (tumor-suppressive Wnt inhibition vs. pro-metastatic in some contexts); this conflict must be resolved experimentally.
- **Next step**: CRISPR knockout or overexpression of DKK1 in LUAD cell lines; assess Wnt/β-catenin activity, proliferation, migration, and invasion; validate in xenograft models.
- **Conclusion status**: Exploratory hypothesis.

### Priority 4: Test the Rho/G-protein signaling module (RHOF + RGS20) as a therapeutic axis
- **Classification**: Therapeutic target
- **Why**: RHOF and RGS20 both show risk direction and share a signaling context (small GTPase / G-protein regulation); RHOF has literature support for poor-OS association in AML (PMID 34405015), suggesting cross-disease relevance.
- **Current dataset evidence**: RHOF HR = 1.40 (FDR = 4.0e-4), RGS20 HR = 1.35 (FDR = 5.8e-4); STRING network predicts interactions with cytoskeleton (ACTN1, ARHGAP1) and G-protein (GNAZ, GNB5) nodes.
- **External evidence**: Rho-family GTPases are established drivers of invasion/metastasis; however, **the existence of drugs targeting Rho/G-protein pathways does not by itself establish therapeutic efficacy in LUAD**.
- **Next step**: siRNA/shRNA knockdown of RHOF and RGS20 in LUAD cell lines; assess migration, invasion, and actin organization; test whether combined knockdown is additive.
- **Conclusion status**: Exploratory hypothesis.

### Priority 5: Distinguish lncRNA signal from technical/composition artifact
- **Classification**: Confounding or composition check
- **Why**: The majority of risk genes are lncRNAs/pseudogenes with extreme HRs; this pattern is as consistent with technical artifacts (multimapping reads, low expression, alignment to repetitive regions) as with genuine biology.
- **Current dataset evidence**: The extreme HR values and the preponderance of unannotated/lncRNA features.
- **External evidence**: ITGB1-DT has LUAD-specific literature support (PMID 34906142), but most other lncRNAs lack functional annotation.
- **Next step**: (a) Quantify tumor purity (e.g., ESTIMATE or inferCNV) and test whether the lncRNA risk signature correlates with purity; (b) re-map reads with stringent multi-mapping filters and check whether the extreme-HR genes survive; (c) validate the top lncRNAs (e.g., ITGB1-DT, LINC01312) by qRT-PCR and RNA-FISH in independent LUAD tissues.
- **Conclusion status**: The artifact hypothesis is a **supported hypothesis**; the biological lncRNA hypothesis is **exploratory** until purity-adjusted and multi-mapping-filtered analyses are performed.

---

## 5. Evidence Grounding

| Conclusion | Direct input evidence | Pathway/ontology | Network/interaction | Disease-association | Literature | Independence assessment |
|-----------|----------------------|------------------|---------------------|---------------------|-----------|------------------------|
| Wnt/developmental TF risk program | Yes (DKK1, TLE1, PITX3, VAX1 HRs, FDRs) | Yes (GO:0030111, KEGG Wnt) | No direct interaction evidence | Weak (no LUAD-specific records retrieved for these genes) | Contextual only | GO/KEGG annotations and the input HRs are independent; but GO/KEGG may share underlying literature with each other |
| Epithelial keratinization/glycan program | Yes (KRT6A, FUT4 HRs) | Yes (KEGG glycan biosynthesis) | Predicted network (FUT4-B3GNT3/B4GALT1) | Weak (KRT6A literature is from alopecia, not LUAD) | Contextual | Pathway and network records are independent of the input statistics but may share underlying databases |
| Rho/G-protein module | Yes (RHOF, RGS20 HRs) | Yes (GO small GTPase, Reactome Gα signaling) | Predicted STRING interactions | Partial (RHOF in AML, PMID 34405015) | Contextual | STRING predictions and Reactome pathways are independent of the input statistics |
| lncRNA risk signature | Yes (statistically strong but degenerate HRs) | No | No | Partial (ITGB1-DT in LUAD, PMID 34906142) | Contextual | The statistical signal is direct but technically suspect; ITGB1-DT literature is independent |
| Protective genes (RBMXP1, CRNDE, CMAHP) | Yes (HRs 0.21–0.72, FDR ≤ 5.8e-4) | No | No | Conflicting (CRNDE oncogenic in other cancers) | Contextual | Directional conflict with literature for CRNDE must be flagged |

**Genuinely independent evidence**: The uploaded HR/FDR statistics and the external database/literature records are independent in origin. However, within the external records, GO, KEGG, Reactome, and STRING may draw on overlapping underlying publications and annotations, so they should not be treated as fully independent confirmations of each other.

**Conflicting evidence**: CRNDE's protective direction (HR = 0.72) conflicts with its reported oncogenic roles in other cancer types; this is a genuine conflict that requires LUAD-specific resolution.

---

## 6. Limitations and Alternative Explanations

### Limitation 1: Complete separation / model instability (dominant limitation)
The near-identical extreme HRs (5.18e+21 for 59 genes) indicate quasi-complete separation. These values are not interpretable as effect sizes. **Mitigation**: penalized likelihood (Firth) regression, exact methods, or dropping near-constant predictors.

### Limitation 2: Tumor purity and cell-composition effects
LUAD tumors contain variable stromal, immune, and normal epithelial content. The lncRNA/pseudogene-dominated risk signature could reflect differences in tumor purity or stromal content rather than tumor-cell-intrinsic biology. **Investigation**: estimate purity (ESTIMATE, ABSOLUTE, or histology), adjust for purity in Cox models, and test whether the risk signature persists in purified tumor-cell data (e.g., single-cell RNA-seq or laser-capture microdissection).

### Limitation 3: Technical artifacts from multi-mapping and low-expression features
Many risk genes are pseudogenes, Y_RNA, snRNAs, and unmapped loci — features prone to multi-mapping and alignment noise. **Investigation**: re-quantify with multi-mapping-aware tools (e.g., Salmon with decoy-aware index, or exclude multi-mappers), filter by mean expression and detection rate, and re-fit the survival model.

### Limitation 4: Disease severity and treatment exposure confounding
OS is influenced by stage, treatment history, and comorbidities. If stage or treatment is imbalanced across expression groups, HRs may reflect these confounders rather than biology. **Investigation**: multivariable Cox models adjusting for stage, age, sex, smoking, and treatment; stratified analyses by stage.

### Limitation 5: Association-versus-causation ambiguity
All results are associational. The risk-associated genes (DKK1, TLE1, RHOF, etc.) may be markers of an aggressive tumor state rather than drivers. **Investigation**: functional perturbation experiments (as proposed in Validation Priorities 3 and 4) are required to move from association toward causation.

### Limitation 6 (additional): Broad/nonspecific pathway enrichment
The GO/KEGG recurrence for "Wnt signaling" and "glycan biosynthesis" may reflect the small number of interpretable protein-coding genes rather than a specific pathway activation. With only ~15 interpretable protein-coding genes, pathway-level conclusions are inherently underpowered.

---

## Summary Statement

The interpretable signal in this LUAD prognostic cohort points to a risk-associated program of developmental transcription factors and Wnt modulators (DKK1, TLE1, PITX3, VAX1), epithelial keratinization and glycan remodeling (KRT6A, FUT4), and small GTPase/G-protein signaling (RHOF, RGS20), but the dominant statistical feature — 59 genes with identical machine-limit HRs of 5.18e+21 — indicates a complete-separation artifact that must be resolved with penalized or exact survival models before any of these biological programs can be considered robust, and no independent-cohort external statistical validation was performed in this analysis.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=40, external claims checked=0, external mismatches=0, status=passed.

Answer model API: deepseek / deepseek-v4-flash.

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 53/100 selected items (records returned); cbioportal 51/100 selected items (records returned); chembl 16/100 selected items (records returned); civic 1/100 selected items (records returned); clinicaltrials 6/100 selected items (records returned); clinvar 30/100 selected items (records returned); ensembl 11/100 selected items (partially returned; some queries failed); europepmc 362 articles / initial full-cohort RAG 100 queries + 4 current-round queries; some queries failed; gtex 81/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 14/100 selected items (records returned); humanbase 56/100 selected items (partially returned; some queries failed); intact 18/100 selected items (records returned); mygene 59/100 selected items (records returned); omnipath 3/100 selected items (records returned); opentargets 55/100 selected items (records returned); pubmed 202 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 17/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 17/100 selected items (records returned)
Local databases: gutmgene 0/100 selected items (reachable but no records for this batch); hmdb 2/100 selected items (records returned); string 14/100 selected items (records returned); trrust 4/100 selected items (records returned)
