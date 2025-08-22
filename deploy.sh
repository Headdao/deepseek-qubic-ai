#!/bin/bash

# QDashboard_Lite Firebase 部署腳本

set -e

echo "🚀 開始部署 QDashboard_Lite..."

# 檢查 Firebase CLI
if ! command -v firebase &> /dev/null; then
    echo "❌ Firebase CLI 未安裝，請執行: npm install -g firebase-tools"
    exit 1
fi

# 檢查 gcloud CLI
if ! command -v gcloud &> /dev/null; then
    echo "⚠️  gcloud CLI 未安裝，請安裝 Google Cloud SDK"
    echo "   將只部署前端到 Firebase Hosting"
    DEPLOY_BACKEND=false
else
    DEPLOY_BACKEND=true
fi

# 設置項目變數
PROJECT_ID="qdashboard-lite"
REGION="us-central1"

echo "📋 項目 ID: $PROJECT_ID"
echo "🌍 地區: $REGION"

# 1. 部署後端到 Cloud Run (可選)
if [ "$DEPLOY_BACKEND" = true ]; then
    echo ""
    echo "🔧 部署後端 API 到 Cloud Run..."
    
    # 設置 gcloud 項目
    gcloud config set project $PROJECT_ID
    
    # 啟用必要的 API
    echo "   啟用 Cloud Run API..."
    gcloud services enable run.googleapis.com
    gcloud services enable cloudbuild.googleapis.com
    
    # 構建並部署
    echo "   構建 Docker 映像..."
    gcloud builds submit --config cloudbuild.yaml
    
    # 獲取 Cloud Run URL
    BACKEND_URL=$(gcloud run services describe qdashboard-api --region=$REGION --format='value(status.url)')
    echo "   ✅ 後端部署完成: $BACKEND_URL"
    
    # 更新前端配置
    echo "   更新前端 API 配置..."
    sed -i.bak "s|PROD_API_BASE_URL: '.*'|PROD_API_BASE_URL: '$BACKEND_URL/api'|" frontend/config.js
    rm frontend/config.js.bak
    
else
    echo ""
    echo "⚠️  跳過後端部署 (gcloud CLI 未安裝)"
    echo "   請手動配置 frontend/config.js 中的 PROD_API_BASE_URL"
fi

# 2. 部署前端到 Firebase Hosting
echo ""
echo "🌐 部署前端到 Firebase Hosting..."

# 登入 Firebase (如果需要)
echo "   檢查 Firebase 登入狀態..."
if ! firebase projects:list &> /dev/null; then
    echo "   請登入 Firebase..."
    firebase login
fi

# 初始化項目 (如果需要)
echo "   初始化 Firebase 項目..."
firebase use $PROJECT_ID || firebase use --add

# 部署
echo "   部署中..."
firebase deploy --only hosting

echo ""
echo "🎉 部署完成！"
echo ""
echo "📱 前端 URL: https://$PROJECT_ID.web.app"
if [ "$DEPLOY_BACKEND" = true ]; then
    echo "🔗 後端 API: $BACKEND_URL"
fi
echo ""
echo "💡 提示:"
echo "   - 前端會自動檢測環境並使用對應的 API 端點"
echo "   - 開發環境 (localhost) 使用本地 API"
echo "   - 生產環境使用 Cloud Run API"
echo ""
