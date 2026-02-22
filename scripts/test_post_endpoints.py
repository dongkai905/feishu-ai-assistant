#!/usr/bin/env python3
"""
测试POST端点，提供有效的请求体数据
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_post_calendar_event():
    """测试创建日历事件"""
    url = f"{BASE_URL}/calendar/events"
    event_data = {
        "summary": "测试会议",
        "description": "这是一个测试会议",
        "start_time": "2026-02-22T14:00:00",
        "end_time": "2026-02-22T15:00:00",
        "location": "会议室A",
        "attendees": ["user1@example.com"]
    }
    
    try:
        response = requests.post(url, json=event_data, timeout=10)
        print(f"测试创建日历事件:")
        print(f"  状态码: {response.status_code}")
        print(f"  响应: {response.json()}")
        print(f"  响应时间: {response.elapsed.total_seconds():.3f}s")
        return response.status_code == 200 or response.status_code == 201
    except Exception as e:
        print(f"  错误: {e}")
        return False

def test_post_task():
    """测试创建任务"""
    url = f"{BASE_URL}/tasks"
    task_data = {
        "title": "测试任务",
        "description": "这是一个测试任务",
        "due_date": "2026-02-23",
        "priority": 2,
        "status": "pending"
    }
    
    try:
        response = requests.post(url, json=task_data, timeout=10)
        print(f"测试创建任务:")
        print(f"  状态码: {response.status_code}")
        print(f"  响应: {response.json()}")
        print(f"  响应时间: {response.elapsed.total_seconds():.3f}s")
        return response.status_code == 200 or response.status_code == 201
    except Exception as e:
        print(f"  错误: {e}")
        return False

def main():
    print("=" * 60)
    print("POST端点详细测试")
    print(f"测试服务器: {BASE_URL}")
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = []
    
    # 测试日历事件创建
    print("\n1. 测试创建日历事件:")
    calendar_result = test_post_calendar_event()
    results.append(("POST /calendar/events", calendar_result))
    
    # 等待一下
    time.sleep(0.5)
    
    # 测试任务创建
    print("\n2. 测试创建任务:")
    task_result = test_post_task()
    results.append(("POST /tasks", task_result))
    
    # 打印摘要
    print("\n" + "=" * 60)
    print("测试摘要:")
    for endpoint, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {endpoint}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    success_rate = (passed / total) * 100 if total > 0 else 0
    
    print(f"\n通过数: {passed}/{total} ({success_rate:.1f}%)")
    
    if passed == total:
        print("🎉 所有POST端点测试通过！")
        return 0
    else:
        print("⚠️  部分POST端点测试失败")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)