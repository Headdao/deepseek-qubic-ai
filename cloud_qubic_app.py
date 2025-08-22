# 雲端版本的 Qubic AI 應用程式
# 適配三 VM 分散式 DeepSeek 架構

import sys
import os
import time
import logging
from typing import Optional, Dict, Any

# 添加專案根目錄到 Python 路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, '/Users/apple/qubic/QubiPy-main')

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# 本地模組導入
from app_config import config
from cloud_integration import CloudAIIntegration, CloudConfig

# QubiPy 導入
try:
    from qubipy.rpc.rpc_client import QubiPy_RPC  # type: ignore
    from qubipy.core.core_client import QubiPy_Core  # type: ignore
    QUBIPY_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ QubiPy 導入失敗: {e}")
    print("🔄 使用模擬數據模式")
    QUBIPY_AVAILABLE = False

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CloudQubicDataProvider:
    """
    雲端版本的 Qubic 資料提供者
    整合三 VM 分散式 AI 架構
    """
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 3  # 3秒快取
        
        # 初始化雲端 AI
        self.cloud_ai = CloudAIIntegration(orchestrator_url=CloudConfig.VM_ORCHESTRATOR)
        
        # 初始化 QubiPy 客戶端
        if QUBIPY_AVAILABLE:
            try:
                self.rpc_client = QubiPy_RPC()
                self.core_client = QubiPy_Core()
                logger.info("✅ QubiPy 客戶端初始化成功")
            except Exception as e:
                logger.error(f"❌ QubiPy 初始化失敗: {e}")
                self.rpc_client = None
                self.core_client = None
        else:
            self.rpc_client = None
            self.core_client = None
    
    def get_cloud_ai_health(self) -> Dict[str, Any]:
        """獲取雲端 AI 健康狀態"""
        return self.cloud_ai.health_check()
    
    def get_current_tick_data(self) -> Dict[str, Any]:
        """獲取當前 tick 資料"""
        cache_key = "current_tick"
        current_time = time.time()
        
        # 檢查快取
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if current_time - timestamp < self.cache_ttl:
                return cached_data
        
        try:
            if self.rpc_client:
                logger.info("🔄 正在獲取真實 Qubic 數據...")
                tick_number = self.rpc_client.get_latest_tick()
                
                # 獲取詳細統計資料
                stats = self.rpc_client.get_latest_stats()
                epoch = stats.get('epoch', 0) if isinstance(stats, dict) else 0
                
                logger.info(f"📊 獲取到 tick 號碼: {tick_number}")
                logger.info(f"📊 獲取到 epoch: {epoch}")
                
                tick_data = {
                    "tick": tick_number,
                    "epoch": epoch,
                    "duration": 1,  # Qubic tick duration
                    "timestamp": int(current_time),
                    "source": "real_qubic_network"
                }
                
                logger.info(f"✅ 成功獲取真實數據: Tick {tick_number}, Duration 1s")
                
                # 更新快取
                self.cache[cache_key] = (tick_data, current_time)
                return tick_data
            else:
                # 模擬數據
                return self._get_mock_tick_data()
                
        except Exception as e:
            logger.error(f"❌ 獲取 tick 數據失敗: {e}")
            return self._get_mock_tick_data()
    
    def get_network_stats(self) -> Dict[str, Any]:
        """獲取網路統計資料"""
        cache_key = "network_stats"
        current_time = time.time()
        
        # 檢查快取
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if current_time - timestamp < self.cache_ttl:
                return cached_data
        
        try:
            if self.rpc_client:
                logger.info("🔄 正在獲取真實 Qubic 數據...")
                stats = self.rpc_client.get_latest_stats()
                
                if isinstance(stats, dict):
                    logger.info(f"📊 獲取到統計數據: {stats}")
                    
                    # 格式化統計資料
                    formatted_stats = {
                        "currentTick": stats.get('currentTick', 0),
                        "epoch": stats.get('epoch', 0),
                        "ticksInCurrentEpoch": stats.get('ticksInCurrentEpoch', 0),
                        "emptyTicksInCurrentEpoch": stats.get('emptyTicksInCurrentEpoch', 0),
                        "epochTickQuality": round(stats.get('epochTickQuality', 0), 2),
                        "activeAddresses": stats.get('activeAddresses', 0),
                        "circulatingSupply": stats.get('circulatingSupply', '0'),
                        "marketCap": stats.get('marketCap', '0'),
                        "price": stats.get('price', 0),
                        "burnedQus": stats.get('burnedQus', '0'),
                        "timestamp": stats.get('timestamp', str(int(current_time))),
                        "source": "real_qubic_network"
                    }
                    
                    # 更新快取
                    self.cache[cache_key] = (formatted_stats, current_time)
                    return formatted_stats
                else:
                    logger.warning(f"⚠️ 統計資料格式異常: {stats}")
                    return self._get_mock_network_stats()
            else:
                return self._get_mock_network_stats()
                
        except Exception as e:
            logger.error(f"❌ 獲取統計數據失敗: {e}")
            return self._get_mock_network_stats()
    
    def get_ai_analysis(self, prompt: str, language: str = "zh-tw") -> str:
        """
        使用雲端分散式 AI 進行分析
        
        Args:
            prompt: 分析提示詞
            language: 回應語言
            
        Returns:
            AI 分析結果
        """
        try:
            # 獲取最新網路數據
            network_data = self.get_network_stats()
            
            # 使用雲端 AI 進行分析
            logger.info(f"🌐 使用雲端分散式 AI 進行分析 (語言: {language})")
            analysis_result = self.cloud_ai.analyze_qubic_data(network_data, language)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ 雲端 AI 分析失敗: {e}")
            
            # 備用回應
            if language == "en":
                return "The distributed AI analysis system is temporarily unavailable. The three-VM DeepSeek cluster is being restored. Please try again in a few moments."
            else:
                return "分散式 AI 分析系統暫時不可用。三 VM DeepSeek 集群正在恢復中。請稍後再試。"
    
    def get_ai_response(self, query: str, language: str = "zh-tw") -> str:
        """
        使用雲端分散式 AI 回答問題
        
        Args:
            query: 使用者查詢
            language: 回應語言
            
        Returns:
            AI 回應
        """
        try:
            logger.info(f"🌐 使用雲端分散式 AI 回答問題 (語言: {language})")
            response = self.cloud_ai.generate_response(query, language)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ 雲端 AI 回應失敗: {e}")
            
            # 備用回應
            if language == "en":
                return "The distributed AI response system is temporarily unavailable. The three-VM DeepSeek cluster is being restored. Please try again in a few moments."
            else:
                return "分散式 AI 回應系統暫時不可用。三 VM DeepSeek 集群正在恢復中。請稍後再試。"
    
    def _get_mock_tick_data(self) -> Dict[str, Any]:
        """模擬 tick 資料"""
        current_time = time.time()
        base_tick = 31500000 + int(current_time % 100000)
        
        return {
            "tick": base_tick,
            "epoch": 175,
            "duration": 1,
            "timestamp": int(current_time),
            "source": "mock_data"
        }
    
    def _get_mock_network_stats(self) -> Dict[str, Any]:
        """模擬網路統計資料"""
        current_time = time.time()
        base_tick = 31500000 + int(current_time % 100000)
        
        return {
            "currentTick": base_tick,
            "epoch": 175,
            "ticksInCurrentEpoch": 35000 + int(current_time % 5000),
            "emptyTicksInCurrentEpoch": 4000,
            "epochTickQuality": 88.5 + (current_time % 10),
            "activeAddresses": 590000 + int(current_time % 10000),
            "circulatingSupply": "155563915170467",
            "marketCap": "424689489",
            "price": 2.73e-06,
            "burnedQus": "19436084829533",
            "timestamp": str(int(current_time)),
            "source": "mock_data"
        }


# 建立 Flask 應用程式
app = Flask(__name__)
CORS(app)

# 初始化資料提供者
data_provider = CloudQubicDataProvider()

@app.route('/')
def index():
    """首頁重導向到 QDashboard"""
    return send_from_directory('frontend', 'index.html')

@app.route('/qdashboard/')
def qdashboard():
    """QDashboard 主頁面"""
    return send_from_directory('frontend/qdashboard', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """提供靜態檔案"""
    try:
        if filename.startswith('qdashboard/'):
            file_path = filename[11:]  # 移除 'qdashboard/' 前綴
            return send_from_directory('frontend/qdashboard', file_path)
        else:
            return send_from_directory('frontend', filename)
    except Exception as e:
        logger.error(f"❌ 靜態檔案錯誤: {e}")
        return jsonify({"error": "File not found"}), 404

# API 端點
@app.route('/api/tick')
def get_tick():
    """獲取當前 tick 資料"""
    try:
        tick_data = data_provider.get_current_tick_data()
        return jsonify({
            "success": True,
            "data": tick_data
        })
    except Exception as e:
        logger.error(f"❌ Tick API 錯誤: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/stats')
def get_stats():
    """獲取網路統計資料"""
    try:
        stats = data_provider.get_network_stats()
        return jsonify({
            "success": True,
            "data": stats
        })
    except Exception as e:
        logger.error(f"❌ Stats API 錯誤: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/health')
def health_check():
    """系統健康檢查"""
    try:
        # 檢查雲端 AI 健康狀態
        cloud_ai_health = data_provider.get_cloud_ai_health()
        
        # 檢查 QubiPy 連線
        qubipy_status = "available" if QUBIPY_AVAILABLE and data_provider.rpc_client else "unavailable"
        
        return jsonify({
            "success": True,
            "status": "healthy",
            "timestamp": int(time.time()),
            "components": {
                "qubipy": qubipy_status,
                "cloud_ai": cloud_ai_health,
                "cache": "active",
                "api": "operational"
            },
            "deployment": "cloud_three_vm"
        })
    except Exception as e:
        logger.error(f"❌ Health Check 錯誤: {e}")
        return jsonify({
            "success": False,
            "status": "unhealthy",
            "error": str(e)
        }), 500

@app.route('/api/ai/query', methods=['POST'])
def ai_query():
    """AI 問答 API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "請求資料格式錯誤"
            }), 400
        
        query = data.get('query', '').strip()
        language = data.get('language', 'zh-tw')
        
        if not query:
            return jsonify({
                "success": False,
                "error": "查詢內容不能為空"
            }), 400
        
        logger.info(f"🤖 AI 查詢: {query} (語言: {language})")
        
        # 使用雲端分散式 AI
        response = data_provider.get_ai_response(query, language)
        
        return jsonify({
            "success": True,
            "response": response,
            "language": language,
            "timestamp": int(time.time()),
            "source": "cloud_distributed_ai"
        })
        
    except Exception as e:
        logger.error(f"❌ AI Query 錯誤: {e}")
        return jsonify({
            "success": False,
            "error": f"AI 查詢失敗: {str(e)}"
        }), 500

@app.route('/api/ai/analyze', methods=['POST'])
def ai_analyze():
    """AI 分析 API"""
    try:
        data = request.get_json()
        language = data.get('language', 'zh-tw') if data else 'zh-tw'
        
        logger.info(f"🤖 AI 分析請求 (語言: {language})")
        
        # 使用雲端分散式 AI 進行分析
        analysis_result = data_provider.get_ai_analysis("分析當前 Qubic 網路狀態", language)
        
        return jsonify({
            "success": True,
            "analysis": analysis_result,
            "language": language,
            "timestamp": int(time.time()),
            "source": "cloud_distributed_ai"
        })
        
    except Exception as e:
        logger.error(f"❌ AI Analyze 錯誤: {e}")
        return jsonify({
            "success": False,
            "error": f"AI 分析失敗: {str(e)}"
        }), 500

if __name__ == '__main__':
    print("🚀 雲端版 QDashboard 啟動中...")
    print("📡 整合三 VM 分散式 DeepSeek 架構")
    config.print_config()
    
    # 檢查雲端 AI 連線
    try:
        health = data_provider.get_cloud_ai_health()
        if health.get('cloud_available', False):
            print("✅ 雲端 AI 系統連線成功")
        else:
            print("⚠️ 雲端 AI 系統連線失敗，將使用備用模式")
    except Exception as e:
        print(f"⚠️ 無法檢查雲端 AI 狀態: {e}")
    
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )

