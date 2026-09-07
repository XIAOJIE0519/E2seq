# psoriasis - glm-5.2

- Benchmark system: E2seq + Agent RAG
- Repeat: 2
- Task type: DISEASE-STATE
- Tissue / sample source: lesional skin
- Comparison or endpoint: psoriatic lesional skin versus normal control skin
- Answer input cohort: Discovery/Core only
- Selected items: 100
- Input fields: gene name, effect size (log2FC/HR), P value, FDR
- E2seq Agent RAG: enabled
- Conversation memory: disabled
- Thinking mode: disabled
- Held-out validation data in prompt/RAG: no
- Model API: Zhipu AI / glm-5.2
- Message SHA-256: d1a33d3f606c81814c4fb94a6c63c8f1abebd3bde37d769e82eae4772d8ff873
- Response HTTP status: 200
- Prompt tokens: 45120
- Completion tokens: 11101
- Reasoning tokens: 0
- Total tokens: 56221
- API requests reported: 4
- Elapsed seconds: 289.68
- RAG status: reused_or_ready
- RAG records/genes reported: 100
- RAG elapsed seconds: 1150.303
- Question handoff seconds: 1163.566
- Final benchmark system: E2seq; file rank 2/5; original repeat 2; model vendor: Zhipu AI

---
# 银屑病皮损皮肤转录组多维解读

## 1. 总体生物学解读

本队列100个基因中90个上调、10个下调，FDR均≤10⁻⁶²，呈现银屑病皮损典型的炎症-分化双重特征。上调基因集中体现三大主题：IL-36/IL-19/IL-20/IL-26细胞因子轴驱动的IL-17信号通路激活、S100A7/A8/A12与β-防御素（DEFB4A/4B/103A/103B）构成的先天免疫/抗菌反应、以及SPRR2家族、LCE3A/3D、KRT6A、SERPINB3/4/13主导的角化包膜重塑与异常分化。下调基因多为非编码RNA或代谢相关基因（如BTC、CYP2W1），可能反映正常皮肤屏障功能的丧失。该谱型与银屑病"炎症-增殖-分化异常"三联病理高度一致。

## 2. 核心生物学程序

**程序一：IL-17/IL-36炎症信号轴** — 上调。支持基因：IL36A（log2FC=11.37）、IL36G（5.68）、IL19（7.58）、IL20（5.67）、IL26（4.36）、IL36RN（3.01）、TNIP3（7.28）、ZC3H12A（3.85）、IRAK2（2.08）。对应KEGG: IL-17 signaling pathway、Cytokine-cytokine receptor interaction。IL36A为效应最显著基因，IL19/IL20为IL-20受体家族成员，IL36RN作为天然拮抗剂同步上调提示反馈调控。TNIP3为NF-κB负调控因子，ZC3H12A（Regnase-1）为mRNA稳定性调控因子，两者共同提示炎症信号存在负反馈层。证据强度：多基因高度一致，FDR极显著（10⁻⁶²至10⁻⁹⁸），KEGG检索独立支持IL-17通路命中。局限：无法区分角质形成细胞与免疫细胞来源。

**程序二：先天抗菌防御** — 上调。支持基因：S100A7（7.09）、S100A7A（9.83）、S100A8（7.73）、S100A12（8.33）、DEFB4A（11.18）、DEFB4B（11.03）、DEFB103A/103B（5.76）、PI3（9.24）。对应GO: Antimicrobial humoral response (GO:0019730)、Response to lipopolysaccharide (GO:0032496)。S100A12与DEFB4A/4B为银屑病皮损标志分子，PI3（丝氨酸蛋白酶抑制剂）参与表皮抗菌屏障。证据强度：基因数最多、效应值最高、GO直接命中。局限：防御素高表达可能部分源于角质形成细胞增殖加速而非纯抗菌功能。

**程序三：角化包膜重塑与异常分化** — 上调。支持基因：SPRR2A（7.31）/2B（6.38）/2D（5.92）/2E（3.99）/2F（7.22）/2G（4.75）/3（7.18）、LCE3A（8.30）/3D（5.31）、KRT6A（4.30）、SERPINB3（6.74）/4（9.12）/13（3.09）、GJB2（4.42）、GJB6（3.02）、KLK13（4.05）。对应Reactome: Formation of the cornified envelope (R-HSA-6809371)；GO: Epidermis development (GO:0008544)。SPRR与LCE家族为角化包膜前体蛋白，KRT6A为银屑病经典标志角蛋白，SERPINB3/4为角质形成细胞蛋白酶抑制剂。证据强度：Reactome直接命中12基因，STRING网络中SPRR家族与KRT6A形成密集互作簇。局限：角化包膜重塑可能是继发于增殖加速的代偿反应。

**程序四：类花生酸与脂质代谢重塑** — 上调。支持基因：PLA2G4D（4.61）、PLA2G4E（2.47）、AKR1B10（6.27）、AKR1B15（5.23）、FABP5（3.65）。PLA2G4D/E为磷脂酶A2家族，释放花生四烯酸为类花生酸合成提供前体；AKR1B10/15为醛酮还原酶，参与脂质过氧化代谢；FABP5为表皮脂肪酸结合蛋白。证据强度：多基因同向且FDR<10⁻⁷⁹，STRING中PLA2G4D/E通过GNAS形成间接连接。局限：无独立KEGG通路直接命中，AKR1B10在银屑病中的特异性不明，其文献主要关联肿瘤化疗耐药（PMID:39017606）。

**程序五：免疫检查点与趋化信号** — 上调。支持基因：CD274/PD-L1（3.44）、CXCL13（5.89）、CXCR2（2.70）、GPR15LG（5.52）、WNT5A（2.53）、PRKCQ（2.88）。CD274上调提示皮损微环境免疫调节/耗竭；CXCL13/CXCR2介导免疫细胞募集；PRKCQ为T细胞受体信号关键激酶。证据强度：基因独立但通路覆盖分散，CD274与CXCL13有银屑病文献支持（PMID:40560938）。局限：CD274上调可能源于炎症微环境的继发响应而非主动免疫逃逸；抗PD-1治疗有诱发银屑病样皮炎的报道，方向性复杂。

## 3. 关键基因与互作模块

| 基因/模块 | 方向 | 程序归属 | 互作类型 |
|---------|------|---------|---------|
| **IL36A** | ↑11.37 | 炎症信号轴 | 通路共成员（IL36G/IL36RN经IL1RAP）；STRING间接互作 |
| **S100A12** | ↑8.33 | 先天抗菌 | STRING互作（S100A7/S100A7A/FABP5/SERPINB3/SERPINB4） |
| **DEFB4A/4B** | ↑11.18/11.03 | 先天抗菌 | STRING互作（DEFB103A/103B、CCR6） |
| **SPRR2A-2G簇** | ↑3.99–7.31 | 角化包膜 | STRING互作簇（SPRR2B与5个家族成员） |
| **SERPINB3/4/13** | ↑3.09–9.12 | 角化包膜/蛋白酶抑制 | STRING互作（CTSG连接三个成员） |
| **KRT6A** | ↑4.30 | 异常分化 | STRING互作（SPRR2A/2B/2D） |
| **CD274** | ↑3.44 | 免疫检查点 | 无直接互作证据 |
| **KYNU** | ↑4.42 | 犬尿氨酸代谢 | 通路共成员（炎症代谢） |
| **WNT5A** | ↑2.53 | 信号/分化 | 无STRING互作记录 |
| **BTC** | ↓−4.30 | 下调模块 | 无互作证据 |

**互作类型说明**：SPRR2家族与KRT6A间的STRING边代表共表达/通路共成员证据，非直接物理相互作用。IL36A/IL36G/IL36RN通过IL1RAP形成STRING互作，为通路共成员关系。DEFB4A/4B与CCR6的STRING连接可能反映防御素-趋化受体功能关联，非直接物理结合。S100A12与S100A7/S100A7A的STRING边代表同家族蛋白的序列/功能关联。

## 4. 验证优先级

**1. IL-36信号轴调控机制（机制假说）**
- 当前证据：IL36A/IL36G/IL36RN同步上调，IL36RN作为拮抗剂上调提示负反馈
- 外部证据：IL-36通路为银屑病公认机制，spesolimab（抗IL-36R）已获批用于泛发性脓疱型银屑病
- 下一步：原位杂交或单细胞RNA-seq确认IL36A细胞来源；IL36RN/IL36A比值与PASI评分关联分析
- 结论级别：**支持假说**

**2. S100A12/DEFB4A作为皮损生物标志物（生物标志物）**
- 当前证据：效应值极高（8.33/11.18），FDR<10⁻⁶⁸
- 外部证据：S100A12与DEFB4A为银屑病经典标志分子（PMID:40560938）
- 下一步：血清/皮损匀浆ELISA检测，与疾病严重程度相关分析
- 结论级别：**支持假说**

**3. CD274/PD-L1免疫检查点调控（治疗靶点）**
- 当前证据：CD274上调3.44倍，FDR=1.82×10⁻⁶³
- 外部证据：PD-L1组合免疫治疗在多种疾病有临床探索（PMID:38354028）；但抗PD-1可能诱发银屑病样皮炎，方向性存在矛盾
- 下一步：银屑病皮损T细胞体外阻断实验；注意反向风险
- 结论级别：**探索假说**

**4. SPRR2-KRT6A角化包膜互作网络（互作/网络假说）**
- 当前证据：STRING网络密集连接，Reactome角化包膜通路命中12基因
- 外部证据：KRT6A为银屑病经典标志（PMID:42216026）
- 下一步：3D表皮模型中SPRR2敲低对角化包膜完整性影响
- 结论级别：**支持假说**

**5. 细胞组成混杂检查（混杂/组成检查）**
- 当前证据：免疫基因（CXCL13/CXCR2/CD274）与角质形成细胞基因（KRT6A/SPRR2）混合上调，无法区分细胞来源
- 下一步：CIBERSORT/xCell去卷积分析；流式分选后RNA-seq
- 结论级别：**必须执行的质控**

## 5. 证据溯源

- **直接证据（输入数据）**：100个基因log2FC与FDR为本队列唯一统计来源，所有结论的效应方向和显著性均基于此
- **通路/本体证据**：GO/KEGG/Reactome检索结果为独立注释，非本研究重新计算的富集P值；通路复发为检索命中而非新计算统计量
- **互作证据**：STRING边为数据库互作记录，来源可能部分依赖共发表文献，非完全独立
- **疾病关联证据**：GWAS目录覆盖100/100基因，但GWAS关联不等同于表达差异因果
- **文献证据**：PMID:40560938（银屑病WGCNA生物标志物）与PMID:38354028（PD-L1组合免疫治疗）提供疾病相关性支持；PMID:42216026支持KRT6A在毛发疾病中的标志作用，但非银屑病直接证据
- **独立队列验证**：未提供外部统计验证；通路复发、数据库覆盖率和文献支持不构成复制证据

## 6. 局限性与替代解释

1. **细胞组成混杂**：皮损中免疫细胞浸润增加可独立产生免疫基因上调信号，角质形成细胞增殖加速可独立产生分化基因上调信号。需去卷积分析（CIBERSORT/xCell）或流式分选后单细胞RNA-seq区分细胞来源。
2. **治疗暴露未记录**：未提供治疗信息，局部糖皮质激素或维生素D类似物可能影响免疫基因与分化基因表达谱。
3. **疾病严重度未分层**：PASI评分未记录，严重度差异可能驱动效应量变异；轻度与重度银屑病的分子谱可能存在质的差异。
4. **非编码基因功能未知**：LOC105376238、LOC107984452等下调非编码RNA功能不明，无法进行可靠的生物学解读，标注为"insufficient evidence"。
5. **关联非因果**：所有差异表达为横断面关联，不能推断因果方向；上调基因可能是疾病原因、后果或旁观者效应。

外部统计验证未执行；以上解读基于输入队列统计值与外部注释/文献的整合，通路富集为检索复发而非新计算的P值。

E2seq statistical audit: selected=100, ledger=100, RAG records=100, numeric claims checked=2, external claims checked=0, external mismatches=0, status=passed.

Answer model API: Zhipu AI / glm-5.2

Source coverage (gene sources = selected items with records / selected RAG items; literature sources = articles / queries)
Online APIs: alliance 91/100 selected items (records returned); cbioportal 91/100 selected items (records returned); chembl 11/100 selected items (partially returned; some queries failed); civic 4/100 selected items (records returned); clinicaltrials 40/100 selected items (records returned); clinvar 90/100 selected items (records returned); ensembl 44/100 selected items (partially returned; some queries failed); europepmc 848 articles / initial full-cohort RAG 100 queries + 4 current-round queries; gtex 83/100 selected items (records returned); gwas 100/100 selected items (records returned); hpa 76/100 selected items (records returned); humanbase 100/100 selected items (records returned); intact 79/100 selected items (records returned); mygene 100/100 selected items (records returned); omnipath 36/100 selected items (records returned); opentargets 90/100 selected items (records returned); pubmed 669 articles / initial full-cohort RAG 100 queries + 3 current-round queries; quickgo 80/100 selected items (records returned); reactome 100/100 selected items (records returned); uniprot 80/100 selected items (records returned)
Local databases: gutmgene 2/100 selected items (records returned); hmdb 25/100 selected items (records returned); string 78/100 selected items (records returned); trrust 17/100 selected items (records returned)
