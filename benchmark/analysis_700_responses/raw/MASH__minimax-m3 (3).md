# metabolic dysfunction-associated steatohepatitis (MASH) - minimax-m3

- Benchmark system: raw
- Repeat: 5
- Task type: DISEASE-STATE
- Tissue / sample source: liver tissue
- Comparison or endpoint: MASH/NASH versus healthy control
- Answer input cohort: Discovery/Core only
- Selected items: 100
- Input fields: gene name, effect size (log2FC/HR), P value, FDR
- E2seq Agent RAG: disabled
- Conversation memory: disabled
- Thinking mode: disabled
- Held-out validation data in prompt/RAG: no
- Model API: MiniMax / minimax-m3
- Message SHA-256: f634f84e95c290ce4195eb13604b114b4c86ce8adb76238e59c436c955ac43b9
- Response HTTP status: 200
- Prompt tokens: 4075
- Completion tokens: 7868
- Reasoning tokens: 
- Total tokens: 11943
- API requests reported: 
- Elapsed seconds: 108.874
- Final benchmark system: raw; file rank 3/5; original repeat 5; model vendor: MiniMax

---
<think>Let me analyze this transcriptomic dataset for MASH (metabolic dysfunction-associated steatohepatitis) vs healthy control in liver tissue. I need to carefully evaluate the genes provided and interpret them in biological context.

First, let me categorize the genes by direction:

**UPREGULATED genes (log2FC > 0):**
- UQCRBP1 (3.73) - UQCRB pseudogene 1, related to mitochondrial complex III
- SNORD140 (3.06) - small nucleolar RNA
- LOC105377700 (3.93) - unknown
- MIR4647 (2.53) - microRNA
- UBD (4.15) - Ubiquitin D, FAT10, involved in immune response
- DTNA (3.72) - Dystrobrevin alpha
- TP53I3 (3.26) - p53 inducible gene 3, oxidative stress
- LOC107984754 (3.64) - unknown
- CIMIP2A (2.48) - unknown
- DYNLT1 (1.52) - Dynein light chain
- AJUBA (1.92) - LIM domain protein
- MIR12136 (3.18) - microRNA
- TMEM154 (3.71) - transmembrane protein
- TREM2 (4.91) - Triggering receptor on myeloid cells 2 - well-known MASH marker
- TRNK (2.73) - mitochondrial tRNA for lysine
- MRPL1-AS1 (2.77) - antisense RNA
- EME1 (1.88) - essential meiotic structure
- CYCS (1.56) - Cytochrome c, somatic - apoptosis/electron transport
- TRNS1 (3.05) - tRNA
- DUSP8 (3.49) - Dual specificity phosphatase 8
- TSC22D1 (1.45) - TGF-beta stimulated
- GGTLC1 (2.33) - Gamma-glutamyltransferase
- MIR4426 (2.24) - microRNA
- MIR1244-1 (1.39) - microRNA
- KCNJ5 (2.69) - potassium channel
- FABP5 (2.85) - Fatty acid binding protein 5
- TRNC (4.07) - mitochondrial tRNA
- CAST (4.02) - Calpastatin
- LINC01485 (2.11) - lincRNA
- PFDN6 (1.49) - Prefoldin subunit
- CXCL10 (3.46) - C-X-C motif chemokine ligand 10 - inflammation
- TNFRSF12A (3.27) - TWEAK receptor, Fn14
- LOC105371873 (3.82) - unknown
- MIR1825 (1.83) - microRNA
- MIR4721 (1.74) - microRNA
- TIMM17A (1.28) - mitochondrial import
- MTHFD1L (1.72) - mitochondrial folate enzyme
- RPL9 (1.47) - ribosomal protein
- RPSA2 (1.22) - ribosomal protein SA2
- CES1P2 (1.77) - carboxylesterase pseudogene
- TRNL2 (3.86) - mitochondrial tRNA
- CAPG (2.57) - Macrophage capping protein
- S100A14 (1.78) - S100 calcium binding protein
- GUSBP2 (2.63) - glucuronidase pseudogene
- TRNY (3.57) - mitochondrial tRNA
- FOXM1 (2.14) - Forkhead box M1
- MACROH2A2 (1.63) - histone variant
- LSMEM2 (1.30) - unknown
- HS3ST2 (3.72) - Heparan sulfate glucosamine 3-O-sulfotransferase 2
- MTRNR2L8 (3.25) - mitochondrial pseudogene
- MANF (1.85) - Mesencephalic astrocyte-derived neurotrophic factor

**DOWNREGULATED genes (log2FC < 0):**
- CD81-AS1 (-2.96) - antisense RNA
- MS4A6E (-3.52) - Macrophage marker
- MARCO (-2.84) - Macrophage receptor with collagenous structure
- VCAM1 (-2.38) - Vascular cell adhesion molecule 1
- GLUD1P2 (-1.94) - glutamate dehydrogenase pseudogene
- CR1 (-3.61) - Complement receptor 1
- FGFRL1 (-1.49) - FGF receptor-like 1
- CD163 (-2.52) - macrophage scavenger receptor - important MASH marker
- LYVE1 (-2.73) - lymphatic vessel endothelial hyaluronan receptor 1
- P4HA1 (-3.19) - Prolyl 4-hydroxylase subunit alpha 1
- P2RY13 (-2.10) - Purinergic receptor
- SPIC (-2.62) - transcription factor in macrophages
- LOC107986183 (-3.64) - unknown
- PCDH20 (-4.59) - Protocadherin 20
- TIMD4 (-4.28) - T-cell immunoglobulin and mucin domain containing 4 - Kupffer cell marker
- ETV5 (-1.93) - ETS transcription factor
- MRC1 (-2.10) - Mannose receptor C type 1 - macrophage marker
- CDH23 (-1.90) - Cadherin 23
- CFP (-1.86) - Complement factor properdin
- CETP (-2.49) - Cholesteryl ester transfer protein
- NUCB1-AS1 (-1.86) - antisense RNA
- MIR6717 (-2.24) - microRNA
- TINAGL1 (-1.78) - Tubulointerstitial nephritis antigen-like 1
- FNBP1 (-1.12) - Formin binding protein 1
- MAST1 (-2.73) - Microtubule associated serine/threonine kinase 1
- CD5L (-2.90) - CD5 molecule like - macrophage marker
- MPEG1 (-1.74) - Macrophage expressed 1
- SIGLEC1 (-2.12) - Sialic acid binding Ig like lectin 1
- MROH2B-DT (-1.73) - divergent transcript
- NDST3 (-2.67) - N-Deacetylase and N-Sulfotransferase 3
- SIGLEC11 (-2.12) - Sialic acid binding Ig like lectin 11
- CBS (-1.25) - Cystathionine beta-synthase
- TCF7L1 (-1.53) - Transcription factor 7 like 1
- CD209 (-2.43) - DC-SIGN, macrophage marker
- PDE2A (-1.63) - Phosphodiesterase 2A
- HCFC1 (-1.25) - Host cell factor C1
- LDB2 (-1.53) - LIM domain binding 2
- CSF1R (-1.98) - Colony stimulating factor 1 receptor - macrophage marker
- FOLR2 (-2.04) - Folate receptor beta - macrophage marker
- SEC14L1 (-1.36) - SEC14 like lipid binding 1
- LOC102724560 (-1.27) - unknown
- RASL10B (-2.57) - RAS like family 10 member B
- SCLY (-1.28) - Selenocysteine lyase
- LOC107986158 (-1.74) - unknown
- CDH5 (-1.38) - Cadherin 5, VE-cadherin
- HSPA9-AS1 (-1.82) - antisense RNA
- CNPY3-GNMT (-1.76) - readthrough
- PLXNB2 (-1.18) - Plexin B2

Let me identify the major biological themes:

**1. Macrophage/Kupffer cell biology:**
The downregulated genes are dominated by macrophage markers:
- MARCO - macrophage receptor
- CD163 - macrophage scavenger receptor
- CD5L - macrophage
- MRC1 (CD206) - M2 macrophage marker
- TIMD4 - Kupffer cell marker
- FOLR2 - macrophage
- CSF1R - macrophage development/survival
- CD209 - DC-SIGN
- MS4A6E - macrophage
- SPIC - macrophage transcription factor
- MPEG1 - macrophage
- SIGLEC1 - macrophage
- P2RY13 - macrophage
- LYVE1 - macrophage/lymphatic
- CFP - complement
- CR1 - complement receptor on macrophages
- SIGLEC11 - macrophage

**2. Inflammation/Immune signaling:**
- CXCL10 (UP) - pro-inflammatory chemokine
- TREM2 (UP) - well-known disease-associated macrophage marker in MASH
- TNFRSF12A (UP, Fn14) - TWEAK receptor, pro-inflammatory/fibrosis
- UBD (UP, FAT10) - immunoproteasome/immune regulation
- DUSP8 (UP) - stress response
- TP53I3 (UP) - oxidative stress response

**3. Mitochondrial function:**
- UQCRBP1 (UP) - complex III
- CYCS (UP) - cytochrome c
- TRNK, TRNC, TRNL2, TRNY (UP) - mitochondrial tRNAs
- TIMM17A (UP) - mitochondrial import
- MTHFD1L (UP) - mitochondrial folate metabolism

**4. Fatty acid/lipid metabolism:**
- FABP5 (UP) - fatty acid binding
- CBS (DOWN) - cystathionine beta-synthase, hydrogen sulfide pathway
- CETP (DOWN) - lipid transfer

**5. Cell adhesion/ECM:**
- VCAM1 (DOWN)
- CDH5 (DOWN)
- PLXNB2 (DOWN)
- P4HA1 (DOWN) - collagen biosynthesis
- PCDH20 (DOWN)
- TINAGL1 (DOWN)

**6. Transcription regulation:**
- TCF7L1 (DOWN)
- ETV5 (DOWN)
- SPIC (DOWN)
- FOXM1 (UP)
- AJUBA (UP)

This is a striking pattern - many macrophage markers are DOWN, while TREM2 is strongly UP. This suggests a shift in the macrophage compartment. TREM2 is a marker of "lipid-associated macrophages" (LAMs) or disease-associated macrophages (DAMs) that emerge in MASH and replace or coexist with resident Kupffer cells (which express MARCO, TIMD4, CD163, etc.). So the data likely reflects:
- Loss of homeostatic Kupffer cells (MARCO, TIMD4, CD163, CD5L, MRC1, FOLR2, CSF1R down)
- Emergence of TREM2+ lipid-associated macrophages (TREM2 up)
- Inflammatory signaling (CXCL10, TNFRSF12A, UBD up)

This is actually the well-described phenomenon in MASH where resident Kupffer cells are depleted and TREM2+ macrophages (MoMFs - monocyte-derived macrophages) become dominant. This is a key feature of MASH progression.

Let me also think about:
- VCAM1 down: This is interesting because VCAM1 is typically associated with endothelial activation/inflammation in liver disease. However, in advanced fibrosis it may be expressed in different cell types.
- P4HA1 down: prolyl hydroxylase, collagen maturation - could reflect altered ECM
- HS3ST2 up: heparan sulfate modification
- CAST up: calpain inhibitor

Let me also look at the mitochondrial signals:
- The mitochondrial tRNAs being up, UQCRBP1 up, CYCS up, MTHFD1L up - these could reflect mitochondrial biogenesis or compensatory responses
- DUSP8 up - stress response

Let me now structure my response carefully:

**Core biological programs:**
1. Kupffer cell depletion / macrophage compartment remodeling (with TREM2+ LAM expansion)
2. Pro-inflammatory chemokine/cytokine signaling
3. Mitochondrial/oxidative stress response
4. ECM and adhesion remodeling
5. Metabolic/hydrogen sulfide dysregulation

**Key genes/modules:**
1. TREM2 (UP, log2FC 4.91) - most striking macrophage signal
2. CXCL10 (UP, log2FC 3.46) - inflammatory chemokine
3. TNFRSF12A/Fn14 (UP, log2FC 3.27) - pro-inflammatory/fibrosis
4. UBD/FAT10 (UP, log2FC 4.15) - immunoproteasome
5. MARCO (DOWN, log2FC -2.84) - Kupffer cell
6. TIMD4 (DOWN, log2FC -4.28) - Kupffer cell
7. CD163 (DOWN, log2FC -2.52) - macrophage
8. CD5L (DOWN, log2FC -2.90) - macrophage
9. CSF1R (DOWN, log2FC -1.98) - macrophage survival
10. Mitochondrial complex/CYCS (UP, log2FC 1.56)

**Validation priorities:**
1. Spatial/single-cell validation of TREM2+ macrophage vs Kupffer cell dynamics
2. CXCL10/CXCR3 axis as biomarker or therapeutic target
3. Fn14/TWEAK signaling in MASH progression
4. Mitochondrial dysfunction program
5. Composition check - confirm cell-type contributions

**Limitations:**
1. Bulk tissue - cell composition changes (macrophage shifts) confound direct interpretation
2. No clear information on disease stage (early vs advanced MASH)
3. Sex/age effects not captured
4. Many pseudogenes and lncRNAs of uncertain function
5. Direction of VCAM1 change is somewhat atypical (usually up in MASH)

Let me now write a comprehensive interpretation.

Actually, I want to double-check some things:
- The downregulated genes strongly suggest loss of resident Kupffer cells: MARCO, TIMD4, CD163, CD5L, MRC1, FOLR2, CSF1R, LYVE1, SPIC, MPEG1, CD209, P2RY13 - these are all well-known Kupffer cell/macrophage markers
- TREM2 upregulation is the hallmark of monocyte-derived lipid-associated macrophages in MASH
- This pattern has been described in multiple single-cell studies of human and mouse MASH

For VCAM1 - it's typically considered a pro-inflammatory endothelial marker that increases in MASH, so seeing it down here is unusual. But VCAM1 can be expressed on hepatocytes in chronic injury and on sinusoidal endothelial cells in different patterns. This might represent a specific disease stage.

For P4HA1 - it's involved in collagen synthesis, so downregulation might seem counterintuitive in fibrosis. But it could reflect specific cellular context.

Let me think about MTHFD1L - it's mitochondrial monofunctional C1-tetrahydrofolate synthase. Has been implicated in liver disease.

The mitochondrial tRNAs being upregulated is interesting - they could reflect mitochondrial stress or biogenesis responses.

Let me finalize my interpretation now.

I should note that many "core programs" can be unified by the macrophage remodeling theme - this is really the dominant signal. Let me structure programs to be distinct:

Program 1: Macrophage compartment remodeling (Kupffer cell loss + TREM2+ LAM expansion)
Program 2: Pro-inflammatory signaling (CXCL10, TNFRSF12A, UBD)
Program 3: Mitochondrial stress response
Program 4: ECM and adhesion remodeling
Program 5: Metabolic dysregulation (CBS, CETP, FABP5, hydrogen sulfide, lipid handling)

These are reasonably distinct.

Let me write the final response now. I'll be careful to:
- Not over-interpret pseudogenes and lncRNAs
- Clearly distinguish direct vs indirect evidence
- Note cell composition concerns
- Be explicit about limitations

Let me also think about HS3ST2 - this is a heparan sulfate sulfotransferase. Has been implicated in inflammation and fibrosis. The upregulation is interesting.

For DYNLT1 - dynein light chain - involved in microtubule-based transport, ciliary function
For FNBP1 - formin binding protein - endocytosis, membrane dynamics
For SEC14L1 - lipid binding, lipid metabolism

Let me now write the comprehensive interpretation.</think>

# Transcriptomic Interpretation: MASH vs Healthy Control Liver

## 1. Overall Biological Interpretation

The transcriptomic signature is dominated by a **coordinated remodeling of the hepatic macrophage compartment**, in which the loss of resident Kupffer cell identity (MARCO, TIMD4, CD163, CD5L, MRC1, FOLR2, CSF1R, SPIC, LYVE1, MPEG1, CD209 all strongly downregulated) coincides with the emergence of a **TREM2-high monocyte-derived, lipid-associated macrophage (LAM/MoMF) signature** (TREM2 log₂FC ≈ +4.9). This is reinforced by a pro-inflammatory chemokine/cytokine program (CXCL10, TNFRSF12A/Fn14, UBD/FAT10) and a secondary mitochondrial/oxidative stress response (CYCS, UQCRBP1, multiple mitochondrial tRNAs, MTHFD1L, MANF, TP53I3, DUSP8). Together these features describe the transition from a quiescent Kupffer-cell-dominated liver to a **TREM2⁺ macrophage-dominated, inflamed, metabolically stressed MASH liver**, a pattern repeatedly observed in human and murine MASH single-cell datasets. Additional signals indicate altered extracellular matrix/adhesion biology (VCAM1, P4HA1, CDH5, PLXNB2, PCDH20) and metabolic dysregulation (CBS, CETP, FABP5), which are consistent with MASH but largely secondary to the dominant immune–macrophage axis.

---

## 2. Core Biological Programs

### Program 1 — Macrophage compartment remodeling (loss of homeostatic Kupffer cells + expansion of TREM2⁺ lipid-associated macrophages)
- **Direction:** bidirectional at the gene level, but with a clear net shift toward a disease-associated myeloid state
- **Key supporting genes (DOWN, Kupffer cell/resident macrophage):** MARCO, TIMD4, CD163, CD5L, MRC1 (CD206), FOLR2, CSF1R, SPIC, LYVE1, MPEG1, CD209, P2RY13, MS4A6E, CFP, CR1, SIGLEC1, SIGLEC11
- **Key supporting genes (UP, monocyte-derived/LAM):** TREM2, CAPG, FABP5
- **Pathway/ontology:** GO "macrophage activation" / "regulation of macrophage differentiation" / Hallmark "Inflammatory Response"; consistent with the KCs→MoMFs transition described in scRNA-seq of NASH (Ramachandran, JCI 2019; Da Silva, Nat Commun 2021; Xiong, Cell Metab 2023)
- **Interpretation rationale:** The simultaneous loss of *bona fide* Kupffer cell markers (Clec4F-independent but MARCO⁺/TIMD4⁺/CD163⁺) and gain of TREM2 is the molecular fingerprint of MoMF/LAM infiltration and replacement. The coordinated downregulation of macrophage lineage survival factors (CSF1R, SPIC) further indicates that the resident population is not merely being transcriptionally modulated, but depleted.
- **Evidence strength:** **Strong.** Many independent macrophage markers move in the same direction, and the TREM2⁺ LAM phenotype is well established in MASH.
- **Major limitations:** In bulk tissue, "downregulation" of Kupffer markers can reflect either (a) loss of cell numbers, (b) transcript suppression within existing cells, or (c) proportional dilution by non-myeloid cells. Bulk data cannot distinguish these; single-cell or spatial validation is required.

### Program 2 — Pro-inflammatory cytokine/chemokine signaling
- **Direction:** Upregulated
- **Key supporting genes:** CXCL10, TNFRSF12A (Fn14), UBD (FAT10), TP53I3, DUSP8, AJUBA
- **Pathway/ontology:** Hallmark "Interferon Gamma Response," "TNFA Signaling via NF-κB," Reactome "Chemokine receptors bind chemokines"
- **Interpretation rationale:** CXCL10 (a CXCR3 ligand) and Fn14 (TWEAK receptor) are established drivers of hepatic inflammation and fibrogenic cross-talk with stellate cells. UBD/FAT10 is induced by IFN-γ/TNF-α and feeds the immunoproteasome. The coherence of three orthogonal inflammatory mediators (chemokine, TNFRSF member, IFN/stress-induced ubiquitin modifier) indicates a genuine inflammatory program rather than a single-gene anomaly.
- **Evidence strength:** **Moderate to strong.** Each gene individually has strong literature support; the bulk coherence adds confidence. However, the size of the inflammatory gene set in this list is modest, suggesting either early-stage disease or a curated/transcriptomic subset.
- **Major limitations:** Inflammatory gene expression is highly sensitive to disease stage, sampling site, and prior meal/treatment. Without clinical metadata, the inflammatory signature cannot be confidently attributed to disease severity.

### Program 3 — Mitochondrial and oxidative-stress response
- **Direction:** Upregulated
- **Key supporting genes:** CYCS (cytochrome c), UQCRBP1 (complex III pseudogene/region), TRNK/TRNC/TRNL2/TRNY (mitochondrial tRNAs), TIMM17A, MTHFD1L, MANF, TP53I3, DUSP8
- **Pathway/ontology:** Reactome "Respiratory electron transport," GO "mitochondrial translational elongation," GO "response to oxidative stress"
- **Interpretation rationale:** CYCS release and mitochondrial tRNA accumulation are associated with oxidative stress and mitochondrial stress signaling in steatohepatitis. MANF and DUSP8 are unfolded-protein-response / stress-kinase effectors. MTHFD1L upregulation has been associated with one-carbon and redox dysregulation in NAFLD.
- **Evidence strength:** **Moderate.** Directionally coherent, but several entries are mitochondrial tRNAs and a pseudogene (UQCRBP1) whose quantitative interpretation is uncertain.
- **Major limitations:** Pseudogenes (UQCRBP1, CES1P2, GGTLC1, GUSBP2, GLUD1P2, RPSA2) often show technical noise in RNA-seq; their inclusion should not be over-interpreted. Functional interpretation of mitochondrial tRNA accumulation in bulk tissue is also ambiguous.

### Program 4 — Extracellular matrix, adhesion, and vascular remodeling
- **Direction:** Mixed (some adhesion molecules downregulated, but supportive of overall ECM remodeling)
- **Key supporting genes:** VCAM1 (DOWN), CDH5/VE-cadherin (DOWN), P4HA1 (DOWN), PLXNB2 (DOWN), PCDH20 (DOWN), TINAGL1 (DOWN); HS3ST2 (UP)
- **Pathway/ontology:** GO "cell–cell adhesion," GO "extracellular matrix organization," Reactome "collagen biosynthesis"
- **Interpretation rationale:** Reduced endothelial/mesenchymal adhesion transcripts (VCAM1, CDH5, PLXNB2, PCDH20) and reduced prolyl hydroxylase (P4HA1) suggest altered sinusoidal endothelial and fibroblastic states. P4HA1 loss is somewhat paradoxical in fibrotic MASH and may reflect a non-fibrotic MASH stage or compensatory/post-translational pathway shifts. HS3ST2 upregulation is associated with heparan sulfate remodeling in inflammation/fibrosis.
- **Evidence strength:** **Weak to moderate.** Fewer coherent gene counts; mixed direction; some findings (e.g., VCAM1 down) are atypical in classical MASH.
- **Major limitations:** This program is heterogeneous and likely reflects partial sampling of ECM changes. P4HA1 downregulation in a fibrotic context requires independent confirmation.

### Program 5 — Metabolic dysregulation (lipid handling and transsulfuration)
- **Direction:** Mixed
- **Key supporting genes:** FABP5 (UP), CETP (DOWN), CBS (DOWN), SEC14L1 (DOWN), HS3ST2 (UP)
- **Pathway/ontology:** GO "lipid transport," KEGG "taurine/hypotaurine metabolism" (CBS), "PPAR signaling" (FABP5)
- **Interpretation rationale:** FABP5 upregulation is consistent with increased fatty-acid trafficking in injured hepatocytes and macrophages. CBS downregulation may compromise transsulfuration/H₂S generation, which is implicated in NAFLD progression. CETP downregulation may reflect altered HDL remodeling in MASH.
- **Evidence strength:** **Weak.** Few coherent metabolic genes; CBS and CETP findings are based on single hits.
- **Major limitations:** A canonical MASLD/MASH signature includes classic lipid-handling genes (PPARA, CPT1A, ACOX1, FASN) that are not represented in the top DEGs here. This likely reflects either (a) early disease where classical lipogenic genes have not yet been maximally perturbed, or (b) curated/filtered reporting. The metabolic program should be considered exploratory.

---

## 3. Key Genes and Interaction Modules

| Rank | Gene | Direction / log₂FC | Role | Interaction type |
|------|------|-------------------|------|------------------|
| 1 | **TREM2** | UP, +4.91 | Defines TREM2⁺ lipid-associated macrophages; suppresses TLR signaling, promotes lipid handling | **Pathway co-membership** with TYROBP/DAP12 signaling; **co-expression** with lipid-handling genes in scRNA-seq (published literature); not direct physical binding to MARCO/CD163 |
| 2 | **CXCL10** | UP, +3.46 | CXCR3 chemokine; recruits T/NK cells; biomarker candidate | **Regulatory interaction** (ligand–receptor with CXCR3); co-expressed with IFN-stimulated genes |
| 3 | **TNFRSF12A (Fn14)** | UP, +3.27 | TWEAK receptor; drives hepatocyte apoptosis and stellate-cell activation | **Direct physical interaction** with TWEAK (TNFSF12); **pathway co-membership** with NF-κB |
| 4 | **UBD (FAT10)** | UP, +4.15 | Ubiquitin-like modifier; targets proteasomal substrates; IFN/TNF-induced | **Regulatory interaction** with NEDD8/ubiquitin machinery; **co-expression** with ISGs |
| 5 | **MARCO** | DOWN, −2.84 | Scavenger receptor; identity marker of homeostatic Kupffer cells | **Co-expression** with TIMD4, CD163; no direct physical interaction demonstrated with TREM2 |
| 6 | **TIMD4** | DOWN, −4.28 | Phosphatidylserine receptor; Kupffer cell identity | **Co-expression** with MARCO, CLEC4F (not in list); not physically bound to TREM2 |
| 7 | **CD163 + CD5L + MRC1** | DOWN, −2.5 to −2.9 | Heme scavenger, M2-like macrophage markers | **Pathway co-membership** (heme/iron handling); **co-expression** in resident Kupffer cells |
| 8 | **CSF1R + SPIC + FOLR2** | DOWN, −1.98 / −2.62 / −2.04 | Macrophage lineage survival, transcription factor, folate receptor | **Regulatory interaction** (CSF1 → CSF1R → SPIC); **co-expression** in Kupffer cells |
| 9 | **CYCS + UQCRBP1 + mitochondrial tRNAs** | UP | Mitochondrial electron transport and translation | **Pathway co-membership** (oxidative phosphorylation); release of CYCS into cytosol is a **regulatory** event in apoptosis initiation |
| 10 | **VCAM1 + CDH5 + PLXNB2** | DOWN, −2.4 / −1.4 / −1.2 | Endothelial adhesion molecules | **Pathway co-membership** (cell adhesion); their simultaneous downregulation suggests sinusoidal endothelial dysfunction rather than independent events |

**Important:** None of the above "interactions" are direct physical protein–protein interactions unless explicitly stated (Fn14↔TWEAK). Most relationships are co-expression, pathway co-membership, or ligand–receptor regulatory pairs, and the macrophage compartment shifts are inferred from independent gene-pattern convergence, not from a direct TREM2–MARCO binding.

---

## 4. Validation Priorities

### Priority 1 — Spatial and single-cell validation of macrophage compartment remodeling
- **Classification:** Interaction / network hypothesis + composition check
- **Why prioritize:** The dominant signal in the dataset is the apparent KC → TREM2⁺ MoMF transition. Bulk tissue cannot distinguish true loss of Kupffer cells from transcriptional downregulation; interpretation depends critically on the answer.
- **Evidence from current dataset:** 14+ macrophage markers down, TREM2 strongly up.
- **External evidence:** Strong published support in human and murine MASH (Ramachandran 2019; Xiong 2023; Da Silva 2021).
- **Next step:** Immunofluorescence for MARCO/TIMD4 (KCs) vs TREM2/CD9 (LAMs) on FFPE liver sections; scRNA-seq or snRNA-seq from a comparable cohort.
- **Confidence label:** **Supported hypothesis** (in MASH generally), **exploratory hypothesis** in this specific dataset without deconvolution.

### Priority 2 — CXCL10–CXCR3 axis as biomarker and mechanistic driver
- **Classification:** Biomarker + mechanistic hypothesis
- **Why prioritize:** CXCL10 is a clinically actionable chemokine measurable in serum and a known driver of MASH inflammation. Its strong upregulation in this dataset is independent of the macrophage identity shift.
- **Evidence from current dataset:** log₂FC ≈ +3.5, FDR ≈ 1.2×10⁻⁷.
- **External evidence:** CXCL10 elevated in human NASH serum and correlated with disease activity (Zhang 2014; multiple studies).
- **Next step:** Serum CXCL10 ELISA in the same cohort; correlation with NAS/fibrosis stage; assess CXCR3⁺ T/NK-cell infiltration by IHC.
- **Confidence label:** **Supported hypothesis.**

### Priority 3 — Fn14 (TNFRSF12A) as a therapeutic target candidate
- **Classification:** Therapeutic target
- **Why prioritize:** Fn14 is upregulated in injured hepatocytes and promotes stellate-cell activation. Antibody drug conjugates against Fn14 are already in oncology trials, providing translational precedent.
- **Evidence from current dataset:** log₂FC ≈ +3.3, FDR ≈ 1.3×10⁻⁷.
- **External evidence:** Mechanistic data in NASH (Affò 2014; Liu 2017); Fn14 inhibitors explored preclinically.
- **Next step:** Validate Fn14 protein expression in MASH vs control by IHC; correlate with fibrosis stage; assess whether Fn14⁺ hepatocytes co-localize with TREM2⁺ LAMs (paracrine cross-talk hypothesis).
- **Caveat:** The existence of Fn14 oncology drugs is **not by itself** evidence of therapeutic efficacy in MASH.
- **Confidence label:** **Exploratory hypothesis.**

### Priority 4 — Mitochondrial stress program (CYCS + MTHFD1L + mitochondrial tRNAs)
- **Classification:** Mechanistic hypothesis + confounding/composition check
- **Why prioritize:** Mitochondrial dysfunction is central to MASH pathogenesis, but several signals here (e.g., UQCRBP1) are pseudogenes of uncertain functional meaning. Validation should distinguish genuine OXPHOS stress from RNA-level noise.
- **Evidence from current dataset:** Coherent direction across multiple mitochondria-encoded/related genes.
- **External evidence:** Strong literature support for mitochondrial dysfunction in MASH.
- **Next step:** qPCR with primers distinguishing UQCRBP1 pseudogene from UQCRB; mtDNA copy-number quantification; OXPHOS complex activity assays.
- **Confidence label:** **Supported hypothesis** (for mitochondrial dysfunction in MASH), **exploratory** for the specific pseudogene signals.

### Priority 5 — Cell-composition / deconvolution check before interpreting KC loss
- **Classification:** Confounding or composition check
- **Why prioritize:** Many of the "downregulated" genes may simply reflect fewer Kupffer cells per hepatocyte, not transcriptional suppression. Downstream mechanistic interpretation requires normalization.
- **Evidence from current dataset:** All 14 macrophage markers move in same direction — strongly suggestive of compositional change.
- **Next step:** Apply a digital deconvolution tool (e.g., CIBERSORTx, MuSiC, BisqueRNA) using a liver single-cell reference to estimate cell-type proportions; cross-reference with histology.
- **Confidence label:** **Established evidence** for compositional effects in bulk liver transcriptomics.

---

## 5. Evidence Grounding Summary

| Claim | Primary evidence | Independence check |
|-------|------------------|--------------------|
| Kupffer cell depletion + TREM2⁺ LAM emergence | Bulk transcriptomics (14+ genes) | Independent of single-study bias, replicates the canonical MASH scRNA-seq literature |
| CXCL10 inflammation | Bulk + extensive published serum/tissue evidence | Genuinely independent (clinical vs mechanistic) |
| Fn14 / TNFRSF12A upregulation | Bulk + published rodent/human liver injury data | Independent, though some human data derive from the same group as the murine work |
| Mitochondrial dysfunction | Bulk coherence + extensive MASH literature | Independent at the disease-association level; some sources share pathway over-representation |
| ECM/adhesion remodeling | Bulk only, mixed direction | Limited independent support; **flag as insufficient evidence** for any specific ECM conclusion |
| Metabolic dysregulation (CBS, CETP, FABP5) | Sparse, partial literature | Limited independent evidence — **exploratory** |

---

## 6. Limitations and Alternative Explanations

1. **Bulk-tissue composition confounding (most critical).** The macrophage signature could reflect (a) genuine loss of Kupffer cells, (b) transcriptional suppression of KC identity, or (c) loss of KCs as a *fraction* of total liver RNA. These have very different biological meanings. Required: deconvolution + IHC.

2. **Disease-stage heterogeneity.** No clinical metadata (NAS score, fibrosis stage, BMI, sex, age) is provided. MASH signatures differ markedly between early (steatosis + mild inflammation) and advanced (fibrosis-dominant) stages. The apparent absence of strong lipogenic-gene and stellate-cell gene signals may indicate early disease, while the atypical VCAM1 and P4HA1 downregulation may indicate a specific stage. *Investigation:* stratify by Brunt/Kleiner stage if metadata become available.

3. **Heavy representation of pseudogenes, lncRNAs, and miRNAs (≥15 of the top 100).** Many (UQCRBP1, CES1P2, GGTLC1, GUSBP2, GLUD1P2, RPSA2, plus multiple LOC/MIR entries) are functionally uncharacterized. They may be biologically real or reflect alignment noise. *Investigation:* re-quantify with a curated reference (e.g., GENCODE primary assembly only), filter low-complexity alignments.

4. **Direction of VCAM1 and P4HA1 is atypical for fibrotic MASH.** Both are typically upregulated in classical MASH/NASH. Their downregulation may indicate (a) endothelial dysfunction rather than activation, (b) early/non-fibrotic disease, or (c) sample-specific effects. *Investigation:* stratify by fibrosis stage and confirm with IHC.

5. **Association vs causation.** All interpretations above are differential-expression-based associations in case/control tissue. No causal inference is possible without perturbation experiments (e.g., TREM2 blockade, macrophage depletion, CXCL10 neutralization). The macrophage compartment shift in particular could be a *consequence* rather than a *driver* of MASH.

---

### Bottom Line

The dataset's dominant signal is a **shift from homeostatic Kupffer cells to TREM2⁺ lipid-associated macrophages**, accompanied by **CXCL10/Fn14-driven inflammation** and a **secondary mitochondrial stress response**. This is consistent with the established cellular model of human MASH. The metabolic and ECM programs are present but less robustly supported. Mechanistic, biomarker, and therapeutic claims should be deferred until single-cell or spatial validation confirms the cellular origin of the macrophage signature and clinical metadata allow stratification by disease stage.
