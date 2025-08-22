"""
AI 分析 API 路由
為 QDashboard 提供 AI 驅動的分析端點
"""

from flask import Blueprint, jsonify, request
from ..app.qubic_client import QubicNetworkClient
import time
import logging

# 設置日誌
logger = logging.getLogger(__name__)

# 建立 AI API 藍圖
ai_bp = Blueprint('ai_api', __name__)

# 初始化組件
qubic_client = QubicNetworkClient()

# 延遲初始化推理引擎
_inference_engine = None

def get_inference_engine():
    """延遲初始化推理引擎"""
    global _inference_engine
    if _inference_engine is None:
        from .inference_engine import get_inference_engine as _get_engine
        _inference_engine = _get_engine()
    return _inference_engine

@ai_bp.route('/analyze', methods=['POST'])
def analyze_network_data():
    """
    分析 Qubic 網路數據
    
    POST Body (JSON):
    {
        "data": {
            "tick": 12345,
            "duration": 1.5,
            "epoch": 174,
            "health": {...}
        },
        "query": "optional custom query"
    }
    
    Returns:
        JSON: AI 分析結果
    """
    try:
        # 獲取推理引擎
        engine = get_inference_engine()
        
        # 解析請求數據
        request_data = request.get_json()
        if not request_data:
            return jsonify({
                "success": False,
                "error": "缺少請求數據",
                "message": "請提供 JSON 格式的數據"
            }), 400
        
        # 獲取要分析的數據
        data_to_analyze = request_data.get('data')
        custom_query = request_data.get('query', '')
        language = request_data.get('language', 'zh-tw')  # 支援語言選擇
        
        # 如果沒有提供數據，嘗試獲取即時數據
        if not data_to_analyze:
            logger.info("未提供分析數據，獲取即時 Qubic 數據")
            
            # 使用與主應用相同的數據源
            try:
                import requests
                import json
                from flask import current_app
                
                # 嘗試從主應用的 API 端點獲取數據
                with current_app.test_client() as client:
                    # 獲取 tick 數據
                    tick_response = client.get('/api/tick')
                    tick_data = json.loads(tick_response.data) if tick_response.status_code == 200 else {}
                    
                    # 獲取統計數據
                    stats_response = client.get('/api/stats')
                    stats_data = json.loads(stats_response.data) if stats_response.status_code == 200 else {}
                    
                    data_to_analyze = {
                        **tick_data,
                        **stats_data
                    }
                    logger.info(f"🔍 從主應用API獲取數據: tick={data_to_analyze.get('tick')}, duration={data_to_analyze.get('duration')}")
                    
            except Exception as e:
                logger.warning(f"從主應用API獲取數據失敗，使用備用方法: {e}")
                # 備用方法：使用原來的 qubic_client
                tick_info = qubic_client.get_tick_info()
                stats = qubic_client.get_network_stats()
                health = qubic_client.get_network_health()
                
                data_to_analyze = {
                    **tick_info,
                    **stats,
                    "health": health
                }
        
        # 執行 AI 分析
        logger.info(f"開始 AI 分析... (語言: {language})")
        logger.info(f"🔍 AI 分析接收到的數據: tick={data_to_analyze.get('tick')}, duration={data_to_analyze.get('duration')}, epoch={data_to_analyze.get('epoch')}")
        start_time = time.time()
        
        analysis_result = engine.analyze_qubic_data(data_to_analyze, language=language)
        
        analysis_time = time.time() - start_time
        logger.info(f"AI 分析完成，耗時: {analysis_time:.2f}秒")
        
        # 添加元數據
        analysis_result.update({
            "analysis_time": analysis_time,
            "data_source": "realtime" if not request_data.get('data') else "provided",
            "custom_query": custom_query,
            "api_version": "1.0"
        })
        
        return jsonify(analysis_result)
        
    except Exception as e:
        logger.error(f"AI 分析失敗: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "AI 分析過程中發生錯誤",
            "timestamp": int(time.time())
        }), 500

@ai_bp.route('/query', methods=['POST'])
def ai_query():
    """
    自然語言查詢端點
    
    POST Body (JSON):
    {
        "question": "What is the current network status?",
        "context": "optional context data"
    }
    
    Returns:
        JSON: AI 回應
    """
    try:
        # 獲取推理引擎
        engine = get_inference_engine()
        
        # 解析請求
        request_data = request.get_json()
        if not request_data or 'question' not in request_data:
            return jsonify({
                "success": False,
                "error": "缺少問題",
                "message": "請在 'question' 欄位中提供要查詢的問題"
            }), 400
        
        question = request_data['question']
        language = request_data.get('language', 'zh-tw')  # 支援 'en' 英文, 'zh-tw' 繁中
        context = request_data.get('context', '')
        
        # 建立查詢提示 - 修正為符合 DeepSeek-R1 最佳實踐
        if context:
            if language == "en":
                prompt = f"""<think>
I need to analyze the provided Qubic network data and answer in English only.
</think>

Based on the following Qubic network data:
{context}

Question: {question}

Please provide a professional analysis in English only. Do not use any Chinese characters.

Analysis:"""
            else:
                prompt = f"""<think>
我需要分析提供的 Qubic 網路數據並用繁體中文回答。
</think>

基於以下 Qubic 網路數據：
{context}

問題：{question}

請用繁體中文提供專業分析：

分析："""
        else:
            # 獲取當前網路數據作為上下文
            try:
                tick_info = qubic_client.get_tick_info()
                health = qubic_client.get_network_health()
                
                if language == "en":
                    prompt = f"""<think>
I need to analyze the user's specific question: "{question}" about Qubic network.
Current data: Tick {tick_info.get('tick', 0)}, Duration {tick_info.get('duration', 0)} seconds, Health {health.get('overall', 'unknown')}.

Question analysis:
- If about network status: focus on current operational metrics and real-time state
- If about health evaluation: focus on system stability, performance metrics, risk assessment
- If about Epoch progress: focus on progress calculation, completion estimation, efficiency trends
- If about performance: focus on throughput, latency, processing efficiency

I must provide a differentiated analysis specific to this question type.
</think>

As a professional Qubic blockchain analyst, current network metrics:
Tick: {tick_info.get('tick', 0)} | Duration: {tick_info.get('duration', 0)}s | Health: {health.get('overall', 'unknown')}

Question: {question}

Professional analysis in English only:"""
                else:
                    prompt = f"""<think>
我需要仔細分析用戶的具體問題："{question}"，並基於當前 Qubic 網路數據提供針對性的專業回答。
當前數據：Tick {tick_info.get('tick', 0)}，持續時間 {tick_info.get('duration', 0)} 秒，健康狀況 {health.get('overall', '未知')}。

用戶問題分析：
- 如果問題是關於網路狀況/狀態，重點分析當前運行指標
- 如果問題是關於健康評估，重點分析系統穩定性和風險
- 如果問題是關於 Epoch 進度，重點分析進度預測和時間估算
- 如果問題是關於性能，重點分析處理速度和效率指標

我需要針對具體問題提供專業且有差異化的回答。
</think>

作為專業的 Qubic 區塊鏈分析師，當前網路狀態：
Tick: {tick_info.get('tick', 0)} | Duration: {tick_info.get('duration', 0)}秒 | Health: {health.get('overall', '未知')}

用戶問題：{question}

針對此問題的專業分析："""
            except:
                if language == "en":
                    prompt = f"""<think>
I need to carefully analyze the user's specific question: "{question}" and provide a targeted professional answer about Qubic blockchain.

Question analysis:
- If about network status/condition, focus on current operational metrics
- If about health assessment, focus on system stability and risk analysis  
- If about Epoch progress, focus on progress prediction and time estimation
- If about performance, focus on processing speed and efficiency metrics

I need to provide a professional and differentiated answer specific to this question.
</think>

As a professional Qubic blockchain analyst, please answer this specific question:

Question: {question}

Professional analysis in English only (no Chinese characters):"""
                else:
                    prompt = f"""<think>
我需要回答這個關於 Qubic 區塊鏈的問題，使用繁體中文。
</think>

作為專業的 Qubic 區塊鏈專家，請回答以下問題：

問題：{question}

請用繁體中文提供專業分析：

分析："""
        
        # 生成回應
        logger.info(f"處理自然語言查詢: {question} (語言: {language})")
        start_time = time.time()
        
        response = engine.generate_response(prompt, max_length=250, language=language)
        
        response_time = time.time() - start_time
        logger.info(f"查詢回應生成完成，耗時: {response_time:.2f}秒")
        
        return jsonify({
            "success": True,
            "question": question,
            "answer": response,
            "response_time": response_time,
            "timestamp": int(time.time()),
            "api_version": "1.0"
        })
        
    except Exception as e:
        logger.error(f"自然語言查詢失敗: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "查詢過程中發生錯誤",
            "timestamp": int(time.time())
        }), 500

@ai_bp.route('/insights', methods=['GET'])
def get_network_insights():
    """
    獲取網路洞察和建議
    
    Returns:
        JSON: 當前網路的 AI 洞察
    """
    try:
        # 獲取推理引擎
        engine = get_inference_engine()
        
        # 獲取最新網路數據
        tick_info = qubic_client.get_tick_info()
        stats = qubic_client.get_network_stats()
        health = qubic_client.get_network_health()
        
        # 合併數據
        network_data = {
            **tick_info,
            **stats,
            "health": health
        }
        
        # 執行洞察分析
        logger.info("生成網路洞察...")
        insights_result = engine.analyze_qubic_data(network_data)
        
        # 添加網路數據快照
        insights_result['network_snapshot'] = {
            "tick": network_data.get('tick', 0),
            "duration": network_data.get('duration', 0),
            "epoch": network_data.get('epoch', 0),
            "health_status": health.get('overall', '未知'),
            "price": network_data.get('price', 0),
            "active_addresses": network_data.get('activeAddresses', 0)
        }
        
        return jsonify(insights_result)
        
    except Exception as e:
        logger.error(f"獲取網路洞察失敗: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "無法獲取網路洞察",
            "timestamp": int(time.time())
        }), 500

@ai_bp.route('/status', methods=['GET'])
def get_ai_status():
    """
    獲取 AI 系統狀態
    
    Returns:
        JSON: AI 系統狀態資訊
    """
    try:
        # 獲取推理引擎狀態
        engine = get_inference_engine()
        engine_status = engine.get_status()
        
        # 測試 Qubic 連接
        try:
            qubic_client.get_tick_info()
            qubic_connected = True
        except:
            qubic_connected = False
        
        # 組合狀態資訊
        status = {
            "ai_engine": {
                "status": "ready" if engine_status['ready'] else "not_ready",
                "model_loaded": engine_status['model_loaded'],
                "model_path": engine_status['model_path'],
                "device": engine_status['device']
            },
            "qubic_client": {
                "status": "connected" if qubic_connected else "disconnected",
                "connected": qubic_connected
            },
            "api": {
                "version": "1.0",
                "endpoints": ["/analyze", "/query", "/insights", "/status"],
                "status": "operational"
            },
            "timestamp": int(time.time()),
            "overall_status": "ready" if (engine_status['ready'] and qubic_connected) else "degraded"
        }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"獲取 AI 狀態失敗: {e}")
        return jsonify({
            "ai_engine": {"status": "error"},
            "qubic_client": {"status": "error"},
            "api": {"status": "error"},
            "error": str(e),
            "timestamp": int(time.time()),
            "overall_status": "error"
        }), 500

@ai_bp.route('/health', methods=['GET'])
def health_check():
    """
    AI API 健康檢查端點
    
    Returns:
        JSON: 簡單的健康狀態
    """
    try:
        engine = get_inference_engine()
        
        # 快速檢查
        model_ready = engine.model_loaded
        
        return jsonify({
            "status": "healthy" if model_ready else "degraded",
            "model_ready": model_ready,
            "timestamp": int(time.time())
        })
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": int(time.time())
        }), 503
