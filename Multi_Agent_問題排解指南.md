# 🛠️ Multi-Agent 問題排解指南
## Cursor 窗口開啟問題解決方案

### 🔍 **問題描述**
- ✅ Cursor 可以開啟新窗口
- ❌ 但無法自動開啟到指定的專案資料夾

---

## 🎯 **解決方案 1: 手動開啟專案 (推薦，最可靠)**

### **步驟 1: 開啟 6 個 Cursor 窗口**
1. 打開 **Cursor 應用程式**
2. 使用快捷鍵 `Cmd + Shift + N` 開啟新窗口 (重複 6 次)
3. 或從選單: `File` → `New Window` (重複 6 次)

### **步驟 2: 在每個窗口開啟專案**
在每個新窗口中：
1. 按 `Cmd + O` (Open Folder)
2. 瀏覽到: `/Users/apple/qubic/qdashboard`
3. 點擊 **"Open"** 或 **"開啟"**

### **步驟 3: 驗證專案已開啟**
確認每個窗口的左側檔案總管顯示專案結構：
```
qdashboard/
├── .cursor/
├── backend/
├── frontend/
├── scripts/
├── Multi_Agent_使用指南.md
└── ...
```

---

## 🎯 **解決方案 2: 使用改進的命令列腳本**

我發現 Cursor CLI 工具確實存在，讓我創建一個改進版的腳本：