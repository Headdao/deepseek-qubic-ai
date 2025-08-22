#!/usr/bin/env python3
"""
最簡化 QDashboard - 純基本功能
"""
from flask import Flask, send_file, jsonify
from flask_cors import CORS
from app_config import config
import os
import time
import random

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return "<h1>QDashboard 正在運行!</h1><p><a href='/qdashboard/'>前往 QDashboard</a></p>"

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
    return jsonify({
        "tick": 31530000 + random.randint(0, 1000),
        "duration": random.choice([0, 1, 2]),
        "epoch": 175,
        "timestamp": int(time.time()),
        "health": {"overall": "健康"}
    })

@app.route('/api/status')
def api_status():
    return jsonify({"status": "ok", "timestamp": int(time.time())})

@app.route('/api/ai/analyze', methods=['POST'])
def ai_analyze():
    return jsonify({
        "analysis": "📊 Qubic 網路運行正常。當前指標顯示網路健康狀況良好，所有核心功能正常運作。",
        "success": True,
        "timestamp": int(time.time())
    })

@app.route('/api/ai/query', methods=['POST'])  
def ai_query():
    from flask import request
    data = request.get_json() or {}
    language = data.get('language', 'zh-tw')
    question = data.get('question', '')
    
    # 根據問題類型提供不同回應
    if any(keyword in question.lower() for keyword in ['network', 'status', '網路', '狀況']):
        if language == 'en':
            answer = "Current network status: HEALTHY. Tick processing is running smoothly with minimal duration. All core metrics indicate optimal performance."
        else:
            answer = "目前網路狀況：健康。Tick 處理運行順暢，持續時間極短。所有核心指標顯示最佳性能。"
    elif any(keyword in question.lower() for keyword in ['epoch', 'progress', 'predict', '進度', '預測']):
        if language == 'en':
            answer = "Epoch 175 is progressing normally. Based on current tick rate and network performance, expect stable progression without anomalies."
        else:
            answer = "Epoch 175 正常進行中。根據當前 tick 速率和網路性能，預期穩定進展，無異常。"
    elif any(keyword in question.lower() for keyword in ['health', 'evaluation', '健康', '評估']):
        if language == 'en':
            answer = "Network health evaluation: EXCELLENT. All systems operational, zero critical alerts, optimal processing speed maintained."
        else:
            answer = "網路健康評估：優秀。所有系統運行正常，零重大警報，保持最佳處理速度。"
    else:
        if language == 'en':
            answer = "System operating normally. Network conditions are stable with all key indicators within optimal ranges."
        else:
            answer = "系統正常運作中。網路狀況穩定，所有關鍵指標均在最佳範圍內。"
    
    return jsonify({
        "answer": answer,
        "success": True,
        "timestamp": int(time.time())
    })

@app.route('/api/stats')
def api_stats():
    # 模擬真實的 Qubic 統計數據，符合前端期望的數據結構
    return jsonify({
        "activeAddresses": 1198,
        "marketCap": 2450000000,  # $2.45B
        "price": 0.000000245,     # $0.000000245
        "epochTickQuality": 99.2,  # 99.2%
        "circulatingSupply": 10000000000000000,  # 10P QUs
        "burnedQus": 500000000000000,  # 500T QUs
        "network": {
            "total_nodes": 1205,
            "active_nodes": 1198,
            "avg_response_time": 45,
            "uptime_percentage": 99.7
        },
        "performance": {
            "tps": 2847,
            "peak_tps": 3421,
            "avg_block_time": 1.2,
            "pending_transactions": 23
        },
        "timestamp": int(time.time())
    })

if __name__ == '__main__':
    print("🚀 啟動最簡化 QDashboard...")
    config.print_config()
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
