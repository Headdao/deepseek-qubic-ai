#!/usr/bin/env python3
"""
簡化的模型測試 - 檢查基本推理功能
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import time

def test_basic_model():
    """測試基本模型功能"""
    
    print("🔍 基本模型功能測試")
    print("=" * 50)
    
    model_path = "/Users/apple/deepseek-qubic-ai/backend/ai/models/deepseek"
    
    try:
        print("📊 載入分詞器...")
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        
        print("🧠 載入模型...")
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            trust_remote_code=True,
            torch_dtype=torch.float16,
            device_map="cpu"  # 強制使用 CPU
        )
        
        print("✅ 模型載入成功")
        
        # 簡單測試
        test_prompt = "請用繁體中文回答：什麼是區塊鏈？"
        print(f"📝 測試提示詞: {test_prompt}")
        
        # 編碼
        inputs = tokenizer.encode(test_prompt, return_tensors="pt", max_length=256, truncation=True)
        print(f"📏 輸入 token 數量: {inputs.shape[1]}")
        
        # 生成
        print("🚀 開始生成...")
        start_time = time.time()
        
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_new_tokens=50,  # 較短的生成長度
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        generation_time = time.time() - start_time
        print(f"⏱️ 生成耗時: {generation_time:.2f}秒")
        
        # 解碼
        full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # 提取新生成的部分
        response = full_response[len(test_prompt):].strip()
        
        print(f"✅ 生成成功")
        print(f"📄 完整回應: {full_response}")
        print(f"📝 新生成內容: {response}")
        print(f"📏 回應長度: {len(response)} 字符")
        
        if response and len(response) > 10:
            print("✅ 模型工作正常")
            return True
        else:
            print("❌ 模型回應異常")
            return False
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_model()
    if success:
        print("\n🎉 基本模型測試通過")
    else:
        print("\n❌ 基本模型測試失敗")
