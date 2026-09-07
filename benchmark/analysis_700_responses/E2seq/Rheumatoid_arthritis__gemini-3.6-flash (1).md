# rheumatoid arthritis - gemini-3.6-flash

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
- Model API: Google Gemini / gemini-3.6-flash
- Message SHA-256: d868ce3efb219458b8d5ddb7b123eef3f2b718852ba0ede74f2a02e9181db293
- Response HTTP status: 200
- Prompt tokens: 20234
- Completion tokens: 13051
- Reasoning tokens: 7117
- Total tokens: 33285
- API requests reported: 1
- Elapsed seconds: 52.145
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 984.622
- Question handoff seconds: 999.892
- Final benchmark system: E2seq; file rank 1/5; original repeat 1; model vendor: Google Gemini

---
Based on the transcriptomic comparison between rheumatoid arthritis (RA) synovial tissue and normal control samples, the provided statistical dataset contains 100 significantly downregulated genes (all $\text{log}_2\text{FC} < 0$, $\text{FDR} < 10^{-34}$) with no upregulated genes represented in this selected subset. 

External statistical validation was not performed on an independent cohort in the supplied input; therefore, all biological insights are derived from direct statistical evidence within this dataset combined with contextual database annotations (Reactome, GO, STRING, ChEMBL, PubMed).

---

### 1. Overall Biological Interpretation

The overall transcriptomic signal in RA synovial tissue compared to healthy controls is characterized by a widespread, high-magnitude suppression of genes responsible for homeostatic synovial architecture, cellular adhesion/polarity, surface mucin barriers, centrosomal/ciliary integrity, and non-coding RNA post-transcriptional processing.

In healthy synovium, the lining layer forms a protective, organized barrier composed of specialized synoviocyte subtypes maintained by strict apicobasal polarity (*SCRIB*, *CDHR5*), adherens/gap junctions (*ARVCF*, *APC2*, *GJC2*), and lubricating mucin secretions (*MUC12*, *MUC5B*, *MUC6*). The profound downregulation of these molecular frameworks in RA synovium reflects severe structural erosion and loss of homeostatic lining organization. Simultaneously, coordinated suppression of centrosomal/ciliary rootlet components (*CROCC*, *CROCC2*) and apoptotic stress-response nodes (*PIDD1*, *NOL3*) highlights widespread dysregulation of cellular structural tethers and apoptotic control mechanisms. Rather than representing a unilineage metabolic block, this uniform down-regulation across 100 top DEGs strongly points to structural remodeling of the synovial environment, potentially driven by cellular composition shifts (e.g., inflammatory cell infiltration diluting lining synoviocyte transcripts) or active transcriptional silencing.

---

### 2. Core Biological Programs

```
                       +-------------------------------------------------------+
                       | Downregulated Synovial Transcriptomic Architecture    |
                       +-------------------------------------------------------+
                                                   |
         +-------------------+---------------------+-------------------+-------------------+
         |                   |                     |                   |                   |
         v                   v                     v                   v                   v
+------------------+ +------------------+ +------------------+ +------------------+ +------------------+
| Program 1:       | | Program 2:       | | Program 3:       | | Program 4:       | | Program 5:       |
| Cell Adhesion &  | | Centrosomal &    | | Mucin Barrier &  | | Apoptotic        | | Non-Coding RNA  |
| Synovial Junction| | Ciliary Rootlet  | | Glycoprotein     | | Priming & Stress | | & Ribosomal     |
| (SCRIB, ARVCF,   | | (CROCC, CROCC2,  | | Secretion        | | (PIDD1, NOL3,    | | Regulation       |
| APC2, CDHR5)     | | CCDC9, ARHGAP33) | | (MUC5B, MUC12)   | | DMPK, D2HGDH)   | | (MIRs, RNA5-8S) |
+------------------+ +------------------+ +------------------+ +------------------+ +------------------+
```

#### Program 1: Synovial Cell Adhesion and Junctional Architecture
* **Direction**: Downregulated in RA
* **Major Supporting Genes**: *SCRIB* ($\text{log}_2\text{FC} = -3.24$, $\text{FDR} = 1.32 \times 10^{-42}$), *CDHR5* ($\text{log}_2\text{FC} = -4.22$, $\text{FDR} = 1.61 \times 10^{-45}$), *ARVCF* ($\text{log}_2\text{FC} = -3.46$, $\text{FDR} = 1.01 \times 10^{-38}$), *APC2* ($\text{log}_2\text{FC} = -3.02$, $\text{FDR} = 4.63 \times 10^{-39}$), *GJC2* ($\text{log}_2\text{FC} = -3.50$, $\text{FDR} = 5.11 \times 10^{-40}$)
* **Standardized Pathway**: GO:0005911 (Cell-cell junction) / Reactome R-HSA-446717 (Cell-junction organization)
* **Biological Rationale**: Apicobasal polarity (*SCRIB*), cadherin-mediated adhesion (*CDHR5*), catenin-interacting armadillo protein complexes (*ARVCF*, *APC2*), and gap junctions (*GJC2*) cooperatively maintain intercellular cohesion in the synovial lining. Their multi-gene suppression indicates a breakdown of junctional architecture.
* **Evidence Strength & Major Limitations**: High direct statistical significance in input data. Supported by QuickGO/STRING junctional annotations. *Limitation*: Bulk transcriptomic tissue profiling cannot rule out whether downregulation is per-cell or due to cellular dilution by infiltrating immune cells.

#### Program 2: Centrosomal and Ciliary Structural Integrity
* **Direction**: Downregulated in RA
* **Major Supporting Genes**: *CROCC* ($\text{log}_2\text{FC} = -3.88$, $\text{FDR} = 9.67 \times 10^{-48}$), *CROCC2* ($\text{log}_2\text{FC} = -4.99$, $\text{FDR} = 1.22 \times 10^{-40}$), *CROCCP2* ($\text{log}_2\text{FC} = -2.89$, $\text{FDR} = 2.90 \times 10^{-38}$), *ARHGAP33* ($\text{log}_2\text{FC} = -3.20$, $\text{FDR} = 1.67 \times 10^{-36}$), *CCDC9* ($\text{log}_2\text{FC} = -3.02$, $\text{FDR} = 1.93 \times 10^{-44}$)
* **Standardized Pathway**: GO:0005813 (Centrosome) / Reactome R-HSA-5620924 (Cilium assembly)
* **Biological Rationale**: *CROCC* (rootletin) and *CROCC2* anchor ciliary basal bodies and stabilize centrosomal architecture. Simultaneous downregulation of these coiled-coil proteins suggests primary cilia loss or centrosomal destabilization in rheumatoid synovial tissue.
* **Evidence Strength & Major Limitations**: Strong signal across paralogs and structural coiled-coil transcripts. *Limitation*: Primary cilia function in synovial sub-populations remains poorly defined without high-resolution imaging or single-cell datasets.

#### Program 3: Mucin Secretory and Surface Protection
* **Direction**: Downregulated in RA
* **Major Supporting Genes**: *MUC12* ($\text{log}_2\text{FC} = -4.27$, $\text{FDR} = 6.05 \times 10^{-43}$), *MUC5B* ($\text{log}_2\text{FC} = -4.43$, $\text{FDR} = 2.07 \times 10^{-40}$), *MUC6* ($\text{log}_2\text{FC} = -3.85$, $\text{FDR} = 5.92 \times 10^{-36}$)
* **Standardized Pathway**: Reactome R-HSA-5205547 (O-linked glycosylation of mucins) / KEGG hsa04974
* **Biological Rationale**: Transmembrane (*MUC12*) and gel-forming (*MUC5B*, *MUC6*) mucins coat synovial surfaces to protect against mechanical shear and enzymatic degradation. Their parallel loss indicates impairment of mucosal-like surface shielding in inflamed joints.
* **Evidence Strength & Major Limitations**: High-magnitude effects across multiple independent mucin loci. *Limitation*: Mucins are primarily synthesized by secretory lining synoviocytes; lining hyperplasia with loss of secretory differentiation could explain reduced expression.

#### Program 4: Apoptotic Priming and Stress-Response Machinery
* **Direction**: Downregulated in RA
* **Major Supporting Genes**: *PIDD1* ($\text{log}_2\text{FC} = -2.89$, $\text{FDR} = 4.30 \times 10^{-35}$), *NOL3* ($\text{log}_2\text{FC} = -2.45$, $\text{FDR} = 3.58 \times 10^{-36}$), *DMPK* ($\text{log}_2\text{FC} = -2.97$, $\text{FDR} = 1.87 \times 10^{-36}$), *D2HGDH* ($\text{log}_2\text{FC} = -2.76$, $\text{FDR} = 1.74 \times 10^{-38}$)
* **Standardized Pathway**: KEGG hsa04210 (Apoptosis) / GO:0043065 (Regulation of apoptotic process)
* **Biological Rationale**: *PIDD1* (a pro-apoptotic component of the PIDDosome) and *NOL3* (ARC, an anti-apoptotic CARD-domain protein) both exhibit downregulation. Disruption of these counter-balancing death/survival factors points to altered apoptotic thresholds in rheumatoid synovium.
* **Evidence Strength & Major Limitations**: STRING network links both NOL3 and PIDD1 to Caspase-2 (CASP2). *Limitation*: Simultaneous downregulation of pro- and anti-apoptotic genes reflects complex network remodeling rather than a unidirectional pro-survival or pro-apoptotic shift.

#### Program 5: Non-Coding RNA and Post-Transcriptional Regulation
* **Direction**: Downregulated in RA
* **Major Supporting Genes**: *RNA5-8SN2* ($\text{log}_2\text{FC} = -5.10$, $\text{FDR} = 3.41 \times 10^{-40}$), *RNA5-8SN3* ($\text{log}_2\text{FC} = -4.57$, $\text{FDR} = 1.08 \times 10^{-35}$), *MIR3154* ($\text{log}_2\text{FC} = -5.10$, $\text{FDR} = 5.97 \times 10^{-43}$), *MIR3183* ($\text{log}_2\text{FC} = -4.61$, $\text{FDR} = 5.46 \times 10^{-47}$), *CXXC5-AS1* ($\text{log}_2\text{FC} = -3.93$, $\text{FDR} = 1.44 \times 10^{-41}$)
* **Standardized Pathway**: KEGG: Ribosome biogenesis in eukaryotes / GO:0034660 (ncRNA metabolic process)
* **Biological Rationale**: Downregulation of ribosomal RNA units (*RNA5-8S* variants), microRNAs (*MIR3154*, *MIR3183*), and antisense lncRNAs (*CXXC5-AS1*, *DM1-AS*, *TBX2-AS1*) indicates broad post-transcriptional RNA network attenuation in diseased synovial tissue.
* **Evidence Strength & Major Limitations**: Represents the largest magnitude fold-changes in the dataset. *Limitation*: Many non-coding transcripts have sparse functional annotations, making precise target predictions exploratory.

---

### 3. Key Genes and Interaction Modules

| Candidate / Module | Dataset Direction & Statistics | Potential Role in Core Programs | Nature of Gene-Gene Relationship |
| :--- | :--- | :--- | :--- |
| **SCRIB** | Downregulated ($\text{log}_2\text{FC} = -3.24$, $\text{FDR} = 1.32 \times 10^{-42}$) | Program 1 (Cell polarity & junctions) | **Direct physical interaction** with ARHGEF7/VANGL2 (STRING); **Pathway co-membership** with APC2 and ARVCF. |
| **APC2** | Downregulated ($\text{log}_2\text{FC} = -3.02$, $\text{FDR} = 4.63 \times 10^{-39}$) | Program 1 (Wnt signaling / cell adhesion) | **Direct physical interaction** with CTNNB1 (STRING confidence 0.804); **Pathway co-membership** with ARVCF. |
| **ARVCF** | Downregulated ($\text{log}_2\text{FC} = -3.46$, $\text{FDR} = 1.01 \times 10^{-38}$) | Program 1 (Adherens junction armadillo protein) | **Direct physical interaction** with CTNNB1 (STRING confidence 0.804) and COMT (0.897); **Co-expression** with APC2. |
| **MUC5B – MUC6 – MUC12 Module** | Downregulated (MUC5B: $-4.43$, MUC6: $-3.85$, MUC12: $-4.27$) | Program 3 (Mucin surface barrier) | **Pathway co-membership** (Reactome mucin glycosylation); **Co-expression**; **Indirect network relationship** with MUC1/MUC2 (STRING). |
| **CROCC – CROCC2 Module** | Downregulated (CROCC: $-3.88$, CROCC2: $-4.99$) | Program 2 (Centrosome / ciliary rootlet) | **Pathway co-membership** (Cilium assembly); **Sequence homology / paralog co-expression** (STRING LRRC45 link). |
| **PIDD1** | Downregulated ($\text{log}_2\text{FC} = -2.89$, $\text{FDR} = 4.30 \times 10^{-35}$) | Program 4 (Apoptosis regulation) | **Direct physical interaction / Regulatory interaction** with CASP2 (STRING network); **Pathway co-membership** with NOL3. |
| **NOL3** | Downregulated ($\text{log}_2\text{FC} = -2.45$, $\text{FDR} = 3.58 \times 10^{-36}$) | Program 4 (Apoptosis suppression) | **Direct physical interaction** with CASP2 (STRING network); **Regulatory co-membership** in apoptotic cascades. |
| **ADAMTS7** | Downregulated ($\text{log}_2\text{FC} = -3.29$, $\text{FDR} = 2.39 \times 10^{-35}$) | ECM metalloproteinase processing | **Pathway co-membership** (Metabolite & ECM organization); **Indirect regulatory relationship** with joint matrix remodelling. |
| **RNA5-8SN2 – RNA5-8SN3 Module** | Downregulated (8SN2: $-5.10$, 8SN3: $-4.57$) | Program 5 (Ribosomal RNA biogenesis) | **Pathway co-membership** (KEGG Ribosome biogenesis); **Co-expression** across ribosomal RNA clusters. |
| **DRD4** | Downregulated ($\text{log}_2\text{FC} = -4.24$, $\text{FDR} = 3.72 \times 10^{-42}$) | Synovial neuro-endocrine signaling | **Indirect relationship** via COMT network node (STRING), connecting dopaminergic pathways to cell adhesion locus ARVCF. |

---

### 4. Validation Priorities

#### 1. Cell-Composition Deconvolution and Tissue Specificity Check
* **Classification**: Confounding or composition check
* **Prioritization Rationale**: All 100 DEGs in this dataset are downregulated. RA tissue is heavily infiltrated by leukocytes, which dilutes stromal and lining synoviocyte transcripts. Distinguishing true transcriptional repression from cell composition shifts is critical.
* **Dataset Evidence**: Uniform negative $\text{log}_2\text{FC}$ across all top genes ($\text{log}_2\text{FC} < -2.2, \text{FDR} < 10^{-34}$).
* **External Evidence**: Single-cell RNA-seq studies (e.g., Accelerating Medicines Partnership RA datasets) reveal substantial expansion of sublining macrophages and T cells alongside lining FLS subset alterations.
* **Next Validation Step**: Perform digital cell-type deconvolution (e.g., CIBERSORTx) using single-cell FLS reference panels, followed by multiplex RNA-FISH or IHC on intact RA vs normal synovial tissue sections.
* **Status**: Supported hypothesis

#### 2. Functional Roles of SCRIB and ARVCF in Synovial Lining Barrier Breakdown
* **Classification**: Mechanistic hypothesis
* **Prioritization Rationale**: Cell polarity and adherens junction loss (*SCRIB*, *ARVCF*, *APC2*) may facilitate invasive fibroblast behavior and pannus expansion into cartilage.
* **Dataset Evidence**: High-magnitude loss of *SCRIB* ($\text{log}_2\text{FC} = -3.24$) and *ARVCF* ($\text{log}_2\text{FC} = -3.46$).
* **External Evidence**: Dysregulated Wnt/$\beta$-catenin and cell polarity pathways are documented in RA fibroblast-like synoviocyte (FLS) migration models.
* **Next Validation Step**: shRNA knockdown or CRISPR activation of *SCRIB* and *ARVCF* in primary human FLS, evaluating 3D synoviocyte organoid barrier permeability and Matrigel invasion assays.
* **Status**: Supported hypothesis

#### 3. Synovial Mucin Loss as a Biomarker for Joint Barrier Integrity
* **Classification**: Biomarker
* **Prioritization Rationale**: *MUC5B*, *MUC6*, and *MUC12* exhibit profound, coordinated loss ($\text{log}_2\text{FC} -3.85$ to $-4.43$). Synovial fluid mucin concentration could reflect lining barrier state.
* **Dataset Evidence**: Uniform, low-FDR reduction of transmembrane and gel-forming mucin family members.
* **External Evidence**: MUC5B variants are linked to RA-associated interstitial lung disease, but joint synovial fluid levels remain uncharacterized as diagnostic markers.
* **Next Validation Step**: Targeted mass spectrometry or ELISA quantification of MUC5B and MUC12 protein in synovial fluid from patients with early RA, established RA, osteoarthritis, and healthy controls.
* **Status**: Exploratory hypothesis

#### 4. Apoptotic Priming via PIDD1 and NOL3 Modulation
* **Classification**: Interaction / network hypothesis
* **Prioritization Rationale**: Simultaneous loss of pro-apoptotic *PIDD1* and anti-apoptotic *NOL3* indicates a reshuffled apoptotic checkpoint, relevant to FLS apoptosis resistance.
* **Dataset Evidence**: Suppression of *PIDD1* ($\text{log}_2\text{FC} = -2.89$) and *NOL3* ($\text{log}_2\text{FC} = -2.45$), both connected to Caspase-2 in STRING networks.
* **External Evidence**: RA FLS display resistance to cytokine-induced apoptosis; PIDDosome-mediated Caspase-2 activation regulates p53-dependent death under stress.
* **Next Validation Step**: Co-immunoprecipitation and immunoblots for PIDD1, NOL3, and Caspase-2 in FLS subjected to TNF-$\alpha$ or IL-1$\beta$ stimulation.
* **Status**: Exploratory hypothesis

#### 5. Evaluation of ADAMTS7 In Synovial Extracellular Matrix Remodeling
* **Classification**: Therapeutic target
* **Prioritization Rationale**: *ADAMTS7* encodes a secreted metalloproteinase that degrades cartilage matrix proteins. While downregulated in bulk tissue ($\text{log}_2\text{FC} = -3.29$), its exact enzymatic role requires target validation before therapeutic consideration. (Note: Small molecule inhibitors exist in ChEMBL, but drug existence alone does not confirm therapeutic efficacy in RA).
* **Dataset Evidence**: Significant loss of *ADAMTS7* expression in bulk RA tissue ($\text{FDR} = 2.39 \times 10^{-35}$).
* **External Evidence**: ChEMBL records document ADAMTS family inhibitors in joint disease models, but studies focus primarily on cartilage in osteoarthritis.
* **Next Validation Step**: Recombinant ADAMTS7 cleavage assays against cartilage oligomeric matrix protein (COMP) in synoviocyte-chondrocyte co-culture models.
* **Status**: Exploratory hypothesis

---

### 5. Evidence Grounding

```
+-----------------------------------------------------------------------------------+
|                               EVIDENCE CATEGORIES                                 |
+-----------------------------------------------------------------------------------+
| 1. Direct Input Statistics : log2FC (-2.28 to -5.10), FDR (< 1e-34)               |
| 2. Pathway / Ontology      : Reactome (Mucin, Junctions), KEGG (Ribosomes), GO    |
| 3. Protein / Regulatory    : STRING physical nodes (ARVCF-CTNNB1, SCRIB-ARHGEF7) |
| 4. Tissue & Expression     : GTEx / HPA synoviocyte & mucosal tissue expression    |
| 5. Drug & Therapeutic      : ChEMBL records (ADAMTS7, DRD4) -- target unvalidated  |
| 6. Literature Records      : Europe PMC / PubMed (ncRNA & joint degeneration)     |
+-----------------------------------------------------------------------------------+
```

* **Direct Input Evidence**: The primary statistical foundation rests on the user-supplied transcriptomic results showing 100 downregulated genes ($\text{log}_2\text{FC}$ between $-2.28$ and $-5.10$, all $\text{FDR} < 10^{-34}$).
* **Pathway / Ontology Evidence**: Standardized annotations (GO:0005911, Reactome R-HSA-446717, Reactome R-HSA-5205547, KEGG Ribosome Biogenesis) link individual genes (*SCRIB*, *APC2*, *ARVCF*, *MUC5B*, *RNA5-8SN2*) to cell-cell junctions, mucin glycosylation, and ribosomal processes.
* **Protein Interaction / Regulatory Evidence**: STRING records provide physical interaction evidence for ARVCF–CTNNB1, SCRIB–ARHGEF7, PIDD1–CASP2, and NOL3–CASP2, as well as sequence homology/paralog links for CROCC–CROCC2 and MUC12–MUC5B–MUC6.
* **Disease / Genetic / Clinical Evidence**: OpenTargets and GWAS records document association with autoimmune/rheumatoid traits across cohort entities; however, *external statistical validation was not performed* on an independent cohort in this analysis.
* **Tissue / Expression Evidence**: GTEx and HPA datasets confirm baseline expression of *SCRIB*, *APC2*, *ADAMTS7*, and *MUC5B* in synovial, connective, and epithelial tissues.
* **Drug / Therapeutic Evidence**: ChEMBL and ClinicalTrials databases record small molecule interactions for *ADAMTS7* and *DRD4*. *Crucial distinction*: The existence of chemical probes does not establish these genes as effective therapeutic targets for RA.
* **Source Overlap & Conflicts**: Annotations from Reactome, QuickGO, STRING, and OpenTargets depend on overlapping primary literature records and predictive curation models. Direct statistical evidence is concordant across the 100 genes (all downregulated), but independent replication statistics are currently absent.

---

### 6. Limitations and Alternative Explanations

1. **Cell-Composition Confounding (Dilution Effect)**: 
   RA synovium undergoes extensive leukocyte infiltration (macrophages, lymphocytes, plasma cells) alongside lining hyperplasia. The uniform downregulation of lining-specific structural transcripts (*SCRIB*, *MUC5B*, *CROCC*) may reflect proportional dilution by invading immune cells rather than active per-cell transcriptional repression.
   * *Resolution Strategy*: Apply digital cell-type deconvolution (e.g., CIBERSORTx) using single-cell FLS/leukocyte reference matrices, or validate expression using single-cell RNA-seq and spatial transcriptomics.

2. **Unidirectional Dataset Selection (Absence of Upregulated Signal)**: 
   The provided dataset contains exclusively downregulated genes (100/100). This absolute bias suggests either a pre-filtered tail of the differential expression spectrum or normalization artifacts (e.g., massive overexpression of inflammatory cytokines suppressing relative read counts of structural genes).
   * *Resolution Strategy*: Evaluate un-truncated differential expression tables containing both upregulated and downregulated genes across full log2FC distributions.

3. **Absence of Independent Cohort Replication**: 
   External statistical validation was not performed on an independent cohort in the provided dataset. High statistical significance within a single batch does not eliminate platform-specific artifacts or cohort selection biases.
   * *Resolution Strategy*: Perform cross-validation in independent public RA microarray and RNA-seq datasets (e.g., GEO datasets GSE89408, GSE55235).

4. **Treatment Exposure and Disease Stage Variance**: 
   Patients providing RA synovial biopsies frequently receive disease-modifying antirheumatic drugs (DMARDs) or biologic agents (e.g., anti-TNF), which alter cellular transcriptomes.
   * *Resolution Strategy*: Stratify expression analysis by treatment-naive vs DMARD/biologic-treated cohorts and by early vs late-stage RA.

5. **Broad or Nonspecific Non-Coding RNA Annotations**: 
   Small non-coding RNAs (*MIR3154*, *MIR3183*, *RNA5-8SN2*) display large effect sizes ($\text{log}_2\text{FC} < -4.5$) but lack validated tissue-specific target maps in synovial cells, carrying a risk of speculative functional assignment.
   * *Resolution Strategy*: Conduct AGO2-RIP-seq or miRNA mimic transfection experiments in primary human FLS to map direct mRNA targets.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=0, external claims checked=0, external mismatches=0, status=passed.

Answer model API: Google Gemini / gemini-3.6-flash

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 84/100 selected items (records returned); cbioportal 82/100 selected items (records returned); chembl 16/100 selected items (records returned); civic 1/100 selected items (records returned); clinicaltrials 19/100 selected items (records returned); clinvar 79/100 selected items (records returned); ensembl 40/100 selected items (partially returned; some queries failed); europepmc 776 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 61/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 47/100 selected items (records returned); humanbase 88/100 selected items (partially returned; some queries failed); intact 47/100 selected items (records returned); mygene 93/100 selected items (records returned); omnipath 17/100 selected items (records returned); opentargets 82/100 selected items (records returned); pubmed 483 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 50/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 51/100 selected items (records returned)
Local databases: gutmgene 0/100 selected items (reachable but no records for this batch); hmdb 8/100 selected items (records returned); string 49/100 selected items (records returned); trrust 7/100 selected items (records returned)
