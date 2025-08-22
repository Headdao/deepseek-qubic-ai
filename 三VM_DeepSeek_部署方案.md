# 三 VM DeepSeek 蒸餾模型部署方案

## 🎯 可行性評估：✅ 高度可行

基於 DeepSeek-R1-Distill-Llama-1.5B 的輕量化特性，使用三個 VM 部署是完全可行的方案。

---

## 🏗️ 架構設計

### 方案 A: 模型拆分式 (推薦)
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    VM-1         │    │    VM-2         │    │    VM-3         │
│  Orchestrator   │◄──►│  Compute Node   │◄──►│  Compute Node   │
│                 │    │                 │    │                 │
│ • 任務調度       │    │ • Embedding     │    │ • Transformer   │
│ • 負載均衡       │    │ • Tokenization  │    │ • Generation    │
│ • 結果聚合       │    │ • Layer 1-8     │    │ • Layer 9-16    │
│ • API Gateway   │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 方案 B: 並行處理式
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    VM-1         │    │    VM-2         │    │    VM-3         │
│   Load Balancer │    │  Model Instance │    │  Model Instance │
│                 │◄──►│       A         │    │       B         │
│ • 請求分發       │    │                 │    │                 │
│ • 健康檢查       │    │ • 完整模型      │    │ • 完整模型      │
│ • 結果聚合       │    │ • 處理 Query A  │    │ • 處理 Query B  │
│ • 快取管理       │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 💻 VM 配置需求

### 基本配置 (每台 VM)
```yaml
minimum_specs:
  cpu: "4 cores (2.5GHz+)"
  memory: "8GB RAM"
  storage: "25GB SSD"
  network: "1Gbps"
  os: "Ubuntu 20.04 LTS"

recommended_specs:
  cpu: "6 cores (3.0GHz+)"
  memory: "16GB RAM"
  storage: "50GB SSD"
  network: "10Gbps"
  gpu: "4GB VRAM (optional)"
```

### 雲端服務商選擇
```yaml
# Google Cloud Platform
gcp_options:
  instance_type: "n1-standard-4"
  cost: "$120/month (3 VMs)"
  gpu_addon: "NVIDIA T4" # +$100/month

# AWS EC2
aws_options:
  instance_type: "m5.xlarge"
  cost: "$140/month (3 VMs)"
  gpu_addon: "NVIDIA T4" # +$90/month

# Azure
azure_options:
  instance_type: "Standard_D4s_v3"
  cost: "$130/month (3 VMs)"
  gpu_addon: "NVIDIA T4" # +$95/month
```

---

## 🛠️ 技術實現

### 1. 環境設置
```bash
# 每台 VM 的基礎環境
sudo apt update && sudo apt upgrade -y
sudo apt install python3.9 python3-pip docker.io -y

# Python 環境
pip3 install torch transformers accelerate
pip3 install flask redis requests
pip3 install onnxruntime # 加速推理
```

### 2. 模型部署策略

#### VM-1: Orchestrator (協調器)
```python
# orchestrator.py
from flask import Flask, request, jsonify
import redis
import requests
import time

app = Flask(__name__)
redis_client = redis.Redis(host='localhost', port=6379)

class TaskOrchestrator:
    def __init__(self):
        self.compute_nodes = [
            "http://vm-2:5000",  # Node A
            "http://vm-3:5000"   # Node B
        ]
        self.current_node = 0
    
    def distribute_task(self, prompt):
        # 負載均衡: 輪詢分發
        node_url = self.compute_nodes[self.current_node]
        self.current_node = (self.current_node + 1) % len(self.compute_nodes)
        
        try:
            response = requests.post(
                f"{node_url}/inference",
                json={"prompt": prompt},
                timeout=30
            )
            return response.json()
        except Exception as e:
            # 故障轉移
            backup_node = self.compute_nodes[1 - self.current_node]
            response = requests.post(
                f"{backup_node}/inference",
                json={"prompt": prompt},
                timeout=30
            )
            return response.json()

@app.route('/api/inference', methods=['POST'])
def inference():
    data = request.json
    prompt = data.get('prompt', '')
    
    orchestrator = TaskOrchestrator()
    result = orchestrator.distribute_task(prompt)
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

#### VM-2 & VM-3: Compute Nodes (計算節點)
```python
# compute_node.py
from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import time
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

class DeepSeekInference:
    def __init__(self):
        self.model_name = "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,  # 半精度節省記憶體
            device_map="auto",
            trust_remote_code=True
        )
        
    def generate(self, prompt, max_length=512):
        start_time = time.time()
        
        inputs = self.tokenizer(prompt, return_tensors="pt")
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs.input_ids,
                max_length=max_length,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        inference_time = time.time() - start_time
        
        return {
            "response": response,
            "inference_time": inference_time,
            "model": self.model_name
        }

# 全域模型實例 (啟動時載入)
deepseek_model = DeepSeekInference()

@app.route('/inference', methods=['POST'])
def inference():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        result = deepseek_model.generate(prompt)
        
        app.logger.info(f"Inference completed in {result['inference_time']:.2f}s")
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Inference error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "model_loaded": deepseek_model is not None,
        "memory_usage": torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### 3. Docker 容器化部署
```dockerfile
# Dockerfile
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    wget curl git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "compute_node.py"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  orchestrator:
    build: .
    ports:
      - "5000:5000"
    environment:
      - ROLE=orchestrator
    volumes:
      - ./orchestrator.py:/app/app.py
    
  compute-node-1:
    build: .
    ports:
      - "5001:5000"
    environment:
      - ROLE=compute
      - NODE_ID=1
    volumes:
      - ./compute_node.py:/app/app.py
      - ./models:/app/models  # 模型快取
    
  compute-node-2:
    build: .
    ports:
      - "5002:5000"
    environment:
      - ROLE=compute
      - NODE_ID=2
    volumes:
      - ./compute_node.py:/app/app.py
      - ./models:/app/models
```

---

## 📊 性能評估

### 預期性能指標
```yaml
performance_metrics:
  single_vm_inference: "3-8 seconds"
  distributed_inference: "4-10 seconds"
  concurrent_requests: "5-10 requests"
  memory_usage: "4-6GB per VM"
  cpu_utilization: "60-80%"
  
throughput_estimates:
  queries_per_minute: "15-30"
  daily_capacity: "20,000+ queries"
  peak_concurrent: "10 users"
```

### 性能優化策略
```python
# 1. 模型量化
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.int8,  # INT8 量化
    device_map="auto"
)

# 2. KV Cache 優化
with torch.no_grad():
    outputs = model.generate(
        inputs.input_ids,
        use_cache=True,  # 啟用 KV cache
        max_length=512
    )

# 3. 批次處理
def batch_inference(prompts, batch_size=4):
    results = []
    for i in range(0, len(prompts), batch_size):
        batch = prompts[i:i+batch_size]
        batch_results = process_batch(batch)
        results.extend(batch_results)
    return results
```

---

## 🔒 部署最佳實踐

### 1. 安全性配置
```bash
# 防火牆設置
sudo ufw enable
sudo ufw allow 22    # SSH
sudo ufw allow 5000  # API port
sudo ufw allow from <vm-ip-range>  # 內部通信

# SSL 憑證 (使用 Let's Encrypt)
sudo certbot --nginx -d your-domain.com
```

### 2. 監控與日誌
```python
# 監控腳本
import psutil
import logging
import time

def monitor_system():
    while True:
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        
        logging.info(f"CPU: {cpu_usage}%, Memory: {memory_usage}%, Disk: {disk_usage}%")
        
        if cpu_usage > 90 or memory_usage > 90:
            logging.warning("High resource usage detected!")
        
        time.sleep(60)
```

### 3. 自動化部署
```bash
#!/bin/bash
# deploy.sh

echo "🚀 部署 DeepSeek 三 VM 集群..."

# VM-1: Orchestrator
ssh vm-1 << 'EOF'
cd /app
git pull origin main
docker-compose up -d orchestrator
EOF

# VM-2 & VM-3: Compute Nodes
for vm in vm-2 vm-3; do
    ssh $vm << 'EOF'
cd /app
git pull origin main
docker-compose up -d compute-node
EOF
done

echo "✅ 部署完成！"
```

---

## 💰 成本分析

### 雲端部署成本 (月費)
```yaml
infrastructure_costs:
  vm_instances: "$120-140 (3 VMs)"
  storage: "$30 (150GB SSD)"
  network: "$20 (頻寬)"
  monitoring: "$15 (Cloud Monitoring)"
  backup: "$10 (自動備份)"
  total_monthly: "$195-215"

# 本地部署成本 (一次性)
on_premise_costs:
  hardware: "$2000-3000 (3台伺服器)"
  setup: "$500 (安裝設置)"
  maintenance: "$100/month"
```

### ROI 分析
- **Break-even**: 約 12-15 個月 (vs 雲端)
- **3年 TCO**: 本地 $6500 vs 雲端 $7500
- **推薦**: 初期使用雲端，穩定後考慮本地

---

## 🎯 部署檢查清單

### Phase 1: 準備階段 ✅
- [ ] 選擇雲端服務商或準備硬體
- [ ] 申請 VM 實例 (3台)
- [ ] 設置網路與安全群組
- [ ] 安裝基礎軟體環境

### Phase 2: 模型部署 ✅
- [ ] 下載 DeepSeek 模型
- [ ] 測試單機推理
- [ ] 配置分散式架構
- [ ] 部署 Orchestrator

### Phase 3: 整合測試 ✅
- [ ] API 端點測試
- [ ] 負載測試
- [ ] 故障轉移測試
- [ ] 性能基準測試

### Phase 4: 生產部署 ✅
- [ ] 監控系統上線
- [ ] 日誌收集配置
- [ ] 備份策略執行
- [ ] 文檔完善

---

## 📈 擴展規劃

### 短期擴展 (1-3個月)
- **增加節點**: 擴展到 5-6 個 VM
- **模型升級**: 使用更大的蒸餾模型
- **快取層**: 增加 Redis 集群
- **API 網關**: 使用 nginx 負載均衡

### 中期擴展 (3-6個月)
- **Kubernetes**: 容器編排管理
- **微服務**: 拆分成更多專用服務
- **GPU 加速**: 添加 GPU 實例
- **CI/CD**: 自動化部署管道

### 長期擴展 (6-12個月)
- **多區域**: 跨地域部署
- **邊緣計算**: CDN + 邊緣節點
- **混合雲**: 本地 + 雲端混合
- **AI 優化**: 模型蒸餾與量化

---

## 🎉 結論

**✅ 高度可行**: 三個 VM 跑 DeepSeek 蒸餾模型是完全可行的方案

**核心優勢**:
- 🚀 **快速部署**: 2-3 天即可上線
- 💰 **成本可控**: 月費 $200 以內
- 📈 **易於擴展**: 水平擴展簡單
- 🔒 **穩定可靠**: 有故障轉移機制

**建議行動**:
1. **立即開始**: 申請 3台 VM (8GB RAM, 4 cores)
2. **分階段部署**: 先單機測試，再分散式
3. **監控優化**: 密切關注性能指標
4. **文檔記錄**: 詳細記錄部署過程

這個方案將為您的 Qubic AI Compute Layer 提供堅實的技術基礎！🎯
