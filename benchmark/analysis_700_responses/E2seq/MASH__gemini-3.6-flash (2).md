# metabolic dysfunction-associated steatohepatitis (MASH) - gemini-3.6-flash

- Benchmark system: E2seq + Agent RAG
- Repeat: 2
- Task type: DISEASE-STATE
- Tissue / sample source: liver tissue
- Comparison or endpoint: MASH/NASH versus healthy control
- Answer input cohort: Discovery/Core only
- Selected items: 100
- Input fields: gene name, effect size (log2FC/HR), P value, FDR
- E2seq Agent RAG: enabled
- Conversation memory: disabled
- Thinking mode: disabled
- Held-out validation data in prompt/RAG: no
- Model API: Google Gemini / gemini-3.6-flash
- Message SHA-256: f634f84e95c290ce4195eb13604b114b4c86ce8adb76238e59c436c955ac43b9
- Response HTTP status: 200
- Prompt tokens: 39956
- Completion tokens: 32423
- Reasoning tokens: 19366
- Total tokens: 72379
- API requests reported: 2
- Elapsed seconds: 56.858
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 1019.869
- Question handoff seconds: 1032.938
- Final benchmark system: E2seq; file rank 2/5; original repeat 2; model vendor: Google Gemini

---
### 1. Overall Biological Interpretation

The differential expression profile comparing liver tissue from patients with metabolic dysfunction-associated steatohepatitis (MASH) to healthy controls reveals a pronounced transcriptomic reorganization centered on hepatic immune cell remodeling, vascular endothelium alterations, pro-inflammatory signaling, and metabolic adaptation. 

A central feature of this dataset is the prominent inverse shift in macrophage transcriptional signatures: homeostatic resident Kupffer cell markers (e.g., **TIMD4**, **MARCO**, **LYVE1**, **SPIC**, **CD163**, **CD5L**, **MRC1**) are systematically downregulated, whereas markers associated with lipid-associated macrophages (LAMs), dendritic cell recruitment, and ubiquitin-mediated protein degradation (e.g., **TREM2**, **FABP5**, **UBD**, **CAPG**) are strongly upregulated. Concurrently, liver tissue exhibits elevated pro-inflammatory chemokine and tissue-stress signaling (**CXCL10**, **TNFRSF12A**, **TP53I3**, **DUSP8**), alongside widespread downregulation of plasma membrane adhesion molecules and endothelial structural markers (**PCDH20**, **VCAM1**, **CDH5**, **CDH23**, **TINAGL1**). Metabolic pathways display shifts in one-carbon folate metabolism and transsulfuration (**MTHFD1L** upregulated; **CBS** downregulated).

Because external statistical validation was not performed on an independent replication cohort within this study, these findings represent within-cohort transcriptomic discoveries grounded by external functional annotations, literature, and interaction databases.

---

### 2. Core Biological Programs

#### Program 1: Lipid-Associated Macrophage (LAM) Polarization and Monocyte Activation
* **Direction:** Upregulated
* **Major Supporting Genes:** `TREM2` (log2FC = 4.911, FDR = 3.899e-09), `UBD` (log2FC = 4.151, FDR = 1.325e-10), `FABP5` (log2FC = 2.849, FDR = 4.938e-08), `CAPG` (log2FC = 2.567, FDR = 3.116e-07).
* **Standardized Pathway:** GO:0006954 (inflammatory response) / Reactome R-HSA-9680350 (Signaling by CSF1/TREM2 pathways in myeloid cells).
* **Biological Explanation:** Lipotoxic stress in MASH triggers the expansion of specialized lipid-associated macrophages (LAMs). Co-induction of `TREM2` (a key receptor for lipid debris and apoptotic cells) alongside `FABP5` (a fatty acid-binding chaperone), `CAPG` (an actin-capping protein driving macrophage motility), and `UBD` (FAT10, involved in ubiquitin-like protein targeting and inflammatory response) reflects active recruitment and metabolic adaptation of monocyte-derived macrophages.
* **Evidence & Limitations:** High statistical significance and magnitude within the dataset; supported by single-cell literature on liver LAMs. *Limitation:* Bulk tissue transcriptomics averages signal across all cell types, making it impossible to separate changes in cellular abundance from per-cell transcriptional activation without cell sorting or single-cell profiling. External statistical validation was not performed.

#### Program 2: Loss / Depletion of Homeostatic Resident Kupffer Cell Signature
* **Direction:** Downregulated
* **Major Supporting Genes:** `TIMD4` (log2FC = -4.282, FDR = 1.502e-08), `MARCO` (log2FC = -2.844, FDR = 3.464e-10), `LYVE1` (log2FC = -2.730, FDR = 5.223e-09), `SPIC` (log2FC = -2.616, FDR = 1.341e-08), `CD163` (log2FC = -2.517, FDR = 3.117e-09), `CD5L` (log2FC = -2.899, FDR = 8.311e-08), `MRC1` (log2FC = -2.102, FDR = 1.877e-08).
* **Standardized Pathway:** Reactome: Scavenger receptor pathway / GO:0002437 (immunoglobulin mediated immune response).
* **Biological Explanation:** Native embryonically derived Kupffer cells express specific surface scavenger receptors (`TIMD4`, `MARCO`, `CD163`, `MRC1`), transcription factors (`SPIC`), and secreted regulators (`CD5L`). Their broad, concordant downregulation indicates either the loss of resident Kupffer cells via apoptosis/necrosis or their phenotypic replacement by recruited monocyte-derived cells during chronic liver inflammation.
* **Evidence & Limitations:** Strongly supported by multiple highly specific lineage markers showing concurrent downregulation. *Limitation:* Transcriptomic suppression alone cannot distinguish physical cell loss from transcriptional silencing. External statistical validation was not performed.

#### Program 3: Pro-Inflammatory Chemokine and Cytokine Receptor Stress Signaling
* **Direction:** Upregulated
* **Major Supporting Genes:** `CXCL10` (log2FC = 3.463, FDR = 1.183e-07), `TNFRSF12A` (log2FC = 3.271, FDR = 1.334e-07), `TP53I3` (log2FC = 3.261, FDR = 2.690e-10), `DUSP8` (log2FC = 3.494, FDR = 1.176e-08).
* **Standardized Pathway:** KEGG: Chemokine signaling pathway / Reactome: Cytokine Signaling in Immune system (R-HSA-1280215).
* **Biological Explanation:** Elevated levels of `CXCL10` (a major CXCR3-activating chemokine recruiting T cells and NK cells) together with `TNFRSF12A` (Fn14, receptor for TWEAK involved in liver injury, progenitor cell expansion, and inflammation) point to sustained active tissue injury and leukocyte recruitment. `TP53I3` and `DUSP8` further reflect intracellular cellular stress responses and MAP kinase pathway feedback regulation.
* **Evidence & Limitations:** Strong effect sizes and high statistical significance. *Limitation:* The specific cell types producing `CXCL10` and expressing `TNFRSF12A` (e.g., hepatocytes vs. endothelial cells vs. macrophages) cannot be resolved from bulk RNA-seq alone. External statistical validation was not performed.

#### Program 4: Downregulation of Hepatic Sinusoidal and Cell-Cell Adhesion Integrity
* **Direction:** Downregulated
* **Major Supporting Genes:** `PCDH20` (log2FC = -4.593, FDR = 1.474e-08), `VCAM1` (log2FC = -2.378, FDR = 4.971e-10), `CDH5` (log2FC = -1.376, FDR = 5.561e-07), `CDH23` (log2FC = -1.904, FDR = 1.900e-08), `TINAGL1` (log2FC = -1.777, FDR = 4.721e-08).
* **Standardized Pathway:** GO:0098742 (Cell-Cell Adhesion Via Plasma-Membrane Adhesion Molecules) / Reactome: Cell junction organization (R-HSA-446728).
* **Biological Explanation:** Sinusoidal endothelial cells maintain hepatic vascular integrity and blood-tissue exchange. Downregulation of key adhesion and junctional components (`CDH5` [VE-cadherin], `PCDH20`, `CDH23`, `VCAM1`, `TINAGL1`) suggests structural disruption of hepatic sinusoids, endothelial capillarization, or altered cell-matrix attachment in inflamed liver tissue.
* **Evidence & Limitations:** Supported by statistical enrichment in GO:0098742 and network interactions (CDH5-CTNNB1). *Limitation:* Morphological or functional microvascular changes require tissue imaging to confirm physiological barrier disruption. External statistical validation was not performed.

#### Program 5: One-Carbon Folate and Transsulfuration Metabolic Reprogramming
* **Direction:** Mixed (`MTHFD1L` upregulated; `CBS` downregulated)
* **Major Supporting Genes:** `MTHFD1L` (log2FC = 1.717, FDR = 1.930e-07), `CBS` (log2FC = -1.254, FDR = 1.804e-07), `FABP5` (log2FC = 2.849, FDR = 4.938e-08), `CYCS` (log2FC = 1.565, FDR = 1.124e-08), `MANF` (log2FC = 1.854, FDR = 6.054e-07).
* **Standardized Pathway:** KEGG: One carbon pool by folate / Reactome: Mitochondrial biogenesis & ER stress response.
* **Biological Explanation:** Mitochondrial `MTHFD1L` catalyzes formate production in one-carbon folate metabolism, supporting nucleotide synthesis and NADPH generation, while cytosolic `CBS` (cystathionine beta-synthase) controls transsulfuration toward glutathione synthesis. Upregulation of `MTHFD1L` alongside downregulation of `CBS` indicates metabolic remodeling under oxidative stress, accompanied by ER stress (`MANF`) and mitochondrial electron transport chain involvement (`CYCS`).
* **Evidence & Limitations:** Biologically consistent with steatohepatitis lipotoxicity models. *Limitation:* Transcriptional alterations in metabolic enzymes do not guarantee corresponding changes in metabolite flux without metabolomic validation. External statistical validation was not performed.

---

### 3. Key Genes and Interaction Modules

1. **TREM2**
   * **Statistical Metrics:** Log2FC = 4.911, P = 5.661e-12, FDR = 3.899e-09 (Upregulated).
   * **Role:** Lipid-sensing receptor driving lipid-associated macrophage differentiation and debris clearance.
   * **Relationship Type:** Functional co-expression and pathway co-membership with `CSF1R` and `FABP5` (myeloid lipid module); indirect signaling crosstalk in OmniPath/Reactome.
2. **TIMD4**
   * **Statistical Metrics:** Log2FC = -4.282, P = 3.570e-11, FDR = 1.502e-08 (Downregulated).
   * **Role:** Phosphatidylserine receptor essential for apoptotic cell clearance by resident Kupffer cells.
   * **Relationship Type:** Co-expressed lineage marker with `MARCO` and `CD163` (homeostatic macrophage module); pathway co-membership, indirect relationship.
3. **UBD (Ubiquitin D / FAT10)**
   * **Statistical Metrics:** Log2FC = 4.151, P = 5.248e-14, FDR = 1.325e-10 (Upregulated).
   * **Role:** Inducible ubiquitin-like modifier marked in Mallory-Denk bodies and inflammatory liver injury.
   * **Relationship Type:** Regulatory co-membership and co-expression with pro-inflammatory mediators (`CXCL10`, `TNFRSF12A`) involved in NF-kB signaling and proteasomal degradation.
4. **CXCL10**
   * **Statistical Metrics:** Log2FC = 3.463, P = 4.686e-10, FDR = 1.183e-07 (Upregulated).
   * **Role:** Pro-inflammatory chemokine directing CXCR3-positive lymphocyte infiltration into steatotic liver.
   * **Relationship Type:** Secreted signaling ligand; regulatory interaction with NF-kB transcriptional pathways; co-expressed with `TNFRSF12A`.
5. **TNFRSF12A (Fn14)**
   * **Statistical Metrics:** Log2FC = 3.271, P = 5.376e-10, FDR = 1.334e-07 (Upregulated).
   * **Role:** Receptor for TWEAK signaling, mediating hepatocellular damage, inflammation, and progenitor cell activation.
   * **Relationship Type:** Direct physical interaction with ligand TNFSF12 in Reactome; pathway co-membership with downstream NF-kB/MAPK cascades and co-expressed with `CXCL10`.
6. **PCDH20**
   * **Statistical Metrics:** Log2FC = -4.593, P = 3.309e-11, FDR = 1.474e-08 (Downregulated).
   * **Role:** Protocadherin family cell-cell adhesion molecule maintaining epithelial/endothelial structural integrity.
   * **Relationship Type:** Pathway co-membership (GO:0098742 cell-cell adhesion) and co-expression with vascular adhesion markers `CDH5` and `CDH23`.
7. **CD163**
   * **Statistical Metrics:** Log2FC = -2.517, P = 3.704e-12, FDR = 3.117e-09 (Downregulated).
   * **Role:** Endocytic scavenger receptor for hemoglobin-haptoglobin complexes on anti-inflammatory macrophages.
   * **Relationship Type:** Direct physical interaction / STRING network connection with `MRC1` (log2FC = -2.102) and `SIGLEC1` (log2FC = -2.118); co-expression within the homeostatic macrophage cluster.
8. **FOXM1**
   * **Statistical Metrics:** Log2FC = 2.144, P = 2.374e-09, FDR = 4.232e-07 (Upregulated).
   * **Role:** Master transcription factor governing cell cycle, DNA repair, and liver regenerative response.
   * **Relationship Type:** Direct regulatory interaction (transcription factor) targeting cell cycle genes; direct physical/STRING network node with `CTNNB1` (beta-catenin); pathway co-membership with Wnt signaling pathway components (`TCF7L1`, `CDH5`).
9. **FABP5**
   * **Statistical Metrics:** Log2FC = 2.849, P = 1.630e-10, FDR = 4.938e-08 (Upregulated).
   * **Role:** Fatty acid-binding protein facilitating cytosolic lipid transport and lipid mediator signaling.
   * **Relationship Type:** Functional co-expression and metabolic pathway co-membership with `TREM2` in lipid-loaded macrophages; indirect metabolic relationship.
10. **MTHFD1L**
    * **Statistical Metrics:** Log2FC = 1.717, P = 8.919e-10, FDR = 1.930e-07 (Upregulated).
    * **Role:** Mitochondrial C1-tetrahydrofolate synthase supporting one-carbon folate cycle flux.
    * **Relationship Type:** Metabolic pathway co-membership with `CBS` (log2FC = -1.254) in folate and transsulfuration pathways; indirect metabolic relationship.

---

### 4. Validation Priorities

#### Priority 1: Shift from Resident Kupffer Cells (TIMD4/MARCO low) to Lipid-Associated Macrophages (TREM2/FABP5 high)
* **Classification:** Mechanistic hypothesis / Confounding or composition check
* **Why Prioritized:** Represents the largest inverse transcriptional fold-change divergence in the dataset (`TREM2` +4.911 vs. `TIMD4` -4.282), pointing to cell population replacement.
* **Input Dataset Evidence:** Strong inverse log2FC metrics between `TREM2` / `FABP5` (upregulated) and `TIMD4` / `MARCO` / `CD163` / `CD5L` (downregulated).
* **External Evidence:** Literature (e.g., PMID: 39497821) and single-cell atlas records confirm TREM2+ LAM accumulation in MASH. Note that external statistical validation was not performed on this specific dataset.
* **Next Step for Validation:** Perform spatial transcriptomics and multiplex immunofluorescence (TIMD4, TREM2, CD68) on human MASH liver biopsies to quantify cell subtype spatial distribution and proportion changes.
* **Conclusion Status:** Supported hypothesis.

#### Priority 2: CXCL10-CXCR3 Axis and TNFRSF12A (Fn14) Signaling in MASH Inflammation
* **Classification:** Therapeutic target / Mechanistic hypothesis
* **Why Prioritized:** Both `CXCL10` (log2FC = 3.463) and `TNFRSF12A` (log2FC = 3.271) are high-fold-change inflammatory drivers with established therapeutic tools.
* **Input Dataset Evidence:** Concurrent upregulation of `CXCL10` and `TNFRSF12A` in liver tissue.
* **External Evidence:** OpenTargets and ChEMBL record CXCR3 antagonists and Fn14-targeting reagents in chronic inflammatory disease models. Note: the existence of drug candidates targeting a pathway does not by itself prove clinical efficacy for MASH.
* **Next Step for Validation:** Test selective CXCR3 antagonists or Fn14-Fc decoy receptors in dietary mouse models of MASH (e.g., GAN or CDAHFD diets) to assess reduction in lobular inflammation and ALT/AST levels.
* **Conclusion Status:** Exploratory hypothesis.

#### Priority 3: Sinusoidal Endothelial Adhesion Loss and Vascular Remodeling (PCDH20 / CDH5 / VCAM1)
* **Classification:** Interaction / network hypothesis
* **Why Prioritized:** Broad downregulation of cell-cell adhesion molecules (GO:0098742) indicates sinusoidal endothelial dysfunction or capillarization.
* **Input Dataset Evidence:** Significant downregulation of `PCDH20` (log2FC = -4.593), `VCAM1` (log2FC = -2.378), `CDH5` (log2FC = -1.376), and `CDH23` (log2FC = -1.904).
* **External Evidence:** Reactome junction pathways and STRING network links (CDH5-CTNNB1).
* **Next Step for Validation:** Perform transmission electron microscopy (TEM) and dual CD31/VE-cadherin immunofluorescence in liver biopsy sections to evaluate endothelial fenestrations and microvascular disruption.
* **Conclusion Status:** Exploratory hypothesis.

#### Priority 4: Transsulfuration and One-Carbon Metabolic Reprogramming (MTHFD1L High / CBS Low)
* **Classification:** Mechanistic hypothesis / Biomarker
* **Why Prioritized:** Recurrent transcriptomic alterations across one-carbon enzymes (`MTHFD1L` log2FC = 1.717, `CBS` log2FC = -1.254) connect lipotoxicity to redox and methylation imbalance.
* **Input Dataset Evidence:** Opposing expression shifts in mitochondrial folate (`MTHFD1L`) and transsulfuration (`CBS`) enzymes.
* **External Evidence:** HMDB records and metabolic studies (PMID: 38323273) link MTHFD1L and transsulfuration defects with hepatic glutathione depletion and oxidative stress.
* **Next Step for Validation:** Quantify plasma and intrahepatic levels of S-adenosylmethionine (SAM), S-adenosylhomocysteine (SAH), homocysteine, formate, and reduced glutathione (GSH) by LC-MS/MS across healthy control vs. MASH patient cohorts.
* **Conclusion Status:** Exploratory hypothesis.

#### Priority 5: Cell-Composition Deconvolution and Cell-Type-Specific Profiling
* **Classification:** Confounding or composition check
* **Why Prioritized:** Bulk transcriptomics conflates shifts in cell type proportions (e.g., monocyte infiltration, hepatocyte loss) with intracellular transcriptional changes.
* **Input Dataset Evidence:** Inverse co-expression patterns of highly cell-type-restricted genes across myeloid, endothelial, and parenchymal markers.
* **External Evidence:** GTEx and Human Protein Atlas (HPA) confirm cell-type enrichment (e.g., `TIMD4`/`TREM2` in myeloid cells; `CDH5` in endothelial cells).
* **Next Step for Validation:** Apply bioinformatic deconvolution algorithms (e.g., CIBERSORTx) using human single-cell RNA-seq reference panels and validate with FACS-sorted liver cell populations.
* **Conclusion Status:** Established evidence (that cell composition shifts confound bulk transcriptomics).

---

### 5. Evidence Grounding

* **Direct Evidence from Input Dataset:** Primary differential expression metrics derived from the uploaded dataset (`TREM2` log2FC = 4.911, FDR = 3.899e-09; `UBD` log2FC = 4.151, FDR = 1.325e-10; `TIMD4` log2FC = -4.282, FDR = 1.502e-08; `PCDH20` log2FC = -4.593, FDR = 1.474e-08; `CXCL10` log2FC = 3.463, FDR = 1.183e-07; `TNFRSF12A` log2FC = 3.271, FDR = 1.334e-07).
* **External Statistical Validation:** External statistical validation was not performed (no independent replication cohort statistics were provided).
* **Pathway / Ontology Evidence:** Annotation records from GO:0098742 (Cell-Cell Adhesion Via Plasma-Membrane Adhesion Molecules), GO:0030450 (Regulation Of Complement Activation, Classical Pathway), KEGG: Aminoacyl-tRNA biosynthesis, and Reactome cytokine pathways contextualize gene functions. *Note:* GO/KEGG pathways share underlying gene annotations and do not represent independent statistical replication.
* **Protein Interaction & Regulatory Network Evidence:** Direct physical interaction evidence from STRING (`FOXM1`-`CTNNB1`, `CD163`-`MRC1`, `CFP`-`CR1`) and TRRUST regulatory targets (`FOXM1`, `TCF7L1`). Distinctions between direct physical binding and co-expression modules are maintained.
* **Expression & Tissue-Specific Evidence:** GTEx and Human Protein Atlas (HPA) records confirm liver and single-cell-type specificity for myeloid markers (`TREM2`, `TIMD4`, `CD163`) and endothelial markers (`CDH5`).
* **Literature & Therapeutic Evidence:** Published literature (e.g., PMID: 39497821 on efferocytosis markers in MASH; PMID: 38323273 on MTHFD1L) and database entries from OpenTargets and ChEMBL provide disease association context. *Note:* Database records sharing literature citations represent non-independent annotations.

---

### 6. Limitations and Alternative Explanations

1. **Cell-Composition Confounding in Bulk Tissue:**
   * Bulk RNA-seq profiles represent an average across hepatocytes, stellate cells, endothelial cells, and immune infiltrates. The observed drop in Kupffer cell markers (`TIMD4`, `MARCO`) and rise in LAM markers (`TREM2`, `FABP5`) primarily reflects altered immune cell population proportions rather than gene expression changes within a single cell lineage.
   * *Investigation:* Validate cell-type-specific transcriptional responses using single-cell RNA sequencing or spatial transcriptomics.
2. **Absence of Independent External Cohort Replication:**
   * Statistical significance metrics derive solely from the provided sample dataset. Without independent cohort statistics, signals could reflect cohort-specific batch artifacts or sampling biases.
   * *Investigation:* Test the top candidate marker panel (`TREM2`, `TIMD4`, `UBD`, `CXCL10`, `PCDH20`) in external public MASH transcriptomic cohorts (e.g., GEO datasets GSE130970 or GSE135251).
3. **Ambiguity in Cause versus Effect (Association vs. Causation):**
   * Differential expression metrics establish statistical correlation with MASH status but cannot determine causality. For instance, `TREM2` upregulation could represent a protective phagocytic clearance response to lipotoxicity rather than a driver of pathology.
   * *Investigation:* Perform genetic loss-of-function and gain-of-function studies in mouse models or human liver organoids to evaluate disease progression phenotypes.
4. **Uncontrolled Clinical and Disease Severity Factors:**
   * MASH encompasses a wide spectrum of disease severity, ranging from simple steatosis with mild lobular inflammation to severe ballooning and advanced fibrosis (F0–F4). The input dataset lacks clinical stratification for NAFLD Activity Score (NAS), fibrosis stage, age, sex, or metabolic co-morbidities (e.g., type 2 diabetes).
   * *Investigation:* Re-analyze expression profiles stratified by histological NAS grades and fibrosis stages.
5. **Vascular and Tissue Structural Artifacts:**
   * Downregulation of cell junction and vascular adhesion markers (`PCDH20`, `CDH5`, `VCAM1`) may stem from sinusoidal endothelial capillarization, localized tissue edema, or mechanical disruption during liver biopsy acquisition.
   * *Investigation:* Evaluate endothelial protein abundance and junctional architecture using quantitative immunohistochemistry on intact, formalin-fixed paraffin-embedded (FFPE) tissue sections.

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=73, external claims checked=0, external mismatches=0, status=passed.

Answer model API: Google Gemini / gemini-3.6-flash

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 93/100 selected items (records returned); cbioportal 85/100 selected items (records returned); chembl 33/100 selected items (partially returned; some queries failed); civic 4/100 selected items (records returned); clinicaltrials 40/100 selected items (records returned); clinvar 82/100 selected items (records returned); ensembl 42/100 selected items (partially returned; some queries failed); europepmc 897 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 75/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 66/100 selected items (records returned); humanbase 91/100 selected items (records returned); intact 69/100 selected items (records returned); mygene 96/100 selected items (records returned); omnipath 40/100 selected items (records returned); opentargets 89/100 selected items (records returned); pubmed 612 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 69/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 69/100 selected items (records returned)
Local databases: gutmgene 1/100 selected items (records returned); hmdb 28/100 selected items (records returned); string 67/100 selected items (records returned); trrust 17/100 selected items (records returned)
