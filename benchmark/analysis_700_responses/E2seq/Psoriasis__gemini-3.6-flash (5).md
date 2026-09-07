# psoriasis - gemini-3.6-flash

- Benchmark system: E2seq + Agent RAG
- Repeat: 7
- Task type: DISEASE-STATE
- Tissue / sample source: lesional skin
- Comparison or endpoint: psoriatic lesional skin versus normal control skin
- Answer input cohort: Discovery/Core only
- Selected items: 100
- Input fields: gene name, effect size (log2FC/HR), P value, FDR
- E2seq Agent RAG: enabled
- Conversation memory: disabled
- Thinking mode: disabled
- Held-out validation data in prompt/RAG: no
- Model API: Google Gemini / gemini-3.6-flash
- Message SHA-256: d1a33d3f606c81814c4fb94a6c63c8f1abebd3bde37d769e82eae4772d8ff873
- Response HTTP status: 200
- Prompt tokens: 22081
- Completion tokens: 48292
- Reasoning tokens: 0
- Total tokens: 70373
- API requests reported: 4
- Elapsed seconds: 50.658
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 1150.303
- Question handoff seconds: 1163.566
- Final benchmark system: E2seq; file rank 5/5; original repeat 7; model vendor: Google Gemini

---
### 1. Overall Biological Interpretation

The transcriptomic comparison between psoriatic lesional skin and normal control skin reveals a coordinated, high-amplitude inflammatory and tissue-remodeling phenotype characteristic of active plaque psoriasis. The dysregulated gene expression pattern is anchored by three primary hyper-activated biological axes alongside specific gene suppression:

1. **Epidermal Differentiation and Cornified Envelope Dysregulation:** Marked up-regulation of small proline-rich proteins (*SPRR2A*, *SPRR2B*, *SPRR2D*, *SPRR2E*, *SPRR2F*, *SPRR2G*, *SPRR3*), late cornified envelope proteins (*LCE3A*, *LCE3D*), keratins (*KRT6A*), and intercellular gap junction channels (*GJB2*, *GJB6*), reflecting aberrant keratinocyte hyperproliferation and altered terminal differentiation.
2. **Pro-Inflammatory Cytokine Amplification Loops:** Robust induction of IL-36 subfamily cytokines (*IL36A*, *IL36G*, *IL36RN*) and IL-20 subfamily cytokines (*IL19*, *IL20*, *IL26*), which drive autocrine and paracrine feed-forward activation in the epidermis and recruit immune cells.
3. **Antimicrobial and Alarmin Defense System:** Massive upregulation of epithelial defensins (*DEFB4A*, *DEFB4B*, *DEFB103A*, *DEFB103B*) and S100 alarmins (*S100A7*, *S100A7A*, *S100A8*, *S100A12*), serving as downstream effectors of IL-17 and IL-36 signaling.
4. **Metabolic and Regulatory Reprogramming:** Induction of lipid, kynurenine, and aldehyde metabolic enzymes (*AKR1B10*, *AKR1B15*, *KYNU*, *FABP5*, *PLA2G4D*) alongside selective suppression of homeostatic epidermal growth factor signaling (*BTC*, $\text{log2FC} = -4.299$) and skin-associated non-coding RNAs (*WAKMAR1*, $\text{log2FC} = -5.628$).

---

### 2. Core Biological Programs

#### Program 1: Cornified Envelope Formation and Keratinocyte Hyperproliferation
* **Direction:** Upregulated
* **Major Supporting Genes:** *SPRR2A* ($\text{log2FC} = 7.312$), *SPRR2B* ($\text{log2FC} = 6.380$), *SPRR2D* ($\text{log2FC} = 5.920$), *SPRR3* ($\text{log2FC} = 7.180$), *LCE3A* ($\text{log2FC} = 8.298$), *LCE3D* ($\text{log2FC} = 5.314$), *PI3* ($\text{log2FC} = 9.240$), *SERPINB3* ($\text{log2FC} = 6.742$), *SERPINB4* ($\text{log2FC} = 9.118$), *KRT6A* ($\text{log2FC} = 4.303$), *GJB2* ($\text{log2FC} = 4.419$), *GJB6* ($\text{log2FC} = 3.018$)
* **Standardized Pathway:** Reactome: *Formation of the cornified envelope* (R-HSA-6809371); GO: *Epidermis Development* (GO:0008544)
* **Collective Evidence Rationale:** Epidermal keratinocytes in psoriatic lesions undergo accelerated differentiation, leading to altered stratum corneum formation. *SPRR* and *LCE* genes encode structural precursor proteins cross-linked by transglutaminases, while *PI3* (elafin) and *SERPINB3/4* encode endogenous protease inhibitors protecting against excessive epidermal degradation.
* **Evidence Strength & Limitations:** High effect magnitude ($\text{log2FC} > 3.0$ to $9.2$) and co-directional consistency across 15+ structural genes. *Limitation:* Bulk transcriptomic measurement cannot separate per-cell transcript hyperactivation from epidermal acanthosis (increased keratinocyte cell density relative to dermis).

#### Program 2: IL-36 and IL-20 Subfamily Cytokine Signaling Axis
* **Direction:** Upregulated
* **Major Supporting Genes:** *IL36A* ($\text{log2FC} = 11.374$), *IL36G* ($\text{log2FC} = 5.684$), *IL36RN* ($\text{log2FC} = 3.005$), *IL19* ($\text{log2FC} = 7.580$), *IL20* ($\text{log2FC} = 5.667$), *IL26* ($\text{log2FC} = 4.361$), *TNIP3* ($\text{log2FC} = 7.279$), *IRAK2* ($\text{log2FC} = 2.083$), *ZC3H12A* ($\text{log2FC} = 3.848$)
* **Standardized Pathway:** KEGG: *IL-17 signaling pathway*; KEGG: *Cytokine-cytokine receptor interaction*
* **Collective Evidence Rationale:** *IL36A* and *IL36G* are primary epithelial alarmins driving NF-$\kappa$B and MAPK cascades via IL1RL2/IL1RAP. Concurrently, *IL19* and *IL20* signal through IL-20 receptor complexes to induce STAT3 phosphorylation and keratinocyte proliferation. Upregulation of *IL36RN* and feedback regulators (*TNIP3*, *ZC3H12A*) reflects active intracellular counter-regulatory mechanisms.
* **Evidence Strength & Limitations:** Supported by extreme statistically significant fold-changes (*IL36A* $\text{FDR} = 1.655 \times 10^{-98}$). *Limitation:* Expression levels in whole-skin tissue biopsies represent a mixed signal of keratinocyte autocrine activity and infiltrating immune cells (macrophages, dendritic cells, T cells).

#### Program 3: Epithelial Antimicrobial Defense and Alarmin Response
* **Direction:** Upregulated
* **Major Supporting Genes:** *DEFB4A* ($\text{log2FC} = 11.183$), *DEFB4B* ($\text{log2FC} = 11.031$), *DEFB103A* ($\text{log2FC} = 5.758$), *DEFB103B* ($\text{log2FC} = 5.751$), *S100A7A* ($\text{log2FC} = 9.833$), *S100A12* ($\text{log2FC} = 8.329$), *S100A8* ($\text{log2FC} = 7.729$), *S100A7* ($\text{log2FC} = 7.095$)
* **Standardized Pathway:** GO: *Antimicrobial Humoral Response* (GO:0019730); GO: *Response To Lipopolysaccharide* (GO:0032496)
* **Collective Evidence Rationale:** Beta-defensins (*DEFB4A/B*, *DEFB103A/B*) act directly as antimicrobial peptides and chemoattractants for immune cells. S100 proteins (*S100A7*, *S100A8*, *S100A12*) function as endogenous danger signals (DAMPs) and calcium-binding alarmins that amplify leukocyte recruitment and keratinocyte stress signaling.
* **Evidence Strength & Limitations:** Extremely high effect sizes ($\text{log2FC} = 7.095$ to $11.183$). *Limitation:* Antimicrobial peptide elevation is a general feature of epithelial cutaneous stress and wound repair, making it partially non-specific to psoriasis etiology.

#### Program 4: Kynurenine and Lipid Metabolic Reprogramming
* **Direction:** Upregulated (Metabolic Enzymes) / Downregulated (Homeostatic Enzymes)
* **Major Supporting Genes:** Upregulated: *AKR1B10* ($\text{log2FC} = 6.265$), *AKR1B15* ($\text{log2FC} = 5.231$), *KYNU* ($\text{log2FC} = 4.416$), *FABP5* ($\text{log2FC} = 3.645$), *PLA2G4D* ($\text{log2FC} = 4.615$), *PLA2G4E* ($\text{log2FC} = 2.470$), *GDA* ($\text{log2FC} = 5.896$), *VNN3P* ($\text{log2FC} = 8.283$). Downregulated: *CYP2W1* ($\text{log2FC} = -4.704$), *UGT3A2* ($\text{log2FC} = -4.591$)
* **Standardized Pathway:** KEGG / Reactome: *Tryptophan metabolism*; *Arachidonic acid metabolism*; *Xenobiotic metabolism*
* **Collective Evidence Rationale:** Induction of *KYNU* (kynureninase) indicates increased tryptophan breakdown along the immunosuppressive kynurenine pathway under cytokine stress. Upregulation of aldo-keto reductases (*AKR1B10/15*) and fatty acid binding proteins (*FABP5*) reflects altered retinoid/lipid metabolism, while downregulation of phase I/II detoxification enzymes (*CYP2W1*, *UGT3A2*) signals loss of homeostatic cutaneous metabolism.
* **Evidence Strength & Limitations:** Coherent shift across multiple metabolic gene families. *Limitation:* Metabolic pathway activation is inferred strictly from mRNA abundance; metabolite fluxes were not directly quantified in this dataset.

#### Program 5: Homeostatic Growth Factor Suppression and Non-Coding RNA Regulation
* **Direction:** Downregulated
* **Major Supporting Genes:** *BTC* ($\text{log2FC} = -4.299$), *WAKMAR1* ($\text{log2FC} = -5.628$), *LINC02660* ($\text{log2FC} = -3.903$), *LOC107984452* ($\text{log2FC} = -6.249$), *LOC107984005* ($\text{log2FC} = -4.270$), *SAPCD1* ($\text{log2FC} = -2.937$), *SAPCD1-AS1* ($\text{log2FC} = -2.836$)
* **Standardized Pathway:** GO: *Regulation of Epidermal Growth Factor Receptor Signaling Pathway*; Non-coding RNA networks
* **Collective Evidence Rationale:** Betacellulin (*BTC*) is a basal EGFR ligand expressed in normal epidermis; its down-regulation indicates a loss of normal quiescent epidermal growth signaling during active plaque formation. Downregulation of skin-specific lncRNAs like *WAKMAR1* highlights the shutdown of basal non-coding regulatory networks that restrain inflammatory skin responses.
* **Evidence Strength & Limitations:** Consistent negative fold-changes among non-coding and homeostatic transcripts. *Limitation:* The precise molecular targets and mechanisms of several uncharacterized lncRNAs (*LOC107984452*, *LINC02660*) remain unknown.

---

### 3. Key Genes and Interaction Modules

| Candidate Gene / Module | Statistical Direction & Effect | Role in Core Biological Programs | Nature of Proposed Gene-Gene Relationship |
| :--- | :--- | :--- | :--- |
| **IL36A / IL36G / IL36RN** | Upregulated (*IL36A* $\text{log2FC} = 11.374$; *IL36G* $\text{log2FC} = 5.684$; *IL36RN* $\text{log2FC} = 3.005$) | Upstream pro-inflammatory cytokine triggers (Program 2) | **Pathway co-membership & regulatory interaction:** *IL36A* and *IL36G* bind the IL-36 receptor complex (IL1RL2/IL1RAP) to trigger downstream NF-$\kappa$B activation, while *IL36RN* acts as a competitive antagonist. |
| **DEFB4A / DEFB4B** | Upregulated (*DEFB4A* $\text{log2FC} = 11.183$; *DEFB4B* $\text{log2FC} = 11.031$) | Primary epithelial antimicrobial effectors (Program 3) | **Co-expression & genomic paralog co-membership:** Functional duplicate genes co-induced by IL-17 and IL-36 in keratinocytes. |
| **S100A7 / S100A7A / S100A8 / S100A12** | Upregulated (*S100A7A* $\text{log2FC} = 9.833$; *S100A12* $\text{log2FC} = 8.329$; *S100A8* $\text{log2FC} = 7.729$; *S100A7* $\text{log2FC} = 7.095$) | Epidermal alarmins and leukocyte chemoattractants (Program 3) | **Direct physical interaction & co-expression:** *S100A8* physically heterodimerizes with *S100A9* (Calprotectin); STRING records confirm physical binding and shared pathway co-membership with *S100A7*. |
| **SPRR Family Module** (*SPRR2A*, *SPRR2B*, *SPRR2D*, *SPRR2E*, *SPRR2F*, *SPRR2G*, *SPRR3*) | Upregulated (*SPRR2A* $\text{log2FC} = 7.312$; *SPRR3* $\text{log2FC} = 7.180$; *SPRR2F* $\text{log2FC} = 7.223$) | Structural cornified envelope precursors (Program 1) | **Direct physical interaction & pathway co-membership:** Substrates physically cross-linked by transglutaminases during cornified envelope assembly. |
| **PI3 & SERPINB3 / SERPINB4** | Upregulated (*PI3* $\text{log2FC} = 9.240$; *SERPINB4* $\text{log2FC} = 9.118$; *SERPINB3* $\text{log2FC} = 6.742$) | Endogenous serine protease inhibitors (Program 1) | **Regulatory interaction & pathway co-membership:** Form physical inhibitory complexes with leukocyte elastase and cathepsins to modulate matrix remodeling. |
| **IL19 / IL20 Axis** | Upregulated (*IL19* $\text{log2FC} = 7.580$; *IL20* $\text{log2FC} = 5.667$) | Paracrine drivers of epidermal hyperplasia (Program 2) | **Pathway co-membership & regulatory interaction:** Signal through shared heterodimeric receptor complexes (IL-20R1/IL-20R2) to induce STAT3 phosphorylation. |
| **AKR1B10** | Upregulated ($\text{log2FC} = 6.265$, $\text{FDR} = 2.348 \times 10^{-89}$) | Aldehyde reduction and lipid metabolism (Program 4) | **Co-expression & pathway co-membership:** Operates in retinoid/lipid metabolic pathways alongside *FABP5* ($\text{log2FC} = 3.645$). |
| **KYNU** | Upregulated ($\text{log2FC} = 4.416$, $\text{FDR} = 2.001 \times 10^{-91}$) | Tryptophan catabolism and kynurenine production (Program 4) | **Pathway co-membership:** Downstream enzyme in the kynurenine pathway induced by IFN-$\gamma$/IL-17 immune activation. |
| **BTC** | Downregulated ($\text{log2FC} = -4.299$, $\text{FDR} = 1.776 \times 10^{-73}$) | Homeostatic EGFR ligand in basal keratinocytes (Program 5) | **Regulatory interaction:** Suppressed EGFR ligand inverse to inflammatory cytokine elevation. |
| **WAKMAR1** | Downregulated ($\text{log2FC} = -5.628$, $\text{FDR} = 2.205 \times 10^{-62}$) | Non-coding RNA controlling skin wound healing and inflammation (Program 5) | **Indirect / Putative regulatory relationship:** Inverse co-expression with epidermal stress genes. |

---

### 4. Validation Priorities

#### Priority 1: In Vitro Blockade of the IL-36 Cytokine Amplification Loop
* **Classification:** Therapeutic target
* **Prioritization Rationale:** *IL36A* ($\text{log2FC} = 11.374$) and *IL36G* ($\text{log2FC} = 5.684$) display massive induction in lesional skin, functioning as key upstream initiators of keratinocyte activation.
* **Current Dataset Evidence:** Co-induction of *IL36A*, *IL36G*, and their regulatory antagonist *IL36RN* ($\text{log2FC} = 3.005$).
* **External Evidence:** Anti-IL-36R monoclonal antibody therapy (e.g., spesolimab) shows efficacy in general pustular psoriasis, and clinical trials explore broader cutaneous indications.
* **Next Validation Step:** Neutralize IL-36R in human 3D reconstituted organotypic epidermis stimulated with IL-17A, quantifying suppression of downstream effectors (*DEFB4A*, *S100A12*, *PI3*).
* **Evidence Status:** Established evidence (pathway clinically validated, though external statistical validation was not performed on this specific dataset cohort).

#### Priority 2: Functional Mass Spectrometry Profiling of KYNU-Mediated Tryptophan Metabolism
* **Classification:** Mechanistic hypothesis
* **Prioritization Rationale:** *KYNU* upregulation ($\text{log2FC} = 4.416$, $\text{FDR} = 2.001 \times 10^{-91}$) suggests active tryptophan degradation into immunosuppressive kynurenine metabolites within lesional skin.
* **Current Dataset Evidence:** Highly significant elevated *KYNU* transcript levels in lesional versus control skin.
* **External Evidence:** Literature shows kynurenine pathway metabolites regulate T-cell responses and aryl hydrocarbon receptor (AhR) signaling in dermatological inflammation.
* **Next Validation Step:** Perform targeted liquid chromatography-tandem mass spectrometry (LC-MS/MS) on paired psoriatic lesional vs. non-lesional skin biopsies to measure tryptophan, kynurenine, and 3-hydroxyanthranilic acid concentrations.
* **Evidence Status:** Supported hypothesis.

#### Priority 3: Non-Invasive Skin Tape-Stripping Biomarker Panel (*DEFB4A*, *S100A12*, *PI3*)
* **Classification:** Biomarker
* **Prioritization Rationale:** Extreme effect sizes (*DEFB4A* $\text{log2FC} = 11.183$; *PI3* $\text{log2FC} = 9.240$; *S100A12* $\text{log2FC} = 8.329$) provide high dynamic range for monitoring tissue inflammation non-invasively.
* **Current Dataset Evidence:** Uniform, highly significant upregulation across lesional samples.
* **External Evidence:** Published cohorts demonstrate correlation between stratum corneum DEFB4A/S100A12 protein levels and PASI clinical severity scores.
* **Next Validation Step:** Evaluate serial tape-strip protein recovery (ELISA/MRM-MS) in patients initiating biologic therapy (e.g., anti-IL-17 or anti-IL-23 antibodies) across 0, 4, and 12 weeks.
* **Evidence Status:** Supported hypothesis.

#### Priority 4: Dissecting the Functional Impact of WAKMAR1 Downregulation on Keratinocyte Homeostasis
* **Classification:** Mechanistic hypothesis
* **Prioritization Rationale:** *WAKMAR1* is strongly suppressed ($\text{log2FC} = -5.628$, $\text{FDR} = 2.205 \times 10^{-62}$), suggesting loss of a non-coding RNA brake on skin inflammation.
* **Current Dataset Evidence:** Prominent inverse fold-change among top dysregulated non-coding transcripts.
* **External Evidence:** Literature indicates *WAKMAR1* regulates keratinocyte migration and inhibits inflammatory cytokine transcription during cutaneous wound repair.
* **Next Validation Step:** Perform CRISPR interference (CRISPRi) and overexpression of *WAKMAR1* in primary human keratinocytes followed by RNA-seq under IL-17A and TNF-$\alpha$ stimulation.
* **Evidence Status:** Exploratory hypothesis.

#### Priority 5: Computational Deconvolution of Acanthosis vs. Cellular Infiltration
* **Classification:** Confounding or composition check
* **Prioritization Rationale:** Bulk skin transcriptomics conflates cellular composition shifts (epidermal hyper-thickening, neutrophil/T-cell infiltration) with true per-cell transcriptional changes.
* **Current Dataset Evidence:** Concurrent elevation of neutrophil markers (*S100A12*, *CXCR2*) and epidermal differentiation markers (*SPRR*, *LCE*).
* **External Evidence:** Single-cell RNA-seq atlases of psoriatic skin show marked expansion of mitotic keratinocytes, inflammatory dendritic cells, and neutrophils.
* **Next Validation Step:** Perform single-cell RNA sequencing or spatial transcriptomics on paired skin biopsies and apply deconvolution algorithms (e.g., CIBERSORTx) to bulk expression profiles.
* **Evidence Status:** Supported hypothesis.

---

### 5. Evidence Grounding

The conclusions in this analysis rely on distinct classes of supporting evidence:

1. **Direct Input Dataset Evidence:** Log2 fold-changes, P values, and FDR values derived from the differential expression analysis between psoriatic lesional skin and normal control skin (e.g., *IL36A* $\text{log2FC} = 11.374$, *DEFB4A* $\text{log2FC} = 11.183$, *BTC* $\text{log2FC} = -4.299$). External statistical validation was not performed, as no independent validation cohort statistic was provided in the input context.
2. **Pathway and Ontology Evidence:** Standardized database annotations from Reactome (*Formation of the cornified envelope* R-HSA-6809371), GO (*Epidermis Development* GO:0008544; *Antimicrobial Humoral Response* GO:0019730), and KEGG (*IL-17 signaling pathway*).
3. **Protein Interaction and Network Evidence:** Interaction records from the STRING database demonstrating physical heterodimerization (S100A8/S100A9), structural cross-linking (SPRR2A/B/D/E, LCE3A/D), and cytokine-receptor complex formation (IL-36 family with IL1RAP).
4. **Disease, Expression, and Tissue-Specific Evidence:** Annotations from Human Protein Atlas (HPA), GTEx, and GWAS records confirming skin-enriched baseline expression of *SPRR*, *LCE*, and *DEFB* gene clusters and genetic risk associations for psoriasis.
5. **Published Literature Evidence:** Question-specific PubMed (e.g., PMID: [40560938], PMID: [38354028]) and Europe PMC records (e.g., [42216026]) contextualizing biomarker networks and therapeutic targets in psoriasis.

**Independence vs. Overlap of Sources:** Pathway annotations (GO/Reactome) and STRING PPI network records share underlying experimental literature and curated databases. Consequently, functional pathway enrichment and protein network clustering reflect consistent biological themes rather than independent statistical replications.

---

### 6. Limitations and Alternative Explanations

1. **Tissue Heterogeneity and Cell Composition Confounding:** Lesional psoriatic skin undergoes substantial structural remodeling, including pronounced epidermal acanthosis (hyperplasia) and immune cell infiltration (neutrophils, T cells, dendritic cells). Elevated bulk transcripts (e.g., *S100A12*, *CXCR2*, *SPRR2A*) may reflect an increased proportion of specific cell types in the biopsy sample rather than increased transcription per individual cell.
2. **Absence of External Statistical Validation:** External statistical validation was not performed on an independent patient cohort in this run. Although the statistical significance within the current dataset is high (FDR $< 10^{-60}$ for top candidates), true population generalizability requires evaluation in independent validation datasets.
3. **Association versus Causation Ambiguity:** Highly upregulated genes may represent secondary downstream reactive processes or counter-regulatory feedback loops rather than primary disease drivers. For example, the upregulation of the receptor antagonist *IL36RN* ($\text{log2FC} = 3.005$) is a compensatory feedback mechanism responding to excessive IL-36 signaling rather than an initiator of pathology.
4. **Lack of Clinical and Treatment Metadata:** The dataset lacks detailed clinical covariates such as patient PASI scores, disease duration, systemic biologic exposure, or topical treatment status. Prior anti-inflammatory treatment could suppress inflammatory pathways while leaving structural keratinocyte markers persistently altered.
5. **mRNA Abundance versus Functional Protein Degradation:** High RNA expression does not guarantee proportional protein accumulation or enzymatic activity. Lesional skin contains elevated serine proteases (*KLK13*, *TMPRSS11D*) and protease inhibitors (*PI3*, *SERPINB3/4*), indicating complex post-translational proteolytic regulation that cannot be fully captured by transcriptomics alone.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=0, external claims checked=0, external mismatches=0, status=passed.

Answer model API: Google Gemini / gemini-3.6-flash

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 91/100 selected items (records returned); cbioportal 91/100 selected items (records returned); chembl 11/100 selected items (partially returned; some queries failed); civic 4/100 selected items (records returned); clinicaltrials 40/100 selected items (records returned); clinvar 90/100 selected items (records returned); ensembl 44/100 selected items (partially returned; some queries failed); europepmc 848 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 83/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 76/100 selected items (records returned); humanbase 100/100 selected items (records returned); intact 79/100 selected items (records returned); mygene 100/100 selected items (records returned); omnipath 36/100 selected items (records returned); opentargets 90/100 selected items (records returned); pubmed 669 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 80/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 80/100 selected items (records returned)
Local databases: gutmgene 2/100 selected items (records returned); hmdb 25/100 selected items (records returned); string 78/100 selected items (records returned); trrust 17/100 selected items (records returned)
