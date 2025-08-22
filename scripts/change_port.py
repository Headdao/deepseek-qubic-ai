#!/usr/bin/env python3
"""
QDashboard 端口管理工具
快速更改所有相關文件中的端口配置
"""

import sys
import os

def change_port(new_port):
    """更改所有配置文件中的端口"""
    
    # 更新 app_config.py
    config_file = 'app_config.py'
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替換端口
        new_content = content.replace(f'PORT = 3000', f'PORT = {new_port}')
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ 已更新 {config_file}: PORT = {new_port}")
    else:
        print(f"❌ 找不到 {config_file}")

def main():
    if len(sys.argv) != 2:
        print("使用方法: python3 scripts/change_port.py <新端口>")
        print("例如: python3 scripts/change_port.py 8080")
        sys.exit(1)
    
    try:
        new_port = int(sys.argv[1])
        if new_port < 1024 or new_port > 65535:
            print("❌ 端口必須在 1024-65535 範圍內")
            sys.exit(1)
        
        print(f"🔧 正在將端口更改為 {new_port}...")
        change_port(new_port)
        print("🎉 端口更改完成！")
        print(f"📝 請重啟應用: python3 minimal_app.py")
        print(f"🌐 新的 URL: http://localhost:{new_port}/qdashboard/")
        
    except ValueError:
        print("❌ 端口必須是數字")
        sys.exit(1)

if __name__ == '__main__':
    main()


