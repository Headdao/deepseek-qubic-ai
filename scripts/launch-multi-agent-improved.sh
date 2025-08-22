#!/bin/bash

# Multi-Agent Workspace Launch Script (Improved Version)
# Qubic AI Compute Layer Project

echo "🚀 改進版多智能體工作區啟動腳本"
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

# Cursor CLI 路徑
CURSOR_CLI="/Applications/Cursor.app/Contents/Resources/app/bin/cursor"

# 檢查專案目錄
if [ ! -d "$PROJECT_ROOT" ]; then
    echo -e "${RED}❌ 專案目錄未找到: $PROJECT_ROOT${NC}"
    exit 1
fi

cd "$PROJECT_ROOT"

# 方法 1: 使用 CLI 工具 (如果可用)
if [ -f "$CURSOR_CLI" ]; then
    echo -e "${GREEN}✅ 找到 Cursor CLI 工具，嘗試使用 CLI 方式啟動...${NC}"
    
    echo -e "${PURPLE}🎯 啟動 Central Coordinator${NC}"
    "$CURSOR_CLI" --new-window "$PROJECT_ROOT" 2>/dev/null &
    sleep 2
    
    echo -e "${BLUE}📊 啟動 Project Manager${NC}"
    "$CURSOR_CLI" --new-window "$PROJECT_ROOT" 2>/dev/null &
    sleep 2
    
    echo -e "${GREEN}💻 啟動 Development Team${NC}"
    "$CURSOR_CLI" --new-window "$PROJECT_ROOT" 2>/dev/null &
    sleep 2
    
    echo -e "${YELLOW}🧪 啟動 Testing Team${NC}"
    "$CURSOR_CLI" --new-window "$PROJECT_ROOT" 2>/dev/null &
    sleep 2
    
    echo -e "${CYAN}📚 啟動 Documentation Team${NC}"
    "$CURSOR_CLI" --new-window "$PROJECT_ROOT" 2>/dev/null &
    sleep 2
    
    echo -e "${RED}🔧 啟動 DevOps Team${NC}"
    "$CURSOR_CLI" --new-window "$PROJECT_ROOT" 2>/dev/null &
    sleep 2
    
    echo -e "${GREEN}🎉 CLI 方式啟動完成！${NC}"
    
else
    echo -e "${YELLOW}⚠️ Cursor CLI 工具未找到，將使用 AppleScript 方式...${NC}"
    
    # 方法 2: 使用 AppleScript
    osascript << EOF
tell application "Cursor"
    activate
    repeat 6 times
        delay 1
        tell application "System Events"
            keystroke "n" using {command down, shift down}
        end tell
        delay 2
    end repeat
end tell
EOF
    
    echo -e "${GREEN}🎉 AppleScript 方式啟動完成！${NC}"
fi

echo ""
echo "=================================================================="
echo -e "${BLUE}📋 接下來請手動操作：${NC}"
echo ""
echo -e "${YELLOW}1. 在每個 Cursor 窗口中開啟專案資料夾：${NC}"
echo -e "   • 按 ${CYAN}Cmd + O${NC}"
echo -e "   • 選擇: ${CYAN}/Users/apple/qubic/qdashboard${NC}"
echo -e "   • 點擊 ${CYAN}Open${NC}"
echo ""
echo -e "${YELLOW}2. 設置 AI Agent 角色 (在每個窗口中)：${NC}"
echo -e "   • 按 ${CYAN}Cmd + K${NC} 或點擊右下角 AI 按鈕"
echo -e "   • 使用對應的 Prompt Template"
echo ""
echo -e "${BLUE}📖 詳細指南: Multi_Agent_手動設置指南.md${NC}"
echo "=================================================================="

# 提供快速開啟資料夾的方法
echo ""
echo -e "${GREEN}💡 快速開啟專案資料夾小技巧：${NC}"
echo -e "1. 複製這個路徑: ${CYAN}/Users/apple/qubic/qdashboard${NC}"
echo -e "2. 在 Cursor 中按 ${CYAN}Cmd + O${NC}"
echo -e "3. 按 ${CYAN}Cmd + Shift + G${NC} (前往資料夾)"
echo -e "4. 貼上路徑並按 ${CYAN}Enter${NC}"

echo ""
echo -e "${PURPLE}🤖 AI Agent Prompt Templates 快速參考：${NC}"
echo ""
echo -e "${PURPLE}Central Coordinator:${NC} 中央協調者，負責總體協調和衝突解決"
echo -e "${BLUE}Project Manager:${NC} 專案經理，負責進度追蹤和里程碑管理"
echo -e "${GREEN}Development Team:${NC} 開發團隊，負責 GCP 設置和程式碼開發"
echo -e "${YELLOW}Testing Team:${NC} 測試團隊，負責測試規劃和品質保證"
echo -e "${CYAN}Documentation Team:${NC} 文檔團隊，負責文檔撰寫和維護"
echo -e "${RED}DevOps Team:${NC} 運維團隊，負責基礎設施和部署"
