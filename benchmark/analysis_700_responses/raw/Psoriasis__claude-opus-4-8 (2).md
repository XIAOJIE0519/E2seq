# psoriasis - claude-opus-4-8

- Benchmark system: raw
- Repeat: 2
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
- Elapsed seconds: 121.664
- Final benchmark system: raw; file rank 2/5; original repeat 2; model vendor: Anthropic

---
# Multidimensional Interpretation of Psoriasis Lesional Skin Transcriptomics

## 1. Overall Biological Interpretation

The transcriptomic profile of psoriatic lesional skin reveals a coordinated hyperactivation of multiple innate immune and epithelial stress response programs characteristic of chronic inflammatory barrier disease. The molecular signature is dominated by profound upregulation of IL-36 family cytokines (IL36A, IL36G, IL36RN), antimicrobial peptides (S100A7/A7A/A8/A12, DEFB4A/B, DEFB103A/B), and keratinocyte differentiation markers (SPRR2 family members, LCE3 proteins), indicating simultaneous activation of innate immunity, antimicrobial defense, and aberrant epidermal differentiation.

The coordinated expression of chemokines (CXCL13), chemokine receptors (CXCR2), immune checkpoint molecules (CD274/PD-L1), and inflammatory signaling mediators (ZC3H12A, IRAK2) alongside keratinocyte-specific responses suggests active crosstalk between immune infiltrates and resident epithelial cells. Notably, the selective downregulation of a small number of genes including BTC (epidermal growth factor family) and metabolic enzymes (CYP2W1, UGT3A2) suggests concurrent suppression of homeostatic epithelial programs during inflammation.

This pattern is consistent with psoriasis as a disease of immune-epithelial circuit activation rather than a purely immune-driven or purely epithelial disorder, with multiple positive feedback loops maintaining the inflammatory state.

## 2. Core Biological Programs

### Program 1: IL-36/IL-17 Axis and Innate Immune Amplification

**Direction:** Strongly upregulated

**Major supporting genes:** IL36A (log2FC=11.37), IL36G (log2FC=5.68), IL36RN (log2FC=3.01), IL19 (log2FC=7.58), IL20 (log2FC=5.67), IL26 (log2FC=4.36), S100A7 (log2FC=7.09), S100A7A (log2FC=9.83), S100A8 (log2FC=7.73), S100A12 (log2FC=8.33), DEFB4A/B (log2FC=11.18/11.03)

**Pathway:** GO:0002376 (immune system process), Reactome: Interleukin-36 signaling, KEGG: IL-17 signaling pathway

**Biological interpretation:** The dramatic upregulation of IL-36 family cytokines, particularly IL36A with the highest statistical significance in the dataset (P=2.5×10⁻¹⁰²), represents a central pathogenic mechanism in psoriasis. IL-36 cytokines are keratinocyte-derived alarmins that amplify both innate and adaptive immune responses. The co-expression of IL-19, IL-20, and IL-26 (all members of the IL-10 superfamily with pro-inflammatory functions in skin) alongside massive induction of antimicrobial peptides (S100A7/A7A/A8/A12, multiple beta-defensins) indicates coordinated activation of a keratinocyte-intrinsic defense program. The presence of IL36RN (IL-36 receptor antagonist) represents an insufficient counter-regulatory response. This program directly links keratinocyte activation to recruitment and activation of neutrophils and T cells through S100 proteins and chemokines.

**Evidence strength:** Very strong. Multiple independent genes within the IL-36 pathway show extreme effect sizes and statistical significance. This is supported by established disease-association evidence (IL36RN loss-of-function mutations cause generalized pustular psoriasis), therapeutic evidence (anti-IL-36 receptor antibody spesolimab is approved for pustular psoriasis), and protein interaction evidence (IL-36 cytokines share the same receptor complex).

**Limitations:** While IL-36 pathway activation is clearly present, the current dataset cannot distinguish whether this represents a primary driver versus an amplification loop secondary to other triggers. The IL-17 pathway components are less prominently represented in this gene list, though S100A7/A8/A9 are known IL-17 target genes, suggesting IL-17 signaling may be captured indirectly.

### Program 2: Aberrant Keratinocyte Differentiation and Cornification

**Direction:** Strongly upregulated

**Major supporting genes:** SPRR2A/B/D/E/F/G (log2FC=7.32/6.38/5.92/3.99/7.22/4.75), SPRR3 (log2FC=7.18), LCE3A (log2FC=8.30), LCE3D (log2FC=5.31), KRT6A (log2FC=4.30), GJB2 (log2FC=4.42), GJB6 (log2FC=3.02)

**Pathway:** GO:0031424 (keratinization), Reactome: Formation of the cornified envelope

**Biological interpretation:** Multiple members of the small proline-rich region (SPRR) and late cornified envelope (LCE) gene families show coordinated upregulation, indicating activation of an alternative epidermal differentiation program. These genes are normally expressed in specific contexts of barrier repair or stress but are pathologically activated in psoriasis. The upregulation of KRT6A (a keratin typically expressed in proliferative or stressed keratinocytes rather than normal differentiation) alongside gap junction proteins (GJB2, GJB6) suggests disruption of normal stratification and cell-cell communication. This program represents the histological hallmarks of psoriatic epidermis: hyperkeratosis, parakeratosis, and altered terminal differentiation.

**Evidence strength:** Strong. Multiple gene family members show consistent directional changes with high effect sizes. Expression evidence confirms these genes are keratinocyte-specific. However, SPRR and LCE genes are clustered in the genome (epidermal differentiation complex on chromosome 1q21), raising the possibility that their co-expression partially reflects coordinated genomic regulation rather than entirely independent pathway activation.

**Limitations:** The transcriptomic signal cannot distinguish whether this altered differentiation program is cell-autonomous (intrinsic keratinocyte defect) or secondary to inflammatory signaling. The absence of classical differentiation markers (e.g., loricrin, involucrin) from this top gene list may indicate these are differently regulated or that the most extreme changes involve stress-induced rather than homeostatic differentiation genes.

### Program 3: Metabolic Reprogramming and Oxidoreductase Activity

**Direction:** Upregulated

**Major supporting genes:** AKR1B10 (log2FC=6.27), AKR1B15 (log2FC=5.23), KYNU (log2FC=4.42), FABP5 (log2FC=3.64), PLA2G4D (log2FC=4.61), PLA2G4E (log2FC=2.47)

**Pathway:** GO:0055114 (oxidation-reduction process), KEGG: Arachidonic acid metabolism, Hallmark: Fatty acid metabolism

**Biological interpretation:** The prominent upregulation of aldo-keto reductase family members (AKR1B10, AKR1B15) alongside kynurenine pathway enzyme KYNU and lipid metabolism genes (FABP5, phospholipase A2 family members) indicates metabolic reprogramming in psoriatic epidermis. AKR1B10 is involved in retinoid metabolism and detoxification of lipid peroxidation products; its upregulation may reflect oxidative stress responses. KYNU catalyzes tryptophan degradation through the kynurenine pathway, which has immunomodulatory functions. FABP5 promotes inflammatory gene expression by delivering retinoic acid to PPARβ/δ rather than RARs. Phospholipase A2 enzymes (PLA2G4D, PLA2G4E) release arachidonic acid for eicosanoid biosynthesis, generating pro-inflammatory lipid mediators.

**Evidence strength:** Moderate. Multiple genes support altered metabolic programs, but their functional relationships are more heterogeneous than in Programs 1 and 2. Disease-association evidence exists for some components (FABP5 is upregulated in psoriasis and promotes inflammation), but the collective significance of this metabolic signature requires further investigation. Some genes may represent responses to inflammation rather than drivers.

**Limitations:** Metabolic changes often reflect tissue composition (proliferating versus differentiated keratinocytes, immune infiltrates) rather than cell-intrinsic reprogramming. Single-cell or spatial transcriptomics would be needed to determine which cell populations drive these signals. The functional consequence of AKR1B family upregulation in psoriasis remains incompletely understood.

### Program 4: Immune Cell Recruitment and T Cell Co-stimulation

**Direction:** Upregulated

**Major supporting genes:** CXCL13 (log2FC=5.89), CXCR2 (log2FC=2.70), CD274/PD-L1 (log2FC=3.44), PRKCQ (log2FC=2.88), IRAK2 (log2FC=2.08), ZC3H12A (log2FC=3.85), TNIP3 (log2FC=7.28)

**Pathway:** GO:0006955 (immune response), Reactome: Chemokine receptors bind chemokines, KEGG: T cell receptor signaling pathway

**Biological interpretation:** The upregulation of CXCL13 (a B cell-attracting chemokine also implicated in tertiary lymphoid structure formation) alongside CXCR2 (neutrophil chemokine receptor) indicates active recruitment of multiple leukocyte populations. CD274 (PD-L1) upregulation in lesional skin represents an immune checkpoint response, likely induced by IFN-γ and attempting to restrain excessive T cell activation. PRKCQ (protein kinase C theta) is critical for T cell receptor signaling and Th17 differentiation. The presence of negative regulators (ZC3H12A/Regnase-1, which destabilizes inflammatory mRNA; TNIP3/TNFAIP3-interacting protein 3, which inhibits NF-κB) indicates concurrent activation of feedback inhibitory mechanisms that are nevertheless insufficient to resolve inflammation.

**Evidence strength:** Moderate to strong. Individual genes have well-established roles in immune regulation, and their collective expression indicates active immune trafficking and T cell activation. However, this program is somewhat heterogeneous, encompassing both pro-inflammatory signals (chemokines, PRKCQ) and counter-regulatory responses (PD-L1, ZC3H12A). Clinical evidence shows that PD-1/PD-L1 blockade can induce or worsen psoriasis, supporting the functional relevance of this pathway.

**Limitations:** The current gene list captures predominantly keratinocyte and myeloid markers rather than lymphocyte-specific genes, suggesting that immune cell transcripts may be diluted in whole-tissue analysis. The functional significance of CXCL13 in psoriasis (a disease not classically associated with B cell pathology or tertiary lymphoid structures) requires clarification. Some of these signals may reflect indirect responses to the primary inflammatory drivers.

### Program 5: Suppression of Homeostatic Growth Factors and Biotransformation

**Direction:** Downregulated (small number of genes)

**Major supporting genes:** BTC (log2FC=-4.30), CYP2W1 (log2FC=-4.70), UGT3A2 (log2FC=-4.59)

**Pathway:** GO:0008152 (metabolic process), KEGG: Drug metabolism - cytochrome P450

**Biological interpretation:** The selective downregulation of BTC (betacellulin, an EGFR ligand), CYP2W1 (a cytochrome P450 enzyme), and UGT3A2 (a UDP-glucuronosyltransferase) represents suppression of homeostatic epithelial programs. BTC normally promotes keratinocyte proliferation and migration during wound healing through EGFR activation; its suppression in lesional skin is paradoxical given the hyperproliferative state and may indicate altered growth factor dependence or feedback inhibition in chronically inflamed epidermis. The downregulation of xenobiotic metabolism enzymes (CYP2W1, UGT3A2) suggests altered capacity for drug metabolism and detoxification in psoriatic skin.

**Evidence strength:** Weak to moderate. The number of prominently downregulated genes is substantially smaller than upregulated genes, and their functional coherence is limited. BTC downregulation is biologically interesting but requires mechanistic investigation. The functional significance of reduced CYP2W1 and UGT3A2 in psoriasis pathogenesis is unclear.

**Limitations:** Downregulated signals in disease-versus-control comparisons may reflect tissue composition (loss of specific cell populations, increased immune infiltration diluting epithelial transcripts) rather than active suppression within individual cells. The relatively modest number of downregulated genes overall suggests psoriasis is predominantly a disease of pathway activation rather than loss of function. Alternative explanations (e.g., BTC downregulation as negative feedback to sustained EGFR activation from other ligands) have not been excluded.

## 3. Key Genes and Interaction Modules

### 1. IL36A (log2FC=11.37, P=2.5×10⁻¹⁰²)

**Statistical direction:** Highly upregulated (third highest fold change, second highest statistical significance)

**Role in biological programs:** Central node in Program 1 (IL-36/innate immunity). IL-36α is a potent keratinocyte-derived alarmin that signals through IL-36 receptor, activating NF-κB and MAPK pathways to amplify inflammatory responses.

**Gene relationships:** IL36A shows pathway co-membership with IL36G and functional antagonism by IL36RN (both present in dataset). IL-36 cytokines induce downstream targets including antimicrobial peptides (S100A7, DEFB4A/B) and chemokines (CXCL8, though not in this top list). This represents a regulatory network rather than direct physical interactions.

**Priority rationale:** IL-36 pathway is genetically validated in pustular psoriasis and represents an emerging therapeutic target. Its extreme statistical signal suggests it is a core disease mechanism.

### 2. S100A7/S100A7A/S100A8/S100A12 Module

**Statistical direction:** All highly upregulated (log2FC range: 7.09-9.83)

**Role in biological programs:** Effectors of Program 1 (innate immunity) and contributors to Program 4 (immune recruitment). S100 proteins function as damage-associated molecular patterns (DAMPs) with antimicrobial activity and chemotactic properties.

**Gene relationships:** These genes show pathway co-membership (all are S100 family calcium-binding proteins) and likely co-expression patterns. S100A8/A9 form calprotectin heterodimers (direct physical interaction), though S100A9 is not in this top list. S100A7 is an IL-17 and IL-22 target gene (regulatory interaction). These proteins signal through receptors including RAGE and TLR4, connecting to downstream inflammatory cascades (indirect pathway relationship).

**Priority rationale:** S100 proteins are abundant in psoriatic scales, detectable in serum, and correlate with disease severity, making them potential biomarkers. Their dual roles as antimicrobial effectors and inflammatory amplifiers position them at the keratinocyte-immune interface.

### 3. DEFB4A/DEFB4B/DEFB103A/DEFB103B

**Statistical direction:** Extremely upregulated (log2FC >5.7 for all, >11 for DEFB4 genes)

**Role in biological programs:** Effectors of Program 1 (innate immunity). Beta-defensins are antimicrobial peptides that also have chemotactic activity for immune cells and can activate dendritic cells.

**Gene relationships:** These genes show genomic clustering (located in the beta-defensin cluster on chromosome 8p23.1) and pathway co-membership. DEFB4A and DEFB4B are highly similar paralogs; DEFB103A and DEFB103B represent another paralogous pair. Their co-expression partially reflects coordinated genomic regulation. Functionally, they are induced by IL-17 and IL-22 (regulatory interaction).

**Priority rationale:** Beta-defensins link innate immunity to adaptive immunity by recruiting and activating T cells. Their extreme upregulation may contribute to autoantigen presentation (LL-37/cathelicidin-DNA complexes activate plasmacytoid dendritic cells in psoriasis; beta-defensins may have analogous roles).

### 4. SPRR2 Family Module (SPRR2A/B/D/E/F/G)

**Statistical direction:** All upregulated (log2FC range: 3.99-7.32)

**Role in biological programs:** Central to Program 2 (aberrant differentiation). SPRR proteins are crosslinked into the cornified envelope during terminal keratinocyte differentiation.

**Gene relationships:** Genomic clustering (epidermal differentiation complex, chromosome 1q21.3) and pathway co-membership. These genes likely share transcriptional regulation through common enhancers. They are induced by IL-17, IL-22, and other inflammatory mediators (regulatory interaction).

**Priority rationale:** SPRR upregulation represents the altered differentiation phenotype visible histologically. However, as clustered genes with overlapping functions, they may represent a single biological signal rather than multiple independent mechanisms. Their prominence in this dataset requires distinguishing whether they are drivers of pathology or secondary markers of inflammation.

### 5. KYNU (log2FC=4.42, P=7.2×10⁻⁹⁵)

**Statistical direction:** Upregulated

**Role in biological programs:** Component of Program 3 (metabolic reprogramming). KYNU (kynureninase) catalyzes steps in tryptophan degradation via the kynurenine pathway.

**Gene relationships:** Pathway co-membership with other kynurenine pathway enzymes (IDO1, though not in this list, is upregulated in psoriasis). Kynurenine metabolites can activate aryl hydrocarbon receptor (AhR), which regulates keratinocyte differentiation and immune responses (indirect regulatory relationship). KYNU activity affects NAD+ biosynthesis and can modulate inflammatory responses.

**Priority rationale:** Kynurenine pathway has emerged as an immunometabolic checkpoint in multiple inflammatory diseases. Its upregulation may represent an immunosuppressive response (kynurenines are generally anti-inflammatory) that is insufficient or dysregulated in psoriasis. This deserves investigation as metabolic pathways are increasingly recognized as therapeutic targets.

### 6. CD274/PD-L1 (log2FC=3.44, P=7.7×10⁻⁶⁶)

**Statistical direction:** Upregulated

**Role in biological programs:** Component of Program 4 (immune regulation). PD-L1 is an immune checkpoint ligand that inhibits T cell activation through PD-1 binding.

**Gene relationships:** PD-L1 physically interacts with PD-1 on T cells (direct protein interaction). It is transcriptionally induced by interferons, particularly IFN-γ (regulatory interaction), indicating active T cell responses in lesional skin. PD-L1 expression represents a counter-regulatory mechanism attempting to restrain T cell activation.

**Priority rationale:** Clinical evidence strongly supports functional relevance—immune checkpoint inhibitors (anti-PD-1/PD-L1 antibodies used in oncology) frequently induce or exacerbate psoriasis, demonstrating that PD-1/PD-L1 signaling normally restrains psoriatic inflammation. This has therapeutic implications (checkpoint inhibitors are contraindicated) and mechanistic significance (suggests T cell activation is incompletely controlled despite checkpoint upregulation).

### 7. WNT5A (log2FC=2.53, P=2.8×10⁻⁷⁰)

**Statistical direction:** Upregulated

**Role in biological programs:** Potential contributor to Programs 2 (differentiation) and 4 (immune activation). WNT5A is a non-canonical Wnt ligand that regulates keratinocyte differentiation, migration, and inflammatory signaling.

**Gene relationships:** WNT5A signals through non-canonical Wnt pathways (pathway co-membership), activating planar cell polarity and Ca²⁺ signaling rather than β-catenin. It can promote inflammatory cytokine production and has been shown to enhance IL-12 and IL-23 production by dendritic cells (indirect regulatory relationship). In keratinocytes, WNT5A influences differentiation programs.

**Priority rationale:** WNT5A represents a less-studied pathway in psoriasis compared to IL-23/IL-17 but has emerging evidence for involvement in inflammatory skin diseases. Its dual roles in epithelial biology and immune regulation make it an interesting candidate for mechanistic investigation.

### 8. FABP5 (log2FC=3.64, P=2.4×10⁻⁸⁴)

**Statistical direction:** Upregulated

**Role in biological programs:** Key mediator in Program 3 (metabolic reprogramming). FABP5 is a fatty acid binding protein that transports retinoic acid and delivers it to PPARβ/δ rather than retinoic acid receptors.

**Gene relationships:** FABP5 has pathway co-membership with other lipid metabolism genes. Functionally, it creates a metabolic switch: when FABP5 is upregulated relative to CRABP2 (cellular retinoic acid binding protein 2), retinoic acid preferentially activates PPARβ/δ (pro-inflammatory) rather than RARs (anti-inflammatory). This represents a regulatory interaction affecting nuclear receptor signaling.

**Priority rationale:** FABP5 provides a mechanistic link between metabolic changes and inflammatory gene expression. Its upregulation may explain altered retinoid responsiveness in psoriasis and represents a potential therapeutic target. Small molecules inhibiting FABP5 have shown preclinical efficacy in inflammatory skin models.

### 9. CXCL13 (log2FC=5.89, P=2.5×10⁻⁷⁰)

**Statistical direction:** Upregulated

**Role in biological programs:** Component of Program 4 (immune recruitment). CXCL13 is a chemokine that attracts B cells and certain T cell subsets through CXCR5 receptor.

**Gene relationships:** Pathway co-membership with other chemokines. CXCL13 is characteristically associated with tertiary lymphoid structure formation and germinal center reactions (pathway/functional relationship). Its cellular source in psoriatic skin requires clarification (could be keratinocytes, dendritic cells, or other cell types).

**Priority rationale:** CXCL13 upregulation is unexpected in psoriasis, which is primarily considered a T cell-mediated disease without prominent B cell involvement. This finding suggests either: (1) underappreciated B cell/plasma cell contributions to psoriasis pathogenesis, (2) formation of ectopic lymphoid structures in chronic lesions, or (3) CXCL13 functions beyond B cell recruitment in this context. This represents an exploratory hypothesis requiring validation.

### 10. BTC (log2FC=-4.30, P=2.4×10⁻⁷⁶)

**Statistical direction:** Downregulated (notable as one of few strongly downregulated genes)

**Role in biological programs:** Represents suppression in Program 5 (loss of homeostatic growth factors). Betacellulin is an EGFR ligand that promotes keratinocyte proliferation and wound healing.

**Gene relationships:** BTC is pathway co-member with other EGF family ligands (EGF, AREG, EREG) that signal through EGFR/ERBB receptors. Its downregulation occurs in the context of keratinocyte hyperproliferation, suggesting compensatory changes or altered growth factor dependence.

**Priority rationale:** BTC downregulation represents a biological paradox that may provide mechanistic insights. Possibilities include: (1) negative feedback regulation in response to sustained EGFR activation by other ligands, (2) epigenetic silencing in inflammatory context, (3) altered growth factor requirements in psoriatic keratinocytes. Investigating this may reveal why psoriatic epidermis maintains hyperproliferation despite losing specific growth factor signals.

## 4. Validation Priorities

### Priority 1: IL-36/Antimicrobial Peptide Amplification Loop (Mechanistic Hypothesis)

**Rationale for prioritization:** IL36A shows the strongest statistical signal among cytokines, and multiple IL-36-induced genes (S100 proteins, defensins) are coordinately upregulated. This suggests a positive feedback loop where IL-36 induces antimicrobial peptides, which may further activate keratinocytes and immune cells.

**Evidence from current dataset:** IL36A, IL36G, IL36RN, S100A7/A7A/A8/A12, DEFB4A/B, DEFB103A/B all show extreme upregulation (log2FC >5 for most, P <10⁻⁶⁰).

**External evidence:** 
- Genetic evidence: IL36RN loss-of-function mutations cause generalized pustular psoriasis (established evidence)
- Therapeutic evidence: Anti-IL-36 receptor antibody (spesolimab) is FDA-approved for pustular psoriasis (established evidence)
- Mechanistic evidence: IL-36 cytokines induce antimicrobial peptides in keratinocyte cultures; S100A7 and β-defensins can activate dendritic cells and promote IL-23 production, creating potential positive feedback (supported hypothesis)

**Next validation step:** 
- Ex vivo: Culture psoriatic skin explants with IL-36 receptor antagonist and measure downstream antimicrobial peptide expression by qPCR/immunostaining
- In vivo: Analyze transcriptomic changes in psoriasis patients treated with IL-23, IL-17, or TNF inhibitors to determine if IL-36 pathway suppression correlates with clinical response
- Mechanistic: Test whether blocking S100 proteins or defensins reduces IL-36-induced inflammation in keratinocyte-immune cell co-cultures

**Conclusion status:** Supported hypothesis for plaque psoriasis; established evidence for pustular psoriasis subtype.

### Priority 2: CXCL13 and Tertiary Lymphoid Structure Formation (Exploratory Hypothesis)

**Rationale for prioritization:** CXCL13 upregulation (log2FC=5.89, P=2.5×10⁻⁷⁰) is unexpected in psoriasis and may indicate underappreciated immune organization. If tertiary lymphoid structures are present in chronic lesions, this would suggest tissue-resident memory mechanisms maintaining disease.

**Evidence from current dataset:** CXCL13 is highly upregulated as a single chemokine signal in this list. Other B cell markers are not prominently represented, but whole-tissue transcriptomics may dilute B cell signals if they are spatially localized.

**External evidence:**
- Expression evidence: Some studies have reported CXCL13 expression in psoriatic skin, but its functional role is unclear (exploratory hypothesis)
- Disease-association evidence: CXCL13 is elevated in serum of some psoriasis patients, but this is not a consistent finding (conflicting evidence)
- Mechanism: Tertiary lymphoid structures have been described in other chronic inflammatory skin diseases but are not classically associated with psoriasis (insufficient evidence in psoriasis specifically)

**Next validation step:**
- Histology: Perform immunohistochemistry for CXCL13, CD20 (B cells), CD3 (T cells), and PNAd (high endothelial venules) on psoriatic skin sections to assess whether organized lymphoid aggregates are present
