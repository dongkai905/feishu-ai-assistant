#!/usr/bin/env python3
"""
飞书AI助手 - 生产环境最终测试
在部署前验证所有关键功能
"""

import requests
import json
import time
from datetime import datetime, timedelta

class ProductionTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        
    def log_test(self, name, success, details=""):
        """记录测试结果"""
        status = "✅" if success else "❌"
        self.test_results.append({
            "name": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"   {status} {name}: {'通过' if success else '失败'} {details}")
        return success
    
    def test_health_endpoints(self):
        """测试健康检查端点"""
        print("\n🏥 1. 健康检查端点测试")
        
        endpoints = [
            ("/", "根端点"),
            ("/health", "健康检查"),
            ("/version", "版本信息"),
            ("/docs", "API文档"),
        ]
        
        all_passed = True
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                success = response.status_code == 200
                details = f"状态码: {response.status_code}"
                if not self.log_test(f"GET {name}", success, details):
                    all_passed = False
            except Exception as e:
                if not self.log_test(f"GET {name}", False, f"连接失败: {e}"):
                    all_passed = False
        
        return all_passed
    
    def test_feishu_connection(self):
        """测试飞书连接"""
        print("\n🔗 2. 飞书API连接测试")
        
        # 测试日历连接
        try:
            response = requests.get(f"{self.base_url}/calendar/today", timeout=10)
            success = response.status_code == 200
            details = f"状态码: {response.status_code}"
            if success:
                data = response.json()
                details += f", 今日事件: {data.get('count', 0)}个"
            return self.log_test("飞书日历连接", success, details)
        except Exception as e:
            return self.log_test("飞书日历连接", False, f"连接失败: {e}")
    
    def test_message_function(self):
        """测试消息发送功能"""
        print("\n💬 3. 消息发送功能测试")
        
        # 使用test群聊进行测试
        params = {
            "receive_id": "oc_4d808220fc67c3f1c2690367f9a9ddd7",  # test群聊
            "message": f"🚀 生产环境最终测试消息\n\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n系统状态: 生产部署前验证\n功能: 消息发送测试",
            "receive_id_type": "chat_id"
        }
        
        try:
            response = requests.post(f"{self.base_url}/messages/send", params=params, timeout=15)
            success = response.status_code == 200
            details = f"状态码: {response.status_code}"
            if success:
                data = response.json()
                details += f", 消息ID: {data.get('data', {}).get('message_id', '未知')}"
            return self.log_test("消息发送", success, details)
        except Exception as e:
            return self.log_test("消息发送", False, f"发送失败: {e}")
    
    def test_calendar_function(self):
        """测试日历功能"""
        print("\n📅 4. 日历功能测试")
        
        # 创建测试会议
        meeting_params = {
            "title": "生产环境测试会议",
            "start_time": (datetime.now() + timedelta(hours=2)).isoformat(),
            "duration_minutes": 30,
            "description": "生产环境最终测试创建的会议"
        }
        
        try:
            response = requests.post(f"{self.base_url}/calendar/meeting", params=meeting_params, timeout=15)
            success = response.status_code == 200
            details = f"状态码: {response.status_code}"
            if success:
                data = response.json()
                details += f", 会议ID: {data.get('data', {}).get('event_id', '未知')}"
            return self.log_test("创建会议", success, details)
        except Exception as e:
            return self.log_test("创建会议", False, f"创建失败: {e}")
    
    def test_task_function(self):
        """测试任务功能"""
        print("\n📝 5. 任务功能测试")
        
        # 创建测试任务
        task_params = {
            "title": "生产环境测试任务",
            "description": "生产环境最终测试创建的任务",
            "priority": 2
        }
        
        try:
            response = requests.post(f"{self.base_url}/tasks", params=task_params, timeout=15)
            success = response.status_code == 200
            details = f"状态码: {response.status_code}"
            if success:
                data = response.json()
                details += f", 任务ID: {data.get('data', {}).get('task_id', '未知')}"
            return self.log_test("创建任务", success, details)
        except Exception as e:
            return self.log_test("创建任务", False, f"创建失败: {e}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 飞书AI助手 - 生产环境最终测试")
        print("=" * 60)
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试地址: {self.base_url}")
        print()
        
        # 运行所有测试
        tests = [
            self.test_health_endpoints,
            self.test_feishu_connection,
            self.test_message_function,
            self.test_calendar_function,
            self.test_task_function,
        ]
        
        results = []
        for test_func in tests:
            try:
                result = test_func()
                results.append(result)
            except Exception as e:
                print(f"   ❌ 测试异常: {e}")
                results.append(False)
        
        # 汇总结果
        print()
        print("=" * 60)
        print("📊 测试结果汇总:")
        
        passed = sum(1 for r in results if r)
        total = len(results)
        
        for i, result in enumerate(results):
            status = "✅" if result else "❌"
            test_name = [
                "健康检查端点",
                "飞书API连接", 
                "消息发送功能",
                "日历功能",
                "任务功能"
            ][i]
            print(f"   {status} {test_name}")
        
        print()
        print(f"通过率: {passed}/{total} ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 所有测试通过! 系统准备就绪，可以开始生产部署!")
            return True
        else:
            print(f"⚠️  {total-passed} 个测试失败，请修复后再进行生产部署")
            return False
    
    def generate_report(self):
        """生成测试报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "total_tests": len(self.test_results),
            "passed_tests": sum(1 for r in self.test_results if r["success"]),
            "failed_tests": sum(1 for r in self.test_results if not r["success"]),
            "results": self.test_results
        }
        
        # 保存报告
        filename = f"production_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 测试报告已保存: {filename}")
        return report

if __name__ == "__main__":
    # 运行测试
    tester = ProductionTester()
    
    try:
        success = tester.run_all_tests()
        
        # 生成报告
        report = tester.generate_report()
        
        # 返回退出码
        exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        exit(1)
    except Exception as e:
        print(f"\n❌ 测试执行异常: {e}")
        exit(1)