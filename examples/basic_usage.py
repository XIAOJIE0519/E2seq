"""Example: Basic usage of E2sc."""

import scanpy as sc
from e2sc import E2scAgent

# Load your single-cell data
print("Loading data...")
adata = sc.read_h5ad("reference.h5ad")

print(f"Dataset: {adata.n_obs} cells, {adata.n_vars} genes")

# Create E2sc agent
print("\nInitializing E2sc agent...")
agent = E2scAgent(
    adata=adata,
    llm_provider="openai",  # or "anthropic", "deepseek", "ollama"
    api_key="your-api-key-here"
)

# Example 1: interpret uploaded gene values
print("\n" + "="*50)
print("Example 1: Input-value interpretation")
print("="*50)

response = agent.chat("Interpret the uploaded gene values for Enterocytes")
print(response["text"])

# Example 2: retrieve pathway annotations
print("\n" + "="*50)
print("Example 2: Pathway annotation retrieval")
print("="*50)

response = agent.chat("Retrieve GO and Reactome annotations for those input genes")
print(response["text"])

# Example 3: retrieve known interaction evidence
print("\n" + "="*50)
print("Example 3: Interaction evidence retrieval")
print("="*50)

response = agent.chat("Explain known STRING and TRRUST evidence for those input genes")
print(response["text"])

# Example 4: comprehensive interpretation
print("\n" + "="*50)
print("Example 4: Comprehensive interpretation")
print("="*50)

response = agent.chat(
    "Comprehensively interpret the uploaded values for Enterocytes and Goblet cells"
)
print(response["text"])

print("\n" + "="*50)
print("All examples completed!")
print("="*50)
