#!/usr/bin/env python3
"""
Qubic 知識庫和上下文增強系統
基於官方文檔提供精確的 Qubic 知識
"""

import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

class QubicKnowledgeBase:
    """Qubic 知識庫"""
    
    def __init__(self):
        """初始化知識庫"""
        self.knowledge_base = self._build_knowledge_base()
        self.contexts = self._build_contexts()
        
    def _build_knowledge_base(self) -> Dict[str, Any]:
        """建立 Qubic 知識庫 - 基於官方文檔"""
        return {
            "basic_info": {
                "definition": "Qubic 是一個創新平台，旨在通過其基於法定人數的電腦（QBC）系統來革命化去中心化計算和金融世界。",
                "key_features": [
                    "去中心化計算平台",
                    "基於法定人數的電腦（Quorum-based Computer, QBC）系統",
                    "智能合約支援",
                    "有用工作量證明（Useful Proof of Work, UPoW）",
                    "量子計算抗性"
                ],
                "website": "https://docs.qubic.org/"
            },
            
            "tokenomics": {
                "native_token": "Qubic Units (QUs)",
                "purpose": "生態系統中的原生代幣",
                "economic_model": "基於有用工作量證明的通縮模型",
                "utility": [
                    "交易費用支付",
                    "智能合約執行",
                    "網路安全維護",
                    "計算資源購買"
                ]
            },
            
            "technology": {
                "consensus": {
                    "name": "Useful Proof of Work (UPoW)",
                    "description": "結合了安全性和實用性的共識機制",
                    "benefits": [
                        "提供網路安全",
                        "產生有用的計算結果",
                        "高效能處理",
                        "量子抗性"
                    ]
                },
                "quorum_system": {
                    "name": "Quorum-based Computer (QBC)",
                    "description": "基於法定人數的分散式計算系統",
                    "components": [
                        "Computors（計算節點）",
                        "Quorum（法定人數機制）",
                        "Smart Contracts（智能合約）"
                    ]
                }
            },
            
            "development": {
                "tools": [
                    "Qubic Dev Kit - 本地測試網和智能合約部署",
                    "Qubic CLI - 命令行介面",
                    "Qubic RPC - 遠程過程調用介面",
                    "Qubic Node - 完整節點實現"
                ],
                "libraries": [
                    "Java Libraries",
                    "TypeScript Libraries", 
                    "Go Libraries",
                    "HTTP Libraries",
                    "C# Libraries"
                ],
                "testnet": "提供測試網資源和水龍頭",
                "integration": "錢包整合指南和資源"
            },
            
            "ecosystem": {
                "aigarth": {
                    "description": "在 Qubic 網路上開發的項目",
                    "purpose": "展示 Qubic 平台能力"
                },
                "programs": [
                    "Grants Program - 資助高品質智能合約開發",
                    "Bug Bounty Program - 安全漏洞回報獎勵"
                ]
            },
            
            "network_metrics": {
                "key_indicators": [
                    "Tick - 網路區塊/週期",
                    "Epoch - 時代/階段", 
                    "Duration - 處理時間",
                    "Active Addresses - 活躍地址數",
                    "Market Cap - 市值",
                    "Price - 代幣價格"
                ],
                "health_factors": [
                    "網路正常運行時間",
                    "交易處理速度",
                    "節點參與度",
                    "計算效率"
                ]
            }
        }
    
    def _build_contexts(self) -> Dict[str, str]:
        """建立上下文模板"""
        return {
            "general": """Qubic 是一個創新的去中心化計算和金融平台，採用基於法定人數的電腦（QBC）系統。
主要特色：
- 使用有用工作量證明（UPoW）共識機制
- 原生代幣為 Qubic Units (QUs)
- 支援智能合約和量子計算抗性
- 提供完整的開發工具生態系統

關鍵指標：
- Tick: 網路處理週期
- Epoch: 網路時代
- Duration: 處理時間
- 健康狀況基於這些指標評估""",

            "technology": """Qubic 技術架構：

1. 共識機制：有用工作量證明（UPoW）
   - 結合安全性和實用性
   - 產生有用的計算結果
   - 提供量子抗性

2. QBC 系統（基於法定人數的電腦）
   - Computors 作為計算節點
   - Quorum 法定人數機制
   - 分散式智能合約執行

3. 網路指標
   - Tick 表示處理週期
   - Duration 影響網路效能
   - Epoch 代表網路階段""",

            "development": """Qubic 開發生態系統：

開發工具：
- Qubic Dev Kit: 本地測試環境
- Qubic CLI: 命令行工具
- Qubic RPC: API 介面
- Qubic Node: 完整節點

支援語言庫：
- Java, TypeScript, Go, C#, HTTP

資源：
- 測試網和水龍頭
- 錢包整合指南
- 官方文檔和教程""",

            "analysis": """Qubic 網路分析指南：

健康指標：
- Tick 數值應穩定增長
- Duration 低於 3 秒為佳
- Epoch 轉換應順暢
- 活躍地址數反映採用度

性能評估：
- Duration = 0-1 秒：優秀
- Duration = 1-2 秒：良好  
- Duration = 2-3 秒：一般
- Duration > 3 秒：需要關注

網路狀態：
- 健康：所有指標正常
- 一般：部分指標異常
- 異常：多項指標有問題"""
        }
    
    def get_relevant_context(self, query: str, data: Optional[Dict] = None) -> str:
        """根據查詢獲取相關上下文"""
        query_lower = query.lower()
        
        # 分析查詢類型
        if any(word in query_lower for word in ['what', 'definition', '是什麼', '什麼是']):
            context_type = "general"
        elif any(word in query_lower for word in ['technology', 'consensus', 'upow', 'qbc', '技術', '共識']):
            context_type = "technology"
        elif any(word in query_lower for word in ['develop', 'api', 'cli', 'sdk', '開發', '工具']):
            context_type = "development"
        elif any(word in query_lower for word in ['analysis', 'health', 'status', '分析', '狀況', '健康']):
            context_type = "analysis"
        else:
            context_type = "general"
        
        base_context = self.contexts[context_type]
        
        # 如果有當前網路數據，添加即時信息
        if data:
            current_info = f"""

當前網路狀態：
- Tick: {data.get('tick', 0):,}
- Duration: {data.get('duration', 0)} 秒
- Epoch: {data.get('epoch', 0)}
- 健康狀況: {data.get('health', {}).get('overall', '未知')}
- 活躍地址: {data.get('activeAddresses', 0):,}
- 價格: ${data.get('price', 0):.9f}"""
            
            base_context += current_info
        
        return base_context
    
    def get_qubic_facts(self, topic: Optional[str] = None) -> List[str]:
        """獲取 Qubic 相關事實"""
        all_facts = [
            "Qubic 使用基於法定人數的電腦（QBC）系統進行去中心化計算",
            "有用工作量證明（UPoW）是 Qubic 的共識機制，結合安全性和實用性",
            "Qubic Units (QUs) 是 Qubic 生態系統的原生代幣",
            "Qubic 提供量子計算抗性，為未來技術做準備",
            "Tick 是 Qubic 網路的處理週期，反映網路活動",
            "Duration 測量 Tick 處理時間，影響網路性能",
            "Epoch 代表 Qubic 網路的時代或階段",
            "Computors 是 Qubic 網路中的計算節點",
            "Qubic 支援智能合約執行和去中心化應用開發",
            "Aigarth 是在 Qubic 網路上開發的重要項目"
        ]
        
        if topic:
            topic_lower = topic.lower()
            relevant_facts = [fact for fact in all_facts 
                            if any(keyword in fact.lower() for keyword in topic_lower.split())]
            return relevant_facts[:5] if relevant_facts else all_facts[:3]
        
        return all_facts[:5]
    
    def enhance_query_with_context(self, query: str, network_data: Optional[Dict] = None, language: str = "zh-tw") -> str:
        """使用 Qubic 知識增強查詢"""
        context = self.get_relevant_context(query, network_data)
        facts = self.get_qubic_facts()
        
        # 根據語言選擇提示詞模板
        if language == "en":
            enhanced_prompt = f"""You are a professional Qubic blockchain network analyst. Answer ONLY in English.

Qubic Knowledge:
{context}

Question: {query}

Analysis:"""
        else:  # Default to Traditional Chinese - 完全按照 AI_API_Usage_Guide.md 最佳實踐
            enhanced_prompt = f"""<think>
我需要仔細分析用戶的具體問題："{query}"
- 如果問題是關於網路狀況，重點分析當前運行指標
- 如果問題是關於健康評估，重點分析系統穩定性和風險
- 如果問題是關於 Epoch 進度，重點分析進度預測和時間估算
我需要針對具體問題提供專業且有差異化的回答。
</think>

作為專業的 Qubic 區塊鏈分析師，當前網路狀態：
{context}
問題：{query}
針對此問題的專業分析："""
        
        return enhanced_prompt
    
    def validate_response(self, response: str) -> Dict[str, Any]:
        """驗證回應的 Qubic 知識準確性 - 重新設計更合理的評分系統"""
        score = 50  # 基礎分數，避免過於嚴苛
        feedback = []
        
        # 檢查回應長度和結構合理性
        if len(response) >= 20:
            score += 10
            feedback.append("回應長度合理")
        
        # 檢查是否包含數值分析（更實用的指標）
        import re
        numbers = re.findall(r'\d+', response)
        if numbers:
            score += 15
            feedback.append("包含數值分析")
        
        # 檢查關鍵 Qubic 概念（放寬要求）
        key_concepts = [
            'tick', 'epoch', 'duration', 'qubic', '網路', 'network', 
            '健康', 'health', '狀況', 'status', '分析', 'analysis'
        ]
        
        found_concepts = [concept for concept in key_concepts if concept.lower() in response.lower()]
        if found_concepts:
            score += min(len(found_concepts) * 5, 25)  # 最多加 25 分
            feedback.append(f"包含相關概念: {len(found_concepts)} 個")
        
        # 檢查是否有具體建議或結論
        conclusion_indicators = [
            '建議', '總結', '結論', 'recommend', 'conclusion', '分析', '評估'
        ]
        
        found_conclusions = [ind for ind in conclusion_indicators if ind.lower() in response.lower()]
        if found_conclusions:
            score += 10
            feedback.append("提供了結論或建議")
        
        # 檢查明顯錯誤（保持原有邏輯）
        error_indicators = [
            'netcat', 'netnat', '移動設備', 'mobile device',
            '比特幣', 'bitcoin', '以太坊', 'ethereum', 'chatgpt', 'openai'
        ]
        
        found_errors = [error for error in error_indicators if error.lower() in response.lower()]
        if found_errors:
            score -= len(found_errors) * 15  # 減少懲罰
            feedback.append(f"發現錯誤信息: {', '.join(found_errors)}")
        
        # 確保分數在合理範圍
        final_score = max(30, min(100, score))  # 最低 30 分，避免過低
        
        return {
            "accuracy_score": final_score,
            "feedback": feedback,
            "quality": "good" if final_score >= 70 else "moderate" if final_score >= 50 else "poor"
        }

# 全域知識庫實例
_qubic_kb = None

def get_qubic_knowledge_base() -> QubicKnowledgeBase:
    """獲取全域 Qubic 知識庫實例"""
    global _qubic_kb
    if _qubic_kb is None:
        _qubic_kb = QubicKnowledgeBase()
    return _qubic_kb
