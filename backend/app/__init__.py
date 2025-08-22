"""
QDashboard Flask 應用程式
"""

from flask import Flask
from flask_cors import CORS

def create_app():
    """建立 Flask 應用程式"""
    app = Flask(__name__)
    
    # 啟用 CORS 以支援前端請求
    CORS(app)
    
    # 設置配置
    app.config['JSON_AS_ASCII'] = False  # 支援中文字符
    
    # 註冊藍圖
    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app
