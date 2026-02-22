#!/bin/bash

# GitHub Codespaces 启动脚本
# 自动配置环境并启动 Feishu AI Assistant

echo "🚀 启动 Feishu AI Assistant (GitHub Codespaces 版本)"

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 检查端口是否被占用
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  端口 8000 已被占用，尝试使用 8001"
    PORT=8001
else
    PORT=8000
fi

# 设置环境变量
export FEISHU_APP_ID=${FEISHU_APP_ID:-"cli_a91ee5dcdab89cc6"}
export FEISHU_APP_SECRET=${FEISHU_APP_SECRET:-"mJ4PzESOgImJN5Kef9zJWs4uoBu0tPML"}
export FEISHU_WEBHOOK_VERIFICATION_TOKEN=${FEISHU_WEBHOOK_VERIFICATION_TOKEN:-"your_verification_token"}
export FEISHU_WEBHOOK_ENCRYPT_KEY=${FEISHU_WEBHOOK_ENCRYPT_KEY:-"your_encrypt_key"}
export CORS_ORIGINS=${CORS_ORIGINS:-"*"}
export PORT=$PORT

echo "📋 环境配置:"
echo "  - 端口: $PORT"
echo "  - App ID: $FEISHU_APP_ID"
echo "  - CORS: $CORS_ORIGINS"

# 安装依赖
echo "📦 安装 Python 依赖..."
pip install -r requirements.txt

# 启动服务
echo "🚀 启动 FastAPI 服务..."
echo "🔗 服务地址: http://localhost:$PORT"
echo "🔗 健康检查: http://localhost:$PORT/health"
echo "🔗 Webhook: http://localhost:$PORT/feishu/webhook/simple"
echo ""
echo "📝 重要提示:"
echo "1. GitHub Codespaces 会自动创建公网 URL"
echo "2. 在 Codespaces 终端中查看端口转发信息"
echo "3. 使用该 URL 配置飞书 Webhook"
echo "4. 按 Ctrl+C 停止服务"

# 启动服务
python -m uvicorn src.main:app --host 0.0.0.0 --port $PORT --reload