#!/usr/bin/env python3
"""
QDashboard - 真實數據版本
使用 QubiPy 獲取真實的 Qubic 網路數據
"""
from flask import Flask, send_file, jsonify, request
from flask_cors import CORS
from app_config import config
import os
import time
import random

# 嘗試導入 QubiPy
try:
    import qubic  # type: ignore
    QUBIC_AVAILABLE = True
    print("✅ QubiPy 已載入，將使用真實 Qubic 數據")
except ImportError as e:
    QUBIC_AVAILABLE = False
    print(f"❌ QubiPy 未安裝: {e}")
    print("📝 將使用模擬數據，要獲取真實數據請安裝 QubiPy")

app = Flask(__name__)
CORS(app)

class QubicDataProvider:
    """Qubic 數據提供者 - 統一管理真實和模擬數據"""
    
    def __init__(self):
        self.use_real_data = QUBIC_AVAILABLE
        self.last_fetch_time = 0
        self.cache_duration = 5  # 5秒緩存
        self.cached_data = None
        
        if self.use_real_data:
            try:
                # 初始化 Qubic 客戶端
                self.qubic_client = qubic.QubicClient()
                print("🌐 Qubic 客戶端初始化成功")
            except Exception as e:
                print(f"⚠️ Qubic 客戶端初始化失敗: {e}")
                self.use_real_data = False
    
    def get_current_tick_data(self):
        """獲取當前 tick 數據"""
        current_time = time.time()
        
        # 檢查緩存
        if (self.cached_data and 
            current_time - self.last_fetch_time < self.cache_duration):
            return self.cached_data
        
        if self.use_real_data:
            try:
                # 獲取真實數據
                tick_info = self.qubic_client.get_tick_info()
                network_status = self.qubic_client.get_status()
                
                data = {
                    "tick": tick_info.get('tick', 0),
                    "duration": tick_info.get('duration', 0),
                    "epoch": tick_info.get('epoch', 0),
                    "timestamp": int(current_time),
                    "health": {
                        "overall": self._determine_health_status(tick_info, network_status)
                    }
                }
                
                self.cached_data = data
                self.last_fetch_time = current_time
                return data
                
            except Exception as e:
                print(f"❌ 獲取真實數據失敗: {e}")
                print("🔄 切換到模擬數據模式")
                self.use_real_data = False
        
        # 模擬數據
        data = {
            "tick": 31530000 + random.randint(0, 1000),
            "duration": random.choice([0, 1, 2]),
            "epoch": 175,
            "timestamp": int(current_time),
            "health": {"overall": "健康"}
        }
        
        self.cached_data = data
        self.last_fetch_time = current_time
        return data
    
    def _determine_health_status(self, tick_info, network_status):
        """根據網路狀態判斷健康狀況"""
        try:
            if network_status.get('connected', False):
                duration = tick_info.get('duration', 0)
                if duration == 0:
                    return "健康"
                elif duration <= 2:
                    return "正常"
                else:
                    return "緩慢"
            else:
                return "離線"
        except:
            return "未知"
    
    def get_network_stats(self):
        """獲取網路統計數據"""
        if self.use_real_data:
            try:
                # 獲取真實統計數據
                stats = self.qubic_client.get_network_stats()
                return {
                    "activeAddresses": stats.get('active_addresses', 0),
                    "marketCap": stats.get('market_cap', 0),
                    "price": stats.get('price', 0.0),
                    "epochTickQuality": stats.get('epoch_quality', 0.0),
                    "circulatingSupply": stats.get('circulating_supply', 0),
                    "burnedQus": stats.get('burned_qus', 0),
                    "timestamp": int(time.time())
                }
            except Exception as e:
                print(f"❌ 獲取統計數據失敗: {e}")
        
        # 模擬統計數據
        return {
            "activeAddresses": 1198,
            "marketCap": 2450000000,
            "price": 0.000000245,
            "epochTickQuality": 99.2,
            "circulatingSupply": 10000000000000000,
            "burnedQus": 500000000000000,
            "timestamp": int(time.time())
        }

# 創建數據提供者實例
data_provider = QubicDataProvider()

@app.route('/')
def index():
    data_source = "真實數據" if data_provider.use_real_data else "模擬數據"
    return f"""
    <h1>QDashboard 正在運行!</h1>
    <p>數據來源: <strong>{data_source}</strong></p>
    <p><a href='/qdashboard/'>前往 QDashboard</a></p>
    """

@app.route('/qdashboard/')
def qdashboard():
    frontend_path = os.path.join(os.path.dirname(__file__), 'frontend', 'qdashboard', 'index.html')
    try:
        return send_file(frontend_path)
    except Exception as e:
        return f"<h1>錯誤</h1><p>無法載入前端: {e}</p><p>路徑: {frontend_path}</p>"

@app.route('/<path:filename>')
def static_files(filename):
    frontend_path = os.path.join(os.path.dirname(__file__), 'frontend', filename)
    try:
        if os.path.exists(frontend_path) and os.path.isfile(frontend_path):
            return send_file(frontend_path)
        else:
            return f"File not found: {filename}", 404
    except Exception as e:
        return f"Error serving {filename}: {e}", 500

@app.route('/api/tick')
def get_tick():
    """獲取當前 tick 數據"""
    data = data_provider.get_current_tick_data()
    data['data_source'] = 'real' if data_provider.use_real_data else 'mock'
    return jsonify(data)

@app.route('/api/stats')
def api_stats():
    """獲取網路統計數據"""
    stats = data_provider.get_network_stats()
    stats['data_source'] = 'real' if data_provider.use_real_data else 'mock'
    return jsonify(stats)

@app.route('/api/status')
def api_status():
    return jsonify({
        "status": "ok", 
        "data_source": "real" if data_provider.use_real_data else "mock",
        "qubic_available": QUBIC_AVAILABLE,
        "timestamp": int(time.time())
    })

@app.route('/api/ai/analyze', methods=['POST'])  
def ai_analyze():
    data = data_provider.get_current_tick_data()
    analysis_text = f"📊 Qubic 網路即時分析 (數據來源: {'真實' if data_provider.use_real_data else '模擬'})\n"
    analysis_text += f"當前 Tick: {data['tick']:,}\n"
    analysis_text += f"持續時間: {data['duration']} 秒\n"
    analysis_text += f"Epoch: {data['epoch']}\n"
    analysis_text += f"網路狀態: {data['health']['overall']}"
    
    return jsonify({
        "analysis": analysis_text,
        "success": True,
        "data_source": "real" if data_provider.use_real_data else "mock",
        "timestamp": int(time.time())
    })

@app.route('/api/ai/query', methods=['POST'])  
def ai_query():
    data = request.get_json() or {}
    language = data.get('language', 'zh-tw')
    question = data.get('question', '')
    
    # 獲取實時數據
    tick_data = data_provider.get_current_tick_data()
    data_source_note = f"(數據來源: {'真實 Qubic 網路' if data_provider.use_real_data else '模擬'})"
    
    # 根據問題類型提供回應
    if any(keyword in question.lower() for keyword in ['network', 'status', '網路', '狀況']):
        if language == 'en':
            answer = f"Current network status: {tick_data['health']['overall'].upper()}. "
            answer += f"Tick {tick_data['tick']:,} processed with {tick_data['duration']} second duration. "
            answer += f"Network operating normally. {data_source_note}"
        else:
            answer = f"目前網路狀況：{tick_data['health']['overall']}。"
            answer += f"Tick {tick_data['tick']:,}，處理時間 {tick_data['duration']} 秒。"
            answer += f"網路運行正常。{data_source_note}"
    else:
        if language == 'en':
            answer = f"System operating with real-time data. Current tick: {tick_data['tick']:,}, "
            answer += f"duration: {tick_data['duration']}s, epoch: {tick_data['epoch']}. {data_source_note}"
        else:
            answer = f"系統使用即時數據運行。當前 tick: {tick_data['tick']:,}，"
            answer += f"持續時間: {tick_data['duration']}秒，epoch: {tick_data['epoch']}。{data_source_note}"
    
    return jsonify({
        "answer": answer,
        "success": True,
        "data_source": "real" if data_provider.use_real_data else "mock",
        "timestamp": int(time.time())
    })

if __name__ == '__main__':
    print("🚀 啟動 QDashboard (真實數據版本)...")
    config.print_config()
    
    if data_provider.use_real_data:
        print("🌐 使用真實 Qubic 網路數據")
    else:
        print("🎭 使用模擬數據 (QubiPy 不可用)")
        print("💡 提示: 安裝 QubiPy 以獲取真實數據")
    
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)

