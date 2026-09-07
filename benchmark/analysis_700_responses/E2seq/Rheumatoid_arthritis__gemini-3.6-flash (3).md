# rheumatoid arthritis - gemini-3.6-flash

- Benchmark system: E2seq + Agent RAG
- Repeat: 4
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
- Model API: Google Gemini / gemini-3.6-flash
- Message SHA-256: d868ce3efb219458b8d5ddb7b123eef3f2b718852ba0ede74f2a02e9181db293
- Response HTTP status: 200
- Prompt tokens: 44449
- Completion tokens: 30271
- Reasoning tokens: 5567
- Total tokens: 74720
- API requests reported: 3
- Elapsed seconds: 44.873
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 984.622
- Question handoff seconds: 999.892
- Final benchmark system: E2seq; file rank 3/5; original repeat 4; model vendor: Google Gemini

---
### Technical Data-Quality Warning & Validation Status

* **Unidirectional Downregulation Bias:** 100% of the selected 100 differential genes in this dataset exhibit uniform downregulation ($\text{log}_2\text{FC}$ ranging from $-2.279$ to $-5.102$, with $\text{FDR} \le 1.56 \times 10^{-35}$). This extreme, unidirectional distribution across all top features—accompanied by a high proportion of non-coding RNAs, pseudogenes, and uncharacterized genomic loci—strongly suggests potential sample composition shifts (e.g., massive inflammatory cell infiltration diluting resident cell transcripts) or preprocessing/filtering artifacts.
* **External Statistical Validation:** **External statistical validation was not performed.** No independent cohort validation statistics were supplied in the input dataset. Biological annotations derived from database records (STRING, Reactome, QuickGO, OpenTargets) are used strictly as contextual evidence to evaluate functional plausibility and hypothesis generation.

---

### 1. Overall Biological Interpretation

The provided transcriptomic dataset compares synovial tissue from patients with **rheumatoid arthritis (RA)** against normal controls. The principal transcriptomic signature is defined by a consistent reduction in transcripts linked to **synovial tissue architecture**, **cell-cell junctional integrity**, **mucosal/surface lining barrier protection**, and **post-transcriptional non-coding RNA networks**.

Rather than isolated gene loss, the co-downregulation of intercellular adhesion complexes (*CDHR5*, *ARVCF*, *GJC2*), cell polarity scaffolds (*SCRIB*), and centrosomal/microtubule structural proteins (*CROCC*, *CROCC2*) points to structural degradation or loss of specialized synovial lining cellular phenotypes. Concurrently, major mucosal protective barrier components (*MUC12*, *MUC5B*, *MUC6*) and structural matrix components (*ADAMTS7*) are markedly reduced. 

Because RA synovial pathology involves extensive synovial lining hyperplasia, barrier erosion, and heavy leukocyte infiltration (macrophages, T cells, plasma cells), these transcriptomic reductions likely reflect a combination of intrinsic cellular dysregulation within resident synoviocytes and relative cell-type dilution caused by immune cell influx into the diseased tissue.

---

### 2. Core Biological Programs

```
                       ┌──────────────────────────────────────────────────────────┐
                       │  RA vs. Normal Control Synovial Transcriptomic Profile   │
                       │           (100% Downregulated DEG Selection)             │
                       └────────────────────────────┬─────────────────────────────┘
                                                    │
         ┌──────────────────────────────┬───────────┴──────────────┬──────────────────────────────┐
         ▼                              ▼                          ▼                              ▼
┌─────────────────┐           ┌─────────────────┐        ┌──────────────────┐           ┌──────────────────┐
│  1. Cell-Cell   │           │ 2. Mucosal &    │        │ 3. Wnt / Hippo   │           │ 4. NcRNA & Post- │
│  Junction &     │           │    Surface      │        │    Cytoskeletal  │           │    Transcript.   │
│  Polarity       │           │    Barrier      │        │    Signaling     │           │    Regulation    │
├─────────────────┤           ├─────────────────┤        ├──────────────────┤           ├──────────────────┤
│ CDHR5, SCRIB,   │           │ MUC12, MUC5B,   │        │ APC2, ARVCF,     │           │ MIR3154, MIR3183,│
│ ARVCF, GJC2,    │           │ MUC6            │        │ INF2, ARHGAP33,  │           │ CXXC5-AS1,       │
│ CROCC, ADAMTS7  │           │                 │        │ PPP1R12C         │           │ PCGF3-AS1        │
└─────────────────┘           └─────────────────┘        └──────────────────┘           └──────────────────┘
```

#### Program 1: Synovial Cell Adhesion, Junctional Integrity, and Tissue Architecture
* **Direction:** Downregulated in RA
* **Major Supporting Genes:** *CDHR5* ($\text{log}_2\text{FC} = -4.224$, $\text{FDR} = 1.613 \times 10^{-45}$), *SCRIB* ($\text{log}_2\text{FC} = -3.235$, $\text{FDR} = 1.316 \times 10^{-42}$), *ARVCF* ($\text{log}_2\text{FC} = -3.462$, $\text{FDR} = 1.008 \times 10^{-38}$), *GJC2* ($\text{log}_2\text{FC} = -3.496$, $\text{FDR} = 5.114 \times 10^{-40}$), *CROCC* ($\text{log}_2\text{FC} = -3.883$, $\text{FDR} = 9.665 \times 10^{-48}$), *CROCC2* ($\text{log}_2\text{FC} = -4.994$, $\text{FDR} = 1.215 \times 10^{-40}$), *ADAMTS7* ($\text{log}_2\text{FC} = -3.294$, $\text{FDR} = 2.386 \times 10^{-35}$)
* **Standardized Pathway:** GO:0007155 (Cell Adhesion) / GO:0030054 (Cell Junction) / Reactome R-CFA-9013148 (CDC42 GTPase cycle)
* **Biological Rationale:** Collective suppression of cadherin-related proteins (*CDHR5*), basolateral polarity scaffolds (*SCRIB*), armadillo-repeat adherens junction components (*ARVCF*), gap junction channels (*GJC2*), and ciliary/centrosomal rootlet structural elements (*CROCC*, *CROCC2*) indicates disruption of intercellular physical contact and tissue polarity in rheumatoid synovium.
* **Evidence Strength & Limitations:** High direct statistical significance in the input dataset; supported by GO cellular component annotations. Main limitation: bulk tissue downregulation can be artifically induced by cell-composition shifts (immune cell expansion diluting resident synovial lining cells).

#### Program 2: Mucosal and Synovial Surface Barrier Mucin Suppression
* **Direction:** Downregulated in RA
* **Major Supporting Genes:** *MUC12* ($\text{log}_2\text{FC} = -4.270$, $\text{FDR} = 6.049 \times 10^{-43}$), *MUC5B* ($\text{log}_2\text{FC} = -4.426$, $\text{FDR} = 2.068 \times 10^{-40}$), *MUC6* ($\text{log}_2\text{FC} = -3.854$, $\text{FDR} = 5.919 \times 10^{-36}$)
* **Standardized Pathway:** Reactome / GO:0005576 (Extracellular Region / Mucin Glycoprotein Complex)
* **Biological Rationale:** Membrane-bound (*MUC12*) and gel-forming (*MUC5B*, *MUC6*) mucins form viscoelastic protective mucosal/lining shields. Their joint reduction reflects severe loss of surface lining protection and lubricant secretion in inflamed joints.
* **Evidence Strength & Limitations:** Strong direct effect sizes ($\text{log}_2\text{FC} < -3.85$); reinforced by STRING co-occurrence network modules (*MUC1*, *MUC2*, *MUC5AC*). Limitation: Mucin expression in normal synovial tissue is restricted to specialized lining layers, making it highly sensitive to lining erosion during pannus formation.

#### Program 3: Wnt/Beta-Catenin and Cytoskeletal Signaling Modulation
* **Direction:** Downregulated in RA
* **Major Supporting Genes:** *APC2* ($\text{log}_2\text{FC} = -3.018$, $\text{FDR} = 4.634 \times 10^{-39}$), *ARVCF* ($\text{log}_2\text{FC} = -3.462$, $\text{FDR} = 1.008 \times 10^{-38}$), *INF2* ($\text{log}_2\text{FC} = -2.759$, $\text{FDR} = 8.103 \times 10^{-36}$), *ARHGAP33* ($\text{log}_2\text{FC} = -3.202$, $\text{FDR} = 1.670 \times 10^{-36}$), *PPP1R12C* ($\text{log}_2\text{FC} = -2.697$, $\text{FDR} = 2.377 \times 10^{-35}$)
* **Standardized Pathway:** KEGG: Hippo signaling pathway / Wnt destruction complex / GO:0005856 (Cytoskeleton)
* **Biological Rationale:** *APC2* is a structural homolog of APC involved in the beta-catenin destruction complex. Its downregulation, combined with loss of *ARVCF* (which interacts directly with $\beta$-catenin/*CTNNB1*) and actin-severing/regulatory proteins (*INF2*, *ARHGAP33*), points to altered intracellular Wnt signaling stability and microfilament remodeling.
* **Evidence Strength & Limitations:** Network evidence from STRING links *APC2* and *ARVCF* to $\beta$-catenin (*CTNNB1*); however, explicit functional downstream target changes of Wnt activation are not evaluated in this input.

#### Program 4: Non-Coding RNA and Post-Transcriptional Regulatory Suppression
* **Direction:** Downregulated in RA
* **Major Supporting Genes:** *MIR3154* ($\text{log}_2\text{FC} = -5.101$, $\text{FDR} = 5.973 \times 10^{-43}$), *MIR3183* ($\text{log}_2\text{FC} = -4.614$, $\text{FDR} = 5.465 \times 10^{-47}$), *MIR3615* ($\text{log}_2\text{FC} = -4.129$, $\text{FDR} = 4.236 \times 10^{-43}$), *MIR937* ($\text{log}_2\text{FC} = -3.696$, $\text{FDR} = 2.029 \times 10^{-42}$), *CXXC5-AS1* ($\text{log}_2\text{FC} = -3.932$, $\text{FDR} = 1.444 \times 10^{-41}$), *PCGF3-AS1* ($\text{log}_2\text{FC} = -3.523$, $\text{FDR} = 1.099 \times 10^{-46}$), *SCARNA17* ($\text{log}_2\text{FC} = -3.831$, $\text{FDR} = 1.881 \times 10^{-41}$), *RNA5-8SN2* ($\text{log}_2\text{FC} = -5.102$, $\text{FDR} = 3.408 \times 10^{-40}$)
* **Standardized Pathway:** KEGG: Ribosome biogenesis / NcRNA processing / GO:0030529 (Ribonucleoprotein complex)
* **Biological Rationale:** Extensive downregulation of microRNAs, antisense lncRNAs, small Cajal body-specific RNAs (*SCARNA17*), and ribosomal RNA fragments (*RNA5-8SN2*, *RNA5-8SN3*, *RNA5-8SN4*) highlights widespread suppression of non-coding regulatory machinery.
* **Evidence Strength & Limitations:** Features show some of the largest negative fold-changes in the study; however, many non-coding RNAs lack confirmed cell-type-specific targets in human synovium.

---

### 3. Key Genes and Interaction Modules

| Key Gene / Module | Direction in Dataset | Biological Role | Proposed Relationship Type & Interacting Partners |
| :--- | :--- | :--- | :--- |
| **SCRIB** | Downregulated ($\text{log}_2\text{FC} = -3.235$, $\text{FDR} = 1.316 \times 10^{-42}$) | Cell polarity scaffold protein; regulates basolateral membrane assembly and tissue architecture. | **Direct Physical Interaction** (STRING: confidence > 0.98 with *ARHGEF7*, *VANGL2*, *GIT1*); **Pathway Co-membership** with cell junction components. |
| **APC2** | Downregulated ($\text{log}_2\text{FC} = -3.018$, $\text{FDR} = 4.634 \times 10^{-39}$) | Wnt signaling regulator; component of the $\beta$-catenin destruction complex. | **Direct Physical Interaction** (STRING: *CTNNB1*); **Pathway Co-membership** (Wnt destruction complex with *ARVCF*). |
| **ARVCF** | Downregulated ($\text{log}_2\text{FC} = -3.462$, $\text{FDR} = 1.008 \times 10^{-38}$) | Cadherin-associated armadillo family protein; anchors adherens junctions to the cytoskeleton. | **Direct Physical Interaction** (STRING: confidence > 0.80 with *CTNNB1*, *ERBIN*, *COMT*); **Pathway Co-membership** (*CDHR5*, *SCRIB*). |
| **MUC5B / MUC12 / MUC6 Module** | Downregulated ($\text{log}_2\text{FC} = -4.426$, $-4.270$, $-3.854$) | Gel-forming and cell-tethered mucins protecting lining epithelium and synovial surfaces. | **Pathway Co-membership & Co-expression** (STRING network links to *MUC1*, *MUC2*, *MUC5AC*); no direct heteromeric physical complex implied. |
| **CDHR5** | Downregulated ($\text{log}_2\text{FC} = -4.224$, $\text{FDR} = 1.613 \times 10^{-45}$) | Cadherin superfamily member involved in microvillar packing and inter-cellular adhesion. | **Pathway Co-membership** with adherens junction and cell polarity scaffolding complexes (*ARVCF*, *SCRIB*). |
| **GJC2** | Downregulated ($\text{log}_2\text{FC} = -3.496$, $\text{FDR} = 5.114 \times 10^{-40}$) | Connexin-47 gap junction protein facilitating intercellular small-molecule exchange. | **Direct Physical Interaction** (STRING: confidence > 0.79 with *FAM126A*, *PNPLA6*, *GJB2*); **Pathway Co-membership** (Gap junctions). |
| **ADAMTS7** | Downregulated ($\text{log}_2\text{FC} = -3.294$, $\text{FDR} = 2.386 \times 10^{-35}$) | Metalloproteinase involved in extracellular matrix degradation and cartilage matrix protein turnover. | **Pathway Co-membership** in extracellular matrix remodeling and cell-matrix interactions. |
| **INF2** | Downregulated ($\text{log}_2\text{FC} = -2.759$, $\text{FDR} = 8.103 \times 10^{-36}$) | Formin family actin-severing protein regulating organelle dynamics and cytoskeletal assembly. | **Pathway Co-membership** with actin-binding and GTPase regulators (*ARHGAP33*, *PPP1R12C*). |
| **CROCC / CROCC2 Module** | Downregulated ($\text{log}_2\text{FC} = -3.883$, $-4.994$) | Rootletin structural proteins organizing centrosomal cohesion and ciliary rootlet stability. | **Direct Physical Interaction & Paralogy** (STRING: *LRRC45*); **Co-expression** within the structural ciliary apparatus. |
| **MIR3154 / RNA5-8SN2** | Downregulated ($\text{log}_2\text{FC} = -5.101$, $-5.102$) | Non-coding microRNA and ribosomal RNA fragments showing maximum fold reductions. | **Putative Regulatory Interaction** (Post-transcriptional gene silencing / RNA processing cascade). |

---

### 4. Validation Priorities

#### Priority 1: Cell-Type Deconvolution and Synovial Composition Profiling
* **Classification:** **Confounding or composition check**
* **Why Prioritized:** 100% unidirectional transcript reduction across all 100 DEGs strongly indicates that cell composition differences (dilution of lining synoviocytes by invading immune cells) drive the observed bulk RNA-seq signature.
* **Input Dataset Evidence:** Unidirectional negative fold-changes across all features, including lineage-specific mucins (*MUC12*, *MUC5B*) and junctional markers (*CDHR5*, *GJC2*).
* **External Evidence:** Published single-cell RNA-seq studies of RA synovium demonstrate dramatic expansion of sublining macrophages and pathogenic fibroblasts, resulting in relative depletion of lining cell fraction in bulk samples.
* **Next Validation Step:** Perform computational deconvolution (e.g., CIBERSORTx, MuSiC) using single-cell RA reference panels, followed by multiplex immunofluorescence (CD68, PRG4, CDHR5) on intact synovial tissue sections.
* **Conclusion Status:** **Supported hypothesis**

#### Priority 2: Synovial Lining Junctional Integrity and Cell Polarity Disruption (SCRIB / ARVCF Axis)
* **Classification:** **Mechanistic hypothesis**
* **Why Prioritized:** Loss of tissue boundary integrity and hyper-permeability are core pathological features of RA synovia.
* **Input Dataset Evidence:** Marked suppression of cell polarity scaffold *SCRIB* ($\text{log}_2\text{FC} = -3.235$) and adherens junction anchor *ARVCF* ($\text{log}_2\text{FC} = -3.462$).
* **External Evidence:** SCRIB and ARVCF maintain cadherin stability and regulate Rho GTPase activity; loss of polarity complexes promotes invasive fibroblast phenotypes in inflammatory arthritis.
* **Next Validation Step:** Measure transepithelial/transendothelial electrical resistance (TEER) and examine cell polarity markers via confocal imaging in cultured primary human RA synovial fibroblasts before and after proinflammatory cytokine (TNF-$\alpha$, IL-1$\beta$) stimulation.
* **Conclusion Status:** **Exploratory hypothesis**

#### Priority 3: Wnt/$\beta$-Catenin Destruction Complex Modulation via APC2 Loss
* **Classification:** **Mechanistic hypothesis**
* **Why Prioritized:** Hyper-activation of Wnt/$\beta$-catenin signaling drives synovial fibroblast proliferation and pannus tissue formation in joint destruction.
* **Input Dataset Evidence:** *APC2* downregulation ($\text{log}_2\text{FC} = -3.018$, $\text{FDR} = 4.634 \times 10^{-39}$).
* **External Evidence:** APC2 participates in the $\beta$-catenin destruction complex; loss of APC family proteins stabilizes active $\beta$-catenin, enabling nuclear transcription of inflammatory genes.
* **Next Validation Step:** Quantification of active (non-phosphorylated) nuclear $\beta$-catenin levels via Western blot and TOPFlash luciferase reporter assays in primary synoviocytes upon *APC2* knockdown or restoration.
* **Conclusion Status:** **Exploratory hypothesis**

#### Priority 4: Non-Coding RNA Panel (MIR3154, MIR3183, CXXC5-AS1) as Synovial Fluid Biomarkers
* **Classification:** **Biomarker**
* **Why Prioritized:** Non-coding RNAs exhibit extreme fold reductions ($\text{log}_2\text{FC} < -3.9$) and are protected from enzymatic degradation inside extracellular vesicles.
* **Input Dataset Evidence:** *MIR3154* ($\text{log}_2\text{FC} = -5.101$) and *MIR3183* ($\text{log}_2\text{FC} = -4.614$) are among the top downregulated transcripts.
* **External Evidence:** MicroRNAs in synovial fluid and serum serve as non-invasive biomarkers of disease activity and therapeutic response in inflammatory arthritis.
* **Next Validation Step:** Quantitative RT-qPCR validation of extracellular vesicle-encapsulated *MIR3154* and *MIR3183* in independent synovial fluid and serum cohorts from early RA, established RA, and non-inflammatory controls.
* **Conclusion Status:** **Exploratory hypothesis**

#### Priority 5: ADAMTS7 Metalloproteinase Axis in Synovial Matrix Degradation
* **Classification:** **Therapeutic target**
* **Why Prioritized:** ADAMTS proteases participate in cartilage matrix degradation and joint destruction.
* **Input Dataset Evidence:** Significant downregulation of *ADAMTS7* ($\text{log}_2\text{FC} = -3.294$, $\text{FDR} = 2.386 \times 10^{-35}$).
* **External Evidence:** ADAMTS7 cleaves cartilage oligomeric matrix protein (COMP); however, drug targeting presence does not by itself establish clinical efficacy in RA.
* **Next Validation Step:** Evaluate ADAMTS7 enzymatic activity in cartilage co-culture assays and investigate joint degradation in collagen-induced arthritis (CIA) animal models under ADAMTS7 modulation.
* **Conclusion Status:** **Exploratory hypothesis**

---

### 5. Evidence Grounding

```
                     ┌──────────────────────────────────────────────────┐
                     │    Multi-Tiered Evidence Grounding Hierarchy     │
                     └────────────────────────┬─────────────────────────┘
                                              │
      ┌──────────────────────┬────────────────┴──────────────────────┬──────────────────────┐
      ▼                      ▼                                       ▼                      ▼
┌───────────┐          ┌───────────┐                           ┌───────────┐          ┌───────────┐
│ Direct    │          │ External  │                           │ Network & │          │ Disease & │
│ Dataset   │          │ Pathways  │                           │ PPI Record│          │ Tissue    │
├───────────┤          ├───────────┤                           ├───────────┤          ├───────────┤
│ Log2FC,   │          │ QuickGO,  │                           │ STRING    │          │ OpenTarg.,│
│ P-values, │          │ Reactome  │                           │ PPIs      │          │ GTEx, HPA │
│ FDRs      │          │ KEGG      │                           │           │          │           │
└─────┬─────┘          └─────┬─────┘                           └─────┬─────┘          └─────┬─────┘
      │                      │                                       │                      │
      └──────────────────────┴───────────────────┬───────────────────┴──────────────────────┘
                                                 ▼
                                ┌──────────────────────────────────┐
                                │ Primary Distinction:             │
                                │ External statistical validation  │
                                │ was NOT performed                │
                                └──────────────────────────────────┘
```

The evidence categories supporting this interpretation are classified as follows:

* **Direct Dataset Evidence:** The uploaded statistical table provides primary evidence ($\text{log}_2\text{FC}$, P-values, FDR). All 100 features show uniform downregulation ($\text{log}_2\text{FC}$ between $-2.279$ and $-5.102$, $\text{FDR} \le 1.56 \times 10^{-35}$).
* **Pathway & Gene Ontology Evidence:** Standardized QuickGO and Reactome annotations map *CDHR5*, *SCRIB*, and *ARVCF* to cell junctions/adhesion, *MUC5B/12/6* to mucin complexes, and *APC2/ARVCF* to Wnt signaling. *Note:* Pathway recurrence across databases represents shared underlying curation, not independent statistical replication.
* **Protein Interaction & Regulatory Network Evidence:** STRING database records provide evidence of physical interaction between ARVCF and CTNNB1 (confidence 0.804), SCRIB and ARHGEF7 (confidence 0.997), and CROCC and LRRC45 (confidence 0.820). Co-expression of mucins (*MUC5B*, *MUC12*, *MUC6*) is network co-membership rather than direct physical binding.
* **Disease & Tissue Evidence:** OpenTargets, GTEx, and HPA provide contextual tissue-expression records confirming that *MUC12*, *CDHR5*, and *GJC2* are expressed in barrier/lining tissues.
* **Independent External Validation:** **Not available.** External statistical validation was not performed on an independent patient cohort. Literature co-occurrence and database coverage must not be mistaken for statistical replication.

---

### 6. Limitations and Alternative Explanations

1. **Cell-Composition Dilution (Inflammatory Infiltration):** Bulk RNA-seq measures average transcript abundance across all cell types in the sample. In RA, massive synovial infiltration by T cells, B cells, and macrophages expands the total RNA pool, causing apparent transcriptional downregulation of resident lining synoviocyte genes (*MUC12*, *CDHR5*, *GJC2*) even if cellular transcription per lining cell remains unchanged.
2. **Technical Selection / Unidirectional Signal Bias:** 100% of the top 100 genes in this dataset are downregulated with extreme statistical significance ($\text{FDR}$ down to $10^{-53}$). This unidirectional distribution raises the possibility of platform normalization artifacts, asymmetrical p-value filtering, or batch-effect biases during input data extraction.
3. **Nonspecific Non-Coding RNA Annotation:** Non-coding RNAs (miRNAs, lncRNAs, snoRNAs, rRNA fragments) constitute a substantial portion of the downregulated list. Many of these non-coding elements lack verified targets or established functional roles in synovial pathophysiology, limiting mechanistic specificity.
4. **Unmeasured Clinical Covariates:** Critical clinical parameters—including disease stage (early vs. end-stage joint destruction), disease activity score (DAS28), synovial pathotype (fibroid, myeloid, or lymphoid), and exposure to disease-modifying antirheumatic drugs (DMARDs) or biologic anti-TNF agents—were not provided. Medication exposure can heavily suppress synovial tissue transcription.
5. **Association vs. Causation Ambiguity:** Differentially expressed genes identified in cross-sectional tissue analyses reflect disease state consequences or secondary inflammatory remodeling rather than causative disease drivers. Functional loss-of-function and gain-of-function perturbation experiments are required before assigning causal roles.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=0, external claims checked=0, external mismatches=0, status=passed.

Answer model API: Google Gemini / gemini-3.6-flash

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 84/100 selected items (records returned); cbioportal 82/100 selected items (records returned); chembl 16/100 selected items (records returned); civic 1/100 selected items (records returned); clinicaltrials 19/100 selected items (records returned); clinvar 79/100 selected items (records returned); ensembl 40/100 selected items (partially returned; some queries failed); europepmc 776 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 61/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 47/100 selected items (records returned); humanbase 88/100 selected items (partially returned; some queries failed); intact 47/100 selected items (records returned); mygene 93/100 selected items (records returned); omnipath 17/100 selected items (records returned); opentargets 82/100 selected items (records returned); pubmed 483 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 50/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 51/100 selected items (records returned)
Local databases: gutmgene 0/100 selected items (reachable but no records for this batch); hmdb 8/100 selected items (records returned); string 49/100 selected items (records returned); trrust 7/100 selected items (records returned)
