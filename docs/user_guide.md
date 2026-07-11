# E2seq User Guide

## Introduction

E2seq (Easy to Chat with Sequencing) interprets gene/value results from bulk and single-cell sequencing files. It uses Agent RAG (Retrieval-Augmented Generation) to retrieve biological evidence for genes already present in the uploaded file.

The default Agent does not calculate marker genes, DEGs, fold changes, p-values, enrichment, clustering, dimensionality reduction, networks, hubs, or modules.

## Core Concepts

### Agentic Workflow

The default Web workflow is:

1. **Input context**: Read supplied genes, numeric values, groups, and cell-type labels
2. **Planner**: Select only relevant genes from that input
3. **Retriever**: Fetch database and literature evidence through Agent RAG
4. **Synthesizer**: Return Markdown text that separates input values from external evidence

### Knowledge Integration

E2sc integrates multiple data sources:

- **Local Databases**: STRING, HMDB, TRRUST, GUTMGENE
- **Online APIs**: UniProt, QuickGO, PubMed, MyGene
- **Your Data**: Bulk or single-cell gene/value results

## Usage Examples

### Example 1: Interpret an H5AD matrix

```python
from e2sc import E2scAgent
import scanpy as sc

# Load data
adata = sc.read_h5ad('data.h5ad')

# Create agent
agent = E2scAgent(adata=adata)

# Ask for interpretation of values already present in the file
response = agent.chat("Interpret the uploaded gene values for Enterocytes")

# View results
print(response['text'])
```

### Example 2: Retrieve pathway annotations

```python
response = agent.chat("Retrieve GO and Reactome annotations for the supplied genes")
print(response['text'])
```

### Example 3: Retrieve interaction evidence

```python
response = agent.chat("Explain known STRING/TRRUST evidence for these input genes")
print(response['text'])
```

### Example 4: Comprehensive interpretation

```python
response = agent.chat(
    "Comprehensively interpret the uploaded values for Enterocytes and Goblet cells"
)

# The Agent preserves input values, retrieves evidence, and returns text.
# It does not run new statistical or network analysis.
```

## CLI Usage

### Interactive Chat

```bash
$ e2sc chat --data data.h5ad

E2sc> 解读 Enterocytes 中上传的基因数值

[Retrieving evidence...]
✓ Preserved the supplied gene values and labels
✓ Retrieved gene annotations and literature evidence
✓ Returned a source-backed text interpretation

E2sc> 继续解释这些基因的 GO 与 Reactome 注释

[Retrieving evidence...]
✓ Returned external pathway annotations without enrichment computation
```

### Commands

- `/load <file>` - Load new data file
- `/help` - Show help
- `/exit` - Exit chat

## Web Interface

### Starting the Server

```bash
python start.py
```

### Using the Interface

1. **Configure LLM**: Enter your API key in the sidebar
2. **Upload Data**: Upload your h5ad file
3. **Ask Questions**: Type questions in the chat box
4. **View Results**: Read the API/SSE-delivered Markdown interpretation

### Features

- 📝 Text-first responses grounded in uploaded values
- 🔎 Source statistics for retrieved RAG evidence
- 📝 Chat history
- 🎨 Beautiful UI with gradient themes

## Advanced Usage

### Legacy Low-level Analysis Utilities

The following APIs remain available for backward compatibility and explicit
manual use. They are **not called by the default Web Agent**. Their results must
not be presented as part of the interpretation-only workflow.

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

- Supply clear gene identifiers and numeric values
- Keep group and cell-type labels in the file when they are relevant
- Complete any desired QC or statistical analysis upstream; E2seq will not run it

### 2. Question Formulation

Good questions are:
- Specific: "Interpret these supplied Enterocyte gene values"
- Clear: "Explain the existing values for group A and group B"
- Evidence-focused: "Retrieve pathway annotations for these input genes"

Avoid vague questions like:
- "Analyze my data"
- "What's interesting here?"

### 3. Iterative Analysis

Use conversation history to build on previous results:

```python
agent.chat("Interpret the supplied Enterocyte gene values")
agent.chat("Now retrieve pathway annotations for those same input genes")
agent.chat("Explain the known interaction evidence without building a network")
```

### 4. Performance Tips

- Subset large datasets before upload when appropriate
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
