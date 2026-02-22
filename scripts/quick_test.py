#!/usr/bin/env python3
"""
快速测试飞书AI助手核心功能
"""
import sys
import os
import time
import json
import logging
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_feishu_client():
    """测试飞书客户端"""
    try:
        from src.feishu_client import FeishuClient
        
        logger.info("测试飞书客户端...")
        
        # 创建客户端
        client = FeishuClient()
        
        # 测试连接
        connected = client.test_connection()
        
        if connected:
            logger.info("✅ 飞书API连接测试成功")
            
            # 获取系统信息
            system_info = client.get_system_info()
            logger.info(f"系统信息: {json.dumps(system_info, indent=2, ensure_ascii=False)}")
            
            # 测试获取日历
            calendars = client.get_calendars()
            logger.info(f"✅ 获取到 {len(calendars)} 个日历")
            
            # 测试获取用户
            users = client.get_users()
            logger.info(f"✅ 获取到 {len(users)} 个用户")
            
            # 测试获取文档
            documents = client.get_documents()
            logger.info(f"✅ 获取到 {len(documents)} 个文档")
            
            return True
        else:
            logger.error("❌ 飞书API连接测试失败")
            return False
    
    except Exception as e:
        logger.error(f"❌ 飞书客户端测试异常: {e}")
        return False

def test_calendar_assistant():
    """测试日历助手"""
    try:
        from src.calendar_assistant import CalendarAssistant
        
        logger.info("测试日历助手...")
        
        # 创建助手
        assistant = CalendarAssistant()
        
        # 测试获取今天事件
        today_events = assistant.get_today_events()
        logger.info(f"✅ 获取到今天 {len(today_events)} 个事件")
        
        # 测试获取即将发生事件
        upcoming_events = assistant.get_upcoming_events(24)
        logger.info(f"✅ 获取到未来24小时内 {len(upcoming_events)} 个事件")
        
        # 测试分析日程
        analysis = assistant.analyze_schedule()
        logger.info(f"✅ 日程分析完成: {analysis.get('total_events', 0)} 个事件")
        
        # 测试每日摘要
        summary = assistant.get_daily_summary()
        logger.info(f"✅ 每日摘要生成完成")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ 日历助手测试异常: {e}")
        return False

def test_task_assistant():
    """测试任务助手"""
    try:
        from src.task_assistant import TaskAssistant
        
        logger.info("测试任务助手...")
        
        # 创建助手
        assistant = TaskAssistant()
        
        # 测试获取任务
        tasks = assistant.get_my_tasks()
        logger.info(f"✅ 获取到 {len(tasks)} 个任务")
        
        # 测试获取过期任务
        overdue_tasks = assistant.get_overdue_tasks()
        logger.info(f"✅ 获取到 {len(overdue_tasks)} 个过期任务")
        
        # 测试获取今天到期任务
        due_today = assistant.get_tasks_due_today()
        logger.info(f"✅ 获取到 {len(due_today)} 个今天到期任务")
        
        # 测试分析工作负载
        analysis = assistant.analyze_workload()
        logger.info(f"✅ 工作负载分析完成")
        
        # 测试智能排序
        prioritized = assistant.prioritize_tasks()
        logger.info(f"✅ 智能排序完成: {len(prioritized)} 个任务")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ 任务助手测试异常: {e}")
        return False

def main():
    """主测试函数"""
    logger.info("=" * 60)
    logger.info("飞书AI助手快速测试")
    logger.info(f"测试时间: {datetime.now()}")
    logger.info("=" * 60)
    
    results = []
    
    # 测试飞书客户端
    results.append(("飞书客户端", test_feishu_client()))
    
    # 测试日历助手
    results.append(("日历助手", test_calendar_assistant()))
    
    # 测试任务助手
    results.append(("任务助手", test_task_assistant()))
    
    # 输出结果
    logger.info("\n" + "=" * 60)
    logger.info("测试结果汇总")
    logger.info("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for _, passed in results if passed)
    
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        logger.info(f"{name}: {status}")
    
    logger.info(f"\n总计: {passed_tests}/{total_tests} 通过")
    
    if passed_tests == total_tests:
        logger.info("🎉 所有测试通过！飞书AI助手核心功能正常。")
        return 0
    else:
        logger.warning("⚠️  部分测试失败，请检查配置和网络连接。")
        return 1

if __name__ == "__main__":
    sys.exit(main())