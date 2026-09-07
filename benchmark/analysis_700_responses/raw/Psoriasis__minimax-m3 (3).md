# psoriasis - minimax-m3

- Benchmark system: raw
- Repeat: 5
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
- Model API: MiniMax / minimax-m3
- Message SHA-256: d1a33d3f606c81814c4fb94a6c63c8f1abebd3bde37d769e82eae4772d8ff873
- Response HTTP status: 200
- Prompt tokens: 4054
- Completion tokens: 8271
- Reasoning tokens: 
- Total tokens: 12325
- API requests reported: 
- Elapsed seconds: 44.143
- Final benchmark system: raw; file rank 3/5; original repeat 5; model vendor: MiniMax

---
<think>The user wants a comprehensive transcriptomic analysis of psoriatic lesional skin vs normal control skin. Let me analyze the gene list carefully.

Let me categorize the genes into functional groups:

**Upregulated genes (log2FC > 0):**

1. **IL-1 family cytokines (IL-36 axis):**
- IL36A (log2FC 11.37) - extremely high
- IL36G (log2FC 5.68)
- IL36RN (log2FC 3.00) - IL-36 receptor antagonist (interesting that it's also up)
- IL19 (log2FC 7.58)
- IL20 (log2FC 5.67)
- IL26 (log2FC 4.36)

2. **Antimicrobial peptides (AMPs):**
- DEFB4A (log2FC 11.18)
- DEFB4B (log2FC 11.03)
- DEFB103A (log2FC 5.76)
- DEFB103B (log2FC 5.75)
- S100A7 (log2FC 7.09) - psoriasin
- S100A7A (log2FC 9.83)
- S100A8 (log2FC 7.73)
- S100A12 (log2FC 8.33)
- PI3 (log2FC 9.24) - elafin
- SPRR2A, 2B, 2D, 2E, 2F, 2G (small proline-rich proteins)

3. **Keratin/cornified envelope:**
- KRT6A (log2FC 4.30)
- LCE3A (log2FC 8.30)
- LCE3D (log2FC 5.31)
- SPRR family
- GJB2 (Connexin 26, log2FC 4.42)
- GJB6 (Connexin 30, log2FC 3.02)

4. **NF-κB / TNF signaling:**
- TNIP3 (log2FC 7.28) - TNF alpha induced protein 3 interacting protein 3 (negative regulator of NF-κB)
- ZC3H12A (log2FC 3.85) - MCPIP1, RNase
- IRAK2 (log2FC 2.08)
- PRKCQ (log2FC 2.88) - PKCθ
- TRIM15, TRIM10

5. **Lipid metabolism:**
- FABP5 (log2FC 3.64)
- PLA2G4D (log2FC 4.61)
- PLA2G4E (log2FC 2.47)
- AKR1B10 (log2FC 6.27)
- AKR1B15 (log2FC 5.23)
- CYP2W1 (log2FC -4.70) - downregulated
- TCN1 (log2FC 8.04)

6. **Cell cycle/proliferation:**
- CCNE1 (log2FC 2.56)
- RRM2 (log2FC 2.72)
- CDK5R1 (log2FC 2.35)

7. **Chemokines/GPCR signaling:**
- CXCL13 (log2FC 5.89)
- CXCR2 (log2FC 2.70)
- GPR15LG (log2FC 5.52)
- HRH2 (log2FC 3.27)
- S1PR-related (GPR15LG)

8. **Other:**
- KYNU (log2FC 4.42) - kynureninase, tryptophan metabolism
- HPSE (log2FC 2.92) - heparanase
- SERPINB3/B4/B11/B13 - serine protease inhibitors
- KLK13 (log2FC 4.05) - kallikrein
- HABP2 (log2FC 4.19)
- HEPHL1 (log2FC 6.33)
- WNT5A (log2FC 2.53) - non-canonical Wnt
- BMAL2 (log2FC 2.21)
- PRSS27 (log2FC 4.24)
- TPBG (log2FC 1.86)
- GDA (log2FC 5.90) - guanine deaminase
- CD274 (log2FC 3.44) - PD-L1
- ENKUR (log2FC 4.88)
- MPZL2 (log2FC 2.51)
- RHCG (log2FC 5.29)
- SLC6A14 (log2FC 4.47) - amino acid transporter
- ADAP2 (log2FC 2.09)
- ADGRF1 (log2FC 6.64) - adhesion GPCR
- TMPRSS11D (log2FC 7.75) - transmembrane protease
- FAM110C
- TTC39A
- ARSF
- CT69
- LINC genes (non-coding)
- LOC genes

**Downregulated genes (log2FC < 0):**
- LOC107984452 (-6.25)
- BTC (-4.30) - betacellulin
- LOC105371988 (-4.10)
- CYP2W1 (-4.70)
- LINC02660 (-3.90)
- LOC107984005 (-4.27)
- SAPCD1 (-2.94)
- UGT3A2 (-4.59)
- WAKMAR1 (-5.63)
- SAPCD1-AS1 (-2.84)

Note: Many of the downregulated "genes" are actually LOC/lncRNA identifiers and may not have well-established functions. BTC is a notable downregulated gene (ErbB ligand).

Let me now structure the analysis:

## Overall Biological Interpretation

The transcriptomic profile of psoriatic lesional skin reveals a hyperinflammatory, hyperproliferative epidermal state dominated by:

1. **Hyperactivation of the IL-36/IL-1 axis** with massive upregulation of IL36A/G (with IL36RN feedback), IL19, IL20, IL26 - these are keratinocyte-derived cytokines that drive feedforward inflammation.

2. **Massive antimicrobial peptide (AMP) response** - DEFB4A/B, S100A7/A7A/A8/A12, PI3 - canonical "psoriasis signature"

3. **Abnormal keratinocyte differentiation** - SPRR2 family, LCE3A/D, KRT6A, GJB2/6 - indicating defective cornified envelope formation

4. **NF-κB hyperactivation** with negative feedback - TNIP3, ZC3H12A

5. **Lipid metabolism rewiring** - PLA2G4D/E, AKR1B10/15, FABP5

6. **Th17/Th22 chemokines** - CXCL13, GPR15LG

Let me structure this properly:

## Core Biological Programs (max 5)

1. **IL-36 / IL-1 axis amplification and autocrine keratinocyte cytokine storm**
2. **Antimicrobial peptide and barrier defense response**
3. **NF-κB hyperactivation with negative feedback regulation**
4. **Abnormal epidermal differentiation and cornified envelope**
5. **Lipid metabolic reprogramming and arachidonic acid signaling**

Or alternatively, I could choose:
1. IL-36/IL-1 cytokine amplification
2. AMP/barrier defense
3. NF-κB signaling
4. Epidermal differentiation
5. Lipid mediator signaling (PLA2/AKR)

## Key Genes (max 10)

- IL36A (most upregulated, IL-36α)
- DEFB4A/B
- S100A7/A8/A12
- KYNU
- TNIP3
- AKR1B10
- IL19/IL20
- CXCL13
- PLA2G4D
- SPRR2A

## Validation Priorities

1. IL-36 axis as therapeutic target (mechanistic/therapeutic)
2. KYNU-aryl hydrocarbon receptor axis
3. AKR1B10 as biomarker
4. CXCL13 in psoriatic B cell/T cell recruitment
5. PLA2G4D lipid mediator signaling

Let me now write the full response with careful evidence grounding.

Actually, let me re-examine the data more carefully:

**Cytokines:**
- IL36A (11.37) - IL-36α
- IL36G (5.68) - IL-36γ
- IL36RN (3.00) - IL-36Ra (antagonist, upregulated as feedback)
- IL19 (7.58) - keratinocyte-derived IL-10 family
- IL20 (5.67) - keratinocyte-derived IL-10 family
- IL26 (4.36) - Th17 cytokine

**AMPs:**
- DEFB4A (11.18) - β-defensin 2
- DEFB4B (11.03) - β-defensin 2 (paralog)
- DEFB103A (5.76), DEFB103B (5.75) - β-defensin 3
- S100A7 (7.09) - psoriasin
- S100A7A (9.83) - psoriasin 2
- S100A8 (7.73) - calprotectin component
- S100A12 (8.33) - calgranulin C
- PI3 (9.24) - elafin/SKALP

**Cornified envelope:**
- SPRR2A/B/D/E/F/G (3.99-7.31)
- LCE3A/D (5.31-8.30)
- KRT6A (4.30)
- GJB2/6 (connexins)

**NF-κB pathway & negative regulators:**
- TNIP3 (7.28) - TNFAIP3-interacting protein 3, terminates NF-κB
- ZC3H12A (3.85) - MCPIP1, RNase that degrades cytokine mRNAs
- IRAK2 (2.08) - IL-1R-associated kinase 2
- PRKCQ (2.88) - PKCθ (T cell signaling)
- TRIM15, TRIM10

**Lipid metabolism:**
- FABP5 (3.64) - fatty acid binding protein
- PLA2G4D (4.61) - phospholipase
- PLA2G4E (2.47) - phospholipase
- AKR1B10 (6.27) - aldo-keto reductase
- AKR1B15 (5.23) - aldo-keto reductase
- CYP2W1 (-4.70) - downregulated

**Amino acid metabolism:**
- KYNU (4.42) - kynureninase (Trp → kynurenine)
- GDA (5.90) - guanine deaminase
- SLC6A14 (4.47) - amino acid transporter
- TCN1 (8.04) - transcobalamin 1 (cobalamin binding)

**T cell / chemokine:**
- CXCL13 (5.89) - B cell / Tfh chemokine
- GPR15LG (5.52)
- CXCR2 (2.70)
- CD274 (3.44) - PD-L1

**Cell proliferation:**
- CCNE1 (2.56) - cyclin E1
- RRM2 (2.72) - ribonucleotide reductase
- CDK5R1 (2.35)

**Proteases/inhibitors:**
- SERPINB3 (6.74), SERPINB4 (9.12), SERPINB11 (4.47), SERPINB13 (3.09)
- KLK13 (4.05) - kallikrein
- HABP2 (4.19)
- TMPRSS11D (7.75)
- PRSS27 (4.24)
- HPSE (2.92) - heparanase

**Other:**
- WNT5A (2.53) - non-canonical Wnt
- HRH2 (3.27) - histamine H2 receptor
- KCNK10 (3.84) - potassium channel
- ADGRF1 (6.64) - adhesion GPCR
- BMAL2 (2.21) - circadian
- GPR15LG
- HEPHL1 (6.33)
- ENKUR (4.88)
- RHCG (5.29)
- MPZL2 (2.51)
- VNN3P (8.28) - pseudogene of vanin

**Downregulated:**
- BTC (-4.30) - betacellulin (ErbB ligand)
- CYP2W1 (-4.70)
- WAKMAR1 (-5.63) - lncRNA
- Others are mostly LOC/lncRNA

Now let me think about the **hallmark features of psoriasis** based on these genes:

1. The IL-23/IL-17/IL-22 axis is suggested indirectly through IL-19, IL-20, IL-36A/G (these are induced by IL-17/IL-22), S100A7/8/9, DEFB4A, KRT6A, LCE3, SPRR2. So while IL-17A itself isn't in the top hits, the downstream effectors are massively upregulated, consistent with IL-17/IL-22-driven inflammation.

2. The IL-36 amplification loop (IL36A, IL36G, IL36RN) is very prominent - this is a known feedforward loop in psoriasis that amplifies keratinocyte inflammation.

3. KYNU upregulation connects to tryptophan-kynurenine-aryl hydrocarbon receptor (AhR) axis, which has been implicated in psoriasis.

4. PD-L1 (CD274) upregulation is notable - keratinocytes can express PD-L1 in psoriasis.

5. The lipid metabolism axis (PLA2G4D, AKR1B10, FABP5) connects to eicosanoid signaling.

Now let me write the comprehensive analysis. I'll aim for thoroughness and accuracy.

Let me structure my response with the appropriate sections and ensure it's evidence-grounded.

Actually, I need to note - the dataset only shows ~100 genes (those shown are the top DEGs). The user did not provide the full list. So I should focus on what's given.

Let me count: looks like ~110 genes total in the table.

Now let me write the response. I should be:
1. Thorough but not bloated
2. Evidence-grounded
3. Honest about limitations
4. Distinguishing direct evidence from inference
5. Not overclaiming

Let me draft now.</think>

# Multidimensional Transcriptomic Interpretation: Psoriatic Lesional Skin vs. Normal Skin

## 1. Overall Biological Interpretation

The provided differentially expressed gene (DEG) set, despite being limited to the top-ranked genes, captures the canonical molecular "fingerprint" of psoriatic lesional epidermis with unusual clarity. Three overlapping but biologically distinguishable themes dominate:

**(a) An IL-36–driven keratinocyte cytokine amplification loop.** The most strongly upregulated genes include *IL36A* (log2FC ≈ 11.4), *IL36G* (≈ 5.7), and *IL36RN* (≈ 3.0), accompanied by the IL-10-family keratinocyte cytokines *IL19* and *IL20*. This pattern is the hallmark of an autocrine feedforward circuit in which IL-36 agonizes its own receptors on keratinocytes, driving *IL19/IL20*, AMPs, and chemokines. *IL36RN* upregulation is best interpreted as a partially effective compensatory brake rather than a corrective response, since IL-36RN is intrinsically a weak antagonist in skin.

**(b) Massive antimicrobial peptide (AMP) and alarmins production.** *DEFB4A/B* (β-defensin 2), *DEFB103A/B* (β-defensin 3), *S100A7/A7A* (psoriasin family), *S100A8* and *S100A12* (calprotectin/calgranulin), and *PI3* (elafin) are all in the top 10 by effect size. These are direct transcriptional targets of IL-17A/IL-22 and IL-36 signaling in keratinocytes and constitute the molecular signature historically used to distinguish psoriatic from healthy or eczematous skin.

**(c) Distorted epidermal terminal differentiation and barrier remodeling.** Co-ordinated upregulation of small proline-rich proteins (*SPRR2A/B/D/E/F/G*), late cornified envelope proteins (*LCE3A/D*), hyperproliferation-associated keratin *KRT6A*, and connexins *GJB2/GJB6* indicates a profound shift from homeostatic to "wound-healing/psoriasiform" differentiation, accompanied by serine/cysteine protease and protease-inhibitor imbalance (*SERPINB3/B4/B11/B13*, *KLK13*, *TMPRSS11D*, *PRSS27*).

Subordinate but biologically informative signals include NF-κB negative-feedback engagement (*TNIP3*, *ZC3H12A*), lipid-mediator pathway activation (*PLA2G4D/E*, *AKR1B10/B15*, *FABP5*), tryptophan-kynurenine pathway induction (*KYNU*), and recruitment of adaptive immune cells (*CXCL13*, *CD274*/PD-L1, *GPR15LG*). The downregulated set is dominated by non-annotated loci and *BTC* (betacellulin) and likely reflects, in part, suppression of certain ErbB-family growth signals and possibly lncRNA context-dependent effects; they do not, on their own, point to a coherent counter-program.

## 2. Core Biological Programs

### Program 1 — IL-36 / IL-1 axis amplification and autocrine keratinocyte cytokine storm
- **Direction:** Upregulated.
- **Major supporting genes:** *IL36A*, *IL36G*, *IL36RN*, *IL19*, *IL20*, *IL26*, *GJB2*, *CXCL13*.
- **Best-matching pathways:** Reactome "Interleukin-36 signaling" (R-HSA-9014823), GO:0006954 inflammatory response, Hallmark "Inflammatory response."
- **Interpretation:** The simultaneous upregulation of two IL-36 agonists (α, γ) and the receptor antagonist suggests strong pathway activation with attempted feedback. *IL19* and *IL20* are well-established IL-36-induced keratinocyte cytokines that further amplify STAT3 signaling and reinforce aberrant differentiation.
- **Evidence strength:** Strong — multi-gene concordance within a single pathway, with very large effect sizes (log2FC up to 11).
- **Limitations:** The upstream trigger (IL-17A/IL-22 from T cells vs. keratinocyte-intrinsic danger signals) cannot be resolved from this dataset alone. *IL36RN* being upregulated does not prove functional pathway suppression; the antagonist is known to be weak in psoriatic epidermis.

### Program 2 — Antimicrobial peptide and alarmin response
- **Direction:** Upregulated.
- **Major supporting genes:** *DEFB4A*, *DEFB4B*, *DEFB103A*, *DEFB103B*, *S100A7*, *S100A7A*, *S100A8*, *S100A12*, *PI3*.
- **Best-matching pathways:** Reactome "Antimicrobial peptides" (R-HSA-6803157), GO:0042742 defense response to bacterium, Hallmark "Inflammatory response."
- **Interpretation:** These genes are direct transcriptional outputs of IL-17A/IL-22/IL-36 signaling in keratinocytes. Their concordant, very large induction indicates that the IL-17/IL-22 axis is functionally active in the lesional samples even though *IL17A* and *IL22* themselves are not in the top DEG list (likely because they are produced by infiltrating lymphocytes at lower absolute abundance).
- **Evidence strength:** Very strong — eight genes, all with log2FC ≥ 5.7, all canonical psoriasis AMP markers.
- **Limitations:** AMPs also respond to barrier disruption and microbial cues independently of IL-17, so their upregulation is necessary but not sufficient evidence of Th17 polarization.

### Program 3 — Aberrant epidermal differentiation and cornified envelope remodeling
- **Direction:** Upregulated.
- **Major supporting genes:** *SPRR2A*, *SPRR2B*, *SPRR2D*, *SPRR2E*, *SPRR2F*, *SPRR2G*, *LCE3A*, *LCE3D*, *KRT6A*, *GJB2*, *GJB6*, *SERPINB3*, *SERPINB4*, *SERPINB11*, *SERPINB13*, *KLK13*, *TMPRSS11D*, *PRSS27*.
- **Best-matching pathways:** GO:0031424 keratinization, Reactome "Keratinization" (R-HSA-6805567), KEGG "Cornified envelope" (not available as standalone KEGG set but overlaps).
- **Interpretation:** Coordinated upregulation of SPRR2 paralogues, LCE3 family, KRT6A, and gap-junction components reflects the wound-healing/psoriasiform differentiation program that replaces the normal granular layer differentiation. The SERPINB family expansion indicates altered protease–antiprotease balance on the skin surface.
- **Evidence strength:** Strong — multiple independent gene families converging on the same biological module.
- **Limitations:** "Differentiation" gene panels in psoriasis are partly a secondary consequence of inflammation rather than primary drivers; the dataset cannot disambiguate cause from consequence.

### Program 4 — NF-κB hyperactivation with negative-feedback engagement
- **Direction:** Upregulated (with negative regulators also induced).
- **Major supporting genes:** *TNIP3*, *ZC3H12A*, *IRAK2*, *PRKCQ*, *TRIM10*, *TRIM15*, *PLA2G4D*.
- **Best-matching pathways:** Reactome "NF-κB activation" (R-HSA-9756987), Hallmark "TNFA signaling via NF-κB."
- **Interpretation:** The induction of NF-κB inhibitors/negative regulators (*TNIP3*, *ZC3H12A*) alongside pathway components (*IRAK2*, *PLA2G4D*, *PRKCQ*) is a textbook signature of an inflammatory system that is being driven hard but is also attempting self-limitation. *TNIP3* in particular is a direct NF-κB target and a known psoriasis susceptibility gene.
- **Evidence strength:** Moderate-to-strong — the program is consistent, but most direct NF-κB readouts (e.g., phospho-p65) require protein-level assays.
- **Limitations:** Transcriptional activation of negative regulators does not imply effective functional restraint; NF-κB may remain hyperactive in psoriasis despite these brakes.

### Program 5 — Lipid-mediator metabolic rewiring
- **Direction:** Predominantly upregulated; *CYP2W1* downregulated.
- **Major supporting genes:** *PLA2G4D*, *PLA2G4E*, *AKR1B10*, *AKR1B15*, *FABP5*, *SLC6A14*, *KYNU*, *GDA*; down: *CYP2W1*.
- **Best-matching pathways:** KEGG "Arachidonic acid metabolism" (hsa00590), Reactome "Synthesis of leukotrienes and lipoxins," Hallmark "Fatty acid metabolism."
- **Interpretation:** *PLA2G4D* liberates arachidonic acid; *AKR1B10/15* are aldo-keto reductases that metabolize lipid aldehydes and inflammatory carbonyls; *FABP5* delivers fatty acids to nuclear receptors (PPARβ/δ). *KYNU* activation diverts tryptophan into the kynurenine pathway, producing ligands for AhR — a pathway with both pro- and anti-inflammatory roles in skin. *SLC6A14* (ATB⁰⁺) is an amino-acid transporter supplying arginine/tryptophan to proliferating keratinocytes.
- **Evidence strength:** Moderate — gene-set consistent but functional contribution to lesional inflammation is less well characterized than Programs 1–3.
- **Limitations:** *CYP2W1* downregulation is a single negative signal of unclear mechanistic significance. CYP/AKR enzymes have overlapping substrates, so transcript changes may not reflect net mediator flux.

## 3. Key Genes and Interaction Modules

1. ***IL36A*** (log2FC 11.37, FDR ≈ 1.7e-98). Central node of Program 1; its secretion by keratinocytes initiates autocrine IL-36R signaling and downstream AMP, chemokine, and differentiation programs. *Interaction type:* ligand–receptor (IL-36R/IL-1RL2); pathway co-membership with *IL36G*; literature co-occurrence with *IL19/IL20*.

2. ***DEFB4A/B*** (log2FC 11.18 / 11.03). Principal β-defensin 2 paralogues; canonical IL-17A target. *Interaction type:* pathway co-membership (IL-17/IL-22 → DEFB4); co-expression with *S100A7*, *KRT6A*.

3. ***S100A7/A7A/A8/A12*** (log2FC 7.1–9.8). Multifunctional alarmins/AMPs. *S100A8/A12* form calprotectin (heterodimer; direct physical interaction supported by extensive biochemistry), drive neutrophil and monocyte recruitment. *S100A7/A7A* act as keratinocyte autocrine amplifiers via RAGE. *Interaction type:* direct physical interaction (S100A8+S100A12); pathway co-membership; literature-co-occurrence.

4. ***TNIP3*** (log2FC 7.28). A20-binding inhibitor of NF-κB; genetic-variant-supported psoriasis gene (TNIP3/ABIN-3). *Interaction type:* protein interaction (binds A20/TNFAIP3); regulatory node of Program 4. Single-gene importance outweighed here by being a convergence point between GWAS signal and transcriptomic program.

5. ***KYNU*** (log2FC 4.42). Kynureninase, second step of the kynurenine pathway; reduces tryptophan availability and produces 3-hydroxyanthranilic acid, an AhR ligand. Connects to Program 5. *Interaction type:* metabolic-pathway co-membership with *IDO1/TDO2* (not in this dataset) and AhR signaling.

6. ***AKR1B10*** (log2FC 6.27). Aldo-keto reductase detoxifying reactive carbonyls and lipid peroxidation products; implicated in keratinocyte hyperproliferation and IL-17A–driven responses. *Interaction type:* pathway co-membership with lipid-mediator metabolism; co-expression with *SPRR* family in published psoriasis datasets.

7. ***CXCL13*** (log2FC 5.89). The defining chemokine for B cells and T follicular helper-like cells. Its presence in lesional epidermis is a strong indicator of lymphoid aggregate / ectopic lymphoid structure formation, increasingly recognized in chronic plaque psoriasis. *Interaction type:* ligand–receptor (CXCR5); co-membership with Program 1 cytokine outputs.

8. ***PLA2G4D*** (log2FC 4.61). Cytosolic phospholipase A2 isoform preferentially expressed in keratinocytes; produces arachidonic acid for eicosanoid synthesis; genetic-variant-supported psoriasis gene (PLA2G4D). *Interaction type:* pathway co-membership with *AKR1B10* and eicosanoid pathway; genetic-disease association.

9. ***IL19/IL20*** (log2FC 7.58 / 5.67). IL-10 family keratinocyte cytokines. Signal through IL-20R1/IL-20R2, drive STAT3 and amplify aberrant differentiation. *Interaction type:* receptor-ligand (IL-20R); pathway co-membership with IL-36 outputs.

10. ***CD274* (PD-L1)** (log2FC 3.44). Immune checkpoint ligand induced by IFN-γ and, in keratinocytes, by inflammatory cytokines. Its upregulation in lesional skin may reflect a tissue-protective negative-feedback program; chronic PD-L1 expression on keratinocytes may locally inhibit T-cell effector function. *Interaction type:* ligand–receptor (PD-1); pathway co-membership with T-cell infiltration signatures.

A note on interactions: the present dataset is bulk transcriptomic and does not provide physical-interaction evidence. Statements above classify relationships by pathway or literature-derived category; none of the listed interactions should be read as directly demonstrated by this RNA-seq table.

## 5. Validation Priorities

### 1. IL-36 axis as a therapeutic target — **Therapeutic target / mechanistic hypothesis**
- **Why prioritization:** *IL36A/G* are the two most strongly induced cytokine genes in the dataset; pharmacological IL-36R blockade (e.g., spesolimab) has already shown efficacy in generalized pustular psoriasis and is being explored in plaque psoriasis. This transcriptomic profile predicts that the pathway is centrally active.
- **Evidence from dataset:** Direct, very large upregulation of IL36A/G plus concordant induction of their downstream targets (DEFB4, S100A7, KRT6A, IL19/20).
- **External evidence:** Established genetic associations (e.g., *IL36RN* mutations in DITRA), positive clinical trial data for IL-36R antagonists in pustular disease; mechanism reproduced in IL-36A-overexpressing mouse models.
- **Next step:** Stratify lesional biopsies by IL36A mRNA or protein abundance and correlate with response to IL-23, IL-17, and IL-36R blockade.
- **Conclusion status:** **Supported hypothesis** — pathway is clearly active; whether IL-36R inhibition will outperform IL-23/IL-17 blockade in plaque psoriasis remains **exploratory**.

### 2. *KYNU* / kynurenine pathway activation as a biomarker and AhR-linked mechanism — **Biomarker / mechanistic hypothesis**
- **Why prioritization:** *KYNU* is the only clearly metabolic enzyme with very large fold change; it integrates with *SLC6A14* (amino-acid uptake) and *GDA*. The kynurenine/AhR axis is a recognized but underexplored therapeutic angle.
- **Evidence from dataset:** Direct *KYNU* upregulation with concordant amino-acid transporter (*SLC6A14*) induction.
- **External evidence:** *IDO1/KYNU* induction has been described in psoriatic skin; AhR ligands (e.g., tapinarof) are clinically active in psoriasis.
- **Next step:** Quantify lesional kynurenine/tryptophan ratios by mass spectrometry and correlate with *KYNU* mRNA; test whether tapinarof response correlates with baseline *KYNU* expression.
- **Conclusion status:** **Supported hypothesis**.

### 3. *AKR1B10* as a stratum-corneum / serum biomarker of lesional activity — **Biomarker**
- **Why prioritization:** Among the largest fold changes for a metabolic enzyme; AKR1B10 protein is measurable in serum and may be psoriasis-associated.
- **Evidence from dataset:** log2FC ≈ 6.27, FDR < 1e-89, concordant with *AKR1B15* and lipid-mediator pathway.
- **External evidence:** Elevated AKR1B10 reported in lesional psoriatic epidermis and proposed as a biomarker.
- **Next step:** Measure serum AKR1B10 by ELISA in plaque psoriasis vs. controls and correlate with PASI.
- **Conclusion status:** **Exploratory hypothesis** for biomarker use; **supported hypothesis** that it is transcriptionally induced in lesions.

### 4. *CXCL13* and ectopic lymphoid-neogenesis as a chronicity mechanism — **Mechanistic / interaction-network hypothesis**
- **Why prioritization:** *CXCL13* is the canonical B-cell-zone chemokine; its presence in lesional epidermis suggests lymphoid aggregates contributing to chronicity, which has implications for B-cell–directed therapies.
- **Evidence from dataset:** *CXCL13* log2FC ≈ 5.89, concordant with *CD274* (PD-L1) and immune-cell-recruitment signals.
- **External evidence:** CXCL13-positive lymphoid aggregates described in chronic psoriatic plaques.
- **Next step:** Immunohistochemistry for CD20/CD3/CXCL13 in lesional biopsies and correlation with disease chronicity/severity.
- **Conclusion status:** **Supported hypothesis**.

### 5. *BTC* (betacellulin) downregulation as a feedback brake on hyperproliferation — **Mechanistic hypothesis / composition check**
- **Why prioritization:** *BTC* is the only well-annotated downregulated gene (log2FC ≈ −4.3); it is an ErbB-family ligand. Its loss may represent a compensatory brake on EGFR/MAPK signaling in hyperproliferative epidermis or, alternatively, a compositional shift.
- **Evidence from dataset:** Direct downregulation at genome-wide significance.
- **External evidence:** EGFR pathway modulation occurs in psoriasis but BTC-specific roles are less characterized.
- **Next step:** Assess phospho-EGFR/ERBB signaling in lesional vs. normal epidermis and test whether recombinant betacellulin modifies keratinocyte proliferation in vitro.
- **Conclusion status:** **Exploratory hypothesis**.

### 6. (Optional) PD-L1 / keratinocyte immune-checkpoint expression — **Interaction/network hypothesis**
- *CD274* upregulation in keratinocytes (log2FC ≈ 3.44) may indicate a tissue-intrinsic checkpoint; this has therapeutic implications for combination strategies.

## 6. Evidence Grounding

| Conclusion | Evidence type | Independence |
|---|---|---|
| IL-36 amplification | Direct (IL36A/G/RN induction); pathway (Reactome); GWAS (IL36RN in pustular psoriasis); therapeutic (anti-IL-36R drugs) | Multiple independent sources — genetic, transcriptomic, pharmacological |
| AMP response | Direct (multi-gene induction); canonical psoriasis literature; IL-17/IL-22 mechanistic studies | Multiple independent sources |
| SPRR/LCE differentiation shift | Direct; GO keratinization; published IHC | Direct + curated pathway + literature — partially overlapping |
| NF-κB negative feedback | Direct (TNIP3, ZC3H12A); GWAS (TNIP3); published | Genetic and transcriptomic partly converge via the same gene |
| KYNU/AKR lipid-metabolic module | Direct; partial external literature | Weaker: transcriptomic evidence stronger than independent functional evidence |
| CXCL13 / lymphoid aggregates | Direct; some published IHC | Transcript + IHC concordant but limited |
| BTC downregulation | Direct only | Single source; **insufficient evidence** for any functional claim beyond correlation |

## 7. Limitations and Alternative Explanations

1. **Tissue composition (infiltrating immune cells vs. keratinocyte-autonomous signals).** Many of the top genes (*CXCL13*, *IL26*, *IL19/20*, AMPs) can originate from either keratinocytes or infiltrating lymphocytes. The dataset cannot distinguish cell-of-origin without single-cell or spatial transcriptomics. This affects interpretation of Programs 1, 2, and the *CXCL13* finding in particular.

2. **Bulk RNA obscuring cell-type-specific direction.** Some "upregulation" of NF-κB inhibitors (*TNIP3*, *ZC3H12A*) might reflect enrichment of cells that intrinsically express them (e.g., neutrophils), rather than induction within keratinocytes.

3. **Lesional vs. non-lesional comparison vs. healthy skin.** The data compare lesional to normal, which conflates disease presence with chronic inflammation, barrier disruption, and microbial colonization. Non-lesional psoriatic skin comparisons would help separate intrinsic disease biology from secondary inflammation.

4. **Absence of treatment exposure information.** Many psoriasis-relevant genes (e.g., *IL36A*, *DEFB4A*, *KYNU*, *AKR1B10*) are highly treatment-responsive; if some samples were taken during or shortly after therapy, effect sizes are attenuated and directionality may shift for certain genes.

5. **Functional ambiguity of non-coding / poorly annotated loci.** A meaningful fraction of the "downregulated" set consists of LOC/lncRNA identifiers (*LOC107984452*, *WAKMAR1*, *LINC02660*, etc.) whose biology is uncharacterized. These should not be used to argue for a coherent counter-program.

6. **Association vs. causation.** Genes in Programs 1 and 4 may be passengers driven by IL-17A/IL-22/IFN-γ rather than drivers of disease. Discriminating drivers from passengers requires functional perturbation (CRISPR, neutralizing antibodies in organoids or mouse models).

7. **Batch / platform effects.** Although FDR values are extremely small, the absence of explicit batch-correction information and the very wide range of fold changes raise the possibility that some extreme outliers (e.g., *IL36A*, *DEFB4A/B*, *IL36A*) are partly amplified by technical factors. Independent datasets (e.g., GSE13355, GSE14905) should be used to confirm.

---

**Bottom line.** The provided top DEGs recapitulate the established core of psoriatic lesional biology — an IL-17A/IL-22/IL-36-driven keratinocyte program producing AMPs, alarmins, and a wound-healing differentiation shift, overlaid on NF-κB hyperactivation and metabolic rewiring (kynurenine, AKR, PLA2). The strongest novel mechanistic leads supported by this dataset are **(i)** the centrality of the IL-36 amplification loop, **(ii)** *KYNU*/kynurenine-AhR axis activity, **(iii)** *CXCL13*–driven lymphoid-neogenesis, and **(iv)** the *AKR1B10*-driven lipid-carbonyl metabolic program. All therapeutic-target claims should be treated as **supported hypotheses**, not as established causal mechanisms, and require functional validation.
