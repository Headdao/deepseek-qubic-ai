# ☁️ GCP 配置指南
## deepseek-qubic-ai 專案設置完成指南

### 🎉 **專案建立成功！**
- **專案名稱**: deepseek-qubic-ai
- **專案編號**: 755847877448
- **專案 ID**: deepseek-qubic-ai
- **狀態**: ✅ Active

---

## 🚀 **下一步：立即執行的關鍵配置**

### **Step 1: 啟用必要的 API (5分鐘)**

在 GCP Console 中 (https://console.cloud.google.com)：

1. **確認您在正確的專案**
   - 確認上方顯示「deepseek-qubic-ai」

2. **前往 API 與服務**
   - 左側選單 → 「API 與服務」→ 「程式庫」

3. **啟用以下 API** (逐一搜尋並啟用)：
   ```
   ✅ 必須啟用的 API：
   - Compute Engine API
   - Cloud Run API
   - Cloud Build API
   - Identity and Access Management (IAM) API
   - Cloud Storage API
   - Cloud Functions API
   - Cloud Logging API
   - Cloud Monitoring API
   ```

4. **驗證 API 啟用**
   - 前往「API 與服務」→ 「已啟用的 API」
   - 確認上述 API 都顯示為「已啟用」

---

### **Step 2: 設置計費告警 (5分鐘)**

1. **前往計費**
   - 左側選單 → 「計費」→ 「預算與告警」

2. **建立預算**
   ```yaml
   預算設定:
     名稱: "deepseek-qubic-ai-budget"
     金額: "$200 USD" (保留 $100 緩衝)
     期間: "每月"
     
   告警閾值:
     - 50% = $100 (第一次警告)
     - 80% = $160 (注意警告) 
     - 90% = $180 (緊急警告)
     - 100% = $200 (最終警告)
   ```

3. **通知設定**
   - 電子郵件通知：您的 Gmail 地址
   - 啟用「將告警發送至 Cloud Monitoring」

---

### **Step 3: 安裝 gcloud CLI (本地開發)**

```bash
# macOS 安裝
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# 初始化
gcloud init

# 選擇步驟：
# 1. 登錄您的 Google 帳號
# 2. 選擇專案: deepseek-qubic-ai
# 3. 選擇預設區域: asia-east1 (台灣)

# 驗證安裝
gcloud config list
gcloud projects list
```

---

### **Step 4: 設置服務帳戶 (5分鐘)**

```bash
# 建立服務帳戶
gcloud iam service-accounts create deepseek-service-account \
    --description="DeepSeek AI Compute Layer Service Account" \
    --display-name="DeepSeek Service Account"

# 授予必要權限
gcloud projects add-iam-policy-binding deepseek-qubic-ai \
    --member="serviceAccount:deepseek-service-account@deepseek-qubic-ai.iam.gserviceaccount.com" \
    --role="roles/compute.admin"

gcloud projects add-iam-policy-binding deepseek-qubic-ai \
    --member="serviceAccount:deepseek-service-account@deepseek-qubic-ai.iam.gserviceaccount.com" \
    --role="roles/run.admin"

# 下載服務帳戶金鑰
gcloud iam service-accounts keys create ./gcp-service-account.json \
    --iam-account=deepseek-service-account@deepseek-qubic-ai.iam.gserviceaccount.com

# 設置環境變數
export GOOGLE_APPLICATION_CREDENTIALS="./gcp-service-account.json"
```

---

### **Step 5: 測試 GCP 環境 (3分鐘)**

```bash
# 測試 gcloud 連接
gcloud auth list
gcloud config get-value project

# 測試 Compute Engine (建立測試 VM)
gcloud compute instances create test-vm \
    --zone=asia-east1-a \
    --machine-type=e2-micro \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud

# 列出 VM (應該看到 test-vm)
gcloud compute instances list

# 刪除測試 VM (節省費用)
gcloud compute instances delete test-vm --zone=asia-east1-a --quiet
```

---

## 🔧 **為 DeepSeek 準備資源**

### **選擇適合的機器類型**
```yaml
開發環境 (本地測試):
  machine_type: "e2-standard-4"
  cpu: "4 vCPU"
  memory: "16 GB"
  estimated_cost: "~$100/month"

生產環境 (模型推理):
  machine_type: "n1-standard-8"  
  cpu: "8 vCPU"
  memory: "30 GB"
  gpu: "nvidia-tesla-t4" (可選)
  estimated_cost: "~$200/month"
```

### **預估成本計算**
```yaml
Phase_1_預估成本 (2個月):
  compute_engine: "$150"
  cloud_run: "$50"
  storage: "$20"
  networking: "$30"
  total: "$250"
  
剩餘預算: "$50" (緩衝)
```

---

## 📊 **配置驗證檢查清單**

### **✅ 必須完成的檢查**
- [ ] GCP 專案 `deepseek-qubic-ai` 建立成功
- [ ] 8 個必要 API 全部啟用
- [ ] 計費告警設置完成 ($100, $160, $180, $200)
- [ ] gcloud CLI 安裝並認證成功
- [ ] 服務帳戶建立和權限設定
- [ ] 測試 VM 建立和刪除成功

### **🔍 驗證指令**
```bash
# 檢查專案配置
gcloud config list project
gcloud services list --enabled

# 檢查計費
gcloud billing budgets list

# 檢查服務帳戶
gcloud iam service-accounts list

# 檢查配額
gcloud compute project-info describe --project=deepseek-qubic-ai
```

---

## 🚀 **完成後的下一步**

### **立即通知其他團隊**
1. **📊 Project Manager**: GCP 環境就緒，可以開始資源規劃
2. **💻 Development Team**: 可以開始準備 Cloud Run 部署腳本
3. **🧪 Testing Team**: 可以規劃雲端測試環境
4. **📚 Documentation Team**: 可以開始撰寫 GCP 部署文檔

### **更新任務看板**
在 `.cursor/shared-state/task-board.md` 中：
- [x] ✅ GCP 專案建立
- [x] ✅ API 啟用
- [x] ✅ 計費告警設置
- [x] ✅ gcloud CLI 配置
- [ ] 🔄 準備 DeepSeek 模型雲端部署

---

## 🎯 **成功！您現在擁有：**

✅ **完整的 GCP 環境** - 準備好部署 DeepSeek AI 模型  
✅ **預算控制** - 確保成本在 $300 預算內  
✅ **必要權限** - 可以建立 VM、部署 Cloud Run、管理儲存  
✅ **本地工具** - gcloud CLI 可以直接管理雲端資源  
✅ **監控機制** - 計費告警確保不會超支

**現在 Development Team 可以開始準備 DeepSeek 模型的雲端部署！** 🚀

---

*需要協助？查看任務看板或聯繫 Central Coordinator 進行團隊協調！*
