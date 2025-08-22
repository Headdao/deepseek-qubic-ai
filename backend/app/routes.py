"""
QDashboard API 路由
"""

from flask import Blueprint, jsonify, render_template
from .qubic_client import QubicNetworkClient
import time

# 建立藍圖
api_bp = Blueprint('api', __name__)

# 初始化 Qubic 客戶端
qubic_client = QubicNetworkClient()

@api_bp.route('/tick', methods=['GET'])
def get_tick():
    """
    獲取當前 tick 資訊的 API 端點
    
    Returns:
        JSON: 包含 tick, epoch, duration, initialTick 和時間戳的資料
    """
    try:
        # 獲取 tick 資訊
        tick_info = qubic_client.get_tick_info()
        
        # 添加時間戳和網路健康狀況
        response_data = {
            **tick_info,
            "timestamp": int(time.time()),
            "health": qubic_client.get_network_health()
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({
            "error": f"伺服器錯誤: {str(e)}",
            "tick": 0,
            "epoch": 0, 
            "duration": 0,
            "initialTick": 0,
            "timestamp": int(time.time()),
            "health": {
                "overall": "錯誤",
                "tick_status": "錯誤",
                "epoch_status": "錯誤",
                "duration_status": "錯誤"
            }
        }), 500

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    獲取網路統計數據的 API 端點
    
    Returns:
        JSON: 包含活躍地址數、市值等統計資訊
    """
    try:
        stats = qubic_client.get_network_stats()
        stats["timestamp"] = int(time.time())
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({
            "error": f"伺服器錯誤: {str(e)}",
            "activeAddresses": 0,
            "marketCap": 0,
            "burnedQus": 0,
            "epochTickQuality": 0,
            "circulatingSupply": 0,
            "price": 0,
            "timestamp": int(time.time())
        }), 500

@api_bp.route('/status', methods=['GET'])
def get_status():
    """
    獲取 API 狀態
    
    Returns:
        JSON: API 狀態資訊
    """
    try:
        # 測試 Qubic 連接
        tick_info = qubic_client.get_tick_info()
        
        return jsonify({
            "status": "online",
            "message": "QDashboard API 運行正常",
            "qubic_connected": "error" not in tick_info,
            "timestamp": int(time.time()),
            "version": "0.1.0"
        })
    
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": f"API 錯誤: {str(e)}",
            "qubic_connected": False,
            "timestamp": int(time.time()),
            "version": "0.1.0"
        }), 500
