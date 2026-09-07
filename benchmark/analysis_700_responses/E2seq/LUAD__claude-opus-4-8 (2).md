# lung adenocarcinoma (LUAD) - claude-opus-4-8

- Benchmark system: E2seq + Agent RAG
- Repeat: 2
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
- Model API: Anthropic / claude-opus-4-8
- Message SHA-256: a2c9355177479f23c6c81afe1b39ba697ac131cc344bb83120b98e2c6bbfee49
- Response HTTP status: 200
- Prompt tokens: 15422
- Completion tokens: 6006
- Reasoning tokens: 0
- Total tokens: 21428
- API requests reported: 1
- Elapsed seconds: 139.626
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 957.651
- Question handoff seconds: 970.897
- Final benchmark system: E2seq; file rank 2/5; original repeat 2; model vendor: Anthropic

---
# Multidimensional Interpretation of Prognostic Transcriptomic Results in Lung Adenocarcinoma

## 1. Overall Biological Interpretation

The prognostic transcriptomic signature in this LUAD cohort is dominated by extremely high hazard ratios (HR > 10^6 to 10^21) for the majority of genes, which is statistically and biologically implausible. This pattern strongly suggests **technical artifacts, model instability, or computational errors** rather than genuine biological signal. 

Among the small subset of genes with plausible effect sizes (HR 0.2–1.5), the data suggests:
- **Wnt pathway dysregulation** (DKK1, TLE1, VAX1) associated with poor prognosis
- **Epithelial differentiation programs** (KRT6A, FUT4) linked to adverse outcomes
- **Rho GTPase signaling** (RHOF, RGS20) associated with risk
- **Protective lncRNA expression** (CRNDE, RBMXP1) associated with better survival

The interpretable signal is limited to approximately 30 genes with biologically reasonable hazard ratios. The remainder require fundamental re-analysis before any biological interpretation is warranted.

---

## 2. Core Biological Programs

### Program 1: Wnt Signaling Dysregulation
- **Direction**: Risk-associated  
- **Supporting genes**: DKK1 (HR=1.48, P=4.3×10⁻¹⁰), TLE1 (HR=1.48, P=3.2×10⁻⁸), VAX1 (HR=1.33, P=1.2×10⁻⁸), PITX3 (HR=1.43, P=4.1×10⁻¹⁴)  
- **Pathway**: GO:0030111 Regulation of Wnt Signaling Pathway; KEGG Wnt signaling pathway  
- **Rationale**: DKK1 is a secreted Wnt antagonist that inhibits canonical Wnt signaling through LRP5/6 binding. TLE1 functions as a transcriptional co-repressor in Wnt target gene regulation. VAX1 and PITX3 are homeobox transcription factors involved in developmental Wnt responses. The coordinated prognostic association of multiple nodes in this pathway, spanning extracellular antagonists, nuclear co-repressors, and downstream transcription factors, indicates that Wnt pathway activity state influences LUAD progression.  
- **Evidence strength**: Moderate. Pathway coherence across multiple independent genes supports a program-level interpretation. DKK1 overexpression has been reported in multiple cancer contexts with context-dependent oncogenic or tumor-suppressive roles. The adverse prognostic association here is consistent with some LUAD studies but conflicts with others where DKK1 downregulation correlates with poor outcome.  
- **Limitations**: The mechanism by which increased DKK1 (a Wnt inhibitor) confers poor prognosis remains unclear and may reflect non-canonical functions, tumor microenvironment effects, or subtype-specific biology not captured here.

### Program 2: Epithelial Differentiation and Glycosylation
- **Direction**: Risk-associated  
- **Supporting genes**: KRT6A (HR=1.39, P=4.2×10⁻⁷), FUT4 (HR=1.40, P=4.5×10⁻⁷), LDLRAD3 (HR=1.42, P=3.3×10⁻⁷), RHCG (HR=1.29, P=7.6×10⁻⁷)  
- **Pathway**: KEGG Mannose type O-glycan biosynthesis; GO Cell Junction Disassembly (GO:0150146)  
- **Rationale**: KRT6A is a type II keratin normally expressed in stratified epithelia but aberrantly induced in stress or squamous differentiation contexts in lung. FUT4 (fucosyltransferase 4) synthesizes Lewis antigens and is involved in cell adhesion glycan modifications. LDLRAD3 participates in cell adhesion and lipoprotein uptake. RHCG is an ammonium transporter. The co-occurrence of altered epithelial structural proteins, glycosylation enzymes, and adhesion molecules suggests a shift toward a more differentiated or squamous-like epithelial program, which in LUAD contexts often correlates with worse prognosis.  
- **Evidence strength**: Weak to moderate. KRT6A has documented associations with squamous differentiation and poor prognosis in lung cancer, supported by independent cohort data. FUT4 is implicated in cancer cell adhesion and metastasis. However, the mechanistic link between these genes as a unified program versus independent risk markers is unclear.  
- **Limitations**: KRT6A expression may reflect squamous cell carcinoma contamination or adenosquamous features rather than a true adenocarcinoma subtype. Glycosylation changes are often secondary to other oncogenic drivers.

### Program 3: Rho GTPase Signaling and Cytoskeletal Remodeling
- **Direction**: Risk-associated  
- **Supporting genes**: RHOF (HR=1.40, P=6.3×10⁻⁷), RGS20 (HR=1.35, P=9.5×10⁻⁷)  
- **Pathway**: GO Regulation of small GTPase mediated signal transduction; GO Actin filament organization  
- **Rationale**: RHOF is a Rho family GTPase that regulates filopodia formation, cell migration, and cytoskeletal dynamics. RGS20 is a GTPase-activating protein for Gα(i/z) subunits, modulating G-protein-coupled receptor signaling that feeds into Rho GTPase cascades. STRING interaction evidence links RHOF to actin cytoskeleton regulators (ACTN1, ARHGAP1). Elevated expression of both regulators suggests enhanced migratory or invasive potential.  
- **Evidence strength**: Weak. RHOF has been reported as a prognostic marker in AML and some solid tumors, and one published study identified RHOF as predictive of worse overall survival in non-M3 AML. However, independent validation in LUAD cohorts is lacking in the provided evidence pack. RGS20's role in cancer is minimally characterized.  
- **Limitations**: RHOF and RGS20 may not represent a tightly coupled functional module. Their prognostic association could reflect independent mechanisms or shared upstream regulation rather than direct interaction.

### Program 4: Long Non-Coding RNA Regulatory Landscape
- **Direction**: Mixed (predominantly risk-associated, with notable protective exceptions)  
- **Supporting genes**: CRNDE (HR=0.72, P=1.4×10⁻⁷, protective), ITGB1-DT (HR=1.30, P=2.1×10⁻⁷, risk), LINC01312 (HR=1.36, P=4.3×10⁻⁹, risk), LINC02178 (HR=1.30, P=1.1×10⁻⁸, risk), multiple other LINC genes and pseudogenes  
- **Pathway**: No standard pathway; regulatory RNA network  
- **Rationale**: Multiple lncRNAs show strong prognostic associations. CRNDE (Colorectal Neoplasia Differentially Expressed) is protective, consistent with some prior reports linking higher CRNDE to better differentiation in certain contexts. ITGB1-DT has been reported as a biomarker in breast cancer and validated in LUAD (literature evidence: 34906142, 37690573). The co-occurrence of multiple lncRNA associations suggests that post-transcriptional and epigenetic regulatory layers contribute to LUAD prognosis.  
- **Evidence strength**: Weak. lncRNA annotations are incomplete, and functional mechanisms remain largely unknown. ITGB1-DT has experimental support in LUAD, but most other lncRNAs lack validation.  
- **Limitations**: lncRNA expression often correlates with nearby protein-coding genes or reflects lineage identity rather than causal drivers. The protective association of CRNDE conflicts with its oncogenic role in colorectal cancer, suggesting context-dependent or subtype-specific functions.

### Program 5: **Not Identified**
Fewer than five robust biological programs can be confidently extracted from this dataset given the technical quality concerns and limited pathway coherence among genes with plausible effect sizes.

---

## 3. Key Genes and Interaction Modules

### Gene 1: DKK1 (Dickkopf WNT Signaling Pathway Inhibitor 1)
- **Association**: Risk (HR=1.48, FDR=3.5×10⁻⁷)  
- **Role**: Secreted Wnt antagonist. Functions as an upstream regulator of Wnt pathway activity by binding LRP5/6 co-receptors and preventing Wnt ligand engagement.  
- **Relationship to programs**: Core member of Wnt signaling dysregulation program. Co-expressed with TLE1 (transcriptional co-repressor downstream of Wnt) in pathway co-membership, not direct physical interaction.  

### Gene 2: TLE1 (Transducin-Like Enhancer of Split 1)
- **Association**: Risk (HR=1.48, FDR=2.5×10⁻⁵)  
- **Role**: Transcriptional co-repressor that mediates repression of Wnt target genes via interaction with TCF/LEF transcription factors.  
- **Relationship to programs**: Wnt signaling program. Pathway co-membership with DKK1; no evidence of direct physical interaction provided.  

### Gene 3: KRT6A (Keratin 6A)
- **Association**: Risk (HR=1.39, FDR=2.8×10⁻⁴)  
- **Role**: Type II keratin expressed in stratified epithelia, induced under stress or during squamous differentiation. Marker of basal or squamous-like epithelial states.  
- **Relationship to programs**: Epithelial differentiation program. May indicate adenosquamous features or basal-like LUAD subtype.  

### Gene 4: RHOF (Ras Homolog Family Member F)
- **Association**: Risk (HR=1.40, FDR=4.0×10⁻⁴)  
- **Role**: Rho GTPase regulating filopodia formation, cell migration, and actin dynamics.  
- **Relationship to programs**: Rho GTPase signaling program. STRING evidence shows protein interactions with ACTN1 (actin-binding protein) and ARHGAP1 (Rho GAP), indicating involvement in a cytoskeletal remodeling network.  

### Gene 5: CRNDE (Colorectal Neoplasia Differentially Expressed)
- **Association**: Protective (HR=0.72, FDR=1.0×10⁻⁴)  
- **Role**: Long non-coding RNA with context-dependent oncogenic or tumor-suppressive functions.  
- **Relationship to programs**: lncRNA regulatory landscape. No direct physical or regulatory interactions with other selected genes documented in the evidence pack.  

### Gene 6: ITGB1-DT (ITGB1 Divergent Transcript)
- **Association**: Risk (HR=1.30, FDR=1.5×10⁻⁴)  
- **Role**: Long non-coding RNA near the ITGB1 (integrin beta-1) locus. Literature evidence (34906142, 37690573) supports prognostic role in LUAD and breast cancer, with proposed regulatory effects on ARNTL2.  
- **Relationship to programs**: lncRNA regulatory landscape. May regulate integrin signaling indirectly; no direct interaction evidence.  

### Gene 7: FUT4 (Fucosyltransferase 4)
- **Association**: Risk (HR=1.40, FDR=2.9×10⁻⁴)  
- **Role**: Catalyzes fucosylation of glycan structures, including Lewis antigens involved in cell adhesion and selectin binding.  
- **Relationship to programs**: Epithelial differentiation and glycosylation program. STRING evidence shows pathway co-membership with B3GNT3 and B4GALT1 (other glycosyltransferases), not direct interaction.  

### Gene 8: RGS20 (Regulator of G Protein Signaling 20)
- **Association**: Risk (HR=1.35, FDR=5.8×10⁻⁴)  
- **Role**: GTPase-activating protein for Gα(i/z) subunits, attenuating GPCR signaling.  
- **Relationship to programs**: Rho GTPase signaling program (upstream regulator). STRING evidence shows protein interactions with GNAZ, GNB5, GNAI2 (G-protein subunits), representing direct or co-complex relationships.  

### Gene 9: LDLRAD3 (Low Density Lipoprotein Receptor Class A Domain Containing 3)
- **Association**: Risk (HR=1.42, FDR=2.2×10⁻⁴)  
- **Role**: Transmembrane protein involved in cell adhesion and lipoprotein uptake. STRING evidence links to APP (amyloid precursor protein), likely reflecting pathway co-membership rather than direct interaction.  
- **Relationship to programs**: Epithelial differentiation program.  

### Gene 10: RBMXP1 (RBMX Pseudogene 1)
- **Association**: Protective (HR=0.21, FDR=1.6×10⁻¹⁷)  
- **Role**: Pseudogene of RBMX (RNA-binding motif protein, X-linked). May produce regulatory RNAs or serve as expression marker for underlying genomic context.  
- **Relationship to programs**: No clear program assignment. Strongest prognostic signal among genes with plausible effect sizes, but functional mechanism unknown.  

---

## 4. Validation Priorities

### Priority 1: Technical Artifact Investigation
- **Classification**: Confounding or composition check  
- **Rationale**: The majority of genes (>70) show hazard ratios exceeding 10^6, which is impossible in Cox regression applied to real survival data. This indicates model overfitting, separation issues (zero events in one expression group), or data preprocessing errors. Addressing this is prerequisite to any biological interpretation.  
- **Current evidence**: Statistical implausibility of reported effect sizes.  
- **External evidence**: None of the genes with extreme HRs have biologically plausible mechanistic explanations for such associations.  
- **Next step**: Re-run Cox regression with proper regularization (e.g., penalized Cox), check for zero-variance expression groups, verify covariate scaling, and inspect Kaplan-Meier curves for separation artifacts. Validate in TCGA-LUAD using standardized pipelines.  
- **Conclusion status**: **Established evidence** that technical issues dominate the dataset.  

### Priority 2: Wnt Pathway Role in LUAD Prognosis (DKK1, TLE1)
- **Classification**: Mechanistic hypothesis  
- **Rationale**: Multiple Wnt pathway components show coherent prognostic associations. However, the adverse effect of DKK1 (a Wnt inhibitor) is counterintuitive and requires mechanistic clarification.  
- **Current evidence**: Pathway co-membership across 4 genes (DKK1, TLE1, VAX1, PITX3). DKK1 HR=1.48, P=4.3×10⁻¹⁰.  
- **External evidence**: DKK1's role is context-dependent: some NSCLC studies report oncogenic functions, others tumor-suppressive. No independent LUAD cohort validation provided in the evidence pack.  
- **Next step**: Validate DKK1 and TLE1 prognostic associations in TCGA-LUAD. Perform immunohistochemistry or single-cell RNA-seq to assess cell-type-specific expression (tumor vs. stroma). Functionally test whether DKK1 knockdown/overexpression affects proliferation, migration, or Wnt target gene expression in LUAD cell lines.  
- **Conclusion status**: **Supported hypothesis** (pathway coherence) requiring mechanistic validation.  

### Priority 3: ITGB1-DT as a Prognostic lncRNA Biomarker
- **Classification**: Biomarker  
- **Rationale**: ITGB1-DT shows risk association (HR=1.30, FDR=1.5×10⁻⁴) and has independent literature support in LUAD (PMID 34906142) reporting association with the ARNTL2 axis.  
- **Current evidence**: Statistically significant in the current cohort; external publication validates prognostic relevance.  
- **External evidence**: Published RT-PCR validation in LUAD (34906142). Also identified in breast cancer (37690573).  
- **Next step**: Validate in additional LUAD cohorts (e.g., GEO, CPTAC). Develop qPCR or in-situ hybridization assay for clinical testing. Investigate proposed regulatory relationship with ARNTL2 using RNA pulldown or CRISPR interference.  
- **Conclusion status**: **Supported hypothesis** with partial external validation.  

### Priority 4: RHOF as a Therapeutic Target
- **Classification**: Therapeutic target  
- **Rationale**: RHOF (HR=1.40, FDR=4.0×10⁻⁴) regulates cytoskeletal dynamics and has been proposed as a therapeutic target in AML. If validated in LUAD, Rho GTPase inhibitors could be explored.  
- **Current evidence**: Prognostic association in the current dataset; literature report of adverse prognostic role in AML (PMID 34405015).  
- **External evidence**: No LUAD-specific external cohort validation. Rho GTPase inhibitors exist but are not RHOF-specific.  
- **Next step**: Validate in TCGA-LUAD. Functionally assess RHOF knockdown effects on LUAD cell migration, invasion, and in vivo metastasis. Screen for small-molecule inhibitors or assess feasibility of targeting with RNA-based therapeutics.  
- **Conclusion status**: **Exploratory hypothesis**. The presence of Rho pathway drugs does not constitute evidence that RHOF is an effective target; functional validation is required.  

### Priority 5: Squamous Differentiation (KRT6A) and Histologic Subtyping
- **Classification**: Confounding or composition check  
- **Rationale**: KRT6A (HR=1.39, FDR=2.8×10⁻⁴) is a squamous marker. Its prognostic association may reflect adenosquamous carcinoma contamination or a basal-like LUAD subtype rather than a broadly applicable mechanism.  
- **Current evidence**: Statistically significant in the current dataset.  
- **External evidence**: KRT6A is a known squamous differentiation marker. Elevated expression in "adenocarcinoma" samples may indicate histologic misclassification or adenosquamous features.  
- **Next step**: Stratify survival analysis by histologic subtype. Perform pathology review to identify adenosquamous cases. Compare KRT6A expression across molecular LUAD subtypes (e.g., TCGA clusters). Assess whether the KRT6A association is driven by a small subset of samples.  
- **Conclusion status**: **Supported hypothesis** that KRT6A reflects subtype heterogeneity; potential confounder for adenocarcinoma-specific biology.  

---

## 5. Evidence Grounding

### Evidence Categories Supporting Major Conclusions

| Conclusion | Dataset | Pathway | Interaction | Disease | Expression | Drug | Literature |
|------------|---------|---------|-------------|---------|------------|------|------------|
| Wnt pathway dysregulation | ✓ (4 genes, HR 1.3–1.5) | ✓ (GO:0030111, KEGG) | — | — | ✓ (GTEx) | — | Partial (context-dependent) |
| Epithelial differentiation program | ✓ (4 genes) | ✓ (glycosylation, junction) | ✓ (STRING co-expression) | ✓ (KRT6A squamous marker) | ✓ (GTEx) | — | ✓ (KRT6A in NSCLC) |
| Rho GTPase signaling | ✓ (2 genes) | ✓ (GO actin organization) | ✓ (STRING PPI for RHOF) | ✓ (RHOF in AML) | ✓ (GTEx) | ✓ (Rho inhibitors exist) | ✓ (PMID 34405015) |
| lncRNA regulatory landscape | ✓ (ITGB1-DT, CRNDE) | — | — | — | — | — | ✓ (ITGB1-DT: 34906142, 37690573) |
| Technical artifacts | ✓ (implausible HRs) | — | — | — | — | — | — |

### Independence of Evidence Sources
- **Pathway and interaction databases** (GO, Reactome, STRING, KEGG) often derive from overlapping literature curation and are not independent.
- **Disease-association evidence** (OpenTargets, ClinVar) aggregates GWAS and literature but does not provide independent prognostic validation for this cohort.
- **Literature records** (PubMed, Europe PMC) for ITGB1-DT and RHOF represent genuinely independent prior studies.
- **Expression evidence** (GTEx) confirms that most genes with plausible effect sizes are expressed in lung tissue, but does not validate prognostic associations.

### Conflicting Evidence
- **DKK1**: Its role as a Wnt inhibitor predicts tumor-suppressive function, but the adverse prognostic association here suggests oncogenic activity. Literature reports both possibilities depending on cancer type and microenvironment context.
- **CRNDE**: Protective association (HR=0.72) in this LUAD cohort conflicts with oncogenic roles reported in colorectal cancer.

### Insufficient Evidence
- No independent cohort validation was provided for any gene in the evidence pack.
- Protein-protein interaction evidence (STRING) does not distinguish direct physical binding from co-complex membership or co-expression.
- Drug availability (e.g., Rho inhibitors) does not constitute evidence of therapeutic efficacy in LUAD.

---

## 6. Limitations and Alternative Explanations

### Limitation 1: Model Instability and Separation Artifacts
The majority of genes exhibit hazard ratios exceeding 10^6, which is statistically impossible in standard Cox regression. This likely results from **perfect or near-perfect separation** in survival outcomes between expression groups, causing numerical instability. Genes with zero events in one expression category will produce infinite or undefined hazard ratios. This is a fundamental model failure, not a biological finding.

**Investigation**: Inspect event counts within expression tertiles/quartiles for each gene. Apply penalized Cox regression (ridge or elastic net) to stabilize estimates. Verify that continuous expression values, not discretized groups, are used if appropriate.

### Limitation 2: Tumor Purity and Stromal Contamination
Several prognostic genes (DKK1, KRT6A, LDLRAD3) may be expressed in stromal or immune cells rather than tumor epithelium. DKK1 is secreted and may reflect cancer-associated fibroblast activity. KRT6A could arise from stromal squamous metaplasia. If tumor purity varies systematically with survival, stromal gene expression could appear prognostic without reflecting tumor-intrinsic biology.

**Investigation**: Adjust for tumor purity using ESTIMATE, InfiniumPurify, or similar methods. Perform cell-type deconvolution (e.g., CIBERSORTx) to identify cell-type-specific expression patterns. Validate candidate genes using single-cell RNA-seq or spatial transcriptomics to confirm tumor cell expression.

### Limitation 3: Histologic Subtype Heterogeneity
KRT6A's strong association suggests adenosquamous carcinoma or basaloid LUAD contamination. If the cohort includes mixed histologic subtypes, prognostic associations may reflect subtype rather than generalizable adenocarcinoma biology. Similarly, genes like PITX3 and VAX1 (developmental transcription factors) may be active only in specific molecular subtypes.

**Investigation**: Stratify by histologic diagnosis (adenocarcinoma vs. adenosquamous vs. large cell). Assess whether candidate gene associations remain significant after excluding non-adenocarcinoma cases. Compare expression across TCGA molecular subtypes (proximal-inflammatory, terminal respiratory unit, proximal-proliferative).

### Limitation 4: Treatment Exposure and Selection Bias
If patients with specific gene expression patterns were preferentially treated with certain therapies (e.g., targeted therapy, immunotherapy), survival differences could reflect treatment effects rather than intrinsic tumor biology. For example, if high DKK1 tumors are less responsive to immunotherapy, the adverse prognosis could be treatment-mediated.

**Investigation**: Stratify analyses by treatment received (surgery-only, chemotherapy, targeted therapy, immunotherapy). Perform interaction testing to assess whether gene associations differ across treatment groups. If treatment data are unavailable, acknowledge this as an uncontrolled confounder.

### Limitation 5: Association vs. Causation
All identified associations are correlative. For example, DKK1 expression may be a consequence of tumor progression (e.g., hypoxia-induced) rather than a driver. Similarly, lncRNA associations may reflect nearby protein-coding gene regulation or genomic context rather than causal lncRNA function.

**Investigation**: Functional experiments (gain/loss-of-function) are required to establish causality. For prioritized candidates (DKK1, ITGB1-DT, RHOF), perform in vitro and in vivo studies to assess effects on proliferation, migration, and survival. For lncRNAs, use CRISPR activation/interference to distinguish cis-regulatory effects from trans-acting functions.

---

## Summary

This LUAD prognostic signature is dominated by technical artifacts that preclude interpretation of most genes. Among the minority of genes with biologically plausible effect sizes, Wnt pathway dysregulation, epithelial differentiation shifts, and Rho GTPase signaling emerge as potential prognostic programs. However, these findings lack independent cohort validation and require careful consideration of tumor purity, histologic heterogeneity, and treatment effects. Immediate priority is technical validation and artifact correction before advancing biological hypotheses. ITGB1-DT and RHOF represent the most promising candidates for further investigation based on external literature support, but functional validation remains essential.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=37, external claims checked=0, external mismatches=0, status=passed.

Answer model API: Anthropic / claude-opus-4-8

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 53/100 selected items (records returned); cbioportal 51/100 selected items (records returned); chembl 16/100 selected items (records returned); civic 1/100 selected items (records returned); clinicaltrials 6/100 selected items (records returned); clinvar 30/100 selected items (records returned); ensembl 11/100 selected items (partially returned; some queries failed); europepmc 362 articles / initial full-cohort RAG 100 queries + 4 current-round queries; some queries failed; gtex 81/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 14/100 selected items (records returned); humanbase 56/100 selected items (partially returned; some queries failed); intact 18/100 selected items (records returned); mygene 59/100 selected items (records returned); omnipath 3/100 selected items (records returned); opentargets 55/100 selected items (records returned); pubmed 202 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 17/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 17/100 selected items (records returned)
Local databases: gutmgene 0/100 selected items (reachable but no records for this batch); hmdb 2/100 selected items (records returned); string 14/100 selected items (records returned); trrust 4/100 selected items (records returned)
