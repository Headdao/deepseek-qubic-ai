#!/usr/bin/env python3
"""
CPU 環境下的模型優化腳本
專注於 CPU 推理優化而非量化
"""

import os
import sys
import time
import torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def optimize_for_cpu():
    """為 CPU 推理優化模型配置"""
    print("🔧 CPU 推理優化")
    print("=" * 40)
    
    model_path = "backend/ai/models/deepseek"
    
    try:
        print("📥 載入模型進行 CPU 優化...")
        
        # 載入 tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        # 載入模型並優化
        start_time = time.time()
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float32,  # 使用 float32 提高 CPU 相容性
            device_map="cpu",
            low_cpu_mem_usage=True,
            trust_remote_code=True
        )
        
        # 優化模型配置
        model.eval()
        
        # 嘗試 JIT 編譯（如果支援）
        try:
            print("⚡ 嘗試 JIT 編譯優化...")
            # 創建示例輸入
            example_input = tokenizer("測試", return_tensors="pt")
            
            # 使用 torch.jit.trace 不適用於生成模型，改用其他優化
            model = torch.jit.optimize_for_inference(model)  # type: ignore
            print("   ✅ JIT 優化成功")
        except Exception as e:
            print(f"   ⚠️  JIT 優化失敗: {e}")
        
        load_time = time.time() - start_time
        print(f"✅ 模型載入和優化完成，耗時: {load_time:.2f}秒")
        
        return model, tokenizer
        
    except Exception as e:
        print(f"❌ CPU 優化失敗: {e}")
        return None, None

def benchmark_inference_speed(model, tokenizer):
    """基準測試推理速度"""
    print(f"\n📊 推理速度基準測試")
    print("-" * 30)
    
    test_prompts = [
        "Qubic 是什麼？",
        "解釋 UPoW 共識機制",
        "當前 Qubic 網路狀況如何？"
    ]
    
    total_time = 0
    successful_tests = 0
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n測試 {i}/3: {prompt}")
        
        try:
            # 預熱（第一次推理通常較慢）
            if i == 1:
                print("   🔥 預熱推理...")
                inputs = tokenizer("預熱", return_tensors="pt")
                with torch.no_grad():
                    _ = model.generate(**inputs, max_new_tokens=10)
            
            # 正式測試
            start_time = time.time()
            inputs = tokenizer(prompt, return_tensors="pt")
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=50,
                    temperature=0.6,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            inference_time = time.time() - start_time
            
            print(f"   ⏱️  推理時間: {inference_time:.2f}秒")
            print(f"   📝 回應長度: {len(response)} 字符")
            
            total_time += inference_time
            successful_tests += 1
            
        except Exception as e:
            print(f"   ❌ 測試 {i} 失敗: {e}")
    
    if successful_tests > 0:
        avg_time = total_time / successful_tests
        print(f"\n📈 性能總結:")
        print(f"   平均推理時間: {avg_time:.2f}秒")
        print(f"   成功測試: {successful_tests}/{len(test_prompts)}")
        
        # 性能評級
        if avg_time < 3:
            grade = "優秀"
        elif avg_time < 6:
            grade = "良好"
        elif avg_time < 10:
            grade = "一般"
        else:
            grade = "需要改進"
        
        print(f"   性能評級: {grade}")
        
        return avg_time
    else:
        print(f"   ❌ 所有測試都失敗了")
        return None

def create_optimized_config():
    """創建優化配置"""
    print(f"\n⚙️  創建 CPU 優化配置...")
    
    config = {
        "optimization_type": "CPU_optimized",
        "device": "cpu",
        "torch_dtype": "float32",
        "optimizations": [
            "low_cpu_mem_usage",
            "eval_mode",
            "inference_optimization"
        ],
        "recommended_settings": {
            "max_new_tokens": 200,
            "temperature": 0.6,
            "top_p": 0.8,
            "top_k": 40,
            "repetition_penalty": 1.2
        },
        "performance_tips": [
            "使用較小的 batch_size",
            "限制 max_new_tokens 以控制推理時間",
            "使用較低的 temperature 提高一致性",
            "啟用 torch.no_grad() 進行推理"
        ]
    }
    
    config_path = Path("backend/ai/cpu_optimization_config.json")
    import json
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ 配置已保存: {config_path}")
    return config_path

def update_inference_engine():
    """更新推理引擎以使用 CPU 優化"""
    print(f"\n🔄 更新推理引擎配置...")
    
    optimization_notes = '''
# CPU 優化建議

## 已實施的優化：
1. 使用 float32 而非 float16（CPU 友善）
2. 啟用 low_cpu_mem_usage
3. 設置較保守的生成參數
4. 添加 Qubic 知識庫增強

## 性能提升技巧：
- 使用 max_new_tokens 而非 max_length
- 降低 temperature 提高一致性
- 使用 torch.no_grad() 進行推理
- 預熱模型（首次推理較慢）

## 監控指標：
- 推理時間：目標 < 10 秒
- 記憶體使用：監控 RAM 消耗
- 回應品質：使用 Qubic 知識驗證
'''
    
    notes_path = Path("backend/ai/CPU_OPTIMIZATION_NOTES.md")
    with open(notes_path, 'w', encoding='utf-8') as f:
        f.write(optimization_notes)
    
    print(f"   📝 優化說明已保存: {notes_path}")

def main():
    """主函數"""
    print("⚡ CPU 模型優化")
    print("=" * 50)
    
    # CPU 優化
    model, tokenizer = optimize_for_cpu()
    
    if model is None or tokenizer is None:
        print("❌ 優化失敗")
        return False
    
    # 性能測試
    avg_time = benchmark_inference_speed(model, tokenizer)
    
    # 創建配置
    create_optimized_config()
    update_inference_engine()
    
    print(f"\n🎉 CPU 優化完成！")
    print(f"✅ 模型已針對 CPU 推理優化")
    if avg_time:
        print(f"✅ 平均推理時間: {avg_time:.2f}秒")
    print(f"✅ 優化配置和說明已創建")
    
    print(f"\n💡 使用建議:")
    print(f"   - 推理時使用 torch.no_grad()")
    print(f"   - 限制 max_new_tokens 以控制時間")
    print(f"   - 使用 Qubic 知識增強提高回應品質")
    print(f"   - 監控記憶體使用情況")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏸️ 優化被用戶中斷")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 優化過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

