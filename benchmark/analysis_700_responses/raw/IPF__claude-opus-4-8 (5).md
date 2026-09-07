# idiopathic pulmonary fibrosis (IPF) - claude-opus-4-8

- Benchmark system: raw
- Repeat: 7
- Task type: PROGNOSIS
- Tissue / sample source: lung tissue
- Comparison or endpoint: all-cause mortality
- Answer input cohort: Discovery/Core only
- Selected items: 100
- Input fields: gene name, effect size (log2FC/HR), P value, FDR
- E2seq Agent RAG: disabled
- Conversation memory: disabled
- Thinking mode: disabled
- Held-out validation data in prompt/RAG: no
- Model API: Anthropic / claude-opus-4-8
- Message SHA-256: d9fe74e971569d03f1ace047ce334e08d788b93d2057913b4d42b34da6d57d2f
- Response HTTP status: 200
- Prompt tokens: 
- Completion tokens: 
- Reasoning tokens: 
- Total tokens: 
- API requests reported: 
- Elapsed seconds: 121.743
- Final benchmark system: raw; file rank 5/5; original repeat 7; model vendor: Anthropic

---
# Multidimensional Interpretation of Transcriptomic Prognostic Analysis in Idiopathic Pulmonary Fibrosis

## Critical Data Quality Assessment

**The dataset contains severe technical anomalies that invalidate statistical interpretation:**

- Multiple features show mathematically impossible hazard ratios (HR ~10²¹ or ~10⁻²²)
- P-values of exactly 0 are computationally implausible
- Control probes (CONTROL_A_33_P3222196, CONTROL_A_33_P3345409) appear as top hits
- Several features are hypothetical loci or non-coding RNAs without functional annotation

**These patterns indicate:**
- Numerical overflow/underflow during Cox regression
- Potential separation issues (perfect prediction in subgroups)
- Technical batch effects or platform artifacts
- Inadequate quality control filtering

**Recommendation:** The top ~10 results should be excluded from biological interpretation. Analysis below focuses on the interpretable gene set (approximately LOC100128226 onward, HR range 0.007-4.3).

---

## 1. Overall Biological Interpretation

The interpretable transcriptomic signature reveals a **multi-system dysregulation** in IPF lung tissue associated with mortality risk. The predominant theme is **aberrant epithelial remodeling and barrier dysfunction**, supported by coordinate upregulation of epithelial markers (MUC1, SLC34A2, CEACAM6/7, keratins), surfactant proteins (SFTPB, SFTA2), and epithelial differentiation factors (AGR3, PRSS8).

Parallel to epithelial stress, there is strong representation of **innate immune activation** (S100A12, S100A14, CXCL1, CXCL14, CCL7, SELL) and **myeloid cell recruitment signals**, suggesting an active inflammatory microenvironment. The presence of HGF, MET, NRG1, and multiple RTK-associated genes (MERTK, SPRY2) points to **dysregulated growth factor signaling**, potentially reflecting failed regenerative attempts or pro-fibrotic signaling.

A fourth major dimension involves **extracellular matrix remodeling** (BMP6, HTRA1, EFEMP1, SPP1), consistent with progressive fibrosis. Notably, the protective gene LOC100128226 (HR=0.007) stands as an outlier requiring further investigation, as it may represent a compensatory mechanism or technical artifact.

The signature does **not** predominantly reflect myofibroblast activation or classical TGF-β targets, suggesting the assayed tissue captures epithelial-immune interfaces rather than fibroblastic foci.

---

## 2. Core Biological Programs

### Program 1: Aberrant Epithelial Differentiation and Barrier Dysfunction
**Direction:** Risk-associated (all HR > 2.0)  
**Major supporting genes:** MUC1 (HR=2.32), SLC34A2 (HR=2.27), CEACAM6 (HR=2.66), CEACAM7 (HR=2.31), MAL2 (HR=2.44), KRT17 (HR=2.19), KRT23 (HR=2.59), SFTPB (HR=2.66), SFTA2 (HR=2.25)  
**Pathway:** GO: Epithelial cell differentiation (GO:0030855); Reactome: Surfactant metabolism (R-HSA-5683826)

**Evidence and interpretation:**  
Nine independent genes converge on epithelial identity and barrier function. SLC34A2 (sodium-phosphate cotransporter) is an alveolar type II (AT2) cell marker; SFTPB and SFTA2 are surfactant components exclusively expressed in AT2 cells. MUC1 is a transmembrane mucin involved in epithelial protection. CEACAM6/7 are cell adhesion molecules upregulated during epithelial stress. Keratins (KRT17, KRT23) are intermediate filaments typically restricted to basal or transitional epithelia, suggesting **abnormal epithelial differentiation or metaplasia**.

This program likely reflects **AT2 cell dysfunction and/or expansion of aberrant epithelial populations** (honeycombing, bronchiolization). The consistent risk association suggests that epithelial exhaustion or maladaptive repair, rather than functional regeneration, predicts poor outcomes.

**Strength:** Strong (9 independent genes, tissue-specific expression pattern)  
**Limitations:** Cannot distinguish AT2 cell stress from compositional increase in AT2/bronchiolar cells. Surfactant gene upregulation may reflect cellular injury rather than function.

---

### Program 2: Neutrophil and Myeloid Cell Activity
**Direction:** Risk-associated (all HR > 2.2)  
**Major supporting genes:** S100A12 (HR=2.53), S100A14 (HR=2.57), CXCL1 (HR=2.99), CXCR1 (HR=3.28), CD177 (HR=2.72), SELL (HR=2.37), STEAP4 (HR=3.03)  
**Pathway:** GO: Neutrophil chemotaxis (GO:0030593); Reactome: Neutrophil degranulation (R-HSA-6798695)

**Evidence and interpretation:**  
Seven genes form a neutrophil/myeloid signature. S100A12 and S100A14 are calcium-binding proteins released by activated neutrophils and implicated in inflammation amplification. CXCL1 is a potent neutrophil chemoattractant; CXCR1 is its cognate receptor. CD177 is a neutrophil-specific GPI-anchored protein. SELL (L-selectin) mediates leukocyte rolling and trafficking. STEAP4 is a metalloreductase expressed in macrophages during inflammatory polarization.

This program indicates **active neutrophil recruitment and activation in the lung microenvironment**. In IPF, neutrophilia in bronchoalveolar lavage fluid has been associated with disease progression and acute exacerbations. The strong risk association (HR 2.5-3.3) suggests that neutrophilic inflammation, rather than being a bystander, may **actively drive tissue injury or impair repair**.

**Strength:** Strong (7 independent genes, convergent pathway)  
**Limitations:** Expression may partially reflect increased neutrophil infiltration (composition) rather than purely transcriptional upregulation. Cannot determine if neutrophils are cause or consequence of disease progression.

---

### Program 3: Receptor Tyrosine Kinase and Growth Factor Signaling
**Direction:** Risk-associated (all HR > 2.5)  
**Major supporting genes:** HGF (HR=2.93), MET (HR=2.53), NRG1 (HR=2.76), MERTK (HR=3.70), SPRY2 (HR=3.26), FBLIM1 (HR=2.59), MARCKS (HR=4.00)  
**Pathway:** Reactome: Signaling by MET (R-HSA-6806834); KEGG: MAPK signaling pathway (hsa04010)

**Evidence and interpretation:**  
Seven genes implicate dysregulated RTK signaling. HGF/MET is the hepatocyte growth factor/receptor pair central to epithelial regeneration and migration. NRG1 (neuregulin-1) signals through ERBB receptors and participates in epithelial-mesenchymal crosstalk. MERTK (MER tyrosine kinase) is involved in apoptotic cell clearance and fibroblast activation. SPRY2 is a negative regulator of RTK/MAPK signaling; its upregulation may reflect feedback inhibition in response to chronic RTK activation. MARCKS is a PKC substrate involved in cytoskeletal dynamics and membrane trafficking.

The **coordinate upregulation of both ligands (HGF, NRG1) and negative regulators (SPRY2)** suggests chronic, dysregulated growth factor signaling. In IPF, HGF/MET signaling has been proposed as both a regenerative response and a pro-fibrotic driver depending on context. The strong risk association here suggests that **persistent RTK activation in this disease stage represents failed repair or pro-fibrotic reprogramming** rather than effective regeneration.

**Strength:** Moderate-strong (7 genes, coherent signaling axis)  
**Limitations:** Ligand/receptor co-expression in bulk tissue does not confirm autocrine/paracrine signaling. SPRY2 upregulation complicates interpretation (negative feedback vs. pathway activation). Cannot distinguish epithelial vs. mesenchymal RTK signaling without spatial resolution.

---

### Program 4: Extracellular Matrix Remodeling and Fibrotic Signaling
**Direction:** Risk-associated (all HR > 2.3)  
**Major supporting genes:** SPP1 (HR=3.40), BMP6 (HR=3.04), HTRA1 (HR=4.30), EFEMP1 (HR=2.33), CHST15 (HR=2.99), SOD3 (HR=2.37)  
**Pathway:** GO: Extracellular matrix organization (GO:0030198); Reactome: Degradation of the extracellular matrix (R-HSA-1474228)

**Evidence and interpretation:**  
Six genes converge on ECM dynamics. SPP1 (osteopontin) is a matricellular protein strongly implicated in fibrosis across organs, promoting macrophage recruitment and myofibroblast activation. BMP6 is a TGF-β superfamily member with context-dependent pro-fibrotic or anti-fibrotic roles. HTRA1 is a secreted serine protease that degrades ECM proteins and inhibits TGF-β signaling; its upregulation may reflect a **compensatory anti-fibrotic response**. EFEMP1 (fibulin-3) is an ECM glycoprotein involved in elastogenesis. CHST15 (carbohydrate sulfotransferase 15) modifies chondroitin sulfate and regulates ECM composition. SOD3 (extracellular superoxide dismutase) protects against oxidative stress in the ECM.

This program reflects **active ECM turnover and remodeling**. The presence of both matrix-stabilizing (SPP1, EFEMP1) and matrix-degrading (HTRA1) factors suggests a **dynamic, dysregulated remodeling state** rather than static fibrosis. SPP1's exceptionally strong evidence in IPF (multiple studies, mechanistic data) makes it the most validated element of this program.

**Strength:** Moderate (6 genes, but roles are heterogeneous; SPP1 has strong independent IPF evidence)  
**Limitations:** BMP6 and HTRA1 have context-dependent functions that may be protective rather than pathogenic. Cannot distinguish active fibrogenesis from attempted resolution without longitudinal data.

---

### Program 5: Lipid Metabolism and Oxidative Stress Response
**Direction:** Risk-associated (all HR > 2.5)  
**Major supporting genes:** CYP4F3 (HR=3.78), SLC7A11 (HR=3.52), ACOX2 (HR=3.18), ALDH1A3 (HR=2.27), SLC39A8 (HR=3.22), SOD3 (HR=2.37)  
**Pathway:** Reactome: Fatty acid metabolism (R-HSA-8978868); GO: Response to oxidative stress (GO:0006979)

**Evidence and interpretation:**  
Six genes implicate metabolic stress and oxidative damage. CYP4F3 is a cytochrome P450 enzyme that metabolizes leukotriene B4 and fatty acids. SLC7A11 (xCT) is the glutamate-cystine antiporter central to glutathione synthesis and ferroptosis resistance. ACOX2 is a peroxisomal acyl-CoA oxidase involved in fatty acid β-oxidation. ALDH1A3 is an aldehyde dehydrogenase that detoxifies lipid peroxidation products. SLC39A8 is a zinc/manganese transporter linked to oxidative stress adaptation.

This program suggests **metabolic reprogramming under oxidative stress**. SLC7A11 upregulation is particularly notable, as it indicates **activation of antioxidant defense and potential ferroptosis resistance**. In cancer, SLC7A11 promotes cell survival under oxidative stress; in IPF, its upregulation may reflect epithelial or immune cell adaptation to the oxidative lung environment. However, chronic SLC7A11 activation can also drive pro-inflammatory signaling.

**Strength:** Moderate (6 genes, but metabolic pathways are broad and context-dependent)  
**Limitations:** Lipid metabolism genes may reflect cell-type composition (macrophages, AT2 cells). Oxidative stress response is a generic stress signature; unclear if it is a driver or consequence of disease.

---

## 3. Key Genes and Interaction Modules

### Gene 1: SPP1 (Osteopontin)
**Statistical association:** HR=3.40, P=9.8×10⁻⁸  
**Role:** Central node in ECM remodeling program. SPP1 is one of the most extensively validated pro-fibrotic genes in IPF, with evidence spanning human genetics (risk variants), transcriptomics (upregulated in multiple cohorts), and mechanistic studies (drives macrophage polarization and myofibroblast differentiation).  
**Interaction context:** SPP1 is a secreted protein that binds integrin receptors (αvβ3, αvβ5, α4β1) and CD44. It participates in **paracrine signaling** from macrophages and epithelial cells to fibroblasts. Its upregulation may reflect epithelial injury signals or macrophage activation.

---

### Gene 2: HTRA1 (HtrA Serine Peptidase 1)
**Statistical association:** HR=4.30, P=7.9×10⁻¹⁰  
**Role:** Highest HR among interpretable genes. HTRA1 degrades ECM proteins (fibronectin, fibrillins) and inhibits TGF-β signaling by cleaving pro-TGF-β and TGF-β receptors. Its strong risk association is paradoxical, as mechanistic studies suggest HTRA1 is **anti-fibrotic**.  
**Alternative interpretations:** (1) HTRA1 upregulation reflects a **compensatory but insufficient response** to TGF-β activation; (2) in advanced disease, HTRA1-mediated ECM degradation may destabilize tissue architecture; (3) HTRA1 may have pro-inflammatory roles independent of TGF-β inhibition.  
**Interaction context:** HTRA1 activity is regulated by binding to ECM components (fibulin-5, EFEMP1). The co-expression of HTRA1 and EFEMP1 (HR=2.33) suggests **pathway co-membership** in ECM remodeling, though whether they act synergistically or antagonistically is unclear.

---

### Gene 3: SLC7A11 (xCT, Glutamate-Cystine Antiporter)
**Statistical association:** HR=3.52, P=1.0×10⁻⁸  
**Role:** Critical for cystine uptake and glutathione synthesis. SLC7A11 protects against ferroptosis (iron-dependent lipid peroxidation-driven cell death). Its upregulation indicates **oxidative stress adaptation**.  
**Interaction context:** SLC7A11 is transcriptionally regulated by NRF2 (oxidative stress response) and ATF4 (amino acid starvation response). Its upregulation may reflect activation of these stress pathways. Functionally, SLC7A11 interacts with the glutathione biosynthesis pathway (indirect biochemical relationship).  
**Therapeutic note:** SLC7A11 inhibitors (e.g., erastin, sulfasalazine) induce ferroptosis in cancer; their role in IPF is unexplored but potentially double-edged (reduce pathologic cell survival vs. exacerbate epithelial injury).

---

### Gene 4-5: HGF and MET (Hepatocyte Growth Factor Signaling Axis)
**Statistical association:** HGF HR=2.93, P=9.9×10⁻⁹; MET HR=2.53, P=1.8×10⁻⁸  
**Role:** HGF/MET signaling is essential for epithelial regeneration, promoting cell proliferation, survival, and migration. Its coordinate upregulation suggests **attempted epithelial repair**.  
**Interaction context:** HGF binds MET (**direct ligand-receptor interaction**). This is one of the few unambiguous direct interactions in the dataset.  
**Paradox:** In acute lung injury, HGF/MET promotes repair; in chronic fibrosis, prolonged activation may drive epithelial-mesenchymal transition (EMT) or fibroblast activation. The strong risk association here suggests the latter predominates in advanced IPF.  
**Interaction with SPRY2:** SPRY2 (HR=3.26) inhibits MET and other RTKs by preventing MAPK activation (**regulatory interaction**). SPRY2 upregulation alongside HGF/MET suggests **negative feedback**, possibly indicating chronic pathway activation.

---

### Gene 6: CEACAM6 and CEACAM7 (Carcinoembryonic Antigen-Related Cell Adhesion Molecules)
**Statistical association:** CEACAM6 HR=2.66, P=5.0×10⁻⁹; CEACAM7 HR=2.31, P=7.1×10⁻⁹  
**Role:** Both are GPI-anchored cell adhesion molecules upregulated in epithelial stress and cancer. They mediate homophilic and heterophilic cell-cell adhesion and can activate intracellular signaling.  
**Interaction context:** CEACAM6 and CEACAM7 are **co-expressed** in differentiated epithelia and may engage in **homophilic trans interactions** across epithelial junctions. They are also expressed on neutrophils and can bind to integrins (**direct protein-protein interaction**).  
**Significance:** CEACAM upregulation may reflect epithelial activation or altered cell-cell adhesion dynamics. In cancer, CEACAMs promote cell survival and immune evasion; their role in IPF is poorly defined but may involve **epithelial-immune crosstalk**.

---

### Gene 7: S100A12 and S100A14 (Calcium-Binding Inflammatory Proteins)
**Statistical association:** S100A12 HR=2.53, P=2.6×10⁻⁹; S100A14 HR=2.57, P=4.5×10⁻⁹  
**Role:** Damage-associated molecular patterns (DAMPs) released during cell stress. S100A12 binds RAGE (receptor for advanced glycation end products) and Toll-like receptor 4, amplifying inflammation. S100A14 is less well-characterized but also implicated in inflammatory signaling and epithelial biology.  
**Interaction context:** Both proteins are **co-expressed** in activated neutrophils and inflammatory epithelial cells. S100A12 **directly binds** RAGE and TLR4 (direct protein-receptor interaction), initiating NF-κB signaling.  
**Significance:** S100A12 is emerging as a biomarker in IPF acute exacerbations. Its strong prognostic association supports a role for **neutrophilic inflammation in disease progression**.

---

### Gene 8: MERTK (MER Tyrosine Kinase)
**Statistical association:** HR=3.70, P=8.0×10⁻⁹  
**Role:** MERTK is a receptor tyrosine kinase in the TAM family (TYRO3, AXL, MERTK) that recognizes phosphatidylserine on apoptotic cells. It mediates **efferocytosis** (apoptotic cell clearance) and regulates macrophage polarization. In fibrosis models, MERTK activation on macrophages promotes pro-fibrotic (M2-like) polarization.  
**Interaction context:** MERTK binds bridging ligands GAS6 and PROS1, which coat apoptotic cells (**indirect interaction via bridging molecule**). Downstream, MERTK activates PI3K/AKT and JAK/STAT pathways (**pathway co-membership**).  
**Significance:** High MERTK expression may reflect increased apoptotic burden and/or expansion of efferocytic macrophages. Its risk association suggests that **impaired or maladaptive efferocytosis** may contribute to fibrosis progression.

---

### Gene 9: BMP6 (Bone Morphogenetic Protein 6)
**Statistical association:** HR=3.04, P=2.4×10⁻⁹  
**Role:** Member of the TGF-β superfamily. BMP6 signals through BMPR1A/BMPR1B and BMPR2, activating SMAD1/5/8. Its role in fibrosis is **context-dependent**: in liver fibrosis, BMP6 is protective (iron homeostasis); in lung, evidence is mixed.  
**Interaction context:** BMP6 binds BMP receptors (**direct ligand-receptor interaction**). It may also interact with BMP antagonists like noggin (direct binding).  
**Significance:** BMP6's strong risk association contrasts with its putative protective role, suggesting either (1) compensatory upregulation that is insufficient, (2) pathologic gain-of-function in IPF context, or (3) indirect association (BMP6-expressing cell populations expand in disease).

---

### Gene 10: LOC100128226
**Statistical association:** HR=0.007, P=1.2×10⁻³⁸ (strongest protective association)  
**Role:** This locus is poorly annotated. It is listed as a long non-coding RNA or hypothetical gene region.  
**Significance:** The extreme protective HR (0.007) and highly significant P-value make this a **priority for validation**, but the lack of functional annotation is concerning. Possible explanations: (1) genuine protective lncRNA regulating fibrosis pathways, (2) technical artifact (mapping issue, annotation error), (3) surrogate marker for a protective cell population.  
**Next steps:** Verify probe specificity, check for overlap with known functional elements, and perform orthogonal validation (qRT-PCR, in situ hybridization).

---

## 4. Validation Priorities

### Priority 1: Neutrophil Infiltration and Functional State
**Classification:** Confounding / composition check → Mechanistic hypothesis  
**Rationale:** The strong neutrophil signature (S100A12, S100A14, CXCL1, CXCR1, CD177) could reflect either increased neutrophil infiltration or transcriptional activation within lung tissue.  
**Current evidence:** Strong transcriptomic signal (7 independent genes, HR 2.5-3.3). Published literature shows neutrophilia in BAL predicts IPF progression.  
**External evidence:** Mixed. Some studies find neutrophils in IPF; others report predominance of macrophages and lymphocytes. Acute exacerbations clearly involve neutrophil influx.  
**Next step:**  
1. **Deconvolution analysis** using reference-based methods (e.g., CIBERSORT, xCell) to estimate neutrophil proportions across samples.  
2. **Correlation analysis:** Test if neutrophil signature genes correlate with estimated neutrophil fraction.  
3. **Immunohistochemistry:** Quantify neutrophil infiltration (myeloperoxidase, CD177 staining) in high vs. low signature samples.  
4. **Functional assay:** Assess if IPF neutrophils show activated transcriptional state (RNA-seq on isolated neutrophils).  
**Conclusion status:** **Supported hypothesis**. Strong transcriptomic evidence, but confounding by composition is plausible and must be ruled out before concluding neutrophil activation (vs. infiltration) drives mortality risk.

---

### Priority 2: SLC7A11 as Therapeutic Target and Ferroptosis Biomarker
**Classification:** Mechanistic hypothesis + Therapeutic target  
**Rationale:** SLC7A11 (HR=3.52) is the master regulator of cystine uptake and ferroptosis resistance. Its strong risk association suggests (1) oxidative stress is central to IPF progression, (2) epithelial or immune cells upregulate SLC7A11 to survive, (3) SLC7A11 inhibition might selectively eliminate pathologic cells.  
**Current evidence:** Strong transcriptomic signal (HR=3.52, P=1.0×10⁻⁸).  
**External evidence:**  
- **Pro:** Oxidative stress is well-documented in IPF. Ferroptosis has been implicated in epithelial injury in preclinical models.  
- **Con:** SLC7A11 inhibition could exacerbate epithelial injury if ferroptosis targets reparative cells. No clinical data on SLC7A11 inhibitors in IPF.  
**Next step:**  
1. **Single-cell RNA-seq:** Identify which cell types express SLC7A11 (AT2 cells, macrophages, fibroblasts?).  
2. **Ferroptosis markers:** Measure lipid peroxidation (4-HNE, MDA) and reduced glutathione (GSH) in IPF tissue.  
3. **Preclinical model:** Test SLC7A11 inhibitors (erastin, sulfasalazine) in bleomycin mouse model—assess fibrosis severity and epithelial injury.  
4. **Drug repurposing:** Sulfasalazine is FDA-approved for inflammatory bowel disease; could be tested in IPF clinical trial.  
**Conclusion status:** **Exploratory hypothesis**. Plausible mechanism, but no direct evidence that SLC7A11 drives pathology. Therapeutic potential exists but is high-risk due to potential for exacerbating injury.

---

### Priority 3: HGF/MET Signaling as Failed Regeneration vs. Pro-Fibrotic Driver
**Classification:** Mechanistic hypothesis + Interaction/network hypothesis  
**Rationale:** HGF and MET are co-upregulated (HR 2.93 and 2.53), alongside negative regulator SPRY2 (HR=3.26). This suggests **chronic pathway activation with feedback inhibition**. The key question: Does HGF/MET activation in advanced IPF represent (1) insufficient regenerative signaling, or (2) pathologic signaling that promotes EMT or fibroblast activation?  
**Current evidence:** Strong co-expression of ligand, receptor, and negative regulator.  
**External evidence:**  
- **Pro-regenerative:** HGF therapy improves outcomes in acute lung injury models. MET knockout worsens fibrosis in some models.  
- **Pro-fibrotic:** Chronic HGF/MET activation promotes EMT in cancer. HGF can activate lung fibroblasts.  
**Next step:**  
1. **Spatial transcriptomics:** Map HGF and MET expression to specific tissue compartments (AT2 cells, bronchial epithelium, stroma).  
2. **Phospho-MET staining:** Assess if MET is actively phosphorylated (pathway active) in high-expressing regions.  
3. **Longitudinal analysis:** Compare HGF/MET expression in early vs. late-stage disease.  
4. **Functional assay:** Treat IPF-derived primary AT2 cells or fibroblasts with HGF; assess proliferation, apoptosis, EMT markers, and pro-fibrotic gene expression.  
**Conclusion status:** **Supported hypothesis** for pathway activation. **Exploratory hypothesis** for whether it is adaptive or maladaptive. The strong risk association suggests it is not effectively regenerative in this disease stage.

---

### Priority 4: SPP1 (Osteopontin) as Prognostic Biomarker
**Classification:** Biomarker  
**Rationale:** SPP1 (HR=3.40) is one of the most extensively validated pro-fibrotic genes in IPF. Multiple independent studies show upregulation at mRNA and protein levels. Mechanistic studies demonstrate that SPP1 knockout or antibody blockade reduces fibrosis in mouse models.  
**Current evidence:** Strong transcriptomic signal (HR=3.40, P=9.8×
