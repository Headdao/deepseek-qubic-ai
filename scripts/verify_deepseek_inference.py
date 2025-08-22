#!/usr/bin/env python3
"""
深度驗證 DeepSeek 模型推理功能
進行多種測試以確保模型正常工作
"""

import os
import sys
import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from pathlib import Path
import traceback

def test_model_loading():
    """測試模型載入"""
    print("🔄 測試 1: 模型載入...")
    
    model_path = "backend/ai/models/deepseek"
    
    try:
        # 檢查模型檔案存在
        model_file = Path(model_path) / "model.safetensors"
        if not model_file.exists():
            print(f"❌ 模型檔案不存在: {model_file}")
            return False
        
        print(f"   ✅ 模型檔案存在: {model_file.stat().st_size / (1024**3):.2f}GB")
        
        # 載入 tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        print(f"   ✅ Tokenizer 載入成功: {tokenizer.__class__.__name__}")
        
        # 載入模型
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float32,
            device_map="cpu",
            low_cpu_mem_usage=True
        )
        print(f"   ✅ 模型載入成功: {model.__class__.__name__}")
        
        return True, tokenizer, model
        
    except Exception as e:
        print(f"   ❌ 載入失敗: {e}")
        traceback.print_exc()
        return False, None, None

def test_tokenization(tokenizer):
    """測試 tokenization"""
    print("\n🔄 測試 2: Tokenization...")
    
    try:
        test_texts = [
            "Hello, how are you?",
            "Qubic 是什麼？",
            "解釋一下區塊鏈技術。",
            "What is artificial intelligence?"
        ]
        
        for text in test_texts:
            inputs = tokenizer(text, return_tensors="pt")
            tokens = tokenizer.tokenize(text)
            print(f"   ✅ '{text}' → {len(tokens)} tokens")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Tokenization 失敗: {e}")
        return False

def test_inference(tokenizer, model):
    """測試推理功能"""
    print("\n🔄 測試 3: 推理功能...")
    
    try:
        test_cases = [
            {
                "input": "Hello, how are you?",
                "max_length": 50,
                "description": "基本英文對話"
            },
            {
                "input": "Qubic 是什麼？",
                "max_length": 100,
                "description": "中文技術問題"
            },
            {
                "input": "Explain blockchain technology.",
                "max_length": 80,
                "description": "技術解釋"
            }
        ]
        
        inference_results = []
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n   測試 3.{i}: {case['description']}")
            print(f"   輸入: {case['input']}")
            
            start_time = time.time()
            
            # Tokenize 輸入
            inputs = tokenizer(case['input'], return_tensors="pt")
            
            # 生成回應
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_length=case['max_length'],
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id
                )
            
            # 解碼結果
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            inference_time = time.time() - start_time
            
            print(f"   推理時間: {inference_time:.2f}秒")
            print(f"   輸出長度: {len(response)} 字符")
            print(f"   輸出內容: {response[:150]}...")
            
            # 檢查輸出品質
            if len(response) > len(case['input']) and response.startswith(case['input']):
                print(f"   ✅ 推理成功")
                inference_results.append(True)
            else:
                print(f"   ⚠️ 推理結果可能有問題")
                inference_results.append(False)
        
        success_rate = sum(inference_results) / len(inference_results) * 100
        print(f"\n   📊 推理成功率: {success_rate:.1f}% ({sum(inference_results)}/{len(inference_results)})")
        
        return success_rate >= 66.7  # 至少 2/3 成功
        
    except Exception as e:
        print(f"   ❌ 推理測試失敗: {e}")
        traceback.print_exc()
        return False

def test_model_configuration():
    """測試模型配置"""
    print("\n🔄 測試 4: 模型配置...")
    
    try:
        model_path = Path("backend/ai/models/deepseek")
        
        # 檢查配置檔案
        config_files = ["config.json", "tokenizer_config.json", "generation_config.json"]
        
        for config_file in config_files:
            file_path = model_path / config_file
            if file_path.exists():
                print(f"   ✅ {config_file}: 存在")
            else:
                print(f"   ❌ {config_file}: 缺失")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ 配置檢查失敗: {e}")
        return False

def test_memory_usage(model):
    """測試記憶體使用"""
    print("\n🔄 測試 5: 記憶體使用...")
    
    try:
        # 獲取模型參數數量
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        
        print(f"   📊 總參數數量: {total_params:,}")
        print(f"   📊 可訓練參數: {trainable_params:,}")
        
        # 估算記憶體使用 (Float32 = 4 bytes per parameter)
        memory_mb = (total_params * 4) / (1024 * 1024)
        print(f"   📊 估算記憶體使用: {memory_mb:.1f}MB")
        
        if memory_mb < 10000:  # 小於 10GB 是合理的
            print(f"   ✅ 記憶體使用合理")
            return True
        else:
            print(f"   ⚠️ 記憶體使用過高")
            return False
        
    except Exception as e:
        print(f"   ❌ 記憶體檢查失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("🚀 DeepSeek 模型深度驗證")
    print("=" * 50)
    
    # 檢查環境
    print(f"🔍 環境資訊:")
    print(f"   Python: {sys.version}")
    print(f"   PyTorch: {torch.__version__}")
    print(f"   工作目錄: {Path.cwd()}")
    print(f"   CUDA 可用: {torch.cuda.is_available()}")
    
    test_results = []
    
    # 測試 1: 模型載入
    load_success, tokenizer, model = test_model_loading()
    test_results.append(("模型載入", load_success))
    
    if not load_success:
        print("\n❌ 模型載入失敗，無法繼續後續測試")
        return False
    
    # 測試 2: Tokenization
    token_success = test_tokenization(tokenizer)
    test_results.append(("Tokenization", token_success))
    
    # 測試 3: 推理功能
    inference_success = test_inference(tokenizer, model)
    test_results.append(("推理功能", inference_success))
    
    # 測試 4: 模型配置
    config_success = test_model_configuration()
    test_results.append(("模型配置", config_success))
    
    # 測試 5: 記憶體使用
    memory_success = test_memory_usage(model)
    test_results.append(("記憶體使用", memory_success))
    
    # 總結
    print("\n" + "=" * 50)
    print("📊 驗證結果總結")
    print("=" * 50)
    
    for test_name, result in test_results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"   {test_name}: {status}")
    
    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\n🎯 總體測試結果: {success_rate:.1f}% ({passed_tests}/{total_tests})")
    
    if success_rate >= 80:
        print("✅ DeepSeek 模型推理功能正常，可以使用")
        return True
    elif success_rate >= 60:
        print("⚠️ DeepSeek 模型基本可用，但可能需要調整")
        return True
    else:
        print("❌ DeepSeek 模型有重大問題，需要重新設置")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏸️ 測試被用戶中斷")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤: {e}")
        traceback.print_exc()
        sys.exit(1)

