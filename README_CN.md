# E2seq - Easy to Chat with Sequencing

<div align="center">

**基于自然语言界面的智能单细胞RNA测序分析平台**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Powered by LangChain](https://img.shields.io/badge/Powered%20by-LangChain-green.svg)](https://www.langchain.dev/)

[English](README.md) | [中文](README_CN.md)

</div>

---

## 概述

**E2seq (Easy to Chat with Sequencing)** 是一个专为单细胞RNA测序（scRNA-seq）数据分析设计的智能代理平台。它将大语言模型（LLM）与检索增强生成（RAG）技术相结合，使研究人员能够通过自然语言查询与单细胞数据进行交互。

研究人员无需编写复杂的代码或手动执行生物信息学流程，只需简单地向系统提问：

- "分析T细胞的标记基因"
- "这个细胞类型富集了哪些通路？"
- "展示这些基因的互作网络"

E2seq 在幕后处理所有复杂性，包括数据处理、分析执行和可视化生成。

---

## 核心功能

### 主要能力

| 功能 | 描述 |
|------|------|
| **自然语言界面** | 使用英文直接查询数据 |
| **差异表达分析** | 识别细胞类型标记基因和差异表达基因 |
| **富集分析** | GO、KEGG、Reactome通路富集分析 |
| **网络分析** | 基于STRING数据库构建PPI网络 |
| **交互式可视化** | UMAP、tSNE、火山图、热图、网络图 |

### 知识库集成

| 数据库 | 类型 | 描述 |
|--------|------|------|
| STRING | PPI网络 | 蛋白质相互作用数据 |
| HMDB | 代谢组学 | 人类代谢组数据库 |
| TRRUST | 转录调控 | 转录因子靶基因网络 |
| GUTMGENE | 微生物组 | 肠道微生物组-基因互作 |

### 大语言模型支持

- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude 3)
- Google Gemini
- 智谱AI (GLM-4)
- DeepSeek
- 硅基流动 (SiliconFlow)

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
git clone https://github.com/XIAOJIE0519/E2seq.git
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

进入设置页面，添加您的大语言模型服务商密钥。

### 3. 上传数据

点击上传按钮添加您的单细胞数据（.h5ad文件）。

### 4. 开始分析

尝试以下示例查询：

```
"分析Enterocytes的标记基因"
"B细胞富集了哪些通路？"
"为这些差异基因构建蛋白质互作网络"
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
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    E2scAgent 主体                             │
│  ┌─────────────┬─────────────┬─────────────┐               │
│  │   Planner   │  Retriever   │ Synthesizer │               │
│  └─────────────┴─────────────┴─────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

### 组件说明

| 组件 | 文件 | 功能 |
|------|------|------|
| API服务器 | `e2sc/api/server.py` | 处理HTTP请求 |
| 主体代理 | `e2sc/agent/orchestrator.py` | 主要智能体编排 |
| 规划器 | `e2sc/agent/planner.py` | 制定分析计划 |
| 检索器 | `e2sc/agent/retriever.py` | 查询数据库 |
| 综合器 | `e2sc/agent/synthesizer.py` | 生成回复 |

---

## 配置

配置存储在 `.e2sc/config.yaml`：

```yaml
llm:
  provider: glm        # LLM服务商
  model: glm-4         # 模型名称
  temperature: 0.7

embedding:
  model_name: sentence-transformers/all-MiniLM-L6-v2
  local_only: true
```

---

## API参考

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | Web界面 |
| `/api/health` | GET | 健康检查 |
| `/api/chat` | POST | 发送聊天消息 |
| `/api/upload` | POST | 上传数据文件 |
| `/docs` | GET | API文档 |

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
  url = {https://github.com/XIAOJIE0519/E2seq}
}
```
