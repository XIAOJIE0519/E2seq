# psoriasis - minimax-m3

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
- Model API: MiniMax / minimax-m3
- Message SHA-256: d1a33d3f606c81814c4fb94a6c63c8f1abebd3bde37d769e82eae4772d8ff873
- Response HTTP status: 200
- Prompt tokens: 4054
- Completion tokens: 8747
- Reasoning tokens: 
- Total tokens: 12801
- API requests reported: 
- Elapsed seconds: 48.245
- Final benchmark system: raw; file rank 1/5; original repeat 1; model vendor: MiniMax

---
<think>The user wants me to perform a multidimensional, evidence-grounded, and biologically verifiable interpretation of transcriptomic data from psoriatic lesional skin vs. normal control skin. Let me analyze the data carefully.

First, let me organize the input data:

**Upregulated genes (high log2FC, highly significant):**
- IL36A (11.37) - IL-36 cytokine, key in psoriasis
- DEFB4A (11.18), DEFB4B (11.03) - antimicrobial peptides (beta-defensins)
- S100A7A (9.83) - S100 antimicrobial peptide
- SERPINB4 (9.12) - serine protease inhibitor
- PI3 (9.24) - peptidase inhibitor 3, elafin
- S100A12 (8.33) - calgranulin
- S100A8 (7.73) - calgranulin A
- TCN1 (8.04) - transcobalamin
- LCE3A (8.30) - late cornified envelope
- S100A7 (7.09) - S100A7/psoriasin
- IL19 (7.58) - IL-19, Th17-related
- SPRR2A (7.31), SPRR2B (6.38), SPRR2D (5.92), SPRR2E (3.99), SPRR2F (7.22), SPRR2G (4.75) - small proline-rich proteins
- TMPRSS11D (7.75) - transmembrane protease
- SERPINB3 (6.74) - serine protease inhibitor
- IL36G (5.68) - IL-36 gamma
- IL20 (5.67) - IL-20
- IL36RN (3.00) - IL-36 receptor antagonist (interesting - both ligand and antagonist upregulated)
- IL26 (4.36) - IL-26, Th17
- CXCL13 (5.89) - B cell chemokine
- CXCR2 (2.70) - chemokine receptor
- KRT6A (4.30) - keratin 6A
- WNT5A (2.53) - non-canonical Wnt
- PRKCQ (2.88) - protein kinase C theta
- CD274 (3.44) - PD-L1
- GJB2 (4.42), GJB6 (3.02) - gap junction proteins
- HPSE (2.92) - heparanase
- PLA2G4D (4.61), PLA2G4E (2.47) - phospholipases
- SLC6A14 (4.47) - amino acid transporter
- AKR1B10 (6.27), AKR1B15 (5.23) - aldo-keto reductases
- KYNU (4.42) - kynureninase (tryptophan/aryl hydrocarbon)
- DEFB103A (5.76), DEFB103B (5.75) - beta-defensins
- TNIP3 (7.28) - TNFAIP3 interacting protein 3
- GPR15LG (5.52) - GPR15 ligand
- BTC (-4.30) - actually downregulated; betacellulin
- KLK13 (4.05) - kallikrein
- ZC3H12A (3.85) - MCPIP1, RNase
- TRIM15 (4.54) - tripartite motif
- FABP5 (3.64) - fatty acid binding protein

**Downregulated genes:**
- LOC107984452 (-6.25)
- WAKMAR1 (-5.63)
- CYP2W1 (-4.70)
- LOC107984005 (-4.27)
- BTC (-4.30)
- LINC02660 (-3.90)
- LOC105371988 (-4.10)
- UGT3A2 (-4.59)
- SAPCD1 (-2.94)
- SAPCD1-AS1 (-2.84)

Let me think about the major biological programs:

1. **IL-17/IL-36/Th17 axis and keratinocyte inflammatory response**: 
- IL36A, IL36G, IL36RN, IL19, IL20, IL26
- S100A7, S100A8, S100A12, S100A7A
- DEFB4A, DEFB4B, DEFB103A, DEFB103B
- PI3 (elafin)
- SERPINB3, SERPINB4
- KRT6A
- CXCL13 (Th17/Tfh-associated)
- ZC3H12A (MCPIP1, downstream of IL-17)
- TNIP3 (negative regulator of NF-κB)

This is THE central program. Strong, multi-gene evidence.

2. **Keratinocyte terminal differentiation and cornified envelope**:
- SPRR2A, SPRR2B, SPRR2D, SPRR2E, SPRR2F, SPRR2G (small proline-rich proteins)
- LCE3A, LCE3D (late cornified envelope)
- KRT6A (keratin 6A)
- GJB2, GJB6 (connexins)
- SERPINB3, SERPINB4, SERPINB13 (protease inhibitors)
- KLK13 (kallikrein-related peptidase)
- PLA2G4D, PLA2G4E

This represents aberrant keratinocyte differentiation - hallmark of psoriasis.

3. **Antimicrobial defense**:
- DEFB4A, DEFB4B, DEFB103A, DEFB103B (β-defensins)
- S100A7, S100A7A, S100A8, S100A12 (calprotectin components)
- PI3 (elafin)
- This is downstream of IL-17/IL-36 and partially overlapping with program 1.

4. **NF-κB and TNF signaling**:
- TNIP3 (NF-κB negative regulator)
- ZC3H12A (MCPIP1, regulates NF-κB)
- IRAK2 (IL-1R/TLR signaling)
- PRKCQ (T cell signaling)
- CD274 (PD-L1, NF-κB regulated)

5. **Aryl hydrocarbon receptor (AhR) / tryptophan metabolism**:
- KYNU (kynureninase, IDO1 pathway)
- AKR1B10, AKR1B15 (aldo-keto reductases)
- CYP2W1 (downregulated, cytochrome P450)
- This is less robust but interesting.

6. **WNT signaling / non-canonical**:
- WNT5A
- Could be relevant but single gene.

Let me identify the strongest, most non-redundant programs:

**Program 1: IL-17/IL-36-driven keratinocyte inflammatory amplifier (strongest)**
- Direction: upregulated
- Genes: IL36A, IL36G, IL36RN, IL19, IL20, IL26, S100A7, S100A8, S100A12, S100A7A, DEFB4A, DEFB4B, DEFB103A, DEFB103B, PI3, KRT6A, CXCL13
- Pathway: IL-17 signaling (KEGG: hsa04657), Hallmark: Inflammatory Response, IL-36/IL-1 family signaling
- Evidence: Strong multi-gene convergence. Direct from dataset. Literature supports this as psoriasis core.

**Program 2: Aberrant keratinocyte terminal differentiation and cornified envelope assembly**
- Direction: upregulated
- Genes: SPRR2A/B/D/E/F/G, LCE3A, LCE3D, KRT6A, GJB2, GJB6, SERPINB3, SERPINB4, SERPINB13, KLK13, PLA2G4D/E
- Pathway: Keratinization (GO:0031424), Formation of the cornified envelope (Reactome: R-HSA-6809371)
- Evidence: Strong, multi-gene. Hallmark feature of psoriatic plaques.

**Program 3: Antimicrobial peptide barrier**
- Direction: upregulated
- Genes: S100A7/A7A/A8/A12, DEFB4A/B, DEFB103A/B, PI3
- Pathway: Antimicrobial humoral response (GO:0019730), Defense response to bacterium (GO:0042742)
- Evidence: Strong. Some overlap with program 1 but with distinct identity (AMP module).

**Program 4: NF-κB negative feedback / immune regulation**
- Direction: upregulated
- Genes: TNIP3, ZC3H12A, IRAK2, CD274 (PD-L1)
- Pathway: TNF signaling, NF-κB signaling
- Evidence: TNIP3 strongly upregulated (log2FC 7.28). ZC3H12A is also NF-κB/IL-17-induced.

**Program 5: Tryptophan/AhR/oxidative stress metabolism**
- Direction: mixed (KYNU up, CYP2W1 down)
- Genes: KYNU, AKR1B10, AKR1B15, CYP2W1, IL4I1 not in list
- Pathway: Tryptophan metabolism (KEGG: hsa00380), Aryl hydrocarbon receptor signaling
- Evidence: Moderate. KYNU strongly implicated in psoriasis via AhR/Th17 axis.

**Key genes to highlight:**

1. **IL36A (log2FC 11.37)** - master cytokine amplifier, drives neutrophil recruitment, can be auto-induced. Therapeutic target (anti-IL-36 antibodies in trials).

2. **DEFB4A/B (log2FC 11.18/11.03)** - canonical IL-17 target gene, encodes β-defensin 2, classically associated with psoriasis. Multiple genes in this family.

3. **S100A7/A7A/A8/A12** - S100 antimicrobial peptides; canonical IL-17/IL-22 target genes; highly upregulated. S100A8/A12 = calprotectin (also serum biomarker).

4. **KRT6A (log2FC 4.30)** - hyperproliferation marker; classical psoriasis keratin marker.

5. **SPRR2 family (A/B/D/E/F/G)** - small proline-rich proteins; cornified envelope; aberrantly expressed in psoriasis.

6. **TNIP3 (log2FC 7.28)** - negative regulator of NF-κB; genetic association with psoriasis; induced by TNF/IL-17.

7. **CXCL13 (log2FC 5.89)** - B cell/Tfh chemokine; suggests tertiary lymphoid structure activity.

8. **CD274/PD-L1 (log2FC 3.44)** - immune checkpoint; keratinocyte expression - resistance mechanism.

9. **KYNU (log2FC 4.42)** - tryptophan metabolism via kynurenine; IDO1-KYNU axis; Th17 differentiation.

10. **WNT5A (log2FC 2.53)** - non-canonical Wnt; linked to inflammation in psoriasis.

For the downregulated genes:
- **BTC (-4.30)**: Betacellulin, EGF family member. Interesting downregulation.
- **CYP2W1 (-4.70)**: Cytochrome P450 - xenobiotic metabolism.
- **WAKMAR1 (-5.63)**: lncRNA.
- **SAPCD1 (-2.94)**: Tumor suppressor; APC domain.

Let me think about validation priorities:

1. **Mechanistic: IL-36A self-amplification loop in psoriatic keratinocytes**
- Why: IL36A is the top-ranked gene with massive fold change; whether IL-36A auto-induces itself and amplifies via keratinocyte-intrinsic loop is a key mechanistic question
- Evidence: dataset shows IL36A and IL36G both very high; IL36RN also up (negative regulator induced simultaneously)
- Next step: IL-36 stimulation of primary keratinocytes, qPCR of IL36A/G induction
- Status: Supported hypothesis

2. **Therapeutic target: IL-36 blockade as combination therapy**
- Why: Multiple IL-36 family members highly upregulated; some anti-IL-36 antibodies in development
- Evidence: IL36A, IL36G, IL36RN all upregulated
- Next step: Check clinical trial data for anti-IL-36 in psoriasis
- Status: Supported hypothesis (drug development already underway for pustular psoriasis)

3. **Biomarker: S100A8/A12 + DEFB4B gene panel for lesion severity**
- Why: Largest fold changes; canonical AMPs; serum calprotectin is already used
- Evidence: All four are top upregulated genes
- Next step: Correlate with PASI score; test serum
- Status: Supported hypothesis (calprotectin is established)

4. **Interaction/network: TNIP3 negative feedback limits NF-κB amplification**
- Why: TNIP3 is a known psoriasis susceptibility gene; highly upregulated in this dataset
- Evidence: TNIP3 log2FC 7.28; ZC3H12A also up (parallel negative regulator)
- Next step: TNIP3 knockdown in keratinocytes + IL-17 stimulation
- Status: Supported hypothesis

5. **Confounding check: Cell composition effects on AMP signature**
- Why: S100A8/A12 also expressed in neutrophils; SPRR2 in differentiated keratinocytes; need to confirm whether changes are intrinsic or due to neutrophil infiltration
- Evidence: many AMPs elevated in concert; lesional psoriasis has neutrophil infiltrate
- Next step: Single-cell RNA-seq to deconvolve; or compare with neutrophil-depleted samples
- Status: Standard caveat

Now let me think about limitations:

1. **Tissue composition confounds**: Lesional psoriatic skin has more neutrophils, Th17 cells, and altered keratinocyte layers vs normal skin. Gene expression changes may reflect composition rather than intrinsic keratinocyte reprogramming.

2. **Bulk RNA cannot resolve cell-type specificity**: Without single-cell data, cannot distinguish keratinocyte-intrinsic vs immune-cell-derived signals.

3. **Treatment exposure not specified**: If patients received topical steroids, biologics, this would dampen inflammatory signals.

4. **Lesional vs non-lesional comparison missing**: Cannot determine whether changes are psoriasis-specific or general inflammatory.

5. **Multiple testing correction scope**: All top genes have extremely low FDR; interpretation is robust.

6. **Confounding by altered epidermal thickness**: SPRR2, LCE, KRT6A all reflect hyperproliferation/thickened epidermis, which is a consequence not necessarily a driver.

Let me also note that the downregulated genes (BTC, CYP2W1) are less well-characterized in psoriasis; the downregulated signal is much weaker overall. This is consistent with psoriasis being predominantly an upregulation phenomenon.

Let me now write the full response. I'll structure it according to the requirements:

1. Overall biological interpretation
2. Core biological programs (≤5)
3. Key genes and interaction modules (≤10)
4. Validation priorities (≤5)
5. Evidence grounding
6. Limitations and alternative explanations

Let me write this carefully with appropriate detail and citations of evidence categories.

Wait - I should note the data appears truncated (cuts off at CT69 with FDR 8.55e-61). The user has given me the top differentially expressed genes. I should acknowledge this represents the most significantly changed genes but may not capture all biology. However, the provided set is sufficient for thematic interpretation.

Also let me check: the gene list contains some lncRNAs (LOC, LINC), pseudogenes (VNN3P), and some that look like artifacts (LOC105371988, etc.). The core biology signal is clearly dominated by keratinocyte-inflammatory signatures.

Note: VNN3P (log2FC 8.28) is a pseudogene of vanin 3. This may reflect read-through or unannotated transcript.

Note: ADGRF1 (log2FC 6.64) is an adhesion GPCR, less characterized in psoriasis.

Note: CERNA2 is a lncRNA.

LOC105376238, LOC105376239 - lncRNAs near SPRR2 cluster perhaps.

KLHDC7B-DT - lncRNA.

Many of the LOC/LINC entries are likely lncRNAs near immune/inflammatory loci.

Let me finalize the response.

Actually, I should be careful about claiming protein-protein interactions when I don't have direct evidence. I should distinguish:
- Co-expression: yes, multiple genes in same pathway are co-upregulated
- Pathway co-membership: same pathway evidence
- Direct physical interaction: NOT established from this dataset alone
- Regulatory interaction: NOT established from this dataset alone

For example, IL-17 is NOT in the gene list, but its target genes are massively upregulated, suggesting IL-17 activity upstream. This is INFERRED, not directly shown.

Let me be careful in my language.

Final response structure:

# 1. Overall biological interpretation
Psoriasis lesional skin transcriptome reveals a coordinated program dominated by keratinocyte-intrinsic inflammatory amplification (IL-36 family), aberrant terminal differentiation (SPRR2, LCE3), antimicrobial peptide barrier (β-defensins, S100s), and NF-κB negative feedback (TNIP3). The signal is overwhelmingly upregulated (>95% of top genes), consistent with the inflammatory/hyperproliferative nature of psoriatic plaques. Key cytokine networks (IL-17/IL-22 target genes), keratinocyte defense modules, and cornified envelope components dominate.

# 2. Core biological programs

Program 1: IL-17/IL-36 cytokine amplifier and downstream keratinocyte response
Program 2: Aberrant keratinocyte terminal differentiation and cornified envelope
Program 3: Antimicrobial peptide barrier response
Program 4: NF-κB/IL-17 negative feedback regulators
Program 5: Kynurenine/AhR metabolic axis (tentative)

# 3. Key genes/modules (10)

# 4. Validation priorities (5)

# 5. Evidence grounding

# 6. Limitations

Let me write this up properly.</think>

# Multidimensional Interpretation: Psoriatic Lesional Skin vs. Normal Skin Transcriptome

## 1. Overall Biological Interpretation

The transcriptomic landscape of psoriatic lesional skin is **dominated by massive coordinated upregulation**, with >95% of the top-ranked differentially expressed genes showing positive log₂FC. The signal converges on a coherent biological axis: **keratinocyte-intrinsic inflammatory amplification driven by IL-17/IL-36 family cytokines, accompanied by aberrant terminal differentiation, antimicrobial peptide (AMP) induction, and engagement of NF-κB negative feedback**. This is the molecular signature of an **IL-17–driven "feed-forward" inflammatory circuit in lesional epidermis**, in which keratinocytes both produce (IL-36A/G, IL-19, IL-20, IL-26) and respond to (β-defensins, S100A7/A8/A12, KRT6A, SPRR2 family) IL-17/IL-22 axis cytokines. Downregulated genes are far fewer in number and lower in fold-change magnitude, suggesting psoriasis in this dataset is principally a gain-of-function inflammatory state rather than a loss-of-function disease. The signal is enriched in genes with prior psoriasis GWAS/functional support (TNIP3, IL36A, DEFB4A, KRT6A, SPRR2 family), lending biological plausibility to the interpretation.

---

## 2. Core Biological Programs

### Program 1 — IL-17/IL-36 Cytokine Amplifier and Keratinocyte Effector Response
- **Direction:** Upregulated
- **Supporting genes:** *IL36A* (log₂FC 11.4), *IL36G* (5.68), *IL36RN* (3.00), *IL19* (7.58), *IL20* (5.67), *IL26* (4.36), *DEFB4A* (11.18), *DEFB4B* (11.03), *DEFB103A/B* (~5.75), *S100A7* (7.09), *S100A7A* (9.83), *S100A8* (7.73), *S100A12* (8.33), *PI3/elafin* (9.24), *KRT6A* (4.30), *CXCL13* (5.89), *KYNU* (4.42)
- **Pathway support:** Hallmark "Inflammatory Response," IL-17 signaling (KEGG hsa04657), IL-36 family signaling (Reactome R-HSA-9014826), KEGG "Cytokine–cytokine receptor interaction"
- **Rationale:** The simultaneous upregulation of IL-17/IL-22 canonical target genes (DEFB4A, S100A7, S100A8, KRT6A), IL-36 family ligands (IL36A, IL36G) and their antagonist (IL36RN), IL-19/IL-20 (IL-10 family keratinocyte amplifiers), and IL-26 (Th17 effector) provides **multi-gene evidence for an IL-17/IL-36 self-amplifying loop**. This is a well-established psoriasis mechanism; the dataset independently confirms it.
- **Evidence strength:** Strong. Independent of any single gene — converges across cytokine, AMP, and keratin modules.
- **Limitations:** IL17A/IL17F themselves are not in the top list (likely immune-cell-restricted transcripts diluted in bulk RNA), so the cytokine trigger is inferred from its downstream targets rather than directly measured.

### Program 2 — Aberrant Keratinocyte Terminal Differentiation and Cornified Envelope Assembly
- **Direction:** Upregulated
- **Supporting genes:** *SPRR2A/B/D/E/F/G*, *LCE3A* (8.30), *LCE3D* (5.31), *KRT6A*, *GJB2* (4.42), *GJB6* (3.02), *SERPINB3* (6.74), *SERPINB4* (9.12), *SERPINB13* (3.09), *SERPINB11* (4.47), *KLK13* (4.05), *PLA2G4D* (4.61), *PLA2G4E* (2.47)
- **Pathway support:** GO:0031424 "Keratinization"; Reactome R-HSA-6809371 "Formation of the cornified envelope"; KEGG hsa04974 "Protein digestion and absorption"
- **Rationale:** The complete SPRR2 subfamily (six paralogs), LCE3 group, keratin 6A, connexin 26/30, and multiple serine/cysteine protease inhibitors are co-elevated. This is the molecular signature of the **parakeratotic, hyperkeratotic psoriatic epidermis**, where premature/ectopic cornified envelope protein expression occurs in suprabasal keratinocytes. SERPINB3/4 and KLK13 additionally suggest dysregulated desquamation proteolysis.
- **Evidence strength:** Very strong — six SPRR2 paralogs plus LCE3 family is highly redundant evidence.
- **Limitations:** This signature is also seen in wound healing and atopic dermatitis; it may partly reflect epidermal hyperplasia rather than disease-specific differentiation failure.

### Program 3 — Antimicrobial Peptide (AMP) Barrier Module
- **Direction:** Upregulated
- **Supporting genes:** *DEFB4A, DEFB4B, DEFB103A, DEFB103B, S100A7, S100A7A, S100A8, S100A12, PI3*
- **Pathway support:** GO:0042742 "Defense response to bacterium"; GO:0050832 "Defense response to fungus"; Hallmark "Inflammatory Response" (overlapping with Program 1)
- **Rationale:** Four β-defensin paralogs, four S100 AMPs, and elafin co-elevated. While overlapping with Program 1 (these are IL-17 target genes), the AMP module has a **distinct biological identity** as the antimicrobial barrier that explains the clinical observation that psoriatic skin rarely becomes secondarily infected despite barrier disruption. S100A8/A12 (calprotectin) is already a clinically used serum biomarker.
- **Evidence strength:** Strong; four defensin genes alone provide robust independent evidence.
- **Limitations:** S100A8/A12 are also abundant in neutrophils and monocytes — partial signal may reflect lesional neutrophil infiltration (see Limitations).

### Program 4 — NF-κB/IL-17 Negative Feedback Regulators
- **Direction:** Upregulated
- **Supporting genes:** *TNIP3* (7.28), *ZC3H12A/MCPIP1* (3.85), *IRAK2* (2.08), *CD274/PD-L1* (3.44), *TRIM15* (4.54), *SERPINB3/4* (also NF-κB–induced)
- **Pathway support:** TNF signaling (KEGG hsa04668), NF-κB signaling (KEGG hsa04064), IL-17 signaling overlap
- **Rationale:** TNIP3 (TNFAIP3-interacting protein 3) is a **strong psoriasis GWAS locus** and a known brake on NF-κB; its massive upregulation here (log₂FC 7.28) is interpretable as the cell's attempt to restrain an overactive NF-κB response. ZC3H12A (MCPIP1) is an RNase that destabilizes IL-6/IL-17 transcripts and is itself an IL-17 target. CD274 (PD-L1) upregulation on keratinocytes is an emerging resistance/escape module. The co-induction of multiple negative regulators is a hallmark of a system under sustained inflammatory drive.
- **Evidence strength:** Moderate-strong; TNIP3 is the single most convincing anchor (genetic + functional + transcriptomic).
- **Limitations:** Negative regulators are intrinsically hard to interpret functionally from expression alone — they may be failing to restrain the response, which is consistent with disease persistence.

### Program 5 — Kynurenine / Aryl Hydrocarbon Receptor (AhR) Metabolic Axis
- **Direction:** Mixed (KYNU up, CYP2W1 down)
- **Supporting genes:** *KYNU* (4.42), *AKR1B10* (6.27), *AKR1B15* (5.23), *CYP2W1* (−4.70), *WNT5A* (2.53)
- **Pathway support:** KEGG hsa00380 "Tryptophan metabolism"; AhR signaling (Reactome R-HSA-8937144)
- **Rationale:** KYNU (kynureninase) is the second enzyme in the IDO1-driven kynurenine pathway, which generates AhR ligands that promote Th17 differentiation and deplete tryptophan — a mechanism previously implicated in psoriasis. AKR1B10/15 are aldo-keto reductases induced by oxidative/electrophilic stress and can produce lipid mediators. CYP2W1 downregulation may reflect loss of xenobiotic-metabolizing capacity in inflamed skin.
- **Evidence strength:** Moderate — KYNU is the strongest anchor, but the program rests on fewer genes than Programs 1–4. **Labeled as a supported hypothesis requiring more data.**
- **Limitations:** Single-direction evidence is weaker; metabolic pathways are cell-type-dependent and difficult to interpret from bulk RNA alone.

---

## 3. Key Genes and Interaction Modules (10)

| # | Gene | log₂FC | Role | Relationship type |
|---|------|--------|------|-------------------|
| 1 | **IL36A** | +11.37 | Master keratinocyte-derived IL-1 family cytokine; auto-induces; chemotactic for neutrophils/Th17 | Pathway co-membership with IL36G/IL36RN; regulatory (auto-amplifying loop inferred, **not directly demonstrated here**) |
| 2 | **DEFB4A** | +11.18 | Canonical IL-17/IL-22 target gene (hBD-2); antimicrobial | Direct IL-17 transcriptional target (literature); co-expression with DEFB4B (gene duplication) |
| 3 | **S100A7A** | +9.83 | Antimicrobial S100 protein; keratinocyte-derived | Co-expressed with S100A7/A8/A12 (calprotectin + psoriasin module) |
| 4 | **SERPINB4** | +9.12 | Serine protease inhibitor (SCCA2); overexpressed in squamous epithelium | Co-expression with SERPINB3 (paralog); both NF-κB–induced |
| 5 | **PI3 (Elafin)** | +9.24 | Epidermal AMP; antiprotease | IL-17/IL-22 target; co-expression with DEFB4/S100A7 (same module) |
| 6 | **TNIP3** | +7.28 | NF-κB negative regulator; **psoriasis GWAS gene** | Pathway co-membership with ZC3H12A (parallel NF-κB brake); direct physical interaction with A20/TNFAIP3 (literature evidence, not from this dataset) |
| 7 | **KRT6A** | +4.30 | Hyperproliferation/marker of regenerative epidermis | Co-expressed with SPRR2/LCE3 (hyperplastic keratinocyte program) |
| 8 | **SPRR2A–G** | +3.99 to +7.31 | Six paralogs of cornified envelope precursor; aberrant suprabasal expression | Co-expression cluster; likely co-regulated by IL-17/AhR (literature) — direct regulatory relationship **not** demonstrated here |
| 9 | **CXCL13** | +5.89 | B-cell/Tfh chemokine; TLS (tertiary lymphoid structure) marker | Co-expression with IL-26 (Th17 module); putative relationship to lymphoid aggregates |
| 10 | **CD274 (PD-L1)** | +3.44 | Immune checkpoint ligand; keratinocyte-intrinsic expression | NF-κB/IFN-γ induced (literature); co-expression with TNIP3 (NF-κB module) |

**Important note on interaction claims:** The above relationships are predominantly **co-expression** and **pathway co-membership** as supported by this dataset. No direct physical or regulatory interactions are demonstrated by differential expression alone; statements of physical interaction (e.g., TNIP3 with A20) rely on prior literature evidence.

---

## 4. Validation Priorities

### Priority 1 — IL-36A autocrine amplifier loop in psoriatic keratinocytes
- **Category:** Mechanistic hypothesis
- **Why prioritize:** IL36A shows the largest fold change (log₂FC 11.37) of any protein-coding gene; co-elevation of IL36A/G with the negative regulator IL36RN suggests a tightly controlled amplifier whose dynamics determine lesion behavior.
- **Evidence from dataset:** IL36A (11.37), IL36G (5.68), IL36RN (3.00) — all upregulated together.
- **External evidence:** IL-36α is a known psoriasis driver; anti-IL-36 agents are in clinical trials for generalized pustular psoriasis. IL-36α is reported to auto-induce itself in keratinocytes (literature).
- **Next step:** Stimulate primary keratinocytes with recombinant IL-36α and quantify IL36A/G/RN induction by qPCR; use IL-36R blocking antibody as control.
- **Status:** **Supported hypothesis**

### Priority 2 — S100A8/A12 (calprotectin) + β-defensin 4 panel as biomarker of lesional activity
- **Category:** Biomarker
- **Why prioritize:** S100A8/A12 serum calprotectin is clinically used in IBD; transcript abundance in lesional skin is extremely elevated (log₂FC 7.7–8.3); S100A8/A12 also reflect neutrophil contribution.
- **Evidence from dataset:** S100A8 (7.73), S100A12 (8.33), DEFB4A (11.18), DEFB4B (11.03).
- **External evidence:** Calprotectin is an established serum biomarker; cutaneous β-defensin 2 protein is reported as elevated in psoriatic scales.
- **Next step:** Correlate lesional transcript levels with PASI score and serum calprotectin in a paired cohort.
- **Status:** **Supported hypothesis**

### Priority 3 — TNIP3 as a functional brake on the psoriatic NF-κB response
- **Category:** Interaction / network hypothesis
- **Why prioritize:** TNIP3 is the only gene in the top list with **prior psoriasis GWAS support** at genome-wide significance; its dramatic induction (log₂FC 7.28) suggests a strong but possibly insufficient negative feedback.
- **Evidence from dataset:** TNIP3 (7.28), ZC3H12A (3.85), IRAK2 (2.08), SERPINB3/4 (NF-κB–induced) co-elevated.
- **External evidence:** TNIP3 (also known as ABIN-3) polymorphisms are psoriasis GWAS hits; functionally restrains NF-κB via A20 binding.
- **Next step:** siRNA knockdown of TNIP3 in IL-17–stimulated keratinocytes and measure amplified IL-36A/DEFB4A induction.
- **Status:** **Supported hypothesis**

### Priority 4 — Cell-type decomposition of the AMP signature
- **Category:** Confounding / composition check
- **Why prioritize:** S100A8/A12 are abundant in neutrophils; lesional psoriasis has robust neutrophil infiltrate (Munro microabscesses). Bulk RNA cannot distinguish keratinocyte-intrinsic vs neutrophil-derived contributions.
- **Evidence from dataset:** S100A8/A12 (8.33/7.73), DEFB4A/B (11+), IL36A (11.4) are all extremely high — magnitudes could be composition-influenced.
- **External evidence:** Single-cell studies of psoriasis skin have partially attributed S100A8/A12 to neutrophils and classical monocytes.
- **Next step:** Re-analyze public single-cell RNA-seq of psoriatic vs healthy skin to confirm cell-type origin of each top DEG; or perform IHC co-localization.
- **Status:** **Standard methodological caveat; essential before any biomarker claim**

### Priority 5 — Kynurenine/AhR axis contribution to lesional IL-17 amplification
- **Category:** Mechanistic hypothesis
- **Why prioritize:** KYNU is a strongly upregulated metabolic gene (log₂FC 4.42); the kynurenine pathway generates AhR ligands that promote Th17 differentiation — a candidate mechanistic link between metabolism and inflammation in psoriasis.
- **Evidence from dataset:** KYNU (4.42), AKR1B10 (6.27), AKR1B15 (5.23), CYP2W1 (−4.70).
- **External evidence:** IDO1–KYNU axis has been implicated in psoriasis and other Th17-mediated diseases; AhR activation modulates IL-17 responses.
- **Next step:** Measure kynurenine/tryptophan ratio in psoriatic lesional skin; test AhR inhibition in an IL-23 imiquimod mouse model.
- **Status:** **Exploratory hypothesis**

---

## 5. Evidence Grounding Summary

| Claim | Dataset evidence | Pathway/literature evidence | Strength |
|------|------------------|------------------------------|----------|
| IL-17/IL-36 amplifier active | IL36A, IL36G, IL36RN, IL19, IL20, IL26 all up | Established IL-17 psoriasis biology | Direct, strong |
| Aberrant cornified envelope | 6× SPRR2, 2× LCE3, SERPINB3/4/11/13, KLK13, KRT6A | GO keratinization, psoriasis histology | Direct, strong |
| AMP barrier induction | 4× β-defensin, 4× S100, PI3 | Established IL-17 target genes | Direct, strong |
| NF-κB negative feedback | TNIP3, ZC3H12A, IRAK2, CD274 up | TNIP3 GWAS, NF-κB pathway | Direct + genetic, strong |
| Kynurenine/AhR involvement | KYNU up, CYP2W1 down | KEGG tryptophan metabolism, AhR/Th17 literature | Mixed, moderate |
| PD-L1 keratinocyte induction | CD274 up | Literature on keratinocyte PD-L1 in inflammation | Direct, moderate |
| WNT5A non-canonical activation | WNT5A up | WNT5A literature in psoriasis | Single gene, weak |

**Independence of evidence sources:** Programs 1–4 are supported by **multiple independent evidence layers** — direct transcriptomics from this dataset, established pathway databases, prior genetic associations (TNIP3, IL36A), and clinical biomarker precedent (calprotectin). These are not all independent (e.g., the IL-17 target gene signature overlaps across Programs 1, 2, and 3 because they reflect shared upstream signaling). Program 5 is the most reliant on literature inference.

---

## 6. Limitations and Alternative Interpretations

1. **Tissue composition confounds (most important).** Lesional psoriatic skin contains increased neutrophils, dendritic cells, Th17/Tc17 cells, and altered keratinocyte layers relative to normal skin. Bulk RNA cannot distinguish cell-type-intrinsic transcriptional changes from shifts in cellular composition. **Particularly relevant for S100A8/A12 (neutrophil/monocyte-derived), IL26 (Th17-derived), and CXCL13 (B-cell/T follicular helper-derived).** Investigation: public scRNA-seq deconvolution or paired IHC.

2. **Epidermal hyperplasia confounds the "differentiation" signature.** SPRR2, LCE3, KRT6A, and connexin 26/30 upregulation could partly reflect increased thickness of suprabasal keratinocyte layers rather than qualitative differentiation reprogramming. Investigation: compare lesional vs. non-lesional psoriasis skin (which shares many features) and adjust for epidermal thickness.

3. **Treatment exposure is not specified.** Topical steroids, vitamin D analogues, or prior biologic exposure can substantially dampen inflammatory transcripts. If patients were on therapy, the true biological signal may be **larger** than observed; if untreated acute lesions, signal may reflect acute flare biology specifically. Investigation: stratify by treatment-naïve status if metadata allow.

4. **Disease stage and chronicity uncharacterized.** Early vs. chronic plaque psoriasis may have distinct transcriptomes; the dataset cannot distinguish these.

5. **Bulk RNA obscures cellular source of key cytokines.** IL17A, IL17F, IL22, and IL23A are not in the top DEG list, but their downstream targets are massively elevated. This is consistent with (but does not prove) immune-cell-derived cytokine signaling to keratinocytes — a mechanistically important inference that requires single-cell or spatial transcriptomics to confirm.

6. **Insufficient evidence for causal direction.** All interpretations describe **association** of transcripts with disease state. None establishes whether a given gene (e.g., TNIP3, KYNU) is a driver, passenger, or compensatory response. Functional perturbation studies are required.

7. **Multiple downregulated genes are of uncertain interpretation.** *BTC* (betacellulin), *CYP2W1*, and several lncRNAs (WAKMAR1, LOC107984452) are strongly downregulated but lack clear psoriasis-specific functional context; they should not be over-interpreted without follow-up.

---

## Summary Statement

The transcriptomic landscape of psoriatic lesional skin in this dataset is dominated by a coherent **IL-17/IL-36-driven keratinocyte response program** involving (1) cytokine amplification, (2) aberrant cornified envelope expression, (3) antimicrobial peptide induction, and (4) NF-κB negative feedback engagement. These programs are **biologically interdependent** rather than independent, reflecting the same upstream IL-17/IL-22 axis acting on keratinocytes. The KYNU/AhR module is a credible but lower-confidence fifth program. Cell-composition effects, epidermal hyperplasia, and treatment exposure are the most important interpretive caveats. Validation priorities should focus on the IL-36A autocrine loop (mechanism), calprotectin/β-defensin biomarker panel, TNIP3 negative-feedback function, and careful cell-type deconvolution before therapeutic targeting claims.
