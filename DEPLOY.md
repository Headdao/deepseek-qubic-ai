# QDashboard_Lite Firebase 部署指南

## 📋 部署概述

QDashboard_Lite 採用前後端分離架構：
- **前端**: Firebase Hosting（靜態網站託管）
- **後端**: Google Cloud Run（容器化 API 服務）

## 🎯 部署策略

### 方案一：完整部署（推薦）
前端 + 後端都部署到 Google Cloud

### 方案二：僅前端部署
只部署前端，API 使用現有服務

## 🚀 快速部署

### 1. 準備工作

確保已安裝必要工具：
```bash
# Firebase CLI
npm install -g firebase-tools

# Google Cloud SDK（可選，用於後端部署）
# 下載：https://cloud.google.com/sdk/docs/install
```

### 2. 設置 Google Cloud 專案

```bash
# 創建新專案（或使用現有的）
gcloud projects create qdashboard-lite

# 設置當前專案
gcloud config set project qdashboard-lite

# 啟用必要的 API
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 3. 執行自動部署

```bash
# 執行部署腳本
./deploy.sh
```

## 🛠 手動部署步驟

### 步驟 1: 部署後端 API

```bash
# 構建並部署到 Cloud Run
gcloud builds submit --config cloudbuild.yaml

# 查看部署結果
gcloud run services list
```

### 步驟 2: 更新前端配置

```bash
# 獲取 Cloud Run URL
BACKEND_URL=$(gcloud run services describe qdashboard-api --region=us-central1 --format='value(status.url)')

# 更新前端配置
# 編輯 frontend/config.js，設置 PROD_API_BASE_URL
```

### 步驟 3: 部署前端

```bash
# 登入 Firebase
firebase login

# 設置專案
firebase use qdashboard-lite

# 部署前端
firebase deploy --only hosting
```

## 🔧 配置說明

### 環境自動檢測

前端會自動檢測運行環境：
- **localhost**: 使用 `http://localhost:8000/api`
- **生產環境**: 使用 Cloud Run API URL

### 關鍵配置文件

1. **`firebase.json`**: Firebase Hosting 配置
2. **`cloudbuild.yaml`**: Cloud Build 配置
3. **`Dockerfile`**: 後端容器配置
4. **`frontend/config.js`**: API 端點配置

## 📊 部署後驗證

### 1. 檢查前端

訪問：`https://qdashboard-lite.web.app`

應該能看到：
- ✅ 頁面正常載入
- ✅ 統計卡片顯示數據
- ✅ 圖表正常渲染
- ✅ 自動更新功能

### 2. 檢查後端 API

```bash
# 測試 API 端點
curl https://YOUR-CLOUD-RUN-URL/api/tick
curl https://YOUR-CLOUD-RUN-URL/api/stats
```

## 🔍 故障排除

### 常見問題

1. **CORS 錯誤**
   - 確認後端 CORS 配置正確
   - 檢查 API URL 是否正確

2. **API 連接失敗**
   - 確認 Cloud Run 服務運行正常
   - 檢查 `frontend/config.js` 中的 URL

3. **QubiPy 依賴問題**
   - 確認 Dockerfile 中正確複製了 QubiPy 目錄
   - 檢查 requirements.txt

### 查看日誌

```bash
# Cloud Run 日誌
gcloud logs read --service=qdashboard-api

# Firebase Hosting 部署日誌
firebase hosting:channel:list
```

## 💡 優化建議

### 效能優化

1. **CDN 緩存**: Firebase Hosting 自動提供全球 CDN
2. **壓縮**: 啟用 gzip 壓縮
3. **緩存策略**: 靜態資源設置適當的緩存標頭

### 安全考量

1. **API 限制**: 考慮添加 API 頻率限制
2. **HTTPS**: Firebase Hosting 自動提供 SSL
3. **監控**: 設置 Cloud Monitoring 警報

## 📱 PWA 功能

部署後的應用支援：
- ✅ 離線訪問
- ✅ 安裝到桌面/主屏幕
- ✅ 推送通知（可擴展）

## 📞 技術支援

如遇問題，請檢查：
1. 部署日誌
2. 瀏覽器開發者工具
3. Cloud Run 服務狀態

---

🎉 祝您部署順利！
