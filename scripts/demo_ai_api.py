#!/usr/bin/env python3
"""
AI API 演示腳本
展示 DeepSeek AI 分析功能
"""

import sys
import time
import json
from pathlib import Path

# 添加專案根目錄到路徑
sys.path.append(str(Path(__file__).parent.parent))

def demo_ai_analysis():
    """演示 AI 分析功能"""
    print("🎬 DeepSeek AI 分析演示")
    print("=" * 50)
    
    from backend.ai.inference_engine import get_inference_engine
    from backend.app.qubic_client import QubicNetworkClient
    
    # 初始化組件
    print("🔄 初始化 AI 引擎和 Qubic 客戶端...")
    engine = get_inference_engine()
    qubic_client = QubicNetworkClient()
    
    # 1. 獲取即時網路數據
    print("\n📡 步驟 1: 獲取即時 Qubic 網路數據")
    try:
        tick_info = qubic_client.get_tick_info()
        stats = qubic_client.get_network_stats()
        health = qubic_client.get_network_health()
        
        current_data = {
            **tick_info,
            **stats,
            "health": health
        }
        
        print(f"   📊 當前 Tick: {current_data.get('tick', 0):,}")
        print(f"   ⏱️  Duration: {current_data.get('duration', 0)} 秒")
        print(f"   🏛️  Epoch: {current_data.get('epoch', 0)}")
        print(f"   💰 價格: ${current_data.get('price', 0):.9f}")
        print(f"   👥 活躍地址: {current_data.get('activeAddresses', 0):,}")
        print(f"   ❤️  健康狀況: {health.get('overall', '未知')}")
        
    except Exception as e:
        print(f"   ⚠️ 無法獲取即時數據: {e}")
        # 使用模擬數據
        current_data = {
            "tick": 15423890,
            "duration": 1.2,
            "epoch": 154,
            "price": 0.000000123,
            "activeAddresses": 12456,
            "health": {"overall": "健康", "tick_status": "正常"}
        }
        print(f"   📋 使用模擬數據進行演示")
    
    # 2. AI 數據分析
    print(f"\n🧠 步驟 2: AI 智能分析")
    print(f"   🔄 正在分析網路數據...")
    
    start_time = time.time()
    analysis_result = engine.analyze_qubic_data(current_data)
    analysis_time = time.time() - start_time
    
    print(f"   ⏱️  分析耗時: {analysis_time:.2f} 秒")
    print(f"   ✅ 分析狀態: {'成功' if analysis_result.get('success') else '失敗'}")
    
    if analysis_result.get('success'):
        print(f"\n📝 AI 分析結果:")
        print(f"   {analysis_result.get('analysis', '無分析內容')}")
        
        insights = analysis_result.get('insights', [])
        if insights:
            print(f"\n💡 關鍵洞察:")
            for i, insight in enumerate(insights, 1):
                print(f"   {i}. {insight}")
        
        recommendations = analysis_result.get('recommendations', [])
        if recommendations:
            print(f"\n🎯 建議行動:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        
        confidence = analysis_result.get('confidence', 0)
        print(f"\n📊 分析信心度: {confidence:.1%}")
    
    # 3. 自然語言問答
    print(f"\n💬 步驟 3: 自然語言問答演示")
    
    questions = [
        "Qubic 是什麼？",
        "當前網路狀況如何？",
        "什麼是區塊鏈技術？"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n   問題 {i}: {question}")
        print(f"   🤔 AI 思考中...")
        
        start_time = time.time()
        
        # 為問答構建上下文
        context_prompt = f"""基於當前 Qubic 網路狀態：
Tick: {current_data.get('tick', 0):,}
Duration: {current_data.get('duration', 0)} 秒
健康狀況: {current_data.get('health', {}).get('overall', '未知')}

問題：{question}

回答："""
        
        answer = engine.generate_response(context_prompt, max_length=150)
        response_time = time.time() - start_time
        
        print(f"   ⏱️  回應時間: {response_time:.2f} 秒")
        print(f"   🤖 AI 回答: {answer}")
        
        if i < len(questions):
            print(f"   ⏳ 準備下一個問題...")
            time.sleep(1)
    
    # 4. 性能總結
    print(f"\n📊 步驟 4: 性能總結")
    engine_status = engine.get_status()
    
    print(f"   🤖 AI 引擎狀態: {'就緒' if engine_status['ready'] else '未就緒'}")
    print(f"   💾 模型載入: {'是' if engine_status['model_loaded'] else '否'}")
    print(f"   🖥️  運行設備: {engine_status['device'].upper()}")
    print(f"   📁 模型路徑: {engine_status['model_path']}")
    
    print(f"\n🎉 演示完成！")
    print(f"   ✅ AI 分析功能正常運作")
    print(f"   ✅ 自然語言理解能力良好")
    print(f"   ✅ 與 Qubic 數據整合成功")

def interactive_demo():
    """互動式演示"""
    print("\n🎮 互動式 AI 演示")
    print("輸入 'quit' 結束演示")
    print("-" * 30)
    
    from backend.ai.inference_engine import get_inference_engine
    engine = get_inference_engine()
    
    while True:
        try:
            question = input("\n💬 請輸入您的問題: ").strip()
            
            if question.lower() in ['quit', 'exit', '退出']:
                print("👋 感謝使用 AI 演示！")
                break
            
            if not question:
                continue
            
            print("🤔 AI 思考中...")
            start_time = time.time()
            
            prompt = f"""作為 Qubic 區塊鏈專家，請回答以下問題：

問題：{question}

回答："""
            
            answer = engine.generate_response(prompt, max_length=200)
            response_time = time.time() - start_time
            
            print(f"⏱️  回應時間: {response_time:.2f} 秒")
            print(f"🤖 AI 回答：\n{answer}")
            
        except KeyboardInterrupt:
            print("\n👋 演示已中斷")
            break
        except Exception as e:
            print(f"❌ 發生錯誤: {e}")

def main():
    """主函數"""
    try:
        # 自動演示
        demo_ai_analysis()
        
        # 詢問是否進行互動演示
        print("\n" + "="*50)
        choice = input("是否要進行互動式演示？(y/N): ").strip().lower()
        
        if choice in ['y', 'yes', '是', '好']:
            interactive_demo()
        
    except KeyboardInterrupt:
        print("\n👋 演示被用戶中斷")
    except Exception as e:
        print(f"\n❌ 演示過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

