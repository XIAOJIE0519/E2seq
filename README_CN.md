# E2seq - Easy to Chat with Sequencing

<div align="center">

**面向 bulk 与单细胞测序基因数值的 Agent RAG 解读工具**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)

[English](README.md) | [中文](README_CN.md)

</div>

---

## 概述

**E2seq (Easy to Chat with Sequencing)** 读取 bulk 或单细胞结果文件中已有的基因、数值和标签，为这些输入基因检索外部证据，并返回带来源的文字解读。

默认 Web Agent 明确**不计算** marker、差异表达、fold change、p 值、富集、聚类、降维、网络、hub 或模块。Reactome、STRING、QuickGO、TRRUST 等内容只作为 RAG 检索到的外部注释，不是从上传文件计算出的分析结果。

研究人员可以直接提问：

- "解读 T 细胞中上传的基因数值"
- "哪些已检索的通路注释有助于解释这些输入基因？"
- "综合解读所有已提供的基因与数值"
- "这些输入基因有哪些已知互作证据？"

Web 服务统一通过 `python start.py` 启动。

---

## 核心功能

### 主要能力

| 功能 | 描述 |
|------|------|
| **自然语言界面** | 使用中文或英文直接查询数据 |
| **输入数值解读** | 保留上传的基因名、数值、分组和细胞类型标签 |
| **Agent RAG 检索** | 针对输入基因查询生物数据库与文献证据 |
| **证据边界** | 清楚区分上传数值和外部数据库注释 |
| **文字优先 API** | 通过 REST/SSE 返回 Markdown 文字，不生成新分析结果 |
| **会话隔离** | 数据集、记忆、状态、缓存和进度按会话隔离 |

### 知识库集成

E2seq 整合了 **20+ 生物数据库**，提供全面的生物学洞察：

#### 本地数据库

| 数据库 | 类型 | 记录数 | 描述 |
|--------|------|--------|------|
| STRING | PPI网络 | 1,858,946 | 蛋白质相互作用数据 |
| HMDB | 代谢组学 | 1,045,796 | 人类代谢组数据库 |
| TRRUST | 转录调控 | 9,398 | 转录因子靶基因网络 |
| GUTMGENE | 微生物组 | 1,334 | 肠道微生物组-基因互作 |

#### 在线API（16个数据源）

| API | 提供方 | 数据类型 |
|-----|--------|----------|
| UniProt | EMBL-EBI | 蛋白质功能、结构域、翻译后修饰 |
| MyGene | scGene | 基因注释、GO terms |
| QuickGO | EMBL-EBI | GO注释及证据代码 |
| Ensembl | EMBL-EBI | 基因组坐标、外显子结构 |
| ChEMBL | EMBL-EBI | 药物靶点结合、临床阶段 |
| Open Targets | EBI-OpenTargets | 基因-疾病关联评分 |
| ClinVar | NCBI | 致病/良性变异分类 |
| CIViC | MSKCC | 癌症变异临床证据 |
| GWAS Catalog | EBI | 性状/SNP关联 |
| Reactome | EMBL-EBI | 生物学通路成员关系 |
| GTEx | GTEx Project | 组织特异性表达（54个组织）|
| HumanBase | HB | 组织特异性共表达网络 |
| BioGRID | BioGRID | 实验验证的PPI |
| Alliance | Alliance of Genome Resources | 跨物种同源基因 |
| PubMed | NCBI | 文献检索 |
| EuropePMC | EMBL-EBI | 预印本及已发表论文 |

### 大语言模型支持

E2seq 支持 **7个大模型服务商**，共 **30+模型**（截至2026年4月）：

| 服务商 | 默认模型 | 推荐模型 |
|--------|----------|----------|
| **OpenAI** | gpt-5.5 | gpt-5.5-pro, gpt-5.1, gpt-5.2, gpt-4o |
| **Anthropic** | claude-opus-4-8 | claude-opus-4-7, claude-sonnet-4-6, claude-haiku-4-5 |
| **DeepSeek** | deepseek-v4-flash | deepseek-v4-pro |
| **Google Gemini** | gemini-3.1-pro-preview | gemini-3-flash-preview, gemini-2.5-pro |
| **硅基流动** | deepseek-ai/DeepSeek-V3 | deepseek-ai/DeepSeek-R1, Qwen/Qwen2.5-72B |
| **智谱AI (GLM)** | glm-5.2 | glm-5.1, glm-4-Plus, glm-4 |
| **Moonshot AI (Kimi)** | kimi-k2.6 | moonshot-v2.5-250415 |
| **Ollama**（本地部署）| - | llama3.2, qwen2.5, deepseek-r1 |

> **注意**：DeepSeek、Gemini 和硅基流动使用 OpenAI 兼容 API。Ollama 可在本地运行，无需 API 密钥。

### 数据格式支持

- **单细胞数据**：`.h5ad`, `.csv`, `.rds`
- **表格数据**：`.csv`, `.tsv`, `.xlsx`

---

## 安装

### 环境要求

- Python 3.9 或更高版本
- pip 或 conda
- 8GB+ 内存（处理大数据集建议16GB+）

### 标准安装

```bash
# 克隆仓库
git clone git@github.com:XIAOJIE0519/E2seq.git
cd E2seq

# 安装依赖
pip install -e .

# 启动应用
python start.py
```

### 依赖项

核心依赖会自动安装：

```
scanpy>=1.9.0
anndata>=0.9.0
langchain>=0.1.0
chromadb>=0.4.0
sentence-transformers>=2.2.0
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
```

---

## 快速开始

### 1. 启动服务器

```bash
python start.py
```

服务器默认在 `http://localhost:8000` 启动。

### 2. 配置API密钥

进入设置页面，添加您的大语言模型服务商密钥。E2seq 支持多种服务商：

| 服务商 | API密钥获取地址 |
|--------|----------------|
| OpenAI | https://platform.openai.com/api-keys |
| Anthropic | https://console.anthropic.com/settings/keys |
| DeepSeek | https://platform.deepseek.com/api_keys |
| Google Gemini | https://aistudio.google.com/app/apikey |
| 硅基流动 | https://cloud.siliconflow.cn/account/ak |
| 智谱AI | https://open.bigmodel.cn/ |
| Moonshot AI | https://platform.moonshot.cn/ |

### 3. 上传数据

点击上传按钮添加您的单细胞数据（.h5ad文件）。

### 4. 开始解读

尝试以下示例查询：

```
"解读 Enterocytes 中上传的基因数值"
"检索这些 B 细胞输入基因的通路注释"
"综合解读所有已提供的基因与数值"
"检索这些输入基因的已知互作证据"
```

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        Web UI                               │
│                   (HTML/CSS/JavaScript)                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI 服务器                           │
│  - REST API 接口                                           │
│  - SSE 流式响应实时推送                                    │
│  - 会话管理                                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    E2scAgent 优化版                        │
│  ┌─────────────┬─────────────┬─────────────┐              │
│  │   Planner   │  Retriever  │ Synthesizer │              │
│  │  (输入基因) │  (RAG/DB)   │   (文字)    │              │
│  └─────────────┴─────────────┴─────────────┘              │
│                                                              │
│  ┌─────────────────────────────────────────┐                │
│  │           Vector Store (ChromaDB)        │                │
│  └─────────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  在线API        │ │ 本地数据库       │ │ 向量数据库       │
│  (16个数据源)   │ │ (4个数据库)     │ │ (RAG分块)       │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### 组件说明

| 组件 | 文件 | 功能 |
|------|------|------|
| API服务器 | `e2sc/api/server.py` | 处理HTTP请求、SSE流式响应 |
| 主体代理 | `e2sc/agent/orchestrator_optimized.py` | 主要智能体编排 |
| 规划器 | `e2sc/agent/orchestrator_optimized.py` | 从上传输入中选择相关基因 |
| 检索器 | `e2sc/agent/orchestrator_optimized.py` | 查询数据库与 API 证据 |
| 综合器 | `e2sc/agent/synthesizer.py` | 生成仅解读的 Markdown 文字 |
| 知识构建器 | `e2sc/agent/knowledge_builder.py` | 构建多源知识库 |
| 向量存储 | `e2sc/data/vector_store.py` | ChromaDB向量检索 |
| 本地数据库 | `e2sc/data/local_db.py` | SQLite本地数据库 |

---

## 配置

配置存储在 `.e2sc/config.yaml`：

```yaml
llm:
  provider: deepseek        # LLM服务商 (openai/anthropic/deepseek/gemini/siliconflow/glm/kimi/ollama)
  model: deepseek-v4-flash  # 模型名称
  temperature: 0.7           # 创造性水平
  max_tokens: 8192           # 最大响应长度

embedding:
  model_name: sentence-transformers/all-MiniLM-L6-v2
  local_only: true           # 仅使用本地嵌入模型

data:
  enabled_apis: [uniprot, mygene, quickgo, ensembl, chembl, pubmed, europepmc, reactome, gtex, humanbase, gwas, biogrid, civic, alliance, opentargets, clinvar]
  enabled_dbs: [string, hmdb, trrust, gutmgene]
```

---

## API参考

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | Web界面 |
| `/api/health` | GET | 健康检查 |
| `/api/chat` | POST | 发送聊天消息 |
| `/api/chat/stream` | POST | SSE流式聊天 |
| `/api/upload` | POST | 上传数据文件 |
| `/api/config` | GET | 获取配置 |
| `/api/settings` | GET/POST | 管理设置 |
| `/api/progress/{chat_id}` | GET | 获取进度更新 |
| `/docs` | GET | API文档 (Swagger) |

---

## 高级功能

### 综合解读模式

当您请求综合解读（综合解读/全面解读）时，E2seq：

1. 整合所有20+数据源
2. 为每个论点引用多个数据库的证据
3. 按生物学主题组织回复
4. 原样保留上传文件中已有的定量值
5. 不授权任何额外统计或网络计算

示例查询：
```
"综合解读所有上传的基因数值"
```

### 多数据库引用

E2seq 为所有论点提供内联引用：

```
"TP53在癌症中频繁突变[ClinVar]，编码调节细胞周期停滞的肿瘤抑制蛋白
[UniProt]。它与BCL2在凋亡通路中相互作用[STRING]。"
```

### 数据来源统计面板

每次回复后，E2seq 显示统计面板，展示：

- 查询的基因数量
- 各数据库的数据覆盖情况（API/本地）
- 每个数据源的命中率
- 从PubMed/EuropePMC检索到的文章总数

---

## 许可证

本项目采用 MIT 许可证。

---

## 引用

```bibtex
@software{e2seq2026,
  title = {E2seq: Easy to Chat with Sequencing},
  author = {E2seq Team},
  year = {2026},
  url = {https://github.com/XIAOJIE0519/E2seq},
  version = {2.0}
}
```

---

## 致谢

E2seq 整合了以下资源的数据：

- STRING Database (https://string-db.org)
- HMDB (https://hmdb.ca)
- TRRUST (https://www.grnpedia.org/trrust/)
- UniProt (https://www.uniprot.org)
- PubMed/EuropePMC (https://pubmed.ncbi.nlm.nih.gov)
- Open Targets Platform (https://platform.opentargets.org)
- 以及12+其他生物数据库
