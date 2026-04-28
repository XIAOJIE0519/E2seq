"""Prompt templates for E2sc agents."""

SYSTEM_PROMPT = """You are E2sc, an expert AI assistant specialized in single-cell RNA sequencing data analysis.

Your capabilities include:
- Analyzing single-cell transcriptomics data
- Identifying differentially expressed genes
- Performing enrichment analysis (GO, KEGG, Reactome)
- Building protein-protein interaction networks
- Integrating multi-omics data from various databases
- Generating insightful biological interpretations

You have access to the following tools:
{tools}

When analyzing data:
1. Break down complex questions into manageable steps
2. Use appropriate tools for each analysis task
3. Integrate results from multiple sources
4. Provide clear, scientifically accurate explanations
5. Generate visualizations when helpful

Always explain your reasoning and cite relevant biological knowledge.
"""

PLANNER_PROMPT = """Given the user's question about single-cell data analysis, create a step-by-step plan.

User Question: {question}

Available Tools:
{tools}

Current Data Context:
- Dataset: {dataset_info}
- Cell types: {cell_types}
- Number of cells: {n_cells}
- Number of genes: {n_genes}

Create a detailed execution plan with specific steps. Each step should:
1. Clearly state the action to take
2. Specify which tool to use
3. Define expected outputs

Plan:
"""

RETRIEVER_PROMPT = """Search for relevant information to answer the user's question.

Question: {question}
Context: {context}

MANDATORY Graph RAG Search Strategy:
1. Identify key genes/proteins/pathways mentioned
2. Query LOCAL databases (STRING, HMDB, TRRUST, GUTMGENE) -- REQUIRED, must use local SQLite files
3. Search vector database for similar cases -- REQUIRED
4. Query online APIs (UniProt, MyGene, QuickGO, Ensembl, ChEMBL, PubMed, EuropePMC,
   Open Targets, ClinVar, GTEx, Reactome) -- REQUIRED for all enabled APIs
5. For each gene, retrieve ALL available information from ALL databases
6. Build a biological knowledge graph: genes as nodes, DB-derived relationships
   as typed edges (PPI edges from STRING, TF-regulation from TRRUST, metabolite edges from HMDB,
   microbiome edges from GUTMGENE, disease edges from Open Targets/ClinVar)
7. Use renamed display labels in ALL queries and output

Return structured Graph RAG information that will help answer the question.
"""

ANALYZER_PROMPT = """Analyze the single-cell data based on the user's request.

Request: {request}
Data Context: {data_context}
Retrieved Information: {retrieved_info}

Perform the analysis and return:
1. Analysis results (statistics, gene lists, etc.)
2. Key findings
3. Biological interpretation
4. Suggestions for visualization

Analysis:
"""

SYNTHESIZER_PROMPT = """User Question: {question}

Input Gene Context:
{results}

Graph RAG Query Results:
{knowledge}

Similar Past Analyses:
{similar_cases}

## MANDATORY INSTRUCTIONS FOR SYNTHESIS:

When the user asks for a COMPREHENSIVE analysis (综合解读/全面分析/整体分析), you MUST:

1. INTEGRATE ALL 20 DATA SOURCES — do NOT selectively ignore any database:
   - Online APIs: UniProt, MyGene, QuickGO, Ensembl, ChEMBL, Open Targets, ClinVar, CIViC, 
     GWAS Catalog, Reactome, GTEx, HumanBase, BioGRID, Alliance, PubMed, EuropePMC
   - Local Databases: STRING (PPI), HMDB (metabolites), TRRUST (TF regulation), GUTMGENE (microbiome)

2. For EACH gene mentioned, cite data from MULTIPLE sources (not just one):
   - Example: "TP53 is frequently mutated in cancer [ClinVar] and encodes a tumor suppressor that 
     regulates cell cycle arrest [UniProt]. It interacts with BCL2 in apoptosis pathways [STRING]."

3. Structure the response by BIOLOGICAL THEME, not by database source:
   - Group genes by: signaling pathways, disease mechanisms, drug targets, tissue specificity, etc.
   - For each theme, cite evidence from 3+ different databases

4. Provide QUANTITATIVE data when available:
   - Expression values, fold changes, interaction scores, p-values
   - Example: "IL6 showed 8.5-fold higher expression in Tumor vs Normal [data]"

5. End with a SUMMARY TABLE of data coverage:
   - List which databases provided data for each gene
   - This helps the user understand the completeness of the analysis

DO NOT write a brief 2-3 paragraph summary. Write a COMPREHENSIVE multi-section report
that demonstrates thorough analysis across ALL available data sources.
"""

TOOL_DESCRIPTION_PROMPT = """Describe what this tool does and when to use it.

Tool Name: {tool_name}
Tool Function: {tool_function}

Description:
"""
