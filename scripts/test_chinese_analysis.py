#!/usr/bin/env python3
"""
測試中文 AI 分析回應
"""
import requests
import json
import logging

# 設置詳細的日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_chinese_analysis():
    """測試中文 AI 分析功能"""
    
    url = "http://localhost:8000/api/ai/analyze"
    
    # 測試數據
    test_data = {
        "tick": 31525500,
        "duration": 1,
        "epoch": 175,
        "health": {"overall": "健康"},
        "price": 0.000012345,
        "activeAddresses": 1234,
        "language": "zh-tw"
    }
    
    print("🧪 測試中文 AI 分析回應")
    print("=" * 50)
    
    try:
        print(f"📤 發送請求到: {url}")
        print(f"📊 測試數據: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"📨 回應狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API 呼叫成功")
            print(f"📋 回應內容: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 檢查回應內容
            analysis = result.get('analysis', '')
            if analysis and analysis.strip():
                print("✅ 成功獲得分析內容")
                print(f"📝 分析長度: {len(analysis)} 字符")
                print(f"📄 分析內容前100字符: {analysis[:100]}")
            else:
                print("❌ 分析內容為空")
                
        else:
            print(f"❌ API 呼叫失敗")
            print(f"錯誤內容: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 請求異常: {e}")
    except Exception as e:
        print(f"❌ 其他錯誤: {e}")

def test_chinese_qa():
    """測試中文 QA 功能"""
    
    url = "http://localhost:8000/api/ai/query"
    
    test_questions = [
        "分析當前網路狀況",
        "評估網路健康",
        "預測 Epoch 進度"
    ]
    
    print("\n🔍 測試中文 QA 回應")
    print("=" * 50)
    
    for question in test_questions:
        print(f"\n❓ 測試問題: {question}")
        
        try:
            data = {
                "question": question,
                "language": "zh-tw"
            }
            
            response = requests.post(url, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('answer', '')
                
                if answer and answer.strip():
                    print(f"✅ 成功獲得回答")
                    print(f"📝 回答長度: {len(answer)} 字符")
                    print(f"📄 回答內容: {answer}")
                else:
                    print("❌ 回答內容為空")
                    print(f"📋 完整回應: {json.dumps(result, indent=2, ensure_ascii=False)}")
            else:
                print(f"❌ API 呼叫失敗: {response.status_code}")
                print(f"錯誤內容: {response.text}")
                
        except Exception as e:
            print(f"❌ 錯誤: {e}")

if __name__ == "__main__":
    test_chinese_analysis()
    test_chinese_qa()


