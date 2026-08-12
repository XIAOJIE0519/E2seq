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
        this._bulkFiles = { counts: null, clinical: null, result: null };
        this._bulkPreview = null;
        this._bulkResultPreview = null;
        this._bulkResult = null;
        this._bulkSelectedGenes = new Set();
        this._bulkFilterState = null;
        this._geneIntersectionList = [];
        this._bulkSelectionInitialized = false;
        this._bulkRestoredSessionId = null;
        this._bulkPollSessionId = null;
        this._bulkPollGeneration = 0;
        this.init();
    }

    /** Localised text lookup — falls back to key when missing. */
    _t(key) {
        if (typeof t === 'function') return t(key);
        return key;
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

    init() {
        this.ensureModeUI();
        this._initPanelResizeHandle();
        document.querySelectorAll('input[name="language"]').forEach(radio => {
            radio.addEventListener('change', () => setTimeout(() => this._refreshBulkLanguage(), 0));
        });
        document.getElementById('closeAnalysisPanel')?.addEventListener('click', () => this.close());
        document.getElementById('apDropUploadBtn')?.addEventListener('click', () => {
            const status = this._dataStatus || {};
            if (status.data_loaded) {
                this.app.showNotification(this._t('analysisPanel.notifHasData'), 'error');
                return;
            }
            if (this.currentMode === 'table') this.app.openFilePicker('table');
            else this.app.openFilePicker('singlecell');
        });
        document.getElementById('apTableUploadBtn')?.addEventListener('click', () => {
            const status = this._dataStatus || {};
            if (status.data_loaded) {
                this.app.showNotification(this._t('analysisPanel.notifHasData'), 'error');
                return;
            }
            this.openBulkDialog();
        });
        document.getElementById('apTableConfirmBtn')?.addEventListener('click', () => this.confirmTableUpload());
        document.getElementById('apTableExprTypePreset')?.addEventListener('change', () => this.updateTableExprTypeInput());
        document.getElementById('apTableGeneCol')?.addEventListener('change', () => this.updateTableGeneCountPreview());
        document.getElementById('apTableExprCol')?.addEventListener('change', () => this.updateTableGeneCountPreview());
        document.getElementById('apTableExprThresh')?.addEventListener('input', () => this.updateTableGeneCountPreview());
        document.getElementById('apTableSigCol')?.addEventListener('change', () => this.updateTableGeneCountPreview());
        document.getElementById('apTableSigThresh')?.addEventListener('input', () => this.updateTableGeneCountPreview());
        document.getElementById('apTableTopN')?.addEventListener('input', () => this.updateTableGeneCountPreview());
        document.getElementById('apModeSinglecell')?.addEventListener('click', () => this.switchMode('singlecell'));
        document.getElementById('apModeTable')?.addEventListener('click', () => this.switchMode('table'));
        document.getElementById('apGeneIntersectionBtn')?.addEventListener('click', () => this.openGeneIntersectionDialog());

        // 清除数据按钮
        document.getElementById('apClearDataBtn')?.addEventListener('click', async () => {
            if (!confirm(this._t('analysisPanel.confirmClear'))) return;
            try {
                await fetch('/api/clear-data', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ session_id: this.app?.currentChatId || 'default' }),
                });
                this._colsLoaded = false;
                this.matrixData = null;
                this._geneIntersectionList = [];
                this._userLabels = { celltype: {}, group: {} };
                this._clearLabelsStorage();
                await this.checkDataStatus();
                this._resetSelectorsToUnused();
                this._resetBulkUI();
                this.app.showNotification(this._t('analysisPanel.dataCleared'), 'success');
            } catch(e) {
                this.app.showNotification(this._t('analysisPanel.clearFailed'), 'error');
            }
        });

        // H5ad drag-drop zone
        window.apH5adDrop = (e) => {
            e.preventDefault();
            const dropZone = document.getElementById('apH5adDropZone');
            if (dropZone) dropZone.style.borderColor = 'var(--border-color,#3d4460)';
            const status = this._dataStatus || {};
            if (status.data_loaded) {
                this.app.showNotification(this._t('analysisPanel.notifHasData'), 'error');
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

    _initPanelResizeHandle() {
        const panel = document.getElementById('analysisPanel');
        const handle = document.getElementById('analysisPanelResizeHandle');
        if (!panel || !handle || handle.dataset.bound === 'true') return;
        handle.dataset.bound = 'true';

        const storageKey = 'e2seq_analysis_panel_width';
        const bounds = () => {
            const viewport = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
            const min = Math.min(320, Math.max(0, viewport - 24));
            const max = Math.max(min, Math.min(760, Math.round(viewport * 0.78)));
            return { min, max };
        };
        const setWidth = (value, persist = false) => {
            if (window.innerWidth <= 768) return;
            const { min, max } = bounds();
            const width = Math.round(Math.max(min, Math.min(max, Number(value) || min)));
            panel.style.width = `${width}px`;
            if (persist) {
                try { localStorage.setItem(storageKey, String(width)); } catch (_) {}
            }
        };

        try {
            const saved = Number(localStorage.getItem(storageKey));
            if (Number.isFinite(saved) && saved > 0) setWidth(saved);
        } catch (_) {}

        let dragging = false;
        let startX = 0;
        let startWidth = 0;

        const stopDragging = (event) => {
            if (!dragging) return;
            dragging = false;
            handle.classList.remove('dragging');
            panel.classList.remove('is-resizing');
            document.body.classList.remove('analysis-panel-resizing');
            try { handle.releasePointerCapture(event.pointerId); } catch (_) {}
            setWidth(panel.getBoundingClientRect().width, true);
        };

        handle.addEventListener('pointerdown', (event) => {
            if (window.innerWidth <= 768) return;
            event.preventDefault();
            dragging = true;
            startX = event.clientX;
            startWidth = panel.getBoundingClientRect().width;
            handle.classList.add('dragging');
            panel.classList.add('is-resizing');
            document.body.classList.add('analysis-panel-resizing');
            try { handle.setPointerCapture(event.pointerId); } catch (_) {}
        });
        handle.addEventListener('pointermove', (event) => {
            if (!dragging) return;
            event.preventDefault();
            setWidth(startWidth + startX - event.clientX);
        });
        handle.addEventListener('pointerup', stopDragging);
        handle.addEventListener('pointercancel', stopDragging);
        handle.addEventListener('keydown', (event) => {
            if (window.innerWidth <= 768) return;
            const current = panel.getBoundingClientRect().width;
            if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
                event.preventDefault();
                setWidth(current + (event.key === 'ArrowLeft' ? 24 : -24), true);
            } else if (event.key === 'Home') {
                event.preventDefault();
                setWidth(bounds().max, true);
            } else if (event.key === 'End') {
                event.preventDefault();
                setWidth(bounds().min, true);
            }
        });
        window.addEventListener('resize', () => {
            if (window.innerWidth > 768) setWidth(panel.getBoundingClientRect().width);
        });
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

    ensureModeUI() {
        const panel = document.getElementById('analysisPanel');
        if (!panel) return;

        // Create mode tabs if missing
        let tabs = panel.querySelector('.ap-mode-tabs');
        if (!tabs) {
            tabs = document.createElement('div');
            tabs.className = 'ap-mode-tabs';
            tabs.style.cssText = 'display:flex;gap:8px;margin:10px 0 12px;';
            tabs.innerHTML = `<button id="apModeTable" class="ap-mode-tab" type="button" data-i18n="analysisPanel.tableMode">${this._t('analysisPanel.tableMode')}</button>` +
                             `<button id="apModeSinglecell" class="ap-mode-tab active" type="button" data-i18n="analysisPanel.singlecellMode">${this._t('analysisPanel.singlecellMode')}</button>`;
            const drop = document.getElementById('apH5adDropZone');
            if (drop) panel.insertBefore(tabs, drop);
        }

        // The same post-filter gene-list intersection is available for both
        // single-cell and expression-profile sessions.  It lives outside the
        // mode-specific forms so the interaction stays identical in both.
        if (!document.getElementById('apGeneIntersectionBar')) {
            const bar = document.createElement('div');
            bar.id = 'apGeneIntersectionBar';
            bar.className = 'ap-gene-intersection-bar';
            bar.style.display = 'none';
            bar.innerHTML = `
                <button id="apGeneIntersectionBtn" class="btn btn-secondary" type="button" data-i18n="analysisPanel.geneIntersectionButton">${this._t('analysisPanel.geneIntersectionButton')}</button>
                <span id="apGeneIntersectionSummary" data-i18n="analysisPanel.geneIntersectionNone">${this._t('analysisPanel.geneIntersectionNone')}</span>`;
            if (tabs?.parentNode) tabs.insertAdjacentElement('afterend', bar);
            else panel.insertBefore(bar, panel.firstChild);
        }

        // Create table section if missing
        if (!document.getElementById('apTableSection')) {
            const sec = document.createElement('div');
            sec.id = 'apTableSection';
            sec.style.display = 'none';
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
                    <span><span data-i18n="analysisPanel.tableModeHint">${this._t('analysisPanel.tableModeHint')}</span> <button id="apTableUploadBtn" style="background:none;border:none;color:var(--accent-secondary);cursor:pointer;text-decoration:underline" data-i18n="analysisPanel.clickToSelect">${this._t('analysisPanel.clickToSelect')}</button></span>
                </div>
                <div class="ap-col-section" style="padding-top:4px;">
                    <div class="ap-col-row">
                        <label data-i18n="analysisPanel.geneCol">${this._t('analysisPanel.geneCol')}</label>
                        <select id="apTableGeneCol" class="form-control ap-select"><option value="" data-i18n="analysisPanel.notUsed">${this._t('analysisPanel.notUsed')}</option></select>
                    </div>
                    <div class="ap-col-row" style="margin-top:10px;">
                        <label data-i18n="analysisPanel.optionalGroupCol">${this._t('analysisPanel.optionalGroupCol')}</label>
                        <select id="apTableGroupCol" class="form-control ap-select"><option value="" data-i18n="analysisPanel.notUsed">${this._t('analysisPanel.notUsed')}</option></select>
                    </div>
                    <div class="ap-col-row" style="margin-top:10px;">
                        <label data-i18n="analysisPanel.expressionCol">${this._t('analysisPanel.expressionCol')}</label>
                        <select id="apTableExprCol" class="form-control ap-select"><option value="" data-i18n="analysisPanel.notUsed">${this._t('analysisPanel.notUsed')}</option></select>
                    </div>
                    <div class="ap-col-row" style="margin-top:10px;">
                        <label data-i18n="analysisPanel.expressionType">${this._t('analysisPanel.expressionType')}</label>
                        <select id="apTableExprTypePreset" class="form-control ap-select">
                            <option value="log2FC">log2FC</option>
                            <option value="logFC">logFC</option>
                            <option value="mean_expr">mean express</option>
                            <option value="custom" data-i18n="analysisPanel.customName">${this._t('analysisPanel.customName')}</option>
                        </select>
                        <input id="apTableExprTypeCustom" class="form-control ap-select" type="text" value="" placeholder="${this._t('analysisPanel.customNamePlaceholder')}" data-i18n-placeholder="analysisPanel.customNamePlaceholder" style="margin-top:8px;display:none;" />
                    </div>
                    <div class="ap-col-row" style="margin-top:10px;">
                        <label data-i18n="analysisPanel.expressionFilter">${this._t('analysisPanel.expressionFilter')}</label>
                        <input id="apTableExprThresh" class="form-control ap-select" type="number" step="0.01" placeholder="${this._t('analysisPanel.exampleThreshold')}" data-i18n-placeholder="analysisPanel.exampleThreshold" />
                    </div>
                    <div class="ap-col-row" style="margin-top:10px;">
                        <label data-i18n="analysisPanel.significanceCol">${this._t('analysisPanel.significanceCol')}</label>
                        <select id="apTableSigCol" class="form-control ap-select"><option value="" data-i18n="analysisPanel.notUsed">${this._t('analysisPanel.notUsed')}</option></select>
                    </div>
                    <div class="ap-col-row" style="margin-top:10px;">
                        <label data-i18n="analysisPanel.significanceThreshold">${this._t('analysisPanel.significanceThreshold')}</label>
                        <input id="apTableSigThresh" class="form-control ap-select" type="number" step="0.01" value="0.05" />
                    </div>
                    <div class="ap-col-row" style="margin-top:10px;">
                        <label data-i18n="analysisPanel.topNSelection">${this._t('analysisPanel.topNSelection')}</label>
                        <input id="apTableTopN" class="form-control ap-select" type="number" min="0" step="1" value="0" placeholder="${this._t('analysisPanel.topNPlaceholder')}" data-i18n-placeholder="analysisPanel.topNPlaceholder" />
                        <small class="form-hint" data-i18n="analysisPanel.topNHint">${this._t('analysisPanel.topNHint')}</small>
                    </div>
                    <div class="ap-col-row" style="margin-top:10px;">
                        <label data-i18n="analysisPanel.datasetDesc">${this._t('analysisPanel.datasetDesc')}</label>
                        <textarea id="apTableDatasetDesc" class="form-control ap-select" rows="3" placeholder="${this._t('analysisPanel.tableDescPlaceholder')}" data-i18n-placeholder="analysisPanel.tableDescPlaceholder"></textarea>
                    </div>
                    <div class="ap-col-row" style="margin-top:10px;">
                        <label data-i18n="analysisPanel.datasetPrompt">${this._t('analysisPanel.datasetPrompt')}</label>
                        <textarea id="apTableDatasetPrompt" class="form-control ap-select" rows="2" placeholder="${this._t('analysisPanel.datasetPromptPlaceholder')}" data-i18n-placeholder="analysisPanel.datasetPromptPlaceholder"></textarea>
                        <small class="form-hint" data-i18n="analysisPanel.datasetPromptHint">${this._t('analysisPanel.datasetPromptHint')}</small>
                    </div>
                    <div id="apTableInfo" style="margin-top:10px;font-size:.8rem;color:var(--text-secondary)" data-i18n="analysisPanel.noTableData">${this._t('analysisPanel.noTableData')}</div>
                    <div id="apTableGeneCountInfo" style="margin-top:4px;font-size:.8rem;color:var(--accent-secondary)" data-i18n="analysisPanel.filteredGenesEmpty">${this._t('analysisPanel.filteredGenesEmpty')}</div>
                    <div id="apTableError" style="margin-top:8px;font-size:.8rem;color:#ef4444;display:none"></div>
                    <button id="apTableConfirmBtn" class="ap-btn-run" style="margin-top:12px;" disabled data-i18n="analysisPanel.confirmTable">${this._t('analysisPanel.confirmTable')}</button>
                </div>`;
            const footer = panel.querySelector('.ap-footer');
            if (footer) footer.parentNode.insertBefore(sec, footer.nextSibling);
            else panel.appendChild(sec);

            // The old one-file expression-table controls remain in the DOM for
            // backward compatibility, but new table uploads use the explicit
            // two-file expression-profile workflow below.
            const legacyDrop = sec.querySelector('.ap-drop-zone');
            const legacyForm = sec.querySelector('.ap-col-section');
            if (legacyDrop) legacyDrop.style.display = 'none';
            if (legacyForm) legacyForm.style.display = 'none';
            const bulkIntro = document.createElement('div');
            bulkIntro.id = 'apBulkIntro';
            bulkIntro.innerHTML = `
                <div class="bulk-intro-card">
                    <div class="bulk-intro-title" data-i18n="bulk.introTitle">${this._t('bulk.introTitle')}</div>
                    <div class="bulk-intro-copy" data-i18n="bulk.introCopy">${this._t('bulk.introCopy')}</div>
                    <div class="bulk-format-hint" data-i18n="bulk.formatHint">${this._t('bulk.formatHint')}</div>
                    <div class="bulk-entry-actions bulk-single-entry">
                        <button id="apBulkStartBtn" class="ap-btn-run" type="button" data-i18n="bulk.startUpload">${this._t('bulk.startUpload')}</button>
                    </div>
                    <div id="apBulkProgress" class="bulk-progress" hidden>
                        <div class="bulk-progress-head"><span id="apBulkProgressLabel" data-i18n="bulk.prepareAnalysis">${this._t('bulk.prepareAnalysis')}</span><strong id="apBulkProgressPercent">0%</strong></div>
                        <div class="bulk-progress-track"><span id="apBulkProgressBar"></span></div>
                    </div>
                    <div id="apBulkStatus" class="bulk-status"></div>
                </div>`;
            sec.insertBefore(bulkIntro, sec.firstChild);
            document.getElementById('apBulkStartBtn')?.addEventListener('click', () => this.openBulkDialog());
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
            runBtn.title = singleReady ? '' : this._t('analysisPanel.singleRequired');
        }
        if (tableBtn) {
            tableBtn.disabled = !tableReady;
            tableBtn.title = tableReady ? '' : this._t('analysisPanel.tableRequired');
        }
        ['apBulkStartBtn'].forEach(id => {
            const bulkBtn = document.getElementById(id);
            if (bulkBtn) bulkBtn.disabled = hasData;
        });
        const intersectionBar = document.getElementById('apGeneIntersectionBar');
        const intersectionBtn = document.getElementById('apGeneIntersectionBtn');
        if (intersectionBar) intersectionBar.style.display = hasData ? 'flex' : 'none';
        if (intersectionBtn) intersectionBtn.disabled = !hasData;
        this._refreshGeneIntersectionSummary();
    }

    _resetBulkUI() {
        this._bulkFiles = { counts: null, clinical: null, result: null };
        this._bulkPreview = null;
        this._bulkResultPreview = null;
        this._bulkResult = null;
        this._bulkFilteredRows = [];
        this._bulkSelectedGenes = new Set();
        this._bulkFilterState = null;
        this._bulkPersistedSelectedGenes = [];
        this._bulkRestoredSelectionPending = false;
        this._bulkSelectionInitialized = false;
        document.getElementById('apBulkResultFilters')?.remove();
        document.getElementById('apBulkRagControls')?.remove();
        const bulkStatus = document.getElementById('apBulkStatus');
        if (bulkStatus) bulkStatus.textContent = '';
    }

    /**
     * Rebind the panel to the active chat session.
     * Dataset files, statistical results, and the RAG manifest live on the
     * server under this session ID; the browser must refresh only the view.
     */
    async onChatChanged() {
        this._colsLoaded = false;
        this.matrixData = null;
        this._bulkRestoredSessionId = null;
        this._bulkPollGeneration += 1;
        this._bulkPollSessionId = null;
        this._geneIntersectionList = [];
        this._resetBulkUI();
        await this.checkDataStatus();
        const mode = this._dataStatus?.data_mode;
        if (mode) this.switchMode(mode === 'table' ? 'table' : 'singlecell');
    }

    _resetSelectorsToUnused() {
        const setNone = (id) => {
            const el = document.getElementById(id);
            if (el) el.value = '';
        };
        ['apCelltypeColSelect', 'apGroupColSelect', 'apTableGeneCol', 'apTableGroupCol', 'apTableExprCol', 'apTableSigCol'].forEach(setNone);
        const topNEl = document.getElementById('apTableTopN');
        if (topNEl) topNEl.value = '0';

        const infoEl = document.getElementById('apTableInfo');
        if (infoEl) infoEl.textContent = this._t('analysisPanel.noTableData');
        const geneInfoEl = document.getElementById('apTableGeneCountInfo');
        if (geneInfoEl) geneInfoEl.textContent = this._t('analysisPanel.filteredGenesEmpty');

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
            this.app.showNotification(this._t('analysisPanel.modeConflict'), 'error');
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

    _bulkOption(value, label = value) {
        const opt = document.createElement('option');
        opt.value = value;
        opt.textContent = label;
        return opt;
    }

    _bulkT(key, replacements = {}) {
        let value = this._t(`bulk.${key}`);
        Object.entries(replacements).forEach(([name, replacement]) => {
            value = value.replaceAll(`{${name}}`, String(replacement));
        });
        return value;
    }

    _geneIntersectionKey(value) {
        return String(value || '').trim().toUpperCase();
    }

    _parseGeneIntersection(value) {
        const values = Array.isArray(value) ? value : String(value || '').split(/\r?\n/);
        const result = [];
        const seen = new Set();
        values.forEach(item => {
            String(item || '').split(/\r?\n/).forEach(line => {
                const gene = line.trim();
                const key = this._geneIntersectionKey(gene);
                if (!key || seen.has(key)) return;
                seen.add(key);
                result.push(gene);
            });
        });
        return result;
    }

    _getGeneIntersectionSet() {
        return new Set((this._geneIntersectionList || []).map(gene => this._geneIntersectionKey(gene)).filter(Boolean));
    }

    _getVisibleIntersectionNames() {
        const names = [];
        const addMatrix = matrix => {
            if (!matrix) return;
            Object.values(matrix.top_genes_per_celltype || {}).forEach(values => names.push(...(values || [])));
            Object.values(matrix.top_genes_per_group || {}).forEach(values => names.push(...(values || [])));
            names.push(...(matrix.all_top_genes || []));
        };
        addMatrix(this.matrixData?.celltype);
        addMatrix(this.matrixData?.group);
        if (Array.isArray(this._bulkResult?.result)) {
            names.push(...this._bulkResult.result.map(row => row?.gene));
        }
        const normalized = names.map(name => this._geneIntersectionKey(name)).filter(Boolean);
        return normalized.length ? new Set(normalized) : null;
    }

    _refreshGeneIntersectionSummary() {
        const summary = document.getElementById('apGeneIntersectionSummary');
        if (!summary) return;
        const genes = this._geneIntersectionList || [];
        if (!genes.length) {
            summary.textContent = this._t('analysisPanel.geneIntersectionNone');
            return;
        }
        const available = this._getVisibleIntersectionNames();
        const matched = available
            ? genes.filter(gene => available.has(this._geneIntersectionKey(gene))).length
            : '—';
        summary.textContent = this._t('analysisPanel.geneIntersectionSummary')
            .replace('{count}', String(genes.length))
            .replace('{matched}', String(matched));
    }

    _refreshGeneIntersectionDialogSummary() {
        const input = document.getElementById('geneIntersectionInput');
        const info = document.getElementById('geneIntersectionDialogInfo');
        if (!input || !info) return;
        const genes = this._parseGeneIntersection(input.value);
        const available = this._getVisibleIntersectionNames();
        const matched = available
            ? genes.filter(gene => available.has(this._geneIntersectionKey(gene))).length
            : '—';
        info.textContent = this._t('analysisPanel.geneIntersectionDialogSummary')
            .replace('{count}', String(genes.length))
            .replace('{matched}', String(matched));
    }

    openGeneIntersectionDialog() {
        if (!(this._dataStatus || {}).data_loaded) return;
        let modal = document.getElementById('geneIntersectionModal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'geneIntersectionModal';
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content bulk-modal-content gene-intersection-modal-content">
                    <div class="modal-header">
                        <h2 data-i18n="analysisPanel.geneIntersectionTitle">${this._t('analysisPanel.geneIntersectionTitle')}</h2>
                        <button class="modal-close" id="geneIntersectionClose" type="button" data-i18n-title="app.close" title="${this._t('app.close')}">×</button>
                    </div>
                    <div class="modal-body">
                        <div class="bulk-help-copy" data-i18n="analysisPanel.geneIntersectionHint">${this._t('analysisPanel.geneIntersectionHint')}</div>
                        <textarea id="geneIntersectionInput" class="form-control" rows="14" data-i18n-placeholder="analysisPanel.geneIntersectionPlaceholder" placeholder="${this._t('analysisPanel.geneIntersectionPlaceholder')}"></textarea>
                        <div id="geneIntersectionDialogInfo" class="bulk-config-info"></div>
                    </div>
                    <div class="modal-footer">
                        <button id="geneIntersectionClear" class="btn btn-secondary" type="button" data-i18n="analysisPanel.geneIntersectionClear">${this._t('analysisPanel.geneIntersectionClear')}</button>
                        <button id="geneIntersectionCancel" class="btn btn-secondary" type="button" data-i18n="analysisPanel.geneIntersectionCancel">${this._t('analysisPanel.geneIntersectionCancel')}</button>
                        <button id="geneIntersectionApply" class="btn btn-primary" type="button" data-i18n="analysisPanel.geneIntersectionApply">${this._t('analysisPanel.geneIntersectionApply')}</button>
                    </div>
                </div>`;
            document.body.appendChild(modal);
            const close = () => modal.classList.remove('active');
            document.getElementById('geneIntersectionClose')?.addEventListener('click', close);
            document.getElementById('geneIntersectionCancel')?.addEventListener('click', close);
            document.getElementById('geneIntersectionClear')?.addEventListener('click', () => {
                const input = document.getElementById('geneIntersectionInput');
                if (input) input.value = '';
                this._refreshGeneIntersectionDialogSummary();
            });
            document.getElementById('geneIntersectionApply')?.addEventListener('click', () => this._applyGeneIntersectionDialog());
            document.getElementById('geneIntersectionInput')?.addEventListener('input', () => this._refreshGeneIntersectionDialogSummary());
        }
        const input = document.getElementById('geneIntersectionInput');
        if (input) input.value = (this._geneIntersectionList || []).join('\n');
        this._refreshGeneIntersectionDialogSummary();
        this._refreshBulkLanguage();
        modal.classList.add('active');
        input?.focus();
    }

    async _applyGeneIntersectionDialog() {
        const genes = this._parseGeneIntersection(document.getElementById('geneIntersectionInput')?.value || '');
        this._geneIntersectionList = genes;
        document.getElementById('geneIntersectionModal')?.classList.remove('active');
        this._refreshGeneIntersectionSummary();
        const sid = this.app?.currentChatId || 'default';
        try {
            const response = await fetch('/api/gene-intersection', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sid, genes }),
            });
            const data = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(data.detail || this._t('analysisPanel.geneIntersectionFailed'));
            if (this.currentMode === 'table' && this._bulkResult) {
                this._applyBulkResultFilters();
            } else if (this.currentMode === 'singlecell' && this.matrixData) {
                await this.loadMatrix();
            }
            this._refreshGeneIntersectionSummary();
            this.app.showNotification(this._t('analysisPanel.geneIntersectionSaved'), 'success');
        } catch (error) {
            this.app.showNotification(`${this._t('analysisPanel.geneIntersectionFailed')}: ${error.message}`, 'error');
        }
    }

    _refreshBulkLanguage() {
        const roots = [
            document.getElementById('apBulkIntro'),
            document.getElementById('bulkUploadModal'),
            document.getElementById('bulkDifferentialConfigModal'),
            document.getElementById('bulkSurvivalConfigModal'),
            document.getElementById('apBulkResultFilters'),
            document.getElementById('apGeneIntersectionBar'),
            document.getElementById('geneIntersectionModal'),
        ].filter(Boolean);
        roots.forEach(root => {
            root.querySelectorAll('[data-i18n]').forEach(element => {
                const translation = this._t(element.getAttribute('data-i18n'));
                if (element.children.length === 0) element.textContent = translation;
                else {
                    const textNode = Array.from(element.childNodes).find(node => node.nodeType === Node.TEXT_NODE);
                    if (textNode) textNode.textContent = translation;
                }
            });
            root.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
                element.placeholder = this._t(element.getAttribute('data-i18n-placeholder'));
            });
            root.querySelectorAll('[data-i18n-title]').forEach(element => {
                element.title = this._t(element.getAttribute('data-i18n-title'));
            });
        });
        if (this._bulkResult && document.getElementById('apBulkResultFilters')) {
            this._applyBulkResultFilters();
            this._localizeBulkFilterCard();
        }
        this._refreshGeneIntersectionSummary();
        if (document.getElementById('geneIntersectionModal')?.classList.contains('active')) {
            this._refreshGeneIntersectionDialogSummary();
        }
    }

    _localizeBulkFilterCard() {
        const card = document.getElementById('apBulkResultFilters');
        if (!card) return;
        const setLabel = (id, key) => {
            const field = document.getElementById(id);
            const label = field?.closest('label');
            if (!label) return;
            const labelText = label.querySelector('.bulk-filter-label');
            if (labelText) labelText.textContent = this._bulkT(key);
        };
        const setOptions = (id, options) => {
            const select = document.getElementById(id);
            if (!select) return;
            options.forEach(([value, key]) => {
                const option = select.querySelector(`option[value="${value}"]`);
                if (option) option.textContent = this._bulkT(key);
            });
        };

        card.querySelector('.bulk-result-title')?.replaceChildren(document.createTextNode(this._bulkT('filterTitle')));
        card.querySelector('.bulk-result-copy')?.replaceChildren(document.createTextNode(this._bulkT('filterCopy')));
        setLabel('bulkFilterSigMetric', 'significanceMetric');
        setLabel('bulkFilterSigThreshold', 'significanceThreshold');
        const resultMetric = String(this._bulkResult?.metadata?.effect_metric || '').toLowerCase();
        const isResultSurvival = this._bulkResult?.analysis_type === 'survival';
        const isCountResult = !isResultSurvival && resultMetric === 'count';
        const isExpressionResult = !isResultSurvival && resultMetric === 'expression';
        setLabel('bulkFilterEffectMetric', isResultSurvival ? 'effectMetric' : isCountResult ? 'countMetric' : isExpressionResult ? 'expressionMetric' : 'changeMetric');
        setLabel('bulkFilterEffectThreshold', isResultSurvival ? 'effectThresholdHr' : isCountResult ? 'countThreshold' : isExpressionResult ? 'expressionThreshold' : 'effectThresholdFc');
        setLabel('bulkFilterDirection', 'direction');
        setLabel('bulkFilterTopN', 'topN');
        setOptions('bulkFilterSigMetric', [['padj', 'fdrOption'], ['pvalue', 'pValueOption']]);
        setOptions('bulkFilterDirection', [['all', 'all'], ['up', 'upHighRisk'], ['down', 'downLowRisk']]);
        const effectOption = card.querySelector('#bulkFilterEffectMetric option[value="log2FoldChange"]');
        if (effectOption) effectOption.textContent = this._bulkT(isCountResult ? 'countValue' : isExpressionResult ? 'expressionValue' : isResultSurvival ? 'effectMetric' : 'changeMetric');
        card.querySelector('#bulkResetFilter')?.replaceChildren(document.createTextNode(this._bulkT('resetFilter')));
        card.querySelector('.bulk-filter-live')?.replaceChildren(document.createTextNode(this._bulkT('liveUpdate')));
        const topNHint = card.querySelector('#bulkFilterTopN + .form-hint');
        if (topNHint) topNHint.textContent = this._bulkT('topNHint');
        this._localizeBulkFilterTable();
        if (this._ragCostEstimate) this._renderRagCostEstimate(this._ragCostEstimate);
    }

    _bulkFillSelect(id, values, includeEmpty = false) {
        const select = document.getElementById(id);
        if (!select) return;
        select.replaceChildren();
        if (includeEmpty) select.appendChild(this._bulkOption('', this._t('analysisPanel.notUsed')));
        (values || []).forEach(value => select.appendChild(this._bulkOption(String(value))));
    }

    _bulkSetModeFields() {
        const type = document.getElementById('bulkAnalysisType')?.value || 'differential';
        const de = document.getElementById('bulkDifferentialFields');
        const surv = document.getElementById('bulkSurvivalFields');
        const advancedDe = document.getElementById('bulkAdvancedDifferential');
        const advancedSurv = document.getElementById('bulkAdvancedSurvival');
        if (de) de.style.display = type === 'differential' ? '' : 'none';
        if (surv) surv.style.display = type === 'survival' ? '' : 'none';
        if (advancedDe) advancedDe.style.display = type === 'differential' ? '' : 'none';
        if (advancedSurv) advancedSurv.style.display = type === 'survival' ? '' : 'none';
        this._bulkSetSurvivalTimeFields();
        this._bulkSetAdjustmentFields();
    }

    _bulkSetSurvivalTimeFields() {
        const dateMode = document.getElementById('bulkSurvivalTimeType')?.value === 'date_ymd';
        const durationWrap = document.getElementById('bulkDurationTimeWrap');
        const dateWrap = document.getElementById('bulkDateTimeWrap');
        if (durationWrap) durationWrap.style.display = dateMode ? 'none' : '';
        if (dateWrap) dateWrap.style.display = dateMode ? '' : 'none';
    }

    _bulkSetInputMode() {
        const mode = document.getElementById('bulkInputMode')?.value || 'raw';
        const rawUpload = document.getElementById('bulkRawUploadSection');
        const resultUpload = document.getElementById('bulkResultUploadSection');
        const rawConfig = document.getElementById('bulkConfigFields');
        const resultConfig = document.getElementById('bulkResultConfigFields');
        const uploadButton = document.getElementById('bulkUploadBtn');
        if (rawUpload) rawUpload.style.display = mode === 'raw' ? '' : 'none';
        if (resultUpload) resultUpload.style.display = mode === 'result' ? '' : 'none';
        if (rawConfig) rawConfig.style.display = mode === 'raw' && this._bulkPreview ? '' : 'none';
        if (resultConfig) resultConfig.style.display = mode === 'result' && this._bulkResultPreview ? '' : 'none';
        const uploadKey = mode === 'raw' ? 'readFiles' : (this._bulkResultPreview ? 'resultReadAgain' : 'readResult');
        if (uploadButton) uploadButton.textContent = this._bulkT(uploadKey);
        if (mode === 'result') this._bulkSetResultEffectMetric();
    }

    _bulkSetResultEffectMetric() {
        const type = document.getElementById('bulkResultAnalysisType')?.value || 'differential';
        const select = document.getElementById('bulkResultEffectMetric');
        if (!select) return;
        const allowed = type === 'survival'
            ? new Set(['HR', 'coef'])
            : new Set(['log2fc', 'expression', 'count', 'coef']);
        Array.from(select.options).forEach(option => {
            option.hidden = !allowed.has(option.value);
        });
        if (!allowed.has(select.value)) select.value = type === 'survival' ? 'HR' : 'log2fc';
        const effectCol = document.getElementById('bulkResultEffectCol');
        const guessed = type === 'survival'
            ? this._bulkResultPreview?.survival?.effect_column_guess
            : this._bulkResultPreview?.differential?.effect_column_guess;
        if (effectCol && guessed) effectCol.value = guessed;
    }

    _bulkSetAdjustmentFields() {
        const type = document.getElementById('bulkAnalysisType')?.value || 'differential';
        const checkedId = type === 'differential' ? 'bulkAdjustClinical' : 'bulkSurvivalAdjust';
        const wrapId = type === 'differential' ? 'bulkCovariateWrap' : 'bulkSurvCovariateWrap';
        const checked = document.getElementById(checkedId)?.checked;
        const wrap = document.getElementById(wrapId);
        if (wrap) wrap.style.display = checked ? '' : 'none';
    }

    _openBulkAnalysisConfig(type) {
        const normalized = type === 'survival' ? 'survival' : 'differential';
        if (!this._bulkPreview) return;
        this._bulkPendingAnalysisType = normalized;
        const modalId = normalized === 'survival' ? 'bulkSurvivalConfigModal' : 'bulkDifferentialConfigModal';
        const titleKey = normalized === 'survival' ? 'bulk.survivalDialogTitle' : 'bulk.differentialDialogTitle';
        let configModal = document.getElementById(modalId);
        if (!configModal) {
            configModal = document.createElement('div');
            configModal.id = modalId;
            configModal.className = 'modal';
            configModal.innerHTML = `
                <div class="modal-content bulk-modal-content bulk-analysis-config-modal">
                    <div class="modal-header"><h2 data-i18n="${titleKey}">${this._t(titleKey)}</h2><button class="modal-close" type="button" data-i18n-title="app.close" title="${this._t('app.close')}">×</button></div>
                    <div class="modal-body bulk-analysis-config-body"></div>
                </div>`;
            document.body.appendChild(configModal);
            configModal.querySelector('.modal-close')?.addEventListener('click', () => this._closeBulkAnalysisConfig());
        }
        document.getElementById('bulkDifferentialConfigModal')?.classList.remove('active');
        document.getElementById('bulkSurvivalConfigModal')?.classList.remove('active');
        const fields = document.getElementById('bulkConfigFields');
        const body = configModal.querySelector('.bulk-analysis-config-body');
        if (fields && body && fields.parentNode !== body) body.appendChild(fields);
        if (fields) fields.style.display = '';
        const typeSelect = document.getElementById('bulkAnalysisType');
        if (typeSelect) {
            typeSelect.value = normalized;
            typeSelect.disabled = true;
            const typeGroup = typeSelect.closest('.form-group');
            if (typeGroup) typeGroup.style.display = 'none';
        }
        document.getElementById('bulkAnalysisChoice')?.style.setProperty('display', 'none');
        document.getElementById('bulkUploadModal')?.classList.remove('active');
        this._bulkSetModeFields();
        this._refreshBulkLanguage();
        configModal.classList.add('active');
    }

    _closeBulkAnalysisConfig() {
        const fields = document.getElementById('bulkConfigFields');
        const mount = document.getElementById('bulkConfigFieldsMount');
        if (fields && mount && fields.parentNode !== mount) mount.appendChild(fields);
        if (fields) fields.style.display = 'none';
        const typeSelect = document.getElementById('bulkAnalysisType');
        if (typeSelect) {
            typeSelect.disabled = false;
            const typeGroup = typeSelect.closest('.form-group');
            if (typeGroup) typeGroup.style.display = '';
        }
        document.getElementById('bulkDifferentialConfigModal')?.classList.remove('active');
        document.getElementById('bulkSurvivalConfigModal')?.classList.remove('active');
        this._bulkPendingAnalysisType = '';
        const uploadModal = document.getElementById('bulkUploadModal');
        const choice = document.getElementById('bulkAnalysisChoice');
        if (choice) choice.style.display = this._bulkPreview ? '' : 'none';
        if (uploadModal && this._bulkPreview) uploadModal.classList.add('active');
    }

    async openBulkDialog(analysisType = '') {
        const status = this._dataStatus || {};
        if (status.data_loaded) {
            this.app.showNotification(this._bulkT('hasData'), 'error');
            return;
        }
        const pendingType = analysisType === 'survival' ? 'survival' : analysisType === 'differential' ? 'differential' : '';
        this._bulkPendingAnalysisType = pendingType;
        this.app?._setInputLocked?.(true, this._bulkT('waitAnalysis'));
        let modal = document.getElementById('bulkUploadModal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'bulkUploadModal';
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content bulk-modal-content">
                    <div class="modal-header"><h2 data-i18n="bulk.modalTitle">${this._t('bulk.modalTitle')}</h2><button class="modal-close" id="bulkCloseBtn" type="button" data-i18n-title="app.close" title="${this._t('app.close')}">×</button></div>
                    <div class="modal-body">
                        <div class="bulk-help-copy" data-i18n="bulk.help">${this._t('bulk.help')}</div>
                        <div class="form-group bulk-input-mode"><label data-i18n="bulk.inputMode">${this._t('bulk.inputMode')}</label><select id="bulkInputMode" class="form-control"><option value="raw" data-i18n="bulk.rawCountsClinical">${this._t('bulk.rawCountsClinical')}</option><option value="result" data-i18n="bulk.precomputedResult">${this._t('bulk.precomputedResult')}</option></select></div>
                        <div id="bulkRawUploadSection" class="bulk-drop-grid">
                            <div id="bulkCountsDrop" class="bulk-drop-zone" tabindex="0">
                                <input id="bulkCountsFile" type="file" accept=".csv,.tsv,.txt,.xlsx,.xls" hidden>
                                <strong data-i18n="bulk.countsTitle">${this._t('bulk.countsTitle')}</strong>
                                <span data-i18n="bulk.countsHint">${this._t('bulk.countsHint')}</span>
                                <small id="bulkCountsName" data-i18n="bulk.dropHint">${this._t('bulk.dropHint')}</small>
                            </div>
                            <div id="bulkClinicalDrop" class="bulk-drop-zone" tabindex="0">
                                <input id="bulkClinicalFile" type="file" accept=".csv,.tsv,.txt,.xlsx,.xls" hidden>
                                <strong data-i18n="bulk.clinicalTitle">${this._t('bulk.clinicalTitle')}</strong>
                                <span data-i18n="bulk.clinicalHint">${this._t('bulk.clinicalHint')}</span>
                                <small id="bulkClinicalName" data-i18n="bulk.dropHint">${this._t('bulk.dropHint')}</small>
                            </div>
                        </div>
                        <div id="bulkResultUploadSection" class="bulk-drop-grid" style="display:none;">
                            <div id="bulkResultDrop" class="bulk-drop-zone bulk-drop-zone-wide" tabindex="0">
                                <input id="bulkResultFile" type="file" accept=".csv,.tsv,.txt,.xlsx,.xls" hidden>
                                <strong data-i18n="bulk.resultTitle">${this._t('bulk.resultTitle')}</strong>
                                <span data-i18n="bulk.resultHint">${this._t('bulk.resultHint')}</span>
                                <small id="bulkResultName" data-i18n="bulk.dropHint">${this._t('bulk.dropHint')}</small>
                            </div>
                        </div>
                        <div id="bulkUploadInfo" class="bulk-upload-info"></div>
                        <div id="bulkUploadProgress" class="bulk-progress" hidden>
                            <div class="bulk-progress-head"><span id="bulkUploadProgressLabel" data-i18n="bulk.prepareUpload">${this._t('bulk.prepareUpload')}</span><strong id="bulkUploadProgressPercent">0%</strong></div>
                            <div class="bulk-progress-track"><span id="bulkUploadProgressBar"></span></div>
                        </div>
                        <button id="bulkUploadBtn" class="btn btn-primary" type="button" data-i18n="bulk.readFiles">${this._t('bulk.readFiles')}</button>
                        <div id="bulkAnalysisChoice" class="bulk-analysis-choice" style="display:none;">
                            <div class="bulk-step-title" data-i18n="bulk.chooseAnalysisTitle">${this._t('bulk.chooseAnalysisTitle')}</div>
                            <div class="bulk-help-copy" data-i18n="bulk.chooseAnalysisCopy">${this._t('bulk.chooseAnalysisCopy')}</div>
                            <div class="bulk-entry-actions" style="display:flex;gap:8px;flex-wrap:wrap;">
                                <button id="bulkChooseDifferentialBtn" class="btn btn-secondary" type="button" data-i18n="bulk.openDifferential">${this._t('bulk.openDifferential')}</button>
                                <button id="bulkChooseSurvivalBtn" class="btn btn-secondary" type="button" data-i18n="bulk.openSurvival">${this._t('bulk.openSurvival')}</button>
                            </div>
                        </div>
                        <div id="bulkConfigFieldsMount"></div>
                        <div id="bulkConfigFields" style="display:none;">
                            <div class="bulk-step-title" data-i18n="bulk.chooseAnalysis">${this._t('bulk.chooseAnalysis')}</div>
                            <div class="form-group"><label data-i18n="bulk.datasetDescription">${this._t('bulk.datasetDescription')}</label><textarea id="bulkDatasetDesc" class="form-control" rows="2" data-i18n-placeholder="bulk.datasetDescriptionPlaceholder" placeholder="${this._t('bulk.datasetDescriptionPlaceholder')}"></textarea><small class="bulk-format-hint" data-i18n="bulk.datasetDescriptionHint">${this._t('bulk.datasetDescriptionHint')}</small></div>
                            <div class="form-group"><label data-i18n="bulk.datasetPrompt">默认提示词（可选） / Dataset prompt (optional)</label><textarea id="bulkDatasetPrompt" class="form-control" rows="2" data-i18n-placeholder="bulk.datasetPromptPlaceholder" placeholder="${this._t('bulk.datasetPromptPlaceholder')}"></textarea><small class="bulk-format-hint" data-i18n="bulk.datasetPromptHint">${this._t('bulk.datasetPromptHint')}</small></div>
                            <div class="form-group"><label data-i18n="bulk.analysisType">${this._t('bulk.analysisType')}</label><select id="bulkAnalysisType" class="form-control"><option value="differential" data-i18n="bulk.differential">${this._t('bulk.differential')}</option><option value="survival" data-i18n="bulk.survival">${this._t('bulk.survival')}</option></select></div>
                            <div id="bulkDifferentialFields">
                                <div class="form-group"><label data-i18n="bulk.deMethod">${this._t('bulk.deMethod')}</label><select id="bulkDeMethod" class="form-control"><option value="deseq2">DESeq2</option><option value="edger">edgeR</option><option value="limma_voom">limma-voom</option></select></div>
                                <label class="bulk-check-row" data-i18n="bulk.adjustClinical"><input id="bulkAdjustClinical" type="checkbox"> ${this._t('bulk.adjustClinical')}</label>
                                <div id="bulkCovariateWrap" class="form-group" style="display:none;margin-top:8px;"><label data-i18n="bulk.chooseCovariates">${this._t('bulk.chooseCovariates')}</label><select id="bulkCovariates" class="form-control" multiple size="4"></select></div>
                            </div>
                            <div id="bulkSurvivalFields" style="display:none;">
                                <div class="form-group"><label data-i18n="bulk.expressionTransform">${this._t('bulk.expressionTransform')}</label><select id="bulkTransform" class="form-control"><option value="vst">VST</option><option value="logcpm">logCPM</option><option value="log2_tpm_1">log2(TPM+1)</option></select></div>
                                <label class="bulk-check-row" data-i18n="bulk.adjustClinical"><input id="bulkSurvivalAdjust" type="checkbox"> ${this._t('bulk.adjustClinical')}</label>
                                <div id="bulkSurvCovariateWrap" class="form-group" style="display:none;margin-top:8px;"><label data-i18n="bulk.chooseCovariates">${this._t('bulk.chooseCovariates')}</label><select id="bulkSurvCovariates" class="form-control" multiple size="4"></select></div>
                            </div>
                            <details id="bulkAdvancedSettings" class="bulk-advanced-settings">
                                <summary data-i18n="bulk.advanced">${this._t('bulk.advanced')}</summary>
                                <div class="bulk-advanced-body">
                                    <div class="form-group"><label data-i18n="bulk.geneCol">${this._t('bulk.geneCol')}</label><input id="bulkGeneCol" class="form-control" type="text"></div>
                                    <div class="form-group"><label data-i18n="bulk.sampleCol">${this._t('bulk.sampleCol')}</label><select id="bulkSampleCol" class="form-control"></select></div>
                                    <div id="bulkAdvancedDifferential">
                                        <div class="form-group"><label data-i18n="bulk.groupCol">${this._t('bulk.groupCol')}</label><select id="bulkGroupCol" class="form-control"></select></div>
                                        <div class="form-row bulk-form-row"><div class="form-group"><label data-i18n="bulk.control">${this._t('bulk.control')}</label><select id="bulkControlLevel" class="form-control"></select></div><div class="form-group"><label data-i18n="bulk.case">${this._t('bulk.case')}</label><select id="bulkCaseLevel" class="form-control"></select></div></div>
                                        <div class="form-group"><label data-i18n="bulk.subgroup">${this._t('bulk.subgroup')}</label><select id="bulkSubgroupCol" class="form-control"></select></div>
                                    </div>
                                    <div id="bulkAdvancedSurvival" style="display:none;">
                                        <div class="form-group"><label data-i18n="bulk.survivalTimeType">${this._t('bulk.survivalTimeType')}</label><select id="bulkSurvivalTimeType" class="form-control"><option value="duration" data-i18n="bulk.duration">${this._t('bulk.duration')}</option><option value="date_ymd" data-i18n="bulk.dateYmd">${this._t('bulk.dateYmd')}</option></select></div>
                                        <div id="bulkDurationTimeWrap" class="form-group"><label data-i18n="bulk.survivalTimeCol">${this._t('bulk.survivalTimeCol')}</label><select id="bulkTimeCol" class="form-control"></select></div>
                                        <div id="bulkDateTimeWrap" style="display:none;">
                                            <div class="form-row bulk-form-row"><div class="form-group"><label data-i18n="bulk.startDateCol">${this._t('bulk.startDateCol')}</label><select id="bulkStartDateCol" class="form-control"></select></div><div class="form-group"><label data-i18n="bulk.endDateCol">${this._t('bulk.endDateCol')}</label><select id="bulkEndDateCol" class="form-control"></select></div></div>
                                            <small class="bulk-format-hint" data-i18n="bulk.dateHint">${this._t('bulk.dateHint')}</small>
                                        </div>
                                        <div class="form-group"><label data-i18n="bulk.eventCol">${this._t('bulk.eventCol')}</label><select id="bulkEventCol" class="form-control"></select></div>
                                        <div class="form-group"><label data-i18n="bulk.eventValue">${this._t('bulk.eventValue')}</label><input id="bulkEventPositive" class="form-control" value=""></div>
                                        <div class="bulk-format-hint" data-i18n="bulk.allGenesHint">${this._t('bulk.allGenesHint')}</div>
                                    </div>
                                </div>
                            </details>
                            <div id="bulkConfigInfo" class="bulk-config-info"></div>
                            <button id="bulkRunBtn" class="btn btn-primary" type="button" data-i18n="bulk.run">${this._t('bulk.run')}</button>
                        </div>
                        <div id="bulkResultConfigFields" style="display:none;">
                            <div class="bulk-step-title" data-i18n="bulk.resultConfigTitle">${this._t('bulk.resultConfigTitle')}</div>
                            <div class="form-group"><label data-i18n="bulk.datasetDescription">${this._t('bulk.datasetDescription')}</label><textarea id="bulkResultDatasetDesc" class="form-control" rows="2" data-i18n-placeholder="bulk.datasetDescriptionPlaceholder" placeholder="${this._t('bulk.datasetDescriptionPlaceholder')}"></textarea><small class="bulk-format-hint" data-i18n="bulk.datasetDescriptionHint">${this._t('bulk.datasetDescriptionHint')}</small></div>
                            <div class="form-group"><label data-i18n="bulk.datasetPrompt">默认提示词（可选） / Dataset prompt (optional)</label><textarea id="bulkResultDatasetPrompt" class="form-control" rows="2" data-i18n-placeholder="bulk.datasetPromptPlaceholder" placeholder="${this._t('bulk.datasetPromptPlaceholder')}"></textarea><small class="bulk-format-hint" data-i18n="bulk.datasetPromptHint">${this._t('bulk.datasetPromptHint')}</small></div>
                            <div class="form-group"><label data-i18n="bulk.resultAnalysisType">${this._t('bulk.resultAnalysisType')}</label><select id="bulkResultAnalysisType" class="form-control"><option value="differential" data-i18n="bulk.differential">${this._t('bulk.differential')}</option><option value="survival" data-i18n="bulk.survival">${this._t('bulk.survival')}</option></select></div>
                            <div class="form-group"><label data-i18n="bulk.resultGeneCol">${this._t('bulk.resultGeneCol')}</label><select id="bulkResultGeneCol" class="form-control"></select></div>
                            <div class="form-group"><label data-i18n="bulk.resultGroupCol">${this._t('bulk.resultGroupCol')}</label><select id="bulkResultGroupCol" class="form-control"></select><small class="bulk-format-hint" data-i18n="bulk.resultGroupHint">${this._t('bulk.resultGroupHint')}</small></div>
                            <div class="form-group"><label data-i18n="bulk.resultGroupValues">${this._t('bulk.resultGroupValues')}</label><select id="bulkResultGroupValues" class="form-control" multiple size="4"></select></div>
                            <div class="form-group"><label data-i18n="bulk.resultEffectCol">${this._t('bulk.resultEffectCol')}</label><select id="bulkResultEffectCol" class="form-control"></select></div>
                            <div class="form-group"><label data-i18n="bulk.resultEffectMetric">${this._t('bulk.resultEffectMetric')}</label><select id="bulkResultEffectMetric" class="form-control"><option value="log2fc" data-i18n="bulk.resultLog2Fc">log2FC / logFC</option><option value="expression" data-i18n="bulk.resultExpression">表达值</option><option value="count" data-i18n="bulk.resultCount">count</option><option value="HR" data-i18n="bulk.resultHr">HR</option><option value="coef" data-i18n="bulk.resultCoef">coef / β</option></select></div>
                            <div class="form-row bulk-form-row"><div class="form-group"><label data-i18n="bulk.resultPvalueCol">${this._t('bulk.resultPvalueCol')}</label><select id="bulkResultPvalueCol" class="form-control"></select></div><div class="form-group"><label data-i18n="bulk.resultPadjCol">${this._t('bulk.resultPadjCol')}</label><select id="bulkResultPadjCol" class="form-control"></select></div></div>
                            <div class="form-group"><label data-i18n="bulk.resultDirectionCol">${this._t('bulk.resultDirectionCol')}</label><select id="bulkResultDirectionCol" class="form-control"></select><small class="bulk-format-hint" data-i18n="bulk.resultDirectionHint">${this._t('bulk.resultDirectionHint')}</small></div>
                            <div id="bulkResultConfigInfo" class="bulk-config-info"></div>
                            <button id="bulkResultConfigureBtn" class="btn btn-primary" type="button" data-i18n="bulk.resultLoad">${this._t('bulk.resultLoad')}</button>
                        </div>
                    </div>
                </div>`;
            document.body.appendChild(modal);
            document.getElementById('bulkCloseBtn')?.addEventListener('click', () => {
                this._closeBulkAnalysisConfig();
                modal.classList.remove('active');
                this.app?._setInputLocked?.(false);
                this.checkDataStatus();
            });
            document.getElementById('bulkInputMode')?.addEventListener('change', () => {
                this._bulkSetInputMode();
                document.getElementById('bulkConfigFields')?.style.setProperty('display', 'none');
                const choice = document.getElementById('bulkAnalysisChoice');
                if (choice) choice.style.display = document.getElementById('bulkInputMode')?.value === 'raw' && this._bulkPreview ? '' : 'none';
            });
            document.getElementById('bulkAnalysisType')?.addEventListener('change', () => this._bulkSetModeFields());
            document.getElementById('bulkResultAnalysisType')?.addEventListener('change', () => this._bulkSetResultEffectMetric());
            document.getElementById('bulkSurvivalTimeType')?.addEventListener('change', () => this._bulkSetSurvivalTimeFields());
            document.getElementById('bulkAdjustClinical')?.addEventListener('change', () => this._bulkSetAdjustmentFields());
            document.getElementById('bulkSurvivalAdjust')?.addEventListener('change', () => this._bulkSetAdjustmentFields());
            document.getElementById('bulkGroupCol')?.addEventListener('change', () => this._bulkUpdateGroupLevels());
            document.getElementById('bulkEventCol')?.addEventListener('change', () => this._bulkUpdateEventPositive());
            document.getElementById('bulkResultGroupCol')?.addEventListener('change', () => this._bulkUpdateResultGroups());
            document.getElementById('bulkUploadBtn')?.addEventListener('click', () => this._bulkUploadFiles());
            document.getElementById('bulkRunBtn')?.addEventListener('click', () => this._bulkConfigureAndRun());
            document.getElementById('bulkChooseDifferentialBtn')?.addEventListener('click', () => this._openBulkAnalysisConfig('differential'));
            document.getElementById('bulkChooseSurvivalBtn')?.addEventListener('click', () => this._openBulkAnalysisConfig('survival'));
            document.getElementById('bulkResultConfigureBtn')?.addEventListener('click', () => this._bulkConfigureResult());
            ['counts', 'clinical', 'result'].forEach(kind => {
                const ids = {
                    counts: ['bulkCountsFile', 'bulkCountsDrop'],
                    clinical: ['bulkClinicalFile', 'bulkClinicalDrop'],
                    result: ['bulkResultFile', 'bulkResultDrop'],
                }[kind];
                const input = document.getElementById(ids[0]);
                const zone = document.getElementById(ids[1]);
                if (!input || !zone) return;
                input.addEventListener('change', event => this._bulkSetFile(kind, event.target.files?.[0]));
                zone.addEventListener('click', event => { if (event.target !== input) input.click(); });
                zone.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') input.click(); });
                zone.addEventListener('dragover', event => { event.preventDefault(); zone.classList.add('is-dragging'); });
                zone.addEventListener('dragleave', () => zone.classList.remove('is-dragging'));
                zone.addEventListener('drop', event => {
                    event.preventDefault();
                    zone.classList.remove('is-dragging');
                    this._bulkSetFile(kind, event.dataTransfer?.files?.[0]);
                });
            });
        }
        // A chat switch resets the in-memory bulk state, but the reusable modal
        // DOM keeps disabled buttons and old upload labels unless we clear them
        // when a new upload session starts.
        if (!this._bulkPreview && !this._bulkResultPreview) {
            const uploadInfo = document.getElementById('bulkUploadInfo');
            if (uploadInfo) uploadInfo.textContent = '';
            const uploadProgress = document.getElementById('bulkUploadProgress');
            if (uploadProgress) uploadProgress.hidden = true;
            const configFields = document.getElementById('bulkConfigFields');
            if (configFields) configFields.style.display = 'none';
            const analysisChoice = document.getElementById('bulkAnalysisChoice');
            if (analysisChoice) analysisChoice.style.display = 'none';
            const resultConfigFields = document.getElementById('bulkResultConfigFields');
            if (resultConfigFields) resultConfigFields.style.display = 'none';
            ['bulkCountsName', 'bulkClinicalName', 'bulkResultName'].forEach(id => {
                const name = document.getElementById(id);
                if (name) name.textContent = this._bulkT('dropHint');
            });
            ['bulkCountsDrop', 'bulkClinicalDrop', 'bulkResultDrop'].forEach(id => {
                document.getElementById(id)?.classList.remove('has-file', 'is-dragging');
            });
            ['bulkCountsFile', 'bulkClinicalFile', 'bulkResultFile'].forEach(id => {
                const input = document.getElementById(id);
                if (input) input.value = '';
            });
        }
        document.getElementById('bulkUploadBtn')?.removeAttribute('disabled');
        document.getElementById('bulkRunBtn')?.removeAttribute('disabled');
        document.getElementById('bulkResultConfigureBtn')?.removeAttribute('disabled');
        this._refreshBulkLanguage();
        this._bulkSetInputMode();
        const inputMode = document.getElementById('bulkInputMode');
        const inputModeGroup = inputMode?.closest('.form-group');
        if (pendingType) {
            if (inputMode) { inputMode.value = 'raw'; inputMode.disabled = true; }
            if (inputModeGroup) inputModeGroup.style.display = 'none';
        } else {
            if (inputMode) inputMode.disabled = false;
            if (inputModeGroup) inputModeGroup.style.display = '';
        }
        const configFields = document.getElementById('bulkConfigFields');
        if (configFields) configFields.style.display = 'none';
        const analysisChoice = document.getElementById('bulkAnalysisChoice');
        if (analysisChoice) analysisChoice.style.display = !pendingType && inputMode?.value === 'raw' && this._bulkPreview ? '' : 'none';
        modal.classList.add('active');
        this._bulkSetModeFields();
        if (pendingType && this._bulkPreview) this._openBulkAnalysisConfig(pendingType);
    }

    _bulkSetFile(kind, file) {
        if (!file) return;
        this._bulkFiles[kind] = file;
        const nameId = kind === 'counts' ? 'bulkCountsName' : kind === 'clinical' ? 'bulkClinicalName' : 'bulkResultName';
        const nameEl = document.getElementById(nameId);
        if (nameEl) nameEl.textContent = `${file.name} (${(file.size / 1024 / 1024).toFixed(1)} MB)`;
        const zoneId = kind === 'counts' ? 'bulkCountsDrop' : kind === 'clinical' ? 'bulkClinicalDrop' : 'bulkResultDrop';
        const zone = document.getElementById(zoneId);
        if (zone) zone.classList.add('has-file');
    }

    _setBulkProgress(prefix, percent, label) {
        const safePercent = Math.max(0, Math.min(100, Math.round(Number(percent) || 0)));
        const root = document.getElementById(`${prefix}Progress`);
        const bar = document.getElementById(`${prefix}ProgressBar`);
        const value = document.getElementById(`${prefix}ProgressPercent`);
        const text = document.getElementById(`${prefix}ProgressLabel`);
        if (root) root.hidden = false;
        if (bar) bar.style.width = `${safePercent}%`;
        if (value) value.textContent = `${safePercent}%`;
        if (text && label) text.textContent = label;
    }

    _uploadWithProgress(url, form, onProgress) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open('POST', url);
            xhr.upload.addEventListener('progress', event => {
                if (event.lengthComputable && typeof onProgress === 'function') {
                    onProgress(event.loaded, event.total);
                }
            });
            xhr.onload = () => {
                let data = {};
                try { data = JSON.parse(xhr.responseText || '{}'); } catch (_) {}
                resolve({ ok: xhr.status >= 200 && xhr.status < 300, status: xhr.status, data });
            };
            xhr.onerror = () => reject(new Error(this._bulkT('networkError')));
            xhr.send(form);
        });
    }

    async _bulkUploadFiles() {
        const inputMode = document.getElementById('bulkInputMode')?.value || 'raw';
        if (inputMode === 'result') {
            await this._bulkUploadResultFile();
            return;
        }
        const counts = this._bulkFiles.counts || document.getElementById('bulkCountsFile')?.files?.[0];
        const clinical = this._bulkFiles.clinical || document.getElementById('bulkClinicalFile')?.files?.[0];
        const info = document.getElementById('bulkUploadInfo');
        if (!counts || !clinical) { if (info) info.textContent = this._bulkT('missingFiles'); return; }
        const form = new FormData();
        form.append('session_id', this.app?.currentChatId || 'default');
        form.append('counts_file', counts);
        form.append('clinical_file', clinical);
        this._setBulkProgress('bulkUpload', 0, this._bulkT('prepareUpload'));
        if (info) info.textContent = this._bulkT('uploading');
        try {
            const response = await this._uploadWithProgress('/api/bulk/upload', form, (loaded, total) => {
                const ratio = total ? loaded / total : 0;
                this._setBulkProgress('bulkUpload', ratio * 70, ratio >= 1 ? this._bulkT('readingStructure') : this._bulkT('uploadingFiles'));
            });
            const data = response.data || {};
            if (!response.ok) throw new Error(data.detail || this._bulkT('uploadFailed'));
            this._setBulkProgress('bulkUpload', 100, this._bulkT('uploadComplete'));
            this._bulkPreview = data.preview || {};
            const c = this._bulkPreview.counts || {};
            const h = this._bulkPreview.clinical || {};
            if (info) info.textContent = this._bulkT('reading', { genes: c.n_genes, samples: c.n_samples, rows: h.n_rows, matched: this._bulkPreview.matched_samples });
            const cols = h.columns || [];
            this._bulkFillSelect('bulkSampleCol', cols);
            this._bulkFillSelect('bulkGroupCol', cols, true);
            this._bulkFillSelect('bulkTimeCol', cols, true);
            this._bulkFillSelect('bulkStartDateCol', cols, true);
            this._bulkFillSelect('bulkEndDateCol', cols, true);
            this._bulkFillSelect('bulkEventCol', cols, true);
            this._bulkFillSelect('bulkSubgroupCol', cols, true);
            this._bulkFillSelect('bulkCovariates', cols);
            this._bulkFillSelect('bulkSurvCovariates', cols);
            const sampleGuess = h.sample_column_guess || cols.find(c => /barcode|sample|aliquot/i.test(c)) || cols[0] || '';
            const preferredGroups = ['tissue_type', 'sample_type', 'definition', 'shortLetterCode', 'group', 'condition', 'subtype'];
            const groupGuess = h.differential_group_column_guess || preferredGroups.find(name => cols.includes(name)) || cols.find(c => /group|condition|disease|phenotype|subtype|class/i.test(c)) || '';
            const timeGuess = h.survival_time_column_guess || cols.find(c => /days_to_last|survival|follow/i.test(c)) || '';
            const startDateGuess = h.start_date_column_guess || cols.find(c => /diagnos|baseline|enroll|start|initial|birth/i.test(c) && /date|dt|time/i.test(c)) || '';
            const endDateGuess = h.end_date_column_guess || cols.find(c => /death|last.*follow|follow.*up|end|date/i.test(c) && c !== startDateGuess) || '';
            const eventGuess = h.event_column_guess || cols.find(c => /vital_status|event|death|status/i.test(c)) || '';
            const set = (id, value) => { const el = document.getElementById(id); if (el && value) el.value = value; };
            set('bulkSampleCol', sampleGuess); set('bulkGroupCol', groupGuess); set('bulkTimeCol', timeGuess); set('bulkStartDateCol', startDateGuess); set('bulkEndDateCol', endDateGuess); set('bulkEventCol', eventGuess); set('bulkSubgroupCol', groupGuess);
            set('bulkEventPositive', h.event_positive_guess || '');
            const geneInput = document.getElementById('bulkGeneCol'); if (geneInput) geneInput.value = c.gene_column || '';
            this._bulkUpdateGroupLevels();
            this._bulkUpdateEventPositive();
            const configFields = document.getElementById('bulkConfigFields'); if (configFields) configFields.style.display = 'none';
            const pendingType = this._bulkPendingAnalysisType;
            const analysisChoice = document.getElementById('bulkAnalysisChoice');
            if (analysisChoice) analysisChoice.style.display = pendingType ? 'none' : '';
            const uploadButton = document.getElementById('bulkUploadBtn'); if (uploadButton) uploadButton.textContent = this._bulkT('readComplete');
            this._bulkSetModeFields();
            await this.checkDataStatus();
            if (pendingType) this._openBulkAnalysisConfig(pendingType);
        } catch (e) {
            this._setBulkProgress('bulkUpload', 0, this._bulkT('readFailed'));
            if (info) info.textContent = `${this._bulkT('readFailed')}：${e.message}`;
        }
    }

    async _bulkUploadResultFile() {
        const file = this._bulkFiles.result || document.getElementById('bulkResultFile')?.files?.[0];
        const info = document.getElementById('bulkUploadInfo');
        if (!file) {
            if (info) info.textContent = this._bulkT('resultMissing');
            return;
        }
        const form = new FormData();
        form.append('session_id', this.app?.currentChatId || 'default');
        form.append('result_file', file);
        this._setBulkProgress('bulkUpload', 0, this._bulkT('prepareUpload'));
        if (info) info.textContent = this._bulkT('resultReading');
        try {
            const response = await this._uploadWithProgress('/api/bulk/result-upload', form, (loaded, total) => {
                const ratio = total ? loaded / total : 0;
                this._setBulkProgress('bulkUpload', ratio * 70, ratio >= 1 ? this._bulkT('readingStructure') : this._bulkT('uploadingFiles'));
            });
            const data = response.data || {};
            if (!response.ok) throw new Error(data.detail || this._bulkT('uploadFailed'));
            this._bulkResultPreview = data.result_preview || {};
            const preview = this._bulkResultPreview;
            const cols = preview.columns || [];
            this._bulkFillSelect('bulkResultGeneCol', cols);
            this._bulkFillSelect('bulkResultGroupCol', cols, true);
            this._bulkFillSelect('bulkResultEffectCol', cols);
            this._bulkFillSelect('bulkResultPvalueCol', cols, true);
            this._bulkFillSelect('bulkResultPadjCol', cols, true);
            this._bulkFillSelect('bulkResultDirectionCol', cols, true);
            const set = (id, value) => { const el = document.getElementById(id); if (el && value) el.value = value; };
            set('bulkResultGeneCol', preview.gene_column_guess || '');
            set('bulkResultGroupCol', preview.group_column_guess || '');
            this._bulkUpdateResultGroups();
            const resultType = document.getElementById('bulkResultAnalysisType')?.value || 'differential';
            set('bulkResultEffectCol', resultType === 'survival' ? preview.survival?.effect_column_guess : preview.differential?.effect_column_guess);
            set('bulkResultPvalueCol', preview.pvalue_column_guess || '');
            set('bulkResultPadjCol', preview.padj_column_guess || '');
            set('bulkResultDirectionCol', preview.direction_column_guess || '');
            this._setBulkProgress('bulkUpload', 100, this._bulkT('resultReadComplete'));
            if (info) info.textContent = this._bulkT('resultReadingSummary', { rows: preview.n_rows || 0, genes: preview.n_genes_guess || 0 });
            const resultConfig = document.getElementById('bulkResultConfigFields');
            if (resultConfig) resultConfig.style.display = '';
            const uploadButton = document.getElementById('bulkUploadBtn');
            if (uploadButton) uploadButton.textContent = this._bulkT('resultReadAgain');
            this._bulkSetResultEffectMetric();
            await this.checkDataStatus();
        } catch (e) {
            this._setBulkProgress('bulkUpload', 0, this._bulkT('readFailed'));
            if (info) info.textContent = `${this._bulkT('readFailed')}：${e.message}`;
        }
    }

    async _bulkConfigureResult() {
        const sid = this.app?.currentChatId || 'default';
        const body = {
            session_id: sid,
            analysis_type: document.getElementById('bulkResultAnalysisType')?.value || 'differential',
            dataset_description: (document.getElementById('bulkResultDatasetDesc')?.value || '').trim(),
            dataset_prompt: (document.getElementById('bulkResultDatasetPrompt')?.value || '').trim(),
            gene_col: document.getElementById('bulkResultGeneCol')?.value || '',
            effect_col: document.getElementById('bulkResultEffectCol')?.value || '',
            effect_metric: document.getElementById('bulkResultEffectMetric')?.value || 'log2fc',
            pvalue_col: document.getElementById('bulkResultPvalueCol')?.value || '',
            padj_col: document.getElementById('bulkResultPadjCol')?.value || '',
            direction_col: document.getElementById('bulkResultDirectionCol')?.value || '',
            group_col: document.getElementById('bulkResultGroupCol')?.value || '',
            group_values: Array.from(document.getElementById('bulkResultGroupValues')?.selectedOptions || [])
                .map(option => option.value).filter(Boolean),
        };
        const info = document.getElementById('bulkResultConfigInfo');
        const btn = document.getElementById('bulkResultConfigureBtn');
        if (btn) btn.disabled = true;
        try {
            const response = await fetch('/api/bulk/result-configure', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(body),
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || this._bulkT('resultConfigFailed'));
            const modal = document.getElementById('bulkUploadModal');
            if (modal) modal.classList.remove('active');
            this._setBulkProgress('apBulk', 100, this._bulkT('resultReady'));
            this._colsLoaded = true;
            await this.checkDataStatus();
            this.switchMode('table');
            await this._showBulkResultPicker(sid);
        } catch (e) {
            if (info) info.textContent = `${this._bulkT('resultConfigFailed')}：${e.message}`;
            if (btn) btn.disabled = false;
        }
    }

    _bulkUpdateGroupLevels() {
        const col = document.getElementById('bulkGroupCol')?.value || '';
        const values = (this._bulkPreview?.clinical?.values || {})[col] || [];
        this._bulkFillSelect('bulkControlLevel', values);
        this._bulkFillSelect('bulkCaseLevel', values);
        if (values.length > 1) {
            const control = values.find(value => /normal|control|healthy|untreated/i.test(value)) || values[0];
            const caseLevel = values.find(value => value !== control && /tumou?r|case|disease|treated|primary/i.test(value)) || values.find(value => value !== control) || values[1];
            document.getElementById('bulkControlLevel').value = control;
            document.getElementById('bulkCaseLevel').value = caseLevel;
        }
    }

    _bulkUpdateResultGroups() {
        const col = document.getElementById('bulkResultGroupCol')?.value || '';
        const select = document.getElementById('bulkResultGroupValues');
        if (!select) return;
        const previous = new Set(Array.from(select.selectedOptions || []).map(option => option.value));
        select.replaceChildren();
        const values = col ? (this._bulkResultPreview?.group_values || {})[col] || [] : [];
        values.forEach(value => {
            const option = this._bulkOption(String(value));
            option.selected = previous.has(option.value);
            select.appendChild(option);
        });
        select.disabled = !col || !values.length;
    }

    _bulkUpdateEventPositive() {
        const col = document.getElementById('bulkEventCol')?.value || '';
        const values = (this._bulkPreview?.clinical?.values || {})[col] || [];
        const input = document.getElementById('bulkEventPositive');
        if (!input || !values.length) return;
        const hints = this._bulkPreview?.clinical || {};
        const hinted = col === hints.event_column_guess ? hints.event_positive_guess : '';
        const positive = hinted || values.find(value => /dead|deceased|death|died|event|yes|true|^1$/i.test(String(value))) || '';
        if (positive) input.value = positive;
    }

    async _bulkConfigureAndRun() {
        const sid = this.app?.currentChatId || 'default';
        const type = document.getElementById('bulkAnalysisType')?.value || 'differential';
        const multi = id => Array.from(document.getElementById(id)?.selectedOptions || []).map(o => o.value).filter(Boolean);
        const body = {
            session_id: sid,
            analysis_type: type,
            dataset_description: (document.getElementById('bulkDatasetDesc')?.value || '').trim(),
            dataset_prompt: (document.getElementById('bulkDatasetPrompt')?.value || '').trim(),
            gene_col: document.getElementById('bulkGeneCol')?.value || '',
            sample_col: document.getElementById('bulkSampleCol')?.value || '',
            subgroup_col: document.getElementById('bulkSubgroupCol')?.value || '',
            all_genes: true,
        };
        if (type === 'differential') Object.assign(body, {
            group_col: document.getElementById('bulkGroupCol')?.value || '',
            control_level: document.getElementById('bulkControlLevel')?.value || '',
            case_level: document.getElementById('bulkCaseLevel')?.value || '',
            adjust_clinical: !!document.getElementById('bulkAdjustClinical')?.checked,
            covariates: document.getElementById('bulkAdjustClinical')?.checked ? multi('bulkCovariates') : [],
            method: document.getElementById('bulkDeMethod')?.value || 'deseq2',
        }); else Object.assign(body, {
            time_type: document.getElementById('bulkSurvivalTimeType')?.value || 'duration',
            time_col: document.getElementById('bulkTimeCol')?.value || '',
            start_date_col: document.getElementById('bulkStartDateCol')?.value || '',
            end_date_col: document.getElementById('bulkEndDateCol')?.value || '',
            event_col: document.getElementById('bulkEventCol')?.value || '',
            event_positive: document.getElementById('bulkEventPositive')?.value || '',
            expression_transform: document.getElementById('bulkTransform')?.value || 'vst',
            adjust_clinical: !!document.getElementById('bulkSurvivalAdjust')?.checked,
            covariates: document.getElementById('bulkSurvivalAdjust')?.checked ? multi('bulkSurvCovariates') : [],
        });
        const info = document.getElementById('bulkConfigInfo');
        const btn = document.getElementById('bulkRunBtn');
        if (btn) btn.disabled = true;
        try {
            let r = await fetch('/api/bulk/configure', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body) });
            let d = await r.json(); if (!r.ok) throw new Error(d.detail || this._bulkT('configFailed'));
            r = await fetch('/api/bulk/analyze', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({session_id:sid}) });
            d = await r.json(); if (!r.ok) throw new Error(d.detail || this._bulkT('analysisStartFailed'));
            this.app?._setInputLocked?.(true, this._bulkT('waitAnalysis'));
            const modal = document.getElementById('bulkUploadModal'); if (modal) modal.classList.remove('active');
            document.getElementById('bulkDifferentialConfigModal')?.classList.remove('active');
            document.getElementById('bulkSurvivalConfigModal')?.classList.remove('active');
            const panelStatus = document.getElementById('apBulkStatus');
            if (panelStatus) panelStatus.textContent = this._bulkT('analysisRunning');
            this._setBulkProgress('apBulk', 0, this._bulkT('preparingStats'));
            this._bulkPoll(sid);
        } catch (e) { if (info) info.textContent = `${this._bulkT('analysisStartFailed')}：${e.message}`; if (btn) btn.disabled = false; }
    }

    _bulkProgressText(rawPhase) {
        const phase = String(rawPhase || '').replace(/^\[bulk\](?:\s*\[\d+%\])?\s*/i, '').trim();
        const exact = {
            '准备读取原始数据': 'bulk.preparingStats',
            '读取原始 count 与临床表；上传阶段未做过滤或归一化': 'bulk.progressRaw',
            '原始 count 与临床变量已读取，开始统计建模': 'bulk.progressModeling',
            '准备统计分析': 'bulk.preparingStats',
            '准备选定表达项目': 'bulk.prepareSelected',
            '文件上传与结构读取完成': 'bulk.uploadComplete',
            '用户结果表结构读取完成': 'bulk.resultProgressStructure',
            '正在分析': 'bulk.analyzing',
            '读取选定表达项目的知识来源': 'bulk.progressSources',
            'GO / KEGG / GSEA / STRING 已完成，正在构建 RAG': 'bulk.progressEnrichmentDone',
            '整理 RAG 知识上下文': 'bulk.progressRagContext',
            '选定表达项目的 RAG 上下文已准备完成': 'bulk.progressRagReady',
        };
        if (exact[phase]) return this._t(exact[phase]);
        let match = phase.match(/^统计建模进行中（(.+)，已运行 (\d+) 秒）$/);
        if (match) return this._bulkT('progressModelingLive', { method: match[1], seconds: match[2] });
        match = phase.match(/^选定 (\d+) 个表达项目，开始并行执行 GO \/ KEGG \/ GSEA \/ STRING$/);
        if (match) return this._bulkT('progressSelected', { count: match[1] });
        match = phase.match(/^开始并行 RAG 检索选定表达项目（(\d+) 个）$/);
        if (match) return this._bulkT('progressRagStart', { count: match[1] });
        match = phase.match(/^RAG 检索选定表达项目 (\d+)\/(\d+)$/);
        if (match) return this._bulkT('progressRag', { done: match[1], total: match[2] });
        match = phase.match(/^富集完成：(.+?) \/ (.+)$/);
        if (match) return this._bulkT('progressEnrichmentItem', { set: match[1], modality: match[2] });
        match = phase.match(/^统计分析完成：(\d+) 个表达项目；右侧筛选已就绪$/);
        if (match) return this._bulkT('analysisCompleteDetail', { count: match[1], ready: this._bulkT('filterReady') });
        match = phase.match(/^用户结果表已载入：(\d+) 个表达项目；右侧筛选已就绪$/);
        if (match) return this._bulkT('resultReadyDetail', { count: match[1], ready: this._bulkT('filterReady') });
        return phase;
    }

    async _bulkPoll(sessionId) {
        if (this._bulkPollSessionId === sessionId) return;
        this._bulkPollSessionId = sessionId;
        const pollGeneration = this._bulkPollGeneration;
        const isCurrentPoll = () => (
            this._bulkPollGeneration === pollGeneration &&
            this._bulkPollSessionId === sessionId
        );
        const info = document.getElementById('apBulkStatus');
        const tick = async () => {
            if (!isCurrentPoll()) return;
            try {
                const response = await fetch(`/api/bulk/status/${encodeURIComponent(sessionId)}`);
                const data = await response.json();
                if (!isCurrentPoll()) return;
                const latest = (data.progress || []).slice(-1)[0] || '';
                const phase = this._bulkProgressText(data.progress_phase || latest || '正在分析');
                this._setBulkProgress('apBulk', data.progress_percent ?? 0, phase);
                if (info) info.textContent = phase;
                if (['ready_for_filter','ready','ready_without_rag','error'].includes(data.status)) {
                    const modal = document.getElementById('bulkUploadModal'); if (modal) modal.classList.remove('active');
                    if (data.status === 'error') this.app.showNotification(this._bulkT('analysisFailed', { error: data.error || '' }), 'error');
                    else {
                        this.app?._setInputLocked?.(false);
                        this._setBulkProgress('apBulk', 100, this._bulkT('analysisComplete'));
                        this.app.showNotification(this._bulkT('filterReady'), 'success');
                        this._colsLoaded = false;
                        await this.checkDataStatus();
                        this.switchMode('table');
                        await this._showBulkResultPicker(sessionId);
                    }
                    this._bulkPollSessionId = null;
                    return;
                }
                if (isCurrentPoll()) setTimeout(tick, 2000);
            } catch (_) {
                if (isCurrentPoll()) setTimeout(tick, 3000);
            }
        };
        tick();
    }

    async _showBulkResultPicker(sessionId) {
        const intro = document.getElementById('apBulkIntro');
        if (!intro) return;
        try {
            const response = await fetch(`/api/bulk/result/${encodeURIComponent(sessionId)}?include_rows=true`);
            const data = await response.json();
            this._bulkResult = data.result || {};
            this._bulkFilteredRows = Array.isArray(this._bulkResult.result) ? this._bulkResult.result.slice() : [];
            const persistedGenes = Array.isArray(this._bulkPersistedSelectedGenes)
                ? this._bulkPersistedSelectedGenes.map(gene => String(gene)).filter(Boolean)
                : [];
            this._bulkSelectedGenes = new Set(persistedGenes);
            this._bulkRestoredSelectionPending = persistedGenes.length > 0;
            // Let the current filter establish the visible selection once;
            // this also removes persisted genes hidden by the current filter.
            this._bulkSelectionInitialized = false;
            this._renderBulkResultFilters(sessionId);
        } catch (_) { /* Results remain available from the API even if the picker cannot render. */ }
    }

    _renderBulkResultFilters(sessionId) {
        const intro = document.getElementById('apBulkIntro');
        if (!intro || !this._bulkResult) return;
        const currentCard = document.getElementById('apBulkResultFilters');
        if (currentCard) {
            this._bulkFilterState = {
                sigMetric: currentCard.querySelector('#bulkFilterSigMetric')?.value || 'padj',
                sigThreshold: currentCard.querySelector('#bulkFilterSigThreshold')?.value,
                effectMetric: currentCard.querySelector('#bulkFilterEffectMetric')?.value,
                effectThreshold: currentCard.querySelector('#bulkFilterEffectThreshold')?.value,
                direction: currentCard.querySelector('#bulkFilterDirection')?.value || 'all',
                topN: currentCard.querySelector('#bulkFilterTopN')?.value,
            };
        }
        const savedFilter = this._bulkFilterState || {};
        document.getElementById('apBulkResultFilters')?.remove();
        document.getElementById('apBulkRagControls')?.remove();

        const result = this._bulkResult;
        const isSurvival = result.analysis_type === 'survival';
        const rows = Array.isArray(result.result) ? result.result : [];
        // When a persisted chat is reopened, keep the N control aligned with
        // the exact selected cohort that was handed off to RAG.  Otherwise
        // the summary can correctly show 500 while the editable control still
        // displays its fresh-session default of 1000.
        const persistedSelectionCount = this._bulkRestoredSelectionPending
            ? new Set(this._bulkPersistedSelectedGenes || []).size
            : 0;
        const initialTopN = savedFilter.topN !== undefined && savedFilter.topN !== ''
            ? Math.max(0, Number.parseInt(savedFilter.topN, 10) || 0)
            : (persistedSelectionCount > 0 ? persistedSelectionCount : 1000);
        const initialSigThreshold = Number.isFinite(Number(savedFilter.sigThreshold))
            ? Number(savedFilter.sigThreshold)
            : 0.05;
        const initialEffectThreshold = Number.isFinite(Number(savedFilter.effectThreshold))
            ? Number(savedFilter.effectThreshold)
            : (isSurvival ? 0 : 0.5);
        const hasNumericValue = value => (
            value !== null && value !== undefined && value !== '' && Number.isFinite(Number(value))
        );
        const hasSignificance = rows.some(row => hasNumericValue(row.padj) || hasNumericValue(row.pvalue));
        const defaultSigMetric = result.metadata?.significance_metric === 'pvalue'
            ? 'pvalue'
            : (rows.some(row => hasNumericValue(row.padj)) ? 'padj' : 'pvalue');
        const filterCard = document.createElement('div');
        filterCard.id = 'apBulkResultFilters';
        filterCard.className = 'bulk-result-card';
        filterCard.innerHTML = `
            <div class="bulk-result-title">${this._bulkT('filterTitle')}</div>
            <div class="bulk-result-copy">${this._bulkT('filterCopy')}</div>
            <div class="bulk-filter-grid">
                <label id="bulkFilterSigMetricWrap" style="${hasSignificance ? '' : 'display:none'}"><span class="bulk-filter-label">${this._bulkT('significanceMetric')}</span>
                    <select id="bulkFilterSigMetric" class="form-control"><option value="padj">${this._bulkT('fdrOption')}</option><option value="pvalue">${this._bulkT('pValueOption')}</option></select>
                </label>
                <label id="bulkFilterSigThresholdWrap" style="${hasSignificance ? '' : 'display:none'}"><span class="bulk-filter-label">${this._bulkT('significanceThreshold')}</span>
                    <input id="bulkFilterSigThreshold" class="form-control" type="number" min="0" max="1" step="0.001" value="${initialSigThreshold}">
                </label>
                <label><span class="bulk-filter-label">${this._bulkT(isSurvival ? 'effectMetric' : 'changeMetric')}</span>
                    <select id="bulkFilterEffectMetric" class="form-control">${isSurvival ? `<option value="HR">HR</option><option value="coef">coef</option>` : `<option value="log2FoldChange">${this._bulkT('changeMetric')}</option>`}</select>
                </label>
                <label><span class="bulk-filter-label">${this._bulkT(isSurvival ? 'effectThresholdHr' : 'effectThresholdFc')}</span>
                    <input id="bulkFilterEffectThreshold" class="form-control" type="number" min="0" step="0.1" value="${initialEffectThreshold}">
                </label>
                <label><span class="bulk-filter-label">${this._bulkT('direction')}</span>
                    <select id="bulkFilterDirection" class="form-control"><option value="all">${this._bulkT('all')}</option><option value="up">${this._bulkT('upHighRisk')}</option><option value="down">${this._bulkT('downLowRisk')}</option></select>
                </label>
                <label data-i18n="bulk.topN"><span class="bulk-filter-label">${this._bulkT('topN')}</span>
                    <input id="bulkFilterTopN" class="form-control" type="number" min="0" step="1" value="${initialTopN}" placeholder="${this._bulkT('topNPlaceholder')}" data-i18n-placeholder="bulk.topNPlaceholder">
                    <small class="form-hint" data-i18n="bulk.topNHint">${this._bulkT('topNHint')}</small>
                </label>
            </div>
            <div class="bulk-filter-actions"><button id="bulkResetFilter" class="btn btn-secondary" type="button">${this._bulkT('resetFilter')}</button><span class="bulk-filter-live">${this._bulkT('liveUpdate')}</span></div>
            <div id="bulkFilterSummary" class="bulk-filter-summary"></div>
            <div id="bulkGeneEstimate" class="bulk-gene-estimate"></div>
            <div id="bulkRagCostEstimate" class="bulk-rag-cost-estimate"></div>
            <div id="bulkFilterTable" class="bulk-filter-table"></div>`;
        intro.appendChild(filterCard);
        this._loadRagCostEstimate();
        const sigMetric = document.getElementById('bulkFilterSigMetric');
        if (sigMetric) sigMetric.value = savedFilter.sigMetric || defaultSigMetric;
        const effectMetric = document.getElementById('bulkFilterEffectMetric');
        if (effectMetric && savedFilter.effectMetric) effectMetric.value = savedFilter.effectMetric;
        const direction = document.getElementById('bulkFilterDirection');
        if (direction) direction.value = savedFilter.direction || 'all';

        const readFilterState = () => ({
            sigMetric: document.getElementById('bulkFilterSigMetric')?.value || 'padj',
            sigThreshold: document.getElementById('bulkFilterSigThreshold')?.value,
            effectMetric: document.getElementById('bulkFilterEffectMetric')?.value,
            effectThreshold: document.getElementById('bulkFilterEffectThreshold')?.value,
            direction: document.getElementById('bulkFilterDirection')?.value || 'all',
            topN: document.getElementById('bulkFilterTopN')?.value,
        });
        const apply = () => {
            this._bulkFilterState = readFilterState();
            this._applyBulkResultFilters();
            this._localizeBulkFilterCard();
        };
        ['bulkFilterSigMetric', 'bulkFilterSigThreshold', 'bulkFilterEffectMetric', 'bulkFilterEffectThreshold', 'bulkFilterDirection']
            .forEach(id => document.getElementById(id)?.addEventListener('input', apply));
        ['bulkFilterSigMetric', 'bulkFilterEffectMetric', 'bulkFilterDirection']
            .forEach(id => document.getElementById(id)?.addEventListener('change', apply));
        document.getElementById('bulkFilterTopN')?.addEventListener('input', () => {
            this._bulkSelectionInitialized = false;
            apply();
        });
        document.getElementById('bulkResetFilter')?.addEventListener('click', () => {
            document.getElementById('bulkFilterSigMetric').value = 'padj';
            document.getElementById('bulkFilterSigThreshold').value = '0.05';
            document.getElementById('bulkFilterEffectThreshold').value = isSurvival ? '0' : '0.5';
            document.getElementById('bulkFilterDirection').value = 'all';
            document.getElementById('bulkFilterTopN').value = '1000';
            this._bulkSelectionInitialized = false;
            apply();
        });
        apply();
        this._localizeBulkFilterCard();
    }

    _updateBulkGeneEstimate() {
        const estimate = document.getElementById('bulkGeneEstimate');
        if (!estimate) return;
        const selected = this._bulkSelectedGenes?.size || 0;
        if (!selected) {
            estimate.textContent = this._bulkT('estimateNone');
            return;
        }
        const submitted = Math.min(selected, 2000);
        const calibration = this._ragCostEstimate?.seconds_per_item || { low: 3, high: 8 };
        const low = Math.max(1, Math.round(submitted * Number(calibration.low || 3)));
        const high = Math.max(low, Math.round(submitted * Number(calibration.high || 8)));
        const cap = selected > submitted ? this._bulkT('estimateCap', { submitted }) : '';
        estimate.textContent = this._bulkT('estimate', { selected, low, high, cap });
    }

    _formatRagDuration(seconds) {
        const value = Math.max(0, Number(seconds) || 0);
        if (value < 60) return `${Math.round(value)}s`;
        const minutes = Math.floor(value / 60);
        const remain = Math.round(value % 60);
        return `${minutes}m ${remain}s`;
    }

    _formatRagTokens(value) {
        if (!value || value.status === 'not_measured') return this._bulkT('costTokensUnavailable');
        const formatRange = part => {
            if (!part) return '—';
            const low = Number(part.low || 0);
            const high = Number(part.high || 0);
            if (low === high) return low.toLocaleString();
            return `${low.toLocaleString()}–${high.toLocaleString()}`;
        };
        const prefix = value.status === 'measured'
            ? this._bulkT('costTokensMeasured')
            : this._bulkT('costTokensEstimated');
        return `${prefix}: ${formatRange(value.total_tokens)} total; ${formatRange(value.prompt_tokens)} in / ${formatRange(value.completion_tokens)} out`;
    }

    async _loadRagCostEstimate() {
        const panel = document.getElementById('bulkRagCostEstimate');
        if (!panel) return;
        try {
            const response = await fetch('/api/rag-cost-estimate');
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || 'cost estimate failed');
            this._ragCostEstimate = data;
            this._renderRagCostEstimate(data);
            this._updateBulkGeneEstimate();
        } catch (error) {
            panel.textContent = this._bulkT('costUnavailable');
        }
    }

    _renderRagCostEstimate(data) {
        const panel = document.getElementById('bulkRagCostEstimate');
        if (!panel || !data) return;
        const rows = Array.isArray(data.estimates) ? data.estimates : [];
        const calibration = /completed bulk RAG manifests/i.test(String(data.calibration || ''))
            ? this._bulkT('costCalibrationCompleted')
            : this._bulkT('costCalibrationBaseline');
        const sourceCount = Number(data.source_query_units_per_item || 0);
        const literatureCount = Number(data.literature_queries_per_item || 0);
        const tokenNote = this._bulkT('costTokenNote')
            .replace('{source}', String(sourceCount))
            .replace('{literature}', String(literatureCount));
        panel.innerHTML = `
            <div class="bulk-rag-cost-title">${this._bulkT('costTitle')}</div>
            <div class="bulk-rag-cost-note">${this._bulkT('costCalibration').replace('{calibration}', calibration)}</div>
            <div class="bulk-rag-cost-scroll"><table class="bulk-rag-cost-table"><thead><tr>
                <th>${this._bulkT('costHeaderItems')}</th><th>${this._bulkT('costHeaderTime')}</th>
                <th>${this._bulkT('costHeaderSources')}</th><th>${this._bulkT('costHeaderLiterature')}</th>
                <th>${this._bulkT('costHeaderTokens')}</th>
            </tr></thead><tbody>${rows.map(row => `<tr>
                <td>${Number(row.selected_items).toLocaleString()}</td>
                <td>${this._formatRagDuration(row.low_seconds)}–${this._formatRagDuration(row.high_seconds)}</td>
                <td>${Number(row.source_query_units).toLocaleString()}</td>
                <td>${Number(row.literature_queries).toLocaleString()}</td>
                <td>${this._formatRagTokens(row.answer_model_tokens)}</td>
            </tr>`).join('')}</tbody></table></div>
            <div class="bulk-rag-cost-note">${tokenNote}</div>`;
    }

    getBulkSelectedGenes() {
        return Array.from(this._bulkSelectedGenes || []);
    }

    toggle() { this.isOpen ? this.close() : this.open(); }

    open() {
        document.getElementById('analysisPanel').classList.add('open');
        this.isOpen = true;
        // Do NOT call checkDataStatus() here — it would re-run loadAvailableGroups
        // if _colsLoaded were somehow false, potentially overwriting user edits.
        // Status was already polled on init and will poll every 60 s.
    }

    close() {
        document.getElementById('analysisPanel').classList.remove('open');
        this.isOpen = false;
    }

    async checkDataStatus() {
        try {
            const sid = this.app?.currentChatId || 'default';
            const r = await fetch(`/api/status?session_id=${encodeURIComponent(sid)}`);
            const data = await r.json();
            const infoEl = document.getElementById('apDataInfo');
            if (data.data_loaded) {
                const bulkStatus = data.bulk_status || null;
                const bulkReady = ['ready_for_filter', 'ready', 'ready_without_rag'].includes(bulkStatus);
                const bulkRunning = ['queued', 'analyzing', 'enriching', 'rag_building'].includes(bulkStatus);
                const bulkInputBlocked = (data.data_mode || 'singlecell') === 'table' && !!bulkStatus && !bulkReady;
                const datasetConfigBlocked = data.analysis_configured === false;
                this._dataStatus = {
                    data_loaded: true,
                    data_mode: data.data_mode || 'singlecell',
                    analysis_configured: data.analysis_configured !== false,
                    bulk_status: bulkStatus,
                    bulk_ready: bulkReady,
                    bulk_running: bulkRunning,
                };
                this._geneIntersectionList = this._parseGeneIntersection(data.gene_intersection || []);
                const inputBlocked = bulkInputBlocked || datasetConfigBlocked;
                this.app?._setInputLocked?.(
                    inputBlocked,
                    bulkInputBlocked
                        ? this._bulkT('waitAnalysis')
                        : (datasetConfigBlocked ? this._t('analysisPanel.waitConfig') : '')
                );
                const modeText = this._dataStatus.data_mode === 'table'
                    ? this._t('analysisPanel.modeTableShort')
                    : this._t('analysisPanel.modeSingleShort');
                const recordUnit = data.data_mode === 'table'
                    ? this._t('analysisPanel.rows')
                    : this._t('analysisPanel.cells');
                const geneUnit = data.data_mode === 'table'
                    ? this._t('analysisPanel.geneProtein')
                    : this._t('analysisPanel.genes');
                infoEl.innerHTML = `<span style="color:var(--accent-secondary)">&#x2713;</span> [${modeText}] ${(data.cells||0).toLocaleString()} ${recordUnit} &middot; ${(data.genes||0).toLocaleString()} ${geneUnit}`;
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

                this._bulkPersistedSelectedGenes = Array.isArray(data.selected_genes)
                    ? data.selected_genes.map(gene => String(gene)).filter(Boolean)
                    : [];
                if (this._dataStatus.data_mode === 'table') {
                    if (this.currentMode !== 'table') this.switchMode('table');
                    if (bulkReady && this._bulkRestoredSessionId !== sid) {
                        this._bulkRestoredSessionId = sid;
                        await this._showBulkResultPicker(sid);
                    } else if (bulkRunning && this._bulkPollSessionId !== sid) {
                        this._bulkPoll(sid);
                    }
                }
            } else {
                this._dataStatus = { data_loaded: false, data_mode: null };
                this._geneIntersectionList = [];
                this.app?._setInputLocked?.(false, '');
                infoEl.textContent = this._t('analysisPanel.noData');
                const clearBtn = document.getElementById('apClearDataBtn');
                if (clearBtn) clearBtn.style.display = 'none';
                this._colsLoaded = false;
                this.matrixData = null;
                this._userLabels = { celltype: {}, group: {} };
                this._clearLabelsStorage();
                this._resetSelectorsToUnused();
                this._bulkRestoredSessionId = null;
                this._bulkPollGeneration += 1;
                this._bulkPollSessionId = null;
                this._resetBulkUI();
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
                ctSel.innerHTML = `<option value="">${this._t('analysisPanel.notUsed')}</option>` +
                    cols.map(c => `<option value="${c}"${c === savedCt ? ' selected' : ''}>${c} (${(groups[c]||[]).slice(0,4).join('/')}${(groups[c]||[]).length > 4 ? '…' : ''})</option>`).join('');
                if (!savedCt && cols.length) {
                    ctSel.value = cols.find(c => /cell|type|cluster/i.test(c)) || cols[0];
                }
            }

            const grpSel = document.getElementById('apGroupColSelect');
            if (grpSel) {
                const savedGrp = grpSel.value;
                grpSel.innerHTML = `<option value="">${this._t('analysisPanel.notUsed')}</option>` +
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
                    value="${saved}" placeholder="${this._t('analysisPanel.displayName')}"
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
        const topNRaw = document.getElementById('apTableTopN')?.value || '0';
        const topNParsed = Number.parseInt(topNRaw, 10);
        const topN = Number.isFinite(topNParsed) ? Math.max(0, topNParsed) : 0;

        if (!geneCol) {
            infoEl.textContent = this._t('analysisPanel.filteredGenesEmpty');
            return;
        }

        const formData = new FormData();
        formData.append('session_id', this.app?.currentChatId || 'default');
        formData.append('gene_col', geneCol);
        if (exprCol) formData.append('expr_col', exprCol);
        if (exprThreshRaw) formData.append('expr_thresh', exprThreshRaw);
        if (sigCol) formData.append('sig_col', sigCol);
        if (sigThreshRaw) formData.append('sig_thresh', sigThreshRaw);
        formData.append('n_top_genes', String(topN));

        try {
            const response = await fetch('/api/csv-gene-count', { method: 'POST', body: formData });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || this._t('analysisPanel.countFailed'));
            infoEl.textContent = this._t('analysisPanel.filteredGenes')
                .replace('{filtered}', (data.n_genes_conditioned ?? data.n_genes ?? 0).toLocaleString())
                .replace('{selected}', (data.n_genes || 0).toLocaleString())
                .replace('{rows}', (data.n_rows_filtered || 0).toLocaleString());
        } catch (_) {
            infoEl.textContent = this._t('analysisPanel.filteredGenesFailed');
        }
    }

    async setTableFile(file) {
        this._pendingTableFile = file;
        const promptEl = document.getElementById('apTableDatasetPrompt');
        if (promptEl) promptEl.value = '';
        const errEl = document.getElementById('apTableError');
        const infoEl = document.getElementById('apTableInfo');
        if (errEl) { errEl.style.display = 'none'; errEl.textContent = ''; }
        if (infoEl) infoEl.textContent = this._t('analysisPanel.reading').replace('{file}', file.name);

        const formData = new FormData();
        formData.append('file', file);
        formData.append('session_id', this.app?.currentChatId || 'default');

        try {
            const response = await fetch('/api/upload-csv', { method: 'POST', body: formData });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || this._t('analysisPanel.uploadFailed'));

            const cols = data.columns || [];
            const fill = (id, allowNone = true) => {
                const sel = document.getElementById(id);
                if (!sel) return;
                sel.innerHTML = `<option value="">${allowNone ? this._t('analysisPanel.notUsed') : this._t('analysisPanel.selectColumn')}</option>` +
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
            if (infoEl) {
                infoEl.textContent = this._t('analysisPanel.fileSummary')
                    .replace('{file}', file.name)
                    .replace('{rows}', String(data.n_rows))
                    .replace('{cols}', String(cols.length));
            }

            // 与单细胞一致：文件上传后即视为已上传（自动应用当前配置）
            await this.confirmTableUpload();
        } catch (e) {
            if (errEl) { errEl.textContent = e.message; errEl.style.display = 'block'; }
            if (infoEl) infoEl.textContent = this._t('analysisPanel.tableReadFailed');
        }
    }

    async confirmTableUpload() {
        const status = this._dataStatus || {};
        if (status.data_loaded && status.data_mode && status.data_mode !== 'table') {
            this.app.showNotification(this._t('analysisPanel.singleDataConflict'), 'error');
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
        const topNRaw = document.getElementById('apTableTopN')?.value || '0';
        const topNParsed = Number.parseInt(topNRaw, 10);
        const topN = Number.isFinite(topNParsed) ? Math.max(0, topNParsed) : 0;
        const datasetDesc = (document.getElementById('apTableDatasetDesc')?.value || '').trim();
        const datasetPrompt = (document.getElementById('apTableDatasetPrompt')?.value || '').trim();
        const errEl = document.getElementById('apTableError');

        if (!file || !geneCol) {
            if (errEl) { errEl.textContent = this._t('analysisPanel.selectFileGene'); errEl.style.display = 'block'; }
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
        if (datasetPrompt) formData.append('dataset_prompt', datasetPrompt);
        formData.append('n_top_genes', String(topN));

        try {
            const response = await fetch('/api/configure-csv', { method: 'POST', body: formData });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || this._t('analysisPanel.configFailed'));
            this.app.showNotification(
                this._t('analysisPanel.tableUploadSuccess').replace('{count}', String(data.n_genes)),
                'success'
            );
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
        return Math.max(5, Math.min(2000, n));
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
                        html += `<div style="margin-bottom:.5rem;font-size:.78rem;color:var(--text-secondary)">${this._t('analysisPanel.celltypeTopGenes').replace('{count}', String(topN))}</div>`;
                        html += '<div style="overflow-x:auto">';
                        html += '<table style="width:100%;font-size:.72rem;border-collapse:collapse">';
                        html += `<thead><tr><th style="text-align:left;padding:2px 6px;color:var(--text-tertiary)">${this._t('analysisPanel.celltype')}</th>`;
                        html += `<th style="text-align:left;padding:2px 6px;color:var(--text-tertiary)">${this._t('analysisPanel.topGeneLabel')}</th></tr></thead><tbody>`;
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
                        html += `<div style="margin:.5rem 0 .3rem;font-size:.78rem;color:var(--text-secondary)">${this._t('analysisPanel.phenotypeTopGenes').replace('{count}', String(topN))}</div>`;
                        html += '<div style="overflow-x:auto">';
                        html += '<table style="width:100%;font-size:.72rem;border-collapse:collapse">';
                        html += `<thead><tr><th style="text-align:left;padding:2px 6px;color:var(--text-tertiary)">${this._t('analysisPanel.group')}</th>`;
                        html += `<th style="text-align:left;padding:2px 6px;color:var(--text-tertiary)">${this._t('analysisPanel.topGeneLabel')}</th></tr></thead><tbody>`;
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
            if (preview) preview.innerHTML = html || `<span style="color:var(--text-tertiary);font-size:.78rem">${this._t('analysisPanel.noPreview')}</span>`;
            if (section) section.style.display = html ? 'block' : 'none';
            this._refreshGeneIntersectionSummary();
        } catch(e) {
            console.error('loadMatrix error:', e);
        }
    }

    async runAnalysis() {
        const status = this._dataStatus || {};
        if (status.data_loaded && status.data_mode && status.data_mode !== 'singlecell') {
            this.app.showNotification(this._t('analysisPanel.tableDataConflict'), 'error');
            return;
        }

        const ctCol  = document.getElementById('apCelltypeColSelect')?.value || '';
        const grpCol = document.getElementById('apGroupColSelect')?.value || '';
        const runBtn = document.getElementById('apRunBtn');
        const topGenesN = this._getTopGenesN();
        const celltypeLabels = this.getLabelMap('celltype');
        const groupLabels    = this.getLabelMap('group');

        if (!ctCol && !grpCol) {
            alert(this._t('analysisPanel.selectAnalysisCol'));
            return;
        }

        runBtn.disabled = true;
        runBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="animation:spin 1s linear infinite"><circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="10"/></svg> ${this._t('analysisPanel.analyzing')}`;

        try {
            const cfgResp = await fetch('/api/configure-dataset', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.app?.currentChatId || 'default',
                    celltype_col: ctCol,
                    group_col: grpCol,
                    n_top_genes: topGenesN,
                    gene_intersection: this._geneIntersectionList || [],
                    celltype_labels: celltypeLabels,
                    group_labels: groupLabels,
                    dataset_description: (document.getElementById('apDatasetDesc')?.value || '').trim(),
                    dataset_prompt: (document.getElementById('apDatasetPrompt')?.value || '').trim(),
                }),
            });
            if (!cfgResp.ok) {
                const err = await cfgResp.json().catch(() => ({}));
                throw new Error(err.detail || this._t('analysisPanel.configFailed'));
            }

            const messageInput = document.getElementById('messageInput');
            if (messageInput) {
                this.app.navigateToChat();
                // Agentic RAG: no offline KB build needed — queries are answered on demand
                this.app._setInputLocked(false, '');
                this.app.showNotification(this._t('analysisPanel.ready'), 'success');
            }
        } catch(e) {
            alert(`${this._t('analysisPanel.startFailed')}: ${e.message}`);
        } finally {
            runBtn.disabled = false;
            runBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg> ${this._t('analysisPanel.startAnalysis')}`;
        }
    }
    // Gene-level filtering is the single source of truth for the bulk picker.
    // Keep these methods after the legacy renderer so reopened sessions and
    // duplicate result rows follow the same expression-item semantics.
    _formatDisplayedNumber(value) {
        if (value === null || value === undefined || value === '') return '—';
        const numeric = typeof value === 'number' ? value : Number(String(value).trim());
        if (!Number.isFinite(numeric)) return String(value);
        if (numeric === 0) return '0';
        const formatted = numeric.toPrecision(2);
        if (!/[eE]/.test(formatted)) {
            return formatted
                .replace(/(\.\d*?[1-9])0+$/, '$1')
                .replace(/\.0+$/, '');
        }
        return formatted
            .replace(/\.0+(?=e)/i, '')
            .replace(/e\+?(-?)0+(\d+)/i, 'e$1$2');
    }

    _bulkDisplayValue(value, numeric = false) {
        if (value === null || value === undefined || value === '') return '—';
        return numeric ? this._formatDisplayedNumber(value) : String(value);
    }

    _bulkGeneKey(row) {
        return String(row?.gene || '').trim();
    }

    _bulkUniqueRows(rows) {
        const seen = new Set();
        return (Array.isArray(rows) ? rows : []).filter(row => {
            const gene = this._bulkGeneKey(row);
            if (!gene || seen.has(gene)) return false;
            seen.add(gene);
            return true;
        });
    }

    _bulkUniqueGeneCount(rows) {
        return this._bulkUniqueRows(rows).length;
    }

    _applyBulkResultFilters() {
        const result = this._bulkResult || {};
        const rows = Array.isArray(result.result) ? result.result : [];
        const sigKey = document.getElementById('bulkFilterSigMetric')?.value || 'padj';
        const sigThreshold = Number(document.getElementById('bulkFilterSigThreshold')?.value || 0.05);
        const effectKey = document.getElementById('bulkFilterEffectMetric')?.value || 'log2FoldChange';
        const effectThreshold = Math.max(0, Number(document.getElementById('bulkFilterEffectThreshold')?.value || 0));
        const direction = document.getElementById('bulkFilterDirection')?.value || 'all';
        const topNRaw = Number.parseInt(document.getElementById('bulkFilterTopN')?.value || '1000', 10);
        const topN = Number.isFinite(topNRaw) ? Math.max(0, topNRaw) : 0;
        const intersection = this._getGeneIntersectionSet();
        const hasNumericValue = value => (
            value !== null && value !== undefined && value !== '' && Number.isFinite(Number(value))
        );
        const hasSelectedSignificance = rows.some(item => hasNumericValue(item[sigKey]));
        const fallbackSigKey = sigKey === 'padj' ? 'pvalue' : 'padj';
        const activeSigKey = hasSelectedSignificance ? sigKey : fallbackSigKey;
        const hasSignificance = rows.some(item => hasNumericValue(item[activeSigKey]));
        const filtered = rows.filter(row => {
            const gene = this._bulkGeneKey(row);
            if (intersection.size && !intersection.has(this._geneIntersectionKey(gene))) return false;
            const sig = hasNumericValue(row[activeSigKey]) ? Number(row[activeSigKey]) : NaN;
            const effect = hasNumericValue(row[effectKey]) ? Number(row[effectKey]) : NaN;
            if ((hasSignificance && (!Number.isFinite(sig) || sig > sigThreshold)) || !Number.isFinite(effect)) return false;
            const magnitude = effectKey === 'HR'
                ? Math.abs(Math.log(Math.max(effect, 1e-12)))
                : Math.abs(effect);
            if (magnitude < effectThreshold) return false;
            if (direction === 'up') return row.direction === 'up' || row.direction === 'high_risk' || (effectKey === 'HR' && effect >= 1);
            if (direction === 'down') return row.direction === 'down' || row.direction === 'low_risk' || (effectKey === 'HR' && effect < 1);
            return true;
        });
        this._bulkFilteredRows = filtered;
        const visibleRows = this._bulkUniqueRows(filtered);
        const visibleGenes = visibleRows.map(row => this._bulkGeneKey(row));
        const selectionGenes = topN > 0 ? visibleGenes.slice(0, topN) : visibleGenes;

        if (!this._bulkSelectionInitialized) {
            const persistedGenes = new Set(
                Array.isArray(this._bulkPersistedSelectedGenes)
                    ? this._bulkPersistedSelectedGenes.map(gene => String(gene).trim()).filter(Boolean)
                    : []
            );
            const persistedVisibleGenes = selectionGenes.filter(gene => persistedGenes.has(gene));
            // A newly completed result has no persisted handoff yet.  Also
            // guard against a stale handoff from a previous result: if none
            // of its IDs occur in the current result, start from the visible
            // filtered set instead of showing “已选 0 个”.
            const restorePersisted = this._bulkRestoredSelectionPending === true && persistedVisibleGenes.length > 0;
            this._bulkSelectedGenes = restorePersisted
                ? new Set(persistedVisibleGenes)
                : new Set(selectionGenes);
            this._bulkRestoredSelectionPending = false;
            this._bulkSelectionInitialized = true;
        } else {
            const visibleSet = new Set(visibleGenes);
            this._bulkSelectedGenes = new Set(
                Array.from(this._bulkSelectedGenes || []).filter(gene => visibleSet.has(gene))
            );
        }

        const setSummary = () => {
            const summary = document.getElementById('bulkFilterSummary');
            if (summary) {
                summary.textContent = this._bulkT('filterSummary', {
                    filtered: visibleGenes.length.toLocaleString(),
                    total: this._bulkUniqueGeneCount(rows).toLocaleString(),
                    selected: this._bulkSelectedGenes.size.toLocaleString(),
                });
            }
            this._updateBulkGeneEstimate();
        };
        setSummary();

        const table = document.getElementById('bulkFilterTable');
        if (!table) return;
        table.replaceChildren();
        if (!visibleRows.length) {
            table.textContent = this._bulkT('noResults');
            return;
        }

        const selectionBar = document.createElement('div');
        selectionBar.className = 'bulk-filter-actions';
        selectionBar.innerHTML = '<button id="bulkSelectFiltered" class="btn btn-secondary" type="button"></button><button id="bulkClearSelected" class="btn btn-secondary" type="button"></button>';
        selectionBar.querySelector('#bulkSelectFiltered')?.addEventListener('click', () => {
            this._bulkSelectedGenes = new Set(selectionGenes);
            this._renderBulkSelectionSummary();
            table.querySelectorAll('input[data-bulk-gene]').forEach(input => {
                input.checked = this._bulkSelectedGenes.has(input.dataset.bulkGene || '');
            });
        });
        selectionBar.querySelector('#bulkClearSelected')?.addEventListener('click', () => {
            this._bulkSelectedGenes.clear();
            this._renderBulkSelectionSummary();
            table.querySelectorAll('input[data-bulk-gene]').forEach(input => { input.checked = false; });
        });
        table.appendChild(selectionBar);

        const tableEl = document.createElement('table');
        tableEl.innerHTML = '<thead><tr><th></th><th></th><th></th><th></th><th></th><th></th><th></th></tr></thead>';
        const tbody = document.createElement('tbody');
        visibleRows.slice(0, 100).forEach(row => {
            const gene = this._bulkGeneKey(row);
            const tr = document.createElement('tr');
            const selectCell = document.createElement('td');
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.dataset.bulkGene = gene;
            checkbox.checked = this._bulkSelectedGenes.has(gene);
            checkbox.addEventListener('change', () => {
                if (checkbox.checked) this._bulkSelectedGenes.add(gene);
                else this._bulkSelectedGenes.delete(gene);
                this._renderBulkSelectionSummary();
            });
            selectCell.appendChild(checkbox);
            tr.appendChild(selectCell);
            [row.gene, row.group, row[effectKey], row.pvalue, row.padj, row.direction].forEach((value, index) => {
                const td = document.createElement('td');
                td.textContent = this._bulkDisplayValue(value, index > 1 && index < 5);
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
        tableEl.appendChild(tbody);
        table.appendChild(tableEl);
        if (visibleRows.length > 100) {
            const more = document.createElement('div');
            more.className = 'bulk-filter-summary';
            more.textContent = this._bulkT('moreThan100');
            table.appendChild(more);
        }
        this._localizeBulkFilterTable();
    }

    _renderBulkSelectionSummary() {
        const summary = document.getElementById('bulkFilterSummary');
        const rows = Array.isArray(this._bulkResult?.result) ? this._bulkResult.result : [];
        if (summary) {
            summary.textContent = this._bulkT('filterSummary', {
                filtered: this._bulkUniqueGeneCount(this._bulkFilteredRows).toLocaleString(),
                total: this._bulkUniqueGeneCount(rows).toLocaleString(),
                selected: this._bulkSelectedGenes.size.toLocaleString(),
            });
        }
        this._updateBulkGeneEstimate();
    }

    _localizeBulkFilterTable() {
        const result = this._bulkResult;
        const tableEl = document.getElementById('bulkFilterTable');
        if (!result || !tableEl) return;
        const rows = Array.isArray(result.result) ? result.result : [];
        const filtered = Array.isArray(this._bulkFilteredRows) ? this._bulkFilteredRows : rows;
        const summary = document.getElementById('bulkFilterSummary');
        if (summary) {
            summary.textContent = this._bulkT('filterSummary', {
                filtered: this._bulkUniqueGeneCount(filtered).toLocaleString(),
                total: this._bulkUniqueGeneCount(rows).toLocaleString(),
                selected: this._bulkSelectedGenes.size.toLocaleString(),
            });
        }
        const buttons = tableEl.querySelectorAll('button');
        if (buttons[0]) buttons[0].textContent = this._bulkT('selectFiltered');
        if (buttons[1]) buttons[1].textContent = this._bulkT('clearSelected');
        tableEl.querySelectorAll('thead th').forEach((th, index) => {
            const keys = ['select', 'expressionItem', 'groupColumn', 'effect', 'pValue', 'fdr', 'directionColumn'];
            if (keys[index]) th.textContent = this._bulkT(keys[index]);
        });
        tableEl.querySelector('.bulk-filter-summary')?.replaceChildren(document.createTextNode(this._bulkT('moreThan100')));
    }
}

// AnalysisPanel is instantiated by app.js DOMContentLoaded handler.
// No separate mount logic needed here.
