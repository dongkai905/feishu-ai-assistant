#!/usr/bin/env python3
"""
修复API测试问题
1. POST /calendar/meeting (不是/calendar/events)
2. POST /tasks 需要title参数
"""

import requests
import json
from datetime import datetime, timedelta

def test_calendar_meeting():
    """测试创建会议"""
    print("📅 测试 POST /calendar/meeting")
    
    # 构建查询参数
    params = {
        "title": "测试会议 - API修复验证",
        "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
        "duration_minutes": 30,
        "description": "这是API修复测试创建的会议",
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/calendar/meeting",
            params=params,
            timeout=10
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 创建会议成功!")
            print(f"   会议ID: {result.get('data', {}).get('event_id', '未知')}")
            print(f"   标题: {result.get('data', {}).get('summary', '未知')}")
            return True
        elif response.status_code == 422:
            print(f"   ❌ 参数验证失败: {response.text}")
            return False
        else:
            print(f"   ❌ 请求失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
        return False

def test_create_task():
    """测试创建任务"""
    print("\n📝 测试 POST /tasks")
    
    # 构建查询参数
    params = {
        "title": "API修复测试任务",
        "description": "这是API修复测试创建的任务",
        "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "priority": 2  # 中等优先级
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/tasks",
            params=params,
            timeout=10
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 创建任务成功!")
            print(f"   任务ID: {result.get('data', {}).get('task_id', '未知')}")
            print(f"   标题: {result.get('data', {}).get('summary', '未知')}")
            return True
        elif response.status_code == 422:
            print(f"   ❌ 参数验证失败: {response.text}")
            return False
        else:
            print(f"   ❌ 请求失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
        return False

def test_all_endpoints():
    """测试所有端点"""
    print("🚀 Feishu AI Assistant - API端点修复测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 测试日历会议创建
    calendar_success = test_calendar_meeting()
    
    # 测试任务创建
    task_success = test_create_task()
    
    print()
    print("=" * 60)
    print("📊 测试结果汇总:")
    print(f"   POST /calendar/meeting: {'✅ 通过' if calendar_success else '❌ 失败'}")
    print(f"   POST /tasks: {'✅ 通过' if task_success else '❌ 失败'}")
    
    if calendar_success and task_success:
        print("\n🎉 所有API端点修复成功!")
        print("   系统API功能完整度: 100%")
    else:
        print("\n🔧 需要进一步修复:")
        if not calendar_success:
            print("   - 检查日历会议创建逻辑")
        if not task_success:
            print("   - 检查任务创建逻辑")
    
    return calendar_success and task_success

def quick_health_check():
    """快速健康检查"""
    print("\n🏥 系统健康检查:")
    
    endpoints = [
        ("/", "根端点", "GET"),
        ("/health", "健康检查", "GET"),
        ("/version", "版本信息", "GET"),
        ("/calendar/today", "今日日历", "GET"),
        ("/tasks", "任务列表", "GET"),
        ("/docs", "API文档", "GET"),  # 替换消息发送，检查文档
    ]
    
    all_healthy = True
    for endpoint, name, method in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            elif method == "POST":
                response = requests.post(f"http://localhost:8000{endpoint}", timeout=5)
            else:
                print(f"   ⚠️ {name}: 未知方法 {method}")
                continue
                
            status = "✅" if response.status_code == 200 else "⚠️"
            print(f"   {status} {name}: {response.status_code}")
            if response.status_code != 200:
                all_healthy = False
        except Exception as e:
            print(f"   ❌ {name}: 连接失败 ({e})")
            all_healthy = False
    
    return all_healthy

if __name__ == "__main__":
    # 先检查系统健康
    if not quick_health_check():
        print("\n⚠️ 系统健康检查失败，请先确保应用正常运行")
        exit(1)
    
    # 运行API测试
    success = test_all_endpoints()
    
    if success:
        print("\n🚀 系统准备就绪，可以开始生产部署!")
    else:
        print("\n🔧 请修复失败的API端点后再进行生产部署")
    
    exit(0 if success else 1)