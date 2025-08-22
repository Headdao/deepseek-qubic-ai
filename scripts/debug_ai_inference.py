#!/usr/bin/env python3
"""
調試 AI 推理問題
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.ai.inference_engine import DeepSeekInferenceEngine
import logging

# 設置詳細日誌
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_direct_inference():
    """直接測試推理引擎"""
    
    print("🔍 直接測試 AI 推理引擎")
    print("=" * 60)
    
    try:
        # 初始化推理引擎
        print("📊 初始化推理引擎...")
        engine = DeepSeekInferenceEngine()
        
        # 測試簡單的中文生成
        print("🧪 測試基本中文生成...")
        simple_prompt = "請用繁體中文回答：什麼是區塊鏈？"
        
        print(f"📝 提示詞: {simple_prompt}")
        
        # 使用基本生成方法，不啟用 Qubic 增強
        response = engine.generate_response(
            simple_prompt, 
            max_length=100,
            enhance_with_qubic=False,
            language="zh-tw"
        )
        
        print(f"✅ 基本生成結果: {response}")
        print(f"📏 回應長度: {len(response)} 字符")
        
        # 測試 Qubic 增強生成
        print("\n🔬 測試 Qubic 增強生成...")
        qubic_prompt = "分析當前網路狀況"
        
        response_enhanced = engine.generate_response(
            qubic_prompt,
            max_length=150,
            enhance_with_qubic=True,
            language="zh-tw"
        )
        
        print(f"✅ 增強生成結果: {response_enhanced}")
        print(f"📏 回應長度: {len(response_enhanced)} 字符")
        
        # 測試分析功能
        print("\n🧮 測試分析功能...")
        test_data = {
            "tick": 31525500,
            "duration": 1,
            "epoch": 175,
            "health": {"overall": "健康"},
            "price": 0.000012345,
            "activeAddresses": 1234
        }
        
        analysis_result = engine.analyze_qubic_data(test_data, language="zh-tw")
        
        print(f"✅ 分析結果: {analysis_result}")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_inference()

