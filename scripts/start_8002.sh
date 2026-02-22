#!/bin/bash
# GitHub Codespace 8002端口快速启动脚本

echo "🚀 启动Feishu AI Assistant服务 (端口8002)"

# 停止可能运行的服务
echo "🛑 停止现有服务..."
pkill -f uvicorn 2>/dev/null || true

# 激活虚拟环境
echo "🐍 激活Python虚拟环境..."
cd /workspaces/feishu-ai-assistant
source venv/bin/activate

# 设置环境变量
echo "🔧 设置环境变量..."
export FEISHU_APP_ID=cli_a91ee5dcdab89cc6
export FEISHU_APP_SECRET=mJ4PzESOgImJN5Kef9zJWs4uoBu0tPML
export FEISHU_WEBHOOK_VERIFICATION_TOKEN=""
export FEISHU_WEBHOOK_ENCRYPT_KEY=""

# 启动服务
echo "🚀 启动Uvicorn服务 (端口8002)..."
echo "📡 服务地址: http://0.0.0.0:8002"
echo "🌐 Webhook端点: http://localhost:8002/feishu/webhook/simple"
echo ""
echo "📋 测试命令:"
echo "  curl http://localhost:8002/health"
echo "  curl -X POST http://localhost:8002/feishu/webhook/simple \\"
echo "    -H \"Content-Type: application/json\" \\"
echo "    -d '{\"type\":\"url_verification\",\"challenge\":\"test_8002\"}'"
echo ""
echo "💡 提示: 在GitHub Codespace中配置端口转发:"
echo "  1. 点击左下角'端口'标签"
echo "  2. 点击'添加端口'"
echo "  3. 输入端口号 8002"
echo "  4. 设置可见性为 Public"
echo "  5. 获取公网URL: https://[codespace-name]-8002.github.dev"

uvicorn src.main:app --host 0.0.0.0 --port 8002