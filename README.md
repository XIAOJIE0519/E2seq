# E2seq - Easy to Chat with Sequencing

<div align="center">

**An AI-powered single-cell RNA sequencing analysis platform with natural language interface**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Powered by LangChain](https://img.shields.io/badge/Powered%20by-LangChain-green.svg)](https://www.langchain.dev/)

[English](README.md) | [中文](README_CN.md)

</div>

---

## Overview

**E2seq (Easy to Chat with Sequencing)** is an intelligent agent platform designed for single-cell RNA sequencing (scRNA-seq) data analysis. It combines the power of Large Language Models (LLMs) with retrieval-augmented generation (RAG) to enable researchers to interact with their single-cell data through natural language queries.

Instead of writing complex code or manually executing bioinformatics pipelines, researchers can simply ask questions like:

- "Analyze marker genes for T cells"
- "What pathways are enriched in this cell type?"
- "Show me the gene interaction network"

E2seq handles the complexity behind the scenes, from data processing to visualization.

---

## Features

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **Natural Language Interface** | Query your data using plain English |
| **Differential Expression Analysis** | Identify marker genes and DEGs between cell groups |
| **Enrichment Analysis** | GO, KEGG, Reactome pathway enrichment |
| **Network Analysis** | Build and analyze PPI networks from STRING database |
| **Interactive Visualization** | UMAP, tSNE, volcano plots, heatmaps, network graphs |

### Knowledge Base Integration

| Database | Type | Description |
|----------|------|-------------|
| STRING | PPI Network | Protein-protein interaction data |
| HMDB | Metabolomics | Human metabolome database |
| TRRUST | TF-Target | Transcription factor regulatory network |
| GUTMGENE | Microbiome | Gut microbiome-gene interactions |

### LLM Provider Support

- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude 3)
- Google Gemini
- Zhipu AI (GLM-4)
- DeepSeek
- SiliconFlow

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
git clone https://github.com/XIAOJIE0519/E2seq.git
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

Go to Settings and add your LLM provider API key.

### 3. Upload Data

Click the upload button to add your single-cell data (.h5ad files).

### 4. Start Analyzing

Try these example queries:

```
"Analyze marker genes for Enterocytes"
"What pathways are enriched in B cells?"
"Build a protein interaction network for these DEGs"
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
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    E2scAgent                                 │
│  ┌─────────────┬─────────────┬─────────────┐                │
│  │   Planner   │  Retriever  │ Synthesizer │                │
│  └─────────────┴─────────────┴─────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

### Component Description

| Component | File | Purpose |
|-----------|------|---------|
| API Server | `e2sc/api/server.py` | Handles HTTP requests |
| Agent | `e2sc/agent/orchestrator.py` | Main agent orchestration |
| Planner | `e2sc/agent/planner.py` | Creates analysis plans |
| Retriever | `e2sc/agent/retriever.py` | Queries databases |
| Synthesizer | `e2sc/agent/synthesizer.py` | Generates responses |

---

## Configuration

Configuration is stored in `.e2sc/config.yaml`:

```yaml
llm:
  provider: glm        # LLM provider
  model: glm-4         # Model name
  temperature: 0.7

embedding:
  model_name: sentence-transformers/all-MiniLM-L6-v2
  local_only: true
```

---

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/api/health` | GET | Health check |
| `/api/chat` | POST | Send chat message |
| `/api/upload` | POST | Upload data file |
| `/docs` | GET | API documentation |

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
  url = {https://github.com/XIAOJIE0519/E2seq}
}
```
