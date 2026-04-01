// E2seq 国际化语言包

const i18n = {
    'zh-CN': {
        // 导航
        'nav.newChat': '发起新对话',
        'nav.knowledgeBase': '我的知识库',
        'nav.settings': '设置和帮助',
        'nav.back': '返回',
        
        // 聊天页面
        'chat.title': 'E2seq',
        'chat.greeting': '✨ 你好，研究者',
        'chat.subGreeting': '需要我为你分析单细胞数据吗？',
        'chat.inputPlaceholder': '输入你的问题，例如：分析Enterocytes细胞的差异基因...',
        'chat.send': '发送',
        'chat.attach': '添加附件',
        'chat.tools': '工具',
        'chat.charts': '可视化图表',
        'chat.hint': 'E2seq 可能会出错，请核实重要信息',
        
        // 建议提示词
        'suggestion.deg': '分析所选细胞类型的高表达基因疾病关联',
        'suggestion.enrichment': '解读基因通路与生物过程（Reactome + QuickGO）',
        'suggestion.network': '分析基因互作网络与转录调控（STRING + TRRUST）',
        'suggestion.hub': '解读药物靶点潜力（ChEMBL + Open Targets）',
        'suggestion.umap': '分析代谢物与肠道菌群关联（HMDB + GUTMGENE）',
        'suggestion.upload': '加载我的h5ad数据文件',
        
        // 知识库页面
        'kb.title': '我的知识库',
        'kb.builtin': '内置数据库',
        'kb.custom': '自定义数据库',
        'kb.upload': '上传数据库',
        'kb.viewDetail': '查看详情',
        'kb.delete': '删除',
        'kb.empty': '暂无自定义数据库',
        'kb.emptyHint': '点击上方按钮上传你的数据库文件',
        'kb.records': '条记录',
        'kb.format': '格式',
        'kb.status': '已加载',
        'kb.description': '描述',
        'kb.uploadInstructions': '上传自定义数据库',
        'kb.requiredFields': '必需字段',
        'kb.csvFormatDesc': '请上传CSV格式文件，文件必须包含以下字段：',
        'kb.formatExample': '格式示例',
        'kb.notes': '注意事项',
        'kb.cancel': '取消',
        'kb.selectFile': '选择文件',
        'kb.downloadTemplate': '下载模板文件',
        'kb.formatRequirements': '文件格式要求',
        'kb.required': '必需',
        'kb.optional': '可选',
        
        // 数据库描述
        'db.string.desc': '蛋白质-蛋白质相互作用',
        'db.hmdb.desc': '基因-代谢物关联',
        'db.trrust.desc': '转录因子调控关系',
        'db.gutmgene.desc': '肠道微生物-基因关联',
        
        // 数据库详情
        'dbDetail.title': '数据库详情',
        'dbDetail.basicInfo': '基本信息',
        'dbDetail.name': '名称',
        'dbDetail.records': '记录数',
        'dbDetail.format': '格式',
        'dbDetail.description': '描述',
        'dbDetail.fields': '字段说明',
        'dbDetail.example': '数据示例',
        'dbDetail.close': '关闭',
        
        // 设置页面
        'settings.title': '设置',
        'settings.apiKeys': 'API Keys',
        'settings.openaiKey': 'OpenAI API Key',
        'settings.openaiPlaceholder': '输入你的 OpenAI API Key 以使用 OpenAI 模型',
        'settings.anthropicKey': 'Anthropic API Key',
        'settings.anthropicPlaceholder': '输入你的 Anthropic API Key 以使用 Claude 模型',
        'settings.geminiKey': 'Google AI Studio API Key',
        'settings.geminiPlaceholder': '输入你的 Google AI Studio API Key 以使用 Google 模型',
        'settings.deepseekKey': 'Deepseek API Key',
        'settings.deepseekPlaceholder': '输入你的 Deepseek API Key 以使用 Deepseek 模型',
        'settings.language': '语言设置',
        'settings.interfaceLanguage': '界面语言',
        'settings.chinese': '🇨🇳 简体中文',
        'settings.english': '🇺🇸 English',
        'settings.dataConfig': '数据配置',
        'settings.dataPath': '数据文件路径',
        'settings.dataPathPlaceholder': '例如: data.h5ad',
        'settings.uploadData': '上传数据文件',
        'settings.save': '保存设置',
        'settings.testConnection': '测试连接',
        
        // 可视化面板
        'charts.title': '📊 可视化图表',
        'charts.umap': 'UMAP/tSNE 散点图',
        'charts.violin': '小提琴图/箱线图',
        'charts.heatmap': '热图',
        'charts.volcano': '火山图',
        'charts.bubble': '气泡图（富集分析）',
        'charts.network': '网络图',
        'charts.chord': '和弦图',
        'charts.download': '下载',
        'charts.fullscreen': '全屏',
        'charts.refresh': '刷新',
        'charts.placeholder': '选择图表类型以查看可视化',
        'charts.close': '关闭',
        'charts.noData': '暂无数据',
        'charts.noDataHint': '请先上传数据文件（h5ad格式）以查看可视化图表',
        
        // 通知消息
        'notify.uploadSuccess': '文件上传成功',
        'notify.uploadFailed': '文件上传失败',
        'notify.saveSuccess': '保存成功',
        'notify.saveFailed': '保存失败',
        'notify.deleteSuccess': '删除成功',
        'notify.deleteFailed': '删除失败',
        'notify.languageChanged': '语言已切换',
        'notify.dbUploaded': '数据库上传成功',
        'notify.dbUploadFailed': '数据库上传失败',
        'notify.dbDeleted': '数据库已删除',
        'notify.dbDeleteFailed': '数据库删除失败',
        'notify.templateDownloaded': '模板文件已下载',
        
        // 错误消息
        'error.chatFailed': '对话失败，请稍后重试',
        'error.loadFailed': '加载失败',
        'error.networkError': '网络错误',
        'error.serverError': '服务器错误',
        'error.invalidFile': '无效的文件格式',
        'error.noData': '未加载数据',
        'error.noConfig': '未配置 LLM',
        'error.fileTooLarge': '文件大小超过50MB限制',
        'error.invalidFileType': '不支持的文件格式，请上传CSV或TSV文件',
        'error.emptyFile': '文件为空或格式错误',
        'error.missingFields': '缺少必需字段',
        'error.fileReadError': '文件读取失败',
        
        // 对话历史
        'history.title': '对话',
        'history.newChat': '新对话',
        'history.empty': '暂无对话历史',
    },
    
    'en-US': {
        // Navigation
        'nav.newChat': 'New Chat',
        'nav.knowledgeBase': 'Knowledge Base',
        'nav.settings': 'Settings & Help',
        'nav.back': 'Back',
        
        // Chat page
        'chat.title': 'E2seq',
        'chat.greeting': '✨ Hello, Researcher',
        'chat.subGreeting': 'Need help analyzing single-cell data?',
        'chat.inputPlaceholder': 'Enter your question, e.g.: Analyze differential genes in Enterocytes...',
        'chat.send': 'Send',
        'chat.attach': 'Attach',
        'chat.tools': 'Tools',
        'chat.charts': 'Charts',
        'chat.hint': 'E2seq may make mistakes. Please verify important information.',
        
        // Suggestion chips
        'suggestion.deg': 'Analyze differential genes in Enterocytes',
        'suggestion.enrichment': 'Perform GO enrichment analysis',
        'suggestion.network': 'Build gene interaction network',
        'suggestion.hub': 'Identify hub genes and query functions',
        'suggestion.umap': 'Visualize UMAP dimensionality reduction',
        'suggestion.upload': 'Load my h5ad data file',
        
        // Knowledge base page
        'kb.title': 'Knowledge Base',
        'kb.builtin': 'Built-in Databases',
        'kb.custom': 'Custom Databases',
        'kb.upload': 'Upload Database',
        'kb.viewDetail': 'View Details',
        'kb.delete': 'Delete',
        'kb.empty': 'No custom databases',
        'kb.emptyHint': 'Click the button above to upload your database file',
        'kb.records': 'records',
        'kb.format': 'Format',
        'kb.status': 'Loaded',
        'kb.description': 'Description',
        
        // Database descriptions
        'db.string.desc': 'Protein-Protein Interactions',
        'db.hmdb.desc': 'Gene-Metabolite Associations',
        'db.trrust.desc': 'Transcription Factor Regulations',
        'db.gutmgene.desc': 'Gut Microbiota-Gene Associations',
        
        // Database details
        'dbDetail.title': 'Database Details',
        'dbDetail.basicInfo': 'Basic Information',
        'dbDetail.name': 'Name',
        'dbDetail.records': 'Records',
        'dbDetail.format': 'Format',
        'dbDetail.description': 'Description',
        'dbDetail.fields': 'Fields',
        'dbDetail.example': 'Example',
        'dbDetail.close': 'Close',
        
        // Settings page
        'settings.title': 'Settings',
        'settings.apiKeys': 'API Keys',
        'settings.openaiKey': 'OpenAI API Key',
        'settings.openaiPlaceholder': 'You can put in your OpenAI key to use OpenAI models at cost.',
        'settings.anthropicKey': 'Anthropic API Key',
        'settings.anthropicPlaceholder': 'You can put in your Anthropic key to use Claude at cost. When enabled, this key will be used for all models beginning with \'claude-\'.',
        'settings.geminiKey': 'Google AI Studio API Key',
        'settings.geminiPlaceholder': 'You can put in your Google AI Studio key to use Google models at-cost.',
        'settings.deepseekKey': 'Deepseek API Key',
        'settings.deepseekPlaceholder': 'You can put in your Deepseek key to use Deepseek models at cost.',
        'settings.language': 'Language Settings',
        'settings.interfaceLanguage': 'Interface Language',
        'settings.chinese': '🇨🇳 简体中文',
        'settings.english': '🇺🇸 English',
        'settings.dataConfig': 'Data Configuration',
        'settings.dataPath': 'Data File Path',
        'settings.dataPathPlaceholder': 'e.g.: data.h5ad',
        'settings.uploadData': 'Upload Data File',
        'settings.save': 'Save Settings',
        'settings.testConnection': 'Test Connection',
        
        // Visualization panel
        'charts.title': '📊 Visualization Charts',
        'charts.umap': 'UMAP/tSNE Scatter Plot',
        'charts.violin': 'Violin/Box Plot',
        'charts.heatmap': 'Heatmap',
        'charts.volcano': 'Volcano Plot',
        'charts.bubble': 'Bubble Plot (Enrichment)',
        'charts.network': 'Network Graph',
        'charts.chord': 'Chord Diagram',
        'charts.download': 'Download',
        'charts.fullscreen': 'Fullscreen',
        'charts.refresh': 'Refresh',
        'charts.placeholder': 'Select a chart type to view visualization',
        'charts.close': 'Close',
        'charts.noData': 'No Data Available',
        'charts.noDataHint': 'Please upload a data file (h5ad format) first to view visualizations',
        
        // Notification messages
        'notify.uploadSuccess': 'File uploaded successfully',
        'notify.uploadFailed': 'File upload failed',
        'notify.saveSuccess': 'Saved successfully',
        'notify.saveFailed': 'Save failed',
        'notify.deleteSuccess': 'Deleted successfully',
        'notify.deleteFailed': 'Delete failed',
        'notify.languageChanged': 'Language changed',
        'notify.dbUploaded': 'Database uploaded successfully',
        'notify.dbUploadFailed': 'Database upload failed',
        'notify.dbDeleted': 'Database deleted',
        'notify.dbDeleteFailed': 'Database delete failed',
        'notify.templateDownloaded': 'Template file downloaded',
        
        // Error messages
        'error.chatFailed': 'Chat failed, please try again later',
        'error.loadFailed': 'Load failed',
        'error.networkError': 'Network error',
        'error.serverError': 'Server error',
        'error.invalidFile': 'Invalid file format',
        'error.noData': 'No data loaded',
        'error.noConfig': 'LLM not configured',
        'error.fileTooLarge': 'File size exceeds 50MB limit',
        'error.invalidFileType': 'Unsupported file format, please upload CSV or TSV file',
        'error.emptyFile': 'File is empty or invalid format',
        'error.missingFields': 'Missing required fields',
        'error.fileReadError': 'Failed to read file',
        
        // Chat history
        'history.title': 'Chats',
        'history.newChat': 'New Chat',
        'history.empty': 'No chat history',
    }
};

// 获取翻译文本
function t(key, lang = null) {
    const currentLang = lang || localStorage.getItem('e2seq_language') || 'zh-CN';
    return i18n[currentLang]?.[key] || key;
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { i18n, t };
}
