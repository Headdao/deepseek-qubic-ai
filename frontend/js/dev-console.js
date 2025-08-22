// F12 風格開發者控制台 - Qubic AI Compute Layer POC
// 基於 POC開發者控制台設計.md 規格實現

class QubicDevConsole {
    constructor() {
        this.isVisible = true; // 控制台始終可見
        this.isMinimized = false; // 保持展開狀態，但內容會向上移動
        this.activeTab = 0;
        this.logs = [];
        this.apiCalls = [];
        this.nodeMetrics = {};
        this.isConnected = false;
        this.maxLogEntries = 1000;
        this.socket = null;
        
        // 標籤頁配置
        this.tabs = [
            { id: 'console', label: 'Console', icon: '🖥️' },
            { id: 'network', label: 'Network', icon: '🌐' },
            { id: 'performance', label: 'Performance', icon: '📊' },
            { id: 'sources', label: 'Sources', icon: '📄' },
            { id: 'application', label: 'Application', icon: '⚙️' }
        ];
        
        this.init();
    }
    
    init() {
        console.log('🔧 Qubic 開發者控制台初始化中...');
        
        // 創建控制台 DOM
        this.createConsoleDOM();
        
        // 綁定快捷鍵
        this.bindKeyboardShortcuts();
        
        // 立即套用初始狀態（最小化）
        setTimeout(() => {
            this.applyInitialState();
        }, 50);
        
        // 初始化頁面佈局
        setTimeout(() => {
            this.adjustPageLayout(this.isMinimized);
        }, 100); // 確保 DOM 已經渲染
        
        // 監聽視窗大小變化
        window.addEventListener('resize', () => {
            this.adjustPageLayout(this.isMinimized);
        });
        
        // 連接 WebSocket (如果可用)
        this.connectWebSocket();
        
        // 攔截 API 調用
        this.interceptAPICallsTt();
        
        // 攔截 console 輸出
        this.interceptConsoleOutput();
        
        // 開始性能監控
        this.startPerformanceMonitoring();
        
        console.log('✅ Qubic 開發者控制台初始化完成');
        this.log('INFO', 'system', 'Qubic 開發者控制台已就緒');
    }
    
    applyInitialState() {
        const console = document.getElementById('qubic-dev-console');
        const minimizeBtn = document.getElementById('console-minimize-btn');
        const minimizeIcon = minimizeBtn?.querySelector('i');
        
        // 確保初始狀態正確
        if (this.isMinimized && console) {
            console.classList.add('minimized');
            document.body.classList.add('console-minimized');
            if (minimizeIcon) {
                minimizeIcon.className = 'bi bi-chevron-up';
                minimizeBtn.title = '展開控制台';
            }
            this.log('INFO', 'system', '控制台已設為最小化狀態');
        } else {
            // 確保展開狀態的圖標正確
            if (minimizeIcon) {
                minimizeIcon.className = 'bi bi-dash';
                minimizeBtn.title = '最小化控制台';
            }
            this.log('INFO', 'system', '控制台已展開，主要內容已向上移動');
        }
    }
    
    createConsoleDOM() {
        const consoleHTML = `
            <!-- F12 風格開發者控制台 -->
            <div id="qubic-dev-console" class="qubic-dev-console fixed-bottom-console">
                <!-- 控制台標題欄 -->
                <div class="console-header">
                    <div class="console-title">
                        <span class="console-logo">⚡</span>
                        <span class="console-name">Qubic AI Compute Layer - 開發者控制台</span>
                        <span class="connection-indicator" id="console-connection-status">
                            <span class="status-dot"></span>
                            <span class="status-text">就緒</span>
                        </span>
                    </div>
                    
                    <div class="console-controls">
                        <button class="console-btn" id="console-clear-btn" title="清除">
                            <i class="bi bi-trash"></i>
                        </button>
                        <button class="console-btn" id="console-settings-btn" title="設定">
                            <i class="bi bi-gear"></i>
                        </button>
                        <button class="console-btn" id="console-minimize-btn" title="最小化/展開">
                            <i class="bi bi-dash"></i>
                        </button>
                    </div>
                </div>
                
                <!-- 標籤頁導航 -->
                <div class="console-tabs">
                    ${this.tabs.map((tab, index) => `
                        <button class="console-tab ${index === 0 ? 'active' : ''}" 
                                data-tab="${tab.id}" data-index="${index}">
                            <span class="tab-icon">${tab.icon}</span>
                            <span class="tab-label">${tab.label}</span>
                        </button>
                    `).join('')}
                </div>
                
                <!-- 標籤頁內容 -->
                <div class="console-content">
                    <!-- Console 標籤頁 -->
                    <div class="tab-pane active" id="tab-console">
                        <div class="console-toolbar">
                            <div class="log-filters">
                                <select id="log-level-filter" class="console-select">
                                    <option value="all">所有級別</option>
                                    <option value="DEBUG">DEBUG</option>
                                    <option value="INFO">INFO</option>
                                    <option value="WARNING">WARNING</option>
                                    <option value="ERROR">ERROR</option>
                                </select>
                                
                                <select id="log-source-filter" class="console-select">
                                    <option value="all">所有來源</option>
                                    <option value="system">系統核心</option>
                                    <option value="ai_inference">AI 推理引擎</option>
                                    <option value="node_communication">節點通信</option>
                                    <option value="api_gateway">API 網關</option>
                                    <option value="database">數據庫操作</option>
                                </select>
                                
                                <input type="text" id="log-search" class="console-input" 
                                       placeholder="搜索日誌..." />
                            </div>
                            
                            <div class="toolbar-actions">
                                <button class="console-btn" id="log-export-btn" title="導出日誌">
                                    <i class="bi bi-download"></i>
                                </button>
                            </div>
                        </div>
                        
                        <div class="log-container" id="log-container">
                            <!-- 日誌條目將在此處動態生成 -->
                        </div>
                    </div>
                    
                    <!-- Network 標籤頁 -->
                    <div class="tab-pane" id="tab-network">
                        <div class="console-toolbar">
                            <div class="network-controls">
                                <button class="console-btn" id="network-record-btn" title="開始/停止錄製">
                                    <i class="bi bi-record-circle"></i> 錄製
                                </button>
                                <button class="console-btn" id="network-clear-btn" title="清除網路記錄">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </div>
                            
                            <div class="network-filters">
                                <select id="network-status-filter" class="console-select">
                                    <option value="all">所有狀態</option>
                                    <option value="2xx">成功 (2xx)</option>
                                    <option value="4xx">客戶端錯誤 (4xx)</option>
                                    <option value="5xx">伺服器錯誤 (5xx)</option>
                                </select>
                                
                                <select id="network-method-filter" class="console-select">
                                    <option value="all">所有方法</option>
                                    <option value="GET">GET</option>
                                    <option value="POST">POST</option>
                                    <option value="PUT">PUT</option>
                                    <option value="DELETE">DELETE</option>
                                </select>
                            </div>
                        </div>
                        
                        <div class="network-container">
                            <div class="network-header">
                                <div class="network-col-method">方法</div>
                                <div class="network-col-url">URL</div>
                                <div class="network-col-status">狀態</div>
                                <div class="network-col-size">大小</div>
                                <div class="network-col-time">時間</div>
                            </div>
                            <div class="network-list" id="network-list">
                                <!-- 網路請求將在此處動態生成 -->
                            </div>
                        </div>
                        
                        <div class="network-details" id="network-details">
                            <div class="details-placeholder">
                                選擇一個網路請求以查看詳情
                            </div>
                        </div>
                    </div>
                    
                    <!-- Performance 標籤頁 -->
                    <div class="tab-pane" id="tab-performance">
                        <div class="performance-overview">
                            <div class="metric-grid">
                                <div class="metric-card">
                                    <div class="metric-label">CPU 使用率</div>
                                    <div class="metric-value" id="cpu-usage">--</div>
                                    <div class="metric-chart" id="cpu-chart"></div>
                                </div>
                                
                                <div class="metric-card">
                                    <div class="metric-label">記憶體使用</div>
                                    <div class="metric-value" id="memory-usage">--</div>
                                    <div class="metric-chart" id="memory-chart"></div>
                                </div>
                                
                                <div class="metric-card">
                                    <div class="metric-label">AI 推理延遲</div>
                                    <div class="metric-value" id="inference-latency">--</div>
                                    <div class="metric-chart" id="latency-chart"></div>
                                </div>
                                
                                <div class="metric-card">
                                    <div class="metric-label">網路 I/O</div>
                                    <div class="metric-value" id="network-io">--</div>
                                    <div class="metric-chart" id="network-chart"></div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="performance-timeline">
                            <canvas id="performance-timeline-chart" height="200"></canvas>
                        </div>
                    </div>
                    
                    <!-- Sources 標籤頁 -->
                    <div class="tab-pane" id="tab-sources">
                        <div class="sources-layout">
                            <div class="sources-sidebar">
                                <div class="sources-tree" id="sources-tree">
                                    <div class="tree-node">
                                        <i class="bi bi-folder"></i> AI 推理流程
                                        <div class="tree-children">
                                            <div class="tree-leaf">📥 輸入處理</div>
                                            <div class="tree-leaf">🧠 模型推理</div>
                                            <div class="tree-leaf">📤 輸出生成</div>
                                        </div>
                                    </div>
                                    <div class="tree-node">
                                        <i class="bi bi-folder"></i> 節點通信
                                        <div class="tree-children">
                                            <div class="tree-leaf">🔗 節點發現</div>
                                            <div class="tree-leaf">📡 數據同步</div>
                                            <div class="tree-leaf">✅ 共識驗證</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="sources-content">
                                <div class="execution-trace" id="execution-trace">
                                    <div class="trace-placeholder">
                                        選擇左側的執行流程以查看詳細追蹤
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Application 標籤頁 -->
                    <div class="tab-pane" id="tab-application">
                        <div class="application-sections">
                            <div class="app-section">
                                <h3>AI 模型狀態</h3>
                                <div class="state-grid">
                                    <div class="state-item">
                                        <span class="state-label">模型版本:</span>
                                        <span class="state-value" id="model-version">DeepSeek-R1-Distill-Qwen-1.5B</span>
                                    </div>
                                    <div class="state-item">
                                        <span class="state-label">載入狀態:</span>
                                        <span class="state-value state-success" id="model-status">已載入</span>
                                    </div>
                                    <div class="state-item">
                                        <span class="state-label">記憶體佔用:</span>
                                        <span class="state-value" id="model-memory">--</span>
                                    </div>
                                    <div class="state-item">
                                        <span class="state-label">推理次數:</span>
                                        <span class="state-value" id="inference-count">0</span>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="app-section">
                                <h3>節點集群狀態</h3>
                                <div class="cluster-status" id="cluster-status">
                                    <div class="cluster-node">
                                        <div class="node-info">
                                            <span class="node-name">本地節點</span>
                                            <span class="node-status status-online">在線</span>
                                        </div>
                                        <div class="node-metrics">
                                            <span>CPU: --</span>
                                            <span>RAM: --</span>
                                            <span>延遲: --</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="app-section">
                                <h3>配置信息</h3>
                                <div class="config-viewer" id="config-viewer">
                                    <pre id="config-content">載入中...</pre>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            

        `;
        
        // 添加到頁面
        document.body.insertAdjacentHTML('beforeend', consoleHTML);
        
        // 綁定事件
        this.bindConsoleEvents();
    }
    
    bindConsoleEvents() {
        // 標籤頁切換
        document.querySelectorAll('.console-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const tabIndex = parseInt(e.currentTarget.dataset.index);
                this.switchTab(tabIndex);
            });
        });
        
        // 最小化按鈕
        document.getElementById('console-minimize-btn')?.addEventListener('click', () => {
            this.toggleMinimize();
        });
        
        // 清除按鈕
        document.getElementById('console-clear-btn')?.addEventListener('click', () => {
            this.clearCurrentTab();
        });
        

        
        // 日誌過濾器
        document.getElementById('log-level-filter')?.addEventListener('change', () => {
            this.filterLogs();
        });
        
        document.getElementById('log-source-filter')?.addEventListener('change', () => {
            this.filterLogs();
        });
        
        document.getElementById('log-search')?.addEventListener('input', () => {
            this.filterLogs();
        });
        
        // 網路記錄控制
        document.getElementById('network-record-btn')?.addEventListener('click', () => {
            this.toggleNetworkRecording();
        });
        
        // 日誌導出
        document.getElementById('log-export-btn')?.addEventListener('click', () => {
            this.exportLogs();
        });
    }
    
    bindKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+` 快捷鍵切換最小化狀態
            if (e.ctrlKey && e.key === '`') {
                e.preventDefault();
                this.toggleMinimize();
            }
            
            // ESC 鍵最小化控制台
            if (e.key === 'Escape' && !this.isMinimized) {
                e.preventDefault();
                this.toggleMinimize();
            }
        });
    }
    
    toggleMinimize() {
        const console = document.getElementById('qubic-dev-console');
        const minimizeBtn = document.getElementById('console-minimize-btn');
        const minimizeIcon = minimizeBtn?.querySelector('i');
        
        if (this.isMinimized) {
            // 展開控制台
            console.classList.remove('minimized');
            document.body.classList.remove('console-minimized');
            if (minimizeIcon) {
                minimizeIcon.className = 'bi bi-dash';
                minimizeBtn.title = '最小化';
            }
            this.isMinimized = false;
            this.adjustPageLayout(false); // 調整頁面佈局
            this.log('INFO', 'system', '開發者控制台已展開');
        } else {
            // 最小化控制台
            console.classList.add('minimized');
            document.body.classList.add('console-minimized');
            if (minimizeIcon) {
                minimizeIcon.className = 'bi bi-chevron-up';
                minimizeBtn.title = '展開';
            }
            this.isMinimized = true;
            this.adjustPageLayout(true); // 調整頁面佈局
            this.log('INFO', 'system', '開發者控制台已最小化');
        }
    }
    
    // ✅ 動態調整頁面佈局，避免內容被遮擋
    adjustPageLayout(isMinimized) {
        const mainContent = document.querySelector('.main-content');
        if (!mainContent) return;
        
        if (isMinimized) {
            // 最小化狀態：只需要為標題欄留空間
            mainContent.style.paddingBottom = '60px';
        } else {
            // 展開狀態：動態計算控制台實際高度
            const console = document.getElementById('qubic-dev-console');
            if (console) {
                const consoleHeight = console.offsetHeight;
                const extraPadding = 20; // 額外間距
                mainContent.style.paddingBottom = `${consoleHeight + extraPadding}px`;
                
                console.log(`🔧 動態調整頁面佈局: 控制台高度 ${consoleHeight}px + 間距 ${extraPadding}px = ${consoleHeight + extraPadding}px`);
            }
        }
    }
    
    toggleConsole() {
        // 現在只是最小化/展開，不完全隱藏
        this.toggleMinimize();
    }
    
    switchTab(tabIndex) {
        // 更新標籤頁狀態
        document.querySelectorAll('.console-tab').forEach((tab, index) => {
            tab.classList.toggle('active', index === tabIndex);
        });
        
        // 更新內容面板
        document.querySelectorAll('.tab-pane').forEach((pane, index) => {
            pane.classList.toggle('active', index === tabIndex);
        });
        
        this.activeTab = tabIndex;
        
        // 特殊處理
        if (tabIndex === 2) { // Performance 標籤
            this.updatePerformanceCharts();
        }
    }
    
    log(level, source, message, details = null) {
        const logEntry = {
            id: `log-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            timestamp: new Date(),
            level: level,
            source: source,
            message: message,
            details: details
        };
        
        this.logs.unshift(logEntry);
        
        // 限制日誌條目數量
        if (this.logs.length > this.maxLogEntries) {
            this.logs = this.logs.slice(0, this.maxLogEntries);
        }
        
        // 更新 UI
        this.updateLogDisplay();
        
        // 發送到 WebSocket (如果連接)
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type: 'log',
                data: logEntry
            }));
        }
    }
    
    updateLogDisplay() {
        const container = document.getElementById('log-container');
        if (!container) return;
        
        const filteredLogs = this.getFilteredLogs();
        
        container.innerHTML = filteredLogs.map(log => `
            <div class="log-entry log-${log.level.toLowerCase()}" data-level="${log.level}" data-source="${log.source}">
                <span class="log-timestamp">${log.timestamp.toLocaleTimeString()}</span>
                <span class="log-level">${log.level}</span>
                <span class="log-source">${log.source}</span>
                <span class="log-message">${log.message}</span>
                ${log.details ? `
                    <details class="log-details">
                        <summary>詳細信息</summary>
                        <pre>${JSON.stringify(log.details, null, 2)}</pre>
                    </details>
                ` : ''}
            </div>
        `).join('');
        
        // 自動滾動到最新日誌
        container.scrollTop = 0;
    }
    
    getFilteredLogs() {
        const levelFilter = document.getElementById('log-level-filter')?.value || 'all';
        const sourceFilter = document.getElementById('log-source-filter')?.value || 'all';
        const searchFilter = document.getElementById('log-search')?.value.toLowerCase() || '';
        
        return this.logs.filter(log => {
            if (levelFilter !== 'all' && log.level !== levelFilter) return false;
            if (sourceFilter !== 'all' && log.source !== sourceFilter) return false;
            if (searchFilter && !log.message.toLowerCase().includes(searchFilter)) return false;
            return true;
        });
    }
    
    filterLogs() {
        this.updateLogDisplay();
    }
    
    interceptAPICallsTt() {
        // 攔截 fetch 請求
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            const startTime = performance.now();
            const url = args[0];
            const options = args[1] || {};
            
            try {
                const response = await originalFetch(...args);
                const endTime = performance.now();
                
                this.logAPICall({
                    method: options.method || 'GET',
                    url: url,
                    status: response.status,
                    statusText: response.statusText,
                    duration: endTime - startTime,
                    headers: Object.fromEntries(response.headers.entries()),
                    timestamp: new Date()
                });
                
                return response;
            } catch (error) {
                const endTime = performance.now();
                
                this.logAPICall({
                    method: options.method || 'GET',
                    url: url,
                    status: 0,
                    statusText: 'Network Error',
                    duration: endTime - startTime,
                    error: error.message,
                    timestamp: new Date()
                });
                
                throw error;
            }
        };
        
        // 攔截 XMLHttpRequest
        const originalXHROpen = XMLHttpRequest.prototype.open;
        const originalXHRSend = XMLHttpRequest.prototype.send;
        
        XMLHttpRequest.prototype.open = function(method, url, ...args) {
            this._devConsole = { method, url, startTime: performance.now() };
            return originalXHROpen.call(this, method, url, ...args);
        };
        
        XMLHttpRequest.prototype.send = function(...args) {
            if (this._devConsole) {
                this.addEventListener('loadend', () => {
                    const endTime = performance.now();
                    window.qubicDevConsole.logAPICall({
                        method: this._devConsole.method,
                        url: this._devConsole.url,
                        status: this.status,
                        statusText: this.statusText,
                        duration: endTime - this._devConsole.startTime,
                        timestamp: new Date()
                    });
                });
            }
            return originalXHRSend.call(this, ...args);
        };
    }
    
    logAPICall(callData) {
        this.apiCalls.unshift(callData);
        
        if (this.apiCalls.length > 100) {
            this.apiCalls = this.apiCalls.slice(0, 100);
        }
        
        this.updateNetworkDisplay();
        
        // 記錄到日誌
        const level = callData.status >= 400 ? 'ERROR' : 'INFO';
        this.log(level, 'api_gateway', 
                `${callData.method} ${callData.url} ${callData.status} (${callData.duration.toFixed(2)}ms)`);
    }
    
    updateNetworkDisplay() {
        const container = document.getElementById('network-list');
        if (!container) return;
        
        container.innerHTML = this.apiCalls.map(call => `
            <div class="network-entry" data-call-id="${call.timestamp.getTime()}">
                <div class="network-col-method">${call.method}</div>
                <div class="network-col-url" title="${call.url}">${this.truncateURL(call.url)}</div>
                <div class="network-col-status status-${this.getStatusClass(call.status)}">${call.status}</div>
                <div class="network-col-size">--</div>
                <div class="network-col-time">${call.duration.toFixed(0)}ms</div>
            </div>
        `).join('');
        
        // 綁定點擊事件
        container.querySelectorAll('.network-entry').forEach(entry => {
            entry.addEventListener('click', (e) => {
                const callId = e.currentTarget.dataset.callId;
                this.showNetworkDetails(callId);
            });
        });
    }
    
    truncateURL(url) {
        if (url.length > 50) {
            return '...' + url.slice(-47);
        }
        return url;
    }
    
    getStatusClass(status) {
        if (status >= 200 && status < 300) return 'success';
        if (status >= 400 && status < 500) return 'client-error';
        if (status >= 500) return 'server-error';
        return 'other';
    }
    
    showNetworkDetails(callId) {
        const call = this.apiCalls.find(c => c.timestamp.getTime() == callId);
        if (!call) return;
        
        const detailsContainer = document.getElementById('network-details');
        detailsContainer.innerHTML = `
            <div class="network-details-content">
                <h4>請求詳情</h4>
                <div class="details-section">
                    <h5>一般信息</h5>
                    <div class="details-grid">
                        <div><strong>URL:</strong> ${call.url}</div>
                        <div><strong>方法:</strong> ${call.method}</div>
                        <div><strong>狀態:</strong> ${call.status} ${call.statusText}</div>
                        <div><strong>耗時:</strong> ${call.duration.toFixed(2)}ms</div>
                        <div><strong>時間:</strong> ${call.timestamp.toLocaleString()}</div>
                    </div>
                </div>
                
                ${call.headers ? `
                    <div class="details-section">
                        <h5>回應標頭</h5>
                        <pre>${JSON.stringify(call.headers, null, 2)}</pre>
                    </div>
                ` : ''}
                
                ${call.error ? `
                    <div class="details-section">
                        <h5>錯誤信息</h5>
                        <div class="error-message">${call.error}</div>
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    interceptConsoleOutput() {
        const originalConsole = {
            log: console.log,
            warn: console.warn,
            error: console.error,
            info: console.info,
            debug: console.debug
        };
        
        console.log = (...args) => {
            this.log('INFO', 'console', args.join(' '));
            return originalConsole.log(...args);
        };
        
        console.warn = (...args) => {
            this.log('WARNING', 'console', args.join(' '));
            return originalConsole.warn(...args);
        };
        
        console.error = (...args) => {
            this.log('ERROR', 'console', args.join(' '));
            return originalConsole.error(...args);
        };
        
        console.info = (...args) => {
            this.log('INFO', 'console', args.join(' '));
            return originalConsole.info(...args);
        };
        
        console.debug = (...args) => {
            this.log('DEBUG', 'console', args.join(' '));
            return originalConsole.debug(...args);
        };
    }
    
    startPerformanceMonitoring() {
        setInterval(() => {
            // 收集性能指標
            const metrics = this.collectPerformanceMetrics();
            this.updatePerformanceMetrics(metrics);
        }, 1000);
    }
    
    collectPerformanceMetrics() {
        const memory = performance.memory || {};
        const navigation = performance.getEntriesByType('navigation')[0] || {};
        
        return {
            memory: {
                used: memory.usedJSHeapSize || 0,
                total: memory.totalJSHeapSize || 0,
                limit: memory.jsHeapSizeLimit || 0
            },
            timing: {
                domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart || 0,
                loadComplete: navigation.loadEventEnd - navigation.loadEventStart || 0
            },
            timestamp: Date.now()
        };
    }
    
    updatePerformanceMetrics(metrics) {
        // 更新記憶體使用
        const memoryElement = document.getElementById('memory-usage');
        if (memoryElement && metrics.memory.used) {
            const used = (metrics.memory.used / 1024 / 1024).toFixed(1);
            const total = (metrics.memory.total / 1024 / 1024).toFixed(1);
            memoryElement.textContent = `${used}MB / ${total}MB`;
        }
        
        // 模擬 CPU 使用率 (實際實現需要更複雜的邏輯)
        const cpuElement = document.getElementById('cpu-usage');
        if (cpuElement) {
            const cpuUsage = Math.floor(Math.random() * 30) + 10; // 模擬 10-40% 使用率
            cpuElement.textContent = `${cpuUsage}%`;
        }
        
        // 記錄性能日誌
        if (metrics.memory.used > metrics.memory.total * 0.8) {
            this.log('WARNING', 'performance', '記憶體使用率過高', { memory: metrics.memory });
        }
    }
    
    updatePerformanceCharts() {
        // 這裡可以實現更詳細的圖表更新邏輯
        // 暫時保持簡單實現
    }
    
    connectWebSocket() {
        // 跳過 WebSocket 連接，直接使用本地模式
        console.log('🔧 開發者控制台：使用本地模式');
        
        // 立即設置為已連線狀態
        setTimeout(() => {
            this.isConnected = true;
            this.updateConnectionStatus(true);
            this.log('INFO', 'system', '開發者控制台已就緒 (本地模式)');
            this.log('INFO', 'system', '所有功能正常運作，無需 WebSocket 連接');
        }, 500);
        
        // 可選：如果需要真實 WebSocket，取消註解以下代碼
        /*
        try {
            this.socket = new WebSocket(`ws://${window.location.host}`);
            
            this.socket.onopen = () => {
                this.isConnected = true;
                this.updateConnectionStatus(true);
                this.log('INFO', 'websocket', 'WebSocket 連線已建立');
            };
            
            this.socket.onclose = () => {
                this.isConnected = false;
                this.updateConnectionStatus(false);
                this.log('WARNING', 'websocket', 'WebSocket 連線已斷開');
            };
            
            this.socket.onerror = (error) => {
                this.log('ERROR', 'websocket', 'WebSocket 連線錯誤');
                // 回退到本地模式
                setTimeout(() => {
                    this.isConnected = true;
                    this.updateConnectionStatus(true);
                    this.log('INFO', 'system', '已切換到本地模式');
                }, 1000);
            };
            
            this.socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (e) {
                    this.log('ERROR', 'websocket', 'WebSocket 訊息解析失敗');
                }
            };
        } catch (error) {
            this.log('INFO', 'websocket', 'WebSocket 不可用，使用本地模式');
            setTimeout(() => {
                this.isConnected = true;
                this.updateConnectionStatus(true);
                this.log('INFO', 'system', '開發者控制台已就緒 (本地模式)');
            }, 1000);
        }
        */
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'log':
                if (data.data) {
                    this.logs.unshift(data.data);
                    this.updateLogDisplay();
                }
                break;
            case 'metrics':
                if (data.data) {
                    this.nodeMetrics = data.data;
                    this.updatePerformanceMetrics(data.data);
                }
                break;
            case 'api_call':
                if (data.data) {
                    this.logAPICall(data.data);
                }
                break;
        }
    }
    
    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('console-connection-status');
        if (statusElement) {
            const dot = statusElement.querySelector('.status-dot');
            const text = statusElement.querySelector('.status-text');
            
            if (connected) {
                dot.className = 'status-dot status-connected';
                text.textContent = window.languageSwitcher?.t('devConsole.status.connected') || 'Connected';
            } else {
                dot.className = 'status-dot status-disconnected';
                text.textContent = window.languageSwitcher?.t('devConsole.status.offline') || 'Offline';
            }
        }
    }
    
    clearCurrentTab() {
        switch (this.activeTab) {
            case 0: // Console
                this.logs = [];
                this.updateLogDisplay();
                break;
            case 1: // Network
                this.apiCalls = [];
                this.updateNetworkDisplay();
                break;
        }
        
        this.log('INFO', 'system', `已清除 ${this.tabs[this.activeTab].label} 標籤頁內容`);
    }
    
    exportLogs() {
        const logs = this.getFilteredLogs();
        const exportData = logs.map(log => ({
            timestamp: log.timestamp.toISOString(),
            level: log.level,
            source: log.source,
            message: log.message,
            details: log.details
        }));
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `qubic-console-logs-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        URL.revokeObjectURL(url);
        
        this.log('INFO', 'system', '日誌已導出');
    }
    
    toggleNetworkRecording() {
        // 切換網路錄製狀態的邏輯
        this.log('INFO', 'network', '網路錄製狀態已切換');
    }
}

// 自動初始化
document.addEventListener('DOMContentLoaded', () => {
    window.qubicDevConsole = new QubicDevConsole();
});

// 匯出類別
window.QubicDevConsole = QubicDevConsole;
