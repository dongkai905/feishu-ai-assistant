#!/usr/bin/env python3
"""
飞书AI助手启动脚本 - 修复导入问题版本
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 检查飞书凭证
app_id = os.getenv("FEISHU_APP_ID")
app_secret = os.getenv("FEISHU_APP_SECRET")

if not app_id or not app_secret:
    print("❌ 飞书应用凭证未配置")
    print("请编辑 .env 文件，设置以下变量：")
    print("FEISHU_APP_ID=your_app_id")
    print("FEISHU_APP_SECRET=your_app_secret")
    sys.exit(1)

print("✅ 飞书凭证配置正常")
print(f"📱 App ID: {app_id[:8]}...")
print(f"🔑 App Secret: {app_secret[:8]}...")

# 启动服务器
if __name__ == "__main__":
    print("🚀 启动飞书AI助手服务器...")
    print("🌐 API文档: http://localhost:8000/docs")
    print("🏥 健康检查: http://localhost:8000/health")
    print("📊 版本信息: http://localhost:8000/version")
    print("\n按 Ctrl+C 停止服务器\n")
    
    # 导入并启动FastAPI应用
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)