# Feishu AI Assistant 使用指南

## 🚀 快速开始

### 1. 启动系统
```bash
# 进入项目目录
cd feishu-ai-assistant

# 启动开发服务器
./scripts/start_dev_server.sh
```

### 2. 检查系统状态
```bash
# 使用命令行工具
python3 scripts/feishu_cli.py dashboard

# 或直接使用curl
curl http://localhost:8000/health
```

### 3. 访问API文档
打开浏览器访问: http://localhost:8000/docs

## 📱 命令行工具使用

### 安装快捷方式
```bash
# 创建别名
alias feishu-cli="python3 /path/to/feishu-ai-assistant/scripts/feishu_cli.py"

# 添加到 ~/.zshrc 或 ~/.bashrc
echo 'alias feishu-cli="python3 /Users/laogudong/.openclaw/workspace/feishu-ai-assistant/scripts/feishu_cli.py"' >> ~/.zshrc
source ~/.zshrc
```

### 常用命令
```bash
# 查看综合仪表板
feishu-cli dashboard

# 检查系统健康
feishu-cli health

# 查看今日日历
feishu-cli calendar

# 查看任务列表
feishu-cli tasks

# 查看文档列表
feishu-cli documents

# 查看版本信息
feishu-cli version
```

## 🔧 API接口使用

### 基础API
```bash
# 根端点
curl http://localhost:8000/

# 健康检查
curl http://localhost:8000/health

# 版本信息
curl http://localhost:8000/version
```

### 日历功能
```bash
# 获取今日日历
curl http://localhost:8000/calendar/today

# 获取本周日历 (待实现)
curl http://localhost:8000/calendar/week

# 创建日历事件 (需要修复)
curl -X POST http://localhost:8000/calendar/events \
  -H "Content-Type: application/json" \
  -d '{"summary": "会议", "start_time": "2026-02-22T14:00:00", "end_time": "2026-02-22T15:00:00"}'
```

### 任务功能
```bash
# 获取任务列表
curl http://localhost:8000/tasks

# 按状态筛选任务
curl "http://localhost:8000/tasks?status=pending"

# 按优先级筛选任务
curl "http://localhost:8000/tasks?priority=1"

# 创建任务 (需要修复)
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "新任务", "description": "任务描述"}'
```

### 文档功能
```bash
# 获取文档列表
curl http://localhost:8000/documents

# 按文件夹获取文档
curl "http://localhost:8000/documents?folder_token=xxx"
```

### 消息功能
```bash
# 发送消息 (需要修复参数)
curl -X POST "http://localhost:8000/messages/send?receive_id=user_id&message=测试消息"
```

## 🎯 日常使用场景

### 场景1: 每日工作开始
```bash
# 1. 检查系统状态
feishu-cli health

# 2. 查看今日日历
feishu-cli calendar

# 3. 查看待办任务
feishu-cli tasks --status pending
```

### 场景2: 会议管理
```bash
# 1. 查看今日会议
feishu-cli calendar

# 2. 创建会议提醒 (待修复)
# curl -X POST http://localhost:8000/calendar/events ...
```

### 场景3: 任务跟踪
```bash
# 1. 查看所有任务
feishu-cli tasks

# 2. 查看高优先级任务
feishu-cli tasks --status pending
```

### 场景4: 文档管理
```bash
# 1. 查看最近文档
feishu-cli documents

# 2. 搜索特定文档
curl "http://localhost:8000/documents?search=项目报告"
```

## 🔍 系统监控

### 监控面板
```bash
# 查看完整监控面板
feishu-cli dashboard

# 输出JSON格式
curl http://localhost:8000/health | python3 -m json.tool
```

### 性能指标
```bash
# 响应时间测试
time curl -s http://localhost:8000/health > /dev/null

# 并发测试 (需要安装ab)
ab -n 100 -c 10 http://localhost:8000/health
```

## 🛠️ 故障排除

### 常见问题

#### 1. 服务器未启动
```bash
# 检查进程
ps aux | grep uvicorn

# 启动服务器
./scripts/start_dev_server.sh
```

#### 2. 数据库连接失败
```bash
# 检查PostgreSQL状态
brew services list | grep postgresql

# 启动PostgreSQL
brew services start postgresql@15
```

#### 3. Redis连接失败
```bash
# 检查Redis状态
brew services list | grep redis

# 启动Redis
brew services start redis
```

#### 4. 飞书连接失败
```bash
# 检查环境变量
echo $FEISHU_APP_ID
echo $FEISHU_APP_SECRET

# 重新设置环境变量
source .env.local
```

### 日志查看
```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log

# 查看访问日志
tail -f logs/access.log
```

## 📈 高级使用

### 自动化脚本
```bash
#!/bin/bash
# daily_check.sh - 每日检查脚本

echo "=== 每日系统检查 ==="
echo "时间: $(date)"

# 检查系统健康
feishu-cli health

# 查看今日日历
echo ""
echo "=== 今日日历 ==="
feishu-cli calendar

# 查看待办任务
echo ""
echo "=== 待办任务 ==="
feishu-cli tasks --status pending

echo ""
echo "检查完成!"
```

### 集成到工作流
```bash
# 在crontab中添加定时任务
crontab -e

# 添加以下行 (每天9点检查)
0 9 * * * /path/to/daily_check.sh >> /path/to/daily_check.log 2>&1
```

### Webhook集成
```bash
# 接收飞书事件通知
curl -X POST http://localhost:8000/webhook/feishu \
  -H "Content-Type: application/json" \
  -d '{"type": "message", "event": {...}}'
```

## 🔗 相关资源

### 文档链接
- **API文档**: http://localhost:8000/docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 配置文件
- **环境配置**: `.env.local`
- **数据库配置**: `config/database.py`
- **飞书配置**: `config/feishu.py`

### 脚本目录
- **启动脚本**: `scripts/start_dev_server.sh`
- **部署脚本**: `scripts/deploy.sh`
- **测试脚本**: `scripts/test_api.py`
- **命令行工具**: `scripts/feishu_cli.py`

## 📞 技术支持

### 问题反馈
1. 检查系统日志: `tail -f logs/app.log`
2. 查看API响应: 使用 `curl -v` 查看详细响应
3. 检查网络连接: `ping localhost`

### 联系开发
- **项目目录**: `feishu-ai-assistant/`
- **源码位置**: `src/`
- **配置文件**: `config/`

### 紧急恢复
```bash
# 重启所有服务
./scripts/restart_all.sh

# 重置数据库 (谨慎使用)
./scripts/reset_db.sh

# 重新安装依赖
pip install -r requirements.txt
```

---

**最后更新**: 2026-02-22  
**版本**: 1.0.0  
**状态**: 🟢 运行正常