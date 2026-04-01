"""Register api/ folder tools into ToolRegistry."""

import sys
from pathlib import Path
from typing import Any

from e2sc.utils import get_logger

logger = get_logger(__name__)

_API_DIR = Path(__file__).parent.parent.parent / "api"
if str(_API_DIR) not in sys.path:
    sys.path.insert(0, str(_API_DIR))


def _load(module: str, cls: str):
    try:
        mod = __import__(module)
        for sub in module.split(".")[1:]:
            mod = getattr(mod, sub)
        instance = getattr(mod, cls)()
        logger.info(f"Loaded API: {cls}")
        return instance
    except Exception as e:
        logger.warning(f"Failed to load {cls}: {e}")
        return None


def register_api_tools(registry) -> None:
    """Register all api/ folder tools."""

    # 1. MyGene
    mg = _load("mygene_api", "MyGene_API")
    if mg:
        registry.register_tool("mygene_query_gene",
            lambda gene: str(mg.query_gene(gene)),
            "查询基因基本信息（Entrez ID/UniProt/Ensembl/位置）。输入：基因符号（如 TP53）",
            {"type":"object","properties":{"gene":{"type":"string"}},"required":["gene"]})
        registry.register_tool("mygene_get_by_id",
            lambda entrez_id: str(mg.get_gene_by_id(entrez_id)),
            "通过 Entrez Gene ID 获取基因详情",
            {"type":"object","properties":{"entrez_id":{"type":"string"}},"required":["entrez_id"]})

    # 2. STRING
    st = _load("string_api", "STRING_API")
    if st:
        registry.register_tool("string_get_interactions",
            lambda gene, limit=10: str(st.get_interactions(gene, limit=limit)),
            "查询 STRING 蛋白质相互作用网络，返回相互作用蛋白列表及评分。输入：基因符号",
            {"type":"object","properties":{"gene":{"type":"string"},"limit":{"type":"integer","default":10}},"required":["gene"]})
        registry.register_tool("string_get_network_image",
            lambda proteins: str(st.get_network_image(proteins)),
            "获取多个蛋白质的相互作用网络图 URL。输入：蛋白质名称列表",
            {"type":"object","properties":{"proteins":{"type":"array","items":{"type":"string"}}},"required":["proteins"]})

    # 3. QuickGO
    qg = _load("quickgo_api", "QuickGO_API")
    if qg:
        registry.register_tool("quickgo_get_annotations",
            lambda uniprot_id: str(qg.get_go_annotations(uniprot_id)),
            "获取基因 GO 功能注释（需要 UniProt ID，如 P04637）",
            {"type":"object","properties":{"uniprot_id":{"type":"string"}},"required":["uniprot_id"]})
        registry.register_tool("quickgo_get_term",
            lambda go_id: str(qg.get_go_term(go_id)),
            "获取 GO term 详细信息。输入：GO ID，如 GO:0006915",
            {"type":"object","properties":{"go_id":{"type":"string"}},"required":["go_id"]})

    # 4. Europe PMC
    epmc = _load("europepmc_api", "EuropePMC_API")
    if epmc:
        registry.register_tool("europepmc_search",
            lambda query, page_size=5: str(epmc.search_articles(query, page_size=page_size)),
            "搜索 Europe PMC 文献，返回标题/期刊/引用次数/DOI",
            {"type":"object","properties":{"query":{"type":"string"},"page_size":{"type":"integer","default":5}},"required":["query"]})

    # 5. ChEMBL
    chembl = _load("chembl_api", "ChEMBL_API")
    if chembl:
        registry.register_tool("chembl_search_compound",
            lambda name: str(chembl.search_compound(name)),
            "搜索 ChEMBL 药物/化合物，返回 ChEMBL ID、名称、临床阶段",
            {"type":"object","properties":{"name":{"type":"string"}},"required":["name"]})
        registry.register_tool("chembl_get_compound",
            lambda chembl_id: str(chembl.get_compound_by_id(chembl_id)),
            "通过 ChEMBL ID 获取化合物详细信息",
            {"type":"object","properties":{"chembl_id":{"type":"string"}},"required":["chembl_id"]})

    # 6. Ensembl
    ens = _load("ensembl_api", "Ensembl_API")
    if ens:
        registry.register_tool("ensembl_lookup_gene",
            lambda gene: str(ens.lookup_gene(gene)),
            "查询 Ensembl 基因组信息：Ensembl ID、染色体位置、基因描述",
            {"type":"object","properties":{"gene":{"type":"string"}},"required":["gene"]})
        registry.register_tool("ensembl_get_sequence",
            lambda ensembl_id: str(ens.get_sequence(ensembl_id)),
            "获取基因 DNA 序列。输入：Ensembl Gene ID，如 ENSG00000141510",
            {"type":"object","properties":{"ensembl_id":{"type":"string"}},"required":["ensembl_id"]})

    # 7. UniProt
    uniprot = _load("uniprot_api", "UniProtAPI")
    if uniprot:
        registry.register_tool("uniprot_search_gene",
            lambda gene: str(uniprot.search_by_gene(gene)),
            "搜索 UniProt 获取蛋白质信息，返回 Accession、功能、结构域",
            {"type":"object","properties":{"gene":{"type":"string"}},"required":["gene"]})
        registry.register_tool("uniprot_get_protein",
            lambda accession: str(uniprot.get_protein_by_accession(accession)),
            "通过 UniProt Accession 获取蛋白质详细信息。如 P04637",
            {"type":"object","properties":{"accession":{"type":"string"}},"required":["accession"]})

    # 8. PubChem
    pubchem = _load("pubchem_api", "PubChem_API")
    if pubchem:
        registry.register_tool("pubchem_search_compound",
            lambda name: str(pubchem.search_and_get_details(name)),
            "搜索 PubChem 化合物，返回 CID、分子式、分子量、SMILES",
            {"type":"object","properties":{"name":{"type":"string"}},"required":["name"]})

    # 9. PubMed
    pubmed = _load("pubmed_api", "PubMed_API")
    if pubmed:
        registry.register_tool("pubmed_search",
            lambda query, max_results=5: str(pubmed.search_and_get_details(query, max_results=max_results)),
            "搜索 PubMed 文献，返回 PMID、标题、摘要、作者、期刊",
            {"type":"object","properties":{"query":{"type":"string"},"max_results":{"type":"integer","default":5}},"required":["query"]})

    # ========== 新增 API ==========

    # 10. GTEx - 基因组织表达
    gtex = _load("gtex_api", "GTExAPI")
    if gtex:
        registry.register_tool("gtex_get_expression",
            lambda gene, max_results=50: str(gtex.get_gene_expression(gene, max_results=max_results)),
            "获取基因在各组织的表达数据（TPM）。输入：基因符号（如 TP53）",
            {"type":"object","properties":{"gene":{"type":"string"},"max_results":{"type":"integer","default":50}},"required":["gene"]})

    # 11. HumanBase - 基因组织特异性
    humanbase = _load("humanbase_api", "HumanBaseAPI")
    if humanbase:
        registry.register_tool("humanbase_get_expression",
            lambda gene, max_results=50: str(humanbase.get_gene_expression(gene, max_results=max_results)),
            "获取基因在各组织的表达特异性分数。输入：基因符号（如 TP53）",
            {"type":"object","properties":{"gene":{"type":"string"},"max_results":{"type":"integer","default":50}},"required":["gene"]})
        registry.register_tool("humanbase_get_tissue_network",
            lambda gene, tissue="brain": str(humanbase.get_tissue_network(gene, tissue)),
            "获取特定组织的基因功能网络。输入：基因符号和组织（如 brain/liver）",
            {"type":"object","properties":{"gene":{"type":"string"},"tissue":{"type":"string","default":"brain"}},"required":["gene"]})
        registry.register_tool("humanbase_search_genes",
            lambda query, max_results=20: str(humanbase.search_genes(query, max_results=max_results)),
            "搜索基因。输入：搜索关键词",
            {"type":"object","properties":{"query":{"type":"string"},"max_results":{"type":"integer","default":20}},"required":["query"]})

    # 12. GWAS Catalog
    gwas = _load("gwas_catalog_api", "GWASCatalogAPI")
    if gwas:
        registry.register_tool("gwas_catalog_search",
            lambda gene, max_results=10: str(gwas.get_gene_trait_associations(gene, max_results=max_results)),
            "查询GWAS Catalog获取基因相关的疾病/表型GWAS证据（rsID、p值、疾病性状、研究PMID）",
            {"type":"object","properties":{"gene":{"type":"string"},"max_results":{"type":"integer","default":10}},"required":["gene"]})

    # 13. BioGRID
    biogrid = _load("biogrid_api", "BioGRIDAPI")
    if biogrid:
        registry.register_tool("biogrid_interactions",
            lambda genes, max_results=50: str(biogrid.get_interactions(genes if isinstance(genes, list) else [genes], max_results=max_results)),
            "查询BioGRID获取实验验证的蛋白互作网络（包含实验系统、PMID、互作类型）",
            {"type":"object","properties":{"genes":{"type":"array","items":{"type":"string"}},"max_results":{"type":"integer","default":50}},"required":["genes"]})

    # 14. CIViC
    civic = _load("civic_api", "CIViCAPI")
    if civic:
        registry.register_tool("civic_gene_variants",
            lambda gene, max_results=10: str(civic.search_variants(gene, max_results=max_results)),
            "查询CIViC获取癌症基因相关的变异及临床证据（therapy/diagnosis/prognosis/FDA）",
            {"type":"object","properties":{"gene":{"type":"string"},"max_results":{"type":"integer","default":10}},"required":["gene"]})

    # 15. Alliance of Genome Resources
    alliance = _load("alliance_api", "AllianceAPI")
    if alliance:
        registry.register_tool("alliance_cross_species",
            lambda query: str(alliance.search_cross_species(query)),
            "跨物种搜索Alliance（人类、小鼠、斑马鱼、果蝇、线虫）的基因/蛋白",
            {"type":"object","properties":{"query":{"type":"string"}},"required":["query"]})
        registry.register_tool("alliance_homologs",
            lambda gene, species="human": str(alliance.get_homologs(gene, species=species)),
            "查询Alliance获取基因的同源基因",
            {"type":"object","properties":{"gene":{"type":"string"},"species":{"type":"string","default":"human"}},"required":["gene"]})

    new_prefixes = ('gtex_', 'humanbase_', 'gwas_', 'biogrid_', 'civic_', 'alliance_')
    total = len([t for t in registry.tools if t.startswith(('mygene_','string_','quickgo_','europepmc_','chembl_','ensembl_','uniprot_','pubchem_','pubmed_') + new_prefixes)])
    logger.info(f"Registered {total} api/ folder tools")
