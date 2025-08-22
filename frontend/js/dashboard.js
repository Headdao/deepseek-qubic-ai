// QDashboard JavaScript 主控制器

class QDashboard {
    constructor() {
        // API 設定 - 動態檢測，無硬編碼端口
        this.apiBaseUrl = this.getDynamicApiBaseUrl();
        this.updateInterval = 5000; // 5秒更新一次
        this.maxDataPoints = 20; // 圖表最大數據點
        
        // 數據儲存
        this.tickHistory = [];
        this.durationHistory = [];
        this.priceHistory = [];
        this.timeLabels = [];
        this.lastStats = null;
        
        // 圖表實例
        this.tickChart = null;
        this.durationChart = null;
        this.priceChart = null;
        
        // 定時器管理
        this.dataUpdateTimer = null;
        this.statsUpdateTimer = null;
        
        // 初始化
        this.init();
    }
    
    getDynamicApiBaseUrl() {
        // 優先使用全域配置
        if (window.QDASHBOARD_CONFIG && window.QDASHBOARD_CONFIG.getApiBaseUrl()) {
            return window.QDASHBOARD_CONFIG.getApiBaseUrl();
        }
        
        // 備用：動態檢測當前頁面端口
        const protocol = window.location.protocol;
        const hostname = window.location.hostname || 'localhost';
        const port = window.location.port || '3000';
        return `${protocol}//${hostname}:${port}/api`;
    }
    
    init() {
        console.log('🚀 QDashboard 初始化中...');
        
        // 隱藏載入覆蓋層（稍後顯示）
        this.hideLoading();
        
        // 初始化圖表
        this.initCharts();
        
        // 載入初始數據
        this.loadInitialData();
        
        // 開始自動更新
        this.startAutoUpdate();
        
        // 綁定事件
        this.bindEvents();
        
        console.log('✅ QDashboard 初始化完成');
    }
    
    async loadInitialData() {
        this.showLoading();
        try {
            // 設置初始連線狀態為連線中
            this.updateConnectionStatus(true, '連線中');
            
            await Promise.all([
                this.fetchAndUpdateData(),
                this.fetchAndUpdateStats()
            ]);
        } catch (error) {
            console.error('❌ 初始數據載入失敗:', error);
            // 不要立即顯示連線失敗，因為可能是部分失敗
            // this.showConnectionError();
        } finally {
            this.hideLoading();
        }
    }
    
    async fetchAndUpdateData() {
        try {
            // 檢查是否為演示模式 (生產環境無後端)
            if (!this.apiBaseUrl && window.QDASHBOARD_CONFIG.shouldTryRealApi()) {
                // 嘗試直接調用 Qubic API
                try {
                    console.log('🌐 嘗試直接調用 Qubic API...');
                    if (!this.qubicProxy) {
                        this.qubicProxy = new window.QubicApiProxy();
                    }
                    const data = await this.qubicProxy.getTickInfo();
                    console.log('✅ 成功獲取真實數據:', data);
                    this.updateMetrics(data);
                    this.updateCharts(data);
                    this.updateHealthIndicators(data.health);
                    this.updateConnectionStatus(true, '真實數據');
                    this.updateLastUpdateTime();
                    return;
                } catch (error) {
                    console.warn('⚠️ 直接 API 調用失敗，回退到模擬模式');
                    // 繼續執行下面的模擬數據邏輯
                }
            }
            
            if (!this.apiBaseUrl) {
                console.log('🎭 演示模式：使用模擬數據');
                const data = window.QDASHBOARD_CONFIG.getMockData();
                this.updateMetrics(data);
                this.updateCharts(data);
                this.updateHealthIndicators(data.health);
                this.updateConnectionStatus(true, '演示模式');
                this.updateLastUpdateTime();
                return;
            }
            
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000); // 10秒超時
            
            const response = await fetch(`${this.apiBaseUrl}/tick`, {
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('📊 收到 tick 數據:', data);
            
            // 更新 UI
            this.updateMetrics(data);
            this.updateCharts(data);
            this.updateHealthIndicators(data.health);
            this.updateConnectionStatus(true);
            this.updateLastUpdateTime();
            
        } catch (error) {
            console.error('❌ Tick 數據獲取失敗:', error);
            // 只有在所有方法都失敗時才顯示離線
            if (!this.apiBaseUrl && !window.QDASHBOARD_CONFIG.shouldTryRealApi()) {
                this.updateConnectionStatus(false);
            }
            throw error;
        }
    }
    
    async fetchAndUpdateStats() {
        try {
            // 檢查是否有本地後端 API
            if (!this.apiBaseUrl) {
                console.log('🎭 演示模式：使用動態模擬統計數據');
                const stats = window.QDASHBOARD_CONFIG.getMockStats();
                this.updateStatsUI(stats);
                this.updatePriceChart(stats);
                this.lastStats = stats;
                return;
            }
            
            const response = await fetch(`${this.apiBaseUrl}/stats`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const stats = await response.json();
            console.log('📊 收到統計數據:', stats);
            
            // 更新統計介面
            this.updateStatsUI(stats);
            
            // 更新價格圖表
            this.updatePriceChart(stats);
            
            // 儲存上次統計數據（用於計算變化）
            this.lastStats = stats;
            
        } catch (error) {
            console.error('❌ 獲取統計數據失敗:', error);
            // 統計數據失敗不影響主要功能
        }
    }
    
    updateMetrics(data) {
        // 更新主要指標 (添加安全檢查)
        const currentTick = document.getElementById('current-tick');
        if (currentTick) currentTick.textContent = data.tick?.toLocaleString() || '--';
        
        const currentEpoch = document.getElementById('current-epoch');
        if (currentEpoch) currentEpoch.textContent = data.epoch || '--';
        
        const tickDuration = document.getElementById('tick-duration');
        if (tickDuration) tickDuration.textContent = `${data.duration || '--'}`;
        
        const networkHealth = document.getElementById('network-health');
        if (networkHealth) networkHealth.textContent = data.health?.overall || '--';
        
        // 更新 Epoch 進度
        this.updateEpochProgress(data);
    }
    
    updateEpochProgress(data) {
        console.log('📊 更新 Epoch 進度數據:', data);
        
        // 獲取統計數據以獲得準確的 Epoch 信息
        this.fetchAndUpdateEpochStats();
    }
    
    // ✅ 獲取並更新精確的 Epoch 統計數據
    async fetchAndUpdateEpochStats() {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000);
            
            const response = await fetch(`${this.apiBaseUrl}/stats`, {
                signal: controller.signal,
                headers: { 'Content-Type': 'application/json' }
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const statsData = await response.json();
            console.log('📈 Epoch 統計數據:', statsData);
            
            this.updateEpochProgressDisplay(statsData);
            
        } catch (error) {
            console.error('❌ Epoch 統計數據獲取失敗:', error);
            this.showEpochProgressError();
        }
    }
    
    // ✅ 更新 Epoch 進度顯示 - 使用真實數據
    updateEpochProgressDisplay(statsData) {
        const currentTick = statsData.currentTick || 0;
        const ticksInEpoch = statsData.ticksInCurrentEpoch || 0;
        const epochQuality = statsData.epochTickQuality || 0;
        const emptyTicks = statsData.emptyTicksInCurrentEpoch || 0;
        
        // 計算 Initial Tick (當前 tick - 當前 epoch 中的 tick 數量)
        const initialTick = currentTick - ticksInEpoch;
        
        // 計算 Epoch 的預估總長度（基於當前品質推算）
        // 假設目標是 100% 品質，根據當前品質推算總長度
        const estimatedTotalTicks = Math.round(ticksInEpoch * (100 / Math.max(epochQuality, 1)));
        
        // 更新顯示值
        const initialTickValue = document.getElementById('initial-tick-value');
        if (initialTickValue) initialTickValue.textContent = initialTick.toLocaleString();
        
        const currentTickValue = document.getElementById('current-tick-value');
        if (currentTickValue) currentTickValue.textContent = currentTick.toLocaleString();
        
        // 計算進度百分比 (使用 epochTickQuality 作為主要指標)
        const progressPercentage = Math.min(epochQuality, 100);
        
        // 更新進度條
        const progressBar = document.getElementById('epoch-progress');
        const progressText = document.getElementById('epoch-progress-text');
        
        if (progressBar) {
            progressBar.style.width = `${progressPercentage}%`;
            
            // 根據進度設定顏色
            if (progressPercentage >= 90) {
                progressBar.className = 'progress-bar bg-success';
            } else if (progressPercentage >= 70) {
                progressBar.className = 'progress-bar bg-info';
            } else if (progressPercentage >= 50) {
                progressBar.className = 'progress-bar bg-warning';
            } else {
                progressBar.className = 'progress-bar bg-danger';
            }
        }
        
        if (progressText) {
            progressText.textContent = `${progressPercentage.toFixed(1)}%`;
        }
        
        // 更新其他統計信息
        const remainingTicksElement = document.getElementById('remaining-ticks');
        if (remainingTicksElement) {
            const remainingTicks = Math.max(0, estimatedTotalTicks - ticksInEpoch);
            remainingTicksElement.textContent = remainingTicks.toLocaleString();
        }
        
        const progressPercentageElement = document.getElementById('progress-percentage');
        if (progressPercentageElement) {
            progressPercentageElement.textContent = `${progressPercentage.toFixed(1)}%`;
        }
        
        // 更新預估時間 (假設每 tick 1 秒)
        const estimatedTimeElement = document.getElementById('estimated-time');
        if (estimatedTimeElement) {
            const remainingTicks = Math.max(0, estimatedTotalTicks - ticksInEpoch);
            const remainingSeconds = remainingTicks * 1; // 假設每 tick 1 秒
            
            if (remainingSeconds > 3600) {
                const hours = Math.floor(remainingSeconds / 3600);
                const minutes = Math.floor((remainingSeconds % 3600) / 60);
                estimatedTimeElement.textContent = `${hours}h ${minutes}m`;
            } else if (remainingSeconds > 60) {
                const minutes = Math.floor(remainingSeconds / 60);
                estimatedTimeElement.textContent = `${minutes}m`;
            } else {
                estimatedTimeElement.textContent = `${remainingSeconds}s`;
            }
        }
        
        console.log(`✅ Epoch 進度更新: ${progressPercentage.toFixed(1)}% (${ticksInEpoch}/${estimatedTotalTicks} ticks)`);
    }
    
    // ✅ 顯示 Epoch 進度錯誤
    showEpochProgressError() {
        const elements = ['initial-tick-value', 'current-tick-value', 'remaining-ticks', 'estimated-time', 'progress-percentage'];
        elements.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.textContent = '--';
        });
        
        const progressBar = document.getElementById('epoch-progress');
        if (progressBar) {
            progressBar.style.width = '0%';
            progressBar.className = 'progress-bar bg-secondary';
        }
        
        const progressText = document.getElementById('epoch-progress-text');
        if (progressText) {
            progressText.textContent = '0%';
        }
    }
    
    updateCharts(data) {
        const now = new Date();
        const timeLabel = now.toLocaleTimeString('zh-TW', { 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit' 
        });
        
        // 添加新數據點
        this.tickHistory.push(data.tick || 0);
        this.durationHistory.push(data.duration || 0);
        this.timeLabels.push(timeLabel);
        
        // 限制數據點數量
        if (this.tickHistory.length > this.maxDataPoints) {
            this.tickHistory.shift();
            this.durationHistory.shift();
            this.timeLabels.shift();
        }
        
        // 更新圖表
        this.updateTickChart();
        this.updateDurationChart();
    }
    
    updateTickChart() {
        if (this.tickChart) {
            this.tickChart.data.labels = [...this.timeLabels];
            this.tickChart.data.datasets[0].data = [...this.tickHistory];
            this.tickChart.update('none');
        }
    }
    
    updateDurationChart() {
        if (this.durationChart) {
            this.durationChart.data.labels = [...this.timeLabels];
            this.durationChart.data.datasets[0].data = [...this.durationHistory];
            this.durationChart.update('none');
        }
    }
    
    updateHealthIndicators(health) {
        if (!health) return;
        
        // 更新健康指標徽章
        this.updateHealthBadge('health-overall', health.overall);
        this.updateHealthBadge('health-tick', health.tick_status);
        this.updateHealthBadge('health-epoch', health.epoch_status);
        this.updateHealthBadge('health-duration', health.duration_status);
    }
    
    updateHealthBadge(elementId, status) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        element.textContent = status || '--';
        
        // 移除所有狀態類別
        element.className = 'badge';
        
        // 根據狀態添加適當的類別
        switch (status) {
            case '健康':
            case '正常':
            case '極快':
            case '快速':
                element.classList.add('bg-success');
                break;
            case '一般':
            case '稍慢':
                element.classList.add('bg-warning');
                break;
            case '緩慢':
            case '異常':
            case '錯誤':
                element.classList.add('bg-danger');
                break;
            case '離線':
                element.classList.add('bg-secondary');
                break;
            default:
                element.classList.add('bg-secondary');
        }
    }
    
    updateConnectionStatus(isConnected, status = null) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            if (isConnected) {
                if (status === '真實數據') {
                    statusElement.textContent = '🌐 真實數據';
                    statusElement.className = 'badge bg-success';
                    this.hideApiStatusAlert(); // 隱藏演示模式警告
                } else if (status === '演示模式') {
                    statusElement.textContent = '🎭 演示模式';
                    statusElement.className = 'badge bg-warning';
                    this.showApiStatusAlert('演示模式', '由於 CORS 限制，此版本使用動態模擬數據。如需真實數據，請使用本地版本或部署後端 API。');
                } else if (status === '連線中') {
                    statusElement.textContent = '🔗 連線中';
                    statusElement.className = 'badge bg-info';
                } else {
                    statusElement.textContent = status || '🔗 已連線';
                    statusElement.className = 'badge bg-success';
                    this.hideApiStatusAlert(); // 隱藏演示模式警告
                }
            } else {
                statusElement.textContent = status === '連線失敗' ? '⚠️ 連線失敗' : '❌ 離線';
                statusElement.className = 'badge bg-danger';
            }
        }
    }
    
    showApiStatusAlert(title, message) {
        const alertElement = document.getElementById('api-status-alert');
        const messageElement = document.getElementById('api-status-message');
        
        if (alertElement && messageElement) {
            messageElement.innerHTML = `<strong>${title}：</strong> ${message}`;
            alertElement.className = 'alert alert-warning';
        }
    }
    
    hideApiStatusAlert() {
        const alertElement = document.getElementById('api-status-alert');
        if (alertElement) {
            alertElement.className = 'alert d-none';
        }
    }
    
    updateLastUpdateTime() {
        const lastUpdateElement = document.getElementById('last-update');
        if (lastUpdateElement) {
            const now = new Date();
            const timeString = now.toLocaleString('zh-TW');
            lastUpdateElement.textContent = timeString;
        }
    }
    
    initCharts() {
        // 檢測暗黑模式
        const isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
        const textColor = isDarkMode ? '#e8eaed' : '#202124';
        
        // 初始化 Tick 趨勢圖
        const tickCtx = document.getElementById('tickChart').getContext('2d');
        this.tickChart = new Chart(tickCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Tick 數值',
                    data: [],
                    borderColor: '#4285f4',
                    backgroundColor: 'rgba(66, 133, 244, 0.15)',
                    tension: 0.4,
                    fill: true,
                    borderWidth: 3,
                    pointBackgroundColor: '#4285f4',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        grid: { color: gridColor },
                        ticks: { color: textColor }
                    },
                    y: {
                        beginAtZero: false,
                        grid: { color: gridColor },
                        ticks: {
                            color: textColor,
                            callback: function(value) {
                                return value.toLocaleString();
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
        
        // 初始化 Duration 變化圖
        const durationCtx = document.getElementById('durationChart').getContext('2d');
        this.durationChart = new Chart(durationCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: '持續時間 (秒)',
                    data: [],
                    borderColor: '#34a853',
                    backgroundColor: 'rgba(52, 168, 83, 0.15)',
                    tension: 0.4,
                    fill: true,
                    borderWidth: 3,
                    pointBackgroundColor: '#34a853',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        grid: { color: gridColor },
                        ticks: { color: textColor }
                    },
                    y: {
                        beginAtZero: true,
                        max: 3,
                        grid: { color: gridColor },
                        ticks: { 
                            color: textColor,
                            stepSize: 0.5
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    startAutoUpdate() {
        // 清除現有定時器，防止重複
        this.stopAutoUpdate();
        
        console.log('🔄 啟動自動更新...');
        
        // 更新 tick 數據（每5秒）
        this.dataUpdateTimer = setInterval(async () => {
            try {
                await this.fetchAndUpdateData();
            } catch (error) {
                console.error('❌ 自動更新失敗:', error);
                // 連續失敗超過3次時可考慮停止自動更新
            }
        }, this.updateInterval);
        
        // 更新統計數據（每30秒，統計數據變化較慢）
        this.statsUpdateTimer = setInterval(async () => {
            try {
                await this.fetchAndUpdateStats();
            } catch (error) {
                console.error('❌ 統計數據更新失敗:', error);
            }
        }, this.updateInterval * 6);
        
        console.log(`✅ 自動更新已啟動 (Tick: ${this.updateInterval/1000}秒, Stats: ${this.updateInterval*6/1000}秒)`);
    }
    
    stopAutoUpdate() {
        if (this.dataUpdateTimer) {
            clearInterval(this.dataUpdateTimer);
            this.dataUpdateTimer = null;
        }
        if (this.statsUpdateTimer) {
            clearInterval(this.statsUpdateTimer);
            this.statsUpdateTimer = null;
        }
        console.log('🛑 自動更新已停止');
    }
    
    showLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.remove('hidden');
        }
    }
    
    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.add('hidden');
        }
    }
    
    showConnectionError() {
        this.updateConnectionStatus(false);
        // 可以在這裡添加更多錯誤處理邏輯
    }
    
    bindEvents() {
        // 可以在這裡添加事件監聽器
        // 例如：手動刷新按鈕、設定等
    }
    
    updateStatsUI(stats) {
        // 更新活躍地址數
        const activeAddresses = document.getElementById('active-addresses');
        if (activeAddresses) {
            activeAddresses.textContent = this.formatNumber(stats.activeAddresses);
        }
        
        // 更新市值
        const marketCap = document.getElementById('market-cap');
        if (marketCap) {
            marketCap.textContent = '$' + this.formatNumber(stats.marketCap);
        }
        
        // 更新價格
        const price = document.getElementById('qubic-price');
        if (price) {
            price.textContent = '$' + stats.price.toFixed(9);
        }
        
        // 更新 Epoch 品質
        const epochQuality = document.getElementById('epoch-quality');
        if (epochQuality) {
            epochQuality.textContent = stats.epochTickQuality.toFixed(2) + '%';
        }
        
        // 更新流通供應量
        const circulatingSupply = document.getElementById('circulating-supply');
        if (circulatingSupply) {
            circulatingSupply.textContent = this.formatLargeNumber(stats.circulatingSupply);
        }
        
        // 更新已燒毀 QUs
        const burnedQus = document.getElementById('burned-qus');
        if (burnedQus) {
            burnedQus.textContent = this.formatLargeNumber(stats.burnedQus);
        }
        
        // 更新變化指標（如果有之前的數據）
        if (this.lastStats) {
            this.updateChangeIndicators(stats);
        }
    }
    
    updateChangeIndicators(currentStats) {
        const changes = [
            { id: 'active-addresses-change', current: currentStats.activeAddresses, previous: this.lastStats.activeAddresses },
            { id: 'market-cap-change', current: currentStats.marketCap, previous: this.lastStats.marketCap },
            { id: 'price-change', current: currentStats.price, previous: this.lastStats.price },
            { id: 'quality-change', current: currentStats.epochTickQuality, previous: this.lastStats.epochTickQuality }
        ];
        
        changes.forEach(change => {
            const element = document.getElementById(change.id);
            if (element && change.previous !== undefined) {
                const diff = change.current - change.previous;
                const percentChange = ((diff / change.previous) * 100);
                
                element.textContent = `${percentChange >= 0 ? '+' : ''}${percentChange.toFixed(2)}%`;
                
                // 設定顏色
                element.className = 'stat-change';
                if (percentChange > 0) {
                    element.classList.add('positive');
                } else if (percentChange < 0) {
                    element.classList.add('negative');
                } else {
                    element.classList.add('neutral');
                }
            }
        });
    }
    
    updatePriceChart(stats) {
        if (!this.priceChart) {
            this.initPriceChart();
        }
        
        const now = new Date();
        const timeLabel = now.toLocaleTimeString('zh-TW', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        // 添加新數據點
        this.priceHistory.push(stats.price);
        this.timeLabels.push(timeLabel);
        
        // 保持最大數據點數量
        if (this.priceHistory.length > this.maxDataPoints) {
            this.priceHistory.shift();
            this.timeLabels.shift();
        }
        
        // 更新圖表
        if (this.priceChart) {
            this.priceChart.data.labels = [...this.timeLabels];
            this.priceChart.data.datasets[0].data = [...this.priceHistory];
            this.priceChart.update('none'); // 無動畫更新以提高性能
        }
    }
    
    initPriceChart() {
        const ctx = document.getElementById('priceChart');
        if (!ctx) return;
        
        // 檢測暗黑模式
        const isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const textColor = isDarkMode ? '#e8eaed' : '#5f6368';
        const gridColor = isDarkMode ? '#3c4043' : '#e8eaed';
        
        this.priceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'QU 價格 (USD)',
                    data: [],
                    borderColor: '#34a853',
                    backgroundColor: 'rgba(52, 168, 83, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        grid: { color: gridColor },
                        ticks: { color: textColor }
                    },
                    y: {
                        beginAtZero: false,
                        grid: { color: gridColor },
                        ticks: { 
                            color: textColor,
                            callback: function(value) {
                                return '$' + value.toFixed(9);
                            }
                        }
                    }
                },
                elements: {
                    point: {
                        radius: 3,
                        hoverRadius: 6
                    }
                }
            }
        });
    }
    
    formatNumber(num) {
        if (num >= 1e9) {
            return (num / 1e9).toFixed(1) + 'B';
        } else if (num >= 1e6) {
            return (num / 1e6).toFixed(1) + 'M';
        } else if (num >= 1e3) {
            return (num / 1e3).toFixed(1) + 'K';
        }
        return num.toLocaleString();
    }
    
    formatLargeNumber(num) {
        if (num >= 1e15) {
            return (num / 1e15).toFixed(1) + 'P';
        } else if (num >= 1e12) {
            return (num / 1e12).toFixed(1) + 'T';
        } else if (num >= 1e9) {
            return (num / 1e9).toFixed(1) + 'B';
        } else if (num >= 1e6) {
            return (num / 1e6).toFixed(1) + 'M';
        }
        return num.toLocaleString();
    }
}

// 當頁面載入完成時初始化 Dashboard
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new QDashboard();
});
