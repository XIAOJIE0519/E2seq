# E2seq User Guide

## Introduction

E2seq (Easy to Chat with Sequencing) is an AI-powered tool for single-cell RNA-seq data analysis. It uses agentic RAG (Retrieval-Augmented Generation) to understand your questions and automatically execute appropriate analyses.

## Core Concepts

### Agentic Workflow

E2seq uses multiple specialized agents:

1. **Planner Agent**: Breaks down your question into analysis steps
2. **Retriever Agent**: Fetches relevant information from databases
3. **Analyzer Agent**: Executes computational analyses
4. **Synthesizer Agent**: Combines results into a comprehensive report

### Knowledge Integration

E2sc integrates multiple data sources:

- **Local Databases**: STRING, HMDB, TRRUST, GUTMGENE
- **Online APIs**: UniProt, QuickGO, PubMed, MyGene
- **Your Data**: Single-cell expression matrix

## Usage Examples

### Example 1: Basic Differential Expression

```python
from e2sc import E2scAgent
import scanpy as sc

# Load data
adata = sc.read_h5ad('data.h5ad')

# Create agent
agent = E2scAgent(adata=adata)

# Ask question
response = agent.chat("Find marker genes for Enterocytes")

# View results
print(response['text'])
```

### Example 2: Enrichment Analysis

```python
response = agent.chat(
    "Perform GO enrichment analysis on differentially expressed genes"
)

# Access enrichment results
enrichment_data = response['data']['enrichment']
```

### Example 3: Network Analysis

```python
response = agent.chat(
    "Build a protein-protein interaction network and identify hub genes"
)

# Access network
network = response['data']['network']['graph']
hubs = response['data']['network']['hubs']
```

### Example 4: Multi-step Analysis

```python
response = agent.chat(
    "Compare Enterocytes and Goblet cells, perform GO enrichment, "
    "and build a PPI network for the top 50 DEGs"
)

# Agent automatically:
# 1. Performs differential expression
# 2. Runs GO enrichment
# 3. Builds network
# 4. Generates visualizations
# 5. Synthesizes comprehensive report
```

## CLI Usage

### Interactive Chat

```bash
$ e2sc chat --data data.h5ad

E2sc> 分析 Enterocytes 细胞的差异基因

[Analyzing...]
✓ Found 245 differentially expressed genes
✓ Top genes: APOA1, APOB, FABP1...
✓ Generated volcano plot: volcano_plot.html

E2sc> 对这些基因进行 GO 富集

[Analyzing...]
✓ GO enrichment completed
✓ Top pathways: lipid metabolism, nutrient absorption...
✓ Generated bubble plot: enrichment_plot.html
```

### Commands

- `/load <file>` - Load new data file
- `/help` - Show help
- `/exit` - Exit chat

## Web Interface

### Starting the Server

```bash
e2sc web --port 8501
```

### Using the Interface

1. **Configure LLM**: Enter your API key in the sidebar
2. **Upload Data**: Upload your h5ad file
3. **Ask Questions**: Type questions in the chat box
4. **View Results**: See text responses and interactive plots

### Features

- 📊 Interactive plots (zoom, pan, hover)
- 💾 Download results
- 📝 Chat history
- 🎨 Beautiful UI with gradient themes

## Advanced Usage

### Custom Analysis Pipeline

```python
from e2sc.tools import ScancpyTools, EnrichmentAnalyzer, NetworkAnalyzer

# Manual control over analysis steps
scanpy_tools = ScancpyTools(adata)
enrichment = EnrichmentAnalyzer()
network = NetworkAnalyzer()

# Step 1: Find DEGs
deg_results = scanpy_tools.find_marker_genes("Enterocytes", n_genes=100)

# Step 2: Enrichment
gene_list = deg_results['names'].tolist()
go_results = enrichment.go_enrichment(gene_list)

# Step 3: Network
G = network.build_ppi_network(gene_list[:50])
hubs = network.identify_hub_genes(G, top_n=10)
```

### Accessing Databases Directly

```python
from e2sc.data import STRINGDatabase, HMDBDatabase

# Query STRING
string_db = STRINGDatabase()
interactions = string_db.get_interactions("APOB", min_score=0.7)

# Query HMDB
hmdb_db = HMDBDatabase()
metabolites = hmdb_db.get_metabolites("APOB")
```

### Custom Visualizations

```python
from e2sc.tools import Visualizer

viz = Visualizer()

# Create custom plots
fig = viz.plot_umap(adata, color_by="cell_type")
fig.show()

fig = viz.plot_volcano(deg_results)
fig.write_html("my_volcano.html")
```

## Best Practices

### 1. Data Preparation

- Ensure cell type annotations are present
- Run basic QC and normalization with Scanpy
- Compute UMAP/tSNE before using E2sc

### 2. Question Formulation

Good questions are:
- Specific: "Find marker genes for Enterocytes"
- Clear: "Compare group A vs group B"
- Actionable: "Perform GO enrichment on DEGs"

Avoid vague questions like:
- "Analyze my data"
- "What's interesting here?"

### 3. Iterative Analysis

Use conversation history to build on previous results:

```python
agent.chat("Find DEGs for Enterocytes")
agent.chat("Now do GO enrichment on those genes")
agent.chat("Build a network for the top 10 hub genes")
```

### 4. Performance Tips

- Subset large datasets before analysis
- Use appropriate gene number thresholds
- Cache results when possible

## Troubleshooting

### Common Issues

**Issue**: "No cell type column found"
**Solution**: Ensure your adata.obs has a column named `cell_type` or `final_annotation`

**Issue**: "API rate limit exceeded"
**Solution**: Wait a moment and try again, or use local databases only

**Issue**: "Out of memory"
**Solution**: Subset your data or use a machine with more RAM

### Getting Help

- Check the [FAQ](faq.md)
- Read [API Documentation](api_reference.md)
- Open an issue on [GitHub](https://github.com/your-org/e2sc/issues)

## Next Steps

- Explore [Examples](examples.md)
- Read [API Reference](api_reference.md)
- Join our [Community](https://discord.gg/e2sc)
