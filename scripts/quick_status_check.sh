#!/bin/bash
# 快速状态检查脚本
# 老板可以随时运行此脚本了解项目状态

echo "================================================"
echo "🚀 Feishu AI Assistant 快速状态检查"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "================================================"

echo ""
echo "📊 1. 项目基本信息"
echo "--------------------------------"
echo "项目目录: $(pwd)"
echo "工作空间: $HOME/.openclaw/workspace"

echo ""
echo "🔧 2. Docker环境状态"
echo "--------------------------------"
# 检查Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker已安装: $(docker --version | head -1)"
else
    echo "❌ Docker未安装"
fi

# 检查Docker Compose
if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose已安装: $(docker-compose --version)"
else
    echo "❌ Docker Compose未安装"
fi

# 检查Colima
if command -v colima &> /dev/null; then
    echo "✅ Colima已安装: $(colima version 2>/dev/null || echo '已安装')"
    colima status 2>/dev/null || echo "  Colima未启动"
else
    echo "❌ Colima未安装"
fi

echo ""
echo "🌐 3. API服务器状态"
echo "--------------------------------"
# 检查开发服务器
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 开发服务器运行中 (http://localhost:8000)"
    echo "   健康状态: $(curl -s http://localhost:8000/health | grep -o '"status":"[^"]*"' | cut -d'"' -f4)"
else
    echo "❌ 开发服务器未运行"
fi

echo ""
echo "📁 4. 关键文件状态"
echo "--------------------------------"
# 检查关键文件
if [ -f ".env.production" ]; then
    echo "✅ 生产环境配置存在"
else
    echo "❌ 生产环境配置缺失"
fi

if [ -f "docker-compose.yml" ]; then
    echo "✅ Docker Compose配置存在"
else
    echo "❌ Docker Compose配置缺失"
fi

if [ -f "scripts/deploy.sh" ]; then
    echo "✅ 部署脚本存在"
    if [ -x "scripts/deploy.sh" ]; then
        echo "✅ 部署脚本可执行"
    else
        echo "⚠️  部署脚本不可执行 (运行: chmod +x scripts/deploy.sh)"
    fi
else
    echo "❌ 部署脚本缺失"
fi

echo ""
echo "📈 5. 最近活动"
echo "--------------------------------"
# 显示最近修改的文件
echo "最近修改的文件:"
find . -type f -name "*.py" -o -name "*.md" -o -name "*.sh" -o -name "*.yml" -o -name "*.yaml" | \
    xargs ls -lt 2>/dev/null | head -5 | awk '{print $6" "$7" "$8" "$9}'

echo ""
echo "📋 6. 下一步建议"
echo "--------------------------------"
if ! command -v docker &> /dev/null; then
    echo "🔴 高优先级: 安装Docker环境"
    echo "   命令: brew install colima docker docker-compose"
elif ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "🔴 高优先级: 启动开发服务器"
    echo "   命令: python3 src/main.py"
else
    echo "🟢 系统状态正常，可以开始部署"
    echo "   命令: ./scripts/deploy.sh --env production --build --up"
fi

echo ""
echo "================================================"
echo "📞 如需帮助:"
echo "1. 查看详细状态: cat STATUS_DASHBOARD.md"
echo "2. 查看工作日志: cat ../memory/2026-02-22.md"
echo "3. 联系贾维斯: 直接在此聊天中反馈"
echo "================================================"