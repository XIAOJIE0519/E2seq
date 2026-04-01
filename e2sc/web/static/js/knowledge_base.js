// 知识库管理 JavaScript

// 数据库详细信息
const DATABASE_INFO = {
    string: {
        name: 'STRING',
        description: '蛋白质-蛋白质相互作用网络数据库',
        records: '1,858,946',
        format: 'CSV',
        fields: [
            { name: 'source_gene', type: 'string', required: true, description: '源基因' },
            { name: 'target_gene', type: 'string', required: true, description: '目标基因' },
            { name: 'weight', type: 'float', required: true, description: '相互作用权重 (0-1)' }
        ],
        example: `source_gene,target_gene,weight
ARF5,CYTH2,0.471
AATF,BAX,0.823`
    },
    hmdb: {
        name: 'HMDB',
        description: '人类代谢组数据库 - 基因与代谢物关联',
        records: '1,045,796',
        format: 'CSV',
        fields: [
            { name: 'gene', type: 'string', required: true, description: '基因名称' },
            { name: 'metabolite', type: 'string', required: true, description: '代谢物ID (HMDB格式)' }
        ],
        example: `gene,metabolite
NT5E,HMDB0014944
ACHE,HMDB0000895`
    },
    trrust: {
        name: 'TRRUST',
        description: '转录因子调控关系数据库',
        records: '9,398',
        format: 'CSV',
        fields: [
            { name: 'tf', type: 'string', required: true, description: '转录因子' },
            { name: 'gene', type: 'string', required: true, description: '目标基因' },
            { name: 'function', type: 'string', required: true, description: '调控功能 (Activation/Repression)' },
            { name: 'pubmed', type: 'string', required: false, description: 'PubMed ID' }
        ],
        example: `tf,gene,function,pubmed
AATF,BAX,Repression,22909821
ABL1,TP53,Activation,15735682`
    },
    gutmgene: {
        name: 'GUTMGENE',
        description: '肠道微生物-基因关联数据库',
        records: '1,334',
        format: 'CSV',
        fields: [
            { name: 'pmid', type: 'string', required: true, description: 'PubMed ID' },
            { name: 'gut_microbiota', type: 'string', required: true, description: '肠道微生物名称' },
            { name: 'gene', type: 'string', required: true, description: '基因名称' },
            { name: 'alteration', type: 'string', required: false, description: '变化类型' },
            { name: 'condition', type: 'string', required: false, description: '条件/疾病' }
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

    document.getElementById('dbDetailTitle').textContent = info.name + ' - 数据库详情';
    
    const bodyHTML = `
        <div class="db-detail">
            <div class="detail-section">
                <h3>基本信息</h3>
                <p><strong>名称：</strong>${info.name}</p>
                <p><strong>描述：</strong>${info.description}</p>
                <p><strong>记录数：</strong>${info.records}</p>
                <p><strong>格式：</strong>${info.format}</p>
            </div>

            <div class="detail-section">
                <h3>必需字段</h3>
                <table class="fields-table">
                    <thead>
                        <tr>
                            <th>字段名</th>
                            <th>类型</th>
                            <th>必需</th>
                            <th>说明</th>
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
                <h3>数据示例</h3>
                <pre><code>${info.example}</code></pre>
            </div>

            <div class="detail-section">
                <h3>上传说明</h3>
                <ul>
                    <li>文件格式必须为 CSV</li>
                    <li>第一行必须包含字段名</li>
                    <li>所有必需字段必须存在</li>
                    <li>字段顺序可以任意</li>
                    <li>文件编码建议使用 UTF-8</li>
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
    if (!file.name.endsWith('.csv')) {
        alert('只支持 CSV 格式文件');
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
            throw new Error('上传失败');
        }

        const result = await response.json();
        alert('上传成功！');
        loadCustomDatabases();
    } catch (error) {
        console.error('上传失败:', error);
        alert('上传失败: ' + error.message);
    }
}

// 加载自定义数据库列表
async function loadCustomDatabases() {
    try {
        const response = await fetch('/api/knowledge-bases/custom');
        if (!response.ok) {
            // 如果API不存在，显示空状态
            document.getElementById('customDbList').innerHTML = '<p class="empty-message">暂无自定义数据库</p>';
            return;
        }

        const databases = await response.json();
        const listEl = document.getElementById('customDbList');
        
        if (databases.length === 0) {
            listEl.innerHTML = '<p class="empty-message">暂无自定义数据库</p>';
            return;
        }

        listEl.innerHTML = databases.map(db => `
            <div class="custom-db-item">
                <div class="db-info">
                    <h4>${db.name}</h4>
                    <p>${db.records} 条记录</p>
                </div>
                <div class="db-actions">
                    <button class="btn-delete" onclick="deleteDatabase('${db.id}')">删除</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('加载失败:', error);
        document.getElementById('customDbList').innerHTML = '<p class="empty-message">暂无自定义数据库</p>';
    }
}

// 删除自定义数据库
async function deleteDatabase(dbId) {
    if (!confirm('确定要删除这个数据库吗？')) return;

    try {
        const response = await fetch(`/api/knowledge-bases/${dbId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('删除失败');
        }

        alert('删除成功！');
        loadCustomDatabases();
    } catch (error) {
        console.error('删除失败:', error);
        alert('删除失败: ' + error.message);
    }
}

// 页面加载时加载自定义数据库
loadCustomDatabases();
