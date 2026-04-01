"""Example: Advanced usage with manual control."""

import scanpy as sc
from e2sc.tools import ScancpyTools, EnrichmentAnalyzer, NetworkAnalyzer, Visualizer

# Load data
print("Loading data...")
adata = sc.read_h5ad("reference.h5ad")

# Initialize tools
scanpy_tools = ScancpyTools(adata)
enrichment = EnrichmentAnalyzer()
network = NetworkAnalyzer()
visualizer = Visualizer()

# Step 1: Find marker genes
print("\nStep 1: Finding marker genes for Enterocytes...")
deg_results = scanpy_tools.find_marker_genes("Enterocytes", n_genes=100)
print(f"Found {len(deg_results)} marker genes")
print(f"Top 10 genes: {', '.join(deg_results['names'].head(10).tolist())}")

# Step 2: GO enrichment
print("\nStep 2: Performing GO enrichment...")
gene_list = deg_results["names"].head(50).tolist()
go_results = enrichment.go_enrichment(gene_list, category="BP")

for category, df in go_results.items():
    print(f"\n{category}: {len(df)} enriched terms")
    print(f"Top 5 terms:")
    for term in df["Term"].head(5):
        print(f"  - {term}")

# Step 3: Build PPI network
print("\nStep 3: Building PPI network...")
G = network.build_ppi_network(gene_list, min_score=0.5)
print(f"Network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

# Identify hub genes
hubs = network.identify_hub_genes(G, top_n=10, method="degree")
print(f"\nTop 10 hub genes:")
for gene, score in hubs:
    print(f"  - {gene}: {score:.3f}")

# Get network statistics
stats = network.get_network_statistics(G)
print(f"\nNetwork statistics:")
print(f"  - Density: {stats['density']:.3f}")
print(f"  - Average degree: {stats['avg_degree']:.2f}")
print(f"  - Clustering coefficient: {stats.get('avg_clustering', 0):.3f}")

# Step 4: Create visualizations
print("\nStep 4: Creating visualizations...")

# UMAP plot
fig_umap = visualizer.plot_umap(adata, color_by="cell_type")
fig_umap.write_html("advanced_umap.html")
print("Saved: advanced_umap.html")

# Volcano plot
fig_volcano = visualizer.plot_volcano(deg_results)
fig_volcano.write_html("advanced_volcano.html")
print("Saved: advanced_volcano.html")

# Enrichment plot
if go_results:
    first_category = list(go_results.values())[0]
    fig_enrichment = visualizer.plot_enrichment(first_category, top_n=15)
    fig_enrichment.write_html("advanced_enrichment.html")
    print("Saved: advanced_enrichment.html")

# Network plot
hub_genes = [h[0] for h in hubs]
fig_network = visualizer.plot_network(G, hub_genes=hub_genes)
fig_network.write_html("advanced_network.html")
print("Saved: advanced_network.html")

# Step 5: Query databases
print("\nStep 5: Querying databases for hub genes...")
from e2sc.data import STRINGDatabase, HMDBDatabase, TRRUSTDatabase

string_db = STRINGDatabase()
hmdb_db = HMDBDatabase()
trrust_db = TRRUSTDatabase()

for gene in hub_genes[:3]:  # Top 3 hub genes
    print(f"\n{gene}:")
    
    # STRING interactions
    interactions = string_db.get_interactions(gene, min_score=0.7)
    if interactions:
        partners = [i.get("target_gene", i.get("source_gene")) for i in interactions[:5]]
        print(f"  Interacts with: {', '.join(partners)}")
    
    # HMDB metabolites
    metabolites = hmdb_db.get_metabolites(gene)
    if metabolites:
        met_names = [m.get("metabolite_name", "Unknown") for m in metabolites[:3]]
        print(f"  Associated metabolites: {', '.join(met_names)}")
    
    # TRRUST regulators
    regulators = trrust_db.get_regulators(gene)
    if regulators:
        tfs = [r.get("tf") for r in regulators[:3]]
        print(f"  Regulated by: {', '.join(tfs)}")

print("\n" + "="*50)
print("Advanced analysis completed!")
print("="*50)
