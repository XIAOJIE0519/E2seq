# rheumatoid arthritis - glm-5.2

- Benchmark system: E2seq + Agent RAG
- Repeat: 7
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
- Prompt tokens: 30487
- Completion tokens: 12776
- Reasoning tokens: 0
- Total tokens: 43263
- API requests reported: 2
- Elapsed seconds: 209.626
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 984.622
- Question handoff seconds: 999.892
- Final benchmark system: E2seq; file rank 5/5; original repeat 7; model vendor: Zhipu AI

---
## 1. Overall Biological Interpretation

**Data-quality warning:** The uploaded dataset is technically suspicious in two respects. First, all 100 selected genes are uniformly downregulated (direction counts: downregulated=100; no upregulated genes), which is unusual for a RA-versus-control synovial tissue comparison where both induced and repressed programs are expected. Second, the P-value and FDR distributions are extremely compressed (all FDR ≤ ~4.3 × 10⁻³⁵), suggesting potential saturation, extreme sample-size inflation, or a pre-filtered top-list rather than a genome-wide differential analysis. The statistical values are preserved as supplied, but direct biological interpretation should be treated as exploratory pending independent confirmation.

Despite these caveats, the downregulated genes converge on several coherent biological themes relevant to rheumatoid arthritis synovial biology. The dominant signals include: (1) mucosal/epithelial barrier and secreted glycoprotein components (MUC5B, MUC6, MUC12, CDHR5), whose reduction is consistent with loss or downregulation of synovial fibroblast-like synoviocyte (FLS) subpopulations maintaining barrier-like or mucin-expressing phenotypes; (2) cytoskeletal architecture and ciliary/rootlet proteins (CROCC, CROCC2, INF2, SCRIB, APC2), pointing to disruption of cell polarity, migration, and primary cilia function—structures increasingly recognized in synovial joint pathobiology; (3) GTPase signaling and small-GTPase regulatory machinery (ARHGAP33, ACAP3, ARHGAP27P1, ARHGEF17-AS1, SH2B1), which modulate cytoskeletal dynamics, Ras/MAPK, and inflammatory signaling; (4) zinc-finger transcriptional and chromatin regulators (ZNF316, ZNF219, ZNF444, ZNF580, CBX7, TNRC18, PAGR1), suggesting epigenetic rewiring or loss of a specific transcriptional program; and (5) a cluster of non-coding RNAs (MIR3154, MIR3183, MIR937, MIR647, DM1-AS, IRAIN, PCGF3-AS1) that may regulate post-transcriptional and epigenetic pathways. The collective downregulation of these programs may reflect either disease-associated loss of protective synovial functions or compositional shifts in cell types between RA and control synovium.

## 2. Core Biological Programs

### Program 1: Mucosal/Barrier Glycoprotein Program
- **Direction:** Downregulated
- **Major supporting genes:** MUC5B (log2FC = −4.43, FDR = 2.07 × 10⁻⁴⁰), MUC6 (log2FC = −3.85, FDR = 5.92 × 10⁻³⁶), MUC12 (log2FC = −4.27, FDR = 6.05 × 10⁻⁴³), CDHR5 (log2FC = −4.22, FDR = 1.61 × 10⁻⁴⁵)
- **Standardized pathway:** GO biological process — O-glycan processing (GO:0006491); Reactome — O-linked glycosylation of mucins (R-HSA-5173105)
- **Explanation:** Multiple mucin family members and the cadherin-related CDHR5 are co-downregulated. STRING network evidence links MUC5B, MUC6, and MUC12 through shared interactions with MUC1, MUC2, MUC5AC, and MUC7. In RA synovium, mucin-like glycoproteins contribute to lubrication and barrier protection; their loss may reflect erosion of a protective lining or a shift in FLS secretory phenotype.
- **Evidence strength:** Direct statistical evidence (strong log2FC and FDR) from the input dataset; STRING co-membership in mucin family network. **Limitation:** STRING edges within the mucin family may reflect sequence homology and shared domain annotations rather than functional interactions; the biological relevance of mucin downregulation specifically in RA synovium requires literature and experimental confirmation.

### Program 2: Cytoskeletal Organization and Cell Polarity
- **Direction:** Downregulated
- **Major supporting genes:** CROCC (log2FC = −3.88, FDR = 9.67 × 10⁻⁴⁸), CROCC2 (log2FC = −4.99, FDR = 1.22 × 10⁻⁴⁰), INF2 (log2FC = −2.76, FDR = 8.10 × 10⁻³⁶), SCRIB (log2FC = −3.24, FDR = 1.32 × 10⁻⁴²), APC2 (log2FC = −3.02, FDR = 4.63 × 10⁻³⁹), ARVCF (log2FC = −3.46, FDR = 1.01 × 10⁻³⁸)
- **Standardized pathway:** GO biological process — establishment or maintenance of cell polarity (GO:0003006); KEGG — Hippo signaling pathway (hsa04390)
- **Explanation:** CROCC and CROCC2 (rootletin family) are structural components of the ciliary rootlet. INF2 is a formin-family actin regulator. SCRIB and APC2 are conserved cell-polarity scaffolds. ARVCF interacts with CTNNB1 (β-catenin) and ERBIN in STRING, linking to adherens junction and polarity networks. Co-downregulation of these genes suggests disruption of primary cilia and apical-basal polarity—structures implicated in synovial mechanotransduction and FLS activation.
- **Evidence strength:** Direct statistical evidence across multiple independent genes; STRING interactions connect ARVCF–CTNNB1 and CROCC–CROCC2 (via LRRC45). KEGG Hippo pathway was retrieved in the batch enrichment. **Limitation:** STRING interactions may be curated or predicted; no direct protein–protein interaction data from co-immunoprecipitation in RA synovium is available. The Hippo pathway assignment is broad and may be driven by a few genes.

### Program 3: GTPase Signaling and Cytoskeletal Dynamics Regulation
- **Direction:** Downregulated
- **Major supporting genes:** ARHGAP33 (log2FC = −3.20, FDR = 1.67 × 10⁻³⁶), ACAP3 (log2FC = −2.80, FDR = 2.27 × 10⁻³⁸), ARHGAP27P1 (log2FC = −2.79, FDR = 6.78 × 10⁻³⁶), ARHGEF17-AS1 (log2FC = −3.98, FDR = 4.86 × 10⁻³⁶), SH2B1 (log2FC = −2.28, FDR = 8.10 × 10⁻³⁶), PPP1R12C (log2FC = −2.70, FDR = 2.38 × 10⁻³⁵)
- **Standardized pathway:** Reactome — RHO GTPase cycle (R-HSA-9012999); RAC1 GTPase cycle; CDC42 GTPase cycle
- **Explanation:** Multiple ARHGAP family members (Rho-GAP domain proteins) and an ARHGEF antisense transcript are co-downregulated, alongside SH2B1 (an adaptor involved in Ras/MAPK signaling) and PPP1R12C (a myosin phosphatase regulatory subunit). Rho-family GTPases regulate FLS migration, invasion, and synovial architecture. Their downregulation may indicate loss of a regulatory checkpoint that normally restrains cytoskeletal remodeling.
- **Evidence strength:** Multiple genes with direct statistical support; Reactome annotations retrieved for GTPase cycle pathways. **Limitation:** ARHGAP27P1 is a pseudogene and may not encode functional protein; its downregulation may not have a direct mechanistic consequence. Reactome GTPase annotations are broad.

### Program 4: Chromatin and Transcriptional Regulation
- **Direction:** Downregulated
- **Major supporting genes:** ZNF316 (log2FC = −3.24, FDR = 2.92 × 10⁻⁴⁸), ZNF219 (log2FC = −2.71, FDR = 3.03 × 10⁻³⁷), ZNF444 (log2FC = −2.46, FDR = 1.91 × 10⁻³⁶), ZNF580 (log2FC = −2.76, FDR = 3.52 × 10⁻³⁶), CBX7 (log2FC = −2.41, FDR = 1.43 × 10⁻³⁵), TNRC18 (log2FC = −3.04, FDR = 2.36 × 10⁻³⁷), PAGR1 (log2FC = −2.34, FDR = 1.17 × 10⁻³⁶)
- **Standardized pathway:** GO molecular function — nucleic acid binding (GO:0003676); cellular component — nucleus (GO:0005634)
- **Explanation:** Multiple zinc-finger transcription factors, the Polycomb-group component CBX7, and the chromatin-associated TNRC18 are co-downregulated. CBX7 is a Polycomb Repressive Complex 1 (PRC1) component involved in transcriptional silencing; PAGR1 (C1orf106) interacts with histone modification machinery. Their coordinated reduction suggests remodeling of epigenetic repression programs in RA synovial tissue.
- **Evidence strength:** Direct statistical evidence across many genes; GO annotations for nuclear function are broad. **Limitation:** No specific pathway enrichment beyond generic nuclear/chromatin annotations; functional consequences of each ZNF in RA synovium are largely uncharacterized.

### Program 5: Non-coding RNA Regulatory Program
- **Direction:** Downregulated
- **Major supporting genes:** MIR3154 (log2FC = −5.10, FDR = 5.97 × 10⁻⁴³), MIR3183 (log2FC = −4.61, FDR = 5.46 × 10⁻⁴⁷), MIR937 (log2FC = −3.70, FDR = 2.03 × 10⁻⁴²), MIR647 (log2FC = −3.83, FDR = 4.68 × 10⁻⁴⁰), MIR4763 (log2FC = −3.90, FDR = 1.45 × 10⁻⁴⁰), DM1-AS (log2FC = −3.65, FDR = 1.71 × 10⁻⁴⁰), IRAIN (log2FC = −3.26, FDR = 1.43 × 10⁻³⁵), PCGF3-AS1 (log2FC = −3.52, FDR = 1.10 × 10⁻⁴⁶)
- **Standardized pathway:** No specific GO/Reactome/KEGG pathway retrieved for this cluster
- **Explanation:** A substantial subset of the downregulated list comprises microRNAs and antisense/lncRNAs. MIR647 has been reported to modulate NF-κB signaling in other disease contexts (Europe PMC:30349310). DM1-AS and IRAIN are antisense transcripts associated with the DMPK and IGF1R loci, respectively. The coordinated downregulation of non-coding regulators suggests post-transcriptional and epigenetic reprogramming in RA synovium.
- **Evidence strength:** Direct statistical evidence for multiple ncRNAs; literature support for MIR647 in NF-κB signaling (non-RA context). **Limitation:** No retrieved pathway enrichment for this program; miRNA target prediction and functional validation in RA synovium is insufficient.

## 3. Key Genes and Interaction Modules

| # | Gene/Module | Statistical Direction | Role in Core Programs | Gene–Gene Relationships |
|---|---|---|---|---|
| 1 | **MUC5B** | Downregulated (log2FC = −4.43, FDR = 2.07 × 10⁻⁴⁰) | Mucosal barrier glycoprotein; may reflect loss of protective synovial lining secretory function | STRING network: interacts with MUC1, MUC2, MUC5AC, MUC7, and co-cluster members MUC6, MUC12 (pathway co-membership / shared family domain; not necessarily direct physical interaction in synovium) |
| 2 | **CROCC** | Downregulated (log2FC = −3.88, FDR = 9.67 × 10⁻⁴⁸) | Ciliary rootlet structural protein; potential disruption of primary cilia in FLS | STRING: interacts with CROCC2 via LRRC45 (predicted co-expression and shared domain; not confirmed as direct physical interaction in synovium) |
| 3 | **SCRIB** | Downregulated (log2FC = −3.24, FDR = 1.32 × 10⁻⁴²) | Cell polarity scaffold; connects to Hippo and Ras/MAPK pathways | STRING: interacts with ARHGEF7, VANGL2, GIT1, UBE3A, LLGL1 (curated/predicted physical interaction evidence from STRING); Reactome: RHO GTPase cycle |
| 4 | **ARVCF** | Downregulated (log2FC = −3.46, FDR = 1.01 × 10⁻³⁸) | Cell adhesion and polarity; links to β-catenin/Wnt signaling | STRING: interacts with COMT, CTNNB1, ERBIN, FMR1 (predicted/curated); CTNNB1 connects to APC2 in the Wnt/Hippo network (pathway co-membership) |
| 5 | **APC2** | Downregulated (log2FC = −3.02, FDR = 4.63 × 10⁻³⁹) | Wnt/β-catenin pathway regulator; KEGG Hippo signaling pathway | Pathway co-membership with ARVCF via CTNNB1; no direct physical interaction retrieved between APC2 and ARVCF |
| 6 | **CBX7** | Downregulated (log2FC = −2.41, FDR = 1.43 × 10⁻³⁵) | Polycomb PRC1 component; epigenetic silencing regulator | Insufficient direct interaction evidence from retrieved records for this dataset |
| 7 | **ZNF316** | Downregulated (log2FC = −3.24, FDR = 2.92 × 10⁻⁴⁸) | Zinc-finger transcription factor; potential chromatin remodeling in RA | Insufficient direct interaction evidence; GO annotation: nucleic acid binding |
| 8 | **ARHGAP33** | Downregulated (log2FC = −3.20, FDR = 1.67 × 10⁻³⁶) | Rho-GAP; regulator of GTPase cycle and cytoskeletal dynamics | Reactome: RHO GTPase cycle; pathway co-membership with ACAP3 and other ARHGAPs |
| 9 | **SH2B1** | Downregulated (log2FC = −2.28, FDR = 8.10 × 10⁻³⁶) | Adaptor protein in Ras/MAPK and growth factor signaling; also linked to metabolic regulation | STRING/IntAct: interacts with signaling adaptors (not shown in truncated records); GO: nucleus, cytoplasm |
| 10 | **MUC12 / MUC6 / MUC5B module** | All downregulated (MUC6: log2FC = −3.85; MUC12: log2FC = −4.27; MUC5B: log2FC = −4.43) | Mucin-family secretory barrier program | STRING: shared network via MUC1, MUC2, MUC5AC, MUC7 (family-level co-membership; not confirmed as direct physical interactions) |

**Interaction type clarification:** STRING edges between mucin family members (MUC5B–MUC6–MUC12) most likely reflect shared protein domains and family co-annotation rather than experimentally validated direct physical interactions. STRING edges for SCRIB (ARHGEF7, VANGL2) and ARVCF (CTNNB1, ERBIN) are curated or predicted interaction evidence from STRING; these should not be assumed to occur in RA synovium without validation. The connection between APC2 and ARVCF is pathway co-membership (Wnt/β-catenin and Hippo signaling), not a direct physical interaction. The CROCC–CROCC2 relationship is likely shared domain and predicted co-expression rather than confirmed direct physical interaction.

## 4. Validation Priorities

### Priority 1: Mucin Family Downregulation as a Synovial Barrier Integrity Biomarker
- **Classification:** Biomarker
- **Why prioritized:** Three independent mucin genes (MUC5B, MUC6, MUC12) are among the most strongly downregulated, with extremely low FDR values; this represents a multi-gene concordant signal.
- **Current dataset evidence:** Direct statistical evidence (log2FC range −3.85 to −4.43; all FDR < 10⁻³⁹).
- **External evidence:** STRING network supports family-level co-membership; specific RA synovium literature on mucin downregulation was not identified in the retrieved records.
- **Next step:** Validate by qPCR or RNAscope in independent RA and control synovial tissue cohorts; correlate with histological assessment of synovial barrier integrity.
- **Evidence status:** Supported hypothesis

### Priority 2: Primary Cilia / Cytoskeletal Disruption in FLS
- **Classification:** Mechanistic hypothesis
- **Why prioritized:** Co-downregulation of CROCC, CROCC2, INF2, and SCRIB points to disruption of primary cilia and cell polarity, which are mechanistically linked to FLS activation.
- **Current dataset evidence:** Multiple independent genes with strong statistical support (CROCC: FDR = 9.67 × 10⁻⁴⁸; CROCC2: FDR = 1.22 × 10⁻⁴⁰; SCRIB: FDR = 1.32 × 10⁻⁴²).
- **External evidence:** STRING interactions for SCRIB (VANGL2, ARHGEF7) and ARVCF (CTNNB1) are curated; published literature on primary cilia in RA FLS exists but was not specifically retrieved in the question-specific literature search.
- **Next step:** Immunofluorescence for ciliary rootlet (CROCC) and primary cilia markers (acetylated α-tubulin, IFT88) in RA vs. control synovium; functional assays for FLS migration and invasion.
- **Evidence status:** Exploratory hypothesis

### Priority 3: Rho-GTPase Regulatory Network in FLS Activation
- **Classification:** Interaction / network hypothesis
- **Why prioritized:** Multiple Rho-GAP and GTPase-cycle genes (ARHGAP33, ACAP3, ARHGEF17-AS1) are co-downregulated; Reactome GTPase cycle annotations support a coherent pathway-level signal.
- **Current dataset evidence:** Direct statistical evidence; Reactome pathway annotations retrieved.
- **External evidence:** Rho-GTPases are well-established regulators of FLS cytoskeleton and migration in RA literature; however, the specific downregulation of ARHGAP33 and ACAP3 in RA synovium is not well-documented.
- **Next step:** Co-expression network analysis in independent RA synovial RNA-seq datasets; functional knockdown/overexpression of ARHGAP33 in RA FLS lines to assess RhoA/Rac1 activity, stress fiber formation, and migration.
- **Evidence status:** Exploratory hypothesis

### Priority 4: CBX7 / Polycomb-Mediated Epigenetic Rewiring
- **Classification:** Therapeutic target
- **Why prioritized:** CBX7 is a druggable epigenetic reader (PRC1 component); co-downregulation with multiple ZNF transcription factors suggests epigenetic remodeling.
- **Current dataset evidence:** CBX7 downregulated (log2FC = −2.41, FDR = 1.43 × 10⁻³⁵); co-downregulation with ZNF316, ZNF219, ZNF444, ZNF580, TNRC18, PAGR1.
- **External evidence:** CBX7 is a known Polycomb group protein with roles in transcriptional silencing; specific therapeutic relevance to RA synovium is insufficient evidence.
- **Next step:** Chromatin immunoprecipitation (ChIP) for H3K27me3 and CBX7 targets in RA vs. control FLS; assess effects of PRC1 inhibitors on FLS inflammatory phenotype.
- **Evidence status:** Exploratory hypothesis
- **Note:** The existence of epigenetic drugs targeting CBX7-related pathways does not constitute evidence that CBX7 is an effective RA therapeutic target.

### Priority 5: Cell-Composition Confounding Check
- **Classification:** Confounding or composition check
- **Why prioritized:** The uniform downregulation and the concentration of mucin, ciliary, and polarity genes raise the possibility that the signal reflects loss of a specific cell population (e.g., barrier-like FLS subtype, fibroblast subset, or epithelial contaminant) rather than gene-level regulation within a stable cell population.
- **Current dataset evidence:** All 100 genes are downregulated with extremely low FDR values; this pattern is consistent with a cell-composition shift.
- **External evidence:** RA synovium is known to undergo dramatic changes in FLS subtype composition (sublining vs. lining fibroblasts, inflammatory vs. resting states).
- **Next step:** Perform single-cell deconvolution (e.g., CIBERSORTx with RA synovium single-cell reference signatures) on the bulk RNA-seq data; confirm key genes (MUC5B, CROCC, SCRIB) in single-cell datasets.
- **Evidence status:** Supported hypothesis (composition confounding is a well-recognized issue in bulk synovial transcriptomics)

## 5. Evidence Grounding

### Evidence type summary

| Evidence Type | Supporting Elements | Independence Assessment |
|---|---|---|
| **Direct evidence from input dataset** | All 100 genes downregulated; log2FC and FDR values from the uploaded table | Single source; no replication cohort provided |
| **Pathway / ontology evidence** | KEGG: Hippo signaling pathway, Ribosome; Reactome: RHO GTPase cycle; GO: protein binding, nucleus, plasma membrane, membrane | KEGG and Reactome annotations may share underlying pathway curation; GO annotations are independent ontology terms but derived from overlapping gene set |
| **Protein interaction evidence** | STRING: SCRIB–ARHGEF7/VANGL2; ARVCF–CTNNB1/ERBIN; mucin family co-cluster; CROCC–CROCC2 via LRRC45 | STRING integrates curated and predicted interactions; confidence scores do not confirm direct physical interaction in RA synovium |
| **Regulatory evidence** | TRRUST records for 7 genes; MIR647 literature on NF-κB (Europe PMC:30349310) | TRRUST and literature may share underlying publications; MIR647 evidence is from a non-RA context |
| **Disease-association evidence** | GWAS records retrieved for 100/100 genes; ClinVar records for 79/100; OpenTargets for 82/100 | GWAS, ClinVar, and OpenTargets may share variant-level data; not all disease associations are specific to RA |
| **Expression / tissue-specific evidence** | GTEx records for 61/100; Human Protein Atlas for 47/100 | GTEx and HPA are independent databases but may share underlying expression data |
| **Drug / therapeutic evidence** | ChEMBL records for 16/100; ClinicalTrials.gov for 19/100 | Drug-target records do not imply therapeutic efficacy in RA; ChEMBL and ClinicalTrials may share trial-level data |
| **Published literature evidence** | PubMed: 483 articles retrieved (up to 6 shown); Europe PMC: 776 articles | Literature records retrieved were not RA-specific for most genes; question-specific literature search did not return focused RA synovial mucin or ciliary studies |

### Conflicting or insufficient evidence
- **Insufficient evidence:** No direct RA synovium literature was retrieved for MUC5B, CROCC, or SCRIB downregulation specifically in RA; disease-association claims are contextual only.
- **Conflict:** The question-specific literature records (PMID:36983764, PMID:35711934, PMID:36211371, PMID:30866732) are predominantly from cancer or degenerative disc disease contexts, not RA; these should not be used to support RA-specific conclusions.
- **No independent cohort validation was performed.** External statistical validation status is not available (cohort not specified, endpoint not specified, study not specified, model not specified). Pathway recurrence, source coverage, and literature support do not constitute replication.

## 6. Limitations and Alternative Explanations

### 1. Cell-composition confounding
The uniform downregulation of mucin, ciliary rootlet, and cell polarity genes is highly suggestive of loss of a specific cell population (e.g., barrier-like FLS, lining fibroblasts, or epithelial remnants) rather than gene-level transcriptional repression within a stable cell population. **Investigation:** Single-cell RNA-seq deconvolution of bulk data; immunohistochemistry for MUC5B, CROCC, and SCRIB in RA vs. control synovium; FACS sorting of FLS subpopulations followed by qPCR.

### 2. All-downregulated gene list and statistical saturation
The absence of any upregulated genes, combined with FDR values as low as 10⁻⁵⁴, suggests either a pre-filtered list (e.g., top 100 downregulated only) or statistical saturation from very large sample sizes. **Investigation:** Request the full differential analysis output (including upregulated genes and non-significant genes); verify sample size, multiple-testing correction method, and whether the list represents a pre-ranked subset.

### 3. Batch or platform effects
If RA and control samples were processed in different batches or on different platforms, systematic technical bias could produce uniformly downregulated signals. **Investigation:** Check batch metadata, RNA integrity numbers, library preparation dates, and sequencing platforms; apply batch correction (e.g., ComBat) if needed.

### 4. Disease severity, treatment exposure, and disease stage
RA synovial tissue is typically obtained from patients with established disease, often on DMARD or biologic therapy. Control synovium may come from trauma or osteoarthritis patients. Treatment exposure and disease stage can dramatically alter transcriptomic profiles. **Investigation:** Stratify analysis by treatment status (treatment-naïve vs. exposed), disease duration, and DAS28 score; compare with publicly available RA synovial datasets (e.g., from the Accelerating Medicines Partnership RA network).

### 5. Association-versus-causation ambiguity
The observed downregulation is an association; it cannot distinguish whether reduced expression of these genes contributes to RA pathogenesis or is a consequence of inflammation, tissue remodeling, or cell loss. **Investigation:** Functional experiments in RA FLS (knockdown/overexpression of SCRIB, CROCC, CBX7); longitudinal analysis in animal models of arthritis; causal inference methods (e.g., Mendelian randomization) using GWAS instruments for key genes.

---

**Summary:** The uploaded dataset reveals a coordinated downregulation of mucosal barrier glycoproteins, cytoskeletal/ciliary rootlet components, Rho-GTPase regulators, chromatin-associated factors, and non-coding RNAs in RA synovium versus control. The strongest program-level evidence supports a mucin-family and cytoskeletal-polarity signal, but the uniform directionality and extreme P-value compression raise data-quality concerns that must be resolved before causal or therapeutic conclusions are drawn. External statistical validation was not performed, and all biological claims should be treated as exploratory hypotheses pending independent cohort replication and single-cell deconvolution.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=41, external claims checked=0, external mismatches=0, status=passed.

Answer model API: Zhipu AI / glm-5.2

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 84/100 selected items (records returned); cbioportal 82/100 selected items (records returned); chembl 16/100 selected items (records returned); civic 1/100 selected items (records returned); clinicaltrials 19/100 selected items (records returned); clinvar 79/100 selected items (records returned); ensembl 40/100 selected items (partially returned; some queries failed); europepmc 776 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 61/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 47/100 selected items (records returned); humanbase 88/100 selected items (partially returned; some queries failed); intact 47/100 selected items (records returned); mygene 93/100 selected items (records returned); omnipath 17/100 selected items (records returned); opentargets 82/100 selected items (records returned); pubmed 483 articles / initial full-cohort RAG 100 queries + 3 current-round queries; some queries failed; quickgo 50/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 51/100 selected items (records returned)
Local databases: gutmgene 0/100 selected items (reachable but no records for this batch); hmdb 8/100 selected items (records returned); string 49/100 selected items (records returned); trrust 7/100 selected items (records returned)
