"""智能查询构建器 - 根据用户问题和分析结果生成优化的搜索关键词。

功能：
1. LLM驱动的意图分析
2. 专业术语映射
3. 针对不同数据源的定制化关键词
"""

from typing import Any, Dict, List, Optional, Tuple
from e2sc.utils import get_logger

logger = get_logger(__name__)

# =============================================================================
# 专业术语映射表 - 用户输入词 -> PubMed/EuropePMC搜索词
# =============================================================================

_DRUG_TERMS = [
    # 药物相关
    "drug", "drugs", "drug target", "drug targets", "target", "targets",
    "药物", "靶点", "药物靶点", "药物研发", "小分子", "抑制剂", "激活剂",
    "agonist", "antagonist", "agonists", "antagonists", "inhibitor",
    "inhibitors", "activator", "activators", "modulator", "modulators",
    "compound", "compounds", "molecule", "molecules", "ligand", "ligands",
    "pharmacology", "pharmacological", "therapeutic", "therapeutics",
    "therapy", "treatment", "clinical trial", "ic50", "ki", "kd",
    "chembl", "binding affinity", "drug discovery", "lead compound",
    "biologics", "monoclonal antibody", "adc", "antibody drug conjugate",
]

_DISEASE_TERMS = [
    # 疾病相关
    "disease", "diseases", "disorder", "pathology", "pathological",
    "疾病", "病理学", "病理", "临床", "clinical", "syndrome",
    "cancer", "tumor", "carcinoma", "tumorigenesis", "oncology",
    "oncogenic", "carcinogenesis", "malignant", "benign", "metastasis",
    "autoimmune", "inflammatory", "inflammation", "immune",
    "neurodegenerative", "alzheimer", "parkinson", "diabetes",
    "cardiovascular", "heart disease", "obesity", "metabolic",
    "fibrosis", "fibrotic", "apoptosis", "necrosis", "autophagy",
    "pathogenesis", "etiology", "prognosis", "diagnosis",
]

_GENETIC_TERMS = [
    # 基因/遗传相关
    "gene", "genes", "genetic", "genomics", "genome", "genetic variant",
    "基因", "基因组", "遗传", "变异", "突变", "variant", "variants",
    "mutation", "mutations", "polymorphism", "snv", "snp", "indel",
    "expression", "expressed", "upregulated", "downregulated",
    "表达", "上调", "下调", "transcription", "transcript",
    "mrna", "protein", "pathway", "pathways", "通路", "信号通路",
]

_PATHWAY_TERMS = [
    # 通路相关
    "pathway", "pathways", "signal transduction", "signaling",
    "通路", "信号通路", "信号转导", "cascade", "cascade",
    "mapk", "pi3k", "akt", "nfkb", "jak-stat", "wnt", "hedgehog",
    "notch", "bmp", "tgfb", "tnf", "il-", "interleukin", "cytokine",
    "receptor", "receptors", "tyrosine kinase", "serine/threonine",
    "g protein coupled", "gpcr", "ion channel", "nuclear receptor",
]

_INTERACTION_TERMS = [
    # 互作相关
    "interaction", "interactions", "binding", "complex", "ppi",
    "互作", "相互作用", "结合", "蛋白互作", "protein protein",
    "network", "networks", "network analysis", "hub gene", "hub genes",
    "网络", "网络分析", "hub", "regulatory", "regulation",
    "coexpression", "co-expression", "co-regulatory",
]

_EXPRESSION_TERMS = [
    # 表达相关
    "expression", "expressed", "expression profile", "expression pattern",
    "表达", "表达谱", "tissue", "tissues", "organ", "specificity",
    "tissue-specific", "cell type", "cell types", "single cell",
    "单细胞", "scRNA", "atlas", "database", "transcriptomics",
    "rna-seq", "rna sequencing", "microarray", "GEO", "tpm", "fpkm",
]

_DRUG_TERMS_CHINESE = [
    "药物", "靶点", "抑制剂", "激活剂", "拮抗剂", "激动剂",
    "小分子", "化合物", "生物制剂", "抗体", "ADC", "免疫治疗",
    "化疗", "靶向治疗", "耐药", "药物研发", "临床试验",
]

_DISEASE_TERMS_CHINESE = [
    "疾病", "肿瘤", "癌症", " carcinoma", "腺癌", "转移",
    "炎症", "自身免疫", "退行性", "纤维化", "代谢",
    "心脑血管", "神经系统", "病理", "临床", "预后",
]

# =============================================================================
# 意图类型枚举
# =============================================================================

class QueryIntent:
    """查询意图类型"""
    DRUG_TARGET = "drug_target"           # 药物靶点
    DISEASE = "disease"                   # 疾病机制
    PATHWAY = "pathway"                   # 通路机制
    INTERACTION = "interaction"           # 蛋白互作
    EXPRESSION = "expression"             # 组织表达
    GENETIC = "genetic"                   # 遗传变异
    COMPREHENSIVE = "comprehensive"        # 综合分析
    UNKNOWN = "unknown"                   # 未知


# 所有意图取值（QueryIntent 为普通类，不可 `for x in QueryIntent`，否则会 TypeError）
ALL_QUERY_INTENTS: Tuple[str, ...] = (
    QueryIntent.DRUG_TARGET,
    QueryIntent.DISEASE,
    QueryIntent.PATHWAY,
    QueryIntent.INTERACTION,
    QueryIntent.EXPRESSION,
    QueryIntent.GENETIC,
    QueryIntent.COMPREHENSIVE,
    QueryIntent.UNKNOWN,
)


# =============================================================================
# 意图检测规则
# =============================================================================

_INTENT_RULES: List[Tuple[List[str], QueryIntent, float]] = [
    # (关键词列表, 意图类型, 权重倍数)
    (_DRUG_TERMS + _DRUG_TERMS_CHINESE, QueryIntent.DRUG_TARGET, 2.0),
    (_DISEASE_TERMS + _DISEASE_TERMS_CHINESE, QueryIntent.DISEASE, 1.5),
    (_PATHWAY_TERMS, QueryIntent.PATHWAY, 1.5),
    (_INTERACTION_TERMS, QueryIntent.INTERACTION, 1.5),
    (_EXPRESSION_TERMS, QueryIntent.EXPRESSION, 1.3),
    (_GENETIC_TERMS, QueryIntent.GENETIC, 1.2),
]


# =============================================================================
# 智能查询构建器
# =============================================================================

class SmartQueryBuilder:
    """智能查询构建器 - 根据问题类型生成优化的搜索关键词"""
    
    def __init__(self, llm=None):
        """初始化
        
        Args:
            llm: 可选的LLM实例，用于生成复杂查询
        """
        self.llm = llm
    
    def detect_intent(self, question: str, analysis_results: Dict[str, Any] = None) -> Tuple[QueryIntent, float, Dict[str, Any]]:
        """检测用户问题的意图
        
        Args:
            question: 用户问题
            analysis_results: 分析结果（可选）
            
        Returns:
            (意图类型, 置信度, 详细信息字典)
        """
        q_lower = question.lower()
        intent_scores: Dict[str, float] = {i: 0.0 for i in ALL_QUERY_INTENTS}
        
        # 1. 基于规则的意图检测
        for keywords, intent, weight in _INTENT_RULES:
            for kw in keywords:
                if kw.lower() in q_lower:
                    intent_scores[intent] += weight
        
        # 2. 检测综合分析意图
        comprehensive_keywords = [
            "综合", "全面", "整体", "解读", "分析", "comprehensive",
            "overall", "analyze", "summary", "summarize", "全部",
            "所有", "整体分析", "深度分析",
        ]
        if any(kw in q_lower for kw in comprehensive_keywords):
            intent_scores[QueryIntent.COMPREHENSIVE] = sum(intent_scores.values()) * 0.5
        
        # 3. 基于分析结果的意图增强
        if analysis_results:
            if analysis_results.get("enrichment"):
                intent_scores[QueryIntent.PATHWAY] += 0.5
            if analysis_results.get("network"):
                intent_scores[QueryIntent.INTERACTION] += 0.5
        
        # 4. 确定最终意图
        max_intent = QueryIntent.UNKNOWN
        max_score = 0.0
        for intent, score in intent_scores.items():
            if intent != QueryIntent.COMPREHENSIVE and score > max_score:
                max_score = score
                max_intent = intent
        
        # 如果综合意图得分高，使用综合意图
        if intent_scores[QueryIntent.COMPREHENSIVE] > max_score * 0.8:
            max_intent = QueryIntent.COMPREHENSIVE
        
        confidence = min(max_score / 3.0, 1.0)  # 归一化到0-1
        
        details = {
            "intent_scores": intent_scores,
            "detected_keywords": self._extract_detected_keywords(q_lower),
            "analysis_context": self._extract_analysis_context(analysis_results),
        }
        
        logger.info(f"[SmartQuery] Intent detected: {max_intent} (confidence={confidence:.2f})")
        
        return max_intent, confidence, details
    
    def _extract_detected_keywords(self, question_lower: str) -> Dict[str, List[str]]:
        """提取检测到的关键词类别"""
        detected = {}
        all_terms = [
            ("drug", _DRUG_TERMS + _DRUG_TERMS_CHINESE),
            ("disease", _DISEASE_TERMS + _DISEASE_TERMS_CHINESE),
            ("pathway", _PATHWAY_TERMS),
            ("interaction", _INTERACTION_TERMS),
            ("expression", _EXPRESSION_TERMS),
            ("genetic", _GENETIC_TERMS),
        ]
        for category, terms in all_terms:
            matched = [kw for kw in terms if kw.lower() in question_lower]
            if matched:
                detected[category] = matched
        return detected
    
    def _extract_analysis_context(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """从分析结果中提取上下文"""
        if not results:
            return {}
        
        context = {}
        
        # DEG结果
        if results.get("deg"):
            deg_blob = results["deg"]
            if isinstance(deg_blob, dict):
                deg_df = deg_blob.get("results")
                if deg_df is not None and hasattr(deg_df, "columns") and "names" in deg_df.columns:
                    context["top_genes"] = deg_df["names"].head(10).tolist()
        
        # 富集结果
        if results.get("enrichment"):
            context["has_enrichment"] = True
        
        # 网络结果
        if results.get("network"):
            context["has_network"] = True
        
        return context
    
    def build_search_keywords(
        self,
        question: str,
        genes: List[str],
        intent: QueryIntent,
        analysis_results: Dict[str, Any] = None,
    ) -> Dict[str, List[str]]:
        """为不同数据源构建优化的搜索关键词
        
        Args:
            question: 用户问题
            genes: 相关基因列表
            intent: 意图类型
            analysis_results: 分析结果
            
        Returns:
            数据源到关键词列表的映射
        """
        search_keywords: Dict[str, List[str]] = {
            "pubmed": [],
            "europepmc": [],
            "uniprot": [],
            "chembl": [],
            "string": [],
            "reactome": [],
            "quickgo": [],
        }
        
        q_lower = question.lower()
        
        # =============================================================
        # 1. PubMed/EuropePMC 关键词构建（最重要）
        # =============================================================
        
        # 基于意图添加专业术语
        intent_terms = self._get_intent_terms(intent)
        
        # 添加用户问题中已有的专业术语
        question_terms = []
        for category, terms in [
            ("drug", _DRUG_TERMS + _DRUG_TERMS_CHINESE),
            ("disease", _DISEASE_TERMS + _DISEASE_TERMS_CHINESE),
            ("pathway", _PATHWAY_TERMS),
            ("genetic", _GENETIC_TERMS),
        ]:
            matched = [kw for kw in terms if kw.lower() in q_lower]
            question_terms.extend(matched)
        
        # 构建搜索查询
        base_queries = []
        
        # 查询类型1: 基因 + 意图术语
        for gene in genes[:5]:  # 最多5个基因
            for term in intent_terms[:3]:  # 最多3个术语
                base_queries.append(f'({gene}[Title/Abstract]) AND ({term}[Title/Abstract])')
        
        # 查询类型2: 基因 + 疾病 + 意图
        if intent == QueryIntent.DRUG_TARGET:
            for gene in genes[:3]:
                for disease in self._extract_diseases(q_lower)[:2]:
                    for term in intent_terms[:2]:
                        base_queries.append(
                            f'({gene}[Title/Abstract]) AND ({disease}[Title/Abstract]) '
                            f'AND ({term}[Title/Abstract])'
                        )
        
        # 查询类型3: 仅意图术语（用于发现相关基因）
        if intent == QueryIntent.DISEASE or intent == QueryIntent.COMPREHENSIVE:
            for term in intent_terms[:5]:
                base_queries.append(f'{term}[Title/Abstract]')
        
        search_keywords["pubmed"] = base_queries[:10]  # 限制查询数量
        search_keywords["europepmc"] = base_queries[:10]
        
        # =============================================================
        # 2. ChEMBL 关键词（药物靶点）
        # =============================================================
        if intent in [QueryIntent.DRUG_TARGET, QueryIntent.COMPREHENSIVE]:
            for gene in genes[:5]:
                search_keywords["chembl"].append(gene)
            # 添加药物相关术语
            search_keywords["chembl"].extend(intent_terms[:5])
        
        # =============================================================
        # 3. STRING/UniProt 关键词
        # =============================================================
        if intent in [QueryIntent.INTERACTION, QueryIntent.COMPREHENSIVE]:
            for gene in genes[:10]:
                search_keywords["string"].append(gene)
        
        if intent in [QueryIntent.DRUG_TARGET, QueryIntent.PATHWAY, QueryIntent.COMPREHENSIVE]:
            for gene in genes[:5]:
                search_keywords["uniprot"].append(gene)
        
        # =============================================================
        # 4. Reactome/QuickGO 关键词
        # =============================================================
        if intent in [QueryIntent.PATHWAY, QueryIntent.COMPREHENSIVE]:
            # 从问题中提取通路相关术语
            pathway_terms = [t for t in _PATHWAY_TERMS if t.lower() in q_lower]
            search_keywords["reactome"].extend(pathway_terms)
            search_keywords["quickgo"].extend(pathway_terms)
        
        logger.info(f"[SmartQuery] Built {len(search_keywords['pubmed'])} PubMed queries")
        
        return search_keywords
    
    def _get_intent_terms(self, intent: QueryIntent) -> List[str]:
        """根据意图类型获取专业术语"""
        intent_map = {
            QueryIntent.DRUG_TARGET: [
                "drug target", "therapeutic target", "druggable",
                "drug discovery", "pharmacological", "binding site",
                "enzyme inhibitor", "receptor agonist", "receptor antagonist",
                "clinical trial", "biomarker", "IC50", "drug response",
                "药物靶点", "药物研发", "临床试验",
            ],
            QueryIntent.DISEASE: [
                "pathogenesis", "disease mechanism", "clinical",
                "prognosis", "diagnosis", "biomarker",
                "疾病机制", "临床意义", "预后",
            ],
            QueryIntent.PATHWAY: [
                "pathway", "signaling", "mechanism",
                "signal transduction", "cascade",
                "信号通路", "调控机制",
            ],
            QueryIntent.INTERACTION: [
                "protein interaction", "PPI network", "binding",
                "complex formation", "coexpression",
                "蛋白互作", "网络分析",
            ],
            QueryIntent.EXPRESSION: [
                "expression", "tissue specificity", "cell type",
                "transcriptomics", "atlas",
                "组织表达", "细胞类型特异性",
            ],
            QueryIntent.GENETIC: [
                "mutation", "variant", "polymorphism",
                "genetic association", "risk factor",
                "基因变异", "遗传风险",
            ],
            QueryIntent.COMPREHENSIVE: [
                "drug target", "disease", "pathway", "mechanism",
                "expression", "interaction", "clinical",
                "治疗", "机制", "通路",
            ],
            QueryIntent.UNKNOWN: [
                "gene", "protein", "function",
                "基因", "功能",
            ],
        }
        return intent_map.get(intent, intent_map[QueryIntent.UNKNOWN])
    
    def _extract_diseases(self, question_lower: str) -> List[str]:
        """从问题中提取疾病名称"""
        diseases = []
        
        # 常见疾病模式
        disease_patterns = [
            "cancer", "tumor", "carcinoma", "leukemia", "lymphoma",
            "diabetes", "obesity", "alzheimer", "parkinson",
            "cardiovascular", "hypertension", "stroke",
            "asthma", "copd", "fibrosis",
            "breast cancer", "lung cancer", "colorectal cancer",
            "prostate cancer", "liver cancer", " gastric cancer",
            "黑色素瘤", "肺癌", "肝癌", "胃癌", "乳腺癌",
        ]
        
        for disease in disease_patterns:
            if disease in question_lower:
                diseases.append(disease)
        
        return diseases if diseases else ["cancer"]  # 默认返回cancer
    
    def build_llm_enhanced_queries(
        self,
        question: str,
        genes: List[str],
        intent: QueryIntent,
        analysis_results: Dict[str, Any] = None,
    ) -> Dict[str, List[str]]:
        """使用LLM生成增强的搜索查询
        
        Args:
            question: 用户问题
            genes: 基因列表
            intent: 意图类型
            analysis_results: 分析结果
            
        Returns:
            增强的搜索关键词
        """
        if not self.llm:
            return self.build_search_keywords(question, genes, intent, analysis_results)
        
        try:
            prompt = f"""你是一个生物医学文献检索专家。根据用户问题和基因列表，生成优化的PubMed搜索查询。

用户问题: {question}

相关基因: {', '.join(genes[:10])}

意图类型: {intent}

要求:
1. 生成5-8个PubMed搜索查询（使用MeSH术语和关键词组合）
2. 查询格式: (基因[Title/Abstract]) AND (术语[Title/Abstract])
3. 包含专业MeSH术语，如: therapeutic, biomarker, pathway, oncogene
4. 如果是药物靶点问题，添加: drug target, therapeutic agent, inhibitor
5. 如果是疾病问题，添加: pathogenesis, clinical, prognosis
6. 只输出查询语句，每行一个，不要其他解释

生成查询:"""
            
            response = self.llm.chat([
                {"role": "system", "content": "You are a biomedical literature search expert."},
                {"role": "user", "content": prompt}
            ])
            
            # 解析LLM响应
            queries = []
            for line in response.strip().split('\n'):
                line = line.strip()
                # 过滤：移除编号、空行、明显不是查询的行
                if line and not line.startswith('-') and not line.startswith('*'):
                    if '[Title/Abstract]' in line or '[All Fields]' in line:
                        queries.append(line)
            
            if queries:
                logger.info(f"[SmartQuery] LLM generated {len(queries)} enhanced queries")
                return {
                    "pubmed": queries[:10],
                    "europepmc": queries[:10],
                }
            
        except Exception as e:
            logger.warning(f"[SmartQuery] LLM query generation failed: {e}")
        
        # 回退到基于规则的查询
        return self.build_search_keywords(question, genes, intent, analysis_results)


# =============================================================================
# 全局实例
# =============================================================================

_smart_query_builder: Optional[SmartQueryBuilder] = None


def get_smart_query_builder(llm=None) -> SmartQueryBuilder:
    """获取智能查询构建器实例"""
    global _smart_query_builder
    if _smart_query_builder is None:
        _smart_query_builder = SmartQueryBuilder(llm)
    return _smart_query_builder
