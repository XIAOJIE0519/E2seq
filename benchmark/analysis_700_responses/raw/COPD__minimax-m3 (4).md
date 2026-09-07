# chronic obstructive pulmonary disease (COPD) - minimax-m3

- Benchmark system: raw
- Repeat: 5
- Task type: DISEASE-STATE
- Tissue / sample source: lung tissue
- Comparison or endpoint: COPD versus normal control
- Answer input cohort: Discovery/Core only
- Selected items: 100
- Input fields: gene name, effect size (log2FC/HR), P value, FDR
- E2seq Agent RAG: disabled
- Conversation memory: disabled
- Thinking mode: disabled
- Held-out validation data in prompt/RAG: no
- Model API: MiniMax / minimax-m3
- Message SHA-256: 75cb1462dc859d10e673df1637d9bfb35fbfd41f53bda923e17881eee80cc2ef
- Response HTTP status: 200
- Prompt tokens: 3923
- Completion tokens: 5624
- Reasoning tokens: 
- Total tokens: 9547
- API requests reported: 
- Elapsed seconds: 66.459
- Final benchmark system: raw; file rank 4/5; original repeat 5; model vendor: MiniMax

---
<think>The user wants a comprehensive, multidimensional interpretation of transcriptomic data comparing COPD vs normal control lung tissue. Let me analyze the provided gene list carefully.

Looking at the data:
- Total genes: ~100
- Most genes are upregulated (positive log2FC)
- A few downregulated (negative log2FC): UQCRBP1, RPL23AP32, LOC105374836, NACA2, LOC105369509, RASSF7, LOC105374056, MIR7703, SNORA70, LOC105373943, SPSB3, LOC112268006, LINC00922, ZNF32-AS1, LOC105375489, PTPRCAP, SNORD60

Key observations:
1. The overwhelming majority of significant genes are long non-coding RNAs (lncRNAs), antisense transcripts, and pseudogenes (LOC genes, LINC genes, AS1 suffixes, etc.)
2. Very few protein-coding genes appear in the top hits:
   - MACF1 (microtubule-actin crosslinking factor 1)
   - CLDN16 (claudin 16)
   - AAK1 (AP2-associated kinase 1)
   - MGAM (maltase-glucoamylase)
   - POMK (protein-O-mannose kinase)
   - FGG (fibrinogen gamma chain)
   - GREM1 (gremlin 1)
   - DEFB1 (defensin beta 1)
   - CNTNAP3C (contactin associated protein-like 3C)
   - PTPRCAP (protein tyrosine phosphatase receptor type C associated protein)
   - SPSB3 (SPRY domain containing B-box...)
   - PTPRCAP
   - NCR3LG1 (natural killer cell cytotoxicity receptor 3 ligand 1)
   - ZNF66, ZNF32
   - INHBA-AS1
   - ETV3L (ETS variant transcription factor 3 like)
   - RASSF7 (Ras association domain family member 7)
   - TGFB2-AS1
   - ZBED6
   - LRP1-AS
   - LDLR-AS1
   - SERPINB9-AS1
   - TENM3

This is unusual - the top hits are dominated by non-coding RNAs and uncharacterized loci, which limits biological interpretation significantly.

Let me think about what biological themes might emerge:

1. **lncRNA/transcriptional regulation dominance**: The vast majority of significant hits are non-coding RNAs (antisense, lncRNAs, pseudogenes). This could suggest:
   - Widespread transcriptional dysregulation
   - Possible technical artifact (e.g., these are lowly expressed genes with high variance)
   - Cell-type composition shifts
   - Regulatory RNA involvement in COPD

2. **Epithelial barrier and mucosal defense**: 
   - DEFB1 (defensin beta 1) - antimicrobial peptide, innate immunity
   - CLDN16 - tight junction protein
   - FGG - fibrinogen
   - MGAM - mucosal enzyme
   - These suggest altered mucosal/epithelial defense

3. **TGF-β signaling and fibrosis/remodeling**:
   - GREM1 (gremlin 1) - BMP antagonist, involved in fibrosis
   - TGFB2-AS1 - TGF-β2 antisense
   - INHBA-AS1 - inhibin subunit beta A antisense
   - These point to tissue remodeling/fibrosis pathways

4. **Cell adhesion/cytoskeleton**:
   - MACF1 (upregulated) - microtubule-actin crosslinking factor
   - TENM3 (upregulated) - teneurin, cell adhesion
   - PTPRCAP (downregulated) - phosphatase, T-cell signaling
   - CNTNAP3C (upregulated) - cell adhesion molecule

5. **Immune cell signaling**:
   - PTPRCAP (downregulated) - T cell signaling
   - NCR3LG1 (upregulated) - NK cell ligand
   - DEFB1 (upregulated) - innate immunity

Let me organize this into a coherent response following the requested structure.

The dominance of non-coding RNAs is striking. I should be honest that this makes biological interpretation challenging. The standard pathway enrichment tools may not work well here.

Let me build the response now.

For core biological programs, I'll identify:
1. TGF-β/BMP signaling and tissue remodeling/fibrosis
2. Epithelial barrier and mucosal defense
3. Cytoskeletal/cell adhesion reorganization
4. Immune cell signaling dysregulation
5. Non-coding RNA/transcriptional landscape

Actually, let me think more carefully. Given the data quality issues (mostly non-coding RNAs), I should probably focus more on the few protein-coding genes that are interpretable:

**Protein-coding genes that are clear and interpretable:**

Upregulated:
- GREM1 (log2FC 1.65, FDR 0.0072): BMP antagonist, promotes fibrosis
- DEFB1 (log2FC 1.40, FDR 0.0074): antimicrobial peptide
- FGG (log2FC 1.76, FDR 0.0053): fibrinogen gamma chain - coagulation
- MGAM (log2FC 1.49, FDR 0.0011): maltase-glucoamylase - mucosal digestion
- CLDN16 (log2FC 1.70, FDR 0.00039): claudin tight junction
- MACF1 (log2FC 1.56, FDR 4.0e-7): cytoskeletal linker
- POMK (log2FC 1.06, FDR 0.0012): glycosylation enzyme
- INHBA-AS1 associated, INHBA (activin A) is fibrosis-related
- AAK1 (log2FC 0.99): endocytic regulator
- TENM3 (log2FC 0.97): cell adhesion

Downregulated:
- PTPRCAP (log2FC -0.87): PTP in T-cell signaling
- SPSB3 (log2FC -0.82): TGF-β signaling regulator (interesting - this is a negative regulator)
- RASSF7 (log2FC -0.91): Hippo/MST signaling

Let me check SPSB3 more carefully - SPSB3 is a SPRY domain SOCS box protein that can regulate various signaling pathways. There are reports of SPSB3 in TGF-β signaling.

Now let me think about validation priorities:

1. GREM1 - TGF-β/BMP axis dysregulation in COPD
2. DEFB1 - mucosal defense impairment
3. PTPRCAP - T-cell signaling reduction
4. FGG - coagulation/fibrin deposition
5. MACF1 - cytoskeletal remodeling

Given the dominance of lncRNAs, I should also note that the dataset appears to be from a specific array or analysis that enriched for these features.

Let me write this out now in a structured response.</think>

# Multidimensional Transcriptomic Interpretation: COPD vs. Normal Lung Tissue

## 1. Overall Biological Interpretation

The current dataset presents an unusual transcriptomic signature in which the overwhelming majority of significantly altered features are non-coding elements — antisense transcripts (e.g., *CELF2-AS1*, *LRP1-AS*, *SERPINB9-AS1*, *TGFB2-AS1*, *INHBA-AS1*), long intergenic non-coding RNAs (e.g., *LINC00260*, *LINC00922*, *LINC02175*), pseudogenes (e.g., *SMG1P1/P3*, *RPL23AP2*, *ZNRF2P1*), small nucleolar RNAs (*SNORD60*, *SNORA70*), ribosomal RNA pseudogenes (*RNA18SN1/N3/N5*), and uncharacterized *LOC* loci. Only ~15–20 protein-coding genes pass FDR < 0.01 with biologically coherent directional change.

When interpreted together, the signal converges on a **chronic epithelial injury, repair, and remodeling phenotype** rather than an acute inflammatory program. Specifically, the protein-coding components are consistent with (i) altered BMP/TGF-β signaling (GREM1↑, SPSB3↓, TGFB2-AS1↑, INHBA-AS1↑), (ii) remodeling of epithelial barrier and mucosal defenses (DEFB1↑, CLDN16↑, MGAM↑), (iii) cytoskeletal and cell-adhesion reorganization (MACF1↑, TENM3↑, CNTNAP3C↑), and (iv) modulation of innate/adaptive immune signaling (PTPRCAP↓, NCR3LG1↑). The dominance of non-coding transcripts, however, complicates functional inference and likely reflects either platform-level overrepresentation of such features or genuine pervasive non-coding transcriptional dysregulation in chronically diseased lung tissue.

---

## 2. Core Biological Programs

### Program A — TGF-β / BMP Axis Activation and Tissue Remodeling
- **Direction**: Activated in COPD vs. control
- **Supporting genes**: *GREM1* (↑, log2FC ≈ 1.65, FDR ≈ 0.0072), *TGFB2-AS1* (↑, log2FC ≈ 1.04), *INHBA-AS1* (↑, log2FC ≈ 1.19), *SPSB3* (↓, log2FC ≈ −0.82)
- **Most appropriate pathway**: Reactome "Signaling by TGF-β family members"; Hallmark "TGF-β signaling"; GO:0007179 (TGF-β receptor signaling)
- **Interpretation**: GREM1 is a secreted BMP antagonist that blocks SMAD1/5 signaling, biasing the BMP:TGF-β balance toward pro-fibrotic SMAD2/3 activation — a well-characterized mechanism in small-airway fibrosis and emphysematous remodeling. *SPSB3* negatively regulates TGF-β receptor stability in some contexts; its downregulation could further potentiate signaling. *INHBA-AS1* and *TGFB2-AS1* may cis-regulate *INHBA* (activin A) and *TGFB2* respectively.
- **Evidence strength**: Moderate. Multiple independent features align on a single pathway, but only one canonical effector (GREM1) is a protein-coding gene.
- **Major limitations**: Antisense lncRNAs cannot be assumed to regulate their neighboring genes without experimental evidence; SPSB3's role in non-immune TGF-β regulation is incompletely characterized.

### Program B — Epithelial Barrier and Antimicrobial Defense Remodeling
- **Direction**: Upregulated
- **Supporting genes**: *DEFB1* (↑, log2FC ≈ 1.40, FDR ≈ 0.0074), *CLDN16* (↑, log2FC ≈ 1.70, FDR ≈ 0.00039), *MGAM* (↑, log2FC ≈ 1.49, FDR ≈ 0.0011), *FGG* (↑, log2FC ≈ 1.76, FDR ≈ 0.0053)
- **Most appropriate pathway**: GO:0045087 (innate immune response); Reactome "Tight junction interactions"; Hallmark "Coagulation"
- **Interpretation**: Concurrent upregulation of a β-defensin antimicrobial peptide, a claudin family tight-junction component, and a mucosal brush-border digestive enzyme (MGAM) suggests adaptive remodeling of the airway/lung epithelial defense layer. The parallel upregulation of fibrinogen γ-chain (*FGG*) is consistent with known airway fibrin deposition in COPD and possibly reflects epithelial/transcriptional stress responses rather than purely hepatic origin.
- **Evidence strength**: Moderate-to-low. The genes are biologically related but heterogeneous (antimicrobial, junctional, digestive, coagulation), and there is limited prior COPD-specific literature linking them as a coordinated module.
- **Major limitations**: CLDN16 is canonically a renal tubular claudin; its functional significance in lung epithelium is not well-established. MGAM is principally an enterocyte brush-border enzyme, raising concern about cell-type-of-origin (see Limitations).

### Program C — Cytoskeletal and Adhesion Reorganization
- **Direction**: Upregulated
- **Supporting genes**: *MACF1* (↑, log2FC ≈ 1.56, FDR ≈ 4.0e-7), *TENM3* (↑, log2FC ≈ 0.97), *CNTNAP3C* (↑, log2FC ≈ 0.95), *AAK1* (↑, log2FC ≈ 0.99), *POMK* (↑, log2FC ≈ 1.06)
- **Most appropriate pathway**: GO:0007010 (cytoskeleton organization); Reactome "Cell-Cell communication"
- **Interpretation**: MACF1 is a giant actin-microtubule crosslinker required for cytoskeletal integrity under mechanical stress; its upregulation is consistent with epithelial stretch/injury responses. TENM3 (teneurin-3) and CNTNAP3C are cell-adhesion molecules previously implicated in neuronal but increasingly recognized in epithelial morphogenesis. AAK1 regulates clathrin-mediated endocytosis and has been linked to inflammatory cytokine receptor trafficking.
- **Evidence strength**: Moderate. MACF1 upregulation has been previously reported in airway remodeling contexts, but TENM3 and CNTNAP3C have minimal COPD-specific literature.
- **Major limitations**: This is a loosely related set; there is no clear canonical pathway unifying all members, and any interpretation as a coordinated "module" is tentative.

### Program D — Immune Cell Signaling Modulation
- **Direction**: Mixed (loss of T-cell co-receptor phosphatase, gain of NK ligand)
- **Supporting genes**: *PTPRCAP* (↓, log2FC ≈ −0.87, FDR ≈ 0.017), *NCR3LG1* (↑, log2FC ≈ 0.95, FDR ≈ 0.0045), *SPSB3* (↓)
- **Most appropriate pathway**: GO:0050852 (T-cell receptor signaling pathway); Reactome "Immune System"
- **Interpretation**: PTPRCAP (CD45-associated protein) is required for efficient T-cell receptor signaling; its downregulation may reflect either T-cell exhaustion/contraction or altered lymphocyte composition in COPD tissue. NCR3LG1 (B7-H6) is an activating ligand for NKp30 on NK cells, suggesting increased NK-cell engagement potential. This combination is consistent with prior descriptions of COPD as a state of adaptive immune dysregulation with relative innate lymphocyte prominence.
- **Evidence strength**: Low-to-moderate. The two canonical signals point in opposite but interpretable directions; however, neither has been a major COPD biomarker in prior literature.
- **Major limitations**: The dataset provides no cellular deconvolution; changes may reflect shifts in immune cell infiltration rather than gene-regulatory changes within a single cell type.

### Program E — Non-coding RNA / Antisense Transcript Layer
- **Direction**: Predominantly upregulated
- **Supporting features**: *CELF2-AS1*, *LRP1-AS*, *SERPINB9-AS1*, *TGFB2-AS1*, *INHBA-AS1*, *LDLR-AS1*, *ZMYM4-AS1*, *KLF9-DT*, *MACF1-AS* (not explicit), and many *LOC*/*LINC* transcripts.
- **Most appropriate annotation**: Insufficiently curated; no canonical pathway
- **Interpretation**: This category may represent a genuine layer of regulatory remodeling or, alternatively, an artifact of the detection platform / library preparation bias toward certain transcript biotypes. Antisense transcripts near TGF-β/BMP signaling genes (TGFB2, INHBA, LRP1, LDLR) raise the hypothesis of cis-regulatory RNA–host gene coupling, but this remains speculative.
- **Evidence strength**: Weak as a functional interpretation; useful as a hypothesis-generating observation.
- **Major limitations**: Without orthogonal RNA-seq validation, motif/sequence analysis, or perturbation data, these features cannot be interpreted mechanistically.

---

## 3. Key Genes and Interaction Modules

| # | Gene | Direction | Role / Module | Type of relationship evidence |
|---|------|-----------|---------------|-------------------------------|
| 1 | **GREM1** | ↑ | BMP antagonist; Program A | Protein-level data in lung fibrosis; pathway co-membership with TGF-β |
| 2 | **DEFB1** | ↑ | Antimicrobial peptide; Program B | Published COPD/asthma expression data; tissue-specific expression evidence |
| 3 | **CLDN16** | ↑ | Tight junction; Program B | Tissue-specific expression primarily renal; cross-tissue role is putative |
| 4 | **MACF1** | ↑ | Cytoskeletal crosslinker; Program C | Protein interaction with actin/microtubules; co-membership with cell-junction pathways |
| 5 | **PTPRCAP** | ↓ | T-cell co-receptor phosphatase; Program D | Direct protein-protein interaction with CD45 (PTPRC); published evidence |
| 6 | **SPSB3** | ↓ | Negative regulator of TGF-β signaling / cytokine receptor turnover; Programs A & D | Indirect regulatory relationship; pathway co-membership |
| 7 | **FGG** | ↑ | Coagulation / fibrin formation; Program B | Disease-association evidence in airway disease |
| 8 | **NCR3LG1** | ↑ | NK cell activating ligand; Program D | Direct receptor-ligand interaction with NCR3/NKp30 |
| 9 | **INHBA-AS1 / TGFB2-AS1** | ↑ | Possible cis-regulators; Program A | Co-expression / genomic proximity (putative regulatory) |
| 10 | **AAK1** | ↑ | Endocytic regulator; Program C | Protein-protein interaction with AP-2 complex |

> Note: Interactions flagged above are predominantly **pathway co-membership**, **protein-protein interaction**, or **putative regulatory co-expression** — **not** direct physical interaction unless explicitly stated. In particular, antisense lncRNA–host-gene pairings should not be interpreted as direct regulatory interactions without perturbation data.

---

## 4. Validation Priorities

### Priority 1 — GREM1 as a candidate mediator of small-airway fibrosis in COPD
- **Category**: Therapeutic target / mechanistic hypothesis
- **Why prioritize**: GREM1 is the single highest-effect, most literature-supported protein-coding signal in the dataset with a plausible mechanistic role.
- **Dataset evidence**: Upregulated (log2FC ≈ 1.65, FDR ≈ 0.0072) with concordant upregulation of *TGFB2-AS1*, *INHBA-AS1*, and downregulation of *SPSB3*.
- **External evidence**: GREM1 is an established BMP antagonist implicated in idiopathic pulmonary fibrosis; recombinant GREM1 blockade is under preclinical investigation.
- **Next step**: Quantify GREM1 protein in COPD vs. control lung tissue by IHC and ELISA; test BMP/TGF-β signaling readouts (pSMAD1/5 vs pSMAD2/3) in matched samples.
- **Conclusion status**: **Supported hypothesis**

### Priority 2 — DEFB1 / CLDN16 axis as a marker of altered mucosal defense
- **Category**: Biomarker / mechanistic hypothesis
- **Why prioritize**: Two independent, biologically coherent protein-coding signals converge on epithelial defense.
- **Dataset evidence**: Both upregulated with FDR < 0.01.
- **External evidence**: DEFB1 SNPs and expression have been associated with COPD susceptibility in multiple cohorts; CLDN18 is the dominant lung claudin, while CLDN16 is typically renal — its lung relevance requires validation.
- **Next step**: Confirm CLDN16 expression specifically in airway epithelium by IHC; quantify β-defensin-1 levels in bronchoalveolar lavage.
- **Conclusion status**: **Supported hypothesis** (DEFB1), **Exploratory hypothesis** (CLDN16 in lung)

### Priority 3 — PTPRCAP downregulation as an indicator of T-cell signaling suppression in COPD lung
- **Category**: Biomarker / confounding check
- **Why prioritize**: PTPRCAP reduction has both mechanistic and compositional interpretations; resolving it has high interpretative value.
- **Dataset evidence**: Decreased (log2FC ≈ −0.87, FDR ≈ 0.017).
- **External evidence**: PTPRCAP (PTP-CD45-AP) is required for T-cell receptor signaling; loss may reflect either T-cell exhaustion or reduced T-cell infiltration.
- **Next step**: Pair gene-expression data with immunophenotyping (flow cytometry or single-cell RNA-seq) on matched samples to distinguish regulatory vs. compositional change.
- **Conclusion status**: **Exploratory hypothesis**

### Priority 4 — MACF1 / AAK1 cytoskeletal-remodeling axis
- **Category**: Mechanistic hypothesis / interaction-network hypothesis
- **Why prioritize**: Strong statistical signal (MACF1: log2FC ≈ 1.56, FDR ≈ 4.0e-7) with biologically coherent direction in chronic injury.
- **Dataset evidence**: Multiple cytoskeletal/adhesion genes coordinately upregulated.
- **External evidence**: MACF1 is required for microtubule-actin coordination; AAK1 regulates endocytic trafficking of cytokine receptors.
- **Next step**: Co-stain MACF1 with markers of epithelial stretch / airway smooth muscle hypertrophy; test whether MACF1 induction is mechanosensitive in vitro.
- **Conclusion status**: **Exploratory hypothesis**

### Priority 5 — Cell-composition / tissue-heterogeneity check
- **Category**: Confounding or composition check
- **Why prioritize**: The dataset contains MGAM (enterocyte marker) and several atypical transcripts (e.g., *IGKV1-8*, an immunoglobulin kappa variable region). The biological interpretation is contingent on whether the COPD and control tissues differ in cellular composition.
- **Dataset evidence**: Ig transcript detection and MGAM elevation are unusual in whole-lung transcriptomics.
- **Next step**: Perform deconvolution (e.g., CIBERSORTx, MuSiC, or single-cell RNA-seq) on existing or matched bulk data; verify using IHC that the protein-coding hits are expressed in expected pulmonary cell types.
- **Conclusion status**: **Confounding check — essential before causal inference**

---

## 5. Evidence Grounding

| Claim | Evidence source | Independence |
|------|------------------|--------------|
| GREM1 → fibrosis/remodeling | Dataset (GREM1↑), published literature (GREM1 in IPF), pathway evidence (BMP/TGF-β balance) | Two independent sources (this dataset + literature), but literature substantially predates and likely drove inclusion |
| DEFB1 → mucosal defense | Dataset (DEFB1↑), published COPD genetics/association | Independent |
| CLDN16 → epithelial defense | Dataset only; protein is canonically renal | **Insufficient evidence** for lung-specific role |
| MACF1 → cytoskeletal remodeling | Dataset (MACF1↑), protein interaction evidence | Likely independent |
| PTPRCAP ↓ → T-cell suppression | Dataset (PTPRCAP↓), TCR signaling pathway | Independent mechanism but compositional confounding unresolved |
| Antisense lncRNAs regulate host genes | Genomic proximity only | **Insufficient evidence** — co-expression/proximity ≠ regulatory interaction |
| FGG ↑ → airway fibrin deposition | Dataset (FGG↑), published COPD airway fibrin | Independent |

**Conflict note**: The dataset shows both *TGFB2-AS1* (↑) and *SPSB3* (↓), which would — under a cis-regulatory model — predict increased TGFB2 ligand. However, no TGFB2 mRNA appears in the significant list, meaning either the regulatory model is wrong, TGFB2 induction occurs at protein not RNA level, or TGFB2 regulation is post-transcriptional. This is unresolved.

---

## 6. Limitations and Alternative Interpretations

1. **Non-coding RNA dominance limits biological inference.** The top hits are predominantly lncRNAs, antisense transcripts, and pseudogenes whose functional consequences cannot be deduced from differential expression alone. Standard pathway enrichment tools (GO/KEGG/Hallmark) will produce weak or misleading results. Independent RNA-seq confirmation is essential.

2. **Cell-composition confounding.** Detection of an immunoglobulin variable region (*IGKV1-8*) and an enterocyte-enriched gene (*MGAM*) suggests either sample contamination, ectopic expression, or substantial shifts in infiltrating cell populations between COPD and control lung tissue. Without cellular deconvolution, all observed signals could partly reflect differences in the proportion of epithelial, immune, and stromal cells.

3. **Lack of protein-coding "anchor" genes.** The dataset does not contain canonical COPD biomarkers (e.g., *MMP9*, *MMP12*, *SERPINA1*, *ELN*, *COL1A1*, *CCL2*, *IL6*, *IL8/CXCL8*) in its significant list at this FDR threshold. This is unusual for a COPD transcriptomic dataset and raises the possibility of (a) a less-affected or early-stage sample cohort, (b) platform-specific dropout of key genes, or (c) reference/normal tissue contamination.

4. **Effect sizes are modest in absolute magnitude.** Most protein-coding genes show log2FC < 2 (i.e., <4-fold change), which is biologically meaningful but not large. Statistical significance here likely reflects sample size rather than massive dysregulation.

5. **Cross-sectional design precludes causal inference.** All signals are associations at the time of sampling; it is not possible to distinguish drivers of COPD from consequences of chronic injury, smoking history, treatment exposure (e.g., inhaled corticosteroids), or comorbid conditions. Confounders such as age, sex, smoking status, and exacerbation history should be considered when generalizing these results.

**How to investigate these limitations**: Match future validation studies for smoking history, GOLD stage, and treatment; perform single-cell or spatial transcriptomics to separate cell-type-intrinsic regulation from compositional shifts; validate protein-coding hits by IHC or targeted proteomics; and confirm key lncRNA signals by an orthogonal method (e.g., strand-specific RT-qPCR).

---

**Overall conclusion**: This dataset suggests a COPD lung transcriptomic state characterized by modest upregulation of TGF-β/BMP-pathway modulators (notably *GREM1*), altered mucosal defense (*DEFB1*, *CLDN16*), cytoskeletal reorganization (*MACF1*), and immune signaling shifts (*PTPRCAP*↓, *NCR3LG1*↑). The dominant non-coding signature should be interpreted cautiously and treated primarily as a hypothesis-generating observation rather than mechanistic evidence. The most actionable next steps are (i) orthogonal confirmation of the protein-coding hits in independent cohorts, (ii) cellular deconvolution to rule out compositional confounding, and (iii) targeted GREM1 functional studies as the highest-priority mechanistic candidate.
