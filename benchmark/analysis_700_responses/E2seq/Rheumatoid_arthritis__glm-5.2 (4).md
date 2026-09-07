# rheumatoid arthritis - glm-5.2

- Benchmark system: E2seq + Agent RAG
- Repeat: 6
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
- Model API: Zhipu AI / glm-5.2
- Message SHA-256: d868ce3efb219458b8d5ddb7b123eef3f2b718852ba0ede74f2a02e9181db293
- Response HTTP status: 200
- Prompt tokens: 38513
- Completion tokens: 11537
- Reasoning tokens: 0
- Total tokens: 50050
- API requests reported: 3
- Elapsed seconds: 122.236
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 984.622
- Question handoff seconds: 999.892
- Final benchmark system: E2seq; file rank 4/5; original repeat 6; model vendor: Zhipu AI

---
# Multidimensional Interpretation of Synovial Tissue Transcriptomics in Rheumatoid Arthritis

## 1. Overall Biological Interpretation

**Data-quality warning:** The uploaded dataset is directionally degenerate—all 100 selected genes are downregulated (log2FC range −2.27 to −5.10; all FDR ≤ 4.32 × 10⁻³⁵). No upregulated genes are present. This extreme directional skew, combined with the absence of any classical RA inflammatory or immune-effectors among the top hits, suggests that the captured signal likely reflects loss or underrepresentation of specific cell populations or tissue structures in RA synovium relative to normal control, rather than the canonical inflammatory activation program that would be expected to dominate an RA-versus-normal comparison.

With that caveat, the major coherent themes are:

- **Loss of mucosal/epithelial barrier and secretory mucin program** (MUC12, MUC5B, MUC6, CDHR5) — a gastrointestinal/epithelial signature not expected in synovial tissue, raising questions about tissue sourcing or contamination.
- **Loss of cytoskeletal and ciliary structural components** (CROCC, CROCC2, INF2, SCRIB, APC2) — consistent with reduced structural cell content.
- **Downregulation of non-coding RNA species** (multiple MIRs, SCARNA17, SNORD167, RNA5-8SN paralogs, antisense RNAs) — potentially reflecting altered transcriptional landscape or cell-composition shifts.
- **Reduction of Rho GTPase signaling modulators** (ARHGAP33, ARHGAP27P1, ACAP3, SCRIB) — suggesting altered cytoskeletal dynamics and cell polarity.
- **Loss of a 22q11.2 genomic neighborhood signal** (ARVCF, COMT-linked, DGCR-region genes) — potentially reflecting copy-number or epigenetic coordinate regulation.

External statistical validation was not performed; no independent-cohort statistic was supplied.

---

## 2. Core Biological Programs

### Program 1: Mucin and Epithelial Barrier Program
**Direction:** Downregulated  
**Major supporting genes:** MUC12 (log2FC=−4.27, FDR=6.05×10⁻⁴³), MUC5B (log2FC=−4.43, FDR=2.07×10⁻⁴⁰), MUC6 (log2FC=−3.85, FDR=5.92×10⁻³⁶), CDHR5 (log2FC=−4.22, FDR=1.61×10⁻⁴⁵)  
**Standardized pathway:** No specific KEGG/Reactome pathway was retrieved for this gene set; STRING network evidence links MUC12, MUC5B, MUC6 to a mucin interaction cluster (via MUC1, MUC2, MUC5AC, MUC7 as connector nodes)  
**Explanation:** Three gel-forming/secreted mucins (MUC5B, MUC6, MUC12) and the cadherin-related epithelial adhesion molecule CDHR5 collectively represent a mucosal epithelial barrier program. Their coordinate downregulation suggests loss of epithelial-type cells in the RA synovial tissue samples. In normal synovium, these genes would not typically be expected at high expression; their presence in the control group and loss in RA is a notable pattern requiring explanation.  
**Evidence strength:** Strong direct statistical evidence (all FDR < 10⁻³⁵); STRING co-membership supports functional grouping.  
**Major limitation:** Mucin expression is characteristic of gastrointestinal and respiratory epithelium, not synovial tissue. This program's presence in the dataset may indicate tissue misannotation, contamination, or an unusual control tissue source rather than a genuine RA synovial mechanism.

### Program 2: Cytoskeletal Architecture and Ciliary Rootlet Program
**Direction:** Downregulated  
**Major supporting genes:** CROCC (log2FC=−3.88, FDR=9.67×10⁻⁴⁸), CROCC2 (log2FC=−4.99, FDR=1.22×10⁻⁴⁰), INF2 (log2FC=−2.76, FDR=8.10×10⁻³⁶), SCRIB (log2FC=−3.24, FDR=1.32×10⁻⁴²), APC2 (log2FC=−3.02, FDR=4.63×10⁻³⁹)  
**Standardized pathway:** Reactome RHO GTPase cycle pathways (SCRIB); KEGG Hippo signaling pathway (APC2); GO cellular component annotations for cytoplasm and plasma membrane  
**Explanation:** CROCC and CROCC2 encode rootlet components of ciliary rootlets; INF2 regulates actin dynamics; SCRIB and APC2 participate in cell polarity and cytoskeletal organization. Their coordinate downregulation suggests reduced structural cell content—potentially loss of ciliated or highly organized stromal cells in RA synovium. STRING evidence connects CROCC and CROCC2 via LRRC45 as a connector node.  
**Evidence strength:** Strong direct statistics; STRING network evidence for CROCC/CROCC2; Reactome/KEGG pathway membership for SCRIB and APC2.  
**Major limitation:** These genes are not established RA synovial markers; the program may reflect non-specific loss of structural stromal cells rather than a disease-specific mechanism.

### Program 3: Rho GTPase Signaling Modulation
**Direction:** Downregulated  
**Major supporting genes:** ARHGAP33 (log2FC=−3.20, FDR=1.67×10⁻³⁶), ACAP3 (log2FC=−2.80, FDR=2.27×10⁻³⁸), SCRIB (log2FC=−3.24, FDR=1.32×10⁻⁴²), ARHGAP27P1 (log2FC=−2.79, FDR=6.78×10⁻³⁶), PPP1R12C (log2FC=−2.70, FDR=2.38×10⁻³⁵)  
**Standardized pathway:** Reactome RHO GTPase cycle (R-BTA-9013406, R-BTA-9696264, R-BTA-9696270); KEGG Hippo signaling pathway  
**Explanation:** ARHGAP33 and ACAP3 are Rho-GAP family proteins that inactivate Rho GTPases; SCRIB interacts with ARHGEF7 (STRING confidence=0.997) and participates in Rho GTPase cycle pathways; PPP1R12C regulates myosin phosphatase activity linked to cytoskeletal contractility. Coordinate downregulation suggests reduced Rho-mediated cytoskeletal remodeling capacity in RA synovium.  
**Evidence strength:** Multiple genes with strong direct statistics; Reactome pathway membership for SCRIB; STRING interaction evidence for SCRIB-ARHGEF7.  
**Major limitation:** ARHGAP27P1 is a pseudogene, reducing its functional interpretability. Rho GTPase signaling is ubiquitous; downregulation here is non-specific without cell-type resolution.

### Program 4: Non-Coding RNA Regulatory Landscape
**Direction:** Downregulated  
**Major supporting genes:** MIR3154 (log2FC=−5.10, FDR=5.97×10⁻⁴³), MIR3183 (log2FC=−4.61, FDR=5.46×10⁻⁴⁷), MIR3615 (log2FC=−4.13, FDR=4.24×10⁻⁴³), MIR937 (log2FC=−3.70, FDR=2.03×10⁻⁴²), MIR647 (log2FC=−3.83, FDR=4.68×10⁻⁴⁰), MIR1301 (log2FC=−3.65, FDR=1.66×10⁻³⁵), SCARNA17 (log2FC=−3.83, FDR=1.88×10⁻⁴¹), SNORD167 (log2FC=−3.28, FDR=1.71×10⁻³⁸), RNA5-8SN2/3/4 (log2FC ≈ −4.6 to −5.1), multiple antisense/lincRNAs (PCGF3-AS1, CXXC5-AS1, DM1-AS, TNK2-AS1, TBX2-AS1, IRAIN, ARHGEF17-AS1)  
**Standardized pathway:** No specific pathway annotations retrieved for this group  
**Explanation:** The breadth of downregulated miRNAs, snoRNAs, snRNAs, and antisense transcripts indicates a broad reduction in non-coding RNA output. This could reflect altered transcriptional regulation, loss of specific cell populations that express these ncRNAs, or coordinate epigenetic silencing. The mitochondrial RNA5-8SN paralogs and ND1 (log2FC=−3.60, FDR=3.74×10⁻³⁵) may additionally signal altered mitochondrial transcript abundance.  
**Evidence strength:** Strong direct statistics across many independent ncRNA genes; however, no pathway or interaction evidence was retrieved to connect them functionally.  
**Major limitation:** Without target-mRNA correlation or functional annotation for most of these ncRNAs, the biological significance is unclear. Many are poorly characterized.

### Program 5: 22q11.2 Genomic Neighborhood and Zinc-Finger Transcriptional Regulation
**Direction:** Downregulated  
**Major supporting genes:** ARVCF (log2FC=−3.46, FDR=1.01×10⁻³⁸), DRD4 (log2FC=−4.24, FDR=3.72×10⁻⁴²), COMT-linked (via STRING ARVCF-COMT interaction), SIX5 (log2FC=−2.86, FDR=3.03×10⁻³⁶), DMPK (log2FC=−2.97, FDR=1.87×10⁻³⁶), ZNF316 (log2FC=−3.24, FDR=2.92×10⁻⁴⁸), ZNF219 (log2FC=−2.71, FDR=3.03×10⁻³⁷), ZNF444 (log2FC=−2.46, FDR=1.91×10⁻³⁶), ZNF580 (log2FC=−2.76, FDR=3.52×10⁻³⁶), ZSWIM9 (log2FC=−4.01, FDR=2.11×10⁻⁵⁰)  
**Standardized pathway:** No specific pathway retrieved; GO molecular function: protein binding (ARVCF); STRING interactions: ARVCF-COMT, ARVCF-CTNNB1  
**Explanation:** ARVCF and DRD4 map to the 22q11.2 region (DiGeorge/VCFS critical region); their coordinate downregulation, along with nearby COMT interactions, suggests possible coordinate regulatory effects or copy-number variation. Separately, multiple zinc-finger transcription factors (ZNF316, ZNF219, ZNF444, ZNF580, ZSWIM9) are downregulated, suggesting reduced transcriptional regulatory complexity. SIX5 and DMPK, both at 19q13.32 (DM1 locus), are also co-downregulated with DM1-AS, suggesting coordinate regulation at this locus as well.  
**Evidence strength:** Strong direct statistics; STRING supports ARVCF-COMT physical interaction (confidence=0.897). Genomic co-localization is annotation-based, not interaction-based.  
**Major limitation:** Coordinate downregulation of neighboring genes can arise from technical artifacts (batch effects, probe density) or copy-number differences, and does not necessarily indicate a shared regulatory mechanism.

---

## 3. Key Genes and Interaction Modules

| Gene/Module | Direction | Role in Core Programs | Gene-gene Relationship Evidence |
|---|---|---|---|
| **SCRIB** | Downregulated (log2FC=−3.24, FDR=1.32×10⁻⁴²) | Cytoskeletal polarity (Program 2), Rho GTPase modulation (Program 3) | STRING: direct physical/functional interactions with ARHGEF7 (conf=0.997), VANGL2 (0.996), GIT1 (0.983), UBE3A (0.980), LLGL1 (0.964). Reactome: RHO GTPase cycle co-membership. |
| **ARVCF** | Downregulated (log2FC=−3.46, FDR=1.01×10⁻³⁸) | 22q11.2 neighborhood (Program 5), cell adhesion | STRING: direct interaction with COMT (conf=0.897), CTNNB1 (0.804), ERBIN (0.831). These are physical/functional interactions. |
| **APC2** | Downregulated (log2FC=−3.02, FDR=4.63×10⁻³⁹) | Cytoskeletal/Wnt-Hippo signaling (Program 2) | KEGG: Hippo signaling pathway co-membership. STRING: interacts with CTNNB1 via the broader Wnt pathway network. Pathway co-membership, not confirmed direct physical interaction in this dataset. |
| **MUC5B / MUC6 / MUC12 module** | All downregulated (log2FC=−4.43, −3.85, −4.27) | Mucin/epithelial barrier (Program 1) | STRING: MUC12, MUC5B, MUC6 connected via MUC1, MUC2, MUC5AC, MUC7 connector nodes. These are STRING functional association edges, not confirmed direct physical interactions. |
| **CROCC / CROCC2** | Downregulated (log2FC=−3.88, −4.99) | Ciliary rootlet structure (Program 2) | STRING: connected via LRRC45 connector node. Functional/putative co-membership; no direct physical interaction evidence supplied. |
| **ZNF316** | Downregulated (log2FC=−3.24, FDR=2.92×10⁻⁴⁸) | Zinc-finger transcriptional regulation (Program 5) | No STRING or Reactome interaction evidence retrieved. Genomic co-localization with other ZNF genes is annotation-based. |
| **DMPK / SIX5 / DM1-AS** | All downregulated (log2FC=−2.97, −2.86, −3.65) | 19q13.32 DM1 locus coordinate regulation (Program 5) | Genomic co-localization at the DM1 locus. DM1-AS is an antisense transcript to DMPK, suggesting regulatory relationship. This is a putative regulatory interaction based on genomic context, not experimentally confirmed in this dataset. |
| **MIR3154** | Downregulated (log2FC=−5.10, FDR=5.97×10⁻⁴³) | Non-coding RNA regulatory landscape (Program 4) | No target or interaction evidence retrieved. Insufficient evidence for specific miRNA-mRNA regulatory relationships. |
| **CDHR5** | Downregulated (log2FC=−4.22, FDR=1.61×10⁻⁴⁵) | Epithelial barrier/adhesion (Program 1) | GO: plasma membrane localization. No direct interaction evidence retrieved for RA context. |
| **NOL3 / PIDD1** | Both downregulated (log2FC=−2.45, −2.89) | Apoptosis-related module | STRING: both connected via CASP2 connector node. Pathway co-membership/putative functional association; not a confirmed direct physical interaction in this dataset. |

---

## 4. Validation Priorities

### Priority 1: Tissue Composition and Sourcing Confounding Check
**Classification:** Confounding or composition check  
**Why:** The mucin/epithelial program (MUC5B, MUC6, MUC12, CDHR5) is not expected in synovial tissue. Its presence among the most significant downregulated genes raises the possibility that control samples were not synovial tissue, or that contamination occurred.  
**Current dataset evidence:** Four mucin/epithelial genes with extreme log2FC (−3.85 to −4.43) and FDR < 10⁻³⁵.  
**External evidence:** GTEx expression data (retrieved for 61/100 genes) could be used to check whether these genes are normally expressed in synovial tissue. Insufficient evidence from the current retrieval to confirm tissue origin.  
**Next step:** Verify tissue source metadata for all samples; perform GTEx-based expression profiling of MUC5B, MUC6, MUC12, CDHR5 across tissue types to confirm whether control tissue was synovial. If controls were non-synovial, re-analysis with matched tissue controls is essential.  
**Conclusion status:** Exploratory hypothesis

### Priority 2: Mucin-Barrier Loss as a Biomarker of Tissue Remodeling
**Classification:** Biomarker  
**Why:** If the tissue sourcing is confirmed correct, coordinate downregulation of mucins and epithelial adhesion molecules could reflect synovial tissue remodeling with loss of mesothelial/epithelial-like cells.  
**Current dataset evidence:** MUC12, MUC5B, MUC6, CDHR5 all downregulated with FDR < 10⁻³⁵.  
**External evidence:** STRING network evidence supports mucin functional grouping. No RA-specific literature evidence was retrieved for these genes in synovial tissue. Insufficient evidence for RA disease-association.  
**Next step:** Perform immunohistochemistry for MUC5B and CDHR5 on RA versus normal synovial tissue sections to confirm protein-level loss and identify which cell types express these markers.  
**Conclusion status:** Exploratory hypothesis

### Priority 3: SCRIB-Mediated Rho GTPase and Cell Polarity Axis
**Classification:** Mechanistic hypothesis  
**Why:** SCRIB is a well-characterized cell polarity scaffold protein with STRING-confirmed interactions (ARHGEF7, VANGL2, GIT1) and Reactome Rho GTPase pathway membership. Its downregulation, combined with coordinate loss of ARHGAP33 and ACAP3, suggests impaired Rho-mediated cytoskeletal dynamics.  
**Current dataset evidence:** SCRIB (log2FC=−3.24, FDR=1.32×10⁻⁴²), ARHGAP33 (log2FC=−3.20, FDR=1.67×10⁻³⁶), ACAP3 (log2FC=−2.80, FDR=2.27×10⁻³⁸).  
**External evidence:** STRING interactions (SCRIB-ARHGEF7 confidence=0.997) and Reactome pathway membership are external annotations, not RA-specific validation. No RA-specific literature was retrieved for SCRIB in synovial tissue.  
**Next step:** Test whether SCRIB knockdown in synovial fibroblasts alters RhoA/Cdc42 activity, cell migration, and invasive phenotype in vitro; validate SCRIB protein expression in RA versus control synovium by Western blot or immunofluorescence.  
**Conclusion status:** Supported hypothesis (for the mechanistic axis); exploratory for RA specificity

### Priority 4: 22q11.2 and 19q13.32 Coordinate Regulation as Interaction/Network Hypothesis
**Classification:** Interaction / network hypothesis  
**Why:** ARVCF and DRD4 (22q11.2) and DMPK, SIX5, DM1-AS (19q13.32) show coordinate downregulation, suggesting potential cis-regulatory or copy-number effects.  
**Current dataset evidence:** ARVCF (FDR=1.01×10⁻³⁸), DRD4 (FDR=3.72×10⁻⁴²), DMPK (FDR=1.87×10⁻³⁶), SIX5 (FDR=3.03×10⁻³⁶), DM1-AS (FDR=1.71×10⁻⁴⁰).  
**External evidence:** STRING confirms ARVCF-COMT physical interaction (conf=0.897). Genomic co-localization is annotation-based. No RA-specific copy-number data was supplied.  
**Next step:** Perform array CGH or SNP-array copy-number analysis on RA and control synovial tissue to determine whether 22q11.2 or 19q13.32 deletions/polymorphisms underlie the coordinate downregulation; check whether these loci show methylation differences.  
**Conclusion status:** Exploratory hypothesis

### Priority 5: Non-Coding RNA Panel as Potential RA Synovial Biomarkers
**Classification:** Biomarker  
**Why:** The large number of downregulated miRNAs (MIR3154, MIR3183, MIR3615, MIR937, MIR647, MIR4763, MIR4492, MIR6821, MIR4730, MIR1301, MIR4665) and sno/snRNAs represents a distinctive regulatory signature.  
**Current dataset evidence:** All miRNAs downregulated with FDR < 10⁻³⁵; MIR3154 has the largest effect (log2FC=−5.10).  
**External evidence:** PubMed record [30349310] reports MIR647 involvement in NF-κB signaling in non-small cell lung cancer, but this is not RA-specific evidence. No RA-specific miRNA literature was retrieved for the panel. Insufficient evidence for RA disease-association for the remaining miRNAs.  
**Next step:** Validate top miRNAs (MIR3154, MIR3183, MIR647) by qRT-PCR in an independent RA synovial cohort; correlate with disease activity scores (DAS28); perform miRNA target prediction and integrate with any available upregulated mRNA data from the same study.  
**Conclusion status:** Exploratory hypothesis

---

## 5. Evidence Grounding

| Conclusion | Direct Input Evidence | Pathway/Ontology | Protein/Regulatory Network | Disease-Association | Expression/Tissue | Genetic/Clinical | Drug/Therapeutic | Literature |
|---|---|---|---|---|---|---|---|---|
| Mucin/epithelial barrier loss | ✓ (4 genes, FDR<10⁻³⁵) | — | STRING mucin functional cluster | Insufficient for RA | GTex records retrieved but not yet evaluated for tissue specificity | — | — | Insufficient for RA synovium |
| Cytoskeletal/ciliary structural loss | ✓ (5+ genes, FDR<10⁻³⁶) | GO: cytoplasm, plasma membrane; Reactome Rho GTPase | STRING: CROCC-CROCC2 via LRRC45 | Insufficient for RA | — | — | — | Insufficient for RA synovium |
| Rho GTPase modulation | ✓ (5 genes, FDR<10⁻³⁵) | Reactome RHO GTPase cycle | STRING: SCRIB-ARHGEF7 (0.997) | Insufficient for RA | — | — | — | Insufficient for RA synovium |
| Non-coding RNA landscape | ✓ (20+ ncRNA genes, FDR<10⁻³⁵) | — | — | Insufficient for RA | — | — | — | MIR647 in NF-κB (PMID 30349310, non-RA) |
| 22q11.2 / ZNF / 19q13.32 | ✓ (10+ genes, FDR<10⁻³⁶) | GO: MF protein binding (ARVCF) | STRING: ARVCF-COMT (0.897), ARVCF-CTNNB1 (0.804) | GWAS records retrieved for 100/100 genes but no RA-specific hit highlighted | — | ClinVar records retrieved for 79/100 genes; no RA-specific variant highlighted | — | Insufficient for RA synovium |

**Evidence independence note:** STRING, Reactome, QuickGO, and GO annotations may share underlying publications and database curation pipelines; they are not automatically independent. The PubMed/Europe PMC records retrieved were predominantly from cancer and cardiometabolic studies, not RA, and thus do not provide disease-specific replication. GWAS and ClinVar record coverage (100/100 and 79/100 respectively) indicates broad genetic annotation availability but does not constitute RA-specific genetic evidence without variant-level inspection.

**Conflict statement:** The absence of canonical RA inflammatory genes (e.g., TNF, IL6, CXCL family, MMPs) among the significant hits conflicts with the expected RA synovial transcriptomic signature. This conflict supports the hypothesis that the dataset may capture a non-standard aspect of RA synovial biology or may be affected by tissue-composition or sourcing issues.

---

## 6. Limitations and Alternative Explanations

1. **Tissue or cell-composition differences (highest concern):** The complete absence of upregulated genes and the dominance of mucin/epithelial genes suggest that RA and control samples may differ in tissue type or cell composition. RA synovium typically shows inflammatory infiltrates; if control tissue contained epithelial/mesothelial components not present in RA samples, this would generate the observed pattern. **Investigation:** Perform cell-type deconvolution (e.g., CIBERSORT, xCell) on the full expression matrix; confirm tissue origin by histopathology; run GTEx tissue-specificity analysis for MUC5B, MUC6, CDHR5.

2. **Batch or platform effects:** Coordinate downregulation of genes from specific genomic regions (22q11.2, 19q13.32) and the uniform directionality could arise from systematic batch effects, probe design bias, or normalization artifacts. **Investigation:** Check whether downregulated genes cluster by genomic position (suggesting CNV or probe-density artifacts); examine PCA plots for batch separation; verify probe sequences for key genes.

3. **Disease severity, treatment exposure, and disease stage:** RA synovial tissue from patients on DMARD/biologic therapy may show suppressed inflammatory gene expression. If all RA samples were from treated patients, the expected inflammatory upregulation could be muted. **Investigation:** Stratify analysis by treatment status, disease duration, and DAS28 if metadata are available.

4. **Association-versus-causation ambiguity:** All findings are cross-sectional differential expression associations. No causal relationship between any gene and RA pathogenesis can be inferred. Downregulation may be a consequence rather than a driver of disease. **Investigation:** Functional validation (knockdown/overexpression in synovial fibroblasts) is required for any mechanistic claim.

5. **Broad or nonspecific pathway enrichment:** The KEGG pathways retrieved (Ribosome biogenesis, Ribosome, Hippo signaling) are broad cellular processes and may not be specifically informative for RA. The GO terms (protein binding, nucleus, plasma membrane) are similarly nonspecific. **Investigation:** Perform more targeted pathway analysis using RA-specific gene sets (e.g., Hallmark Inflammatory Response, TNF-α signaling via NF-κB) on the full expression dataset, not just the selected downregulated genes.

---

**Summary:** The uploaded data provide strong statistical evidence for coordinate downregulation of mucin/epithelial barrier genes, cytoskeletal structural components, Rho GTPase modulators, non-coding RNAs, and zinc-finger transcription factors in RA versus normal synovial tissue. However, the directional degeneracy, the unexpected mucin/epithelial signature, and the absence of canonical RA inflammatory genes raise substantial concerns about tissue composition or sourcing that must be resolved before biological conclusions can be drawn. External statistical validation was not performed, and no RA-specific literature evidence was retrieved for the key genes. The most urgent next step is verifying tissue origin and cell-type composition before proceeding to mechanistic or biomarker validation.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=46, external claims checked=0, external mismatches=0, status=passed.

Answer model API: Zhipu AI / glm-5.2

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 84/100 selected items (records returned); cbioportal 82/100 selected items (records returned); chembl 16/100 selected items (records returned); civic 1/100 selected items (records returned); clinicaltrials 19/100 selected items (records returned); clinvar 79/100 selected items (records returned); ensembl 40/100 selected items (partially returned; some queries failed); europepmc 776 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 61/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 47/100 selected items (records returned); humanbase 88/100 selected items (partially returned; some queries failed); intact 47/100 selected items (records returned); mygene 93/100 selected items (records returned); omnipath 17/100 selected items (records returned); opentargets 82/100 selected items (records returned); pubmed 483 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 50/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 51/100 selected items (records returned)
Local databases: gutmgene 0/100 selected items (reachable but no records for this batch); hmdb 8/100 selected items (records returned); string 49/100 selected items (records returned); trrust 7/100 selected items (records returned)
