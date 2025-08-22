# QDashboard 安裝指南

## 🔧 系統需求

- Python 3.10+
- QubiPy 函式庫 (已下載到本機)

## 📦 安裝步驟

### 1. 建立虛擬環境
```bash
cd /Users/apple/qubic/qdashboard
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
```

### 2. 安裝基本依賴
```bash
pip install -r requirements.txt
```

### 3. 安裝 QubiPy
```bash
pip install -e /Users/apple/qubic/QubiPy-main
```

### 4. 驗證安裝
```bash
python -c "from qubipy.rpc import rpc_client; print('✅ QubiPy 安裝成功')"
```

### 5. 啟動應用程式
```bash
python app.py
```

## 🌐 訪問應用程式

- **Web 介面**: http://localhost:8000/
- **API 端點**: http://localhost:8000/api/tick
- **狀態檢查**: http://localhost:8000/api/status

## 🔍 故障排除

### QubiPy 匯入錯誤
如果遇到 `無法解析匯入 "qubipy.rpc"` 錯誤：

1. 確認 QubiPy 已正確安裝：
   ```bash
   pip list | grep -i qubipy
   ```

2. 重新安裝 QubiPy：
   ```bash
   pip uninstall QubiPy
   pip install -e /Users/apple/qubic/QubiPy-main
   ```

3. 檢查 Python 路徑：
   ```bash
   python -c "import sys; print(sys.path)"
   ```

### 端口衝突
如果端口 8000 被佔用：

1. 檢查佔用進程：
   ```bash
   lsof -i :8000
   ```

2. 停止佔用進程：
   ```bash
   pkill -f "python.*app.py"
   ```

3. 或使用其他端口：
   ```bash
   # 修改 app.py 中的端口號
   app.run(debug=True, host='0.0.0.0', port=8001)
   ```

## 📋 依賴列表

- **Flask**: Web 框架
- **Flask-CORS**: 跨域支援
- **QubiPy**: Qubic RPC 客戶端
- **Requests**: HTTP 請求庫
- **Gunicorn**: 生產伺服器

## 🚀 生產部署

使用 Gunicorn 啟動生產伺服器：
```bash
gunicorn --bind 0.0.0.0:8000 --workers 2 app:app
```

## 🐳 Docker 部署

```bash
docker build -t qdashboard .
docker run -p 8000:8000 qdashboard
```

---

如有問題，請參考 [README.md](README.md) 或建立 Issue。
