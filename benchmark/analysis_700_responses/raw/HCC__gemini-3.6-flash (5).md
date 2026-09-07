# hepatocellular carcinoma (HCC) - gemini-3.6-flash

- Benchmark system: raw
- Repeat: 7
- Task type: PROGNOSIS
- Tissue / sample source: liver tumor tissue
- Comparison or endpoint: overall survival (OS)
- Answer input cohort: Discovery/Core only
- Selected items: 100
- Input fields: gene name, effect size (log2FC/HR), P value, FDR
- E2seq Agent RAG: disabled
- Conversation memory: disabled
- Thinking mode: disabled
- Held-out validation data in prompt/RAG: no
- Model API: Google Gemini / gemini-3.6-flash
- Message SHA-256: be503ca72a7bcd2f0eb88c8049c4935f5ef704fb40bd5170c65ca64b33a1d716
- Response HTTP status: 200
- Prompt tokens: 3774
- Completion tokens: 9667
- Reasoning tokens: 
- Total tokens: 13441
- API requests reported: 
- Elapsed seconds: 24.538
- Final benchmark system: raw; file rank 5/5; original repeat 7; model vendor: Google Gemini

---
### 1. Overall Biological Interpretation

This transcriptomic prognosis dataset evaluates overall survival (OS) in hepatocellular carcinoma (HCC) using liver tumor tissue samples. The statistical results demonstrate a striking pattern: nearly all top-ranked features associated with poor OS present extremely high hazard ratios ($\text{HR} \approx 5.18 \times 10^{21}$ or $1.51 \times 10^6$ to $6.63 \times 10^{13}$) accompanied by nominal $P = 0$ and $\text{FDR} = 0$. Similarly, a small subset of features exhibits extreme protective associations ($\text{HR} \approx 1.93 \times 10^{-22}$). 

Biologically, despite the obvious numerical artifacts (such as complete statistical separation in Cox modeling due to zero-count features or unnormalized expression subsets), the gene set converges on four dominant oncogenic axes characteristic of highly aggressive, poorly differentiated HCC:

1. **Reactivation of Oncofetal and Lineage-Unfaithful Transcription Factors**: Overexpression of developmental transcription factors (`OTX2`, `FOXR2`, `FOXI1`) indicates dedifferentiation and reactivation of embryonic gene expression programs that drive stemness and aggressive tumor phenotypes.
2. **Mitogenic and Anabolic Receptor Signaling Rewiring**: Upregulation of `IRS4` (a key activator of the PI3K/AKT axis), `SLC1A6` (a high-affinity glutamate transporter), and ectopic hormones (`CGB2`, `CRH`) points to altered growth factor sensitivity, neuroendocrine signaling, and metabolic adaptation under tumor microenvironmental stress.
3. **Non-Coding RNA Dysregulation and RNA Processing Machinery**: Widespread hazard association among microRNAs (`MIR182`), small nuclear RNA pseudogenes/snRNAs (`RNU6-1134P`, `RNU1-139P`, `RNU4-72P`), signal recognition particle RNA (`Metazoa_SRP`), and long non-coding RNAs (`LINC00454`, `LINC01672`, `XKR4-AS1`) reflects severe disruption of RNA splicing, post-transcriptional silencing, and nuclear non-coding RNA architecture.
4. **Widespread Deregulation of Pseudogenes Derived from Key Cancer Pathways**: A high proportion of the top risk-associated features consists of processed pseudogenes (`SNAI1P1`, `NF1P7`, `ALDH7A1P3`, `MORF4L1P6`, `HMGB3P27`, `S100A7P1`, `PLA2G10P1`). This signature suggests global epigenetic derepression and genomic instability in high-risk tumors, potentially mirroring the dysregulation of their parental pathways (e.g., EMT, RAS signaling, and chromatin remodeling).

---

### 2. Core Biological Programs

```
                    ┌───────────────────────────────────────────────────────────┐
                    │      Aggressive HCC Transcriptomic Risk Landscape         │
                    └─────────────────────────────┬─────────────────────────────┘
                                                  │
         ┌──────────────────────┬─────────────────┴────────────────┬──────────────────────┐
         ▼                      ▼                                  ▼                      ▼
┌─────────────────┐   ┌───────────────────┐              ┌───────────────────┐  ┌───────────────────┐
│ Program 1:      │   │ Program 2:        │              │ Program 3:        │  │ Program 4:        │
│ Dedifferentiation│   │ Anabolic Signaling│              │ Ectopic GPCR &    │  │ ncRNA & Splicing  │
│ & TF Activation │   │ & Glutamate Axis  │              │ Stress Axis       │  │ Instability       │
│ (OTX2, FOXR2,   │   │ (IRS4, SLC1A6,    │              │ (CRH, CGB2,       │  │ (MIR182, RNU6,    │
│  FOXI1)         │   │  CGB2)            │              │  OR5M10)          │  │  LINC00454)       │
└─────────────────┘   └───────────────────┘              └───────────────────┘  └───────────────────┘
```

#### Program 1: Oncofetal Dedifferentiation and Lineage Transcription Factor Activation
* **Direction / Association**: High risk (Associated with poor overall survival; $\text{HR} > 1$).
* **Major Supporting Genes**: `OTX2`, `FOXR2`, `FOXI1`.
* **Standardized Pathway**: GO:0001077 (transcriptional regulation, DNA-templated) / Reactome R-HSA-5663205 (Inactivation of GATA3 and FOXP3 transcription factor networks in cancer / Developmental Biology).
* **Biological Rationale**: Primary hepatocytes normally maintain a differentiated metabolic profile driven by HNF1A, HNF4A, and FOXA factors. Ectopic expression of neural/embryonic transcription factors such as `OTX2` (Orthodenticle Homeobox 2) and `FOXR2` (Forkhead Box R2) signifies lineage unfaithfulness, acquisition of stem cell-like traits, and loss of hepatic differentiation. `FOXI1` further reflects dysregulated forkhead box signaling, which promotes tumor invasiveness.
* **Evidence Strength & Limitations**: *Moderate-to-Strong biological rationale*, supported by published cellular models of HCC dedifferentiation. *Limitation*: Extreme statistical HR values ($\text{HR} = 5.18 \times 10^{21}$) indicate mathematical overflow/separation rather than a true multi-billion-fold hazard increase.

#### Program 2: Hyperactive Anabolic Signaling and Amino Acid Metabolic Transport
* **Direction / Association**: High risk (Associated with poor overall survival; $\text{HR} > 1$).
* **Major Supporting Genes**: `IRS4`, `SLC1A6`.
* **Standardized Pathway**: KEGG hsa04910 (Insulin signaling pathway) / Reactome R-HSA-352230 (Amino acid transport across plasma membrane).
* **Biological Rationale**: `IRS4` (Insulin Receptor Substrate 4) acts as a constitutive activator of the PI3K/AKT/mTOR signaling axis, bypassing classical receptor down-regulation mechanisms. Co-activation of `SLC1A6` (EAAT4, Excitatory Amino Acid Transporter 4) facilitates high-affinity glutamate and d-aspartate influx, supplying nitrogen and carbon skeletons for central carbon metabolism, glutathione synthesis, and nucleotide biosynthesis to sustain rapid tumor growth.
* **Evidence Strength & Limitations**: *Strong mechanistic rationale* linking growth factor signaling to metabolic rewiring in liver cancer. *Limitation*: Protein-level validation is absent in transcriptomic cross-sections, and baseline liver metabolic background can obscure cell-type-specific uptake.

#### Program 3: Ectopic Neuroendocrine and Stress Response Signaling
* **Direction / Association**: High risk (Associated with poor overall survival; $\text{HR} > 1$).
* **Major Supporting Genes**: `CRH`, `CGB2`, `OR5M10`, `VN1R96P`.
* **Standardized Pathway**: KEGG hsa04080 (Neuroactive ligand-receptor interaction) / Reactome R-HSA-372790 (GPCR downstream signaling).
* **Biological Rationale**: Severe hepatic malignancy is frequently accompanied by neuroendocrine transdifferentiation. Upregulation of `CRH` (Corticotropin-Releasing Hormone) suggests locally mediated stress signaling, immunosuppression, or autocrine GPCR stimulation. Ectopic secretion of gonadotropin components (`CGB2`) and aberrant expression of olfactory/vomeronasal receptors (`OR5M10`, `VN1R96P`) reflect derepressed GPCR networks that can signal through $G_{\alpha s}$ or $G_{\alpha q}$ to promote cell survival.
* **Evidence Strength & Limitations**: *Moderate pathway co-membership*. *Limitation*: Olfactory receptor genes and pseudogenes often exhibit low/spurious read counts in RNA-seq datasets, predisposing them to extreme artifactual hazard ratios under standard unpenalized Cox modeling.

#### Program 4: MicroRNA Dysregulation and Spliceosomal RNA Instability
* **Direction / Association**: High risk (Associated with poor overall survival; $\text{HR} > 1$).
* **Major Supporting Genes**: `MIR182`, `RNU6-1134P`, `RNU1-139P`, `RNU4-72P`, `RN7SKP270`, `Metazoa_SRP`, `LINC00454`.
* **Standardized Pathway**: KEGG hsa05206 (MicroRNAs in cancer) / Reactome R-HSA-72163 (mRNA Splicing - Major Pathway).
* **Biological Rationale**: `MIR182` is a well-established oncogenic microRNA (miR-182) in liver cancer that silences tumor suppressors (e.g., FOXO1, MTSS1) to accelerate cell proliferation and epithelial-mesenchymal transition (EMT). Concurrently, widespread altered levels of small nuclear non-coding RNAs (snRNAs involved in the U1, U4, and U6 spliceosomal machinery) and 7SK snRNA pseudogenes indicate severe spliceosomal stress and disruption of post-transcriptional gene regulation.
* **Evidence Strength & Limitations**: *High literature support* for `MIR182`. *Limitation*: Total RNA-seq without specialized small-RNA sequencing often captures snRNA/microRNA fragments suboptimally, increasing measurement noise.

---

### 3. Key Genes and Interaction Modules

```
                    ┌─────────────────────────────────────────┐
                    │      Key Oncogenic Hubs & Modules       │
                    └────────────────────┬────────────────────┘
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
 ┌───────────────┐               ┌───────────────┐                ┌───────────────┐
 │ Growth/PI3K   │               │ Lineage TFs   │                │ MicroRNA/ncRNA│
 │  IRS4 (HR≫1)  │               │  OTX2 (HR≫1)  │                │  MIR182 (HR≫1)│
 │  SLC1A6 (HR≫1)│               │  FOXR2 (HR≫1) │                │  RNU6 (HR≫1)  │
 └───────┬───────┘               └───────┬───────┘                └───────┬───────┘
         │                               │                                │
         └───────────────────────┬───────┴────────────────────────────────┘
                                 ▼
                     ┌───────────────────────┐
                     │ Epigenetic/Pseudogene │
                     │ Dysregulation         │
                     │  SNAI1P1, NF1P7       │
                     └───────────────────────┘
```

| Gene Symbol | Statistical Direction & HR | Proposed Biological Role | Proposed Inter-Gene Relationship |
| :--- | :--- | :--- | :--- |
| **`IRS4`** | High Risk ($\text{HR} = 5.18 \times 10^{21}$) | Constitutive signaling adapter linking RTKs to PI3K/AKT activation. | **Pathway co-membership**: Acts upstream of AKT/mTOR networks; co-expressed with metabolic regulators (`SLC1A6`). |
| **`OTX2`** | High Risk ($\text{HR} = 5.18 \times 10^{21}$) | Oncofetal homeobox transcription factor promoting neural/stemness traits. | **Regulatory interaction**: Acts as an upstream master transcriptional regulator of lineage-unfaithful genes; pathway co-membership with `FOXR2`. |
| **`FOXR2`** | High Risk ($\text{HR} = 5.18 \times 10^{21}$) | Forkhead transcription factor driver of oncogenic proliferation and MYC stabilization. | **Pathway co-membership**: Co-operates with `OTX2` and `FOXI1` in an ectopic developmental transcriptional program. |
| **`MIR182`** | High Risk ($\text{HR} = 5.18 \times 10^{21}$) | Oncogenic microRNA inhibiting negative regulators of cell cycle and EMT. | **Regulatory interaction**: Post-transcriptional repression of target tumor suppressor mRNAs (indirect regulation of FOXO factors). |
| **`SLC1A6`** | High Risk ($\text{HR} = 5.18 \times 10^{21}$) | Excitatory amino acid transporter supplying glutamate for tumor cell metabolism. | **Pathway co-membership**: Functional synergy with `IRS4`-driven anabolic signaling to fuel nutrient uptake. |
| **`CRH`** | High Risk ($\text{HR} = 1.51 \times 10^{6}$) | Stress-response neuropeptide driving autocrine/paracrine GPCR activation. | **Indirect relationship**: Synergizes with ectopic GPCR signaling (`OR5M10`) to activate cAMP/PKA or $IP_3$/DAG pathways. |
| **`FOXI1`** | High Risk ($\text{HR} = 6.63 \times 10^{13}$) | Forkhead family TF involved in epithelial differentiation and ion transport regulation. | **Co-expression**: Expressed concurrently with `FOXR2` and `OTX2` during tumor lineage destabilization. |
| **`SNAI1P1`** | High Risk ($\text{HR} = 5.18 \times 10^{21}$) | Processed pseudogene derived from the master EMT regulator *SNAI1*. | **Indirect / Putative relationship**: May act as a competitive endogenous RNA (ceRNA) sponge for miR-182 or reflect genomic locus hypomethylation alongside parental *SNAI1*. |
| **`NF1P7`** | High Risk ($\text{HR} = 3.63 \times 10^{7}$) | Pseudogene corresponding to Neurofibromin 1 (*NF1* tumor suppressor). | **Indirect relationship**: Serves as a genomic marker of broad epigenetic instability; pathway co-membership with RAS/MAPK signaling locus. |
| **`CENPVL3`** | Protective ($\text{HR} = 1.93 \times 10^{-22}$) | Centromere protein V-like 3 locus (pseudogene/non-coding transcript). | **Co-expression**: Strongly anti-correlated with aggressive tumor subclones; likely reflects a low-count feature absent in high-risk tumors. |

*Note: All listed relationships represent pathway co-membership, regulatory, co-expression, or indirect relationships. No direct physical protein-protein interaction is claimed between these candidates based solely on these transcriptomic associations.*

---

### 4. Validation Priorities

```
  Priority 1: Statistical Firth Correction (Confounding Check)
  └─► Priority 2: IRS4-PI3K Signal Axis (Mechanistic Hypothesis)
      └─► Priority 3: MIR182 Biomarker Panel (Biomarker)
          └─► Priority 4: OTX2/FOXR2 Lineage Plasticity (Mechanistic Hypothesis)
              └─► Priority 5: SLC1A6 Glutamate Vulnerability (Therapeutic Target)
```

#### Priority 1: Re-estimation of Cox Proportional Hazards using Firth's Penalized Likelihood
* **Category**: Confounding or composition check.
* **Why Prioritize**: The presence of infinite/extreme hazard ratios ($\text{HR} \sim 10^{21}$ and $10^{-22}$) with nominal $P=0$ indicates mathematical model instability (complete separation / Hauck-Donner effect), likely driven by zero-count features in specific patient subgroups.
* **Current Dataset Evidence**: Extreme magnitude of HR values across diverse biotypes (pseudogenes, protein-coding, non-coding RNAs).
* **External Evidence**: Standard statistical literature establishes that Cox regression fails under complete separation, producing inflated parameters.
* **Next Validation Step**: Re-analyze raw count data using Firth’s penalized Cox regression ($L_1$/$L_2$ regularization) after filtering out features with low variance or high zero-inflation.
* **Certainty Level**: **Established evidence** (Statistical methodology requirement).

#### Priority 2: In Vitro and In Vivo Functional Characterization of IRS4-Driven PI3K/AKT Activation
* **Category**: Mechanistic hypothesis.
* **Why Prioritize**: `IRS4` is one of the few well-characterized protein-coding oncogenes in the risk set capable of directly driving mitogenic proliferation in HCC.
* **Current Dataset Evidence**: High risk association ($\text{HR} > 1$, $P = 0$).
* **External Evidence**: Literature demonstrates IRS4 can constitutively activate PI3K/AKT signaling independently of upstream insulin receptor engagement in breast and lung cancers.
* **Next Validation Step**: Knockdown (shRNA/CRISPRi) and overexpression of `IRS4` in human HCC cell lines (e.g., HepG2, Huh7), followed by western blot for phospho-AKT (Ser473)/phospho-S6 and cell proliferation assays.
* **Certainty Level**: **Supported hypothesis**.

#### Priority 3: Clinical Biomarker Evaluation of Circulating/Tissue miR-182 (`MIR182`)
* **Category**: Biomarker.
* **Why Prioritize**: MicroRNA-182 is stable in circulating fluids and tissue, making it a viable candidate for non-invasive prognostic stratification.
* **Current Dataset Evidence**: Strong adverse prognostic signal ($\text{HR} > 1$, $P = 0$).
* **External Evidence**: Independent TCGA-LIHC and ICGC cohorts validate miR-182 overexpression as a predictor of vascular invasion, early recurrence, and poor overall survival in HCC.
* **Next Validation Step**: Quantitative RT-qPCR measurement of miR-182 in serum samples from a prospectively collected validation cohort of HCC patients undergoing surgical resection or systemic therapy.
* **Certainty Level**: **Supported hypothesis**.

#### Priority 4: Investigation of OTX2 and FOXR2 as Drivers of HCC Lineage Plasticity and Stemness
* **Category**: Mechanistic hypothesis.
* **Why Prioritize**: Simultaneous risk association of `OTX2` and `FOXR2` points to oncofetal transcription factor reactivation driving poor differentiation.
* **Current Dataset Evidence**: Both genes demonstrate high risk associations ($\text{HR} > 1$, $P = 0$).
* **External Evidence**: FOXR2 promotes ETS transcriptional programs and MYC stabilization in CNS malignancies; OTX2 drives medulloblastoma proliferation and stemness.
* **Next Validation Step**: Perform ATAC-seq and ChIP-seq in $OTX2$/$FOXR2$-high liver cancer stem cell models to map open chromatin landscapes and downstream target genes.
* **Certainty Level**: **Exploratory hypothesis**.

#### Priority 5: Targeting SLC1A6-Mediated Glutamate Transport as a Metabolic Vulnerability
* **Category**: Therapeutic target.
* **Why Prioritize**: Upregulation of glutamate transporter `SLC1A6` suggests metabolic dependency on exogenous glutamate/aspartate for tumor survival.
* **Current Dataset Evidence**: High risk association ($\text{HR} > 1$, $P = 0$).
* **External Evidence**: Glutamate pathway inhibition sensitizes liver cancer cells to oxidative stress and ferroptosis.
* **Next Validation Step**: Test small-molecule inhibitors of EAAT transporters (e.g., TBOA analogs) or glutaminase inhibitors (CB-839) in $SLC1A6$-overexpressing HCC organoids under nutrient-restricted conditions.
* **Certainty Level**: **Exploratory hypothesis**.

---

### 5. Evidence Grounding

```
                                    ┌─────────────────────────────────────────────────────────┐
                                    │               Evidence Grounding Matrix                 │
                                    └────────────────────────────┬────────────────────────────┘
                                                                 │
         ┌──────────────────────────────┬────────────────────────┴──────────────────────────────┬──────────────────────────────┐
         ▼                              ▼                                                       ▼                              ▼
┌─────────────────┐            ┌─────────────────┐                                     ┌─────────────────┐            ┌─────────────────┐
│ Direct Dataset  │            │ Pathway/Ontology│                                     │ Literature      │            │ Clinical/Drug   │
│ Evidence        │            │ Evidence        │                                     │ Evidence        │            │ Evidence        │
├─────────────────┤            ├─────────────────┤                                     ├─────────────────┤            ├─────────────────┤
│ • HR > 1 for    │            │ • GO: TF Activity│                                     │ • MIR182 in HCC │            │ • Insufficient  │
│   IRS4, OTX2,   │            │ • KEGG: Insulin │                                     │ • IRS4-PI3K Axis│            │   direct drug   │
│   MIR182        │            │   Signaling     │                                     │ • FOXR2 in      │            │   target        │
│ • P = 0, FDR=0  │            │ • Reactome:     │                                     │   Oncogenesis   │            │   evidence in   │
│ • HR < 1 for    │            │   RNA Metabolism│                                     │                 │            │   current data  │
│   CENPVL3       │            │                 │                                     │                 │            │                 │
└─────────────────┘            └─────────────────┘                                     └─────────────────┘            └─────────────────┘
```

#### Detailed Evidence Categorization

* **Direct Evidence from Input Dataset**:
  * Strong statistical association ($P=0$, $\text{FDR}=0$) for 100 features.
  * Risk features ($\text{HR} > 1$): `IRS4`, `OTX2`, `FOXR2`, `FOXI1`, `SLC1A6`, `CRH`, `CGB2`, `MIR182`, `SNAI1P1`, `NF1P7`, etc.
  * Protective features ($\text{HR} < 1$): `CENPVL3`, `LOC105372753`, `RP11-506K19.2`.
* **Pathway / Ontology Evidence**:
  * GO:0001077 (Transcription factor activity) links `OTX2`, `FOXR2`, `FOXI1`.
  * KEGG hsa04910 (Insulin signaling) links `IRS4`.
  * Reactome R-HSA-352230 (Amino acid transport) links `SLC1A6`.
  * KEGG hsa05206 (MicroRNAs in cancer) links `MIR182`.
* **Protein Interaction or Regulatory Evidence**:
  * Literature-derived PPI evidence connects IRS4 to PIK3R1/PIK3CA complex (*overlapping with pathway evidence*).
  * miR-182 target interaction networks target *FOXO1* and *MTSS1* (independent literature evidence).
* **Disease-Association Evidence**:
  * TCGA-LIHC and ICGC public data show elevated expression of `MIR182`, `IRS4`, and `FOXR2` in high-grade liver carcinomas compared to non-tumor liver tissue.
* **Drug or Therapeutic Evidence**:
  * **Insufficient Evidence**: The present dataset provides **no direct therapeutic response or drug sensitivity data**. While PI3K/mTOR inhibitors and glutamate transport antagonists exist, their efficacy in $IRS4$-high or $SLC1A6$-high HCC cannot be inferred from survival associations alone.

---

### 6. Limitations and Alternative Explanations

1. **Numerical Separation and Statistical Overflow Artifacts**:
   * *Issue*: Hazard ratios reaching $5.18 \times 10^{21}$ coupled with $P=0.0$ are hallmark indicators of **complete separation** in unpenalized Cox proportional hazards models. This occurs when a transcript has zero expression in one survival outcome group (e.g., long-term survivors) and positive expression in another.
   * *Resolution*: Re-estimate hazard ratios using Firth's penalized Cox regression or regularized Cox models ($L_1$/$L_2$ penalty) to obtain biologically realistic effect estimates.

2. **Dominance of Pseudogenes and Unmapped Transcripts**:
   * *Issue*: A substantial portion of top risk features consists of pseudogenes (`SNAI1P1`, `NF1P7`, `ALDH7A1P3`, `HMGB3P27`, `PLA2G10P1`) and unmapped Ensembl IDs (`ENSG00000283631`). These may reflect global genomic demethylation, open-chromatin noise, or mapping alignment ambiguity rather than functional protein-coding driver mechanisms.
   * *Resolution*: Perform locus-specific long-read RNA sequencing (PacBio/Nanopore) to verify actual transcription of full-length pseudogene transcripts versus mapping cross-talk with parental loci.

3. **Cellular Composition and Microenvironmental Confounding**:
   * *Issue*: Expression of neuronal/neuroendocrine markers (`CRH`, `OTX2`, `SLC1A6`) could stem from changes in tumor microenvironment composition—such as nerve fiber innervation, neuroendocrine transdifferentiation, or infiltrating non-parenchymal cells—rather than intrinsic hepatocellular alterations.
   * *Resolution*: Analyze single-cell RNA-seq (scRNA-seq) or spatial transcriptomics datasets of HCC to localize expression of `CRH`, `OTX2`, and `SLC1A6` strictly to malignant cytokeratin-positive hepatocytes versus stromal elements.

4. **Unadjusted Clinical Covariates**:
   * *Issue*: The univariate prognostic signal does not account for critical clinical confounders, including tumor stage (BCLC / TNM stage), underlying liver disease etiology (HBV, HCV, MASLD), Child-Pugh liver function score, or surgical resection status.
   * *Resolution*: Perform multivariate Cox proportional hazards modeling adjusting for age, sex, BCLC stage, Child-Pugh class, and etiology.

5. **Nonspecific Epigenetic Derepression Noise**:
   * *Issue*: Widespread reactivation of developmental transcription factors (`OTX2`, `FOXR2`), ectopic hormones (`CGB2`), and olfactory receptors (`OR5M10`, `OR2M7`) may collectively reflect generic epigenetic failure (e.g., loss of H3K27me3 or DNA hypomethylation) in terminally end-stage tumors, rather than independent oncogenic drivers.
   * *Resolution*: Integrate DNA methylation (Illumina EPIC array) and histone modification data (ChIP-seq for H3K27me3/H3K4me3) to test whether these features co-localize within globally hypomethylated genomic blocks.
