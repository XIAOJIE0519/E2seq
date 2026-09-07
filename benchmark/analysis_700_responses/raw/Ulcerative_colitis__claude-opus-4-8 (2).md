# ulcerative colitis (UC) - claude-opus-4-8

- Benchmark system: raw
- Repeat: 2
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
- Model API: Anthropic / claude-opus-4-8
- Message SHA-256: 478acec7ab00f0e9bda085b6ecab7aa16a2bc8aa5cde3f2ba8fb71b2af94f79a
- Response HTTP status: 200
- Prompt tokens: 
- Completion tokens: 
- Reasoning tokens: 
- Total tokens: 
- API requests reported: 
- Elapsed seconds: 121.747
- Final benchmark system: raw; file rank 2/5; original repeat 2; model vendor: Anthropic

---
# Multidimensional Interpretation of Ulcerative Colitis Transcriptomic Data

## 1. Overall Biological Interpretation

The transcriptomic signature reveals a tissue under acute inflammatory stress with profound disruption of baseline colonic epithelial identity. The upregulated genes converge on innate immune activation, antimicrobial defense, neutrophil chemotaxis, and epithelial damage responses, while downregulated genes reflect systematic loss of mature colonocyte absorptive and metabolic functions. This is not simply inflammation superimposed on normal mucosa—it represents a fundamental reprogramming where the tissue prioritizes defense and repair over homeostatic nutrient transport, bile acid metabolism, and energy production. The magnitude of effect sizes (log2FC frequently exceeding ±2–4) and statistical confidence (FDR < 1e-10 for top hits) indicate these are robust, disease-defining changes rather than subtle perturbations.

## 2. Core Biological Programs

### Program 1: Neutrophil Recruitment and Innate Antimicrobial Defense
**Direction:** Strongly upregulated  
**Major supporting genes:** CXCL1 (log2FC 3.46), CXCL2 (2.80), CXCL3 (2.33), S100A8 (3.80), LCN2 (2.67), DUOX2 (4.67), DUOXA2 (2.89), IL1RN (2.88)  
**Pathway alignment:** GO:0006954 (inflammatory response), KEGG:hsa04062 (chemokine signaling pathway), Reactome:R-HSA-6798695 (neutrophil degranulation)  

**Rationale:** Multiple independent chemokine ligands (CXCL1/2/3) form a coherent neutrophil chemoattractant module, all significantly upregulated with large effect sizes. S100A8 and LCN2 are canonical neutrophil-associated proteins elevated in active UC and correlate with fecal calprotectin clinically. DUOX2/DUOXA2 generate hydrogen peroxide at the epithelial surface for host defense. IL1RN (IL-1 receptor antagonist) reflects counter-regulatory signaling. These genes do not merely co-occur—they represent sequential steps in neutrophil recruitment (chemokines), infiltration (S100A8), and antimicrobial oxidative burst (DUOX2).

**Evidence strength:** High—supported by input dataset effect sizes, pathway coherence, established UC biomarker status (LCN2, S100A8), and direct protein interaction evidence for CXCL signaling networks.  
**Limitations:** Cannot distinguish whether neutrophil signals arise from epithelial production versus infiltrating cells. Cell composition confounding likely contributes but does not fully explain epithelial-intrinsic upregulation of DUOX2 and chemokines.

---

### Program 2: Loss of Colonocyte Absorptive and Solute Transport Identity
**Direction:** Strongly downregulated  
**Major supporting genes:** SLC38A4 (-3.07), SLC23A1 (-2.40), SLC16A1 (-2.38), SLC51A (-3.71), AQP7 (-2.32), AQP8 (-4.42), SLC23A3 (-1.93), SLC19A3 (-1.34), ABCG2 (-2.92), ABCB11 (-1.15)  
**Pathway alignment:** GO:0006811 (ion transport), GO:0055085 (transmembrane transport), Reactome:R-HSA-382551 (transport of small molecules)  

**Rationale:** At least ten distinct solute carrier (SLC) family members and aquaporins are coordinately suppressed, spanning amino acid (SLC38A4), vitamin (SLC23A1/A3, SLC19A3), monocarboxylate (SLC16A1), bile acid (SLC51A), and water (AQP7/8) transport. This is not random transporter loss—it represents systematic downregulation of mature colonocyte absorptive machinery. SLC51A and ABCG2 loss disrupts bile acid and xenobiotic efflux. The breadth across unrelated transporter families and the magnitude of suppression (AQP8 log2FC -4.42, SLC51A -3.71) indicate loss of differentiated epithelial phenotype.

**Evidence strength:** High—consistent direction across multiple independent transporter families, alignment with known UC epithelial dysfunction, and magnitude of effect.  
**Limitations:** Cannot determine whether suppression is cause or consequence of inflammation. May partially reflect epithelial regeneration with immature cells replacing damaged mature colonocytes.

---

### Program 3: Impaired Colonocyte Lipid and Energy Metabolism
**Direction:** Downregulated  
**Major supporting genes:** HMGCS2 (-3.45), GBA3 (-3.00), HSD3B2 (-2.77), G6PC (-1.52), LIPC (-1.57), ACSF2 (-1.93), ETNK1 (-1.58)  
**Pathway alignment:** GO:0006629 (lipid metabolic process), KEGG:hsa00072 (synthesis and degradation of ketone bodies), Reactome:R-HSA-77289 (mitochondrial fatty acid beta-oxidation)  

**Rationale:** HMGCS2 (hydroxymethylglutaryl-CoA synthase 2) catalyzes the rate-limiting step in ketogenesis and is the most tissue-specific marker of colonocyte energy metabolism via butyrate oxidation. Its profound suppression (-3.45 log2FC) alongside GBA3 (glucosylceramidase), HSD3B2 (steroid metabolism), and ACSF2 (acyl-CoA synthetase for short-chain fatty acids) indicates disrupted lipid handling and mitochondrial fuel utilization. Colonocytes normally derive 60–70% of energy from butyrate; this program's collapse aligns with UC metabolic dysfunction and may contribute to epithelial energy deficit.

**Evidence strength:** Moderate to high—HMGCS2 is well-established in colonic metabolism, supported by additional lipid pathway genes. Functional link between butyrate metabolism loss and UC pathogenesis is biologically plausible and supported by mechanistic literature.  
**Limitations:** HMGCS2 expression is highly cell-type specific (surface colonocytes); loss may partly reflect cellular composition change. Direct metabolomic or functional validation needed to confirm metabolic consequence.

---

### Program 4: Epithelial Remodeling and Damage-Associated Molecular Pattern Response
**Direction:** Upregulated  
**Major supporting genes:** MMP3 (4.64), CHI3L1 (4.59), TNC (2.58), TIMP1 (1.97), SERPINB5 (3.29), S100P (1.77), REG4 (2.05), TGM2 (1.91)  
**Pathway alignment:** GO:0030198 (extracellular matrix organization), Hallmark:EPITHELIAL_MESENCHYMAL_TRANSITION, Reactome:R-HSA-1474244 (extracellular matrix degradation)  

**Rationale:** MMP3 (matrix metalloproteinase-3) and CHI3L1 (chitinase-3-like protein 1, YKL-40) show the largest upregulation among damage-response genes. MMP3 degrades collagen and other ECM components, contributing to tissue remodeling and damage; TIMP1 (tissue inhibitor of metalloproteinases) provides counter-regulation. CHI3L1 is secreted during tissue injury and inflammatory remodeling. TNC (tenascin-C) is an ECM glycoprotein upregulated during wound healing. S100P and REG4 (regenerating islet-derived protein 4) are epithelial stress/regeneration markers. TGM2 (transglutaminase 2) cross-links ECM and is involved in wound repair. This ensemble reflects active tissue remodeling, ECM turnover, and epithelial stress signaling.

**Evidence strength:** Moderate to high—MMP3 and TIMP1 have established roles in IBD tissue remodeling; CHI3L1 is validated as a UC biomarker. Gene functions are complementary (matrix degradation, inhibition, remodeling).  
**Limitations:** Cannot distinguish adaptive repair from pathological remodeling. ECM changes may be secondary to inflammation rather than primary drivers. Cell-source ambiguity (epithelial versus stromal/immune) for some genes.

---

### Program 5: Adaptive Immune Activation and B Cell Infiltration
**Direction:** Upregulated  
**Major supporting genes:** IGHV4-31|IGHM|IGHG1 (1.89), CTLA4 (2.62), IFI16 (1.39), IRAK3 (1.78), UBD (2.58), SOCS3 (2.79), PARP8 (1.73)  
**Pathway alignment:** GO:0006955 (immune response), GO:0002377 (immunoglobulin production), KEGG:hsa04659 (Th17 cell differentiation)  

**Rationale:** Immunoglobulin heavy chain genes indicate B cell/plasma cell infiltration. CTLA4 (cytotoxic T-lymphocyte-associated protein 4) is a T cell checkpoint receptor upregulated in activated T cells and regulatory T cells. SOCS3 (suppressor of cytokine signaling 3) is a negative feedback regulator induced by inflammatory cytokines (IL-6, IFN). IRAK3 (interleukin-1 receptor-associated kinase 3) is a negative regulator of TLR signaling. UBD (ubiquitin D) is IFN-inducible. This program reflects adaptive immune infiltration (B/T cells) and counter-regulatory signaling attempting to limit inflammation.

**Evidence strength:** Moderate—immunoglobulin presence confirms adaptive immune infiltration, consistent with UC histopathology. CTLA4 and SOCS3 roles are well-established, but these are broad immune markers rather than UC-specific.  
**Limitations:** Adaptive immune signals are expected in UC and less informative than innate signatures for mechanistic insight. Cannot determine clonality or antigen specificity from bulk expression. Cell composition is a major confounder here.

---

## 3. Key Genes and Interaction Modules

### 1. **SLC6A14** (log2FC 4.85, FDR 8.1e-39)
**Direction:** Strongly upregulated (top-ranked gene)  
**Role:** SLC6A14 is a sodium- and chloride-dependent amino acid transporter, broadly specific for neutral and cationic amino acids. Its dramatic upregulation in UC is well-documented and mechanistically linked to inflammatory signaling (TNF-α, IL-1β induction via NF-κB). It is not a typical colonocyte transporter—its induction represents pathological reprogramming rather than loss of normal function.  
**Relationship to programs:** Functionally distinct from the downregulated absorptive transporters (Program 2). May support amino acid supply for proliferating/stressed epithelium or immune cells. Published evidence links SLC6A14 overexpression to mucosal inflammation and suggests it may be a therapeutic target.  
**Gene interactions:** No direct physical interaction with other top genes; represents an independent inflammatory response module.

### 2. **DUOX2 / DUOXA2** (log2FC 4.67 / 2.89)
**Direction:** Upregulated  
**Role:** DUOX2 (dual oxidase 2) generates hydrogen peroxide at the apical epithelial surface for antimicrobial defense. DUOXA2 is its essential maturation factor. Together they form a functional complex.  
**Relationship to programs:** Core component of Program 1 (antimicrobial defense).  
**Gene interactions:** Direct protein-protein interaction (DUOX2-DUOXA2 obligate heterocomplex). Functionally linked to innate immunity but operates independently of chemokine signaling.  
**Evidence:** Genetic variants in DUOX2 are associated with IBD risk. Its upregulation in UC is reproducible and reflects epithelial-intrinsic innate immune activation.

### 3. **CXCL1 / CXCL2 / CXCL3 chemokine module** (log2FC 3.46 / 2.80 / 2.33)
**Direction:** Upregulated  
**Role:** These three chemokines are ELR+ CXC chemokines that bind CXCR2 and mediate neutrophil chemotaxis. They are co-regulated by NF-κB and AP-1 transcription factors in response to inflammatory cytokines.  
**Relationship to programs:** Central to Program 1 (neutrophil recruitment).  
**Gene interactions:** Pathway co-membership and shared receptor (CXCR2), but not direct physical interaction with each other. Co-expression likely reflects shared transcriptional regulation rather than direct regulatory interaction.  
**Evidence:** Elevated in UC tissue and serum; correlate with disease activity. Represent a therapeutically targetable node (CXCR2 antagonists in development).

### 4. **MMP3** (log2FC 4.64, FDR 5.4e-14)
**Direction:** Strongly upregulated  
**Role:** Matrix metalloproteinase-3 degrades multiple ECM components (collagens, proteoglycans, fibronectin) and activates other MMPs. Central to tissue remodeling and damage in UC.  
**Relationship to programs:** Key driver of Program 4 (ECM remodeling).  
**Gene interactions:** Functionally opposed by TIMP1 (also upregulated, log2FC 1.97), reflecting MMP-TIMP regulatory axis. MMP3 can activate MMP9 (not in top list but likely also elevated). No direct physical interaction with TIMP1; regulatory relationship is indirect via enzymatic inhibition.  
**Evidence:** Elevated MMP3 in UC mucosa is well-established. Contributes to mucosal ulceration and correlates with endoscopic severity.

### 5. **HMGCS2** (log2FC -3.45, FDR 1.1e-16)
**Direction:** Downregulated  
**Role:** Rate-limiting enzyme for ketogenesis from butyrate. Its suppression is a hallmark of colonocyte metabolic dysfunction in UC.  
**Relationship to programs:** Defines Program 3 (metabolic dysfunction).  
**Gene interactions:** Metabolically linked to ACSF2 (acyl-CoA synthetase, log2FC -1.93) in butyrate oxidation pathway. Relationship is metabolic pathway co-membership, not direct protein interaction.  
**Evidence:** HMGCS2 loss in UC is reproducible across studies. May contribute to epithelial energy deficit and impaired barrier function. Mechanistic link to PPARγ signaling.

### 6. **CHI3L1** (log2FC 4.59, FDR 3.2e-11)
**Direction:** Strongly upregulated  
**Role:** Chitinase-3-like protein 1 (YKL-40) is secreted during inflammation and tissue remodeling. Lacks enzymatic activity but binds receptors (IL-13Rα2, others) to modulate inflammation and fibrosis.  
**Relationship to programs:** Program 4 (tissue remodeling). Elevated CHI3L1 in UC serum correlates with disease activity and has been investigated as a biomarker.  
**Gene interactions:** No direct physical interactions with other top genes. Likely secreted by multiple cell types (epithelial, macrophages).  
**Evidence:** Well-validated UC biomarker. Serum levels decrease with effective therapy.

### 7. **AQP8** (log2FC -4.42, FDR 1.6e-13)
**Direction:** Strongly downregulated (largest effect among downregulated genes by magnitude)  
**Role:** Aquaporin-8 is a colonocyte water channel facilitating transcellular water absorption. Its profound loss reflects impaired absorptive function and contributes to diarrhea in UC.  
**Relationship to programs:** Core component of Program 2 (loss of absorptive function).  
**Gene interactions:** Functionally parallel to AQP7 (also downregulated, log2FC -2.32); both mediate water transport but with different tissue distributions. No direct interaction; represent independent transporter loss.  
**Evidence:** AQP8 downregulation in UC is consistent across studies and mechanistically linked to TNF-α signaling.

### 8. **S100A8** (log2FC 3.80, FDR 4.4e-11)
**Direction:** Upregulated  
**Role:** S100A8 (calgranulin A) forms heterodimers with S100A9 (calprotectin) and is released by neutrophils and activated epithelium. Functions as a damage-associated molecular pattern (DAMP) amplifying inflammation.  
**Relationship to programs:** Program 1 (neutrophil/innate immune). Fecal calprotectin (S100A8/A9) is the standard noninvasive biomarker for UC activity.  
**Gene interactions:** Direct protein interaction with S100A9 (not in top list but almost certainly elevated). Functionally linked to neutrophil infiltration.  
**Evidence:** Gold-standard biomarker. Strong association with mucosal neutrophil burden.

### 9. **CTLA4** (log2FC 2.62, FDR 1.1e-10)
**Direction:** Upregulated  
**Role:** CTLA-4 is an inhibitory checkpoint receptor on activated T cells and constitutively expressed on regulatory T cells. Its upregulation may reflect both effector T cell activation and regulatory T cell infiltration.  
**Relationship to programs:** Program 5 (adaptive immune activation). Relevant as a therapeutic target—anti-CTLA4 therapy (ipilimumab) can cause colitis, and CTLA4 pathway modulation is under investigation in IBD.  
**Gene interactions:** No direct physical interactions with other top genes in this list. Functionally linked to T cell activation networks.  
**Evidence:** CTLA4 expression in UC tissue is increased and correlates with T cell infiltration. Polymorphisms in CTLA4 are associated with IBD susceptibility in some populations.

### 10. **SOCS3** (log2FC 2.79, FDR 8.1e-12)
**Direction:** Upregulated  
**Role:** Suppressor of cytokine signaling 3 is a negative feedback regulator induced by IL-6, IFN-γ, and other inflammatory cytokines via STAT3. Its upregulation indicates active cytokine signaling and attempted dampening.  
**Relationship to programs:** Program 5 (adaptive immune) and broadly relevant to inflammatory cytokine networks.  
**Gene interactions:** Regulatory interaction—SOCS3 inhibits JAK-STAT signaling downstream of multiple cytokine receptors. Not a direct physical interaction with cytokines themselves but a regulatory feedback module.  
**Evidence:** SOCS3 is consistently upregulated in IBD. Its induction is protective in some models (limits STAT3 hyperactivation) but may impair certain repair pathways.

---

## 4. Validation Priorities

### Priority 1: **SLC6A14 as a therapeutic target**
**Classification:** Therapeutic target  
**Rationale:** SLC6A14 shows the largest upregulation with the strongest statistical evidence. Unlike typical UC genes that reflect inflammation consequences, SLC6A14 is mechanistically induced by inflammatory cytokines and its inhibition reduces mucosal inflammation in preclinical models. It is druggable (small-molecule inhibitors exist) and may represent a non-immunosuppressive therapeutic approach.  
**Evidence from dataset:** Top-ranked upregulated gene (log2FC 4.85, FDR 8.1e-39).  
**External evidence:** Multiple independent studies confirm SLC6A14 upregulation in UC. Mouse models show that SLC6A14 deletion or inhibition reduces colitis severity. Preliminary small-molecule inhibitors have been tested preclinically.  
**Next step:** Validate that SLC6A14 inhibition reduces inflammation in human organoid or ex vivo tissue models. Determine whether expression level correlates with disease severity and treatment response in clinical cohorts.  
**Conclusion level:** **Supported hypothesis**—preclinical evidence is encouraging, but human therapeutic benefit is unproven.

---

### Priority 2: **CXCR2 antagonism for neutrophil-driven inflammation**
**Classification:** Therapeutic target  
**Rationale:** The coordinated upregulation of CXCL1/2/3 (all CXCR2 ligands) and S100A8 indicates neutrophil-driven inflammation is a dominant pathogenic process. CXCR2 antagonists are in clinical development for other inflammatory diseases and could be repurposed for UC.  
**Evidence from dataset:** CXCL1 (log2FC 3.46), CXCL2 (2.80), CXCL3 (2.33), S100A8 (3.80)—all strongly upregulated with high confidence.  
**External evidence:** CXCR2 antagonists reduce neutrophil infiltration and mucosal damage in animal colitis models. Phase 2 trials in COPD and other diseases show proof of mechanism for neutrophil inhibition. No UC-specific clinical trial data yet.  
**Next step:** Correlate CXCL1/2/3 expression with fecal calprotectin and endoscopic severity in UC cohorts. Test CXCR2 antagonist in UC-relevant preclinical models.  
**Conclusion level:** **Supported hypothesis**—strong biological rationale and preclinical data, but clinical efficacy in UC is speculative.

---

### Priority 3: **Metabolic reprogramming and butyrate oxidation rescue**
**Classification:** Mechanistic hypothesis  
**Rationale:** The profound loss of HMGCS2 and related metabolic genes raises the question: Is impaired butyrate oxidation a driver of epithelial dysfunction, or simply a consequence of inflammation and cell damage? If causal, restoring metabolic capacity could be therapeutic.  
**Evidence from dataset:** HMGCS2 (log2FC -3.45), GBA3 (-3.00), ACSF2 (-1.93)—consistent suppression of lipid/energy metabolism.  
**External evidence:** Mouse studies show that forced HMGCS2 expression or PPARγ agonists (which induce HMGCS2) can ameliorate colitis. Butyrate supplementation has mixed clinical results in UC—possibly because the machinery to utilize it is suppressed.  
**Next step:** Determine whether HMGCS2 expression correlates with disease severity and mucosal healing. Test whether PPARγ agonists or metabolic interventions (butyrate + PPARγ agonist combination) restore epithelial metabolic function in organoid or ex vivo models.  
**Conclusion level:** **Exploratory hypothesis**—mechanistic link is plausible but causality is unproven. Association versus causation is ambiguous.

---

### Priority 4: **MMP3/TIMP1 axis and fibrosis risk stratification**
**Classification:** Biomarker  
**Rationale:** MMP3 and TIMP1 are both elevated, but their ratio may predict progression to fibrosis or stricture formation (a subset of UC patients). High MMP3 relative to TIMP1 could indicate unchecked ECM degradation and remodeling risk.  
**Evidence from dataset:** MMP3 (log2FC 4.64), TIMP1 (1.97)—both upregulated but MMP3 shows larger effect.  
**External evidence:** MMP/TIMP imbalance is implicated in fibrosis in Crohn's disease and liver disease. Limited data on UC-specific fibrosis biomarkers. UC strictures are less common than in Crohn's but still clinically significant.  
**Next step:** Measure MMP3/TIMP1 ratio in UC cohorts and correlate with longitudinal outcomes (stricture formation, need for surgery). Validate in independent cohort.  
**Conclusion level:** **Exploratory hypothesis**—logical biomarker candidate but requires prospective validation. No current evidence that MMP3/TIMP1 ratio predicts UC outcomes.

---

### Priority 5: **Cell composition deconvolution to distinguish epithelial versus immune signals**
**Classification:** Confounding / composition check  
**Rationale:** Many upregulated genes (S100A8, immunoglobulins, CTLA4) likely derive from infiltrating immune cells rather than epithelial cells. Failing to account for cell composition may lead to misattribution of signals to wrong cell types and confound mechanistic interpretation.  
**Evidence from dataset:** Cannot distinguish cell source from bulk RNA-seq. Markers of neutrophils (S100A8), B cells (IGHV), and T cells (CTLA4) are prominent.  
**External evidence:** Single-cell RNA-seq studies of UC mucosa show distinct epithelial, immune, and stromal compartments with cell-type-specific gene signatures. Deconvolution methods (CIBERSORTx, MuSiC) can estimate cell proportions from bulk data.  
**Next step:** Apply deconvolution algorithms to estimate cell-type proportions. Re-analyze gene expression adjusting for immune infiltration to isolate epithelial-intrinsic changes. Validate key findings (e.g., SLC6A14, DUOX2) in sorted epithelial cells or single-cell data.  
**Conclusion level:** **Established need**—cell composition is a major confounder in bulk tissue transcriptomics and must be addressed for mechanistic precision.

---

## 5. Evidence Grounding

**Direct dataset evidence:** All gene expression changes are statistically robust (FDR < 1e-10 for the majority of top genes) with large effect sizes (many log2FC > 2 in absolute value). This provides high confidence that these are real, disease-defining signals.

**Pathway / ontology evidence:** Identified programs align well with established GO, KEGG, and Reactome pathways (chemokine signaling, solute transport, lipid metabolism, ECM organization, immune response). This supports biological coherence.

**Protein interaction evidence:** Limited direct physical interactions among top genes. DUOX2-DUOXA2 is a validated protein complex. CXCL chemokines share a receptor (CXCR2) but do not physically interact with each other. S100A8-S100A9 form calprotectin (S100A9 not in top list but implied). MMP3-TIMP1 is an enzyme-inhibitor pair (functional, not physical interaction). Most other relationships are pathway co-membership or co-expression rather than direct interaction.

**Disease-association evidence:** Many genes are well-established UC-associated markers:
- **Established UC markers:** LCN2, S100A8/A9 (fecal calprotectin), CHI3L1, SLC6A14, DUOX2, MMP3.
- **IBD genetic risk loci:** CTLA4 polymorphisms are associated with IBD in some populations. DUOX2 variants are IBD risk factors.

**Expression / tissue evidence:** Several genes are highly tissue- or cell-type specific:
- HMGCS2 is colonocyte-specific (surface epithelium).
- DUOX2 is epithelial-specific.
- S100A8 is predominantly neutrophil-derived.
- CTLA4 is T-cell specific.
- Immunoglobulins indicate B cell/plasma cell infiltration.

**Conflicting evidence:** 
- **SLC6A14:** Upregulated in UC (clear from dataset and literature), but its precise role is debated—some evidence suggests it is protective (nutrient supply), other evidence suggests it is pathogenic (inflammatory amplification). Majority of recent evidence supports pathogenic role and therapeutic targeting.
- **SOCS3:** Can be protective (limits STAT3 hyperactivation) or detrimental (impairs IL-22-mediated repair). Context-dependent.

**Evidence independence:** Many
