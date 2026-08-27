# E2seq — Easy to Chat with Sequencing

**Agent + RAG interpretation and analysis for compatible expression-profile data.**

[中文说明](README_CN.md) · [Installation](docs/installation.md) · [Quick guide](docs/user_guide.md)


<img width="1920" height="1080" alt="Figure1" src="https://github.com/user-attachments/assets/41e0f2a7-7507-4ce6-abdd-e6916ac0e533" />

<img width="2557" height="1372" alt="image" src="https://github.com/user-attachments/assets/276968c3-4392-41b4-a2b6-d9ab1fd749ce" />

## What E2seq does

E2seq accepts compatible expression-profile files rather than assuming one assay type. It can read expression/count tables, clinical variables, existing differential or prognostic result tables, multi-group tables, and compatible single-cell files. Users choose the relevant columns in the interface.

Raw counts are not filtered or normalized during upload. After configuration, the selected statistical workflow models all valid input items first; the right panel then provides live filtering and first-N selection. Existing result tables are loaded as supplied and are not recomputed.

## Agent + RAG workflow

1. Upload and map the data.
2. Run the requested full statistical model, or load an existing result table.
3. Filter and explicitly select expression items.
4. On the first question, the Agent runs the applicable selected-item enrichment/network batch and builds a persistent multi-source RAG context.
5. For every question, the Agent decides whether the existing evidence is sufficient, retrieves more relevant literature or source records when needed, and synthesizes an answer grounded in the uploaded values and retrieved evidence.

The system keeps uploaded statistics separate from external evidence. Source selection in the Knowledge Base page applies to new answers; a dataset prompt is optional and is stored with that dataset.

## Start

```bash
python -m pip install -e .
python start.py
```

For a new machine / 新机器：

```bash
git clone https://github.com/XIAOJIE0519/E2seq.git
cd E2seq
python start.py
```

Do not copy `venv`, `.e2seq`, `.env`, caches, or uploaded data between
machines. The bilingual launcher detects the new Python environment and asks
only for paths and missing dependencies. / 不要在机器之间复制 `venv`、`.e2seq`、`.env`、
缓存或上传数据；双语启动器会在新机器上重新检测 Python，并只询问路径和缺失依赖。

Windows users can double-click `launch_server.bat`. The bilingual launcher detects the project directory, lets you select Python/library/R paths, checks only the imports required by the server, offers to install missing packages, and selects a free port.

For portable automation:

```bash
python start.py --python <python-executable> --r <R-executable> --port 8521 --non-interactive
```

Use `E2SEQ_PYTHON`, `E2SEQ_LIBRARY_PATH`, `E2SEQ_R_EXE`, `E2SEQ_DATA_DIR`, `E2SEQ_HOST`, and `E2SEQ_PORT` when paths or storage must be outside the project. R is needed only for raw-count modeling; precomputed results and compatible single-cell workflows can start without it.

## Supported inputs

- Tables: CSV, TSV, XLSX.
- Raw modeling: expression/count table + clinical-variable table.
- Existing results: one table with an expression-item ID and an effect/value column; P/FDR/group/direction are optional.
- Single-cell: H5AD and CSV; RDS when the corresponding reader is installed.

## Runtime footprint

The source tree, Python environment, R installation/packages, local databases, embedding model, and uploaded datasets are separate. See the startup audit report in the current task for measured sizes; do not copy databases or datasets when only the application code is needed.

## License

MIT.
