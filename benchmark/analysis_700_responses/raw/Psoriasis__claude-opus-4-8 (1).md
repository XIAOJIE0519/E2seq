# psoriasis - claude-opus-4-8

- Benchmark system: raw
- Repeat: 1
- Task type: DISEASE-STATE
- Tissue / sample source: lesional skin
- Comparison or endpoint: psoriatic lesional skin versus normal control skin
- Answer input cohort: Discovery/Core only
- Selected items: 100
- Input fields: gene name, effect size (log2FC/HR), P value, FDR
- E2seq Agent RAG: disabled
- Conversation memory: disabled
- Thinking mode: disabled
- Held-out validation data in prompt/RAG: no
- Model API: Anthropic / claude-opus-4-8
- Message SHA-256: d1a33d3f606c81814c4fb94a6c63c8f1abebd3bde37d769e82eae4772d8ff873
- Response HTTP status: 200
- Prompt tokens: 
- Completion tokens: 
- Reasoning tokens: 
- Total tokens: 
- API requests reported: 
- Elapsed seconds: 125.482
- Final benchmark system: raw; file rank 1/5; original repeat 1; model vendor: Anthropic

---
# Multidimensional Interpretation of Psoriatic Lesional Skin Transcriptomics

## 1. Overall Biological Interpretation

The transcriptomic signature of psoriatic lesional skin reveals a disease state dominated by **hyperproliferative keratinocyte activation**, **IL-17/IL-36 cytokine axis amplification**, and **antimicrobial defense response**, accompanied by **loss of lipid homeostasis and barrier differentiation programs**. 

This is not simply an inflammatory disease but a coordinated reprogramming of epidermal biology. The upregulated genes form a tightly interconnected network involving epidermal barrier disruption (SPRR family, LCE3 family, KRT6A), cytokine storm (IL36A, IL36G, IL19, IL20, IL26), chemokine signaling (CXCL13), neutrophil recruitment markers (S100A7/8/12, DEFB4A/B), and metabolic reprogramming (KYNU, AKR1B10/15). The downregulated genes (BTC, CYP2W1, LINC02660) suggest suppression of lipid metabolism and keratinocyte differentiation pathways. The magnitude of dysregulation—with multiple genes showing >8 log2FC—indicates profound architectural remodeling rather than subtle inflammatory modulation.

---

## 2. Core Biological Programs

### **Program 1: IL-36/IL-17 Cytokine Amplification Loop**

**Direction:** Strongly upregulated  
**Major supporting genes:** IL36A (log2FC=11.37), IL36G (5.68), IL19 (7.58), IL20 (5.67), IL26 (4.36), IL36RN (3.01)  
**Pathway:** Reactome "Interleukin-36 pathway" / KEGG "IL-17 signaling pathway"  

**Rationale:** The extreme upregulation of multiple IL-36 family members (IL36A, IL36G) alongside their endogenous antagonist (IL36RN, though insufficient to counterbalance agonists) and downstream IL-17-associated cytokines (IL19, IL20, IL26—all IL-10 family members induced by IL-17/IL-23) indicates a self-amplifying cytokine network. IL-36 cytokines are keratinocyte-derived alarmin cytokines that drive psoriatic inflammation by activating dendritic cells and amplifying IL-23/IL-17 responses. The co-expression of multiple members across different IL-36 loci and distinct IL-17-responsive cytokines provides convergent evidence.

**Evidence strength:** Strong. Multiple independent genes within the same pathway, extremely high statistical significance (P < 10^-90 for IL36A/G), and direct mechanistic evidence linking IL-36 to psoriasis pathogenesis.

**Limitations:** IL36RN upregulation (3.01 log2FC) suggests attempted negative feedback, but the agonist/antagonist imbalance is inferred from fold-change rather than measured activity. Cannot distinguish primary driver from secondary amplification without kinetic data.

---

### **Program 2: Keratinocyte Hyperproliferation and Altered Differentiation**

**Direction:** Upregulated (proliferation markers) / Dysregulated (differentiation markers)  
**Major supporting genes:** SPRR2A/B/D/E/F/G (5.99–7.32 log2FC), LCE3A/D (8.30, 5.31), KRT6A (4.30), RRM2 (2.72), CCNE1 (2.56), GJB2 (4.42), GJB6 (3.02)  
**Pathway:** GO "Keratinocyte differentiation" / "Cornified envelope" / Reactome "Formation of the cornified envelope"  

**Rationale:** The massive upregulation of small proline-rich repeat proteins (SPRR2 family, 7 members) and late cornified envelope proteins (LCE3A/D) represents a shift toward stress-induced differentiation rather than normal terminal differentiation. SPRR and LCE proteins are normally expressed in wound healing and inflammatory conditions. Concurrent upregulation of KRT6A (stress keratin), RRM2 (ribonucleotide reductase, cell cycle), and CCNE1 (cyclin E1) indicates hyperproliferation. Gap junction proteins GJB2/6 upregulation suggests altered intercellular communication. This program reflects keratinocytes trapped in a hyperproliferative, incompletely differentiated state typical of psoriatic plaques.

**Evidence strength:** Strong. Multiple independent gene families (SPRR, LCE, KRT6, cell cycle regulators), pathway co-membership, and direct RNA-seq evidence. Consistent with established psoriasis biology (epidermal acanthosis/hyperkeratosis).

**Limitations:** SPRR and LCE gene clusters reside at chr1q21.3; high correlation may partly reflect coordinated genomic regulation rather than independent pathway activation. Cannot distinguish primary keratinocyte dysfunction from secondary response to cytokine milieu.

---

### **Program 3: Antimicrobial Defense and Neutrophil Recruitment**

**Direction:** Strongly upregulated  
**Major supporting genes:** DEFB4A/4B (11.18, 11.03), DEFB103A/B (5.76, 5.75), S100A7/7A/8/12 (7.09–9.83), PI3 (9.24), SERPINB3/4/13 (6.74–9.12)  
**Pathway:** GO "Defense response to bacterium" / Reactome "Antimicrobial peptides"  

**Rationale:** Extreme upregulation of β-defensins (DEFB4A/B, DEFB103A/B), S100 alarmins (S100A7/7A/8/12—psoriasin family and calgranulin), and elafin (PI3, a SLPI-family antimicrobial protease inhibitor) indicates a potent innate immune response. S100A8/A12 form calprotectin, a damage-associated molecular pattern (DAMP) and neutrophil marker. Serpins (SERPINB3/4/13) are cysteine protease inhibitors with antimicrobial and anti-inflammatory roles. This program likely reflects both antimicrobial defense and neutrophil infiltration (S100A8/12), consistent with Munro microabscesses in psoriasis.

**Evidence strength:** Strong. Multiple independent antimicrobial peptide families, extremely high fold-changes (>9 log2FC for DEFB4A/B, S100A7A, PI3), and known expression in psoriatic epidermis.

**Limitations:** Cannot distinguish between keratinocyte-produced antimicrobial peptides and neutrophil-derived S100 proteins (potential cell composition confounding). Antimicrobial response may be secondary to barrier disruption rather than primary pathogenic event.

---

### **Program 4: Kynurenine/Tryptophan Metabolism and Aryl Hydrocarbon Receptor Activation**

**Direction:** Upregulated  
**Major supporting genes:** KYNU (4.42), AKR1B10 (6.27), AKR1B15 (5.23)  
**Pathway:** KEGG "Tryptophan metabolism" / Reactome "Biological oxidations"  

**Rationale:** KYNU (kynureninase) catalyzes a rate-limiting step in tryptophan catabolism via the kynurenine pathway, which generates immunomodulatory metabolites and aryl hydrocarbon receptor (AhR) ligands. AKR1B10/15 (aldo-keto reductases) metabolize retinoids and lipid aldehydes, and AKR1B10 is a known AhR target gene. Kynurenine pathway activation occurs in inflammatory conditions and may modulate immune responses and keratinocyte proliferation. This program suggests metabolic reprogramming linking inflammation, immune tolerance, and barrier function.

**Evidence strength:** Moderate. Multiple genes in tryptophan metabolism and retinoid metabolism with high statistical significance (P < 10^-90 for KYNU). However, this program is supported by fewer independent genes than cytokine or keratinocyte programs.

**Limitations:** AKR1B10/15 have broad substrate specificities; their upregulation may reflect general oxidative stress or retinoid dysregulation rather than specific kynurenine pathway activation. AhR activation is inferred, not directly measured. The functional consequence of kynurenine pathway activation in psoriasis (pro-inflammatory vs. regulatory) remains unclear.

---

### **Program 5: Suppression of Lipid Metabolism and Epidermal Barrier Lipids**

**Direction:** Downregulated  
**Major supporting genes:** BTC (-4.30), CYP2W1 (-4.70), UGT3A2 (-4.59), SAPCD1 (-2.94)  
**Pathway:** GO "Lipid metabolic process" / Reactome "Metabolism of lipids"  

**Rationale:** BTC (betacellulin, an EGFR ligand) promotes keratinocyte proliferation and differentiation; its downregulation suggests disrupted growth factor signaling. CYP2W1 (cytochrome P450) metabolizes arachidonic acid and eicosanoids; UGT3A2 conjugates lipids and bile acids. Downregulation of these lipid-metabolizing enzymes suggests impaired lipid homeostasis, potentially contributing to barrier dysfunction. SAPCD1 (suppressor APC domain containing 1) is less characterized but implicated in lipid droplet biology.

**Evidence strength:** Weak to moderate. Fewer downregulated genes overall, and those present have lower statistical significance (P ~ 10^-70 to 10^-76) and smaller fold-changes than upregulated programs. Functional coherence of these genes as a unified program is less established than for upregulated programs.

**Limitations:** Downregulated genes may reflect cell composition changes (loss of sebaceous glands, altered dermal fibroblast populations) rather than active transcriptional repression. BTC's role in psoriasis is not well established. CYP2W1 and UGT3A2 have broad functions; their specific contribution to barrier lipid deficiency is speculative. This program is the weakest of the five and should be considered exploratory.

---

## 3. Key Genes and Interaction Modules

### **Gene 1: IL36A**
**Direction:** Extreme upregulation (log2FC = 11.37, P = 2.5×10^-102)  
**Role:** Central pro-inflammatory cytokine in psoriasis pathogenesis. IL-36α activates dendritic cells and promotes IL-23/IL-17 axis amplification.  
**Interactions:** **Pathway co-membership** with IL36G and IL36RN (all IL-1 family members). **Regulatory interaction** with IL-17-producing T cells via dendritic cell activation. Not a direct physical interaction.  
**Evidence:** Direct RNA-seq evidence (extreme fold-change), established disease-association evidence (IL36RN mutations cause generalized pustular psoriasis), clinical evidence (IL-36 receptor antagonists in clinical trials for psoriasis).

---

### **Gene 2: KYNU (kynureninase)**
**Direction:** Upregulated (log2FC = 4.42, P = 7.2×10^-95)  
**Role:** Metabolic checkpoint linking inflammation, immune regulation, and AhR signaling. May modulate T cell function and keratinocyte proliferation via kynurenine metabolites.  
**Interactions:** **Indirect metabolic relationship** with AKR1B10/15 (both are potential AhR target genes). **Pathway co-membership** in tryptophan metabolism.  
**Evidence:** Direct RNA-seq evidence, pathway evidence (tryptophan metabolism), emerging literature linking kynurenine pathway to psoriasis. However, functional role in psoriasis is less established than for cytokines.

---

### **Gene 3-4: S100A7/S100A7A (psoriasin)**
**Direction:** Extreme upregulation (S100A7: 7.09, S100A7A: 9.83 log2FC)  
**Role:** Antimicrobial peptides, chemotactic for neutrophils and T cells, and DAMPs amplifying inflammation. Named "psoriasin" due to strong psoriasis association.  
**Interactions:** **Co-expression** with S100A8/A12 (S100A7A locus at chr1q21.3 contains S100 gene cluster; co-expression may reflect genomic clustering). **Regulatory interaction** with IL-17 (IL-17 induces S100A7 expression). **Direct protein interaction** evidence between S100A8/S100A9 forming calprotectin heterodimer, but S100A7 does not directly interact with S100A8/12.  
**Evidence:** Direct RNA-seq evidence, strong disease-association evidence (S100A7 overexpression in psoriatic epidermis is a diagnostic feature), protein interaction evidence for S100A8/A9 heterodimerization.

---

### **Gene 5-6: DEFB4A/DEFB4B (β-defensin 2)**
**Direction:** Extreme upregulation (DEFB4A: 11.18, DEFB4B: 11.03 log2FC)  
**Role:** Antimicrobial peptides with chemotactic activity for dendritic cells and T cells. Link innate and adaptive immunity.  
**Interactions:** **Co-expression** (DEFB4A/B are nearly identical gene duplicates at chr8p23.1). **Pathway co-membership** with other defensins and antimicrobial peptides. **Indirect relationship** with IL-17 (IL-17 induces DEFB4 expression).  
**Evidence:** Direct RNA-seq evidence (highest fold-changes in dataset), disease-association evidence (DEFB4 overexpression in psoriasis), literature evidence (DEFB4 copy number variation associated with psoriasis risk in some studies, though findings are inconsistent).

---

### **Gene 7: SERPINB3/SERPINB4**
**Direction:** Strong upregulation (SERPINB3: 6.74, SERPINB4: 9.12 log2FC)  
**Role:** Serine protease inhibitors with antimicrobial, anti-apoptotic, and proliferation-promoting functions in keratinocytes.  
**Interactions:** **Co-expression** (SERPINB3/4 are tandem genes at chr18q21.33). **Pathway co-membership** with other antimicrobial defense genes.  
**Evidence:** Direct RNA-seq evidence, tissue-specific expression evidence (keratinocyte-specific), disease-association evidence (upregulated in psoriasis and atopic dermatitis). Functional role less established than for defensins/S100 proteins.

---

### **Gene 8: WNT5A**
**Direction:** Upregulated (log2FC = 2.53, P = 2.8×10^-70)  
**Role:** Non-canonical Wnt signaling pathway member. Promotes keratinocyte proliferation and inflammatory signaling.  
**Interactions:** **Regulatory interaction** with β-catenin-independent Wnt pathways (planar cell polarity, Wnt/Ca2+ pathways). **Indirect relationship** with IL-17 (IL-17 may induce WNT5A expression).  
**Evidence:** Direct RNA-seq evidence, pathway evidence (Wnt signaling), literature evidence (WNT5A implicated in psoriasis and inflammatory skin diseases). However, effect size is moderate compared to cytokine/antimicrobial programs.

---

### **Gene 9: CD274 (PD-L1)**
**Direction:** Upregulated (log2FC = 3.44, P = 7.7×10^-66)  
**Role:** Immune checkpoint ligand. Upregulation may represent attempted negative feedback on T cell activation, or paradoxically may indicate chronic T cell stimulation.  
**Interactions:** **Direct physical interaction** with PDCD1 (PD-1 receptor on T cells). **Regulatory interaction** with T cell exhaustion and activation pathways.  
**Evidence:** Direct RNA-seq evidence, protein interaction evidence (well-established PD-L1/PD-1 interaction), disease-association evidence (PD-L1 upregulation reported in psoriasis, though less studied than in cancer). Clinical evidence: PD-1/PD-L1 inhibitors (cancer immunotherapy) can trigger psoriasis as an immune-related adverse event, suggesting complex role.

---

### **Gene 10: CXCL13**
**Direction:** Upregulated (log2FC = 5.89, P = 2.5×10^-70)  
**Role:** B cell-attracting chemokine, marker of tertiary lymphoid structure formation.  
**Interactions:** **Direct physical interaction** with CXCR5 receptor on B cells and follicular helper T cells. **Pathway co-membership** with chemokine signaling.  
**Evidence:** Direct RNA-seq evidence, protein interaction evidence (CXCL13-CXCR5 interaction), literature evidence (CXCL13 implicated in chronic inflammatory diseases with B cell involvement). However, B cells are not traditionally considered central to psoriasis pathogenesis (primarily T cell/myeloid disease), raising questions about cell composition or evolving disease concepts.

---

## 4. Validation Priorities

### **Priority 1: IL-36 pathway as therapeutic target**
**Classification:** Therapeutic target  

**Rationale:** IL36A and IL36G show extreme upregulation with the strongest statistical evidence in the dataset. The IL-36/IL-36R axis is mechanistically central to psoriatic inflammation.

**Current dataset evidence:** IL36A (log2FC = 11.37, P = 2.5×10^-102), IL36G (5.68, P = 5.9×10^-94)—among the top upregulated genes.

**External evidence:**  
- Genetic evidence: IL36RN loss-of-function mutations cause generalized pustular psoriasis.  
- Clinical evidence: IL-36 receptor antagonists (spesolimab, imsidolimab) show efficacy in pustular psoriasis clinical trials.  
- Disease-association evidence: IL-36 overexpression consistently reported in psoriatic skin.

**Next validation step:** Confirm IL-36 protein levels via immunohistochemistry in lesional vs. non-lesional skin from the same patients. Assess whether IL-36 correlates with disease severity (PASI score). However, **the existence of IL-36-targeting drugs does not, by itself, prove therapeutic efficacy in this specific patient cohort or psoriasis subtype** (plaque vs. pustular).

**Evidence classification:** Supported hypothesis for therapeutic relevance, though causal role is not proven by transcriptomics alone.

---

### **Priority 2: Kynurenine pathway metabolic checkpoint**
**Classification:** Mechanistic hypothesis  

**Rationale:** KYNU upregulation suggests novel metabolic reprogramming linking inflammation and immune regulation. Less explored than cytokine pathways in psoriasis.

**Current dataset evidence:** KYNU (log2FC = 4.42, P = 7.2×10^-95), AKR1B10 (6.27, P = 1.2×10^-92)—both highly significant and suggest coordinated tryptophan/AhR metabolism.

**External evidence:**  
- Pathway evidence: Kynurenine pathway activated in inflammatory diseases and cancers.  
- Literature evidence: Emerging data link kynurenine to immune tolerance and keratinocyte proliferation, but psoriasis-specific evidence is limited.  
- Conflicting evidence: Kynurenine metabolites can be immunosuppressive (via AhR) or pro-inflammatory (via oxidative stress), so directionality of effect is unclear.

**Next validation step:** Measure kynurenine and kynurenic acid levels in lesional skin and serum. Assess AhR activity via reporter assays or target gene expression. Test whether KYNU inhibition or AhR modulation affects keratinocyte proliferation and cytokine production in ex vivo skin models.

**Evidence classification:** Exploratory hypothesis requiring mechanistic validation.

---

### **Priority 3: Cell composition confounding (neutrophil/T cell infiltration)**
**Classification:** Confounding or composition check  

**Rationale:** Many upregulated genes (S100A8/A12, DEFB4A/B, CXCL13, CD274) may reflect immune cell infiltration rather than keratinocyte reprogramming. Distinguishing cell-type-specific signals is critical for interpreting pathogenic mechanisms.

**Current dataset evidence:** Bulk RNA-seq cannot distinguish keratinocyte, neutrophil, T cell, and dendritic cell contributions.

**External evidence:**  
- Histological evidence: Psoriatic skin contains Munro microabscesses (neutrophil aggregates) and dense dermal T cell infiltrates.  
- Expression evidence: S100A8/A12 are predominantly neutrophil/monocyte markers; CXCL13 may derive from fibroblasts or immune cells.

**Next validation step:**  
1. Perform computational deconvolution (e.g., CIBERSORTx, Bisque) to estimate immune cell proportions.  
2. Validate with immunohistochemistry or single-cell RNA-seq to assign genes to specific cell types.  
3. Compare keratinocyte-specific signatures in single-cell data to bulk RNA-seq results.

**Evidence classification:** Essential confounding check. Without cell-type resolution, conclusions about keratinocyte dysfunction vs. immune infiltration remain ambiguous.

---

### **Priority 4: SPRR/LCE gene cluster coordinated regulation**
**Classification:** Mechanistic hypothesis / Biomarker  

**Rationale:** Seven SPRR2 genes and two LCE3 genes are massively upregulated. These genes cluster at chr1q21.3 epidermal differentiation complex (EDC), suggesting coordinated epigenetic or super-enhancer regulation rather than independent pathway activation.

**Current dataset evidence:** SPRR2A/B/D/E/F/G (5.99–7.32 log2FC), LCE3A/D (8.30, 5.31 log2FC)—all highly significant (P < 10^-70).

**External evidence:**  
- Genomic evidence: EDC locus (chr1q21.3) harbors multiple psoriasis-associated SNPs (GWAS).  
- Epigenetic evidence: Super-enhancers at EDC regulate coordinated gene expression in inflammatory conditions.  
- Disease-association evidence: SPRR and LCE upregulation is a hallmark of psoriasis, but also occurs in wound healing.

**Next validation step:**  
1. Perform chromatin immunoprecipitation (ChIP-seq) for histone marks (H3K27ac) to identify super-enhancers at EDC locus.  
2. Test whether EDC gene expression serves as a quantitative biomarker for disease activity or treatment response.  
3. Use CRISPR interference to test whether suppressing individual SPRR/LCE genes affects keratinocyte phenotypes, or whether the entire locus must be modulated.

**Evidence classification:** Supported hypothesis for coordinated regulation; exploratory hypothesis for individual gene functions. Potential biomarker application requires clinical validation.

---

### **Priority 5: BTC downregulation and EGFR pathway dysfunction**
**Classification:** Mechanistic hypothesis  

**Rationale:** BTC (betacellulin) is the most significantly downregulated gene (log2FC = -4.30, P = 2.4×10^-76). As an EGFR ligand, its downregulation contradicts expectations of hyperproliferative signaling in psoriasis.

**Current dataset evidence:** BTC is the top downregulated gene with high statistical confidence.

**External evidence:**  
- Conflicting evidence: EGFR activation typically promotes keratinocyte proliferation, yet other EGFR ligands (e.g., AREG, EREG) are not significantly downregulated in this dataset (not shown in top 100 genes).  
- Literature evidence: Sparse literature on BTC in psoriasis; role uncertain.  
- Pathway evidence: EGFR pathway is implicated in keratinocyte homeostasis, but specific role of BTC vs. other ligands is unclear.

**Next validation step:**  
1. Measure BTC protein levels to confirm transcriptional downregulation translates to reduced protein.  
2. Test whether exogenous BTC supplementation affects psoriatic keratinocyte proliferation or differentiation in organotypic cultures.  
3. Assess whether BTC downregulation reflects loss of dermal fibroblasts or other stromal cells (cell composition issue) vs. active repression.

**Evidence classification:** Exploratory hypothesis. BTC downregulation is statistically robust but biological significance is unclear. Alternative explanation: BTC may be a bystander effect of tissue remodeling rather than a driver of pathology.

---

## 5. Evidence Grounding Summary

### **IL-36 cytokine program:**
- Direct RNA-seq evidence (current dataset): Extreme upregulation  
- Disease-association evidence: IL36RN mutations → pustular psoriasis  
- Clinical evidence: IL-36R antagonists in trials  
- **Independent convergent evidence from genomics, transcriptomics, and clinical interventions**

### **KYNU/kynurenine pathway:**
- Direct RNA-seq evidence: Strong upregulation  
- Pathway evidence: Tryptophan metabolism  
- Literature evidence: Emerging but limited  
- **Single-source evidence (transcriptomics); mechanistic role requires validation**

### **S100A7/DEFB4 antimicrobial program:**
- Direct RNA-seq evidence: Extreme upregulation  
- Tissue-specific expression evidence: Keratinocyte markers  
- Disease-association evidence: Diagnostic feature of psoriasis  
- Protein interaction evidence: S100A8/A9 heterodimerization  
- **Convergent evidence, but cannot exclude neutrophil contamination without spatial/single-cell data**

### **SPRR/LCE keratinocyte differentiation:**
- Direct RNA-seq evidence: Massive upregulation  
- Genomic evidence: EDC locus GWAS associations  
- Pathway evidence: Cornified envelope formation  
- **Strong evidence, but gene cluster co-regulation may inflate apparent pathway enrichment (genomic proximity confounding)**

### **BTC downregulation:**
- Direct RNA-seq evidence: Significant downregulation  
- Literature evidence: Insufficient  
- **Single-source evidence with unclear biological significance; may reflect cell composition artifact**

### **Conflicting evidence:**
- **CD274 (PD-L1) upregulation:** Clinical evidence shows PD-1/PD-L1 blockade can trigger psoriasis, yet PD-L1 is upregulated in lesional skin. This suggests either: (1) PD-L1 upregulation is insufficient to restrain inflammation, (2) PD-L1 blockade unmasks pre-existing autoreactive T cells, or (3) PD-L1 has context-dependent pro-inflammatory functions. **Insufficient evidence to resolve this paradox.**

---

## 6. Limitations and Alternative Explanations

### **Limitation 1: Immune cell infiltration confounding**
Psoriatic lesions contain dense neutrophil, T cell, and dendritic cell infiltrates. Many upregulated genes (S100A8/A12, CXCL13, CD274, PRKCQ) are immune cell markers. Bulk RNA-seq cannot distinguish whether these signals reflect:
- Keratinocyte reprogramming  
- Immune cell infiltration  
- Dermal fibroblast or endothelial changes  

**Impact:** Overinterpretation of keratinocyte-intrinsic pathology when signals derive from infiltrating cells.

**Mitigation:** Perform computational deconvolution (e.g., CIBERSORTx with reference immune cell signatures). Validate with immunohistochemistry or single-cell RNA-seq. Compare keratinoc
