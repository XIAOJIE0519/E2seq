"""Example: Basic usage of E2seq."""

import scanpy as sc
from e2seq import E2seqAgent

# Load your single-cell data
print("Loading data...")
adata = sc.read_h5ad("reference.h5ad")

print(f"Dataset: {adata.n_obs} cells, {adata.n_vars} genes")

# Create E2seq agent
print("\nInitializing E2seq agent...")
agent = E2seqAgent(
    adata=adata,
    llm_provider="openai",  # or "anthropic", "deepseek", "ollama"
    api_key="your-api-key-here"
)

# Example 1: Find marker genes
print("\n" + "="*50)
print("Example 1: Finding marker genes")
print("="*50)

response = agent.chat("Find marker genes for Enterocytes")
print(response["text"])

# Save plots
for plot_name, fig in response["plots"]:
    fig.write_html(f"example1_{plot_name}.html")
    print(f"Saved: example1_{plot_name}.html")

# Example 2: GO enrichment
print("\n" + "="*50)
print("Example 2: GO enrichment analysis")
print("="*50)

response = agent.chat("Perform GO enrichment on the differentially expressed genes")
print(response["text"])

for plot_name, fig in response["plots"]:
    fig.write_html(f"example2_{plot_name}.html")
    print(f"Saved: example2_{plot_name}.html")

# Example 3: Network analysis
print("\n" + "="*50)
print("Example 3: Network analysis")
print("="*50)

response = agent.chat("Build a PPI network and identify hub genes")
print(response["text"])

for plot_name, fig in response["plots"]:
    fig.write_html(f"example3_{plot_name}.html")
    print(f"Saved: example3_{plot_name}.html")

# Example 4: Multi-step analysis
print("\n" + "="*50)
print("Example 4: Comprehensive analysis")
print("="*50)

response = agent.chat(
    "Compare Enterocytes and Goblet cells, perform GO enrichment, "
    "and build a network for the top hub genes"
)
print(response["text"])

for plot_name, fig in response["plots"]:
    fig.write_html(f"example4_{plot_name}.html")
    print(f"Saved: example4_{plot_name}.html")

print("\n" + "="*50)
print("All examples completed!")
print("="*50)
