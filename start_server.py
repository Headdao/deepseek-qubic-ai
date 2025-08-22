#!/usr/bin/env python3
"""
QDashboard 伺服器啟動腳本
"""

import os
import sys

# 確保在正確的目錄
os.chdir('/Users/apple/qubic/qdashboard')

# 匯入應用程式
from app import app

def main():
    """啟動 QDashboard 伺服器"""
    print("🚀 正在啟動 QDashboard...")
    print("📍 工作目錄:", os.getcwd())
    print("🐍 Python 版本:", sys.version)
    
    try:
        print("📡 API 端點: http://localhost:8000/api/tick")
        print("🌐 Web 介面: http://localhost:8000/")
        print("🔍 狀態檢查: http://localhost:8000/api/status")
        print("\n" + "="*50)
        print("伺服器正在啟動...")
        print("按 Ctrl+C 停止伺服器")
        print("="*50 + "\n")
        
        # 啟動伺服器
        app.run(
            debug=True,
            host='0.0.0.0',
            port=8000,
            use_reloader=False  # 避免重載問題
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 伺服器已停止")
    except Exception as e:
        print(f"\n❌ 啟動失敗: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
