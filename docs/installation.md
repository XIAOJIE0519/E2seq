# E2seq Installation Guide

## Prerequisites

- Python 3.9 or higher
- pip package manager

## Installation

### From PyPI (Recommended)

```bash
pip install e2seq
```

### From Source

```bash
git clone https://github.com/your-org/e2seq.git
cd e2seq
pip install -e .
```

## Initial Setup

### 1. Configure LLM Provider

E2seq requires an LLM provider to function. Configure it using:

```bash
e2sc config
```

You'll be prompted to enter:
- LLM Provider (openai, anthropic, deepseek, ollama)
- API Key (if not using ollama)
- Model name

Alternatively, set environment variables:

```bash
export E2SC_LLM_PROVIDER=openai
export E2SC_API_KEY=your-api-key
export E2SC_MODEL=gpt-4
```

### 2. Initialize Databases

E2sc uses local databases for fast knowledge retrieval. Initialize them from CSV files:

```bash
e2sc init-db /path/to/database/directory
```

The directory should contain:
- `STRING.csv` - Protein-protein interactions
- `HMDB.csv` - Gene-metabolite associations
- `TRRUST.csv` - Transcription factor regulations
- `GUTMGENE.csv` - Gut microbiome-gene associations

## Quick Start

### CLI Usage

```bash
# Start interactive chat
e2sc chat

# Load data and start chat
e2sc chat --data your_data.h5ad
```

### Web Interface

```bash
# Start the supported FastAPI Web launcher
python start.py
```

The launcher checks the environment and asks for an available port before
starting `e2sc.api.server:app`. The `e2sc web` command is retained only as a
compatibility alias and delegates to `start.py`.

### Python API

```python
from e2sc import E2scAgent
import scanpy as sc

# Load your data
adata = sc.read_h5ad('your_data.h5ad')

# Create agent
agent = E2scAgent(
    adata=adata,
    llm_provider='openai',
    api_key='your-api-key'
)

# Ask questions
response = agent.chat("解读 Enterocytes 中上传的基因数值")
print(response['text'])

# Show plots
for plot_name, fig in response['plots']:
    fig.show()
```

## Data Requirements

Your single-cell data (h5ad format) should contain:

### Required fields in `adata.obs`:
- `cell_type` or `final_annotation` - Cell type annotations

### Required fields in `adata.obsm`:
- `X_umap` or `X_tsne` - Dimensionality reduction coordinates

### Optional but recommended:
- `group` or `condition` - Experimental groups
- `leiden_clusters` - Clustering results

## Troubleshooting

### API Key Issues

If you get authentication errors:
1. Check your API key is correct
2. Verify the provider name matches your key
3. Try reconfiguring: `e2sc config`

### Database Issues

If database queries fail:
1. Ensure databases are initialized: `e2sc init-db`
2. Check database files exist in `~/.e2sc/databases/`

### Memory Issues

For large datasets:
1. Subset your data before analysis
2. Increase system memory
3. Use a machine with more RAM

## Next Steps

- Read the [User Guide](user_guide.md)
- Check [API Documentation](api_reference.md)
- See [Examples](examples.md)
