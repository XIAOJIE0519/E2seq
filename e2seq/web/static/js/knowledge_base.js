// 知识库管理 JavaScript

// 数据库详细信息
const DATABASE_INFO = {
    string: {
        name: 'STRING',
        description: '蛋白质-蛋白质相互作用网络数据库 / Protein–protein interaction network',
        records: '1,858,946',
        format: 'CSV',
        fields: [
            { name: 'source_gene', type: 'string', required: true, description: '源基因 / Source gene' },
            { name: 'target_gene', type: 'string', required: true, description: '目标基因 / Target gene' },
            { name: 'weight', type: 'float', required: true, description: '相互作用权重 (0-1) / Interaction weight (0–1)' }
        ],
        example: `source_gene,target_gene,weight
ARF5,CYTH2,0.471
AATF,BAX,0.823`
    },
    hmdb: {
        name: 'HMDB',
        description: '人类代谢组数据库 - 基因与代谢物关联 / Human metabolome; gene–metabolite associations',
        records: '1,045,796',
        format: 'CSV',
        fields: [
            { name: 'gene', type: 'string', required: true, description: '基因名称 / Gene name' },
            { name: 'metabolite', type: 'string', required: true, description: '代谢物 ID (HMDB格式) / Metabolite ID (HMDB format)' }
        ],
        example: `gene,metabolite
NT5E,HMDB0014944
ACHE,HMDB0000895`
    },
    trrust: {
        name: 'TRRUST',
        description: '转录因子调控关系数据库 / Transcription-factor regulation',
        records: '9,398',
        format: 'CSV',
        fields: [
            { name: 'tf', type: 'string', required: true, description: '转录因子 / Transcription factor' },
            { name: 'gene', type: 'string', required: true, description: '目标基因 / Target gene' },
            { name: 'function', type: 'string', required: true, description: '调控功能 (Activation/Repression)' },
            { name: 'pubmed', type: 'string', required: false, description: 'PubMed ID' }
        ],
        example: `tf,gene,function,pubmed
AATF,BAX,Repression,22909821
ABL1,TP53,Activation,15735682`
    },
    gutmgene: {
        name: 'GUTMGENE',
        description: '肠道微生物-基因关联数据库 / Gut microbiota–gene associations',
        records: '1,334',
        format: 'CSV',
        fields: [
            { name: 'pmid', type: 'string', required: true, description: 'PubMed ID' },
            { name: 'gut_microbiota', type: 'string', required: true, description: '肠道微生物名称 / Gut-microbiota name' },
            { name: 'gene', type: 'string', required: true, description: '基因名称 / Gene name' },
            { name: 'alteration', type: 'string', required: false, description: '变化类型 / Change type' },
            { name: 'condition', type: 'string', required: false, description: '条件/疾病 / Condition or disease' }
        ],
        example: `pmid,gut_microbiota,gene,alteration,condition
12345678,Lactobacillus,IL6,Increased,IBD
23456789,Bacteroides,TNF,Decreased,Healthy`
    }
};

// 查看数据库详情
function viewDatabase(dbName) {
    const info = DATABASE_INFO[dbName];
    if (!info) return;

    document.getElementById('dbDetailTitle').textContent = info.name + ' - 数据库详情 / Database details';

    const bodyHTML = `
        <div class="db-detail">
            <div class="detail-section">
                <h3>基本信息 / Basic information</h3>
                <p><strong>名称 / Name：</strong>${info.name}</p>
                <p><strong>描述 / Description：</strong>${info.description}</p>
                <p><strong>记录数 / Records：</strong>${info.records}</p>
                <p><strong>格式 / Format：</strong>${info.format}</p>
            </div>

            <div class="detail-section">
                <h3>字段 / Fields</h3>
                <table class="fields-table">
                    <thead>
                        <tr>
                            <th>字段名 / Field</th>
                            <th>类型 / Type</th>
                            <th>必需 / Required</th>
                            <th>说明 / Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${info.fields.map(field => `
                            <tr>
                                <td><code>${field.name}</code></td>
                                <td>${field.type}</td>
                                <td>${field.required ? '✓' : '×'}</td>
                                <td>${field.description}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>

            <div class="detail-section">
                <h3>数据示例 / Example</h3>
                <pre><code>${info.example}</code></pre>
            </div>

            <div class="detail-section">
                <h3>上传说明 / Upload notes</h3>
                <ul>
                    <li>文件格式：CSV / TSV / TXT / File format: CSV / TSV / TXT</li>
                    <li>第一行必须包含字段名 / The first row must contain field names</li>
                    <li>所有必需字段必须存在 / All required fields must be present</li>
                    <li>字段顺序可以任意 / Field order is arbitrary</li>
                    <li>文件编码建议使用 UTF-8 / UTF-8 encoding is recommended</li>
                </ul>
            </div>
        </div>
    `;

    document.getElementById('dbDetailBody').innerHTML = bodyHTML;
    document.getElementById('dbDetailModal').classList.add('active');
}

// 关闭详情模态框
function closeDbDetail() {
    document.getElementById('dbDetailModal').classList.remove('active');
}

// 文件上传处理
document.addEventListener('DOMContentLoaded', () => {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');

    // 拖拽上传
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    // 文件选择上传
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
});

// 处理文件上传
async function handleFileUpload(file) {
    if (!/\.(csv|tsv|txt)$/i.test(file.name)) {
        alert('只支持 CSV、TSV 或 TXT 格式 / Only CSV, TSV, or TXT files are supported');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/knowledge-bases/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('上传失败 / Upload failed');
        }

        const result = await response.json();
        alert('上传成功 / Upload successful');
        loadCustomDatabases();
    } catch (error) {
        console.error('Upload failed / 上传失败:', error);
        alert('上传失败 / Upload failed: ' + error.message);
    }
}

// 加载自定义数据库列表
async function loadCustomDatabases() {
    try {
        const response = await fetch('/api/knowledge-bases/custom');
        if (!response.ok) {
            // 如果API不存在，显示空状态
            document.getElementById('customDbList').innerHTML = '<p class="empty-message">暂无自定义基因注释 / No custom gene annotations</p>';
            return;
        }

        const databases = await response.json();
        const listEl = document.getElementById('customDbList');

        if (databases.length === 0) {
            listEl.innerHTML = '<p class="empty-message">暂无自定义基因注释 / No custom gene annotations</p>';
            return;
        }

        listEl.innerHTML = databases.map(db => `
            <div class="custom-db-item">
                <div class="db-info">
                    <h4>${db.name}</h4>
                    <p>${db.records} 条记录 / records</p>
                </div>
                <div class="db-actions">
                    <button class="btn-delete" onclick="deleteDatabase('${db.id}')">删除 / Delete</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Load failed / 加载失败:', error);
        document.getElementById('customDbList').innerHTML = '<p class="empty-message">暂无自定义基因注释 / No custom gene annotations</p>';
    }
}

// 删除自定义数据库
async function deleteDatabase(dbId) {
    if (!confirm('确定要删除这个数据库吗？ / Delete this database?')) return;

    try {
        const response = await fetch(`/api/knowledge-bases/${dbId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('删除失败 / Delete failed');
        }

        alert('删除成功 / Delete successful');
        loadCustomDatabases();
    } catch (error) {
        console.error('Delete failed / 删除失败:', error);
        alert('删除失败 / Delete failed: ' + error.message);
    }
}

// 页面加载时加载自定义数据库
loadCustomDatabases();
