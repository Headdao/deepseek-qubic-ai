#!/usr/bin/env python3
"""
Multi-Agent Synchronization Monitor
Qubic AI Compute Layer Project

這個腳本監控多智能體協作狀態，確保所有 Agent 保持同步。
"""

import json
import time
import yaml
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any
import logging

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.cursor/shared-state/sync-monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MultiAgentSyncMonitor:
    """多智能體同步監控器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.state_file = self.project_root / ".cursor/shared-state/project-state.json"
        self.config_file = self.project_root / ".cursor/sync-protocols/sync-config.yml"
        self.task_board_file = self.project_root / ".cursor/shared-state/task-board.md"
        
        # 載入配置
        self.config = self.load_config()
        
        # 初始化狀態
        self.last_sync_time = None
        self.file_checksums = {}
        self.sync_stats = {
            'total_syncs': 0,
            'successful_syncs': 0,
            'failed_syncs': 0,
            'conflicts_detected': 0,
            'conflicts_resolved': 0
        }
        
        logger.info("🚀 Multi-Agent Sync Monitor initialized")
    
    def load_config(self) -> Dict:
        """載入同步配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"❌ Failed to load config: {e}")
            return {}
    
    def load_project_state(self) -> Dict:
        """載入項目狀態"""
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ Failed to load project state: {e}")
            return {}
    
    def save_project_state(self, state: Dict) -> bool:
        """保存項目狀態"""
        try:
            # 更新時間戳
            state['timestamp'] = datetime.now(timezone.utc).isoformat()
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            
            logger.info("💾 Project state saved successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save project state: {e}")
            return False
    
    def calculate_file_checksum(self, file_path: Path) -> str:
        """計算檔案校驗碼"""
        if not file_path.exists():
            return ""
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception as e:
            logger.warning(f"⚠️ Failed to calculate checksum for {file_path}: {e}")
            return ""
    
    def detect_file_changes(self) -> List[Dict]:
        """檢測檔案變更"""
        changes = []
        
        # 監控重要檔案
        important_files = [
            self.state_file,
            self.task_board_file,
            self.project_root / ".cursor/shared-state/daily-standup.md",
            self.project_root / "Qubic_AI_Compute_Layer_詳細任務清單.md",
            self.project_root / "開發日誌.md"
        ]
        
        for file_path in important_files:
            if file_path.exists():
                current_checksum = self.calculate_file_checksum(file_path)
                file_str = str(file_path)
                
                if file_str in self.file_checksums:
                    if self.file_checksums[file_str] != current_checksum:
                        changes.append({
                            'file': file_str,
                            'type': 'modified',
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        })
                        logger.info(f"📝 File changed: {file_path.name}")
                else:
                    changes.append({
                        'file': file_str,
                        'type': 'new',
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })
                    logger.info(f"➕ New file detected: {file_path.name}")
                
                self.file_checksums[file_str] = current_checksum
        
        return changes
    
    def check_agent_activity(self, state: Dict) -> Dict:
        """檢查智能體活動狀態"""
        now = datetime.now(timezone.utc)
        agent_status = {}
        
        for agent_name, team_info in state.get('teams', {}).items():
            last_update_str = team_info.get('last_update', '')
            
            try:
                last_update = datetime.fromisoformat(last_update_str.replace('Z', '+00:00'))
                time_diff = (now - last_update).total_seconds() / 60  # 分鐘
                
                if time_diff < 10:
                    status = "active"
                elif time_diff < 30:
                    status = "idle"
                elif time_diff < 60:
                    status = "inactive"
                else:
                    status = "unresponsive"
                
                agent_status[agent_name] = {
                    'status': status,
                    'last_seen': last_update_str,
                    'minutes_since_update': round(time_diff, 1)
                }
                
            except Exception as e:
                logger.warning(f"⚠️ Invalid timestamp for {agent_name}: {e}")
                agent_status[agent_name] = {
                    'status': 'unknown',
                    'last_seen': last_update_str,
                    'minutes_since_update': -1
                }
        
        return agent_status
    
    def detect_conflicts(self, state: Dict) -> List[Dict]:
        """檢測潛在衝突"""
        conflicts = []
        
        # 檢查檔案衝突 (多個 Agent 編輯同一檔案)
        file_usage = {}
        for agent_name, team_info in state.get('teams', {}).items():
            working_files = team_info.get('working_files', [])
            for file_pattern in working_files:
                if file_pattern not in file_usage:
                    file_usage[file_pattern] = []
                file_usage[file_pattern].append(agent_name)
        
        for file_pattern, agents in file_usage.items():
            if len(agents) > 1:
                conflicts.append({
                    'type': 'file_conflict',
                    'description': f"Multiple agents working on {file_pattern}",
                    'agents': agents,
                    'severity': 'medium',
                    'detected_at': datetime.now(timezone.utc).isoformat()
                })
        
        # 檢查任務衝突 (依賴關係違反)
        dependencies = state.get('dependencies', [])
        for dep in dependencies:
            from_agent = dep['from']
            to_agent = dep['to']
            
            from_status = state.get('teams', {}).get(from_agent, {}).get('status', 'unknown')
            to_status = state.get('teams', {}).get(to_agent, {}).get('status', 'unknown')
            
            if from_status == 'blocked' and to_status == 'active':
                conflicts.append({
                    'type': 'dependency_conflict',
                    'description': f"Dependency violation: {from_agent} blocked but {to_agent} active",
                    'from_agent': from_agent,
                    'to_agent': to_agent,
                    'severity': 'high',
                    'detected_at': datetime.now(timezone.utc).isoformat()
                })
        
        return conflicts
    
    def resolve_minor_conflicts(self, conflicts: List[Dict]) -> List[Dict]:
        """自動解決輕微衝突"""
        unresolved = []
        
        for conflict in conflicts:
            if conflict['severity'] == 'low':
                logger.info(f"🔧 Auto-resolving conflict: {conflict['description']}")
                self.sync_stats['conflicts_resolved'] += 1
            else:
                unresolved.append(conflict)
                logger.warning(f"⚠️ Conflict requires manual resolution: {conflict['description']}")
        
        return unresolved
    
    def update_sync_metrics(self, state: Dict, conflicts: List[Dict]) -> None:
        """更新同步指標"""
        self.sync_stats['total_syncs'] += 1
        
        if conflicts:
            self.sync_stats['failed_syncs'] += 1
            self.sync_stats['conflicts_detected'] += len(conflicts)
        else:
            self.sync_stats['successful_syncs'] += 1
        
        # 更新狀態中的指標
        if 'metrics' not in state:
            state['metrics'] = {}
        
        state['metrics'].update({
            'sync_success_rate': round(
                (self.sync_stats['successful_syncs'] / self.sync_stats['total_syncs']) * 100, 2
            ) if self.sync_stats['total_syncs'] > 0 else 0,
            'conflicts_per_sync': round(
                self.sync_stats['conflicts_detected'] / self.sync_stats['total_syncs'], 2
            ) if self.sync_stats['total_syncs'] > 0 else 0,
            'last_sync_time': datetime.now(timezone.utc).isoformat()
        })
    
    def generate_sync_report(self, agent_status: Dict, conflicts: List[Dict]) -> str:
        """生成同步報告"""
        report = []
        report.append("=" * 60)
        report.append(f"🤖 Multi-Agent Sync Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)
        
        # Agent 狀態
        report.append("\n📊 Agent Status:")
        for agent, status in agent_status.items():
            emoji = {
                'active': '🟢',
                'idle': '🟡', 
                'inactive': '🟠',
                'unresponsive': '🔴',
                'unknown': '⚪'
            }.get(status['status'], '⚪')
            
            report.append(f"  {emoji} {agent}: {status['status']} "
                         f"({status['minutes_since_update']}min ago)")
        
        # 衝突狀態
        if conflicts:
            report.append(f"\n⚠️ Active Conflicts ({len(conflicts)}):")
            for i, conflict in enumerate(conflicts, 1):
                report.append(f"  {i}. {conflict['type']}: {conflict['description']}")
        else:
            report.append("\n✅ No conflicts detected")
        
        # 同步統計
        report.append(f"\n📈 Sync Statistics:")
        report.append(f"  Total syncs: {self.sync_stats['total_syncs']}")
        report.append(f"  Success rate: {self.sync_stats['successful_syncs']}/{self.sync_stats['total_syncs']}")
        report.append(f"  Conflicts resolved: {self.sync_stats['conflicts_resolved']}")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def run_sync_cycle(self) -> None:
        """執行一次同步週期"""
        try:
            logger.info("🔄 Starting sync cycle...")
            
            # 載入當前狀態
            state = self.load_project_state()
            if not state:
                logger.error("❌ Cannot load project state, skipping sync cycle")
                return
            
            # 檢測檔案變更
            changes = self.detect_file_changes()
            if changes:
                logger.info(f"📝 Detected {len(changes)} file changes")
            
            # 檢查 Agent 活動
            agent_status = self.check_agent_activity(state)
            
            # 檢測衝突
            conflicts = self.detect_conflicts(state)
            
            # 嘗試自動解決輕微衝突
            if conflicts:
                conflicts = self.resolve_minor_conflicts(conflicts)
            
            # 更新狀態
            state['conflicts'] = conflicts
            state['last_sync'] = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'agent_status': agent_status,
                'changes_detected': len(changes),
                'conflicts_detected': len(conflicts)
            }
            
            # 更新指標
            self.update_sync_metrics(state, conflicts)
            
            # 保存狀態
            self.save_project_state(state)
            
            # 生成報告
            report = self.generate_sync_report(agent_status, conflicts)
            logger.info(f"\n{report}")
            
            # 如果有未解決的衝突，發送警告
            if conflicts:
                logger.warning(f"⚠️ {len(conflicts)} unresolved conflicts require attention!")
            
            self.last_sync_time = datetime.now(timezone.utc)
            logger.info("✅ Sync cycle completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Sync cycle failed: {e}")
            self.sync_stats['failed_syncs'] += 1
    
    def monitor(self, sync_interval: int = 300) -> None:
        """開始監控 (預設每5分鐘同步一次)"""
        logger.info(f"🎯 Starting continuous monitoring (sync every {sync_interval}s)")
        
        try:
            while True:
                self.run_sync_cycle()
                time.sleep(sync_interval)
                
        except KeyboardInterrupt:
            logger.info("🛑 Monitoring stopped by user")
        except Exception as e:
            logger.error(f"❌ Monitoring error: {e}")

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Multi-Agent Sync Monitor")
    parser.add_argument('--interval', type=int, default=300, 
                       help='Sync interval in seconds (default: 300)')
    parser.add_argument('--once', action='store_true',
                       help='Run sync once and exit')
    
    args = parser.parse_args()
    
    monitor = MultiAgentSyncMonitor()
    
    if args.once:
        monitor.run_sync_cycle()
    else:
        monitor.monitor(args.interval)

if __name__ == "__main__":
    main()
