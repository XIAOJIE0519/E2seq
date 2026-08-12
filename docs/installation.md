# E2seq installation and startup / E2seq 安装与启动

## 1. Copy and requirements / 复制项目与环境要求

For a clean GitHub copy, use HTTPS and do not copy a local `venv`, `.e2seq`,
`.env`, cache, or uploaded-data directory. / 从 GitHub 复制时使用 HTTPS；不要把本机的
`venv`、`.e2seq`、`.env`、缓存或上传数据目录复制到新环境。

```bash
git clone https://github.com/XIAOJIE0519/E2seq.git
cd E2seq
```

- Python 3.10+ with pip / Python 3.10 及以上，并可使用 pip。
- R is optional for startup. It is required only when modeling raw count data; precomputed result tables and compatible single-cell files do not require R. / R 不是启动必需项；只有原始 count 统计建模需要 R，已有结果表和兼容的单细胞文件不要求 R。
- The default embedding model is local. Hugging Face API mode is optional. / Embedding 默认本地运行，Hugging Face API 模式可选。

RDS input is optional. Install the reader only when needed: / RDS 输入为可选功能，只有需要时安装读取器：

```bash
python -m pip install -e ".[rds]"
```

## 2. Install / 安装

From the project directory / 在项目目录中运行：

```bash
python -m pip install -e .
```

The launcher checks the actual server import graph and offers to install only missing Python packages. / 启动器会检查服务端真实导入链，只在发现缺少依赖时询问是否安装。

## 3. Start / 启动

Recommended / 推荐：

```bash
python start.py
```

The bilingual launcher asks for Python, its library path, and an optional R executable, then asks for a free port. / 双语启动器会询问 Python、Python 库目录和可选的 R 解释器，并检查可用端口。

Portable non-interactive example / 可迁移的非交互示例：

```bash
python start.py --python <python-executable> --r <Rterm-or-R-executable> --port 8521 --non-interactive
```

Windows shortcut / Windows 快捷启动：

```bat
launch_server.bat
```

On the first run, press Enter to accept detected Python/library paths, enter R
only if raw-count modeling is needed, and allow installation of missing Python
packages when prompted. / 首次运行时，检测到的 Python/库路径可直接回车接受；只有需要原始
count 建模时才填写 R；如果提示缺少 Python 依赖，选择安装即可。

Useful environment variables / 常用环境变量：

```text
E2SEQ_PYTHON           Python executable / Python 解释器
E2SEQ_LIBRARY_PATH     Python site-packages / Python 库目录
E2SEQ_R_EXE            Rterm/R executable / R 解释器
E2SEQ_DATA_DIR         persistent data root / 持久化数据根目录
E2SEQ_HOST             bind address / 监听地址
E2SEQ_PORT             service port / 服务端口
```

After startup, open the printed Web URL. `/api/health` is the basic health check. / 启动后打开终端打印的网页地址；`/api/health` 可用于基础健康检查。

## 4. R packages for raw counts / 原始 count 所需 R 包

Install only the packages needed by the selected workflow. / 只安装所选流程需要的 R 包：

- Differential expression / 差异分析: `DESeq2`, `edgeR`, `limma`。
- Survival / 预后分析: `survival`。
- JSON bridge / JSON 桥接: `jsonlite`。

If R is not found, E2seq reports the reason and keeps precomputed-table workflows available. / 找不到 R 时，E2seq 会明确报告原因，同时仍可使用已有结果表流程。
