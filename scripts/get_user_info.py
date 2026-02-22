#!/usr/bin/env python3
"""
获取当前飞书用户信息的脚本
"""

import os
import sys
import json
from datetime import datetime

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from feishu_client import FeishuClient
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请确保在feishu-ai-assistant目录下运行此脚本")
    sys.exit(1)

def main():
    print("🔍 获取飞书用户信息")
    print("=" * 60)
    
    # 检查环境变量
    app_id = os.getenv('FEISHU_APP_ID')
    app_secret = os.getenv('FEISHU_APP_SECRET')
    
    if not app_id or not app_secret:
        print("❌ 环境变量未设置")
        print("请先设置环境变量:")
        print("  export FEISHU_APP_ID=您的AppID")
        print("  export FEISHU_APP_SECRET=您的AppSecret")
        print("或者运行: source .env.local")
        return
    
    print(f"应用ID: {app_id[:10]}...")
    print(f"应用密钥: {'*' * len(app_secret)}")
    print()
    
    try:
        # 初始化飞书客户端
        print("🔄 初始化飞书客户端...")
        feishu = FeishuClient()
        print("✅ 飞书客户端初始化成功")
        print()
        
        # 尝试获取当前用户信息
        print("📋 尝试获取用户信息...")
        print("注: 需要实现获取用户信息的API方法")
        print()
        
        # 显示应用权限信息
        print("🔐 应用权限检查:")
        print("1. 发送消息权限: 需要 'im:message' 权限")
        print("2. 用户信息权限: 需要 'contact:user:read' 权限")
        print("3. 群聊权限: 需要 'im:chat:read' 权限")
        print()
        
        # 建议
        print("💡 如何获取正确的ID:")
        print()
        print("方法A: 通过飞书开放平台")
        print("1. 登录 https://open.feishu.cn")
        print("2. 进入'开发者后台'")
        print("3. 选择您的应用")
        print("4. 进入'权限管理' -> '用户与组织' -> '用户管理'")
        print("5. 找到您的用户，查看open_id/user_id")
        print()
        print("方法B: 通过飞书应用")
        print("1. 打开飞书应用")
        print("2. 点击您的头像")
        print("3. 查看'用户ID' (通常是数字)")
        print()
        print("方法C: 创建测试群聊")
        print("1. 在飞书中创建测试群聊")
        print("2. 右键群聊 -> '获取群聊ID'")
        print("3. 使用chat_id发送消息")
        print()
        print("方法D: 使用邮箱")
        print("1. 使用您的飞书邮箱地址")
        print("2. receive_id_type设置为'email'")
        print()
        
        print("📝 ID格式参考:")
        print("- open_id: ou_da5****************dfe (部分隐藏)")
        print("- user_id: 64*******87 (数字)")
        print("- chat_id: oc_xxxxxxxxxx (群聊ID)")
        print("- email: yourname@company.com")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        print(f"错误类型: {type(e).__name__}")

if __name__ == "__main__":
    main()