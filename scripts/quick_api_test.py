#!/usr/bin/env python3
"""
快速 API 測試 - 檢查基本連線和回應
"""
import requests
import json
import signal
import sys

def timeout_handler(signum, frame):
    print("\n⏰ 請求超時，終止測試")
    sys.exit(1)

def test_api_basic():
    """測試基本 API 連線"""
    
    print("🔍 快速 API 連線測試")
    print("=" * 40)
    
    # 設置30秒超時
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)
    
    try:
        # 測試健康檢查
        print("🏥 測試健康檢查...")
        health_response = requests.get("http://localhost:8000/api/tick", timeout=5)
        print(f"✅ 健康檢查狀態: {health_response.status_code}")
        
        # 測試簡單的分析請求
        print("🧪 測試分析 API...")
        test_data = {
            "tick": 31525500,
            "duration": 1,
            "epoch": 175,
            "health": {"overall": "健康"},
            "language": "zh-tw"
        }
        
        print("📤 發送分析請求...")
        analysis_response = requests.post(
            "http://localhost:8000/api/ai/analyze", 
            json=test_data, 
            timeout=15
        )
        
        print(f"📨 分析回應狀態: {analysis_response.status_code}")
        
        if analysis_response.status_code == 200:
            result = analysis_response.json()
            analysis = result.get('analysis', '')
            print(f"📝 分析內容: {analysis[:100]}...")
            
            if analysis == "生成的回應為空，請重試。":
                print("❌ 確認問題：回應為空")
            else:
                print("✅ 獲得有效回應")
        else:
            print(f"❌ API 錯誤: {analysis_response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ 請求超時 - AI 推理可能卡住")
    except requests.exceptions.ConnectionError:
        print("🔌 連線錯誤 - 後端可能未啟動")
    except Exception as e:
        print(f"❌ 其他錯誤: {e}")
    finally:
        signal.alarm(0)  # 取消超時

if __name__ == "__main__":
    test_api_basic()


