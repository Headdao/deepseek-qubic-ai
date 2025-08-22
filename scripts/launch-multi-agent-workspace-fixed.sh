#!/bin/bash

# Multi-Agent Workspace Launch Script (Fixed for macOS)
# Qubic AI Compute Layer Project

echo "🚀 Launching Multi-Agent Collaborative Workspace for Qubic AI Compute Layer"
echo "=================================================================="

# 設置顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 項目根目錄
PROJECT_ROOT="/Users/apple/qubic/qdashboard"

# macOS Cursor 路徑
CURSOR_APP="/Applications/Cursor.app"
CURSOR_CLI="$CURSOR_APP/Contents/Resources/app/bin/cursor"

# 檢查 Cursor 是否安裝
if [ ! -d "$CURSOR_APP" ]; then
    echo -e "${RED}❌ Cursor.app not found in Applications folder.${NC}"
    echo -e "${YELLOW}Please install Cursor from: https://cursor.sh${NC}"
    exit 1
fi

# 檢查 CLI 工具
if [ ! -f "$CURSOR_CLI" ]; then
    echo -e "${YELLOW}⚠️ Cursor CLI not found at expected location.${NC}"
    echo -e "${YELLOW}Trying alternative method...${NC}"
    # 備用方法：直接打開應用程式
    CURSOR_CMD="open -a Cursor"
else
    CURSOR_CMD="$CURSOR_CLI"
fi

echo -e "${GREEN}✅ Cursor found. Preparing multi-agent workspace...${NC}"

# 檢查項目目錄
if [ ! -d "$PROJECT_ROOT" ]; then
    echo -e "${RED}❌ Project directory not found: $PROJECT_ROOT${NC}"
    exit 1
fi

cd "$PROJECT_ROOT"

# 建立工作區配置文件目錄
echo -e "${YELLOW}📁 Creating workspace configurations...${NC}"
mkdir -p .cursor/workspaces

# 檢查必要的目錄和檔案
if [ ! -f ".cursor/shared-state/project-state.json" ]; then
    echo -e "${YELLOW}⚠️ Project state file not found. Creating initial state...${NC}"
    python3 -c "
import json
from datetime import datetime, timezone

state = {
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'project_info': {
        'name': 'Qubic AI Compute Layer',
        'version': '1.0.0',
        'current_phase': 'Phase1',
        'current_week': 1
    },
    'teams': {},
    'active_agents': ['central_coordinator', 'project_manager', 'development_team', 'testing_team', 'documentation_team', 'devops_team']
}

with open('.cursor/shared-state/project-state.json', 'w', encoding='utf-8') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)

print('✅ Project state initialized')
"
fi

# 啟動函數 (修正版)
launch_agent_workspace() {
    local agent_name=$1
    local window_title=$2
    local color=$3
    local focus_files=$4
    
    echo -e "${color}🚀 Launching $window_title...${NC}"
    
    # 根據是否有 CLI 工具選擇不同的啟動方式
    if [ -f "$CURSOR_CLI" ]; then
        # 使用 CLI 工具
        "$CURSOR_CLI" --new-window "$PROJECT_ROOT" &
    else
        # 使用 open 命令
        open -n -a "Cursor" --args "$PROJECT_ROOT" &
    fi
    
    # 等待一下讓窗口載入
    sleep 3
    
    echo -e "${color}✅ $window_title workspace ready${NC}"
}

# 啟動多智能體工作區
echo -e "${BLUE}🌟 Starting Multi-Agent Workspaces...${NC}"
echo ""

echo -e "${PURPLE}1/6${NC} Central Coordinator (總協調者)"
launch_agent_workspace "central_coordinator" "Central Coordinator" "$PURPLE" "*.md,.cursor/**"

echo -e "${BLUE}2/6${NC} Project Manager (專案經理)"
launch_agent_workspace "project_manager" "Project Manager" "$BLUE" "*任務清單*.md,*開發計畫*.md"

echo -e "${GREEN}3/6${NC} Development Team (開發團隊)"
launch_agent_workspace "development_team" "Development Team" "$GREEN" "*.py,*.js,backend/**,frontend/**"

echo -e "${YELLOW}4/6${NC} Testing Team (測試團隊)"
launch_agent_workspace "testing_team" "Testing Team" "$YELLOW" "tests/**,*test*.py"

echo -e "${CYAN}5/6${NC} Documentation Team (文檔團隊)"
launch_agent_workspace "documentation_team" "Documentation Team" "$CYAN" "docs/**,*.md"

echo -e "${RED}6/6${NC} DevOps Team (運維團隊)"
launch_agent_workspace "devops_team" "DevOps Team" "$RED" "docker/**,.github/**,*.yml"

echo ""
echo -e "${GREEN}🎉 All Multi-Agent Workspaces Launched Successfully!${NC}"
echo ""
echo "=================================================================="
echo -e "${BLUE}📋 Next Steps:${NC}"
echo ""
echo -e "1. ${YELLOW}在每個 Cursor 窗口中，點擊右下角的 AI 按鈕${NC}"
echo -e "2. ${YELLOW}使用以下 Prompt Templates 來設置對應的 Agent 角色：${NC}"
echo ""
echo -e "${PURPLE}🎯 Central Coordinator Prompt:${NC}"
echo -e "${CYAN}你是 Qubic AI Compute Layer 項目的中央協調者。負責總體協調、衝突解決和全局決策。當前正在 Phase 1 Week 1，請開始協調團隊工作，監控 .cursor/shared-state/ 中的狀態檔案。${NC}"
echo ""
echo -e "${BLUE}📊 Project Manager Prompt:${NC}"
echo -e "${CYAN}你是專案經理，負責追蹤進度、管理里程碑。請基於 Qubic_AI_Compute_Layer_詳細任務清單.md 追蹤 Week 1-2 的任務進度，更新 .cursor/shared-state/task-board.md。${NC}"
echo ""
echo -e "${GREEN}💻 Development Team Prompt:${NC}"
echo -e "${CYAN}你是開發團隊領導，負責 GCP 設置、DeepSeek 模型準備和程式碼開發。當前任務：環境設置與模型部署 (Week 1-2)。${NC}"
echo ""
echo -e "${YELLOW}🧪 Testing Team Prompt:${NC}"
echo -e "${CYAN}你是測試團隊負責人，負責測試規劃、框架選型和品質保證。目標：建立 >85% 測試覆蓋率，支援開發團隊的測試需求。${NC}"
echo ""
echo -e "${CYAN}📚 Documentation Team Prompt:${NC}"
echo -e "${CYAN}你是文檔團隊負責人，負責技術文檔撰寫和維護。請使用繁體中文，確保文檔與開發同步，維護項目文檔完整性。${NC}"
echo ""
echo -e "${RED}🔧 DevOps Team Prompt:${NC}"
echo -e "${CYAN}你是 DevOps 團隊負責人，負責 GCP 基礎設施、Docker 環境和 CI/CD 管道。當前重點：建立開發環境和部署流程。${NC}"
echo ""
echo -e "3. ${YELLOW}開始按照任務清單執行 Phase 1 Week 1-2 任務${NC}"
echo -e "4. ${YELLOW}通過 .cursor/shared-state/ 檔案進行團隊同步${NC}"
echo ""
echo -e "${BLUE}📁 重要檔案位置:${NC}"
echo -e "• Task Board: ${CYAN}.cursor/shared-state/task-board.md${NC}"
echo -e "• Project State: ${CYAN}.cursor/shared-state/project-state.json${NC}"
echo -e "• Agent Configs: ${CYAN}.cursor/multi-agent-config/${NC}"
echo -e "• 使用指南: ${CYAN}Multi_Agent_使用指南.md${NC}"
echo ""
echo -e "${GREEN}🤖 現在可以開始多智能體協作開發 Qubic AI Compute Layer!${NC}"
echo "=================================================================="

# 提供手動指令
echo ""
echo -e "${YELLOW}💡 如果自動啟動有問題，您也可以手動操作：${NC}"
echo -e "1. 手動開啟 6 個 Cursor 窗口，都指向這個專案目錄"
echo -e "2. 在每個窗口中設置不同的 AI Agent 角色"
echo -e "3. 讓每個 Agent 專注於自己的職責範圍"
echo ""
echo -e "${BLUE}📖 詳細說明請參考：Multi_Agent_使用指南.md${NC}"
