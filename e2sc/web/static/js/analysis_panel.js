// ========== Analysis Control Panel ==========

class AnalysisPanel {
    constructor(app) {
        this.app = app;
        this.matrixData = null;
        this.isOpen = false;
        this.availableCols = {}; // col -> [values]
        this._colsLoaded = false; // guard: only populate selectors once per data load
        // _userLabels: persisted user edits — NEVER cleared except on explicit column
        // change or data unload. Survives panel open/close, status polls,
        // and page reloads (backed by localStorage).
        this._userLabels = this._loadLabelsFromStorage();
        this.currentMode = 'singlecell';
        this._dataStatus = { data_loaded: false, data_mode: null };
        this.init();
    }

    /** Persist user label edits to localStorage so they survive page reloads. */
    _saveLabelsToStorage() {
        try {
            localStorage.setItem('e2seq_user_labels', JSON.stringify(this._userLabels));
        } catch (_) {}
    }

    /** Restore user label edits from localStorage. */
    _loadLabelsFromStorage() {
        try {
            const raw = localStorage.getItem('e2seq_user_labels');
            if (raw) {
                const parsed = JSON.parse(raw);
                if (parsed && typeof parsed === 'object') {
                    return { celltype: parsed.celltype || {}, group: parsed.group || {} };
                }
            }
        } catch (_) {}
        return { celltype: {}, group: {} };
    }

    /** Clear persisted labels (called only when data is unloaded). */
    _clearLabelsStorage() {
        try { localStorage.removeItem('e2seq_user_labels'); } catch (_) {}
    }

    /** Apply i18n translations to all static text in the analysis panel. */
    applyI18n(lang = null) {
        const _t = (key) => {
            const currentLang = lang || localStorage.getItem('e2seq_language') || 'zh-CN';
            return i18n[currentLang]?.[key] || key;
        };

        // Panel title and info
        const panelTitle = document.getElementById('apPanelTitle');
        if (panelTitle) panelTitle.textContent = _t('analysis.dataSettings');

        // Tab buttons
        const apModeTable = document.getElementById('apModeTable');
        if (apModeTable) apModeTable.textContent = _t('analysis.tableMode');
        const apModeSc = document.getElementById('apModeSinglecell');
        if (apModeSc) apModeSc.textContent = _t('analysis.singlecellMode');

        // Drop zone text
        this._updateDropZoneText();

        // Column labels
        const ctLabel = document.getElementById('apCelltypeColLabel');
        if (ctLabel) ctLabel.textContent = _t('analysis.celltypeCol');
        const grpLabel = document.getElementById('apGroupColLabel');
        if (grpLabel) grpLabel.textContent = _t('analysis.groupCol');

        // Top genes label
        const tgLabel = document.getElementById('apTopGenesLabel');
        if (tgLabel) tgLabel.textContent = _t('analysis.topGenes');

        // Matrix preview title
        const matrixTitle = document.getElementById('apMatrixTitle');
        if (matrixTitle) matrixTitle.textContent = _t('analysis.topGenesPreview');

        // Description label
        const descLabel = document.getElementById('apDescLabel');
        if (descLabel) descLabel.textContent = _t('analysis.descPlaceholder');

        // Run button text
        const runBtn = document.getElementById('apRunBtn');
        if (runBtn) {
            const span = runBtn.querySelector('span[data-i18n]');
            if (span) span.textContent = _t('analysis.startAnalysis');
        }

        // Clear data button text
        const clearBtn = document.getElementById('apClearDataBtn');
        if (clearBtn) {
            const span = clearBtn.querySelector('span[data-i18n]');
            if (span) span.textContent = _t('analysis.clearData');
        }

        // Data info text
        const apDataInfo = document.getElementById('apDataInfo');
        if (apDataInfo) {
            if (!this._dataStatus?.data_loaded) {
                apDataInfo.textContent = _t('analysis.noDataLoaded');
            }
        }
    }

    _updateDropZoneText() {
        const _t = (key) => {
            const lang = localStorage.getItem('e2seq_language') || 'zh-CN';
            return i18n[lang]?.[key] || key;
        };
        const zone = document.getElementById('apH5adDropZone');
        if (!zone) return;
        const span = document.getElementById('apDropZoneText');
        if (!span) return;
        const isSc = this.currentMode !== 'table';
        const prefix = isSc ? _t('analysis.singlecellDropzone') : _t('analysis.tableDropzone');
        const clickText = _t('chat.pleaseSelectFile');
        // Replace the text node before the button, keep the button element intact
        const btn = span.querySelector('button');
        const textNode = Array.from(span.childNodes).find(n => n.nodeType === Node.TEXT_NODE);
        if (textNode) textNode.textContent = prefix + '，';
        if (btn) btn.textContent = clickText;
    }

    init() {
        this.ensureModeUI();
        document.getElementById('closeAnalysisPanel')?.addEventListener('click', () => this.close());
        document.getElementById('apDropUploadBtn')?.addEventListener('click', () => {
            const status = this._dataStatus || {};
            if (status.data_loaded) {
                this.app.showNotification(t('analysis.currentlyLoaded'), 'error');
                return;
            }
            if (this.currentMode === 'table') this.app.openFilePicker('table');
            else this.app.openFilePicker('singlecell');
        });
        document.getElementById('apTableUploadBtn')?.addEventListener('click', () => {
            const status = this._dataStatus || {};
            if (status.data_loaded) {
                this.app.showNotification(t('analysis.currentlyLoaded'), 'error');
                return;
            }
            this.app.openFilePicker('table');
        });
        document.getElementById('apTableConfirmBtn')?.addEventListener('click', () => this.confirmTableUpload());
        document.getElementById('apTableExprTypePreset')?.addEventListener('change', () => this.updateTableExprTypeInput());
        document.getElementById('apTableGeneCol')?.addEventListener('change', () => this.updateTableGeneCountPreview());
        document.getElementById('apTableExprCol')?.addEventListener('change', () => this.updateTableGeneCountPreview());
        document.getElementById('apTableExprThresh')?.addEventListener('input', () => this.updateTableGeneCountPreview());
        document.getElementById('apTableSigCol')?.addEventListener('change', () => this.updateTableGeneCountPreview());
        document.getElementById('apTableSigThresh')?.addEventListener('input', () => this.updateTableGeneCountPreview());
        document.getElementById('apModeSinglecell')?.addEventListener('click', () => this.switchMode('singlecell'));
        document.getElementById('apModeTable')?.addEventListener('click', () => this.switchMode('table'));

        // 清除数据按钮
        document.getElementById('apClearDataBtn')?.addEventListener('click', async () => {
            if (!confirm(t('analysis.confirmClear'))) return;
            try {
                await fetch('/api/clear-data', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ session_id: this.app?.currentChatId || 'default' }),
                });
                this._colsLoaded = false;
                this.matrixData = null;
                this._userLabels = { celltype: {}, group: {} };
                this._clearLabelsStorage();
                await this.checkDataStatus();
                this._resetSelectorsToUnused();
                this.app.showNotification(t('analysis.dataCleared'), 'success');
            } catch(e) {
                this.app.showNotification(t('analysis.clearFailed'), 'error');
            }
        });

        // H5ad drag-drop zone
        window.apH5adDrop = (e) => {
            e.preventDefault();
            const dropZone = document.getElementById('apH5adDropZone');
            if (dropZone) dropZone.style.borderColor = 'var(--border-color,#3d4460)';
            const status = this._dataStatus || {};
            if (status.data_loaded) {
                this.app.showNotification(t('analysis.currentlyLoaded'), 'error');
                return;
            }
            if (this.currentMode === 'table') this.app.openFilePicker('table');
            else this.app.openFilePicker('singlecell');
        };

        // On column change: snapshot current inputs first, then clear only
        // the new column's entries so user edits for other columns survive.
        document.getElementById('apCelltypeColSelect')?.addEventListener('change', () => {
            this._snapshotLabelRows('celltype');
            const col = document.getElementById('apCelltypeColSelect')?.value || '';
            if (col) {
                (this.availableCols[col] || []).forEach(v => { delete this._userLabels.celltype[v]; });
            }
            this._saveLabelsToStorage();
            this.buildLabelRows('celltype');
            if (this.matrixData) this.loadMatrix();
        });
        document.getElementById('apGroupColSelect')?.addEventListener('change', () => {
            this._snapshotLabelRows('group');
            const col = document.getElementById('apGroupColSelect')?.value || '';
            if (col) {
                (this.availableCols[col] || []).forEach(v => { delete this._userLabels.group[v]; });
            }
            this._saveLabelsToStorage();
            this.buildLabelRows('group');
            if (this.matrixData) this.loadMatrix();
        });
        document.getElementById('apTopGenesInput')?.addEventListener('input', () => {
            if (this.matrixData) this.loadMatrix();
        });

        document.getElementById('apRunBtn')?.addEventListener('click', () => this.runAnalysis());


        this.checkDataStatus();
        this.switchMode(this.currentMode);
        // Long poll interval (60 s) to reduce chance of racing with label edits.
        // Label changes are persisted to the backend immediately via _persistLabelsSoon().
        setInterval(() => this.checkDataStatus(), 60000);
    }

    /**
     * Snapshot live DOM label inputs into _userLabels[which] without
     * clearing existing entries. Called before any DOM rebuild so no
     * user edit is ever lost.
     */
    _snapshotLabelRows(which) {
        const rowsId = which === 'celltype' ? 'apCelltypeLabelRows' : 'apGroupLabelRows';
        document.querySelectorAll(`#${rowsId} .ap-label-input`).forEach(inp => {
            if (inp.dataset.orig) {
                this._userLabels[which][inp.dataset.orig] = inp.value;
            }
        });
    }

    /**
     * Debounced persist of current label maps to the backend so that any
     * downstream analysis (literature search, interpretation) always uses
     * the latest display names, even before the user clicks "Run Analysis".
     * Fires 800 ms after the last keystroke to avoid a request per key press.
     * Snapshots DOM first so labels are always up-to-date even if a poll
     * fires during the debounce window.
     */
    _persistLabelsSoon() {
        // Snapshot immediately on each keystroke so the in-memory map is always
        // current, regardless of when the debounced network call fires.
        this._snapshotLabelRows('celltype');
        this._snapshotLabelRows('group');
        this._saveLabelsToStorage();

        if (this._persistTimer) clearTimeout(this._persistTimer);
        this._persistTimer = setTimeout(() => this._persistLabelsNow(), 800);
    }

    async _persistLabelsNow() {
        const ctCol  = document.getElementById('apCelltypeColSelect')?.value || '';
        const grpCol = document.getElementById('apGroupColSelect')?.value || '';
        if (!ctCol && !grpCol) return;
        const celltypeLabels = this.getLabelMap('celltype');
        const groupLabels    = this.getLabelMap('group');
        try {
            await fetch('/api/configure-dataset', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.app?.currentChatId || 'default',
                    celltype_col: ctCol,
                    group_col: grpCol,
                    celltype_labels: celltypeLabels,
                    group_labels: groupLabels,
                }),
            });
        } catch (_) { /* non-fatal — labels still live in localStorage */ }
    }

    _bindModeTabListeners() {
        document.getElementById('apModeSinglecell')?.addEventListener('click', () => this.switchMode('singlecell'));
        document.getElementById('apModeTable')?.addEventListener('click', () => this.switchMode('table'));
    }

    ensureModeUI() {
        const panel = document.getElementById('analysisPanel');
        if (!panel) return;

        // Tab buttons now exist in HTML — only ensure labels are correct (i18n)
        this._bindModeTabListeners();

        // Tab buttons exist in HTML; do NOT recreate them here to avoid overwriting i18n
        const tabs = panel.querySelector('.ap-mode-tabs');
        if (!tabs) {
            tabs = document.createElement('div');
            tabs.className = 'ap-mode-tabs';
            tabs.style.cssText = 'display:flex;gap:8px;margin:10px 0 12px;';
            tabs.innerHTML = `<button id="apModeTable" class="ap-mode-tab" type="button">${t('analysis.tableMode')}</button>` +
                             `<button id="apModeSinglecell" class="ap-mode-tab active" type="button">${t('analysis.singlecellMode')}</button>`;
            const drop = document.getElementById('apH5adDropZone');
            if (drop) panel.insertBefore(tabs, drop);
        }

        // Create table section if missing (use i18n for all text)
        if (!document.getElementById('apTableSection')) {
            const sec = document.createElement('div');
            sec.id = 'apTableSection';
            sec.style.display = 'none';
            const _t2 = (k) => {
                const lang = localStorage.getItem('e2seq_language') || 'zh-CN';
                return i18n[lang]?.[k] || k;
            };
            sec.innerHTML = `
                <div class="ap-drop-zone"
                    ondragover="event.preventDefault(); this.style.borderColor='var(--accent-primary)'"
                    ondragleave="event.preventDefault(); this.style.borderColor='var(--border-color,#3d4460)'"
                    ondrop="window.apH5adDrop(event)">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="17 8 12 3 7 8"></polyline>
                        <line x1="12" y1="3" x2="12" y2="15"></line>
                    </svg>
                    <span>${_t2('analysis.tableDropzone')} <button id="apTableUploadBtn" style="background:none;border:none;color:var(--accent-secondary);cursor:pointer;text-decoration:underline">${_t2('chat.pleaseSelectFile')}</button></span>
                </div>
                <div class="ap-col-section" style="padding-top:4px;">
                    <div class="ap-col-row">
                        <label>${_t2('upload.geneCol')}</label>
                        <select id="apTableGeneCol" class="form-control ap-select"><option value="">— 不使用 —</option></select>
                    </div>
                    <div class="ap-col-row" style="margin-top:10px;">
                        <label>${_t2('upload.groupCol')}</label>
                        <select id="apTableGroupCol" class="form-control ap-select"><option value="">— 不使用 —</option></select>
                    </div>
                    <div class="ap-col-row" style="margin-top:10px;">
                        <label>${_t2('upload.exprCol')}</label>
                        <select id="apTableExprCol" class="form-control ap-select"><option value="">— 不使用 —</option></select>
                    </div>
                    <div class="ap-col-row" style="margin-top:10px;">
                        <label>${_t2('upload.exprType')}</label>
                        <select id="apTableExprTypePreset" class="form-control ap-select">
                            <option value="log2FC">log2FC</option>
                            <option value="logFC">logFC</option>
                            <option value="mean_expr">mean expression</option>
                            <option value="custom">custom</option>
                        </select>
                        <input id="apTableExprTypeCustom" class="form-control ap-select" type="text" value="" placeholder="${_t2('analysis.displayName')}" style="margin-top:8px;display:none;" />
                    </div>
                    <div class="ap-col-row" style="margin-top:10px;">
                        <label>${_t2('upload.exprThresh')}</label>
                        <input id="apTableExprThresh" class="form-control ap-select" type="number" step="0.01" placeholder="0.5" />
                    </div>
                    <div class="ap-col-row" style="margin-top:10px;">
                        <label>${_t2('upload.sigCol')}</label>
                        <select id="apTableSigCol" class="form-control ap-select"><option value="">— 不使用 —</option></select>
                    </div>
                    <div class="ap-col-row" style="margin-top:10px;">
                        <label>${_t2('upload.sigThresh')}</label>
                        <input id="apTableSigThresh" class="form-control ap-select" type="number" step="0.01" value="0.05" />
                    </div>
                    <div class="ap-col-row" style="margin-top:10px;">
                        <label>${_t2('analysis.descPlaceholder')}</label>
                        <textarea id="apTableDatasetDesc" class="form-control ap-select" rows="3" placeholder="${_t2('analysis.descPlaceholder')}"></textarea>
                    </div>
                    <div id="apTableInfo" style="margin-top:10px;font-size:.8rem;color:var(--text-secondary)">${_t2('analysis.noDataLoaded')}</div>
                    <div id="apTableGeneCountInfo" style="margin-top:4px;font-size:.8rem;color:var(--accent-secondary)">${_t2('analysis.filteredGenes')}: -</div>
                    <div id="apTableError" style="margin-top:8px;font-size:.8rem;color:#ef4444;display:none"></div>
                    <button id="apTableConfirmBtn" class="ap-btn-run" style="margin-top:12px;" disabled>${_t2('upload.confirmUpload')}</button>
                </div>`;
            const footer = panel.querySelector('.ap-footer');
            if (footer) footer.parentNode.insertBefore(sec, footer.nextSibling);
            else panel.appendChild(sec);
        }
    }

    _refreshActionButtons() {
        const runBtn = document.getElementById('apRunBtn');
        const tableBtn = document.getElementById('apTableConfirmBtn');
        const status = this._dataStatus || {};

        const hasData = !!status.data_loaded;
        const mode = status.data_mode || null;
        const singleReady = this.currentMode === 'singlecell' && hasData && mode === 'singlecell';
        const tableReady = this.currentMode === 'table' && hasData && mode === 'table';

        if (runBtn) {
            runBtn.disabled = !singleReady;
            runBtn.title = singleReady ? '' : t('analysis.needUploadSinglecell');
        }
        if (tableBtn) {
            tableBtn.disabled = !tableReady;
            tableBtn.title = tableReady ? '' : t('analysis.needUploadTable');
        }
    }

    _resetSelectorsToUnused() {
        const setNone = (id) => {
            const el = document.getElementById(id);
            if (el) el.value = '';
        };
        ['apCelltypeColSelect', 'apGroupColSelect', 'apTableGeneCol', 'apTableGroupCol', 'apTableExprCol', 'apTableSigCol'].forEach(setNone);

        const infoEl = document.getElementById('apTableInfo');
        if (infoEl) infoEl.textContent = t('analysis.noDataLoaded');
        const geneInfoEl = document.getElementById('apTableGeneCountInfo');
        if (geneInfoEl) geneInfoEl.textContent = t('analysis.filteredGenes') + ': -';

        const ctRows = document.getElementById('apCelltypeLabelRows');
        const gpRows = document.getElementById('apGroupLabelRows');
        if (ctRows) ctRows.innerHTML = '';
        if (gpRows) gpRows.innerHTML = '';

        this._pendingTableFile = null;
    }

    switchMode(mode) {
        const target = mode === 'table' ? 'table' : 'singlecell';
        const status = this._dataStatus || {};
        if (status.data_loaded && status.data_mode && status.data_mode !== target) {
            this.app.showNotification(t('analysis.modeSwitchBlocked'), 'error');
            return;
        }

        this.currentMode = target;
        const tabSc = document.getElementById('apModeSinglecell');
        const tabTb = document.getElementById('apModeTable');
        if (tabSc) tabSc.classList.toggle('active', this.currentMode === 'singlecell');
        if (tabTb) tabTb.classList.toggle('active', this.currentMode === 'table');

        const singleSections = [
            document.getElementById('apH5adDropZone'),
            document.querySelector('#analysisPanel .ap-col-section'),
            document.getElementById('apMatrixSection'),
            document.querySelector('#analysisPanel .ap-desc-section'),
            document.querySelector('#analysisPanel .ap-footer'),
        ];
        singleSections.forEach(el => {
            if (el) el.style.display = this.currentMode === 'singlecell' ? '' : 'none';
        });

        const tbSection = document.getElementById('apTableSection');
        if (tbSection) tbSection.style.display = this.currentMode === 'table' ? 'block' : 'none';

        this._refreshActionButtons();
    }

    toggle() { this.isOpen ? this.close() : this.open(); }

    open() {
        document.getElementById('analysisPanel').classList.add('open');
        document.getElementById('mainContent')?.classList.add('panel-open');
        this.isOpen = true;
    }

    close() {
        document.getElementById('analysisPanel').classList.remove('open');
        document.getElementById('mainContent')?.classList.remove('panel-open');
        this.isOpen = false;
    }

    async checkDataStatus() {
        try {
            const sid = this.app?.currentChatId || 'default';
            const r = await fetch(`/api/status?session_id=${encodeURIComponent(sid)}`);
            const data = await r.json();
            const infoEl = document.getElementById('apDataInfo');
            if (data.data_loaded) {
                this._dataStatus = { data_loaded: true, data_mode: data.data_mode || 'singlecell' };
                const isTable = this._dataStatus.data_mode === 'table';
                const modeText = isTable ? t('analysis.tableMode') : t('analysis.singlecellMode');
                const cellUnit = t('dataset.cells');
                const geneUnit = t('dataset.genes');
                infoEl.innerHTML = `<span style="color:var(--accent-secondary)">&#x2713;</span> [${modeText}] ${(data.cells||0).toLocaleString()} ${cellUnit} &middot; ${(data.genes||0).toLocaleString()} ${geneUnit}`;
                // Show clear button when data is loaded
                const clearBtn = document.getElementById('apClearDataBtn');
                if (clearBtn) clearBtn.style.display = 'block';
                // _colsLoaded stays true once set; NEVER reset by status polls.
                // Only resets when data is unloaded (else branch below).
                // This is the key fix preventing label edits from being overwritten.
                if (!this._colsLoaded) {
                    await this.loadAvailableGroups();
                    this._colsLoaded = true;
                }
                if (!this.matrixData) this.loadMatrix();
            } else {
                this._dataStatus = { data_loaded: false, data_mode: null };
                infoEl.textContent = t('analysis.noDataLoaded');
                const clearBtn = document.getElementById('apClearDataBtn');
                if (clearBtn) clearBtn.style.display = 'none';
                this._colsLoaded = false;
                this.matrixData = null;
                this._userLabels = { celltype: {}, group: {} };
                this._clearLabelsStorage();
                this._resetSelectorsToUnused();
            }
            this._refreshActionButtons();
        } catch(e) {}
    }

    async loadAvailableGroups() {
        try {
            const sid = this.app?.currentChatId || 'default';
            const r = await fetch(`/api/matrix/groups?session_id=${encodeURIComponent(sid)}`);
            if (!r.ok) return;
            const groups = await r.json();
            this.availableCols = groups;
            const cols = Object.keys(groups);

            const ctSel = document.getElementById('apCelltypeColSelect');
            if (ctSel) {
                const savedCt = ctSel.value;
                ctSel.innerHTML = '<option value="">— 不使用 —</option>' +
                    cols.map(c => `<option value="${c}"${c === savedCt ? ' selected' : ''}>${c} (${(groups[c]||[]).slice(0,4).join('/')}${(groups[c]||[]).length > 4 ? '…' : ''})</option>`).join('');
                if (!savedCt && cols.length) {
                    ctSel.value = cols.find(c => /cell|type|cluster/i.test(c)) || cols[0];
                }
            }

            const grpSel = document.getElementById('apGroupColSelect');
            if (grpSel) {
                const savedGrp = grpSel.value;
                grpSel.innerHTML = '<option value="">— 不使用 —</option>' +
                    cols.map(c => `<option value="${c}"${c === savedGrp ? ' selected' : ''}>${c} (${(groups[c]||[]).slice(0,4).join('/')}${(groups[c]||[]).length > 4 ? '…' : ''})</option>`).join('');
                if (!savedGrp && cols.length) {
                    grpSel.value = cols.find(c => /group|disease|condition|phenotype/i.test(c)) || cols[1] || '';
                }
            }

            this.buildLabelRows('celltype');
            this.buildLabelRows('group');
        } catch(e) {}
    }

    buildLabelRows(which) {
        const selId  = which === 'celltype' ? 'apCelltypeColSelect' : 'apGroupColSelect';
        const rowsId = which === 'celltype' ? 'apCelltypeLabelRows'  : 'apGroupLabelRows';
        const col = document.getElementById(selId)?.value;
        const container = document.getElementById(rowsId);
        if (!container) return;
        if (!col) { container.innerHTML = ''; return; }
        const values = this.availableCols[col] || [];
        if (!values.length) { container.innerHTML = ''; return; }

        // Snapshot any live DOM edits BEFORE rebuilding so no edit is lost.
        this._snapshotLabelRows(which);

        container.innerHTML = values.map(v => {
            const saved = (this._userLabels[which][v] !== undefined)
                ? this._userLabels[which][v]
                : v;
            return `
            <div style="display:flex;align-items:center;gap:.4rem">
                <span style="width:90px;font-size:.78rem;color:var(--text-secondary);flex-shrink:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${v}">${v}</span>
                <span style="color:var(--text-tertiary);font-size:.78rem">→</span>
                <input type="text" class="form-control ap-label-input" data-col="${col}" data-orig="${v}"
                    value="${saved}" placeholder="显示名称"
                    style="flex:1;height:26px;font-size:.78rem;padding:0 .4rem">
            </div>`;
        }).join('');

        container.querySelectorAll('.ap-label-input').forEach(inp => {
            inp.addEventListener('input', () => {
                this._userLabels[which][inp.dataset.orig] = inp.value;
                this._saveLabelsToStorage();
                this._persistLabelsSoon();
            });
        });
    }

    getLabelMap(which) {
        const rowsId = which === 'celltype' ? 'apCelltypeLabelRows' : 'apGroupLabelRows';
        const map = {};
        document.querySelectorAll(`#${rowsId} .ap-label-input`).forEach(el => {
            const orig = el.dataset.orig;
            if (orig) map[orig] = el.value.trim() || orig;
        });
        const cached = this._userLabels[which] || {};
        Object.entries(cached).forEach(([orig, val]) => {
            if (!(orig in map)) map[orig] = val || orig;
        });
        return map;
    }

    _getTableExprTypeValue() {
        const preset = document.getElementById('apTableExprTypePreset')?.value || 'log2FC';
        const custom = (document.getElementById('apTableExprTypeCustom')?.value || '').trim();
        return preset === 'custom' ? (custom || 'value') : preset;
    }

    updateTableExprTypeInput() {
        const preset = document.getElementById('apTableExprTypePreset')?.value || 'log2FC';
        const customInput = document.getElementById('apTableExprTypeCustom');
        if (!customInput) return;
        customInput.style.display = preset === 'custom' ? 'block' : 'none';
    }

    async updateTableGeneCountPreview() {
        const infoEl = document.getElementById('apTableGeneCountInfo');
        const file = this._pendingTableFile;
        if (!file || !infoEl) return;

        const geneCol = document.getElementById('apTableGeneCol')?.value || '';
        const exprCol = document.getElementById('apTableExprCol')?.value || '';
        const exprThreshRaw = document.getElementById('apTableExprThresh')?.value || '';
        const sigCol = document.getElementById('apTableSigCol')?.value || '';
        const sigThreshRaw = document.getElementById('apTableSigThresh')?.value || '';

        if (!geneCol) {
                infoEl.textContent = t('analysis.filteredGenes') + ': -';
            return;
        }

        const formData = new FormData();
        formData.append('session_id', this.app?.currentChatId || 'default');
        formData.append('gene_col', geneCol);
        if (exprCol) formData.append('expr_col', exprCol);
        if (exprThreshRaw) formData.append('expr_thresh', exprThreshRaw);
        if (sigCol) formData.append('sig_col', sigCol);
        if (sigThreshRaw) formData.append('sig_thresh', sigThreshRaw);

        try {
            const response = await fetch('/api/csv-gene-count', { method: 'POST', body: formData });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || '统计失败');
            infoEl.textContent = `${t('analysis.filteredGenes')}: ${(data.n_genes || 0).toLocaleString()} (${(data.n_rows_filtered || 0).toLocaleString()} rows)`;
        } catch (_) {
            infoEl.textContent = `${t('analysis.filteredGenes')}: ${t('analysis.statFailed')}`;
        }
    }

    async setTableFile(file) {
        this._pendingTableFile = file;
        const errEl = document.getElementById('apTableError');
        const infoEl = document.getElementById('apTableInfo');
        if (errEl) { errEl.style.display = 'none'; errEl.textContent = ''; }
        if (infoEl) infoEl.textContent = `正在读取：${file.name}`;

        const formData = new FormData();
        formData.append('file', file);
        formData.append('session_id', this.app?.currentChatId || 'default');

        try {
            const response = await fetch('/api/upload-csv', { method: 'POST', body: formData });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || '上传失败');

            const cols = data.columns || [];
            const fill = (id, allowNone = true) => {
                const sel = document.getElementById(id);
                if (!sel) return;
                sel.innerHTML = (allowNone ? '<option value="">— 不使用 —</option>' : '<option value="">— 选择列 —</option>') +
                    cols.map(c => `<option value="${c}">${c}</option>`).join('');
            };
            fill('apTableGeneCol', false);
            fill('apTableGroupCol', true);
            fill('apTableExprCol', true);
            fill('apTableSigCol', true);

            const lower = cols.map(c => c.toLowerCase());
            const pick = (regex) => cols[lower.findIndex(c => regex.test(c))] || '';
            const geneGuess = pick(/gene|symbol|name|ensembl/);
            const groupGuess = pick(/group|condition|disease|class|phenotype/);
            const exprGuess = pick(/log2fc|logfc|mean.*expr|expression|fc$/);
            const sigGuess = pick(/fdr|padj|adj.*p|pvalue|pval|qval/);

            if (geneGuess) document.getElementById('apTableGeneCol').value = geneGuess;
            if (groupGuess) document.getElementById('apTableGroupCol').value = groupGuess;
            if (exprGuess) {
                document.getElementById('apTableExprCol').value = exprGuess;
                const preset = document.getElementById('apTableExprTypePreset');
                const customInput = document.getElementById('apTableExprTypeCustom');
                if (preset) {
                    const low = exprGuess.toLowerCase();
                    if (low.includes('log2fc')) preset.value = 'log2FC';
                    else if (low.includes('logfc')) preset.value = 'logFC';
                    else if (low.includes('mean')) preset.value = 'mean_expr';
                    else {
                        preset.value = 'custom';
                        if (customInput) customInput.value = exprGuess;
                    }
                }
            }
            if (sigGuess) document.getElementById('apTableSigCol').value = sigGuess;

            this.updateTableExprTypeInput();
            await this.updateTableGeneCountPreview();
            if (infoEl) infoEl.textContent = `${file.name} · ${data.n_rows} 行 · ${cols.length} 列`;

            // 与单细胞一致：文件上传后即视为已上传（自动应用当前配置）
            await this.confirmTableUpload();
        } catch (e) {
            if (errEl) { errEl.textContent = e.message; errEl.style.display = 'block'; }
            if (infoEl) infoEl.textContent = '表格读取失败';
        }
    }

    async confirmTableUpload() {
        const status = this._dataStatus || {};
        if (status.data_loaded && status.data_mode && status.data_mode !== 'table') {
            this.app.showNotification(t('analysis.tableModeLoaded'), 'error');
            return;
        }

        const file = this._pendingTableFile;
        const geneCol = document.getElementById('apTableGeneCol')?.value || '';
        const groupCol = document.getElementById('apTableGroupCol')?.value || '';
        const exprType = this._getTableExprTypeValue();
        const exprCol = document.getElementById('apTableExprCol')?.value || '';
        const exprThresh = document.getElementById('apTableExprThresh')?.value || '';
        const sigCol = document.getElementById('apTableSigCol')?.value || '';
        const sigThresh = document.getElementById('apTableSigThresh')?.value || '0.05';
        const datasetDesc = (document.getElementById('apTableDatasetDesc')?.value || '').trim();
        const errEl = document.getElementById('apTableError');

        if (!file || !geneCol) {
            if (errEl) { errEl.textContent = '请先上传文件并选择基因列'; errEl.style.display = 'block'; }
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('session_id', this.app?.currentChatId || 'default');
        formData.append('gene_col', geneCol);
        if (groupCol) formData.append('group_col', groupCol);
        formData.append('expr_type', exprType);
        if (exprCol) formData.append('expr_col', exprCol);
        if (exprThresh) formData.append('expr_thresh', exprThresh);
        if (sigCol) formData.append('sig_col', sigCol);
        if (sigThresh) formData.append('sig_thresh', sigThresh);
        if (datasetDesc) formData.append('dataset_description', datasetDesc);
        formData.append('n_top_genes', 0);

        try {
            const response = await fetch('/api/configure-csv', { method: 'POST', body: formData });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || '配置失败');
            this.app.showNotification(t('analysis.uploadSuccess', null, {count: data.n_genes}), 'success');
            const clearBtn = document.getElementById('apClearDataBtn');
            if (clearBtn) clearBtn.style.display = 'block';
            this._colsLoaded = false;
            await this.checkDataStatus();
            this.switchMode('table');
            this.app.navigateToChat();
        } catch (e) {
            if (errEl) { errEl.textContent = e.message; errEl.style.display = 'block'; }
        }
    }

    _getTopGenesN() {
        const raw = parseInt(document.getElementById('apTopGenesInput')?.value || '50', 10);
        const n = Number.isFinite(raw) ? raw : 50;
        return Math.max(5, Math.min(100, n));
    }

    async loadMatrix() {
        const sid = this.app?.currentChatId || 'default';
        const ctCol  = document.getElementById('apCelltypeColSelect')?.value || '';
        const grpCol = document.getElementById('apGroupColSelect')?.value || '';
        const topN   = this._getTopGenesN();
        const section = document.getElementById('apMatrixSection');
        const preview = document.getElementById('apMatrixPreview');
        if (!ctCol && !grpCol) return;

        try {
            let html = '';
            if (ctCol) {
                const r = await fetch(`/api/matrix?session_id=${encodeURIComponent(sid)}&n_top_genes=${topN}&celltype_col=${encodeURIComponent(ctCol)}`);
                if (r.ok) {
                    const data = await r.json();
                    this.matrixData = this.matrixData || {};
                    this.matrixData.celltype = data;
                    const ctLabels = this.getLabelMap('celltype');
                    const cellTypes = data.cell_types || [];
                    if (cellTypes.length) {
                        html += `<div style="margin-bottom:.5rem;font-size:.78rem;color:var(--text-secondary)">细胞类型 Top ${topN} 高表达基因</div>`;
                        html += '<div style="overflow-x:auto">';
                        html += '<table style="width:100%;font-size:.72rem;border-collapse:collapse">';
                        html += '<thead><tr><th style="text-align:left;padding:2px 6px;color:var(--text-tertiary)">细胞类型</th>';
                        html += '<th style="text-align:left;padding:2px 6px;color:var(--text-tertiary)">Top 基因</th></tr></thead><tbody>';
                        cellTypes.forEach(ct => {
                            const displayCt = ctLabels[ct] || ct;
                            const genes = (data.top_genes_per_celltype || {})[ct] || [];
                            const preview = genes.slice(0, 12).join(', ');
                            const extra = genes.length > 12 ? ` <span style="color:var(--text-tertiary)">+${genes.length - 12}</span>` : '';
                            html += `<tr><td style="padding:2px 6px;color:var(--accent-secondary);white-space:nowrap">${displayCt}</td>`;
                            html += `<td style="padding:2px 6px;color:var(--text-primary)">${preview}${extra}</td></tr>`;
                        });
                        html += '</tbody></table></div>';
                    }
                }
            }
            if (grpCol) {
                const r2 = await fetch(`/api/matrix/by-group?session_id=${encodeURIComponent(sid)}&group_col=${encodeURIComponent(grpCol)}&n_top_genes=${topN}`);
                if (r2.ok) {
                    const data2 = await r2.json();
                    this.matrixData = this.matrixData || {};
                    this.matrixData.group = data2;
                    const grpLabels = this.getLabelMap('group');
                    const groups = data2.groups || [];
                    if (groups.length) {
                        html += `<div style="margin:.5rem 0 .3rem;font-size:.78rem;color:var(--text-secondary)">疾病表型 Top ${topN} 高表达基因</div>`;
                        html += '<div style="overflow-x:auto">';
                        html += '<table style="width:100%;font-size:.72rem;border-collapse:collapse">';
                        html += '<thead><tr><th style="text-align:left;padding:2px 6px;color:var(--text-tertiary)">分组</th>';
                        html += '<th style="text-align:left;padding:2px 6px;color:var(--text-tertiary)">Top 基因</th></tr></thead><tbody>';
                        groups.forEach(grp => {
                            const displayGrp = grpLabels[grp] || grp;
                            const genes = (data2.top_genes_per_group || {})[grp] || [];
                            const preview2 = genes.slice(0, 12).join(', ');
                            const extra2 = genes.length > 12 ? ` <span style="color:var(--text-tertiary)">+${genes.length - 12}</span>` : '';
                            html += `<tr><td style="padding:2px 6px;color:var(--accent-secondary);white-space:nowrap">${displayGrp}</td>`;
                            html += `<td style="padding:2px 6px;color:var(--text-primary)">${preview2}${extra2}</td></tr>`;
                        });
                        html += '</tbody></table></div>';
                    }
                }
            }
            if (preview) preview.innerHTML = html || '<span style="color:var(--text-tertiary);font-size:.78rem">暂无数据</span>';
            if (section) section.style.display = html ? 'block' : 'none';
        } catch(e) {
            console.error('loadMatrix error:', e);
        }
    }

    async runAnalysis() {
        const status = this._dataStatus || {};
        if (status.data_loaded && status.data_mode && status.data_mode !== 'singlecell') {
            this.app.showNotification(t('analysis.singlecellModeLoaded'), 'error');
            return;
        }

        const ctCol  = document.getElementById('apCelltypeColSelect')?.value || '';
        const grpCol = document.getElementById('apGroupColSelect')?.value || '';
        const runBtn = document.getElementById('apRunBtn');
        const topGenesN = this._getTopGenesN();
        const celltypeLabels = this.getLabelMap('celltype');
        const groupLabels    = this.getLabelMap('group');

        if (!ctCol && !grpCol) {
            alert(t('analysis.selectColumn'));
            return;
        }

        runBtn.disabled = true;
        const spinnerSvg = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="animation:spin 1s linear infinite"><circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="10"/></svg>';
        runBtn.innerHTML = `${spinnerSvg} ${t('analysis.analyzing')}`;

        try {
            const cfgResp = await fetch('/api/configure-dataset', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.app?.currentChatId || 'default',
                    celltype_col: ctCol,
                    group_col: grpCol,
                    n_top_genes: topGenesN,
                    celltype_labels: celltypeLabels,
                    group_labels: groupLabels,
                    dataset_description: (document.getElementById('apDatasetDesc')?.value || '').trim(),
                }),
            });
            if (!cfgResp.ok) {
                const err = await cfgResp.json().catch(() => ({}));
                throw new Error(err.detail || '配置失败');
            }

            const messageInput = document.getElementById('messageInput');
            if (messageInput) {
                this.app.navigateToChat();
                // Agentic RAG: no offline KB build needed — queries are answered on demand
                this.app._setInputLocked(false, '');
                this.app.showNotification(t('analysis.configComplete'), 'success');
            }
        } catch(e) {
            alert(t('analysis.startFailed') + ': ' + e.message);
        } finally {
            runBtn.disabled = false;
            const span = runBtn.querySelector('span[data-i18n]');
            if (span) span.textContent = t('analysis.startAnalysis');
            else runBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg> ${t('analysis.startAnalysis')}`;
        }
    }
}

// AnalysisPanel is instantiated by app.js DOMContentLoaded handler.
// No separate mount logic needed here.
