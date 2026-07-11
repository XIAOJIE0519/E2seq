# E2seq - Easy to Chat with Sequencing

<div align="center">

**An Agent RAG interpreter for bulk and single-cell sequencing gene-value results**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)

[English](README.md) | [中文](README_CN.md)

</div>

---

## Overview

**E2seq (Easy to Chat with Sequencing)** reads gene identifiers, numeric values, and existing labels from bulk or single-cell result files, retrieves evidence for those input genes, and returns a source-backed textual interpretation.

The default Web Agent intentionally does **not** compute marker genes, DEGs, fold changes, p-values, enrichment, clustering, dimensionality reduction, networks, hubs, or modules. Reactome, STRING, QuickGO, TRRUST, and similar content is treated as external RAG evidence—not as a result computed from the uploaded file.

Researchers can ask questions such as:

- "Interpret the supplied gene values for T cells"
- "What retrieved pathway annotations help explain these input genes?"
- "Summarize the evidence for the genes with the supplied values"
- "Which known interactions are relevant to these uploaded genes?"

The supported Web startup command is `python start.py`.

---

## Features

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **Natural Language Interface** | Query your data using plain English or Chinese |
| **Input-value interpretation** | Preserve uploaded gene names, values, group labels, and cell-type labels |
| **Agent RAG retrieval** | Query biological databases and literature for the selected input genes |
| **Evidence separation** | Clearly distinguish uploaded values from external annotations |
| **Text-first API** | Return Markdown text through REST/SSE without computing new analysis results |
| **Session isolation** | Keep datasets, memory, state, caches, and progress scoped to one chat |

### Knowledge Base Integration

E2seq integrates **20+ biological databases** to provide comprehensive insights:

#### Local Databases

| Database | Type | Records | Description |
|----------|------|---------|-------------|
| STRING | PPI Network | 1,858,946 | Protein-protein interaction data |
| HMDB | Metabolomics | 1,045,796 | Human metabolome database |
| TRRUST | TF-Target | 9,398 | Transcription factor regulatory network |
| GUTMGENE | Microbiome | 1,334 | Gut microbiome-gene interactions |

#### Online APIs (16 Sources)

| API | Provider | Data Type |
|-----|----------|-----------|
| UniProt | EMBL-EBI | Protein function, domains, PTMs |
| MyGene | scGene | Gene annotation, GO terms |
| QuickGO | EMBL-EBI | GO annotations with evidence codes |
| Ensembl | EMBL-EBI | Genomic coordinates, exon structure |
| ChEMBL | EMBL-EBI | Drug-target binding, clinical phases |
| Open Targets | EBI-OpenTargets | Gene-disease association scores |
| ClinVar | NCBI | Pathogenic/benign variants |
| CIViC | MSKCC | Clinical evidence for cancer variants |
| GWAS Catalog | EBI | Trait/SNP associations |
| Reactome | EMBL-EBI | Biological pathway membership |
| GTEx | GTEx Project | Tissue-specific expression (54 tissues) |
| HumanBase | HB | Tissue-specific co-expression networks |
| BioGRID | BioGRID | Experimental PPI (Y2H, co-IP) |
| Alliance | Alliance of Genome Resources | Cross-species orthology |
| PubMed | NCBI | Literature search |
| EuropePMC | EMBL-EBI | Preprints + published papers |

### LLM Provider Support

E2seq supports **7 LLM providers** with **30+ models** (as of April 2026):

| Provider | Default Model | Recommended Models |
|----------|--------------|-------------------|
| **OpenAI** | gpt-5.5 | gpt-5.5-pro, gpt-5.1, gpt-5.2, gpt-4o |
| **Anthropic** | claude-opus-4-8 | claude-opus-4-7, claude-sonnet-4-6, claude-haiku-4-5 |
| **DeepSeek** | deepseek-v4-flash | deepseek-v4-pro |
| **Google Gemini** | gemini-3.1-pro-preview | gemini-3-flash-preview, gemini-2.5-pro |
| **SiliconFlow** | deepseek-ai/DeepSeek-V3 | deepseek-ai/DeepSeek-R1, Qwen/Qwen2.5-72B |
| **Zhipu AI (GLM)** | glm-5.2 | glm-5.1, glm-4-Plus, glm-4 |
| **Moonshot AI (Kimi)** | kimi-k2.6 | moonshot-v2.5-250415 |
| **Ollama** (local) | - | llama3.2, qwen2.5, deepseek-r1 |

> **Note**: DeepSeek, Gemini, and SiliconFlow use OpenAI-compatible APIs. Ollama runs locally without API keys.

### Data Format Support

- **Single-cell**: `.h5ad`, `.csv`, `.rds`
- **Tables**: `.csv`, `.tsv`, `.xlsx`

---

## Installation

### Prerequisites

- Python 3.9 or higher
- pip or conda
- 8GB+ RAM (16GB recommended for large datasets)

### Standard Installation

```bash
# Clone the repository
git clone git@github.com:XIAOJIE0519/E2seq.git
cd E2seq

# Install dependencies
pip install -e .

# Run the application
python start.py
```

### Dependencies

Core dependencies are automatically installed:

```
scanpy>=1.9.0
anndata>=0.9.0
langchain>=0.1.0
chromadb>=0.4.0
sentence-transformers>=2.2.0
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
```

---

## Quick Start

### 1. Launch the Server

```bash
python start.py
```

The server will start at `http://localhost:8000` by default.

### 2. Configure API Keys

Go to Settings page and add your LLM provider API key. E2seq supports multiple providers:

| Provider | API Key URL |
|----------|-------------|
| OpenAI | https://platform.openai.com/api-keys |
| Anthropic | https://console.anthropic.com/settings/keys |
| DeepSeek | https://platform.deepseek.com/api_keys |
| Google Gemini | https://aistudio.google.com/app/apikey |
| SiliconFlow | https://cloud.siliconflow.cn/account/ak |
| Zhipu AI | https://open.bigmodel.cn/ |
| Moonshot AI | https://platform.moonshot.cn/ |

### 3. Upload Data

Click the upload button to add your single-cell data (.h5ad files).

### 4. Start Interpreting

Try these example queries:

```
"Interpret the uploaded Enterocyte gene values"
"Retrieve pathway annotations for these B-cell input genes"
"Summarize the evidence for all supplied genes and values"
"Retrieve known interaction evidence for these input genes"
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Web UI                               │
│                   (HTML/CSS/JavaScript)                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Server                          │
│  - REST API endpoints                                       │
│  - SSE streaming for real-time responses                   │
│  - Session management                                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    E2scAgent Optimized                     │
│  ┌─────────────┬─────────────┬─────────────┐              │
│  │   Planner   │  Retriever  │ Synthesizer │              │
│  │(input genes)│  (RAG/DB)   │   (Text)    │              │
│  └─────────────┴─────────────┴─────────────┘              │
│                                                              │
│  ┌─────────────────────────────────────────┐                │
│  │           Vector Store (ChromaDB)        │                │
│  └─────────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Online APIs    │ │ Local Databases │ │ Vector Store    │
│  (16 sources)   │ │ (4 databases)   │ │ (RAG chunks)    │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### Component Description

| Component | File | Purpose |
|-----------|------|---------|
| API Server | `e2sc/api/server.py` | Handles HTTP requests, SSE streaming |
| Agent | `e2sc/agent/orchestrator_optimized.py` | Main agent orchestration |
| Planner | `e2sc/agent/orchestrator_optimized.py` | Selects genes from uploaded input context |
| Retriever | `e2sc/agent/orchestrator_optimized.py` | Queries databases & APIs for evidence |
| Synthesizer | `e2sc/agent/synthesizer.py` | Generates interpretation-only Markdown text |
| Knowledge Builder | `e2sc/agent/knowledge_builder.py` | Builds multi-source knowledge base |
| Vector Store | `e2sc/data/vector_store.py` | ChromaDB-based RAG |
| Local DB | `e2sc/data/local_db.py` | SQLite-based local databases |

---

## Configuration

Configuration is stored in `.e2sc/config.yaml`:

```yaml
llm:
  provider: deepseek        # LLM provider (openai/anthropic/deepseek/gemini/siliconflow/glm/kimi/ollama)
  model: deepseek-v4-flash  # Model name
  temperature: 0.7           # Creativity level
  max_tokens: 8192           # Max response length

embedding:
  model_name: sentence-transformers/all-MiniLM-L6-v2
  local_only: true           # Use local embeddings only

data:
  enabled_apis: [uniprot, mygene, quickgo, ensembl, chembl, pubmed, europepmc, reactome, gtex, humanbase, gwas, biogrid, civic, alliance, opentargets, clinvar]
  enabled_dbs: [string, hmdb, trrust, gutmgene]
```

---

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/api/health` | GET | Health check |
| `/api/chat` | POST | Send chat message |
| `/api/chat/stream` | POST | SSE streaming chat |
| `/api/upload` | POST | Upload data file |
| `/api/config` | GET | Get configuration |
| `/api/settings` | GET/POST | Manage settings |
| `/api/progress/{chat_id}` | GET | Get progress updates |
| `/docs` | GET | API documentation (Swagger) |

---

## Advanced Features

### Comprehensive Interpretation Mode

When you ask for a comprehensive interpretation (综合解读/全面解读), E2seq:

1. Integrates ALL 20+ data sources
2. Cites evidence from multiple databases for each claim
3. Organizes the response by biological theme
4. Preserves quantitative values already present in the uploaded file
5. Does not authorize any additional statistical or network computation

Example query:
```
"Give me a comprehensive interpretation of all uploaded gene values"
```

### Multi-Database Citation

E2seq provides inline citations for all claims:

```
"TP53 is frequently mutated in cancer [ClinVar] and encodes a tumor 
suppressor that regulates cell cycle arrest [UniProt]. It interacts 
with BCL2 in apoptosis pathways [STRING]."
```

### Source Statistics Panel

After each response, E2seq displays a statistics panel showing:

- Number of genes queried
- Data coverage from each database (API/Local)
- Hit rate per source
- Total articles retrieved from PubMed/EuropePMC

---

## License

This project is licensed under the MIT License.

---

## Citation

```bibtex
@software{e2seq2026,
  title = {E2seq: Easy to Chat with Sequencing},
  author = {E2seq Team},
  year = {2026},
  url = {https://github.com/XIAOJIE0519/E2seq},
  version = {2.0}
}
```

---

## Acknowledgments

E2seq integrates data from the following resources:

- STRING Database (https://string-db.org)
- HMDB (https://hmdb.ca)
- TRRUST (https://www.grnpedia.org/trrust/)
- UniProt (https://www.uniprot.org)
- PubMed/EuropePMC (https://pubmed.ncbi.nlm.nih.gov)
- Open Targets Platform (https://platform.opentargets.org)
- And 12+ other biological databases
