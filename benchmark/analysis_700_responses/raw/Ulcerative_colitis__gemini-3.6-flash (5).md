# ulcerative colitis (UC) - gemini-3.6-flash

- Benchmark system: raw
- Repeat: 7
- Task type: DISEASE-STATE
- Tissue / sample source: colonic mucosal tissue
- Comparison or endpoint: ulcerative colitis versus healthy control
- Answer input cohort: Discovery/Core only
- Selected items: 100
- Input fields: gene name, effect size (log2FC/HR), P value, FDR
- E2seq Agent RAG: disabled
- Conversation memory: disabled
- Thinking mode: disabled
- Held-out validation data in prompt/RAG: no
- Model API: Google Gemini / gemini-3.6-flash
- Message SHA-256: 478acec7ab00f0e9bda085b6ecab7aa16a2bc8aa5cde3f2ba8fb71b2af94f79a
- Response HTTP status: 200
- Prompt tokens: 5426
- Completion tokens: 12818
- Reasoning tokens: 
- Total tokens: 18244
- API requests reported: 
- Elapsed seconds: 26.934
- Final benchmark system: raw; file rank 5/5; original repeat 7; model vendor: Google Gemini

---
### 1. Overall Biological Interpretation

The transcriptomic profile comparing colonic mucosal tissue from patients with active Ulcerative Colitis (UC) to healthy controls reveals a profound, reciprocal biological shift. The data demonstrate massive activation of mucosal inflammatory, antimicrobial, and matrix-remodeling cascades coupled with a widespread collapse of homeostatic epithelial functions, mature colonocyte metabolism, and mucosal barrier transport.

The upregulated gene program is dominated by three main coordinated processes:
1. **Neutrophil infiltration and innate alarm responses**: Driven by intense upregulation of CXC-family chemokines (`CXCL1`, `CXCL2`, `CXCL3`), alarmins (`S100A8`, `S100P`), and bacteriostatic/antimicrobial effectors (`LCN2`, `PI3`, `PLA2G2A`).
2. **Epithelial oxidative stress**: Anchored by extreme elevation of the hydrogen peroxide-generating complex `DUOX2` and its obligate maturation factor `DUOXA2`, supported by high nutrient transporter expression (`SLC6A14`).
3. **Extracellular matrix (ECM) destruction and tissue remodeling**: Led by matrix metalloproteinases (`MMP3`), tissue inhibitors (`TIMP1`), matricellular proteins (`TNC`, `CHI3L1`, `PDPN`), and stromal transcription factors (`PRRX1`).

Conversely, the downregulated gene program reflects the loss or functional suppression of the differentiated mucosal epithelium:
1. **Colonocyte bioenergetic failure**: Marked by severe depletion of key enzymes in short-chain fatty acid (SCFA) transport (`SLC16A1`/MCT1) and mitochondrial ketogenesis (`HMGCS2`), depriving colonocytes of their primary energy source (butyrate).
2. **Loss of absorptive and secretory transport**: Drastic reductions in water channels (`AQP8`, `AQP7`), amino acid and vitamin transporters (`SLC38A4`, `SLC23A1`, `SLC23A3`), and basolateral bile acid efflux machinery (`SLC51A`).
3. **Shutdown of epithelial xenobiotic detoxification and barrier maintenance**: Marked decrease in Phase I/II metabolic enzymes (`CYP2B6`, `UGT2A3`, `GBA3`), apical metalloproteases (`MEP1B`), and constitutive defensins (`DEFB1`).

Together, these changes capture the pathophysiological hallmark of active UC: loss of mature absorptive colonocytes (through detachment, necrosis, or dedifferentiation) accompanied by an intense recruitment of inflammatory granulocytes and remodeling stroma into the colonic mucosa.

---

### 2. Core Biological Programs

```
                       ULCERATIVE COLITIS MUCOSAL PATHOBIOLOGY
                                          │
         ┌────────────────────────────────┴────────────────────────────────┐
         ▼                                                                 ▼
UPREGULATED INFLAMMATORY CASCADE                                DOWNREGULATED EPITHELIAL PROGRAM
 ├─ Neutrophil Chemotaxis (CXCL1/2/3, S100A8)                    ├─ Colonocyte Energetics (HMGCS2, SLC16A1)
 ├─ Oxidative Burst (DUOX2, DUOXA2, SLC6A14)                     ├─ Solute/Water Transport (AQP8, SLC51A)
 └─ Matrix Degradation (MMP3, TIMP1, TNC)                        └─ Xenobiotic Metabolism (CYP2B6, UGT2A3)
```

#### Program 1: Neutrophil Recruitment and Innate Mucosal Host Defense
* **Direction**: Upregulated
* **Major Supporting Genes**: `CXCL1` (log2FC = +3.46, FDR = 1.15e-15), `CXCL2` (+2.80, FDR = 1.73e-11), `CXCL3` (+2.33, FDR = 2.51e-11), `S100A8` (+3.80, FDR = 4.43e-11), `LCN2` (+2.67, FDR = 1.37e-21), `PI3` (+2.21, FDR = 3.97e-19), `VNN1` (+3.20, FDR = 1.54e-15), `PLA2G2A` (+1.53, FDR = 1.36e-11).
* **Standardized Pathway**: KEGG: hsa04657 (IL-17 signaling pathway) / GO:0042119 (Neutrophil activation).
* **Biological Rationale**: Co-induction of `CXCL1`, `CXCL2`, and `CXCL3` creates a gradient for CXCR2+ neutrophil extravasation into the lamina propria. Concurrently, elevated `S100A8` (a component of calprotectin), `LCN2` (siderocalin), `PI3` (elafin), and `PLA2G2A` reflect mass activation of innate defense proteins aimed at containing luminal bacteria during epithelial barrier disruption.
* **Evidence Strength & Limitations**: *Evidence Strength*: Extremely high statistical significance across multiple independent gene families. *Limitations*: Driven largely by changes in tissue cell composition (granulocyte infiltration) rather than purely altered transcription per cell.

#### Program 2: Epithelial Oxidative Stress and Reactive Oxygen Species (ROS) Generation
* **Direction**: Upregulated
* **Major Supporting Genes**: `DUOX2` (log2FC = +4.67, FDR = 4.45e-26), `DUOXA2` (+2.89, FDR = 1.12e-10), `SLC6A14` (+4.85, FDR = 8.07e-39), `CHI3L1` (+4.59, FDR = 3.20e-11), `UBD` (+2.58, FDR = 1.01e-10).
* **Standardized Pathway**: Reactome: R-HSA-1247679 (ROS and RNS production in phagocytes and epithelia) / GO:0050664 (Hydrogen peroxide biosynthetic process).
* **Biological Rationale**: Dual oxidase 2 (`DUOX2`) and its essential maturation factor (`DUOXA2`) form a membrane-bound complex that transfers electrons to produce H₂O₂ at the mucosal surface. Its parallel upregulation with `SLC6A14` (which transports L-arginine and other amino acids) fuels mucosal oxidative stress and antimicrobial responses, which, when sustained, exacerbate epithelial mucosal injury.
* **Evidence Strength & Limitations**: *Evidence Strength*: `SLC6A14` and `DUOX2` exhibit two of the largest fold-changes in the entire dataset (> 25-fold induction). *Limitations*: Difficult to distinguish whether elevated ROS serves as an effective antimicrobial defense or a driver of collateral mucosal tissue destruction.

#### Program 3: Extracellular Matrix Degradation and Tissue Remodeling
* **Direction**: Upregulated
* **Major Supporting Genes**: `MMP3` (log2FC = +4.64, FDR = 5.40e-14), `TIMP1` (+1.97, FDR = 1.81e-17), `TNC` (+2.58, FDR = 2.51e-11), `PDPN` (+2.54, FDR = 1.75e-10), `PRRX1` (+2.91, FDR = 4.35e-16), `CHI3L1` (+4.59, FDR = 3.20e-11).
* **Standardized Pathway**: Reactome: R-HSA-1474228 (Degradation of the extracellular matrix) / GO:0030198 (Extracellular matrix organization).
* **Biological Rationale**: Upregulation of `MMP3` (Stromelysin-1) alongside its counter-regulatory inhibitor `TIMP1`, matricellular proteins Tenascin C (`TNC`) and Podoplanin (`PDPN`), and the mesenchymal transcription factor `PRRX1` points to extracellular matrix destruction, stromal cell activation, and wound repair mechanisms accompanying deep mucosal ulceration.
* **Evidence Strength & Limitations**: *Evidence Strength*: Massive effect sizes for `MMP3` and `CHI3L1`. *Limitations*: Bulk transcriptomics cannot distinguish functional matrix turnover supporting epithelial healing from chronic profibrotic mucosal remodeling.

#### Program 4: Impairment of Colonocyte Energetics and SCFA Oxidation
* **Direction**: Downregulated
* **Major Supporting Genes**: `HMGCS2` (log2FC = -3.45, FDR = 1.10e-16), `SLC16A1` (-2.38, FDR = 5.82e-21), `G6PC` (-1.52, FDR = 1.92e-17), `ACSF2` (-1.93, FDR = 9.78e-13), `LIPC` (-1.57, FDR = 1.54e-15).
* **Standardized Pathway**: KEGG: hsa00072 (Synthesis and degradation of ketone bodies) / GO:0015718 (Monocarboxylate transport).
* **Biological Rationale**: Healthy colonocytes rely on short-chain fatty acids (primarily butyrate) imported via `SLC16A1` (MCT1) and oxidized through mitochondrial pathways requiring `HMGCS2` (the rate-limiting enzyme of ketogenesis). Deep downregulation of both genes indicates a severe metabolic starvation state in the colonic epithelium, suppressing ATP generation required for barrier maintenance.
* **Evidence Strength & Limitations**: *Evidence Strength*: High statistical significance across independent transport and metabolic steps. *Limitations*: Highly dependent on mature colonocyte cell fraction in the biopsy; complete mucosal denudation will artificially lower these epithelial-specific transcripts.

#### Program 5: Loss of Mature Epithelial Solute Transport and Xenobiotic Metabolism
* **Direction**: Downregulated
* **Major Supporting Genes**: `AQP8` (log2FC = -4.42, FDR = 1.60e-13), `AQP7` (-2.32, FDR = 4.04e-20), `SLC51A` (-3.71, FDR = 1.54e-20), `SLC38A4` (-3.07, FDR = 4.70e-37), `SLC23A1` (-2.40, FDR = 8.89e-29), `MEP1B` (-2.99, FDR = 1.11e-22), `CYP2B6` (-2.78, FDR = 4.18e-13), `UGT2A3` (-2.68, FDR = 7.16e-11), `ABCG2` (-2.92, FDR = 1.11e-10), `DEFB1` (-2.31, FDR = 1.25e-10).
* **Standardized Pathway**: KEGG: hsa00980 (Metabolism of xenobiotics by cytochrome P450) / Reactome: R-HSA-5607761 (Transport of inorganic cations/anions and amino acids).
* **Biological Rationale**: Differentiation markers of mature absorptive colonocytes—including apical water channels (`AQP8`), basolateral bile acid transporters (`SLC51A`), brush-border metalloproteases (`MEP1B`), detoxification enzymes (`CYP2B6`, `UGT2A3`), and constitutive defenses (`DEFB1`)—are simultaneously lost. This represents the functional dismantling of mucosal absorptive and barrier capabilities.
* **Evidence Strength & Limitations**: *Evidence Strength*: High statistical consensus across multiple solute transport families. *Limitations*: Reflects a mixture of transcriptional gene repression and physical loss of the surface epithelial cell layer.

---

### 3. Key Genes and Interaction Modules

| Gene / Module | Direction | log2FC | FDR | Proposed Role in Core Biological Programs | Relationship Type to Other Genes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`SLC6A14`** | Upregulated | +4.85 | 8.07e-39 | Concentrative amino acid transporter; supplies metabolic substrates to inflamed mucosa and immune cells. | **Co-expression / Pathway co-membership** with `DUOX2` and inflammatory cytokine networks. |
| **`DUOX2` / `DUOXA2`** | Upregulated | +4.67 / +2.89 | 4.45e-26 / 1.12e-10 | Primary epithelial hydrogen peroxide-generating complex for mucosal oxidative burst. | **Direct physical interaction & functional obligate maturation pair** (DUOXA2 is required for DUOX2 surface transport and activity). |
| **`MMP3` / `TIMP1`** | Upregulated | +4.64 / +1.97 | 5.40e-14 / 1.81e-17 | Enzymatic degradation of stromal collagen and extracellular matrix during mucosal ulceration. | **Direct physical interaction** (protease-inhibitor stoichiometric complex) and **pathway co-membership**. |
| **`CHI3L1`** | Upregulated | +4.59 | 3.20e-11 | Chitinase-3-like 1 (YKL-40); drives mucosal tissue remodeling, cell survival, and macrophage activation. | **Co-expression** with stromal markers (`MMP3`, `TNC`, `PDPN`) in response to pro-inflammatory cytokines. |
| **`AQP8`** | Downregulated | -4.42 | 1.60e-13 | Apical water channel in mature colonocytes; loss directly accounts for defective fluid absorption and diarrhea. | **Co-expression / Common cell-type lineage marker** with `HMGCS2` and `SLC16A1` in mature colonocytes. |
| **`S100A8`** | Upregulated | +3.79 | 4.43e-11 | Calcium-binding alarmin subunit of heterodimeric Calprotectin (S100A8/A9); neutrophil biomarker. | **Direct physical interaction** (forms obligate heterodimer S100A8/A9) and **co-expression** with `CXCL1/2/3`. |
| **`HMGCS2`** | Downregulated | -3.45 | 1.10e-16 | Rate-limiting mitochondrial enzyme for ketogenesis; critical for colonocyte SCFA (butyrate) oxidation. | **Pathway co-membership & functional metabolic coupling** with `SLC16A1` (MCT1). |
| **`SLC51A`** | Downregulated | -3.71 | 1.54e-20 | Organic Solute Transporter Alpha (OST-alpha); mediates basolateral efflux of bile acids and steroids. | **Pathway co-membership** with epithelial xenobiotic and lipid transport machinery (`ABCG2`, `CYP2B6`). |
| **`CXCL1` / `CXCL2` / `CXCL3`** | Upregulated | +3.46 / +2.80 / +2.33 | 1.15e-15 / 1.73e-11 / 2.51e-11 | CXC chemokine triad that recruits CXCR2+ polymorphonuclear neutrophils into mucosal tissue. | **Paralogous gene family, regulatory co-expression** (common NF-κB activation), and **pathway co-membership**. |
| **`SLC16A1`** | Downregulated | -2.38 | 5.82e-21 | Monocarboxylate Transporter 1 (MCT1); primary apical/basal transporter for SCFA (butyrate) uptake. | **Functional metabolic coupling** with `HMGCS2` (supplies substrate for mitochondrial oxidation). |

---

### 4. Validation Priorities

#### Priority 1: Colonocyte Energetic Collapse via SLC16A1 / HMGCS2 Repression
* **Category**: Mechanistic hypothesis
* **Prioritization Rationale**: Essential for understanding whether epithelial metabolic starvation (loss of butyrate transport and ketogenesis) is a primary driver of non-healing mucosal ulcers in UC.
* **Current Dataset Evidence**: Deep, concurrent downregulation of the primary SCFA transporter `SLC16A1` (log2FC = -2.38, FDR = 5.82e-21) and the rate-limiting ketogenic enzyme `HMGCS2` (log2FC = -3.45, FDR = 1.10e-16).
* **External Evidence**: Published literature demonstrates that butyrate is the primary oxidative fuel for healthy colonocytes, and impaired SCFA oxidation correlates with disease activity in IBD.
* **Next Steps**: Conduct ex vivo metabolic flux experiments using $^{13}\text{C}$-labeled butyrate in patient-derived mucosal biopsies or human intestinal organoids under cytokine challenge (TNF-α/IL-17) to measure oxygen consumption rate (OCR) and ketogenesis pathways.
* **Conclusion State**: Supported hypothesis

#### Priority 2: Pathological Mucosal H₂O₂ Generation by the DUOX2 / DUOXA2 Complex
* **Category**: Interaction / network hypothesis
* **Prioritization Rationale**: Defines whether epithelial hydrogen peroxide generation acts as an injurious autocrine driver of mucosal damage.
* **Current Dataset Evidence**: Massive co-induction of `DUOX2` (log2FC = +4.67, FDR = 4.45e-26) and its mandatory maturation partner `DUOXA2` (log2FC = +2.89, FDR = 1.12e-10).
* **External Evidence**: DUOX2/DUOXA2 complex formation on the luminal plasma membrane is required for enzymatic stability. Human GWAS and transcriptomic studies link high DUOX2 expression to severe mucosal inflammation and microbial dysbiosis.
* **Next Steps**: Perform co-immunoprecipitation (Co-IP) and live-cell ROS imaging (e.g., HyPer biosensors) in epithelial organoid monolayers co-cultured with luminal bacteria or inflammatory cytokines, with and without siRNA knockdown of `DUOXA2`.
* **Conclusion State**: Supported hypothesis

#### Priority 3: Bulk Mucosal Deconvolution vs. Single-Cell Spatial Validation
* **Category**: Confounding or composition check
* **Prioritization Rationale**: Critical for determining whether downregulated epithelial transport signals represent cell-intrinsic gene silencing or physical denudation/loss of mature surface colonocytes.
* **Current Dataset Evidence**: Polarized expression signatures displaying intense loss of mature colonocyte markers (`AQP8`, `SLC51A`, `MEP1B`) alongside high signals from recruited immune cells (`S100A8`, `CXCL1`, `LOC100290146|IGH...`).
* **External Evidence**: Single-cell RNA sequencing (scRNA-seq) datasets of active UC mucosa confirm dramatic shifting in epithelial subpopulation ratios (e.g., loss of mature absorptive colonocytes and expansion of inflammatory monocytes/neutrophils).
* **Next Steps**: Perform multiplex spatial transcriptomics (e.g., Xenium or Visium HD) or single-cell profiling on paired inflamed and non-inflamed UC biopsies to quantify per-cell transcript density versus total cell population counts.
* **Conclusion State**: Established evidence

#### Priority 4: MMP3 / TIMP1 Proteolytic Imbalance as a Therapeutic Target for Ulceration
* **Category**: Therapeutic target
* **Prioritization Rationale**: Severe matrix destruction drives clinical complications in UC (e.g., deep mucosal tears, toxic megacolon, stricturing/fibrosis).
* **Current Dataset Evidence**: Enormous induction of `MMP3` (log2FC = +4.64, FDR = 5.40e-14), which substantially outpaces the induction of its tissue inhibitor `TIMP1` (log2FC = +1.97, FDR = 1.81e-17).
* **External Evidence**: High MMP3 levels in mucosal tissue correlate with non-response to anti-TNF agents and endoscopic severity in IBD. Historically, broad-spectrum MMP inhibitors failed due to toxicity, requiring selective target validation.
* **Next Steps**: Validate protein-level activity using fluorogenic cleavage assays in colonic explant cultures treated with selective MMP-3 inhibitors or neutralizing monoclonal antibodies to assess mucosal integrity.
* **Conclusion State**: Exploratory hypothesis

#### Priority 5: Epithelial-to-Inflammatory Transcriptomic Ratio as a Biomarker for Mucosal Healing
* **Category**: Biomarker
* **Prioritization Rationale**: Objective transcriptomic markers of mucosal healing are needed to guide clinical management beyond subjective endoscopic scoring.
* **Current Dataset Evidence**: High statistical discrimination (FDR values down to $10^{-39}$) between elevated inflammatory markers (`SLC6A14`, `DUOX2`, `CXCL1`) and depleted epithelial markers (`AQP8`, `SLC38A4`, `HMGCS2`).
* **External Evidence**: Mucosal transcriptomic signatures in prospective pediatric and adult IBD cohorts (e.g., RISK and PROTECT studies) correlate with sustained corticosteroid-free remission.
* **Next Steps**: Formulate a composite transcriptomic index (e.g., $[\text{DUOX2} + \text{SLC6A14} + \text{CXCL1}] / [\text{AQP8} + \text{HMGCS2} + \text{SLC16A1}]$) and evaluate its predictive performance for endoscopic mucosal healing in pre- and post-treatment clinical trial biopsies.
* **Conclusion State**: Supported hypothesis

---

### 5. Evidence Grounding

```
                               EVIDENCE GROUNDING MATRIX
 ┌─────────────────────────┬─────────────────────────────────────────────────────────────┐
 │ Evidence Category       │ Applied Findings in Current Analysis                        │
 ├─────────────────────────┼─────────────────────────────────────────────────────────────┤
 │ Direct Input Data       │ Fold-change and FDR values (e.g., SLC6A14, DUOX2, AQP8)     │
 │ Pathway / Ontology      │ KEGG IL-17 signaling, Reactome ECM degradation, Ketogenesis  │
 │ Protein Interaction     │ DUOX2-DUOXA2 complex, MMP3-TIMP1 pair, S100A8/A9 dimer     │
 │ Disease-Association     │ S100A8 (Calprotectin) elevation in active UC mucosa         │
 │ Cell/Tissue-Specific    │ AQP8/HMGCS2 (absorptive colonocytes), CXCL1/S100A8 (granulocyte)│
 └─────────────────────────┴─────────────────────────────────────────────────────────────┘
```

* **Direct Input Dataset Evidence**: Differential expression values directly support the primary reciprocal pattern (e.g., `SLC6A14` log2FC = +4.85, FDR = 8.07e-39 vs. `AQP8` log2FC = -4.42, FDR = 1.60e-13). Unannotated or probeset-specific entries (such as `PROBE_241592_PM_at` and `PROBE_227140_PM_at`) represent **insufficient evidence** for functional interpretation without sequence re-annotation.
* **Pathway and Protein-Interaction Evidence**: Functional linkages between `DUOX2` and `DUOXA2` are grounded in established biochemistry showing obligate heterodimerization for ROS transport. Similarly, `MMP3` and `TIMP1` represent a classic protease-inhibitor pair, while `CXCL1`, `CXCL2`, and `CXCL3` form a paralogous chemokine module acting on the CXCR2 receptor. These pathways derive from standardized ontology databases (KEGG/Reactome).
* **Cell/Tissue-Specific Evidence**: Tissue localization of `AQP8` and `HMGCS2` to mature absorptive colonocytes, and `S100A8` to polymorphonuclear neutrophils, is supported by established cell-atlas databases.
* **Addressing Conflicting Evidence**: A notable internal divergence exists within mucosal defense genes: `S100A8` (+3.79), `LCN2` (+2.67), and `PI3` (+2.21) are strongly upregulated, whereas human beta-defensin 1 (`DEFB1`, log2FC = -2.31, FDR = 1.25e-10) is strongly downregulated. This conflict is reconciled by cell-type specificity: `DEFB1` is a constitutive gene expressed by healthy mature colonocytes (which are depleted), whereas `S100A8`, `LCN2`, and `PI3` are inducible alarmins expressed by infiltrating granulocytes or stress-induced crypt cells.
* **Redundancy of Evidence**: Upregulation of `CXCL1`, `CXCL2`, and `CXCL3` should not be interpreted as three independent pathological mechanisms. These genes sit in the same genomic locus, share common upstream transcription factors (NF-κB), and act on the same receptor (CXCR2), representing a single redundant biological module.

---

### 6. Limitations and Alternative Explanations

1. **Cell-Composition Confounding (Shift in Cell Fractions)**: Bulk tissue transcriptomics averages signals across mucosal epithelial, stromal, and immune cell populations. Downregulation of `AQP8`, `HMGCS2`, `SLC51A`, and `MEP1B` may simply reflect the loss of surface epithelial cells (erosion/ulceration) rather than transcriptional repression within intact cells. Conversely, high `S100A8` and `CXCL1` signals predominantly reflect the physical presence of infiltrating neutrophils.
2. **Inflammation-Nonspecific Signals**: Core upregulated programs (e.g., `CXCL1/2/3`, `MMP3`, `LCN2`, `S100A8`) are general features of active mucosal inflammation and are similarly observed in Crohn's disease, infectious colitis, or ischemic colitis. They represent active mucosal injury rather than disease-specific etiologic drivers unique to Ulcerative Colitis.
3. **Lack of Clinical and Treatment Covariates**: The dataset lacks metadata regarding patient treatment history (e.g., systemic corticosteroids, anti-TNF biologics, or 5-ASA compounds), disease duration, or endoscopic Mayo scores. Medical therapies (e.g., immunosuppressants) can alter mucosal gene profiles, potentially confounding comparison with healthy controls.
4. **Association vs. Causation Ambiguity**: Highly downregulated metabolic genes (e.g., `HMGCS2`, `SLC16A1`) cannot be definitively identified as causal drivers of tissue injury. Energy depletion could be an executioner or downstream consequence of mucosal damage, cytokine exposure (TNF-α, IFN-γ), and localized hypoxia.
5. **Broad and Redundant Pathway Signals**: Broad enrichment in pathways such as "immune response" or "transport" can mask specific molecular drivers. For example, multiple probes mapping to immunoglobulin heavy chains (`LOC100290146|IGHV4-31|IGHM|IGHG1|IGH`) reflect secondary plasma cell expansion rather than primary mucosal pathology.
