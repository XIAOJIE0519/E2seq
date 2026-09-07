# ulcerative colitis (UC) - gemini-3.6-flash

- Benchmark system: E2seq + Agent RAG
- Repeat: 4
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
- Model API: Google Gemini / gemini-3.6-flash
- Message SHA-256: 478acec7ab00f0e9bda085b6ecab7aa16a2bc8aa5cde3f2ba8fb71b2af94f79a
- Response HTTP status: 200
- Prompt tokens: 39728
- Completion tokens: 39631
- Reasoning tokens: 10150
- Total tokens: 79359
- API requests reported: 3
- Elapsed seconds: 52.524
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 1095.213
- Question handoff seconds: 1109.559
- Final benchmark system: E2seq; file rank 4/5; original repeat 4; model vendor: Google Gemini

---
### 1. Overall Biological Interpretation

The differential transcriptomic profile of colonic mucosal tissue in ulcerative colitis (UC) versus healthy controls reveals a dramatic, coordinated shift characterized by two dominant, opposing physiological events:

1. **Massive Activation of Inflammatory, Antimicrobial, and Remodeling Responses:** 
   Upregulated transcripts are heavily enriched for neutrophil-attracting ELR+ CXC chemokines (*CXCL1*, *CXCL2*, *CXCL3*), inflammatory alarmins/calprotectin subunits (*S100A8*, *S100P*), mucosal defense proteins (*LCN2*, *PI3*, *VNN1*), reactive oxygen species (ROS) generating complexes (*DUOX2*, *DUOXA2*), matrix-degrading enzymes (*MMP3*), matrix glycoproteins (*CHI3L1*, *TNC*, *PDPN*), and inducible nutrient transporters (*SLC6A14*). Concurrently, negative feedback counter-regulators (*SOCS3*, *IL1RN*, *IRAK3*) and T-cell checkpoint molecules (*CTLA4*) are upregulated, reflecting an intense cellular counter-regulatory attempt to curb tissue damage.

2. **Severe Collapse of Normal Colonic Epithelial Transport, Metabolism, and Barrier Functions:** 
   Downregulated genes reflect a widespread loss or metabolic shutdown of mature colonocytes. This includes profound suppression of transcellular fluid and water channels (*AQP8*, *AQP7*), solute and vitamin transporters (*SLC51A*, *SLC38A4*, *SLC23A1*, *SLC16A1*, *SLC23A3*, *ABCG2*, *ABCB11*), key mitochondrial ketogenic and metabolic enzymes (*HMGCS2*, *GBA3*, *G6PC*, *LIPC*, *HSD3B2*), phase I/II xenobiotic metabolizing enzymes (*CYP2B6*, *UGT2A3*), and mucosal surface brush-border peptidases (*MEP1B*, *DEFB1*).

*Note: External statistical validation was not performed on an independent replication cohort in this dataset.*

---

### 2. Core Biological Programs

```
                       ┌──────────────────────────────────────────────────────────┐
                       │        UC vs. Healthy Control Colonic Mucosa            │
                       └────────────────────────────┬─────────────────────────────┘
                                                    │
             ┌──────────────────────────────────────┴──────────────────────────────────────┐
             ▼                                                                             ▼
   UPREGULATED PROGRAMS                                                          DOWNREGULATED PROGRAMS
 ┌─────────────────────────────────────────┐                                   ┌─────────────────────────────────────────┐
 │ 1. Neutrophil Chemotaxis & Cytokines    │                                   │ 4. Epithelial Transport & Solute Loss   │
 │    (CXCL1/2/3, S100A8, SOCS3, IL1RN)    │                                   │    (AQP8, AQP7, SLC51A, SLC38A4, SLC16A1)  │
 │ 2. Epithelial ROS & Defense            │                                   │ 5. Mitochondrial & Xenobiotic Metabolism│
 │    (DUOX2, DUOXA2, LCN2, PI3, VNN1)     │                                   │    (HMGCS2, GBA3, MEP1B, CYP2B6, UGT2A3)│
 │ 3. ECM Remodeling & Tissue Repair       │                                   └─────────────────────────────────────────┘
 │    (MMP3, TIMP1, CHI3L1, TNC, PRRX1)    │
 └─────────────────────────────────────────┘
```

#### Program 1: Neutrophil Chemotaxis and Pro-inflammatory Cytokine Signaling
* **Direction:** Upregulated
* **Major Supporting Genes:** *CXCL1* (log2FC = 3.456, FDR = 1.15e-15), *CXCL2* (log2FC = 2.799, FDR = 1.73e-11), *CXCL3* (log2FC = 2.330, FDR = 2.51e-11), *S100A8* (log2FC = 3.799, FDR = 4.43e-11), *SOCS3* (log2FC = 2.786, FDR = 8.13e-12), *IL1RN* (log2FC = 2.876, FDR = 3.09e-18), *IRAK3* (log2FC = 1.782, FDR = 2.10e-11).
* **Standardized Pathway:** KEGG: IL-17 signaling pathway (hsa04657) / GO: Chemokine-mediated signaling pathway (GO:0070098).
* **Program Explanation:** The coordinated elevation of ELR+ CXC chemokines (*CXCL1*, *CXCL2*, *CXCL3*) and neutrophil alarmin *S100A8* indicates prominent recruitment and activation of neutrophils in the intestinal mucosa. Co-induction of *SOCS3*, *IL1RN*, and *IRAK3* indicates an active endogenous feedback mechanism attempting to restrain IL-1, TLR, and cytokine receptor signaling.
* **Evidence Strength & Limitations:** High statistical significance and clear functional coherence across multiple chemokine ligands. Limitation: In bulk tissue biopsies, this signal primarily reflects immune cell infiltration rather than pure epithelial transcriptomic reprogramming.

#### Program 2: Epithelial Reactive Oxygen Species (ROS) Generation and Mucosal Antimicrobial Defense
* **Direction:** Upregulated
* **Major Supporting Genes:** *DUOX2* (log2FC = 4.666, FDR = 4.45e-26), *DUOXA2* (log2FC = 2.892, FDR = 1.12e-10), *LCN2* (log2FC = 2.668, FDR = 1.37e-21), *PI3* (log2FC = 2.208, FDR = 3.97e-19), *VNN1* (log2FC = 3.199, FDR = 1.54e-15), *S100P* (log2FC = 1.775, FDR = 1.22e-21).
* **Standardized Pathway:** GO: Antimicrobial humoral response (GO:0140375) / Reactome: ROS and RNS production in phagocytes / mucosal surface defense.
* **Program Explanation:** Dual oxidase 2 (*DUOX2*) and its obligate maturation factor *DUOXA2* form an apical epithelial enzyme complex generating mucosal H2O2. Elevated *LCN2* (siderophore sequestration) and *PI3* (Elafin, antiprotease/antimicrobial) demonstrate an activated mucosal host-defense system responding to damaged epithelial barrier integrity and microbial contact.
* **Evidence Strength & Limitations:** Strong statistical magnitude (*DUOX2* log2FC = 4.666). Limitation: Sustained high ROS production can exacerbate collateral oxidative mucosal damage.

#### Program 3: Extracellular Matrix (ECM) Remodeling and Stromal Tissue Repair
* **Direction:** Upregulated
* **Major Supporting Genes:** *MMP3* (log2FC = 4.642, FDR = 5.40e-14), *TIMP1* (log2FC = 1.969, FDR = 1.81e-17), *CHI3L1* (log2FC = 4.590, FDR = 3.20e-11), *TNC* (log2FC = 2.579, FDR = 2.51e-11), *PDPN* (log2FC = 2.539, FDR = 1.75e-10), *PRRX1* (log2FC = 2.907, FDR = 4.35e-16), *CDH3* (log2FC = 2.293, FDR = 2.60e-11).
* **Standardized Pathway:** GO: Extracellular matrix organization (GO:0030198) / Reactome: Degradation of the extracellular matrix (R-HSA-1474228).
* **Program Explanation:** Upregulation of matrix metalloproteinase-3 (*MMP3*) alongside stromal activation markers (*PRRX1*, *PDPN*, *TNC*) and chitinase 3-like 1 (*CHI3L1*) reflects active mucosal ulceration, collagen turnover, and stromal fibroblast remodeling during active UC.
* **Evidence Strength & Limitations:** High fold-change magnitudes across multiple ECM component genes. Limitation: RNA expression levels do not measure extracellular protease cleavage activity directly.

#### Program 4: Colonic Epithelial Fluid, Electrolyte, and Solute Transport Loss
* **Direction:** Downregulated (with exception of *SLC6A14*)
* **Major Supporting Genes:** *AQP8* (log2FC = -4.417, FDR = 1.60e-13), *AQP7* (log2FC = -2.322, FDR = 4.04e-20), *SLC51A* (log2FC = -3.711, FDR = 1.54e-20), *SLC38A4* (log2FC = -3.067, FDR = 4.70e-37), *SLC23A1* (log2FC = -2.402, FDR = 8.89e-29), *SLC16A1* (log2FC = -2.375, FDR = 5.83e-21), *ABCG2* (log2FC = -2.919, FDR = 1.11e-10). (Upregulated transport exception: *SLC6A14*, log2FC = 4.849, FDR = 8.07e-39).
* **Standardized Pathway:** GO: Fluid Transport (GO:0042044) / GO: Water Transport (GO:0006833) / KEGG: Bile secretion (hsa04976).
* **Program Explanation:** Downregulation of apical aquaporins (*AQP8*, *AQP7*), solute carriers for bile acids (*SLC51A*), short-chain fatty acids (*SLC16A1* / MCT1), and vitamins (*SLC23A1*) captures the functional breakdown of absorptive colonocytes responsible for mucosal electrolyte/water homeostasis in UC diarrhea. Conversely, *SLC6A14* (a nutrient-inducible amino acid transporter) is strongly upregulated to supply amino acids to the inflamed tissue.
* **Evidence Strength & Limitations:** Extremely consistent downregulation across independent solute carrier families. Limitation: Partly driven by physical shedding or loss of mature surface epithelial cells.

#### Program 5: Mitochondrial/Metabolic Dysfunction and Xenobiotic Metabolism Suppression
* **Direction:** Downregulated
* **Major Supporting Genes:** *HMGCS2* (log2FC = -3.445, FDR = 1.10e-16), *GBA3* (log2FC = -3.002, FDR = 4.12e-17), *MEP1B* (log2FC = -2.991, FDR = 1.11e-22), *CYP2B6* (log2FC = -2.777, FDR = 4.18e-13), *HSD3B2* (log2FC = -2.769, FDR = 4.62e-16), *UGT2A3* (log2FC = -2.677, FDR = 7.16e-11), *DEFB1* (log2FC = -2.305, FDR = 1.25e-10).
* **Standardized Pathway:** KEGG: Drug metabolism - cytochrome P450 (hsa0980) / GO: Carboxylic acid metabolic process (GO:0019752).
* **Program Explanation:** Key metabolic hubs including ketogenic rate-limiting enzyme *HMGCS2*, phase I/II detoxifying enzymes (*CYP2B6*, *UGT2A3*), and brush-border proteolytic enzyme *MEP1B* are suppressed, indicating metabolic starvation and blunted physiological processing in damaged colonic epithelia.
* **Evidence Strength & Limitations:** High statistical significance across distinct metabolic pathways. Limitation: Bulk transcriptomics cannot distinguish cell-intrinsic metabolic inhibition from shift in tissue cell-type proportions.

---

### 3. Key Genes and Interaction Modules

| Candidate Gene / Module | Direction in Dataset | Role in Biological Programs | Specified Relationship Type |
| :--- | :--- | :--- | :--- |
| **DUOX2 & DUOXA2** | Both Upregulated (*DUOX2*: log2FC = 4.666; *DUOXA2*: log2FC = 2.892) | ROS generation & mucosal innate defense | **Direct physical interaction** (DUOXA2 is an obligate maturation factor that physically heterodimerizes with DUOX2 for membrane transport) and **Pathway co-membership**. |
| **MMP3 & TIMP1** | Both Upregulated (*MMP3*: log2FC = 4.642; *TIMP1*: log2FC = 1.969) | ECM turnover and protease inhibition balance | **Direct physical interaction** (TIMP1 protein physically binds and inhibits active MMP3 enzyme) and **Regulatory co-expression**. |
| **CXCL1, CXCL2, & CXCL3** | All Upregulated (*CXCL1*: 3.456; *CXCL2*: 2.799; *CXCL3*: 2.330) | Neutrophil chemoattraction | **Pathway co-membership** (IL-17/chemokine signaling) and shared **Receptor interaction** (all bind CXCR2; no direct physical binding to each other). |
| **SLC6A14** | Upregulated (log2FC = 4.849, FDR = 8.07e-39) | Inducible amino acid transport in inflamed mucosa | **Pathway co-membership** and **Co-expression** with mucosal metabolic stress responses. |
| **AQP8 & AQP7** | Both Downregulated (*AQP8*: -4.417; *AQP7*: -2.322) | Mucosal fluid absorption and water transport | **Pathway co-membership** (passive aquaporin transport) and **Co-expression** in mature colonocytes. |
| **HMGCS2** | Downregulated (log2FC = -3.445, FDR = 1.10e-16) | Epithelial ketogenesis and butyrate utilization | **Regulatory interaction** (repressed by inflammatory cytokines like TNF/IFN-γ) and **Pathway co-membership**. |
| **CHI3L1** | Upregulated (log2FC = 4.590, FDR = 3.20e-11) | Tissue remodeling and cell adhesion modulation | **Indirect / putative relationship** with extracellular matrix structural components. |
| **LCN2 & S100A8** | Both Upregulated (*LCN2*: 2.668; *S100A8*: 3.798) | Neutrophil-mediated antimicrobial protection | **Co-expression** (co-secreted during neutrophil infiltration) and **Pathway co-membership** (no direct complex reported). |
| **MEP1B** | Downregulated (log2FC = -2.991, FDR = 1.11e-22) | Brush-border peptide processing & mucus barrier | **Pathway co-membership** in mucosal surface proteolysis. |
| **CTLA4** | Upregulated (log2FC = 2.616, FDR = 1.11e-10) | T-cell checkpoint regulation in lamina propria | **Regulatory interaction** and **Co-expression** with immune cell infiltrate markers. |

---

### 4. Validation Priorities

```
                                  VALIDATION PRIORITIES
                                            │
   ┌───────────────────┬────────────────────┼────────────────────┬───────────────────┐
   ▼                   ▼                    ▼                    ▼                   ▼
1. DUOX2/DUOXA2     2. HMGCS2            3. SLC6A14           4. AQP8 / AQP7      5. Deconvolution
[Mechanistic]       [Mechanistic]        [Therapeutic Target] [Biomarker]         [Composition Check]
   │                   │                    │                    │                   │
   ▼                   ▼                    ▼                    ▼                   ▼
Single-cell /       Biopsy & Stool       Small-molecule       Ussing chamber      Digital CIBERSORTx
Organoid ROS        Metabolomics         Blockade In Vitro    Transepithelial     & Single-Cell
Assays              (SCFA / Ketones)     (Organoid Cultures)  Flux Assays         RNA-seq
```

#### 1. DUOX2 / DUOXA2 Maturation Complex Activation
* **Classification:** Mechanistic hypothesis
* **Why Prioritized:** Strongest co-upregulated epithelial oxidase enzyme-maturation factor pair (*DUOX2* log2FC = 4.666, *DUOXA2* log2FC = 2.892).
* **Current Dataset Evidence:** Synchronous marked elevation of catalyst and maturation obligate subunit.
* **External Evidence:** Literature (PMID: 41029776) and Reactome pathway records link *DUOX2/DUOXA2* to mucosal antimicrobial ROS release in active intestinal inflammation.
* **Appropriate Next Step:** Single-cell RNA-seq combined with spatial immunofluorescence on UC mucosal biopsies and intestinal organoid ROS fluorometric assays under IL-17/TNF stimulation.
* **Conclusion Status:** Supported hypothesis

#### 2. Loss of HMGCS2-Driven Epithelial Ketogenesis
* **Classification:** Mechanistic hypothesis
* **Why Prioritized:** Severe downregulation of *HMGCS2* (log2FC = -3.445, FDR = 1.10e-16) highlights mucosal metabolic failure.
* **Current Dataset Evidence:** Concurrent suppression of *HMGCS2* and short-chain fatty acid transporter *SLC16A1* (log2FC = -2.375).
* **External Evidence:** KEGG pathway annotations and metabolic literature demonstrate colonocyte reliance on butyrate oxidation and ketogenesis for mucosal integrity.
* **Appropriate Next Step:** Mass-spectrometry metabolomic quantification of mucosal acetoacetate and β-hydroxybutyrate levels in patient biopsy tissue.
* **Conclusion Status:** Supported hypothesis

#### 3. SLC6A14 Transporter as an Inflammatory Mucosal Target
* **Classification:** Therapeutic target / Biomarker
* **Why Prioritized:** *SLC6A14* exhibits the highest statistical significance and upregulation magnitude in the entire dataset (log2FC = 4.849, FDR = 8.07e-39, P = 1.48e-43).
* **Current Dataset Evidence:** Extreme upward fold-change.
* **External Evidence:** Functional studies document *SLC6A14* induction by pro-inflammatory cytokines (TNF, IL-1β) to sustain cellular amino acid transport during inflammation.
* **Appropriate Next Step:** Pharmacological inhibition using α-methyl-L-tryptophan (α-MT) in intestinal organoid-immune cell co-cultures. *Note: Drug targeting record presence alone does not establish clinical therapeutic efficacy.*
* **Conclusion Status:** Exploratory hypothesis

#### 4. Aquaporin (AQP8/AQP7) Downregulation as a Driver of Malabsorptive Diarrhea
* **Classification:** Biomarker / Mechanistic hypothesis
* **Why Prioritized:** *AQP8* is the most downregulated gene in the dataset (log2FC = -4.417, FDR = 1.60e-13).
* **Current Dataset Evidence:** Concurrent collapse of *AQP8* (-4.417) and *AQP7* (-2.322).
* **External Evidence:** QuickGO and Reactome annotations confirm role in passive epithelial water transport.
* **Appropriate Next Step:** Ussing chamber transepithelial fluid flux assays on freshly isolated endoscopic mucosal biopsies from UC patients versus controls.
* **Conclusion Status:** Supported hypothesis

#### 5. Deconvolution of Cell-Type Compositional Confounding
* **Classification:** Confounding or composition check
* **Why Prioritized:** Bulk tissue transcriptomics convolves immune cell infiltration with epithelial gene expression changes.
* **Current Dataset Evidence:** Reciprocal upregulation of neutrophil markers (*S100A8*, *CXCL1*) and downregulation of mature colonocyte genes (*AQP8*, *MEP1B*).
* **External Evidence:** Single-cell transcriptomic studies demonstrate that bulk differential expression in IBD is strongly influenced by shifts in cell type proportions.
* **Appropriate Next Step:** Digital cell-type deconvolution (e.g., CIBERSORTx) using single-cell reference panels of human colon mucosa.
* **Conclusion Status:** Established evidence (that cell-composition shifts confound bulk mucosal RNA profiling)

---

### 5. Evidence Grounding

```
                            EVIDENCE HIERARCHY & GROUNDING
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 1. DIRECT INPUT DATASET STATISTICS                                                  │
│    Primary fold-changes & FDR (SLC6A14 +4.85, DUOX2 +4.67, MMP3 +4.64, AQP8 -4.42) │
└──────────────────────────┬──────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────────────────────┐
│ 2. PATHWAY & ONTOLOGY ANNOTATIONS (GO / KEGG / Reactome)                            │
│    Contextualizes functional groupings (IL-17 signaling, Water/Fluid transport)     │
└──────────────────────────┬──────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────────────────────┐
│ 3. NETWORK & INTERACTION RECORDS (STRING / OmniPath / IntAct)                       │
│    Establishes interaction types (DUOX2-DUOXA2 direct physical, CXCLs shared receptor) │
└──────────────────────────┬──────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────────────────────┐
│ 4. LITERATURE & DISEASE ANNOTATIONS (PubMed / Europe PMC / OpenTargets)             │
│    Plausibility & clinical associations (PMID: 41029776, PMID: 25171508)            │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

* **Direct Evidence from Input Dataset:** 
  Authoritative differential statistics confirm profound alterations: *SLC6A14* (+4.849), *DUOX2* (+4.666), *MMP3* (+4.642), *CHI3L1* (+4.590), *S100A8* (+3.799), *CXCL1* (+3.456) vs. *AQP8* (-4.417), *SLC51A* (-3.711), *HMGCS2* (-3.445), *SLC38A4* (-3.067), *MEP1B* (-2.991).
* **Pathway / Ontology Evidence:** 
  Standardized annotations (GO:0042044 Fluid Transport, GO:0070098 Chemokine-mediated signaling, KEGG hsa04657 IL-17 signaling, Reactome R-HSA-1474228 ECM degradation) contextualize functional programs. *Pathway recurrence contextualizes biological mechanisms but does not constitute statistical replication.*
* **Protein Interaction / Regulatory Evidence:** 
  STRING and Reactome interaction records support direct physical heterodimerization for *DUOX2*–*DUOXA2* and complex formation for *MMP3*–*TIMP1*. Chemokines (*CXCL1/2/3*) share receptor binding (*CXCR2*), representing pathway co-membership rather than direct physical chemokine-chemokine binding.
* **Disease / Literature Evidence:** 
  External literature (PMID: 41029776, PMID: 25171508) and OpenTargets records establish disease association for *BRINP3*, *DUOX2*, *LCN2*, and *S100A8* in IBD.
* **Independence Analysis & Conflicts:** 
  Pathway and literature records share underlying primary publications and are not fully independent evidence sources. No directional conflicts were found among concordant functional modules.
* **External Statistical Validation Statement:** 
  **External statistical validation was not performed on an independent cohort in this analysis.**

---

### 6. Limitations and Alternative Explanations

1. **Tissue Cell-Composition Confounding:** 
   Bulk mucosal tissue contains epithelial, stromal, and infiltrating immune cells. The suppression of colonocyte genes (*AQP8*, *HMGCS2*, *MEP1B*) and elevation of immune markers (*S100A8*, *CXCL1*) partly reflect mucosal ulceration and immune cell influx rather than pure intracellular transcriptional activation or repression.
2. **Absence of External Cohort Replication:** 
   External statistical validation was not performed on an independent cohort; conclusions remain based solely on the input dataset ledger and database context.
3. **Unmeasured Treatment Exposure and Disease Severity:** 
   The dataset lacks metadata regarding patient medication (5-ASAs, corticosteroids, biologics) or endoscopic disease severity. Upregulated anti-inflammatory regulators (*SOCS3*, *IL1RN*, *IRAK3*) might reflect treatment exposure or variable flare states.
4. **RNA Abundance vs. Enzymatic Activity Ambiguity:** 
   Transcriptional changes in matrix enzymes (*MMP3*), oxidases (*DUOX2*), or metabolic enzymes (*HMGCS2*) do not directly indicate functional enzymatic activity without protein and post-translational assay verification.
5. **Association vs. Causation Ambiguity:** 
   Observed transcriptomic changes represent concurrent pathological states of established UC mucosal inflammation rather than confirmed primary disease-causing drivers.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=95, external claims checked=0, external mismatches=0, status=passed.

Answer model API: Google Gemini / gemini-3.6-flash

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 94/100 selected items (records returned); cbioportal 87/100 selected items (records returned); chembl 40/100 selected items (partially returned; some queries failed); civic 7/100 selected items (records returned); clinicaltrials 51/100 selected items (records returned); clinvar 90/100 selected items (records returned); ensembl 55/100 selected items (partially returned; some queries failed); europepmc 936 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 91/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 85/100 selected items (records returned); humanbase 87/100 selected items (records returned); intact 85/100 selected items (records returned); mygene 93/100 selected items (records returned); omnipath 45/100 selected items (records returned); opentargets 92/100 selected items (records returned); pubmed 750 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 87/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 88/100 selected items (records returned)
Local databases: gutmgene 8/100 selected items (records returned); hmdb 46/100 selected items (records returned); string 85/100 selected items (records returned); trrust 31/100 selected items (records returned)
