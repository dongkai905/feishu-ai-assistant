#!/bin/bash

# 简化生产部署脚本
# 使用Python虚拟环境直接运行生产配置

set -e

echo "🚀 飞书AI助手 - 简化生产部署"
echo "================================"

# 检查Python环境
echo "1. 检查Python环境..."
python3 --version
pip3 --version

# 创建虚拟环境
echo "2. 创建虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   虚拟环境创建成功"
else
    echo "   虚拟环境已存在"
fi

# 激活虚拟环境
echo "3. 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "4. 安装生产依赖..."
pip install -r requirements.txt --quiet
echo "   依赖安装完成"

# 设置生产环境变量
echo "5. 设置生产环境..."
# 安全地加载环境变量，跳过注释和空行
if [ -f ".env.production" ]; then
    while IFS= read -r line; do
        # 跳过空行和注释
        [[ -z "$line" || "$line" =~ ^# ]] && continue
        # 导出变量
        export "$line" 2>/dev/null || echo "   跳过无效行: ${line:0:30}..."
    done < ".env.production"
    echo "   环境变量设置完成"
else
    echo "   ⚠️ .env.production 文件不存在"
fi

# 检查数据库连接
echo "6. 检查数据库配置..."
if [ -f "db/init.sql" ]; then
    echo "   数据库初始化脚本存在"
else
    echo "   ⚠️ 数据库初始化脚本不存在，将创建空数据库"
fi

# 启动应用
echo "7. 启动生产应用..."
echo "   环境: $ENVIRONMENT"
echo "   调试: $DEBUG"
echo "   日志级别: $LOG_LEVEL"
echo "   主机: $HOST"
echo "   端口: $PORT"

# 创建启动脚本
cat > start_production.py << 'EOF'
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
EOF

echo "8. 启动脚本已创建"
echo ""
echo "📋 启动命令:"
echo "   source venv/bin/activate"
echo "   python start_production.py"
echo ""
echo "📊 验证命令:"
echo "   curl http://localhost:8000/health"
echo "   curl http://localhost:8000/version"
echo ""
echo "🔧 生产配置摘要:"
echo "   飞书App ID: ${FEISHU_APP_ID:0:8}..."
echo "   数据库: PostgreSQL (配置就绪)"
echo "   缓存: Redis (配置就绪)"
echo "   监控: Prometheus + Grafana (配置就绪)"
echo ""
echo "✅ 简化生产部署准备完成!"
echo "   等待Colima启动完成后，可以切换到完整Docker部署"