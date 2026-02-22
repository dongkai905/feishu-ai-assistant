#!/usr/bin/env python3
"""
Feishu AI Assistant 命令行工具
简化系统使用，提供常用功能
"""

import argparse
import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"

def check_health():
    """检查系统健康状态"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("🟢 系统状态: 健康")
            print(f"   服务: {data.get('service')}")
            print(f"   飞书连接: {'✅ 正常' if data.get('feishu_connected') else '❌ 异常'}")
            print(f"   时间: {data.get('timestamp')}")
            return True
        else:
            print(f"🔴 系统状态: 异常 (状态码: {response.status_code})")
            return False
    except Exception as e:
        print(f"🔴 连接失败: {e}")
        return False

def show_version():
    """显示版本信息"""
    try:
        response = requests.get(f"{BASE_URL}/version", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"📱 应用名称: {data.get('name')}")
            print(f"   版本: {data.get('version')}")
            print(f"   描述: {data.get('description')}")
            print(f"   时间: {data.get('timestamp')}")
        else:
            print(f"获取版本信息失败 (状态码: {response.status_code})")
    except Exception as e:
        print(f"获取版本信息失败: {e}")

def show_today_calendar():
    """显示今日日历"""
    try:
        response = requests.get(f"{BASE_URL}/calendar/today", timeout=5)
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print(f"📅 今日日历 ({data.get('date')})")
            print(f"   事件总数: {count}")
            
            if count > 0:
                for i, event in enumerate(data.get('data', []), 1):
                    print(f"   {i}. {event.get('summary', '未命名')}")
                    if event.get('start_time'):
                        print(f"      时间: {event.get('start_time')}")
                    if event.get('location'):
                        print(f"      地点: {event.get('location')}")
                    print()
            else:
                print("   (暂无日历事件)")
        else:
            print(f"获取日历失败 (状态码: {response.status_code})")
    except Exception as e:
        print(f"获取日历失败: {e}")

def show_tasks(status=None):
    """显示任务列表"""
    try:
        url = f"{BASE_URL}/tasks"
        if status:
            url += f"?status={status}"
        
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print(f"✅ 任务列表")
            print(f"   任务总数: {count}")
            
            if count > 0:
                for i, task in enumerate(data.get('data', []), 1):
                    print(f"   {i}. {task.get('title', '未命名')}")
                    print(f"      状态: {task.get('status', '未知')}")
                    print(f"      优先级: {task.get('priority', '未知')}")
                    if task.get('due_date'):
                        print(f"      截止时间: {task.get('due_date')}")
                    print()
            else:
                print("   (暂无任务)")
        else:
            print(f"获取任务失败 (状态码: {response.status_code})")
    except Exception as e:
        print(f"获取任务失败: {e}")

def show_documents():
    """显示文档列表"""
    try:
        response = requests.get(f"{BASE_URL}/documents", timeout=5)
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print(f"📄 文档列表")
            print(f"   文档总数: {count}")
            
            if count > 0:
                for i, doc in enumerate(data.get('data', []), 1):
                    print(f"   {i}. {doc.get('name', '未命名')}")
                    print(f"      类型: {doc.get('type', '未知')}")
                    if doc.get('size'):
                        print(f"      大小: {doc.get('size')}")
                    if doc.get('updated_time'):
                        print(f"      更新时间: {doc.get('updated_time')}")
                    print()
            else:
                print("   (暂无文档)")
        else:
            print(f"获取文档失败 (状态码: {response.status_code})")
    except Exception as e:
        print(f"获取文档失败: {e}")

def show_dashboard():
    """显示综合仪表板"""
    print("=" * 60)
    print("📊 Feishu AI Assistant 仪表板")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # 检查健康状态
    if not check_health():
        print("\n❌ 系统不可用，请检查服务是否运行")
        return
    
    print()
    show_version()
    print()
    show_today_calendar()
    print()
    show_tasks()
    print()
    show_documents()
    
    print("=" * 60)
    print("💡 使用提示:")
    print("  feishu-cli health     - 检查系统健康")
    print("  feishu-cli calendar   - 查看今日日历")
    print("  feishu-cli tasks      - 查看任务列表")
    print("  feishu-cli dashboard  - 查看综合仪表板")
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="Feishu AI Assistant 命令行工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # health 命令
    subparsers.add_parser("health", help="检查系统健康状态")
    
    # version 命令
    subparsers.add_parser("version", help="显示版本信息")
    
    # calendar 命令
    subparsers.add_parser("calendar", help="显示今日日历")
    
    # tasks 命令
    tasks_parser = subparsers.add_parser("tasks", help="显示任务列表")
    tasks_parser.add_argument("--status", help="任务状态筛选 (pending/completed)")
    
    # documents 命令
    subparsers.add_parser("documents", help="显示文档列表")
    
    # dashboard 命令
    subparsers.add_parser("dashboard", help="显示综合仪表板")
    
    args = parser.parse_args()
    
    if not args.command:
        show_dashboard()
        return
    
    if args.command == "health":
        check_health()
    elif args.command == "version":
        show_version()
    elif args.command == "calendar":
        show_today_calendar()
    elif args.command == "tasks":
        show_tasks(args.status)
    elif args.command == "documents":
        show_documents()
    elif args.command == "dashboard":
        show_dashboard()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()