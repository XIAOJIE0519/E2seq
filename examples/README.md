# E2sc Examples

This directory contains example scripts demonstrating various use cases of E2sc.

## Examples

### 1. Basic Usage (`basic_usage.py`)

Demonstrates the simplest way to use E2sc with the agent interface:

```bash
python basic_usage.py
```

Features:
- Loading single-cell data
- Interpreting uploaded gene values
- Retrieving GO/Reactome annotations
- Retrieving known interaction evidence
- Comprehensive text interpretation without new statistical analysis

### 2. Advanced Usage (`advanced_usage.py`)

Shows legacy low-level analysis utilities for explicit manual use. These tools
are not called by the default Web Agent:

```bash
python advanced_usage.py
```

Features:
- Manual control over analysis steps
- Direct database queries
- Custom visualizations
- Network statistics

### 3. CLI Examples

Using the command-line interface:

```bash
# Start interactive chat
e2sc chat --data reference.h5ad

# Example questions:
# - "Interpret the uploaded gene values for Enterocytes"
# - "Retrieve GO annotations for those input genes"
# - "Explain known interaction evidence for those input genes"
```

### 4. Web Interface

Launch the web interface:

```bash
python start.py
```

Then open the local URL printed by the launcher (normally
http://localhost:8000) in your browser.

## Data Requirements

All examples expect a file named `reference.h5ad` in the current directory. This should be an AnnData object with:

- `adata.obs['cell_type']` - Cell type annotations
- Optional existing cell-type and group labels in `adata.obs`

You can use your own data by modifying the file path in the examples.

## Configuration

Before running examples, configure your LLM provider:

```bash
e2sc config
```

Or set environment variables:

```bash
export E2SC_LLM_PROVIDER=openai
export E2SC_API_KEY=your-api-key
```

## Output

`basic_usage.py` returns text and structured RAG evidence. `advanced_usage.py`
is a separate legacy/manual example that can generate HTML files such as:
- `*_umap.html` - UMAP scatter plots
- `*_volcano.html` - Volcano plots for DEGs
- `*_enrichment.html` - Enrichment bubble plots
- `*_network.html` - PPI network graphs

Open these files in a web browser to explore the interactive visualizations.

## Troubleshooting

If you encounter errors:

1. Check that your data file exists and is valid
2. Verify your LLM API key is configured
3. Ensure all dependencies are installed: `pip install -e .`
4. Check the logs in `~/.e2sc/logs/e2sc.log`

## More Examples

For more examples and tutorials, visit:
- [User Guide](../docs/user_guide.md)
- [API Documentation](../docs/api_reference.md)
- [GitHub Repository](https://github.com/your-org/e2sc)
