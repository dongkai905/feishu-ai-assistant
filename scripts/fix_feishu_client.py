#!/usr/bin/env python3
"""
修复飞书客户端API调用
"""

import re

def fix_create_event():
    """修复创建事件方法"""
    with open('src/feishu_client.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找创建事件的方法
    pattern = r'def create_event\(.*?\):.*?(?=def|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        method_text = match.group(0)
        print("找到 create_event 方法")
        
        # 检查是否需要修复
        if 'request_body' not in method_text:
            print("需要修复 create_event 方法")
    
    return content

def fix_create_task():
    """修复创建任务方法"""
    with open('src/feishu_client.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找创建任务的方法
    pattern = r'def create_task\(.*?\):.*?(?=def|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        method_text = match.group(0)
        print("找到 create_task 方法")
        
        # 检查是否需要修复
        if 'request_body' not in method_text:
            print("需要修复 create_task 方法")
    
    return content

def fix_send_message():
    """修复发送消息方法"""
    with open('src/feishu_client.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找发送消息的方法
    pattern = r'def send_message\(.*?\):.*?(?=def|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        method_text = match.group(0)
        print("找到 send_message 方法")
        
        # 检查是否需要修复
        if 'request_body' not in method_text:
            print("需要修复 send_message 方法")
    
    return content

def main():
    print("检查飞书客户端修复需求...")
    
    # 检查各个方法
    fix_create_event()
    fix_create_task()
    fix_send_message()
    
    print("\n✅ 检查完成")

if __name__ == "__main__":
    main()