#!/usr/bin/env python3
"""
簡化版 QDashboard - 不含 AI 功能
"""

from flask import Flask, send_file, jsonify
from flask_cors import CORS
import os
import time
import random

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    """首頁路由"""
    frontend_path = os.path.join(os.path.dirname(__file__), 'frontend', 'index.html')
    return send_file(frontend_path)

@app.route('/qdashboard/')
def qdashboard():
    """QDashboard 主頁面"""
    frontend_path = os.path.join(os.path.dirname(__file__), 'frontend', 'qdashboard', 'index.html')
    return send_file(frontend_path)

@app.route('/<path:filename>')
def static_files(filename):
    """靜態文件路由"""
    if filename.endswith('/'):
        index_path = os.path.join(os.path.dirname(__file__), 'frontend', filename, 'index.html')
        if os.path.exists(index_path):
            return send_file(index_path)
    
    frontend_path = os.path.join(os.path.dirname(__file__), 'frontend', filename)
    if os.path.exists(frontend_path) and os.path.isfile(frontend_path):
        return send_file(frontend_path)
    else:
        return "File not found", 404

@app.route('/api/tick')
def get_tick():
    """獲取 tick 資訊"""
    return jsonify({
        "tick": 31530000 + random.randint(0, 1000),
        "duration": random.choice([0, 1, 2]),
        "epoch": 175,
        "timestamp": int(time.time()),
        "health": {
            "overall": "健康",
            "computors": 676,
            "active": 650
        }
    })

@app.route('/api/status')
def api_status():
    """API 狀態檢查"""
    return jsonify({
        "status": "ok",
        "timestamp": int(time.time()),
        "version": "0.1.0"
    })

@app.route('/api/ai/analyze', methods=['POST'])
def ai_analyze():
    """AI 分析 API - 簡化版"""
    return jsonify({
        "analysis": "📊 **Qubic 網路即時狀況分析**\n\n🔹 **當前指標**:\n- Tick: 穩定增長中\n- Duration: 優秀表現\n- Epoch: 175 運行中\n- 整體健康度: 健康\n\n✅ 網路運行順暢，所有核心指標都在預期範圍內。",
        "success": True,
        "timestamp": int(time.time()),
        "analysis_time": 0.1
    })

@app.route('/api/ai/query', methods=['POST'])
def ai_query():
    """AI QA API - 簡化版"""
    return jsonify({
        "answer": "基於當前 Qubic 網路數據，系統運行狀況良好。Tick 持續穩定增長，Duration 表現優秀，整體網路健康度維持在理想狀態。",
        "success": True,
        "timestamp": int(time.time())
    })

if __name__ == '__main__':
    print("🚀 啟動簡化版 QDashboard...")
    print("📡 API 端點: http://localhost:8088/api/tick")
    print("🌐 Web 介面: http://localhost:8088/qdashboard/")
    print("💡 簡化版：不含複雜 AI 功能")
    app.run(debug=True, host='0.0.0.0', port=8088)


