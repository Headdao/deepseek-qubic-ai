// QDashboard 配置文件 - 動態端口配置
const CONFIG = {
    // 動態獲取當前頁面的端口
    getDynamicApiBaseUrl() {
        const protocol = window.location.protocol;
        const hostname = window.location.hostname || 'localhost';
        const port = window.location.port || '3000';
        return `${protocol}//${hostname}:${port}/api`;
    },
    
    // 開發環境 API 端點 (備用)
    DEV_API_BASE_URL: null, // 將使用動態檢測
    
    // 生產環境 API 端點 (演示模式，返回模擬數據)
    PROD_API_BASE_URL: null, // 設為 null 將使用模擬數據
    
    // 自動檢測環境
    getApiBaseUrl() {
        // 優先使用動態端口檢測
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return this.getDynamicApiBaseUrl();
        } else {
            return this.PROD_API_BASE_URL; // null = 演示模式
        }
    },
    
            // 檢查是否應該嘗試真實 API
        shouldTryRealApi() {
            return false; // 使用本地後端 API 替代直接調用
        },
    
    // 模擬數據 (用於演示)
    getMockData() {
        return {
            tick: Math.floor(31470000 + Math.random() * 1000),
            epoch: 174,
            duration: Math.floor(Math.random() * 3),
            initialTick: 31231000,
            timestamp: Math.floor(Date.now() / 1000),
            health: {
                overall: "健康",
                tick_status: "正常",
                epoch_status: "正常", 
                duration_status: ["極快", "快速", "正常"][Math.floor(Math.random() * 3)]
            }
        };
    },
    
    getMockStats() {
        const basePrice = 0.000002804;
        const variation = (Math.random() - 0.5) * 0.0000001;
        const price = basePrice + variation;
        
        return {
            activeAddresses: 592605 + Math.floor((Math.random() - 0.5) * 1000),
            marketCap: Math.floor(price * 154906810258577),
            price: price,
            epochTickQuality: 97.28 + (Math.random() - 0.5) * 0.5,
            circulatingSupply: 154906810258577,
            burnedQus: 19093189741423,
            timestamp: Math.floor(Date.now() / 1000)
        };
    }
};

// 全域配置
window.QDASHBOARD_CONFIG = CONFIG;
