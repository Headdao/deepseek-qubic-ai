#!/usr/bin/env python3
"""
QDashboard 應用配置 - 集中式端口管理
解決端口不一致的問題
"""

class AppConfig:
    """應用配置類 - 統一管理所有端口和設定"""
    
    # 🔧 端口配置 - 唯一真實來源
    PORT = 3000
    HOST = '127.0.0.1'
    
    # 🌐 環境配置
    DEBUG = False
    ENVIRONMENT = 'development'
    
    # 📊 API 配置
    API_PREFIX = '/api'
    
    # ⏱️ 更新間隔 (秒)
    UPDATE_INTERVALS = {
        'tick': 5,
        'stats': 30,
        'health': 10
    }
    
    @classmethod
    def get_server_url(cls):
        """獲取完整的伺服器 URL"""
        return f"http://{cls.HOST}:{cls.PORT}"
    
    @classmethod
    def get_api_base_url(cls):
        """獲取 API 基礎 URL"""
        return f"{cls.get_server_url()}{cls.API_PREFIX}"
    
    @classmethod
    def print_config(cls):
        """打印當前配置"""
        print("🚀 QDashboard 配置:")
        print(f"   📡 伺服器: {cls.get_server_url()}")
        print(f"   🔌 API: {cls.get_api_base_url()}")
        print(f"   🌐 前端: {cls.get_server_url()}/qdashboard/")
        print(f"   🏠 主機: {cls.HOST}")
        print(f"   🔢 端口: {cls.PORT}")
        print(f"   🐛 調試: {cls.DEBUG}")

# 導出配置實例
config = AppConfig()


