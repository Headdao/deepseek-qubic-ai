#!/usr/bin/env python3
"""
最終 Qubic AI 增強測試
驗證知識增強和優化效果
"""

import sys
import time
from pathlib import Path

# 添加專案根目錄到路徑
sys.path.append(str(Path(__file__).parent.parent))

def final_qubic_test():
    """最終測試"""
    print("🎯 最終 Qubic AI 增強測試")
    print("=" * 50)
    
    from backend.ai.inference_engine import get_inference_engine
    from backend.ai.qubic_knowledge import get_qubic_knowledge_base
    
    # 初始化組件
    engine = get_inference_engine()
    qubic_kb = get_qubic_knowledge_base()
    
    # 測試問題 - 現在應該有準確的 Qubic 知識
    test_scenarios = [
        {
            "question": "Qubic 是什麼？",
            "expected_keywords": ["qubic", "qbc", "去中心化", "計算", "upow"],
            "category": "基礎定義"
        },
        {
            "question": "什麼是有用工作量證明 UPoW？",
            "expected_keywords": ["upow", "共識", "安全性", "實用性", "量子"],
            "category": "技術概念"
        },
        {
            "question": "QBC 系統如何運作？",
            "expected_keywords": ["qbc", "法定人數", "computors", "分散式"],
            "category": "系統架構"
        },
        {
            "question": "Qubic Units (QUs) 有什麼用途？",
            "expected_keywords": ["qus", "代幣", "交易", "智能合約"],
            "category": "代幣經濟"
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*20} 測試 {i}/{len(test_scenarios)} {'='*20}")
        print(f"📂 類別: {scenario['category']}")
        print(f"❓ 問題: {scenario['question']}")
        
        # 執行 AI 回應
        start_time = time.time()
        response = engine.generate_response(
            scenario['question'], 
            enhance_with_qubic=True,
            max_length=150
        )
        response_time = time.time() - start_time
        
        print(f"⏱️  回應時間: {response_time:.2f}秒")
        print(f"📝 AI 回應:\n{response}")
        
        # 評估回應品質
        quality = qubic_kb.validate_response(response)
        
        # 檢查關鍵詞
        response_lower = response.lower()
        found_keywords = [kw for kw in scenario['expected_keywords'] 
                         if kw.lower() in response_lower]
        keyword_score = len(found_keywords) / len(scenario['expected_keywords']) * 100
        
        print(f"\n📊 評估結果:")
        print(f"   品質評級: {quality['quality']}")
        print(f"   準確性分數: {quality['accuracy_score']}")
        print(f"   關鍵詞覆蓋: {keyword_score:.1f}% ({len(found_keywords)}/{len(scenario['expected_keywords'])})")
        print(f"   找到的關鍵詞: {found_keywords}")
        
        # 整體評估
        overall_score = (quality['accuracy_score'] + keyword_score) / 2
        if overall_score >= 70:
            grade = "優秀 ✅"
        elif overall_score >= 50:
            grade = "良好 👍"
        elif overall_score >= 30:
            grade = "一般 ⚠️"
        else:
            grade = "需要改進 ❌"
        
        print(f"   整體評級: {grade} ({overall_score:.1f}分)")
        
        results.append({
            "category": scenario['category'],
            "question": scenario['question'],
            "response_time": response_time,
            "quality_score": quality['accuracy_score'],
            "keyword_score": keyword_score,
            "overall_score": overall_score,
            "grade": grade
        })
    
    # 總結報告
    print(f"\n" + "="*50)
    print("📊 最終測試報告")
    print("="*50)
    
    avg_time = sum(r['response_time'] for r in results) / len(results)
    avg_quality = sum(r['quality_score'] for r in results) / len(results)
    avg_keyword = sum(r['keyword_score'] for r in results) / len(results)
    avg_overall = sum(r['overall_score'] for r in results) / len(results)
    
    print(f"📈 平均性能:")
    print(f"   回應時間: {avg_time:.2f}秒")
    print(f"   品質分數: {avg_quality:.1f}")
    print(f"   關鍵詞覆蓋: {avg_keyword:.1f}%")
    print(f"   整體分數: {avg_overall:.1f}")
    
    # 各項目詳細結果
    print(f"\n📋 詳細結果:")
    for result in results:
        print(f"   {result['category']}: {result['grade']}")
    
    # 改進程度評估
    improvement_level = ""
    if avg_overall >= 70:
        improvement_level = "🎉 重大改進！Qubic 知識增強非常成功"
    elif avg_overall >= 50:
        improvement_level = "✅ 顯著改進！知識增強效果良好"
    elif avg_overall >= 30:
        improvement_level = "👍 適度改進，仍有提升空間"
    else:
        improvement_level = "⚠️ 改進有限，需要進一步優化"
    
    print(f"\n🎯 改進評估: {improvement_level}")
    
    # 建議
    print(f"\n💡 建議:")
    if avg_time > 5:
        print(f"   ⏱️  考慮進一步優化推理速度")
    if avg_quality < 60:
        print(f"   📚 擴展 Qubic 知識庫內容")
    if avg_keyword < 70:
        print(f"   🔍 改進關鍵詞匹配邏輯")
    
    print(f"\n✅ 系統狀態: {'就緒投產' if avg_overall >= 60 else '需要改進'}")
    
    return avg_overall >= 50

if __name__ == "__main__":
    try:
        success = final_qubic_test()
        print(f"\n{'🎉 測試通過！' if success else '⚠️ 需要改進'}")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


