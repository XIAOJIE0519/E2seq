# 生物信息学API调用工具集

本目录包含了常用生物信息学数据库的API调用示例代码。

## 📁 可用的API文件

### ✅ 核心API（必须 - 已测试通过）

1. **mygene_api.py** - MyGene.info 基因注释（替代多个API）
2. **string_api.py** - STRING 蛋白质互作网络
3. **quickgo_api.py** - QuickGO GO注释
4. **europepmc_api.py** - Europe PMC 文献检索

### ✅ 增强API（推荐 - 已测试通过）

5. **chembl_api.py** - ChEMBL 药物/化合物
6. **ensembl_api.py** - Ensembl 基因组信息

### ✅ 基础API（已测试通过）

7. **uniprot_api.py** - UniProt 蛋白质数据库
8. **pubchem_api.py** - PubChem 化合物数据库
9. **pubmed_api.py** - PubMed 文献数据库

---

## 🚀 快速开始

### 1. MyGene.info - 基因注释（推荐）

```python
from mygene_api import MyGene_API

api = MyGene_API()

# 查询基因信息
result = api.query_gene("TP53")
print(f"Entrez ID: {result['entrez_id']}")
print(f"基因名称: {result['name']}")
print(f"UniProt ID: {result['uniprot']['Swiss-Prot']}")
print(f"Ensembl ID: {result['ensembl']['gene']}")
```

**返回信息包括：**
- Entrez Gene ID
- 基因符号和名称
- 基因组位置
- Ensembl ID
- UniProt ID
- 基因类型

---

### 2. STRING - 蛋白质互作网络

```python
from string_api import STRING_API

api = STRING_API()

# 获取蛋白质相互作用
result = api.get_interactions("TP53", limit=10)
for interaction in result['interactions']:
    print(f"{interaction['partner']}: score={interaction['score']}")

# 获取蛋白质网络图
proteins = ["TP53", "BAX", "BCL2", "CASP3", "CASP9"]
result = api.get_network_image(proteins)
print(f"网络图URL: {result['image_url']}")
```

**返回信息包括：**
- 相互作用蛋白列表
- 相互作用评分
- 网络图像URL

---

### 3. QuickGO - GO注释

```python
from quickgo_api import QuickGO_API

api = QuickGO_API()

# 获取GO注释（需要使用UniProt ID）
result = api.get_go_annotations("P04637")  # TP53的UniProt ID
for annotation in result['annotations'][:5]:
    print(f"{annotation['go_id']}: {annotation['go_aspect']}")

# 获取GO term详细信息
result = api.get_go_term("GO:0006915")  # apoptosis
print(f"名称: {result['name']}")
print(f"定义: {result['definition']}")
```

**返回信息包括：**
- GO ID和名称
- GO分类（biological_process/molecular_function/cellular_component）
- 证据代码
- GO term定义

---

### 4. Europe PMC - 文献检索

```python
from europepmc_api import EuropePMC_API

api = EuropePMC_API()

# 搜索文献
result = api.search_articles("TP53 AND cancer", page_size=5)
print(f"总共找到: {result['total_hits']} 篇文献")

for article in result['articles']:
    print(f"标题: {article['title']}")
    print(f"期刊: {article['journal']}")
    print(f"引用次数: {article['citation_count']}")
```

**返回信息包括：**
- PMID
- 标题和作者
- 期刊和发表年份
- DOI
- 引用次数

---

### 5. ChEMBL - 药物/化合物

```python
from chembl_api import ChEMBL_API

api = ChEMBL_API()

# 搜索化合物
result = api.search_compound("aspirin")
for compound in result['compounds']:
    print(f"ChEMBL ID: {compound['chembl_id']}")
    print(f"名称: {compound['pref_name']}")
    print(f"临床阶段: {compound['max_phase']}")
```

**返回信息包括：**
- ChEMBL ID
- 化合物名称
- 分子类型
- 临床开发阶段

---

### 6. Ensembl - 基因组信息

```python
from ensembl_api import Ensembl_API

api = Ensembl_API()

# 查询基因信息
result = api.lookup_gene("TP53")
print(f"Ensembl ID: {result['ensembl_id']}")
print(f"染色体: {result['chromosome']}")
print(f"位置: {result['start']}-{result['end']}")

# 获取基因序列
result = api.get_sequence(result['ensembl_id'])
print(f"序列长度: {result['sequence_length']} bp")
```

**返回信息包括：**
- Ensembl ID
- 基因描述
- 染色体位置
- 基因序列

---

## 📊 API测试结果

| API | 状态 | 说明 |
|-----|------|------|
| MyGene.info | ✅ | 成功 - 推荐用于基因注释 |
| STRING | ✅ | 成功 - 蛋白质互作网络 |
| QuickGO | ✅ | 成功 - 需要UniProt ID |
| Europe PMC | ✅ | 成功 - 文献检索 |
| ChEMBL | ✅ | 成功 - 药物化合物 |
| Ensembl | ✅ | 成功 - 基因组信息 |
| UniProt | ✅ | 成功 - 蛋白质信息 |
| PubChem | ✅ | 成功 - 化合物信息 |
| PubMed | ✅ | 成功 - 文献检索 |


---

## 💡 使用建议

### 基因查询工作流

1. **MyGene.info** - 获取基因基本信息和各种ID
2. **UniProt** - 获取蛋白质详细信息（使用MyGene返回的UniProt ID）
3. **STRING** - 获取蛋白质相互作用网络
4. **QuickGO** - 获取GO功能注释（使用UniProt ID）
5. **Ensembl** - 获取基因组位置和序列

### 代谢物查询工作流

1. **PubChem** - 搜索化合物基本信息
2. **ChEMBL** - 查询药物相关信息

### 文献检索工作流

1. **PubMed** 或 **Europe PMC** - 搜索相关文献
2. Europe PMC提供引用次数，更适合评估文献影响力

---

## 🔧 安装依赖

```bash
pip install requests
```

---

## 📝 测试示例

```bash
# 测试所有核心API
python mygene_api.py
python string_api.py
python quickgo_api.py
python europepmc_api.py

# 测试增强API
python chembl_api.py
python ensembl_api.py

# 测试基础API
python uniprot_api.py
python pubchem_api.py
python pubmed_api.py
```

---

## 🎯 综合使用示例

查看 `example_usage.py` 了解如何整合多个API进行综合查询。

---