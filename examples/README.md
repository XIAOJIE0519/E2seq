# Examples / 示例

The examples are optional direct Python demonstrations. The main web product
uses the Agent + RAG workflow described in `docs/user_guide.md`.

这些示例是可选的 Python 直接调用演示；主网页使用 `docs/user_guide.md` 中的
Agent + RAG 流程。

## Web interface / 网页启动

From the project root:

在项目根目录运行：

```bash
python start.py
```

Open the URL printed by the launcher. The default is
`http://127.0.0.1:8521`; use `--port` to choose another free port.

打开启动器打印的地址。默认地址是 `http://127.0.0.1:8521`；也可以用
`--port` 指定其他空闲端口。

## Optional scripts / 可选脚本

- `basic_usage.py`: single-cell loading and common analysis tools.
- `advanced_usage.py`: lower-level tool and visualization examples.
- `../api/example_usage.py`: direct UniProt, PubChem, and PubMed queries.

- `basic_usage.py`：单细胞读取与常用分析工具。
- `advanced_usage.py`：底层工具和可视化示例。
- `../api/example_usage.py`：直接调用 UniProt、PubChem、PubMed。

## Data / 数据

Use your own compatible expression-profile table or `.h5ad` file. The web UI
asks you to choose the gene/feature, group, expression, and significance
columns, so the file does not need a fixed filename.

可使用自己的兼容表达谱表格或 `.h5ad` 文件。网页会让你选择基因/表达项目、
组别、表达值和显著性列，不要求固定文件名。
