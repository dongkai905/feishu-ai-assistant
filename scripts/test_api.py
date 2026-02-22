#!/usr/bin/env python3
"""
飞书AI助手API测试脚本
测试所有API端点功能
"""
import sys
import os
import time
import json
import logging
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API配置
BASE_URL = "http://localhost:8000"
TIMEOUT = 30


class APITester:
    """API测试器"""
    
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.results = []
        self.start_time = None
        self.end_time = None
    
    def run_all_tests(self):
        """运行所有测试"""
        self.start_time = datetime.now()
        logger.info("=" * 60)
        logger.info("开始飞书AI助手API测试")
        logger.info(f"测试时间: {self.start_time}")
        logger.info(f"API地址: {self.base_url}")
        logger.info("=" * 60)
        
        # 测试基础API
        self.test_basic_apis()
        
        # 测试日历API
        self.test_calendar_apis()
        
        # 测试任务API
        self.test_task_apis()
        
        # 测试其他API
        self.test_other_apis()
        
        # 测试智能助手API
        self.test_assistant_apis()
        
        self.end_time = datetime.now()
        self.print_summary()
    
    def test_basic_apis(self):
        """测试基础API"""
        logger.info("\n" + "=" * 60)
        logger.info("测试基础API")
        logger.info("=" * 60)
        
        # 测试根端点
        self.test_endpoint("GET", "/", "根端点")
        
        # 测试健康检查
        self.test_endpoint("GET", "/health", "健康检查")
        
        # 测试版本信息
        self.test_endpoint("GET", "/version", "版本信息")
        
        # 测试系统信息
        self.test_endpoint("GET", "/system/info", "系统信息")
    
    def test_calendar_apis(self):
        """测试日历API"""
        logger.info("\n" + "=" * 60)
        logger.info("测试日历API")
        logger.info("=" * 60)
        
        # 测试获取日历列表
        self.test_endpoint("GET", "/calendar/calendars", "获取日历列表")
        
        # 测试获取今天事件
        self.test_endpoint("GET", "/calendar/today", "获取今天事件")
        
        # 测试获取即将发生事件
        self.test_endpoint("GET", "/calendar/upcoming?hours=24", "获取即将发生事件")
        
        # 测试分析日程
        self.test_endpoint("GET", "/calendar/analysis", "分析日程")
        
        # 测试每日摘要
        self.test_endpoint("GET", "/calendar/daily-summary", "每日摘要")
        
        # 测试创建会议（需要参数，先跳过或使用模拟数据）
        # self.test_endpoint("POST", "/calendar/meeting", "创建会议")
    
    def test_task_apis(self):
        """测试任务API"""
        logger.info("\n" + "=" * 60)
        logger.info("测试任务API")
        logger.info("=" * 60)
        
        # 测试获取任务列表
        self.test_endpoint("GET", "/tasks", "获取任务列表")
        
        # 测试获取过期任务
        self.test_endpoint("GET", "/tasks/overdue", "获取过期任务")
        
        # 测试获取今天到期任务
        self.test_endpoint("GET", "/tasks/due-today", "获取今天到期任务")
        
        # 测试智能排序
        self.test_endpoint("GET", "/tasks/prioritize", "智能排序任务")
        
        # 测试分析工作负载
        self.test_endpoint("GET", "/tasks/analysis", "分析工作负载")
        
        # 测试每日待办
        self.test_endpoint("GET", "/tasks/daily-todo", "每日待办清单")
        
        # 测试创建任务（需要参数，先跳过）
        # self.test_endpoint("POST", "/tasks", "创建任务")
    
    def test_other_apis(self):
        """测试其他API"""
        logger.info("\n" + "=" * 60)
        logger.info("测试其他API")
        logger.info("=" * 60)
        
        # 测试获取文档列表
        self.test_endpoint("GET", "/documents", "获取文档列表")
        
        # 测试获取用户列表
        self.test_endpoint("GET", "/users", "获取用户列表")
    
    def test_assistant_apis(self):
        """测试智能助手API"""
        logger.info("\n" + "=" * 60)
        logger.info("测试智能助手API")
        logger.info("=" * 60)
        
        # 测试每日报告
        self.test_endpoint("GET", "/assistant/daily-report", "每日综合报告")
    
    def test_endpoint(self, method, endpoint, description):
        """测试单个端点"""
        try:
            url = f"{self.base_url}{endpoint}"
            logger.info(f"测试: {description}")
            logger.info(f"URL: {method} {url}")
            
            start_time = time.time()
            
            if method == "GET":
                response = requests.get(url, timeout=TIMEOUT)
            elif method == "POST":
                response = requests.post(url, timeout=TIMEOUT)
            elif method == "PUT":
                response = requests.put(url, timeout=TIMEOUT)
            elif method == "DELETE":
                response = requests.delete(url, timeout=TIMEOUT)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            response_time = time.time() - start_time
            
            # 检查响应
            if response.status_code == 200:
                try:
                    data = response.json()
                    success = data.get("success", True)
                    
                    if success:
                        status = "✅ 成功"
                        logger.info(f"  状态: {status} ({response.status_code})")
                        logger.info(f"  响应时间: {response_time:.3f}秒")
                        
                        # 记录成功结果
                        self.results.append({
                            "endpoint": endpoint,
                            "method": method,
                            "description": description,
                            "status": "success",
                            "response_time": response_time,
                            "status_code": response.status_code,
                        })
                    else:
                        status = "⚠️ 业务失败"
                        logger.warning(f"  状态: {status} ({response.status_code})")
                        logger.warning(f"  错误: {data.get('error', '未知错误')}")
                        
                        self.results.append({
                            "endpoint": endpoint,
                            "method": method,
                            "description": description,
                            "status": "business_failure",
                            "response_time": response_time,
                            "status_code": response.status_code,
                            "error": data.get("error"),
                        })
                
                except json.JSONDecodeError:
                    status = "⚠️ JSON解析失败"
                    logger.warning(f"  状态: {status} ({response.status_code})")
                    logger.warning(f"  响应内容: {response.text[:100]}...")
                    
                    self.results.append({
                        "endpoint": endpoint,
                        "method": method,
                        "description": description,
                        "status": "json_error",
                        "response_time": response_time,
                        "status_code": response.status_code,
                        "response_text": response.text[:100],
                    })
            
            else:
                status = "❌ HTTP错误"
                logger.error(f"  状态: {status} ({response.status_code})")
                logger.error(f"  响应: {response.text[:200]}...")
                
                self.results.append({
                    "endpoint": endpoint,
                    "method": method,
                    "description": description,
                    "status": "http_error",
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "response_text": response.text[:200],
                })
        
        except requests.exceptions.Timeout:
            status = "⏰ 超时"
            logger.error(f"  状态: {status} (超过{TIMEOUT}秒)")
            
            self.results.append({
                "endpoint": endpoint,
                "method": method,
                "description": description,
                "status": "timeout",
                "response_time": TIMEOUT,
            })
        
        except requests.exceptions.ConnectionError:
            status = "🔌 连接失败"
            logger.error(f"  状态: {status} (无法连接到服务器)")
            
            self.results.append({
                "endpoint": endpoint,
                "method": method,
                "description": description,
                "status": "connection_error",
            })
        
        except Exception as e:
            status = "💥 异常"
            logger.error(f"  状态: {status}")
            logger.error(f"  异常: {e}")
            
            self.results.append({
                "endpoint": endpoint,
                "method": method,
                "description": description,
                "status": "exception",
                "error": str(e),
            })
        
        finally:
            logger.info("")  # 空行分隔
    
    def print_summary(self):
        """打印测试摘要"""
        logger.info("\n" + "=" * 60)
        logger.info("测试摘要")
        logger.info("=" * 60)
        
        total_tests = len(self.results)
        success_tests = len([r for r in self.results if r["status"] == "success"])
        failed_tests = total_tests - success_tests
        
        # 计算平均响应时间
        response_times = [r.get("response_time", 0) for r in self.results if r.get("response_time")]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        logger.info(f"测试总数: {total_tests}")
        logger.info(f"成功: {success_tests}")
        logger.info(f"失败: {failed_tests}")
        logger.info(f"成功率: {success_tests/total_tests*100:.1f}%")
        logger.info(f"平均响应时间: {avg_response_time:.3f}秒")
        logger.info(f"测试开始时间: {self.start_time}")
        logger.info(f"测试结束时间: {self.end_time}")
        logger.info(f"测试总耗时: {(self.end_time - self.start_time).total_seconds():.1f}秒")
        
        # 打印失败详情
        if failed_tests > 0:
            logger.info("\n失败详情:")
            for result in self.results:
                if result["status"] != "success":
                    logger.info(f"  - {result['description']} ({result['method']} {result['endpoint']})")
                    logger.info(f"    状态: {result['status']}")
                    if result.get('error'):
                        logger.info(f"    错误: {result['error']}")
                    if result.get('response_text'):
                        logger.info(f"    响应: {result['response_text']}")
        
        # 保存测试结果
        self.save_results()
    
    def save_results(self):
        """保存测试结果到文件"""
        try:
            results_dir = os.path.join(os.path.dirname(__file__), "..", "test_results")
            os.makedirs(results_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(results_dir, f"api_test_{timestamp}.json")
            
            report = {
                "metadata": {
                    "project": "飞书AI助手",
                    "test_time": self.start_time.isoformat() if self.start_time else None,
                    "duration_seconds": (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else None,
                    "base_url": self.base_url,
                },
                "summary": {
                    "total_tests": len(self.results),
                    "success_tests": len([r for r in self.results if r["status"] == "success"]),
                    "failed_tests": len([r for r in self.results if r["status"] != "success"]),
                    "success_rate": len([r for r in self.results if r["status"] == "success"]) / len(self.results) * 100 if self.results else 0,
                },
                "results": self.results,
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"测试结果已保存到: {filename}")
        
        except Exception as e:
            logger.error(f"保存测试结果失败: {e}")


def check_server_running():
    """检查服务器是否运行"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def main():
    """主函数"""
    # 检查服务器是否运行
    if not check_server_running():
        logger.error("服务器未运行！请先启动服务器：")
        logger.error("  cd feishu-ai-assistant")
        logger.error("  python3 src/main.py")
        logger.error("或")
        logger.error("  ./start.sh")
        return
    
    # 运行测试
    tester = APITester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()