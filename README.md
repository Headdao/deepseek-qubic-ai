# QDashboard - Qubic 網路監控儀表板

## 📋 專案簡介

QDashboard 是一個專為 Qubic 網路設計的即時監控儀表板，提供網路關鍵指標的可視化展示。本專案聚焦於行動裝置優化，讓用戶能隨時隨地監控 Qubic 網路狀況。

## ✨ 主要功能

### 🎯 四大核心指標
1. **Tick (區塊數)** - 即時顯示網路區塊高度趨勢
2. **Epoch (週期數)** - 監控網路週期進度
3. **Duration (持續時間)** - 追蹤每個 Tick 的處理時間
4. **Initial Tick (起始 Tick)** - 顯示當前 Epoch 的起始點

### 📊 視覺化特色
- **即時圖表** - 使用 Chart.js 呈現動態數據
- **健康指標** - 智能分析網路健康狀況
- **響應式設計** - 完美適配行動裝置
- **PWA 支援** - 可安裝為行動應用程式

## 🛠 技術架構

### 後端 (Flask)
- **框架**: Flask + Flask-CORS
- **數據源**: QubiPy (Qubic RPC 客戶端)
- **API**: RESTful JSON API

### 前端 (現代 Web)
- **框架**: HTML5 + Bootstrap 5
- **圖表**: Chart.js
- **樣式**: 自訂 CSS + Bootstrap Icons
- **支援**: PWA (Progressive Web App)

## 🚀 快速開始

### 前置需求
- Python 3.10+
- QubiPy 函式庫

### 安裝步驟

1. **複製專案**
   ```bash
   cd /Users/apple/qubic/qdashboard
   ```

2. **建立虛擬環境**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   ```

3. **安裝依賴**
   ```bash
   pip install -r requirements.txt
   ```

4. **設定 QubiPy 路徑**
   確保 QubiPy 位於 `/Users/apple/qubic/QubiPy-main`

5. **啟動應用程式**
   ```bash
   python app.py
   ```

6. **開啟瀏覽器**
   前往 http://localhost:5000

## 📱 行動裝置使用

### PWA 安裝 (推薦)
1. 使用 Safari (iOS) 或 Chrome (Android) 開啟網站
2. 點選「加入主畫面」或「安裝應用程式」
3. 即可在主畫面直接啟動 QDashboard

### 特色功能
- ✅ 離線支援 (部分功能)
- ✅ 全螢幕體驗
- ✅ 原生應用程式感受
- ✅ 自動更新數據 (每 5 秒)

## 🔧 設定說明

### API 端點
- `GET /api/tick` - 獲取即時 tick 資訊
- `GET /api/status` - 檢查 API 狀態

### 回應格式
```json
{
  "tick": 31469232,
  "epoch": 174,
  "duration": 2,
  "initialTick": 31231000,
  "timestamp": 1755673174,
  "health": {
    "overall": "健康",
    "tick_status": "正常",
    "epoch_status": "正常",
    "duration_status": "正常"
  }
}
```

## 📊 指標解讀

### Tick 趨勢分析
- **穩定上升** → 網路正常運行
- **停滯/下降** → 可能出現共識異常

### Duration 監控
- **0-2 秒** → 正常範圍
- **3-5 秒** → 稍慢，需關注
- **>5 秒** → 異常，可能有問題

### 健康狀況
- **健康** 🟢 - 所有指標正常
- **一般** 🟡 - 部分指標異常
- **異常** 🔴 - 嚴重問題

## 🧪 測試

### API 測試
```bash
python test_api.py
```

### 整合測試
```bash
python test_integration.py
```

### QubiPy 連接測試
```bash
python test_qubipy.py
```

## 📦 部署

### Google Cloud Run (推薦)
1. 建立 `Dockerfile`
2. 使用 `gcloud` 部署
3. 設定自動縮放

### Firebase Hosting (靜態資源)
1. 部署前端文件至 Firebase
2. 設定 API 代理

### 本地生產環境
```bash
gunicorn --bind 0.0.0.0:8000 app:app
```

## 🔐 安全性

- CORS 已正確設定
- 無敏感資訊暴露
- 僅讀取公開 RPC 數據
- 建議使用 HTTPS (生產環境)

## 🤝 貢獻指南

1. Fork 專案
2. 建立功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

## 📝 變更日誌

### v0.1.0 (2025-08-20)
- ✅ 基礎 API 實作
- ✅ 響應式前端界面
- ✅ 四大指標視覺化
- ✅ PWA 支援
- ✅ 即時數據更新
- ✅ 健康狀況監控

## 📄 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 文件

## 🆘 支援與回饋

如有問題或建議，請建立 Issue 或聯繫開發團隊。

---

**QDashboard v0.1.0** | 專為 Qubic 網路設計的現代化監控解決方案
