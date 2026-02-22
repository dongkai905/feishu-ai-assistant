#!/usr/bin/env python3
"""
快速API测试脚本
验证所有18个API端点是否正常工作
"""

import requests
import json
import time
from typing import List, Dict, Any

BASE_URL = "http://localhost:8000"

def test_endpoint(method: str, endpoint: str, expected_status: int = 200) -> Dict[str, Any]:
    """测试单个API端点"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json={}, timeout=5)
        else:
            return {"success": False, "error": f"Unsupported method: {method}"}
        
        success = response.status_code == expected_status
        return {
            "success": success,
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "expected_status": expected_status,
            "response_time": response.elapsed.total_seconds(),
            "data": response.json() if success else None,
            "error": None if success else f"Expected {expected_status}, got {response.status_code}"
        }
    except Exception as e:
        return {
            "success": False,
            "endpoint": endpoint,
            "method": method,
            "error": str(e),
            "response_time": None
        }

def run_all_tests() -> Dict[str, Any]:
    """运行所有API测试"""
    tests = [
        # 基础API
        ("GET", "/", 200),
        ("GET", "/health", 200),
        ("GET", "/version", 200),
        ("GET", "/system/info", 200),
        
        # 日历API
        ("GET", "/calendar/calendars", 200),
        ("GET", "/calendar/today", 200),
        ("GET", "/calendar/upcoming", 200),
        ("GET", "/calendar/analysis", 200),
        ("GET", "/calendar/daily-summary", 200),
        ("POST", "/calendar/events", 200),  # 注意：POST请求需要有效数据
        
        # 任务API
        ("GET", "/tasks", 200),
        ("GET", "/tasks/overdue", 200),
        ("GET", "/tasks/due-today", 200),
        ("GET", "/tasks/prioritize", 200),
        ("GET", "/tasks/analysis", 200),
        ("GET", "/tasks/daily-todo", 200),
        ("POST", "/tasks", 200),  # 注意：POST请求需要有效数据
        
        # 其他API
        ("GET", "/documents", 200),
        ("GET", "/users", 200),
        ("GET", "/assistant/daily-report", 200),
    ]
    
    results = []
    total_tests = len(tests)
    passed_tests = 0
    failed_tests = 0
    total_response_time = 0
    
    print(f"🚀 开始测试 {total_tests} 个API端点...")
    print("=" * 60)
    
    for method, endpoint, expected_status in tests:
        print(f"测试: {method} {endpoint}...", end="", flush=True)
        result = test_endpoint(method, endpoint, expected_status)
        results.append(result)
        
        if result["success"]:
            passed_tests += 1
            if result["response_time"]:
                total_response_time += result["response_time"]
            print(f" ✅ 通过 ({result['response_time']:.3f}s)")
        else:
            failed_tests += 1
            print(f" ❌ 失败: {result.get('error', 'Unknown error')}")
        
        # 避免请求过快
        time.sleep(0.1)
    
    print("=" * 60)
    
    # 计算统计数据
    avg_response_time = total_response_time / passed_tests if passed_tests > 0 else 0
    success_rate = (passed_tests / total_tests) * 100
    
    summary = {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "success_rate": success_rate,
        "avg_response_time": avg_response_time,
        "total_response_time": total_response_time,
        "results": results
    }
    
    # 打印摘要
    print(f"📊 测试摘要:")
    print(f"  总测试数: {total_tests}")
    print(f"  通过数: {passed_tests}")
    print(f"  失败数: {failed_tests}")
    print(f"  成功率: {success_rate:.1f}%")
    print(f"  平均响应时间: {avg_response_time:.3f}秒")
    print(f"  总响应时间: {total_response_time:.3f}秒")
    
    if success_rate == 100:
        print("🎉 所有API端点测试通过！系统运行正常。")
    elif success_rate >= 90:
        print("👍 大部分API端点测试通过，系统基本正常。")
    else:
        print("⚠️  部分API端点测试失败，需要检查。")
    
    return summary

def save_test_report(summary: Dict[str, Any]):
    """保存测试报告"""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    report_file = f"test_report_{timestamp}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"📄 测试报告已保存到: {report_file}")
    return report_file

def main():
    """主函数"""
    print("=" * 60)
    print("飞书AI助手API测试脚本")
    print(f"测试服务器: {BASE_URL}")
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # 运行所有测试
        summary = run_all_tests()
        
        # 保存测试报告
        report_file = save_test_report(summary)
        
        # 返回退出码
        if summary["success_rate"] == 100:
            return 0
        else:
            return 1
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return 2

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)