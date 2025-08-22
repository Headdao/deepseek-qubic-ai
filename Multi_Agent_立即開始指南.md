# 🚀 Multi-Agent 立即開始指南
## 解決 Cursor 資料夾開啟問題

### ❗ **當前問題**
- Cursor 可以開啟窗口，但無法自動開啟專案資料夾

### ✅ **立即解決方案 (5分鐘完成)**

---

## 🎯 **Step 1: 開啟 6 個 Cursor 窗口**

1. **打開 Cursor 應用程式**
2. **按 6 次** `Cmd + Shift + N` (開新窗口)
   - 或從選單: `File` → `New Window` (重複 6 次)

---

## 📁 **Step 2: 在每個窗口開啟專案 (關鍵步驟)**

### **方法 A: 使用快捷鍵 (最快)**
在每個新窗口中：
1. 按 `Cmd + O`
2. 按 `Cmd + Shift + G` (前往資料夾)
3. 輸入: `/Users/apple/qubic/qdashboard`
4. 按 `Enter`

### **方法 B: 使用選單**
在每個新窗口中：
1. `File` → `Open Folder...`
2. 瀏覽到: `/Users/apple/qubic/qdashboard`
3. 點擊 `Open`

### **方法 C: 拖拽 (如果可見)**
- 從 Finder 拖拽 `qdashboard` 資料夾到 Cursor 窗口

---

## 🤖 **Step 3: 設置 AI Agents (複製貼上即可)**

在每個已開啟專案的窗口中，按 `Cmd + K` 並使用對應的 Prompt：

### **窗口 1: 🎯 Central Coordinator**
```
你是 Qubic AI Compute Layer 項目的中央協調者。

職責: 總體協調、衝突解決、全局決策、監控 .cursor/shared-state/ 狀態檔案

當前階段: Phase 1, Week 1-2 (環境設置與模型部署)

請開始協調團隊工作，確保所有 6 個智能體高效協作。
```

### **窗口 2: 📊 Project Manager**
```
你是專案經理，負責進度追蹤和里程碑管理。

重點檔案: Qubic_AI_Compute_Layer_詳細任務清單.md

當前任務: 追蹤 Week 1-2 進度 (環境設置與模型部署)

請更新 .cursor/shared-state/task-board.md 中的任務狀態。
```

### **窗口 3: 💻 Development Team**
```
你是開發團隊領導，負責程式碼開發和技術實現。

當前任務:
- GCP 帳號設置與配置
- Python 3.9+ 和 venv 環境
- DeepSeek 模型下載準備

重點: Flask 後端、React 前端、QubiPy 整合
```

### **窗口 4: 🧪 Testing Team**
```
你是測試團隊負責人，負責品質保證。

當前任務:
- 測試環境規劃
- 測試框架選型 (pytest, jest)
- 設定測試覆蓋率目標 >85%

專注於建立完整的測試策略。
```

### **窗口 5: 📚 Documentation Team**
```
你是文檔團隊負責人，負責技術文檔撰寫。

語言: 繁體中文優先，技術術語保持英文

當前任務:
- 技術文檔模板建立
- 確保文檔與開發同步
- 維護 docs/ 和所有 .md 檔案
```

### **窗口 6: 🔧 DevOps Team**
```
你是 DevOps 團隊負責人，負責基礎設施管理。

當前任務:
- GCP 基礎設施規劃
- Docker 環境配置
- CI/CD 管道設計

重點: 穩定部署、高可用性、安全性
```

---

## ✅ **Step 4: 驗證設置成功**

### **檢查項目**
- [ ] 6 個 Cursor 窗口都顯示 `qdashboard` 專案
- [ ] 左側檔案總管顯示完整專案結構
- [ ] 每個窗口的 AI 都設置為對應角色
- [ ] 可以看到 `.cursor/` 資料夾

### **如果成功**，您會看到：
```
qdashboard/
├── .cursor/
│   ├── multi-agent-config/
│   ├── shared-state/
│   └── sync-protocols/
├── backend/
├── frontend/
├── scripts/
├── Multi_Agent_使用指南.md
└── ...
```

---

## 🚀 **Step 5: 開始協作**

### **立即可以做的事**
1. **Central Coordinator** 檢查 `.cursor/shared-state/task-board.md`
2. **Project Manager** 更新任務進度
3. **Development Team** 開始 GCP 設置
4. **Testing Team** 規劃測試框架
5. **Documentation Team** 檢查文檔結構
6. **DevOps Team** 準備基礎設施

### **共享檔案位置**
- 📋 任務看板: `.cursor/shared-state/task-board.md`
- 📊 項目狀態: `.cursor/shared-state/project-state.json`
- 📝 詳細任務: `Qubic_AI_Compute_Layer_詳細任務清單.md`

---

## 🆘 **故障排解**

### **如果還是無法開啟專案資料夾**
1. 確認路徑正確: `/Users/apple/qubic/qdashboard`
2. 在 Terminal 中執行: `open /Users/apple/qubic/qdashboard` 確認資料夾存在
3. 嘗試重新啟動 Cursor
4. 使用 Finder 手動瀏覽到資料夾後拖拽到 Cursor

### **如果 AI 設置有問題**
- 確保點擊了右下角的 AI 按鈕或按 `Cmd + K`
- 重新複製貼上 Prompt Template
- 檢查 AI 是否回應確認了角色設定

---

## 🎉 **完成！**

現在您就有了 6 個專門的 AI Agent 在協作開發 Qubic AI Compute Layer！

**每個 Agent 都會專注於自己的專業領域，通過共享狀態檔案保持同步，這就是未來的協作開發模式！** 🚀

---

*有問題？查看 `Multi_Agent_使用指南.md` 獲得更詳細的說明！*
