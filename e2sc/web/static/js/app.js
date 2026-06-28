// E2seq Web Application JavaScript

class E2seqApp {
    constructor() {
        this.currentChatId = this._genChatId();
        this.messages = [];
        this.isProcessing = false;
        this.isAborting = false;
        this.currentPage = 'chat';
        this.currentLanguage = localStorage.getItem('e2seq_language') || 'zh-CN';
        // Safe local reference to the global translation function.
        // Falls back to returning the key itself if window.t is not yet available.
        this.t = window.t || ((key) => key);
        this.builtinDatabases = [
            {
                name: 'STRING',
                records: '1,858,946',
                descriptionKey: 'db.string.desc',
                format: 'CSV',
                fields: ['source_gene', 'target_gene', 'weight'],
                example: 'ARF5,CYTH2,0.471'
            },
            {
                name: 'HMDB',
                records: '858,077',
                descriptionKey: 'db.hmdb.desc',
                format: 'CSV',
                fields: ['gene', 'metabolite'],
                example: 'NT5E,HMDB0014944'
            },
            {
                name: 'TRRUST',
                records: '9,398',
                descriptionKey: 'db.trrust.desc',
                format: 'CSV',
                fields: ['TF', 'gene', 'function', 'pubmed'],
                example: 'AATF,BAX,Repression,22909821'
            },
            {
                name: 'GUTMGENE',
                records: '1,334',
                descriptionKey: 'db.gutmgene.desc',
                format: 'CSV',
                fields: ['PMID', 'Gut Microbiota', 'Gene', 'Alteration', 'Condition'],
                example: '12345678,Lactobacillus,IL10,Increased,IBD'
            }
        ];
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.placeBottomNav();
        this.loadChatHistory();
        this.autoResizeTextarea();
        // Load builtin databases immediately; must happen before applyLanguage
        // so that dynamically inserted HTML has translations applied.
        this.loadBuiltinDatabases().catch(err => console.warn('loadBuiltinDatabases error:', err));
        this.applyLanguage();
        this.initTheme();
        // Load active model badge on startup
        fetch('/api/config').then(r => r.json()).then(d => {
            if (d.configured) this._updateModelBadge(d.provider, d.model);
        }).catch(() => {});
    }

    initTheme() {
        const saved = localStorage.getItem('e2seq_theme') || 'light';
        this.setTheme(saved);
        
        // Listen to theme radio buttons in settings
        document.querySelectorAll('input[name="theme"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.setTheme(e.target.value);
            });
            // Set initial checked state
            if (radio.value === saved) {
                radio.checked = true;
            }
        });
    }

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('e2seq_theme', theme);
        // Update radio buttons in settings
        document.querySelectorAll('input[name="theme"]').forEach(radio => {
            radio.checked = (radio.value === theme);
        });
    }


    setupEventListeners() {
        // 导航按钮
        document.getElementById('newChatBtn')?.addEventListener('click', () => { this.createNewChat(); this.navigateToChat(); });
        document.getElementById('clearHistoryBtn')?.addEventListener('click', () => this.clearAllHistory());
        document.getElementById('knowledgeBaseBtn')?.addEventListener('click', () => this.navigateToKnowledgeBase());
        document.getElementById('settingsBtn')?.addEventListener('click', () => this.navigateToSettings());
        document.getElementById('backFromKBBtn')?.addEventListener('click', () => this.navigateToChat());
        document.getElementById('backFromSettingsBtn')?.addEventListener('click', () => this.navigateToChat());

        // Charts panel toggle
        document.getElementById('chartsBtn')?.addEventListener('click', () => this.openChartsPanel());
        document.getElementById('closeChartsPanel')?.addEventListener('click', () => this.closeChartsPanel());

        // Chart type selection
        document.querySelectorAll('.chart-type-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.loadChart(e.target.dataset.type));
        });

        // Chart actions
        document.getElementById('downloadChartBtn')?.addEventListener('click', () => this.downloadChart());
        document.getElementById('fullscreenChartBtn')?.addEventListener('click', () => this.fullscreenChart());
        document.getElementById('refreshChartBtn')?.addEventListener('click', () => this.refreshChart());

        // Message input and send
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');

        messageInput?.addEventListener('input', (e) => {
            this.handleInputChange(e.target.value);
        });

        messageInput?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        sendBtn?.addEventListener('click', () => {
            if (this.isProcessing) {
                this.abortChat();
            } else {
                this.sendMessage();
            }
        });

        // 首页示例卡片仅做展示动画，不绑定点击行为

        // 附件按钮 — 打开文件选择器上传文件
        document.getElementById('attachBtn')?.addEventListener('click', () => {
            this.handleAttachment();
        });

        // Database management
        const _uploadDBBtn = document.getElementById('uploadDBBtn');
        console.log('[SETUP] uploadDBBtn:', _uploadDBBtn, 'binding:', !!_uploadDBBtn);
        _uploadDBBtn?.addEventListener('click', () => { console.log('[CLICK] uploadDBBtn'); this.uploadDatabase(); });

        const _closeDBDetail = document.getElementById('closeDBDetail');
        console.log('[SETUP] closeDBDetail:', _closeDBDetail, 'binding:', !!_closeDBDetail);
        _closeDBDetail?.addEventListener('click', () => { console.log('[CLICK] closeDBDetail'); this.closeDBDetail(); });

        // Settings save
        const _saveBtn = document.getElementById('saveSettingsBtn');
        console.log('[SETUP] saveSettingsBtn:', _saveBtn, 'binding:', !!_saveBtn);
        _saveBtn?.addEventListener('click', () => { console.log('[CLICK] saveSettingsBtn'); this.saveSettings(); });

        // Embedding 模型测试按钮
        const _testBtn = document.getElementById('testEmbedBtn');
        console.log('[SETUP] testEmbedBtn:', _testBtn, 'binding:', !!_testBtn);
        _testBtn?.addEventListener('click', () => { console.log('[CLICK] testEmbedBtn'); this.testEmbeddingModel(); });

        const _savePathBtn = document.getElementById('embedSavePathBtn');
        console.log('[SETUP] embedSavePathBtn:', _savePathBtn, 'binding:', !!_savePathBtn);
        _savePathBtn?.addEventListener('click', () => { console.log('[CLICK] embedSavePathBtn'); this.saveCurrentEmbedPath(); });

        const _addCustomBtn = document.getElementById('embedAddCustomBtn');
        console.log('[SETUP] embedAddCustomBtn:', _addCustomBtn, 'binding:', !!_addCustomBtn);
        _addCustomBtn?.addEventListener('click', () => { console.log('[CLICK] embedAddCustomBtn'); this.addCustomEmbeddingModel(); });

        // Language & theme
        const _langRadios = document.querySelectorAll('input[name="language"]');
        console.log('[SETUP] language radios:', _langRadios.length);
        _langRadios.forEach(r => r.addEventListener('change', (e) => { console.log('[CLICK] language change:', e.target.value); this.changeLanguage(e.target.value); }));

        const _themeRadios = document.querySelectorAll('input[name="theme"]');
        console.log('[SETUP] theme radios:', _themeRadios.length);
        _themeRadios.forEach(r => r.addEventListener('change', (e) => { console.log('[CLICK] theme change:', e.target.value); this.setTheme(e.target.value); }));

        // key 输入框失焦时自动拉取模型
        ['openai','anthropic','gemini','deepseek','siliconflow','glm','kimi'].forEach(provider => {
            const keyEl = document.getElementById(provider + 'Key');
            const btnEl = document.querySelector(`.btn-fetch-models[data-provider='${provider}']`);
            const clearBtnEl = document.querySelector(`.btn-clear-key[data-provider='${provider}']`);
            const selEl = document.getElementById(provider + 'Model');
            const statusEl = document.getElementById('status-' + provider);
            const PROVIDER_FIELDS = {
                openai: 'openai_key', anthropic: 'anthropic_key', gemini: 'gemini_key',
                deepseek: 'deepseek_key', siliconflow: 'siliconflow_key', glm: 'glm_key',
                kimi: 'kimi_key'
            };
            const PROVIDER_LABELS = {
                openai: 'OpenAI', anthropic: 'Anthropic', gemini: 'Gemini',
                deepseek: 'DeepSeek', siliconflow: '硅基流动', glm: 'GLM',
                kimi: 'Moonshot Kimi'
            };

            if (keyEl) {
                keyEl.addEventListener('blur', () => {
                    if (keyEl.value.trim()) this.fetchModels(provider);
                });
                keyEl.addEventListener('input', () => {
                    if (!keyEl.value.trim()) {
                        if (selEl) selEl.style.display = 'none';
                        if (statusEl) statusEl.innerHTML = '';
                    }
                });
            }

            if (btnEl) {
                btnEl.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.fetchModels(provider);
                });
            }

            // 清除按钮 — 清除 API key 并断开连接
            if (clearBtnEl) {
                clearBtnEl.addEventListener('click', async (e) => {
                    e.preventDefault();
                    const providerLabel = PROVIDER_LABELS[provider] || provider;
                    this.showConfirmModal(
                        `${window.t('confirm.clearKey', null, {provider: providerLabel}) || `确定要清除 ${providerLabel} 的 API Key 并断开连接吗？`}`,
                        async () => {
                            try {
                                const r = await fetch('/api/settings/clear', {
                                    method: 'POST',
                                    headers: {'Content-Type':'application/json'},
                                    body: JSON.stringify({provider})
                                });
                                const d = await r.json();
                                if (d.success) {
                                    if (keyEl) keyEl.value = '';
                                    if (selEl) { selEl.style.display = 'none'; selEl.innerHTML = ''; }
                                    if (statusEl) statusEl.innerHTML = '<span style="color:#9aa0ac;font-size:.8rem">' + d.message + '</span>';
                                    this._updateModelBadge('ollama', 'llama3.2');
                                    this.showNotification(d.message, 'info');
                                } else {
                                    this.showNotification(d.detail || '清除失败', 'error');
                                }
                            } catch(err) {
                                this.showNotification('清除失败: ' + err.message, 'error');
                            }
                        },
                        window.t('confirm.clearKeyTitle') || '清除 API Key',
                        window.t('confirm.clear') || '确认清除',
                        window.t('confirm.cancel') || '取消',
                        true
                    );
                });
            }

            // 模型下拉框切换 — 自动切换到新模型（无需保存 API key）
            if (selEl) {
                selEl.addEventListener('change', async () => {
                    const selectedModel = selEl.value;
                    if (!selectedModel) return;
                    // 获取当前已配置的 provider 和 decrypted key（从 status badge 推断，或用已配置的）
                    // 显示连接中状态
                    const testingOverlay = this.showConnectionStatus('testing', '');
                    try {
                        const r = await fetch('/api/settings/switch-model', {
                            method: 'POST',
                            headers: {'Content-Type':'application/json'},
                            body: JSON.stringify({
                                provider,
                                model: selectedModel,
                                key_field: PROVIDER_FIELDS[provider]
                            })
                        });
                        testingOverlay.remove();
                        const d = await r.json();
                        if (d.success) {
                            if (d.connection_test) {
                                this.showConnectionStatus(d.connection_test.success ? 'success' : 'error', 
                                    d.connection_test.message || (d.connection_test.success ? '连接成功' : '连接失败'));
                            }
                            if (statusEl) statusEl.innerHTML = '<span style="color:#34d399;font-size:.8rem">✓ 已切换至 ' + selectedModel + '</span>';
                            this._updateModelBadge(provider, selectedModel);
                        } else {
                            this.showConnectionStatus('error', d.detail || '切换失败');
                            if (statusEl) statusEl.innerHTML = '<span style="color:#ef4444;font-size:.8rem">' + (d.detail||'切换失败') + '</span>';
                        }
                    } catch(err) {
                        testingOverlay.remove();
                        this.showConnectionStatus('error', err.message || '切换失败');
                    }
                });
            }
        });

        // Language switching
        document.querySelectorAll('input[name="language"]').forEach(radio => {
            radio.addEventListener('change', (e) => this.changeLanguage(e.target.value));
        });
    }

    placeBottomNav() {
        const sidebar = document.querySelector('.sidebar');
        const nav = document.querySelector('.sidebar-nav');
        const kbBtn = document.getElementById('knowledgeBaseBtn');
        const settingsBtn = document.getElementById('settingsBtn');
        if (!sidebar || !nav || !kbBtn || !settingsBtn) return;

        let footer = sidebar.querySelector('.sidebar-footer');
        if (!footer) {
            footer = document.createElement('div');
            footer.className = 'sidebar-footer';
            sidebar.appendChild(footer);
        }

        footer.appendChild(kbBtn);
        footer.appendChild(settingsBtn);
    }

    // Navigation
    navigateToChat() {
        this.switchPage('chat');
        // KB build polling removed — agentic RAG builds on demand per question
    }

    _setInputLocked(locked, placeholder) {
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        if (messageInput) {
            messageInput.disabled = locked;
            if (placeholder) messageInput.placeholder = placeholder;
            else messageInput.placeholder = this.t('chat.placeholder', this.currentLanguage);
        }
        if (sendBtn) sendBtn.disabled = locked;
    }

    navigateToKnowledgeBase() {
        this.switchPage('knowledgeBase');
        this.loadBuiltinDatabases();
        this.loadCustomDatabases();
    }

    navigateToSettings() {
        this.switchPage('settings');
        this.loadSettings();
    }

    switchPage(pageName) {
        const pages = {
            'chat': document.getElementById('chatPage'),
            'knowledgeBase': document.getElementById('knowledgeBasePage'),
            'settings': document.getElementById('settingsPage')
        };

        Object.values(pages).forEach(page => page?.classList.add('hidden'));
        pages[pageName]?.classList.remove('hidden');
        this.currentPage = pageName;
    }

    // Database listing
    async loadBuiltinDatabases() {
        const grid = document.getElementById('builtinDBGrid');
        if (!grid) return;

        // Fetch actual database status from backend
        let dbStatus = {};
        try {
            const resp = await fetch('/api/db/status');
            if (resp.ok) {
                dbStatus = await resp.json();
            }
        } catch (e) {
            console.warn('Failed to fetch db status:', e);
        }

        grid.innerHTML = this.builtinDatabases.map(db => {
            const status = dbStatus[db.name.toLowerCase()];
            const isLoaded = status && status.status === 'ok';
            const statusClass = isLoaded ? 'db-status' : 'db-status db-status-inactive';
            const statusText = isLoaded ? this.t('kb.status') : this.t('kb.statusNotLoaded');
            return `
            <div class="db-card" data-db="${db.name}">
                <div class="db-card-header">
                    <h3>${db.name}</h3>
                    <span class="${statusClass}">${statusText}</span>
                </div>
                <div class="db-card-body">
                    <p class="db-description">${this.t(db.descriptionKey)}</p>
                    <div class="db-stats">
                        <span class="stat-item">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                                <circle cx="12" cy="7" r="4"></circle>
                            </svg>
                            ${db.records} ${this.t('kb.records')}
                        </span>
                        <span class="stat-item">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                                <polyline points="14 2 14 8 20 8"></polyline>
                            </svg>
                            ${db.format}
                        </span>
                    </div>
                </div>
                <div class="db-card-footer">
                    <button class="btn-text" onclick="window.e2seqApp.showDBDetail('${db.name}')">${this.t('kb.viewDetail')}</button>
                </div>
            </div>
        `}).join('');
    }

    showDBDetail(dbName) {
        const db = this.builtinDatabases.find(d => d.name === dbName);
        if (!db) return;

        const modal = document.getElementById('dbDetailModal');
        const title = document.getElementById('dbDetailTitle');
        const body = document.getElementById('dbDetailBody');

        title.textContent = `${db.name} - ${this.t('dbDetail.title')}`;
        body.innerHTML = `
            <div class="db-detail">
                <div class="detail-section">
                    <h4>${this.t('dbDetail.basicInfo')}</h4>
                    <table class="detail-table">
                        <tr><td>${this.t('dbDetail.name')}</td><td>${db.name}</td></tr>
                        <tr><td>${this.t('dbDetail.records')}</td><td>${db.records}</td></tr>
                        <tr><td>${this.t('dbDetail.format')}</td><td>${db.format}</td></tr>
                        <tr><td>${this.t('dbDetail.description')}</td><td>${this.t(db.descriptionKey)}</td></tr>
                    </table>
                </div>
                <div class="detail-section">
                    <h4>${this.t('dbDetail.fields')}</h4>
                    <ul class="field-list">
                        ${db.fields.map(field => `<li><code>${field}</code></li>`).join('')}
                    </ul>
                </div>
                <div class="detail-section">
                    <h4>${this.t('dbDetail.example')}</h4>
                    <pre class="code-block">${db.example}</pre>
                </div>
            </div>
        `;

        modal.classList.add('active');
    }

    closeDBDetail() {
        document.getElementById('dbDetailModal')?.classList.remove('active');
    }

    async uploadDatabase() {
        // Show upload instructions modal
        this.showUploadInstructions();
    }

    showUploadInstructions() {
        const modal = document.getElementById('uploadInstructionsModal');
        if (!modal) {
            const modalHTML = `
                <div class="modal" id="uploadInstructionsModal">
                    <div class="modal-content" style="max-width: 700px;">
                        <div class="modal-header">
                            <h2 data-i18n="kb.uploadInstructions">上传自定义数据库</h2>
                            <button class="modal-close" onclick="window.e2seqApp.closeUploadInstructions()">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <line x1="18" y1="6" x2="6" y2="18"></line>
                                    <line x1="6" y1="6" x2="18" y2="18"></line>
                                </svg>
                            </button>
                        </div>
                        <div class="modal-body">
                            <div class="upload-instructions">
                                <div class="instruction-section">
                                    <h3 data-i18n="kb.requiredFields">必需字段</h3>
                                    <p data-i18n="kb.csvFormatDesc">请上传 CSV 格式文件，文件第一行为表头</p>
                                    <ul class="field-requirements">
                                        <li>
                                            <code>source</code>
                                            <span class="field-desc">来源基因/节点</span>
                                            <span class="required-badge">必需</span>
                                        </li>
                                        <li>
                                            <code>target</code>
                                            <span class="field-desc">目标基因/节点</span>
                                            <span class="required-badge">必需</span>
                                        </li>
                                        <li>
                                            <code>relationship</code>
                                            <span class="field-desc">关系类型，如 interaction, regulation, binding</span>
                                            <span class="optional-badge">可选</span>
                                        </li>
                                        <li>
                                            <code>weight</code>
                                            <span class="field-desc">权重值（0-1之间）</span>
                                            <span class="optional-badge">可选</span>
                                        </li>
                                    </ul>
                                </div>

                                <div class="instruction-section">
                                    <h3>文件格式</h3>
                                    <ul class="format-list">
                                        <li>
                                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                                <polyline points="20 6 9 17 4 12"></polyline>
                                            </svg>
                                            <span>CSV、TSV、TXT 格式</span>
                                        </li>
                                        <li>
                                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                                <polyline points="20 6 9 17 4 12"></polyline>
                                            </svg>
                                            <span>UTF-8 编码</span>
                                        </li>
                                        <li>
                                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                                <polyline points="20 6 9 17 4 12"></polyline>
                                            </svg>
                                            <span>文件不超过 50MB</span>
                                        </li>
                                    </ul>
                                </div>

                                <div class="instruction-section">
                                    <h3 data-i18n="kb.formatExample">格式示例</h3>
                                    <pre class="code-block">source,target,relationship,weight
TP53,MDM2,regulation,0.95
BRCA1,BRCA2,interaction,0.87
EGFR,KRAS,binding,0.78</pre>
                                    <button class="btn-text download-template-btn" onclick="window.e2seqApp.downloadTemplate()">
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                                            <polyline points="7 10 12 15 17 10"></polyline>
                                            <line x1="12" y1="15" x2="12" y2="3"></line>
                                        </svg>
                                        <span data-i18n="kb.downloadTemplate">下载模板文件</span>
                                    </button>
                                </div>

                                <div class="instruction-section">
                                    <h3 data-i18n="kb.notes">注意事项</h3>
                                    <ul class="notes-list">
                                        <li>请使用 UTF-8 编码保存文件</li>
                                        <li>第一行必须为表头</li>
                                        <li>source 和 target 为必需列</li>
                                        <li>权重值建议在 0-1 之间</li>
                                    </ul>
                                </div>
                            </div>

                            <div class="upload-actions">
                                <button class="btn-secondary" onclick="window.e2seqApp.closeUploadInstructions()">
                                    <span data-i18n="kb.cancel">取消</span>
                                </button>
                                <button class="btn-primary" onclick="window.e2seqApp.selectFileToUpload()">
                                    <span data-i18n="kb.selectFile">选择文件</span>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHTML);
        }

        document.getElementById('uploadInstructionsModal').classList.add('active');
        this.applyLanguage();
    }

    closeUploadInstructions() {
        const modal = document.getElementById('uploadInstructionsModal');
        if (modal) {
            modal.classList.remove('active');
        }
    }

    downloadTemplate() {
        // Generate CSV template content
        const templateContent = `source,target,relationship,weight
TP53,MDM2,regulation,0.95
BRCA1,BRCA2,interaction,0.87
EGFR,KRAS,binding,0.78
MYC,MAX,binding,0.92
STAT3,IL6,regulation,0.88`;

        // Create download link via Blob
        const blob = new Blob([templateContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        
        link.setAttribute('href', url);
        link.setAttribute('download', 'database_template.csv');
        link.style.visibility = 'hidden';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        this.showNotification(this.t('notify.templateDownloaded'), 'success');
    }

    selectFileToUpload() {
        this.closeUploadInstructions();
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.csv,.tsv,.txt';
        input.onchange = async (e) => {
            const file = e.target.files[0];
            if (file) {
                // Validate file before upload
                const validation = await this.validateDBFile(file);
                if (validation.valid) {
                    await this.uploadDBFile(file);
                } else {
                    this.showNotification(validation.error, 'error');
                }
            }
        };
        input.click();
    }

    async validateDBFile(file) {
        // Check file size limit
        const maxSize = 50 * 1024 * 1024; // 50MB
        if (file.size > maxSize) {
            return {
                valid: false,
                error: this.t('error.fileTooLarge')
            };
        }

        // Check file extension
        const validExtensions = ['.csv', '.tsv', '.txt'];
        const fileName = file.name.toLowerCase();
        const hasValidExtension = validExtensions.some(ext => fileName.endsWith(ext));

        if (!hasValidExtension) {
            return {
                valid: false,
                error: this.t('error.invalidFileType')
            };
        }

        // Validate CSV content
        try {
            const text = await file.text();
            const lines = text.split('\n').filter(line => line.trim());

            if (lines.length < 2) {
                return {
                    valid: false,
                    error: this.t('error.emptyFile')
                };
            }

            // Check for required columns in header
            const header = lines[0].toLowerCase();
            const requiredFields = ['source', 'target'];
            const missingFields = requiredFields.filter(field => !header.includes(field));
            
            if (missingFields.length > 0) {
                return {
                    valid: false,
                    error: this.t('error.missingFields') + ': ' + missingFields.join(', ')
                };
            }

            return { valid: true };
        } catch (error) {
            return {
                valid: false,
                error: this.t('error.fileReadError')
            };
        }
    }

    async uploadDBFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/knowledge-bases/upload', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error(this.t('notify.dbUploadFailed'));
            }

            this.showNotification(this.t('notify.dbUploaded') + `: ${file.name}`, 'success');
            this.loadCustomDatabases();
        } catch (error) {
            console.error('DB upload error:', error);
            this.showNotification(this.t('notify.dbUploadFailed'), 'error');
        }
    }

    async loadCustomDatabases() {
        try {
            const response = await fetch('/api/knowledge-bases/custom');
            if (!response.ok) return;

            const databases = await response.json();
            const grid = document.getElementById('customDBGrid');

            if (!databases || databases.length === 0) {
                grid.innerHTML = `
                    <div class="empty-state">
                        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                            <line x1="3" y1="9" x2="21" y2="9"></line>
                            <line x1="9" y1="21" x2="9" y2="9"></line>
                        </svg>
                        <p>${this.t('kb.empty')}</p>
                        <small>${this.t('kb.emptyHint')}</small>
                    </div>
                `;
            } else {
                grid.innerHTML = databases.map(db => `
                    <div class="db-card" data-db-id="${db.id}">
                        <div class="db-card-header">
                            <h3>${db.name}</h3>
                            <span class="db-type-badge">自定义</span>
                        </div>
                        <div class="db-card-body">
                            <div class="db-stats">
                                <span class="stat-item">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                                        <circle cx="12" cy="7" r="4"></circle>
                                    </svg>
                                    ${db.records} ${this.t('kb.records')}
                                </span>
                            </div>
                        </div>
                        <div class="db-card-footer">
                            <button class="btn-text" onclick="window.e2seqApp.deleteDatabase('${db.id}')">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polyline points="3 6 5 6 21 6"></polyline>
                                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                </svg>
                                删除
                            </button>
                        </div>
                    </div>
                `).join('');
            }
        } catch (error) {
            console.error('Load databases error:', error);
        }
    }

    async deleteDatabase(dbName) {
        this.showConfirmModal(
            `${window.t('confirm.deleteDb', null, {name: dbName}) || `确定要删除数据库 "${dbName}" 吗？此操作不可撤销。`}`,
            async () => {
                try {
                    const response = await fetch(`/api/knowledge-bases/${dbName}`, {
                        method: 'DELETE',
                    });

                    if (!response.ok) {
                        throw new Error(this.t('notify.dbDeleteFailed'));
                    }

                    this.showNotification(this.t('notify.dbDeleted'), 'success');
                    this.loadCustomDatabases();
                } catch (error) {
                    console.error('Delete database error:', error);
                    this.showNotification(this.t('notify.dbDeleteFailed'), 'error');
                }
            },
            window.t('confirm.deleteDbTitle') || '删除数据库',
            window.t('confirm.delete') || '确认删除',
            window.t('confirm.cancel') || '取消',
            true
        );
    }

    // Charts panel
    openChartsPanel() {
        document.getElementById('chartsPanel')?.classList.add('active');
    }

    closeChartsPanel() {
        document.getElementById('chartsPanel')?.classList.remove('active');
    }

    async loadChart(type) {
        // Highlight selected chart type button
        document.querySelectorAll('.chart-type-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.type === type);
        });

        const container = document.getElementById('chartContainer');
        container.innerHTML = '<div class="loading-spinner"></div>';

        try {
            const response = await fetch(`/api/plots/${type}`);
            if (!response.ok) {
                throw new Error(this.t('error.loadFailed'));
            }

            const plotData = await response.json();

            // Handle empty data case
            if (plotData.data && plotData.data.length === 0 && plotData.layout.annotations) {
                // Show no data message
                container.innerHTML = `
                    <div class="chart-error">
                        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                            <polyline points="14 2 14 8 20 8"></polyline>
                            <line x1="16" y1="13" x2="8" y2="13"></line>
                            <line x1="16" y1="17" x2="8" y2="17"></line>
                        </svg>
                        <p>${this.t('charts.noData')}</p>
                        <small>${this.t('charts.noDataHint')}</small>
                    </div>
                `;
            } else {
                // Render chart with Plotly
                Plotly.newPlot('chartContainer', plotData.data, plotData.layout, {responsive: true});
            }
        } catch (error) {
            console.error('Load chart error:', error);
            container.innerHTML = `
                <div class="chart-error">
                    <p>${this.t('error.loadFailed')}</p>
                    <small>${error.message}</small>
                </div>
            `;
        }
    }

    downloadChart() {
        Plotly.downloadImage('chartContainer', {
            format: 'png',
            width: 1200,
            height: 800,
            filename: 'e2seq_chart'
        });
    }

    fullscreenChart() {
        const container = document.getElementById('chartContainer');
        if (container.requestFullscreen) {
            container.requestFullscreen();
        }
    }

    refreshChart() {
        const activeBtn = document.querySelector('.chart-type-btn.active');
        if (activeBtn) {
            this.loadChart(activeBtn.dataset.type);
        }
    }

    // Embedding model helper
    _getEmbeddingMetaById(modelId) {
        return (this._embeddingModels || []).find(m => m.id === modelId) || null;
    }

    async saveCurrentEmbedPath() {
        const sel = document.getElementById('embeddingModelSelect');
        const pathInput = document.getElementById('embedModelPathInput');
        const modelId = sel?.value;
        const path = (pathInput?.value || '').trim();
        if (!modelId) return;

        const cfgResp = await fetch('/api/embedding/config');
        const cfg = cfgResp.ok ? await cfgResp.json() : {};
        const modelPaths = { ...(cfg.model_paths || {}) };
        if (path) modelPaths[modelId] = path;
        else delete modelPaths[modelId];

        const saveResp = await fetch('/api/embedding/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model_name: cfg.model_name || modelId,
                model_dimension: cfg.model_dimension,
                normalize: cfg.normalize,
                local_only: cfg.local_only,
                model_paths: modelPaths,
                custom_models: cfg.custom_models || [],
            }),
        });
        const data = await saveResp.json();
        if (!saveResp.ok || !data.success) {
            this.showNotification(data.detail || data.message || '保存路径失败', 'error');
            return;
        }
        this.showNotification('模型路径已保存', 'success');
        await this.loadEmbeddingSettings();
    }

    async addCustomEmbeddingModel() {
        const id = (document.getElementById('embedCustomId')?.value || '').trim();
        const name = (document.getElementById('embedCustomName')?.value || '').trim();
        const path = (document.getElementById('embedCustomPath')?.value || '').trim();
        const dimRaw = (document.getElementById('embedCustomDim')?.value || '').trim();
        const size = (document.getElementById('embedCustomSize')?.value || '').trim();

        if (!id || !path) {
            this.showNotification('自定义模型需要填写模型ID和本地路径', 'error');
            return;
        }

        const cfgResp = await fetch('/api/embedding/config');
        const cfg = cfgResp.ok ? await cfgResp.json() : {};
        const customModels = [...(cfg.custom_models || [])].filter(m => (m.id || '') !== id);
        customModels.push({
            id,
            name: name || id,
            path,
            dimension: dimRaw ? parseInt(dimRaw, 10) : null,
            size: size || '未知',
            description: '用户自定义模型',
        });

        const modelPaths = { ...(cfg.model_paths || {}), [id]: path };

        const saveResp = await fetch('/api/embedding/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model_name: cfg.model_name || id,
                model_dimension: cfg.model_dimension,
                normalize: cfg.normalize,
                local_only: cfg.local_only,
                model_paths: modelPaths,
                custom_models: customModels,
            }),
        });
        const data = await saveResp.json();
        if (!saveResp.ok || !data.success) {
            this.showNotification(data.detail || data.message || '添加自定义模型失败', 'error');
            return;
        }

        this.showNotification('自定义模型已添加', 'success');
        await this.loadEmbeddingSettings();
        const sel = document.getElementById('embeddingModelSelect');
        if (sel) sel.value = id;
        this.updateEmbeddingInfo(this._embeddingModels || [], id);
    }

    async loadSettings() {
        try {
            const response = await fetch('/api/settings');
            if (!response.ok) return;
            const data = await response.json();
            const fields = [
                ['openaiKey', 'openai_key'],
                ['anthropicKey', 'anthropic_key'],
                ['geminiKey', 'gemini_key'],
                ['deepseekKey', 'deepseek_key'],
                ['siliconflowKey', 'siliconflow_key'],
                ['glmKey', 'glm_key'],
                ['kimiKey', 'kimi_key'],
            ];
            // 回填已保存的模型名称
            const modelFields = [
                ['openaiModel', 'openai_model'],
                ['anthropicModel', 'anthropic_model'],
                ['geminiModel', 'gemini_model'],
                ['deepseekModel', 'deepseek_model'],
                ['siliconflowModel', 'siliconflow_model'],
                ['glmModel', 'glm_model'],
                ['kimiModel', 'kimi_model'],
            ];
            modelFields.forEach(([elemId, dataKey]) => {
                const el = document.getElementById(elemId);
                if (el && data[dataKey]) el.placeholder = data[dataKey];
            });
            fields.forEach(([elemId, dataKey]) => {
                const el = document.getElementById(elemId);
                if (el && data[dataKey]) {
                    el.placeholder = data[dataKey];
                }
            });
            // 若已配置 provider，自动拉取对应模型列表
            if (data.provider && data.provider !== 'ollama') {
                const currentModel = data[data.provider + '_model'];
                const CURATED = {
                    openai: ['gpt-5.5','gpt-5.5-pro','gpt-5.1','gpt-5.2','gpt-5.3-chat-latest','gpt-4o'],
                    anthropic: ['claude-sonnet-4-6','claude-opus-4-7','claude-haiku-4-5'],
                    gemini: ['gemini-3.1-pro-preview','gemini-3-flash-preview','gemini-3.1-flash-lite-preview','gemini-2.5-pro','gemini-2.5-flash'],
                    deepseek: ['deepseek-v4-flash','deepseek-v4-pro'],
                    siliconflow: ['deepseek-ai/DeepSeek-V3','deepseek-ai/DeepSeek-R1','Qwen/Qwen2.5-72B-Instruct'],
                    glm: ['glm-5.1','glm-4-Plus','glm-4'],
                    kimi: ['kimi-k2.6','moonshot-v2.5-250415'],
                };
                // Show curated lists for ALL providers so user can switch immediately
                ['openai','anthropic','gemini','deepseek','siliconflow','glm','kimi'].forEach(p => {
                    const curated = CURATED[p] || [];
                    if (!curated.length) return;
                    const pModel = data[p + '_model'];
                    if (!pModel) return; // only show if key is configured
                    const pSel = document.getElementById(p + 'Model');
                    if (!pSel) return;
                    const opts = curated.includes(pModel)
                        ? curated
                        : [pModel, ...curated];
                    pSel.innerHTML = opts.map(m => `<option value="${m}"${m===pModel?' selected':''}>${m}${m===pModel?' (当前)':''}</option>`).join('');
                    pSel.style.display = 'block';
                    pSel.disabled = false;
                    const statusEl = document.getElementById('status-' + p);
                    if (statusEl) statusEl.innerHTML = '<span style="color:#8ab4f8;font-size:0.8rem">当前模型: ' + pModel + '</span>';
                });
            }
            // 加载 Embedding 模型配置
            this.loadEmbeddingSettings(data);
            // Update model badge in chat header
            this._updateModelBadge(data.provider, data.model);
        } catch (error) {
            console.error('Failed to load settings:', error);
        }
    }

    async loadEmbeddingSettings(settingsData) {
        try {
            const resp = await fetch('/api/embedding/config');
            const cfg = resp.ok ? await resp.json() : {};
            const currentModel = cfg.model_name || settingsData?.embedding_model || 'sentence-transformers/all-MiniLM-L6-v2';

            const modelsResp = await fetch('/api/embedding/models');
            const modelsData = modelsResp.ok ? await modelsResp.json() : { models: [] };
            this._embeddingModels = modelsData.models || [];

            const sel = document.getElementById('embeddingModelSelect');
            if (sel && this._embeddingModels.length) {
                sel.innerHTML = this._embeddingModels.map(m =>
                    `<option value="${m.id}"${m.id === currentModel ? ' selected' : ''}>${m.name}</option>`
                ).join('');

                sel.onchange = () => {
                    this.updateEmbeddingInfo(this._embeddingModels, sel.value);
                    this._embedSettingsChanged = true;
                };
                this.updateEmbeddingInfo(this._embeddingModels, currentModel);
            }

            const localOnlyEl = document.getElementById('embedLocalOnly');
            if (localOnlyEl && cfg.local_only !== undefined) {
                localOnlyEl.checked = cfg.local_only;
                localOnlyEl.onchange = () => { this._embedSettingsChanged = true; };
            }

            const pathInput = document.getElementById('embedModelPathInput');
            if (pathInput) {
                const activePath = (cfg.model_paths || {})[currentModel] || '';
                pathInput.value = activePath;
            }
        } catch (error) {
            console.error('Failed to load embedding settings:', error);
        }
    }

    updateEmbeddingInfo(models, selectedId) {
        const model = models.find(m => m.id === selectedId);
        if (!model) return;

        const nameEl = document.getElementById('embedModelName');
        const dimEl = document.getElementById('embedModelDim');
        const descEl = document.getElementById('embedModelDesc');
        const statusEl = document.getElementById('embedModelStatus');
        const warnEl = document.getElementById('embedRebuildWarning');
        const sizeEl = document.getElementById('embedModelSize');
        const pathEl = document.getElementById('embedModelPath');

        if (nameEl) nameEl.textContent = model.name || model.id;
        if (dimEl) dimEl.textContent = (model.dimension || '-') + ' ' + this.t('settings.dim');
        if (descEl) descEl.textContent = model.description || '';
        if (sizeEl) sizeEl.textContent = this.t('settings.modelSize') + ': ' + (model.size || '-');
        if (pathEl) {
            if (model.path) {
                pathEl.textContent = this.t('settings.modelPath') + ': ' + model.path;
            } else if (model.path_required) {
                pathEl.textContent = this.t('settings.modelPathNeeded');
            } else if (model.builtin) {
                pathEl.textContent = this.t('settings.builtinNoPath');
            } else {
                pathEl.textContent = this.t('settings.downloadHF');
            }
        }

        const hasLocal = !!(model.builtin || model.path);
        if (model.path_required && !model.path) {
            if (statusEl) { statusEl.textContent = this.t('settings.pathNeeded'); statusEl.className = 'embed-status error'; }
        } else if (hasLocal) {
            if (statusEl) { statusEl.textContent = this.t('settings.localAvailable') + ' ✓'; statusEl.className = 'embed-status ok'; }
        } else {
            if (statusEl) { statusEl.textContent = this.t('settings.needDownload'); statusEl.className = 'embed-status'; }
        }

        const pathInput = document.getElementById('embedModelPathInput');
        if (pathInput) pathInput.value = model.path || '';

        // 如果选择了默认模型，隐藏警告
        if (warnEl) {
            warnEl.style.display = model.default ? 'none' : 'flex';
        }
    }

    async saveEmbeddingSettings() {
        const sel = document.getElementById('embeddingModelSelect');
        const localOnlyEl = document.getElementById('embedLocalOnly');
        const pathInput = document.getElementById('embedModelPathInput');
        const modelId = sel?.value;
        if (!modelId) return { success: false };

        try {
            const cfgResp = await fetch('/api/embedding/config');
            const cfg = cfgResp.ok ? await cfgResp.json() : {};
            const modelPaths = { ...(cfg.model_paths || {}) };
            const p = (pathInput?.value || '').trim();
            if (p) modelPaths[modelId] = p;

            const resp = await fetch('/api/embedding/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model_name: modelId,
                    local_only: localOnlyEl?.checked || false,
                    model_paths: modelPaths,
                    custom_models: cfg.custom_models || [],
                }),
            });
            const data = await resp.json();
            return data;
        } catch (error) {
            console.error('Failed to save embedding config:', error);
            return { success: false, error: error.message };
        }
    }

    async testEmbeddingModel() {
        const sel = document.getElementById('embeddingModelSelect');
        const statusEl = document.getElementById('embedModelStatus');
        const modelId = sel?.value;
        const localPath = (document.getElementById('embedModelPathInput')?.value || '').trim();
        if (!modelId) return;

        if (statusEl) { statusEl.textContent = '测试中...'; statusEl.className = 'embed-status testing'; }

        try {
            const resp = await fetch('/api/embedding/test', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model_name: modelId, local_path: localPath }),
            });
            const data = await resp.json();

            if (data.success) {
                if (statusEl) { statusEl.textContent = '✓ ' + data.message + ' (' + data.time_ms + 'ms)'; statusEl.className = 'embed-status ok'; }
            } else {
                if (statusEl) { statusEl.textContent = '✗ ' + data.message; statusEl.className = 'embed-status error'; }
            }
        } catch (error) {
            if (statusEl) { statusEl.textContent = '测试失败: ' + error.message; statusEl.className = 'embed-status error'; }
        }
    }

    async fetchModels(provider) {
        const keyEl = document.getElementById(provider + 'Key');
        const sel   = document.getElementById(provider + 'Model');
        const statusEl = document.getElementById('status-' + provider);
        const btn = document.querySelector(`.btn-fetch-models[data-provider="${provider}"]`);
        if (!keyEl || !sel) return;
        const apiKey = keyEl.value.trim();
        if (!apiKey) {
            if (statusEl) statusEl.innerHTML = `<span style="color:#9aa0ac;font-size:.8rem">${window.t('settings.enterKeyFirst')}</span>`;
            return;
        }
        // Loading state
        if (btn) btn.classList.add('spinning');
        if (statusEl) statusEl.innerHTML = `<span style="color:#9aa0ac;font-size:.8rem">${window.t('settings.fetchingModels')}</span>`;
        const CURATED = {
            openai: ['gpt-5.5','gpt-5.5-pro','gpt-5.1','gpt-5.2','gpt-5.3-chat-latest','gpt-4o'],
            anthropic: ['claude-opus-4-8','claude-opus-4-7','claude-sonnet-4-6','claude-haiku-4-5'],
            gemini: ['gemini-3.1-pro-preview','gemini-3-flash-preview','gemini-3.1-flash-lite-preview','gemini-2.5-pro','gemini-2.5-flash'],
            deepseek: ['deepseek-v4-flash','deepseek-v4-pro'],
            siliconflow: ['deepseek-ai/DeepSeek-V3','deepseek-ai/DeepSeek-R1','Qwen/Qwen2.5-72B-Instruct'],
            glm: ['glm-5.2','glm-5.1','glm-4-Plus','glm-4'],
            kimi: ['kimi-k2.6','moonshot-v2.5-250415'],
        };
        const curated = CURATED[provider] || [];
        if (curated.length) {
            sel.innerHTML = curated.map((m,i) => `<option value="${m}"${i===0?' selected':''}>${m}</option>`).join('');
            sel.style.display = 'block';
        }
        try {
            const r = await fetch('/api/settings/models', {
                method: 'POST',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify({provider, api_key: apiKey})
            });
            const d = await r.json();
            if (!r.ok) {
                if (statusEl) statusEl.innerHTML = `<span style="color:#ef4444;font-size:.8rem">${d.detail||'获取失败'}</span>`;
                if (btn) btn.classList.remove('spinning');
                return;
            }
            const models = d.models || curated;
            if (models.length) {
                let final = curated.length ? [...new Set([...curated, ...models])] : models;
                sel.innerHTML = final.map((m,i) => `<option value="${m}"${i===0?' selected':''}>${m}</option>`).join('');
                sel.style.display = 'block';
            }
            if (statusEl) statusEl.innerHTML = `<span style="color:#34d399;font-size:.8rem">✓ ${window.t('settings.modelsReady', null, {count: models.length})}</span>`;
            if (btn) btn.classList.remove('spinning');
        } catch(e) {
            if (statusEl) statusEl.innerHTML = `<span style="color:#9aa0ac;font-size:.8rem">${window.t('settings.loadedDefault')}</span>`;
            if (btn) btn.classList.remove('spinning');
        }
    }

    /** Update the model indicator badge in the chat header. */
    _updateModelBadge(provider, model) {
        const badge = document.getElementById('activeModelBadge');
        if (!badge) return;
        if (provider && model) {
            const providerLabels = {
                openai: 'OpenAI', anthropic: 'Anthropic', gemini: 'Gemini',
                deepseek: 'DeepSeek', siliconflow: '硅基流动', glm: 'GLM', ollama: 'Ollama'
            };
            const pLabel = providerLabels[provider] || provider;
            badge.textContent = `${pLabel} · ${model}`;
            badge.style.display = 'inline-block';
        } else {
            badge.style.display = 'none';
        }
    }

    async saveSettings() {
        const openaiKey = document.getElementById('openaiKey')?.value.trim();
        const anthropicKey = document.getElementById('anthropicKey')?.value.trim();
        const geminiKey = document.getElementById('geminiKey')?.value.trim();
        const deepseekKey = document.getElementById('deepseekKey')?.value.trim();
        const siliconflowKey = document.getElementById('siliconflowKey')?.value.trim();
        const glmKey = document.getElementById('glmKey')?.value.trim();
        const kimiKey = document.getElementById('kimiKey')?.value.trim();
        // 从下拉菜单读取用户选择的模型（拉取列表后由用户选定）
        const openaiModel = document.getElementById('openaiModel')?.value || '';
        const anthropicModel = document.getElementById('anthropicModel')?.value || '';
        const geminiModel = document.getElementById('geminiModel')?.value || '';
        const deepseekModel = document.getElementById('deepseekModel')?.value || '';
        const siliconflowModel = document.getElementById('siliconflowModel')?.value || '';
        const glmModel = document.getElementById('glmModel')?.value || '';
        const kimiModel = document.getElementById('kimiModel')?.value || '';

        // 如果没有输入任何 API Key，只保存 Embedding 设置
        const hasAnyKey = openaiKey || anthropicKey || geminiKey || deepseekKey || siliconflowKey || glmKey || kimiKey;
        if (!hasAnyKey) {
            // 只保存 Embedding 配置
            await this.saveEmbeddingSettings();
            return;
        }

        const settings = {
            openai_key: openaiKey,
            anthropic_key: anthropicKey,
            gemini_key: geminiKey,
            deepseek_key: deepseekKey,
            siliconflow_key: siliconflowKey,
            glm_key: glmKey,
            kimi_key: kimiKey,
            openai_model: openaiModel,
            anthropic_model: anthropicModel,
            gemini_model: geminiModel,
            deepseek_model: deepseekModel,
            siliconflow_model: siliconflowModel,
            glm_model: glmModel,
            kimi_model: kimiModel,
        };

        try {
            // 先显示连接中弹窗
            this.showConnectionStatus('testing', '');

            const response = await fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings),
            });

            if (!response.ok) {
                const err = await response.json().catch(() => ({}));
                this.showConnectionStatus('error', err.detail || '保存失败');
                throw new Error(err.detail || '保存失败');
            }

            const result = await response.json();

            ['openaiKey', 'anthropicKey', 'geminiKey', 'deepseekKey', 'siliconflowKey'].forEach(id => {
                const el = document.getElementById(id);
                if (el) el.value = '';
            });

            // 同时保存 Embedding 设置
            await this.saveEmbeddingSettings();

            // Refresh badge immediately from save result
            if (result.provider && result.model) {
                this._updateModelBadge(result.provider, result.model);
            }
            await this.loadSettings();

            // 显示连接状态弹窗（使用后端返回的连接测试结果）
            const connTest = result.connection_test;
            if (connTest) {
                this.showConnectionStatus(connTest.success ? 'success' : 'error', connTest.message || (connTest.success ? '连接成功' : '连接失败'));
            }

        } catch (error) {
            console.error('Save settings failed:', error);
            this.showNotification(error.message || this.t('notify.saveFailed'), 'error');
        }
    }

    showConnectionStatus(type, message) {
        const existing = document.getElementById('conn-modal-overlay');
        if (existing) existing.remove();

        const overlay = document.createElement('div');
        overlay.id = 'conn-modal-overlay';
        overlay.style.cssText = 'position:fixed;inset:0;z-index:20000;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.55);backdrop-filter:blur(4px)';

        const card = document.createElement('div');
        card.style.cssText = 'background:var(--bg-secondary, #1a1f2e);border:1px solid var(--border-color, #2d3348);border-radius:16px;padding:40px 48px;display:flex;flex-direction:column;align-items:center;gap:20px;box-shadow:0 20px 60px rgba(0,0,0,0.6);min-width:280px;transform:translateY(0)';

        const labels = { testing: '连接中...', success: '连接成功', error: '连接失败' };
        const colors = { testing: '#3b82f6', success: '#10b981', error: '#ef4444' };

        if (type === 'testing') {
            card.innerHTML =
                '<div style="width:64px;height:64px;position:relative">' +
                '<svg viewBox="0 0 64 64" width="64" height="64" style="animation:spin 1s linear infinite;display:block">' +
                '<circle cx="32" cy="32" r="28" fill="none" stroke="#2d3348" stroke-width="5"/>' +
                '<circle cx="32" cy="32" r="28" fill="none" stroke="#3b82f6" stroke-width="5" stroke-dasharray="44 132" stroke-linecap="round"/>' +
                '</svg></div>' +
                '<p style="margin:0;font-size:1.1rem;font-weight:600;color:#e8eaed">连接中...</p>' +
                '<p style="margin:0;font-size:0.85rem;color:#8ab4f8">正在验证 API Key</p>';
        } else if (type === 'success') {
            card.innerHTML =
                '<div style="width:64px;height:64px;border-radius:50%;background:#10b981;display:flex;align-items:center;justify-content:center">' +
                '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>' +
                '</div>' +
                '<p style="margin:0;font-size:1.1rem;font-weight:600;color:#e8eaed">连接成功</p>' +
                '<p style="margin:0;font-size:0.82rem;color:#6ee7b7;text-align:center;max-width:240px;word-break:break-all">' + (message || '') + '</p>';
            setTimeout(function() { if (overlay.parentNode) overlay.remove(); }, 1500);
        } else {
            card.innerHTML =
                '<div style="width:64px;height:64px;border-radius:50%;background:#ef4444;display:flex;align-items:center;justify-content:center">' +
                '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>' +
                '</div>' +
                '<p style="margin:0;font-size:1.1rem;font-weight:600;color:#e8eaed">连接失败</p>' +
                '<p style="margin:0;font-size:0.82rem;color:#fca5a5;text-align:center;max-width:240px;word-break:break-all">' + (message || '') + '</p>' +
                '<button onclick="document.getElementById(\'conn-modal-overlay\').remove()" style="padding:8px 24px;border-radius:8px;border:1px solid #ef4444;background:transparent;color:#ef4444;cursor:pointer;font-size:0.875rem">\u5173\u95ed</button>';
        }

        overlay.appendChild(card);
        document.body.appendChild(overlay);
        return overlay;
    }

    async testConnectionWithFeedback() {
        const testingToast = this.showConnectionStatus('testing', '');
        try {
            const resp = await fetch('/api/settings/test-connection', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({}),
            });
            testingToast.remove();
            if (resp.ok) {
                const data = await resp.json();
                this.showConnectionStatus('success', data.message || '连接成功');
            } else {
                const err = await resp.json().catch(() => ({}));
                this.showConnectionStatus('error', err.detail || '连接失败');
            }
        } catch (e) {
            testingToast.remove();
            this.showConnectionStatus('error', e.message || '网络错误');
        }
    }

    // Language change handler
    changeLanguage(lang) {
        this.currentLanguage = lang;
        localStorage.setItem('e2seq_language', lang);
        this.applyLanguage();
        this.showNotification(this.t('notify.languageChanged'), 'success');
    }

    applyLanguage() {
        // 翻译所有 data-i18n 元素
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = this.t(key, this.currentLanguage);

            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                if (element.placeholder !== undefined) {
                    element.placeholder = translation;
                }
            } else if (element.tagName === 'OPTION') {
                element.textContent = translation;
            } else {
                if (element.children.length === 0) {
                    element.textContent = translation;
                } else {
                    const textNode = Array.from(element.childNodes).find(node => node.nodeType === Node.TEXT_NODE);
                    if (textNode) textNode.textContent = translation;
                    else element.textContent = translation;
                }
            }
        });
        // 翻译 data-i18n-placeholder
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            const key = el.getAttribute('data-i18n-placeholder');
            if (el.placeholder !== undefined) {
                el.placeholder = this.t(key, this.currentLanguage);
            }
        });
        // 翻译 data-i18n-title
        document.querySelectorAll('[data-i18n-title]').forEach(el => {
            const key = el.getAttribute('data-i18n-title');
            el.title = this.t(key, this.currentLanguage);
        });

        // 翻译所有 data-i18n-title 元素的 title 属性
        document.querySelectorAll('[data-i18n-title]').forEach(element => {
            const key = element.getAttribute('data-i18n-title');
            element.title = this.t(key, this.currentLanguage);
        });

        // 翻译所有 data-i18n-placeholder 元素的 placeholder 属性
        document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
            const key = element.getAttribute('data-i18n-placeholder');
            element.placeholder = this.t(key, this.currentLanguage);
        });

        // 翻译 chart type buttons（动态注入文本）
        const chartTypes = ['umap', 'violin', 'heatmap', 'volcano', 'bubble', 'network', 'chord'];
        document.querySelectorAll('.chart-type-btn').forEach((btn, index) => {
            if (index < chartTypes.length) {
                btn.textContent = this.t('charts.' + chartTypes[index], this.currentLanguage);
            }
        });

        // 翻译 chart action button titles
        const downloadBtn = document.getElementById('downloadChartBtn');
        if (downloadBtn) downloadBtn.title = this.t('charts.download', this.currentLanguage);
        const fullscreenBtn = document.getElementById('fullscreenChartBtn');
        if (fullscreenBtn) fullscreenBtn.title = this.t('charts.fullscreen', this.currentLanguage);
        const refreshBtn = document.getElementById('refreshChartBtn');
        if (refreshBtn) refreshBtn.title = this.t('charts.refresh', this.currentLanguage);

        // 翻译上传抽屉内容
        const uploadTitle = document.querySelector('#uploadDrawer h2');
        if (uploadTitle) uploadTitle.textContent = this.t('upload.title', this.currentLanguage);
        const scTitle = document.querySelector('#uploadSingleCell h3');
        if (scTitle) scTitle.textContent = this.t('upload.singlecellTitle', this.currentLanguage);
        const scFormats = document.querySelector('#uploadSingleCell p');
        if (scFormats) scFormats.textContent = this.t('upload.singlecellFormats', this.currentLanguage);
        const scDesc = document.querySelector('#uploadSingleCell small');
        if (scDesc) scDesc.textContent = this.t('upload.singlecellDesc', this.currentLanguage);
        const tblTitle = document.querySelector('#uploadTable h3');
        if (tblTitle) tblTitle.textContent = this.t('upload.tableTitle', this.currentLanguage);
        const tblFormats = document.querySelector('#uploadTable p');
        if (tblFormats) tblFormats.textContent = this.t('upload.tableFormats', this.currentLanguage);

        // 翻译数据集配置弹窗
        const datasetModalTitle = document.querySelector('#datasetConfigModal h2');
        if (datasetModalTitle) datasetModalTitle.textContent = this.t('dataset.configTitle', this.currentLanguage);
        const datasetModalCancel = document.getElementById('cfgCancelBtn');
        if (datasetModalCancel) datasetModalCancel.textContent = this.t('dataset.cancel', this.currentLanguage);
        const datasetModalConfirm = document.getElementById('cfgConfirmBtn');
        if (datasetModalConfirm) datasetModalConfirm.textContent = this.t('dataset.confirmAndAnalyze', this.currentLanguage);

        // Translate dataset config modal labels
        const cfgCelltypeLabel = document.getElementById('cfgCelltypeColLabel');
        if (cfgCelltypeLabel) cfgCelltypeLabel.textContent = this.t('dataset.celltypeCol', this.currentLanguage);
        const cfgGroupColLabel = document.getElementById('cfgGroupColLabel');
        if (cfgGroupColLabel) cfgGroupColLabel.textContent = this.t('dataset.groupCol', this.currentLanguage);
        const cfgApiLabel = document.getElementById('cfgApiLabel');
        if (cfgApiLabel) cfgApiLabel.textContent = this.t('dataset.apiData', this.currentLanguage);
        const cfgCelltypePlaceholder = document.getElementById('cfgCelltypeCol');
        if (cfgCelltypePlaceholder) cfgCelltypePlaceholder.placeholder = this.t('dataset.selectColumn', this.currentLanguage);
        const cfgGroupColPlaceholder = document.getElementById('cfgGroupCol');
        if (cfgGroupColPlaceholder) cfgGroupColPlaceholder.placeholder = this.t('dataset.optional', this.currentLanguage);

        // 翻译分析面板
        if (window.analysisPanel && typeof window.analysisPanel.applyI18n === 'function') {
            window.analysisPanel.applyI18n(this.currentLanguage);
        }

        // 更新 Embedding 信息面板
        const selEl = document.getElementById('embeddingModelSelect');
        if (selEl && this._embeddingModels) {
            this.updateEmbeddingInfo(this._embeddingModels, selEl.value);
        }

        // Translate suggestion chips
        const suggestions = [
            'suggestion.deg',
            'suggestion.enrichment',
            'suggestion.network',
            'suggestion.hub',
            'suggestion.umap',
            'suggestion.upload'
        ];

        document.querySelectorAll('.chip span').forEach((span, index) => {
            if (index < suggestions.length) {
                span.textContent = this.t(suggestions[index], this.currentLanguage);
            }
        });

        // Refresh current page content
        if (this.currentPage === 'knowledgeBase') {
            this.loadBuiltinDatabases();
            this.loadCustomDatabases();
        }

        // Translate chart type buttons
        const chartTypeKeys = ['umap', 'violin', 'heatmap', 'volcano', 'bubble', 'network', 'chord'];
        document.querySelectorAll('.chart-type-btn').forEach((btn, index) => {
            if (index < chartTypeKeys.length) {
                btn.textContent = this.t('charts.' + chartTypeKeys[index], this.currentLanguage);
            }
        });

        // Update language radio selection
        document.querySelectorAll('input[name="language"]').forEach(radio => {
            radio.checked = (radio.value === this.currentLanguage);
        });

        // Update page title
        document.title = this.t('chat.title', this.currentLanguage) + ' - Easy to Chat with Sequencing';
    }

    // Input change handler
    handleInputChange(value) {
        const sendBtn = document.getElementById('sendBtn');
        if (sendBtn) {
            sendBtn.disabled = !value.trim();
        }
    }

    autoResizeTextarea() {
        const messageInput = document.getElementById('messageInput');
        if (!messageInput) return;

        messageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 200) + 'px';
        });
    }

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput?.value.trim();

        if (!message || this.isProcessing) return;

        const greetingModule = document.getElementById('greetingModule');
        if (greetingModule) {
            greetingModule.style.display = 'none';
        }

        this.addMessage('user', message);
        messageInput.value = '';
        this.handleInputChange('');
        messageInput.style.height = 'auto';

        this.isProcessing = true;
        this.isAborting = false;
        this._setSendButtonAbort();

        // Add loading bubble with progress display
        const loadingId = this.addMessage('assistant', '', true);
        const sessionId = this.currentChatId || 'default';
        const streamUrl = '/api/chat/stream';

        // State for assembling the streamed response
        let streamedText = '';
        let streamedPlots = [];
        let streamedThinking = [];
        let streamedData = {};
        let aborted = false;
        let errored = false;

        // Start progress polling — reads the in-memory buffer updated by the
        // orchestrator's logger handler. This runs in parallel with the SSE
        // stream so the user sees progress even if LLM is still generating.
        let lastProgressCount = 0;
        const progressEl = document.getElementById(loadingId)?.querySelector('.progress-log');
        const pollProgress = async () => {
            try {
                const pr = await fetch(`/api/progress/${sessionId}`);
                if (pr.ok) {
                    const pd = await pr.json();
                    const msgs = pd.messages || [];
                    if (msgs.length > lastProgressCount) {
                        lastProgressCount = msgs.length;
                        const bubble = document.getElementById(loadingId);
                        if (bubble) {
                            const pl = bubble.querySelector('.progress-log');
                            if (pl) {
                                pl.innerHTML = msgs.map(m =>
                                    `<div class="progress-step">${m}</div>`
                                ).join('');
                                pl.scrollTop = pl.scrollHeight;
                            }
                        }
                    }
                }
            } catch (_) {}
        };
        const progressTimer = setInterval(pollProgress, 800);

        try {
            const response = await fetch(streamUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'text/event-stream',
                },
                body: JSON.stringify({
                    message: message,
                    chat_id: this.currentChatId,
                }),
            });

            if (!response.ok || !response.body) {
                let errMsg = this.t('error.chatFailed');
                try {
                    const errJson = JSON.parse(await response.text());
                    if (errJson && errJson.detail) errMsg = errJson.detail;
                } catch (_) {}
                throw new Error(errMsg);
            }

            // Parse the SSE stream. Each record is "event: <name>\ndata: <json>\n\n".
            // Server emits: text, thinking, plots, source_stats, aborted, error, done.
            const reader = response.body.getReader();
            const decoder = new TextDecoder('utf-8');
            let buf = '';
            while (true) {
                const { value, done: rdone } = await reader.read();
                if (rdone) break;
                buf += decoder.decode(value, { stream: true });
                let sep;
                while ((sep = buf.indexOf('\n\n')) !== -1) {
                    const record = buf.slice(0, sep);
                    buf = buf.slice(sep + 2);
                    let ev = '';
                    let dataStr = '';
                    for (const line of record.split(/\r?\n/)) {
                        if (!line || line.startsWith(':')) continue;
                        const colon = line.indexOf(':');
                        if (colon === -1) continue;
                        const field = line.slice(0, colon).trim();
                        let val = line.slice(colon + 1);
                        if (val.startsWith(' ')) val = val.slice(1);
                        if (field === 'event') ev = val;
                        else if (field === 'data') dataStr = dataStr ? dataStr + '\n' + val : val;
                    }
                    if (!ev || !dataStr) continue;
                    let payload;
                    try { payload = JSON.parse(dataStr); }
                    catch (_) { continue; }
                    console.log('[SSE]', ev, payload);
                    if (ev === 'text') {
                        streamedText += (payload.content || '');
                    } else if (ev === 'plot' || ev === 'plots') {
                        // server emits 'plots' (plural) with an array
                        if (Array.isArray(payload)) streamedPlots.push(...payload);
                        else streamedPlots.push(payload);
                    } else if (ev === 'thinking') {
                        streamedThinking.push(payload);
                        // Also push progress messages into the visible progress log
                        // so the user sees something happening even when /api/progress
                        // polling is unavailable.
                        if (payload && payload.step === 'progress' && payload.content) {
                            try {
                                const bubble = document.getElementById(loadingId);
                                if (bubble) {
                                    const pl = bubble.querySelector('.progress-log');
                                    if (pl) {
                                        const step = document.createElement('div');
                                        step.className = 'progress-step';
                                        step.textContent = payload.content;
                                        pl.appendChild(step);
                                        pl.scrollTop = pl.scrollHeight;
                                    }
                                }
                            } catch (_) {}
                        }
                    } else if (ev === 'data') {
                        streamedData = payload.content || streamedData;
                    } else if (ev === 'source_stats') {
                        streamedData = { ...(streamedData || {}), source_stats: payload };
                    } else if (ev === 'aborted') {
                        aborted = true;
                    } else if (ev === 'error') {
                        errored = true;
                        streamedText = (payload && payload.detail) || payload || 'LLM 调用失败';
                        console.error('[SSE] error event:', payload);
                    } else if (ev === 'done') {
                        // CRITICAL: in non-streaming LLM mode, the server emits the full
                        // response text ONLY in the 'done' event, not in incremental
                        // 'text' events. Always populate streamedText from done — even
                        // if we already got some text — so we have a single source of truth.
                        if (typeof payload.response === 'string') {
                            if (!streamedText || payload.response.length > streamedText.length) {
                                streamedText = payload.response;
                            }
                        }
                        if (Array.isArray(payload.plots) && payload.plots.length && !streamedPlots.length) {
                            streamedPlots = payload.plots;
                        }
                        if (payload.data) {
                            streamedData = { ...(streamedData || {}), ...payload.data };
                        }
                    }
                }
            }

            // Stop progress polling now that the SSE stream is done.
            clearInterval(progressTimer);

            if (aborted) {
                // User-triggered abort — show what was streamed so far, mark as aborted.
                this.removeMessage(loadingId);
                const abortText = streamedText
                    ? streamedText + '\n\n_[回复已被用户中止]_'
                    : '_[回复已被用户中止]_';
                this.addMessage('assistant', abortText);
                this.loadChatHistory();
                return;
            }

            if (errored) {
                throw new Error('LLM 调用失败，请查看控制台');
            }

            const resultText = streamedText;
            const plotsData = streamedPlots;
            const thinkingSteps = streamedThinking;
            const sourceStats = streamedData?.source_stats || null;

            // Remove loading bubble and create assistant message with full response
            this.removeMessage(loadingId);
            const finalText = resultText || '_(服务器未返回内容，请稍后重试或检查后端日志)_';
            const messageId = this.addMessage('assistant', finalText);
            const messageEl = document.getElementById(messageId);

            if (plotsData.length > 0) {
                this.displayPlots(plotsData);
            }

            if (sourceStats) {
                const msgContent = messageEl?.querySelector('.message-content');
                if (msgContent) {
                    this._renderSourceStats(msgContent, sourceStats);
                }
            }

            this.loadChatHistory();

        } catch (error) {
            clearInterval(progressTimer);
            console.error('sendMessage error:', error);
            this.removeMessage(loadingId);
            this.addMessage('assistant', this.t('error.chatFailed'));
        } finally {
            this.isProcessing = false;
            this.isAborting = false;
            this._setSendButtonNormal();
        }
    }

    _setSendButtonAbort() {
        const sendBtn = document.getElementById('sendBtn');
        const sendIcon = document.getElementById('sendIcon');
        const abortIcon = document.getElementById('abortIcon');
        if (sendBtn) {
            sendBtn.classList.add('aborting');
            sendBtn.disabled = false;
            sendBtn.title = '中止回复';
        }
        if (sendIcon) sendIcon.style.display = 'none';
        if (abortIcon) abortIcon.style.display = 'block';
    }

    _setSendButtonNormal() {
        const sendBtn = document.getElementById('sendBtn');
        const sendIcon = document.getElementById('sendIcon');
        const abortIcon = document.getElementById('abortIcon');
        if (sendBtn) {
            sendBtn.classList.remove('aborting');
            sendBtn.title = '';
        }
        if (sendIcon) sendIcon.style.display = 'block';
        if (abortIcon) abortIcon.style.display = 'none';
    }

    async abortChat() {
        if (!this.isProcessing || this.isAborting) return;
        this.isAborting = true;
        this._setSendButtonAbort();
        try {
            const resp = await fetch('/api/chat/abort', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({chat_id: this.currentChatId}),
            });
            const result = await resp.json();
            console.log('[Abort] Server response:', result);
        } catch (e) {
            console.error('[Abort] Failed to send abort request:', e);
        }
    }

    addMessage(role, content, isLoading = false) {
        const messagesArea = document.getElementById('messagesArea');
        const messageId = `msg-${Date.now()}-${Math.random()}`;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        messageDiv.id = messageId;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = role === 'user' ? 'U' : 'E';

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';

        if (isLoading) {
            messageContent.innerHTML = `
                <div class="thinking-indicator">思考中<span class="thinking-dots"></span></div>
                <div class="progress-header">
                    <span class="progress-stage">📊 准备中</span>
                    <div class="progress-bar-wrap"><div class="progress-bar-fill" id="progressBarFill"></div></div>
                    <span class="progress-pct" id="progressPct">0%</span>
                </div>
                <div class="progress-log" id="progressLog"></div>
            `;
        } else if (role === 'assistant' && typeof marked !== 'undefined') {
            // Render markdown with marked.js
            try {
                messageContent.innerHTML = marked.parse(content || '');
                messageContent.querySelectorAll('pre code').forEach(function(b) {
                    if (typeof hljs !== 'undefined') hljs.highlightElement(b);
                });
            } catch (e) {
                console.warn('Marked parse error:', e);
                messageContent.textContent = content;
            }
        } else {
            // Fallback: basic markdown rendering without marked.js
            if (role === 'assistant' && content) {
                messageContent.innerHTML = _renderMarkdownFallback(content);
            } else {
                messageContent.textContent = content;
            }
        }

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        messagesArea.appendChild(messageDiv);

        messagesArea.scrollTop = messagesArea.scrollHeight;
        this.messages.push({ id: messageId, role, content });

        return messageId;
    }

    removeMessage(messageId) {
        const message = document.getElementById(messageId);
        if (message) {
            message.remove();
        }
        this.messages = this.messages.filter(m => m.id !== messageId);
    }

    _renderSourceStats(msgContent, stats) {
        // Render data source statistics below the response content
        const container = document.createElement('div');
        container.className = 'source-stats';

        // Build subtitle label
        const header = document.createElement('div');
        header.className = 'source-stats-header';
        header.textContent = '📊 数据来源统计';
        container.appendChild(header);

        // Total genes queried
        const totalGenes = stats.total_genes || 0;
        const totalSection = document.createElement('div');
        totalSection.className = 'stats-section';
        totalSection.innerHTML = `<div class="stats-row"><span class="stats-label">查询基因数</span><span class="stats-value">${totalGenes}</span></div>`;
        container.appendChild(totalSection);

        // Articles
        const pmCount = Array.isArray(stats.pubmed) ? stats.pubmed.length : 0;
        const epmcCount = Array.isArray(stats.europepmc) ? stats.europepmc.length : 0;
        if (pmCount > 0 || epmcCount > 0) {
            const litSection = document.createElement('div');
            litSection.className = 'stats-section';
            let litHtml = '<div class="stats-row"><span class="stats-label">文献来源</span></div>';
            if (pmCount > 0) litHtml += `<div class="stats-row sub-row"><span class="stats-label-sub">PubMed</span><span class="stats-value">${pmCount} 篇</span></div>`;
            if (epmcCount > 0) litHtml += `<div class="stats-row sub-row"><span class="stats-label-sub">EuropePMC</span><span class="stats-value">${epmcCount} 篇</span></div>`;
            litSection.innerHTML = litHtml;
            container.appendChild(litSection);
        }

        // API sources
        const apiHits = this._collectSourceHits(stats, 'apis');
        if (apiHits.length > 0) {
            const apiSection = document.createElement('div');
            apiSection.className = 'stats-section';
            apiSection.innerHTML = '<div class="stats-row"><span class="stats-label">在线 API</span></div>';
            apiHits.forEach(item => {
                const row = document.createElement('div');
                row.className = 'stats-row sub-row';
                const pct = totalGenes > 0 ? Math.round((item.hits / totalGenes) * 100) : 0;
                row.innerHTML = `<span class="stats-label-sub">${item.name}</span><span class="stats-value">${item.hits} 基因 (${pct}%)</span>`;
                apiSection.appendChild(row);
            });
            container.appendChild(apiSection);
        }

        // Local DB sources
        const dbHits = this._collectSourceHits(stats, 'dbs');
        if (dbHits.length > 0) {
            const dbSection = document.createElement('div');
            dbSection.className = 'stats-section';
            dbSection.innerHTML = '<div class="stats-row"><span class="stats-label">本地数据库</span></div>';
            dbHits.forEach(item => {
                const row = document.createElement('div');
                row.className = 'stats-row sub-row';
                const pct = totalGenes > 0 ? Math.round((item.hits / totalGenes) * 100) : 0;
                row.innerHTML = `<span class="stats-label-sub">${item.name}</span><span class="stats-value">${item.hits} 基因 (${pct}%)</span>`;
                dbSection.appendChild(row);
            });
            container.appendChild(dbSection);
        }

        msgContent.appendChild(container);
    }

    _collectSourceHits(stats, category) {
        const result = [];
        const cat = stats[category];
        if (!cat) return result;
        for (const [name, info] of Object.entries(cat)) {
            const hits = info && info.hit_genes ? info.hit_genes.size || (Array.isArray(info.hit_genes) ? info.hit_genes.length : 0) : 0;
            if (hits > 0) {
                result.push({ name, hits });
            }
        }
        return result.sort((a, b) => b.hits - a.hits);
    }

    displayPlots(plots) {
        const messagesArea = document.getElementById('messagesArea');
        
        plots.forEach((plot, index) => {
            const plotDiv = document.createElement('div');
            plotDiv.className = 'message assistant';
            
            const avatar = document.createElement('div');
            avatar.className = 'message-avatar';
            avatar.textContent = 'E';
            
            const plotContent = document.createElement('div');
            plotContent.className = 'message-content';

            const containerId = 'plot-container-' + Date.now() + '-' + index;
            plotContent.innerHTML = '<div style="margin-top:8px"><p style="margin-bottom:6px;color:var(--text-secondary);font-size:0.875rem">' + (plot.title || '') + '</p><div id="' + containerId + '" style="width:100%;min-height:400px;border-radius:8px;overflow:hidden"></div></div>';
            
            plotDiv.appendChild(avatar);
            plotDiv.appendChild(plotContent);
            messagesArea.appendChild(plotDiv);

            try {
                const figData = JSON.parse(plot.figure);
                const layout = Object.assign({
                    paper_bgcolor: '#0a0e1a',
                    plot_bgcolor: '#131825',
                    font: { color: '#e8eaed' },
                    margin: { t: 40, r: 20, b: 40, l: 50 }
                }, figData.layout || {});
                Plotly.newPlot(containerId, figData.data || [], layout, { responsive: true });
            } catch (e) {
                const el = document.getElementById(containerId);
                if (el) el.innerHTML = '<p style="color:#ef4444;padding:12px">\u56fe\u8868\u6e32\u67d3\u5931\u8d25: ' + e.message + '</p>';
            }
        });

        messagesArea.scrollTop = messagesArea.scrollHeight;
    }

    _genChatId() {
        // Generate a RFC4122-compliant UUID v4 without external deps
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
            const r = Math.random() * 16 | 0;
            return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
        });
    }

    createNewChat() {
        this.currentChatId = this._genChatId();
        this.messages = [];

        // Reset KB poll state for new chat session
        if (this._kbPollTimer) {
            clearInterval(this._kbPollTimer);
            this._kbPollTimer = null;
        }
        this._setInputLocked(false, '');
        
        const messagesArea = document.getElementById('messagesArea');
        messagesArea.innerHTML = '';
        
        const greetingModule = document.getElementById('greetingModule');
        if (greetingModule) {
            greetingModule.style.display = 'block';
        }
    }

    async loadChatHistory() {
        try {
            const response = await fetch('/api/chats');
            if (!response.ok) return;

            const chats = await response.json();
            const chatList = document.getElementById('chatList');
            if (!chatList) return;
            chatList.innerHTML = '';

            if (chats.length === 0) {
                chatList.innerHTML = '<div class="empty-state-small">暂无历史记录</div>';
                return;
            }

            chats.forEach(chat => {
                const chatItem = document.createElement('div');
                chatItem.className = 'chat-item';
                chatItem.dataset.id = chat.id;
                chatItem.dataset.title = chat.title || '';
                // 格式化时间
                let timeStr = '';
                if (chat.updated_at) {
                    const d = new Date(chat.updated_at + 'Z');
                    timeStr = d.toLocaleString('zh-CN', {month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'});
                }
                chatItem.innerHTML =
                    '<div class="chat-item-body">' +
                    '<span class="chat-item-title">' + this._escapeHtml(chat.title || '新对话') + '</span>' +
                    '<span class="chat-item-time">' + timeStr + '</span>' +
                    '</div>' +
                    '<button class="chat-item-rename" title="重命名" data-chat-rename="' + chat.id + '">' +
                    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>' +
                    '</button>' +
                    '<button class="chat-item-del" title="删除" data-chat-del="' + chat.id + '">×</button>';
                chatItem.addEventListener('click', (e) => {
                    const delBtn = e.target.closest('[data-chat-del]');
                    const renameBtn = e.target.closest('[data-chat-rename]');
                    if (delBtn) { e.stopPropagation(); this.deleteChat(delBtn.dataset.chatDel); return; }
                    if (renameBtn) { e.stopPropagation(); this._showRenameInput(renameBtn.dataset.chatRename, chat.title); return; }
                    this.navigateToChat();
                    this.loadChat(chat.id);
                });
                // Right-click context menu for rename
                chatItem.addEventListener('contextmenu', (e) => {
                    e.preventDefault();
                    this._showChatContextMenu(e, chat.id, chat.title);
                });
                chatList.appendChild(chatItem);
            });
        } catch (error) {
            console.error('loadChatHistory error:', error);
        }
    }

    async loadChat(chatId) {
        try {
            const response = await fetch(`/api/chats/${chatId}`);
            if (!response.ok) return;

            const chat = await response.json();
            this.currentChatId = chatId;
            this.messages = chat.messages || [];

            // Sync title into sidebar dataset so rename reads the current title
            const sidebarItem = document.querySelector(`.chat-item[data-id="${chatId}"]`);
            if (sidebarItem) sidebarItem.dataset.title = chat.title || '新对话';

            const messagesArea = document.getElementById('messagesArea');
            if (messagesArea) messagesArea.innerHTML = '';

            const greetingModule = document.getElementById('greetingModule');
            if (greetingModule) greetingModule.style.display = 'none';

            (chat.messages || []).forEach(msg => {
                this.addMessage(msg.role, msg.content);
            });

            // 高亮当前选中的历史条目
            document.querySelectorAll('.chat-item').forEach(el => el.classList.remove('active'));
            const activeItem = document.querySelector(`.chat-item[data-id="${chatId}"]`);
            if (activeItem) activeItem.classList.add('active');
        } catch (error) {
            console.error('loadChat error:', error);
        }
    }

    async deleteChat(chatId) {
        this.showConfirmModal(
            window.t('chat.confirmDelete') || '确认删除这条历史记录？此操作不可撤销。',
            async () => {
                try {
                    await fetch(`/api/chats/${chatId}`, { method: 'DELETE' });
                    if (this.currentChatId === chatId) {
                        this.createNewChat();
                    }
                    this.loadChatHistory();
                } catch (e) {
                    console.error('deleteChat error:', e);
                }
            },
            window.t('chat.deleteTitle') || '删除历史记录',
            window.t('confirm.delete') || '确认删除',
            window.t('confirm.cancel') || '取消',
            true
        );
    }

    async clearAllHistory() {
        this.showConfirmModal(
            window.t('chat.confirmClearAll') || '确认清空所有历史对话？仅保留最近一条记录，此操作不可撤销。',
            async () => {
                try {
                    const r = await fetch('/api/chats', { method: 'DELETE' });
                    if (!r.ok) throw new Error('清空失败');
                    const data = await r.json();
                    const chatList = document.getElementById('chatList');
                    if (chatList) chatList.innerHTML = '<div class="empty-state-small">暂无历史记录</div>';
                    if (data.kept && data.kept !== this.currentChatId) {
                        await this.loadChat(data.kept);
                    } else if (!data.kept) {
                        this.createNewChat();
                    }
                    await this.loadChatHistory();
                    const deleted = data.deleted || 0;
                    const kept = data.kept ? 1 : 0;
                    this.showNotification(
                        deleted > 0
                            ? `已清空 ${deleted} 条历史记录${kept ? '，保留最近 1 条' : ''}`
                            : '历史记录已是最新，无需清空',
                        'success'
                    );
                } catch (e) {
                    console.error('clearAllHistory error:', e);
                    this.showNotification('清空历史失败: ' + e.message, 'error');
                }
            },
            window.t('chat.clearAllTitle') || '清空历史记录',
            window.t('confirm.clearAll') || '确认清空',
            window.t('confirm.cancel') || '取消',
            true
        );
    }

    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    _showChatContextMenu(e, chatId, currentTitle) {
        // Remove any existing menu
        const existing = document.getElementById('chat-context-menu');
        if (existing) existing.remove();

        const menu = document.createElement('div');
        menu.id = 'chat-context-menu';
        menu.className = 'chat-context-menu';

        // Rename button
        const renameBtn = document.createElement('div');
        renameBtn.className = 'context-menu-item';
        renameBtn.textContent = window.t('chat.contextRename') || '重命名';
        renameBtn.addEventListener('click', () => {
            this._showRenameInput(chatId, currentTitle);
            menu.remove();
        });

        // Delete button
        const deleteBtn = document.createElement('div');
        deleteBtn.className = 'context-menu-item context-menu-item-danger';
        deleteBtn.textContent = window.t('chat.contextDelete') || '删除';
        deleteBtn.addEventListener('click', () => {
            menu.remove();
            this.deleteChat(chatId);
        });

        menu.appendChild(renameBtn);
        menu.appendChild(deleteBtn);
        document.body.appendChild(menu);

        // Position near cursor, clamp to viewport
        const rect = menu.getBoundingClientRect();
        let x = e.clientX;
        let y = e.clientY;
        if (x + rect.width > window.innerWidth) x = window.innerWidth - rect.width - 4;
        if (y + rect.height > window.innerHeight) y = window.innerHeight - rect.height - 4;
        menu.style.left = x + 'px';
        menu.style.top = y + 'px';

        // Dismiss on outside click or Escape
        const dismiss = (ev) => {
            if (!menu.contains(ev.target)) {
                menu.remove();
                document.removeEventListener('click', dismiss);
                document.removeEventListener('keydown', onEsc);
            }
        };
        const onEsc = (ev) => {
            if (ev.key === 'Escape') { menu.remove(); document.removeEventListener('click', dismiss); }
        };
        setTimeout(() => {
            document.addEventListener('click', dismiss);
            document.addEventListener('keydown', onEsc);
        }, 10);
    }

    _showRenameInput(chatId, currentTitle) {
        // Remove any existing input
        const existing = document.querySelector('.chat-rename-input-wrapper');
        if (existing) existing.remove();

        const item = document.querySelector(`.chat-item[data-id="${chatId}"]`);
        if (!item) return;

        const wrapper = document.createElement('div');
        wrapper.className = 'chat-rename-input-wrapper';

        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'chat-rename-input';
        input.value = currentTitle || '';
        input.maxLength = 200;
        input.placeholder = '输入新标题...';

        // Confirm on Enter, cancel on Escape or blur
        input.addEventListener('keydown', (ev) => {
            if (ev.key === 'Enter') {
                ev.preventDefault();
                this._doRename(chatId, input.value.trim(), item);
            } else if (ev.key === 'Escape') {
                wrapper.remove();
            }
        });
        input.addEventListener('blur', () => {
            // Small delay to allow Enter key to fire first
            setTimeout(() => {
                if (document.contains(wrapper)) {
                    this._doRename(chatId, input.value.trim(), item);
                }
            }, 150);
        });

        wrapper.appendChild(input);
        item.querySelector('.chat-item-body').replaceWith(wrapper);
        input.focus();
        input.select();
    }

    async _doRename(chatId, newTitle, itemEl) {
        const wrapper = document.querySelector('.chat-rename-input-wrapper');
        if (wrapper) wrapper.remove();

        if (!newTitle || newTitle === (itemEl.dataset.title || '')) {
            // Restore the original body if no change
            this._restoreChatItemBody(itemEl, itemEl.dataset.title || '新对话');
            return;
        }

        try {
            const r = await fetch(`/api/chats/${chatId}`, {
                method: 'PATCH',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({title: newTitle})
            });
            if (!r.ok) throw new Error('Rename failed');
            itemEl.dataset.title = newTitle;
            this._restoreChatItemBody(itemEl, newTitle);
            this.showNotification('已重命名', 'success');
        } catch (e) {
            console.error('_doRename error:', e);
            this._restoreChatItemBody(itemEl, itemEl.dataset.title || '新对话');
            this.showNotification('重命名失败: ' + e.message, 'error');
        }
    }

    _restoreChatItemBody(itemEl, title) {
        // Rebuild the body HTML after rename input is removed
        const timeEl = itemEl.querySelector('.chat-item-time');
        const timeStr = timeEl ? timeEl.textContent : '';
        const body = document.createElement('div');
        body.className = 'chat-item-body';
        body.innerHTML =
            '<span class="chat-item-title">' + this._escapeHtml(title) + '</span>' +
            '<span class="chat-item-time">' + timeStr + '</span>';
        itemEl.insertBefore(body, itemEl.querySelector('.chat-item-del'));
    }

    handleAttachment(fileArg) {
        if (fileArg) {
            this.uploadFile(fileArg);
            return;
        }
        // 统一进入右侧分析面板（顶部切换单细胞/表格）
        if (window.analysisPanel && typeof window.analysisPanel.open === 'function') {
            window.analysisPanel.open();
            if (typeof window.analysisPanel.switchMode === 'function') {
                window.analysisPanel.switchMode('singlecell');
            }
            return;
        }
        // 兜底
        this.openUploadDrawer();
    }

    // 打开上传抽屉
    openUploadDrawer() {
        const drawer = document.getElementById('uploadDrawer');
        const overlay = document.getElementById('drawerOverlay');
        if (drawer) {
            drawer.classList.add('active');
            if (overlay) overlay.classList.add('active');
            document.getElementById('mainContent')?.classList.add('drawer-open');
        }
    }

    // 关闭上传抽屉
    closeUploadDrawer() {
        const drawer = document.getElementById('uploadDrawer');
        const overlay = document.getElementById('drawerOverlay');
        if (drawer) drawer.classList.remove('active');
        if (overlay) overlay.classList.remove('active');
        // Only remove drawer-open if no other drawer is active
        const anyDrawerActive = document.querySelector('.drawer.active');
        if (!anyDrawerActive) {
            document.getElementById('mainContent')?.classList.remove('drawer-open');
        }
    }

    // 打开表格配置抽屉
    openTableDrawer() {
        const drawer = document.getElementById('tableUploadDrawer');
        const overlay = document.getElementById('drawerOverlay');
        if (drawer) {
            drawer.classList.add('active');
            if (overlay) overlay.classList.add('active');
            document.getElementById('mainContent')?.classList.add('drawer-open');
        }
    }

    // 关闭表格配置抽屉
    closeTableDrawer() {
        const drawer = document.getElementById('tableUploadDrawer');
        if (drawer) drawer.classList.remove('active');
        // 关闭所有抽屉时也关闭遮罩
        const anyDrawerActive = document.querySelector('.drawer.active');
        if (!anyDrawerActive) {
            const overlay = document.getElementById('drawerOverlay');
            if (overlay) overlay.classList.remove('active');
            document.getElementById('mainContent')?.classList.remove('drawer-open');
        }
    }

    showUploadTypeModal() {
        const modal = document.getElementById('uploadTypeModal');
        if (modal) modal.classList.add('active');
    }

    hideUploadTypeModal() {
        const modal = document.getElementById('uploadTypeModal');
        if (modal) modal.classList.remove('active');
    }

    openFilePicker(type) {
        this.closeUploadDrawer();
        const input = document.createElement('input');
        input.type = 'file';
        if (type === 'singlecell') {
            input.accept = '.h5ad,.csv,.rds';
        } else {
            input.accept = '.csv,.tsv,.xlsx';
        }
        input.onchange = async (e) => {
            const file = e.target.files[0];
            if (file) {
                if (type === 'singlecell') {
                    await this.uploadFile(file);
                } else {
                    if (window.analysisPanel && typeof window.analysisPanel.open === 'function') {
                        window.analysisPanel.switchMode('table');
                        window.analysisPanel.open();
                        await window.analysisPanel.setTableFile(file);
                    } else {
                        await this.openTableConfig(file);
                    }
                }
            }
        };
        input.click();
    }

    async openTableConfig(file) {
        // 关闭上传抽屉，打开配置抽屉
        this.closeUploadDrawer();

        const drawer = document.getElementById('tableUploadDrawer');
        const fileNameEl = document.getElementById('tableFileName');
        const fileInfoEl = document.getElementById('tableFileInfo');
        const geneColEl = document.getElementById('tableGeneCol');
        const groupColEl = document.getElementById('tableGroupCol');
        const exprTypeEl = document.getElementById('tableExprType');
        const exprColEl = document.getElementById('tableExprCol');
        const sigColEl = document.getElementById('tableSigCol');
        const errorEl = document.getElementById('tableUploadError');

        // 显示抽屉
        fileNameEl.textContent = file.name;
        fileInfoEl.textContent = window.t('analysis.readingFile') || '正在读取...';
        errorEl.style.display = 'none';
        geneColEl.innerHTML = '<option value="">' + (window.t('analysis.readingFile') || '加载中...') + '</option>';
        groupColEl.innerHTML = '<option value="">— ' + (window.t('upload.notUse') || '不使用') + ' —</option>';
        exprColEl.innerHTML = '<option value="">— ' + (window.t('upload.selectCol') || '选择列') + ' —</option>';
        sigColEl.innerHTML = '<option value="">— ' + (window.t('upload.notUse') || '不使用') + ' —</option>';
        drawer.classList.add('active');
        document.getElementById('drawerOverlay')?.classList.add('active');
        document.getElementById('mainContent')?.classList.add('drawer-open');

        // 上传并获取列信息
        const formData = new FormData();
        formData.append('file', file);
        formData.append('session_id', this.currentChatId);

        try {
            const response = await fetch('/api/upload-csv', {
                method: 'POST',
                body: formData,
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || '上传失败');

            fileInfoEl.textContent = `${data.n_rows} 行 × ${data.columns.length} 列`;

            // 填充所有列选择
            const cols = data.columns || [];
            const allOptions = cols.map(c => `<option value="${c}">${c}</option>`).join('');

            geneColEl.innerHTML = '<option value="">— 选择列 —</option>' + allOptions;
            groupColEl.innerHTML = '<option value="">— ' + (window.t('upload.notUse') || '不使用') + ' —</option>' + allOptions;
            exprColEl.innerHTML = '<option value="">— 选择列 —</option>' + allOptions;
            sigColEl.innerHTML = '<option value="">— ' + (window.t('upload.notUse') || '不使用') + ' —</option>' + allOptions;

            // 自动检测列名
            const colLower = cols.map(c => c.toLowerCase());
            const geneIdx = colLower.findIndex(c => /gene|ensembl|symbol|name/i.test(c));
            const groupIdx = colLower.findIndex(c => /group|condition|treatment|class/i.test(c));
            const exprIdx = colLower.findIndex(c => /log2fc|logfc|mean.*exp|expression|fc$/i.test(c));
            const sigIdx = colLower.findIndex(c => /fdr|pvalue|pval|adj.*p|significance/i.test(c));

            if (geneIdx >= 0) geneColEl.value = cols[geneIdx];
            if (groupIdx >= 0) groupColEl.value = cols[groupIdx];
            if (exprIdx >= 0) {
                exprColEl.value = cols[exprIdx];
                // 根据列名自动选择表达类型
                const exprLower = cols[exprIdx].toLowerCase();
                if (/log2fc|logfc/i.test(exprLower)) exprTypeEl.value = exprLower.includes('log2') ? 'log2FC' : 'logFC';
                else if (/mean/i.test(exprLower)) exprTypeEl.value = 'mean_expr';
                else exprTypeEl.value = 'custom';
            }
            if (sigIdx >= 0) sigColEl.value = cols[sigIdx];

            // 监听表达类型变化
            exprTypeEl.onchange = () => {
                const typeGroup = document.getElementById('tableExprColGroup');
                typeGroup.style.display = exprTypeEl.value === 'custom' ? 'block' : 'none';
            };

            // 保存文件引用
            this._pendingTableFile = file;
        } catch (e) {
            errorEl.textContent = e.message;
            errorEl.style.display = 'block';
        }
    }

    async confirmTableUpload() {
        const file = this._pendingTableFile;
        const geneCol = document.getElementById('tableGeneCol')?.value;
        const groupCol = document.getElementById('tableGroupCol')?.value;
        const exprType = document.getElementById('tableExprType')?.value;
        const exprCol = document.getElementById('tableExprCol')?.value;
        const exprThresh = document.getElementById('tableExprThresh')?.value;
        const sigCol = document.getElementById('tableSigCol')?.value;
        const sigThresh = document.getElementById('tableSigThresh')?.value;
        const topGenes = 0; // 表格数据不限制基因数量
        const errorEl = document.getElementById('tableUploadError');

        // 收集启用的 API
        const enabledApis = [];
        ['apiUniprot','apiMygene','apiEnsembl','apiChembl','apiOpentargets',
         'apiClinvar','apiReactome','apiPubmed','apiQuickgo','apiEuropepmc',
         'apiGtex','apiGwas','apiBiogrid'].forEach(id => {
            const el = document.getElementById(id);
            if (el?.checked) enabledApis.push(id.replace('api', '').toLowerCase());
        });

        // 收集启用的数据库
        const enabledDbs = [];
        ['dbString','dbHmdb','dbTrrust','dbGutmgene'].forEach(id => {
            const el = document.getElementById(id);
            if (el?.checked) enabledDbs.push(id.replace('db', '').toLowerCase());
        });

        if (!file || !geneCol) {
            errorEl.textContent = '请选择基因列';
            errorEl.style.display = 'block';
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('session_id', this.currentChatId);
        formData.append('gene_col', geneCol);
        if (groupCol) formData.append('group_col', groupCol);
        formData.append('expr_type', exprType);
        if (exprCol && exprType === 'custom') formData.append('expr_col', exprCol);
        if (exprThresh) formData.append('expr_thresh', exprThresh);
        if (sigCol) formData.append('sig_col', sigCol);
        if (sigThresh) formData.append('sig_thresh', sigThresh);
        formData.append('n_top_genes', topGenes);
        formData.append('enabled_apis', JSON.stringify(enabledApis));
        formData.append('enabled_dbs', JSON.stringify(enabledDbs));

        try {
            const response = await fetch('/api/configure-csv', {
                method: 'POST',
                body: formData,
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || '配置失败');

            this.closeTableDrawer();
            this.showNotification(`表格数据上传成功：${data.n_genes} 个基因`, 'success');

            // 重置分析面板状态
            if (window.analysisPanel) {
                window.analysisPanel._colsLoaded = false;
                window.analysisPanel.checkDataStatus();
            }
        } catch (e) {
            errorEl.textContent = e.message;
            errorEl.style.display = 'block';
        }
    }

    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('session_id', this.currentChatId);

        try {
            this.showNotification('正在上传并解析数据集，请稍候...', 'info');
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const err = await response.json().catch(() => ({}));
                throw new Error(err.detail || this.t('notify.uploadFailed'));
            }

            const data = await response.json();
            // Do NOT overwrite currentChatId with the server's session_id.
            // The upload endpoint may return a generic session; the frontend
            // UUID must remain the authoritative chat identifier.
            this._pendingUploadData = data;
            // Instead of showing a config modal, refresh the analysis panel
            // and open it so the user can confirm settings there.
            if (window.analysisPanel && typeof window.analysisPanel.open === 'function') {
                window.analysisPanel._colsLoaded = false;
                await window.analysisPanel.checkDataStatus();
                window.analysisPanel.open();
            }
            this.showNotification(`数据上传成功：${data.cells} 细胞 × ${data.genes} 基因`, 'success');
            const greetingModule = document.getElementById('greetingModule');
            if (greetingModule) greetingModule.style.display = 'none';
        } catch (error) {
            console.error('uploadFile error:', error);
            this.showNotification(error.message || this.t('notify.uploadFailed'), 'error');
        }
    }

    showDatasetConfigDialog(data) {
        const modal = document.getElementById('datasetConfigModal');
        if (!modal) return;

        // Fill stats
        const cfgCells = document.getElementById('cfgCells');
        const cfgGenes = document.getElementById('cfgGenes');
        if (cfgCells) cfgCells.textContent = (data.cells || 0).toLocaleString();
        if (cfgGenes) cfgGenes.textContent = (data.genes || 0).toLocaleString();

        // Fill column selectors
        const cols = data.obs_columns || [];
        const ctSel = document.getElementById('cfgCelltypeCol');
        const grpSel = document.getElementById('cfgGroupCol');
        if (ctSel) {
            ctSel.innerHTML = cols.map(c =>
                `<option value="${c}"${c === data.celltype_col_guess ? ' selected' : ''}>${c}</option>`
            ).join('');
        }
        if (grpSel) {
            grpSel.innerHTML = '<option value="">— ' + (window.t('upload.notUse') || '不使用') + ' —</option>' +
                cols.map(c =>
                    `<option value="${c}"${c === data.group_col_guess ? ' selected' : ''}>${c}</option>`
                ).join('');
        }

        // Helper: fetch unique values for a given obs column
        const fetchColValues = async (col) => {
            if (!col) return [];
            if (!data.col_values) data.col_values = {};
            if (data.col_values[col]) return data.col_values[col];
            try {
                const r = await fetch(`/api/group-values?session_id=${this.currentChatId || 'default'}&col=${encodeURIComponent(col)}`);
                const d = await r.json();
                data.col_values[col] = d.values || [];
                return data.col_values[col];
            } catch { return []; }
        };

        // Build rename input rows for any column
        const buildLabelRows = (sectionId, rowsId, values) => {
            const section = document.getElementById(sectionId);
            const container = document.getElementById(rowsId);
            if (!section || !container) return;
            if (!values || !values.length) { section.style.display = 'none'; return; }
            section.style.display = 'block';
            container.innerHTML = values.map(v => `
                <div style="display:flex;align-items:center;gap:.6rem">
                    <span style="width:130px;font-size:.85rem;color:var(--text-secondary);flex-shrink:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${v}">${v}</span>
                    <span style="color:var(--text-tertiary);font-size:.85rem">→</span>
                    <input type="text" class="form-control cfg-label-input" data-orig="${v}"
                        value="${v}" placeholder="显示名称"
                        style="flex:1;height:30px;font-size:.85rem">
                </div>`).join('');
        };

        // Rebuild group label rows when group col changes
        const buildGroupLabelRows = async () => {
            const values = await fetchColValues(grpSel?.value || '');
            buildLabelRows('cfgGroupLabelSection', 'cfgGroupLabelRows', values);
        };

        // Rebuild celltype label rows when celltype col changes
        const buildCelltypeLabelRows = async () => {
            const values = await fetchColValues(ctSel?.value || '');
            buildLabelRows('cfgCelltypeLabelSection', 'cfgCelltypeLabelRows', values);
        };

        grpSel?.addEventListener('change', buildGroupLabelRows);
        ctSel?.addEventListener('change', buildCelltypeLabelRows);

        // Pre-populate for guessed columns
        buildGroupLabelRows();
        buildCelltypeLabelRows();

        // Error reset
        const cfgError = document.getElementById('cfgError');
        if (cfgError) { cfgError.style.display = 'none'; cfgError.textContent = ''; }

        // Show modal
        modal.style.display = 'flex';
        modal.classList.add('active');

        // Bind buttons (remove old listeners by cloning)
        const confirmBtn = document.getElementById('cfgConfirmBtn');
        const cancelBtn = document.getElementById('cfgCancelBtn');
        const newConfirm = confirmBtn.cloneNode(true);
        const newCancel = cancelBtn.cloneNode(true);
        confirmBtn.replaceWith(newConfirm);
        cancelBtn.replaceWith(newCancel);

        newCancel.addEventListener('click', () => {
            modal.style.display = 'none';
            modal.classList.remove('active');
        });

        newConfirm.addEventListener('click', async () => {
            const celltypeCol = document.getElementById('cfgCelltypeCol')?.value || '';
            const groupCol = document.getElementById('cfgGroupCol')?.value || '';
            const enabledApis = [...document.querySelectorAll('.cfg-api:checked')].map(el => el.value);
            const enabledDbs  = [...document.querySelectorAll('.cfg-db:checked')].map(el => el.value);

            // Collect celltype label mappings {orig: display}
            const celltypeLabels = {};
            document.querySelectorAll('#cfgCelltypeLabelRows .cfg-label-input').forEach(inp => {
                const orig = inp.dataset.orig || '';
                const display = inp.value.trim() || orig;
                if (orig) celltypeLabels[orig] = display;
            });

            // Collect group label mappings {orig: display}
            const groupLabels = {};
            document.querySelectorAll('#cfgGroupLabelRows .cfg-label-input').forEach(inp => {
                const orig = inp.dataset.orig || '';
                const display = inp.value.trim() || orig;
                if (orig) groupLabels[orig] = display;
            });

            newConfirm.disabled = true;
            newConfirm.textContent = '配置中...';

            try {
                const r = await fetch('/api/configure-dataset', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: this.currentChatId || 'default',
                        celltype_col: celltypeCol,
                        group_col: groupCol,
                        enabled_apis: enabledApis,
                        enabled_dbs: enabledDbs,
                        celltype_labels: celltypeLabels,
                        group_labels: groupLabels,
                    }),
                });
                if (!r.ok) {
                    const e = await r.json().catch(() => ({}));
                    throw new Error(e.detail || '配置失败');
                }
                modal.style.display = 'none';
                modal.classList.remove('active');

                this.showNotification(`数据集配置完成：${data.cells} 细胞 × ${data.genes} 基因`, 'success');

                const greetingModule = document.getElementById('greetingModule');
                if (greetingModule) greetingModule.style.display = 'none';

                const messageInput = document.getElementById('messageInput');
                if (messageInput) {
                    messageInput.value = '';
                    this.handleInputChange('');
                    messageInput.focus();
                }
            } catch (err) {
                const cfgError = document.getElementById('cfgError');
                if (cfgError) { cfgError.textContent = err.message; cfgError.style.display = 'block'; }
                newConfirm.disabled = false;
                newConfirm.textContent = '确认并开始分析';
            }
        });
    }

    showToolsMenu() {
        console.log('必填');
        // TODO: 必填
    }

    showConfirmModal(message, onConfirm, title = null, confirmText = null, cancelText = null, isDanger = true) {
        const modal = document.getElementById('confirmModal');
        const titleEl = document.getElementById('confirmModalTitle');
        const msgEl = document.getElementById('confirmModalMessage');
        const confirmBtn = document.getElementById('confirmModalConfirm');
        const cancelBtn = document.getElementById('confirmModalCancel');
        const closeBtn = document.getElementById('confirmModalClose');
        if (!modal) return;
        if (titleEl) titleEl.textContent = title || window.t('confirm.title') || '确认';
        if (msgEl) msgEl.textContent = message;
        if (confirmBtn) {
            confirmBtn.textContent = confirmText || window.t('confirm.delete') || '确认删除';
            confirmBtn.className = isDanger ? 'btn-danger' : 'btn-primary';
        }
        if (cancelBtn) cancelBtn.textContent = cancelText || window.t('confirm.cancel') || '取消';

        // Resolve/reject promise
        let resolved = false;
        const resolve = (val) => { if (!resolved) { resolved = true; modal.style.display = 'none'; if (val && onConfirm) onConfirm(); } };
        const cleanup = () => { modal.style.display = 'none'; };

        // Remove old listeners
        const newConfirmBtn = confirmBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
        const newCancelBtn = cancelBtn.cloneNode(true);
        cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);
        const newCloseBtn = closeBtn.cloneNode(true);
        closeBtn.parentNode.replaceChild(newCloseBtn, closeBtn);

        newConfirmBtn.addEventListener('click', () => resolve(true));
        newCancelBtn.addEventListener('click', () => resolve(false));
        newCloseBtn.addEventListener('click', () => resolve(false));

        modal.style.display = 'flex';
        // Center the modal
        modal.style.alignItems = 'center';
        modal.style.justifyContent = 'center';
        modal.style.zIndex = '10000';
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 16px 24px;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            z-index: 10000;
            animation: slideInRight 0.3s ease-out;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Inject dynamic styles for analysis panel
// ========== Analysis Panel Tab + CSV Logic ==========
// Module-level code (executed at load time, outside the class)
let _csvColumns = [];
    let _csvSessionId = '';

    // ---- Tab switching ----
    window.apSwitchTab = function(tab) {
        const h5adContent = document.getElementById('apContentH5ad');
        const csvContent  = document.getElementById('apContentCsv');
        const tabH5ad = document.getElementById('apTabH5ad');
        const tabCsv  = document.getElementById('apTabCsv');
        if (!h5adContent || !csvContent) return;
        if (tab === 'csv') {
            h5adContent.style.display = 'none';
            csvContent.style.display  = '';
            tabH5ad.style.color = '#9aa0ac'; tabH5ad.style.borderBottomColor = 'transparent';
            tabCsv.style.color  = '#34d399'; tabCsv.style.borderBottomColor  = '#34d399';
        } else {
            csvContent.style.display  = 'none';
            h5adContent.style.display = '';
            tabCsv.style.color  = '#9aa0ac'; tabCsv.style.borderBottomColor  = 'transparent';
            tabH5ad.style.color = '#8ab4f8'; tabH5ad.style.borderBottomColor = '#8ab4f8';
        }
    };

    // ---- CSV file upload ----
    async function apHandleCsvFile(file) {
        window.apHandleCsvFile = apHandleCsvFile; // expose globally
        const sid = window.e2seqApp?.currentChatId || 'default';
        _csvSessionId = sid;
        const formData = new FormData();
        formData.append('session_id', sid);
        formData.append('file', file);
        const errEl = document.getElementById('apCsvError');
        if (errEl) { errEl.style.display = 'none'; errEl.textContent = ''; }
        try {
            const r = await fetch('/api/upload-csv', { method: 'POST', body: formData });
            const d = await r.json();
            if (!r.ok) { if (errEl) { errEl.textContent = d.detail || '上传失败'; errEl.style.display = 'block'; } return; }
            _csvColumns = d.columns || [];
            const elFname = document.getElementById('apCsvFileName');
            if (elFname) elFname.textContent = d.filename || file.name;
            const elRows = document.getElementById('apCsvRowCount');
            if (elRows) elRows.textContent = d.n_rows;
            const elCols = document.getElementById('apCsvColCount');
            if (elCols) elCols.textContent = _csvColumns.length;
            const selIds = ['apCsvGroupCol','apCsvGeneCol','apCsvExprCol','apCsvSigCol'];
            selIds.forEach(id => {
                const sel = document.getElementById(id);
                if (!sel) return;
                const keepEmpty = id === 'apCsvSigCol';
                sel.innerHTML = keepEmpty ? '<option value="">-- ' + (window.t('upload.notUse') || '不使用') + ' --</option>' : '';
                _csvColumns.forEach(c => {
                    const opt = document.createElement('option');
                    opt.value = c; opt.textContent = c;
                    sel.appendChild(opt);
                });
            });
            const guess = (hints) => _csvColumns.find(c => hints.some(h => c.toLowerCase().includes(h))) || _csvColumns[0] || '';
            document.getElementById('apCsvGroupCol').value = guess(['group','condition','disease','phenotype']);
            document.getElementById('apCsvGeneCol').value  = guess(['name','gene','protein','symbol']);
            document.getElementById('apCsvExprCol').value  = guess(['log2fc','logfc','lfc','mean_expr','expr','fc']);
            const sigGuess = _csvColumns.find(c => ['fdr','adj','padj','qval','p.adj'].some(h => c.toLowerCase().includes(h))) || '';
            document.getElementById('apCsvSigCol').value = sigGuess;
            // Update data status info (keep step1 visible, just update text)
            const csvInfo = document.getElementById('apCsvDataInfo');
            if (csvInfo) csvInfo.innerHTML = `<span style="color:#34d399">&#x2713;</span> ${d.filename || file.name} &middot; ${d.n_rows} 行 &middot; ${_csvColumns.length} 列`;
            const csvClearBtn = document.getElementById('apCsvClearBtn');
            if (csvClearBtn) csvClearBtn.style.display = 'block';
            // Enable selects and confirm button now that data is uploaded
            ['apCsvGroupCol','apCsvGeneCol','apCsvExprCol','apCsvSigCol'].forEach(id => {
                const el = document.getElementById(id);
                if (el) el.disabled = false;
            });
            const confirmBtn = document.getElementById('apCsvConfirmBtn');
            if (confirmBtn) confirmBtn.disabled = false;
        } catch(e) {
            if (errEl) { errEl.textContent = '上传出错: ' + e.message; errEl.style.display = 'block'; }
        }
    }

    window.apCsvDrop = function(e) {
        e.preventDefault();
        const dropZone = document.getElementById('apCsvDropZone');
        if (dropZone) dropZone.style.borderColor = '#3d4460';
        const file = e.dataTransfer.files[0];
        if (file) apHandleCsvFile(file);
    };

    window.apCsvReset = function() {
        document.getElementById('apCsvFileInput').value = '';
        const csvInfo = document.getElementById('apCsvDataInfo');
        if (csvInfo) csvInfo.textContent = '未加载数据';
        const csvClearBtn = document.getElementById('apCsvClearBtn');
        if (csvClearBtn) csvClearBtn.style.display = 'none';
        // Reset selects to placeholder state
        const groupSel = document.getElementById('apCsvGroupCol');
        if (groupSel) { groupSel.innerHTML = '<option value="">— 上传文件后自动填充 —</option>'; groupSel.disabled = true; }
        const geneSel = document.getElementById('apCsvGeneCol');
        if (geneSel) { geneSel.innerHTML = '<option value="">name / gene_symbol</option>'; geneSel.disabled = true; }
        const exprSel = document.getElementById('apCsvExprCol');
        if (exprSel) { exprSel.innerHTML = '<option value="">log2FC / mean_expr</option>'; exprSel.disabled = true; }
        const sigSel = document.getElementById('apCsvSigCol');
        if (sigSel) { sigSel.innerHTML = '<option value="">-- ' + (window.t('upload.notUse') || '不使用') + ' --</option>'; sigSel.disabled = true; }
        const confirmBtn = document.getElementById('apCsvConfirmBtn');
        if (confirmBtn) confirmBtn.disabled = true;
        const errEl = document.getElementById('apCsvError');
        if (errEl) { errEl.style.display = 'none'; errEl.textContent = ''; }
    };

    window.apCsvConfirm = async function() {
        const btn = document.getElementById('apCsvConfirmBtn');
        const errEl = document.getElementById('apCsvError');
        if (errEl) errEl.style.display = 'none';
        btn.disabled = true;
        const origHTML = btn.innerHTML;
        btn.textContent = '配置中...';
        const exprTypeEl = document.getElementById('apCsvExprType');
        const exprType = exprTypeEl.value === 'custom'
            ? (document.getElementById('apCsvExprTypeCustom').value.trim() || 'value')
            : exprTypeEl.value;
        const exprThreshRaw = document.getElementById('apCsvExprThresh').value.trim();
        const sigThreshRaw  = document.getElementById('apCsvSigThresh').value.trim();
        const body = {
            session_id:   _csvSessionId,
            group_col:    document.getElementById('apCsvGroupCol').value,
            gene_col:     document.getElementById('apCsvGeneCol').value,
            expr_col:     document.getElementById('apCsvExprCol').value,
            expr_type:    exprType,
            expr_thresh:  exprThreshRaw ? parseFloat(exprThreshRaw) : null,
            sig_col:      document.getElementById('apCsvSigCol').value,
            sig_thresh:   sigThreshRaw ? parseFloat(sigThreshRaw) : 0.05,
            enabled_apis: Array.from(document.querySelectorAll('#apCsvApiChecks input:checked')).map(el => el.value).filter(v => ['uniprot','mygene','quickgo','ensembl','chembl','pubmed','europepmc','opentargets','clinvar','gtex','reactome','gwas','biogrid'].includes(v)),
            enabled_dbs:  Array.from(document.querySelectorAll('#apCsvApiChecks input:checked')).map(el => el.value).filter(v => ['string','hmdb','trrust','gutmgene'].includes(v)),
            n_top_genes:  30,
            dataset_description: (document.getElementById('apCsvDatasetDesc')?.value || '').trim(),
        };
        try {
            const r = await fetch('/api/configure-csv', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });
            const d = await r.json();
            if (!r.ok) {
                if (errEl) { errEl.textContent = d.detail || '配置失败'; errEl.style.display = 'block'; }
                btn.disabled = false; btn.innerHTML = origHTML; return;
            }
            const ap = window.analysisPanel;
            if (ap && typeof ap.close === 'function') ap.close();
            const grps = (d.groups || []).join(' / ');
            window.e2seqApp?.showNotification('CSV 配置完成：' + d.n_genes + ' 个基因，分组：' + grps, 'success');
            const gm = document.getElementById('greetingModule');
            if (gm) gm.style.display = 'none';
            window.e2seqApp?.navigateToChat?.();
            const mi = document.getElementById('messageInput');
            if (mi) { mi.value = ''; mi.focus(); }
        } catch(e) {
            if (errEl) { errEl.textContent = '请求失败: ' + e.message; errEl.style.display = 'block'; }
        } finally {
            btn.disabled = false; btn.innerHTML = origHTML;
        }
    };

    document.addEventListener('DOMContentLoaded', () => {
        document.getElementById('apCsvExprType')?.addEventListener('change', function() {
            const custom = document.getElementById('apCsvExprTypeCustom');
            if (custom) custom.style.display = this.value === 'custom' ? '' : 'none';
        });
        document.getElementById('apCsvFileInput')?.addEventListener('change', function() {
            if (this.files[0]) apHandleCsvFile(this.files[0]);
        });
    });

    window.apClearData = async function() {
        window.e2seqApp?.showConfirmModal(
            window.t('confirm.clearData') || '确认清空当前数据？清空后需要重新上传文件才能分析。',
            async () => {
                const sid = window.e2seqApp?.currentChatId || 'default';
                try {
                    const r = await fetch('/api/clear-data', {
                        method: 'POST',
                        headers: {'Content-Type':'application/json'},
                        body: JSON.stringify({session_id: sid})
                    });
                    if (r.ok) {
                        const result = await r.json();
                        logger.info('Clear result:', result);
                    }
                } catch(e) {
                    logger.error('Clear failed:', e);
                }
                // Reset CSV panel
                window.apCsvReset();
                // Reset h5ad panel status
                const info = document.getElementById('apDataInfo');
                if (info) info.textContent = '未加载数据';
                const clearBtn = document.getElementById('apClearDataBtn');
                if (clearBtn) clearBtn.style.display = 'none';
                // Reset h5ad selects to '不使用'
                const ctSel = document.getElementById('apCelltypeColSelect');
                if (ctSel) { ctSel.innerHTML = '<option value="">— ' + (window.t('upload.notUse') || '不使用') + ' —</option>'; }
                const grpSel = document.getElementById('apGroupColSelect');
                if (grpSel) { grpSel.innerHTML = '<option value="">— ' + (window.t('upload.notUse') || '不使用') + ' —</option>'; }
                const ctRows = document.getElementById('apCelltypeLabelRows');
                if (ctRows) ctRows.innerHTML = '';
                const grpRows = document.getElementById('apGroupLabelRows');
                if (grpRows) grpRows.innerHTML = '';
                // Clear localStorage labels
                try { localStorage.removeItem('e2seq_user_labels'); } catch(_) {}
                // Hide matrix preview
                const matSec = document.getElementById('apMatrixSection');
                if (matSec) matSec.style.display = 'none';
                // Disable run button
                const runBtn = document.getElementById('apRunBtn');
                if (runBtn) { runBtn.disabled = true; }
                // Show greeting module (clean slate)
                const greetingModule = document.getElementById('greetingModule');
                if (greetingModule) greetingModule.style.display = 'block';
                // Refresh the analysis panel status to sync with server
                if (window.analysisPanel) {
                    window.analysisPanel._colsLoaded = false;
                    window.analysisPanel.matrixData = null;
                    window.analysisPanel._userLabels = { celltype: {}, group: {} };
                    window.analysisPanel.checkDataStatus();
                }
                window.e2seqApp?.showNotification('数据已清空，请重新上传文件', 'info');
            },
            window.t('confirm.clearDataTitle') || '清空数据',
            window.t('confirm.clearData') || '确认清空',
            window.t('confirm.cancel') || '取消',
            true
        );
    }


// Fix CSV file input: use event delegation since panel may not be in DOM on DOMContentLoaded
document.addEventListener('change', function(e) {
    if (e.target && e.target.id === 'apCsvFileInput') {
        if (e.target.files[0]) window.apHandleCsvFile ? window.apHandleCsvFile(e.target.files[0]) : null;
    }
});

document.addEventListener('DOMContentLoaded', () => {
    window.e2seqApp = window.app = new E2seqApp();
    // Always create a fresh AnalysisPanel instance.
    if (typeof AnalysisPanel !== 'undefined') {
        window.analysisPanel = new AnalysisPanel(window.e2seqApp);
    }
    // Bind header button to open analysis panel
    // (removed per UX: upload now starts from right-side drawer only)
    // 上传抽屉事件
    document.getElementById('closeUploadDrawer')?.addEventListener('click', () => {
        window.e2seqApp.closeUploadDrawer();
    });
    document.getElementById('uploadSingleCell')?.addEventListener('click', () => {
        window.e2seqApp.openFilePicker('singlecell');
    });
    document.getElementById('uploadTable')?.addEventListener('click', () => {
        window.e2seqApp.openFilePicker('table');
    });
    // 表格配置抽屉事件
    document.getElementById('closeTableUploadDrawer')?.addEventListener('click', () => {
        window.e2seqApp.closeTableDrawer();
    });
    document.getElementById('confirmTableUpload')?.addEventListener('click', () => {
        window.e2seqApp.confirmTableUpload();
    });
});

// Dynamic style injection for analysis panel
const style = document.createElement('style');
style.textContent = `    .chat-item { display:flex; align-items:center; justify-content:space-between; gap:6px; padding:8px 10px; border-radius:8px; cursor:pointer; transition:background 0.15s; }
    .chat-item:hover { background:var(--bg-hover, rgba(255,255,255,0.06)); }
    .chat-item.active { background:var(--accent-primary, #3b82f6)22; }
    .chat-item-body { flex:1; min-width:0; display:flex; flex-direction:column; gap:2px; overflow:hidden; }
    .chat-item-title { font-size:0.875rem; color:var(--text-primary,#e8eaed); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .chat-item-time { font-size:0.72rem; color:var(--text-secondary,#9aa0ac); }
    .chat-item-del { flex-shrink:0; width:20px; height:20px; border:none; background:transparent; color:var(--text-secondary,#9aa0ac); cursor:pointer; font-size:1rem; line-height:1; border-radius:4px; display:flex; align-items:center; justify-content:center; opacity:0; transition:opacity 0.15s,color 0.15s; }
    .chat-item:hover .chat-item-del { opacity:1; }
    .chat-item-del:hover { color:#ef4444; }

    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes slideOutRight {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100px);
        }
    }

    .loading-spinner {
        width: 40px;
        height: 40px;
        margin: 40px auto;
        border: 4px solid rgba(138, 180, 248, 0.2);
        border-top-color: #8ab4f8;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    .loading-dots {
        display: flex;
        gap: 8px;
        padding: 12px 0;
    }

    .loading-dots span {
        width: 8px;
        height: 8px;
        background: #8ab4f8;
        border-radius: 50%;
        animation: bounce 1.4s infinite ease-in-out both;
    }

    .loading-dots span:nth-child(1) {
        animation-delay: -0.32s;
    }

    /* ===== Thinking & Progress ===== */
    .thinking-indicator {
        font-size: 0.85rem;
        color: var(--text-secondary);
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 8px;
    }
    .thinking-dots::after {
        content: '';
        display: inline-block;
        animation: thinkingEllipsis 1.4s infinite;
    }
    @keyframes thinkingEllipsis {
        0%   { content: ''; }
        25%  { content: '.'; }
        50%  { content: '..'; }
        75%  { content: '...'; }
        100% { content: ''; }
    }

    .progress-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
        font-size: 0.78rem;
    }
    .progress-stage {
        white-space: nowrap;
        color: var(--text-secondary);
        min-width: 90px;
    }
    .progress-bar-wrap {
        flex: 1;
        height: 5px;
        background: rgba(255,255,255,0.08);
        border-radius: 3px;
        overflow: hidden;
    }
    .progress-bar-fill {
        height: 100%;
        width: 0%;
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 3px;
        transition: width 0.4s ease;
        animation: progressGlow 2s ease-in-out infinite;
    }
    @keyframes progressGlow {
        0%, 100% { opacity: 1; }
        50%       { opacity: 0.7; }
    }
    .progress-pct {
        white-space: nowrap;
        color: #4facfe;
        font-family: 'Fira Mono', monospace;
        min-width: 32px;
        text-align: right;
    }

    .loading-dots span:nth-child(2) {
        animation-delay: -0.16s;
    }

    @keyframes bounce {
        0%, 80%, 100% {
            transform: scale(0);
        }
        40% {
            transform: scale(1);
        }
    }

    .empty-state-small {
        padding: 20px;
        text-align: center;
        color: var(--text-secondary);
        font-size: 0.875rem;
    }

    .progress-log {
        margin-top: 6px;
        max-height: 200px;
        overflow-y: auto;
        font-size: 0.76rem;
        font-family: 'Fira Mono', 'Consolas', monospace;
        color: #8ab4f8;
        line-height: 1.8;
        border-left: 2px solid #3b82f633;
        padding-left: 10px;
        scrollbar-width: thin;
        scrollbar-color: rgba(74,172,254,0.3) transparent;
    }
    .progress-log::-webkit-scrollbar { width: 4px; }
    .progress-log::-webkit-scrollbar-thumb { background: rgba(74,172,254,0.3); border-radius: 2px; }

    .progress-step {
        padding: 1px 0;
        white-space: pre-wrap;
        word-break: break-all;
        animation: fadeInUp 0.15s ease;
    }
    .progress-step .step-name {
        color: #f59e0b;
        margin-right: 4px;
    }
    .progress-step .step-text {
        color: #93c5fd;
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(4px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ===== Dataset Config Modal ===== */
    #datasetConfigModal {
        display: none;
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,.55);
        z-index: 2000;
        align-items: center;
        justify-content: center;
    }
    #datasetConfigModal.active { display: flex !important; }
    #datasetConfigModal .modal-content {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-xl);
        padding: 0;
        width: 95%;
        max-width: 560px;
        box-shadow: var(--shadow-lg);
    }
    #datasetConfigModal .modal-header {
        padding: 1.2rem 1.5rem;
        border-bottom: 1px solid var(--border-color);
    }
    #datasetConfigModal .modal-header h2 {
        margin: 0;
        font-size: 1.1rem;
        color: var(--text-primary);
    }
    #datasetConfigModal .modal-body {
        padding: 1.4rem 1.5rem;
        max-height: 70vh;
        overflow-y: auto;
    }
    #datasetConfigModal .modal-footer {
        padding: 1rem 1.5rem;
        border-top: 1px solid var(--border-color);
        display: flex;
        justify-content: flex-end;
        gap: .75rem;
    }
    .config-stat {
        background: var(--bg-tertiary);
        border-radius: var(--radius-md);
        padding: .6rem 1.2rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        min-width: 90px;
    }
    .config-stat span {
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--accent-secondary);
    }
    .config-stat small {
        font-size: .75rem;
        color: var(--text-tertiary);
    }
    .cfg-check-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: .4rem .8rem;
        margin-top: .5rem;
    }

    .chart-error {
        padding: 40px;
        text-align: center;
        color: var(--text-secondary);
    }

    .chart-error p {
        font-size: 1.125rem;
        margin-bottom: 8px;
    }

    .chart-error small {
        font-size: 0.875rem;
        opacity: 0.7;
    }
    .cite-badge {
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 600;
        color: var(--accent-color, #60a5fa);
        background: rgba(96,165,250,0.1);
        border: 1px solid rgba(96,165,250,0.25);
        border-radius: 4px;
        padding: 0 4px;
        margin: 0 1px;
        vertical-align: baseline;
        letter-spacing: 0.02em;
    }
    .message-content h1, .message-content h2, .message-content h3 {
        margin: 1em 0 0.4em;
        font-weight: 700;
        line-height: 1.3;
    }
    .message-content h2 { font-size: 1.1rem; }
    .message-content h3 { font-size: 1rem; }
    .message-content p { margin: 0.5em 0; line-height: 1.7; }
    .message-content strong { font-weight: 700; }
    .message-content code {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85em;
        background: rgba(255,255,255,0.08);
        border-radius: 3px;
        padding: 1px 4px;
    }
    .message-content hr { border: none; border-top: 1px solid var(--border-color); margin: 1em 0; }

`;
document.head.appendChild(style);


// Markdown fallback renderer
function _renderMarkdownFallback(text) {
    if (!text) return '';
    if (typeof marked !== 'undefined') {
        try {
            marked.setOptions({ breaks: true, gfm: true });
            return marked.parse(text);
        } catch(e) { console.warn('marked error', e); }
    }
    var html = text
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/\*\*([^*\n]+?)\*\*/g, '<strong>$1</strong>')
        .replace(/__([^_\n]+?)__/g, '<strong>$1</strong>')
        .replace(/`([^`\n]+?)`/g, '<code>$1</code>')
        .replace(/^### (.+)$/gm, '<h3>$1</h3>')
        .replace(/^## (.+)$/gm, '<h2>$1</h2>')
        .replace(/^# (.+)$/gm, '<h1>$1</h1>')
        .replace(/\[([A-Za-z][A-Za-z0-9:_]+)\]/g, '<span class="cite-badge">[$1]</span>')
        .replace(/^---+$/gm, '<hr>')
        .replace(/\n{2,}/g, '</p><p>')
        .replace(/\n/g, '<br>');
    return '<p>' + html + '</p>';
}
