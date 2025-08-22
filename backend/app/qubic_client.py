"""
Qubic 網路客戶端
整合 QubiPy 提供數據服務
"""

import sys
import os
from typing import Dict, Any, Optional

try:
    from qubipy.rpc import rpc_client
    from qubipy.exceptions import QubiPy_Exceptions
except ImportError as e:
    print(f"❌ 無法匯入 QubiPy: {e}")
    print("請確保已安裝 QubiPy: pip install -e /path/to/QubiPy-main")
    raise

class QubicNetworkClient:
    """Qubic 網路客戶端類別"""
    
    def __init__(self, rpc_url: str = None, timeout: int = 10):
        """
        初始化 Qubic 網路客戶端
        
        Args:
            rpc_url: RPC 伺服器 URL
            timeout: 請求超時時間（秒）
        """
        try:
            self.rpc = rpc_client.QubiPy_RPC(rpc_url=rpc_url, timeout=timeout) if rpc_url else rpc_client.QubiPy_RPC(timeout=timeout)
            self.last_tick_info = None
        except Exception as e:
            print(f"❌ QubiPy RPC 客戶端初始化失敗: {e}")
            raise
    
    def get_tick_info(self) -> Dict[str, Any]:
        """
        獲取當前 tick 資訊
        
        Returns:
            包含 tick, epoch, duration, initialTick 的字典
        """
        try:
            tick_info = self.rpc.get_tick_info()
            self.last_tick_info = tick_info
            return tick_info
        except QubiPy_Exceptions as e:
            print(f"❌ 獲取 tick 資訊失敗: {e}")
            return self._get_fallback_data()
        except Exception as e:
            print(f"❌ 未知錯誤: {e}")
            return self._get_fallback_data()
    
    def get_network_stats(self) -> Dict[str, Any]:
        """
        獲取網路統計數據
        
        Returns:
            包含活躍地址、市值等統計資訊的字典
        """
        try:
            stats = self.rpc.get_latest_stats()
            return {
                "activeAddresses": int(stats.get("activeAddresses", 0)),
                "marketCap": int(stats.get("marketCap", 0)),
                "burnedQus": int(stats.get("burnedQus", 0)),
                "epochTickQuality": float(stats.get("epochTickQuality", 0)),
                "circulatingSupply": int(stats.get("circulatingSupply", 0)),
                "price": float(stats.get("price", 0))
            }
        except Exception as e:
            print(f"❌ 獲取網路統計失敗: {e}")
            return {
                "activeAddresses": 0,
                "marketCap": 0,
                "burnedQus": 0,
                "epochTickQuality": 0,
                "circulatingSupply": 0,
                "price": 0,
                "error": "無法獲取統計數據"
            }
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """
        當 API 請求失敗時提供備用數據
        
        Returns:
            備用的 tick 資訊
        """
        return {
            "tick": 0,
            "epoch": 0,
            "duration": 0,
            "initialTick": 0,
            "error": "無法獲取即時數據",
            "status": "offline"
        }
    
    def get_network_health(self) -> Dict[str, str]:
        """
        分析網路健康狀況
        
        Returns:
            網路健康狀況分析
        """
        if not self.last_tick_info:
            self.get_tick_info()
        
        if not self.last_tick_info or "error" in self.last_tick_info:
            return {
                "overall": "離線",
                "tick_status": "無數據",
                "epoch_status": "無數據", 
                "duration_status": "無數據"
            }
        
        tick = self.last_tick_info.get('tick', 0)
        duration = self.last_tick_info.get('duration', 0)
        
        # 分析 tick 狀態
        tick_status = "正常" if tick > 0 else "異常"
        
        # 分析 duration 狀態
        if duration == 0:
            duration_status = "極快"
        elif duration == 1:
            duration_status = "快速"
        elif duration == 2:
            duration_status = "正常"
        elif duration <= 3:
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
            "tick_status": tick_status,
            "epoch_status": "正常",
            "duration_status": duration_status
        }
