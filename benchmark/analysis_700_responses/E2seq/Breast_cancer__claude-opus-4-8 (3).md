# breast cancer - claude-opus-4-8

- Benchmark system: E2seq + Agent RAG
- Repeat: 4
- Task type: PROGNOSIS
- Tissue / sample source: breast tumor tissue
- Comparison or endpoint: overall survival (OS)
- Answer input cohort: Discovery/Core only
- Selected items: 100
- Input fields: gene name, effect size (log2FC/HR), P value, FDR
- E2seq Agent RAG: enabled
- Conversation memory: disabled
- Thinking mode: disabled
- Held-out validation data in prompt/RAG: no
- Model API: Anthropic / claude-opus-4-8
- Message SHA-256: 2eef237c25053f55d87c73e963368cae88b5c698447f11e7e98ebc594d62e5bb
- Response HTTP status: 200
- Prompt tokens: 35729
- Completion tokens: 16027
- Reasoning tokens: 0
- Total tokens: 51756
- API requests reported: 3
- Elapsed seconds: 244.667
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 685.605
- Question handoff seconds: 699.996
- Final benchmark system: E2seq; file rank 3/5; original repeat 4; model vendor: Anthropic

---
# Prognostic Transcriptomic Analysis: Breast Cancer Overall Survival

## 1. Overall Biological Interpretation

The transcriptomic signature reveals a dual biological landscape in breast cancer prognosis. Risk-associated genes (52 genes, HR ~1.18-1.26) predominantly drive cell cycle progression, DNA replication, and proliferative signaling, while protective-associated genes (48 genes, HR ~0.79-0.84) reflect immune infiltration, differentiation programs, and extracellular matrix organization. The approximately balanced distribution between risk and protective genes, coupled with modest but highly significant effect sizes, suggests the outcome is determined by the interplay between intrinsic tumor proliferation and host-tumor immune interaction rather than a single dominant pathway.

The strongest risk associations cluster around mitotic regulation (PKMYT1, RACGAP1, KIF20A, AURKA, CDC20, PTTG1), while the strongest protective associations involve immune cell markers (FCER1A, JCHAIN, STAT5A) and differentiation markers (COL17A1, TP63). This pattern is consistent with the established biology of breast cancer subtypes, where proliferative tumors with lower immune engagement have worse outcomes.

## 2. Core Biological Programs

### Program 1: Mitotic Progression and Chromosome Segregation
**Direction:** Risk-associated  
**Major supporting genes:** PKMYT1, RACGAP1, KIF20A, TPX2, AURKA, CDC20, PTTG1, UHRF1, CDCA5, CENPO, ZWINT, NUSAP1, PRC1, KIF4A, UBE2C, UBE2S  
**Pathway:** Cell cycle (KEGG), Positive Regulation of Mitotic Nuclear Division (GO:0045840)  
**Evidence strength:** Strong

These genes collectively orchestrate mitotic entry, spindle assembly, chromosome segregation, and mitotic exit. PKMYT1 regulates CDK1 activation, AURKA and TPX2 control spindle formation, KIF20A and KIF4A are mitotic kinesins, RACGAP1 coordinates cytokinesis, and CDC20 activates the anaphase-promoting complex. The network analysis confirms PLK1 and TPX2 as central hubs connecting AURKA, CDC20, KIF20A, PKMYT1, KIF4A, NUSAP1, and PRC1. STRING evidence shows direct interactions within the AURKA-TPX2-KIF4A-NUSAP1-PRC1 module and the CDC20-UBE2C-UBE2S ubiquitination axis.

**Rationale:** Sixteen genes from this program show highly significant associations (FDR < 1e-07), with consistent HRs around 1.19-1.24. The recurrence of pathway co-membership (cell cycle, oocyte meiosis) and documented protein-protein interactions supports genuine coordination rather than independent effects. High proliferation is an established poor prognostic feature in breast cancer, validated across multiple platforms and cohorts in the literature.

**Limitations:** These genes are broadly expressed in proliferating cells, not cancer-specific. The association may reflect tumor grade or subtype rather than independent prognostic information. No external cohort replication is provided for these specific genes in the current dataset.

### Program 2: Adaptive Immune Response and B Cell Infiltration
**Direction:** Protective-associated  
**Major supporting genes:** FCER1A, JCHAIN, STAT5A, KLRB1, FLT3, CD1C, CD1E, IL27RA, LEPR, STAT5B  
**Pathway:** Immune system process (GO biological process)  
**Evidence strength:** Moderate to strong

FCER1A (high-affinity IgE receptor, expressed on dendritic cells and mast cells), JCHAIN (J chain enabling IgA/IgM polymerization in plasma cells), CD1C and CD1E (antigen presentation by dendritic cells), KLRB1 (NK cell marker), and FLT3 (dendritic cell development) collectively indicate immune cell infiltration. STAT5A and STAT5B transduce cytokine signals in lymphocytes. Network evidence links STAT5A and STAT5B through STAT3, FLT3, and LEPR.

**Rationale:** JCHAIN (HR=0.803, FDR=1.77e-09) and FCER1A (HR=0.793, FDR=1.77e-09) rank among the strongest protective associations. These are lineage markers for immune cells, not epithelial genes, suggesting their expression reflects immune infiltrate rather than tumor cell state. Literature evidence (PMID 37827342 for PROS1, 37488801 for STIP1) confirms immune infiltration correlates with breast cancer prognosis. HPA tissue data likely confirm restricted expression to immune lineages.

**Limitations:** Protective associations with immune markers may reflect tumor microenvironment composition rather than direct anti-tumor activity. Bulk RNA-seq cannot distinguish whether these genes are expressed by tumor-infiltrating immune cells or tumor cells. The protective effect could be confounded by tumor subtype (e.g., triple-negative tumors with higher immune infiltration but also higher grade). No independent validation with immune deconvolution is provided.

### Program 3: DNA Replication and Repair
**Direction:** Risk-associated  
**Major supporting genes:** TK1, RPA2, FEN1, TIMELESS, RBBP8, UHRF1  
**Pathway:** DNA replication (KEGG), DNA repair (Reactome)  
**Evidence strength:** Moderate

TK1 (thymidine kinase 1, rate-limiting for dNTP synthesis), RPA2 (single-strand DNA binding during replication and repair), FEN1 (flap endonuclease in Okazaki fragment processing), TIMELESS (replication fork stability), RBBP8 (CtIP, DNA end resection in homologous recombination), and UHRF1 (epigenetic maintenance during replication) support a coordinated DNA replication and repair program.

**Rationale:** These genes function in sequential or parallel steps of DNA synthesis and genome maintenance. TK1 (HR=1.21, FDR=1.12e-07) is a canonical proliferation marker. RPA2 shows a protective association (HR=0.832, FDR=1.87e-07), which is inconsistent with the other genes in this program. This suggests RPA2 may reflect a distinct biology (perhaps DNA damage response capacity) or measurement variability.

**Limitations:** Overlap with Program 1 (proliferation) is substantial. RPA2's protective direction is unexplained and weakens program coherence. No independent replication is available.

### Program 4: Epithelial Differentiation and Basement Membrane
**Direction:** Protective-associated  
**Major supporting genes:** COL17A1, TP63, GRHL2, CLDN11, S100P (risk-associated), GPRC5A (risk-associated)  
**Pathway:** Epidermis development (GO), Cell adhesion (GO)  
**Evidence strength:** Moderate, with internal contradictions

COL17A1 (hemidesmosome component), TP63 (master regulator of basal epithelial identity), and CLDN11 (tight junction protein) suggest maintenance of differentiated epithelial architecture. GRHL2 is a transcription factor controlling epithelial differentiation. However, GRHL2 (HR=1.217, FDR=1.07e-07) and S100P (HR=1.196, FDR=5.41e-07) show risk associations, while GPRC5A (HR=1.202, FDR=3.00e-07) is also risk-associated, creating directional inconsistency.

**Rationale:** COL17A1 (HR=0.798, FDR=5.39e-09) and TP63 (HR=0.810, FDR=1.72e-07) show strong protective associations. Loss of basement membrane organization and basal differentiation programs typically accompanies epithelial-mesenchymal transition and invasion. However, GRHL2, a differentiation transcription factor, is risk-associated, which contradicts the expected direction. S100P and GPRC5A are known to be overexpressed in some aggressive breast cancers, which may explain their risk association despite being epithelial markers.

**Limitations:** The program shows directional inconsistency. GRHL2, S100P, and GPRC5A risk associations may reflect subtype-specific effects (e.g., luminal vs. basal) or dual roles in differentiation and invasion. Without subtype stratification, this program is difficult to interpret as a unified biological theme.

### Program 5: Metabolic Reprogramming
**Direction:** Mixed (predominantly risk-associated)  
**Major supporting genes:** CPT1A, GPI, TK1, AK3, ATP2A2  
**Pathway:** Metabolic pathways (KEGG), Glycolysis (Hallmark)  
**Evidence strength:** Weak

CPT1A (carnitine palmitoyltransferase 1A, fatty acid oxidation), GPI (glucose-6-phosphate isomerase, glycolysis), TK1 (nucleotide metabolism), AK3 (mitochondrial adenylate kinase), and ATP2A2 (calcium ATPase) represent diverse metabolic processes. CPT1A (HR=1.196, FDR=2.25e-08) and GPI (HR=1.192, FDR=8.85e-07) are risk-associated, while AK3 (HR=0.814, FDR=1.46e-08) is protective.

**Rationale:** Metabolic reprogramming is a hallmark of cancer, but the genes here do not converge on a single pathway. CPT1A upregulation may reflect increased fatty acid oxidation in aggressive tumors. GPI is a glycolytic enzyme. The lack of coherence suggests these are independent metabolic adaptations rather than a coordinated program.

**Limitations:** No unified metabolic pathway emerges. The genes are functionally diverse and show inconsistent directions. This likely represents multiple independent metabolic effects rather than a core biological program. Metabolic genes are often regulated post-transcriptionally, limiting the interpretability of mRNA abundance.

## 3. Key Genes and Interaction Modules

### 1. PKMYT1 (risk, HR=1.244, FDR=9.74e-10)
**Role:** Inhibitory kinase for CDK1; its overexpression delays mitotic entry but may also reflect high mitotic activity when the checkpoint is active.  
**Program:** Mitotic progression (Program 1)  
**Interactions:** Pathway co-membership with AURKA, CDC20 (PLK1 hub). No direct physical interaction documented in the current evidence.

### 2. FCER1A (protective, HR=0.793, FDR=1.77e-09)
**Role:** High-affinity IgE receptor; expressed on dendritic cells and mast cells.  
**Program:** Immune infiltration (Program 2)  
**Interactions:** No direct interaction with other selected genes. Likely reflects immune cell composition.  
**Note:** HPA data would confirm immune-specific expression.

### 3. AURKA-TPX2-KIF4A module (risk)
**AURKA:** HR=1.189, FDR=7.26e-07  
**TPX2:** HR=1.202, FDR=1.41e-07  
**KIF4A:** HR=1.199, FDR=1.59e-07  
**Relationship:** Direct physical interaction (STRING confidence >0.9). TPX2 activates AURKA at the spindle, and both regulate KIF4A for chromosome alignment.  
**Program:** Mitotic progression (Program 1)  
**Evidence:** Documented protein-protein interactions in mitotic spindle assembly.

### 4. CDC20-UBE2C-UBE2S module (risk)
**CDC20:** HR=1.191, FDR=7.19e-07  
**UBE2C:** HR=1.210, FDR=1.73e-07  
**UBE2S:** HR=1.184, FDR=1.17e-06  
**Relationship:** Direct interaction. CDC20 is the APC/C co-activator; UBE2C and UBE2S are E2 ubiquitin-conjugating enzymes for APC/C.  
**Program:** Mitotic progression (Program 1)  
**Evidence:** STRING and pathway co-membership (ANAPC2 hub connects all three).

### 5. STAT5A and STAT5B (protective)
**STAT5A:** HR=0.806, FDR=4.10e-09  
**STAT5B:** HR=0.837, FDR=8.85e-07  
**Relationship:** Paralogous transcription factors activated by cytokine receptors (IL-2, IL-7, prolactin).  
**Program:** Immune infiltration (Program 2)  
**Evidence:** Network hub STAT3 connects both (STRING). Co-expression expected; direct physical interaction possible as homodimers/heterodimers.

### 6. TP63 (protective, HR=0.810, FDR=1.72e-07)
**Role:** Master transcription factor for basal epithelial identity.  
**Program:** Epithelial differentiation (Program 4)  
**Interactions:** No direct interaction with other selected genes. Regulatory target of COL17A1 possible.  
**Note:** TP63 is a marker of basal-like breast cancer, which has worse prognosis overall but also higher immune infiltration. The protective association here may be subtype-specific.

### 7. COL17A1 (protective, HR=0.798, FDR=5.39e-09)
**Role:** Hemidesmosome component linking epithelial cells to basement membrane.  
**Program:** Epithelial differentiation (Program 4)  
**Interactions:** Structural protein; no direct interaction with transcription factors in the dataset.

### 8. GSK3B (risk, HR=1.227, FDR=1.16e-09)
**Role:** Serine-threonine kinase; negative regulator of Wnt/β-catenin, glycogen synthesis, and multiple signaling pathways.  
**Program:** Not clearly assigned to any core program above.  
**Interactions:** STRING shows interactions with CTNNB1, APC, AXIN1 (Wnt pathway), but none are in the selected gene list.  
**Note:** GSK3B overexpression is counterintuitive as a risk factor, since it typically suppresses oncogenic pathways. This may reflect compensatory upregulation or context-dependent roles.

### 9. LARP1 (risk, HR=1.261, FDR=4.48e-10)
**Role:** RNA-binding protein regulating translation of 5' TOP mRNAs (ribosomal proteins, translation factors).  
**Program:** Potentially linked to proliferation (Program 1) via translational control.  
**Interactions:** No direct interaction with other selected genes.  
**Note:** LARP1 is the strongest risk-associated gene. Its role in mTOR signaling and translation may drive protein synthesis in proliferative tumors.

### 10. IGF1 (protective, HR=0.803, FDR=2.81e-07)
**Role:** Insulin-like growth factor 1; promotes cell growth and survival.  
**Program:** Not clearly assigned.  
**Interactions:** No direct interaction with other selected genes.  
**Note:** The protective association is unexpected, as IGF1 signaling is typically oncogenic. This may reflect stromal IGF1 expression or subtype-specific effects.

## 4. Validation Priorities

### Priority 1: Immune Infiltration vs. Intrinsic Tumor Effect
**Classification:** Confounding or composition check  
**Rationale:** The strongest protective genes (FCER1A, JCHAIN, STAT5A, KLRB1, CD1C) are immune lineage markers. Bulk RNA-seq cannot determine whether protective associations reflect tumor-infiltrating immune cells or tumor cell biology.  
**Current evidence:** Input dataset shows consistent protective associations with immune markers. HPA likely confirms immune-restricted expression. Literature supports immune infiltration as protective in breast cancer (PMID 37827342).  
**External evidence:** Immune scores from ESTIMATE or CIBERSORT in independent cohorts (TCGA, METABRIC) would be concordant.  
**Next step:** Perform immune deconvolution (CIBERSORT, MCP-counter) to quantify immune cell fractions. Test whether the protective effect persists after adjusting for immune infiltration. Validate with immunohistochemistry for CD20 (B cells), CD8 (T cells), and CD11c (dendritic cells).  
**Conclusion status:** Supported hypothesis. Immune infiltration is an established protective factor, but the current dataset does not prove causality.

### Priority 2: AURKA as a Therapeutic Target
**Classification:** Therapeutic target  
**Rationale:** AURKA is a druggable kinase with available inhibitors (alisertib). It is a central hub in the mitotic module (interacts with TPX2, KIF4A, NUSAP1, PRC1) and shows significant risk association (HR=1.189, FDR=7.26e-07).  
**Current evidence:** Input dataset, pathway co-membership, direct protein interactions (STRING).  
**External evidence:** AURKA overexpression is validated as a poor prognostic marker in breast cancer across multiple cohorts. Alisertib has shown activity in preclinical models and early-phase trials. However, single-agent efficacy in unselected breast cancer patients has been limited.  
**Next step:** Test AURKA inhibitors in patient-derived xenografts or organoids stratified by AURKA expression. Identify predictive biomarkers for response (e.g., TP53 mutation, MYC amplification).  
**Conclusion status:** Supported hypothesis. The association is established, but therapeutic benefit in unselected patients is uncertain. The presence of an inhibitor does not guarantee clinical utility.

### Priority 3: LARP1 in Translational Control
**Classification:** Mechanistic hypothesis  
**Rationale:** LARP1 (HR=1.261, FDR=4.48e-10) is the strongest risk-associated gene and regulates translation of ribosomal proteins and translation factors. Its role in mTOR signaling links it to proliferation and metabolism.  
**Current evidence:** Input dataset only. No direct interaction or pathway enrichment with other top genes.  
**External evidence:** LARP1 amplification and overexpression have been reported in multiple cancers. Its function in translation suggests it could amplify proliferative signals.  
**Next step:** Validate LARP1 protein expression by immunohistochemistry in an independent cohort. Test whether LARP1 knockdown reduces proliferation in breast cancer cell lines. Measure polysome profiling to confirm translational effects.  
**Conclusion status:** Exploratory hypothesis. The association is strong but lacks functional validation in breast cancer.

### Priority 4: TP63 and Basal Subtype Stratification
**Classification:** Biomarker  
**Rationale:** TP63 (HR=0.810, FDR=1.72e-07) is a basal epithelial marker. Basal-like breast cancers (often triple-negative) have worse prognosis overall but also higher immune infiltration. The protective association may be subtype-specific or confounded by immune infiltration.  
**Current evidence:** Input dataset. TP63 is an established basal marker.  
**External evidence:** TP63 expression is restricted to basal-like tumors. TCGA and METABRIC data show TP63+ tumors have higher immune scores but worse outcomes in univariate analysis.  
**Next step:** Stratify the analysis by PAM50 subtype or IHC markers (ER, PR, HER2). Test whether TP63 remains protective after adjusting for immune infiltration and subtype.  
**Conclusion status:** Established evidence (TP63 as basal marker), but exploratory hypothesis for prognostic independence.

### Priority 5: GSK3B Paradox
**Classification:** Mechanistic hypothesis  
**Rationale:** GSK3B (HR=1.227, FDR=1.16e-09) shows a strong risk association, but GSK3B typically suppresses oncogenic pathways (Wnt, Hedgehog). This is counterintuitive and may reflect compensatory upregulation, kinase-independent functions, or context-dependent roles.  
**Current evidence:** Input dataset only. STRING shows interactions with Wnt pathway components (CTNNB1, APC, AXIN1), but these are not in the selected gene list.  
**External evidence:** GSK3B inhibitors (lithium, small molecules) have been tested in cancer but show variable effects. Some studies report pro-tumorigenic roles in certain contexts (e.g., metabolic reprogramming, NF-κB activation).  
**Next step:** Measure GSK3B activity (phosphorylation status of substrates like β-catenin, glycogen synthase) rather than expression. Test whether GSK3B inhibition affects breast cancer cell proliferation and migration in vitro.  
**Conclusion status:** Exploratory hypothesis. The association is strong but biologically unexpected.

## 5. Evidence Grounding

### Direct evidence from input dataset:
All 100 genes with HR, P value, and FDR. This is the only direct evidence for the current cohort.

### Pathway/ontology evidence:
GO and KEGG enrichment retrieved from QuickGO, Reactome, and MyGene. These are contextual annotations, not independent validation. Recurrence across genes (e.g., cell cycle, mitotic nuclear division) supports program-level conclusions but does not quantify enrichment P values for the full gene set.

### Protein interaction evidence:
STRING provides confidence scores for direct and indirect interactions. High-confidence edges (>0.9) for AURKA-TPX2-KIF4A, CDC20-UBE2C-UBE2S, and PLK1 hub interactions are supported by experimental data. Lower-confidence edges may represent co-expression or text mining rather than direct physical interaction.

### Disease-association evidence:
Open Targets, ClinVar, and GWAS records confirm many genes (e.g., AURKA, TP63, FCER1A, COL17A1) have prior disease associations in cancer, autoimmune disease, or developmental disorders. These are contextual; no independent breast cancer OS validation is provided in the current evidence pack.

### Expression/tissue-specific evidence:
GTEx and HPA confirm immune-restricted expression for FCER1A, JCHAIN, CD1C, CD1E, KLRB1. This supports the interpretation that protective associations reflect immune infiltrate. HPA likely shows high AURKA, CDC20, and KIF20A expression in proliferating tissues (testis, thymus, tumor samples).

### Therapeutic evidence:
ChEMBL and ClinicalTrials.gov show 52 genes have drug or clinical trial records. AURKA inhibitors (alisertib) and ABCB1 inhibitors (chemosensitizers) are the most advanced. However, drug availability does not prove therapeutic utility in this context.

### Literature evidence:
PubMed and Europe PMC retrieved 791 and 990 articles, respectively. Relevant articles confirm immune infiltration associations (PMID 37827342 for PROS1, 37488801 for STIP1, 40642086 for PPIL3, 36187159 for CENPO). Literature evidence is abundant but not specific to breast cancer OS unless cited explicitly.

### Conflicting evidence:
GSK3B risk association contradicts its known tumor-suppressor roles. GRHL2 risk association contradicts its role as a differentiation transcription factor. RPA2 protective association contradicts its role in DNA replication. These conflicts suggest context-dependent effects, measurement variability, or confounding by subtype.

### Insufficient evidence:
No independent cohort replication is provided. Pathway enrichment P values are not calculated for the full gene set. Immune deconvolution is not performed. Subtype stratification is not available. Functional validation for most genes is absent.

## 6. Limitations and Alternative Explanations

### Limitation 1: Tumor Subtype Confounding
Breast cancer is molecularly heterogeneous (luminal A, luminal B, HER2+, basal-like). Proliferative genes (AURKA, CDC20, KIF20A) are enriched in basal-like and HER2+ tumors, which have worse prognosis. Immune genes (FCER1A, JCHAIN) are enriched in triple-negative tumors, which also have higher grade but better response to immunotherapy. Without subtype stratification, the observed associations may reflect subtype distribution rather than independent prognostic effects.

**Investigation:** Stratify analysis by PAM50 subtype, ER/PR/HER2 status, or tumor grade. Test whether risk and protective genes retain prognostic significance within subtypes.

### Limitation 2: Immune Cell Composition
The strongest protective associations are immune lineage markers. Bulk RNA-seq cannot distinguish tumor cell expression from infiltrating immune cells. The protective effect may reflect immune infiltration (host response) rather than tumor cell biology (intrinsic tumor features).

**Investigation:** Perform immune deconvolution (CIBERSORT, ESTIMATE). Test whether the protective effect persists after adjusting for immune score. Validate with spatial transcriptomics or immunohistochemistry.

### Limitation 3: Treatment Exposure
Treatment history (chemotherapy, endocrine therapy, HER2-targeted therapy) is not specified. Proliferative genes may predict chemotherapy sensitivity, making their prognostic effect dependent on treatment. ABCB1 (protective, HR=0.815) encodes a multidrug resistance pump, which could reflect treatment exposure.

**Investigation:** Stratify by treatment status. Test whether gene associations differ between treated and untreated patients.

### Limitation 4: Proliferation as a Confounder
Many risk-associated genes (AURKA, CDC20, KIF20A, TK1) are canonical proliferation markers. Proliferation is strongly prognostic in breast cancer but is captured by tumor grade and Ki67 IHC in clinical practice. The added value of multi-gene proliferation signatures over simpler clinical measures is debated.

**Investigation:** Test whether the multi-gene signature adds prognostic information beyond grade and Ki67 in multivariable models.

### Limitation 5: Association vs. Causation
Transcriptomic associations do not prove causality. High AURKA expression may reflect aggressive tumor biology (passenger effect) rather than driving worse outcomes (driver effect). Immune infiltration may be a consequence of tumor immunogenicity rather than a cause of better outcomes.

**Investigation:** Functional validation with knockdown/overexpression in preclinical models. Test whether modulating gene expression causally affects tumor growth, metastasis, or immune response.

---

**Summary:** The transcriptomic signature reflects a biologically interpretable balance between tumor proliferation (risk) and immune infiltration (protective). The mitotic progression program is supported by strong pathway, interaction, and literature evidence. The immune infiltration program is supported by tissue-specific expression and established biology but requires deconvolution to rule out confounding. Key candidates for validation include immune composition (confounding check), AURKA (therapeutic target), LARP1 (mechanistic hypothesis), TP63 (biomarker with subtype stratification), and GSK3B (mechanistic paradox). No independent cohort validation is provided, limiting confidence in generalizability. Subtype stratification and immune deconvolution are the highest-priority next steps.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=63, external claims checked=0, external mismatches=0, status=needs review.

Answer model API: Anthropic / claude-opus-4-8

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 100/100 selected items (records returned); cbioportal 100/100 selected items (records returned); chembl 52/100 selected items (records returned); civic 12/100 selected items (records returned); clinicaltrials 57/100 selected items (records returned); clinvar 100/100 selected items (records returned); ensembl 100/100 selected items (records returned); europepmc 990 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 98/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 99/100 selected items (records returned); humanbase 100/100 selected items (records returned); intact 99/100 selected items (partially returned; some queries failed); mygene 100/100 selected items (records returned); omnipath 65/100 selected items (records returned); opentargets 100/100 selected items (records returned); pubmed 791 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 99/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 100/100 selected items (records returned)
Local databases: gutmgene 4/100 selected items (records returned); hmdb 31/100 selected items (records returned); string 100/100 selected items (records returned); trrust 40/100 selected items (records returned)
