# ulcerative colitis (UC) - gemini-3.6-flash

- Benchmark system: E2seq + Agent RAG
- Repeat: 2
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
- Prompt tokens: 20041
- Completion tokens: 14193
- Reasoning tokens: 8295
- Total tokens: 34234
- API requests reported: 1
- Elapsed seconds: 61.254
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 1095.213
- Question handoff seconds: 1109.559
- Final benchmark system: E2seq; file rank 2/5; original repeat 2; model vendor: Google Gemini

---
### 1. Overall Biological Interpretation

Transcriptomic profiling of colonic mucosal tissue from patients with ulcerative colitis (UC) compared to healthy controls demonstrates a dramatic shift characterized by **intense mucosal inflammatory infiltration, active tissue remodeling, oxidative stress, and profound suppression of mature epithelial absorptive and metabolic programs**. 

The overall biological architecture reveals two major functional axes:
1. **Inflammatory & Stromal Activation Axis (Upregulated):** A coordinated surge in neutrophil-attracting CXC chemokines (*CXCL1*, *CXCL2*, *CXCL3*), inflammatory alarmins (*S100A8*, *LCN2*), extracellular matrix-degrading enzymes (*MMP3*), matrix components (*TNC*), tissue protection factor antiproteases (*PI3*, *SERPINB5*), and epithelial antimicrobial/reactive oxygen species generating machinery (*DUOX2*, *DUOXA2*). Nutrient import transporters such as *SLC6A14* are markedly induced to sustain inflammatory and regenerative demands.
2. **Epithelial Dysfunction & Barrier Collapse Axis (Downregulated):** Severe loss of mature enterocyte functional gene expression, including transcellular water channels (*AQP8*, *AQP7*), short-chain fatty acid (SCFA) transporters (*SLC16A1* / MCT1), solute/vitamin transporters (*SLC23A1*, *SLC38A4*, *SLC23A3*), bile acid handling transporters (*SLC51A*, *ABCB11*, *ABCG2*), and rate-limiting mitochondrial ketogenesis enzymes (*HMGCS2*).

This dual-axis pattern reflects active mucosal ulceration, neutrophil infiltration, and crypt architecture disruption accompanied by loss of mature absorptive colonocyte mass.

---

### 2. Core Biological Programs

```
                  ┌─────────────────────────────────────────────────────────┐
                  │   Colonic Mucosal Transcriptomic Remodeling in UC       │
                  └────────────────────────────┬────────────────────────────┘
                                               │
               ┌───────────────────────────────┴───────────────────────────────┐
               ▼                                                               ▼
 ┌───────────────────────────┐                                   ┌───────────────────────────┐
 │   Upregulated Programs    │                                   │   Downregulated Programs  │
 ├───────────────────────────┤                                   ├───────────────────────────┤
 │ 1. Neutrophil Recruitment │                                   │ 4. Epithelial Fluid &     │
 │    (CXCL1/2/3, S100A8)    │                                   │    Solute Transport       │
 │ 2. Oxidative ROS & H2O2   │                                   │    (AQP8, SLC16A1, AQP7)  │
 │    (DUOX2, DUOXA2, PI3)   │                                   │ 5. Bile Acid & Metabolite │
 │ 3. ECM Remodeling         │                                   │    Detoxification         │
 │    (MMP3, TIMP1, TNC)     │                                   │    (SLC51A, HMGCS2, ABCG2)│
 └───────────────────────────┘                                   └───────────────────────────┘
```

#### Program 1: Mucosal Neutrophil Recruitment and Chemokine Signaling
* **Direction:** Upregulated in UC
* **Major Supporting Genes:** *CXCL1* ($\text{log}_2\text{FC} = 3.46$, $\text{FDR} = 1.15 \times 10^{-15}$), *CXCL2* ($\text{log}_2\text{FC} = 2.80$, $\text{FDR} = 1.73 \times 10^{-11}$), *CXCL3* ($\text{log}_2\text{FC} = 2.33$, $\text{FDR} = 2.51 \times 10^{-11}$), *S100A8* ($\text{log}_2\text{FC} = 3.80$, $\text{FDR} = 4.43 \times 10^{-11}$), *LCN2* ($\text{log}_2\text{FC} = 2.67$, $\text{FDR} = 1.37 \times 10^{-21}$)
* **Standardized Pathway:** KEGG: IL-17 signaling pathway (`hsa04657`) / GO: Chemokine-mediated signaling pathway (`GO:0070098`)
* **Biological Rationale:** *CXCL1*, *CXCL2*, and *CXCL3* are CXCR2 receptor agonists responsible for directing neutrophil extravasation into inflamed colonic mucosa. Elevated *S100A8* (calprotectin subunit) and *LCN2* (lipocalin-2) reflect granule exocytosis and alarmin secretion by infiltrating myeloid cells.
* **Evidence Strength & Limitations:** Strong statistical confidence ($\text{FDR} < 10^{-10}$) across multiple inflammatory markers. *Limitation:* Transcript upregulation reflects both cell-intrinsic activation and an increased ratio of infiltrating neutrophils within biopsy samples. External statistical validation was not performed.

#### Program 2: Epithelial Oxidative Stress and Antimicrobial $\text{H}_2\text{O}_2$ Generation
* **Direction:** Upregulated in UC
* **Major Supporting Genes:** *DUOX2* ($\text{log}_2\text{FC} = 4.67$, $\text{FDR} = 4.45 \times 10^{-26}$), *DUOXA2* ($\text{log}_2\text{FC} = 2.89$, $\text{FDR} = 1.12 \times 10^{-10}$), *PI3* ($\text{log}_2\text{FC} = 2.21$, $\text{FDR} = 3.97 \times 10^{-19}$), *SERPINB5* ($\text{log}_2\text{FC} = 3.29$, $\text{FDR} = 2.58 \times 10^{-17}$), *VNN1* ($\text{log}_2\text{FC} = 3.20$, $\text{FDR} = 1.54 \times 10^{-15}$)
* **Standardized Pathway:** Reactome: ROS and RNS production in phagocytes / mucosal defense (`R-HSA-3299685` / `GO:0042742`)
* **Biological Rationale:** Dual oxidase 2 (*DUOX2*) and its essential maturation factor (*DUOXA2*) form an apical membrane complex generating hydrogen peroxide ($\text{H}_2\text{O}_2$) for mucosal host defense. Concurrent induction of *PI3* (peptidase inhibitor 3 / elafin), *SERPINB5*, and *VNN1* indicates protective oxidative stress and antiprotease mucosal responses.
* **Evidence Strength & Limitations:** High effect sizes and tight biological concordance between enzyme (*DUOX2*) and accessory factor (*DUOXA2*). *Limitation:* Chronic mucosal $\text{H}_2\text{O}_2$ hyperproduction can exacerbate oxidative mucosal injury. External statistical validation was not performed.

#### Program 3: Extracellular Matrix Remodeling and Stromal Activation
* **Direction:** Upregulated in UC
* **Major Supporting Genes:** *MMP3* ($\text{log}_2\text{FC} = 4.64$, $\text{FDR} = 5.40 \times 10^{-14}$), *TNC* ($\text{log}_2\text{FC} = 2.58$, $\text{FDR} = 2.51 \times 10^{-11}$), *PDPN* ($\text{log}_2\text{FC} = 2.54$, $\text{FDR} = 1.75 \times 10^{-10}$), *PRRX1* ($\text{log}_2\text{FC} = 2.91$, $\text{FDR} = 4.35 \times 10^{-16}$), *TIMP1* ($\text{log}_2\text{FC} = 1.97$, $\text{FDR} = 1.81 \times 10^{-17}$)
* **Standardized Pathway:** Reactome: Degradation of the extracellular matrix (`R-HSA-1474228`) / GO: Extracellular matrix organization (`GO:0030198`)
* **Biological Rationale:** Ulceration triggers basement membrane degradation and stromal tissue remodeling. *MMP3* degrades connective tissue components and activates other metalloproteinases, balanced by endogenous metalloproteinase inhibitor *TIMP1*. *TNC* (tenascin C) and *PDPN* (podoplanin) signal activated subepithelial myofibroblasts under regulatory transcription factors like *PRRX1*.
* **Evidence Strength & Limitations:** Strongly co-regulated module of enzymes, inhibitors, matrix glycoproteins, and mesenchyme-associated transcription factors. *Limitation:* Cannot distinguish productive mucosal wound healing from pathological tissue destruction in bulk tissue. External statistical validation was not performed.

#### Program 4: Mucosal Epithelial Fluid, Electrolyte, and Solute Transport Deficit
* **Direction:** Downregulated in UC
* **Major Supporting Genes:** *AQP8* ($\text{log}_2\text{FC} = -4.42$, $\text{FDR} = 1.60 \times 10^{-13}$), *AQP7* ($\text{log}_2\text{FC} = -2.32$, $\text{FDR} = 4.04 \times 10^{-20}$), *SLC16A1* ($\text{log}_2\text{FC} = -2.38$, $\text{FDR} = 5.82 \times 10^{-21}$), *SLC23A1* ($\text{log}_2\text{FC} = -2.40$, $\text{FDR} = 8.89 \times 10^{-29}$), *SLC38A4* ($\text{log}_2\text{FC} = -3.07$, $\text{FDR} = 4.70 \times 10^{-37}$)
* **Standardized Pathway:** GO: Fluid Transport (`GO:0042044`) / GO: Carboxylic Acid Transport (`GO:0046942`)
* **Biological Rationale:** Major reduction in transcellular fluid and nutrient uptake mechanisms. *AQP8* (apical colonocyte water channel) and *AQP7* water/glycerol transport failure directly contribute to inflammatory secretory diarrhea. Downregulation of *SLC16A1* (MCT1) impairs luminal butyrate uptake necessary for colonocyte energetic homeostasis.
* **Evidence Strength & Limitations:** Extremely strong statistical significance ($\text{FDR} < 10^{-13}$) across solute carrier and aquaporin gene families. *Limitation:* Downregulation is driven both by cellular transcriptional repression and physical loss of surface enterocytes due to erosion. External statistical validation was not performed.

#### Program 5: Enterocyte Bile Acid Handling and Metabolic Detoxification Suppression
* **Direction:** Downregulated in UC
* **Major Supporting Genes:** *SLC51A* ($\text{log}_2\text{FC} = -3.71$, $\text{FDR} = 1.54 \times 10^{-20}$), *HMGCS2* ($\text{log}_2\text{FC} = -3.45$, $\text{FDR} = 1.10 \times 10^{-16}$), *GBA3* ($\text{log}_2\text{FC} = -3.00$, $\text{FDR} = 4.12 \times 10^{-17}$), *ABCG2* ($\text{log}_2\text{FC} = -2.92$, $\text{FDR} = 1.11 \times 10^{-10}$), *ABCB11* ($\text{log}_2\text{FC} = -1.15$, $\text{FDR} = 8.91 \times 10^{-11}$), *CYP2B6* ($\text{log}_2\text{FC} = -2.78$, $\text{FDR} = 4.18 \times 10^{-13}$)
* **Standardized Pathway:** KEGG: Bile secretion (`hsa04976`) / Reactome: Metabolism of lipids (`R-HSA-556833`)
* **Biological Rationale:** Suppression of mature colonocyte metabolic and xenobiotic handling functions. *SLC51A* (OST-alpha) and *ABCB11* handle organic solute and bile salt export, *ABCG2* transports xenobiotics/drugs, and *HMGCS2* regulates mitochondrial ketogenesis. Phase I/II enzymes (*CYP2B6*, *GBA3*) are lost alongside normal epithelial differentiation.
* **Evidence Strength & Limitations:** Broad co-directional suppression of metabolic networks. *Limitation:* Likely represents secondary suppression by pro-inflammatory cytokines (e.g., TNF, IL-1$\beta$) rather than a primary genetic etiology. External statistical validation was not performed.

---

### 3. Key Genes and Interaction Modules

| Candidate / Module | Statistical Direction | Role in Core Programs | Proposed Relationship Type |
| :--- | :--- | :--- | :--- |
| **DUOX2 / DUOXA2** | Upregulated<br>(*DUOX2* $\text{log}_2\text{FC} = 4.67$;<br>*DUOXA2* $\text{log}_2\text{FC} = 2.89$) | Mucosal ROS/$\text{H}_2\text{O}_2$ production for innate defense | **Regulatory & Physical Interaction:** DUOXA2 is an obligate endoplasmic reticulum maturation factor and subunit required for DUOX2 surface trafficking and functional enzymatic activation. |
| **CXCL1 / CXCL2 / CXCL3** | Upregulated<br>(*CXCL1* $+3.46$;<br>*CXCL2* $+2.80$;<br>*CXCL3* $+2.33$) | Chemoattraction of circulating CXCR2+ neutrophils into mucosa | **Pathway Co-Membership & Co-Expression:** Paralogous CXC chemokines co-expressed in activated mucosal and immune cells; share common CXCR2 receptor binding mechanisms. |
| **MMP3 / TIMP1** | Upregulated<br>(*MMP3* $+4.64$;<br>*TIMP1* $+1.97$) | Extracellular matrix degradation and tissue turnover regulation | **Direct Physical & Regulatory Interaction:** TIMP1 protein physically binds to active MMP3 to inhibit catalytic matrix cleavage; co-member of ECM remodeling pathways. |
| **SLC6A14** | Upregulated<br>($\text{log}_2\text{FC} = 4.85$, $\text{FDR} = 8.07 \times 10^{-39}$) | Top upregulated gene; sodium-coupled nutrient transporter | **Co-Expression / Functional Adaptation:** Co-induced during epithelial repair and cell stress to increase uptake of amino acids (glutamine, arginine) in regenerating crypt mucosa. |
| **AQP8 / AQP7** | Downregulated<br>(*AQP8* $-4.42$;<br>*AQP7* $-2.32$) | Transcellular fluid absorption across mucosal enterocytes | **Pathway Co-Membership:** Co-regulated aquaporin family members responsible for mucosal water/glycerol homeostasis (STRING interaction module). |
| **SLC16A1 / HMGCS2** | Downregulated<br>(*SLC16A1* $-2.38$;<br>*HMGCS2* $-3.45$) | Butyrate uptake (*SLC16A1*) and mitochondrial oxidation (*HMGCS2*) | **Pathway Co-Membership:** Sequential metabolic steps enabling colonocytes to import and convert short-chain fatty acids into ketone bodies for energy. |
| **S100A8 / LCN2** | Upregulated<br>(*S100A8* $+3.80$;<br>*LCN2* $+2.67$) | Neutrophil-derived alarmins and antimicrobial iron-sequestration | **Co-Expression:** Co-released from neutrophil granules into the mucosal lumen during acute inflammation. |
| **SLC51A / ABCB11** | Downregulated<br>(*SLC51A* $-3.71$;<br>*ABCB11* $-1.15$) | Basolateral and luminal transport of bile salts and organic solutes | **Pathway Co-Membership:** Functional co-transporters in epithelial organic anion and bile acid clearance networks. |

---

### 4. Validation Priorities

#### Priority 1: Mechanistic Hypothesis — Epithelial Barrier Defense vs Oxidative Damage by DUOX2/DUOXA2
* **Rationale:** *DUOX2* ($\text{log}_2\text{FC} = 4.67$) and *DUOXA2* ($\text{log}_2\text{FC} = 2.89$) are among the most strongly induced genes in UC colonic mucosa.
* **Dataset Evidence:** Concurrent, highly significant induction of both catalytic (*DUOX2*) and maturation (*DUOXA2*) subunits alongside cytoprotective genes (*PI3*, *SERPINB5*).
* **External Evidence:** Literature (PMID: 41029776, 38059894) links *DUOX2* induction to mucosal oxidative stress in IBD; mouse models demonstrate that *Duox2* activity is required for luminal microbial containment but excess ROS causes crypt atrophy.
* **Validation Next Step:** Human primary patient-derived colonic organoids subjected to inflammatory cytokines (TNF-$\alpha$, IFN-$\gamma$) $\pm$ selective DUOX2 knockdown, evaluating barrier trans-epithelial electrical resistance (TEER) and hydrogen peroxide output.
* **Evidence Status:** Supported hypothesis.

#### Priority 2: Confounding / Composition Check — Distinguishing Epithelial Transport Silencing from Epithelial Cell Depletion
* **Rationale:** Widespread downregulation of enterocyte transporters (*AQP8*, *SLC16A1*, *SLC51A*, *SLC38A4*) could reflect cell-intrinsic transcriptional repression versus physical loss of surface enterocytes due to mucosal ulceration.
* **Dataset Evidence:** Co-directional loss of multiple enterocyte-specific markers (*AQP8* $\text{log}_2\text{FC} = -4.42$, *SLC51A* $-3.71$, *HMGCS2* $-3.45$).
* **External Evidence:** Single-cell transcriptomic surveys in IBD demonstrate both enterocyte population depletion and intrinsic downregulation of absorptive genes in surviving colonocytes.
* **Validation Next Step:** Quantitative single-cell RNA sequencing or spatial transcriptomics (e.g., RNAscope multiplexing) on inflamed UC mucosal biopsies, normalizing solute carrier expression against epithelial lineage drivers (e.g., *KRT8*, *VIL1*).
* **Evidence Status:** Exploratory hypothesis.

#### Priority 3: Therapeutic Target — CXCR2 Receptor Antagonism (*CXCL1*, *CXCL2*, *CXCL3*)
* **Rationale:** CXC chemokines drive pathogenic neutrophil infiltration and crypt abscess formation in UC.
* **Dataset Evidence:** High co-induction of *CXCL1* ($\text{log}_2\text{FC} = 3.46$), *CXCL2* ($+2.80$), *CXCL3* ($+2.33$), and neutrophil markers (*S100A8*, *LCN2*).
* **External Evidence:** Small-molecule CXCR2 antagonists reduce colitis severity in preclinical rodent models; clinical trial data show mixed efficacy depending on tissue exposure and patient stratification.
* **Validation Next Step:** In vitro human neutrophil trans-endothelial migration assays using patient mucosal biopsy supernatants with selective CXCR2 inhibitors. *Note: Target presence does not guarantee clinical efficacy.*
* **Evidence Status:** Supported hypothesis.

#### Priority 4: Biomarker — Stool/Serum Non-Invasive Diagnostic Panel (*CHI3L1*, *S100A8*, *LCN2*, *MMP3*)
* **Rationale:** Secreted protein products with marked statistical upregulation represent candidates for non-invasive disease monitoring.
* **Dataset Evidence:** *CHI3L1* ($\text{log}_2\text{FC} = 4.59$), *MMP3* ($+4.64$), *S100A8* ($+3.80$), and *LCN2* ($+2.67$) rank among the top induced genes.
* **External Evidence:** Fecal calprotectin (*S100A8/S100A9*) is an established UC clinical biomarker; CHI3L1 and LCN2 correlate with endoscopic inflammation scores in clinical studies.
* **Validation Next Step:** Multi-center prospective clinical cohort testing of ELISA-based stool/serum protein concentrations against endoscopic Mayo scores during therapeutic induction.
* **Evidence Status:** Established evidence (for S100A8/calprotectin); Supported hypothesis (for multi-marker diagnostic performance).

#### Priority 5: Interaction / Network Hypothesis — MMP3/TIMP1 Stoichiometric Imbalance in Mucosal Healing
* **Rationale:** Tissue injury outcomes depend on the proteolytic balance between matrix metalloproteinases and endogenous tissue inhibitors.
* **Dataset Evidence:** *MMP3* induction ($\text{log}_2\text{FC} = 4.64$) outpaces *TIMP1* induction ($\text{log}_2\text{FC} = 1.97$).
* **External Evidence:** Elevated MMP-to-TIMP ratios in mucosal biopsies correlate with therapy non-response and fistulizing/ulcerative disease progression in IBD.
* **Validation Next Step:** Substrate zymography and stoichiometric protein profiling of mucosal tissue extracts to measure net collagenolytic activity in patient mucosal biopsies.
* **Evidence Status:** Supported hypothesis.

---

### 5. Evidence Grounding

```
  Evidence Category                                Contextual Description & Scope
 ───────────────────────────────────────────────────────────────────────────────────────────────────
  Direct Input Dataset Evidence    Differential expression of 100 genes (40 up, 60 down; all FDR <= 1e-10).
                                   Primary findings include SLC6A14 (+4.85), DUOX2 (+4.67), MMP3 (+4.64),
                                   AQP8 (-4.42), SLC51A (-3.71), and HMGCS2 (-3.45).

  Pathway / Ontology Evidence     KEGG (IL-17 signaling, Bile secretion) and GO (Fluid transport, 
                                   Chemokine signaling) records from Reactome, KEGG, and QuickGO.
                                   *Note: Annotations are external and do not substitute for statistical
                                   replication.*

  Protein / Regulatory Evidence   STRING network links (50 edges) for CXCL1/2/3, MMP3/TIMP1, and AQP7/8.
                                   TRRUST regulatory annotations for immune transcription networks.

  Disease & Genetic Evidence       GWAS and OpenTargets records linking DUOX2, MMP3, S100A8, CTLA4, and 
                                   BRINP3 (PMID: 25171508) to IBD susceptibility.

  Tissue-Specific Evidence         HPA and GTEx data confirming high baseline expression of AQP8, SLC16A1, 
                                   and HMGCS2 in healthy colonic epithelium.

  External Cohort Replication     *External statistical validation was not performed* (no independent cohort
                                   statistics supplied in the input dataset).
```

*Note on Source Independence:* Database records (STRING, Reactome, QuickGO, OpenTargets) frequently overlap by aggregating shared literature sources (e.g., PubMed citations) and should be interpreted as interconnected biological contextualization rather than independent confirmatory statistics.

---

### 6. Limitations and Alternative Explanations

1. **Cell-Composition Confounding (Infiltrate vs. Epithelium):** Bulk mucosal tissue biopsies capture both native structural cells and infiltrating immune populations. Increased expression of *CXCL1*, *S100A8*, *LCN2*, and *CTLA4* likely reflects an increased proportion of infiltrating neutrophils and lymphocytes rather than cell-intrinsic transcriptomic upregulation alone.
   * *Resolution Strategy:* Perform single-cell RNA sequencing or spatial cell deconvolution (e.g., CIBERSORTx) to isolate cell-type proportion shifts from cell-intrinsic transcriptional changes.
2. **Epithelial Damage and Mass Depletion:** Downregulation of absorptive markers (*AQP8*, *AQP7*, *SLC16A1*, *SLC51A*) may stem directly from mucosal ulceration and loss of surface enterocyte mass rather than specific gene suppression in healthy cells.
   * *Resolution Strategy:* Normalize absorptive gene expression against epithelial cell-type markers (e.g., *KRT8*, *VIL1*) or analyze enriched epithelial fractions.
3. **Treatment Exposure Artifacts:** Biopsies from UC patients often originate from individuals receiving anti-inflammatory medications (e.g., 5-aminosalicylates, corticosteroids, biologic therapies), which can modify transcriptomic profiles independently of baseline disease pathology.
   * *Resolution Strategy:* Stratify patient cohorts into treatment-naive versus pharmacologically treated groups prior to differential expression testing.
4. **Lack of Independent Statistical Replication:** All statistical conclusions are derived from a single input dataset without independent external statistical validation.
   * *Resolution Strategy:* Test key marker panels (*DUOX2*, *MMP3*, *AQP8*, *SLC16A1*) across independent GEO/ArrayExpress transcriptomic cohorts (e.g., GSE38713, GSE59071).
5. **Association vs. Causation Ambiguity:** Differentially expressed genes represent correlated disease features; transcriptomic induction (e.g., *DUOX2* or *MMP3*) does not establish whether a gene plays a causal pathogenic role, serves a protective compensatory function, or is a bystander effect.
   * *Resolution Strategy:* Apply Mendelian Randomization (MR) using human eQTL GWAS data paired with functional gene knockout models in colonic organoid systems.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=0, external claims checked=0, external mismatches=0, status=passed.

Answer model API: Google Gemini / gemini-3.6-flash

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 94/100 selected items (records returned); cbioportal 87/100 selected items (records returned); chembl 40/100 selected items (partially returned; some queries failed); civic 7/100 selected items (records returned); clinicaltrials 51/100 selected items (records returned); clinvar 90/100 selected items (records returned); ensembl 55/100 selected items (partially returned; some queries failed); europepmc 936 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 91/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 85/100 selected items (records returned); humanbase 87/100 selected items (records returned); intact 85/100 selected items (records returned); mygene 93/100 selected items (records returned); omnipath 45/100 selected items (records returned); opentargets 92/100 selected items (records returned); pubmed 750 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 87/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 88/100 selected items (records returned)
Local databases: gutmgene 8/100 selected items (records returned); hmdb 46/100 selected items (records returned); string 85/100 selected items (records returned); trrust 31/100 selected items (records returned)
