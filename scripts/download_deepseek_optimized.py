#!/usr/bin/env python3
"""
優化的 DeepSeek 模型下載腳本
支援斷點續傳、進度顯示和錯誤恢復
"""

import os
import sys
import time
from pathlib import Path
from huggingface_hub import snapshot_download, hf_hub_download
from transformers import AutoTokenizer, AutoModelForCausalLM
import json
import subprocess

def check_available_models():
    """檢查可用的 DeepSeek 模型選項"""
    models = {
        "1": {
            "name": "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
            "size": "~3.5GB",
            "description": "原計劃模型 - 較大但功能完整"
        },
        "2": {
            "name": "deepseek-ai/deepseek-coder-1.3b-base",
            "size": "~2.6GB", 
            "description": "程式碼專用模型 - 適合技術分析"
        },
        "3": {
            "name": "microsoft/DialoGPT-medium",
            "size": "~1.4GB",
            "description": "對話模型 - 較小但適合測試"
        }
    }
    
    print("🤖 可用的模型選項:")
    for key, model in models.items():
        print(f"   {key}. {model['name']}")
        print(f"      大小: {model['size']}")
        print(f"      說明: {model['description']}\n")
    
    return models

def download_with_cli(model_name, target_dir):
    """使用 huggingface-cli 下載 (支援斷點續傳)"""
    print(f"🚀 使用 CLI 下載模型: {model_name}")
    print(f"📁 目標目錄: {target_dir}")
    
    cmd = [
        sys.executable, "-m", "huggingface_hub.commands.huggingface_cli",
        "download", model_name,
        "--local-dir", str(target_dir),
        "--resume-download"
    ]
    
    print("📥 開始下載 (支援斷點續傳)...")
    print("💡 提示: 如果下載中斷，重新執行此腳本即可從斷點繼續")
    
    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=False)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ CLI 下載失敗: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⏸️ 下載被用戶中斷")
        print("💡 重新執行此腳本可以從中斷點繼續下載")
        return False

def download_with_python(model_name, target_dir):
    """使用 Python API 下載"""
    print(f"🐍 使用 Python API 下載: {model_name}")
    
    try:
        print("📥 下載模型檔案...")
        snapshot_download(
            repo_id=model_name,
            local_dir=target_dir,
            resume_download=True,
            local_dir_use_symlinks=False
        )
        return True
    except Exception as e:
        print(f"❌ Python API 下載失敗: {e}")
        return False

def test_model(model_path, tokenizer_path=None):
    """測試下載的模型"""
    print("\n🧪 測試模型...")
    
    try:
        if tokenizer_path is None:
            tokenizer_path = model_path
            
        print("   載入 tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
        
        print("   載入模型...")
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype="auto",
            device_map="auto" if not sys.platform.startswith('darwin') else "cpu"
        )
        
        print("   執行推理測試...")
        test_input = "Qubic 是什麼？"
        inputs = tokenizer(test_input, return_tensors="pt")
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=100,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"✅ 測試成功!")
        print(f"   輸入: {test_input}")
        print(f"   輸出: {response[:150]}...")
        
        return True
        
    except Exception as e:
        print(f"⚠️ 模型測試失敗: {e}")
        print("   模型已下載但可能需要調整配置")
        return False

def save_model_config(model_name, model_path, success=True):
    """保存模型配置"""
    config = {
        "model_name": model_name,
        "model_path": str(model_path.absolute()),
        "download_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "download_success": success,
        "status": "ready" if success else "partial",
        "notes": "Model ready for inference" if success else "Download incomplete or test failed"
    }
    
    config_path = model_path.parent / "deepseek_config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"💾 配置已保存: {config_path}")
    return config_path

def main():
    """主函數"""
    print("🚀 DeepSeek 模型下載器")
    print("=" * 50)
    
    # 檢查可用模型
    models = check_available_models()
    
    # 用戶選擇
    choice = input("請選擇要下載的模型 (1-3, 預設=2): ").strip() or "2"
    
    if choice not in models:
        print("❌ 無效選擇，使用預設模型")
        choice = "2"
    
    selected_model = models[choice]
    model_name = selected_model["name"]
    
    print(f"\n✅ 已選擇: {model_name}")
    print(f"📊 預估大小: {selected_model['size']}")
    
    # 設置下載路徑
    models_dir = Path("backend/ai/models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = models_dir / "deepseek"
    model_path.mkdir(exist_ok=True)
    
    print(f"📁 下載目錄: {model_path.absolute()}")
    
    # 確認下載
    confirm = input("\n確定要開始下載嗎? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 下載已取消")
        return False
    
    # 嘗試下載
    print(f"\n🔄 開始下載 {model_name}...")
    start_time = time.time()
    
    # 優先使用 CLI 方式 (更穩定)
    success = download_with_cli(model_name, model_path)
    
    if not success:
        print("\n🔄 CLI 下載失敗，嘗試 Python API...")
        success = download_with_python(model_name, model_path)
    
    download_time = time.time() - start_time
    
    if success:
        print(f"\n🎉 模型下載完成! (耗時: {download_time:.1f}秒)")
        
        # 測試模型 (可選)
        test_choice = input("是否要測試模型? (y/N): ").strip().lower()
        if test_choice == 'y':
            try:
                import torch
                test_success = test_model(model_path)
            except ImportError:
                print("⚠️ PyTorch 未安裝，跳過模型測試")
                test_success = True
        else:
            test_success = True
            
        # 保存配置
        config_path = save_model_config(model_name, model_path, test_success)
        
        print(f"\n✅ 設置完成!")
        print(f"📋 下一步:")
        print(f"   1. 建立推理 API: python scripts/setup_inference_api.py")
        print(f"   2. 整合到 QDashboard")
        print(f"   3. 開始 AI 分析功能開發")
        
        return True
    else:
        print(f"\n❌ 下載失敗")
        print("🔧 建議:")
        print("   1. 檢查網路連接")
        print("   2. 確認磁碟空間充足")
        print("   3. 重新執行此腳本 (支援斷點續傳)")
        
        # 仍然保存配置以記錄狀態
        save_model_config(model_name, model_path, False)
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏸️ 用戶中斷下載")
        print("💡 重新執行此腳本可以從中斷點繼續")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 未預期的錯誤: {e}")
        sys.exit(1)

