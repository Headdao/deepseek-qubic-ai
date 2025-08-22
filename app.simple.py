"""
QDashboard_Lite 簡化版後端
直接調用 Qubic 官方 API，避免 QubiPy 依賴問題
"""

from flask import Flask, jsonify, send_file, send_from_directory
from flask_cors import CORS
import requests
import os
import time

app = Flask(__name__)
CORS(app)  # 允許跨域請求

# Qubic 官方 API 端點
QUBIC_API_BASE = 'https://rpc.qubic.org/v1'

def call_qubic_api(endpoint):
    """調用 Qubic 官方 API"""
    try:
        url = f"{QUBIC_API_BASE}{endpoint}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ API 調用失敗 {endpoint}: {e}")
        raise

def analyze_health(duration, tick):
    """分析網路健康狀況"""
    # Duration 狀態 (支援小數精度)
    if duration <= 0.2:
        duration_status = "極快"
    elif duration <= 0.8:
        duration_status = "很快"
    elif duration <= 1.2:
        duration_status = "快速" 
    elif duration <= 2.0:
        duration_status = "正常"
    elif duration <= 3.0:
        duration_status = "稍慢"
    else:
        duration_status = "異常"
    
    # 總體狀況
    if tick > 0 and duration <= 2:
        overall = "健康"
    elif tick > 0 and duration <= 3:
        overall = "一般"
    elif tick > 0:
        overall = "緩慢"
    else:
        overall = "異常"
    
    return {
        "overall": overall,
        "tick_status": "正常",
        "epoch_status": "正常",
        "duration_status": duration_status
    }

@app.route('/api/tick', methods=['GET'])
def get_tick():
    """獲取 Tick 資訊"""
    try:
        # 調用官方 API
        data = call_qubic_api('/latest-stats')
        api_data = data.get('data', {})
        
        # 轉換為我們的格式
        tick = int(api_data.get('currentTick', 0))
        
        # 計算更精確的 duration
        ticks_in_epoch = int(api_data.get('ticksInCurrentEpoch', 0))
        empty_ticks = int(api_data.get('emptyTicksInCurrentEpoch', 0))
        epoch_quality = float(api_data.get('epochTickQuality', 100))
        
        # 基於 epoch quality 推算 duration
        # epoch quality 越低，duration 越高
        if epoch_quality >= 99:
            duration = 0.1  # 極快
        elif epoch_quality >= 98:
            duration = 0.5  # 很快  
        elif epoch_quality >= 97:
            duration = 1.0  # 快速
        elif epoch_quality >= 95:
            duration = 1.5  # 正常
        elif epoch_quality >= 90:
            duration = 2.5  # 稍慢
        else:
            duration = 3.5  # 緩慢
            
        # 如果 empty ticks 比例很高，增加 duration
        if ticks_in_epoch > 0:
            empty_ratio = empty_ticks / ticks_in_epoch
            if empty_ratio > 0.05:  # 超過 5% 空 tick
                duration += empty_ratio * 2
        
        epoch = int(api_data.get('epoch', 174))
        initial_tick = tick - ticks_in_epoch
        
        health = analyze_health(duration, tick)
        
        result = {
            "tick": tick,
            "duration": duration,
            "epoch": epoch,
            "initialTick": initial_tick,
            "timestamp": int(time.time()),
            "health": health
        }
        
        print(f"✅ Tick 數據: {tick:,}, Duration: {duration:.1f}, Quality: {epoch_quality:.2f}%")
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ 獲取 Tick 失敗: {e}")
        return jsonify({
            "error": f"無法獲取數據: {str(e)}",
            "tick": 0,
            "duration": 0,
            "epoch": 174,
            "initialTick": 0,
            "timestamp": int(time.time()),
            "health": {
                "overall": "異常",
                "tick_status": "異常",
                "epoch_status": "異常", 
                "duration_status": "異常"
            }
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """獲取統計數據"""
    try:
        # 調用官方 API
        data = call_qubic_api('/latest-stats')
        api_data = data.get('data', {})
        
        # 轉換為我們的格式
        result = {
            "activeAddresses": int(api_data.get('activeAddresses', 0)),
            "marketCap": int(api_data.get('marketCap', 0)),
            "price": float(api_data.get('price', 0)),
            "epochTickQuality": float(api_data.get('epochTickQuality', 0)),
            "circulatingSupply": int(api_data.get('circulatingSupply', 0)),
            "burnedQus": int(api_data.get('burnedQus', 0)),
            "timestamp": int(time.time())
        }
        
        print(f"✅ 統計數據: 價格=${result['price']:.9f}")
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ 獲取統計失敗: {e}")
        return jsonify({
            "error": f"無法獲取統計數據: {str(e)}",
            "activeAddresses": 0,
            "marketCap": 0,
            "price": 0,
            "epochTickQuality": 0,
            "circulatingSupply": 0,
            "burnedQus": 0,
            "timestamp": int(time.time())
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """檢查服務狀態"""
    try:
        # 測試 API 連接
        call_qubic_api('/latest-stats')
        return jsonify({
            "status": "healthy",
            "timestamp": int(time.time()),
            "api_connected": True
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "timestamp": int(time.time()),
            "api_connected": False,
            "error": str(e)
        }), 500

@app.route('/')
def index():
    """首頁路由 - 提供前端頁面"""
    frontend_path = os.path.join(os.path.dirname(__file__), 'frontend', 'index.html')
    return send_file(frontend_path)

@app.route('/<path:filename>')
def static_files(filename):
    """靜態文件路由"""
    frontend_path = os.path.join(os.path.dirname(__file__), 'frontend', filename)
    if os.path.exists(frontend_path):
        return send_file(frontend_path)
    else:
        return "File not found", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print("🚀 啟動 QDashboard 簡化版後端...")
    print(f"📡 API 端點: http://localhost:{port}/api/")
    print(f"🌐 Web 介面: http://localhost:{port}/")
    app.run(debug=True, host='0.0.0.0', port=port)
