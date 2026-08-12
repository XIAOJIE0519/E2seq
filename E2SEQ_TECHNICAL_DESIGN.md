# E2seq architecture / E2seq 架构

This is the short technical overview. The operational instructions are in
`docs/installation.md` and `docs/user_guide.md`.

这是技术概要；实际安装和使用请看 `docs/installation.md` 与
`docs/user_guide.md`。

## 1. Core architecture / 核心架构

```text
Upload / 上传
  -> inspect and configure / 读取结构并配置列
  -> full statistical model / 全量统计建模
  -> live filtering / 实时筛选
  -> Agent planner / Agent 任务规划
  -> parallel source retrieval + literature / 并行数据库与文献检索
  -> persistent vector index / 持久化向量索引
  -> question-specific retrieval / 按问题再次检索
  -> evidence-grounded synthesis / 基于证据综合回答
```

The application is an Agent + RAG system. The Agent decides which available
tools and sources are relevant to the user question; RAG supplies stored
analysis context, database records, and literature. The LLM is the synthesis
layer, not a replacement for the statistical model or source records.

本应用是 Agent + RAG 系统。Agent 根据用户问题决定调用哪些工具和数据源；
RAG 提供已保存的分析上下文、数据库记录和文献；LLM 负责综合表达，不能替代
统计模型或原始证据。

## 2. Data boundary / 数据边界

The web interface accepts compatible expression-profile tables, single-cell
`.h5ad`, and precomputed statistical-result tables. A table may contain raw
counts, expression values, effects, significance values, hazard ratios, or a
group/contrast column. Users choose the relevant columns in the interface.

网页支持兼容的表达谱表格、单细胞 `.h5ad` 和已经计算好的统计结果表。表格可
包含原始 count、表达值、效应值、显著性值、HR，或组别/比较列；具体使用哪一列
由用户在界面中选择。

Raw-count modeling leaves uploaded values unchanged until the selected analysis
starts. Differential analysis applies the selected method's own filtering and
normalization; survival analysis applies the selected VST, logCPM, or log2(TPM+1)
transformation during modeling.

原始 count 在统计分析开始前不被改写。差异分析在建模时执行所选方法对应的过滤
与校正；预后分析在建模时执行所选的 VST、logCPM 或 log2(TPM+1) 转换。

## 3. Persistence and portability / 持久化与可迁移性

- Chat state and uploaded datasets are stored under `E2SEQ_DATA_DIR` when set.
- Runtime settings are stored relative to the project in `.e2seq`.
- Python and R are resolved from CLI options, environment variables, saved
  settings, or PATH; no drive letter is required by the launcher.
- Local embeddings are the default. Hugging Face is opt-in through the UI or
  `E2SEQ_HF_ENDPOINT`.

- 设置 `E2SEQ_DATA_DIR` 后，对话和上传数据保存到该目录。
- 运行时配置保存在项目目录下的 `.e2seq`。
- Python 与 R 按命令行参数、环境变量、已保存设置或 PATH 查找，启动器不依赖
  固定盘符。
- 默认使用本地 embedding；Hugging Face 仅在界面或 `E2SEQ_HF_ENDPOINT` 显式
  设置后使用。

## 4. Runtime dependencies / 运行依赖

Python 3.10+ is required. R 4.4+ and the configured Bioconductor packages are
needed only for raw-count DESeq2/edgeR/limma-voom modeling; precomputed-result,
single-cell, and compatible expression-value workflows do not require R.

需要 Python 3.10+。只有原始 count 的 DESeq2/edgeR/limma-voom 建模需要 R 4.4+
及相应 Bioconductor 包；预计算结果、单细胞和兼容表达值流程不需要 R。
