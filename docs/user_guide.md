# E2seq quick guide / E2seq 简明教程

## What it is / 它是什么

E2seq is an Agent + RAG application for compatible expression-profile data. It accepts expression matrices, clinical variables, existing differential/prognostic tables, multi-group tables, and compatible single-cell files. / E2seq 是面向兼容表达谱数据的 Agent + RAG 应用，可载入表达矩阵、临床变量、已有差异/预后结果、多组结果表和兼容的单细胞文件。

## Four steps / 四步使用

1. **Upload / 上传** — Choose expression-profile or single-cell data. Raw counts and clinical variables are read without filtering or normalization at upload time. / 选择表达谱或单细胞数据；原始 count 与临床变量上传时只读取结构，不过滤、不归一化。
2. **Configure / 配置** — Select ID, sample, group, effect, significance, survival-time, event, and covariate columns. Choose DESeq2, edgeR, limma-voom, or a survival transform when raw modeling is requested. / 选择 ID、样本、分组、效应值、显著性、生存时间、事件和校正列；原始数据建模时选择 DESeq2、edgeR、limma-voom 或生存变换。
3. **Filter / 筛选** — Modeling runs on the full valid input first. Then use the right panel to filter by FDR/P value, log2FC/HR/expression, direction, and the first N items. / 先对全部有效输入建模，再在右侧按 FDR/P 值、log2FC/HR/表达值、方向和前 N 项筛选。
4. **Ask / 提问** — Ask any question after analysis is ready. The first question runs the selected-item GO/KEGG/GSEA/STRING batch where applicable and builds Agent RAG; later questions reuse the persisted evidence and may retrieve more relevant literature. / 分析完成后自由提问；第一次提问时对选定项目执行适用的 GO/KEGG/GSEA/STRING 批量分析并构建 Agent RAG，后续问题复用持久化证据，并可继续检索更相关文献。

## Data formats / 数据格式

- Expression tables / 表格: CSV, TSV, XLSX。
- Raw count workflow / 原始 count 流程: one expression/count table plus one clinical-variable table. / 一份表达/count 表加一份临床变量表。
- Existing results / 已有结果: one table with an expression-item ID and an effect/value column; P/FDR/group/direction columns are optional. / 一份包含表达项目 ID 和效应值/表达值的表；P/FDR/分组/方向列可选。
- Single-cell: H5AD, CSV, RDS when the required reader is installed. / 单细胞：H5AD、CSV；安装相应读取器后可读 RDS。

Columns are user-selectable; no fixed file name or fixed column order is required. / 列均由用户选择，不要求固定文件名或固定列顺序。

## Agent RAG boundary / Agent RAG 边界

The uploaded values remain the analysis result. External APIs, literature, local databases, custom gene-annotation files, and the local embedding index are evidence for interpretation; they do not silently replace uploaded statistics. / 上传值仍是分析结果；外部 API、文献、本地数据库、自定义基因注释文件和本地 Embedding 索引仅作为解读证据，不会静默替换上传统计量。

The answer source panel controls which sources may be used for new answers. A dataset prompt is optional and belongs to that dataset, not to the global database settings. / 回答来源面板控制新回答可调用的来源；数据集提示词是可选的，属于具体数据，不属于全局数据库设置。

## Short troubleshooting / 常见排查

- No page: check the printed URL and `/api/health`. / 页面打不开：检查终端打印地址和 `/api/health`。
- Raw modeling fails: configure `E2SEQ_R_EXE` and install the required R packages. / 原始建模失败：配置 `E2SEQ_R_EXE` 并安装所需 R 包。
- API answer fails: verify the selected provider, model, endpoint, and key in Settings. / API 回答失败：在设置中检查服务商、模型、端点和密钥。
- Large jobs: network retrieval is bounded; progress is shown in percent. / 大任务：网络检索有并发上限，页面显示百分比进度。
