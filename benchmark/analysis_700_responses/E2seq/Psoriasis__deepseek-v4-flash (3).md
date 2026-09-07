# psoriasis - deepseek-v4-flash

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
- Model API: DeepSeek / deepseek-v4-flash
- Message SHA-256: d1a33d3f606c81814c4fb94a6c63c8f1abebd3bde37d769e82eae4772d8ff873
- Response HTTP status: 200
- Prompt tokens: 49126
- Completion tokens: 21496
- Reasoning tokens: 0
- Total tokens: 70622
- API requests reported: 4
- Elapsed seconds: 112.287
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 1150.303
- Question handoff seconds: 1163.566
- Final benchmark system: E2seq; file rank 3/5; original repeat 5; model vendor: DeepSeek

---
# Multidimensional Interpretation of Psoriatic Lesional Skin Transcriptomics

## 1. Overall Biological Interpretation

The transcriptomic profile of psoriatic lesional skin versus normal control skin reveals a coordinated, multi-layered inflammatory and epithelial response. The most striking feature is the dominance of **IL-36/IL-17 axis-driven innate inflammation** (IL36A log2FC=11.37, IL36G=5.68, IL19=7.58, IL20=5.67, IL26=4.36), accompanied by **massive antimicrobial peptide induction** (DEFB4A=11.18, DEFB4B=11.03, S100A7A=9.83, PI3=9.24, S100A12=8.33, S100A8=7.73, S100A7=7.09), and **profound epidermal differentiation dysregulation** with upregulation of cornified envelope components (SPRR2A-F, SPRR3, LCE3A/D) alongside the keratinocyte hyperproliferation marker KRT6A (4.30). The concurrent upregulation of neutrophil chemoattractant receptors (CXCR2=2.70) and lipid-metabolizing enzymes (PLA2G4D=4.61, PLA2G4E=2.47, KYNU=4.42) points to a **neutrophilic infiltrate and altered lipid/amino-acid metabolism** characteristic of the psoriatic plaque. Notably, the downregulated genes (BTC, CYP2W1, SAPCD1 and its antisense, WAKMAR1, UGT3A2, and several uncharacterized LOCs) are fewer (10/100) and suggest **loss of normal epidermal differentiation/maturation programs** and possibly altered xenobiotic metabolism in lesional skin. All 100 genes pass FDR ≤ 0.01, providing a statistically robust foundation, though the analysis is limited to a single comparison without independent cohort validation.

## 2. Core Biological Programs

### Program 1: IL-36/IL-17-Driven Innate Inflammation
- **Direction:** Upregulated
- **Major supporting genes:** IL36A (11.37), IL36G (5.68), IL36RN (3.01), IL19 (7.58), IL20 (5.67), IL26 (4.36), IRAK2 (2.08), ZC3H12A (3.85), TNIP3 (7.28)
- **Pathway:** KEGG IL-17 signaling pathway; Reactome Interleukin-20 family signaling (R-HSA-8854691)
- **Explanation:** The IL-36 cytokines (IL36A, IL36G) are keratinocyte-derived amplifiers of the IL-23/IL-17 axis in psoriasis. Their co-upregulation with the IL-20 family members (IL19, IL20, IL26) and the signaling adaptor IRAK2, together with the NF-κB negative regulator TNIP3 (an inducible feedback gene), indicates an active, self-amplifying inflammatory loop. IL36RN (the receptor antagonist) is also induced, suggesting concurrent negative feedback—a pattern consistent with chronic, partially compensated inflammation.
- **Evidence strength:** Strong direct statistical support (multiple genes, very low FDR); pathway coherence is high. Limitations: this is a single-cohort transcriptomic snapshot; the IL-36/IL-17 relationship is inferred from pathway membership, not demonstrated causally here.

### Program 2: Antimicrobial Peptide and S100 Alarmin Response
- **Direction:** Upregulated
- **Major supporting genes:** DEFB4A (11.18), DEFB4B (11.03), DEFB103A (5.76), DEFB103B (5.75), S100A7 (7.09), S100A7A (9.83), S100A8 (7.73), S100A12 (8.33), PI3 (9.24)
- **Pathway:** GO Antimicrobial Humoral Response (GO:0019730); KEGG Staphylococcus aureus infection
- **Explanation:** Psoriatic epidermis characteristically overproduces antimicrobial peptides (β-defensins, S100 proteins, PI3/skin-derived antileukoprotease). These genes cluster tightly and are among the most strongly induced in the dataset. They serve dual roles: direct antimicrobial defense and, for S100 proteins, as alarmins that amplify inflammation via RAGE and TLR4 signaling.
- **Evidence strength:** Strong direct evidence; the STRING network shows S100A7 connecting to FABP5, S100A12, S100A7A, SERPINB3/B4, and CCR6 connecting to the defensins, supporting a coordinated module. Limitation: antimicrobial peptide expression in lesional skin may partly reflect the altered microbial colonization of psoriatic plaques rather than a primary driver.

### Program 3: Aberrant Epidermal Differentiation and Cornified Envelope Formation
- **Direction:** Mostly upregulated (with select downregulated differentiation genes)
- **Major supporting genes:** SPRR2A (7.31), SPRR2B (6.38), SPRR2D (5.92), SPRR2E (3.99), SPRR2F (7.22), SPRR2G (4.75), SPRR3 (7.18), LCE3A (8.30), LCE3D (5.31), KRT6A (4.30), GJB2 (4.42), GJB6 (3.02), KLK13 (4.05), SERPINB3 (6.74), SERPINB4 (9.12), TCN1 (8.04); Downregulated: BTC (-4.30), CYP2W1 (-4.70)
- **Pathway:** Reactome Formation of the cornified envelope (R-HSA-6809371); GO Epidermis Development (GO:0008544)
- **Explanation:** The coordinated upregulation of small proline-rich proteins (SPRR2 family, SPRR3), late cornified envelope proteins (LCE3A, LCE3D), keratins (KRT6A), and gap junction proteins (GJB2, GJB6) reflects the **hyperproliferative/regenerative differentiation phenotype** of psoriatic epidermis, where the normal terminal differentiation program is replaced by a "wound-healing" keratins (KRT6) and premature cornification. The serine protease inhibitor SERPINB3/B4 and KLK13 co-upregulation suggests altered protease–antiprotease balance in the stratum corneum. Downregulation of BTC (betacellulin) and CYP2W1 may reflect loss of normal suprabasal differentiation and metabolic maturation.
- **Evidence strength:** Strong direct evidence; Reactome cornified envelope pathway lists 12 of the selected genes. Limitation: the SPRR/LCE upregulation could partly reflect the **thickened, parakeratotic epidermis** composition rather than a purely cell-intrinsic program change.

### Program 4: Neutrophil Recruitment and Lipid Mediator Metabolism
- **Direction:** Upregulated
- **Major supporting genes:** CXCR2 (2.70), CXCL13 (5.89), PLA2G4D (4.61), PLA2G4E (2.47), HPSE (2.92), KYNU (4.42), GDA (5.90), HRH2 (3.27), SLC6A14 (4.47)
- **Pathway:** GO Response to Lipopolysaccharide (GO:0032496); KEGG Cytokine-cytokine receptor interaction
- **Explanation:** CXCR2 is the receptor for IL-8/CXCL1/2/3 and mediates neutrophil recruitment—a hallmark of psoriatic plaques. The phospholipase A2 group IV members (PLA2G4D, PLA2G4E) generate arachidonic acid and lysophospholipids, fueling eicosanoid production and potentially activating the NLRP3 inflammasome. HPSE (heparanase) degrades extracellular matrix heparan sulfate, releasing growth factors and facilitating leukocyte trafficking. KYNU (kynureninase) and GDA (guanine deaminase) point to altered tryptophan and purine metabolism. The STRING network links PLA2G4D/PLA2G4E to GNAS and HRH2, suggesting a G-protein-coupled signaling module.
- **Evidence strength:** Moderate-to-strong direct evidence; functional coherence is plausible but the connection between lipid metabolism and neutrophil recruitment is indirect in this dataset. Limitation: without cell-type deconvolution, we cannot determine whether PLA2G4D/E and CXCR2 are expressed in the same cells or represent different infiltrating populations.

### Program 5: Immune Checkpoint and T-Cell Co-stimulation Module
- **Direction:** Upregulated
- **Major supporting genes:** CD274 (PD-L1, 3.44), PRKCQ (PKCθ, 2.88), CXCL13 (5.89), ADAP2 (2.09), TRIM15 (4.54), TRIM10 (4.04)
- **Pathway:** Reactome PD-1 signaling; GO immune response
- **Explanation:** CD274 (PD-L1) upregulation in psoriatic skin is a known counter-regulatory mechanism that may limit T-cell-driven inflammation. PRKCQ (PKCθ) is a critical TCR signaling component in T cells and has been genetically associated with psoriasis. CXCL13 marks tertiary lymphoid structures and follicular helper T-cell infiltration. The TRIM family members may regulate innate immune signaling. This module suggests an **active T-cell infiltrate with concurrent immune-checkpoint engagement**—a balance between inflammation and its negative regulation.
- **Evidence strength:** Moderate direct evidence (individual genes significant but the module is less cohesive than Programs 1–3). Limitation: the functional relationship between CD274 and PRKCQ in this context is inferred from pathway membership, not demonstrated in the data.

## 3. Key Genes and Interaction Modules

### Module A: IL-36 Signaling Hub (IL36A, IL36G, IL36RN, IL1RAP)
- **Direction:** All upregulated (IL36A=11.37, IL36G=5.68, IL36RN=3.01)
- **Role:** Central to Program 1; IL-36 cytokines are keratinocyte-derived amplifiers of the IL-23/IL-17 axis.
- **Gene-gene relationships:** STRING records show direct physical interaction between IL36A and IL1RL2 (confidence=0.996), IL36A and IL1RAP (0.908), and IL36A with IL36RN (0.789). IL36RN is the natural receptor antagonist, so its co-upregulation with the agonists suggests a **regulatory feedback loop** (pathway co-membership plus direct binding evidence). This is a direct physical interaction for IL36A–IL1RL2/IL1RAP; the IL36RN antagonism is a receptor-level regulatory interaction.

### Module B: Antimicrobial Peptide Cluster (DEFB4A, DEFB4B, DEFB103A/B, S100A7, S100A7A, PI3)
- **Direction:** All strongly upregulated (log2FC 5.75–11.18)
- **Role:** Program 2; antimicrobial defense and alarmin function.
- **Gene-gene relationships:** STRING shows CCR6 connecting to DEFB4A/B and DEFB103A (pathway co-membership/co-expression, not necessarily direct binding). S100A7 connects to FABP5, S100A12, S100A7A, SERPINB3/B4 in STRING—these are likely co-expression or shared pathway relationships rather than verified physical interactions. The defensins and S100 genes are clustered in the epidermal differentiation complex on chromosome 1q21 and 8p23, respectively, so **genomic co-localization** may drive co-regulation.

### Gene C: CXCR2
- **Direction:** Upregulated (2.70)
- **Role:** Neutrophil chemoattractant receptor; central to Program 4.
- **Gene-gene relationships:** No direct interaction evidence in the retrieved STRING records for CXCR2 with the other selected genes. Its relationship to PLA2G4D/E and HPSE is best described as **pathway co-membership** (neutrophil recruitment/activation) rather than direct interaction.

### Gene D: CD274 (PD-L1)
- **Direction:** Upregulated (3.44)
- **Role:** Immune checkpoint; potential negative feedback on T-cell inflammation.
- **Gene-gene relationships:** No direct interaction with other selected genes in STRING records. Its co-upregulation with PRKCQ and CXCL13 suggests **co-occurrence in the inflamed T-cell microenvironment** (indirect/putative relationship).

### Gene E: SERPINB3/SERPINB4
- **Direction:** Upregulated (6.74 and 9.12, respectively)
- **Role:** Serine protease inhibitors; may protect against excessive protease activity in the hyperproliferative epidermis.
- **Gene-gene relationships:** STRING shows CTSG (cathepsin G) connecting to SERPINB13, SERPINB3, SERPINB4—this is a plausible **direct physical interaction** (protease–inhibitor binding), though the confidence values are not provided in the retrieved records. The co-upregulation with KLK13 suggests altered protease–antiprotease balance.

### Gene F: WNT5A
- **Direction:** Upregulated (2.53)
- **Role:** Non-canonical Wnt signaling; implicated in epidermal regeneration and inflammation.
- **Gene-gene relationships:** No direct interaction with other selected genes in retrieved records. Its relationship to the epidermal differentiation program is **indirect/putative** (Wnt signaling modulates keratinocyte differentiation).

### Gene G: HPSE (Heparanase)
- **Direction:** Upregulated (2.92)
- **Role:** Extracellular matrix remodeling; releases growth factors and facilitates immune cell trafficking.
- **Gene-gene relationships:** No direct interaction evidence with other selected genes retrieved. Its relationship to CXCR2-mediated neutrophil recruitment is **indirect** (both contribute to leukocyte infiltration).

### Gene H: KYNU
- **Direction:** Upregulated (4.42)
- **Role:** Tryptophan metabolism; kynurenine pathway activation may modulate T-cell responses.
- **Gene-gene relationships:** No direct interaction with other selected genes in retrieved records. Its role is **metabolic**, potentially feeding into immune regulation via aryl hydrocarbon receptor (AhR) ligands—an indirect relationship.

### Gene I: TCN1 (Transcobalamin I)
- **Direction:** Upregulated (8.04)
- **Role:** Vitamin B12-binding protein; neutrophil granule component.
- **Gene-gene relationships:** TCN1 is a neutrophil granule protein, so its upregulation likely reflects **neutrophil infiltration** (indirect evidence of the cellular composition change). No direct interaction with other selected genes.

### Gene J: ADGRF1 (GPR111)
- **Direction:** Upregulated (6.64)
- **Role:** Adhesion G-protein-coupled receptor; may regulate keratinocyte adhesion/differentiation.
- **Gene-gene relationships:** No direct interaction with other selected genes retrieved. Its relationship to the epidermal program is **putative**—adhesion GPCRs are poorly characterized in psoriasis.

## 4. Validation Priorities

### Priority 1: IL-36/IL-17 Axis Functional Validation
- **Classification:** Mechanistic hypothesis
- **Why:** The IL-36 family is the most strongly induced cytokine module (IL36A=11.37, IL36G=5.68) and is central to the psoriasis inflammatory loop. Validating its functional role will determine whether the observed expression pattern is causal or reactive.
- **Dataset evidence:** Direct upregulation of IL36A, IL36G, IL36RN, IRAK2, TNIP3 with very low FDR.
- **External evidence:** IL-36 blockade is in clinical trials for psoriasis (spesolimab); the IL-36/IL-17 amplification loop is well documented in the literature (PubMed records support this). However, **external statistical validation was not performed** in this dataset.
- **Next step:** In vitro keratinocyte stimulation with IL-36A/IL-36G + IL-17A, measuring downstream S100/defensin expression; or ex vivo lesional skin explant culture with IL-36 receptor antagonist.
- **Status:** **Supported hypothesis** (strong direct evidence + established literature, but not validated in an independent cohort here).

### Priority 2: Cell-Type Deconvolution and Composition Check
- **Classification:** Confounding or composition check
- **Why:** The massive upregulation of neutrophil granule proteins (TCN1, S100A8/A12, defensins) and T-cell markers (PRKCQ, CXCL13) likely reflects the **cellular composition** of lesional skin (neutrophil and T-cell infiltrate) rather than purely keratinocyte-intrinsic transcriptional changes. Distinguishing composition from cell-intrinsic changes is essential for correct interpretation.
- **Dataset evidence:** The pattern of co-upregulated immune and keratinocyte genes is consistent with a mixed infiltrate, but bulk RNA-seq cannot resolve this.
- **External evidence:** Single-cell RNA-seq of psoriatic skin (published) shows that S100A7/A8/A12 and defensins are predominantly keratinocyte-derived, while CXCL13 and PRKCQ are immune-cell-derived. This supports a mixed origin.
- **Next step:** Single-cell RNA-seq or deconvolution (CIBERSORTx, MuSiC) of the same samples; immunohistochemistry for key markers (S100A7, CD3, MPO).
- **Status:** **Established evidence** that cell composition differs; the specific contribution to each gene's log2FC requires validation.

### Priority 3: Cornified Envelope Program as a Disease-Activity Biomarker
- **Classification:** Biomarker
- **Why:** The SPRR/LCE/KRT6A module is consistently and strongly upregulated (log2FC 3.99–8.30) and may serve as a molecular readout of epidermal hyperplasia and disease activity.
- **Dataset evidence:** SPRR2A–G, SPRR3, LCE3A/D, KRT6A all strongly upregulated with FDR < 1e-60.
- **External evidence:** LCE3B/3C deletion is a psoriasis risk locus (GWAS), and SPRR/LCE expression tracks with PASI improvement after treatment in published studies. External statistical validation was not performed here.
- **Next step:** Test whether SPRR2/LCE3 expression correlates with PASI score or treatment response in an independent cohort (qPCR or RNA-seq).
- **Status:** **Supported hypothesis** (strong direct evidence + genetic risk association from GWAS, but no independent transcriptomic validation in this analysis).

### Priority 4: Protease–Antiprotease Balance (SERPINB3/B4–KLK13–CTSG)
- **Classification:** Interaction/network hypothesis
- **Why:** The coordinated upregulation of SERPINB3/B4 (6.74, 9.12) with KLK13 (4.05) and the STRING-predicted CTSG interaction suggests that altered protease–antiprotease balance may contribute to the parakeratosis and barrier dysfunction of psoriatic skin.
- **Dataset evidence:** Direct upregulation of SERPINB3, SERPINB4, SERPINB11, SERPINB13, KLK13.
- **External evidence:** STRING predicts CTSG–SERPINB3/B4 interaction (direct physical interaction, protease–inhibitor); published literature supports kallikrein dysregulation in psoriasis. The interaction is **predicted**, not experimentally confirmed in this dataset.
- **Next step:** Co-immunoprecipitation or activity-based protease assays in psoriatic keratinocytes; measure KLK13 activity in lesional scale extracts.
- **Status:** **Exploratory hypothesis** (the interaction is predicted from STRING; direct experimental confirmation is required).

### Priority 5: CD274/PD-L1 as a Negative-Feedback Checkpoint in Psoriatic Inflammation
- **Classification:** Mechanistic hypothesis / Therapeutic target (with caution)
- **Why:** CD274 upregulation (3.44) in lesional skin suggests an endogenous brake on T-cell inflammation. Understanding whether this represents a protective feedback or a marker of chronic antigenic stimulation is important for both disease biology and therapeutic considerations (anti-PD-1 therapy can trigger or exacerbate psoriasis).
- **Dataset evidence:** Direct upregulation of CD274 alongside T-cell markers (PRKCQ, CXCL13).
- **External evidence:** Published case reports document psoriasis flares during anti-PD-1 cancer immunotherapy; PD-L1 is expressed on psoriatic keratinocytes. This is **disease-association and drug evidence**, not proof of a therapeutic target for psoriasis.
- **Next step:** Immunohistochemistry for PD-L1 on lesional skin; functional assays blocking PD-L1 in psoriatic skin explants to test whether inflammation increases.
- **Status:** **Exploratory hypothesis**. The existence of anti-PD-1 drugs does not imply that PD-L1 is an effective therapeutic target for psoriasis; rather, the checkpoint may be a disease-modulating factor.

## 5. Evidence Grounding Summary

| Claim | Direct Dataset Evidence | Pathway/Ontology | Interaction/Regulatory | Disease-Association | Literature | Independence Assessment |
|---|---|---|---|---|---|---|
| IL-36/IL-17 axis activation | IL36A, IL36G, IL19, IL20, IL26, IRAK2 up (FDR<1e-60) | KEGG IL-17; Reactome IL-20 family | STRING: IL36A–IL1RL2/IL1RAP direct binding; IL26–IL10RB/IL20RA | GWAS: IL36RN mutations in generalized pustular psoriasis | Extensive psoriasis literature | Direct + pathway + interaction records may share underlying publications; the IL-36/IL-17 loop is supported by multiple independent gene families |
| Antimicrobial peptide/alarmin response | DEFB4A/B, DEFB103A/B, S100A7/A7A/A8/A12, PI3 strongly up | GO antimicrobial humoral response | STRING: S100A7 cluster, CCR6–defensin links (co-expression likely) | S100 genes in epidermal differentiation complex (psoriasis GWAS locus) | Well-documented | Direct evidence strong; STRING edges likely reflect co-expression rather than verified physical binding |
| Cornified envelope dysregulation | SPRR2A–G, SPRR3, LCE3A/D, KRT6A up | Reactome cornified envelope (12 genes) | STRING: SPRR2B–LCE3A/D–SPRR2D/E/F cluster | LCE3B/C deletion GWAS risk | Published | Direct + pathway + GWAS are genuinely independent evidence classes |
| Neutrophil recruitment/lipid metabolism | CXCR2, PLA2G4D/E, HPSE, KYNU up | GO LPS response | STRING: PLA2G4D/E–GNAS–HRH2 (indirect/co-expression) | Neutrophilic pustules are a psoriasis hallmark | Published | Direct evidence strong; the functional link between lipid metabolism and neutrophil recruitment is inferred, not demonstrated |
| Immune checkpoint engagement | CD274, PRKCQ, CXCL13 up | Reactome PD-1 signaling | No direct interaction retrieved | Anti-PD-1 triggers psoriasis flares (case reports) | Published case series | Direct evidence + clinical case reports are independent; no interaction evidence retrieved |

## 6. Limitations and Alternative Explanations

### Limitation 1: Tissue/Cell-Composition Differences
The bulk tissue comparison of lesional versus normal skin conflates **changes in cell proportions** (increased neutrophils, T cells, Langerhans cells; altered keratinocyte differentiation state) with **cell-intrinsic transcriptional changes**. Genes like TCN1, CXCL13, and PRKCQ likely reflect immune-cell infiltration rather than keratinocyte-specific upregulation. **Investigation:** single-cell RNA-seq, deconvolution, or immunohistochemistry to assign gene expression to specific cell types.

### Limitation 2: Disease Severity and Heterogeneity
Psoriasis lesions vary in severity, stage (early vs. chronic plaque), and body site. The current dataset does not provide PASI scores, lesion duration, or anatomic site. The extreme log2FC values (some >10) may reflect a particularly severe or active lesion cohort. **Investigation:** stratify by PASI or lesion chronicity; compare with non-lesional skin from the same patients (which would control for genetic background and systemic factors).

### Limitation 3: Treatment Exposure
The dataset does not indicate whether patients were treatment-naïve or had prior/current topical or systemic therapy. Many psoriasis treatments (corticosteroids, biologics, methotrexate) profoundly alter the transcriptome, potentially dampening or reshaping the inflammatory signature. **Investigation:** obtain treatment history; if unavailable, compare with published treatment-naïve psoriatic skin datasets.

### Limitation 4: Batch/Platform Effects and Technical Artifacts
The presence of multiple uncharacterized LOCs (LOC105376238, LOC105376239, LOC105371569, LOC105376342, LOC112268153) and pseudogenes (VNN3P) among the top hits raises the question of whether some signals reflect mapping artifacts, multi-mapping reads, or annotation issues rather than genuine biological regulation. **Investigation:** verify with qPCR or independent RNA-seq platform; check read alignment quality for these loci.

### Limitation 5: Association-Versus-Causation Ambiguity and Pathway Overlap
The co-upregulation of IL-36, S100, and cornified envelope genes may reflect a **shared upstream driver** (e.g., IL-17A, TNF, or IL-22) rather than independent programs. The pathways are highly interconnected—IL-17 induces both S100 genes and keratinocyte hyperproliferation markers. This is not a limitation of the statistics but of the interpretative framework: the "programs" I identified may be **facets of a single IL-17-driven response** rather than independent biological processes. **Investigation:** perturbation experiments (IL-17 blockade in skin explants) to determine which downstream genes are directly regulated versus indirectly affected.

---

**In summary**, this transcriptomic profile provides strong direct evidence (all 100 genes at FDR ≤ 0.01) for an IL-36/IL-17-driven inflammatory response with coordinated antimicrobial peptide induction, epidermal differentiation dysregulation, and neutrophil recruitment in psoriatic lesional skin. The most defensible conclusions are the activation of the IL-36/IL-17 axis and the cornified envelope/antimicrobial program; the specific cell-type origins and causal relationships require single-cell resolution and functional validation, and external statistical validation was not performed in this analysis.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=2, external claims checked=0, external mismatches=0, status=needs review.

Answer model API: deepseek / deepseek-v4-flash.

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 91/100 selected items (records returned); cbioportal 91/100 selected items (records returned); chembl 11/100 selected items (partially returned; some queries failed); civic 4/100 selected items (records returned); clinicaltrials 40/100 selected items (records returned); clinvar 90/100 selected items (records returned); ensembl 44/100 selected items (partially returned; some queries failed); europepmc 848 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 83/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 76/100 selected items (records returned); humanbase 100/100 selected items (records returned); intact 79/100 selected items (records returned); mygene 100/100 selected items (records returned); omnipath 36/100 selected items (records returned); opentargets 90/100 selected items (records returned); pubmed 669 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 80/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 80/100 selected items (records returned)
Local databases: gutmgene 2/100 selected items (records returned); hmdb 25/100 selected items (records returned); string 78/100 selected items (records returned); trrust 17/100 selected items (records returned)
