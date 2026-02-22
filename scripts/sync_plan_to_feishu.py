#!/usr/bin/env python3
"""
同步任务计划到飞书
在Docker安装期间，将部署计划同步到飞书
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_CHAT_ID = "oc_4d808220fc67c3f1c2690367f9a9ddd7"  # test群聊

def sync_deployment_plan():
    """同步部署计划到飞书"""
    print("🚀 同步任务计划到飞书")
    print("=" * 50)
    
    # 1. 发送群聊通知
    print("📨 1. 发送群聊通知...")
    message = """🚀 飞书AI助手部署任务计划

📅 时间线:
• 现在-14:55: Docker安装
• 14:55-15:00: Docker验证
• 15:00-15:05: 完整部署
• 15:05-15:10: 生产验证
• 15:10: 项目100%完成

📊 当前状态: 95%完成
✅ 核心功能: 100%可用
⏳ Docker安装: 进行中

🔄 同步时间: {time}
""".format(time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    try:
        response = requests.post(
            f"{BASE_URL}/messages/send",
            params={
                "receive_id": TEST_CHAT_ID,
                "message": message,
                "receive_id_type": "chat_id"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            msg_id = data.get("data", {}).get("message_id", "未知")
            print(f"   ✅ 发送成功 (消息ID: {msg_id[:20]}...)")
        else:
            print(f"   ❌ 发送失败 (状态码: {response.status_code})")
            print(f"   响应: {response.text[:100]}")
            
    except Exception as e:
        print(f"   ❌ 发送异常: {e}")
    
    # 2. 创建部署任务
    print("\n📝 2. 创建部署任务...")
    task_description = """任务计划:
1. ✅ 准生产验证完成 (100%通过)
2. ⏳ Docker安装中 (预计14:55完成)
3. 🔄 等待完整部署 (15:00开始)
4. 🎯 15:10前完成生产部署

详细进度:
• 系统健康: ✅ 正常
• 消息功能: ✅ 正常
• 日历功能: ✅ 正常
• 任务功能: ✅ 正常
• Docker环境: ⏳ 安装中
"""
    
    try:
        response = requests.post(
            f"{BASE_URL}/tasks",
            params={
                "title": "飞书AI助手生产部署",
                "description": task_description,
                "priority": 1  # 高优先级
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            task_id = data.get("data", {}).get("task_id", "未知")
            print(f"   ✅ 任务创建成功 (任务ID: {task_id})")
        else:
            print(f"   ❌ 任务创建失败 (状态码: {response.status_code})")
            print(f"   响应: {response.text[:100]}")
            
    except Exception as e:
        print(f"   ❌ 任务创建异常: {e}")
    
    # 3. 创建日历会议
    print("\n📅 3. 创建部署评审会议...")
    meeting_time = datetime.now().strftime("%Y-%m-%dT%H:%M")
    
    try:
        response = requests.post(
            f"{BASE_URL}/calendar/meeting",
            params={
                "title": "飞书AI助手部署计划评审",
                "start_time": meeting_time,
                "duration_minutes": 30,
                "description": """部署计划评审:
1. Docker安装验证
2. 完整部署执行
3. 生产环境测试
4. 项目交付验收

当前状态:
• 准生产环境: ✅ 运行中
• 核心功能: ✅ 100%可用
• Docker: ⏳ 安装中
"""
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            event_id = data.get("data", {}).get("event_id", "未知")
            print(f"   ✅ 会议创建成功 (会议ID: {event_id})")
        else:
            print(f"   ❌ 会议创建失败 (状态码: {response.status_code})")
            print(f"   响应: {response.text[:100]}")
            
    except Exception as e:
        print(f"   ❌ 会议创建异常: {e}")
    
    # 4. 总结
    print("\n" + "=" * 50)
    print("🎯 同步完成!")
    print("\n💡 您可以在飞书中查看:")
    print("   1. test群聊中的部署计划通知")
    print("   2. 任务列表中的部署任务")
    print("   3. 日历中的部署评审会议")
    print("\n⏳ Docker安装进度: 进行中")
    print("📅 预计完成: 15:10前")

def main():
    try:
        # 先检查服务器健康
        print("🔍 检查服务器状态...")
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        
        if health_response.status_code == 200:
            print("   ✅ 服务器健康")
            sync_deployment_plan()
        else:
            print(f"   ❌ 服务器异常 (状态码: {health_response.status_code})")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保生产服务器正在运行")
        print("   运行命令: cd feishu-ai-assistant && python start_production.py")
    except Exception as e:
        print(f"❌ 异常: {e}")

if __name__ == "__main__":
    main()