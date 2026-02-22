# GitHub Codespaces 部署指南

## 🚀 快速开始

### 步骤1: 创建 GitHub 仓库
1. 访问 https://github.com/new
2. 仓库名称: `feishu-ai-assistant`
3. 描述: "Feishu AI Assistant - 智能日历和任务管理助手"
4. 选择 **Public** (公开)
5. 点击 "Create repository"

### 步骤2: 推送代码到 GitHub
```bash
# 在本地项目目录中
cd /Users/laogudong/.openclaw/workspace/feishu-ai-assistant

# 初始化 Git 仓库
git init
git add .
git commit -m "Initial commit: Feishu AI Assistant"

# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/feishu-ai-assistant.git

# 推送代码
git branch -M main
git push -u origin main
```

### 步骤3: 创建 Codespace
1. 访问您的 GitHub 仓库页面
2. 点击绿色的 "Code" 按钮
3. 选择 "Codespaces" 标签页
4. 点击 "Create codespace on main"

### 步骤4: 启动服务
在 Codespace 终端中运行:
```bash
# 方法1: 使用启动脚本
./scripts/codespaces_start.sh

# 方法2: 手动启动
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## 🌐 获取公网 URL

GitHub Codespaces 会自动创建公网 URL:

1. 在 Codespace 中，查看端口转发面板
2. 找到端口 8000 的转发信息
3. URL 格式: `https://YOUR-CODESPACE-XXXXXX.github.dev`

**示例 URL**: `https://feishu-ai-123456.github.dev`

## 🔧 配置飞书 Webhook

### 1. 获取 Webhook URL
```
https://YOUR-CODESPACE-XXXXXX.github.dev/feishu/webhook/simple
```

### 2. 配置飞书开放平台
1. 访问: https://open.feishu.cn/app
2. 选择您的应用
3. 进入 "事件订阅" 页面
4. 请求地址: 填入上面的 Webhook URL
5. 验证令牌: 使用 `FEISHU_WEBHOOK_VERIFICATION_TOKEN`
6. 加密密钥: 使用 `FEISHU_WEBHOOK_ENCRYPT_KEY`
7. 保存配置

### 3. 测试 Webhook
1. 在飞书开放平台点击 "测试"
2. 系统会发送测试事件
3. 查看 Codespace 日志确认接收成功

## ⚙️ 环境变量配置

### 必需的环境变量
```bash
# 在 Codespace 中设置
export FEISHU_APP_ID="cli_a91ee5dcdab89cc6"
export FEISHU_APP_SECRET="mJ4PzESOgImJN5Kef9zJWs4uoBu0tPML"
export FEISHU_WEBHOOK_VERIFICATION_TOKEN="your_verification_token"
export FEISHU_WEBHOOK_ENCRYPT_KEY="your_encrypt_key"
```

### 可选的环境变量
```bash
export CORS_ORIGINS="*"
export PORT=8000
export LOG_LEVEL="INFO"
```

## 📊 监控和日志

### 查看服务状态
```
# 健康检查
curl http://localhost:8000/health

# 版本信息
curl http://localhost:8000/version

# 飞书连接状态
curl http://localhost:8000/feishu/health
```

### 查看日志
```bash
# Codespace 终端中直接查看
tail -f logs/app.log

# 或查看系统日志
journalctl -u feishu-ai
```

## 🔒 安全性配置

### 1. 使用 GitHub Secrets
在 GitHub 仓库设置中配置敏感信息:
- `FEISHU_APP_SECRET`
- `FEISHU_WEBHOOK_ENCRYPT_KEY`

### 2. 限制访问
```bash
# 在启动脚本中设置
export CORS_ORIGINS="https://open.feishu.cn"
```

### 3. 定期更新令牌
建议每月更新一次:
1. 在飞书开放平台重新生成 App Secret
2. 更新 GitHub Secrets
3. 重启 Codespace

## 💰 免费额度说明

### GitHub Codespaces 免费计划
- **每月 60 小时** 免费使用时间
- **2 核 CPU, 8GB 内存, 32GB 存储**
- **足够 Feishu Webhook 24/7 运行**

### 使用建议
1. **自动停止**: Codespace 30分钟无活动会自动停止
2. **按需启动**: 需要时手动启动
3. **监控使用**: 在 GitHub 设置中查看使用量

## 🚨 故障排除

### 常见问题

#### 1. 端口被占用
```bash
# 检查端口占用
lsof -i :8000

# 使用其他端口
export PORT=8001
```

#### 2. 飞书连接失败
```bash
# 测试飞书 API 连接
curl http://localhost:8000/feishu/test
```

#### 3. Webhook 验证失败
1. 检查飞书平台配置的令牌和密钥
2. 确保环境变量正确设置
3. 查看日志中的错误信息

#### 4. Codespace 连接超时
1. 检查网络连接
2. 重启 Codespace
3. 联系 GitHub 支持

## 📞 支持

### 官方文档
- GitHub Codespaces: https://docs.github.com/codespaces
- FastAPI: https://fastapi.tiangolo.com
- 飞书开放平台: https://open.feishu.cn/document

### 社区支持
- GitHub Discussions
- 飞书开发者社区
- OpenClaw Discord

## 🎉 成功部署标志

1. ✅ Codespace 正常运行
2. ✅ 服务响应健康检查
3. ✅ 飞书 API 连接正常
4. ✅ Webhook 验证通过
5. ✅ 可以接收飞书消息

**恭喜！您的 Feishu AI Assistant 已在 GitHub Codespaces 上成功部署！** 🚀