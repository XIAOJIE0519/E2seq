# rheumatoid arthritis - glm-5.2

- Benchmark system: E2seq + Agent RAG
- Repeat: 1
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
- Prompt tokens: 27937
- Completion tokens: 7986
- Reasoning tokens: 0
- Total tokens: 35923
- API requests reported: 2
- Elapsed seconds: 382.098
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 984.622
- Question handoff seconds: 999.892
- Final benchmark system: E2seq; file rank 1/5; original repeat 1; model vendor: Zhipu AI

---
### Multidimensional Interpretation of Synovial Tissue Transcriptomics in Rheumatoid Arthritis

**Data-Quality Warning and Statistical Scope**
The uploaded dataset consists of 100 unique genes, all of which are statistically significant (FDR ≤ 0.05) and uniformly downregulated (log2FC range: −2.27 to −5.10) in rheumatoid arthritis (RA) synovial tissue compared to normal control. There are no upregulated genes in this input, strongly suggesting this table represents a pre-filtered subset of downregulated DEGs rather than the totality of the differential expression analysis. Furthermore, the extreme statistical significance (minimum FDR = 8.78 × 10⁻⁵⁴) and massive effect sizes suggest a very strong biological signal, though they may also indicate a small sample size or severe cellular composition shifts. External statistical validation was not performed; no independent cohort statistics are available. Therefore, all biological programs discussed below are exploratory interpretations grounded in the direct statistical evidence and contextualized by external databases, not externally replicated findings.

---

### 1. Overall Biological Interpretation

The uniform downregulation of genes in RA synovial tissue points to a set of suppressed molecular programs rather than the classical inflammatory amplification typically expected in RA. The dominant themes emerging from this cohort include: (1) loss of structural and mucosal barrier genes (MUC12, MUC5B, MUC6, CDHR5), (2) suppression of cytoskeletal and ciliary architecture components (CROCC, CROCC2, INF2, SCRIB, CCDC9), and (3) widespread downregulation of non-coding RNAs (MIR3154, MIR3183, MIR647, PCGF3-AS1, CXXC5-AS1) with potential regulatory roles. The presence of multiple zinc finger transcription factors (ZNF316, ZNF219, ZNF444, ZNF580) and chromatin-associated genes (CBX7, PAGR1, TNRC18) suggests epigenetic and transcriptional reprogramming. Notably, the absence of canonical RA inflammatory pathways (e.g., TNF, IL-6, NF-κB) in this downregulated subset suggests the input captures a counter-regulatory or tissue-structural program rather than the primary inflammatory cascade.

---

### 2. Core Biological Programs

**Program 1: Mucosal Barrier and Secreted Mucin Suppression**
- **Direction:** Downregulated
- **Major supporting genes:** MUC12 (log2FC = −4.27, FDR = 6.05 × 10⁻⁴³), MUC5B (log2FC = −4.43, FDR = 2.07 × 10⁻⁴⁰), MUC6 (log2FC = −3.85, FDR = 5.92 × 10⁻³⁶), CDHR5 (log2FC = −4.22, FDR = 1.61 × 10⁻⁴⁵)
- **Appropriate standardized pathway:** GO: Biological Process — mucin-type O-glycan biosynthesis; Reactome — Post-translational modification: synthesis of GPI-anchored proteins (overlapping via CDHR5)
- **Explanation:** The coordinated downregulation of three gel-forming and transmembrane mucins (MUC12, MUC5B, MUC6) alongside CDHR5 (cadherin-related family member 5, an intestinal barrier protein) suggests a disruption of protective epithelial or mucosal barrier function. In the synovial context, the synovial intimal lining contains fibroblast-like synoviocytes (FLS) with epithelioid features; loss of mucin expression could reflect altered lining integrity or a phenotypic shift away from a barrier-maintaining state.
- **Evidence strength:** Strong direct statistical evidence from four independent genes. STRING network evidence connects MUC12, MUC5B, and MUC6 via shared interactions with MUC2, MUC5AC, and MUC7, confirming a co-functional mucin network. Major limitation: mucins are not canonical RA synovial markers; this signal could reflect contamination from adjacent tissue or a non-FLS cellular source.

**Program 2: Ciliary and Cytoskeletal Architecture Disruption**
- **Direction:** Downregulated
- **Major supporting genes:** CROCC (log2FC = −3.88, FDR = 9.67 × 10⁻⁴⁸), CROCC2 (log2FC = −4.99, FDR = 1.22 × 10⁻⁴⁰), INF2 (log2FC = −2.76, FDR = 8.10 × 10⁻³⁶), SCRIB (log2FC = −3.24, FDR = 1.32 × 10⁻⁴²), CCDC9 (log2FC = −3.02, FDR = 1.93 × 10⁻⁴⁴)
- **Appropriate standardized pathway:** GO: Cellular Component — cilium axoneme; Reactome — Hair bundle morphogenesis (overlapping)
- **Explanation:** CROCC (rootletin) and CROCC2 are critical structural components of ciliary rootlets. INF2 is a formin-family actin regulator involved in mitochondrial and cytoskeletal dynamics. SCRIB is a scaffolding protein regulating cell polarity and migration. CCDC9 is a coiled-coil domain protein of unknown function but likely cytoskeletal. Collectively, these genes suggest suppression of primary cilia or cytoskeletal polarity programs. Synoviocytes possess primary cilia that sense mechanical stress and modulate inflammatory signaling; their structural disruption could contribute to altered mechanotransduction in RA.
- **Evidence strength:** Strong direct evidence across five genes with large effect sizes. STRING links CROCC and CROCC2 via LRRC45 (a ciliary rootlet coiled-coil protein), confirming a physical interaction network. Limitation: ciliary gene expression is highly cell-type-specific; downregulation could simply reflect loss of ciliated cells rather than active program suppression.

**Program 3: Non-Coding RNA Regulatory Network Suppression**
- **Direction:** Downregulated
- **Major supporting genes:** MIR3154 (log2FC = −5.10, FDR = 5.97 × 10⁻⁴³), MIR3183 (log2FC = −4.61, FDR = 5.46 × 10⁻⁴⁷), MIR647 (log2FC = −3.83, FDR = 4.68 × 10⁻⁴⁰), MIR937 (log2FC = −3.70, FDR = 2.03 × 10⁻⁴²), PCGF3-AS1 (log2FC = −3.52, FDR = 1.10 × 10⁻⁴⁶), CXXC5-AS1 (log2FC = −3.93, FDR = 1.44 × 10⁻⁴¹), DM1-AS (log2FC = −3.65, FDR = 1.71 × 10⁻⁴⁰), TBX2-AS1 (log2FC = −3.85, FDR = 5.85 × 10⁻³⁸), TNK2-AS1 (log2FC = −3.71, FDR = 4.80 × 10⁻³⁸), IRAIN (log2FC = −3.26, FDR = 1.44 × 10⁻³⁵)
- **Appropriate standardized pathway:** No standardized KEGG/Hallmark pathway; GO: Biological Process — regulation of transcription, DNA-templated (for antisense lncRNAs)
- **Explanation:** The dataset contains a striking cluster of downregulated microRNAs (miRNAs) and antisense long non-coding RNAs (lncRNAs). PCGF3-AS1, CXXC5-AS1, DM1-AS, TBX2-AS1, TNK2-AS1, and IRAIN are all natural antisense transcripts that regulate their sense-strand partners or broader chromatin states. Their coordinated suppression suggests a large-scale de-repression of regulatory targets or a shift in the epigenetic landscape. For miRNAs (MIR3154, MIR3183, MIR647, MIR937), downregulation could release brakes on inflammatory or proliferative programs, though their specific RA synovial targets are largely uncharacterized.
- **Evidence strength:** Strong direct statistical evidence from >10 non-coding RNA genes. However, functional annotation of these ncRNAs in RA synovium is sparse; literature evidence for MIR647 exists in cancer (PMID: 30349310) but not RA. Limitation: ncRNA function is highly context-dependent, and target prediction without experimental validation is insufficient evidence.

**Program 4: Wnt/Hippo Signaling and Cell Polarity Suppression**
- **Direction:** Downregulated
- **Major supporting genes:** APC2 (log2FC = −3.02, FDR = 4.63 × 10⁻³⁹), SCRIB (log2FC = −3.24, FDR = 1.32 × 10⁻⁴²), ARVCF (log2FC = −3.46, FDR = 1.01 × 10⁻³⁸), GJC2 (log2FC = −3.50, FDR = 5.11 × 10⁻⁴⁰), ARHGAP33 (log2FC = −3.20, FDR = 1.67 × 10⁻³⁶)
- **Appropriate standardized pathway:** KEGG: Hippo signaling pathway; Reactome — Signaling by Wnt (via APC2)
- **Explanation:** APC2 is a negative regulator of Wnt signaling (β-catenin destruction complex). SCRIB and ARVCF are cell polarity scaffolds that interact with β-catenin (CTNNB1, per STRING evidence). GJC2 (gap junction gamma-2) mediates intercellular communication. ARHGAP33 is a Rho-GAP regulating cytoskeletal dynamics. The coordinated downregulation of these genes suggests suppression of cell polarity, cell-cell adhesion, and contact inhibition pathways. In RA, loss of polarity and adhesion in FLS is associated with invasive phenotype acquisition.
- **Evidence strength:** Moderate direct evidence from five genes. KEGG retrieval specifically identified "Hippo signaling pathway" for this gene set, providing independent pathway-level support. STRING network evidence links APC2 and ARVCF via shared interaction with CTNNB1. Limitation: these genes span multiple pathways; attributing the signal specifically to Hippo/Wnt requires pathway-level enrichment testing that was not performed in this analysis.

**Program 5: Zinc Finger and Chromatin Transcriptional Reprogramming**
- **Direction:** Downregulated
- **Major supporting genes:** ZNF316 (log2FC = −3.24, FDR = 2.92 × 10⁻⁴⁸), ZNF219 (log2FC = −2.71, FDR = 3.03 × 10⁻³⁷), ZNF444 (log2FC = −2.46, FDR = 1.91 × 10⁻³⁶), ZNF580 (log2FC = −2.76, FDR = 3.52 × 10⁻³⁶), CBX7 (log2FC = −2.41, FDR = 1.43 × 10⁻³⁵), PAGR1 (log2FC = −2.34, FDR = 1.17 × 10⁻³⁶), TNRC18 (log2FC = −3.04, FDR = 2.36 × 10⁻³⁷)
- **Appropriate standardized pathway:** GO: Cellular Component — nucleus; GO: Biological Process — regulation of transcription, DNA-templated
- **Explanation:** Multiple zinc finger transcription factors (ZNF316, ZNF219, ZNF444, ZNF580) alongside polycomb-associated (CBX7, PAGR1) and chromatin-binding (TNRC18) genes suggest coordinated suppression of specific transcriptional programs. CBX7 is a polycomb repressive complex 1 component that maintains transcriptional repression. Their downregulation could de-repress genes involved in inflammation or cell proliferation, though the specific target programs are unknown.
- **Evidence strength:** Moderate direct evidence from seven genes. GO annotations confirm nuclear localization for CEMP1, FLYWCH1, PAGR1, SCAF1, and SH2B1. However, functional targets of these specific ZNFs in RA are largely uncharacterized. Limitation: zinc finger genes are numerous and often poorly annotated; their collective downregulation could be a non-specific consequence of broad chromatin remodeling.

---

### 3. Key Genes and Interaction Modules

| # | Gene/Module | Statistical Direction | Role in Core Programs | Nature of Gene-Gene Relationship |
|---|---|---|---|---|
| 1 | **CROCC** | Downregulated (log2FC = −3.88, FDR = 9.67 × 10⁻⁴⁸) | Central ciliary rootlet component; Program 2 | Direct physical interaction with CROCC2 via LRRC45 (STRING) |
| 2 | **MUC5B** | Downregulated (log2FC = −4.43, FDR = 2.07 × 10⁻⁴⁰) | Gel-forming mucin; Program 1 | Pathway co-membership with MUC12, MUC6 via STRING links to MUC2, MUC5AC, MUC7 |
| 3 | **SCRIB** | Downregulated (log2FC = −3.24, FDR = 1.32 × 10⁻⁴²) | Cell polarity scaffold; Programs 2 & 4 | Direct physical interaction with ARHGEF7, VANGL2, GIT1, UBE3A (STRING) |
| 4 | **APC2** | Downregulated (log2FC = −3.02, FDR = 4.63 × 10⁻³⁹) | Wnt pathway negative regulator; Program 4 | Pathway co-membership with ARVCF via shared CTNNB1 interaction (STRING) |
| 5 | **MIR3154** | Downregulated (log2FC = −5.10, FDR = 5.97 × 10⁻⁴³) | Largest-magnitude miRNA suppression; Program 3 | Insufficient evidence for direct targets in RA |
| 6 | **PCGF3-AS1** | Downregulated (log2FC = −3.52, FDR = 1.10 × 10⁻⁴⁶) | Antisense lncRNA to PCGF3 (polycomb); Program 3 | Regulatory interaction (antisense) with PCGF3 locus; co-expression inferred |
| 7 | **CDHR5** | Downregulated (log2FC = −4.22, FDR = 1.61 × 10⁻⁴⁵) | Cadherin family barrier protein; Program 1 | Pathway co-membership with mucin network; no direct physical interaction evidence among selected genes |
| 8 | **CBX7** | Downregulated (log2FC = −2.41, FDR = 1.43 × 10⁻³⁵) | Polycomb chromatin silencer; Program 5 | Regulatory interaction (polycomb complex); no direct physical interaction evidence among selected genes |
| 9 | **ARVCF** | Downregulated (log2FC = −3.46, FDR = 1.01 × 10⁻³⁸) | Cell adhesion/polarity; Programs 2 & 4 | Direct physical interaction with CTNNB1, COMT, ERBIN (STRING) |
| 10 | **Mucin module (MUC12/MUC5B/MUC6)** | All downregulated (FDR < 10⁻³⁶) | Secreted/membrane mucin network; Program 1 | STRING network: shared interactions with MUC2, MUC5AC, MUC7; pathway co-membership |

---

### 4. Validation Priorities

**Priority 1: Confounding or Composition Check — Ciliated Epithelial or Mucosal Cell Contamination**
- **Why:** The mucin cluster (MUC12, MUC5B, MUC6) and ciliary genes (CROCC, CROCC2) are not canonical RA synovial markers. Their uniform downregulation could reflect differences in tissue composition (e.g., synovial samples with less adjacent mucosal/epithelial contamination than controls) rather than disease-specific transcriptional changes.
- **Current dataset evidence:** Four mucin genes and two ciliary rootlet genes are among the most significantly downregulated genes.
- **External evidence:** GTEx data available for 61/100 genes; HPA has records for 47/100 genes, enabling tissue-specificity checks. Mucin expression is characteristically high in gastrointestinal and respiratory tissues but low in synovium.
- **Next step:** Perform cell-type deconvolution (e.g., CIBERSORTx, xCell) on the original expression matrix; confirm tissue origin via histological review of synovial samples.
- **Conclusion status:** Exploratory hypothesis

**Priority 2: Mechanistic Hypothesis — Synoviocyte Ciliary Mechanotransduction in RA**
- **Why:** Primary cilia on synoviocytes regulate mechanosensing and inflammatory signaling. Coordinated downregulation of CROCC, CROCC2, and INF2 could impair ciliary structure and alter mechanotransduction, contributing to pathological FLS activation.
- **Current dataset evidence:** Three cytoskeletal/ciliary genes with large effect sizes (log2FC < −2.7) and extreme FDR values.
- **External evidence:** STRING confirms CROCC–CROCC2 interaction via LRRC45. No RA-specific ciliary literature was retrieved in the PubMed search, though primary cilia biology in RA has been reported elsewhere.
- **Next step:** Immunofluorescence for CROCC/rootletin and acetylated α-tubulin in RA vs. control synovial tissue; assess ciliary frequency and length.
- **Conclusion status:** Exploratory hypothesis

**Priority 3: Interaction / Network Hypothesis — Wnt/β-Catenin–Polarity Axis (APC2–ARVCF–SCRIB)**
- **Why:** These three genes converge on β-catenin regulation and cell polarity. Their coordinated suppression could release proliferative and invasive programs in FLS, relevant to pannus formation.
- **Current dataset evidence:** All three downregulated with FDR < 10⁻³⁸; KEGG identified Hippo signaling pathway enrichment.
- **External evidence:** STRING confirms APC2–CTNNB1 and ARVCF–CTNNB1 direct physical interactions; SCRIB interacts with ARHGEF7 (a Rac/Cdc42 GEF). No independent RA cohort validation is available.
- **Next step:** Co-immunoprecipitation or proximity ligation for APC2/ARVCF/β-catenin in RA FLS; assess β-catenin transcriptional activity (TOPFLASH reporter) when these genes are knocked down.
- **Conclusion status:** Exploratory hypothesis

**Priority 4: Biomarker — Circulating MIR3154 and MIR3183 as RA Activity Markers**
- **Why:** These miRNAs show the largest magnitudes of suppression (log2FC −5.10 and −4.61, respectively) and could serve as non-invasive biomarkers if detectable in serum or synovial fluid.
- **Current dataset evidence:** Two miRNAs with extreme effect sizes and FDR < 10⁻⁴⁶.
- **External evidence:** No RA-specific literature was retrieved for these miRNAs. Literature for MIR647 exists in cancer (PMID: 30349310) but not RA. Disease-association databases (GWAS catalog: 100/100 genes queried; ClinVar: 79/100 genes queried) may contain records but were not specifically filtered for RA.
- **Next step:** qRT-PCR for MIR3154 and MIR3183 in paired serum and synovial fluid from RA patients vs. controls; correlate with DAS28 or CRP.
- **Conclusion status:** Exploratory hypothesis

**Priority 5: Therapeutic Target — Mucin/Barrier Restoration as Adjunct Strategy**
- **Why:** If the mucin downregulation is disease-specific (not a composition artifact), it suggests loss of a protective barrier in the synovial lining, potentially exposing underlying stroma to inflammatory damage.
- **Current dataset evidence:** Three mucin genes and CDHR5 downregulated with FDR < 10⁻³⁶.
- **External evidence:** No RA-specific mucin therapy literature was retrieved. ChEMBL records exist for 16/100 selected genes, but mucin-targeted therapies are not established in RA. The existence of mucin biology in other diseases (e.g., cystic fibrosis, MUC5B in idiopathic pulmonary fibrosis) is not transferable evidence for RA therapeutic efficacy.
- **Next step:** Confirm mucin expression in synovial intimal lining by RNAscope or in situ hybridization; if confirmed, assess whether barrier disruption correlates with synovitis severity.
- **Conclusion status:** Exploratory hypothesis

---

### 5. Evidence Grounding

| Conclusion | Direct Input Evidence | Pathway/Ontology | Protein/Regulatory Network | Disease/Genetic | Expression/Tissue | Drug/Therapeutic | Published Literature |
|---|---|---|---|---|---|---|---|
| Mucin barrier suppression | MUC12, MUC5B, MUC6, CDHR5 all downregulated (FDR < 10⁻³⁶) | GO: mucin-type O-glycan biosynthesis | STRING: MUC12/MUC5B/MUC6 linked via MUC2, MUC5AC, MUC7 | GWAS records available for 100/100 genes; no RA-specific filtering performed | GTEx: 61/100 genes queried; mucin tissue specificity expected but not explicitly verified | Insufficient evidence | Insufficient evidence for RA-specific mucin literature |
| Ciliary/cytoskeletal disruption | CROCC, CROCC2, INF2, CCDC9 downregulated (FDR < 10⁻³⁶) | GO: cilium axoneme (inferred) | STRING: CROCC–CROCC2 via LRRC45 (direct physical interaction evidence) | Insufficient evidence | HPA: 47/100 genes queried; CROCC tissue expression not explicitly verified | Insufficient evidence | Insufficient evidence for RA-specific ciliary literature |
| ncRNA regulatory suppression | 10+ miRNAs and antisense lncRNAs downregulated | GO: regulation of transcription (antisense lncRNAs) | Insufficient evidence for target networks | Insufficient evidence | Insufficient evidence | Insufficient evidence | MIR647 in cancer (PMID: 30349310); no RA literature |
| Wnt/Hippo polarity axis | APC2, SCRIB, ARVCF, GJC2, ARHGAP33 downregulated | KEGG: Hippo signaling pathway (retrieved) | STRING: APC2–CTNNB1, ARVCF–CTNNB1 (direct physical interactions); SCRIB–ARHGEF7 | Insufficient evidence | Insufficient evidence | Insufficient evidence | Insufficient evidence for this specific gene combination in RA |
| Zinc finger/chromatin reprogramming | ZNF316, ZNF219, ZNF444, ZNF580, CBX7, PAGR1, TNRC18 downregulated | GO: nucleus (confirmed for subset) | Insufficient evidence among selected genes | Insufficient evidence | Insufficient evidence | Insufficient evidence | Insufficient evidence |

**Independence assessment:** The KEGG pathway retrieval ("Hippo signaling pathway," "Ribosome biogenesis") and STRING interaction evidence are derived from separate databases but ultimately draw on overlapping experimental literature for their annotations. They should not be treated as fully independent evidence layers. The direct input statistics are the only fully independent evidence layer.

---

### 6. Limitations and Alternative Explanations

1. **Tissue or cell-composition differences (most critical):** The mucin and ciliary gene clusters are strongly suggestive of epithelial or ciliated cell types that are not predominant in synovial tissue. The uniform downregulation could arise if RA synovial samples contain proportionally fewer of these cells than controls (e.g., due to sampling differences, stromal expansion in RA, or adjacent tissue contamination in controls). This should be investigated via cell-type deconvolution and histological review.

2. **Pre-filtered input bias:** The dataset contains only downregulated genes with no upregulated counterpart. This pre-selection means the interpretation is inherently biased toward suppressive programs and cannot capture the full RA transcriptomic landscape, including the expected upregulation of inflammatory mediators. Any "dominant theme" identified here applies only to the downregulated subset.

3. **Treatment exposure:** RA patients are typically treated with DMARDs, biologics, or glucocorticoids, any of which could suppress specific gene programs. The dataset does not include treatment metadata; the downregulated ncRNA and chromatin programs could partly reflect medication effects rather than intrinsic disease biology.

4. **Association-versus-causation ambiguity:** The cross-sectional design cannot establish whether gene downregulation is a cause or consequence of RA pathology. For example, CROCC downregulation could lead to ciliary dysfunction (causal) or could be a secondary consequence of FLS phenotypic transformation (consequential). This distinction requires longitudinal or perturbation studies.

5. **Batch or platform effects:** The extreme statistical significance values (P values as low as 10⁻⁵⁸) can arise from small sample sizes with low variance within groups, potentially amplified by batch effects. Without access to sample sizes, normalization methods, or batch correction details, the magnitude of the effect sizes should be interpreted cautiously.

---

**Summary:** The uploaded downregulated gene set in RA synovial tissue reveals a coordinated suppression of mucosal barrier, ciliary/cytoskeletal, non-coding RNA regulatory, Wnt/Hippo polarity, and zinc finger/chromatin programs. The strongest convergent evidence supports ciliary-cytoskeletal and mucin-barrier programs based on multiple genes with consistent directionality and external network support, while the ncRNA and chromatin programs remain exploratory due to limited functional annotation in RA. External statistical validation was not performed; all findings should be considered exploratory hypotheses pending independent cohort replication and experimental validation.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=40, external claims checked=0, external mismatches=0, status=passed.

Answer model API: Zhipu AI / glm-5.2

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 84/100 selected items (records returned); cbioportal 82/100 selected items (records returned); chembl 16/100 selected items (records returned); civic 1/100 selected items (records returned); clinicaltrials 19/100 selected items (records returned); clinvar 79/100 selected items (records returned); ensembl 40/100 selected items (partially returned; some queries failed); europepmc 776 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 61/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 47/100 selected items (records returned); humanbase 88/100 selected items (partially returned; some queries failed); intact 47/100 selected items (records returned); mygene 93/100 selected items (records returned); omnipath 17/100 selected items (records returned); opentargets 82/100 selected items (records returned); pubmed 483 articles / initial full-cohort RAG 100 queries + 3 current-round queries; some queries failed; quickgo 50/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 51/100 selected items (records returned)
Local databases: gutmgene 0/100 selected items (reachable but no records for this batch); hmdb 8/100 selected items (records returned); string 49/100 selected items (records returned); trrust 7/100 selected items (records returned)
