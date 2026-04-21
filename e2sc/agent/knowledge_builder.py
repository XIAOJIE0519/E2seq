"""Gene Knowledge Base Builder - 预先构建基因知识库模块。

功能：
1. 接受基因列表，调用18个API（跳过文献）预先构建知识库
2. 支持异步构建和进度查询
3. 保存知识库到文件，支持增量更新
4. 与Synthesizer集成，实现实时文献查询

使用流程：
1. 用户筛选基因后 → 调用 /api/knowledge/build 构建知识库
2. 后台异步构建 → 用户可查询构建进度
3. 构建完成 → 用户提问时基于知识库 + 实时文献回答
"""

import json
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from e2sc.utils import get_logger

logger = get_logger(__name__)

# 知识库存储目录
_KNOWLEDGE_DIR = Path(__file__).parent.parent.parent / "_knowledge_bases"
_KNOWLEDGE_DIR.mkdir(exist_ok=True)


class GeneKnowledgeBuilder:
    """基因知识库构建器。
    
    在后台预先构建基因知识库，包含18个API的数据（不含文献）。
    文献在用户提问时实时查询。
    """
    
    def __init__(
        self,
        string_db=None,
        hmdb_db=None,
        trrust_db=None,
        gutmgene_db=None,
        api_clients: Dict[str, Any] = None,
    ):
        """初始化构建器。
        
        Args:
            string_db: STRING数据库实例
            hmdb_db: HMDB数据库实例  
            trrust_db: TRRUST数据库实例
            gutmgene_db: GUTMGENE数据库实例
            api_clients: API客户端字典
        """
        self.string_db = string_db
        self.hmdb_db = hmdb_db
        self.trrust_db = trrust_db
        self.gutmgene_db = gutmgene_db
        self.api_clients = api_clients or {}
        
        # 正在构建的知识库 {build_id: BuildStatus}
        self._builds: Dict[str, "BuildStatus"] = {}
        self._lock = threading.Lock()

    def bind_agent(self, agent: Any) -> None:
        """从 E2scAgent 实例绑定数据库与 API 客户端（多会话共用同一构建器时每次构建前调用）。"""
        if agent is None:
            return
        self.string_db = getattr(agent, "string_db", None) or self.string_db
        self.hmdb_db = getattr(agent, "hmdb_db", None) or self.hmdb_db
        self.trrust_db = getattr(agent, "trrust_db", None) or self.trrust_db
        self.gutmgene_db = getattr(agent, "gutmgene_db", None) or self.gutmgene_db
        ac = getattr(agent, "api_clients", None)
        if ac:
            self.api_clients = ac
    
    def start_build(
        self,
        genes: List[str],
        session_id: str,
        metadata: Dict[str, Any] = None,
        on_complete: Optional[Callable[[str, str, Dict[str, Any]], None]] = None,
    ) -> str:
        """启动异步知识库构建。
        
        Args:
            genes: 基因列表
            session_id: 会话ID（用于标识知识库）
            metadata: 附加元数据（如数据集信息）
            
        Returns:
            build_id: 构建任务ID
        """
        build_id = f"{session_id}_{int(time.time() * 1000)}"
        
        status = BuildStatus(
            build_id=build_id,
            session_id=session_id,
            genes=genes,
            metadata=metadata or {},
            status="pending",
            progress=0.0,
            total_genes=len(genes),
            processed_genes=0,
            created_at=datetime.now().isoformat(),
            completed_at=None,
            knowledge={},
            errors=[],
        )
        
        with self._lock:
            self._builds[build_id] = status
        
        # 启动后台构建线程
        thread = threading.Thread(
            target=self._build_knowledge_base,
            args=(build_id, on_complete),
            daemon=True,
        )
        thread.start()
        
        logger.info(f"Started knowledge base build: {build_id}, {len(genes)} genes")
        return build_id
    
    def get_status(self, build_id: str) -> Optional[Dict[str, Any]]:
        """获取构建状态。
        
        Args:
            build_id: 构建任务ID
            
        Returns:
            状态字典，如果不存在返回None
        """
        with self._lock:
            build = self._builds.get(build_id)
            if not build:
                return None
            
            return {
                "build_id": build.build_id,
                "session_id": build.session_id,
                "status": build.status,  # pending, building, completed, failed
                "progress": build.progress,
                "total_genes": build.total_genes,
                "processed_genes": build.processed_genes,
                "created_at": build.created_at,
                "completed_at": build.completed_at,
                "error_count": len(build.errors),
                "errors": build.errors[-5:],  # 最近5个错误
            }
    
    def get_knowledge(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取已构建的知识库。
        
        Args:
            session_id: 会话ID
            
        Returns:
            知识库字典，如果不存在或未完成返回None
        """
        # 先检查内存中的构建
        with self._lock:
            for build in self._builds.values():
                if build.session_id == session_id and build.status == "completed":
                    return build.knowledge
        
        # 再检查磁盘缓存
        cache_path = _KNOWLEDGE_DIR / f"{session_id}.json"
        if cache_path.exists():
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("knowledge", {})
            except Exception as e:
                logger.warning(f"Failed to load cached knowledge: {e}")
        
        return None
    
    def save_knowledge(self, session_id: str, knowledge: Dict[str, Any], metadata: Dict[str, Any] = None) -> bool:
        """保存知识库到磁盘。
        
        Args:
            session_id: 会话ID
            knowledge: 知识库数据
            metadata: 附加元数据
            
        Returns:
            是否成功
        """
        try:
            cache_path = _KNOWLEDGE_DIR / f"{session_id}.json"
            data = {
                "session_id": session_id,
                "knowledge": knowledge,
                "metadata": metadata or {},
                "saved_at": datetime.now().isoformat(),
                "gene_count": len(knowledge.get("genes", {})),
            }
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved knowledge base: {session_id}, {data['gene_count']} genes")
            return True
        except Exception as e:
            logger.error(f"Failed to save knowledge base: {e}")
            return False
    
    def delete_knowledge(self, session_id: str) -> bool:
        """删除知识库。
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否成功
        """
        # 删除内存中的构建
        with self._lock:
            for build_id, build in list(self._builds.items()):
                if build.session_id == session_id:
                    del self._builds[build_id]
        
        # 删除磁盘缓存
        cache_path = _KNOWLEDGE_DIR / f"{session_id}.json"
        if cache_path.exists():
            try:
                cache_path.unlink()
                return True
            except Exception:
                pass
        
        return True
    
    def _build_knowledge_base(
        self,
        build_id: str,
        on_complete: Optional[Callable[[str, str, Dict[str, Any]], None]] = None,
    ) -> None:
        """后台构建知识库。
        
        Args:
            build_id: 构建任务ID
            on_complete: 可选回调 ``(session_id, build_id, knowledge)``，构建成功并完成落盘后调用。
        """
        with self._lock:
            build = self._builds.get(build_id)
            if not build:
                return
            build.status = "building"
        
        try:
            genes = build.genes
            total = len(genes)
            knowledge = {
                "genes": {},
                "retrieval_stats": {
                    "vector_db_success": False,
                    "genes_queried": total,
                    "genes_with_info": 0,
                    "databases_queried": [
                        "UniProt", "MyGene", "Ensembl", "QuickGO", "ChEMBL",
                        "GTEx", "HumanBase", "GWAS Catalog", "BioGRID", "CIViC",
                        "Alliance", "STRING", "HMDB", "TRRUST", "GUTMGENE"
                    ],
                },
                "metadata": build.metadata,
            }
            
            for i, gene in enumerate(genes):
                try:
                    gene_info = self._retrieve_gene_info(gene)
                    if gene_info:
                        knowledge["genes"][gene] = gene_info
                        build.processed_genes += 1
                        if self._has_useful_info(gene_info):
                            knowledge["retrieval_stats"]["genes_with_info"] += 1
                    else:
                        knowledge["genes"][gene] = {
                            "gene": gene,
                            "status": "no_information_found"
                        }
                        build.processed_genes += 1
                    
                    # 更新进度
                    build.progress = (i + 1) / total
                    
                except Exception as e:
                    logger.warning(f"Failed to retrieve {gene}: {e}")
                    build.errors.append(f"{gene}: {str(e)}")
                    knowledge["genes"][gene] = {
                        "gene": gene,
                        "status": "error",
                        "error": str(e)
                    }
                    build.processed_genes += 1
            
            # 保存结果
            build.knowledge = knowledge
            build.status = "completed"
            build.completed_at = datetime.now().isoformat()
            build.progress = 1.0
            
            # 持久化到磁盘
            self.save_knowledge(build.session_id, knowledge, build.metadata)
            
            logger.info(
                f"Knowledge base build completed: {build_id}, "
                f"{knowledge['retrieval_stats']['genes_with_info']}/{total} genes with info"
            )
            if on_complete:
                try:
                    on_complete(build.session_id, build_id, knowledge)
                except Exception as cb_e:
                    logger.exception(f"on_complete callback failed: {cb_e}")
            
        except Exception as e:
            logger.error(f"Knowledge base build failed: {build_id}, {e}")
            build.status = "failed"
            build.errors.append(f"Fatal: {str(e)}")
            build.completed_at = datetime.now().isoformat()
    
    def _retrieve_gene_info(self, gene: str) -> Dict[str, Any]:
        """检索单个基因的信息（跳过文献API）。
        
        Args:
            gene: 基因符号
            
        Returns:
            基因信息字典
        """
        info = {
            "gene": gene,
            "interactions": [],
            "metabolites": [],
            "regulators": [],
            "targets": [],
            "microbiome": [],
            "uniprot": None,
        }
        
        # STRING interactions
        if self.string_db:
            try:
                with self.string_db as db:
                    interactions = db.get_interactions(gene, min_score=0.5)
                    info["interactions"] = [
                        {
                            "partner": i.get("target_gene") if i.get("source_gene") == gene else i.get("source_gene"),
                            "score": i.get("score", 0)
                        }
                        for i in interactions[:10]
                    ]
            except Exception as e:
                logger.warning(f"STRING query failed for {gene}: {e}")
        
        # HMDB metabolites
        if self.hmdb_db:
            try:
                with self.hmdb_db as db:
                    metabolites = db.get_metabolites(gene)
                    info["metabolites"] = [
                        {"id": m.get("metabolite_id"), "name": m.get("metabolite_name", "Unknown")}
                        for m in metabolites[:5]
                    ]
            except Exception as e:
                logger.warning(f"HMDB query failed for {gene}: {e}")
        
        # TRRUST regulators
        if self.trrust_db:
            try:
                with self.trrust_db as db:
                    regulators = db.get_regulators(gene)
                    info["regulators"] = [
                        {"tf": r.get("tf"), "mode": r.get("mode", "Unknown")}
                        for r in regulators[:5]
                    ]
                    targets = db.get_targets(gene)
                    info["targets"] = [
                        {"gene": t.get("target_gene"), "mode": t.get("mode", "Unknown")}
                        for t in targets[:5]
                    ]
            except Exception as e:
                logger.warning(f"TRRUST query failed for {gene}: {e}")
        
        # GUTMGENE microbiome
        if self.gutmgene_db:
            try:
                with self.gutmgene_db as db:
                    microbes = db.get_microbes(gene)
                    info["microbiome"] = [
                        {"microbe": m.get("gut_microbiota"), "condition": m.get("condition", "Unknown")}
                        for m in microbes[:3]
                    ]
            except Exception as e:
                logger.warning(f"GUTMGENE query failed for {gene}: {e}")
        
        # UniProt API
        if self.api_clients.get("uniprot"):
            try:
                uniprot_data = self.api_clients["uniprot"].get_protein_info(gene)
                if uniprot_data and "results" in uniprot_data and len(uniprot_data["results"]) > 0:
                    entry = uniprot_data["results"][0]
                    function_text = ""
                    for comment in entry.get("comments", []):
                        if comment.get("commentType") == "FUNCTION":
                            texts = comment.get("text", [])
                            if texts:
                                function_text = texts[0].get("value", "")[:300]
                                break
                    info["uniprot"] = {
                        "accession": entry.get("primaryAccession"),
                        "protein_name": entry.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value", ""),
                        "function": function_text,
                    }
            except Exception as e:
                logger.warning(f"UniProt query failed for {gene}: {e}")
        
        # MyGene API
        if self.api_clients.get("mygene"):
            try:
                mg = self.api_clients["mygene"].get_gene_info(gene)
                if mg and mg.get("status") == "success":
                    info["mygene"] = {
                        "symbol": mg.get("symbol"),
                        "name": mg.get("name"),
                        "entrez_id": mg.get("entrez_id"),
                        "type": mg.get("type_of_gene")
                    }
            except Exception as e:
                logger.warning(f"MyGene query failed for {gene}: {e}")
        
        # Ensembl API
        if self.api_clients.get("ensembl"):
            try:
                ens = self.api_clients["ensembl"].get_gene_info(gene)
                if ens and ens.get("status") == "success":
                    info["ensembl"] = {
                        "ensembl_id": ens.get("ensembl_id"),
                        "description": ens.get("description", "")[:200],
                        "biotype": ens.get("biotype")
                    }
            except Exception as e:
                logger.warning(f"Ensembl query failed for {gene}: {e}")
        
        # QuickGO API
        if self.api_clients.get("quickgo"):
            try:
                go = self.api_clients["quickgo"].get_go_terms(gene)
                if go and go.get("status") == "success" and go.get("total_annotations", 0) > 0:
                    anns = go.get("annotations", [])
                    info["go_terms"] = [
                        {"go_id": a.get("go_id"), "aspect": a.get("go_aspect")}
                        for a in anns[:8]
                    ]
            except Exception as e:
                logger.warning(f"QuickGO query failed for {gene}: {e}")
        
        # ChEMBL API
        if self.api_clients.get("chembl"):
            try:
                ch = self.api_clients["chembl"].search_target(gene)
                targets = ch.get("targets", []) if isinstance(ch, dict) else []
                if targets:
                    info["chembl_targets"] = [
                        {"chembl_id": t.get("target_chembl_id"), "name": t.get("pref_name", "")[:100]}
                        for t in targets[:5]
                    ]
            except Exception as e:
                logger.warning(f"ChEMBL query failed for {gene}: {e}")
        
        # GTEx API
        if self.api_clients.get("gtex"):
            try:
                gtex = self.api_clients["gtex"].get_gene_expression(gene, max_results=5)
                if gtex and gtex.get("status") == "success" and gtex.get("total", 0) > 0:
                    info["gtex"] = {
                        "total_tissues": gtex.get("total"),
                        "top_tissues": [
                            {"tissue": r.get("tissue"), "median": r.get("median_expression")}
                            for r in gtex.get("records", [])[:5]
                        ]
                    }
            except Exception as e:
                logger.warning(f"GTEx query failed for {gene}: {e}")
        
        # HumanBase API
        if self.api_clients.get("humanbase"):
            try:
                hb = self.api_clients["humanbase"].get_tissue_network(gene, "brain")
                if hb and hb.get("status") == "success" and hb.get("total", 0) > 0:
                    info["humanbase"] = {
                        "tissue": "brain",
                        "network_genes": [g.get("gene") for g in hb.get("network_genes", [])[:10]]
                    }
            except Exception as e:
                logger.warning(f"HumanBase query failed for {gene}: {e}")
        
        # GWAS Catalog API
        if self.api_clients.get("gwas"):
            try:
                gw = self.api_clients["gwas"].get_gene_trait_associations(gene)
                if gw and gw.get("status") == "success" and gw.get("total", 0) > 0:
                    assocs = gw.get("associations", [])
                    info["gwas"] = [
                        {"trait": a.get("trait"), "pvalue": a.get("p_value")}
                        for a in assocs[:5]
                    ]
            except Exception as e:
                logger.warning(f"GWAS query failed for {gene}: {e}")
        
        # BioGRID API
        if self.api_clients.get("biogrid"):
            try:
                bg = self.api_clients["biogrid"].get_interactions([gene])
                if bg and bg.get("status") == "success" and bg.get("total", 0) > 0:
                    ints = bg.get("interactions", [])
                    info["biogrid"] = [
                        {
                            "partner": i.get("gene_b") if i.get("gene_a") == gene else i.get("gene_a"),
                            "evidence": i.get("evidence_type", "")
                        }
                        for i in ints[:8]
                    ]
            except Exception as e:
                logger.warning(f"BioGRID query failed for {gene}: {e}")
        
        # CIViC API
        if self.api_clients.get("civic"):
            try:
                cv = self.api_clients["civic"].search_variants(gene)
                if cv and cv.get("status") == "success" and cv.get("total", 0) > 0:
                    info["civic"] = {
                        "total_variants": cv.get("total"),
                        "variants": [
                            {"name": v.get("name"), "disease": v.get("disease", "")}
                            for v in cv.get("variants", [])[:5]
                        ]
                    }
            except Exception as e:
                logger.warning(f"CIViC query failed for {gene}: {e}")
        
        # Alliance API
        if self.api_clients.get("alliance"):
            try:
                al = self.api_clients["alliance"].get_homologs(gene)
                if al and al.get("status") == "success" and al.get("total", 0) > 0:
                    info["alliance"] = {
                        "total_homologs": al.get("total"),
                        "homologs": [
                            {"species": h.get("species"), "symbol": h.get("symbol")}
                            for h in al.get("homologs", [])[:5]
                        ]
                    }
            except Exception as e:
                logger.warning(f"Alliance query failed for {gene}: {e}")
        
        return info
    
    def _has_useful_info(self, gene_info: Dict[str, Any]) -> bool:
        """检查基因信息是否有用。"""
        if not gene_info or gene_info.get("status") in ("no_information_found", "error"):
            return False
        
        return bool(
            gene_info.get("interactions") or
            gene_info.get("metabolites") or
            gene_info.get("regulators") or
            gene_info.get("targets") or
            gene_info.get("microbiome") or
            gene_info.get("uniprot") or
            gene_info.get("mygene") or
            gene_info.get("ensembl") or
            gene_info.get("go_terms") or
            gene_info.get("chembl_targets") or
            gene_info.get("gtex") or
            gene_info.get("humanbase") or
            gene_info.get("gwas") or
            gene_info.get("biogrid") or
            gene_info.get("civic") or
            gene_info.get("alliance")
        )


class BuildStatus:
    """构建状态数据类。"""
    
    def __init__(
        self,
        build_id: str,
        session_id: str,
        genes: List[str],
        metadata: Dict[str, Any],
        status: str,
        progress: float,
        total_genes: int,
        processed_genes: int,
        created_at: str,
        completed_at: Optional[str],
        knowledge: Dict[str, Any],
        errors: List[str],
    ):
        self.build_id = build_id
        self.session_id = session_id
        self.genes = genes
        self.metadata = metadata
        self.status = status
        self.progress = progress
        self.total_genes = total_genes
        self.processed_genes = processed_genes
        self.created_at = created_at
        self.completed_at = completed_at
        self.knowledge = knowledge
        self.errors = errors


# 全局构建器实例
_builder_instance: Optional[GeneKnowledgeBuilder] = None
_builder_lock = threading.Lock()


def get_knowledge_builder(
    string_db=None,
    hmdb_db=None,
    trrust_db=None,
    gutmgene_db=None,
    api_clients: Dict[str, Any] = None,
) -> GeneKnowledgeBuilder:
    """获取全局知识库构建器实例。
    
    Args:
        string_db: STRING数据库实例
        hmdb_db: HMDB数据库实例
        trrust_db: TRRUST数据库实例
        gutmgene_db: GUTMGENE数据库实例
        api_clients: API客户端字典
        
    Returns:
        GeneKnowledgeBuilder实例
    """
    global _builder_instance
    
    with _builder_lock:
        if _builder_instance is None:
            _builder_instance = GeneKnowledgeBuilder(
                string_db=string_db,
                hmdb_db=hmdb_db,
                trrust_db=trrust_db,
                gutmgene_db=gutmgene_db,
                api_clients=api_clients,
            )
        return _builder_instance
