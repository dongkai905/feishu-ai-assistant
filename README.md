# 🚀 飞书AI助手项目

基于FastAPI和飞书开放平台构建的智能助手系统，提供日历管理、任务跟踪、智能提醒等全套办公自动化功能。

## ✨ 功能特性

### 📅 日历智能助手
- 日程自动管理
- 会议安排优化
- 智能时间分配
- 每日日程摘要

### ✅ 任务智能助手
- 任务优先级排序
- 智能工作负载分析
- 过期任务提醒
- 每日待办清单

### 📱 消息集成
- 自动消息发送
- 会议提醒通知
- 任务状态更新

### 📊 文档管理
- 文档列表查看
- 文档搜索
- 团队协作支持

## 🚀 快速开始

### 开发环境

#### 1. 安装依赖
```bash
cd feishu-ai-assistant
pip install -r requirements.txt
```

#### 2. 配置飞书应用
飞书应用凭证已自动配置完成，使用现有凭证：
- App ID: `cli_a91ee5dcdab89cc6`
- App Secret: `mJ4PzESOgImJN5Kef9zJWs4uoBu0tPML`

#### 3. 启动开发服务器
```bash
# 方式1: 使用Python直接运行
python src/main.py

# 方式2: 使用启动脚本
./start.sh
```

#### 4. 访问API
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health
- 版本信息: http://localhost:8000/version

### 生产环境部署

#### 1. 一键部署
```bash
# 授予执行权限
chmod +x scripts/deploy.sh

# 执行部署
./scripts/deploy.sh
```

#### 2. 手动部署
```bash
# 复制生产环境配置
cp .env.production .env

# 编辑.env文件，配置生产环境变量
vim .env

# 启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f api
```

## 📁 项目结构

```
feishu-ai-assistant/
├── src/                          # 源代码
│   ├── main.py                   # FastAPI主应用
│   ├── feishu_client.py          # 飞书API客户端
│   ├── calendar_assistant.py     # 日历智能助手
│   └── task_assistant.py         # 任务智能助手
├── tests/                        # 测试文件
├── scripts/                      # 部署和测试脚本
│   ├── deploy.sh                 # 生产部署脚本
│   └── test_api.py               # API测试脚本
├── nginx/                        # Nginx配置
│   └── nginx.conf                # Nginx配置文件
├── docker-compose.yml            # Docker Compose配置
├── Dockerfile                    # Docker镜像配置
├── requirements.txt              # Python依赖
├── .env                          # 开发环境配置
├── .env.production               # 生产环境配置
├── start.sh                      # 启动脚本
└── README.md                     # 项目说明
```

## 🔧 API接口

### 基础API
- `GET /` - 欢迎页面
- `GET /health` - 健康检查（包含飞书连接状态）
- `GET /version` - 版本信息
- `GET /system/info` - 系统信息

### 日历API
- `GET /calendar/calendars` - 获取日历列表
- `GET /calendar/today` - 获取今天事件
- `GET /calendar/upcoming` - 获取即将发生事件
- `POST /calendar/meeting` - 创建会议
- `GET /calendar/analysis` - 分析日程安排
- `GET /calendar/daily-summary` - 获取每日摘要

### 任务API
- `GET /tasks` - 获取任务列表
- `GET /tasks/overdue` - 获取过期任务
- `GET /tasks/due-today` - 获取今天到期任务
- `POST /tasks` - 创建任务
- `GET /tasks/prioritize` - 智能优先级排序
- `GET /tasks/analysis` - 分析工作负载
- `GET /tasks/daily-todo` - 获取每日待办清单

### 智能助手API
- `GET /assistant/daily-report` - 获取每日综合报告

## 🐳 Docker部署

### 服务架构
```
┌─────────┐    ┌─────────┐    ┌─────────┐
│  Nginx  │◄───┤   API   │◄───┤  Redis  │
└─────────┘    └─────────┘    └─────────┘
                    │               │
                    ▼               ▼
               ┌─────────┐    ┌─────────┐
               │PostgreSQL│    │ Celery  │
               └─────────┘    └─────────┘
```

### 可用服务
- **API服务**: http://localhost:8000
- **PostgreSQL数据库**: localhost:5432
- **Redis缓存**: localhost:6379
- **Nginx反向代理**: http://localhost:80
- **Flower监控**: http://localhost:5555
- **Grafana仪表板**: http://localhost:3000 (admin/admin)
- **Prometheus监控**: http://localhost:9090

### 管理命令
```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f api
docker-compose logs -f db
docker-compose logs -f redis

# 重启服务
docker-compose restart api

# 进入容器
docker-compose exec api bash
```

## 🧪 测试

### API测试
```bash
# 运行API测试
python scripts/test_api.py

# 测试结果保存在 test_results/ 目录
```

### 健康检查
```bash
curl http://localhost:8000/health
```

## 🔒 安全配置

### 环境变量安全
- 生产环境使用 `.env.production` 文件
- 敏感信息通过环境变量传递
- 数据库密码、API密钥等需要定期更换

### 网络安全
- 使用Nginx反向代理
- 配置SSL证书（推荐）
- 设置安全HTTP头部
- 限制CORS来源

## 📈 监控和日志

### 监控面板
- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090
- **Flower**: http://localhost:5555

### 日志位置
- 应用日志: `logs/app.log`
- Nginx访问日志: `logs/nginx/access.log`
- Nginx错误日志: `logs/nginx/error.log`
- 数据库日志: Docker容器内部

## 🔄 备份和恢复

### 数据备份
```bash
# 手动备份
./scripts/deploy.sh  # 部署脚本包含自动备份

# 数据库备份
docker exec feishu-ai-assistant-db pg_dump -U postgres feishu_ai > backup.sql
```

### 数据恢复
```bash
# 恢复数据库
cat backup.sql | docker exec -i feishu-ai-assistant-db psql -U postgres feishu_ai
```

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 支持

- 问题反馈: 创建GitHub Issue
- 功能建议: 通过Issue或Pull Request
- 紧急问题: 直接联系维护者

---

**飞书AI助手** - 让办公更智能，让工作更高效！ 🚀
