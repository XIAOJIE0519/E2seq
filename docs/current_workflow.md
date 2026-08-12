# E2seq 当前流程说明 / Current Workflow

> 文档版本：2026-08-12
> 适用目录：`F:\\1a-E2seq`
> 说明：本文按照当前代码的实际执行链路撰写，区分“上传/统计建模”和“第一次提问时的富集与 Agent RAG”，不把旧版本行为或未来设想混入当前流程。

## 1. 一句话概览 / One-sentence overview

E2seq 当前是一个“浏览器 + FastAPI 服务 + 会话级数据/记忆 + 统计分析 + Agent RAG + 可配置 LLM”的分析系统：

```text
上传表达谱数据
    → 读取结构并让用户映射列
    → （原始 count 才执行）全量统计建模
    → 右侧边栏按条件实时筛选
    → 用户选择表达项目/基因
    → 第一次提问时并行执行 GO / KEGG / GSEA / STRING 和全量选定基因 RAG
    → Agent 根据用户问题选择证据、必要时追加文献检索
    → LLM 综合回答，并返回来源、覆盖率、时间和 token/API 信息
```

当前最重要的边界是：

- 上传原始 count 和临床表时只做结构读取、样本匹配检查和列建议；上传阶段不做过滤、归一化或统计校正。
- 原始 count 的差异/预后建模完成后，才显示结果筛选边栏；在建模未完成前不能提问。
- GO、KEGG、GSEA、STRING 和大批量 RAG 不在上传阶段执行，而是在用户完成筛选、选定表达项目并发送第一次问题时启动。
- 后续问题会复用该会话已经保存的数据、统计结果、RAG 知识和对话记忆；Agent 会依据当前问题判断是否需要继续检索文献或数据库。

## 2. 总体架构 / Overall architecture

```mermaid
flowchart TD
    A["浏览器 UI / Browser UI"] --> B["FastAPI 服务 /api"]
    B --> C["会话 ID / chat_id"]
    C --> D["会话数据与配置 / Dataset manifest"]
    C --> E["统计结果与筛选状态 / Result + filters"]
    C --> F["会话记忆与历史 / Memory + transcript"]

    B --> G{ "数据入口 / Data entry" }
    G --> G1["原始 count + 临床变量"]
    G --> G2["既有差异/预后/多组结果表"]
    G --> G3["h5ad、CSV 等表达谱文件"]

    G1 --> H["列映射与校验 / Inspect + configure"]
    H --> I["全量统计建模 / Full modeling"]
    I --> J["右侧实时筛选 / Live filtering"]
    G2 --> J
    G3 --> J
    J --> K["用户选定表达项目 / Selected genes"]

    K --> L["第一次提问 / First question"]
    L --> M["GO、KEGG、GSEA、STRING 并行"]
    L --> N["20 个在线 API + 4 个本地数据库并行检索"]
    M --> O["会话级 RAG 知识库 / Chroma + hybrid retrieval"]
    N --> O
    O --> P["Agent 判断问题、证据与追加检索"]
    P --> Q["可配置 LLM 综合回答 / Answer"]
    Q --> P
```

这里的 `chat_id` 是数据隔离的核心。上传、分析、筛选、第一次 RAG、每次问答、历史恢复和删除都必须使用同一个会话 ID，不能跨会话继承数据或记忆。

## 3. 启动与部署流程 / Startup and deployment

### 3.1 当前启动入口

推荐从项目根目录启动：

```powershell
cd F:\\1a-E2seq
E:\\python.exe start.py --python E:\\python.exe --r E:\\R-4.4.2\\bin\\x64\\Rterm.exe --port 8521
```

也可以直接运行：

```powershell
cd F:\\1a-E2seq
E:\\python.exe start.py
```

或双击/命令行运行便携启动器：

```powershell
F:\\1a-E2seq\\launch_server.bat
```

`launch_server.bat` 会优先使用项目内的 `venv\\Scripts\\python.exe`；如果没有项目虚拟环境，再寻找系统 Python。若需要强制使用指定解释器，应显式使用 `start.py --python ...`。

### 3.2 启动器实际做什么

`start.py` 的实际顺序是：

1. 检查当前目录是否是 E2seq 项目目录。
2. 读取或询问 Python 解释器路径、Python 库路径和 R 解释器路径。
3. 检查服务器真正导入链路所需要的依赖，而不是只检查一个表面包。
4. 仅对缺失依赖询问是否安装；也可以使用 `--no-install` 禁止自动安装。
5. 检查应用配置。
6. 启动 `uvicorn e2seq.api.server:app`。
7. 在指定 host/port 上提供网页和 API。

常用参数：

```powershell
E:\\python.exe start.py --check-only
E:\\python.exe start.py --non-interactive --no-install --port 8521
E:\\python.exe start.py --python E:\\python.exe --library-path E:\\python_libs --r E:\\R-4.4.2\\bin\\x64\\Rterm.exe
```

默认监听地址通常是 `127.0.0.1:8521`。例如换端口：

```powershell
E:\\python.exe start.py --port 8501
```

启动后可检查：

```text
http://127.0.0.1:8521/
http://127.0.0.1:8521/api/health
```

### 3.3 运行环境与统计后端

- Python 最低要求为 3.10；当前机器给定的解释器为 `E:\\python.exe`。
- R 是原始 count 统计分析的推荐后端；当前机器给定的 R 为 `E:\\R-4.4.2\\bin\\x64\\Rterm.exe`。
- R/Bioconductor 可用时，差异分析优先调用原生 DESeq2、edgeR、limma；预后分析优先调用 `survival::coxph`。
- 如果 R 或相应 R 包不可用，代码有透明标注的 Python 兼容后端。结果会写入 warning，论文级结果应安装并使用正确的 R 包后重新运行，而不能把 fallback 当成无条件等价替代。
- 默认 embedding 是本地 `sentence-transformers/all-MiniLM-L6-v2`；它与回答所用的 LLM API 是两条独立链路。只有用户明确配置 Hugging Face embedding API 时，embedding 才会走在线接口。
- LLM provider、API key、模型、OpenAI-compatible base URL 和 thinking 开关在设置中配置。thinking 默认关闭；只有当前模型已确认支持时，开启才会使用对应的 provider 参数。

常用环境变量：

| 变量 | 作用 |
|---|---|
| `E2SEQ_PYTHON` | 指定 Python 解释器 |
| `E2SEQ_LIBRARY_PATH` | 指定额外 Python 库路径 |
| `E2SEQ_R_EXE` | 指定 Rterm/R 解释器 |
| `E2SEQ_HOST` | 指定监听地址 |
| `E2SEQ_PORT` | 指定端口 |
| `E2SEQ_DATA_DIR` | 指定用户数据根目录 |
| `E2SEQ_DB_PATH` | 指定状态、记忆和向量库根目录 |
| `E2SEQ_HF_ENDPOINT` | 指定 Hugging Face 镜像/服务端点 |

API key、个人 token、虚拟环境、运行时下载的模型和用户数据不应提交到 GitHub。

## 4. 会话、数据和持久化 / Session, data and persistence

### 4.1 会话生命周期

1. 点击新建对话时，前端创建或接收一个新的 `chat_id`。
2. 上传文件、配置列、启动分析和发送问题都带上这个 `chat_id`。
3. 后端以 `chat_id` 为命名空间保存数据文件、bulk 状态、统计结果、RAG 快照、向量集合、对话记录和 token/API 用量。
4. 切换到历史对话时，后端从持久化文件/SQLite/向量库恢复该会话；不要求重新上传文件，也不应该继承另一个会话的数据。
5. 删除对话时执行级联清理，避免“界面删除了但后台 RAG 还在”的残留。

### 4.2 主要存储对象

默认情况下，用户数据根目录是项目下的 `.e2seq\\user_data`，也可以由 `E2SEQ_DATA_DIR` 改变。状态数据库由 `E2SEQ_DB_PATH` 控制。

| 对象 | 当前保存内容 | 是否按会话隔离 |
|---|---|---|
| 原始上传文件 | count、clinical、h5ad、CSV 或结果表 | 是 |
| bulk manifest/config | 文件位置、列映射、分析类型、方法、协变量、提示词 | 是 |
| 统计结果 | 全量差异或 Cox 结果、元数据、warning、时间 | 是 |
| 筛选/选定表达项目 | 当前条件、选定基因、分析集合 | 是 |
| RAG JSON 快照 | 外部 API、本地库、文献、富集、网络和来源统计 | 是 |
| Chroma 向量集合 | 当前会话的可检索文档块 | 是 |
| 对话历史 | 用户问题、回答、消息时间等 | 是 |
| Agent 工作记忆 | 当前会话上下文与历史恢复内容 | 是 |
| 自定义 gene-annotation 文件 | 基因—注释记录，作为知识库来源 | 否，属于全局知识库 |
| 内置 STRING/HMDB/TRRUST/GutMGene 数据 | 项目/用户数据库目录中的本地种子数据 | 否，属于全局来源 |

自定义 gene-annotation 文件目前是全局知识库文件，不属于某一个对话。删除某个对话不会删除它；删除自定义知识库文件时才会删除该全局来源。

## 5. 数据入口 / Data entry points

当前界面名称统一使用“表达谱数据 / Expression Profile Data”，不把所有输入强行称作 bulk。系统接受的是能够被当前分析器读取、映射和计算的表达谱/统计结果数据。

### 5.1 原始 count + 临床变量

入口：`/api/bulk/upload`

一次上传两张表：

**原始 count 矩阵**

- 一列是表达项目/feature/gene ID。
- 后续列是样本。
- 差异分析要求 raw integer count；不能在上传前自行把 count 转成 log、TPM 或 z-score 后再选择 DESeq2/edgeR/limma-voom。

**临床变量表**

- 一行对应一个样本。
- 至少要有可以和 count 矩阵样本列对应的样本 ID 列。
- 可以包含分组、事件、随访时长、起始日期、结束/末次随访日期和协变量。

支持 CSV、TSV/TXT 和 Excel（`.csv`、`.tsv`、`.txt`、`.xlsx`、`.xls`）。上传后系统读取表头、行数、列值摘要、样本重叠情况和建议列；此时不做统计预处理。

### 5.2 已完成的差异/预后/多组结果表

入口：`/api/bulk/result-upload`，配置接口为 `/api/bulk/result-configure`。

适用于：

- 已经在 R、Python 或其他工具完成的差异结果。
- 已经完成的 Cox/预后结果。
- 一个结果表中包含多个组、多个 contrast、细胞亚群或其他条件。
- 只想提取某个效应值、表达值、P/FDR、HR 或某一组进行二次分析。

用户在对话框中选择列，不要求文件名固定。通常需要：

| 结果表字段 | 用途 |
|---|---|
| 表达项目 ID | 基因、feature、蛋白、峰或其他表达项目标识 |
| 表达/效应值 | 差异分析通常是 log2FC/表达值；预后通常是 HR 或 coefficient |
| P 值 | 可选显著性列 |
| FDR/padj | 可选显著性列 |
| 方向 | 可选；没有时根据效应值推断 |
| 分组/对比列 | 可选；支持多组/多 contrast |

P/FDR 列可以不提供。没有显著性列时，系统不会凭空补算 P 值或 FDR；右侧筛选会以已选择的效应/表达列和结果顺序等可用信息工作，具体以当前界面映射为准。既有统计结果不会被重新建模、归一化或校正。

### 5.3 h5ad、CSV 等表达谱文件

系统还保留通用表达谱入口，例如 h5ad 和 CSV。h5ad 会被读取为 AnnData；CSV/TSV 可以按当前界面选择表达项目列、组列、表达/效应列和其他元数据。单细胞数据和表达谱结果表走各自的配置和筛选逻辑，但最终都可以进入会话级 Agent RAG。

如果数据尚未配置完成，后端会拒绝数据问答；用户必须先完成必要的列选择/分析设置。

### 5.4 自定义知识库文件 / Custom knowledge base

入口：知识库页面的 `/api/knowledge-bases/upload`。

这里上传的不是 count 矩阵，而是 **gene-annotation** 表：

- 至少有一个基因/feature 标识列。
- 至少有一个注释列。
- 支持 CSV、TSV、TXT，当前上传大小限制为 50 MB，要求 UTF-8。
- 上传后解析成可供 Agent RAG 检索的知识来源。

它是全局来源，供之后新回答使用；不会随着某个会话删除。

### 5.5 基因列表交集 / Gene-list intersection

在表达项目选择区域，用户可以输入一批名字（通常一行一个），然后选择“与列表取交集”。系统将：

```text
统计结果
  ∩ 当前筛选条件
  ∩ 用户输入的基因/表达项目列表
  = 最终可选集合
```

最终只有交集中的项目会进入选定集合、第一次问题的 GO/KEGG/GSEA/STRING 和 RAG。输入列表不会改变原始统计结果。

## 6. 原始 count 的配置与建模 / Raw-count configuration and modeling

### 6.1 配置对话框

上传两张表并完成结构读取后，用户选择：

1. 做差异分析或预后分析。
2. 样本 ID 列。
3. 差异分析的分组列、对照组和实验组。
4. 预后分析的时间类型、事件列、事件阳性值，以及可选协变量。
5. 是否把临床变量作为校正变量；只有选择使用时，才选择具体协变量。
6. 可选的数据描述或数据级提示词，例如“这是一份乳腺癌表达谱差异分析数据”。留空则不添加默认提示词。

配置阶段会先做可运行性检查：

- count 样本列与临床样本 ID 至少匹配足够样本；当前校验要求至少匹配 3 个样本。
- 差异分析的两组必须不同，且每组至少有 2 个样本。
- 预后分析需要至少 5 个有效样本和至少 2 个事件。
- 日期型预后分析的起始/结束日期必须能解析，并且结束日期晚于起始日期。
- 事件阳性值必须明确，例如 `Dead`、`1` 或 `Yes`。

配置保存后，原始表仍保持原样。后端返回的核心语义是 `raw_counts_unchanged=True`。

### 6.2 差异分析 / Differential analysis

差异分析会对输入中满足条件的表达项目执行完整统计建模。当前支持三种方法：

#### DESeq2

```text
raw integer count
→ 统一低表达过滤
→ DESeq2 size-factor normalization
→ negative-binomial GLM
→ Wald test
→ Benjamini–Hochberg FDR（结果表中的 padj）
```

#### edgeR

```text
raw integer count
→ filterByExpr
→ TMM normalization
→ estimateDisp
→ glmQLFit
→ glmQLFTest
→ Benjamini–Hochberg FDR
```

#### limma-voom

```text
raw integer count
→ filterByExpr
→ TMM normalization
→ voom
→ lmFit
→ contrasts.fit
→ eBayes
→ Benjamini–Hochberg FDR
```

低表达过滤、归一化和校正全部发生在这个统计阶段，不发生在文件上传或单纯读取阶段。原始文件本身不会被覆盖。

### 6.3 预后分析 / Prognostic analysis

预后分析从原始 count 的分析时副本构造表达值，然后对每个可拟合表达项目执行 Cox proportional hazards regression。

表达转换可选：

- `VST`。
- `logCPM`。
- `log2(TPM+1)`；如果没有 gene length，当前实现会给出 warning，并可能回退为 `log2(CPM+1)`，需要在结果中注意这一点。

时间变量可选：

- 数值随访时长：选择一列，例如 days/months，并说明单位由输入数据提供。
- 年/月/日日期：选择起始日期列和结束/末次随访日期列，系统计算两个日期的差值；当前元数据以天为单位保存。

事件列和事件阳性值必须单独选择。临床协变量可选；只有用户选择校正并选中变量时，Cox 设计矩阵才会加入这些变量。没有选择协变量时，使用表达值作为主变量进行 Cox 分析。

结果包括 `coef`、`HR`、`z`、`pvalue`、`padj`、方向和有效样本数等字段。

### 6.4 全量建模与结果规模

当前 raw-count 配置默认 `all_genes=True`：

- 差异分析先对全量可用表达项目建模。
- 预后分析也先对全量可用表达项目建模。
- `top_n` 可以产生高/低表达、HR 高/低、亚群 top 等辅助集合，但它不是第一次提问时强制只保留 50 个基因的隐藏限制。
- 统计建模完成后，结果状态变成 `ready_for_filter`，右侧边栏才负责用户可见的筛选。

## 7. 进度、阻塞和“什么时候可以提问” / Progress and readiness

### 7.1 上传进度

上传使用带进度的请求。界面显示文件读取/上传百分比，并在两个文件都成功保存和结构检查后进入配置阶段。

上传完成不等于统计分析完成。原始 count 上传完成后，提示会明确说明尚未执行过滤、归一化和建模。

### 7.2 统计建模进度

原始 count 分析以后台任务执行，前端轮询：

```text
POST /api/bulk/analyze
        ↓
GET /api/bulk/status/{session_id}
        ↓
GET /api/bulk/result/{session_id}
```

状态中包含 `progress_percent`、`progress_phase`、消息日志、计时、结果预览和 selected genes。典型阶段包括：

```text
读取原始 count/临床变量
→ 样本对齐与模型校验
→ 统计建模
→ 结果整理与 FDR
→ 100% / ready_for_filter
```

只有状态进入 `ready_for_filter`、`ready` 或兼容的 `ready_without_rag` 后，数据问答才会通过后端的 ready 检查。未完成设置或仍在建模时，问答请求会被拒绝，而不是一边建模一边悄悄回答。

### 7.3 RAG/富集进度

RAG 不是统计建模的前置步骤。第一次问题携带当前选定表达项目后，进度才进入：

```text
准备选定表达项目
→ 读取知识来源
→ 并行执行 GO / KEGG / GSEA / STRING
→ 构建 RAG
→ 选定表达项目的 RAG 上下文已准备完成
```

进度百分比是任务阶段的可见进度和 heartbeat，不应被解释为每个 API 返回记录数的精确线性比例。系统同时保存建模、富集、RAG handoff、LLM 回答和 token 用量等计时信息。

## 8. 建模完成后的右侧筛选 / Right-side filtering after modeling

统计结果完成后，用户在右侧边栏筛选，不需要重新运行 DESeq2、edgeR、limma-voom 或 Cox：

### 差异结果常用筛选

- 显著性指标：FDR/padj 或 P 值。
- 显著性阈值：例如 `FDR ≤ 0.05` 或 `FDR < 0.01`。
- 表达变化指标：`log2FC`。
- 变化阈值：例如 `|log2FC| ≥ 0.5`。
- 方向：全部、上调、高表达或下调、低表达。

### 预后结果常用筛选

- FDR/padj 或 P 值。
- `HR` 阈值。
- 高风险/低风险方向。
- 结果顺序或效应大小。

### 共同功能

- 修改条件后即时更新当前结果数量。
- “当前条件下选择前 N 个”：`0` 表示全部；大于 0 时按当前结果顺序选前 N 个。
- 通过用户输入列表取交集。
- 显示“当前筛选结果 / 全部表达项目”和“已选表达项目”两个数；这两个数含义不同：前者是符合条件的候选集合，后者是将实际交给第一次问题/RAG 的集合。
- 只有点击选择或确认后，最终 selected genes 才会随问题发送到后端。

当前后端会对一次 bulk 问题收到的 selected gene 列表去重，并设置最多 2,000 个的安全上限。这不是旧的 50 基因 RAG 限制；top500、top1000 可以完整进入当前 handoff。若将来需要一次超过 2,000 个，应再设计分批 handoff，而不是误以为当前已无上限。

## 9. 第一次提问时的 Agent RAG 流程 / First-question Agent RAG

### 9.1 触发条件

第一次问题只有在以下条件同时满足时，才启动表达项目的批量知识整理：

1. 当前会话已经有可用的表达谱/统计结果。
2. 原始 count 的统计分析已经完成，状态不是 `uploaded`、`configuring` 或 `analyzing`。
3. 用户已经通过右侧筛选/交集/前 N 选择出 selected genes。
4. 用户发送了一个实际问题。

“上传完成”或“统计建模完成”本身不会自动启动 GO/KEGG/GSEA/STRING，也不会自动生成一份脱离用户问题的回答。

### 9.2 批量富集与网络

当前第一次问题会把选定集合交给并行任务：

- GO enrichment。
- KEGG enrichment。
- GSEA；使用统计结果中的排序值，若无法使用则使用有限的降级排序。
- STRING 网络/互作。

代码中的并行任务使用超时、进度回调和受控 worker；目的是让服务保持可响应，避免一个网络库或 permutation 任务无限占用 CPU。结果会保留到当前会话的统计结果/RAG 上下文中。

富集结果会保存完整的核心结构，给 LLM 的摘要只取代表性条目；这不是把所有基因删掉。源数据和统计结果仍按选定集合保存，摘要只是回答上下文压缩。

### 9.3 全量选定表达项目 RAG

当前 RAG handoff 的策略是：

```text
用户最终选定的表达项目集合
→ 去重
→ 保留每个选定项目的统计字段
→ 并行查询启用的在线 API 和本地数据库
→ 保存逐项目来源记录、文献记录和覆盖统计
→ 构建当前会话的 Chroma 向量库
→ 混合 dense + BM25 检索
```

重要含义：

- RAG 查询对象是用户最终选定的集合，不是固定取“最上面 50 个”。
- 逐基因/逐表达项目的统计值（log2FC、HR、P/FDR、方向等）会随 RAG handoff 保留，Agent 可以把统计证据和外部注释区分开。
- 当前策略记录为 `all-selected-genes; one initial literature query per gene; question-time literature retrieval remains enabled`。
- 文献来源会尝试 PubMed、Europe PMC 等；数据库注释来源和文献来源在来源审计中分开统计。
- 没有命中不等于没有调用成功。来源统计需要区分：请求成功但该项目没有记录、API 返回空、网络错误、超时和 key/权限问题。

### 9.4 向量化与本地 embedding

默认情况下：

- 采用本地 `sentence-transformers/all-MiniLM-L6-v2` 生成 embedding。
- Chroma 使用持久化客户端保存会话级集合。
- 检索同时使用 dense 相似度和 BM25，尽量兼顾语义相似与基因/数据库精确匹配。
- embedding 不等于 LLM 回答；本地 embedding 不会产生 LLM token 消耗。
- 如果配置了 Hugging Face embedding API，只有向量生成会改为在线调用；回答仍由设置中选定的 LLM provider 负责。

## 10. 后续问题的流程 / Later questions

第二次及之后的问题不应重新上传文件，也不应无条件重新构建同一份 RAG：

1. 后端按 `chat_id` 恢复数据、统计结果、selected genes、RAG 快照和对话记忆。
2. Agent 读取当前用户问题，而不是套用固定的“模块—互作—靶点”回答模板。
3. Agent 判断当前知识是否足够回答；若不够，继续按问题语义检索更相关的文献或数据库。
4. 如果问题涉及新的筛选条件或用户重新选择了表达项目，使用新的 selected set；必要时刷新对应的批量知识 handoff。
5. LLM 依据用户真正的问题综合回答，并标注所用的 LLM/API provider、模型、调用次数、token、耗时和主要来源。

因此用户可以问：

- 综合解释表达变化和预后风险。
- 只解释 FDR 小于 0.01 的项目。
- 比较某两个组或某个 contrast。
- 寻找最可能的互作或潜在靶点。
- 只看某个通路、某种临床亚组或某种文献证据。
- 要求使用中文、英文或标准科学语言。

回答样式由当前问题决定。可选的数据级提示词只补充数据背景；留空时不添加默认指令。知识库中“启用哪些来源”的变更只对新回答生效，不会篡改已经保存的历史回答。

### 10.1 面对 1,000 个表达项目时的回答策略

Agent 不应把 1,000 个基因逐个机械罗列。当前合理输出结构是：

1. 先给总体统计和主要模式。
2. 按方向、效应大小、显著性、通路、网络模块或证据层级进行聚类/归纳。
3. 给代表性项目、核心节点和边界案例，而不是重复完整列表。
4. 明确哪些结论来自上传结果，哪些来自 API/文献，哪些只是候选机制。
5. 需要完整列表时，再提供可下载/可展开的结构化结果，而不是把全部内容塞入回答正文。

## 11. 当前默认来源 / Current source catalog

当前 `ANSWER_SOURCE_CATALOG` 包含 20 个在线 API 和 4 个本地数据库：

### 11.1 在线 API / Online APIs

```text
UniProt
MyGene
QuickGO
Ensembl
ChEMBL
PubMed
Europe PMC
Reactome
GTEx
Human Protein Atlas
GWAS
CIViC
Alliance
Open Targets
ClinVar
cBioPortal
OmniPath
IntAct
HumanBase
ClinicalTrials
```

### 11.2 本地数据库 / Local databases

```text
STRING
HMDB
TRRUST
GutMGene
```

当前默认目录不再包含 BioGRID 和 DepMap。代码中可能仍有兼容模块或历史文件，但它们不属于当前默认批量查询集合，不能把兼容代码存在误认为默认 API 已成功接入。

用户可以在知识库/设置中调整启用来源，也可以上传 gene-annotation 文件作为自定义来源。每次回答的来源审计应至少说明：

- 实际启用和实际尝试的来源。
- 返回记录或命中表达项目数。
- 目标表达项目数/文献查询数。
- 成功、空结果、超时、错误和跳过的数量。
- 文献结果和结构化注释结果的区别。

“返回记录/检索目标”中的分母必须结合来源类型解释：基因注释 API 通常以选定表达项目数为目标；PubMed/Europe PMC 通常以文献查询数为目标，并另行统计返回文章数。因此 `x/1` 不能直接解读为“数据库只有一条记录”，而要看它对应的是一个查询单位还是一个基因命中单位。

## 12. 低 CPU 与并行策略 / CPU-aware parallelism

系统要求“尽量并行但不能让 Python 长时间占满 CPU”。当前采取的是受控并行，而不是无限创建任务：

- 原始 count 建模通过后台线程运行，并有 bulk model gate，避免多个重型统计任务同时争抢 CPU。
- 第一次问题的 GO/KEGG/GSEA/STRING 使用受控 worker、请求超时和进度回调。
- RAG 的多来源查询使用批量/并行策略，但仍受会话级检索 gate 和来源实现的并发限制。
- GSEA permutation 使用有界设置，避免网络或 permutation 任务无限运行。
- 浏览器断开或点击中止时，后台任务会收到取消标记，避免留下孤立的高 CPU RAG 任务。
- 进度 heartbeat 继续更新，不代表每个来源都必须返回一条记录。

影响速度的主要因素：表达项目数量、样本数量、R 后端速度、R 包状态、选定基因数量、启用来源数量、网络延迟、文献检索量、embedding 计算和 LLM 响应速度。系统显示实际耗时，不应把固定的“每个基因几秒”当成严格保证。

## 13. 删除对话时会发生什么 / What chat deletion removes

删除对话接口：

```text
DELETE /api/chats/{chat_id}
```

当前级联清理包括：

- 该会话的消息/SQLite transcript。
- count、clinical、h5ad、CSV、结果表等会话文件。
- bulk manifest、配置、统计结果、筛选状态和选定项目。
- 该会话的 RAG JSON 快照。
- 该会话的 Chroma vector collection。
- Agent session state、工作记忆和回答/token 使用记录。
- 内存中的 agent、dataset、bulk session、任务、进度、executor 引用。
- 正在运行的相关后台任务会设置取消/删除标记，防止任务完成后把数据重新写回来。

不会被某个对话删除的对象：

- 其他对话的数据和 RAG。
- 全局内置数据库。
- 全局自定义 gene-annotation 知识库文件。
- 项目代码和 Python/R 运行环境。

“清除数据”和“删除对话”是两个不同动作：清除数据可以只清除当前数据平面而保留会话记录；删除对话才是完整的会话级清理。清空全部历史时，服务会逐个执行会话清理，不能只删除左侧列表文字。

## 14. 主要 API 路由 / Main API routes

| 路由 | 作用 |
|---|---|
| `POST /api/upload` | h5ad/传统表达谱文件上传 |
| `POST /api/upload-csv` | CSV/TSV/Excel 表格上传 |
| `POST /api/configure-csv` | 配置既有结果/表达表的列与筛选入口 |
| `POST /api/configure-dataset` | 配置 h5ad/表达谱数据集 |
| `POST /api/bulk/upload` | 上传原始 count + 临床变量两张表 |
| `POST /api/bulk/result-upload` | 上传既有差异/预后/多组结果表 |
| `POST /api/bulk/configure` | 配置差异/预后类型、列、方法和协变量 |
| `POST /api/bulk/result-configure` | 配置既有结果表的列、组和效应指标 |
| `POST /api/bulk/analyze` | 排队执行完整 raw-count 统计建模 |
| `GET /api/bulk/status/{session_id}` | 获取上传/建模/RAG 进度和状态 |
| `GET /api/bulk/result/{session_id}` | 获取完整统计结果和元数据 |
| `POST /api/bulk/rag` | 显式触发/刷新选定集合的 bulk RAG handoff |
| `POST /api/chat` | 非流式 Agent 问答 |
| `POST /api/chat/stream` | SSE 流式 Agent 问答 |
| `POST /api/chat/abort` | 中止当前流式回答/相关任务 |
| `GET /api/chats` | 获取会话列表 |
| `DELETE /api/chats/{chat_id}` | 删除一个会话及其级联数据 |
| `DELETE /api/chats` | 清理全部会话 |
| `GET /api/knowledge-bases` | 查看全局知识库来源 |
| `POST /api/knowledge-bases/upload` | 上传 gene-annotation 文件 |
| `DELETE /api/knowledge-bases/{kb_id}` | 删除全局自定义注释文件 |
| `GET /api/health` | 检查服务健康状态 |

## 15. GitHub 可迁移范围 / GitHub portability

GitHub 下载者需要区分三类体积：

1. **核心代码和启动/配置文件**：此前盘点约 8.32 MB（约 7.93 MiB）。
2. **随项目提供的本地 RAG 种子 CSV**：约 81.53 MB（约 77.75 MiB），主要是 HMDB、STRING、GutMGene、TRRUST。
3. **推荐的代码 + 本地种子 + 文档包**：约 89.87 MB（约 85.71 MiB）。

纯核心代码包不包含默认本地 embedding 模型；但本次 GitHub 推荐发布包会额外带上 `models/embedding/all-MiniLM-L6-v2/`，因此下载该推荐包后不需要再次下载这一默认模型。模型文件约 91.58 MB；Python 依赖、R、Bioconductor 包、用户数据和 API key 仍不应与核心代码混在一起提交。

一个新手从 GitHub 复制后，应按下面顺序完成迁移：

```text
复制项目
→ 安装 Python 依赖
→ 配置 E2SEQ_PYTHON / E2SEQ_R_EXE（raw count 需要 R）
→ 启动 start.py 或 launch_server.bat
→ 打开网页并配置 LLM API
→ 需要 RAG 时准备本地 embedding 或配置 Hugging Face embedding API
→ 上传数据、完成列选择、完成统计建模
→ 筛选并选定表达项目
→ 第一次提问触发富集和 Agent RAG
```

## 16. 用户实际操作清单 / User checklist

### 原始 count 工作流

1. 新建对话。
2. 上传 count 矩阵和临床变量表。
3. 等待上传进度到 100%，检查样本匹配数。
4. 选择差异分析或预后分析。
5. 选择正确的样本 ID、分组/时间/事件/日期列。
6. 如需要校正，再选择临床协变量；不需要时保持不选。
7. 选择 DESeq2、edgeR、limma-voom，或选择表达转换并运行 Cox。
8. 等待统计建模到 `ready_for_filter`，期间不要提问。
9. 在右侧筛选 FDR/P、log2FC/HR、方向和前 N。
10. 如有外部基因列表，取交集并确认 selected genes。
11. 第一次提问；这时才执行 GO/KEGG/GSEA/STRING 和全量选定集合 RAG。
12. 后续问题直接复用该对话的数据和知识，Agent 按问题继续检索或综合。

### 已有结果表工作流

1. 新建对话。
2. 上传结果表。
3. 选择表达项目 ID、效应/表达、P/FDR、方向、组/contrast 等列。
4. 如果没有 P/FDR，只使用已有效应值和结果顺序筛选；系统不会重新计算。
5. 在右侧筛选并选择表达项目。
6. 第一次提问后进入同样的富集、网络和 Agent RAG 流程。

## 17. 当前限制与科学解释 / Current limitations

- 原始 count 的差异分析必须是整数 count；已经 log 转换的矩阵不能直接当作 DESeq2/edgeR/limma-voom raw count 输入。
- R/Bioconductor 是发表级 raw-count 结果的推荐后端；如果结果 warning 标明使用 Python fallback，应先修复 R 依赖再作最终科学结论。
- 日期型生存分析得到的是日期差值；必须确认输入日期的临床含义、删失编码和单位。
- 没有 P/FDR 的用户结果表不会被系统虚构出显著性统计量。
- API 返回 0 可能是合法的空命中，也可能是接口/网络/权限问题；回答中的来源审计需要把这些状态区分开。
- 选定集合越大，第一次问题的 GO/KEGG/GSEA/STRING、全量 API/RAG 和 LLM 上下文整理耗时越长；当前 bulk 问题 handoff 的后端安全上限为 2,000 个 selected genes。
- RAG 的存在不保证每个问题都必须展示一长串基因；Agent 应根据问题把大量结果压缩为模式、通路、网络和代表性证据，并在需要时提供结构化明细。
- 删除会话不会删除全局自定义注释库；这是为了让其他对话继续使用同一知识源。

## 18. 当前流程结论 / Final status

当前实际流程可以概括为：

```text
先上传并配置
→ 原始 count 先全量建模，既有结果不重算
→ 建模完成后右侧实时筛选
→ 用户决定最终表达项目集合
→ 第一次提问才并行富集、网络和全量选定集合 RAG
→ Agent 根据问题综合回答，必要时每次追加文献检索
→ 会话级保存数据、RAG、记忆和用量
→ 删除会话时级联删除该会话全部数据与 RAG
```

这就是当前 E2seq 的实际“API + Agent RAG”工作流；统计建模、知识构建、问答综合和会话存储是四个相互连接但职责分开的阶段。
