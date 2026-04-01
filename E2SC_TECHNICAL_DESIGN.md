# E2sc: Easy to Explore Single-Cell via Agentic RAG
## 技术设计文档 v1.0

---

## 📋 项目概述

### 项目定位
E2sc 是一个基于 Agentic RAG（检索增强生成）的单细胞数据分析工具，旨在让研究人员通过自然语言对话的方式，轻松探索和分析单细胞测序数据。

### 核心价值主张
- **零门槛使用**：安装即用，无需编程基础
- **智能对话**：通过自然语言提问，AI自动执行分析
- **本地优先**：数据和计算在本地进行，保护隐私
- **灵活接入**：支持多种LLM API（ChatGPT、Claude、DeepSeek等）
- **深度分析**：整合多个生物信息学数据库，提供立体化解读

### 使用场景
```
用户: "帮我分析一下Enterocytes细胞中高表达的基因"
E2sc: [自动执行]
      1. 提取Enterocytes细胞
      2. 识别差异表达基因
      3. 进行GO富集分析
      4. 构建基因互作网络
      5. 查询hub基因的UniProt注释
      6. 生成可视化图表
      7. 返回综合解读报告
```

---

## 🏗️ 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户界面层                              │
│  ┌──────────────┐              ┌──────────────┐             │
│  │  终端CLI界面  │              │  Web界面      │             │
│  │  (Rich/Typer)│              │  (Streamlit)  │             │
│  └──────────────┘              └──────────────┘             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      对话管理层                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  LLM Agent Orchestrator (LangChain/LlamaIndex)       │   │
│  │  - 意图识别  - 任务规划  - 工具调用  - 结果整合      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      工具执行层                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │单细胞分析 │  │富集分析   │  │网络分析   │  │可视化     │   │
│  │(Scanpy)  │  │(GSEApy)  │  │(NetworkX) │  │(Plotly)  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      数据访问层                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │本地数据库 │  │在线API    │  │向量数据库 │  │缓存层     │   │
│  │(SQLite)  │  │(REST)    │  │(ChromaDB) │  │(Redis)   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 💾 数据层设计

### 1. 用户单细胞数据

**输入格式**：AnnData (.h5ad)

**必需字段**：
```python
adata.obs:
  - cell_type / final_annotation  # 细胞类型注释
  - group / condition             # 实验分组
  - leiden_clusters               # 聚类信息（可选）

adata.var:
  - gene_ids                      # 基因ID
  - highly_variable               # 高变基因标记（可选）

adata.obsm:
  - X_umap / X_tsne              # 降维坐标
  - X_pca                        # PCA坐标（可选）
```

### 2. 本地知识库数据

#### 2.1 HMDB 数据库 (1,045,796 条记录)
```
结构: gene -> metabolite
用途: 基因-代谢物关联分析
示例: NT5E -> HMDB0014944
```

#### 2.2 STRING 数据库 (1,858,946 条记录)
```
结构: source_gene -> target_gene (weight)
用途: 蛋白质-蛋白质相互作用网络
示例: ARF5 -> CYTH2 (0.471)
```

#### 2.3 TRRUST 数据库 (9,398 条记录)
```
结构: TF -> gene (function, pubmed)
用途: 转录因子调控关系
示例: AATF -> BAX (Repression, 22909821)
```

#### 2.4 GUTMGENE 数据库 (1,334 条记录)
```
结构: 肠道微生物 -> 基因 (关联信息)
用途: 肠道微生物-基因关联分析
字段: PMID, Gut Microbiota, Gene, Alteration, Condition等
```

### 3. 在线API资源

**已集成的API**：
- MyGene.info - 基因注释
- STRING API - 蛋白质互作
- QuickGO - GO注释
- Europe PMC - 文献检索
- ChEMBL - 药物化合物
- Ensembl - 基因组信息
- UniProt - 蛋白质详细信息
- PubChem - 化合物信息
- PubMed - 文献数据库

---

## 🤖 Agentic RAG 设计

### Agent 架构

```python
E2scAgent
├── Planner Agent          # 任务规划
│   └── 分解用户问题为子任务
├── Retriever Agent        # 信息检索
│   ├── 向量检索（相似问题/案例）
│   ├── 本地数据库查询
│   └── 在线API调用
├── Analyzer Agent         # 数据分析
│   ├── 单细胞分析工具
│   ├── 富集分析工具
│   └── 网络分析工具
├── Visualizer Agent       # 可视化
│   ├── UMAP/tSNE图
│   ├── 热图/小提琴图
│   └── 网络图
└── Synthesizer Agent      # 结果整合
    └── 生成综合报告
```

### RAG 工作流

```
用户提问
    ↓
[意图识别] → 识别分析类型（差异分析/富集分析/网络分析等）
    ↓
[任务规划] → 生成执行计划
    ↓
[知识检索] → 并行检索
    ├── 向量数据库：查找相似案例
    ├── 本地数据库：查询基因/代谢物关联
    └── 在线API：获取最新注释信息
    ↓
[工具执行] → 调用分析工具
    ├── Scanpy: 单细胞分析
    ├── GSEApy: 富集分析
    ├── NetworkX: 网络构建
    └── Plotly: 可视化
    ↓
[结果整合] → LLM生成解读报告
    ↓
返回给用户（文字+图表+数据）
```

---

## 🛠️ 核心功能模块

### 1. 单细胞分析模块

**功能清单**：
- 细胞类型筛选与统计
- 差异表达基因分析（DEG）
- 标记基因识别
- 细胞亚群比较
- 轨迹分析（可选）

**技术栈**：Scanpy, AnnData

### 2. 富集分析模块

**分析类型**：
- GO富集分析（BP/MF/CC）
- KEGG通路富集
- Reactome通路分析
- 自定义基因集富集

**数据源**：
- 本地：预下载的GMT文件
- 在线：Enrichr API, GSEA API

**技术栈**：GSEApy, scipy

### 3. 网络分析模块

**网络类型**：
- PPI网络（基于STRING数据库）
- 转录调控网络（基于TRRUST）
- 基因-代谢物网络（基于HMDB）
- 共表达网络

**网络分析**：
- Hub基因识别（度中心性、介数中心性）
- 社区检测
- 关键路径分析

**技术栈**：NetworkX, igraph, pyvis

### 4. 知识整合模块

**整合策略**：
```python
对于Top基因（如hub基因）：
1. 本地数据库查询
   - STRING: 获取互作蛋白
   - TRRUST: 获取调控关系
   - HMDB: 获取相关代谢物
   - GUTMGENE: 获取肠道微生物关联

2. 在线API查询
   - UniProt: 蛋白质功能详解
   - QuickGO: GO注释
   - Europe PMC: 最新文献

3. LLM整合
   - 将所有信息输入LLM
   - 生成立体化、易懂的解释
```

---

## 📊 可视化设计

### 交互式图表

**使用Plotly实现**：
1. UMAP/tSNE散点图（可按细胞类型着色）
2. 小提琴图/箱线图（基因表达分布）
3. 热图（差异基因表达）
4. 火山图（差异分析结果）
5. 气泡图（富集分析结果）
6. 网络图（基因互作网络）
7. 和弦图（基因-代谢物关联）

### 3D可视化

**立体化展示**：
- 3D UMAP（Plotly 3D scatter）
- 3D网络图（pyvis + 3D force layout）
- 时间序列轨迹（3D trajectory）

---

## 🖥️ 用户界面设计

### 方案A：终端CLI界面

**技术栈**：Rich + Typer

**特点**：
- 轻量级，启动快
- 适合命令行用户
- 支持彩色输出、进度条、表格

**示例交互**：
```bash
$ e2sc chat

E2sc> 加载我的数据 data.h5ad
[✓] 数据加载成功: 3728 cells, 5000 genes

E2sc> 分析Enterocytes细胞的差异基因
[→] 正在提取Enterocytes细胞...
[→] 正在进行差异分析...
[→] 正在进行GO富集...
[✓] 分析完成！

发现 245 个差异表达基因
Top 10 上调基因: APOA1, APOB, FABP1...
GO富集结果: lipid metabolism, nutrient absorption...

E2sc> 构建这些基因的互作网络
[→] 正在查询STRING数据库...
[→] 正在构建网络...
[✓] 网络已生成: network.html

Hub基因: APOB, APOA1, FABP2
网络包含 180 个节点, 523 条边
```

### 方案B：Web界面

**技术栈**：Streamlit / Gradio

**特点**：
- 图形化界面，更直观
- 支持拖拽上传文件
- 实时显示图表

**页面布局**：
```
┌─────────────────────────────────────────┐
│  E2sc - Single Cell Explorer            │
├─────────────────────────────────────────┤
│  [上传数据] [配置API] [历史记录]         │
├─────────────────────────────────────────┤
│  对话区域                    │  图表区域  │
│  ┌─────────────────────┐   │  ┌───────┐ │
│  │ 用户: 分析Enterocytes│   │  │ UMAP  │ │
│  │ E2sc: [分析中...]    │   │  │       │ │
│  │                      │   │  └───────┘ │
│  │                      │   │  ┌───────┐ │
│  │                      │   │  │ 热图   │ │
│  └─────────────────────┘   │  └───────┘ │
│  [输入框]                   │            │
└─────────────────────────────────────────┘
```

---

## 🔌 LLM接入设计

### 统一接口

```python
class LLMProvider:
    """LLM提供商统一接口"""
    
    def __init__(self, provider: str, api_key: str):
        self.provider = provider  # 'openai', 'anthropic', 'deepseek'
        self.api_key = api_key
    
    def chat(self, messages: List[Dict], tools: List[Dict] = None):
        """统一的对话接口"""
        pass
    
    def stream_chat(self, messages: List[Dict]):
        """流式输出"""
        pass
```

### 支持的LLM

| 提供商 | 模型 | 特点 |
|--------|------|------|
| OpenAI | GPT-4, GPT-3.5 | 强大的推理能力 |
| Anthropic | Claude 3 | 长上下文，安全性高 |
| DeepSeek | DeepSeek-V2 | 性价比高，中文友好 |
| 本地模型 | Ollama | 完全离线，隐私保护 |

### 配置方式

**方式1：配置文件**
```yaml
# ~/.e2sc/config.yaml
llm:
  provider: openai
  api_key: sk-xxx
  model: gpt-4
  temperature: 0.7
```

**方式2：环境变量**
```bash
export E2SC_LLM_PROVIDER=openai
export E2SC_API_KEY=sk-xxx
```

**方式3：交互式配置**
```bash
$ e2sc config
选择LLM提供商: [1] OpenAI [2] Claude [3] DeepSeek
输入API Key: ****
```

---

## 📦 Python包设计

### 包结构

```
e2sc/
├── __init__.py
├── __main__.py              # 入口点
├── cli/                     # 命令行界面
│   ├── __init__.py
│   ├── app.py              # CLI主程序
│   └── commands.py         # 命令定义
├── web/                     # Web界面
│   ├── __init__.py
│   └── app.py              # Streamlit应用
├── agent/                   # Agent核心
│   ├── __init__.py
│   ├── orchestrator.py     # Agent编排器
│   ├── planner.py          # 任务规划
│   ├── retriever.py        # 信息检索
│   └── synthesizer.py      # 结果整合
├── tools/                   # 分析工具
│   ├── __init__.py
│   ├── scanpy_tools.py     # 单细胞分析
│   ├── enrichment.py       # 富集分析
│   ├── network.py          # 网络分析
│   └── visualization.py    # 可视化
├── data/                    # 数据访问
│   ├── __init__.py
│   ├── local_db.py         # 本地数据库
│   ├── api_client.py       # API客户端
│   └── vector_store.py     # 向量数据库
├── llm/                     # LLM接口
│   ├── __init__.py
│   ├── provider.py         # 统一接口
│   └── prompts.py          # Prompt模板
├── utils/                   # 工具函数
│   ├── __init__.py
│   ├── config.py           # 配置管理
│   └── logger.py           # 日志
└── databases/               # 内置数据库
    ├── hmdb.db             # SQLite格式
    ├── string.db
    ├── trrust.db
    └── gutmgene.db
```

### 安装方式

```bash
# PyPI安装
pip install e2sc

# 开发安装
git clone https://github.com/your-org/e2sc.git
cd e2sc
pip install -e .
```

### 使用方式

**方式1：命令行**
```bash
# 启动CLI
e2sc chat

# 启动Web界面
e2sc web

# 配置
e2sc config
```

**方式2：Python API**
```python
from e2sc import E2scAgent
import scanpy as sc

# 加载数据
adata = sc.read_h5ad('data.h5ad')

# 创建Agent
agent = E2scAgent(
    adata=adata,
    llm_provider='openai',
    api_key='sk-xxx'
)

# 对话分析
response = agent.chat("分析Enterocytes细胞的差异基因")
print(response.text)
response.show_plots()  # 显示图表
```

---

## 🔄 工作流示例

### 示例1：差异基因分析 + 富集 + 网络

**用户输入**：
```
"比较Enterocytes和Goblet cells，找出差异基因，
进行GO富集，并构建hub基因的互作网络"
```

**Agent执行流程**：

1. **意图识别**
   - 任务类型：差异分析 + 富集分析 + 网络分析
   - 目标细胞：Enterocytes vs Goblet cells

2. **任务规划**
   ```
   Step 1: 提取两种细胞类型
   Step 2: 差异表达分析
   Step 3: GO富集分析
   Step 4: 识别hub基因
   Step 5: 构建PPI网络
   Step 6: 查询hub基因详细信息
   Step 7: 生成报告
   ```

3. **执行分析**
   ```python
   # Step 1-2: Scanpy差异分析
   sc.tl.rank_genes_groups(adata, groupby='cell_type')
   
   # Step 3: GSEApy富集
   enr = gp.enrichr(gene_list, gene_sets='GO_Biological_Process')
   
   # Step 4-5: NetworkX网络分析
   G = build_ppi_network(deg_genes, string_db)
   hub_genes = identify_hubs(G, top_n=10)
   
   # Step 6: 查询hub基因
   for gene in hub_genes:
       info = query_uniprot(gene)
       go_terms = query_quickgo(info['uniprot_id'])
       interactions = query_string(gene)
   ```

4. **生成报告**
   ```
   LLM Prompt:
   "基于以下分析结果，生成一份综合报告：
   - 差异基因：245个（120上调，125下调）
   - GO富集：主要涉及脂质代谢、营养吸收
   - Hub基因：APOB, APOA1, FABP2等
   - 网络特征：...
   
   请用通俗易懂的语言解释这些发现的生物学意义"
   ```

5. **返回结果**
   - 文字报告
   - 火山图（差异基因）
   - 气泡图（GO富集）
   - 网络图（PPI网络）
   - 表格（hub基因详细信息）

---

## 🎯 核心技术挑战与解决方案

### 挑战1：大规模数据库的快速检索

**问题**：STRING数据库有180万条记录，如何快速查询？

**解决方案**：
1. 转换为SQLite数据库，建立索引
2. 使用内存缓存（Redis/LRU cache）
3. 预计算常用基因的网络

```python
# 数据库索引
CREATE INDEX idx_source ON string(source_gene);
CREATE INDEX idx_target ON string(target_gene);

# 缓存策略
@lru_cache(maxsize=1000)
def get_gene_interactions(gene: str):
    return query_string_db(gene)
```

### 挑战2：多数据源信息整合

**问题**：如何整合本地数据库和在线API的信息？

**解决方案**：
1. 并行查询（asyncio）
2. 超时控制
3. 降级策略（API失败时使用本地数据）

```python
async def query_gene_info(gene: str):
    tasks = [
        query_local_db(gene),      # 本地数据库
        query_uniprot_api(gene),   # UniProt API
        query_string_api(gene),    # STRING API
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return merge_results(results)
```

### 挑战3：LLM上下文长度限制

**问题**：分析结果可能很长，超过LLM上下文限制

**解决方案**：
1. 分层总结（先总结子结果，再整合）
2. 关键信息提取
3. 使用长上下文模型（Claude 3）

```python
# 分层总结
deg_summary = summarize_deg_results(deg_results)
enrichment_summary = summarize_enrichment(enr_results)
network_summary = summarize_network(network_results)

# 整合总结
final_report = llm.generate(
    f"整合以下分析结果：\n"
    f"1. 差异分析：{deg_summary}\n"
    f"2. 富集分析：{enrichment_summary}\n"
    f"3. 网络分析：{network_summary}"
)
```

### 挑战4：可视化性能

**问题**：大型网络图（>1000节点）渲染慢

**解决方案**：
1. 只显示top节点和边
2. 使用WebGL渲染（plotly）
3. 提供静态图和交互图两种选项

---

## 📈 性能优化策略

### 1. 数据库优化
- SQLite索引优化
- 查询结果缓存
- 连接池管理

### 2. 计算优化
- 多进程并行（multiprocessing）
- GPU加速（可选，用于大规模计算）
- 增量计算（缓存中间结果）

### 3. 内存优化
- 稀疏矩阵存储（scipy.sparse）
- 分块处理大数据
- 及时释放不用的对象

---

## 🔒 安全与隐私

### 数据安全
- 所有单细胞数据在本地处理
- 不上传原始数据到云端
- API调用只传输基因名称等元数据

### API密钥管理
- 加密存储在本地配置文件
- 支持环境变量
- 不在日志中记录密钥
- 用户在前端填写LLM的apikey后，使用rsa非对称加密，对用户输入的apikey用公钥加密，传输到后端再用私钥解密，确保apikey不外泄

---

## 🚀 开发路线图

### Phase 1: MVP（最小可行产品）
- [x] 本地数据库构建
- [x] API客户端开发
- [ ] 基础Agent框架
- [ ] CLI界面
- [ ] 核心分析功能

### Phase 2: 功能完善
- [ ] Web界面
- [ ] 向量数据库集成
- [ ] 更多分析工具
- [ ] 可视化增强

### Phase 3: 生态建设
- [ ] 插件系统
- [ ] 社区数据库
- [ ] 文档和教程
- [ ] PyPI发布

---

## 📚 技术栈总结

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| 界面层 | Rich/Typer, Streamlit | CLI和Web界面 |
| Agent层 | LangChain/LlamaIndex | Agent框架 |
| LLM层 | OpenAI/Anthropic/DeepSeek | 多LLM支持 |
| 分析层 | Scanpy, GSEApy, NetworkX | 生物信息学工具 |
| 可视化层 | Plotly, Matplotlib | 交互式图表 |
| 数据层 | SQLite, ChromaDB, Redis | 数据存储和检索 |
| API层 | requests, aiohttp | HTTP客户端 |

---

## 📝 下一步行动

1. **确认技术方案**：选择CLI还是Web，或两者都做
2. **搭建开发环境**：创建项目结构，配置依赖
3. **开发Agent核心**：实现基础的对话和工具调用
4. **集成分析工具**：封装Scanpy等工具为Agent可调用的函数
5. **测试与迭代**：用真实数据测试，优化用户体验

---

**文档版本**：v1.0  
**最后更新**：2024-03-02  
**作者**：E2sc开发团队
