#!/usr/bin/env python3
"""
專案進度檢查腳本
檢查所有組件狀態並更新配置
"""

import os
import sys
import json
import time
from pathlib import Path

def check_environment():
    """檢查環境設置"""
    print("🔍 檢查環境設置...")
    
    checks = {
        "Python 版本": sys.version_info >= (3, 9),
        "虛擬環境": os.environ.get('VIRTUAL_ENV') is not None,
        "工作目錄": Path.cwd().name == "deepseek-qubic-ai"
    }
    
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"   {status} {check}: {result}")
    
    return all(checks.values())

def check_dependencies():
    """檢查依賴套件"""
    print("\n📦 檢查依賴套件...")
    
    required_packages = [
        "torch", "transformers", "accelerate", 
        "bitsandbytes", "huggingface_hub", "flask", "qubipy"
    ]
    
    installed = {}
    for package in required_packages:
        try:
            __import__(package)
            if package == "torch":
                import torch
                version = torch.__version__
            elif package == "transformers":
                import transformers
                version = transformers.__version__
            else:
                version = "已安裝"
            installed[package] = version
            print(f"   ✅ {package}: {version}")
        except ImportError:
            installed[package] = None
            print(f"   ❌ {package}: 未安裝")
    
    return installed

def check_models():
    """檢查模型狀態"""
    print("\n🤖 檢查模型狀態...")
    
    models_dir = Path("backend/ai/models")
    if not models_dir.exists():
        print("   ❌ 模型目錄不存在")
        return {}
    
    # 檢查測試模型
    test_model = models_dir / "test_model"
    test_status = "✅ 可用" if test_model.exists() else "❌ 缺失"
    print(f"   📝 測試模型 (GPT2): {test_status}")
    
    # 檢查 DeepSeek 模型
    deepseek_dir = models_dir / "deepseek"
    deepseek_model = deepseek_dir / "model.safetensors"
    
    if deepseek_model.exists():
        size_gb = deepseek_model.stat().st_size / (1024**3)
        print(f"   🎯 DeepSeek 模型: ✅ 已下載 ({size_gb:.2f}GB)")
        
        # 檢查配置檔案
        config_file = models_dir / "deepseek_config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
            print(f"   📋 配置狀態: {config.get('status', '未知')}")
            
            # 嘗試測試推理
            test_result = test_deepseek_inference()
            if test_result:
                # 更新配置為成功
                config['download_success'] = True
                config['status'] = 'ready'
                config['notes'] = 'Model ready for inference'
                config['last_test'] = time.strftime("%Y-%m-%d %H:%M:%S")
                
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                print("   ✅ 推理測試: 成功")
            else:
                print("   ⚠️ 推理測試: 需要調整")
        else:
            print("   ⚠️ 配置檔案: 缺失")
    else:
        print("   ❌ DeepSeek 模型: 未下載")
    
    return {
        "test_model": test_model.exists(),
        "deepseek_model": deepseek_model.exists(),
        "model_size_gb": size_gb if deepseek_model.exists() else 0
    }

def test_deepseek_inference():
    """測試 DeepSeek 推理功能"""
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        model_path = "backend/ai/models/deepseek"
        
        # 載入 tokenizer 和模型
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float32,  # 使用 float32 確保相容性
            device_map="cpu"  # 強制使用 CPU
        )
        
        # 簡單測試
        test_input = "Hello, how are you?"
        inputs = tokenizer(test_input, return_tensors="pt")
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=50,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return True
        
    except Exception as e:
        print(f"   ⚠️ 推理測試錯誤: {e}")
        return False

def generate_progress_report():
    """生成進度報告"""
    print("\n" + "="*50)
    print("📊 專案進度總結")
    print("="*50)
    
    # 檢查各項目
    env_ok = check_environment()
    deps = check_dependencies()
    models = check_models()
    
    # 計算完成度
    total_tasks = 10
    completed_tasks = 0
    
    if env_ok:
        completed_tasks += 3
    if all(deps.values()):
        completed_tasks += 3
    if models.get("test_model"):
        completed_tasks += 1
    if models.get("deepseek_model"):
        completed_tasks += 2
    if models.get("model_size_gb", 0) > 3:  # 模型完整下載
        completed_tasks += 1
    
    completion_rate = (completed_tasks / total_tasks) * 100
    
    print(f"\n🎯 整體完成度: {completion_rate:.1f}% ({completed_tasks}/{total_tasks})")
    
    # 狀態分類
    if completion_rate >= 90:
        print("✅ 狀態: 準備就緒，可以開始 API 開發")
    elif completion_rate >= 70:
        print("🔄 狀態: 基本完成，需要微調")
    elif completion_rate >= 50:
        print("⚠️ 狀態: 進行中，需要繼續完成")
    else:
        print("❌ 狀態: 需要重新設置")
    
    # 下一步建議
    print(f"\n📋 下一步建議:")
    if completion_rate >= 80:
        print("   1. 建立推理 API 端點")
        print("   2. 整合到 QDashboard")
        print("   3. 開發 AI 分析功能")
    else:
        print("   1. 完成模型設置和測試")
        print("   2. 解決任何剩餘的依賴問題")
        print("   3. 驗證推理功能")
    
    return {
        "completion_rate": completion_rate,
        "environment": env_ok,
        "dependencies": deps,
        "models": models
    }

if __name__ == "__main__":
    report = generate_progress_report()
    
    # 保存報告
    report_file = Path("progress_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 進度報告已保存: {report_file}")

