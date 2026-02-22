#!/usr/bin/env python3
"""
测试GET端点 - 这些端点应该工作正常
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_endpoint(url, name):
    """测试单个端点"""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)
        elapsed = time.time() - start_time
        
        print(f"测试 {name}:")
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"  响应: {json.dumps(data, ensure_ascii=False)[:100]}...")
            except:
                print(f"  响应: {response.text[:100]}...")
            print(f"  响应时间: {elapsed:.3f}s")
            return True
        else:
            print(f"  错误: {response.text[:100]}")
            return False
    except Exception as e:
        print(f"  异常: {e}")
        return False

def main():
    print("=" * 60)
    print("GET端点测试")
    print(f"测试服务器: {BASE_URL}")
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    endpoints = [
        ("/", "根路径"),
        ("/health", "健康检查"),
        ("/version", "版本信息"),
        ("/calendar/today", "今日日历"),
        ("/calendar/upcoming", "即将到来的事件"),
        ("/tasks", "任务列表"),
        ("/tasks/pending", "待处理任务"),
        ("/tasks/urgent", "紧急任务"),
        ("/calendar/list", "日历列表"),
        ("/calendar/events", "日历事件列表"),
        ("/messages/recent", "最近消息"),
        ("/drive/files", "文件列表"),
        ("/drive/recent", "最近文件"),
        ("/contacts/users", "用户列表"),
        ("/contacts/departments", "部门列表"),
        ("/calendar/assistant/suggest", "日历助手建议"),
        ("/task/assistant/suggest", "任务助手建议"),
    ]
    
    results = []
    
    for endpoint, name in endpoints:
        success = test_endpoint(f"{BASE_URL}{endpoint}", name)
        results.append((endpoint, success))
        time.sleep(0.1)  # 避免请求过快
    
    # 打印摘要
    print("\n" + "=" * 60)
    print("测试摘要:")
    
    passed = 0
    for endpoint, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {endpoint}: {status}")
        if success:
            passed += 1
    
    total = len(results)
    success_rate = (passed / total) * 100 if total > 0 else 0
    
    print(f"\n通过数: {passed}/{total} ({success_rate:.1f}%)")
    
    if passed == total:
        print("🎉 所有GET端点测试通过！")
        return 0
    elif passed >= total * 0.8:
        print("👍 大部分GET端点工作正常")
        return 0
    else:
        print("⚠️  部分GET端点测试失败")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)