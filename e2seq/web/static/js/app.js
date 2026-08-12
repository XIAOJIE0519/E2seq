// E2seq Web Application JavaScript

class E2seqApp {
    constructor() {
        this.currentChatId = this._genChatId();
        this.messages = [];
        this.isProcessing = false;
        this._chatRequestToken = 0;
        this._chatInputLocked = false;
        this.currentPage = 'chat';
        this.currentLanguage = localStorage.getItem('e2seq_language') || 'zh-CN';
        this.selectedProvider = '';
        this._providerProfiles = {};
        this._modelCapabilities = {};
        this._activeThinkingModel = '';
        this._activeProviderConfigured = false;
        this.customAnswerSources = [];
        this._answerSourceCatalog = [];
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
        this.loadBuiltinDatabases();
        this.applyLanguage();
        this.initTheme();
        // Load the active model and thinking state for the API settings panel.
        fetch('/api/config').then(async response => {
            const data = await response.json();
            if (!data.configured) return;
            this.selectedProvider = data.provider || this.selectedProvider;
            this._activeThinkingModel = data.model || this._activeThinkingModel;
            this._activeProviderConfigured = true;
            this._updateModelBadge(data.provider, data.model);
            const params = new URLSearchParams({
                provider: data.provider || '',
                model: data.model || '',
            });
            const thinkingResponse = await fetch(`/api/settings/thinking?${params.toString()}`);
            if (thinkingResponse.ok) {
                const thinking = await thinkingResponse.json();
                const thinkingMode = document.getElementById('thinkingModeSelect');
                if (thinkingMode) thinkingMode.value = thinking.thinking_enabled ? 'on' : 'off';
                this._modelCapabilities[data.provider] = {
                    ...(this._modelCapabilities[data.provider] || {}),
                    [data.model]: thinking,
                };
                this._renderThinkingEffortOptions(thinking.effort_levels || []);
                const effort = document.getElementById('thinkingEffortSelect');
                if (effort && thinking.thinking_effort && effort.querySelector(`option[value="${thinking.thinking_effort}"]`)) {
                    effort.value = thinking.thinking_effort;
                }
                await this._updateThinkingCapability(data.provider, data.model, false);
            }
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

        // 必填
        document.getElementById('chartsBtn')?.addEventListener('click', () => this.openChartsPanel());
        document.getElementById('closeChartsPanel')?.addEventListener('click', () => this.closeChartsPanel());

        // Chart type controls / 图表类型控件
        document.querySelectorAll('.chart-type-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.loadChart(e.target.dataset.type));
        });

        // 必填
        document.getElementById('downloadChartBtn')?.addEventListener('click', () => this.downloadChart());
        document.getElementById('fullscreenChartBtn')?.addEventListener('click', () => this.fullscreenChart());
        document.getElementById('refreshChartBtn')?.addEventListener('click', () => this.refreshChart());

        // 必填
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

        sendBtn?.addEventListener('click', () => this.sendMessage());
        // 首页示例卡片仅做展示动画，不绑定点击行为

        // 附件按钮 — 打开文件选择器上传文件
        document.getElementById('attachBtn')?.addEventListener('click', () => {
            this.handleAttachment();
        });

        // Upload and answer-source controls / 上传与回答数据源控件
        document.getElementById('uploadDBBtn')?.addEventListener('click', () => this.uploadDatabase());
        document.getElementById('closeDBDetail')?.addEventListener('click', () => this.closeDBDetail());
        document.getElementById('saveAnswerSettingsBtn')?.addEventListener('click', () => this.saveAnswerSettings());
        document.getElementById('addCustomAnswerSourceBtn')?.addEventListener('click', () => this.addCustomAnswerSource());

        // 必填
        document.getElementById('saveSettingsBtn')?.addEventListener('click', () => this.saveSettings());
        document.querySelectorAll('.provider-choice[data-provider]').forEach(button => {
            button.addEventListener('click', () => this.selectProvider(button.dataset.provider, true));
        });

        // Embedding 模型测试按钮
        document.getElementById('testEmbedBtn')?.addEventListener('click', () => this.testEmbeddingModel());
        document.getElementById('embedSavePathBtn')?.addEventListener('click', () => this.saveCurrentEmbedPath());
        document.getElementById('embedAddCustomBtn')?.addEventListener('click', () => this.addCustomEmbeddingModel());
        document.getElementById('embedAddHfModelBtn')?.addEventListener('click', () => this.addHfEmbeddingModel());
        document.getElementById('embedDownloadBtn')?.addEventListener('click', () => this.downloadEmbeddingModel());

        // key 输入框失焦时自动拉取模型
        ['openai','anthropic','gemini','deepseek','siliconflow','sdu','glm','kimi'].forEach(provider => {
            const keyEl = document.getElementById(provider + 'Key');
            const btnEl = document.querySelector(`.btn-fetch-models[data-provider='${provider}']`);
            const sel = document.getElementById(provider + 'Model');
            const customEl = document.getElementById(provider + 'ModelCustom');
            if (keyEl) {
                keyEl.addEventListener('blur', () => {
                    if (keyEl.value.trim()) this.fetchModels(provider);
                });
                keyEl.addEventListener('input', () => {
                    // 清空时隐藏下拉框
                    if (!keyEl.value.trim()) {
                        const sel = document.getElementById(provider + 'Model');
                        if (sel) sel.style.display = 'none';
                        if (customEl) customEl.style.display = 'none';
                        const status = document.getElementById('status-' + provider);
                        if (status) status.innerHTML = '';
                    }
                });
            }
            if (btnEl) {
                btnEl.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.fetchModels(provider);
                });
            }
            // Custom model input: when user types, clear dropdown selection
            if (customEl) {
                customEl.addEventListener('input', () => {
                    const sel = document.getElementById(provider + 'Model');
                    if (sel) sel.selectedIndex = -1;
                    this._updateThinkingCapability(provider, customEl.value.trim());
                });
            }
            if (sel) {
                sel.addEventListener('change', () => {
                    this._updateThinkingCapability(provider, sel.value);
                });
            }
        });

        // Custom API fetch button
        document.getElementById('fetchModelsCustomBtn')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.fetchModelsCustom();
        });
        document.getElementById('customModel')?.addEventListener('change', (e) => {
            this._updateThinkingCapability('custom', e.target.value);
        });
        // On Enter in custom URL field, also trigger
        document.getElementById('customBaseUrl')?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') { e.preventDefault(); this.fetchModelsCustom(); }
        });
        document.getElementById('customKey')?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') { e.preventDefault(); this.fetchModelsCustom(); }
        });

        document.getElementById('thinkingModeSelect')?.addEventListener('change', () => {
            this._persistThinkingMode(true);
        });
        document.getElementById('thinkingEffortSelect')?.addEventListener('change', () => {
            if (document.getElementById('thinkingModeSelect')?.value === 'on') {
                this._persistThinkingMode(true);
            }
        });

        // 必填
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

    // ========== 必填 ==========
    navigateToChat() {
        this.switchPage('chat');
        // KB build polling removed — agentic RAG builds on demand per question
    }

    _setInputLocked(locked, placeholder) {
        this._chatInputLocked = !!locked;
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        if (messageInput) {
            messageInput.disabled = this._chatInputLocked;
            if (placeholder) messageInput.placeholder = placeholder;
            else messageInput.placeholder = this._t('chat.inputPlaceholder');
        }
        if (sendBtn) sendBtn.disabled = this._chatInputLocked || !messageInput?.value.trim();
    }

    navigateToKnowledgeBase() {
        this.switchPage('knowledgeBase');
        // Re-render database descriptions after a language change.
        this.loadBuiltinDatabases();
        this.loadCustomDatabases();
        this.loadAnswerSettings();
    }

    navigateToSettings() {
        this.switchPage('settings');
        this.loadSettings();
        this.loadStorageInfo();
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

    // ========== 必填? ==========
    _answerSourceLabelKey(sourceId) {
        return `kb.source.${String(sourceId || '').trim().toLowerCase()}`;
    }

    _renderAnswerSources(sources, enabledApis, enabledDbs) {
        this._answerSourceCatalog = Array.isArray(sources) ? sources : [];
        const containers = {
            api: document.getElementById('kbAnswerSourcesApi'),
            db: document.getElementById('kbAnswerSourcesDb'),
        };
        Object.values(containers).forEach(container => container?.replaceChildren());
        (Array.isArray(sources) ? sources : []).forEach(source => {
            const kind = source.kind === 'db' ? 'db' : 'api';
            const container = containers[kind];
            if (!container) return;
            const id = String(source.id || '').trim();
            if (!id) return;
            const label = document.createElement('label');
            label.className = 'kb-source-option';
            const input = document.createElement('input');
            input.type = 'checkbox';
            input.value = id;
            input.dataset.sourceKind = kind;
            input.checked = kind === 'api' ? enabledApis.includes(id) : enabledDbs.includes(id);
            const name = document.createElement('span');
            if (source.name) {
                name.textContent = String(source.name);
            } else {
                name.dataset.i18n = this._answerSourceLabelKey(id);
                name.textContent = this._t(this._answerSourceLabelKey(id)) || id;
            }
            label.append(input, name);
            container.appendChild(label);
        });
    }

    _renderCustomAnswerSources() {
        const container = document.getElementById('kbCustomAnswerSourcesList');
        if (!container) return;
        container.replaceChildren();
        this.customAnswerSources.forEach(source => {
            const row = document.createElement('div');
            row.className = 'kb-custom-api-row';
            const meta = document.createElement('div');
            meta.className = 'kb-custom-api-meta';
            const title = document.createElement('strong');
            title.textContent = String(source.name || source.id || 'Custom API');
            const detail = document.createElement('small');
            const auth = source.has_headers || (source.headers && Object.keys(source.headers).length) ? ' · auth configured' : '';
            detail.textContent = `${source.id || ''} · ${source.method || 'GET'}${auth}`;
            meta.append(title, detail);
            const remove = document.createElement('button');
            remove.type = 'button';
            remove.className = 'btn-secondary kb-custom-api-remove';
            remove.textContent = this._t('kb.removeCustomApi') || 'Remove';
            remove.addEventListener('click', () => {
                const checkedApis = Array.from(document.querySelectorAll('#kbAnswerSourcesApi input[type="checkbox"]'))
                    .filter(input => input.checked && input.value !== source.id)
                    .map(input => input.value);
                const checkedDbs = Array.from(document.querySelectorAll('#kbAnswerSourcesDb input[type="checkbox"]'))
                    .filter(input => input.checked)
                    .map(input => input.value);
                this.customAnswerSources = this.customAnswerSources.filter(item => item.id !== source.id);
                const sources = this._answerSourceCatalog.filter(item => item.id !== source.id);
                this._renderAnswerSources(sources, checkedApis, checkedDbs);
                this._renderCustomAnswerSources();
            });
            row.append(meta, remove);
            container.appendChild(row);
        });
    }

    addCustomAnswerSource() {
        const idInput = document.getElementById('customAnswerSourceId');
        const nameInput = document.getElementById('customAnswerSourceName');
        const methodInput = document.getElementById('customAnswerSourceMethod');
        const urlInput = document.getElementById('customAnswerSourceUrl');
        const pathInput = document.getElementById('customAnswerSourceRecordsPath');
        const geneParamInput = document.getElementById('customAnswerSourceGeneParam');
        const queryParamInput = document.getElementById('customAnswerSourceQueryParam');
        const contextParamInput = document.getElementById('customAnswerSourceContextParam');
        const headersInput = document.getElementById('customAnswerSourceHeaders');
        const bodyInput = document.getElementById('customAnswerSourceBody');
        const name = nameInput?.value.trim() || '';
        const url = urlInput?.value.trim() || '';
        if (!name || !url) {
            this.showNotification(this._t('kb.customApiRequired') || 'Name and URL are required', 'error');
            return;
        }
        const generatedId = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 48);
        const id = (idInput?.value.trim().toLowerCase() || generatedId).replace(/[^a-z0-9_-]/g, '-');
        if (!/^[a-z][a-z0-9_-]{1,48}$/.test(id)) {
            this.showNotification(this._t('kb.customApiIdInvalid') || 'Use a valid source id', 'error');
            return;
        }
        if (this._answerSourceCatalog.some(source => source.id === id)) {
            this.showNotification(this._t('kb.customApiDuplicate') || 'This source id already exists', 'error');
            return;
        }
        let headers = {};
        const headerText = headersInput?.value.trim() || '';
        if (headerText) {
            try {
                headers = JSON.parse(headerText);
                if (!headers || Array.isArray(headers) || typeof headers !== 'object') throw new Error('object required');
            } catch (error) {
                this.showNotification(this._t('kb.customApiHeadersInvalid') || 'Headers must be valid JSON', 'error');
                return;
            }
        }
        let bodyTemplate = '';
        const bodyText = bodyInput?.value.trim() || '';
        if (bodyText) {
            try {
                bodyTemplate = JSON.parse(bodyText);
                if (!bodyTemplate || (typeof bodyTemplate !== 'object')) throw new Error('object required');
            } catch (error) {
                this.showNotification(this._t('kb.customApiBodyInvalid') || 'POST body must be valid JSON', 'error');
                return;
            }
        }
        const source = {
            id,
            name,
            url_template: url,
            method: methodInput?.value === 'POST' ? 'POST' : 'GET',
            records_path: pathInput?.value.trim() || '',
            gene_param: geneParamInput?.value.trim() || 'gene',
            query_param: queryParamInput?.value.trim() || 'query',
            context_param: contextParamInput?.value.trim() || 'context',
            headers,
            body_template: bodyTemplate,
            enabled: true,
            max_records: 20,
            timeout: 20,
        };
        this.customAnswerSources.push(source);
        const checkedApis = Array.from(document.querySelectorAll('#kbAnswerSourcesApi input[type="checkbox"]'))
            .filter(input => input.checked).map(input => input.value);
        checkedApis.push(id);
        const checkedDbs = Array.from(document.querySelectorAll('#kbAnswerSourcesDb input[type="checkbox"]'))
            .filter(input => input.checked).map(input => input.value);
        this._renderAnswerSources(
            [...this._answerSourceCatalog, { id, kind: 'api', custom: true, name }],
            checkedApis,
            checkedDbs,
        );
        this._renderCustomAnswerSources();
        [idInput, nameInput, urlInput, pathInput, geneParamInput, queryParamInput,
         contextParamInput, headersInput, bodyInput].forEach(input => { if (input) input.value = ''; });
        if (methodInput) methodInput.value = 'GET';
        this.showNotification(this._t('kb.customApiAdded') || 'API added; save answer settings to activate it', 'success');
    }

    async loadAnswerSettings() {
        try {
            const response = await fetch('/api/answer-settings');
            if (!response.ok) return;
            const data = await response.json();
            this.customAnswerSources = Array.isArray(data.custom_sources) ? data.custom_sources : [];
            this._renderAnswerSources(
                data.sources || [],
                Array.isArray(data.enabled_apis) ? data.enabled_apis : [],
                Array.isArray(data.enabled_dbs) ? data.enabled_dbs : [],
            );
            this._renderCustomAnswerSources();
            const status = document.getElementById('kbAnswerSettingsStatus');
            if (status) status.textContent = data.configured ? this._t('kb.answerSettingsLoaded') : '';
        } catch (error) {
            console.error('Failed to load answer settings:', error);
        }
    }

    async saveAnswerSettings() {
        const inputs = Array.from(document.querySelectorAll('#kbAnswerSourcesApi input[type="checkbox"], #kbAnswerSourcesDb input[type="checkbox"]'));
        const enabledApis = inputs.filter(input => input.dataset.sourceKind === 'api' && input.checked).map(input => input.value);
        const enabledDbs = inputs.filter(input => input.dataset.sourceKind === 'db' && input.checked).map(input => input.value);
        const button = document.getElementById('saveAnswerSettingsBtn');
        const status = document.getElementById('kbAnswerSettingsStatus');
        if (button) button.disabled = true;
        try {
            const response = await fetch('/api/answer-settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    enabled_apis: enabledApis,
                    enabled_dbs: enabledDbs,
                    custom_sources: this.customAnswerSources,
                }),
            });
            const data = await response.json().catch(() => ({}));
            if (!response.ok || !data.success) throw new Error(data.detail || this._t('kb.answerSettingsSaveFailed'));
            this.customAnswerSources = Array.isArray(data.custom_sources) ? data.custom_sources : this.customAnswerSources;
            if (Array.isArray(data.sources)) {
                this._renderAnswerSources(data.sources, data.enabled_apis || enabledApis, data.enabled_dbs || enabledDbs);
                this._renderCustomAnswerSources();
            }
            if (status) status.textContent = this._t('kb.answerSettingsSaved');
            this.showNotification(this._t('kb.answerSettingsSaved'), 'success');
        } catch (error) {
            if (status) status.textContent = error.message || this._t('kb.answerSettingsSaveFailed');
            this.showNotification(error.message || this._t('kb.answerSettingsSaveFailed'), 'error');
        } finally {
            if (button) button.disabled = false;
        }
    }

    loadBuiltinDatabases() {
        const grid = document.getElementById('builtinDBGrid');
        if (!grid) return;

        grid.innerHTML = this.builtinDatabases.map(db => `
            <div class="db-card" data-db="${db.name}">
                <div class="db-card-header">
                    <h3>${db.name}</h3>
                    <span class="db-status">${t('kb.status')}</span>
                </div>
                <div class="db-card-body">
                    <p class="db-description">${t(db.descriptionKey)}</p>
                    <div class="db-stats">
                        <span class="stat-item">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                                <circle cx="12" cy="7" r="4"></circle>
                            </svg>
                            ${db.records} ${t('kb.records')}
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
                    <button class="btn-text" onclick="window.e2seqApp.showDBDetail('${db.name}')">${t('kb.viewDetail')}</button>
                </div>
            </div>
        `).join('');
    }

    showDBDetail(dbName) {
        const db = this.builtinDatabases.find(d => d.name === dbName);
        if (!db) return;

        const modal = document.getElementById('dbDetailModal');
        const title = document.getElementById('dbDetailTitle');
        const body = document.getElementById('dbDetailBody');

        title.textContent = `${db.name} - ${t('dbDetail.title')}`;
        body.innerHTML = `
            <div class="db-detail">
                <div class="detail-section">
                    <h4>${t('dbDetail.basicInfo')}</h4>
                    <table class="detail-table">
                        <tr><td>${t('dbDetail.name')}</td><td>${db.name}</td></tr>
                        <tr><td>${t('dbDetail.records')}</td><td>${db.records}</td></tr>
                        <tr><td>${t('dbDetail.format')}</td><td>${db.format}</td></tr>
                        <tr><td>${t('dbDetail.description')}</td><td>${t(db.descriptionKey)}</td></tr>
                    </table>
                </div>
                <div class="detail-section">
                    <h4>${t('dbDetail.fields')}</h4>
                    <ul class="field-list">
                        ${db.fields.map(field => `<li><code>${field}</code></li>`).join('')}
                    </ul>
                </div>
                <div class="detail-section">
                    <h4>${t('dbDetail.example')}</h4>
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
        // 必填必填?
        this.showUploadInstructions();
    }

    showUploadInstructions() {
        const modal = document.getElementById('uploadInstructionsModal');
        if (!modal) {
            // 必填?
            const modalHTML = `
                <div class="modal" id="uploadInstructionsModal">
                    <div class="modal-content" style="max-width: 700px;">
                        <div class="modal-header">
                            <h2 data-i18n="kb.uploadTitle">上传自定义数据库</h2>
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
                                    <h3 data-i18n="kb.requiredFields">必填</h3>
                                    <p data-i18n="kb.csvFormatDesc">请上传 CSV 文件，文件必须包含以下字段：</p>
                                    <ul class="field-requirements">
                                        <li>
                                            <code>gene</code>
                                            <span class="field-desc" data-i18n="kb.sourceFieldDesc">基因列</span>
                                            <span class="required-badge" data-i18n="kb.required">必需</span>
                                        </li>
                                        <li>
                                            <code>annotation</code>
                                            <span class="field-desc" data-i18n="kb.targetFieldDesc">任意注释列</span>
                                            <span class="required-badge" data-i18n="kb.required">必需</span>
                                        </li>
                                    </ul>
                                </div>

                                <div class="instruction-section">
                                    <h3 data-i18n="kb.formatRequirements">文件格式要求</h3>
                                    <ul class="format-list">
                                        <li>
                                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                                <polyline points="20 6 9 17 4 12"></polyline>
                                            </svg>
                                            <span data-i18n="kb.supportedTextFormats">CSV、TSV 或 TXT 格式</span>
                                        </li>
                                        <li>
                                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                                <polyline points="20 6 9 17 4 12"></polyline>
                                            </svg>
                                            <span data-i18n="kb.utf8Encoding">UTF-8 编码</span>
                                        </li>
                                        <li>
                                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                                <polyline points="20 6 9 17 4 12"></polyline>
                                            </svg>
                                            <span data-i18n="kb.maxFileSize">文件大小不超过 50 MB</span>
                                        </li>
                                    </ul>
                                </div>

                                <div class="instruction-section">
                                    <h3 data-i18n="kb.formatExample">格式示例</h3>
                                    <pre class="code-block">gene,annotation,source
TP53,tumor suppressor,example
BRCA1,DNA repair,example
EGFR,receptor tyrosine kinase,example</pre>
                                    <button class="btn-text download-template-btn" onclick="window.e2seqApp.downloadTemplate()">
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                                            <polyline points="7 10 12 15 17 10"></polyline>
                                            <line x1="12" y1="15" x2="12" y2="3"></line>
                                        </svg>
                                        <span data-i18n="kb.downloadTemplate">下载模板</span>
                                    </button>
                                </div>

                                <div class="instruction-section">
                                    <h3 data-i18n="kb.notes">注意事项</h3>
                                    <ul class="notes-list">
                                        <li data-i18n="kb.noteUtf8">请使用 UTF-8 编码保存文件</li>
                                        <li data-i18n="kb.noteHeader">第一行必须包含字段名</li>
                                        <li data-i18n="kb.noteRequired">所有必需字段都必须存在</li>
                                        <li data-i18n="kb.noteOrder">字段顺序可以任意</li>
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
        this.applyLanguage(); // 必填选填
    }

    closeUploadInstructions() {
        const modal = document.getElementById('uploadInstructionsModal');
        if (modal) {
            modal.classList.remove('active');
        }
    }

    downloadTemplate() {
        // 必填CSV选填
        const templateContent = `gene,annotation,source
TP53,tumor suppressor,example
BRCA1,DNA repair,example
EGFR,receptor tyrosine kinase,example
MYC,transcription factor,example
STAT3,immune signaling,example`;

        // 选填Blob选填?
        const blob = new Blob([templateContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);

        link.setAttribute('href', url);
        link.setAttribute('download', 'gene_annotation_template.csv');
        link.style.visibility = 'hidden';

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        this.showNotification(t('notify.templateDownloaded'), 'success');
    }

    selectFileToUpload() {
        this.closeUploadInstructions();
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.csv,.tsv,.txt';
        input.onchange = async (e) => {
            const file = e.target.files[0];
            if (file) {
                // 必填
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
        // 必填选填
        const maxSize = 50 * 1024 * 1024; // 50MB
        if (file.size > maxSize) {
            return {
                valid: false,
                error: t('error.fileTooLarge')
            };
        }

        // 必填选填?
        const validExtensions = ['.csv', '.tsv', '.txt'];
        const fileName = file.name.toLowerCase();
        const hasValidExtension = validExtensions.some(ext => fileName.endsWith(ext));

        if (!hasValidExtension) {
            return {
                valid: false,
                error: t('error.invalidFileType')
            };
        }

        // 必填必填?
        try {
            const text = await file.text();
            const lines = text.split('\n').filter(line => line.trim());

            if (lines.length < 2) {
                return {
                    valid: false,
                    error: t('error.emptyFile')
                };
            }

            // 必填
            const header = lines[0].toLowerCase();
            const requiredFields = ['gene'];
            const missingFields = requiredFields.filter(field => !header.includes(field));

            if (missingFields.length > 0) {
                return {
                    valid: false,
                    error: t('error.missingFields') + ': ' + missingFields.join(', ')
                };
            }

            return { valid: true };
        } catch (error) {
            return {
                valid: false,
                error: t('error.fileReadError')
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
                throw new Error(t('notify.dbUploadFailed'));
            }

            this.showNotification(t('notify.dbUploaded') + `: ${file.name}`, 'success');
            this.loadCustomDatabases();
        } catch (error) {
            console.error('必填?:', error);
            this.showNotification(t('notify.dbUploadFailed'), 'error');
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
                        <p>${t('kb.empty')}</p>
                        <small>${t('kb.emptyHint')}</small>
                    </div>
                `;
            } else {
                grid.innerHTML = databases.map(db => `
                    <div class="db-card" data-db-id="${db.id}">
                        <div class="db-card-header">
                            <h3>${db.name}</h3>
                            <span class="db-type-badge">${t('kb.customBadge')}</span>
                        </div>
                        <div class="db-card-body">
                            <div class="db-stats">
                                <span class="stat-item">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                                        <circle cx="12" cy="7" r="4"></circle>
                                    </svg>
                                    ${db.records} ${t('kb.records')}
                                </span>
                            </div>
                        </div>
                        <div class="db-card-footer">
                            <button class="btn-text" onclick="window.e2seqApp.deleteDatabase('${db.id}')">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polyline points="3 6 5 6 21 6"></polyline>
                                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                </svg>
                                ${t('kb.delete')}
                            </button>
                        </div>
                    </div>
                `).join('');
            }
        } catch (error) {
            console.error('必填选填:', error);
        }
    }

    async deleteDatabase(dbName) {
        if (!confirm(`${t('kb.delete')} ${dbName}?`)) return;

        try {
            const response = await fetch(`/api/knowledge-bases/${dbName}`, {
                method: 'DELETE',
            });

            if (!response.ok) {
                throw new Error(t('notify.dbDeleteFailed'));
            }

            this.showNotification(t('notify.dbDeleted'), 'success');
            this.loadCustomDatabases();
        } catch (error) {
            console.error('必填?:', error);
            this.showNotification(t('notify.dbDeleteFailed'), 'error');
        }
    }

    // ========== 选填 ==========
    openChartsPanel() {
        document.getElementById('chartsPanel')?.classList.add('active');
    }

    closeChartsPanel() {
        document.getElementById('chartsPanel')?.classList.remove('active');
    }

    async loadChart(type) {
        // 必填必填
        document.querySelectorAll('.chart-type-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.type === type);
        });

        const container = document.getElementById('chartContainer');
        container.innerHTML = '<div class="loading-spinner"></div>';

        try {
            const response = await fetch(`/api/plots/${type}`);
            if (!response.ok) {
                throw new Error(t('error.loadFailed'));
            }

            const plotData = await response.json();

            // 必填选填?
            if (plotData.data && plotData.data.length === 0 && plotData.layout.annotations) {
                // 必填必填?
                container.innerHTML = `
                    <div class="chart-error">
                        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                            <polyline points="14 2 14 8 20 8"></polyline>
                            <line x1="16" y1="13" x2="8" y2="13"></line>
                            <line x1="16" y1="17" x2="8" y2="17"></line>
                        </svg>
                        <p>${t('charts.noData')}</p>
                        <small>${t('charts.noDataHint')}</small>
                    </div>
                `;
            } else {
                // 必填
                Plotly.newPlot('chartContainer', plotData.data, plotData.layout, {responsive: true});
            }
        } catch (error) {
            console.error('必填选填:', error);
            container.innerHTML = `
                <div class="chart-error">
                    <p>${t('error.loadFailed')}</p>
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

    // ========== 选填 ==========
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
        const provider = cfg.provider || this._getEmbeddingProvider();

        const saveResp = await fetch('/api/embedding/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model_name: modelId,
                model_dimension: cfg.model_dimension,
                normalize: cfg.normalize,
                provider,
                local_only: provider === 'local',
                model_paths: modelPaths,
                custom_models: cfg.custom_models || [],
            }),
        });
        const data = await saveResp.json();
        if (!saveResp.ok || !data.success) {
            this.showNotification(data.detail || data.message || this._t('embed.pathSaveFailed'), 'error');
            return;
        }
        this.showNotification(this._t('embed.pathSaved'), 'success');
        await this.loadEmbeddingSettings();
    }

    async addCustomEmbeddingModel() {
        const id = (document.getElementById('embedCustomId')?.value || '').trim();
        const name = (document.getElementById('embedCustomName')?.value || '').trim();
        const path = (document.getElementById('embedCustomPath')?.value || '').trim();
        const dimRaw = (document.getElementById('embedCustomDim')?.value || '').trim();
        const size = (document.getElementById('embedCustomSize')?.value || '').trim();

        if (!id || !path) {
            this.showNotification(this._t('embed.customRequired'), 'error');
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
            size: size || '—',
            description: '',
        });

        const modelPaths = { ...(cfg.model_paths || {}), [id]: path };
        const provider = cfg.provider || this._getEmbeddingProvider();

        const saveResp = await fetch('/api/embedding/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model_name: cfg.model_name || id,
                model_dimension: cfg.model_dimension,
                normalize: cfg.normalize,
                provider,
                local_only: provider === 'local',
                model_paths: modelPaths,
                custom_models: customModels,
            }),
        });
        const data = await saveResp.json();
        if (!saveResp.ok || !data.success) {
            this.showNotification(data.detail || data.message || this._t('embed.customAddFailed'), 'error');
            return;
        }

        this.showNotification(this._t('embed.customAdded'), 'success');
        await this.loadEmbeddingSettings();
        const sel = document.getElementById('embeddingModelSelect');
        if (sel) sel.value = id;
        this.updateEmbeddingInfo(this._embeddingModels || [], id);
    }

    async addHfEmbeddingModel() {
        const input = document.getElementById('embeddingHfModelId');
        const modelId = (input?.value || '').trim();
        if (!modelId) {
            this.showNotification(this._t('embed.hfModelRequired'), 'error');
            input?.focus();
            return;
        }

        try {
            const cfgResp = await fetch('/api/embedding/config');
            const cfg = cfgResp.ok ? await cfgResp.json() : {};
            const customModels = [...(cfg.custom_models || [])]
                .filter(model => (model?.id || '') !== modelId);
            customModels.push({
                id: modelId,
                name: modelId,
                dimension: null,
                size: this._t('embed.unknownValue'),
                description: this._t('embed.userHfDescription'),
                provider: 'hf_api',
            });
            const modelPaths = { ...(cfg.model_paths || {}) };
            delete modelPaths[modelId];
            const token = (document.getElementById('embeddingHfToken')?.value || '').trim();
            const resp = await fetch('/api/embedding/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model_name: modelId,
                    model_dimension: null,
                    normalize: cfg.normalize,
                    provider: 'hf_api',
                    local_only: false,
                    model_paths: modelPaths,
                    custom_models: customModels,
                    ...(token ? { hf_token: token } : {}),
                }),
            });
            const data = await resp.json();
            if (!resp.ok || !data.success) {
                this.showNotification(data.detail || data.message || this._t('embed.customAddFailed'), 'error');
                return;
            }
            if (input) input.value = '';
            const tokenInput = document.getElementById('embeddingHfToken');
            if (tokenInput && token) tokenInput.value = '';
            await this.loadEmbeddingSettings();
            const sel = document.getElementById('embeddingModelSelect');
            if (sel) sel.value = modelId;
            this.updateEmbeddingInfo(this._embeddingModels || [], modelId);
            this.showNotification(this._t('embed.remoteAdded'), 'success');
        } catch (error) {
            this.showNotification(error.message || this._t('embed.customAddFailed'), 'error');
        }
    }

    async downloadEmbeddingModel() {
        const modelId = document.getElementById('embeddingModelSelect')?.value;
        const path = (document.getElementById('embedModelPathInput')?.value || '').trim();
        const button = document.getElementById('embedDownloadBtn');
        if (!modelId) return;

        if (button) {
            button.disabled = true;
            button.textContent = this._t('embed.downloadStarted');
        }
        try {
            const resp = await fetch('/api/embedding/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model_name: modelId, local_path: path }),
            });
            const data = await resp.json();
            if (!resp.ok || !data.success) {
                this.showNotification(data.detail || data.message || this._t('embed.downloadFailed'), 'error');
                return;
            }
            await this.loadEmbeddingSettings();
            this.showNotification(this._t('embed.downloadSuccess'), 'success');
        } catch (error) {
            this.showNotification(error.message || this._t('embed.downloadFailed'), 'error');
        } finally {
            if (button) {
                button.disabled = false;
                button.textContent = this._t('settings.downloadEmbed');
            }
        }
    }

    _renderProviderState(activeProvider) {
        this.selectedProvider = activeProvider || this.selectedProvider || '';
        document.querySelectorAll('[data-provider-card]').forEach(card => {
            const provider = card.dataset.providerCard;
            const profile = this._providerProfiles?.[provider] || {};
            const isActive = provider === this.selectedProvider;
            card.classList.toggle('is-active', isActive);
            card.classList.toggle('is-configured', !!profile.configured);
            card.classList.remove('has-error');
            const choice = card.querySelector('.provider-choice');
            if (choice) {
                choice.setAttribute('aria-pressed', String(isActive));
                choice.setAttribute('aria-busy', 'false');
            }
            const state = card.querySelector('.provider-choice-state');
            if (state) {
                state.textContent = isActive
                    ? this._t('settings.activeProvider')
                    : (profile.configured ? this._t('settings.providerConfigured') : this._t('settings.useProvider'));
            }
            const status = document.getElementById('status-' + provider);
            if (status && profile.model) {
                status.textContent = `${this._t('embed.currentModel')}: ${profile.model}`;
            }
        });
    }

    async selectProvider(provider, activate = false) {
        if (!provider) return;
        this.selectedProvider = provider;
        this._renderProviderState(provider);
        if (!activate) return;

        const profile = this._providerProfiles?.[provider] || {};
        if (!profile.configured) {
            document.querySelector(`[data-provider-card="${provider}"]`)?.classList.add('has-error');
            document.getElementById(provider + 'Key')?.focus();
            this.showNotification(this._t('settings.providerNeedsKey'), 'info');
            return;
        }

        const choice = document.querySelector(`.provider-choice[data-provider="${provider}"]`);
        choice?.setAttribute('aria-busy', 'true');
        const model = this._getProviderModel(provider) || profile.model || '';
        try {
            const response = await fetch('/api/settings/switch-model', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    provider,
                    model,
                    thinking_enabled: this._thinkingEnabledFromUi(),
                    thinking_effort: this._thinkingEffortFromUi(),
                }),
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.detail || this._t('app.connectError'));
            this._updateModelBadge(result.provider, result.model);
            this.showNotification(this._t('settings.providerSwitched'), 'success');
            await this.loadSettings();
        } catch (error) {
            document.querySelector(`[data-provider-card="${provider}"]`)?.classList.add('has-error');
            this.showNotification(error.message, 'error');
        } finally {
            choice?.setAttribute('aria-busy', 'false');
        }
    }

    _getProviderModel(provider) {
        const customValue = document.getElementById(provider + 'ModelCustom')?.value?.trim();
        const selectedValue = document.getElementById(provider + 'Model')?.value;
        return customValue || selectedValue || this._providerProfiles?.[provider]?.model || '';
    }

    _thinkingEnabledFromUi() {
        return document.getElementById('thinkingModeSelect')?.value === 'on';
    }

    _thinkingEffortFromUi() {
        return document.getElementById('thinkingEffortSelect')?.value || 'high';
    }

    _renderThinkingEffortOptions(levels) {
        const select = document.getElementById('thinkingEffortSelect');
        if (!select) return;
        const values = Array.isArray(levels) ? levels.filter(Boolean).map(String) : [];
        if (!values.length) {
            select.innerHTML = '';
            select.style.display = 'none';
            return;
        }
        const current = this._thinkingEffortFromUi();
        select.innerHTML = values.map(value => {
            const normalized = value.toLowerCase();
            const labelKey = normalized === 'low'
                ? 'settings.thinkingLow'
                : normalized === 'medium'
                    ? 'settings.thinkingMedium'
                    : normalized === 'high'
                        ? 'settings.thinkingHigh'
                        : normalized === 'xhigh'
                            ? 'settings.thinkingXhigh'
                            : normalized === 'max' ? 'settings.thinkingMax' : '';
            const label = labelKey ? this._t(labelKey) : value;
            return `<option value="${value.replace(/"/g, '&quot;')}">${label}</option>`;
        }).join('');
        select.value = values.includes(current) ? current : values[0];
        select.style.display = values.length > 1 ? '' : 'none';
    }

    _thinkingCapabilityAllowsOn(capability) {
        if (!capability) return false;
        if (capability.always_on || capability.capability_state === 'always_on') return true;
        if (capability.capability_state) return capability.capability_state === 'supported';
        // Compatibility with older server responses: only a confirmed,
        // model-specific positive result can enable the control.
        return Boolean(
            capability.capability_known
            && capability.supports_thinking
            && capability.model_supported
        );
    }

    async _updateThinkingCapability(provider, model, fetchIfMissing = true) {
        const modelId = String(model || '').trim();
        const activeModel = document.getElementById('thinkingActiveModel');
        const hint = document.getElementById('thinkingCapabilityHint');
        const mode = document.getElementById('thinkingModeSelect');
        const effort = document.getElementById('thinkingEffortSelect');
        if (!activeModel || !hint || !mode) return;
        if (!modelId) {
            this._activeThinkingModel = '';
            activeModel.textContent = this._t('settings.thinkingNoModel');
            hint.textContent = '';
            hint.title = '';
            mode.value = 'off';
            mode.disabled = true;
            if (effort) effort.disabled = true;
            this._renderThinkingEffortOptions([]);
            return;
        }

        activeModel.textContent = `${provider} / ${modelId}`;
        this._activeThinkingModel = modelId;
        this._modelCapabilities[provider] = this._modelCapabilities[provider] || {};
        let capability = this._modelCapabilities[provider][modelId];
        if (!capability && fetchIfMissing) {
            try {
                const params = new URLSearchParams({provider, model: modelId});
                const response = await fetch(`/api/settings/thinking?${params.toString()}`);
                if (response.ok) {
                    capability = await response.json();
                    this._modelCapabilities[provider][modelId] = capability;
                }
            } catch (_) {
                // A failed capability lookup remains safely off until a
                // confirmed provider/model result is available.
            }
        }
        capability = capability || {
            supports_thinking: false,
            model_supported: false,
            capability_known: false,
            always_on: false,
            capability_state: 'unknown',
            thinking_parameter: 'unknown',
            effort_levels: [],
        };
        this._renderThinkingEffortOptions(capability.effort_levels);

        const alwaysOn = Boolean(capability.always_on || capability.capability_state === 'always_on');
        const canEnable = this._thinkingCapabilityAllowsOn(capability);
        if (alwaysOn) {
            mode.value = 'on';
        } else if (!canEnable) {
            // Unknown and unsupported models stay off.  This prevents a stale
            // setting from silently sending an unverified parameter.
            mode.value = 'off';
        }
        mode.disabled = !canEnable || alwaysOn;
        if (effort) effort.disabled = !canEnable;

        let messageKey = 'settings.thinkingUnknown';
        if (alwaysOn) {
            messageKey = 'settings.thinkingAlwaysOn';
        } else if (capability.capability_state === 'supported' || canEnable) {
            messageKey = 'settings.thinkingSupported';
        } else if (capability.capability_state === 'unsupported' || capability.capability_known) {
            messageKey = 'settings.thinkingUnsupported';
        }
        const message = this._t(messageKey);
        hint.textContent = message;
        hint.title = message;
        mode.title = message;
        if (effort) effort.title = message;
    }

    async _persistThinkingMode(showFeedback = false) {
        const provider = this.selectedProvider;
        const profile = this._providerProfiles?.[provider] || {};
        if (!provider || (!profile.configured && !this._activeProviderConfigured)) return;
        try {
            const response = await fetch('/api/settings/thinking', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    enabled: this._thinkingEnabledFromUi(),
                    effort: this._thinkingEffortFromUi(),
                }),
            });
            const result = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(result.detail || this._t('notify.saveFailed'));
            if (showFeedback) {
                this.showNotification(
                    this._thinkingEnabledFromUi()
                        ? this._t('settings.thinkingOn')
                        : this._t('settings.thinkingOff'),
                    'success'
                );
            }
        } catch (error) {
            this.showNotification(error.message || this._t('notify.saveFailed'), 'error');
        }
    }

    async loadStorageInfo() {
        try {
            const response = await fetch('/api/storage');
            if (!response.ok) return;
            const data = await response.json();
            const values = {
                storageRoot: data.root,
                storageChats: data.chat_history,
                storageDatasets: data.datasets,
                storageKnowledge: data.knowledge_bases,
                storageVector: data.vector_database,
                storageConfig: data.config,
            };
            Object.entries(values).forEach(([id, value]) => {
                const element = document.getElementById(id);
                if (element) element.textContent = value || '—';
            });
        } catch (error) {
            console.error('Failed to load storage locations:', error);
        }
    }

    async loadSettings() {
        try {
            const response = await fetch('/api/settings');
            if (!response.ok) return;
            const data = await response.json();

            this._providerProfiles = data.provider_profiles || {};
            this._activeProviderConfigured = Boolean(
                data.provider && (
                    this._providerProfiles?.[data.provider]?.configured || data.configured
                )
            );
            const providers = ['openai','anthropic','gemini','deepseek','siliconflow','sdu','glm','kimi','custom'];
            providers.forEach(provider => {
                const profile = this._providerProfiles[provider] || {};
                const keyEl = document.getElementById(provider + 'Key');
                if (keyEl && profile.key) keyEl.placeholder = profile.key;

                const model = profile.model || data[provider + '_model'] || '';
                const modelSelect = document.getElementById(provider + 'Model');
                if (modelSelect && model) {
                    modelSelect.innerHTML = `<option value="${model}">${model}</option>`;
                    modelSelect.style.display = 'block';
                }
                const statusEl = document.getElementById('status-' + provider);
                if (statusEl && model) {
                    statusEl.textContent = `${this._t('embed.currentModel')}: ${model}`;
                }
            });

            const customUrlEl = document.getElementById('customBaseUrl');
            const customProfile = this._providerProfiles.custom || {};
            if (customUrlEl && customProfile.base_url) {
                customUrlEl.value = customProfile.base_url;
            }
            this._renderProviderState(data.provider);
            this._activeThinkingModel = data.model || this._activeThinkingModel;

            const thinkingMode = document.getElementById('thinkingModeSelect');
            if (thinkingMode) thinkingMode.value = data.thinking_enabled ? 'on' : 'off';
            this._renderThinkingEffortOptions(['high', 'max']);
            const thinkingEffort = document.getElementById('thinkingEffortSelect');
            if (thinkingEffort && data.thinking_effort && thinkingEffort.querySelector(`option[value="${data.thinking_effort}"]`)) {
                thinkingEffort.value = data.thinking_effort;
            }
            await this._updateThinkingCapability(data.provider, data.model);

            // 加载 Embedding 模型配置
            await this.loadEmbeddingSettings(data);
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
            const currentProvider = cfg.provider || settingsData?.embedding_provider || 'local';
            this._embeddingProviderConfig = { ...cfg, provider: currentProvider };

            const modelsResp = await fetch('/api/embedding/models');
            const modelsData = modelsResp.ok ? await modelsResp.json() : { models: [] };
            this._embeddingModels = modelsData.models || [];

            const sel = document.getElementById('embeddingModelSelect');
            if (sel && this._embeddingModels.length) {
                sel.innerHTML = '';
                this._embeddingModels.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.id || '';
                    option.textContent = this._embeddingModelName(model);
                    option.selected = model.id === currentModel;
                    sel.appendChild(option);
                });

                sel.onchange = () => {
                    this.updateEmbeddingInfo(this._embeddingModels, sel.value);
                    this._embedSettingsChanged = true;
                };
                this.updateEmbeddingInfo(this._embeddingModels, currentModel);
            }

            const providerEl = document.getElementById('embeddingProviderSelect');
            if (providerEl) {
                providerEl.value = currentProvider;
                providerEl.onchange = () => {
                    const provider = providerEl.value === 'hf_api' ? 'hf_api' : 'local';
                    this._embeddingProviderConfig = {
                        ...this._embeddingProviderConfig,
                        provider,
                    };
                    this._updateEmbeddingProviderUI(provider, this._embeddingProviderConfig);
                    this.updateEmbeddingInfo(this._embeddingModels || [], sel?.value || currentModel);
                    this._embedSettingsChanged = true;
                };
            }
            const clearTokenBtn = document.getElementById('clearEmbeddingHfToken');
            if (clearTokenBtn) clearTokenBtn.onclick = () => this.clearHfToken();
            this._updateEmbeddingProviderUI(currentProvider, this._embeddingProviderConfig);

            const hfModelInput = document.getElementById('embeddingHfModelId');
            if (hfModelInput) {
                hfModelInput.value = currentProvider === 'hf_api' ? currentModel : '';
            }

            const pathInput = document.getElementById('embedModelPathInput');
            if (pathInput) {
                const activePath = (cfg.model_paths || {})[currentModel] || '';
                pathInput.value = activePath;
            }
            if (sel?.value) {
                this.updateEmbeddingInfo(this._embeddingModels || [], sel.value);
            }
        } catch (error) {
            console.error('Failed to load embedding settings:', error);
        }
    }

    _getEmbeddingProvider() {
        const value = document.getElementById('embeddingProviderSelect')?.value;
        return value === 'hf_api' ? 'hf_api' : 'local';
    }

    _updateEmbeddingProviderUI(provider, cfg = {}) {
        const isRemote = provider === 'hf_api';
        const localControls = document.getElementById('embeddingLocalPathControls');
        const customSection = document.getElementById('embeddingCustomLocalSection');
        const hintEl = document.getElementById('embeddingProviderHint');
        const statusEl = document.getElementById('embeddingProviderStatus');
        const tokenControls = document.getElementById('embeddingHfTokenControls');
        const tokenInput = document.getElementById('embeddingHfToken');
        const hfModelControls = document.getElementById('embeddingHfModelControls');

        if (localControls) localControls.style.display = isRemote ? 'none' : 'flex';
        if (customSection) customSection.style.display = isRemote ? 'none' : '';
        if (tokenControls) tokenControls.style.display = isRemote ? 'block' : 'none';
        if (hfModelControls) hfModelControls.style.display = isRemote ? 'flex' : 'none';
        if (tokenInput) {
            tokenInput.placeholder = cfg.hf_token_masked
                ? `${this._t('settings.hfTokenDetected')}: ${cfg.hf_token_masked}`
                : this._t('settings.hfTokenPlaceholder');
        }
        if (hintEl) {
            hintEl.textContent = this._t(isRemote ? 'settings.embeddingHfApiHint' : 'settings.embeddingLocalHint');
        }
        if (statusEl) {
            if (isRemote) {
                const configured = cfg.hf_token_configured === true;
                statusEl.textContent = this._t(configured ? 'settings.hfTokenDetected' : 'settings.hfTokenMissing');
                statusEl.className = `embed-status ${configured ? 'ok' : 'error'}`;
            } else {
                statusEl.textContent = this._t('settings.embeddingLocalReady');
                statusEl.className = 'embed-status ok';
            }
        }
    }

    async clearHfToken() {
        const current = this._embeddingProviderConfig || {};
        const modelId = document.getElementById('embeddingModelSelect')?.value || current.model_name;
        const provider = this._getEmbeddingProvider();
        if (!modelId) return;

        try {
            const resp = await fetch('/api/embedding/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model_name: modelId,
                    model_dimension: current.model_dimension,
                    normalize: current.normalize,
                    provider,
                    local_only: provider === 'local',
                    model_paths: current.model_paths || {},
                    custom_models: current.custom_models || [],
                    clear_hf_token: true,
                }),
            });
            const data = await resp.json();
            if (!resp.ok || !data.success) {
                this.showNotification(data.detail || data.message || this._t('notify.saveFailed'), 'error');
                return;
            }
            const tokenInput = document.getElementById('embeddingHfToken');
            if (tokenInput) tokenInput.value = '';
            this._embeddingProviderConfig = { ...current, ...data, hf_token_configured: false, hf_token_masked: '' };
            this._updateEmbeddingProviderUI(provider, this._embeddingProviderConfig);
            this.updateEmbeddingInfo(this._embeddingModels || [], modelId);
            this._embedSettingsChanged = false;
            this.showNotification(this._t('settings.hfTokenCleared'), 'success');
        } catch (error) {
            this.showNotification(error.message || this._t('notify.saveFailed'), 'error');
        }
    }

    _embeddingModelName(model) {
        const keys = {
            'sentence-transformers/all-MiniLM-L6-v2': 'embed.model.minilmName',
            'BAAI/bge-base-en-v1.5': 'embed.model.bgeBaseName',
            'BAAI/bge-large-en-v1.5': 'embed.model.bgeLargeName',
            'sentence-transformers/all-mpnet-base-v2': 'embed.model.mpnetName',
        };
        const key = keys[model?.id];
        return key ? this._t(key) : (model?.name || model?.id || '');
    }

    _embeddingModelDescription(model) {
        const keys = {
            'sentence-transformers/all-MiniLM-L6-v2': 'embed.model.minilmDesc',
            'BAAI/bge-base-en-v1.5': 'embed.model.bgeBaseDesc',
            'BAAI/bge-large-en-v1.5': 'embed.model.bgeLargeDesc',
            'sentence-transformers/all-mpnet-base-v2': 'embed.model.mpnetDesc',
        };
        const key = keys[model?.id];
        return key ? this._t(key) : (model?.description || '');
    }

    updateEmbeddingInfo(models, selectedId) {
        const model = models.find(m => m.id === selectedId);
        if (!model) return;
        const provider = this._getEmbeddingProvider();
        const isRemote = provider === 'hf_api';

        const nameEl = document.getElementById('embedModelName');
        const dimEl = document.getElementById('embedModelDim');
        const descEl = document.getElementById('embedModelDesc');
        const statusEl = document.getElementById('embedModelStatus');
        const warnEl = document.getElementById('embedRebuildWarning');
        const sizeEl = document.getElementById('embedModelSize');
        const pathEl = document.getElementById('embedModelPath');
        const downloadBtn = document.getElementById('embedDownloadBtn');

        if (nameEl) nameEl.textContent = this._embeddingModelName(model);
        if (dimEl) dimEl.textContent = (model.dimension || '-') + this._t('embed.dimensionSuffix');
        if (descEl) descEl.textContent = this._embeddingModelDescription(model);
        if (sizeEl) sizeEl.textContent = `${this._t('embed.modelSize')}: ${model.size || '-'}`;
        if (pathEl) {
            if (isRemote) {
                pathEl.textContent = this._t('embed.onlineModel');
            } else if (model.path) {
                pathEl.textContent = `${this._t('embed.localPath')}: ${model.path}`;
            } else if (model.path_required) {
                pathEl.textContent = this._t('embed.pathRequiredHelp');
            } else if (model.builtin) {
                pathEl.textContent = this._t('embed.builtinPath');
            } else {
                pathEl.textContent = this._t('embed.downloadAvailable');
            }
        }

        const hasLocal = !!(model.builtin || model.path);
        const remoteReady = this._embeddingProviderConfig?.hf_token_configured === true;
        if (isRemote) {
            if (statusEl) {
                statusEl.textContent = this._t(remoteReady ? 'embed.onlineAvailable' : 'embed.onlineTokenMissing');
                statusEl.className = `embed-status ${remoteReady ? 'ok' : 'error'}`;
            }
        } else if (model.path_required && !model.path) {
            if (statusEl) { statusEl.textContent = this._t('embed.pathRequired'); statusEl.className = 'embed-status error'; }
        } else if (hasLocal) {
            if (statusEl) { statusEl.textContent = this._t('embed.localAvailable'); statusEl.className = 'embed-status ok'; }
        } else {
            if (statusEl) { statusEl.textContent = this._t('embed.needsDownload'); statusEl.className = 'embed-status'; }
        }

        const pathInput = document.getElementById('embedModelPathInput');
        if (pathInput) pathInput.value = model.path || '';
        if (downloadBtn) {
            const canDownload = !isRemote && !model.builtin && !model.path;
            downloadBtn.style.display = canDownload ? 'inline-flex' : 'none';
        }

        // 如果选择了默认模型，隐藏警告
        if (warnEl) {
            warnEl.style.display = (model.default && !isRemote) ? 'none' : 'flex';
            const warningText = warnEl.querySelector('span');
            if (warningText) warningText.textContent = this._t('embed.reindexWarning');
        }
    }

    async saveEmbeddingSettings() {
        const sel = document.getElementById('embeddingModelSelect');
        const pathInput = document.getElementById('embedModelPathInput');
        const modelId = sel?.value;
        const modelMeta = this._getEmbeddingMetaById(modelId);
        if (!modelId) return { success: false };

        try {
            const cfgResp = await fetch('/api/embedding/config');
            const cfg = cfgResp.ok ? await cfgResp.json() : {};
            const modelPaths = { ...(cfg.model_paths || {}) };
            const p = (pathInput?.value || '').trim();
            if (p) modelPaths[modelId] = p;
            const provider = this._getEmbeddingProvider();
            const hfTokenInput = (document.getElementById('embeddingHfToken')?.value || '').trim();

            const resp = await fetch('/api/embedding/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model_name: modelId,
                    model_dimension: Number.isInteger(modelMeta?.dimension) ? modelMeta.dimension : cfg.model_dimension,
                    normalize: cfg.normalize,
                    provider,
                    local_only: provider === 'local',
                    model_paths: modelPaths,
                    custom_models: cfg.custom_models || [],
                    ...(hfTokenInput ? { hf_token: hfTokenInput } : {}),
                }),
            });
            const data = await resp.json();
            if (!resp.ok || !data.success) {
                this.showNotification(data.detail || data.message || this._t('notify.saveFailed'), 'error');
                return { success: false, ...data };
            }
            this._embedSettingsChanged = false;
            if (hfTokenInput) {
                const tokenInput = document.getElementById('embeddingHfToken');
                if (tokenInput) tokenInput.value = '';
            }
            this._embeddingProviderConfig = { ...cfg, ...data, provider };
            this._updateEmbeddingProviderUI(provider, this._embeddingProviderConfig);
            this.updateEmbeddingInfo(this._embeddingModels || [], modelId);
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
        const provider = this._getEmbeddingProvider();
        if (!modelId) return;

        if (statusEl) { statusEl.textContent = this._t('embed.testing'); statusEl.className = 'embed-status testing'; }

        try {
            const resp = await fetch('/api/embedding/test', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model_name: modelId,
                    local_path: provider === 'local' ? localPath : '',
                    provider,
                    normalize: this._embeddingProviderConfig?.normalize,
                }),
            });
            const data = await resp.json();

            if (data.success) {
                const dimension = Number.isFinite(Number(data.dimension)) ? ` (${data.dimension}D)` : '';
                if (statusEl) {
                    statusEl.textContent = '✓ ' + this._t('embed.testSuccess') + dimension + ` (${data.time_ms}ms)`;
                    statusEl.className = 'embed-status ok';
                }
            } else {
                if (statusEl) {
                    statusEl.textContent = '✕ ' + (data.message || this._t('embed.testFailed'));
                    statusEl.className = 'embed-status error';
                }
            }
        } catch (error) {
            if (statusEl) { statusEl.textContent = this._t('embed.testFailed') + ': ' + error.message; statusEl.className = 'embed-status error'; }
        }
    }

    async fetchModels(provider) {
        const keyEl = document.getElementById(provider + 'Key');
        const sel   = document.getElementById(provider + 'Model');
        const customEl = document.getElementById(provider + 'ModelCustom');
        const statusEl = document.getElementById('status-' + provider);
        if (!keyEl || !sel) return;
        const apiKey = keyEl.value.trim();
        if (!apiKey) return;
        if (statusEl) statusEl.innerHTML = `<span style="color:#9aa0ac;font-size:.8rem">${this._t('app.fetchingModels')}</span>`;

        // Always show custom model input field
        if (customEl) customEl.style.display = 'block';

        try {
            const r = await fetch('/api/settings/models', {
                method: 'POST',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify({provider, api_key: apiKey})
            });
            const d = await r.json();
            if (!r.ok) {
                if (statusEl) statusEl.innerHTML = `<span style="color:#ef4444;font-size:.8rem">${d.detail||this._t('app.fetchFailed')}</span>`;
                return;
            }
            const models = d.models || [];
            this._modelCapabilities[provider] = d.model_capabilities || {};
            if (models.length) {
                sel.innerHTML = models.map((m,i) => `<option value="${m}">${m}</option>`).join('');
                sel.style.display = 'block';
                await this._updateThinkingCapability(provider, sel.value, false);
            } else {
                if (statusEl) statusEl.innerHTML = `<span style="color:#9aa0ac;font-size:.8rem">${this._t('app.noModels')}</span>`;
            }
            if (statusEl && models.length) statusEl.innerHTML = `<span style="color:#34d399;font-size:.8rem">✓ ${models.length} ${this._t('app.modelsCountSuffix')}</span>`;
        } catch(e) {
            if (statusEl) statusEl.innerHTML = `<span style="color:#ef4444;font-size:.8rem">${this._t('app.fetchFailed')}</span>`;
        }
    }

    /** Fetch models from a completely custom OpenAI-compatible endpoint (e.g. a6api). */
    async fetchModelsCustom() {
        const baseUrl = document.getElementById('customBaseUrl')?.value.trim();
        const apiKey  = document.getElementById('customKey')?.value.trim();
        const sel     = document.getElementById('customModel');
        const customEl = document.getElementById('customModelCustom');
        const statusEl = document.getElementById('status-custom');

        if (!baseUrl) {
            if (statusEl) statusEl.innerHTML = `<span style="color:#ef4444;font-size:.8rem">${this._t('app.customUrlRequired')}</span>`;
            return;
        }
        if (!apiKey) {
            if (statusEl) statusEl.innerHTML = `<span style="color:#ef4444;font-size:.8rem">${this._t('app.customKeyRequired')}</span>`;
            return;
        }

        if (statusEl) statusEl.innerHTML = `<span style="color:#9aa0ac;font-size:.8rem">${this._t('app.fetchingModels')}</span>`;
        if (customEl) customEl.style.display = 'block';

        try {
            const r = await fetch('/api/settings/models-custom', {
                method: 'POST',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify({base_url: baseUrl, api_key: apiKey})
            });
            const d = await r.json();
            if (!r.ok) {
                if (statusEl) statusEl.innerHTML = `<span style="color:#ef4444;font-size:.8rem">${d.detail||this._t('app.fetchFailed')}</span>`;
                return;
            }
            const models = d.models || [];
            this._modelCapabilities.custom = d.model_capabilities || {};
            if (models.length) {
                sel.innerHTML = models.map((m,i) => `<option value="${m}">${m}</option>`).join('');
                sel.style.display = 'block';
                await this._updateThinkingCapability('custom', sel.value, false);
            } else {
                if (statusEl) statusEl.innerHTML = `<span style="color:#9aa0ac;font-size:.8rem">${this._t('app.noModels')}</span>`;
            }
            if (statusEl && models.length) statusEl.innerHTML = `<span style="color:#34d399;font-size:.8rem">✓ ${models.length} ${this._t('app.modelsCountSuffix')}</span>`;
        } catch(e) {
            if (statusEl) statusEl.innerHTML = `<span style="color:#ef4444;font-size:.8rem">${this._t('app.fetchFailed')}</span>`;
        }
    }

    /** Update the model indicator badge in the chat header. */
    _updateModelBadge(provider, model) {
        const badge = document.getElementById('activeModelBadge');
        if (!badge) return;
        if (provider && model) {
            const providerLabels = {
                openai: 'OpenAI', anthropic: 'Anthropic', gemini: 'Gemini',
                deepseek: 'DeepSeek', siliconflow: 'SiliconFlow', glm: 'GLM',
                kimi: 'Kimi', sdu: 'SDU-AI', custom: 'Custom API', ollama: 'Ollama'
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
        const sduKey = document.getElementById('sduKey')?.value.trim();
        const glmKey = document.getElementById('glmKey')?.value.trim();
        const kimiKey = document.getElementById('kimiKey')?.value.trim();
        const customKey = document.getElementById('customKey')?.value.trim();
        const customBaseUrl = document.getElementById('customBaseUrl')?.value.trim();
        // 从下拉菜单读取用户选择的模型（拉取列表后由用户选定）
        const openaiModel = this._getProviderModel('openai');
        const anthropicModel = this._getProviderModel('anthropic');
        const geminiModel = this._getProviderModel('gemini');
        const deepseekModel = this._getProviderModel('deepseek');
        const siliconflowModel = this._getProviderModel('siliconflow');
        const sduModel = this._getProviderModel('sdu');
        const glmModel = this._getProviderModel('glm');
        const kimiModel = this._getProviderModel('kimi');
        const customModel = this._getProviderModel('custom');

        const settings = {
            provider: this.selectedProvider,
            openai_key: openaiKey,
            anthropic_key: anthropicKey,
            gemini_key: geminiKey,
            deepseek_key: deepseekKey,
            siliconflow_key: siliconflowKey,
            sdu_key: sduKey,
            glm_key: glmKey,
            kimi_key: kimiKey,
            custom_key: customKey,
            custom_base_url: customBaseUrl,
            openai_model: openaiModel,
            anthropic_model: anthropicModel,
            gemini_model: geminiModel,
            deepseek_model: deepseekModel,
            siliconflow_model: siliconflowModel,
            sdu_model: sduModel,
            glm_model: glmModel,
            kimi_model: kimiModel,
            custom_model: customModel,
            thinking_enabled: this._thinkingEnabledFromUi(),
            thinking_effort: this._thinkingEffortFromUi(),
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
                this.showConnectionStatus('error', err.detail || this._t('notify.saveFailed'));
                throw new Error(err.detail || this._t('notify.saveFailed'));
            }

            const result = await response.json();

            ['openaiKey', 'anthropicKey', 'geminiKey', 'deepseekKey', 'siliconflowKey', 'sduKey', 'glmKey', 'kimiKey', 'customKey'].forEach(id => {
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

            // 显示连接状态弹窗
            const connTest = result.connection_test;
            if (connTest) {
                if (connTest.success) {
                    this.showConnectionStatus('success', connTest.message || this._t('app.connectSuccess'));
                } else {
                    this.showConnectionStatus('error', connTest.message || this._t('app.connectError'));
                }
            } else {
                this.testConnectionWithFeedback();
            }

        } catch (error) {
            console.error('Save settings failed:', error);
            this.showNotification(error.message || t('notify.saveFailed'), 'error');
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

        const labels = { testing: this._t('app.connectTesting'), success: this._t('app.connectSuccess'), error: this._t('app.connectError') };
        const colors = { testing: '#3b82f6', success: '#10b981', error: '#ef4444' };

        if (type === 'testing') {
            card.innerHTML =
                '<div style="width:64px;height:64px;position:relative">' +
                '<svg viewBox="0 0 64 64" width="64" height="64" style="animation:spin 1s linear infinite;display:block">' +
                '<circle cx="32" cy="32" r="28" fill="none" stroke="#2d3348" stroke-width="5"/>' +
                '<circle cx="32" cy="32" r="28" fill="none" stroke="#3b82f6" stroke-width="5" stroke-dasharray="44 132" stroke-linecap="round"/>' +
                '</svg></div>' +
                `<p style="margin:0;font-size:1.1rem;font-weight:600;color:#e8eaed">${this._t('app.connectTesting')}</p>` +
                `<p style="margin:0;font-size:0.85rem;color:#8ab4f8">${this._t('app.verifyApiKey')}</p>`;
        } else if (type === 'success') {
            card.innerHTML =
                '<div style="width:64px;height:64px;border-radius:50%;background:#10b981;display:flex;align-items:center;justify-content:center">' +
                '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>' +
                '</div>' +
                `<p style="margin:0;font-size:1.1rem;font-weight:600;color:#e8eaed">${this._t('app.connectSuccess')}</p>` +
                '<p style="margin:0;font-size:0.82rem;color:#6ee7b7;text-align:center;max-width:240px;word-break:break-all">' + (message || '') + '</p>';
            setTimeout(function() { if (overlay.parentNode) overlay.remove(); }, 1500);
        } else {
            card.innerHTML =
                '<div style="width:64px;height:64px;border-radius:50%;background:#ef4444;display:flex;align-items:center;justify-content:center">' +
                '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>' +
                '</div>' +
                `<p style="margin:0;font-size:1.1rem;font-weight:600;color:#e8eaed">${this._t('app.connectError')}</p>` +
                '<p style="margin:0;font-size:0.82rem;color:#fca5a5;text-align:center;max-width:240px;word-break:break-all">' + (message || '') + '</p>' +
                `<button onclick="document.getElementById('conn-modal-overlay').remove()" style="padding:8px 24px;border-radius:8px;border:1px solid #ef4444;background:transparent;color:#ef4444;cursor:pointer;font-size:0.875rem">${this._t('app.close')}</button>`;
        }

        overlay.appendChild(card);
        document.body.appendChild(overlay);
        return overlay;
    }

    async testConnectionWithFeedback(opts = null) {
        const testingToast = this.showConnectionStatus('testing', '');
        try {
            const body = opts && typeof opts === 'object' ? { ...opts } : {};
            const resp = await fetch('/api/settings/test-connection', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });
            testingToast.remove();
            if (resp.ok) {
                const data = await resp.json();
                this.showConnectionStatus('success', data.message || this._t('app.connectSuccess'));
            } else {
                const err = await resp.json().catch(() => ({}));
                this.showConnectionStatus('error', err.detail || this._t('app.connectError'));
            }
        } catch (e) {
            testingToast.remove();
            this.showConnectionStatus('error', e.message || this._t('error.networkError'));
        }
    }

    // ========== 选填 ==========
    changeLanguage(lang) {
        this.currentLanguage = lang;
        localStorage.setItem('e2seq_language', lang);
        document.documentElement.lang = lang;
        this.applyLanguage();
        // Re-render dynamic regions whose empty/loading states are not marked
        // with data-i18n attributes.
        void this.loadChatHistory();
        this.showNotification(t('notify.languageChanged'), 'success');
    }

    /** Localised text lookup (uses global t() with current language). */
    _t(key) {
        if (typeof t === 'function') return t(key, this.currentLanguage);
        return key;
    }

    applyLanguage() {
        document.documentElement.lang = this.currentLanguage;
        // 处理 data-i18n 属性（用于文本内容）
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = t(key, this.currentLanguage);

            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                if (element.placeholder !== undefined) {
                    element.placeholder = translation;
                }
            } else {
                if (element.children.length === 0) {
                    element.textContent = translation;
                } else {
                    const textNode = Array.from(element.childNodes).find(node => node.nodeType === Node.TEXT_NODE);
                    if (textNode) textNode.textContent = translation;
                }
            }
        });

        // 处理 data-i18n-placeholder 属性（用于占位符文本）
        document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
            const key = element.getAttribute('data-i18n-placeholder');
            const translation = t(key, this.currentLanguage);
            if (translation && translation !== key) {
                element.placeholder = translation;
            }
        });

        // 处理 data-i18n-title 属性（用于工具提示）
        document.querySelectorAll('[data-i18n-title]').forEach(element => {
            const key = element.getAttribute('data-i18n-title');
            const translation = t(key, this.currentLanguage);
            if (translation && translation !== key) {
                element.title = translation;
            }
        });

        // 必填?
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
                span.textContent = t(suggestions[index], this.currentLanguage);
            }
        });

        // 必填?
        if (this.currentPage === 'knowledgeBase') {
            this.loadBuiltinDatabases();
            this.loadCustomDatabases();
        }

        // 必填
        const chartTypes = ['umap', 'violin', 'heatmap', 'volcano', 'bubble', 'network', 'chord'];
        document.querySelectorAll('.chart-type-btn').forEach((btn, index) => {
            if (index < chartTypes.length) {
                btn.textContent = t(`charts.${chartTypes[index]}`, this.currentLanguage);
            }
        });

        // 必填必填选填?
        document.querySelectorAll('input[name="language"]').forEach(radio => {
            radio.checked = (radio.value === this.currentLanguage);
        });

        this._renderProviderState(this.selectedProvider);
        const embeddingProviderSelect = document.getElementById('embeddingProviderSelect');
        if (embeddingProviderSelect) {
            this._updateEmbeddingProviderUI(
                this._getEmbeddingProvider(),
                this._embeddingProviderConfig || {}
            );
        }
        const embeddingSelect = document.getElementById('embeddingModelSelect');
        if (embeddingSelect?.value && this._embeddingModels?.length) {
            embeddingSelect.innerHTML = this._embeddingModels.map(model =>
                `<option value="${model.id}"${model.id === embeddingSelect.value ? ' selected' : ''}>${this._embeddingModelName(model)}</option>`
            ).join('');
            this.updateEmbeddingInfo(this._embeddingModels, embeddingSelect.value);
        }

        // 必填?
        document.title = t('chat.title', this.currentLanguage) + ' - Easy to Chat with Sequencing';
        if (this.selectedProvider && this._activeThinkingModel) {
            void this._updateThinkingCapability(this.selectedProvider, this._activeThinkingModel, false);
        }
    }

    // ========== 选填 ==========
    handleInputChange(value) {
        const sendBtn = document.getElementById('sendBtn');
        if (sendBtn) {
            sendBtn.disabled = this._chatInputLocked || !value.trim();
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

        if (this._chatInputLocked || !message || this.isProcessing) return;

        const requestChatId = this.currentChatId || 'default';
        const requestToken = ++this._chatRequestToken;
        const isCurrentRequest = () => (
            this._chatRequestToken === requestToken &&
            this.currentChatId === requestChatId
        );

        const greetingModule = document.getElementById('greetingModule');
        if (greetingModule) {
            greetingModule.style.display = 'none';
        }

        this.addMessage('user', message);
        messageInput.value = '';
        this.handleInputChange('');
        messageInput.style.height = 'auto';

        this.isProcessing = true;

        // Add loading bubble with progress display
        const loadingId = this.addMessage('assistant', '', true);
        const sessionId = requestChatId;

        // Start progress polling
        // The progress endpoint is session-scoped and deliberately retains
        // completed analysis history. Start this question's progress cursor
        // at the current end so an old modeling/RAG log is not replayed in a
        // new answer bubble (which previously looked like duplicate work).
        // The server keeps a bounded tail (currently 60 entries) rather than
        // an ever-growing progress history.  Comparing only message counts
        // therefore freezes the UI as soon as that tail is full: new entries
        // replace old entries without increasing `messages.length`.  Keep a
        // content snapshot instead, so the progress bubble continues to
        // update while long Agent RAG retrieval is running.
        let lastProgressSnapshot = '';
        try {
            const initialProgress = await fetch(`/api/progress/${sessionId}`);
            if (initialProgress.ok) {
                const initialData = await initialProgress.json();
                lastProgressSnapshot = (initialData.messages || []).join('\n');
            }
        } catch (_) {}
        const progressEl = document.getElementById(loadingId)?.querySelector('.progress-log');
        const pollProgress = async () => {
            if (!isCurrentRequest()) return;
            try {
                const pr = await fetch(`/api/progress/${sessionId}`);
                if (!isCurrentRequest()) return;
                if (pr.ok) {
                    const pd = await pr.json();
                    const msgs = pd.messages || [];
                    const progressSnapshot = msgs.join('\n');
                    if (progressSnapshot !== lastProgressSnapshot) {
                        lastProgressSnapshot = progressSnapshot;
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
        // Keep live progress responsive without creating a request storm while
        // a large RAG batch is running.  The bulk panel itself polls at 2 s.
        const progressTimer = setInterval(pollProgress, 1500);

        try {
            const bulkSelectedGenes = window.analysisPanel?.getBulkSelectedGenes?.() || [];
            const chatPayload = {
                message: message,
                chat_id: requestChatId,
            };
            if (bulkSelectedGenes.length) chatPayload.bulk_selected_genes = bulkSelectedGenes;

            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(chatPayload),
            });

            clearInterval(progressTimer);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                const detail = errorData.detail || '';
                const message = detail === 'bulk_analysis_not_ready'
                    ? this._t('bulk.waitAnalysis')
                    : detail || t('error.chatFailed');
                throw new Error(message);
            }

            const data = await response.json();
            if (!isCurrentRequest()) return;
            this.removeMessage(loadingId);
            this.addMessage('assistant', data.response, false, {
                llm_usage: data.data?.llm_usage || null,
                bulk_timing: data.data?.bulk_timing || null,
                answer_language: /[\u3400-\u9fff]/.test(message) ? 'zh' : 'en',
            });

            // Refresh the visible estimate after every completed answer so the
            // user sees measured/estimated model-token usage without reopening
            // the upload dialog.
            void window.analysisPanel?._loadRagCostEstimate?.();

            if (data.plots) {
                this.displayPlots(data.plots);
            }

            // NOTE: do NOT overwrite this.currentChatId with data.chat_id.
            // The frontend UUID is the authoritative session ID; the server
            // echoes it back but we must not let a stale server value replace
            // a freshly-generated chat ID (which would merge conversations).

            // Refresh history after new message
            this.loadChatHistory();

        } catch (error) {
            clearInterval(progressTimer);
            if (!isCurrentRequest()) return;
            console.error('sendMessage error:', error);
            this.removeMessage(loadingId);
            this.addMessage('assistant', error?.message || t('error.chatFailed'));
        } finally {
            if (isCurrentRequest()) this.isProcessing = false;
        }
    }

    addMessage(role, content, isLoading = false, metadata = null) {
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
                <div class="loading-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
                <div class="progress-log"></div>
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

        if (role === 'assistant' && !isLoading && metadata) {
            const usage = metadata.llm_usage;
            const timing = metadata.bulk_timing;
            const answerLanguage = metadata.answer_language === 'en' ? 'en' : 'zh';
            if (usage || timing) {
                const meta = document.createElement('div');
                meta.className = 'message-meta';
                const lines = [];
                if (usage) {
                    let usageText = this._t(answerLanguage === 'en' ? 'chat.usageEn' : 'chat.usage')
                        .replace('{provider}', String(usage.provider || 'unknown'))
                        .replace('{model}', String(usage.model || 'unknown'))
                        .replace('{elapsed}', String(usage.elapsed_seconds ?? usage.latency_seconds ?? 0))
                        .replace('{requests}', String(usage.requests ?? 0))
                        .replace('{prompt}', String(usage.prompt_tokens ?? 0))
                        .replace('{completion}', String(usage.completion_tokens ?? 0))
                        .replace('{total}', String(usage.total_tokens ?? 0));
                    if (!usage.token_usage_available) usageText += ' ' + this._t('chat.usageUnavailable');
                    lines.push(usageText);
                }
                if (timing) {
                    const modeling = timing.statistical_model_seconds ?? timing.analysis_elapsed_seconds;
                    const handoff = timing.question_handoff_seconds ?? timing.rag_elapsed_seconds;
                    if (modeling != null || handoff != null) {
                        lines.push(this._t(answerLanguage === 'en' ? 'chat.bulkTimingEn' : 'chat.bulkTiming')
                            .replace('{modeling}', String(modeling ?? 0))
                            .replace('{handoff}', String(handoff ?? 0)));
                    }
                }
                meta.textContent = lines.join(' · ');
                messageContent.appendChild(meta);
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
        this._chatRequestToken += 1;
        this.isProcessing = false;
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
        window.analysisPanel?.onChatChanged?.();
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
                chatList.innerHTML = `<div class="empty-state-small">${this._t('history.empty')}</div>`;
                return;
            }

            chats.forEach(chat => {
                const chatItem = document.createElement('div');
                chatItem.className = 'chat-item';
                // 格式化时间
                let timeStr = '';
                if (chat.updated_at) {
                    const d = new Date(chat.updated_at + 'Z');
                    const locale = this.currentLanguage.startsWith('en') ? 'en-US' : 'zh-CN';
                    timeStr = d.toLocaleString(locale, {month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'});
                }
                chatItem.innerHTML =
                    '<div class="chat-item-body">' +
                    '<span class="chat-item-title">' + (chat.title || this._t('history.newChat')) + '</span>' +
                    '<span class="chat-item-time">' + timeStr + '</span>' +
                    '</div>' +
                    `<button class="chat-item-del" title="${this._t('history.delete')}" data-chat-del="${chat.id}">×</button>`;
                chatItem.addEventListener('click', (e) => {
                    const delBtn = e.target.closest('[data-chat-del]');
                    if (delBtn) { e.stopPropagation(); this.deleteChat(delBtn.dataset.chatDel); return; }
                    this.navigateToChat();
                    this.loadChat(chat.id);
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
            await window.analysisPanel?.onChatChanged?.();
        } catch (error) {
            console.error('loadChat error:', error);
        }
    }

    async deleteChat(chatId) {
        if (!confirm(this._t('history.deleteConfirm'))) return;
        try {
            await fetch(`/api/chats/${chatId}`, { method: 'DELETE' });
            if (this.currentChatId === chatId) {
                this.createNewChat();
            }
            this.loadChatHistory();
        } catch (e) {
            console.error('deleteChat error:', e);
        }
    }

    async clearAllHistory() {
        if (!confirm(this._t('history.clearConfirm'))) return;
        try {
            const r = await fetch('/api/chats', { method: 'DELETE' });
            if (!r.ok) throw new Error(this._t('history.clearFailed'));
            const data = await r.json();
            // Clear the sidebar list immediately
            const chatList = document.getElementById('chatList');
            if (chatList) chatList.innerHTML = `<div class="empty-state-small">${this._t('history.empty')}</div>`;
            // If the kept session is not the current one, switch to it
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
                    ? this._t('history.cleared')
                        .replace('{count}', String(deleted))
                        .replace('{kept}', kept ? this._t('history.keptOne') : '')
                    : this._t('history.nothingToClear'),
                'success'
            );
        } catch (e) {
            console.error('clearAllHistory error:', e);
            this.showNotification(`${this._t('history.clearFailed')}: ${e.message}`, 'error');
        }
    }

    handleAttachment(fileArg) {
        if (fileArg) {
            this.uploadFile(fileArg);
            return;
        }
        // 统一进入右侧分析面板（顶部切换单细胞/表格）
        if (window.analysisPanel) {
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
        }
    }

    // 关闭上传抽屉
    closeUploadDrawer() {
        const drawer = document.getElementById('uploadDrawer');
        const overlay = document.getElementById('drawerOverlay');
        if (drawer) drawer.classList.remove('active');
        if (overlay) overlay.classList.remove('active');
    }

    // 打开表格配置抽屉
    openTableDrawer() {
        const drawer = document.getElementById('tableUploadDrawer');
        const overlay = document.getElementById('drawerOverlay');
        if (drawer) {
            drawer.classList.add('active');
            if (overlay) overlay.classList.add('active');
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
        if (type === 'table' && window.analysisPanel) {
            window.analysisPanel.switchMode('table');
            window.analysisPanel.open();
            window.analysisPanel.openBulkDialog();
            return;
        }
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
                    if (window.analysisPanel) {
                        window.analysisPanel.switchMode('table');
                        window.analysisPanel.open();
                        await window.analysisPanel.openBulkDialog();
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
        const topGenesEl = document.getElementById('tableTopGenes');
        const errorEl = document.getElementById('tableUploadError');

        // 显示抽屉
        fileNameEl.textContent = file.name;
        fileInfoEl.textContent = this._t('analysisPanel.reading').replace('{file}', file.name);
        errorEl.style.display = 'none';
        geneColEl.innerHTML = `<option value="">${this._t('embed.loading')}</option>`;
        groupColEl.innerHTML = `<option value="">${this._t('tableConfig.notUsed')}</option>`;
        exprColEl.innerHTML = `<option value="">${this._t('analysisPanel.selectColumn')}</option>`;
        sigColEl.innerHTML = `<option value="">${this._t('tableConfig.notUsed')}</option>`;
        if (topGenesEl) topGenesEl.value = '0';
        drawer.classList.add('active');
        document.getElementById('drawerOverlay')?.classList.add('active');

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
            if (!response.ok) throw new Error(data.detail || this._t('analysisPanel.uploadFailed'));

            fileInfoEl.textContent = this._t('analysisPanel.fileSummary')
                .replace('{file}', file.name)
                .replace('{rows}', String(data.n_rows))
                .replace('{cols}', String(data.columns.length));

            // 填充所有列选择
            const cols = data.columns || [];
            const allOptions = cols.map(c => `<option value="${c}">${c}</option>`).join('');

            geneColEl.innerHTML = `<option value="">${this._t('analysisPanel.selectColumn')}</option>` + allOptions;
            groupColEl.innerHTML = `<option value="">${this._t('tableConfig.notUsed')}</option>` + allOptions;
            exprColEl.innerHTML = `<option value="">${this._t('analysisPanel.selectColumn')}</option>` + allOptions;
            sigColEl.innerHTML = `<option value="">${this._t('tableConfig.notUsed')}</option>` + allOptions;

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
        const topGenesRaw = document.getElementById('tableTopGenes')?.value || '0';
        const topGenesParsed = Number.parseInt(topGenesRaw, 10);
        const topGenes = Number.isFinite(topGenesParsed) ? Math.max(0, topGenesParsed) : 0;
        const errorEl = document.getElementById('tableUploadError');

        // 收集启用的 API
        const enabledApis = [];
        ['apiUniprot','apiMygene','apiEnsembl','apiChembl','apiOpentargets',
         'apiClinvar','apiReactome','apiPubmed','apiQuickgo','apiEuropepmc',
         'apiGtex','apiHpa','apiGwas','apiCivic','apiAlliance',
         'apiCbioportal','apiOmnipath','apiIntact',
         'apiHumanbase','apiClinicaltrials'].forEach(id => {
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
            errorEl.textContent = this._t('analysisPanel.selectFileGene');
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
            if (!response.ok) throw new Error(data.detail || this._t('analysisPanel.configFailed'));

            this.closeTableDrawer();
            this.showNotification(this._t('analysisPanel.tableUploadSuccess').replace('{count}', String(data.n_genes)), 'success');

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
            this.showNotification(this._t('app.uploadingDataset'), 'info');
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const err = await response.json().catch(() => ({}));
                throw new Error(err.detail || t('notify.uploadFailed'));
            }

            const data = await response.json();
            // Do NOT overwrite currentChatId with the server's session_id.
            // The upload endpoint may return a generic session; the frontend
            // UUID must remain the authoritative chat identifier.
            this._pendingUploadData = data;
            // Instead of showing a config modal, refresh the analysis panel
            // and open it so the user can confirm settings there.
            if (window.analysisPanel) {
                window.analysisPanel._colsLoaded = false;
                await window.analysisPanel.checkDataStatus();
                window.analysisPanel.open();
            }
            this.showNotification(this._t('analysisPanel.singleUploadSuccess')
                .replace('{cells}', String(data.cells)).replace('{genes}', String(data.genes)), 'success');
            const greetingModule = document.getElementById('greetingModule');
            if (greetingModule) greetingModule.style.display = 'none';
        } catch (error) {
            console.error('uploadFile error:', error);
            this.showNotification(error.message || t('notify.uploadFailed'), 'error');
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
            grpSel.innerHTML = `<option value="">${this._t('analysisPanel.notUsed')}</option>` +
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
                        value="${v}" placeholder="${this._t('analysisPanel.displayName')}"
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
            newConfirm.textContent = this._t('analysisPanel.analyzing');

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
                    throw new Error(e.detail || this._t('analysisPanel.configFailed'));
                }
                modal.style.display = 'none';
                modal.classList.remove('active');

                this.showNotification(this._t('analysisPanel.datasetConfigured')
                    .replace('{cells}', String(data.cells)).replace('{genes}', String(data.genes)), 'success');

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
                newConfirm.textContent = this._t('datasetConfig.confirm');
            }
        });
    }

    showToolsMenu() {
        console.log('必填');
        // TODO: 必填
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

// 必填必填选填
// ========== Analysis Panel Tab + CSV Logic ==========
(function() {
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
            if (!r.ok) { if (errEl) { errEl.textContent = d.detail || (window.e2seqApp?._t('analysisPanel.uploadFailed') || 'Upload failed'); errEl.style.display = 'block'; } return; }
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
                sel.innerHTML = keepEmpty ? `<option value="">${window.e2seqApp?._t('analysisPanel.notUsed') || '-- Not used --'}</option>` : '';
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
            if (csvInfo) csvInfo.textContent = (window.e2seqApp?._t('analysisPanel.fileSummary') || '{file} · {rows} rows · {cols} columns')
                .replace('{file}', d.filename || file.name)
                .replace('{rows}', String(d.n_rows))
                .replace('{cols}', String(_csvColumns.length));
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
            if (errEl) { errEl.textContent = (window.e2seqApp?._t('analysisPanel.uploadFailed') || 'Upload failed') + ': ' + e.message; errEl.style.display = 'block'; }
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
        if (csvInfo) csvInfo.textContent = window.e2seqApp?._t('analysisPanel.noData') || 'No data loaded';
        const csvClearBtn = document.getElementById('apCsvClearBtn');
        if (csvClearBtn) csvClearBtn.style.display = 'none';
        // Reset selects to placeholder state
        const groupSel = document.getElementById('apCsvGroupCol');
        if (groupSel) { groupSel.innerHTML = `<option value="">${window.e2seqApp?._t('analysisPanel.uploadAfterSelect') || '— Upload a file to populate —'}</option>`; groupSel.disabled = true; }
        const geneSel = document.getElementById('apCsvGeneCol');
        if (geneSel) { geneSel.innerHTML = '<option value="">name / gene_symbol</option>'; geneSel.disabled = true; }
        const exprSel = document.getElementById('apCsvExprCol');
        if (exprSel) { exprSel.innerHTML = '<option value="">log2FC / mean_expr</option>'; exprSel.disabled = true; }
        const sigSel = document.getElementById('apCsvSigCol');
        if (sigSel) { sigSel.innerHTML = `<option value="">${window.e2seqApp?._t('analysisPanel.notUsed') || '— Not Used —'}</option>`; sigSel.disabled = true; }
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
        btn.textContent = window.e2seqApp?._t('analysisPanel.analyzing') || 'Analyzing...';
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
            enabled_apis: Array.from(document.querySelectorAll('#apCsvApiChecks input:checked')).map(el => el.value).filter(v => ['uniprot','mygene','quickgo','ensembl','chembl','pubmed','europepmc','opentargets','clinvar','gtex','hpa','reactome','gwas','civic','alliance','cbioportal','omnipath','intact','humanbase','clinicaltrials'].includes(v)),
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
                if (errEl) { errEl.textContent = d.detail || (window.e2seqApp?._t('analysisPanel.configFailed') || 'Configuration failed'); errEl.style.display = 'block'; }
                btn.disabled = false; btn.innerHTML = origHTML; return;
            }
            const ap = window.analysisPanel;
            if (ap && typeof ap.close === 'function') ap.close();
            const grps = (d.groups || []).join(' / ');
            const summary = (window.e2seqApp?._t('analysisPanel.tableUploadSuccess') || 'Tabular data uploaded: {count} genes')
                .replace('{count}', String(d.n_genes));
            window.e2seqApp?.showNotification(summary + (grps ? ` (${grps})` : ''), 'success');
            const gm = document.getElementById('greetingModule');
            if (gm) gm.style.display = 'none';
            window.e2seqApp?.navigateToChat?.();
            const mi = document.getElementById('messageInput');
            if (mi) { mi.value = ''; mi.focus(); }
        } catch(e) {
            if (errEl) { errEl.textContent = (window.e2seqApp?._t('analysisPanel.requestFailed') || 'Request failed') + ': ' + e.message; errEl.style.display = 'block'; }
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
        if (!confirm(window.e2seqApp?._t('analysisPanel.confirmClear') || 'Are you sure you want to clear the current dataset?')) return;
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
        if (info) info.textContent = window.e2seqApp?._t('analysisPanel.noData') || 'No data loaded';
        const clearBtn = document.getElementById('apClearDataBtn');
        if (clearBtn) clearBtn.style.display = 'none';
        // Reset h5ad selects to '不使用'
        const ctSel = document.getElementById('apCelltypeColSelect');
        if (ctSel) { ctSel.innerHTML = `<option value="">${window.e2seqApp?._t('analysisPanel.notUsed') || '— Not Used —'}</option>`; }
        const grpSel = document.getElementById('apGroupColSelect');
        if (grpSel) { grpSel.innerHTML = `<option value="">${window.e2seqApp?._t('analysisPanel.notUsed') || '— Not Used —'}</option>`; }
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
        window.e2seqApp?.showNotification(window.e2seqApp?._t('analysisPanel.dataCleared') || 'Dataset cleared', 'info');
    };
})();

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

// 必填
const style = document.createElement('style');
style.textContent = `
    .chat-item { display:flex; align-items:center; justify-content:space-between; gap:6px; padding:8px 10px; border-radius:8px; cursor:pointer; transition:background 0.15s; }
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
        margin-top: 10px;
        max-height: 220px;
        overflow-y: auto;
        font-size: 0.78rem;
        font-family: 'Fira Mono', 'Consolas', monospace;
        color: #8ab4f8;
        line-height: 1.7;
        border-left: 2px solid #3b82f633;
        padding-left: 10px;
    }

    .progress-step {
        padding: 1px 0;
        white-space: pre-wrap;
        word-break: break-all;
        animation: fadeInUp 0.2s ease;
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
