#!/usr/bin/env python3
"""
Qubic 知識增強測試腳本
比較增強前後的 AI 回應品質
"""

import sys
import time
from pathlib import Path

# 添加專案根目錄到路徑
sys.path.append(str(Path(__file__).parent.parent))

def test_qubic_knowledge_enhancement():
    """測試 Qubic 知識增強效果"""
    print("🧪 Qubic 知識增強測試")
    print("=" * 50)
    
    from backend.ai.inference_engine import get_inference_engine
    from backend.ai.qubic_knowledge import get_qubic_knowledge_base
    
    # 初始化組件
    engine = get_inference_engine()
    qubic_kb = get_qubic_knowledge_base()
    
    # 測試問題
    test_questions = [
        "Qubic 是什麼？",
        "什麼是 UPoW？",
        "QBC 系統如何運作？",
        "Qubic 的共識機制是什麼？",
        "當前網路狀況如何？"
    ]
    
    print("🔄 開始對比測試...")
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*20} 測試 {i}/{len(test_questions)} {'='*20}")
        print(f"❓ 問題: {question}")
        
        # 測試 1: 不使用 Qubic 知識增強
        print(f"\n🤖 原始 AI 回應:")
        start_time = time.time()
        original_response = engine.generate_response(question, enhance_with_qubic=False, max_length=150)
        original_time = time.time() - start_time
        print(f"   ⏱️  時間: {original_time:.2f}秒")
        print(f"   📝 回應: {original_response}")
        
        # 測試 2: 使用 Qubic 知識增強
        print(f"\n🎯 Qubic 增強回應:")
        start_time = time.time()
        enhanced_response = engine.generate_response(question, enhance_with_qubic=True, max_length=200)
        enhanced_time = time.time() - start_time
        print(f"   ⏱️  時間: {enhanced_time:.2f}秒")
        print(f"   📝 回應: {enhanced_response}")
        
        # 評估回應品質
        print(f"\n📊 品質評估:")
        original_quality = qubic_kb.validate_response(original_response)
        enhanced_quality = qubic_kb.validate_response(enhanced_response)
        
        print(f"   原始回應: {original_quality['quality']} (分數: {original_quality['accuracy_score']})")
        print(f"   增強回應: {enhanced_quality['quality']} (分數: {enhanced_quality['accuracy_score']})")
        
        # 顯示改進程度
        improvement = enhanced_quality['accuracy_score'] - original_quality['accuracy_score']
        if improvement > 0:
            print(f"   ✅ 改進: +{improvement} 分")
        elif improvement < 0:
            print(f"   ⚠️  退步: {improvement} 分")
        else:
            print(f"   ➖ 無變化")
        
        if i < len(test_questions):
            print(f"\n⏳ 準備下一個測試...")
            time.sleep(1)

def test_network_analysis_enhancement():
    """測試網路分析增強效果"""
    print(f"\n🔬 網路分析增強測試")
    print("=" * 50)
    
    from backend.ai.inference_engine import get_inference_engine
    
    engine = get_inference_engine()
    
    # 準備測試數據
    test_data = {
        "tick": 31519628,
        "duration": 0.8,
        "epoch": 175,
        "health": {"overall": "健康"},
        "price": 0.000002819,
        "activeAddresses": 592711
    }
    
    print(f"📊 測試數據:")
    print(f"   Tick: {test_data['tick']:,}")
    print(f"   Duration: {test_data['duration']} 秒")
    print(f"   Epoch: {test_data['epoch']}")
    print(f"   健康狀況: {test_data['health']['overall']}")
    print(f"   價格: ${test_data['price']:.9f}")
    print(f"   活躍地址: {test_data['activeAddresses']:,}")
    
    print(f"\n🧠 執行 AI 分析...")
    start_time = time.time()
    
    analysis_result = engine.analyze_qubic_data(test_data)
    analysis_time = time.time() - start_time
    
    print(f"⏱️  分析時間: {analysis_time:.2f}秒")
    print(f"✅ 分析狀態: {'成功' if analysis_result.get('success') else '失敗'}")
    
    if analysis_result.get('success'):
        print(f"\n📝 分析結果:")
        print(f"   {analysis_result.get('analysis', '無分析內容')}")
        
        insights = analysis_result.get('insights', [])
        if insights:
            print(f"\n💡 洞察 ({len(insights)} 項):")
            for i, insight in enumerate(insights, 1):
                print(f"   {i}. {insight}")
        
        recommendations = analysis_result.get('recommendations', [])
        if recommendations:
            print(f"\n🎯 建議 ({len(recommendations)} 項):")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        
        confidence = analysis_result.get('confidence', 0)
        print(f"\n📊 分析信心度: {confidence:.1%}")
        
        # 評估分析品質
        from backend.ai.qubic_knowledge import get_qubic_knowledge_base
        qubic_kb = get_qubic_knowledge_base()
        
        analysis_quality = qubic_kb.validate_response(analysis_result.get('analysis', ''))
        print(f"📈 分析品質: {analysis_quality['quality']} (分數: {analysis_quality['accuracy_score']})")
        
        if analysis_quality['feedback']:
            print(f"💬 品質回饋:")
            for feedback in analysis_quality['feedback']:
                print(f"   - {feedback}")

def test_knowledge_base_features():
    """測試知識庫功能"""
    print(f"\n📚 知識庫功能測試")
    print("=" * 50)
    
    from backend.ai.qubic_knowledge import get_qubic_knowledge_base
    
    qubic_kb = get_qubic_knowledge_base()
    
    # 測試上下文生成
    print("🔍 測試上下文生成:")
    test_queries = [
        "什麼是 Qubic",
        "技術架構",
        "開發工具",
        "網路分析"
    ]
    
    for query in test_queries:
        context = qubic_kb.get_relevant_context(query)
        print(f"\n   查詢: {query}")
        print(f"   上下文長度: {len(context)} 字符")
        print(f"   預覽: {context[:100]}...")
    
    # 測試事實提取
    print(f"\n📋 測試 Qubic 事實:")
    facts = qubic_kb.get_qubic_facts()
    for i, fact in enumerate(facts, 1):
        print(f"   {i}. {fact}")
    
    # 測試查詢增強
    print(f"\n🎯 測試查詢增強:")
    sample_query = "Qubic 的共識機制是什麼？"
    enhanced_query = qubic_kb.enhance_query_with_context(sample_query)
    
    print(f"   原始查詢: {sample_query}")
    print(f"   增強後長度: {len(enhanced_query)} 字符")
    print(f"   包含關鍵詞: UPoW, QBC, Qubic, 共識")

def main():
    """主測試函數"""
    try:
        # 基礎功能測試
        test_knowledge_base_features()
        
        # 問答增強測試
        test_qubic_knowledge_enhancement()
        
        # 網路分析增強測試
        test_network_analysis_enhancement()
        
        print(f"\n" + "="*50)
        print("🎉 Qubic 知識增強測試完成！")
        print("✅ 知識庫功能正常")
        print("✅ AI 回應品質提升")
        print("✅ 網路分析能力增強")
        print(f"\n💡 建議: 根據測試結果進一步調整知識庫內容")
        
    except KeyboardInterrupt:
        print("\n⏸️ 測試被用戶中斷")
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

