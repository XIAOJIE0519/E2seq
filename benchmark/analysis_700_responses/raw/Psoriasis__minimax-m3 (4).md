# psoriasis - minimax-m3

- Benchmark system: raw
- Repeat: 6
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
- Completion tokens: 7575
- Reasoning tokens: 
- Total tokens: 11629
- API requests reported: 
- Elapsed seconds: 44.604
- Final benchmark system: raw; file rank 4/5; original repeat 6; model vendor: MiniMax

---
<think>The user wants me to perform a multidimensional, evidence-grounded, and biologically verifiable interpretation of transcriptomic data comparing psoriatic lesional skin vs normal control skin. Let me analyze the provided gene list carefully.

The data shows a list of differentially expressed genes with their log2FC, P values, and FDR. I need to organize these into upregulated and downregulated genes, then interpret the biological themes.

Let me first separate the genes by direction:

Upregulated genes (positive log2FC):
- VNN3P (8.28)
- ADGRF1 (6.64)
- IL36A (11.37)
- S100A12 (8.33)
- LOC105376238 (5.15)
- CERNA2 (5.40)
- KYNU (4.42)
- IL36G (5.68)
- AKR1B10 (6.27)
- AKR1B15 (5.23)
- GJB2 (4.42)
- SPRR2A (7.31)
- IL19 (7.58)
- TNIP3 (7.28)
- TMPRSS11D (7.75)
- LOC105376239 (4.68)
- FABP5 (3.64)
- PLA2G4D (4.61)
- SPRR2B (6.38)
- HPSE (2.92)
- SERPINB3 (6.74)
- GPR15LG (5.52)
- SPRR2D (5.92)
- CDK5R1 (2.35)
- LINC01206 (5.49)
- ABCG4 (4.75)
- KLHDC7B-DT (4.30)
- LOC105371569 (4.60)
- ZC3H12A (3.85)
- TPBG (1.86)
- IL20 (5.67)
- DEFB4B (11.03)
- LINC03232 (4.16)
- SPRR3 (7.18)
- KLK13 (4.05)
- TCN1 (8.04)
- PLBD1 (2.08)
- PI3 (9.24)
- GJB6 (3.02)
- TRIM15 (4.54)
- DEFB4A (11.18)
- SPRR2E (3.99)
- RHCG (5.29)
- DEFB103B (5.75)
- DEFB103A (5.76)
- HRH2 (3.27)
- CXCL13 (5.89)
- KRT6A (4.30)
- WNT5A (2.53)
- SLC6A14 (4.47)
- BMAL2 (2.21)
- KCNK10 (3.84)
- SERPINB13 (3.09)
- GDA (5.90)
- ADAP2 (2.09)
- LINC01269 (4.77)
- FAM110C (2.14)
- HABP2 (4.19)
- S100A8 (7.73)
- TEX101 (4.28)
- SERPINB4 (9.12)
- ACP7 (3.77)
- SPRR2F (7.22)
- PLA2G4E (2.47)
- IL26 (4.36)
- LINC01605 (2.83)
- TTC39A (2.61)
- LCE3A (8.30)
- ARSF (3.65)
- LOC105376342 (5.67)
- MPZL2 (2.51)
- ENKUR (4.88)
- CXCR2 (2.70)
- LCE3D (5.31)
- CD274 (3.44) - this is PD-L1
- HEPHL1 (6.33)
- TRIM10 (4.04)
- S100A7A (9.83)
- PRKCQ (2.88)
- PRSS27 (4.24)
- S100A7 (7.09)
- LINC01215 (3.70)
- IL36RN (3.01)
- SPRR2G (4.75)
- LOC112268153 (4.73)
- RRM2 (2.72)
- IRAK2 (2.08)
- SERPINB11 (4.47)
- CCNE1 (2.56)
- CT69 (3.85)

Downregulated genes (negative log2FC):
- LOC107984452 (-6.25)
- BTC (-4.30)
- LOC105371988 (-4.10)
- CYP2W1 (-4.70)
- LINC02660 (-3.90)
- LOC107984005 (-4.27)
- SAPCD1 (-2.94)
- UGT3A2 (-4.59)
- WAKMAR1 (-5.63)
- SAPCD1-AS1 (-2.84)

Now let me think about the biological themes in psoriasis:

1. IL-17/IL-23 axis and Th17 cytokines - IL36A, IL36G, IL19, IL20, IL26, IL36RN - all upregulated
2. Antimicrobial peptides - DEFB4A, DEFB4B, DEFB103A, DEFB103B, S100A7, S100A7A, S100A8, S100A12, PI3
3. Keratinocyte differentiation/barrier - SPRR2A, SPRR2B, SPRR2D, SPRR2E, SPRR2F, SPRR2G, SPRR3, LCE3A, LCE3D, KRT6A, FABP5, GJB2, GJB6
4. Neutrophil chemotaxis - CXCL13, CXCR2
5. NF-κB signaling - TNIP3, IRAK2, ZC3H12A
6. Cell proliferation - CCNE1, RRM2
7. T cell costimulation/PD-L1 - CD274 (PD-L1)
8. Kallikreins - KLK13
9. Serine proteases/inhibitors - SERPINB3, SERPINB4, SERPINB11, SERPINB13
10. Lipid metabolism - PLA2G4D, PLA2G4E, AKR1B10, AKR1B15, FABP5

Downregulated genes:
- BTC (Betacellulin, an EGF family member)
- CYP2W1 (cytochrome p450)
- UGT3A2 (UDP-glucuronosyltransferase)
- WAKMAR1 (lncRNA)
- SAPCD1 (suppressor APC domain containing 1)

Let me identify key biological programs:

1. IL-36/IL-17/IL-23 inflammatory cytokine network
   - IL36A, IL36G, IL36RN, IL19, IL20, IL26
   
2. Antimicrobial peptide defense
   - DEFB4A/B, DEFB103A/B, S100A7, S100A7A, S100A8, S100A12, PI3
   
3. Keratinocyte hyperproliferation and abnormal differentiation (cornified envelope)
   - SPRR2A/B/D/E/F/G, SPRR3, LCE3A, LCE3D, KRT6A, GJB2, GJB6
   
4. Neutrophil chemotaxis/innate immune cell recruitment
   - CXCL13, CXCR2, GPR15LG
   
5. NF-κB pathway activation and negative feedback
   - TNIP3, ZC3H12A, IRAK2

6. Lipid/arachidonic acid metabolism
   - PLA2G4D, PLA2G4E, AKR1B10, AKR1B15

7. Serine protease/antiprotease balance
   - KLK13, SERPINB3, SERPINB4, SERPINB11, SERPINB13

8. Tryptophan metabolism (KYNU is kynureninase)

9. PD-L1 immune checkpoint (CD274)

10. Cell cycle/proliferation (CCNE1, RRM2)

Let me select the top 5 most important biological programs:

1. IL-36/Th17 inflammatory cytokine amplification
2. Antimicrobial peptide/barrier defense response
3. Keratinocyte cornified envelope assembly & hyperproliferation
4. NF-κB signaling and feedback regulation
5. Neutrophil and innate immune cell recruitment

Let me think about key genes:
- IL36A and IL36G are key amplifiers of psoriatic inflammation
- S100A7, S100A7A, S100A8, S100A12 are alarmins
- DEFB4A/B are strongly induced by IL-17
- KRT6A is a marker of hyperproliferative keratinocytes
- SPRR2 family members are cornified envelope proteins
- TNIP3 is a negative regulator of NF-κB, induced as feedback
- CD274 (PD-L1) is interesting - induced in keratinocytes in psoriasis
- CXCL13 and CXCR2 are chemotactic

For interaction modules, the most important ones:
- IL-36/Th17 axis
- NF-κB feedback loop (TNIP3, IRAK2, ZC3H12A)
- Cornified envelope assembly
- Antimicrobial peptide cluster

Let me think about validation priorities:
1. IL-36RN as a therapeutic target - already has biologic (spesolimab)
2. CD274 (PD-L1) expression in psoriatic keratinocytes
3. DEFB4A/B as biomarker
4. KYNU and tryptophan metabolism
5. CXCL13/CXCR2 axis

Now let me structure the response.

Note: The input shows only upregulated and downregulated genes - no prognostic HRs, so this is purely disease-state interpretation.

Let me also think about specific biological interpretations:

The downregulated genes:
- BTC (Betacellulin) - downregulated, may reflect altered EGFR signaling
- CYP2W1 - cytochrome P450, less characterized
- UGT3A2 - conjugation enzyme
- WAKMAR1 - lncRNA involved in wound healing, notably its downregulation in psoriasis
- SAPCD1 - poorly characterized

These downregulated genes are relatively few compared to upregulated, which is typical of psoriasis where inflammation drives massive transcriptional upregulation.

The WAKMAR1 downregulation is interesting - WAKMAR1 is involved in wound healing/re-epithelialization. Its downregulation in chronic psoriatic plaques may suggest disrupted resolution programs.

Let me finalize the analysis:

Major biological programs (limit to 5):

1. IL-36/Th17 cytokine inflammatory amplification
2. Antimicrobial peptide and alarmin defense response
3. Epidermal keratinocyte cornified envelope hyperproliferation/dysregulated differentiation
4. NF-κB signaling and feedback regulation
5. Innate immune cell (neutrophil) recruitment and chemotaxis

Key genes (limit to 10):
1. IL36A
2. IL36G
3. DEFB4A
4. S100A7
5. S100A8
6. TNIP3
7. KRT6A
8. CXCL13
9. CD274 (PD-L1)
10. KYNU

Validation priorities (limit to 5):
1. IL-36 pathway as therapeutic target (biomarker/mechanistic)
2. DEFB4A as psoriatic biomarker
3. CD274/PD-L1 expression in keratinocytes
4. KYNU and tryptophan metabolism
5. WAKMAR1 downregulation as disrupted resolution

Let me now write the response.</think>

# Transcriptomic Interpretation: Psoriatic Lesional Skin vs. Normal Skin

## 1. Overall Biological Interpretation

The transcriptomic profile of psoriatic lesional skin is dominated by **massive upregulation of inflammatory and epidermal defense programs**, with the upregulated set vastly outnumbering the downregulated set. The strongest signals (log₂FC > 7) converge on three biologically coherent themes:

- **IL-36 / Th17-cytokine amplification** (IL36A, IL36G, IL19, IL20, IL26) — a self-reinforcing keratinocyte–T-cell cytokine circuit that drives psoriatic inflammation.
- **Antimicrobial peptide (AMP) and alarmin bursts** (β-defensins DEFB4A/B, DEFB103A/B; S100 alarmins S100A7/A7A/A8/A12; PI3/elafin) — a stereotyped IL-17A/IL-22–induced "psoriasis signature."
- **Hyperproliferation and dysregulated cornified envelope assembly** (KRT6A, SPRR2A/B/D/E/F/G, LCE3A/D, GJB2, GJB6) — molecular hallmarks of the thickened, parakeratotic psoriatic epidermis.

Supporting these are coordinated NF-κB feedback (TNIP3, IRAK2, ZC3H12A), neutrophil chemotaxis (CXCL13, CXCR2, GPR15LG), lipid/oxidative remodeling (AKR1B10, AKR1B15, PLA2G4D/E), and tryptophan catabolism (KYNU). The downregulated arm is small but biologically informative: BTC (EGFR ligand), WAKMAR1 (a pro-re-epithelialization lncRNA), CYP2W1, UGT3A2, and SAPCD1 collectively suggest **impaired epidermal differentiation maturation and failed resolution/homeostatic signaling**, rather than broad transcriptional collapse.

---

## 2. Core Biological Programs

### Program 1 — IL-36 / Th17 Cytokine Amplification Loop
- **Direction:** Strongly upregulated.
- **Key supporting genes:** IL36A (log₂FC 11.4), IL36G (5.7), IL36RN (3.0), IL19 (7.6), IL20 (5.7), IL26 (4.4).
- **Best-matching pathway:** Reactome *Interleukin-36 signaling*; KEGG *Cytokine–cytokine receptor interaction*; Hallmark *Inflammatory response*.
- **Why these genes together:** IL36A/G are neutrophil- and keratinocyte-derived IL-17A target genes that act in an autocrine/paracrine feed-forward loop to amplify IL-17/IL-22 responses and neutrophil chemotaxis; IL36RN encodes the natural antagonist (IL-36Ra), also upregulated but functionally insufficient — its administration (spesolimab) is therapeutically validated. IL19/IL20 are IL-17A-induced keratinocyte mitogens, and IL26 is a Th17-cell-secreted antimicrobial cytokine deposited at lesional sites.
- **Evidence strength:** Very high — convergent input dataset signal, strong pathway/reactome support, and clinical trial–level therapeutic validation.
- **Limitations:** Whole-tissue RNA cannot distinguish cellular source (keratinocyte vs. immune cell) without deconvolution; effect sizes for IL36RN appear paradoxically high given that the antagonist is rarely fully protective.

### Program 2 — Antimicrobial Peptide and Alarmin Defense Response
- **Direction:** Strongly upregulated.
- **Key supporting genes:** DEFB4A (11.2), DEFB4B (11.0), DEFB103A (5.8), DEFB103B (5.8), S100A7 (7.1), S100A7A (9.8), S100A8 (7.7), S100A12 (8.3), PI3/elafin (9.2), LCN-family lipocalins (not in top list but typical).
- **Best-matching pathway:** Reactome *Innate immune responses to bacterial stimuli*; Hallmark *Inflammatory response*; GO *antimicrobial humoral response*.
- **Why these genes together:** β-defensins and S100 alarmins are direct transcriptional targets of IL-17A/IL-22/IL-36 in keratinocytes and constitute the canonical "psoriasis transcriptome signature" used in biomarker panels. Their coordinate extreme upregulation (log₂FC 5–11) reflects massive IL-17A activity.
- **Evidence strength:** Very high — these genes form one of the most replicated transcriptomic signatures in psoriasis.
- **Limitations:** The DEFB4A/DEFB4B paralogs are nearly identical and partially redundant in array-based measurements; elevation is sensitive to lesional biopsy depth and acanthosis.

### Program 3 — Epidermal Cornified Envelope Hyperproliferation and Altered Differentiation
- **Direction:** Strongly upregulated (with selective loss of homeostatic factors).
- **Key supporting genes:** SPRR2A (7.3), SPRR2B (6.4), SPRR2D (5.9), SPRR2E (4.0), SPRR2F (7.2), SPRR2G (4.8), SPRR3 (7.2), LCE3A (8.3), LCE3D (5.3), KRT6A (4.3), GJB2 (4.4), GJB6 (3.0), FABP5 (3.6), KLK13 (4.1).
- **Best-matching pathway:** Reactome *Keratinization*; GO *cornified envelope assembly*; KEGG *Keratinocyte differentiation*.
- **Why these genes together:** Small proline-rich proteins (SPRRs) and late cornified envelope (LCE) proteins are normally induced late in differentiation but are ectopically and massively upregulated in suprabasal psoriatic keratinocytes, where KRT6A (a wound-healing/hyperproliferative keratin) replaces KRT1/KRT10. Connexins GJB2/GJB6 reflect abnormal gap-junction remodeling. KLK13 (kallikrein-related peptidase) and SERPINB3/B4/B11/B13 family inhibitors indicate an altered protease/anti-protease balance on the skin surface.
- **Evidence strength:** High — replicated signature with strong ontology support.
- **Limitations:** Cannot distinguish whether changes are cause or consequence of hyperproliferation from bulk tissue; keratinocyte-specific signals are diluted by infiltrating immune cells.

### Program 4 — NF-κB Pathway Activation with Coordinated Negative Feedback
- **Direction:** Strongly upregulated (negative regulators as a feedback signature).
- **Key supporting genes:** TNIP3 (7.3), ZC3H12A/MCPIP1 (3.8), IRAK2 (2.1), PRKCQ (2.9), SERPINB3/B4 (6.7/9.1).
- **Best-matching pathway:** Reactome *NF-κB signaling*; KEGG *TNF signaling*; Hallmark *TNFA_signaling_via_NFKB*.
- **Why these genes together:** TNIP3 (TNF-α–induced protein 3-interacting protein) and ZC3H12A (an RNase that degrades cytokine mRNAs including IL-6/IL-17 targets) are well-characterized NF-κB negative-feedback effectors; their strong induction alongside IRAK2 (a proximal TLR/IL-1R kinase) and SERPINB3/B4 (which inhibit caspase and inflammasome activity) indicates **active NF-κB drive plus an attempted but overwhelmed resolution response**. PRKCQ/PKC-θ links to T-cell/NF-κB signaling.
- **Evidence strength:** High — biologically coherent module, with genetic evidence (TNIP3 loss-of-function variants associate with psoriasis and psoriatic arthritis).
- **Limitations:** Whole-tissue resolution is limited; cell-type-specific NF-κB activity (keratinocyte vs. dendritic vs. T cell) cannot be disentangled.

### Program 5 — Neutrophil and Innate Immune Cell Recruitment
- **Direction:** Strongly upregulated.
- **Key supporting genes:** CXCL13 (5.9), CXCR2 (2.7), GPR15LG (5.5), IL36A/G (above), S100A8/A12 (above), DEFB4A/B, PI3.
- **Best-matching pathway:** Reactome *Chemokine signaling*; GO *neutrophil chemotaxis*; Hallmark *Inflammatory response*.
- **Why these genes together:** CXCR2 ligands (CXCL1/2/8, and CXCL13 in B-cell/lymphoid-like patterning) plus IL-36-driven neutrophil-attracting chemokines explain the characteristic Munro microabscesses (neutrophil aggregates in the parakeratotic stratum corneum). GPR15LG is the ligand for GPR15, a homing receptor for skin-tropic T cells and a known susceptibility gene locus.
- **Evidence strength:** High — directly explains histopathology.
- **Limitations:** Chemokine cell-of-origin (keratinocyte vs. endothelial vs. resident immune cell) requires single-cell validation; CXCL13 elevation in skin is also implicated in ectopic lymphoid-like structures in chronic plaques.

---

## 3. Key Genes and Interaction Modules (≤10)

| # | Gene | Direction | Program | Relationship Type |
|---|------|-----------|---------|-------------------|
| 1 | **IL36A** | ↑↑↑ (log₂FC 11.4) | Program 1 | **Direct cytokine** — keratinocyte-derived IL-17A target; receptor IL-36R activates NF-κB/MAPK in keratinocytes and DCs; pathway co-membership with IL36G, IL19/20, DEFB4A |
| 2 | **IL36G** | ↑↑↑ (5.7) | Program 1 | Direct cytokine; same IL-36R axis as IL36A; co-expression and pathway co-membership |
| 3 | **DEFB4A** | ↑↑↑ (11.2) | Program 2 | Direct antimicrobial effector; IL-17A/IL-22/IL-36 transcriptional target; co-expression with S100A7/A8 and DEFB4B (paralog, near-identical) |
| 4 | **S100A7** (psoriasin) | ↑↑↑ (7.1) | Program 2 | Alarmin/AMP; secreted by suprabasal keratinocytes; co-expression with S100A7A, S100A8, S100A12 (gene cluster at 1q21) — represents a true genomic cluster with co-regulated expression |
| 5 | **S100A8** | ↑↑↑ (7.7) | Program 2 + 5 | Alarmin; neutrophil chemoattractant (via TLR4/RAGE); co-expressed with S100A12 and S100A7; dimerizes with S100A9 (calprotectin) |
| 6 | **TNIP3** | ↑↑↑ (7.3) | Program 4 | **NF-κB negative regulator** (inhibits NF-κB signaling by interfering with A20/TNFAIP3); genetic psoriasis/PsA susceptibility locus; **regulatory interaction** with NF-κB targets; co-expressed with other negative-feedback genes |
| 7 | **KRT6A** | ↑↑ (4.3) | Program 3 | Structural keratin of hyperproliferative keratinocytes; replaces KRT1/10 in psoriatic plaques; co-expression with KRT6B/C, KRT16, KRT17 (typical psoriatic signature) |
| 8 | **CXCL13** | ↑↑ (5.9) | Program 5 | B-cell/follicular chemokine; typically lymphoid but ectopic in chronic plaques; CXCR5 ligand (not CXCR2 — note distinction); potential indirect interaction with infiltrating T/B cells |
| 9 | **CXCR2** | ↑↑ (2.7) | Program 5 | Neutrophil chemokine receptor; receptor for CXCL1/2/5/8; likely on infiltrating neutrophils rather than keratinocytes; **direct receptor-ligand interaction** |
| 10 | **CD274 (PD-L1)** | ↑↑ (3.4) | Cross-cutting (Program 1/4) | Immune checkpoint ligand; IFN-γ/IL-17–induced on keratinocytes; **receptor interaction** with PD-1 on T cells; co-expressed with IL-36 axis — possibly a negative feedback loop dampening T-cell responses |

**Module-level interactions (explicit distinctions):**
- **Direct physical/receptor-ligand:** IL36A/G → IL-36R; CXCL chemokines → CXCR2/CXCR5; PD-L1 → PD-1.
- **Regulatory (transcriptional target):** IL17A → DEFB4A, S100A7, KRT6A (via ACT1/TRAF6/SEB), NF-κB → TNIP3 (negative feedback).
- **Co-expression / gene cluster:** S100A7/A7A/A8/A12 at 1q21; SPRR2 family cluster at 1q21; DEFB4A/DEFB4B paralog pair at 8p23.
- **Pathway co-membership:** TNIP3, ZC3H12A, IRAK2 — all in NF-κB signaling.
- **Indirect / putative:** IL-36 ↔ CD274 induction (literature-supported but not directly demonstrated in this dataset).

---

## 4. Validation Priorities (≤5)

### Priority 1 — IL-36 Pathway as a Therapeutic Target in Established Plaques
- **Type:** Therapeutic target / Mechanistic hypothesis.
- **Current dataset evidence:** IL36A, IL36G, IL36RN all strongly upregulated — confirms active pathway engagement at the lesional transcript level.
- **External evidence:** Strongly supports — spesolimab and imsidolimab (anti-IL-36R monoclonal antibodies) have demonstrated efficacy in generalized pustular psoriasis; evidence in plaque psoriasis is mixed but mechanistically sound. Genetic IL-36RN deficiency causes DITRA (gain-of-function IL-36 signaling).
- **Next step:** Stratify plaque-psoriasis patients by lesional IL36A/G RNA or protein; assess response to IL-36R blockade in IL-36-high subgroups.
- **Status:** **Established evidence** for pustular psoriasis; **supported hypothesis** for plaque psoriasis.

### Priority 2 — DEFB4A and S100A7 as Companion Biomarkers for IL-17-Pathway Activity
- **Type:** Biomarker.
- **Current dataset evidence:** DEFB4A/B (log₂FC ≈ 11) and S100A7/A7A (7–10) are among the most upregulated transcripts; coordinate induction is a recognized IL-17A read-out.
- **External evidence:** Supports — DEFB4 and S100A7 expression in lesional skin is a robust IL-17-pathway biomarker used in clinical pharmacology to verify target engagement of IL-17/IL-23 biologics (e.g., secukinumab trials).
- **Next step:** Measure lesional DEFB4A/S100A7 mRNA or protein by qPCR/IHC before and after IL-17A blockade to confirm pharmacodynamic response; assess serum S100A7/A8 as a non-invasive correlate.
- **Status:** **Established evidence** as pharmacodynamic biomarker; **supported hypothesis** for prognostic stratification.

### Priority 3 — TNIP3 / NF-κB Negative Feedback Failure as a Mechanism of Chronicity
- **Type:** Mechanistic hypothesis / Interaction-network hypothesis.
- **Current dataset evidence:** TNIP3 is among the most upregulated transcripts (log₂FC 7.3) despite being a *negative* NF-κB regulator — strongly suggests attempted but insufficient feedback; co-induced with ZC3H12A.
- **External evidence:** Supports — TNIP3 is a confirmed GWAS locus for psoriasis; rare loss-of-function variants predispose to psoriatic arthritis; TNIP3 deficiency in mice exacerbates skin inflammation.
- **Next step:** Compare TNIP3 induction between acute and chronic plaque transcriptomes; assess whether non-responders to IL-17/IL-23 blockade have lower TNIP3 induction; consider keratinocyte-specific TNIP3 knockdown in 3D skin models.
- **Status:** **Supported hypothesis.**

### Priority 4 — Keratinocyte PD-L1 (CD274) Induction as a Local Immune-Checkpoint Brake
- **Type:** Mechanistic hypothesis / Therapeutic-target contextualization.
- **Current dataset evidence:** CD274 (PD-L1) is significantly upregulated (log₂FC 3.4), co-occurring with massive IFN-γ/IL-17-driven inflammation — implies a keratinocyte-intrinsic attempt to inhibit infiltrating T cells.
- **External evidence:** Mixed/conflicting — systemic PD-1/PD-L1 blockade can both improve and exacerbate psoriasis (paradoxical psoriasis), and keratinocyte PD-L1 induction has been described in inflammatory skin. However, whether this represents protective feedback or contributes to chronic dysregulation is unsettled.
- **Next step:** Single-cell RNA-seq to confirm PD-L1 expression is keratinocyte-intrinsic; immunohistochemistry for PD-L1 protein in lesional epidermis; correlate with lesional T-cell activity.
- **Status:** **Exploratory hypothesis** — biology is plausible but evidence in this dataset is correlative only.

### Priority 5 — KYNU and Tryptophan Catabolism as a Modulator of Lesional Immune Tone
- **Type:** Mechanistic hypothesis.
- **Current dataset evidence:** KYNU (kynureninase, log₂FC 4.4) is among the top upregulated transcripts; KYNU drives tryptophan → 3-hydroxyanthranilic acid, which can skew toward Treg differentiation and suppress effector T cells.
- **External evidence:** Supports — KYNU is induced by IFN-γ, and IDO1/KYNU axis activation is documented in psoriatic skin; downstream metabolites are immunomodulatory.
- **Next step:** Measure kynurenine pathway metabolites (kynurenine, 3-HAA, quinolinic acid) in lesional vs. non-lesional skin and serum; assess correlation with disease severity; experimentally test whether pathway inhibition (e.g., 1-methyl-D/L-tryptophan) worsens or improves inflammation in preclinical models.
- **Status:** **Supported hypothesis.**

---

## 5. Evidence Grounding (Cross-Cutting)

| Claim | Dataset | Pathway/Ontology | Protein Interaction | Disease Association | Expression/Tissue | Genetic/Clinical | Drug/Therapeutic |
|-------|---------|------------------|--------------------|--------------------|--------------------|------------------|------------------|
| IL-36 axis drives inflammation | ✔ (IL36A/G↑↑↑) | ✔ Reactome | ✔ IL-36R known | ✔ Strong | ✔ Keratinocyte | ✔ DITRA | ✔ Spesolimab |
| AMP/alarmin burst | ✔ (S100/DEFB↑↑↑) | ✔ GO AMP response | Limited | ✔ Strong | ✔ Keratinocyte | — | ✔ Used as PD biomarker |
| Cornified envelope dysregulation | ✔ (SPRR/LCE↑) | ✔ Reactome keratinization | Co-expression | ✔ Strong | ✔ Suprabasal KC | — | — |
| NF-κB feedback | ✔ (TNIP3↑↑) | ✔ NF-κB pathway | ✔ A20/TNIP3 complex | ✔ GWAS locus | ✔ | ✔ PsA risk | — |
| Neutrophil recruitment | ✔ (CXCL/CXCR2↑) | ✔ Chemokine signaling | ✔ CXCR2 ligand | ✔ Histology | ✔ | — | CXCR2 antagonists (developmental) |
| KYNU/tryptophan | ✔ (KYNU↑) | ✔ KEGG tryptophan metabolism | — | Moderate | Mixed | — | IDO inhibitors (oncology) |

**Independent vs. overlapping evidence:** The IL-36, AMP, and cornified-envelope programs are **genuinely independent** at the gene level (different genomic loci, distinct transcription factors: NF-κB/CEBP/AP-1 for AMP, KLF/p63 dysregulation for cornified envelope). The NF-κB feedback program partly **overlaps** with the IL-36 and AMP programs because NF-κB is upstream of all three — feedback gene induction therefore serves as a single cross-cutting signal rather than truly independent evidence.

**Conflicting evidence:** The CD274 (PD-L1) induction conflicts with the prevailing view that psoriasis is a relatively PD-1-independent disease; this warrants caution before assuming functional significance.

---

## 6. Limitations and Alternative Explanations

1. **Tissue/cell-composition confounding (most important).** Psoriatic plaques contain infiltrating neutrophils, T cells, dendritic cells, and macrophages in addition to altered keratinocyte mass. Upregulated transcripts (CXCL13, CXCR2, CD274, IL26, IL19/20) may reflect infiltrating immune cells rather than keratinocyte-intrinsic gene expression. **How to test:** Single-cell RNA-seq or spatial transcriptomics; deconvolution with reference signatures (e.g., CIBERSORTx); in situ hybridization.

2. **Acanthosis and biopsy depth.** The thickened epidermis in plaques inflates keratinocyte-derived transcripts (KRT6A, SPRR2, LCE3) relative to normal skin partly because of increased cell number, not just per-cell induction. **How to test:** Report expression per estimated keratinocyte count; compare with non-lesional psoriatic skin to control for baseline acanthosis.

3. **Treatment exposure and disease duration.** If biopsy donors had prior topical or systemic therapy, immunosuppression could partially suppress inflammatory programs and produce a mixed signal. Conversely, treatment-naïve chronic plaques may reflect a partially resolved or adapted inflammatory state. **How to test:** Stratify by treatment history and disease chronicity.

4. **Small-subgroup and demographic effects.** Age, sex, body site (intertriginous vs. extensor), and PASI score can shift the inflammatory balance (e.g., IL-36 dominance in pustular phenotypes). A few of the downregulated genes (WAKMAR1, SAPCD1) may reflect rare homeostatic lncRNAs whose loss is sample-specific. **How to test:** Larger cohorts with metadata; sensitivity analyses.

5. **Association vs. causation and circular pathway enrichment.** Many "pathways" (NF-κB, chemokine, AMP) are interrelated hubs — apparent pathway enrichment can reflect a single NF-κB-driven transcriptional wave rather than discrete biological programs. The dataset cannot distinguish causative drivers from secondary consequences (e.g., SPRR2 induction may simply follow hyperproliferation, not drive it). **How to test:** Perturbation studies (CRISPR knockdown of TNIP3 or IL36A in 3D skin models); Mendelian randomization using psoriasis GWAS instruments.

---

**Bottom line:** The transcriptomic landscape of psoriatic lesional skin is dominated by a coordinated **IL-36/IL-17A-driven inflammatory amplification loop** that induces antimicrobial peptides, neutrophil chemokines, and a hyperproliferative/dysdifferentiation program in keratinocytes — with **NF-κB negative feedback (TNIP3, ZC3H12A) engaged but apparently insufficient**. The strongest, most actionable signals are IL-36 pathway engagement, AMP induction as a pharmacodynamic biomarker, and the unmet therapeutic opportunity represented by **keratinocyte PD-L1 upregulation** and **tryptophan catabolism via KYNU**, both of which merit focused experimental validation.
