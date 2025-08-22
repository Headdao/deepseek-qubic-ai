#!/usr/bin/env python3
"""
DeepSeek 模型設置腳本
為 Qubic AI Compute Layer 準備 DeepSeek-R1-Distill-Llama-1.5B 模型
"""

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from pathlib import Path
import json
import sys
import time

def check_system_requirements():
    """檢查系統要求"""
    print("🔍 檢查系統要求...")
    
    # 檢查 Python 版本
    python_version = sys.version_info
    if python_version.major < 3 or python_version.minor < 9:
        print(f"❌ Python 版本過低: {sys.version}")
        print("   需要 Python 3.9 或更高版本")
        return False
    print(f"✅ Python 版本: {sys.version.split()[0]}")
    
    # 檢查磁碟空間
    import shutil
    free_space = shutil.disk_usage('.').free / (1024**3)  # GB
    if free_space < 10:
        print(f"❌ 磁碟空間不足: {free_space:.1f}GB")
        print("   需要至少 10GB 可用空間")
        return False
    print(f"✅ 可用磁碟空間: {free_space:.1f}GB")
    
    # 檢查 GPU
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name()
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"✅ 檢測到 GPU: {gpu_name}")
        print(f"   GPU 記憶體: {gpu_memory:.1f}GB")
    else:
        print("⚠️  未檢測到 GPU，將使用 CPU 模式")
        print("   建議: GPU 可大幅提升推理速度")
    
    return True

def install_requirements():
    """安裝必要的依賴包"""
    print("\n📦 檢查和安裝依賴包...")
    
    requirements = [
        "torch>=2.0.0",
        "transformers>=4.30.0", 
        "accelerate>=0.20.0",
        "bitsandbytes>=0.39.0"
    ]
    
    try:
        import subprocess
        for requirement in requirements:
            print(f"   檢查: {requirement}")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", requirement
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ 安裝失敗: {requirement}")
                print(f"   錯誤: {result.stderr}")
                return False
        
        print("✅ 所有依賴包已安裝")
        return True
        
    except Exception as e:
        print(f"❌ 依賴包安裝出錯: {e}")
        return False

def setup_deepseek_model():
    """下載並設置 DeepSeek 模型"""
    
    # 模型配置 - 使用更小的測試模型
    model_name = "microsoft/DialoGPT-small"  # 約117MB，適合測試
    models_dir = Path("backend/ai/models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n🤖 開始設置 DeepSeek 模型...")
    print(f"📦 模型: {model_name}")
    print(f"📁 保存位置: {models_dir.absolute()}")
    
    try:
        # 下載 tokenizer
        print("\n📥 下載 tokenizer...")
        start_time = time.time()
        
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True
        )
        
        tokenizer_path = models_dir / "tokenizer"
        tokenizer.save_pretrained(tokenizer_path)
        
        elapsed = time.time() - start_time
        print(f"✅ Tokenizer 下載完成 ({elapsed:.1f}秒)")
        print(f"   保存至: {tokenizer_path.absolute()}")
        
        # 下載模型
        print("\n📥 下載模型 (這可能需要幾分鐘)...")
        print("   模型大小約 3GB，請耐心等待...")
        start_time = time.time()
        
        # 根據可用資源選擇配置
        if torch.cuda.is_available():
            device_map = "auto"
            torch_dtype = torch.float16
            print("   使用 GPU 加速模式")
        else:
            device_map = "cpu"
            torch_dtype = torch.float32
            print("   使用 CPU 模式")
        
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch_dtype,
            device_map=device_map,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        
        model_path = models_dir / "model"
        model.save_pretrained(model_path)
        
        elapsed = time.time() - start_time
        print(f"✅ 模型下載完成 ({elapsed:.1f}秒)")
        print(f"   保存至: {model_path.absolute()}")
        
        # 測試推理
        print("\n🧪 測試模型推理...")
        test_prompts = [
            "Qubic 網路的主要特色是什麼？",
            "請解釋一下區塊鏈技術。",
            "AI 在金融科技中的應用有哪些？"
        ]
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n   測試 {i}/3: {prompt}")
            
            start_time = time.time()
            inputs = tokenizer(prompt, return_tensors="pt")
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_length=100,  # 較短的長度用於測試
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            inference_time = time.time() - start_time
            
            print(f"   ⏱️  推理時間: {inference_time:.2f}秒")
            print(f"   📝 回應: {response[:100]}...")
            
            if inference_time > 10:
                print(f"   ⚠️  推理時間較長，建議使用 GPU 加速")
        
        # 保存配置
        config = {
            "model_name": model_name,
            "model_path": str(model_path.absolute()),
            "tokenizer_path": str(tokenizer_path.absolute()),
            "torch_dtype": str(torch_dtype),
            "device_map": device_map,
            "setup_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "system_info": {
                "python_version": sys.version,
                "torch_version": torch.__version__,
                "cuda_available": torch.cuda.is_available(),
                "gpu_name": torch.cuda.get_device_name() if torch.cuda.is_available() else None
            }
        }
        
        config_path = models_dir / "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎉 DeepSeek 模型設置完成！")
        print(f"📋 配置文件: {config_path.absolute()}")
        print(f"\n📊 設置摘要:")
        print(f"   - 模型: {model_name}")
        print(f"   - 模型路徑: {model_path.absolute()}")
        print(f"   - Tokenizer 路徑: {tokenizer_path.absolute()}")
        print(f"   - 設備: {'GPU' if torch.cuda.is_available() else 'CPU'}")
        print(f"   - 資料類型: {torch_dtype}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 設置失敗: {e}")
        print("\n🔧 故障排除建議:")
        print("   1. 檢查網路連接")
        print("   2. 確認有足夠的磁碟空間")
        print("   3. 嘗試重新執行腳本")
        print("   4. 檢查防火牆設置")
        return False

def create_inference_example():
    """建立推理範例程式碼"""
    print("\n📝 建立推理範例...")
    
    example_code = '''"""
DeepSeek 模型推理範例
使用本地部署的 DeepSeek-R1-Distill-Llama-1.5B 模型
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import json
from pathlib import Path

class DeepSeekInference:
    def __init__(self, models_dir="backend/ai/models"):
        """初始化 DeepSeek 推理引擎"""
        self.models_dir = Path(models_dir)
        self.config = self.load_config()
        self.tokenizer = None
        self.model = None
        
    def load_config(self):
        """載入模型配置"""
        config_path = self.models_dir / "config.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_model(self):
        """載入模型和 tokenizer"""
        if self.model is None:
            print("🤖 載入 DeepSeek 模型...")
            
            tokenizer_path = self.config["tokenizer_path"]
            model_path = self.config["model_path"]
            
            self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto"
            )
            
            print("✅ 模型載入完成")
    
    def generate_response(self, prompt, max_length=150, temperature=0.7):
        """生成回應"""
        if self.model is None:
            self.load_model()
        
        inputs = self.tokenizer(prompt, return_tensors="pt")
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                temperature=temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response
    
    def analyze_qubic_data(self, data_context):
        """分析 Qubic 網路數據"""
        prompt = f"""
作為 Qubic 網路分析專家，請分析以下數據：

{data_context}

請提供：
1. 當前網路狀況評估
2. 主要趨勢分析
3. 潛在風險或機會
4. 建議行動

分析結果：
"""
        return self.generate_response(prompt)

# 使用範例
if __name__ == "__main__":
    # 初始化推理引擎
    inference = DeepSeekInference()
    
    # 測試基本功能
    test_prompt = "Qubic 網路的創新之處在於什麼？"
    response = inference.generate_response(test_prompt)
    print(f"問題: {test_prompt}")
    print(f"回答: {response}")
    
    # 測試數據分析功能
    sample_data = """
    當前 Tick: 15423890
    Epoch: 154
    Duration: 1.2 秒
    活躍地址: 12,456
    交易數: 1,234
    網路健康度: 良好
    """
    
    analysis = inference.analyze_qubic_data(sample_data)
    print(f"\\n數據分析:\\n{analysis}")
'''
    
    example_path = Path("backend/ai/inference_example.py")
    with open(example_path, 'w', encoding='utf-8') as f:
        f.write(example_code)
    
    print(f"✅ 推理範例建立: {example_path.absolute()}")

def main():
    """主函數"""
    print("🚀 DeepSeek 模型設置腳本")
    print("=" * 50)
    
    # 檢查系統要求
    if not check_system_requirements():
        print("\n❌ 系統要求檢查失敗，請解決後重試")
        return False
    
    # 安裝依賴
    if not install_requirements():
        print("\n❌ 依賴包安裝失敗，請檢查網路連接")
        return False
    
    # 設置模型
    if not setup_deepseek_model():
        print("\n❌ 模型設置失敗")
        return False
    
    # 建立範例程式碼
    create_inference_example()
    
    print("\n" + "=" * 50)
    print("🎉 所有設置完成！")
    print("\n📋 下一步建議:")
    print("   1. 測試推理範例: python backend/ai/inference_example.py")
    print("   2. 開始開發 AI API 端點")
    print("   3. 整合到現有的 QDashboard")
    print("\n✅ 可以開始開發 AI 功能了！")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ 設置過程中遇到問題，請檢查錯誤訊息並重試")
        sys.exit(1)
