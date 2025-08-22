#!/usr/bin/env python3
"""
測試模型設置腳本 - 使用小型模型驗證流程
"""

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GPT2LMHeadModel, GPT2Tokenizer
from pathlib import Path
import json
import sys
import time

def setup_test_model():
    """設置小型測試模型"""
    print("🧪 設置測試模型以驗證推理流程...")
    
    # 使用 GPT2-small (約 500MB) 作為測試
    model_name = "gpt2"
    models_dir = Path("backend/ai/models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📦 測試模型: {model_name}")
    print(f"📁 保存位置: {models_dir.absolute()}")
    
    try:
        # 下載 tokenizer
        print("\n📥 下載 tokenizer...")
        tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        tokenizer_path = models_dir / "test_tokenizer"
        tokenizer.save_pretrained(tokenizer_path)
        print(f"✅ Tokenizer 完成: {tokenizer_path}")
        
        # 下載模型
        print("\n📥 下載模型...")
        model = GPT2LMHeadModel.from_pretrained(model_name)
        model_path = models_dir / "test_model"
        model.save_pretrained(model_path)
        print(f"✅ 模型完成: {model_path}")
        
        # 簡單測試
        print("\n🧪 測試推理...")
        inputs = tokenizer("Hello, how are you?", return_tensors="pt")
        with torch.no_grad():
            outputs = model.generate(**inputs, max_length=50, pad_token_id=tokenizer.eos_token_id)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"✅ 測試成功: {response}")
        
        # 保存配置
        config = {
            "model_name": model_name,
            "model_path": str(model_path.absolute()),
            "tokenizer_path": str(tokenizer_path.absolute()),
            "model_type": "test",
            "setup_date": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        config_path = models_dir / "test_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎉 測試模型設置完成!")
        print(f"📋 配置: {config_path}")
        print("\n📋 下一步:")
        print("   1. 準備下載正式的 DeepSeek 模型")
        print("   2. 建立推理 API")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試模型設置失敗: {e}")
        return False

if __name__ == "__main__":
    success = setup_test_model()
    sys.exit(0 if success else 1)

