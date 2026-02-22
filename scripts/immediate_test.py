#!/usr/bin/env python3
"""
立即测试脚本 - 在Docker安装期间体验核心功能
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_CHAT_ID = "oc_4d808220fc67c3f1c2690367f9a9ddd7"  # test群聊

def print_section(title):
    print(f"\n{'='*60}")
    print(f"📌 {title}")
    print('='*60)

def test_endpoint(name, method="GET", endpoint="", params=None):
    """测试API端点"""
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        else:  # POST
            response = requests.post(url, params=params, timeout=10)
        
        success = response.status_code == 200
        status = "✅" if success else "❌"
        
        print(f"   {status} {name}: ", end="")
        
        if success:
            data = response.json()
            if "message_id" in str(data):
                print(f"成功 (消息ID: {data.get('data', {}).get('message_id', '未知')[:20]}...)")
            elif "event_id" in str(data):
                print(f"成功 (会议ID: {data.get('data', {}).get('event_id', '未知')})")
            elif "task_id" in str(data):
                print(f"成功 (任务ID: {data.get('data', {}).get('task_id', '未知')})")
            else:
                print("成功")
        else:
            print(f"失败 (状态码: {response.status_code})")
        
        return success
        
    except Exception as e:
        print(f"   ❌ {name}: 连接失败 - {e}")
        return False

def main():
    print("🚀 飞书AI助手 - 立即体验")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"地址: {BASE_URL}")
    
    # 1. 系统健康检查
    print_section("1. 系统健康检查")
    test_endpoint("根端点", "GET", "/")
    test_endpoint("健康检查", "GET", "/health")
    test_endpoint("版本信息", "GET", "/version")
    
    # 2. 发送欢迎消息
    print_section("2. 发送测试消息到'test'群聊")
    message = f"🎉 飞书AI助手立即体验测试\n\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n状态: 准生产环境运行中\n功能: 消息/日历/任务管理"
    test_endpoint("发送文本消息", "POST", "/messages/send", {
        "receive_id": TEST_CHAT_ID,
        "message": message,
        "receive_id_type": "chat_id"
    })
    
    # 3. 日历功能
    print_section("3. 日历功能测试")
    test_endpoint("查看今日日历", "GET", "/calendar/today")
    
    # 创建测试会议
    meeting_time = datetime.now().strftime('%Y-%m-%dT%H:%M')
    test_endpoint("创建测试会议", "POST", "/calendar/meeting", {
        "title": "立即体验测试会议",
        "start_time": meeting_time,
        "duration_minutes": 30,
        "description": "立即体验脚本创建的测试会议"
    })
    
    # 4. 任务功能
    print_section("4. 任务功能测试")
    test_endpoint("查看任务列表", "GET", "/tasks")
    
    test_endpoint("创建测试任务", "POST", "/tasks", {
        "title": "立即体验测试任务",
        "description": "立即体验脚本创建的测试任务",
        "priority": 2
    })
    
    # 5. 高级功能
    print_section("5. 高级功能预览")
    test_endpoint("系统信息", "GET", "/info")
    test_endpoint("本周日历", "GET", "/calendar/week")
    
    # 6. 总结
    print_section("🎯 立即行动建议")
    print("💡 您现在可以:")
    print("   1. 访问API文档: http://localhost:8000/docs")
    print("   2. 在'test'群聊中发送更多消息")
    print("   3. 创建更多会议和任务")
    print("   4. 测试不同的API端点")
    
    print("\n⏳ Docker安装进度:")
    print("   - 正在下载Docker Desktop")
    print("   - 预计完成: 14:55 GMT+8")
    print("   - 然后执行完整容器化部署")
    
    print("\n📊 项目状态: 90%完成 → 等待Docker安装")
    print("🎯 最终目标: 15:10前完成100%生产部署")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")