# ulcerative colitis (UC) - deepseek-v4-flash

- Benchmark system: E2seq + Agent RAG
- Repeat: 6
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
- Model API: DeepSeek / deepseek-v4-flash
- Message SHA-256: 478acec7ab00f0e9bda085b6ecab7aa16a2bc8aa5cde3f2ba8fb71b2af94f79a
- Response HTTP status: 200
- Prompt tokens: 49623
- Completion tokens: 18641
- Reasoning tokens: 0
- Total tokens: 68264
- API requests reported: 4
- Elapsed seconds: 97.145
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 1095.213
- Question handoff seconds: 1109.559
- Final benchmark system: E2seq; file rank 4/5; original repeat 6; model vendor: DeepSeek

---
# Multidimensional Interpretation of Ulcerative Colitis Colonic Mucosal Transcriptomics

## 1. Overall Biological Interpretation

The dataset comprises 100 unique genes (60 downregulated, 40 upregulated) with extremely strong statistical support (all FDR < 4×10⁻¹⁰), comparing colonic mucosal tissue from ulcerative colitis (UC) patients versus healthy controls. The transcriptomic landscape reveals a coherent picture of active mucosal inflammation with concurrent loss of normal epithelial differentiation and absorptive function.

The dominant themes are: (1) a robust innate immune and inflammatory response with neutrophil chemoattraction (CXCL1, CXCL2, CXCL3, S100A8, LCN2, CHI3L1, MMP3); (2) profound loss of differentiated colonocyte identity, reflected in downregulation of water channels (AQP7, AQP8), solute transporters (SLC16A1, SLC51A, SLC23A1, SLC23A3), and metabolic enzymes (HMGCS2, CYP2B6, ABCG2); (3) activation of epithelial stress/repair programs (DUOX2/DUOXA2, TGM2, TNC, REG4, CDH3); and (4) immune-regulatory feedback (CTLA4, SOCS3, IL1RN, IRAK3). These patterns are consistent with the established pathophysiology of UC involving epithelial barrier dysfunction, oxidative stress, and neutrophil-dominated inflammation, but the data also point toward a significant epithelial metabolic and differentiation collapse that may be underappreciated in simpler models of the disease.

## 2. Core Biological Programs

### Program 1: Neutrophil Chemotaxis and Innate Inflammatory Amplification
- **Direction**: Upregulated
- **Supporting genes**: CXCL1 (log2FC=3.46), CXCL2 (2.80), CXCL3 (2.33), S100A8 (3.80), LCN2 (2.67), CHI3L1 (4.59), MMP3 (4.64), S100P (1.77), VNN1 (3.20)
- **Standardized pathway**: KEGG IL-17 signaling pathway; Hallmark Inflammatory Response; Reactome Chemokine receptors bind chemokines
- **Explanation**: The coordinated upregulation of CXCL1/2/3 (all ligands for CXCR2) alongside S100A8 (calprotectin subunit) and LCN2 (NGAL) indicates active neutrophil recruitment and activation. MMP3 and CHI3L1 reflect matrix remodeling and macrophage/neutrophil activity. The STRING network evidence identifies CXCR2 as a hub connecting CXCL1, CXCL2, and CXCL3 (pathway co-membership/ligand-receptor relationship, not direct physical interaction among the ligands themselves).
- **Evidence strength**: Strong. Multiple independent genes with very low FDRs; the pattern is biologically coherent and consistent with the well-documented neutrophilic infiltrate of active UC. **Limitation**: These genes are also upregulated in other inflammatory conditions; the signal is not UC-specific.

### Program 2: Loss of Differentiated Colonocyte Identity and Absorptive/Secretory Function
- **Direction**: Downregulated
- **Supporting genes**: AQP8 (log2FC=−4.42), AQP7 (−2.32), SLC51A (−3.71), SLC16A1 (−2.38), SLC23A1 (−2.40), SLC23A3 (−1.93), ABCG2 (−2.92), ABCB11 (−1.15), G6PC (−1.52), MEP1B (−2.99)
- **Standardized pathway**: GO Fluid Transport (GO:0042044); GO Water Transport (GO:0006833); KEGG Bile Secretion
- **Explanation**: The dramatic downregulation of water channels (AQP7, AQP8) and multiple solute carriers indicates loss of differentiated absorptive epithelium. AQP8 is a key colonic water channel; its near-complete loss (log2FC=−4.42) is striking. The concurrent downregulation of bile acid transporters (SLC51A, ABCB11) and xenobiotic efflux pumps (ABCG2) suggests impaired epithelial detoxification and bile acid handling. MEP1B (meprin A metallopeptidase) loss further indicates brush-border enzyme deficiency.
- **Evidence strength**: Strong. Multiple independent transporter genes with very low FDRs; the pattern is coherent and consistent with the epithelial dedifferentiation seen in UC. **Limitation**: Some of this signal may reflect loss of surface epithelium and goblet cells due to ulceration (composition effect), not just transcriptional reprogramming of remaining cells.

### Program 3: Epithelial Oxidative Stress Response and DUOX2-Mediated ROS Production
- **Direction**: Upregulated
- **Supporting genes**: DUOX2 (log2FC=4.67), DUOXA2 (2.89), TRIM29 (2.83), SLC6A14 (4.85), TGM2 (1.91), REG4 (2.05)
- **Standardized pathway**: Reactome Detoxification of Reactive Oxygen Species; GO Response to oxidative stress
- **Explanation**: DUOX2 (dual oxidase 2) and its maturation factor DUOXA2 are strongly induced, indicating active epithelial ROS production—a hallmark of IBD mucosa. TRIM29, an E3 ligase implicated in DNA damage responses and epithelial defense, is co-induced. SLC6A14 (amino acid transporter) is among the most strongly upregulated genes and has been repeatedly associated with IBD, particularly in the context of epithelial stress responses. TGM2 (tissue transglutaminase) supports epithelial remodeling and barrier fortification.
- **Evidence strength**: Strong for the DUOX2/DUOXA2 pair and SLC6A14. **Limitation**: The functional relationship among these genes (whether TRIM29, SLC6A14, and DUOX2 are co-regulated by shared transcription factors or interact physically) is not established by this dataset; pathway co-membership is inferred, not demonstrated.

### Program 4: Immune Checkpoint and Negative-Feedback Regulation
- **Direction**: Upregulated
- **Supporting genes**: CTLA4 (log2FC=2.62), SOCS3 (2.79), IL1RN (2.88), IRAK3 (1.78), DAPP1 (2.20), CD55 (2.04)
- **Standardized pathway**: Reactome Regulation of innate immune responses; GO Negative regulation of immune response
- **Explanation**: The co-induction of CTLA4 (T-cell checkpoint), SOCS3 (suppressor of cytokine signaling), IL1RN (IL-1 receptor antagonist), and IRAK3 (negative regulator of TLR/IL-1 signaling) indicates active engagement of negative-feedback loops that limit excessive inflammation. This is consistent with the concept that UC mucosa is not simply pro-inflammatory but is in a state of attempted immune resolution. CD55 (decay-accelerating factor) protects against complement-mediated damage.
- **Evidence strength**: Moderate-to-strong. Multiple genes with coherent function; however, these genes are expressed by different cell types (CTLA4 by T cells; SOCS3, IRAK3 by myeloid/epithelial cells), so the signal may reflect mixed cell populations rather than a single coordinated program. **Limitation**: The cell-type heterogeneity of mucosal biopsies complicates interpretation.

### Program 5: Suppression of Epithelial Metabolic and Biosynthetic Capacity
- **Direction**: Downregulated
- **Supporting genes**: HMGCS2 (log2FC=−3.45), CYP2B6 (−2.78), CYP2B7P (−2.72), GBA3 (−3.00), HSD3B2 (−2.77), ETNK1 (−1.58), ACSF2 (−1.93), LIPC (−1.57), SDR16C5 (upregulated, +1.74)
- **Standardized pathway**: KEGG Bile secretion; Reactome Metabolism; GO Lipid metabolic process
- **Explanation**: The marked downregulation of HMGCS2 (ketogenesis enzyme), CYP2B6/CYP2B7P (xenobiotic metabolism), GBA3 (glycosylceramidase), and HSD3B2 (steroid metabolism) indicates collapse of colonocyte metabolic specialization. In contrast, SDR16C5 (retinoic acid biosynthesis) is upregulated, suggesting a shift toward retinoid signaling that may drive epithelial differentiation or repair. This metabolic remodeling is likely both a consequence of inflammation and a contributor to impaired barrier function.
- **Evidence strength**: Moderate. The genes are individually highly significant, and the pattern is coherent, but the functional consequences of this metabolic shift in UC are less well established than the inflammatory program. **Limitation**: Some of this signal may reflect loss of differentiated epithelial cells rather than active metabolic reprogramming.

## 3. Key Genes and Interaction Modules

### 1. SLC6A14 (upregulated, log2FC=4.85, FDR=8.07×10⁻³⁹)
- **Role**: Among the strongest signals in the dataset; SLC6A14 encodes a sodium/chloride-dependent neutral and basic amino acid transporter. It has been repeatedly associated with IBD susceptibility (GWAS) and is induced by inflammatory cytokines in intestinal epithelium.
- **Interaction nature**: No direct physical interaction evidence from this dataset; its co-induction with DUOX2/TRIM29 suggests pathway co-membership in an epithelial stress response, but this is a hypothesis, not a demonstrated interaction.

### 2. DUOX2/DUOXA2 module (both upregulated, log2FC=4.67 and 2.89)
- **Role**: DUOX2 is the epithelial NADPH oxidase that generates H₂O₂ for antimicrobial defense; DUOXA2 is its maturation factor. This module represents the oxidative burst of inflamed colonic epithelium.
- **Interaction nature**: Direct physical interaction is well documented (DUOXA2 is required for DUOX2 maturation and trafficking to the plasma membrane)—this is established from the literature, not from this dataset.

### 3. CXCL1/CXCL2/CXCL3 chemokine module (all upregulated)
- **Role**: Neutrophil chemoattractants signaling through CXCR2. STRING evidence places them as ligands of CXCR2 (pathway co-membership/ligand-receptor relationship).
- **Interaction nature**: These three chemokines share a receptor (CXCR2) and are co-regulated; they are not known to physically interact with each other. Their co-expression reflects shared transcriptional regulation (likely NF-κB and IL-17 signaling).

### 4. S100A8/S100P/LCN2 module (all upregulated)
- **Role**: S100A8 (calprotectin subunit), S100P, and LCN2 (NGAL) are damage-associated molecular patterns and antimicrobial peptides released by neutrophils and stressed epithelium. S100A8 forms a heterodimer with S100A9 (calprotectin)—a clinical fecal biomarker for IBD.
- **Interaction nature**: S100A8/S100A9 heterodimerization is a direct physical interaction (well established). S100A8 and LCN2 are co-expressed in neutrophils but do not directly interact; their co-upregulation reflects shared cellular origin.

### 5. AQP8 (downregulated, log2FC=−4.42)
- **Role**: The most strongly downregulated gene; AQP8 is the major colonic water channel. Its loss likely contributes to diarrhea, a cardinal symptom of UC. Reactome places it in passive water transport pathways.
- **Interaction nature**: No interaction module; its downregulation is best interpreted as a marker of lost differentiated colonocyte identity.

### 6. MMP3 (upregulated, log2FC=4.64)
- **Role**: Matrix metalloproteinase 3; degrades extracellular matrix and contributes to mucosal ulceration. Co-upregulated with TIMP1 (1.97), its inhibitor, suggesting an active remodeling balance.
- **Interaction nature**: TIMP1 directly inhibits MMP3 enzymatic activity (direct physical interaction at the protein level, well documented). Their co-upregulation in the dataset is consistent with this regulatory relationship.

### 7. CTLA4 (upregulated, log2FC=2.62)
- **Role**: T-cell checkpoint receptor; its upregulation in UC mucosa indicates active T-cell regulation. This is notable because CTLA4 is the target of ipilimumab (cancer immunotherapy), and CTLA4 blockade can trigger immune-related colitis—a clinical observation that links this gene to colonic immune regulation.
- **Interaction nature**: No direct interaction with other selected genes; its upregulation reflects infiltrating regulatory T cells (composition effect likely).

### 8. TGM2 (upregulated, log2FC=1.91)
- **Role**: Tissue transglutaminase; cross-links proteins to stabilize the extracellular matrix and epithelial barrier. STRING evidence connects TGM2 with TNC and FREM2 through ITGB1 (integrin β1) as a network hub—this is pathway co-membership, not necessarily direct physical interaction.
- **Interaction nature**: TGM2 can cross-link TNC (tenascin C, also upregulated, log2FC=2.58) in the extracellular matrix; this is a plausible direct enzymatic interaction, but it is not demonstrated in this dataset.

### 9. SOCS3 (upregulated, log2FC=2.79)
- **Role**: Suppressor of cytokine signaling 3; negative regulator of JAK-STAT signaling. Its upregulation indicates active feedback inhibition of cytokine signaling, likely in response to IL-6/IL-23 pathway activation.
- **Interaction nature**: SOCS3 directly binds JAK2 and cytokine receptors to inhibit signaling (direct physical interaction, well established); this is inferred from the literature, not from this dataset.

### 10. HMGCS2 (downregulated, log2FC=−3.45)
- **Role**: Mitochondrial HMG-CoA synthase; rate-limiting enzyme for ketogenesis. Its downregulation indicates loss of colonocyte metabolic specialization (colonocytes use butyrate and ketone bodies as fuel).
- **Interaction nature**: No interaction module; its loss is a marker of metabolic reprogramming.

## 4. Validation Priorities

### Priority 1: Cell-Type Deconvolution and Composition Adjustment
- **Classification**: Confounding or composition check
- **Rationale**: Mucosal biopsies contain epithelium, immune cells, stroma, and vasculature. The "loss of differentiated colonocyte identity" program (AQP8, SLC51A, HMGCS2 downregulation) could reflect either transcriptional repression or physical loss of surface epithelium due to ulceration. Conversely, CTLA4 and S100A8 upregulation may reflect increased T-cell and neutrophil infiltration, not transcriptional changes in resident cells.
- **Current dataset evidence**: Directional signals are extremely strong, but cannot distinguish composition from cell-intrinsic changes.
- **External evidence**: Single-cell RNA-seq studies of UC have shown both epithelial cell loss and cell-intrinsic transcriptional changes (e.g., DUOX2 induction in remaining epithelial cells).
- **Next step**: Perform cell-type deconvolution (e.g., CIBERSORTx, MuSiC) using a UC-specific single-cell reference; validate with immunohistochemistry for AQP8, DUOX2, and CD68/CD3 markers.
- **Conclusion status**: The composition effect is a **supported hypothesis** that must be tested; the raw differential expression is **established evidence** for the cohort.

### Priority 2: DUOX2/DUOXA2 Oxidative Stress Axis as a Mechanistic Driver
- **Classification**: Mechanistic hypothesis
- **Rationale**: DUOX2 is the most strongly induced oxidase and is known to be induced by IFN-γ and TNF-α in intestinal epithelium. Its product, H₂O₂, can drive both antimicrobial defense and tissue damage. Understanding whether DUOX2 activity is protective (antimicrobial) or pathogenic (tissue damage) is critical.
- **Current dataset evidence**: DUOX2 and DUOXA2 are both strongly upregulated (FDR < 10⁻¹⁰); co-induction of TRIM29 and SLC6A14 suggests a coordinated epithelial stress program.
- **External evidence**: DUOX2 is consistently upregulated in IBD mucosa in multiple published cohorts; DUOX2 loss-of-function mutations are associated with very early onset IBD (genetic evidence).
- **Next step**: Use organoid or patient-derived epithelial models to test whether DUOX2 inhibition reduces or exacerbates epithelial damage; measure ROS production and barrier integrity.
- **Conclusion status**: **Supported hypothesis**—the association is established, but causality and therapeutic directionality require functional testing.

### Priority 3: SLC6A14 as a Biomarker and Potential Therapeutic Target
- **Classification**: Biomarker (with therapeutic target potential)
- **Rationale**: SLC6A14 is the most strongly upregulated gene in this dataset (log2FC=4.85, FDR=8×10⁻³⁹) and has been identified as an IBD risk gene in GWAS. Its protein product transports amino acids and is expressed on the apical surface of intestinal epithelium.
- **Current dataset evidence**: Single strongest signal in the cohort.
- **External evidence**: GWAS associations (SLC6A14 is near the IL23R locus and has been independently associated with IBD in multiple studies); published UC transcriptomic studies consistently show SLC6A14 upregulation. However, **external statistical validation in an independent cohort was not performed** in this analysis.
- **Next step**: Validate SLC6A14 protein expression by immunohistochemistry in an independent UC cohort; test whether SLC6A14 inhibition alters epithelial amino acid uptake and inflammatory responses in organoids.
- **Conclusion status**: **Supported hypothesis** for biomarker utility; therapeutic targeting remains **exploratory**.

### Priority 4: CXCL1/CXCL2/CXCL3–CXCR2 Axis as a Therapeutic Target
- **Classification**: Therapeutic target
- **Rationale**: The coordinated upregulation of all three CXCR2 ligands indicates active neutrophil recruitment. CXCR2 antagonists have been developed for inflammatory diseases and could be repurposed for UC.
- **Current dataset evidence**: CXCL1 (3.46), CXCL2 (2.80), CXCL3 (2.33) all strongly upregulated; STRING evidence places CXCR2 as the shared receptor.
- **External evidence**: Neutrophil infiltration is a hallmark of active UC; CXCR2 blockade reduces colitis in mouse models. **However, drug availability does not constitute evidence of efficacy in UC.**
- **Next step**: Test CXCR2 antagonist in a preclinical colitis model with measurement of neutrophil infiltration and mucosal healing; assess whether the effect is additive to standard-of-care (e.g., anti-TNF).
- **Conclusion status**: **Exploratory hypothesis**—the target is biologically plausible but requires preclinical efficacy data.

### Priority 5: AQP8 Restoration as a Marker of Epithelial Recovery
- **Classification**: Biomarker
- **Rationale**: AQP8 is the most strongly downregulated gene (log2FC=−4.42) and its loss likely contributes to diarrhea. Monitoring AQP8 expression could serve as a marker of epithelial differentiation and mucosal healing.
- **Current dataset evidence**: AQP8 is dramatically downregulated; AQP7 (−2.32) is also reduced.
- **External evidence**: AQP8 downregulation has been reported in UC and in mouse models of colitis; its restoration correlates with epithelial recovery.
- **Next step**: Measure AQP8 mRNA and protein in serial biopsies from UC patients undergoing therapy to determine whether AQP8 recovery predicts clinical remission.
- **Conclusion status**: **Exploratory hypothesis**—requires longitudinal validation.

## 5. Evidence Grounding

| Interpretation | Direct dataset evidence | Pathway/ontology | Protein interaction/regulatory | Disease-association | Expression/tissue | Genetic/clinical | Drug/therapeutic | Literature |
|---|---|---|---|---|---|---|---|---|
| Neutrophil chemotaxis program | Strong (CXCL1/2/3, S100A8, LCN2) | KEGG IL-17; Hallmark Inflammatory Response | CXCR2 hub (STRING) | Consistent with UC neutrophilia | Consistent with known biology | — | CXCR2 antagonists exist (not evidence of UC efficacy) | Multiple UC transcriptomic studies |
| Loss of colonocyte identity | Strong (AQP8, SLC51A, HMGCS2) | GO Water/Fluid Transport; KEGG Bile Secretion | — | Reported in UC | Consistent with colonocyte biology | — | — | Published UC mucosal transcriptomics |
| DUOX2 oxidative stress | Strong (DUOX2, DUOXA2) | Reactome ROS detoxification | DUOXA2-DUOX2 direct interaction (established) | DUOX2 in IBD | Epithelial expression | DUOX2 mutations in VEO-IBD | — | Multiple IBD studies |
| Immune checkpoint/feedback | Strong (CTLA4, SOCS3, IL1RN) | GO Negative regulation of immune response | SOCS3-JAK direct interaction (established) | CTLA4 in immune-mediated colitis | T-cell/myeloid expression | CTLA4 blockade causes colitis (clinical) | Ipilimumab (not evidence for UC therapy) | Literature on immune regulation in IBD |
| Metabolic collapse | Strong (HMGCS2, CYP2B6, GBA3) | KEGG Bile secretion; Reactome Metabolism | — | Less established | Colonocyte-specific | — | — | Emerging evidence for metabolic remodeling in IBD |

**Independence of evidence sources**: The pathway annotations (Reactome, KEGG, GO), protein interaction databases (STRING, IntAct), and literature records may share underlying publications and prediction models. They are therefore not fully independent. The GWAS, ClinVar, and expression-tissue records (GTEx, HPA) are more likely to be independent, but even these may share cohort data. The only truly independent evidence in this analysis is (a) the uploaded differential expression statistics and (b) any external cohort statistics, which were **not available** for this analysis.

## 6. Limitations and Alternative Explanations

### Limitation 1: Tissue and Cell-Composition Differences
The most important confounder. Mucosal biopsies in active UC contain variable proportions of epithelium, inflammatory infiltrate, granulation tissue, and stroma. The "loss of colonocyte identity" program could be driven by epithelial loss rather than transcriptional repression. Conversely, immune cell marker upregulation (CTLA4, S100A8) may reflect infiltration rather than cell-intrinsic activation.
**How to address**: Single-cell RNA-seq or deconvolution; immunohistochemistry for key markers (AQP8, DUOX2, CD3, MPO).

### Limitation 2: Disease Severity and Treatment Exposure
The dataset does not specify disease severity (Mayo score, endoscopic activity) or treatment status. Patients on anti-TNF, vedolizumab, or corticosteroids would have different transcriptomic profiles. The extreme effect sizes (e.g., SLC6A14 log2FC=4.85) suggest active, untreated or treatment-refractory disease, but this cannot be confirmed.
**How to address**: Stratify by clinical phenotype and treatment; report endoscopic activity scores.

### Limitation 3: Association Versus Causation
This is a cross-sectional case-control comparison. All genes are differentially expressed, but none can be assigned a causal role from this design. The DUOX2 oxidative stress program could be protective (antimicrobial) or pathogenic (tissue damage); the immune checkpoint program could represent failed resolution or active suppression.
**How to address**: Functional perturbation studies (organoids, mouse models); Mendelian randomization where genetic instruments exist.

### Limitation 4: Batch and Platform Effects
The presence of probe IDs (PROBE_241592_PM_at, PROBE_227140_PM_at, PROBE_235105_PM_at) indicates an Affymetrix microarray platform. Batch effects, array version, and normalization choices can influence results. The ledger notes 43 duplicated genes/probes, and several genes have multiple rows (e.g., SLC16A1 rows=5, ETNK1 rows=7), which may reflect probe redundancy or annotation ambiguity.
**How to address**: Confirm with qPCR or RNA-seq in a subset; report array version and batch correction methods.

### Limitation 5: Broad Nonspecific Pathway Signals
The "inflammatory response" and "epithelial stress" programs are not UC-specific; they are shared with Crohn's disease, infectious colitis, and other inflammatory conditions. The absence of a healthy control comparison with another inflammatory bowel condition limits the ability to identify UC-specific signatures.
**How to address**: Include Crohn's disease and infectious colitis comparator groups; perform supervised classification to identify UC-specific gene signatures.

## Summary

This dataset provides extremely robust statistical evidence (FDR < 4×10⁻¹⁰ for all 100 genes) for a coordinated transcriptomic response in UC mucosa characterized by: (1) neutrophil chemotaxis and innate inflammation, (2) loss of differentiated colonocyte absorptive/secretory function, (3) epithelial oxidative stress with DUOX2 activation, (4) immune checkpoint/negative-feedback engagement, and (5) metabolic collapse. The most defensible interpretations are the neutrophil chemotaxis program and the loss of colonocyte identity, both supported by multiple independent genes with coherent biology. The DUOX2 oxidative stress axis and SLC6A14 represent high-value targets for mechanistic follow-up. External statistical validation in an independent cohort was not performed, and the results must be interpreted with the caveat that tissue composition, disease severity, treatment exposure, and platform effects could influence the findings. The data support hypothesis generation and targeted validation, not causal conclusions.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=14, external claims checked=0, external mismatches=0, status=needs review.

Answer model API: deepseek / deepseek-v4-flash.

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 94/100 selected items (records returned); cbioportal 87/100 selected items (records returned); chembl 40/100 selected items (partially returned; some queries failed); civic 7/100 selected items (records returned); clinicaltrials 51/100 selected items (records returned); clinvar 90/100 selected items (records returned); ensembl 55/100 selected items (partially returned; some queries failed); europepmc 936 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 91/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 85/100 selected items (records returned); humanbase 87/100 selected items (records returned); intact 85/100 selected items (records returned); mygene 93/100 selected items (records returned); omnipath 45/100 selected items (records returned); opentargets 92/100 selected items (records returned); pubmed 750 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 87/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 88/100 selected items (records returned)
Local databases: gutmgene 8/100 selected items (records returned); hmdb 46/100 selected items (records returned); string 85/100 selected items (records returned); trrust 31/100 selected items (records returned)
