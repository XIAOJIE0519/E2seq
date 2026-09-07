# colorectal cancer - deepseek-v4-flash

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
- Model API: DeepSeek / deepseek-v4-flash
- Message SHA-256: dfb8fe82357dbea353d34030380d74028b528c91505f5793c7261ee9e4376675
- Response HTTP status: 200
- Prompt tokens: 46617
- Completion tokens: 18049
- Reasoning tokens: 0
- Total tokens: 64666
- API requests reported: 4
- Elapsed seconds: 106.637
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 1848.064
- Question handoff seconds: 1861.273
- Final benchmark system: E2seq; file rank 5/5; original repeat 7; model vendor: DeepSeek

---
# Multidimensional Interpretation of Prognostic Transcriptomic Results in Colorectal Cancer (OS)

## 1. Overall Biological Interpretation

The prognostic transcriptomic profile of colorectal cancer (CRC) tumor tissue reveals a striking dichotomy between two opposing gene expression programs associated with overall survival. On one side, a cluster of risk-associated genes (HR > 1) points toward **mesenchymal/stromal-like remodeling, TGF-β/BMP signaling, and invasive cellular phenotypes** — exemplified by INHBB, ZEB1-AS1, DCBLD2, TPM4, ITGBL1, MSLN, and NT5E. On the other side, a protective-associated cluster (HR < 1) is enriched for **mitochondrial function, oxidative metabolism, and intestinal epithelial differentiation markers** — including ATP5B, ATP5G1, NDUFA9, CS, CDX2, CDX1, and LGALS4. This pattern suggests that tumors with preserved epithelial differentiation and oxidative metabolic capacity have better outcomes, while those shifting toward mesenchymal/invasive programs and altered metabolism face worse prognosis. Notably, the protective cluster also includes several components of mitochondrial protein import and assembly (TIMM13, COA3, ATP23), reinforcing a coherent mitochondrial/metabolic survival signature.

The risk-associated genes collectively implicate **extracellular matrix remodeling, TGF-β superfamily signaling, and epithelial-mesenchymal transition (EMT)** — a program strongly associated with aggressive CRC biology. The protective genes, in contrast, support a **differentiation- and metabolism-preserving phenotype** consistent with more indolent disease.

---

## 2. Core Biological Programs

### Program 1: TGF-β/BMP Signaling and Mesenchymal Transition
- **Prognostic association:** Risk-associated (worse OS)
- **Major supporting genes:** INHBB (HR=1.433), ZEB1-AS1 (HR=1.372), DCBLD2 (HR=1.408), TPM4 (HR=1.364), ITGBL1 (HR=1.299), MSLN (HR=1.313), NT5E (HR=1.313), GADD45B (HR=1.324)
- **Pathway:** KEGG "TGF-beta signaling pathway"; Hallmark "Epithelial Mesenchymal Transition"
- **Explanation:** INHBB encodes the inhibin βB subunit that dimerizes to form activin B, a TGF-β superfamily ligand with established pro-invasive roles in CRC. ZEB1-AS1 is an antisense transcript that stabilizes ZEB1, a master EMT transcription factor. DCBLD2, TPM4, and ITGBL1 are all associated with mesenchymal/invasive phenotypes and ECM remodeling. MSLN (mesothelin) is a well-characterized tumor-associated antigen linked to aggressive CRC. NT5E/CD73 has documented roles in immunosuppression and metastasis.
- **Evidence strength:** Moderate. Multiple independent genes converge on this program with strong individual statistics (FDR < 0.05 for most). However, no formal pathway enrichment was computed for this cohort, and the program is inferred from gene-level annotations.
- **Limitations:** ZEB1-AS1's role is inferred from its well-known relationship to ZEB1; DCBLD2 has direction-conflict rows in the ledger, adding uncertainty.

### Program 2: Mitochondrial Function and Oxidative Metabolism
- **Prognostic association:** Protective-associated (better OS)
- **Major supporting genes:** ATP5B (HR=0.748), ATP5G1 (HR=0.747), NDUFA9 (HR=0.689), CS (HR=0.754), TIMM13 (HR=0.751), COA3 (HR=0.744), ATP23 (HR=0.688)
- **Pathway:** KEGG "Oxidative phosphorylation"; GO "Mitochondrial respiratory chain complex assembly"
- **Explanation:** The coordinated protective association of multiple mitochondrial components — from complex I (NDUFA9), complex V (ATP5B, ATP5G1), TCA cycle (CS), and mitochondrial import/assembly machinery (TIMM13, COA3, ATP23) — suggests that preserved mitochondrial function is a marker of less aggressive disease. This is consistent with the "Warburg effect" paradigm where aggressive tumors shift away from oxidative phosphorylation toward glycolysis.
- **Evidence strength:** Moderate-to-strong. The convergence of six independent mitochondrial genes all with HR < 1 is a coherent and biologically interpretable signal.
- **Limitations:** The effect sizes are modest (HR 0.69–0.75). Tumor purity could confound this signal if stromal content dilutes epithelial mitochondrial gene expression.

### Program 3: Intestinal Epithelial Differentiation
- **Prognostic association:** Protective-associated (better OS)
- **Major supporting genes:** CDX2 (HR=0.748), CDX1 (HR=0.781), LGALS4 (HR=0.771), MYB (HR=0.771), PRR15L (HR=0.801)
- **Pathway:** GO "Intestinal epithelial cell differentiation"; KEGG "Gastric cancer" (retrieved module context)
- **Explanation:** CDX2 and CDX1 are master transcription factors for intestinal differentiation and are well-established tumor suppressors in CRC. CDX2 loss is a recognized marker of poor prognosis and is associated with the consensus molecular subtype 4 (mesenchymal) in CRC. LGALS4 (galectin-4) is a differentiation marker of intestinal epithelium. MYB has context-dependent roles but is generally associated with differentiated intestinal epithelium.
- **Evidence strength:** Moderate. The combination of CDX2/CDX1 with LGALS4 provides a coherent differentiation signature, and CDX2's protective role is supported by extensive literature (e.g., PMID 30631044 showing CDX2 suppresses Wnt/β-catenin signaling).
- **Limitations:** MYB's role is complex and tissue-dependent; PRR15L's function is poorly characterized.

### Program 4: Cell Migration, Cytoskeletal Dynamics, and Vesicular Trafficking
- **Prognostic association:** Mixed (risk-associated: NIN, MAP1B, BICD1; protective-associated: MYO5B, RAB11FIP4, DNPEP)
- **Major supporting genes:** NIN (HR=1.345), MAP1B (HR=1.327), BICD1 (HR=1.293), MYO5B (HR=0.748), RAB11FIP4 (HR=0.736), DNPEP (HR=0.728)
- **Pathway:** GO "Microtubule anchoring at microtubule organizing center"; GO "Regulation of cell migration"
- **Explanation:** The retrieved GO modules include "Microtubule Anchoring At Microtubule Organizing Center" (GO:0072393), which is directly relevant to NIN and BICD1 — both involved in microtubule organization and centrosome function. MAP1B stabilizes microtubules and promotes neuronal/axonal migration but is also implicated in cancer cell invasion. In contrast, MYO5B (myosin Vb) and RAB11FIP4 are involved in apical trafficking and recycling endosome function, important for maintaining epithelial polarity. The opposing directions suggest that cytoskeletal reorganization favoring invasive migration (risk) versus maintenance of epithelial polarity (protective) is prognostically relevant.
- **Evidence strength:** Weak-to-moderate. The direction split within this program complicates interpretation, and the biological coherence across the mixed group is less tight than Programs 1–3.
- **Limitations:** The program may be over-aggregated; the risk and protective arms may represent distinct biological processes rather than a single program.

### Program 5: Amino Acid and One-Carbon Metabolism
- **Prognostic association:** Protective-associated (better OS)
- **Major supporting genes:** ASL (HR=0.739), GLYCTK (HR=0.709), ILVBL (HR=0.725), MCCC2 (HR=0.739), OGDHL (HR=0.686)
- **Pathway:** KEGG "Glycine, serine and threonine metabolism"; KEGG "Glyoxylate and dicarboxylate metabolism"
- **Explanation:** ASL (argininosuccinate lyase, urea cycle), GLYCTK (glycerate kinase, serine metabolism), ILVBL (acetolactate synthase-like), MCCC2 (methylcrotonoyl-CoA carboxylase, leucine catabolism), and OGDHL (oxoglutarate dehydrogenase-like) all participate in amino acid catabolism feeding into the TCA cycle. Their coordinated protective association suggests that preserved amino acid oxidative metabolism is favorable, consistent with Program 2's mitochondrial theme.
- **Evidence strength:** Weak-to-moderate. The individual genes are statistically significant, and the metabolic coherence is plausible, but the connection to CRC prognosis specifically is less well established in the literature.
- **Limitations:** OGDHL has the strongest HR (0.686) but FDR = 0.074, above the 0.05 threshold — this gene should be interpreted cautiously.

---

## 3. Key Genes and Interaction Modules

### 1. INHBB (HR=1.433, FDR=0.0011)
- **Direction:** Strongest risk-associated gene in the cohort.
- **Role:** TGF-β superfamily ligand (activin B); drives EMT and malignant phenotypes.
- **Evidence:** Direct input statistic; literature (Europe PMC 41992239: "High INHBB expression in colorectal cancer is associated with poor prognosis and drives malignant phenotypes in tumor cells").
- **Relationship to other genes:** Pathway co-membership with the TGF-β/EMT program (ZEB1-AS1, DCBLD2). No direct physical interaction evidence in the supplied records.
- **Status:** Supported hypothesis for a prognostic biomarker and potential therapeutic target.

### 2. CDX2 (HR=0.748, FDR=0.036)
- **Direction:** Protective-associated.
- **Role:** Master intestinal differentiation transcription factor; suppresses Wnt/β-catenin signaling (PMID 30631044).
- **Evidence:** Direct input statistic; extensive published literature supporting tumor-suppressive function in CRC.
- **Relationship to other genes:** Regulatory interaction — CDX2 transactivates GSK-3β and Axin2, suppressing Wnt signaling (literature-supported). Co-expression with CDX1 and LGALS4 in the differentiation program.
- **Status:** Established evidence for CDX2's tumor-suppressive role in CRC; supported hypothesis for its prognostic value in this cohort.

### 3. Mitochondrial module (ATP5B, ATP5G1, NDUFA9, CS, TIMM13, COA3, ATP23)
- **Direction:** All protective-associated (HR 0.69–0.75).
- **Role:** Oxidative phosphorylation, TCA cycle, mitochondrial protein import/assembly.
- **Evidence:** Direct input statistics; STRING network evidence connects COA3 to MT-CO1 (mitochondrial complex IV) and CS to ACSS2/ILVBL (metabolic co-membership).
- **Relationship type:** Pathway co-membership (oxidative phosphorylation); potential co-expression in tumor epithelium.
- **Status:** Supported hypothesis — preserved mitochondrial function associates with better OS; warrants validation as a metabolic subtype biomarker.

### 4. ZEB1-AS1 (HR=1.372, FDR=0.0086)
- **Direction:** Risk-associated.
- **Role:** Antisense lncRNA stabilizing ZEB1 mRNA; promotes EMT.
- **Evidence:** Direct input statistic; literature supports ZEB1-AS1 as an oncogenic lncRNA in multiple cancers.
- **Relationship to other genes:** Regulatory interaction with ZEB1 (post-transcriptional stabilization) — this is a literature-supported regulatory relationship, not a direct physical protein interaction.
- **Status:** Supported hypothesis.

### 5. NT5E/CD73 (HR=1.313, FDR=0.039)
- **Direction:** Risk-associated.
- **Role:** Ecto-5'-nucleotidase generating immunosuppressive adenosine; promotes metastasis.
- **Evidence:** Direct input statistic; literature (PMID 36480312: "CD73/NT5E is a Potential Biomarker for Cancer Prognosis and Immunotherapy for Multiple Types of Cancers").
- **Relationship to other genes:** Co-expression with the EMT/stromal program; functionally linked to immunosuppression in the tumor microenvironment.
- **Status:** Supported hypothesis; already a therapeutic target in clinical trials for other cancers (therapeutic evidence exists, but this does not establish efficacy in CRC).

### 6. MSLN (HR=1.313, FDR=0.045)
- **Direction:** Risk-associated.
- **Role:** Mesothelin, tumor-associated antigen; promotes invasion.
- **Evidence:** Direct input statistic; Europe PMC 42363170 describes mesothelin-targeted CAR-T cells in CRC organoids.
- **Relationship to other genes:** Pathway co-membership with the invasive/mesenchymal program.
- **Status:** Supported hypothesis as a biomarker; therapeutic targeting (CAR-T) is in preclinical development — the existence of a drug/CAR-T does not establish clinical efficacy.

### 7. MYB (HR=0.771, FDR=0.019)
- **Direction:** Protective-associated.
- **Role:** Transcription factor; STRING evidence shows interactions with CREBBP, EP300, CEBPB, KMT2A, GATA2 — all chromatin regulators/transcription factors.
- **Evidence:** Direct input statistic; STRING protein interaction network (high-confidence edges to CREBBP at 0.999, EP300 at 0.996).
- **Relationship to other genes:** Direct physical interaction with CREBBP/EP300 (STRING, high confidence); regulatory interaction with CEBPB and GATA2.
- **Status:** Supported hypothesis — MYB's protective association is notable but its role in CRC is context-dependent and requires validation.

### 8. GLYCTK (HR=0.709, FDR=0.020)
- **Direction:** Protective-associated.
- **Role:** Glycerate kinase; serine/glycine metabolism. STRING shows interactions with GRHPR (0.986), TKFC (0.970), ENO1/2/3 (0.94–0.95) — glycolytic enzymes.
- **Evidence:** Direct input statistic; STRING network evidence connecting to glycolysis enzymes suggests metabolic co-regulation.
- **Relationship to other genes:** Direct physical interaction with GRHPR and TKFC (STRING, high confidence); pathway co-membership with glycolysis (ENO1/2/3).
- **Status:** Supported hypothesis — warrants functional validation of its metabolic role in CRC.

### 9. LRCH3/LRCH1 module (LRCH3 HR=1.341; LRCH1 HR=1.337)
- **Direction:** Both risk-associated.
- **Role:** LRCH proteins interact with DOCK family guanine nucleotide exchange factors (STRING: DOCK6, DOCK7, DOCK8, LRCH4 connections).
- **Evidence:** Direct input statistics; STRING network evidence showing LRCH1/LRCH3 co-membership with DOCK6/7/8 and LRCH4.
- **Relationship to other genes:** Direct physical interaction with DOCK proteins (STRING); pathway co-membership in Rho/Rac signaling via DOCK-mediated GEF activity.
- **Status:** Exploratory hypothesis — the DOCK/LRCH module is a plausible risk-associated signaling axis but is poorly characterized in CRC.

### 10. AKT3 (HR=1.318, FDR=0.039)
- **Direction:** Risk-associated.
- **Role:** PI3K/AKT signaling; cell survival and proliferation.
- **Evidence:** Direct input statistic (7 rows in ledger, indicating multiple probes supporting the signal).
- **Relationship to other genes:** Pathway co-membership with PI3K/AKT signaling; the retrieved KEGG module includes "Melanoma" and "Gastric cancer" pathways, both of which involve AKT signaling.
- **Status:** Supported hypothesis — AKT3's role in cancer progression is well established, but its specific contribution to CRC prognosis in this cohort requires validation.

---

## 4. Validation Priorities

### Priority 1: INHBB/Activin B as a Prognostic Biomarker and Therapeutic Target
- **Classification:** Biomarker + Therapeutic target
- **Why:** Strongest risk-associated gene (HR=1.433, FDR=0.0011); literature directly links INHBB to poor CRC prognosis and malignant phenotypes.
- **Current dataset evidence:** Direct HR statistic with the lowest FDR in the cohort.
- **External evidence:** Europe PMC 41992239 supports INHBB's pro-tumorigenic role in CRC.
- **Next step:** Immunohistochemistry on an independent CRC cohort to confirm protein-level association with OS; functional knockdown/overexpression studies in CRC cell lines to test activin B's role in invasion.
- **Conclusion status:** Supported hypothesis (prognostic); exploratory hypothesis (therapeutic target — no efficacy data in CRC).

### Priority 2: Mitochondrial Program as a Metabolic Subtype Marker
- **Classification:** Biomarker
- **Why:** Seven independent mitochondrial genes show coordinated protective association; this may define a clinically relevant metabolic subtype.
- **Current dataset evidence:** ATP5B, ATP5G1, NDUFA9, CS, TIMM13, COA3, ATP23 all HR < 1.
- **External evidence:** STRING network connects COA3 to MT-CO1; literature supports oxidative phosphorylation preservation as favorable in some cancers.
- **Next step:** Validate using a composite mitochondrial score in an independent CRC cohort; correlate with CMS classification (mitochondrial genes are typically low in CMS4/mesenchymal subtype).
- **Conclusion status:** Supported hypothesis.

### Priority 3: CDX2/CDX1 Differentiation Axis and EMT Status
- **Classification:** Mechanistic hypothesis
- **Why:** CDX2 is a well-established tumor suppressor; its loss defines aggressive CRC. The opposing directions of differentiation markers (protective) and EMT markers (risk) suggest a mechanistic axis.
- **Current dataset evidence:** CDX2 (HR=0.748), CDX1 (HR=0.781) protective; ZEB1-AS1, INHBB risk.
- **External evidence:** PMID 30631044 (CDX2 suppresses Wnt/β-catenin); extensive CMS literature.
- **Next step:** Test whether CDX2 loss correlates with ZEB1-AS1/INHBB upregulation in the same tumors; chromatin immunoprecipitation to test direct regulatory relationships.
- **Conclusion status:** Established evidence for CDX2's tumor-suppressive function; the specific antagonistic axis with the EMT program in this cohort is a supported hypothesis.

### Priority 4: Tumor Purity and Stromal Content Confounding Check
- **Classification:** Confounding or composition check
- **Why:** Many risk-associated genes (ITGBL1, DCBLD2, MSLN, NT5E) are expressed in stromal or immune cells, not just tumor epithelium. Low tumor purity could drive the apparent risk association.
- **Current dataset evidence:** The risk-associated gene set overlaps with known stromal/mesenchymal markers.
- **External evidence:** Stromal genes are consistently enriched in CMS4 CRC; tumor purity varies widely across platforms.
- **Next step:** Estimate tumor purity (e.g., ESTIMATE, or histology review); stratify analysis by purity; perform single-cell or spatial transcriptomics to localize expression of INHBB, ITGBL1, DCBLD2.
- **Conclusion status:** This is a necessary quality check, not a biological conclusion.

### Priority 5: Independent Cohort Replication of the Risk-Associated EMT Program
- **Classification:** Interaction / network hypothesis
- **Why:** The EMT/proliferation axis is the most clinically actionable signal, but no external cohort statistic was provided.
- **Current dataset evidence:** Multiple risk-associated genes with FDR < 0.05.
- **External evidence:** EMT and TGF-β signaling are well-established in CRC aggressiveness; however, **external statistical validation was not performed** — no independent cohort HR/FDR values were supplied.
- **Next step:** Test the composite EMT risk score in a publicly available CRC cohort (e.g., TCGA-COAD/READ, GSE39582) with survival data.
- **Conclusion status:** Supported hypothesis for the biological program; the prognostic value in independent cohorts remains unvalidated.

---

## 5. Evidence Grounding Summary

| Evidence Category | Contribution | Independence Assessment |
|---|---|---|
| **Direct input statistics** | All HR/P/FDR values; primary evidence for effect direction and significance | Authoritative for this cohort |
| **Pathway/ontology (GO, KEGG, Reactome)** | Contextual support for mitochondrial, metabolic, and differentiation programs | Partially independent; annotations derive from curated databases that may share literature sources |
| **Protein interaction (STRING)** | Supports GLYCTK-GRHPR/TKFC/ENO, MYB-CREBBP/EP300, LRCH-DOCK connections | STRING integrates multiple evidence types; high-confidence edges are informative but not proof of direct physical binding |
| **Disease-association (literature)** | INHBB (Europe PMC 41992239), NT5E (PMID 36480312), CDX2 (PMID 30631044) | Independent literature support for specific genes; does not validate the full cohort signal |
| **Expression/tissue (GTEx, HPA)** | Contextual; supports tissue relevance but not prognostic direction | Not used to establish prognosis |
| **Drug/therapeutic (ChEMBL, ClinicalTrials)** | MSLN CAR-T, NT5E/CD73 inhibitors exist | Presence of a drug does not establish efficacy in CRC; therapeutic claims are exploratory |
| **Independent cohort replication** | **Not available** — no external cohort statistic supplied | External statistical validation was not performed |

**Key independence caveat:** Pathway annotations, STRING interactions, and literature records may share underlying publications or prediction models. The convergence of multiple evidence types for INHBB, CDX2, and the mitochondrial module is suggestive but does not constitute independent replication.

---

## 6. Limitations and Alternative Explanations

### 1. Tumor Purity and Cell Composition
The risk-associated genes (ITGBL1, DCBLD2, MSLN, NT5E, SCARA3) are enriched in stromal/immune cells. If low-purity tumors are overrepresented in the poor-prognosis group, the association may reflect stromal content rather than tumor-intrinsic biology. **Investigation:** ESTIMATE purity scores, histology review, single-cell RNA-seq to localize expression.

### 2. Platform/Probe Artifacts
The dataset contains 53 duplicated genes/probes and several direction-conflict rows (DCBLD2, BCL2L14, LOC101928747|RBMX|SNORD61). Probe-level inconsistencies could indicate cross-hybridization or annotation errors. **Investigation:** Verify probe mapping; collapse to gene level with consistent direction; sensitivity analysis excluding direction-conflict genes.

### 3. Disease Severity and Stage Confounding
HR values are unadjusted for stage in the provided table. If high-stage tumors preferentially express the risk-associated genes, the prognostic association may reflect stage rather than an independent biological program. **Investigation:** Multivariable Cox regression including stage, age, sex; stratified analysis by stage.

### 4. Association vs. Causation
All findings are correlational. The protective association of mitochondrial genes could reflect a general "healthier" tumor state rather than a causal metabolic dependency. **Investigation:** Functional perturbation studies (e.g., mitochondrial complex inhibition in CRC organoids) to test causal contribution.

### 5. Broad/Nonspecific Pathway Enrichment
The retrieved GO modules (e.g., "protein binding," "cytosol") are too broad to be informative. The specific programs I identified (TGF-β/EMT, mitochondrial, differentiation) are inferred from gene-level annotations and literature, not from formal enrichment statistics computed on this cohort. **Investigation:** Run GSEA or over-representation analysis with a proper background and multiple-testing correction on the full gene list.

---

## Concluding Statement

The current data support a coherent model in which CRC tumors with preserved intestinal differentiation (CDX2/CDX1) and mitochondrial oxidative metabolism exhibit better overall survival, while those engaging TGF-β/EMT programs (INHBB, ZEB1-AS1, DCBLD2) and stromal/mesenchymal remodeling face worse outcomes — but these conclusions rest on the uploaded cohort statistics alone, external statistical validation was not performed, and tumor purity, stage, and probe-level inconsistencies must be addressed before the risk-associated EMT program can be considered a validated prognostic or therapeutic signal.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=54, external claims checked=0, external mismatches=0, status=needs review.

Answer model API: deepseek / deepseek-v4-flash.

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 86/100 selected items (records returned); cbioportal 78/100 selected items (records returned); chembl 14/100 selected items (partially returned; some queries failed); civic 7/100 selected items (records returned); clinicaltrials 32/100 selected items (records returned); clinvar 83/100 selected items (records returned); ensembl 41/100 selected items (partially returned; some queries failed); europepmc 866 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 81/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 75/100 selected items (records returned); humanbase 78/100 selected items (records returned); intact 78/100 selected items (records returned); mygene 86/100 selected items (records returned); omnipath 32/100 selected items (records returned); opentargets 40/100 selected items (partially returned; some queries failed); pubmed 699 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 79/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 80/100 selected items (records returned)
Local databases: gutmgene 0/100 selected items (reachable but no records for this batch); hmdb 25/100 selected items (records returned); string 73/100 selected items (records returned); trrust 14/100 selected items (records returned)
