# chronic obstructive pulmonary disease (COPD) - gemini-3.6-flash

- Benchmark system: E2seq + Agent RAG
- Repeat: 3
- Task type: DISEASE-STATE
- Tissue / sample source: lung tissue
- Comparison or endpoint: COPD versus normal control
- Answer input cohort: Discovery/Core only
- Selected items: 100
- Input fields: gene name, effect size (log2FC/HR), P value, FDR
- E2seq Agent RAG: enabled
- Conversation memory: disabled
- Thinking mode: disabled
- Held-out validation data in prompt/RAG: no
- Model API: Google Gemini / gemini-3.6-flash
- Message SHA-256: 75cb1462dc859d10e673df1637d9bfb35fbfd41f53bda923e17881eee80cc2ef
- Response HTTP status: 200
- Prompt tokens: 82642
- Completion tokens: 69724
- Reasoning tokens: 24790
- Total tokens: 152366
- API requests reported: 5
- Elapsed seconds: 66.05
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 936.215
- Question handoff seconds: 951.58
- Final benchmark system: E2seq; file rank 2/5; original repeat 3; model vendor: Google Gemini

---
### 1. Overall Biological Interpretation

The provided transcriptomic dataset compares human chronic obstructive pulmonary disease (COPD) lung tissue to normal control lung tissue across 100 statistically significant unique features (83 upregulated and 17 downregulated; all false discovery rates $\text{FDR} \le 0.0204$). 

Rather than isolated gene alterations, the transcriptomic program reveals four integrated pathological themes characterizing diseased lung tissue:
1. **Airway Epithelial Barrier Integrity and Extracellular Matrix (ECM) Remodeling:** Robust upregulation of structural, tight-junction, and matricellular regulators (e.g., *MACF1*, *CLDN16*, *GREM1*, *FGG*, *TENM3*) indicates ongoing tissue repair, altered paracellular permeability, and ECM remodeling secondary to chronic airway injury.
2. **Innate Mucosal Defense and Leukocyte Activation:** Significant elevation of antimicrobial peptides and inflammatory mediators (e.g., *DEFB1*, *IGKV1-8*, *MGAM*, *CRACR2A*, *NCR3LG1*) reflects persistent airway luminal inflammation and immune cell engagement.
3. **Non-Coding RNA Transcriptional and Post-Transcriptional Networks:** High representation of upregulated long non-coding RNAs (lncRNAs) and microRNAs (e.g., *CELF2-AS1*, *SNX29-AS3*, *PTCSC1*, *LRP1-AS*, *TGFB2-AS1*, *INHBA-AS1*, *MIR132*) highlights altered non-coding epigenetic and post-transcriptional regulatory architecture in COPD lungs.
4. **Bioenergetic and Translational Suppression:** Downregulation of mitochondrial respiratory chain subunit transcripts and ribosomal/translation-associated factors (e.g., *UQCRBP1*, *RPL23AP32*, *NACA2*) suggests localized cellular stress and impaired oxidative energy production.

Because external statistical validation was not performed on an independent cohort in this context, these transcriptomic patterns represent biologically grounded exploratory signatures within the supplied dataset.

---

### 2. Core Biological Programs

```
+---------------------------------------------------------------------------------------------------+
|                                     CORE BIOLOGICAL PROGRAMS                                      |
+------------------------------------+---------------+---------------------+------------------------+
| Program Name                       | Direction     | Key Genes           | Representative Pathway |
+------------------------------------+---------------+---------------------+------------------------+
| 1. Epithelial & ECM Remodeling     | Upregulated   | GREM1, MACF1, CLDN16| Reactome: ECM          |
|                                    |               | FGG, TENM3          | organization           |
| 2. Innate Mucosal Defense          | Upregulated   | DEFB1, IGKV1-8, MGAM| GO: Innate immune      |
|                                    |               | CRACR2A, NCR3LG1    | response               |
| 3. Non-Coding Regulatory Network   | Upregulated   | CELF2-AS1, MIR132   | Reactome: ncRNA        |
|                                    |               | TGFB2-AS1, INHBA-AS1| processing             |
| 4. Bioenergetic & Metabolic Shift  | Downregulated | UQCRBP1, RPL23AP32  | Reactome: Respiratory  |
|                                    |               | NACA2               | electron transport     |
+------------------------------------+---------------+---------------------+------------------------+
```

#### Program 1: Epithelial Barrier Integrity and Extracellular Matrix Remodeling
* **Direction:** Upregulated in COPD lung tissue.
* **Major Supporting Genes:** *MACF1* ($\text{log}_2\text{FC} = 1.5574$, $\text{FDR} = 4.017 \times 10^{-7}$), *CLDN16* ($\text{log}_2\text{FC} = 1.6960$, $\text{FDR} = 3.869 \times 10^{-4}$), *GREM1* ($\text{log}_2\text{FC} = 1.6519$, $\text{FDR} = 7.160 \times 10^{-3}$), *FGG* ($\text{log}_2\text{FC} = 1.7630$, $\text{FDR} = 5.306 \times 10^{-3}$), *TENM3* ($\text{log}_2\text{FC} = 0.9747$, $\text{FDR} = 0.0107$).
* **Standardized Pathway:** Reactome: Extracellular matrix organization (`R-HSA-1474244`) / GO: Cell adhesion (`GO:0007155`).
* **Biological Explanation:** *MACF1* crosslinks microfilaments and microtubules to maintain cellular architecture, while *CLDN16* forms tight junction complexes regulating paracellular transport. *GREM1* (Gremlin-1) acts as a bone morphogenetic protein (BMP) antagonist driving Transforming Growth Factor-beta (TGF-$\beta$) dependent fibrotic extracellular matrix deposition. *FGG* (fibrinogen gamma chain) accumulates during vascular permeability and tissue repair. Together, these genes signal active architectural degradation and compensatory fibrotic repair in COPD parenchymal and airway tissue.
* **Evidence & Limitations:** Supported by high effect sizes ($\text{log}_2\text{FC} > 1.5$) and low FDR values. Limitations include bulk tissue heterogeneity, making it impossible to separate alveolar wall breakdown from bronchial epithelial wall thickening without spatial resolution.

#### Program 2: Innate Mucosal Defense and Leukocyte Inflammation
* **Direction:** Upregulated in COPD lung tissue.
* **Major Supporting Genes:** *DEFB1* ($\text{log}_2\text{FC} = 1.4044$, $\text{FDR} = 7.366 \times 10^{-3}$), *IGKV1-8* ($\text{log}_2\text{FC} = 1.8424$, $\text{FDR} = 8.586 \times 10^{-4}$), *MGAM* ($\text{log}_2\text{FC} = 1.4866$, $\text{FDR} = 1.072 \times 10^{-3}$), *CRACR2A* ($\text{log}_2\text{FC} = 1.0343$, $\text{FDR} = 3.572 \times 10^{-4}$), *NCR3LG1* ($\text{log}_2\text{FC} = 0.9453$, $\text{FDR} = 4.479 \times 10^{-3}$).
* **Standardized Pathway:** GO: Innate immune response (`GO:0045087`) / Reactome: Neutrophil degranulation (`R-HSA-6798695`).
* **Biological Explanation:** *DEFB1* encodes Beta-Defensin 1, an antimicrobial peptide constitutively expressed by airway epithelia to defend against microbial colonization. *MGAM* plays roles in carbohydrate hydrolysis and neutrophil degranulation granules. *CRACR2A* mediates calcium flux driving T-cell and innate lymphocyte activation, while *IGKV1-8* reflects local B-cell/plasma cell humoral activity.
* **Evidence & Limitations:** Strongly aligned with established COPD airway pathophysiology. However, bulk transcriptomics cannot distinguish whether upregulation stems from increased transcript induction per cell or leukocyte infiltration into the tissue biopsy.

#### Program 3: Non-Coding Regulatory RNA Networks
* **Direction:** Upregulated in COPD lung tissue.
* **Major Supporting Genes:** *CELF2-AS1* ($\text{log}_2\text{FC} = 2.0551$, $\text{FDR} = 1.084 \times 10^{-8}$), *SNX29-AS3* ($\text{log}_2\text{FC} = 1.6777$, $\text{FDR} = 1.005 \times 10^{-9}$), *PTCSC1* ($\text{log}_2\text{FC} = 1.6157$, $\text{FDR} = 3.134 \times 10^{-6}$), *LRP1-AS* ($\text{log}_2\text{FC} = 1.2851$, $\text{FDR} = 3.134 \times 10^{-6}$), *MIR132* ($\text{log}_2\text{FC} = 1.6461$, $\text{FDR} = 2.372 \times 10^{-4}$), *TGFB2-AS1* ($\text{log}_2\text{FC} = 1.0385$, $\text{FDR} = 7.366 \times 10^{-3}$), *INHBA-AS1* ($\text{log}_2\text{FC} = 1.1893$, $\text{FDR} = 0.0136$).
* **Standardized Pathway:** Reactome: ncRNA processing (`R-HSA-6781827`) / GATA6-AS1 lncRNA pathway (`R-HSA-9827615`).
* **Biological Explanation:** Antisense lncRNAs frequently act as *cis*- or *trans*-regulatory elements modulating parental gene expression or chromatin remodeling. For example, *TGFB2-AS1* and *INHBA-AS1* are non-coding antisense transcripts associated with TGF-$\beta$/activin family growth factor loci, central mediators of pulmonary remodeling. *MIR132* is an established regulator of inflammatory cascades and cellular senescence.
* **Evidence & Limitations:** Comprises the largest total fraction of high-fold-change hits in the dataset. Limited by incomplete functional annotation for novel lncRNA loci in standardized reference databases.

#### Program 4: Bioenergetic and Metabolic Suppression
* **Direction:** Downregulated in COPD lung tissue.
* **Major Supporting Genes:** *UQCRBP1* ($\text{log}_2\text{FC} = -1.2049$, $\text{FDR} = 3.134 \times 10^{-6}$), *RPL23AP32* ($\text{log}_2\text{FC} = -1.6567$, $\text{FDR} = 1.359 \times 10^{-4}$), *NACA2* ($\text{log}_2\text{FC} = -1.1534$, $\text{FDR} = 4.022 \times 10^{-4}$).
* **Standardized Pathway:** Reactome: Respiratory electron transport (`R-HSA-611105`) / KEGG: Oxidative phosphorylation (`hsa00190`).
* **Biological Explanation:** Downregulation of mitochondrial Complex III-associated transcripts (*UQCRBP1*) alongside nascent polypeptide complex and ribosomal components (*NACA2*, *RPL23AP32*) points to metabolic exhaustion, oxidative stress damage, or mitochondrial dysfunction in severe COPD parenchymal tissue.
* **Evidence & Limitations:** Conforms to known mitochondrial pathology in chronic lung disease. However, only 17 total genes in the input dataset are downregulated, constraining comprehensive pathway overrepresentation testing.

---

### 3. Key Genes and Interaction Modules

```
+----------------------------------------------------------------------------------------------------+
|                                    KEY GENES AND RELATIONSHIPS                                     |
+--------------+---------------+--------------------------------------+------------------------------+
| Gene Symbol  | Input Status  | Core Biological Role                 | Proposed Relationship Type   |
+--------------+---------------+--------------------------------------+------------------------------+
| 1. ETV3L     | Upregulated   | Transcription factor regulation      | Putative regulatory          |
| 2. GREM1     | Upregulated   | BMP antagonist / ECM fibrosis driver | Pathway co-membership        |
| 3. MACF1     | Upregulated   | Cytoskeletal actin-microtubule cross | Pathway co-membership        |
| 4. DEFB1     | Upregulated   | Antimicrobial mucosal defense peptide| Pathway co-membership        |
| 5. CELF2-AS1 | Upregulated   | Antisense RNA splicing regulator     | Putative regulatory          |
| 6. UQCRBP1   | Downregulated | Mitochondrial respiratory complex III| Pathway co-membership        |
| 7. CLDN16    | Upregulated   | Epithelial tight junction pore       | Pathway co-membership        |
| 8. MIR132    | Upregulated   | Inflammatory microRNA regulator      | Putative regulatory          |
| 9. AAK1      | Upregulated   | AP2-associated endocytic kinase      | Direct physical interaction  |
| 10. TGFB2-AS1| Upregulated   | Remodeling lncRNA (TGF-beta locus)   | Co-expression / Indirect     |
+--------------+---------------+--------------------------------------+------------------------------+
```

1. **ETV3L** ($\text{log}_2\text{FC} = 1.4722$, $P = 1.366 \times 10^{-15}$, $\text{FDR} = 2.749 \times 10^{-11}$)
   * **Role:** ETS-family transcription factor involved in cellular differentiation and nuclear transcriptional programs.
   * **Relationship:** Putative regulatory interaction with downstream nuclear transcriptional networks (GO: Nucleus annotation).
2. **GREM1** ($\text{log}_2\text{FC} = 1.6519$, $P = 2.312 \times 10^{-5}$, $\text{FDR} = 7.160 \times 10^{-3}$)
   * **Role:** Secreted BMP antagonist that promotes TGF-$\beta$ mediated pulmonary fibrotic repair and airway remodeling.
   * **Relationship:** Pathway co-membership with *TGFB2-AS1* and *FGG* within extracellular matrix synthesis and remodeling networks.
3. **MACF1** ($\text{log}_2\text{FC} = 1.5574$, $P = 7.982 \times 10^{-11}$, $\text{FDR} = 4.017 \times 10^{-7}$)
   * **Role:** Cytoskeletal cross-linker connecting actin filaments and microtubules to maintain cellular structural integrity.
   * **Relationship:** Pathway co-membership and cell-structural co-expression with tight-junction components like *CLDN16*.
4. **DEFB1** ($\text{log}_2\text{FC} = 1.4044$, $P = 2.563 \times 10^{-5}$, $\text{FDR} = 7.366 \times 10^{-3}$)
   * **Role:** Antimicrobial peptide protecting epithelial surfaces against microbial pathogen invasion.
   * **Relationship:** Pathway co-membership and co-expression within innate mucosal immune response programs alongside *IGKV1-8* and *MGAM*.
5. **CELF2-AS1** ($\text{log}_2\text{FC} = 2.0551$, $P = 1.616 \times 10^{-12}$, $\text{FDR} = 1.084 \times 10^{-8}$)
   * **Role:** Top upregulated transcript in dataset; antisense non-coding RNA associated with pre-mRNA splicing regulator loci.
   * **Relationship:** Putative regulatory interaction (antisense-mediated post-transcriptional processing).
6. **UQCRBP1** ($\text{log}_2\text{FC} = -1.2049$, $P = 1.556 \times 10^{-9}$, $\text{FDR} = 3.134 \times 10^{-6}$)
   * **Role:** Key downregulated mitochondrial respiratory subunit transcript linked to electron transport.
   * **Relationship:** Pathway co-membership with ribosomal and protein processing factors (*RPL23AP32*, *NACA2*) in metabolic maintenance.
7. **CLDN16** ($\text{log}_2\text{FC} = 1.6960$, $P = 6.961 \times 10^{-7}$, $\text{FDR} = 3.869 \times 10^{-4}$)
   * **Role:** Claudin family transmembrane protein regulating tight junction permeability and ion transport.
   * **Relationship:** Pathway co-membership with *MACF1* in epithelial cell junction architecture.
8. **MIR132** ($\text{log}_2\text{FC} = 1.6461$, $P = 3.064 \times 10^{-7}$, $\text{FDR} = 2.372 \times 10^{-4}$)
   * **Role:** MicroRNA regulator involved in neuroinflammatory signaling and cell survival.
   * **Relationship:** Putative regulatory interaction (microRNA-mediated mRNA suppression).
9. **AAK1** ($\text{log}_2\text{FC} = 0.9916$, $P = 8.668 \times 10^{-7}$, $\text{FDR} = 4.474 \times 10^{-4}$)
   * **Role:** AP2-associated protein kinase 1 governing clathrin-mediated endocytosis and receptor trafficking.
   * **Relationship:** Direct physical interaction (validated kinase-substrate interactions in OmniPath/PhosphoSite databases) with AP2 endocytic adaptor complexes.
10. **TGFB2-AS1** ($\text{log}_2\text{FC} = 1.0385$, $P = 2.474 \times 10^{-5}$, $\text{FDR} = 7.366 \times 10^{-3}$)
    * **Role:** Non-coding antisense transcript at the TGFB2 locus involved in modulating TGF-$\beta$ signaling.
    * **Relationship:** Indirect regulatory relationship and pathway co-membership with *GREM1* in tissue remodeling.

---

### 4. Validation Priorities

#### Priority 1: GREM1-Driven BMP/TGF-$\beta$ Airway Remodeling Axis
* **Classification:** Mechanistic hypothesis
* **Why Prioritized:** *GREM1* is heavily upregulated ($\text{log}_2\text{FC} = 1.6519$, $\text{FDR} = 0.0072$) and represents a well-characterized inhibitor of BMP signaling that promotes fibrotic extracellular matrix expansion.
* **Input Dataset Evidence:** Statistically significant transcript elevation in COPD vs. control lung tissue.
* **External Evidence:** Published functional studies demonstrate Gremlin-1 induction in chronic obstructive lung disease and pulmonary fibrosis driven by smoke exposure.
* **Next Validation Step:** *In vitro* knockout or siRNA knockdown of *GREM1* in human bronchial epithelial cells (HBECs) exposed to cigarette smoke extract, quantifying collagen deposition and EMT markers.
* **Conclusion Status:** Supported hypothesis.

#### Priority 2: DEFB1 Antimicrobial Mucosal Defense in Airway Secretions
* **Classification:** Biomarker
* **Why Prioritized:** *DEFB1* ($\text{log}_2\text{FC} = 1.4044$, $\text{FDR} = 0.0074$) provides a direct link between epithelial transcription and mucosal immunity against bacterial colonization.
* **Input Dataset Evidence:** Significant statistical upregulation in diseased lung tissue.
* **External Evidence:** Beta-defensin-1 protein is detectable in sputum and bronchoalveolar lavage fluid (BALF), with altered secretion linked to COPD exacerbation frequency.
* **Next Validation Step:** ELISA measurement of DEFB1 protein levels in BALF and sputum samples across GOLD stage I–IV COPD patients vs. healthy controls.
* **Conclusion Status:** Supported hypothesis.

#### Priority 3: MACF1–CLDN16 Epithelial Barrier Tight Junction Integrity
* **Classification:** Interaction / network hypothesis
* **Why Prioritized:** High effect sizes for both cytoskeletal (*MACF1*, $\text{log}_2\text{FC} = 1.5574$) and tight junction (*CLDN16*, $\text{log}_2\text{FC} = 1.6960$) genes suggest structural remodeling of the airway epithelial barrier.
* **Input Dataset Evidence:** Concordant strong statistical upregulation in bulk tissue transcriptomics.
* **External Evidence:** Loss of epithelial barrier integrity and altered tight junction protein expression are hallmark features of chronic smoke-induced lung disease.
* **Next Validation Step:** Immunofluorescence co-localization and transepithelial electrical resistance (TEER) permeability assays in primary air-liquid interface (ALI) cultured human airway epithelial cells.
* **Conclusion Status:** Exploratory hypothesis.

#### Priority 4: Functional Characterization of CELF2-AS1 Non-Coding RNA
* **Classification:** Mechanistic hypothesis
* **Why Prioritized:** *CELF2-AS1* is among the most significantly upregulated transcripts in the study ($\text{log}_2\text{FC} = 2.0551$, $\text{FDR} = 1.084 \times 10^{-8}$).
* **Input Dataset Evidence:** Very strong statistical confidence and effect size.
* **External Evidence:** Broad lncRNA literature supports role in RNA-binding protein sequestering, but direct functional data for *CELF2-AS1* in chronic lung disease remains absent.
* **Next Validation Step:** Antisense oligonucleotide (ASO) knock-down followed by RNA sequencing to identify downstream mRNA stability and pre-mRNA splicing alterations.
* **Conclusion Status:** Exploratory hypothesis.

#### Priority 5: Cell Deconvolution of Epithelial vs. Inflammatory Signals
* **Classification:** Confounding or composition check
* **Why Prioritized:** Bulk transcriptomics blends parenchymal, airway epithelial, vascular, and infiltrating immune cell transcripts.
* **Input Dataset Evidence:** Co-existence of mucosal/epithelial markers (*CLDN16*, *DEFB1*) and leukocyte transcripts (*IGKV1-8*, *MGAM*, *NCR3LG1*).
* **External Evidence:** Single-cell RNA-sequencing (scRNA-seq) atlases of human COPD lungs show major shifts in cellular proportions, such as neutrophil recruitment and loss of alveolar type II cells.
* **Next Validation Step:** Apply computational deconvolution algorithms (e.g., CIBERSORTx) to the bulk dataset, followed by single-nucleus RNA-seq or spatial transcriptomics on matching frozen tissue biopsies.
* **Conclusion Status:** Supported hypothesis.

---

### 5. Evidence Grounding

The conclusions in this report rely on distinct, explicitly categorized layers of evidence:

```
+--------------------------------------------------------------------------------------------------+
|                                  EVIDENCE GROUNDING MATRIX                                       |
+--------------------------+----------------------------------+------------------------------------+
| Evidence Category        | Sources Covered                  | Directness / Independence Status   |
+--------------------------+----------------------------------+------------------------------------+
| 1. Direct Input Data     | Uploaded transcriptomic table    | Direct cohort evidence (Primary)   |
| 2. External Validation   | None supplied in context         | NOT PERFORMED (0 external cohorts) |
| 3. Pathway & Ontology    | Reactome, QuickGO                | Non-independent secondary context  |
| 4. Network Interactions  | OmniPath, STRING                 | Non-independent physical/co-expr   |
| 5. Literature & Disease  | PubMed, Europe PMC, Open Targets | External functional context        |
+--------------------------+----------------------------------+------------------------------------+
```

* **Direct Evidence from Input Dataset:** Primary statistical parameters provided in the ledger (100 unique genes, $\text{FDR} \le 0.0204$, $\text{log}_2\text{FC}$ range $-1.6567$ to $+2.0551$) serve as the definitive quantitative foundation.
* **External Statistical Validation:** **External statistical validation was not performed** because no independent validation cohort dataset or external statistical replication metrics were provided.
* **Pathway / Ontology Evidence:** Standardized database annotations (Reactome, QuickGO) contextualize high-level program assignment (e.g., ECM organization, innate immune response). Note that pathway databases frequently draw from overlapping primary literature and do not constitute independent statistical replication.
* **Protein Interaction / Regulatory Evidence:** OmniPath and STRING databases confirm direct physical interaction evidence for *AAK1* endocytic kinase complexes, while structural and non-coding RNA relationships represent pathway co-membership or co-expression rather than direct physical binding.
* **Disease / Literature Evidence:** Literature records (PubMed, Europe PMC) provide functional plausibility for *GREM1* in pulmonary fibrosis/remodeling, *DEFB1* in airway antimicrobial response, and *MIR132* in chronic inflammation.

---

### 6. Limitations and Alternative Explanations

1. **Bulk Tissue Cell-Composition Confounding:** Bulk lung tissue homogenates merge signals from multiple cell types. Upregulation of immunoglobulin (*IGKV1-8*) or myeloid (*MGAM*) genes may reflect inflammatory cell infiltration into the lung tissue rather than intrinsic transcriptional activation of lung parenchymal cells.
2. **Absence of Independent Cohort Replication:** Without external statistical validation in an independent COPD clinical dataset, individual gene associations must be considered exploratory and subject to potential cohort-specific bias.
3. **High Fraction of Uncharacterized Non-Coding RNAs:** Many top statistical hits are lncRNAs, pseudogenes, or microRNA precursors (e.g., *SNX29-AS3*, *PTCSC1*, *ANP32A-IT1*, *LOC100131395*). Current functional databases lack detailed mechanistic annotations for these non-protein-coding loci.
4. **Association vs. Causation Ambiguity:** Transcriptional changes in extracellular matrix remodeling (*GREM1*, *FGG*) or innate defense (*DEFB1*) may represent secondary stress responses or reactive inflammation rather than primary causal drivers of disease pathogenesis.
5. **Unadjusted Clinical Confounders:** The input dataset lacks metadata regarding patient smoking status, pack-years, disease severity stage (GOLD I–IV), steroid medication exposure, or acute exacerbation status, all of which introduce unmeasured biological variance.

Computational cell deconvolution and spatial transcriptomics represent the most effective experimental strategies to resolve these cell-type and composition ambiguities.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=10, external claims checked=0, external mismatches=0, status=needs review.

Answer model API: Google Gemini / gemini-3.6-flash

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 67/100 selected items (records returned); cbioportal 68/100 selected items (records returned); chembl 31/100 selected items (records returned); civic 1/100 selected items (records returned); clinicaltrials 13/100 selected items (records returned); clinvar 68/100 selected items (records returned); ensembl 29/100 selected items (partially returned; some queries failed); europepmc 657 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 43/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 17/100 selected items (records returned); humanbase 89/100 selected items (partially returned; some queries failed); intact 20/100 selected items (records returned); mygene 93/100 selected items (records returned); omnipath 9/100 selected items (records returned); opentargets 65/100 selected items (records returned); pubmed 254 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 22/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 23/100 selected items (records returned)
Local databases: gutmgene 0/100 selected items (reachable but no records for this batch); hmdb 4/100 selected items (records returned); string 19/100 selected items (records returned); trrust 2/100 selected items (records returned)
