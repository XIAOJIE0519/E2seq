# E2seq —— Easy to Chat with Sequencing

**面向兼容表达谱数据的 Agent + RAG 分析与科学解读工具。**

[English](README.md) · [安装说明](docs/installation.md) · [简明教程](docs/user_guide.md)

## E2seq 做什么

E2seq 不把输入限定为某一种实验类型，可载入表达/count 表、临床变量、已有差异或预后结果、多组结果表，以及兼容的单细胞文件。用户在界面中自行选择需要的列。

原始 count 上传时不做过滤或归一化。完成配置后，对全部有效输入先进行所选统计建模，再在右侧实时按条件筛选和选择前 N 项。已有结果表按原样载入，不重新计算。

## Agent + RAG 流程

1. 上传数据并映射列。
2. 对全部有效数据执行所选统计分析，或直接载入已有结果表。
3. 在右侧筛选并明确选择表达项目。
4. 第一次提问时，对选定项目执行适用的批量富集/网络分析，并构建持久化的多来源 RAG 上下文。
5. 每次提问时，Agent 判断已有证据是否足够；必要时继续检索更相关的文献或数据库记录，最后结合上传数值和检索证据综合回答。

上传统计结果与外部证据始终分开。知识库页面的来源选择只对新回答生效；默认提示词是可选项，并随具体数据保存。

## 启动

```bash
python -m pip install -e .
python start.py
```

新机器可直接从 GitHub 复制：

```bash
git clone https://github.com/XIAOJIE0519/E2seq.git
cd E2seq
python start.py
```

不要复制其他机器的 `venv`、`.e2seq`、`.env`、缓存或上传数据。双语启动器会重新检测
Python 环境，并询问库路径、可选的 R 路径和缺失依赖；Windows 也可双击
`launch_server.bat`。

Windows 用户也可以双击 `launch_server.bat`。双语启动器会自动识别项目目录，让用户设置 Python、库目录和可选的 R 路径，只检查服务端实际需要的依赖，缺少时再询问是否安装，并自动选择可用端口。

可迁移的非交互启动示例：

```bash
python start.py --python <python解释器> --r <R解释器> --port 8521 --non-interactive
```

如需把路径或数据放在项目外，可设置 `E2SEQ_PYTHON`、`E2SEQ_LIBRARY_PATH`、`E2SEQ_R_EXE`、`E2SEQ_DATA_DIR`、`E2SEQ_HOST` 和 `E2SEQ_PORT`。只有原始 count 统计建模需要 R；已有结果和兼容的单细胞流程不要求 R。

## 支持的输入

- 表格：CSV、TSV、XLSX。
- 原始建模：一份表达/count 表 + 一份临床变量表。
- 已有结果：一份包含表达项目 ID 和效应值/表达值的表；P/FDR/分组/方向列可选。
- 单细胞：H5AD、CSV；安装相应读取器后可读 RDS。

## 运行体积

源代码、Python 环境、R 及 R 包、本地数据库、Embedding 模型和用户数据分别计算。当前任务的启动审计会给出实测大小；只部署程序代码时不需要复制数据库和数据文件。

## 许可证

MIT。
