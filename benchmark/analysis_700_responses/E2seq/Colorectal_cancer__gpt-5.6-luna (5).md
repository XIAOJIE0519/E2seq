# colorectal cancer - gpt-5.6-luna

- Benchmark system: E2seq + Agent RAG
- Repeat: 7
- Task type: PROGNOSIS
- Tissue / sample source: colorectal tumor tissue
- Comparison or endpoint: overall survival (OS)
- Answer input cohort: Discovery/Core only
- Selected items: 100
- Input fields: gene name, effect size (log2FC/HR), P value, FDR
- E2seq Agent RAG: enabled
- Conversation memory: disabled
- Thinking mode: disabled
- Held-out validation data in prompt/RAG: no
- Model API: OpenAI / gpt-5.6-luna
- Message SHA-256: dfb8fe82357dbea353d34030380d74028b528c91505f5793c7261ee9e4376675
- Response HTTP status: 200
- Prompt tokens: 55916
- Completion tokens: 26031
- Reasoning tokens: 0
- Total tokens: 81947
- API requests reported: 5
- Elapsed seconds: 244.228
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 1848.064
- Question handoff seconds: 1861.273
- Final benchmark system: E2seq; file rank 5/5; original repeat 7; model vendor: OpenAI

---
## Data-quality and evidence status

This is an **overall-survival prognostic analysis**, so the uploaded HRs indicate association with hazard, not differential expression or causality. Among 100 unique genes, 54 are risk-associated (HR > 1) and 46 protective-associated (HR < 1); 8 have FDR ≤ 0.01 and 71 have FDR ≤ 0.05. The results therefore contain a substantial prognostic signal, but interpretation requires caution because 209 input rows correspond to 100 unique genes, with 53 duplicated gene/probe entries. Direction conflicts are specifically reported for **DCBLD2**, **LOC101928747|RBMX|SNORD61**, and **BCL2L14**. The representative ledger values are used below, but these conflicting annotations should be resolved at the probe-to-gene level.

**External statistical validation was not performed.** Pathway, interaction, tissue, genetic, and literature records are contextual evidence and do not constitute replication of the OS associations. The supplied GO/KEGG/STRING results were retrieved previously and were not recomputed here; they should therefore be considered exploratory annotation rather than formal enrichment statistics.

## 1. Overall biological interpretation

The prognostic pattern is consistent with several partly connected features of colorectal tumor biology:

1. A **risk-associated stromal, extracellular-matrix, and cell-motility phenotype**, represented by INHBB, ITGBL1, DCBLD2, PTPN14, ABL2, TPM4, SCEL, and ADAMTS18.
2. A **protective epithelial differentiation and intestinal epithelial-function phenotype**, represented by CDX2, CDX1, LGALS4, MYO5B, and related genes.
3. A **protective mitochondrial and intermediary-metabolism signature**, including ATP23, NDUFA9, CS, GLYCTK, MCCC2, ILVBL, COA3, ATP5B, and OGDHL.
4. A **mixed immune or tumor–immune microenvironment signal**, including risk-associated NT5E and protective-associated LGALS9, TAPBPL, CCL15, and CCDC134.
5. Additional risk-associated signaling and regulatory features, including AKT3, MIR31HG, ZEB1-AS1, FGF19, SLC2A3, and several poorly annotated probes or noncoding transcripts.

The most defensible interpretation is not that one pathway explains prognosis, but that poorer OS is associated with a tumor state combining **invasive/stromal remodeling and altered signaling**, whereas better OS is associated with **retained epithelial identity and mitochondrial/metabolic function**. This remains a prognostic association; the dataset does not establish that any of these programs cause mortality or treatment resistance.

## 2. Core biological programs

### Program 1: Extracellular matrix remodeling, adhesion, and invasive cell-state biology

- **Direction:** Predominantly risk-associated.
- **Supporting genes:** **INHBB** HR 1.433, FDR 0.00109; **DCBLD2** HR 1.408, FDR 0.00865; **ITGBL1** HR 1.299, FDR 0.0306; **PTPN14** HR 1.362, FDR 0.0250; **ABL2** HR 1.301, FDR 0.0276; **TPM4** HR 1.364, FDR 0.00891; **SCEL** HR 1.254, FDR 0.0394; **ADAMTS18** HR 1.263, FDR 0.0468.
- **Relevant standardized pathways:** GO terms related to extracellular matrix organization, cell-substrate adhesion, actin cytoskeleton organization, and regulation of cell migration; Reactome extracellular-matrix and integrin-associated processes would be appropriate if formally tested.
- **Interpretation:** Multiple risk-associated genes span signaling, cytoskeletal structure, adhesion, and matrix remodeling rather than representing a single isolated marker. This supports a possible invasive or stromally supported tumor phenotype. **TPM4**, **ABL2**, and **PTPN14** are compatible with cytoskeletal or adhesion-related biology, while **ITGBL1**, **DCBLD2**, and **ADAMTS18** are compatible with extracellular or matrix-associated processes. **INHBB** is the strongest statistical signal and has direct colorectal-cancer literature support: the supplied Europe PMC record PMID **41992239** reports that high INHBB expression in colorectal cancer is associated with poor prognosis and malignant phenotypes.
- **Evidence strength:** **Moderate for a prognostic program**, because several independent genes have HR > 1 and FDR ≤ 0.05, with additional pathway plausibility and literature support for INHBB.
- **Limitations:** Formal pathway enrichment was not supplied. Matrix-associated transcripts can reflect fibroblast abundance, tumor purity, desmoplasia, or advanced stage rather than tumor-cell-intrinsic invasion. DCBLD2 has duplicate direction conflict, so its contribution requires probe-level review. The literature for INHBB supports plausibility but is not an independent statistical validation of this cohort.

### Program 2: Intestinal epithelial differentiation and epithelial integrity

- **Direction:** Predominantly protective-associated.
- **Supporting genes:** **CDX2** HR 0.748, FDR 0.0355; **MYO5B** HR 0.748, FDR 0.0282; **LGALS4** HR 0.771, FDR 0.0512; **CDX1** HR 0.781, FDR 0.0573; **RAB11FIP4** HR 0.736, FDR 0.0329; **MYO5B** and **LGALS4** are particularly compatible with epithelial differentiation and polarized epithelial function.
- **Relevant standardized pathways:** GO intestinal epithelial differentiation, epithelial cell differentiation, cell-cell junction organization, and apical membrane organization; Hallmark **Epithelial–Mesenchymal Transition** may be relevant as an inverse biological contrast, but it was not calculated here.
- **Interpretation:** The coordinated protective direction of CDX2, MYO5B, RAB11FIP4, and several epithelial-associated genes suggests that preservation of intestinal epithelial identity may be associated with better OS. The supplied PMID **30631044** reports that CDX2 inhibits proliferation and tumor formation in colon cancer cells through suppression of Wnt/β-catenin signaling, providing mechanistic plausibility. However, CDX1 and LGALS4 do not meet FDR ≤ 0.05 in the supplied ledger, so the strongest direct evidence comes from CDX2, MYO5B, and RAB11FIP4.
- **Evidence strength:** **Supported hypothesis**, not established program-level evidence.
- **Limitations:** These genes may be markers of tumor differentiation, tumor purity, or the proportion of normal mucosa rather than causal protective factors. An inverse EMT interpretation is plausible but cannot be inferred directly without EMT gene-set scores, expression directions, or histopathology.

### Program 3: Mitochondrial respiration and intermediary metabolism

- **Direction:** Predominantly protective-associated.
- **Supporting genes:** **ATP23** HR 0.688, FDR 0.00664; **NDUFA9** HR 0.689, FDR 0.00865; **GLYCTK** HR 0.709, FDR 0.0203; **MCCC2** HR 0.739, FDR 0.0282; **ILVBL** HR 0.725, FDR 0.0329; **CS** HR 0.754, FDR 0.0388; **COA3** HR 0.744, FDR 0.0434; **ATP5B** HR 0.748, FDR 0.0593; **OGDHL** HR 0.686, FDR 0.0744.
- **Relevant standardized pathways:** Reactome mitochondrial electron transport, TCA cycle, and respiratory electron transport; KEGG glyoxylate and dicarboxylate metabolism and amino-acid metabolism are relevant annotations. GLYCTK is annotated to fructose catabolism, pentose-phosphate-related metabolism, and glycine/serine/threonine metabolism.
- **Interpretation:** Several mitochondrial and metabolic genes show HR < 1, including the highly significant ATP23 and NDUFA9. The pattern is compatible with better survival among tumors retaining oxidative and intermediary-metabolic functions. The retrieved STRING records provide limited network support, including associations involving **CS–ACSS2**, **COA3–ILVBL**, and **MT-CO1** connections; these should be interpreted as database-supported network relationships, not necessarily direct physical interactions among the selected genes.
- **Evidence strength:** **Moderate for a metabolic prognostic pattern**, based on multiple concordant HRs and pathway annotation.
- **Limitations:** Survival associations do not reveal whether oxidative phosphorylation is increased or decreased in the tumors because expression levels and reference contrasts are not provided. Metabolic genes are strongly affected by cellular composition, hypoxia, nutritional state, and tissue handling. The retrieved pathway recurrence is not a newly calculated enrichment P value.

### Program 4: Immune, inflammatory, and purinergic tumor–microenvironment signaling

- **Direction:** Mixed, with both risk- and protective-associated components.
- **Supporting genes:** Risk-associated **NT5E** HR 1.313, FDR 0.0394; protective-associated **LGALS9** HR 0.753, FDR 0.0420; **TAPBPL** HR 0.711, FDR 0.0192; **CCL15** HR 0.753, FDR 0.0355; **CCDC134** HR 0.712, FDR 0.0252.
- **Relevant standardized pathways:** GO regulation of T-cell migration, purine nucleotide metabolism/adenosine signaling, antigen presentation, and immune-cell communication.
- **Interpretation:** The retrieved GO annotation included regulation of T-cell migration, while NT5E/CD73 is a recognized component of extracellular adenosine biology. The supplied PubMed record PMID **36480312** describes CD73/NT5E as a potential cancer-prognostic and immunotherapy biomarker across cancers, and PMID **42363170** concerns mesothelin-targeted immunotherapy in colorectal-cancer organoids. These records support biological relevance but not efficacy or cohort replication. The protective and risk directions are mixed, suggesting that this is more likely a composition- or context-dependent microenvironmental signal than a uniform “immune activation” program.
- **Evidence strength:** **Exploratory hypothesis**.
- **Limitations:** Bulk tumor tissue cannot distinguish malignant-cell expression from immune, endothelial, or stromal expression. The direction of NT5E may reflect immunosuppressive adenosine biology, whereas LGALS9, TAPBPL, CCL15, and CCDC134 may reflect different immune compartments. Cell deconvolution and spatial validation are required.

### Program 5: Pro-survival signaling, metabolic stress, and regulatory transcripts

- **Direction:** Predominantly risk-associated, but less coherent than Programs 1–3.
- **Supporting genes:** **AKT3** HR 1.318, FDR 0.0388; **SLC2A3** HR 1.281, FDR 0.0722; **FGF19** HR 1.291, FDR 0.0512; **MIR31HG** HR 1.309, FDR 0.00664; **ZEB1-AS1** HR 1.372, FDR 0.00865; **GADD45B** HR 1.324, FDR 0.0630.
- **Relevant standardized pathways:** Reactome PI3K/AKT signaling, FGFR signaling, cellular responses to stress, and glucose transport; FGF19 is annotated to FGFR4/β-Klotho signaling, PI3K cascade, and phospholipase-C-mediated signaling.
- **Interpretation:** AKT3 is FDR-significant and FGF19 is directionally compatible with a growth and survival signaling axis, while SLC2A3 is compatible with increased glucose transport or stress adaptation. MIR31HG and ZEB1-AS1 may represent regulatory or state-associated noncoding components. These genes form a biologically plausible but not formally demonstrated risk module.
- **Evidence strength:** **Exploratory to supported hypothesis**, strongest for AKT3 and the noncoding RNA associations individually.
- **Limitations:** The genes do not demonstrate a common causal pathway in this dataset. FGF19 and SLC2A3 have FDR values above 0.05. The supplied FGF19 STRING/Reactome records establish ligand–receptor/pathway relationships but do not establish that FGF19 drives the observed AKT3 association.

## 3. Key genes and interaction modules

The following candidates are prioritized by statistical strength, biological coherence, or validation value. Relationships are classified explicitly.

1. **INHBB** — risk-associated, HR 1.433, P = 1.999e-08, FDR = 0.001093. It is the strongest uploaded signal and fits the matrix/remodeling and TGF-β-family context. The colorectal-cancer literature record PMID **41992239** supports association with poor prognosis and malignant phenotypes. Any relationship to ITGBL1, DCBLD2, or PTPN14 is currently **indirect or putative pathway/state co-occurrence**, not a demonstrated direct interaction.

2. **DCBLD2** — risk-associated representative HR 1.408, P = 9.860e-07, FDR = 0.008647, but with a reported **direction conflict across duplicate rows**. It is a candidate matrix/vascular or signaling-associated marker. Its relationship to INHBB and ITGBL1 is **pathway or microenvironmental co-membership**, not direct physical interaction. Probe-level concordance must be checked before prioritization.

3. **ITGBL1** — risk-associated, HR 1.299, P = 1.959e-05, FDR = 0.03061. It is compatible with extracellular-matrix and adhesion biology. Its relationship to ABL2, TPM4, and PTPN14 is best described as **functional co-membership in adhesion/cytoskeletal processes** or an indirect invasive-state relationship.

4. **TPM4–ABL2–PTPN14 cytoskeletal/adhesion module** — TPM4 HR 1.364, FDR 0.00891; ABL2 HR 1.301, FDR 0.0276; PTPN14 HR 1.362, FDR 0.0250. Together they support a risk-associated motility or adhesion state. The available evidence supports **pathway co-membership and possible co-expression**, not a direct physical complex.

5. **CDX2** — protective-associated, HR 0.7478, P = 2.985e-05, FDR = 0.0355. It represents retained intestinal differentiation and has colorectal-cancer mechanistic literature support in PMID **30631044**. Its relationship to CDX1 and LGALS4 is **lineage/pathway co-membership**; the supplied data do not establish direct regulation among these genes.

6. **ATP23–NDUFA9 mitochondrial module** — ATP23 HR 0.6885, FDR 0.00664; NDUFA9 HR 0.6886, FDR 0.00865. This is one of the strongest protective-associated modules and is compatible with mitochondrial respiratory function. The ATP23 literature record PMID **17135288** concerns interaction of prohibitins with ATP23, but does not validate the present colorectal-cancer survival association. Their relationship is **mitochondrial pathway co-membership**, not evidence of direct interaction between ATP23 and NDUFA9.

7. **GLYCTK–CS–ILVBL metabolic module** — GLYCTK HR 0.709, FDR 0.0203; CS HR 0.754, FDR 0.0388; ILVBL HR 0.725, FDR 0.0329. These genes support intermediary metabolism and mitochondrial/TCA-related biology. STRING records report network associations involving **CS–ACSS2** and **COA3–ILVBL**; the exact relationship type is database-dependent, and these records should not be treated as proof of direct physical interaction among all module members.

8. **NT5E** — risk-associated, HR 1.313, P = 4.326e-05, FDR = 0.03939. It is a candidate purinergic/adenosine microenvironment marker. Its relationship to LGALS9, TAPBPL, and CCL15 is **immune-program co-occurrence or indirect microenvironmental association**, not direct interaction. PMID **36480312** supports its broad prognostic and immunotherapy relevance but not clinical efficacy in this cohort.

9. **MIR31HG–ZEB1-AS1 regulatory pair** — MIR31HG HR 1.309, FDR 0.00664; ZEB1-AS1 HR 1.372, FDR 0.00865. Both are risk-associated noncoding transcripts and may mark transcriptional plasticity, invasion, or epithelial-state change. The relationship is **putative regulatory or co-expression association**; no direct regulatory edge was supplied.

10. **FGF19–AKT3 signaling hypothesis** — FGF19 HR 1.291, FDR 0.05123; AKT3 HR 1.318, FDR 0.03875. FGF19 has curated ligand relationships with FGFR4, FGFR1, FGFR2, and KLB and is linked to PI3K/AKT and phospholipase-C pathways. These are **ligand–receptor and pathway relationships** in external annotations; a functional FGF19-to-AKT3 relationship in these tumors remains **putative**, and FGF19 itself is not FDR-significant at 0.05.

## 4. Validation priorities

### 1. Validate an INHBB-centered stromal/invasive mechanism  
**Classification:** Mechanistic hypothesis

- **Why prioritize:** INHBB is the strongest risk-associated gene, HR 1.433 and FDR 0.001093, and is supported by the colorectal-cancer literature record PMID **41992239**.
- **Current dataset evidence:** Strong direct OS association, with additional risk-associated matrix and adhesion genes including ITGBL1, DCBLD2, PTPN14, TPM4, and ABL2.
- **External evidence:** Literature supports INHBB association with poor prognosis and malignant phenotypes. This is contextual and may overlap with the same biological literature base; it is not independent cohort replication.
- **Next step:** Confirm INHBB protein and cellular localization by immunohistochemistry or spatial transcriptomics, stratifying tumor cells, fibroblasts, and other stromal compartments; test INHBB perturbation in colorectal cancer organoids with stromal co-culture.
- **Status:** **Supported hypothesis**, not established causality.

### 2. Test whether epithelial differentiation is a prognostic state rather than a confounder  
**Classification:** Biomarker

- **Why prioritize:** CDX2, MYO5B, RAB11FIP4, LGALS4, and CDX1 collectively point toward epithelial identity, with CDX2, MYO5B, and RAB11FIP4 meeting FDR ≤ 0.05.
- **Current dataset evidence:** Protective HRs, particularly CDX2 HR 0.7478 and MYO5B HR 0.7483.
- **External evidence:** PMID **30631044** supports a tumor-suppressive role for CDX2 in colon cancer models. This does not demonstrate prognostic performance in an independent cohort.
- **Next step:** Construct a prespecified epithelial-differentiation score and evaluate it in an independent colorectal cancer cohort using multivariable Cox models adjusted for stage, grade, MSI status, treatment, age, and sex. Validate protein-level associations.
- **Status:** **Supported hypothesis** for prognostic biomarker development.

### 3. Validate the mitochondrial/intermediary-metabolism signature  
**Classification:** Mechanistic hypothesis

- **Why prioritize:** ATP23 and NDUFA9 are among the most statistically significant protective-associated genes, and several additional metabolic genes show concordant HR < 1.
- **Current dataset evidence:** ATP23 HR 0.6885, FDR 0.00664; NDUFA9 HR 0.6886, FDR 0.00865; concordant protective associations for GLYCTK, MCCC2, ILVBL, CS, and COA3.
- **External evidence:** Reactome and gene annotations support mitochondrial and metabolic roles; STRING provides limited network context. These are annotations, not functional validation.
- **Next step:** Measure respiratory capacity, oxygen consumption, TCA intermediates, and mitochondrial abundance in tumor organoids or freshly isolated tumor cells, while controlling for hypoxia and cell composition.
- **Status:** **Supported hypothesis**, with causal direction unresolved.

### 4. Evaluate NT5E-associated immune suppression and response biology  
**Classification:** Biomarker

- **Why prioritize:** NT5E is risk-associated at HR 1.313 and FDR 0.03939, and CD73/NT5E has broad cancer-prognostic literature support.
- **Current dataset evidence:** Direct OS association plus a mixed immune-associated pattern involving LGALS9, TAPBPL, CCL15, and CCDC134.
- **External evidence:** PMID **36480312** supports CD73 as a potential prognostic and immunotherapy biomarker across cancers. PMID **42363170** supports the broader relevance of immunotherapy testing in colorectal-cancer models, but neither record establishes that NT5E blockade is effective for these patients.
- **Next step:** Measure NT5E/CD73 protein, extracellular adenosine-related markers, T-cell infiltration, and spatial proximity to immune cells; test association with MSI, immune checkpoint status, and treatment response.
- **Status:** **Exploratory hypothesis** because cell source and treatment context are unknown.

### 5. Resolve tumor purity and cellular-composition effects  
**Classification:** Confounding or composition check

- **Why prioritize:** ECM, epithelial, metabolic, and immune signals can all arise from different proportions of malignant, stromal, immune, endothelial, or normal epithelial cells.
- **Current dataset evidence:** The coexistence of risk-associated matrix genes, protective epithelial genes, and mixed immune genes is compatible with variation in tumor composition.
- **External evidence:** Tissue-expression and pathway annotations support cell-type plausibility, but they do not distinguish composition from tumor-cell-intrinsic regulation.
- **Next step:** Apply bulk RNA-seq deconvolution or single-cell/spatial profiling, estimate tumor purity, and repeat survival models with purity and immune/stromal scores as covariates. Reassess whether INHBB, NT5E, CDX2, and the metabolic module retain independent prognostic effects.
- **Status:** **Established methodological priority**, while the specific confounding explanation remains a hypothesis.

## 5. Evidence grounding and conflicts

- **Direct cohort evidence:** The HR, P value, FDR, and direction in the supplied table are the only direct statistical evidence. The strongest individual signals include INHBB, SCARA3, MIR31HG, ATP23, ZEB1-AS1, DCBLD2, NDUFA9, and TPM4.
- **Pathway/ontology evidence:** The retrieved annotations include regulation of phospholipase C activity, microtubule anchoring at the microtubule-organizing center, regulation of T-cell migration, glyoxylate and dicarboxylate metabolism, and cancer-related KEGG annotations. These support plausibility but are not newly computed enrichment results.
- **Network evidence:** The batch reports 42 STRING edges and selected relationships such as CS–ACSS2, COA3–ILVBL, and LRCH1/LRCH3 connections to DOCK-family proteins. STRING edges may represent physical interaction, functional association, co-expression, literature transfer, or prediction depending on the record; they should not automatically be called direct binding.
- **Literature evidence:** PMID **41992239** supports INHBB relevance in colorectal cancer; PMID **30631044** supports CDX2 biology in colon cancer; PMID **36480312** supports broad NT5E prognostic relevance; PMID **17135288** provides ATP23-related mitochondrial interaction context; PMID **34342374** supports a prognostic role for LINC00852 in lung cancer, but that disease context is not directly transferable to colorectal cancer.
- **Independent validation:** No external cohort HR, P value, FDR, endpoint, or model was supplied. Therefore, **external statistical validation was not performed**, and no candidate can be called replicated or clinically validated.
- **Conflicts and annotation limitations:** Duplicate probes and direction conflicts complicate DCBLD2 and other grouped entries. Several identifiers are probes, lncRNA/gene combinations, or multi-feature labels, so gene-level biological interpretation may be uncertain. External source coverage is incomplete and sources may share publications or prediction models; record counts do not measure evidence strength.

## 6. Major limitations and alternative explanations

1. **Tumor purity and cellular composition:** Risk-associated ECM genes may reflect fibroblasts or vascular cells, while CDX2, MYO5B, and LGALS4 may reflect differentiated epithelium or contaminating normal mucosa. Deconvolution, pathology review, and spatial or single-cell assays can distinguish these possibilities.

2. **Stage, grade, and disease severity:** A prognostic signature may capture advanced stage rather than an independent biological mechanism. Multivariable analyses should adjust for TNM stage, grade, metastasis, MSI status, molecular subtype, and treatment.

3. **Treatment exposure and clinical heterogeneity:** OS associations can differ by surgery, chemotherapy, radiotherapy, targeted therapy, and immunotherapy. Treatment-stratified and interaction analyses are needed.

4. **Probe duplication and annotation ambiguity:** Multiple probes can inflate apparent support or produce direction conflicts. Probe sequences, gene annotations, batch effects, and transcript isoforms should be reviewed before constructing a gene score.

5. **Association-versus-causation and broad pathway interpretation:** HRs identify prognostic associations, not causal drivers. The retrieved pathway and literature evidence can explain plausibility but cannot replace perturbation experiments or independent survival statistics. In particular, the presence of a therapeutic record or a druggable pathway would not by itself establish therapeutic effectiveness.

Overall, the most reproducible-looking hypotheses are an **INHBB-associated invasive/stromal risk state**, a **CDX2-centered epithelial differentiation state associated with lower hazard**, and a **mitochondrial/intermediary-metabolism state associated with lower hazard**, while the NT5E immune axis and FGF19–AKT3 signaling require stronger cellular and independent-cohort validation.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=116, external claims checked=0, external mismatches=0, status=needs review.

Answer model API: OpenAI / gpt-5.6-luna

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 86/100 selected items (records returned); cbioportal 78/100 selected items (records returned); chembl 14/100 selected items (partially returned; some queries failed); civic 7/100 selected items (records returned); clinicaltrials 32/100 selected items (records returned); clinvar 83/100 selected items (records returned); ensembl 41/100 selected items (partially returned; some queries failed); europepmc 866 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 81/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 75/100 selected items (records returned); humanbase 78/100 selected items (records returned); intact 78/100 selected items (records returned); mygene 86/100 selected items (records returned); omnipath 32/100 selected items (records returned); opentargets 40/100 selected items (partially returned; some queries failed); pubmed 699 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 79/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 80/100 selected items (records returned)
Local databases: gutmgene 0/100 selected items (reachable but no records for this batch); hmdb 25/100 selected items (records returned); string 73/100 selected items (records returned); trrust 14/100 selected items (records returned)
