# psoriasis - minimax-m3

- Benchmark system: E2seq + Agent RAG
- Repeat: 5
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
- Model API: MiniMax / minimax-m3
- Message SHA-256: d1a33d3f606c81814c4fb94a6c63c8f1abebd3bde37d769e82eae4772d8ff873
- Response HTTP status: 200
- Prompt tokens: 101056
- Completion tokens: 84110
- Reasoning tokens: 13453
- Total tokens: 185166
- API requests reported: 8
- Elapsed seconds: 210.849
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 1150.303
- Question handoff seconds: 1163.566
- Final benchmark system: E2seq; file rank 3/5; original repeat 5; model vendor: MiniMax

---
<think>The user wants a comprehensive, multidimensional interpretation of a transcriptomics dataset comparing psoriatic lesional skin versus normal control skin. Let me organize the analysis carefully.

**Input summary:**
- 100 selected genes (DEGs), 90 upregulated and 10 downregulated
- Disease: psoriasis, tissue: lesional skin
- All genes have FDR << 0.01, all are highly significant
- log2FC ranges from -6.25 (most downregulated) to +11.37 (most upregulated)

**Key gene categories I can identify:**

1. **IL-36 cytokines and IL-20 family cytokines (Th17/IL-17 axis):**
   - IL36A (log2FC=11.37, top upregulated)
   - IL36G (log2FC=5.68)
   - IL36RN (log2FC=3.00, IL-36 receptor antagonist)
   - IL19 (log2FC=7.58)
   - IL20 (log2FC=5.67)
   - IL26 (log2FC=4.36)
   - This is the IL-17/IL-23 axis signature

2. **Antimicrobial peptides (AMPs):**
   - DEFB4A (log2FC=11.18)
   - DEFB4B (log2FC=11.03)
   - DEFB103A (log2FC=5.76)
   - DEFB103B (log2FC=5.75)
   - S100A7 (log2FC=7.09)
   - S100A7A (log2FC=9.83)
   - S100A8 (log2FC=7.73)
   - S100A12 (log2FC=8.33)
   - PI3 (log2FC=9.24)
   - LCN2 (not in list)
   - These are classic psoriasis AMP signature

3. **Keratinocyte cornified envelope/barrier:**
   - SPRR2A, SPRR2B, SPRR2D, SPRR2E, SPRR2F, SPRR2G (small proline rich proteins)
   - LCE3A, LCE3D (late cornified envelope)
   - KRT6A (keratin 6A)
   - SERPINB3, SERPINB4, SERPINB11, SERPINB13 (serine protease inhibitors)
   - KLK13 (kallikrein)
   - These relate to keratinocyte hyperproliferation and barrier dysfunction

4. **Neutrophil chemotaxis/inflammation:**
   - CXCL13 (log2FC=5.89) - B cell/T cell chemokine
   - CXCR2 (log2FC=2.70) - neutrophil chemokine receptor
   - These drive neutrophil infiltration

5. **NF-κB negative regulators:**
   - TNIP3 (log2FC=7.28)
   - ZC3H12A (log2FC=3.85) - MCPIP1, Regnase-1
   - NFKBIZ (not in list)
   - These are negative feedback regulators

6. **Cell proliferation/cell cycle:**
   - CCNE1 (log2FC=2.56)
   - RRM2 (log2FC=2.72)
   - These relate to keratinocyte hyperproliferation

7. **Lipid metabolism:**
   - AKR1B10, AKR1B15 (aldo-keto reductases)
   - FABP5 (fatty acid binding protein 5)
   - PLA2G4D, PLA2G4E (phospholipases)
   - KYNU (kynureninase - tryptophan metabolism)

8. **Downregulated genes (potential lipid metabolism):**
   - CYP2W1 (-4.70)
   - BTC (betacellulin, -4.30)
   - WAKMAR1 (-5.63)
   - UGT3A2 (-4.59)
   - SAPCD1 (-2.94)
   - SAPCD1-AS1 (-2.84)
   - LOC107984452 (-6.25)
   - LINC02660 (-3.90)
   - LOC107984005 (-4.27)
   - LOC105371988 (-4.10)

**Pathway support from RAG batch:**
- GO: Response To Lipopolysaccharide (GO:0032496)
- GO: Epidermis Development (GO:0008544)
- GO: Antimicrobial Humoral Response (GO:0019730)
- KEGG: IL-17 signaling pathway
- KEGG: Cytokine-cytokine receptor interaction
- KEGG: Staphylococcus aureus infection

**Network evidence:**
- SPRR family clustering (SPRR1B hub with 8 selected genes)
- S100A7 clustering with FABP5, S100A12, S100A7A, SERPINB3, SERPINB4
- CCR6 with DEFB103A, DEFB4A, DEFB4B
- CTSG with SERPINB13, SERPINB3, SERPINB4
- IL1RAP with IL36A, IL36G, IL36RN

Let me structure the response following the user's requested format:

1. Overall biological interpretation
2. Core biological programs (max 5)
3. Key genes and interaction modules (max 10)
4. Validation priorities (max 5)
5. Evidence grounding
6. Limitations and alternative explanations

Important constraints:
- Distinguish association from causation
- Note that independent cohort replication is not available
- Pathway/network/tissue/literature records are contextual, not replication
- Mark evidence strength appropriately

Let me now write the answer with appropriate depth and rigor.</think>

# Multidimensional Interpretation: Psoriatic Lesional Skin vs Normal Skin Transcriptome

## 1. Overall Biological Interpretation

The uploaded differential expression analysis reveals a strongly polarized transcriptomic signature dominated by **upregulation** (90/100 selected genes; log2FC range up to ~11.4), with the strongest signals concentrated in five coherent biological domains: (i) **IL-17/IL-23 axis cytokine activity** (IL36A, IL36G, IL19, IL20, IL26); (ii) **keratinocyte antimicrobial/defense responses** (β-defensins DEFB4A/B, DEFB103A/B; S100 alarmins S100A7/A7A/A8/A12; PI3/elafin); (iii) **epidermal cornified-envelope/barrier remodeling** (SPRR2A/B/D/E/F/G, LCE3A/D, SERPINB3/B4/B11/B13, KRT6A, KLK13); (iv) **innate-adaptive immune cross-talk and neutrophil chemotaxis** (CXCL13, CXCR2); and (v) **negative feedback on NF-κB/inflammation** (TNIP3, ZC3H12A). The minor downregulated set is dominated by loci with unclear functional annotation (multiple uncharacterized LOC/lncRNAs such as LOC107984452, WAKMAR1, LINC02660) plus BTC (betacellulin, an EGFR ligand), CYP2W1, UGT3A2, and SAPCD1/SAPCD1-AS1. The overall pattern is highly consistent with established psoriatic molecular biology — a Th17/IL-17-driven, keratinocyte-centered, AMP-rich, hyperproliferative lesion with concurrent compensatory NF-κB restraint.

**Important caveat:** No independent replication cohort statistic is supplied; the RAG pathway, network, and literature records are *contextual* and do not constitute replication of the uploaded effect estimates.

---

## 2. Core Biological Programs (≤5)

### Program 1 — IL-17/IL-22/IL-36 Axis Activation
- **Direction:** Upregulated in lesional vs normal skin.
- **Supporting genes:** IL36A (log2FC=11.37), IL36G (5.68), IL36RN (3.00), IL19 (7.58), IL20 (5.67), IL26 (4.36).
- **Best pathway mapping:** KEGG *IL-17 signaling pathway*; Reactome *Interleukin-20 family signaling* (R-HSA-8854691, per IL26 vector evidence); KEGG *Cytokine–cytokine receptor interaction*.
- **Why this is a coherent program:** IL-36α/γ are neutrophil- and keratinocyte-derived IL-17–inducible alarmins whose upregulation is a hallmark of psoriatic epidermis; IL-19/IL-20 share the IL-20R/IL-22R receptor system and drive keratinocyte hyperplasia; IL-26 is a Th17/Th22-derived antimicrobial cytokine. The concurrent rise of IL-36RN reflects a homeostatic counter-response rather than disease inactivity. STRING records link IL36A/IL36G/IL36RN via IL1RAP (receptor co-chain), a direct physical/receptor-level relationship.
- **Evidence strength:** **Established evidence** for IL-17 axis involvement in psoriasis. **Supported hypothesis** that IL-36 sub-family specifically drives neutrophil recruitment in this lesion.
- **Limitations:** Effect estimates cannot distinguish keratinocyte-intrinsic vs infiltrating-cell contributions without deconvolution; the receptors (IL1RAP, IL20RA/RB) were not in the selected list and require separate confirmation.

### Program 2 — Antimicrobial Peptide & Alarmin Storm
- **Direction:** Upregulated.
- **Supporting genes:** DEFB4A (11.18), DEFB4B (11.03), DEFB103A (5.76), DEFB103B (5.75), S100A7 (7.09), S100A7A (9.83), S100A8 (7.73), S100A12 (8.33), PI3/elafin (9.24).
- **Best pathway mapping:** GO *Antimicrobial humoral response* (GO:0019730); KEGG *Staphylococcus aureus infection* (a surrogate S100/defensin signature).
- **Why this is a coherent program:** β-defensin 2/4 and β-defensin 3 are directly IL-17/IL-22-induced; S100A7/A7A/A8/A12 are calcium-binding alarmins that amplify IL-17 signaling, recruit neutrophils, and are virtually pathognomonic of psoriatic plaques; PI3 is an epithelial serine protease inhibitor with antimicrobial activity. The KEGG *S. aureus infection* hit reflects the defensin/S100 antimicrobial cassette rather than actual pathogen presence.
- **Evidence strength:** **Established evidence**.
- **Limitations:** These AMPs are not psoriasis-specific (also induced in atopic dermatitis, wound healing); the very high effect sizes (log2FC > 10) suggest strong IL-17 induction but cannot distinguish cause from consequence.

### Program 3 — Epidermal Cornified-Envelope Remodeling & Hyperproliferation
- **Direction:** Upregulated.
- **Supporting genes:** SPRR2A/B/D/E/F/G (log2FC 4.0–7.3), LCE3A (8.30), LCE3D (5.31), SERPINB3 (6.74), SERPINB4 (9.12), SERPINB11 (4.47), SERPINB13 (3.10), KRT6A (4.30), KLK13 (4.05), FABP5 (3.65).
- **Best pathway mapping:** GO *Epidermis development* (GO:0008544); Reactome *Formation of the cornified envelope* (R-HSA-6809371, with KRT6A, LCE3A/D, PI3, KLK13 among the RAG-confirmed hits).
- **Why this is a coherent program:** SPRR2 family and LCE3 proteins are structural components of the cornified envelope whose aberrant expression reflects epidermal stress response and hyperproliferation; KRT6A replaces KRT5/KRT10 in hyperproliferative psoriatic epidermis; SERPINB3/B4/B11/B13 and KLK13 regulate desquamation and form a protease–antiprotease axis. STRING groups SPRR family members around the SPRR1B hub (8 selected genes) and groups SERPINBs via CTSG (3 selected) — these represent **co-expression / pathway co-membership** in curated PPI databases, not necessarily direct physical binding.
- **Evidence strength:** **Established evidence** for hyperproliferation/barrier remodeling.
- **Limitations:** Cornified-envelope gene induction is also seen in wound healing; co-expression does not imply physical interaction.

### Program 4 — NF-κB Negative Feedback & Resolution Signaling
- **Direction:** Upregulated.
- **Supporting genes:** TNIP3 (7.28), ZC3H12A/MCPIP1 (3.85), TNFAIP3 (not in list but pathway-relevant), IRAK2 (2.08).
- **Best pathway mapping:** GO *Response to lipopolysaccharide* (GO:0032496, supported by RAG batch); Reactome *TNF signaling* / NF-κB negative regulation modules.
- **Why this is a coherent program:** TNIP3 (TNFAIP3-interacting protein 3) and ZC3H12A are direct NF-κB target genes that act as negative-feedback regulators (deubiquitinase recruitment and endoribonuclease-mediated mRNA decay, respectively). Their strong upregulation in psoriasis is paradoxical but well documented — it likely reflects chronic NF-κB activation triggering compensatory restraint. IRAK2 amplifies TLR/IL-1R signaling upstream.
- **Evidence strength:** **Supported hypothesis** that this represents compensatory rather than primary pathogenic signaling.
- **Limitations:** "Upregulation of a brake" is mechanistically ambiguous without kinetic or functional perturbation data.

### Program 5 — Lipid Metabolism & Xenobiotic-Handling Shift
- **Direction:** Mostly upregulated (AKR1B10 6.27, AKR1B15 5.23, FABP5 3.65, PLA2G4D 4.62, PLA2G4E 2.47); with several downregulated xenobiotic/lipid loci (CYP2W1 −4.70, UGT3A2 −4.59, BTC −4.30, WAKMAR1 −5.63).
- **Best pathway mapping:** Reactome *Signaling by Retinoic Acid* (R-HSA-5362517, FABP5 vector evidence); KEGG *Arachidonic acid metabolism*; GO *Lipid metabolic process*.
- **Why this is a coherent program:** AKR1B10/15 are aldo-keto reductases metabolizing lipid aldehydes and retinoids; FABP5 shuttles fatty acids to PPARβ/δ, driving keratinocyte proliferation and a retinoic-acid metabolic axis implicated in psoriasis; PLA2G4D/E release arachidonic acid for eicosanoid production. The downregulated CYP2W1/UGT3A2 suggest a broader xenobiotic-metabolism suppression, while BTC (an EGFR ligand) reduction may reflect altered ErbB signaling in lesional epidermis.
- **Evidence strength:** **Supported hypothesis** for lipid metabolic reprogramming.
- **Limitations:** Direction-consistent functional consequences require metabolomic/lipidomic confirmation; WAKMAR1 is a lncRNA of uncertain function, and LOC105371988, LOC105376238/239/342 are unannotated.

---

## 3. Key Genes / Interaction Modules (≤10)

| # | Gene (log2FC) | Program | Proposed Relationship | Evidence Type |
|---|---|---|---|---|
| 1 | **IL36A** (+11.37) | IL-17/IL-36 axis | Direct physical interaction via IL1RAP co-receptor (STRING); IL-17–induced gene; alarmin amplifier | Direct (input) + STRING network + literature |
| 2 | **DEFB4A/B** (+11.18/+11.03) | Antimicrobial | CCR6-mediated ligand–chemokine co-expression module (STRING: CCR6 hub with DEFB103A, DEFB4A, DEFB4B); co-membership not direct binding | Direct (input) + STRING + KEGG S. aureus infection |
| 3 | **S100A7 / S100A7A / S100A8 / S100A12** (+7.09 to +8.33) | Antimicrobial & alarmin | S100A7 STRING hub with FABP5, S100A12, S100A7A, SERPINB3, SERPINB4 (co-expression/physical heterodimerization) | Direct (input) + STRING |
| 4 | **SPRR2 family** (SPRR2A/B/D/E/F/G; +4.0 to +7.3) | Cornified envelope | STRING hub at SPRR1B connecting 8 selected genes (co-expression/pathway co-membership) | Direct (input) + STRING + Reactome cornified envelope |
| 5 | **IL19 / IL20 / IL26** (+7.58, +5.67, +4.36) | IL-17/IL-20 family | STRING: IL26–IL19, IL26–IL20RA, IL26–IL20RB, IL26–IL10RB/IL22RA1 — receptor/co-receptor physical interactions | Direct (input) + STRING + Reactome IL-20 family signaling |
| 6 | **KRT6A** (+4.30) | Cornified envelope / hyperproliferation | Reactome cornified envelope module | Direct (input) + Reactome |
| 7 | **TNIP3** (+7.28) | NF-κB feedback | TNIP3 is an A20-binding partner regulating NF-κB termination; no direct PPI in STRING but pathway co-membership with TNFAIP3 | Direct (input) + pathway ontology |
| 8 | **CXCL13 / CXCR2** (+5.89 / +2.70) | Chemokine module | Ligand–receptor pair; co-expression not direct binding in STRING | Direct (input) + GO chemokine activity |
| 9 | **FABP5** (+3.65) | Lipid metabolism | STRING: FABP5–PPARD (0.988, direct physical interaction known from structural studies), FABP5–S100A7 (0.883, putative) | Direct (input) + STRING physical + Reactome RA signaling |
| 10 | **ZC3H12A / IRAK2** (+3.85 / +2.08) | NF-κB / IL-1R–TLR feedback | IRAK2–TLR/IL-1R pathway co-membership; ZC3H12A is RNase that degrades inflammatory mRNAs | Direct (input) + pathway ontology |

**Explicit interaction caveat:** All listed STRING relationships are *annotation-supported physical or functional interactions*; some are direct physical binding (e.g., FABP5–PPARD, IL26–IL20RA), while SPRR/S100A7 hubs predominantly reflect **co-expression, co-curation, or pathway co-membership**. None of the listed gene pairs should be presented as novel physical interactions without experimental confirmation.

---

## 4. Validation Priorities (≤5)

### Priority 1 — IL-36A/IL-36G as upstream amplifiers (Mechanistic hypothesis + Therapeutic target)
- **Why prioritize:** IL36A shows the largest log2FC in the entire list (11.37), and IL-36 pathway blockade (e.g., spesolimab) has clinical activity in pustular psoriasis — a directly testable, clinically actionable hypothesis.
- **Dataset evidence:** Largest single effect in the cohort.
- **External evidence:** IL-36RN deficiency causes DITRA; IL-36 blockade trials in pustular psoriasis (literature support).
- **Next step:** Quantify IL-36A protein in lesional vs non-lesional vs resolved skin; test IL-36R blockade in 3D organotypic psoriatic skin models.
- **Status:** **Supported hypothesis** for plaque psoriasis role (established for pustular variants).

### Priority 2 — DEFB4A/B + S100A7 as composite biomarker (Biomarker)
- **Why prioritize:** These show the highest effect sizes (log2FC > 7–11) and represent the core IL-17 transcriptional readout; could be developed as a serum or tape-strip biomarker for IL-17 pathway activity.
- **Dataset evidence:** Strongest, most consistent upregulation; concordant across multiple AMP genes.
- **External evidence:** DEFB2/4 (DEFB4A) and S100A7 are well-characterized IL-17 readout genes.
- **Next step:** Measure DEFB4 and S100A7 protein in stratum corneum tape strips or serum in an independent psoriatic cohort vs atopic dermatitis controls.
- **Status:** **Supported hypothesis**; not validated as a clinical biomarker in this cohort.

### Priority 3 — Cornified-envelope remodeling as outcome of, vs driver of, hyperproliferation (Mechanistic hypothesis)
- **Why prioritize:** The SPRR2/LCE3/SERPINB cluster is large and very strong (log2FC 4–9) but mechanistically ambiguous.
- **Dataset evidence:** Multiple co-regulated genes within Reactome cornified envelope module.
- **External evidence:** SPRR2 induction is observed in wound healing; causal role in psoriasis unclear.
- **Next step:** Use SPRR2-knockdown keratinocytes + IL-17A stimulation to test whether SPRR2 affects proliferation or inflammatory cytokine release.
- **Status:** **Exploratory hypothesis**.

### Priority 4 — TNIP3 / ZC3H12A induction as feedback brake vs NF-κB amplifier (Mechanistic / Interaction hypothesis)
- **Why prioritize:** Distinguishing compensatory from causal NF-κB regulators is critical for therapeutic targeting of TNIP3.
- **Dataset evidence:** Strong upregulation (TNIP3 log2FC=7.28, ZC3H12A=3.85).
- **External evidence:** Both are well-known NF-κB negative regulators; genetic variants in TNIP3 are GWAS hits for psoriasis (RAG gwas=100/100 coverage).
- **Next step:** Chromatin (ATAC/ChIP) for RELA binding at TNIP3/ZC3H12A promoters in lesional vs resolved skin; CRISPR perturbation in organoids.
- **Status:** **Supported hypothesis** for compensatory role.

### Priority 5 — Composition check: keratinocyte vs neutrophil vs Th17 contributions (Confounding / composition check)
- **Why prioritize:** The very large effect sizes for DEFB4, S100A8, CXCL13, CXCR2 are also neutrophil/Th17 markers; bulk RNA may confound cell-intrinsic keratinocyte programs with infiltrating immune cell signatures.
- **Dataset evidence:** Co-induction of neutrophil chemokines (CXCL13, CXCR2) and AMPs.
- **External evidence:** Established that psoriatic plaques contain neutrophil microabscesses (Munro's) and dermal Th17 infiltrates.
- **Next step:** Single-cell RNA-seq deconvolution or spatial transcriptomics on the same lesions; compare to scRNA-seq references (e.g., Reynolds et al., *J Invest Dermatol* 2021, Cheng et al. *Nat Med* 2018) to assign each gene to keratinocyte vs immune compartments.
- **Status:** **Established evidence** that composition matters; **exploratory hypothesis** that specific DEGs are immune-driven.

---

## 5. Evidence Grounding

| Evidence Category | What it supports | Independence status |
|---|---|---|
| **Direct input dataset** (100 genes, log2FC/P/FDR) | Direction, magnitude, and significance of all listed gene changes | Primary |
| **Pathway/ontology (GO, KEGG, Reactome)** | Functional categorization (IL-17 signaling, antimicrobial humoral response, epidermis development, cornified envelope formation) | May share underlying curation; not independent replication |
| **Protein/regulatory network (STRING, IntAct, OmniPath)** | Hub structure (SPRR1B, S100A7, CCR6, IL1RAP, CTSG); physical interactions (FABP5–PPARD, IL26–IL20RA) | STRING edges are mostly curated/literature-derived; **not independent of literature evidence** |
| **Disease/genetic evidence (GWAS, ClinVar, OpenTargets)** | Disease association backstop (e.g., TNIP3 GWAS locus for psoriasis) | Genuinely independent of this transcriptomic dataset |
| **Expression/tissue (GTEx, HPA, HumanBase)** | Tissue-specific baseline expression context | Independent of this DE analysis |
| **Therapeutic (ChEMBL, ClinicalTrials, CIVIC)** | Drug-target presence for IL-36, PDE4, etc.; not validation | Not independent causal evidence |
| **Literature (PubMed, Europe PMC)** | Mechanistic background for IL-36, IL-17 axis, AMPs | May overlap with STRING/Reactome curation |

**No conflicts** were detected between the input data and external annotations; the input direction (upregulation) is concordant with prior psoriasis transcriptome studies (e.g., PMID 40560938 on WGCNA + LASSO biomarkers; broader literature). **Independent cohort replication statistics are not available** in this evidence pack, so concordance should be reported as direction-consistent literature support, not as statistical replication.

---

## 6. Limitations and Alternative Explanations

1. **Cell-composition confounding.** Bulk RNA from whole skin cannot separate keratinocyte-intrinsic changes from infiltrating neutrophil, Th17, or dendritic cell contributions. AMPs (DEFB4, S100A8), chemokines (CXCL13), and IL-26 are partly immune-derived. Without single-cell or spatial transcriptomic deconvolution, a gene may appear "keratinocyte-upregulated" simply because neutrophils increased.

2. **Treated vs untreated patients.** If any samples come from patients on systemic or topical therapy (corticosteroids, vitamin D analogues, biologics), the signal could be attenuated or reshaped. Drug-target genes (e.g., TNIP3, IL36A) are particularly vulnerable. Treatment exposure is not annotated in the input.

3. **Lesional heterogeneity / disease severity.** Plaque psoriasis shows spatial heterogeneity (active edge vs central plaque) and stage variation (early vs chronic). Genes like SPRR2 and SERPINB3 may reflect chronic remodeling rather than acute inflammation.

4. **Batch and platform effects.** Microarray vs RNA-seq vs different probe designs may produce cross-platform log2FC differences for the same gene; without explicit platform annotation, comparisons to external datasets are confounded.

5. **Association vs causation.** All genes show association with lesional status. Upregulation of negative regulators (TNIP3, ZC3H12A) and antimicrobial alarmins could be either causal, compensatory, or epiphenomenal. The uploaded cross-sectional data cannot resolve causal direction; perturbation experiments (CRISPR, antisense, neutralizing antibodies) are required.

---

## Summary

The transcriptomic signature is a high-confidence, IL-17/IL-36-centered, keratinocyte-driven, AMP-rich, cornified-envelope–remodeling, NF-κB–feedback response that closely matches the canonical psoriatic molecular program. **Independent cohort replication statistics are not available**, so the interpretation rests on (a) direct input effects, (b) directional concordance with prior literature, and (c) pathway/ontology/network contextual evidence. The highest-priority next steps are composition-aware (scRNA-seq/spatial) confirmation, IL-36 functional perturbation, and DEFB4/S100A7 biomarker validation against atopic dermatitis controls to assess disease specificity.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=24, external claims checked=0, external mismatches=0, status=needs review.

Answer model API: MiniMax / minimax-m3

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 91/100 selected items (records returned); cbioportal 91/100 selected items (records returned); chembl 11/100 selected items (partially returned; some queries failed); civic 4/100 selected items (records returned); clinicaltrials 40/100 selected items (records returned); clinvar 90/100 selected items (records returned); ensembl 44/100 selected items (partially returned; some queries failed); europepmc 848 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 83/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 76/100 selected items (records returned); humanbase 100/100 selected items (records returned); intact 79/100 selected items (records returned); mygene 100/100 selected items (records returned); omnipath 36/100 selected items (records returned); opentargets 90/100 selected items (records returned); pubmed 669 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 80/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 80/100 selected items (records returned)
Local databases: gutmgene 2/100 selected items (records returned); hmdb 25/100 selected items (records returned); string 78/100 selected items (records returned); trrust 17/100 selected items (records returned)
