#!/bin/bash

# Multi-Agent Workspace Launch Script
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

# 檢查 Cursor 是否安裝
if ! command -v cursor &> /dev/null; then
    echo -e "${RED}❌ Cursor not found. Please install Cursor first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Cursor found. Preparing multi-agent workspace...${NC}"

# 檢查項目目錄
if [ ! -d "$PROJECT_ROOT" ]; then
    echo -e "${RED}❌ Project directory not found: $PROJECT_ROOT${NC}"
    exit 1
fi

cd "$PROJECT_ROOT"

# 建立工作區配置文件
echo -e "${YELLOW}📁 Creating workspace configurations...${NC}"

# Central Coordinator Workspace
cat > .cursor/workspaces/central-coordinator.code-workspace << EOF
{
    "folders": [
        {
            "name": "🎯 Central Coordinator",
            "path": "."
        }
    ],
    "settings": {
        "files.associations": {
            "*.md": "markdown",
            "*.json": "jsonc"
        },
        "editor.wordWrap": "on",
        "markdown.preview.doubleClickToSwitchToEditor": false
    },
    "extensions": {
        "recommendations": [
            "ms-python.python",
            "ms-vscode.vscode-json"
        ]
    }
}
EOF

# Project Manager Workspace  
cat > .cursor/workspaces/project-manager.code-workspace << EOF
{
    "folders": [
        {
            "name": "📊 Project Management",
            "path": "."
        },
        {
            "name": "📋 Task Lists",
            "path": "./workspaces/pm-workspace"
        }
    ],
    "settings": {
        "files.associations": {
            "*.md": "markdown"
        },
        "files.exclude": {
            "src/**": true,
            "backend/**": true,
            "frontend/**": true,
            "tests/**": true,
            "docker/**": true,
            ".github/**": true
        }
    }
}
EOF

# Development Team Workspace
cat > .cursor/workspaces/development-team.code-workspace << EOF
{
    "folders": [
        {
            "name": "💻 Development",
            "path": "."
        },
        {
            "name": "🔧 Dev Workspace", 
            "path": "./workspaces/dev-workspace"
        }
    ],
    "settings": {
        "python.defaultInterpreterPath": "./venv/bin/python",
        "python.linting.enabled": true,
        "python.linting.pylintEnabled": true,
        "files.exclude": {
            "docs/**": true,
            "*.md": true,
            "docker/**": true,
            ".github/**": true
        }
    }
}
EOF

# Testing Team Workspace
cat > .cursor/workspaces/testing-team.code-workspace << EOF
{
    "folders": [
        {
            "name": "🧪 Testing",
            "path": "."
        },
        {
            "name": "🔍 Test Workspace",
            "path": "./workspaces/test-workspace"
        }
    ],
    "settings": {
        "python.testing.pytestEnabled": true,
        "python.testing.unittestEnabled": false,
        "files.exclude": {
            "docs/**": true,
            "*.md": true,
            "docker/**": true,
            ".github/**": true
        }
    }
}
EOF

# Documentation Team Workspace
cat > .cursor/workspaces/documentation-team.code-workspace << EOF
{
    "folders": [
        {
            "name": "📚 Documentation",
            "path": "."
        },
        {
            "name": "📖 Doc Workspace",
            "path": "./workspaces/doc-workspace"
        }
    ],
    "settings": {
        "markdown.preview.doubleClickToSwitchToEditor": false,
        "markdown.preview.markEditorSelection": true,
        "files.associations": {
            "*.md": "markdown"
        },
        "files.exclude": {
            "src/**": true,
            "backend/**": true,
            "frontend/**": true,
            "tests/**": true,
            "docker/**": true,
            ".github/**": true,
            "*.py": true,
            "*.js": true,
            "*.ts": true
        }
    }
}
EOF

# DevOps Team Workspace
cat > .cursor/workspaces/devops-team.code-workspace << EOF
{
    "folders": [
        {
            "name": "🔧 DevOps",
            "path": "."
        },
        {
            "name": "☁️ Ops Workspace",
            "path": "./workspaces/ops-workspace"
        }
    ],
    "settings": {
        "files.associations": {
            "*.yml": "yaml",
            "*.yaml": "yaml",
            "Dockerfile*": "dockerfile"
        },
        "files.exclude": {
            "docs/**": true,
            "*.md": true,
            "src/**": true,
            "backend/**": true,
            "frontend/**": true,
            "tests/**": true
        }
    }
}
EOF

# 建立工作區目錄
mkdir -p .cursor/workspaces

echo -e "${GREEN}✅ Workspace configurations created.${NC}"

# 啟動函數
launch_agent_workspace() {
    local agent_name=$1
    local workspace_file=$2
    local window_title=$3
    local color=$4
    
    echo -e "${color}🚀 Launching $window_title...${NC}"
    
    # 在新窗口中打開 workspace
    cursor --new-window --folder-uri "file://$PROJECT_ROOT" &
    
    # 等待一下讓窗口載入
    sleep 2
    
    echo -e "${color}✅ $window_title launched${NC}"
}

# 啟動多智能體工作區
echo -e "${BLUE}🌟 Starting Multi-Agent Workspaces...${NC}"
echo ""

echo -e "${PURPLE}1/6${NC} Central Coordinator (總協調者)"
launch_agent_workspace "central_coordinator" "central-coordinator.code-workspace" "Central Coordinator" "$PURPLE"

echo -e "${BLUE}2/6${NC} Project Manager (專案經理)"
launch_agent_workspace "project_manager" "project-manager.code-workspace" "Project Manager" "$BLUE"

echo -e "${GREEN}3/6${NC} Development Team (開發團隊)"
launch_agent_workspace "development_team" "development-team.code-workspace" "Development Team" "$GREEN"

echo -e "${YELLOW}4/6${NC} Testing Team (測試團隊)"
launch_agent_workspace "testing_team" "testing-team.code-workspace" "Testing Team" "$YELLOW"

echo -e "${CYAN}5/6${NC} Documentation Team (文檔團隊)"
launch_agent_workspace "documentation_team" "documentation-team.code-workspace" "Documentation Team" "$CYAN"

echo -e "${RED}6/6${NC} DevOps Team (運維團隊)"
launch_agent_workspace "devops_team" "devops-team.code-workspace" "DevOps Team" "$RED"

echo ""
echo -e "${GREEN}🎉 All Multi-Agent Workspaces Launched Successfully!${NC}"
echo ""
echo "=================================================================="
echo -e "${BLUE}📋 Next Steps:${NC}"
echo ""
echo -e "1. ${YELLOW}在每個 Cursor 窗口中設置對應的 AI Agent 角色${NC}"
echo -e "2. ${YELLOW}使用各自的 prompt template 來初始化 Agent${NC}"
echo -e "3. ${YELLOW}開始按照任務清單執行 Phase 1 Week 1-2 任務${NC}"
echo -e "4. ${YELLOW}通過 .cursor/shared-state/ 檔案進行團隊同步${NC}"
echo ""
echo -e "${BLUE}📁 重要檔案位置:${NC}"
echo -e "• Task Board: ${CYAN}.cursor/shared-state/task-board.md${NC}"
echo -e "• Project State: ${CYAN}.cursor/shared-state/project-state.json${NC}"
echo -e "• Agent Configs: ${CYAN}.cursor/multi-agent-config/${NC}"
echo -e "• Sync Config: ${CYAN}.cursor/sync-protocols/sync-config.yml${NC}"
echo ""
echo -e "${GREEN}🤖 開始多智能體協作開發 Qubic AI Compute Layer!${NC}"
echo "=================================================================="
