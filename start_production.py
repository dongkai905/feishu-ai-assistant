import os
import uvicorn
import sys

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import app

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    print(f"🚀 启动飞书AI助手生产服务器...")
    print(f"   地址: http://{host}:{port}")
    print(f"   环境: {os.getenv('ENVIRONMENT', 'production')}")
    print(f"   调试模式: {os.getenv('DEBUG', 'false')}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
        reload=False  # 生产环境不启用热重载
    )
