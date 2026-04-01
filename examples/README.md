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
- Finding marker genes
- GO enrichment analysis
- Network analysis
- Multi-step comprehensive analysis

### 2. Advanced Usage (`advanced_usage.py`)

Shows how to use individual tools for fine-grained control:

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
# - "Find marker genes for Enterocytes"
# - "Perform GO enrichment on DEGs"
# - "Build a PPI network"
```

### 4. Web Interface

Launch the web interface:

```bash
e2sc web
```

Then open http://localhost:8501 in your browser.

## Data Requirements

All examples expect a file named `reference.h5ad` in the current directory. This should be an AnnData object with:

- `adata.obs['cell_type']` - Cell type annotations
- `adata.obsm['X_umap']` - UMAP coordinates

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

Examples generate HTML files with interactive plots:
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
