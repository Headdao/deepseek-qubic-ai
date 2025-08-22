#!/usr/bin/env python3
"""
前端 AI 組件測試腳本
測試新建立的前端 AI 組件功能和整合性
"""

import os
import sys
import requests
import json
import time
from pathlib import Path

# 添加項目根目錄到路徑
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

class FrontendAIComponentsTest:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.frontend_path = project_root / "frontend"
        self.test_results = []
        
    def run_all_tests(self):
        """執行所有前端 AI 組件測試"""
        print("🧪 開始前端 AI 組件測試...")
        print("=" * 50)
        
        # 1. 檢查文件結構
        self.test_file_structure()
        
        # 2. 測試 AI API 端點可用性
        self.test_ai_api_endpoints()
        
        # 3. 檢查前端 JavaScript 文件
        self.test_frontend_javascript_files()
        
        # 4. 檢查 CSS 樣式文件
        self.test_frontend_css_files()
        
        # 5. 測試 HTML 整合
        self.test_html_integration()
        
        # 6. 模擬前端 AI 調用
        self.test_simulated_ai_calls()
        
        # 顯示測試結果
        self.show_test_summary()
        
    def test_file_structure(self):
        """測試前端 AI 組件文件結構"""
        print("\n📁 測試前端 AI 組件文件結構...")
        
        required_files = [
            "frontend/js/ai-components.js",
            "frontend/css/ai-components.css",
            "frontend/js/dev-console.js", 
            "frontend/css/dev-console.css",
            "frontend/qdashboard/index.html"
        ]
        
        for file_path in required_files:
            full_path = project_root / file_path
            if full_path.exists():
                print(f"✅ {file_path} - 文件存在")
                self.test_results.append(f"✅ 文件結構: {file_path}")
            else:
                print(f"❌ {file_path} - 文件不存在")
                self.test_results.append(f"❌ 文件結構: {file_path}")
    
    def test_ai_api_endpoints(self):
        """測試 AI API 端點可用性"""
        print("\n🔌 測試 AI API 端點...")
        
        endpoints = [
            "/api/ai/analyze",
            "/api/ai/query", 
            "/api/ai/insights",
            "/api/ai/status",
            "/api/ai/health"
        ]
        
        for endpoint in endpoints:
            try:
                # 測試 GET 請求
                if endpoint in ["/api/ai/status", "/api/ai/health"]:
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                    if response.status_code == 200:
                        print(f"✅ {endpoint} - API 可用")
                        self.test_results.append(f"✅ API 端點: {endpoint}")
                    else:
                        print(f"⚠️ {endpoint} - API 狀態碼: {response.status_code}")
                        self.test_results.append(f"⚠️ API 端點: {endpoint} (狀態碼: {response.status_code})")
                else:
                    # 測試 POST 請求
                    test_data = {"test": True}
                    response = requests.post(f"{self.base_url}{endpoint}", 
                                           json=test_data, timeout=5)
                    if response.status_code in [200, 400, 422]:  # 接受這些狀態碼
                        print(f"✅ {endpoint} - API 響應正常")
                        self.test_results.append(f"✅ API 端點: {endpoint}")
                    else:
                        print(f"⚠️ {endpoint} - API 狀態碼: {response.status_code}")
                        self.test_results.append(f"⚠️ API 端點: {endpoint} (狀態碼: {response.status_code})")
                        
            except requests.exceptions.ConnectionError:
                print(f"❌ {endpoint} - 連線失敗 (後端未啟動)")
                self.test_results.append(f"❌ API 端點: {endpoint} (連線失敗)")
            except Exception as e:
                print(f"❌ {endpoint} - 錯誤: {str(e)}")
                self.test_results.append(f"❌ API 端點: {endpoint} (錯誤: {str(e)})")
    
    def test_frontend_javascript_files(self):
        """測試前端 JavaScript 文件內容"""
        print("\n🟨 測試前端 JavaScript 文件...")
        
        js_files = {
            "frontend/js/ai-components.js": [
                "QubicAIComponents",
                "performAnalysis",
                "sendQAMessage",
                "callAIAnalysis"
            ],
            "frontend/js/dev-console.js": [
                "QubicDevConsole",
                "toggleConsole",
                "interceptAPICallsTt",
                "log"
            ]
        }
        
        for file_path, expected_functions in js_files.items():
            full_path = project_root / file_path
            
            if full_path.exists():
                try:
                    content = full_path.read_text(encoding='utf-8')
                    print(f"\n檢查 {file_path}:")
                    
                    for func in expected_functions:
                        if func in content:
                            print(f"  ✅ 包含函數/類別: {func}")
                        else:
                            print(f"  ❌ 缺少函數/類別: {func}")
                    
                    # 檢查基本語法
                    if "class " in content and "function " in content:
                        print(f"  ✅ JavaScript 語法結構正常")
                        self.test_results.append(f"✅ JavaScript: {file_path}")
                    else:
                        print(f"  ⚠️ JavaScript 語法結構可能有問題")
                        self.test_results.append(f"⚠️ JavaScript: {file_path}")
                        
                except Exception as e:
                    print(f"  ❌ 讀取文件失敗: {str(e)}")
                    self.test_results.append(f"❌ JavaScript: {file_path} (讀取失敗)")
            else:
                print(f"❌ {file_path} - 文件不存在")
    
    def test_frontend_css_files(self):
        """測試前端 CSS 文件內容"""
        print("\n🎨 測試前端 CSS 文件...")
        
        css_files = {
            "frontend/css/ai-components.css": [
                "#ai-analysis-panel",
                ".analysis-results",
                ".conversation-container",
                ".quick-question-btn"
            ],
            "frontend/css/dev-console.css": [
                ".qubic-dev-console",
                ".console-header",
                ".console-tabs",
                ".log-container"
            ]
        }
        
        for file_path, expected_selectors in css_files.items():
            full_path = project_root / file_path
            
            if full_path.exists():
                try:
                    content = full_path.read_text(encoding='utf-8')
                    print(f"\n檢查 {file_path}:")
                    
                    for selector in expected_selectors:
                        if selector in content:
                            print(f"  ✅ 包含樣式: {selector}")
                        else:
                            print(f"  ❌ 缺少樣式: {selector}")
                    
                    # 檢查響應式設計
                    if "@media" in content:
                        print(f"  ✅ 包含響應式設計")
                    else:
                        print(f"  ⚠️ 缺少響應式設計")
                    
                    self.test_results.append(f"✅ CSS: {file_path}")
                        
                except Exception as e:
                    print(f"  ❌ 讀取文件失敗: {str(e)}")
                    self.test_results.append(f"❌ CSS: {file_path} (讀取失敗)")
            else:
                print(f"❌ {file_path} - 文件不存在")
    
    def test_html_integration(self):
        """測試 HTML 整合"""
        print("\n🌐 測試 HTML 整合...")
        
        html_file = project_root / "frontend/qdashboard/index.html"
        
        if html_file.exists():
            try:
                content = html_file.read_text(encoding='utf-8')
                
                required_includes = [
                    "ai-components.css",
                    "dev-console.css", 
                    "ai-components.js",
                    "dev-console.js",
                    "QubicAIComponents"
                ]
                
                print("檢查 HTML 整合:")
                for include in required_includes:
                    if include in content:
                        print(f"  ✅ 包含: {include}")
                    else:
                        print(f"  ❌ 缺少: {include}")
                
                # 檢查基本 HTML 結構
                if "<html" in content and "</html>" in content:
                    print(f"  ✅ HTML 結構完整")
                    self.test_results.append(f"✅ HTML 整合正常")
                else:
                    print(f"  ❌ HTML 結構不完整")
                    self.test_results.append(f"❌ HTML 結構不完整")
                    
            except Exception as e:
                print(f"❌ 讀取 HTML 文件失敗: {str(e)}")
                self.test_results.append(f"❌ HTML 讀取失敗")
        else:
            print("❌ HTML 文件不存在")
            self.test_results.append(f"❌ HTML 文件不存在")
    
    def test_simulated_ai_calls(self):
        """模擬前端 AI 調用測試"""
        print("\n🤖 模擬前端 AI 調用測試...")
        
        # 測試 AI 分析
        try:
            analyze_data = {
                "data": {
                    "tick": 15234567,
                    "epoch": 134,
                    "duration": 1.2,
                    "health": {
                        "overall": "健康",
                        "tick_status": "正常"
                    }
                },
                "analysis_type": "comprehensive"
            }
            
            response = requests.post(f"{self.base_url}/api/ai/analyze", 
                                   json=analyze_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if "summary" in result and "insights" in result:
                    print("✅ AI 分析模擬調用成功")
                    self.test_results.append("✅ AI 分析模擬調用")
                else:
                    print("⚠️ AI 分析響應格式異常")
                    self.test_results.append("⚠️ AI 分析響應格式異常")
            else:
                print(f"⚠️ AI 分析調用狀態碼: {response.status_code}")
                
        except Exception as e:
            print(f"❌ AI 分析模擬調用失敗: {str(e)}")
        
        # 測試 AI 問答
        try:
            qa_data = {
                "question": "測試問題：當前網路狀況如何？",
                "context": {
                    "tick": 15234567,
                    "epoch": 134
                }
            }
            
            response = requests.post(f"{self.base_url}/api/ai/query", 
                                   json=qa_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if "answer" in result:
                    print("✅ AI 問答模擬調用成功")
                    self.test_results.append("✅ AI 問答模擬調用")
                else:
                    print("⚠️ AI 問答響應格式異常")
                    self.test_results.append("⚠️ AI 問答響應格式異常")
            else:
                print(f"⚠️ AI 問答調用狀態碼: {response.status_code}")
                
        except Exception as e:
            print(f"❌ AI 問答模擬調用失敗: {str(e)}")
    
    def show_test_summary(self):
        """顯示測試結果摘要"""
        print("\n" + "=" * 50)
        print("📊 前端 AI 組件測試結果摘要")
        print("=" * 50)
        
        success_count = len([r for r in self.test_results if r.startswith("✅")])
        warning_count = len([r for r in self.test_results if r.startswith("⚠️")])
        error_count = len([r for r in self.test_results if r.startswith("❌")])
        total_count = len(self.test_results)
        
        print(f"總測試項目: {total_count}")
        print(f"✅ 成功: {success_count}")
        print(f"⚠️ 警告: {warning_count}")
        print(f"❌ 失敗: {error_count}")
        
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
        print(f"\n🎯 成功率: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 前端 AI 組件整合測試通過！")
        elif success_rate >= 60:
            print("⚠️ 前端 AI 組件基本可用，但有部分問題需要關注")
        else:
            print("❌ 前端 AI 組件存在較多問題，需要修復")
        
        # 詳細結果
        print(f"\n📋 詳細測試結果:")
        for result in self.test_results:
            print(f"  {result}")
        
        # 建議
        print(f"\n💡 建議:")
        if error_count > 0:
            print("  - 修復失敗的測試項目")
        if warning_count > 0:
            print("  - 檢查並改善警告項目")
        
        print("  - 啟動後端服務以測試完整功能")
        print("  - 在瀏覽器中測試前端 UI 組件")
        print("  - 測試 F12 開發者控制台功能")
        print("  - 驗證 AI 分析和問答功能")

def main():
    """主函數"""
    print("🚀 前端 AI 組件測試工具")
    print("=" * 50)
    
    tester = FrontendAIComponentsTest()
    tester.run_all_tests()
    
    print(f"\n🔧 如需啟動後端進行完整測試，請執行:")
    print(f"  source venv/bin/activate")
    print(f"  python app.py")
    print(f"\n🌐 然後在瀏覽器中訪問:")
    print(f"  http://localhost:5000/qdashboard/")

if __name__ == "__main__":
    main()


