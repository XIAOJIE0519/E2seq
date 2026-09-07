# rheumatoid arthritis - claude-opus-4-8

- Benchmark system: E2seq + Agent RAG
- Repeat: 2
- Task type: DISEASE-STATE
- Tissue / sample source: synovial tissue
- Comparison or endpoint: rheumatoid arthritis versus normal control
- Answer input cohort: Discovery/Core only
- Selected items: 100
- Input fields: gene name, effect size (log2FC/HR), P value, FDR
- E2seq Agent RAG: enabled
- Conversation memory: disabled
- Thinking mode: disabled
- Held-out validation data in prompt/RAG: no
- Model API: Anthropic / claude-opus-4-8
- Message SHA-256: d868ce3efb219458b8d5ddb7b123eef3f2b718852ba0ede74f2a02e9181db293
- Response HTTP status: 200
- Prompt tokens: 43322
- Completion tokens: 16168
- Reasoning tokens: 0
- Total tokens: 59490
- API requests reported: 4
- Elapsed seconds: 247.366
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 984.622
- Question handoff seconds: 999.892
- Final benchmark system: E2seq; file rank 1/5; original repeat 2; model vendor: Anthropic

---
# Multidimensional Interpretation of Rheumatoid Arthritis Synovial Transcriptomics

## 1. Overall Biological Interpretation

The transcriptomic signature shows uniform downregulation of 100 genes in rheumatoid arthritis (RA) synovial tissue compared to normal controls, with no upregulated genes in this dataset. This unidirectional pattern is unusual for inflammatory disease and suggests either:

- Analysis of a specific cell population depleted in RA synovium
- Technical artifact or batch effect
- Selective focus on downregulated genes from a larger dataset

The downregulated genes span diverse functions including zinc finger transcription factors (ZNF316, ZNF219, ZNF444, ZNF580), structural/cytoskeletal proteins (CROCC, SCRIB, INF2), mucins (MUC12, MUC5B, MUC6), and numerous long non-coding RNAs and microRNAs. Many top-ranked genes are poorly characterized (LOC identifiers, MIR genes), limiting biological interpretation. The absence of classical RA-associated inflammatory markers (cytokines, chemokines, matrix metalloproteinases) that are typically upregulated in RA synovium suggests this represents a subset of the transcriptional landscape rather than the complete synovial signature.

## 2. Core Biological Programs

### Program 1: Epithelial/Mucosal Gene Silencing
**Direction:** Downregulated  
**Major supporting genes:** MUC12, MUC5B, MUC6, CDHR5, GJC2  
**Pathway:** Not directly mapped to standard pathways; represents tissue-specific epithelial markers  
**Biological basis:** Multiple mucin genes (MUC12, MUC5B, MUC6) show strong downregulation (log2FC -3.85 to -4.43, FDR < 1e-40). These are gel-forming mucins typically expressed in respiratory and gastrointestinal epithelia, not synovium. CDHR5 (cadherin-related family member 5) and GJC2 (gap junction protein) also represent epithelial markers. The STRING network shows MUC1 connects MUC12, MUC5B, and MUC6.

**Evidence strength:** Strong statistical signal but biologically questionable for synovial tissue.  
**Major limitation:** Mucins are not typically expressed in synovium. Their downregulation likely reflects contaminating epithelial cells in normal controls, sample heterogeneity, or technical artifact rather than RA pathogenesis. This calls into question the biological relevance of the entire dataset.

### Program 2: Transcriptional Regulation via Zinc Finger Proteins
**Direction:** Downregulated  
**Major supporting genes:** ZNF316, ZNF219, ZNF444, ZNF580, FLYWCH1  
**Pathway:** GO:0003700 DNA-binding transcription factor activity  
**Biological basis:** Multiple C2H2-type zinc finger transcription factors show consistent downregulation (log2FC -2.46 to -3.24, FDR < 3e-36). These proteins typically regulate gene expression programs, and their coordinated loss could affect downstream transcriptional networks. However, most are poorly characterized with limited functional annotation.

**Evidence strength:** Moderate. Consistent statistical pattern but limited mechanistic understanding.  
**Major limitation:** Most zinc finger proteins have unknown target genes and tissue-specific functions. Cannot determine whether their downregulation is cause, consequence, or bystander to RA pathology without functional validation. High abundance of ZNF genes may reflect cell-type composition rather than disease mechanism.

### Program 3: Cytoskeletal Organization and Cell Architecture
**Direction:** Downregulated  
**Major supporting genes:** CROCC, CROCC2, SCRIB, INF2, ARHGAP33  
**Pathway:** GO biological processes in cytoskeletal organization; Hippo signaling pathway (from batch enrichment)  
**Biological basis:** CROCC/CROCC2 (ciliary rootlet coiled-coil proteins, log2FC -3.88 and -4.99) are microtubule-organizing proteins. SCRIB (log2FC -3.24) is a cell polarity regulator that interacts with ARHGEF7 and VANGL2 in the planar cell polarity pathway. INF2 (inverted formin 2, log2FC -2.76) regulates actin dynamics. ARHGAP33 (log2FC -3.20) is a Rho GTPase-activating protein affecting cell shape and motility.

**Evidence strength:** Moderate. These genes have established functions in cytoskeletal regulation, but their specific relevance to RA synovium is unclear.  
**Major limitation:** Cytoskeletal changes could reflect altered cell-type composition (loss of resident fibroblasts, gain of infiltrating immune cells) rather than functional changes within a single cell type. The Hippo pathway connection from batch enrichment is interesting but speculative without further validation.

### Program 4: Non-Coding RNA Regulation
**Direction:** Downregulated  
**Major supporting genes:** MIR3183, MIR3615, MIR3154, MIR937, MIR647, PCGF3-AS1, DM1-AS  
**Pathway:** Post-transcriptional gene regulation  
**Biological basis:** Numerous microRNAs and long non-coding RNAs show strong downregulation (log2FC -3.52 to -5.10, FDR < 1e-40). These regulatory RNAs can control gene expression networks, but most have limited functional characterization.

**Evidence strength:** Weak. Strong statistical signal but minimal biological understanding.  
**Major limitation:** Most microRNAs listed have no validated targets or disease associations. Their expression may reflect tissue composition or technical factors. The presence of multiple miRNAs with extreme fold changes raises concern about RNA quality or contamination. Without target validation, these findings have limited interpretability.

### Program 5: Ribosomal and Translation Machinery
**Direction:** Inferred from batch enrichment; not strongly represented in top 100 downregulated genes  
**Major supporting genes:** Limited representation in provided gene list  
**Pathway:** KEGG: Ribosome biogenesis in eukaryotes, Ribosome (from batch enrichment)  
**Biological basis:** The question-time enrichment identified ribosome-related pathways, but the top 100 downregulated genes do not prominently feature ribosomal proteins or translation factors.

**Evidence strength:** Insufficient. Pathway enrichment without clear gene-level support.  
**Major limitation:** Cannot validate this program with the provided data. Ribosome pathway enrichment may emerge from genes beyond the top 100 or reflect indirect associations. This illustrates the importance of examining actual gene membership rather than relying solely on pathway labels.

## 3. Key Genes and Interaction Modules

### 1. SCRIB (log2FC -3.24)
**Role:** Cell polarity regulator and tumor suppressor  
**Program association:** Cytoskeletal organization, Hippo signaling  
**Interactions:** STRING evidence shows direct physical interaction with ARHGEF7, VANGL2, GIT1, and UBE3A (confidence >0.98). These represent established components of the planar cell polarity and Scribble polarity complexes.  
**Relevance:** SCRIB regulates epithelial architecture and has been studied in cancer but not prominently in RA. Its downregulation could affect synovial lining integrity, but this hypothesis lacks RA-specific evidence.

### 2. CROCC/CROCC2 (log2FC -3.88 and -4.99)
**Role:** Ciliary rootlet structural proteins  
**Program association:** Cytoskeletal organization  
**Interactions:** STRING network identifies LRRC45 as a shared interactor with both CROCC and CROCC2 (pathway co-membership).  
**Relevance:** These proteins organize microtubule networks in ciliated cells. Their extreme downregulation in RA synovium is biologically puzzling since synoviocytes are not ciliated. May indicate loss of a specific cell population or technical artifact.

### 3. MUC5B/MUC6/MUC12 (log2FC -4.27 to -4.43)
**Role:** Gel-forming mucins for mucosal protection  
**Program association:** Epithelial gene silencing  
**Interactions:** STRING network shows these three mucins cluster with MUC1 and MUC2 (protein family relationship, not direct physical interaction).  
**Relevance:** Mucins are not synovial markers. Their presence suggests either contaminating epithelial cells in control samples or off-target tissue sampling. This is a red flag for data quality rather than a biological finding.

### 4. APC2 (log2FC -3.02)
**Role:** Wnt signaling negative regulator  
**Program association:** Could relate to fibroblast proliferation control  
**Interactions:** STRING evidence shows APC2 and ARVCF both interact with CTNNB1 (β-catenin), indicating pathway co-membership in Wnt signaling. Not direct physical interaction between APC2 and ARVCF.  
**Relevance:** Wnt signaling is implicated in synovial fibroblast activation in RA. APC2 downregulation could theoretically enhance Wnt signaling and promote pathogenic fibroblast behavior, but this is speculative without validation of pathway activity.

### 5. ARVCF (log2FC -3.46)
**Role:** Armadillo repeat protein involved in cell adhesion  
**Program association:** Cell-cell junction organization  
**Interactions:** STRING shows interactions with COMT, CTNNB1 (Wnt signaling), and ERBIN (confidence >0.80).  
**Relevance:** ARVCF is located in the 22q11.2 deletion region associated with DiGeorge syndrome. Its role in RA is unknown. The interaction with CTNNB1 suggests potential Wnt pathway involvement.

### 6. NOL3/PIDD1 (log2FC -2.45 and -2.89)
**Role:** Apoptosis regulation  
**Program association:** Cell death and survival pathways  
**Interactions:** STRING network indicates these genes cluster with CASP2 (caspase-2), suggesting pathway co-membership in apoptosis regulation.  
**Relevance:** NOL3 (nucleolar protein 3) is an anti-apoptotic factor, while PIDD1 is a pro-apoptotic protein. Their coordinated downregulation could affect synoviocyte survival, but the net effect on apoptosis is unclear.

### 7. SH2B1 (log2FC -2.28)
**Role:** Adaptor protein for growth factor and cytokine signaling  
**Program association:** Signal transduction  
**Interactions:** QuickGO annotation indicates protein binding activity; known to interact with JAK2 and insulin receptor pathways (literature evidence, not in STRING output).  
**Relevance:** SH2B1 modulates JAK-STAT signaling, which is therapeutically targeted in RA (JAK inhibitors). Its downregulation could reflect feedback regulation in chronically inflamed tissue or cell-type shifts.

### 8. ADAMTS7 (log2FC -3.29)
**Role:** Metalloproteinase with roles in cartilage degradation and atherosclerosis  
**Program association:** Extracellular matrix remodeling  
**Interactions:** QuickGO and Reactome indicate proteolytic activity and ECM interactions.  
**Relevance:** ADAMTS family members degrade cartilage oligomeric matrix protein and other ECM substrates. However, most ADAMTS proteases are upregulated in RA. ADAMTS7 downregulation is counterintuitive but could represent a compensatory response or tissue-specific regulation.

### 9. D2HGDH (log2FC -2.76)
**Role:** D-2-hydroxyglutarate dehydrogenase; metabolic enzyme  
**Program association:** Mitochondrial metabolism  
**Interactions:** Limited interaction data available.  
**Relevance:** D-2-hydroxyglutarate is an oncometabolite associated with IDH mutations in cancer. Its role in RA is unexplored. Metabolic reprogramming occurs in RA synoviocytes, but evidence for D2HGDH involvement is absent.

### 10. DMPK (log2FC -2.97)
**Role:** Myotonic dystrophy protein kinase  
**Program association:** Signal transduction, potential role in cytoskeletal dynamics  
**Interactions:** Limited synovium-relevant interaction data.  
**Relevance:** DMPK mutations cause myotonic dystrophy type 1. Its downregulation in RA synovium lacks a clear mechanistic connection to disease pathology. May reflect cell-type composition or be incidental.

## 4. Validation Priorities

### Priority 1: Cell-Type Composition Analysis
**Category:** Confounding or composition check  
**Rationale:** The presence of mucins, ciliary proteins, and other non-synovial markers strongly suggests cell-type heterogeneity is driving the observed downregulation pattern. Before interpreting any gene as biologically relevant to RA, the cellular composition of normal versus RA samples must be defined.  
**Current evidence:** Statistical downregulation of epithelial markers in a supposedly synovial dataset.  
**External evidence:** Insufficient. Standard RA synovial transcriptomics shows upregulation of inflammatory markers and matrix-degrading enzymes, not downregulation of epithelial genes.  
**Next step:** Single-cell RNA sequencing or cell-type deconvolution analysis to quantify fibroblasts, immune cells, endothelial cells, and potential epithelial contamination in each sample.  
**Conclusion status:** Exploratory hypothesis. The dataset may not represent pure synovial biology.

### Priority 2: Wnt/β-Catenin Pathway Activity
**Category:** Mechanistic hypothesis  
**Rationale:** Downregulation of APC2 and ARVCF, both negative regulators of Wnt signaling, could theoretically enhance β-catenin activity and promote synovial fibroblast proliferation and inflammatory responses.  
**Current evidence:** Transcriptional downregulation of two Wnt pathway components; STRING network connection through CTNNB1.  
**External evidence:** Mixed. Wnt signaling activation has been reported in RA synovium in some studies, but APC2 and ARVCF have not been specifically implicated. Opentargets data show limited genetic association of these genes with RA.  
**Next step:** Measure β-catenin protein levels, localization, and downstream target gene expression (e.g., AXIN2, LEF1) in RA versus control synovium. Functional validation through APC2 knockdown in cultured synoviocytes.  
**Conclusion status:** Supported hypothesis. Plausible mechanism based on pathway biology, but causal relationship unproven.

### Priority 3: SCRIB-Mediated Polarity and Tissue Architecture
**Category:** Mechanistic hypothesis  
**Rationale:** SCRIB loss could disrupt synovial lining organization and contribute to the invasive, hyperplastic phenotype of RA synovium.  
**Current evidence:** SCRIB downregulation with well-characterized protein interactions in polarity pathways.  
**External evidence:** SCRIB is studied primarily in cancer and epithelial biology. No published evidence linking SCRIB to RA or synovial pathology. Opentargets and clinical databases show no RA association.  
**Next step:** Immunohistochemistry to confirm SCRIB protein loss in RA synovial lining. Functional studies examining effects of SCRIB depletion on synoviocyte invasiveness, proliferation, and inflammatory cytokine production.  
**Conclusion status:** Exploratory hypothesis. Biologically plausible but no disease-specific evidence.

### Priority 4: Mucin Gene Expression as a Compositional Biomarker
**Category:** Biomarker (for sample quality/composition, not disease activity)  
**Rationale:** Mucin expression levels could serve as quality control markers to identify epithelial contamination or aberrant tissue sampling.  
**Current evidence:** Extreme statistical signal for mucin downregulation in RA samples.  
**External evidence:** Mucins are not established synovial markers. Their presence indicates either technical issue or biological phenomenon (e.g., respiratory tissue sampling in controls).  
**Next step:** Review original tissue collection protocols and histological slides. Quantify mucin protein by immunostaining to determine if transcriptional signal reflects protein presence.  
**Conclusion status:** Established evidence that mucins should not be in synovium. The dataset likely contains a confounding factor.

### Priority 5: SH2B1 and JAK-STAT Pathway Feedback
**Category:** Therapeutic target (exploratory)  
**Rationale:** SH2B1 modulates JAK-STAT signaling, which is a validated therapeutic target in RA (tofacitinib, baricitinib). Understanding its downregulation could inform combination therapy strategies.  
**Current evidence:** SH2B1 downregulation in this dataset; known role in JAK signaling from general literature.  
**External evidence:** JAK inhibitors are effective in RA (clinical evidence), but SH2B1 specifically has not been studied in RA. Opentargets shows no genetic association with RA susceptibility.  
**Next step:** Measure SH2B1 protein levels in RA synovium and synoviocytes. Examine whether JAK inhibitor treatment affects SH2B1 expression. Test whether SH2B1 overexpression alters cytokine responsiveness in synoviocytes.  
**Conclusion status:** Exploratory hypothesis. Indirect connection through pathway membership; requires multiple validation steps before considering as a therapeutic target.

## 5. Evidence Grounding

**Direct dataset evidence (strongest):**  
All 100 genes show statistically robust downregulation (FDR < 5e-35) with effect sizes ranging from log2FC -2.23 to -5.10. This represents the only direct evidence for this specific cohort.

**Pathway/ontology evidence (contextual):**  
GO annotation indicates enrichment in protein binding, nucleus localization, and membrane-associated components. KEGG batch enrichment suggested ribosome pathways (not validated in gene list). These annotations describe general molecular features but do not provide disease-specific mechanistic insight.

**Protein interaction evidence (contextual):**  
STRING database identifies protein-protein interactions, primarily reflecting pathway co-membership rather than direct physical interactions. Examples include the mucin cluster, SCRIB polarity complex, and Wnt signaling components. These networks inform biological coherence but do not validate causal relationships.

**Disease association evidence (weak to absent):**  
Opentargets, ClinVar, and GWAS data show limited genetic associations between these genes and RA. SH2B1 appears in some metabolic trait GWAS. ADAMTS7 has cardiovascular associations. No genes show strong genetic evidence for RA susceptibility or severity.

**Expression/tissue-specific evidence (conflicting):**  
GTEx shows many genes (e.g., mucins) are not normally expressed in relevant musculoskeletal tissues, indicating a fundamental mismatch between the dataset and expected synovial biology. HPA confirms this for MUC5B, MUC6, and CDHR5.

**Therapeutic evidence (limited):**  
ChEMBL identifies drugs targeting 16/100 genes, but most are not RA-relevant. The existence of SH2B1's connection to JAK signaling (targeted by approved RA drugs) is the only therapeutically relevant finding, and this connection is indirect.

**Published literature evidence (sparse and non-independent):**  
PubMed and EuroPMC searches retrieved 483 and 776 articles respectively, but most are not RA-specific. Example articles discuss microRNA roles in cancer (e.g., MIR647 in lung cancer, PRRT3-AS1 in melanoma), which are not relevant to RA synovial biology. Literature for mucins, SCRIB, and zinc finger proteins is dominated by cancer and developmental biology studies. True RA-specific literature for these genes is minimal.

**Evidence independence:**  
Many evidence sources overlap. Pathway annotations feed into GO databases, which inform literature curation. Protein interactions may derive from shared publications. The apparently large evidence volume does not represent 20+ independent validations per gene. In reality, most genes have one or two genuine lines of evidence: the input statistic and general protein function annotation.

**Conflicting evidence:**  
The direction of change conflicts with established RA biology. Inflammatory diseases typically show upregulation of chemokines, cytokines, matrix metalloproteinases, and immune activation genes—none of which appear in this dataset. The presence of epithelial-specific markers downregulated in RA synovium contradicts tissue-specific expression expectations and suggests technical or compositional confounding.

## 6. Limitations and Alternative Explanations

### Limitation 1: Potential Cell-Type Composition Confounding
The single most critical limitation is that the downregulated gene signature may reflect differences in cellular composition between RA and control samples rather than changes within a specific cell type. Normal synovium contains fibroblasts, macrophages, and endothelial cells in different proportions than inflamed RA synovium, which is infiltrated by T cells, B cells, plasma cells, and activated macrophages. If normal controls were enriched for a particular cell population (or contaminated with epithelial cells), that population's marker genes would appear "downregulated" in RA purely due to compositional shifts.

**Evidence:** The presence of mucins, ciliary proteins, and gap junction proteins strongly suggests epithelial cell contribution in controls. The absence of upregulated inflammatory markers indicates this is not a complete RA synovial signature.

**Experimental distinction:** Single-cell RNA sequencing or immunostaining-based cell-type quantification could determine whether gene expression changes occur within specific cell types or reflect population shifts. Cell-type deconvolution algorithms applied to bulk RNA-seq could estimate proportions.

### Limitation 2: Incomplete Dataset Representation
Only downregulated genes are provided. This unidirectional pattern is biologically implausible for a complex inflammatory disease. RA synovium invariably shows upregulation of inflammatory pathways, suggesting either:
- The analysis was filtered to show only downregulated genes
- A specific cell population or experimental condition was isolated
- Technical artifact introduced directional bias

**Evidence:** Standard RA transcriptomic studies show both up- and downregulated genes, with prominent upregulation of IL6, TNF, MMPs, chemokines, and complement components.

**Experimental distinction:** Request the complete dataset including upregulated genes. Examine quality control metrics (RNA quality scores, batch effects, sample clustering). Verify tissue source and histological characteristics.

### Limitation 3: Unknown Clinical Context
Critical clinical variables are not provided:
- Disease duration and severity
- Treatment status (naive vs. DMARD-exposed)
- Patient demographics (age, sex, RF/ACPA status)
- Control tissue source (orthopedic surgery, trauma, autopsy)

Treatment with DMARDs, corticosteroids, or biologics could dramatically alter gene expression. Long-standing versus early RA has different transcriptional profiles. Control tissue from osteoarthritis patients would differ from healthy donor tissue.

**Evidence:** Many genes respond to immunosuppressive therapies. For example, corticosteroids broadly suppress gene expression, potentially creating artifactual downregulation patterns.

**Experimental distinction:** Stratify analysis by treatment status. Compare treatment-naive RA patients to controls. Examine temporal changes within patients before and after treatment.

### Limitation 4: Statistical Artifact or Batch Effect
The extreme uniformity of downregulation (100/100 genes, FDR < 5e-35) raises the possibility of systematic technical bias. Potential sources include:
- RNA degradation in one sample group
- Batch effect (samples processed in different runs)
- Normalization artifact
- PCR amplification bias

**Evidence:** The most downregulated genes include multiple microRNAs and poorly annotated loci, which could be differentially affected by technical factors. The extreme P-values (some <1e-50) are unusual even for genuine biological effects.

**Experimental distinction:** Examine raw expression distributions and quality metrics. Check for batch correlation with disease status. Validate top hits by qRT-PCR in independent samples. Compare sequencing platform, library prep protocol, and bioinformatics pipeline between RA and control samples.

### Limitation 5: Lack of Independent Cohort Validation
No independent cohort statistics are provided for replication. Without external validation, it is impossible to determine which findings are reproducible versus cohort-specific, especially given the concerns about tissue composition and technical quality.

**Evidence:** The evidence pack explicitly states "INDEPENDENT COHORT VALIDATION: status=not_available." All conclusions rely on a single dataset with potential confounding factors.

**Experimental distinction:** Analyze publicly available RA synovial transcriptomic datasets (e.g., GSE77298, GSE89408) to determine whether these 100 genes show consistent downregulation. Lack of replication would indicate cohort-specific or technical effects rather than generalizable RA biology.

---

## Summary

This transcriptomic dataset presents a puzzling pattern of uniform downregulation inconsistent with established RA synovial biology. The presence of epithelial markers (mucins, ciliary proteins) not normally found in synovium, combined with the absence of expected inflammatory signals, suggests major cell-type composition differences or technical artifacts confound interpretation.

The only biologically plausible finding with potential RA relevance is the coordinated downregulation of Wnt pathway negative regulators (APC2, ARVCF), which could theoretically enhance pathogenic fibroblast behavior, but this remains a speculative hypothesis requiring functional validation.

**Before investing resources in follow-up studies, the top priority must be validating sample composition, confirming tissue identity, and ruling out technical confounding.** Single-cell analysis or histological verification of the original samples would clarify whether this signature represents genuine synovial biology or reflects contamination, compositional artifact, or technical bias.

The current evidence is insufficient to support mechanistic conclusions about RA pathogenesis or identify therapeutic targets. This dataset should be considered exploratory pending comprehensive quality control and independent replication.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=15, external claims checked=0, external mismatches=0, status=needs review.

Answer model API: Anthropic / claude-opus-4-8

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 84/100 selected items (records returned); cbioportal 82/100 selected items (records returned); chembl 16/100 selected items (records returned); civic 1/100 selected items (records returned); clinicaltrials 19/100 selected items (records returned); clinvar 79/100 selected items (records returned); ensembl 40/100 selected items (partially returned; some queries failed); europepmc 776 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 61/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 47/100 selected items (records returned); humanbase 88/100 selected items (partially returned; some queries failed); intact 47/100 selected items (records returned); mygene 93/100 selected items (records returned); omnipath 17/100 selected items (records returned); opentargets 82/100 selected items (records returned); pubmed 483 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 50/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 51/100 selected items (records returned)
Local databases: gutmgene 0/100 selected items (reachable but no records for this batch); hmdb 8/100 selected items (records returned); string 49/100 selected items (records returned); trrust 7/100 selected items (records returned)
