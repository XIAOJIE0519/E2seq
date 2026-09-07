# idiopathic pulmonary fibrosis (IPF) - claude-opus-4-8

- Benchmark system: E2seq + Agent RAG
- Repeat: 6
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
- Model API: Anthropic / claude-opus-4-8
- Message SHA-256: d9fe74e971569d03f1ace047ce334e08d788b93d2057913b4d42b34da6d57d2f
- Response HTTP status: 200
- Prompt tokens: 26774
- Completion tokens: 8971
- Reasoning tokens: 0
- Total tokens: 35745
- API requests reported: 2
- Elapsed seconds: 155.788
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 1387.824
- Question handoff seconds: 1401.194
- Final benchmark system: E2seq; file rank 4/5; original repeat 6; model vendor: Anthropic

---
# Transcriptomic Analysis of Idiopathic Pulmonary Fibrosis Prognosis

## 1. Overall Biological Interpretation

This prognostic transcriptomic signature from IPF lung tissue reveals a predominant risk profile characterized by abnormal epithelial differentiation, sustained inflammatory signaling, and extracellular matrix remodeling. The cohort includes 93 risk-associated genes (HR > 1) versus only 7 protective-associated genes, indicating that increased expression of most identified transcripts correlates with worse all-cause mortality.

The signature centers on aberrant epithelial cell states—particularly alveolar type 2 (AT2) cell dysfunction and markers of epithelial-to-mesenchymal transition—alongside persistent neutrophil and monocyte activation. Several genes implicate growth factor signaling pathways (HGF/MET, NRG1) and membrane transporters (SLC family members), suggesting metabolic reprogramming and altered tissue microenvironment contribute to disease progression. The extreme hazard ratios for some genes (CONTROL probes, microRNAs, and lincRNAs with HR values approaching 10^21 or 10^-22) indicate probable data artifacts or platform-specific technical issues; these are excluded from biological interpretation.

## 2. Core Biological Programs

### Program 1: Aberrant Epithelial Differentiation and AT2 Cell Dysfunction
**Direction:** Risk-associated  
**Major supporting genes:** SFTPB (HR=2.66), SLC34A2 (HR=2.27), SFTA2 (HR=2.25), AGR3 (HR=2.40), MUC1 (HR=2.32), CEACAM6 (HR=2.66), CEACAM7 (HR=2.31)  
**Pathway context:** Surfactant metabolism (Reactome), Epithelial cell signaling (KEGG)  

**Rationale:** SFTPB and SFTA2 encode surfactant-associated proteins normally restricted to AT2 cells, while SLC34A2 is the sodium-phosphate cotransporter essential for surfactant phospholipid homeostasis. Their elevated expression as risk factors suggests AT2 cell stress or dysregulated differentiation rather than normal physiological function. AGR3, a protein disulfide isomerase involved in mucin processing, alongside MUC1 and CEACAM family members, indicates goblet cell metaplasia or aberrant mucin production—features atypical for normal distal lung epithelium. This collective pattern points to loss of normal alveolar identity and adoption of proximal airway-like or secretory phenotypes.

**Evidence strength:** Strong pathway coherence and tissue-specific context. Multiple independent genes converge on epithelial differentiation. Limitation: expression changes could reflect altered cell composition (increased AT2 proportions in fibrotic regions) rather than per-cell transcriptional reprogramming.

### Program 2: Sustained Neutrophil and Monocyte Activation
**Direction:** Risk-associated  
**Major supporting genes:** S100A12 (HR=2.53), S100A14 (HR=2.57), CXCL1 (HR=2.99), CCL7 (HR=3.02), CXCR1 (HR=3.28), CD177 (HR=2.72), SELL (HR=2.38), STEAP4 (HR=3.03)  
**Pathway context:** Neutrophil degranulation (GO:1990266), Chemokine signaling (KEGG), RAGE receptor signaling (Reactome)  

**Rationale:** S100A12 and S100A14 are calgranulins released during neutrophil and monocyte activation, functioning as damage-associated molecular patterns (DAMPs) that amplify inflammation via RAGE and TLR4. CXCL1 and CCL7 are chemokines recruiting neutrophils and monocytes, while CXCR1 is the receptor for CXCL1. CD177 and SELL (L-selectin) are neutrophil surface markers. STEAP4, a metalloreductase induced during myeloid cell activation, completes this module. The coordinate upregulation of ligands, receptors, activation markers, and effector molecules indicates active neutrophil/monocyte infiltration and sustained innate immune signaling.

**Evidence strength:** STRING network analysis confirms direct interactions (S100A12–AGER confidence 0.999; S100A12–TLR4 confidence 0.970). Multiple independent genes across ligand-receptor-effector axis. Limitation: cannot distinguish whether these cells drive fibrosis progression or accumulate secondary to tissue injury.

### Program 3: Growth Factor Receptor Signaling and Epithelial Proliferation
**Direction:** Risk-associated  
**Major supporting genes:** HGF (HR=2.93), MET (HR=2.53), NRG1 (HR=2.76), HTRA1 (HR=4.30), SPRY2 (HR=3.26), EFEMP1 (HR=2.33), BMP6 (HR=3.04)  
**Pathway context:** MET receptor signaling, EGFR-related pathways (inferred from network), TGF-β superfamily  

**Rationale:** HGF and its receptor MET constitute a major epithelial regeneration pathway, typically promoting alveolar repair after injury. NRG1, an EGFR family ligand, similarly drives epithelial proliferation. Their elevation as risk factors suggests aberrant or futile activation in progressive fibrosis. HTRA1, a secreted serine protease that degrades TGF-β family members and matrix proteins, may represent a failed counter-regulatory response. SPRY2, an inhibitor of receptor tyrosine kinase signaling, paradoxically shows risk association, possibly reflecting compensatory feedback. EFEMP1 and BMP6, both ECM-associated TGF-β superfamily modulators, link growth factor signaling to matrix remodeling. STRING analysis places EFEMP1, HGF, MET, MUC1, and NRG1 in an EGFR-centered network.

**Evidence strength:** Multiple pathway-validated genes with known regulatory relationships. Network-level support from STRING. Limitation: elevated expression may indicate attempted repair rather than causal drivers of progression; directionality of effect is unclear from cross-sectional transcriptomics.

### Program 4: Extracellular Matrix Remodeling and Glycosaminoglycan Metabolism
**Direction:** Risk-associated  
**Major supporting genes:** SPP1 (HR=3.40), CHST15 (HR=2.99), HS3ST1 (HR=3.24), GALNT14 (HR=3.11), FAM20A (HR=3.27), MMP25 (HR=3.26), SOD3 (HR=2.37)  
**Pathway context:** ECM organization, Glycosaminoglycan biosynthesis (KEGG), Golgi apparatus localization (GO)  

**Rationale:** SPP1 (osteopontin) is a matricellular protein promoting fibroblast recruitment and ECM deposition. CHST15 and HS3ST1 are sulfotransferases modifying heparan sulfate and chondroitin sulfate, glycosaminoglycans that regulate growth factor bioavailability and cell-matrix interactions. GALNT14 initiates O-glycosylation of mucins and ECM proteins, while FAM20A phosphorylates xylose in proteoglycan biosynthesis. MMP25, a membrane-type metalloproteinase, remodels ECM and activates latent growth factors. SOD3, the extracellular superoxide dismutase, localizes to ECM and modulates oxidative stress. Multiple genes localize to Golgi apparatus, the glycosylation and secretion hub. This module indicates active ECM biosynthesis and post-translational modification.

**Evidence strength:** Biochemically coherent pathway involving glycosylation enzymes, ECM structural proteins, and remodeling proteases. Limitation: does not distinguish productive matrix deposition from aberrant glycosylation contributing to fibrosis.

### Program 5: Membrane Transport and Metabolic Reprogramming
**Direction:** Mixed association  
**Major supporting genes:** SLC7A11 (HR=3.52, risk), SLC39A8 (HR=3.22, risk), SLC6A8 (HR=3.21, risk), SLC34A2 (HR=2.27, risk), SLCO4A1 (HR=2.97, risk), KCNJ15 (HR=3.58, risk), CYP4F3 (HR=3.78, risk)  
**Pathway context:** Amino acid transport, metal ion homeostasis, phosphate transport, organic anion transport  

**Rationale:** SLC7A11 (xCT) mediates cystine uptake for glutathione synthesis, conferring oxidative stress resistance and a feature of metabolic reprogramming in cancer and fibrosis. SLC39A8 imports zinc and manganese, regulating metalloenzymes and inflammatory signaling. SLC6A8 transports creatine for energy metabolism. SLCO4A1 mediates prostaglandin and thyroid hormone uptake. KCNJ15, a potassium channel, regulates membrane potential and cell volume. CYP4F3, a cytochrome P450 enzyme metabolizing leukotrienes, connects to inflammatory lipid signaling. The diversity of transporters suggests broad metabolic rewiring to support biosynthesis, redox balance, and inflammatory mediator production.

**Evidence strength:** Each gene is well-characterized functionally. Limitation: lacks coherent upstream regulator or unified pathway; may reflect cell-type heterogeneity rather than a single coordinated program. Unclear whether transport changes are adaptive or maladaptive.

## 3. Key Genes and Interaction Modules

### Gene 1: SPP1 (Osteopontin)
**Association:** HR=3.40 (P=9.77×10⁻⁸, FDR=3.99×10⁻⁵), risk  
**Role:** Central mediator of ECM remodeling (Program 4). SPP1 recruits fibroblasts and macrophages via integrin and CD44 receptors, promotes myofibroblast differentiation, and inhibits apoptosis of fibrotic cells. STRING analysis links SPP1 to CD44, SLC7A11, and HGF/FN1 networks.  
**Interaction evidence:** Pathway co-membership (ECM organization); literature-validated roles in IPF and other fibrotic diseases.

### Gene 2: HGF–MET Axis
**Association:** HGF HR=2.93, MET HR=2.53, both risk  
**Role:** Core component of growth factor signaling (Program 3). HGF–MET normally promotes alveolar epithelial repair, but chronic activation may drive aberrant epithelial proliferation or failed regeneration. STRING places HGF and MET in the same network module with EGFR-related genes.  
**Interaction evidence:** Direct ligand-receptor pair (physical interaction established).

### Gene 3: S100A12
**Association:** HR=2.53 (P=2.58×10⁻⁹, FDR=5.49×10⁻⁶), risk  
**Role:** DAMP released by activated neutrophils (Program 2). Binds RAGE and TLR4 to amplify inflammation. STRING confirms S100A12–AGER interaction (confidence 0.999) and S100A12–TLR4 (0.970).  
**Interaction evidence:** Direct physical interaction with AGER; regulatory interaction with TLR4-mediated NF-κB signaling (Reactome pathway TAK1-dependent IKK activation).

### Gene 4: HTRA1
**Association:** HR=4.30 (P=7.86×10⁻¹⁰, FDR=2.57×10⁻⁶), risk  
**Role:** Secreted serine protease that cleaves TGF-β family members, fibronectin, and other ECM proteins. Typically considered anti-fibrotic, yet elevated expression associates with poor prognosis. May indicate failed compensatory response or context-dependent pro-fibrotic cleavage products.  
**Interaction evidence:** Substrate relationships with TGF-β family and ECM proteins (regulatory/enzymatic, not physical complex).

### Gene 5: SLC7A11 (xCT)
**Association:** HR=3.52 (P=1.03×10⁻⁸, FDR=1.09×10⁻⁵), risk  
**Role:** Cystine-glutamate antiporter conferring oxidative stress resistance (Program 5). Overexpression in cancer enables survival under oxidative stress. In IPF, may support fibroblast and myofibroblast survival in the oxidative lung microenvironment. STRING links SLC7A11 to CD44 and SPP1 networks.  
**Interaction evidence:** Co-expression and pathway co-membership with ECM genes; indirect relationship via CD44-mediated signaling.

### Gene 6: CXCL1–CXCR1 Axis
**Association:** CXCL1 HR=2.99, CXCR1 HR=3.28, both risk  
**Role:** Chemokine ligand-receptor pair driving neutrophil chemotaxis (Program 2). CXCL1 binds CXCR1 and CXCR2 to recruit neutrophils. STRING confirms CXCL1, CXCR1, CCL7, and CXCL14 in a chemokine network module with CXCL5 and CXCL6 as hubs.  
**Interaction evidence:** Direct ligand-receptor interaction.

### Gene 7: SFTPB
**Association:** HR=2.66 (P=7.47×10⁻⁸, FDR=3.37×10⁻⁵), risk  
**Role:** Surfactant protein B, essential for surfactant function and AT2 cell identity (Program 1). Elevated expression may reflect AT2 cell stress, proliferation, or abnormal differentiation in fibrotic regions.  
**Interaction evidence:** Co-expression with other AT2 markers (SLC34A2, SFTA2); pathway co-membership in surfactant metabolism.

### Gene 8: BMP6
**Association:** HR=3.04 (P=2.42×10⁻⁹, FDR=5.49×10⁻⁶), risk  
**Role:** TGF-β superfamily member with context-dependent effects. Can promote or inhibit fibroblast activation depending on downstream SMAD signaling. Risk association suggests pro-fibrotic signaling dominates in this context.  
**Interaction evidence:** Pathway co-membership in TGF-β superfamily signaling.

### Gene 9: MARCKS
**Association:** HR=3.998 (P=3.63×10⁻⁸, FDR=2.12×10⁻⁵), risk  
**Role:** Myristoylated alanine-rich C-kinase substrate, a PKC substrate regulating actin cytoskeleton, cell motility, and secretion. Implicated in fibroblast migration and ECM secretion. STRING links MARCKS to BASP1 and calmodulin-like proteins (CALML4, CALML6), suggesting calcium-dependent cytoskeletal regulation.  
**Interaction evidence:** Regulatory interaction via PKC signaling; co-expression with cytoskeletal regulators.

### Gene 10: LOC100128226
**Association:** HR=0.007 (P=1.24×10⁻³⁸, FDR=4.80×10⁻³⁵), protective  
**Role:** Uncharacterized locus with extreme protective association. The HR near zero and vanishingly small P-value suggest technical artifact, batch effect, or a biologically implausible effect size. Requires independent validation before biological interpretation.  
**Interaction evidence:** Insufficient characterization for network analysis.

## 4. Validation Priorities

### Priority 1: Neutrophil Burden and S100A12 as Prognostic Biomarker
**Classification:** Biomarker + mechanistic hypothesis  
**Current evidence:** Transcriptomic data show coordinated upregulation of neutrophil markers (S100A12, CD177, CXCL1, CXCR1, SELL). STRING network analysis confirms S100A12–AGER and S100A12–TLR4 interactions. Literature supports S100A12 as a DAMP amplifying inflammation via RAGE signaling.  
**External evidence:** S100A12 is elevated in BAL fluid and serum of IPF patients in some cohorts, though not universally replicated. RAGE signaling has been implicated in experimental pulmonary fibrosis.  
**Validation approach:** Measure S100A12 protein in serum or BAL; correlate with disease progression and mortality in independent cohorts. Immunohistochemistry to localize neutrophils in fibrotic versus non-fibrotic regions. Flow cytometry to quantify neutrophil subsets.  
**Conclusion status:** Supported hypothesis. Transcriptomic association is strong, but protein-level replication and mechanistic causality are unproven.

### Priority 2: HGF–MET Signaling as Failed Regeneration vs. Aberrant Proliferation
**Classification:** Mechanistic hypothesis  
**Current evidence:** HGF (HR=2.93) and MET (HR=2.53) both associate with risk. STRING places them in a growth factor network with EGFR-related genes. Normally, HGF–MET promotes epithelial repair, raising the paradox of why increased expression predicts worse outcomes.  
**External evidence:** HGF is elevated in IPF serum and correlates with disease severity in some studies. MET activation in alveolar epithelial cells can promote regeneration, but chronic activation may drive dysplasia or senescence.  
**Validation approach:** Immunostaining to determine whether HGF and MET are elevated in epithelial cells, fibroblasts, or both. Single-cell RNA-seq to identify which epithelial subpopulations express MET. Functional studies in organoid or mouse models to test whether HGF–MET inhibition slows or accelerates fibrosis. Measure soluble HGF in serum across disease stages.  
**Conclusion status:** Exploratory hypothesis. Association–causation ambiguity is unresolved. Could represent attempted repair, futile activation, or compensatory upregulation.

### Priority 3: SLC7A11 and Oxidative Stress Resistance in Fibroblast Survival
**Classification:** Therapeutic target + mechanistic hypothesis  
**Current evidence:** SLC7A11 (HR=3.52) is the second-strongest single-gene risk factor. It imports cystine for glutathione synthesis, conferring oxidative stress resistance. Overexpressed in cancer and fibrotic tissues.  
**External evidence:** SLC7A11 inhibition (e.g., erastin, sulfasalazine) induces ferroptosis in cancer cells. In lung fibrosis models, SLC7A11 supports myofibroblast survival under oxidative stress. Genetic or pharmacologic SLC7A11 inhibition reduces fibrosis in some preclinical studies.  
**Validation approach:** Immunostaining to localize SLC7A11 to fibroblasts, myofibroblasts, or epithelial cells. Measure intracellular glutathione and lipid peroxidation markers. Test SLC7A11 inhibitors in IPF-derived fibroblasts and organoid models. Assess whether SLC7A11 high-expressing patients respond differently to antioxidant or anti-fibrotic therapies.  
**Conclusion status:** Supported hypothesis with therapeutic rationale. SLC7A11 inhibitors are available, but clinical safety in IPF is unproven.

### Priority 4: AT2 Cell Dysfunction and Aberrant Differentiation
**Classification:** Mechanistic hypothesis + confounding check  
**Current evidence:** SFTPB, SLC34A2, SFTA2, and AGR3 (all risk-associated) suggest AT2 cell stress or expansion. Could reflect increased AT2 proportion in fibrotic tissue, per-cell transcriptional reprogramming, or aberrant differentiation toward a secretory phenotype.  
**External evidence:** Single-cell studies show that IPF lungs contain expanded AT2-like populations with abnormal gene expression, including KRT17+ transitional cells. AT2 cells are considered the primary injured cell type in IPF.  
**Validation approach:** Single-cell RNA-seq to resolve AT2 subpopulations and differentiation trajectories. Immunofluorescence co-staining for surfactant proteins and epithelial markers (KRT17, MUC1) to identify aberrant cell states. Lineage tracing in mouse models to determine whether AT2 cells adopt pro-fibrotic fates. Cell-type deconvolution of bulk transcriptomics to estimate AT2 proportions and per-cell expression.  
**Conclusion status:** Supported hypothesis with significant confounding risk. Transcriptomic changes may reflect cell composition rather than disease mechanism. Single-cell resolution is essential.

### Priority 5: Extracellular Matrix Glycosylation and Therapeutic Modulation
**Classification:** Mechanistic hypothesis  
**Current evidence:** CHST15 (HR=2.99), HS3ST1 (HR=3.24), GALNT14 (HR=3.11), FAM20A (HR=3.27) are glycosylation enzymes modifying ECM. Multiple genes localize to Golgi apparatus, the site of post-translational glycosylation.  
**External evidence:** Aberrant glycosaminoglycan sulfation alters growth factor binding, cell adhesion, and ECM stiffness. CHST15 knockout reduces fibrosis in some models. Heparan sulfate mimetics and glycosaminoglycan-targeting therapies are in preclinical development.  
**Validation approach:** Mass spectrometry to profile glycosaminoglycan sulfation patterns in IPF vs. control lung tissue. Immunostaining to localize CHST15 and HS3ST1 to fibroblasts or epithelial cells. Test glycosylation enzyme inhibitors or heparan sulfate mimetics in fibrosis models. Assess whether glycosylation patterns predict response to anti-fibrotic drugs.  
**Conclusion status:** Exploratory hypothesis. Mechanistic plausibility is high, but direct evidence linking glycosylation to IPF progression is limited.

## 5. Evidence Grounding

**Dataset evidence:** All HR, P, and FDR values derive from the uploaded statistical table and represent direct evidence for this cohort. No independent cohort validation is available.

**Pathway/ontology evidence:** GO/KEGG/Reactome annotations confirm that selected genes cluster in neutrophil degranulation, chemokine signaling, ECM organization, and epithelial cell signaling pathways. This provides biological coherence but does not constitute replication of the prognostic associations.

**Protein interaction evidence:** STRING analysis provides high-confidence physical interactions (e.g., S100A12–AGER 0.999, HGF–MET ligand-receptor pair) and network co-membership (e.g., EGFR-centered module). These are database-derived and may reflect text-mining or prediction rather than direct experimental validation.

**Disease-association evidence:** Literature retrieval identified relevant publications for genes like KRT23, CYP4F3, FAM198B, VGF, IHH, CTSH, and SFTA2, though most focus on other diseases (MAFLD, lung cancer, psychiatric disorders). IPF-specific literature for these genes is limited.

**Expression/tissue evidence:** GTEx confirms lung-enriched or lung-expressed genes (e.g., SFTPB, SLC34A2, surfactant proteins), supporting tissue-appropriate interpretation. However, GTEx represents normal tissue; disease-state expression patterns may differ.

**Genetic/clinical evidence:** GWAS and ClinVar annotations are available for many genes, but SNPs in these genes are not established IPF risk loci. No genetic evidence directly supports causal roles in IPF.

**Drug/therapeutic evidence:** ChEMBL and ClinicalTrials.gov identify drugs targeting some genes (e.g., CXCR1 antagonists, MET inhibitors, SLC7A11 inhibitors), but their clinical relevance to IPF is unproven. The existence of a drug does not validate the gene as an effective therapeutic target.

**Conflicts:** Some genes (e.g., HTRA1, SPRY2) have reported anti-fibrotic functions, yet associate with poor prognosis here. This conflict may reflect compensatory upregulation, context-dependent roles, or post-transcriptional regulation.

**Insufficient evidence:** Validation priorities related to glycosylation enzymes and metabolic transporters lack direct experimental evidence in IPF. Most interaction networks derive from generic databases rather than IPF-specific studies.

## 6. Limitations and Alternative Explanations

### Limitation 1: Cell Composition Confounding
Bulk transcriptomics cannot distinguish increased gene expression per cell from altered cell-type proportions. For example, elevated SFTPB, S100A12, and neutrophil markers could reflect increased AT2 cells and neutrophils in fibrotic tissue rather than per-cell transcriptional changes driving disease. Single-cell RNA-seq or cell-type deconvolution is required to resolve this ambiguity.

### Limitation 2: Disease Severity and Stage Effects
The prognostic associations may capture disease severity at baseline rather than mechanistic drivers of progression. Patients with more severe fibrosis at baseline may have higher expression of fibrosis-associated genes and worse outcomes, but this does not prove that these genes cause progression. Longitudinal sampling and time-to-event modeling are needed to distinguish severity markers from progression drivers.

### Limitation 3: Extreme Effect Sizes Suggest Technical Artifacts
Several genes show HR values near 10²¹ or 10⁻²² with P=0, which are biologically implausible. These likely reflect probe failures, batch effects, or mathematical artifacts in the survival model. CONTROL probes, unannotated lncRNAs, and genes like MIR221, IHH, FAM75A2, OR2M2 with extreme HRs should be flagged for quality control. Their exclusion does not alter the major biological programs but underscores the need for technical validation.

### Limitation 4: Association vs. Causation
Transcriptomic associations do not establish causality. Elevated HGF–MET or SLC7A11 expression could represent failed compensatory responses rather than disease drivers. Functional validation (knockdown, knockout, or pharmacologic inhibition in models) is required to test causal roles. The current results identify candidates for validation but do not prove that modulating these genes will alter disease outcomes.

### Limitation 5: Lack of Independent Cohort Validation
No external cohort statistics are provided. The prognostic associations are dataset-specific and may not generalize to other IPF cohorts, which differ in demographics, disease stage, treatment exposure, and technical platforms. Replication in independent datasets is essential before clinical application.

---

**Summary:** This IPF prognostic signature centers on epithelial dysfunction, neutrophil-driven inflammation, growth factor signaling, ECM remodeling, and metabolic reprogramming. Validation priorities include S100A12 as a biomarker, HGF–MET signaling as a mechanistic target, and SLC7A11 as a therapeutic candidate, with emphasis on resolving cell composition confounding and association–causation ambiguity through single-cell and functional studies.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=47, external claims checked=0, external mismatches=0, status=passed.

Answer model API: Anthropic / claude-opus-4-8

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 77/100 selected items (partially returned; some queries failed); cbioportal 78/100 selected items (records returned); chembl 13/100 selected items (partially returned; some queries failed); civic 8/100 selected items (records returned); clinicaltrials 48/100 selected items (records returned); clinvar 78/100 selected items (records returned); ensembl 25/100 selected items (partially returned; some queries failed); europepmc 860 articles / initial full-cohort RAG 100 queries + 4 current-round queries; some queries failed; gtex 83/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 78/100 selected items (records returned); humanbase 78/100 selected items (records returned); intact 81/100 selected items (partially returned; some queries failed); mygene 91/100 selected items (records returned); omnipath 47/100 selected items (records returned); opentargets 80/100 selected items (partially returned; some queries failed); pubmed 658 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 83/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 84/100 selected items (records returned)
Local databases: gutmgene 3/100 selected items (records returned); hmdb 32/100 selected items (records returned); string 79/100 selected items (records returned); trrust 25/100 selected items (records returned)
