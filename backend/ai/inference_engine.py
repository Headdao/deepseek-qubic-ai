#!/usr/bin/env python3
"""
DeepSeek AI 推理引擎
為 QDashboard 提供智能分析功能
"""

import os
import sys
import time
import json
import torch
from typing import Dict, Any, List, Optional
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM
import threading
import logging
from .qubic_knowledge import get_qubic_knowledge_base

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeepSeekInferenceEngine:
    """DeepSeek 推理引擎類別"""
    
    def __init__(self, model_path: str = "/Users/apple/deepseek-qubic-ai/backend/ai/models/deepseek"):
        """
        初始化推理引擎
        
        Args:
            model_path: 模型檔案路徑
        """
        self.model_path = Path(model_path)
        self.tokenizer = None
        self.model = None
        self.device = "cpu"  # 使用 CPU 模式
        self.model_loaded = False
        self.load_lock = threading.Lock()
        
        # 初始化 Qubic 知識庫
        self.qubic_kb = get_qubic_knowledge_base()
        
        # 推理配置 - 針對 Qubic 知識優化
        self.generation_config = {
            "max_new_tokens": 200,    # 使用 max_new_tokens 而非 max_length
            "temperature": 0.6,       # 降低溫度提高準確性
            "do_sample": True,
            "top_p": 0.8,            # 更保守的採樣
            "top_k": 40,             # 減少隨機性
            "repetition_penalty": 1.2 # 增加重複懲罰
        }
        
        logger.info(f"DeepSeek 推理引擎初始化，模型路徑: {self.model_path}")
        logger.info(f"Qubic 知識庫已載入")
    
    def _load_model(self) -> bool:
        """
        載入模型和 tokenizer
        
        Returns:
            載入是否成功
        """
        try:
            if self.model_loaded:
                return True
            
            with self.load_lock:
                if self.model_loaded:  # 雙重檢查
                    return True
                
                logger.info("開始載入 DeepSeek 模型...")
                start_time = time.time()
                
                # 檢查模型檔案
                model_file = self.model_path / "model.safetensors"
                if not model_file.exists():
                    logger.error(f"模型檔案不存在: {model_file}")
                    return False
                
                # 載入 tokenizer - 加入錯誤處理
                logger.info("載入 tokenizer...")
                try:
                    self.tokenizer = AutoTokenizer.from_pretrained(
                        str(self.model_path),
                        trust_remote_code=True,
                        local_files_only=True  # 避免網路延遲
                    )
                    logger.info("✅ Tokenizer 載入成功")
                except Exception as e:
                    logger.error(f"❌ Tokenizer 載入失敗: {e}")
                    return False
                
                # 載入模型 - 加入錯誤處理
                logger.info("載入模型...")
                try:
                    self.model = AutoModelForCausalLM.from_pretrained(
                        str(self.model_path),
                        torch_dtype=torch.float16,  # 使用 float16 減少記憶體
                        device_map=self.device,
                        low_cpu_mem_usage=True,
                        trust_remote_code=True,
                        local_files_only=True  # 避免網路延遲
                    )
                    logger.info("✅ 模型載入成功")
                except Exception as e:
                    logger.error(f"❌ 模型載入失敗: {e}")
                    return False
                
                # 設置為評估模式
                self.model.eval()
                
                load_time = time.time() - start_time
                logger.info(f"模型載入完成，耗時: {load_time:.2f}秒")
                
                self.model_loaded = True
                return True
                
        except Exception as e:
            logger.error(f"模型載入失敗: {e}")
            return False
    
    def _clean_response_format(self, response: str) -> str:
        """清理回應格式，移除過度格式化"""
        # 移除過多的表情符號（保留適量）
        import re
        
        # 移除連續的表情符號，只保留第一個
        response = re.sub(r'([📊🔹✅⚠️💡🎯🔍📈📉🚀⭐🌟]+)\s*([📊🔹✅⚠️💡🎯🔍📈📉🚀⭐🌟]+)', r'\1', response)
        
        # 移除過度的星號格式
        response = re.sub(r'\*\*([^*]+)\*\*', r'\1', response)
        
        # 簡化分隔線
        response = re.sub(r'[-=]{3,}', '', response)
        
        # 移除過多的換行
        response = re.sub(r'\n{3,}', '\n\n', response)
        
        # 確保句子結構自然
        response = response.strip()
        
        return response
    
    def generate_response(self, prompt: str, max_length: Optional[int] = None, enhance_with_qubic: bool = True, language: str = "zh-tw", **kwargs) -> str:
        """
        生成 AI 回應 - 支援 Qubic 知識增強
        
        Args:
            prompt: 輸入提示
            max_length: 最大生成長度
            enhance_with_qubic: 是否使用 Qubic 知識增強
            **kwargs: 其他生成參數
            
        Returns:
            生成的回應文本
        """
        try:
            # 確保模型已載入
            if not self._load_model():
                logger.warning("⚠️ 模型載入失敗，使用備用回應")
                if language == "en":
                    return self._get_fallback_english_response(prompt)
                else:
                    return self._get_fallback_qubic_response(prompt)
            
            logger.info(f"🧠 使用 DeepSeek 模型生成回應 (語言: {language})")
            
            # 使用 Qubic 知識增強提示
            enhanced_prompt = prompt
            if enhance_with_qubic:
                enhanced_prompt = self.qubic_kb.enhance_query_with_context(prompt, network_data=None, language=language)
                logger.info(f"使用 Qubic 知識庫增強提示 (語言: {language})")
            
            # 準備生成配置
            config = self.generation_config.copy()
            if max_length:
                config['max_new_tokens'] = max_length
            config.update(kwargs)
            
            # 確保模型已載入
            if not self.model_loaded or self.tokenizer is None or self.model is None:
                raise RuntimeError("模型尚未載入，請先呼叫 load_model() 方法")
            
            # Tokenize 輸入
            inputs = self.tokenizer(enhanced_prompt, return_tensors="pt")
            input_length = inputs['input_ids'].shape[1]
            
            # 生成回應
            logger.info(f"開始生成回應，輸入長度: {input_length}")
            start_time = time.time()
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=150,       # 適中長度
                    temperature=0.6,          # DeepSeek-R1 建議溫度
                    do_sample=True,
                    top_p=0.8,               # 適度多樣性
                    top_k=40,                # 平衡選擇
                    repetition_penalty=1.2,  # 適度防重複
                    pad_token_id=self.tokenizer.eos_token_id,
                    no_repeat_ngram_size=3   # 避免重複
                )
            
            # 解碼回應
            full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            logger.info(f"完整回應長度: {len(full_response)} 字符")
            logger.info(f"完整回應前200字符: {full_response[:200]}")
            logger.info(f"提示詞長度: {len(enhanced_prompt)} 字符")
            
            # 處理 DeepSeek-R1 的回應格式
            # 首先移除輸入提示詞
            if full_response.startswith(enhanced_prompt):
                response = full_response[len(enhanced_prompt):].strip()
            else:
                response = full_response.strip()
            
            logger.info(f"移除提示詞後的回應長度: {len(response)}")
            logger.info(f"移除提示詞後的回應前100字符: {response[:100]}")
            
            # 處理 DeepSeek-R1 的 <think> 標籤
            if '<think>' in response and '</think>' in response:
                # 提取 </think> 之後的實際回應
                think_end = response.find('</think>')
                if think_end != -1:
                    response = response[think_end + 8:].strip()  # 8 = len('</think>')
                    logger.info(f"移除 <think> 標籤後: {response[:50]}")
            
            # 如果是 Qubic 增強查詢，嘗試找到標記
            if enhance_with_qubic and response:
                answer_markers = ["專業分析：", "分析：", "Analysis:", "回答：", "答案：", "Answer:", "回應："]
                found_marker = False
                
                for marker in answer_markers:
                    if marker in response:
                        response = response.split(marker)[-1].strip()
                        logger.info(f"✅ 找到標記 '{marker}'，提取回應: {response[:50]}")
                        found_marker = True
                        break
                
                if not found_marker:
                    logger.info("未找到特定標記，使用完整回應")
            
            # 最終清理
            if not response or len(response.strip()) < 10:
                logger.warning("回應過短或為空，使用備用回應")
                if language == "en":
                    response = self._get_fallback_english_response(enhanced_prompt)
                else:
                    response = self._get_fallback_qubic_response(enhanced_prompt)
            
            generation_time = time.time() - start_time
            logger.info(f"回應生成完成，耗時: {generation_time:.2f}秒")
            
            # 清理回應格式
            response = self._clean_response_format(response)
            
            # 語言一致性檢查
            if language == "en":
                # 檢查是否包含中文字符
                has_chinese = any('\u4e00' <= char <= '\u9fff' for char in response)
                if has_chinese:
                    logger.warning("英文回應包含中文字符，使用備用英文回應")
                    response = self._get_fallback_english_response(prompt)
            
            # 驗證回應品質（僅針對 Qubic 相關查詢）
            if enhance_with_qubic:
                validation = self.qubic_kb.validate_response(response)
                logger.info(f"回應品質評估: {validation['quality']} (分數: {validation['accuracy_score']})")
                
                # 只有在極端情況下才使用備用回應
                if validation['accuracy_score'] < 40:
                    logger.warning(f"回應品質偏低 (分數: {validation['accuracy_score']})，使用備用回應")
                    if language == "en":
                        response = self._get_fallback_english_response(prompt)
                    else:
                        response = self._get_fallback_qubic_response(prompt)
                else:
                    logger.info(f"回應品質良好 (分數: {validation['accuracy_score']})，使用 AI 生成回應")
            
            return response if response else "生成的回應為空，請重試。"
            
        except Exception as e:
            logger.error(f"生成回應失敗: {e}")
            return f"錯誤: 無法生成回應 - {str(e)}"
    
    def _get_fallback_qubic_response(self, query: str) -> str:
        """當 AI 回應品質不佳時的備用 Qubic 回應"""
        query_lower = query.lower()
        
        # 嘗試獲取當前網路數據來提供即時分析
        try:
            from backend.app.qubic_client import QubicNetworkClient
            client = QubicNetworkClient()
            tick_info = client.get_tick_info()
            health = client.get_network_health()
            
            current_tick = tick_info.get('tick', 0)
            current_duration = tick_info.get('duration', 0) 
            current_epoch = tick_info.get('epoch', 0)
            health_status = health.get('overall', '未知')
            
            # 根據問題類型提供差異化回應
            if any(word in query_lower for word in ['網路狀況', '網路狀態', 'network status', '分析', 'analyze']):
                return f"""基於當前網路數據分析：
                
Tick: {current_tick:,} - 穩定增長，處理週期正常
Duration: {current_duration} 秒 - {"極佳表現，零延遲" if current_duration == 0 else "正常範圍，運行順暢" if current_duration <= 2 else "輕微延遲，需持續觀察"}
Epoch: {current_epoch} - 當前階段運行中
健康狀態: {health_status}

總結：網路整體運行{"極為順暢" if current_duration == 0 else "穩定正常" if current_duration <= 2 else "有輕微波動"}，所有核心指標都在預期範圍內。"""
            
            elif any(word in query_lower for word in ['健康', 'health', '評估', 'evaluate']):
                stability_score = "優秀" if current_duration == 0 else "良好" if current_duration <= 2 else "普通"
                return f"""網路健康狀況評估報告：

系統穩定性: {stability_score} - Duration {current_duration}秒表現{"卓越" if current_duration == 0 else "穩定" if current_duration <= 2 else "需關注"}
處理能力: 當前 Tick {current_tick:,}，持續正常增長
風險評估: {"無風險" if current_duration <= 1 else "低風險" if current_duration <= 2 else "中等風險"}

建議：{"繼續保持當前狀態" if current_duration <= 1 else "持續監控，暫無異常" if current_duration <= 2 else "加強監控，觀察趨勢變化"}"""
            
            elif any(word in query_lower for word in ['epoch', '進度', 'progress', '預測', 'predict']):
                # 計算 Epoch 進度（假設每個 Epoch 約 1000 個 Tick）
                epoch_start_tick = current_epoch * 1000
                epoch_progress = ((current_tick - epoch_start_tick) / 1000) * 100
                remaining_ticks = 1000 - (current_tick - epoch_start_tick)
                estimated_minutes = remaining_ticks * (current_duration + 1) / 60
                
                return f"""Epoch {current_epoch} 進度預測分析：

當前進度: {epoch_progress:.1f}%
剩餘 Ticks: 約 {remaining_ticks:,}
預估完成時間: {estimated_minutes:.1f} 分鐘（基於當前 {current_duration}秒 Duration）

趨勢分析：{"進度穩定，預計按時完成" if current_duration <= 1 else "進度正常，預計如期完成" if current_duration <= 2 else "進度略慢，密切觀察"}
效率評估: {"高效率" if current_duration == 0 else "正常效率" if current_duration <= 2 else "效率偏低"}"""
        
        except Exception as e:
            if any(word in query_lower for word in ['status', 'health', '狀況', '健康']):
                return """Qubic 網路健康狀況主要通過以下指標評估：

- Tick: 網路處理週期，應穩定增長
- Duration: 處理時間，低於 3 秒為佳  
- Epoch: 網路階段，轉換應順暢
- 活躍地址數: 反映網路採用度

當前網路運行狀況可通過 Qubic 官方工具監控。"""
        
        if any(word in query_lower for word in ['what', 'definition', '是什麼', '什麼是']):
            return """Qubic 是一個創新的去中心化計算和金融平台，採用基於法定人數的電腦（QBC）系統。主要特色包括：

1. 有用工作量證明（UPoW）- 結合安全性和實用性的共識機制
2. Qubic Units (QUs) - 生態系統的原生代幣
3. 智能合約支援和量子計算抗性
4. 完整的開發工具生態系統

更多詳細信息請參考: https://docs.qubic.org/"""
        
        else:
            return """Qubic 是基於法定人數電腦（QBC）系統的去中心化平台，使用有用工作量證明（UPoW）共識機制。

關鍵特色：
- 量子計算抗性
- 智能合約支援  
- 高效能計算
- 完整開發生態

詳細信息: https://docs.qubic.org/"""
    
    def _get_fallback_english_response(self, query: str) -> str:
        """英文備用回應系統"""
        query_lower = query.lower()
        
        # 嘗試獲取當前網路數據
        try:
            from backend.app.qubic_client import QubicNetworkClient
            client = QubicNetworkClient()
            tick_info = client.get_tick_info()
            health = client.get_network_health()
            
            current_tick = tick_info.get('tick', 0)
            current_duration = tick_info.get('duration', 0) 
            current_epoch = tick_info.get('epoch', 0)
            health_status = health.get('overall', 'Unknown')
            
            if any(word in query_lower for word in ['status', 'health', 'analysis', 'analyze', 'network', 'performance']):
                return f"""📊 **Qubic Network Real-time Analysis**

🔹 **Current Metrics**:
- Tick: {current_tick:,} (continuously growing)
- Duration: {current_duration} seconds ({"Excellent" if current_duration == 0 else "Normal" if current_duration <= 2 else "Attention needed"})
- Epoch: {current_epoch}
- Overall Health: {health_status}

🔹 **Status Assessment**:
{"✅ Network running smoothly with excellent processing speed" if current_duration == 0 else "⚠️ Network under moderate load, monitoring" if current_duration <= 2 else "🔴 High network load, requires close monitoring"}

🔹 **Recommendations**:
- Continue monitoring Duration metric changes
- Watch for Tick growth trends
- Observe Epoch transition stability

💡 Data sourced from real-time Qubic network status."""
        
        except Exception:
            if any(word in query_lower for word in ['status', 'health', 'analysis', 'network']):
                return """Qubic network health is evaluated through key indicators:

- Tick: Network processing cycles, should grow steadily
- Duration: Processing time, optimal under 3 seconds  
- Epoch: Network phases, transitions should be smooth
- Active addresses: Reflects network adoption

Current network status can be monitored through official Qubic tools."""
        
        if any(word in query_lower for word in ['what', 'definition', 'about']):
            return """Qubic is an innovative decentralized computing and financial platform based on Quorum-based Computer (QBC) system. Key features include:

1. Useful Proof of Work (UPoW) - consensus mechanism combining security and utility
2. Qubic Units (QUs) - native ecosystem token
3. Smart contract support and quantum computing resistance
4. Complete development toolchain ecosystem

For more information, visit: https://docs.qubic.org/"""
        
        else:
            return """Qubic is a decentralized platform based on Quorum-based Computer (QBC) system using Useful Proof of Work (UPoW) consensus.

Key Features:
- Quantum computing resistance
- Smart contract support  
- Decentralized computing
- Qubic Units (QUs) token economy

Learn more at: https://docs.qubic.org/"""
    
    def analyze_qubic_data(self, data: Dict[str, Any], language: str = "zh-tw") -> Dict[str, Any]:
        """
        分析 Qubic 網路數據 - 使用優化的推理引擎
        
        Args:
            data: Qubic 網路數據
            language: 回應語言 ("zh-tw" 或 "en")
            
        Returns:
            分析結果
        """
        try:
            # 構建優化的分析提示
            prompt = self._build_analysis_prompt(data)
            
            # 使用優化的 generate_response 方法，包含所有改進
            analysis = self.generate_response(
                prompt, 
                max_length=300,
                enhance_with_qubic=True,
                language=language
            )
            
            # 解析和結構化結果
            result = self._parse_analysis_result(analysis, data)
            
            # 確保成功標記
            result["success"] = True
            
            logger.info(f"Qubic 數據分析完成，語言: {language}")
            return result
            
        except Exception as e:
            logger.error(f"數據分析失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": "無法完成數據分析",
                "insights": [],
                "recommendations": [],
                "timestamp": int(time.time())
            }
    
    def _build_analysis_prompt(self, data: Dict[str, Any]) -> str:
        """
        建立分析提示 - 使用 DeepSeek-R1 最佳實踐和 Qubic 知識增強
        
        Args:
            data: Qubic 數據
            
        Returns:
            格式化的分析提示
        """
        tick = data.get('tick', 0)
        duration = data.get('duration', 0)
        epoch = data.get('epoch', 0)
        health = data.get('health', {})
        price = data.get('price', 0)
        active_addresses = data.get('activeAddresses', 0)
        
        # 使用 Qubic 知識庫獲取分析上下文
        context = self.qubic_kb.get_relevant_context("network analysis", data)
        
        # 應用 DeepSeek-R1 最佳實踐：<think> 模式 + 結構化分析
        prompt = f"""<think>
我需要對當前 Qubic 網路數據進行專業綜合分析。
當前關鍵指標：
- Tick: {tick:,} (網路處理週期)
- Duration: {duration} 秒 (處理時間)
- Epoch: {epoch} (當前階段)
- 健康狀況: {health.get('overall', '未知')}
- 活躍地址: {active_addresses:,}

分析重點：
1. 基於這些具體數值評估網路性能
2. 對比 Qubic 網路的正常運行標準
3. 識別任何異常或優化機會
4. 提供實用的監控建議

我需要提供專業、針對性的分析，避免通用模板。
</think>

作為專業的 Qubic 區塊鏈網路分析師，基於當前網路數據進行綜合評估：

{context}

當前網路指標：
- Tick: {tick:,}
- Duration: {duration} 秒
- Epoch: {epoch}
- 健康狀況: {health.get('overall', '未知')}
- 價格: ${price:.9f}
- 活躍地址: {active_addresses:,}

請提供專業的 Qubic 網路分析，包含：
1. 當前性能評估（基於 Duration 和 Tick 指標）
2. 網路健康狀況分析
3. 關鍵洞察和發現
4. 具體監控建議

專業分析："""

        return prompt
    
    def _parse_analysis_result(self, analysis: str, original_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析分析結果
        
        Args:
            analysis: AI 生成的分析文本
            original_data: 原始數據
            
        Returns:
            結構化的分析結果
        """
        # 提取關鍵洞察
        insights = self._extract_insights(analysis)
        
        # 提取建議
        recommendations = self._extract_recommendations(analysis)
        
        # 計算信心度
        confidence = self._calculate_confidence(original_data)
        
        return {
            "success": True,
            "analysis": analysis,
            "insights": insights,
            "recommendations": recommendations,
            "confidence": confidence,
            "data_quality": "good" if original_data.get('tick', 0) > 0 else "poor",
            "timestamp": int(time.time())
        }
    
    def _extract_insights(self, analysis: str) -> List[str]:
        """
        從分析中提取關鍵洞察
        
        Args:
            analysis: 分析文本
            
        Returns:
            洞察列表
        """
        insights = []
        
        # 簡單的關鍵詞提取邏輯
        keywords = [
            "網路正常", "性能良好", "運行穩定", "健康狀況",
            "異常", "延遲", "問題", "建議", "優化"
        ]
        
        lines = analysis.split('\n')
        for line in lines:
            line = line.strip()
            if line and any(keyword in line for keyword in keywords):
                insights.append(line)
        
        return insights[:3]  # 最多返回 3 個洞察
    
    def _extract_recommendations(self, analysis: str) -> List[str]:
        """
        從分析中提取建議
        
        Args:
            analysis: 分析文本
            
        Returns:
            建議列表
        """
        recommendations = []
        
        # 尋找建議相關的內容
        lines = analysis.split('\n')
        in_recommendations = False
        
        for line in lines:
            line = line.strip()
            if '建議' in line or '行動' in line or 'recommendations' in line.lower():
                in_recommendations = True
                continue
            
            if in_recommendations and line:
                if line.startswith(('-', '•', '1.', '2.', '3.')):
                    recommendations.append(line)
                elif not line[0].isdigit() and len(recommendations) > 0:
                    break
        
        return recommendations[:3]  # 最多返回 3 個建議
    
    def _calculate_confidence(self, data: Dict[str, Any]) -> float:
        """
        計算分析信心度
        
        Args:
            data: 數據品質
            
        Returns:
            信心度 (0.0-1.0)
        """
        confidence = 0.5  # 基礎信心度
        
        # 根據數據品質調整
        if data.get('tick', 0) > 0:
            confidence += 0.2
        
        if 'health' in data and data['health'].get('overall') != '異常':
            confidence += 0.2
        
        if data.get('duration', 0) > 0:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def get_status(self) -> Dict[str, Any]:
        """
        獲取推理引擎狀態
        
        Returns:
            狀態資訊
        """
        return {
            "model_loaded": self.model_loaded,
            "model_path": str(self.model_path),
            "device": self.device,
            "ready": self.model_loaded,
            "last_check": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def _get_emergency_fallback_response(self, language: str = "zh-tw") -> str:
        """
        緊急備用回應（當模型無法加載時使用）
        """
        if language == "en":
            return """**System Notice:**
The AI analysis model is currently unavailable. Please try again later or contact system administrator.

**Current Status:** Model loading in progress
**Recommended Action:** Wait a few moments and retry your request"""
        else:
            return """**系統通知：**
AI 分析模型目前無法使用，請稍後重試或聯繫系統管理員。

**目前狀況：** 模型載入中
**建議動作：** 請稍等片刻後重新嘗試"""

# 全域推理引擎實例
_inference_engine = None

def get_inference_engine() -> DeepSeekInferenceEngine:
    """
    獲取全域推理引擎實例（單例模式）
    
    Returns:
        推理引擎實例
    """
    global _inference_engine
    if _inference_engine is None:
        _inference_engine = DeepSeekInferenceEngine()
    return _inference_engine
