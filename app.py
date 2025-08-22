#!/usr/bin/env python3
"""
QDashboard 主應用程式入口
"""

from backend.app import create_app

# 建立 Flask 應用程式
app = create_app()

@app.route('/')
def index():
    """首頁路由 - 提供前端頁面"""
    from flask import send_file
    import os
    frontend_path = os.path.join(os.path.dirname(__file__), 'frontend', 'index.html')
    return send_file(frontend_path)

@app.route('/<path:filename>')
def static_files(filename):
    """靜態文件路由"""
    from flask import send_file
    import os
    frontend_path = os.path.join(os.path.dirname(__file__), 'frontend', filename)
    if os.path.exists(frontend_path):
        return send_file(frontend_path)
    else:
        return "File not found", 404

@app.route('/old-index')
def old_index():
    """舊的測試首頁"""
    return '''
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>QDashboard - Qubic 網路監控</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
            .status { padding: 20px; margin: 20px; border-radius: 10px; }
            .online { background-color: #d4edda; color: #155724; }
            .offline { background-color: #f8d7da; color: #721c24; }
        </style>
    </head>
    <body>
        <h1>🚀 QDashboard</h1>
        <p>Qubic 網路即時監控 Dashboard</p>
        
        <div class="status online">
            <h2>✅ API 狀態: 運行中</h2>
            <p>Flask 應用程式已成功啟動</p>
        </div>
        
        <h3>📡 可用 API 端點:</h3>
        <ul style="text-align: left; max-width: 400px; margin: 0 auto;">
            <li><a href="/api/tick" target="_blank">GET /api/tick</a> - 獲取 tick 資訊</li>
            <li><a href="/api/status" target="_blank">GET /api/status</a> - API 狀態檢查</li>
        </ul>
        
        <p style="margin-top: 30px;">
            <small>QDashboard v0.1.0 | 2025年8月20日</small>
        </p>
    </body>
    </html>
    '''

if __name__ == '__main__':
    from app_config import config
    
    print("🚀 啟動 QDashboard...")
    config.print_config()
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
