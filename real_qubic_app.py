#!/usr/bin/env python3
"""
QDashboard - 真實 Qubic 數據版本
使用 QubiPy 獲取真實的 Qubic 網路數據
"""
from flask import Flask, send_file, jsonify, request
from flask_cors import CORS
from app_config import config
import os
import time
import threading
import logging

# 導入 QubiPy
try:
    from qubipy.rpc.rpc_client import QubiPy_RPC  # type: ignore
    from qubipy.core.core_client import QubiPy_Core  # type: ignore
    print("✅ QubiPy 已載入，將使用真實 Qubic 數據")
    QUBIC_AVAILABLE = True
except ImportError as e:
    print(f"❌ QubiPy 導入失敗: {e}")
    QUBIC_AVAILABLE = False

# 導入 AI 組件
try:
    from backend.ai.inference_engine import get_inference_engine
    print("✅ AI 推理引擎已載入")
    AI_AVAILABLE = True
except ImportError as e:
    print(f"❌ AI 推理引擎導入失敗: {e}")
    AI_AVAILABLE = False

app = Flask(__name__)
CORS(app)

class RealQubicDataProvider:
    """真實 Qubic 數據提供者"""
    
    def __init__(self):
        self.qubic_client = None
        self.last_tick_data = None
        self.last_fetch_time = 0
        self.cache_duration = 3  # 3秒緩存
        self.connection_status = "初始化中"
        self.ai_engine = None
        # 高精度時間紀錄（毫秒級計算用）
        self._last_tick_ns = None
        
        if QUBIC_AVAILABLE:
            self._initialize_client()
        else:
            self.connection_status = "QubiPy 不可用"
            
        # 延遲初始化 AI 引擎
        if AI_AVAILABLE:
            self._initialize_ai_engine()
        else:
            print("⚠️ AI 推理引擎不可用")
    
    def _initialize_client(self):
        """初始化 Qubic 客戶端"""
        try:
            # 初始化 RPC 和 Core 客戶端
            self.rpc_client = QubiPy_RPC()
            self.core_client = QubiPy_Core()
            self.qubic_client = self.rpc_client  # 主要使用 RPC 客戶端
            self.connection_status = "已連線"
            print("🌐 Qubic RPC 和 Core 客戶端初始化成功")
        except Exception as e:
            print(f"⚠️ Qubic 客戶端初始化失敗: {e}")
            self.connection_status = f"連線失敗: {str(e)}"
            self.qubic_client = None
            self.rpc_client = None
            self.core_client = None
    
    def _initialize_ai_engine(self):
        """延遲初始化 AI 推理引擎"""
        try:
            print("⏳ 正在初始化 AI 推理引擎...")
            # 延遲到第一次 API 調用時才初始化
            self.ai_engine = None  # 將在第一次使用時初始化
            print("✅ AI 推理引擎初始化完成")
        except Exception as e:
            print(f"❌ AI 推理引擎初始化失敗: {e}")
            self.ai_engine = None
    
    def get_ai_engine(self):
        """獲取 AI 推理引擎（延遲載入）"""
        if self.ai_engine is None and AI_AVAILABLE:
            try:
                self.ai_engine = get_inference_engine()
                print("🧠 AI 推理引擎已載入")
            except Exception as e:
                print(f"❌ 載入 AI 推理引擎失敗: {e}")
                self.ai_engine = None
        return self.ai_engine
    
    def get_current_tick_data(self):
        """獲取當前 tick 數據"""
        current_time = time.time()
        
        # 檢查緩存
        if (self.last_tick_data and 
            current_time - self.last_fetch_time < self.cache_duration):
            return self.last_tick_data
        
        if self.qubic_client and self.rpc_client:
            try:
                # 獲取真實的 Qubic 網路數據
                print("🔄 正在獲取真實 Qubic 數據...")
                
                # 獲取當前 tick 信息（返回整數）
                tick_number = self.rpc_client.get_latest_tick()
                print(f"📊 獲取到 tick 號碼: {tick_number}")
                
                # 嘗試獲取 epoch 信息（從統計數據中獲取）
                try:
                    stats_data = self.rpc_client.get_latest_stats()
                    epoch = stats_data.get('epoch', 0)
                    print(f"📊 獲取到 epoch: {epoch}")
                except Exception as e:
                    print(f"⚠️ 無法從統計數據獲取 epoch: {e}")
                    epoch = 0
                
                # 嘗試獲取更多狀態信息
                try:
                    status_info = self.rpc_client.get_status()
                    print(f"📊 獲取到狀態信息: {status_info}")
                except:
                    status_info = {}
                
                # 計算持續時間（毫秒級 + 相容秒級）
                duration_info = self._calculate_duration(tick_number, status_info)
                
                data = {
                    "tick": tick_number,
                    # 相容欄位（整數秒）
                    "duration": duration_info.get("duration", 0),
                    # 新增毫秒級/浮點秒欄位
                    "duration_ms": duration_info.get("duration_ms", 0),
                    "duration_s": duration_info.get("duration_s", 0.0),
                    "epoch": epoch,
                    "timestamp": int(current_time),
                    "health": {
                        "overall": self._determine_health_status(tick_number, status_info)
                    },
                    "data_source": "real",
                    "connection_status": self.connection_status
                }
                
                self.last_tick_data = data
                self.last_fetch_time = current_time
                print(
                    f"✅ 成功獲取真實數據: Tick {data['tick']}, "
                    f"Duration {data.get('duration_s', 0.0):.2f}s (int={data.get('duration', 0)}s)"
                )
                return data
                
            except Exception as e:
                print(f"❌ 獲取真實數據失敗: {e}")
                self.connection_status = f"數據獲取失敗: {str(e)}"
        
        # 如果無法獲取真實數據，返回錯誤信息
        return {
            "tick": 0,
            "duration": 0,
            "epoch": 0,
            "timestamp": int(current_time),
            "health": {"overall": "無法連接"},
            "data_source": "error",
            "connection_status": self.connection_status,
            "error": "無法獲取真實 Qubic 數據"
        }
    
    def _calculate_duration(self, tick_number, status_info):
        """計算 tick 持續時間，提供毫秒級與秒級（相容）。"""
        try:
            delta_ms = None
            # 1) 優先使用 RPC 提供的時間戳
            if isinstance(status_info, dict):
                if 'timestamp_ms' in status_info and 'previous_timestamp_ms' in status_info:
                    delta_ms = max(0, int(status_info['timestamp_ms']) - int(status_info['previous_timestamp_ms']))
                elif 'timestamp' in status_info and 'previous_timestamp' in status_info:
                    # 秒 → 毫秒
                    delta_ms = max(0, int(status_info['timestamp']) - int(status_info['previous_timestamp'])) * 1000
                elif 'duration' in status_info:
                    # 僅有整數秒
                    delta_ms = max(0, int(status_info['duration']) * 1000)

            # 2) 回退：使用高精度計時器估算（僅在 tick 前進時）
            if delta_ms is None:
                now_ns = time.perf_counter_ns()
                if self._last_tick_ns is not None and hasattr(self, 'last_tick_number') and self.last_tick_number is not None:
                    if tick_number > self.last_tick_number:
                        delta_ms = max(0, (now_ns - self._last_tick_ns) // 1_000_000)
                self._last_tick_ns = now_ns

            # 記錄最近 tick
            self.last_tick_number = tick_number

            # 3) 統一輸出
            if delta_ms is None:
                delta_ms = 1000  # 最末回退 1 秒

            duration_s = delta_ms / 1000.0
            duration_int = 0 if delta_ms == 0 else int((delta_ms + 999) // 1000)  # ceil

            return {
                'duration_ms': delta_ms,
                'duration_s': duration_s,
                'duration': duration_int
            }
        except Exception:
            return {
                'duration_ms': 0,
                'duration_s': 0.0,
                'duration': 0
            }
    
    def _determine_health_status(self, tick_number, status):
        """根據網路狀態判斷健康狀況"""
        try:
            # 檢查 tick 是否有效
            if tick_number > 0:
                # 基於 tick 變化判斷健康狀況
                if hasattr(self, 'last_tick_number') and self.last_tick_number:
                    if tick_number > self.last_tick_number:
                        return "健康"  # Tick 在增長
                    elif tick_number == self.last_tick_number:
                        return "停滯"  # Tick 沒有變化
                    else:
                        return "異常"  # Tick 倒退
                else:
                    return "健康"  # 首次獲取，假設健康
            else:
                return "錯誤"  # 無效的 tick
        except Exception as e:
            print(f"⚠️ 健康狀態判斷失敗: {e}")
            return "未知"
    
    def get_network_stats(self):
        """獲取網路統計數據"""
        if self.rpc_client:
            try:
                # 獲取真實統計數據
                stats = self.rpc_client.get_latest_stats()
                print(f"📊 獲取到統計數據: {stats}")
                
                return {
                    "activeAddresses": stats.get('activeAddresses', 0),
                    "marketCap": stats.get('marketCap', 0),
                    "price": stats.get('price', 0.0),
                    "epochTickQuality": stats.get('epochTickQuality', 0.0),
                    "circulatingSupply": int(stats.get('circulatingSupply', 0)),
                    "burnedQus": int(stats.get('burnedQus', 0)),
                    "timestamp": int(time.time()),
                    "data_source": "real",
                    "epoch": stats.get('epoch', 0),
                    "currentTick": stats.get('currentTick', 0),
                    "ticksInCurrentEpoch": stats.get('ticksInCurrentEpoch', 0),
                    "emptyTicksInCurrentEpoch": stats.get('emptyTicksInCurrentEpoch', 0)
                }
            except Exception as e:
                print(f"❌ 獲取統計數據失敗: {e}")
        
        # 返回錯誤狀態
        return {
            "activeAddresses": 0,
            "marketCap": 0,
            "price": 0.0,
            "epochTickQuality": 0.0,
            "circulatingSupply": 0,
            "burnedQus": 0,
            "timestamp": int(time.time()),
            "data_source": "error",
            "error": "無法獲取統計數據"
        }

# 創建真實數據提供者實例
data_provider = RealQubicDataProvider()

@app.route('/')
def index():
    return f"""
    <h1>QDashboard - 真實 Qubic 數據版本</h1>
    <p>連接狀態: <strong>{data_provider.connection_status}</strong></p>
    <p>QubiPy 狀態: <strong>{'可用' if QUBIC_AVAILABLE else '不可用'}</strong></p>
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
    return jsonify(data_provider.get_current_tick_data())

@app.route('/api/stats')
def api_stats():
    """獲取網路統計數據"""
    return jsonify(data_provider.get_network_stats())

@app.route('/api/status')
def api_status():
    return jsonify({
        "status": "ok", 
        "qubic_available": QUBIC_AVAILABLE,
        "connection_status": data_provider.connection_status,
        "data_source": "real",
        "timestamp": int(time.time())
    })

@app.route('/api/ai/status', methods=['GET'])
def ai_status():
    """AI 狀態檢查端點"""
    try:
        ai_engine = data_provider.get_ai_engine()
        ai_available = ai_engine is not None
        
        # 獲取模型狀態
        model_status = "unknown"
        if ai_available:
            try:
                # 嘗試簡單的模型調用來檢查狀態
                model_status = "ready"
            except Exception:
                model_status = "error"
        
        return jsonify({
            "status": "ok",
            "ai_available": AI_AVAILABLE,
            "ai_engine_loaded": ai_available,
            "model_status": model_status,
            "qubic_integration": QUBIC_AVAILABLE,
            "timestamp": int(time.time())
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "ai_available": False,
            "error": str(e),
            "timestamp": int(time.time())
        }), 500

@app.route('/api/ai/analyze', methods=['POST'])  
def ai_analyze():
    """AI 分析端點 - 使用真正的 DeepSeek 引擎"""
    try:
        # 解析請求數據
        request_data = request.get_json() or {}
        language = request_data.get('language', 'zh-tw')
        
        # 獲取 AI 引擎
        ai_engine = data_provider.get_ai_engine()
        
        # 獲取要分析的數據
        data_to_analyze = request_data.get('data')
        if not data_to_analyze:
            # 使用實時數據
            data_to_analyze = data_provider.get_current_tick_data()
        
        if ai_engine and data_to_analyze.get('data_source') != 'error':
            # 數據健全性：若 duration 缺失或為 0，嘗試以最新 tick 值補充；最後保底為 1
            try:
                duration_val = data_to_analyze.get('duration')
                if duration_val in (None, 0):
                    fresh = data_provider.get_current_tick_data()
                    fresh_duration = fresh.get('duration')
                    data_to_analyze['duration'] = fresh_duration if fresh_duration not in (None, 0) else 1
            except Exception:
                data_to_analyze['duration'] = data_to_analyze.get('duration') or 1
            # 使用真正的 AI 引擎進行分析
            print(f"🧠 開始 AI 分析... (語言: {language})")
            start_time = time.time()
            
            analysis_result = ai_engine.analyze_qubic_data(data_to_analyze, language=language)
            
            analysis_time = time.time() - start_time
            print(f"✅ AI 分析完成，耗時: {analysis_time:.2f}秒")
            
            # 添加元數據
            analysis_result.update({
                "analysis_time": analysis_time,
                "data_source": "realtime_ai",
                "ai_engine": "deepseek-r1",
                "api_version": "2.0"
            })
            
            return jsonify(analysis_result)
        else:
            # 備用回應 - 使用語言查找表 (符合 i18n 最佳實踐)
            fallback_responses = {
                'zh-tw': {
                    'analysis': "❌ AI 分析暫時不可用\n📊 當前網路數據概覽\n⚡ 系統將繼續嘗試重新連接 AI 引擎",
                    'summary': "AI 引擎離線，提供基礎數據概覽"
                },
                'en': {
                    'analysis': "❌ AI analysis temporarily unavailable\n📊 Current network data overview\n⚡ System will continue attempting to reconnect AI engine",
                    'summary': "AI engine offline, providing basic data overview"
                }
            }
            
            response_lang = fallback_responses.get(language, fallback_responses['zh-tw'])
            
            return jsonify({
                "analysis": response_lang['analysis'],
                "summary": response_lang['summary'],
                "success": True,
                "data_source": "fallback",
                "ai_available": ai_engine is not None,
                "timestamp": int(time.time())
            })
            
    except Exception as e:
        print(f"❌ AI 分析失敗: {e}")
        
        # 錯誤回應 - 使用語言查找表
        error_responses = {
            'zh-tw': {
                'error': f"AI 分析過程中發生錯誤: {str(e)}",
                'message': "請稍後重試或聯繫技術支援"
            },
            'en': {
                'error': f"Error occurred during AI analysis: {str(e)}",
                'message': "Please try again later or contact technical support"
            }
        }
        
        language = request.get_json().get('language', 'zh-tw') if request.get_json() else 'zh-tw'
        response_lang = error_responses.get(language, error_responses['zh-tw'])
        
        return jsonify({
            "success": False,
            "error": response_lang['error'],
            "message": response_lang['message'],
            "timestamp": int(time.time())
        }), 500

@app.route('/api/ai/query', methods=['POST'])  
def ai_query():
    """AI 問答端點 - 使用真正的 DeepSeek 引擎"""
    try:
        # 解析請求數據
        request_data = request.get_json() or {}
        language = request_data.get('language', 'zh-tw')
        question = request_data.get('question', '')
        
        if not question:
            # 錯誤回應 - 使用語言查找表
            error_responses = {
                'zh-tw': {
                    'error': "缺少問題",
                    'message': "請在 'question' 欄位中提供要查詢的問題"
                },
                'en': {
                    'error': "Missing question",
                    'message': "Please provide a question in the 'question' field"
                }
            }
            
            response_lang = error_responses.get(language, error_responses['zh-tw'])
            return jsonify({
                "success": False,
                "error": response_lang['error'],
                "message": response_lang['message']
            }), 400
        
        # 獲取 AI 引擎
        ai_engine = data_provider.get_ai_engine()
        
        if ai_engine:
            # 使用真正的 AI 引擎
            print(f"🧠 處理 AI 問答: {question[:50]}... (語言: {language})")
            start_time = time.time()
            
            # 獲取當前網路數據作為上下文
            tick_data = data_provider.get_current_tick_data()
            
            # 建立 DeepSeek-R1 最佳實踐的提示詞
            if language == "en":
                prompt = f"""<think>
User question: "{question}" about Qubic network.
Current data: Tick {tick_data.get('tick', 0)}, Duration {tick_data.get('duration', 0)}s, Health {tick_data.get('health', {}).get('overall', 'unknown')}.
Need to provide targeted professional analysis in English only.
</think>

As a Qubic blockchain analyst, current network: Tick {tick_data.get('tick', 0)} | Duration {tick_data.get('duration', 0)}s | Health {tick_data.get('health', {}).get('overall', 'unknown')}

Question: {question}

Professional analysis in English:"""
            else:
                prompt = f"""<think>
用戶問題："{question}"，需要基於當前 Qubic 數據提供專業回答。
當前數據：Tick {tick_data.get('tick', 0)}，{tick_data.get('duration', 0)} 秒，{tick_data.get('health', {}).get('overall', '未知')}。
</think>

作為 Qubic 區塊鏈分析師，當前網路：Tick {tick_data.get('tick', 0)} | Duration {tick_data.get('duration', 0)}秒 | Health {tick_data.get('health', {}).get('overall', '未知')}

問題：{question}

專業分析："""
            
            response = ai_engine.generate_response(prompt, max_length=200, language=language)
            
            response_time = time.time() - start_time
            print(f"✅ AI 問答完成，耗時: {response_time:.2f}秒")
            
            return jsonify({
                "success": True,
                "question": question,
                "answer": response,
                "response_time": response_time,
                "language": language,
                "data_source": "realtime_ai",
                "timestamp": int(time.time())
            })
        else:
            # 備用回應 - 使用語言查找表
            tick_data = data_provider.get_current_tick_data()
            
            fallback_responses = {
                'zh-tw': f"基於真實 Qubic 數據：Tick {tick_data.get('tick', 0):,}，{tick_data.get('duration', 0)} 秒，健康狀況 {tick_data.get('health', {}).get('overall', '未知')}。（AI 引擎離線）",
                'en': f"Based on real Qubic data: Tick {tick_data.get('tick', 0):,}, {tick_data.get('duration', 0)}s, Health {tick_data.get('health', {}).get('overall', 'unknown')}. (AI engine offline)"
            }
            
            answer = fallback_responses.get(language, fallback_responses['zh-tw'])
            
            return jsonify({
                "success": True,
                "question": question,
                "answer": answer,
                "language": language,
                "data_source": "fallback",
                "timestamp": int(time.time())
            })
            
    except Exception as e:
        print(f"❌ AI 問答失敗: {e}")
        
        # 錯誤回應 - 使用語言查找表
        error_responses = {
            'zh-tw': f"AI 問答錯誤: {str(e)}",
            'en': f"AI query error: {str(e)}"
        }
        
        language = request.get_json().get('language', 'zh-tw') if request.get_json() else 'zh-tw'
        error_msg = error_responses.get(language, error_responses['zh-tw'])
        
        return jsonify({
            "success": False,
            "error": error_msg,
            "timestamp": int(time.time())
        }), 500

if __name__ == '__main__':
    print("🚀 啟動 QDashboard (真實 Qubic 數據版本)...")
    config.print_config()
    
    if QUBIC_AVAILABLE:
        print("🌐 QubiPy 可用，將嘗試連接真實 Qubic 網路")
        print("⏳ 正在初始化 Qubic 客戶端...")
    else:
        print("❌ QubiPy 不可用，無法獲取真實數據")
    
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
