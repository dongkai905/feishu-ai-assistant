#!/bin/bash
# 每日系统检查脚本

echo "=========================================="
echo "📊 Feishu AI Assistant 每日检查"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="
echo ""

# 进入项目目录
cd /Users/laogudong/.openclaw/workspace/feishu-ai-assistant

# 1. 检查系统健康
echo "🟢 1. 系统健康检查"
python3 scripts/feishu_cli.py health
echo ""

# 2. 查看今日日历
echo "📅 2. 今日日历"
python3 scripts/feishu_cli.py calendar
echo ""

# 3. 查看任务列表
echo "✅ 3. 任务统计"
python3 scripts/feishu_cli.py tasks
echo ""

# 4. 查看文档列表
echo "📄 4. 文档统计"
python3 scripts/feishu_cli.py documents
echo ""

echo "=========================================="
echo "🎯 今日建议:"
echo "1. 检查是否有重要会议"
echo "2. 查看待办任务优先级"
echo "3. 整理重要文档"
echo "=========================================="
echo "检查完成于: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 记录到日志文件
LOG_FILE="logs/daily_check_$(date '+%Y%m%d').log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 每日检查完成" >> "$LOG_FILE"