# 前端 AI 組件使用指南

## 📋 概述

本指南介紹 Qubic AI Compute Layer 專案中新建立的前端 AI 組件，包括 AI 分析面板、互動式問答、F12 風格開發者控制台等功能。

## 🎯 功能特色

### 1. AI 智能分析面板
- **自動分析**: 定期分析 Qubic 網路數據
- **評分系統**: 0-100 分的健康評分
- **洞察建議**: 結構化的分析結果和建議
- **歷史記錄**: 保存最近 10 次分析結果

### 2. 互動式問答組件  
- **自然語言問答**: 支援中文問答互動
- **快速問題**: 預設常見問題快速按鈕
- **上下文理解**: 結合當前 Qubic 數據回答
- **對話歷史**: 保留對話記錄

### 3. F12 風格開發者控制台
- **即時日誌**: 系統、AI、API 等各類日誌
- **網路監控**: 攔截並顯示所有 API 調用
- **性能監控**: CPU、記憶體、延遲等指標
- **執行追蹤**: AI 推理流程可視化
- **應用狀態**: 模型狀態、集群信息

## 🚀 快速開始

### 1. 啟動服務

```bash
# 啟動後端 AI 服務
source venv/bin/activate
python app.py

# 訪問前端界面  
open http://localhost:5000/qdashboard/
```

### 2. 使用 AI 分析

1. 點擊「開始分析」按鈕
2. 等待 AI 分析完成 (約 3-12 秒)
3. 查看分析結果和建議
4. 點擊「歷史記錄」查看過往分析

### 3. 使用問答功能

1. 在問答區域輸入問題
2. 或點擊快速問題按鈕
3. 等待 AI 回答
4. 繼續對話互動

### 4. 開啟開發者控制台

- 按 `F12` 鍵開啟/關閉控制台
- 或點擊右下角觸發按鈕
- 切換不同標籤頁查看詳細信息

## 📊 API 端點

### AI 分析端點

**POST** `/api/ai/analyze`
```json
{
  "data": {
    "tick": 15234567,
    "epoch": 134,
    "duration": 1.2,
    "health": {
      "overall": "健康"
    }
  },
  "analysis_type": "comprehensive"
}
```

**回應範例:**
```json
{
  "summary": "網路運行穩定",
  "insights": [
    "當前 Tick 15234567 顯示網路運行良好",
    "Tick 持續時間 1.2 秒屬於正常範圍"
  ],
  "recommendations": [
    "建議定期檢查 Tick 持續時間變化"
  ],
  "score": 85,
  "timestamp": "2025-08-21T09:15:10.000Z"
}
```

### AI 問答端點

**POST** `/api/ai/query`
```json
{
  "question": "當前網路狀況如何？",
  "context": {
    "tick": 15234567,
    "epoch": 134
  }
}
```

**回應範例:**
```json
{
  "answer": "根據當前數據分析，Qubic 網路運行穩定...",
  "confidence": 0.85,
  "sources": ["qubic_knowledge", "current_data"]
}
```

## 🎨 UI 組件說明

### AI 分析面板結構

```html
<div id="ai-analysis-panel" class="card">
  <div class="card-header">
    <h5>AI 智能分析</h5>
    <span id="ai-status" class="badge">就緒</span>
  </div>
  <div class="card-body">
    <div id="ai-analysis-results">
      <!-- 分析結果顯示區 -->
    </div>
    <button id="start-analysis-btn">開始分析</button>
  </div>
</div>
```

### 問答組件結構

```html
<div id="ai-qa-panel" class="card">
  <div class="card-header">
    <h5>AI 問答助手</h5>
  </div>
  <div class="card-body">
    <div id="qa-conversation">
      <!-- 對話歷史 -->
    </div>
    <div class="quick-questions">
      <!-- 快速問題按鈕 -->
    </div>
    <div class="input-group">
      <input id="qa-input" type="text" placeholder="輸入問題...">
      <button id="qa-send-btn">發送</button>
    </div>
  </div>
</div>
```

### 開發者控制台結構

```html
<div id="qubic-dev-console" class="qubic-dev-console">
  <div class="console-header">
    <!-- 標題和控制按鈕 -->
  </div>
  <div class="console-tabs">
    <!-- Console, Network, Performance, Sources, Application -->
  </div>
  <div class="console-content">
    <!-- 標籤頁內容 -->
  </div>
</div>
```

## ⚙️ 配置選項

### AI 組件配置

```javascript
// 在 frontend/js/ai-components.js 中修改
class QubicAIComponents {
  constructor() {
    this.apiBaseUrl = 'http://localhost:5000/api';
    this.updateInterval = 5 * 60 * 1000; // 5分鐘自動分析
    this.maxHistoryEntries = 10; // 最大歷史記錄數
  }
}
```

### 開發者控制台配置

```javascript  
// 在 frontend/js/dev-console.js 中修改
class QubicDevConsole {
  constructor() {
    this.maxLogEntries = 1000; // 最大日誌條目
    this.autoConnect = true; // 自動連接 WebSocket
    this.defaultTab = 0; // 預設標籤頁 (0=Console)
  }
}
```

## 🎛️ 自訂樣式

### AI 組件樣式

主要 CSS 類別：
- `.analysis-results` - 分析結果容器
- `.score-circle` - 評分圓圈
- `.conversation-container` - 對話容器
- `.quick-question-btn` - 快速問題按鈕

### 開發者控制台樣式

主要 CSS 類別：
- `.qubic-dev-console` - 主控制台容器
- `.console-header` - 標題欄
- `.console-tabs` - 標籤頁導航
- `.log-entry` - 日誌條目

## 🔧 故障排除

### 常見問題

**1. AI 分析失敗**
- 檢查後端服務是否啟動
- 確認 AI 模型已正確載入
- 查看瀏覽器控制台錯誤信息

**2. 問答無回應**
- 檢查網路連接
- 確認問題格式正確
- 查看 F12 控制台中的 API 調用記錄

**3. 開發者控制台無法開啟**
- 確認 JavaScript 沒有錯誤
- 檢查 CSS 文件是否正確載入
- 嘗試刷新頁面

### 除錯技巧

1. **使用瀏覽器開發者工具**
   - 按 F12 開啟瀏覽器控制台
   - 查看 Console 標籤頁的錯誤信息
   - 檢查 Network 標籤頁的 API 調用

2. **查看 Qubic 開發者控制台**
   - 按 F12 開啟 Qubic 專用控制台
   - 查看詳細的系統日誌
   - 監控 API 調用和性能指標

3. **檢查後端日誌**
   ```bash
   # 查看後端服務日誌
   python app.py
   ```

## 📱 行動裝置支援

### 響應式設計特色

- **自適應佈局**: 支援不同螢幕尺寸
- **觸控優化**: 按鈕和輸入框觸控友好
- **字體縮放**: 小螢幕上自動調整字體大小
- **滑動支援**: 支援滑動切換標籤頁

### 行動裝置使用建議

1. **豎屏模式**: 建議使用豎屏模式獲得最佳體驗
2. **全螢幕**: 使用 PWA 模式獲得全螢幕體驗  
3. **觸控操作**: 支援長按、雙擊等手勢

## 🔄 更新和維護

### 版本更新

```bash
# 拉取最新程式碼
git pull origin main

# 重新啟動服務
source venv/bin/activate
python app.py
```

### 清除快取

```javascript
// 在瀏覽器控制台執行
localStorage.clear();
sessionStorage.clear();
location.reload();
```

## 📞 技術支援

如遇到問題，請：

1. 查看本指南的故障排除部分
2. 檢查 GitHub Issues 是否有類似問題
3. 提交新的 Issue 並附上錯誤信息
4. 聯繫開發團隊獲得支援

---

**版本**: v1.0  
**更新日期**: 2025-08-21  
**維護**: Qubic AI Compute Layer 開發團隊


