#!/bin/bash

# 飞书AI助手启动脚本

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 启动飞书AI助手...${NC}"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装，请先安装Python3"
    exit 1
fi

# 检查依赖
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt文件不存在"
    exit 1
fi

# 检查环境变量
if [ ! -f ".env" ]; then
    echo "⚠️  .env文件不存在，从示例文件复制"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ 已创建.env文件，请编辑配置"
    else
        echo "❌ .env.example文件也不存在"
        exit 1
    fi
fi

# 安装依赖（如果venv不存在）
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境并安装依赖..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "📦 激活虚拟环境..."
    source venv/bin/activate
fi

# 检查飞书凭证
if [ -z "$FEISHU_APP_ID" ] && [ -z "$(grep FEISHU_APP_ID .env)" ]; then
    echo "⚠️  飞书应用凭证未配置"
    echo "请编辑 .env 文件，设置以下变量："
    echo "FEISHU_APP_ID=your_app_id"
    echo "FEISHU_APP_SECRET=your_app_secret"
    exit 1
fi

# 启动服务器
echo -e "${GREEN}✅ 启动FastAPI服务器...${NC}"
echo "🌐 API文档: http://localhost:8000/docs"
echo "🏥 健康检查: http://localhost:8000/health"
echo "📊 版本信息: http://localhost:8000/version"
echo ""
echo "按 Ctrl+C 停止服务器"

# 设置Python路径并启动
export PYTHONPATH=$(pwd)/src:$PYTHONPATH
cd src && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload