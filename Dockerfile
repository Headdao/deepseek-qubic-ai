# QDashboard_Lite Backend for Cloud Run
FROM python:3.11-slim

# 設置工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 從 Git 安裝 QubiPy
RUN pip install git+https://github.com/qubic/QubiPy.git

# 複製應用程式代碼
COPY backend /app/backend
COPY app.py .

# 設置環境變數
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PORT=8080
ENV PYTHONPATH="/app:$PYTHONPATH"

# 暴露端口
EXPOSE 8080

# 啟動應用
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app