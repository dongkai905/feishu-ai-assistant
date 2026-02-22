#!/usr/bin/env python3
"""
探索飞书API的正确使用方法
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lark_oapi.api.calendar.v4 import CreateCalendarEventRequest, CalendarEvent
from lark_oapi.api.task.v2 import CreateTaskRequest, Task
from lark_oapi.api.im.v1 import CreateMessageRequest

print("探索飞书API Builder方法:")
print("=" * 60)

# 1. 检查CreateCalendarEventRequest
print("1. CreateCalendarEventRequest.builder() 方法:")
builder = CreateCalendarEventRequest.builder()
print(f"   Builder对象: {builder}")
print(f"   Builder方法: {dir(builder)}")

# 查找包含calendar的方法
calendar_methods = [m for m in dir(builder) if 'calendar' in m.lower()]
print(f"   包含'calendar'的方法: {calendar_methods}")

print("\n2. CreateTaskRequest.builder() 方法:")
builder2 = CreateTaskRequest.builder()
print(f"   Builder对象: {builder2}")
print(f"   Builder方法: {dir(builder2)}")

# 查找包含task的方法
task_methods = [m for m in dir(builder2) if 'task' in m.lower()]
print(f"   包含'task'的方法: {task_methods}")

print("\n3. CreateMessageRequest.builder() 方法:")
builder3 = CreateMessageRequest.builder()
print(f"   Builder对象: {builder3}")
print(f"   Builder方法: {dir(builder3)}")

# 查找包含message的方法
message_methods = [m for m in dir(builder3) if 'message' in m.lower() or 'body' in m.lower()]
print(f"   包含'message'或'body'的方法: {message_methods}")

print("\n4. 检查CalendarEvent.builder() 方法:")
event_builder = CalendarEvent.builder()
print(f"   CalendarEvent Builder方法: {dir(event_builder)}")

print("\n5. 检查Task.builder() 方法:")
task_builder = Task.builder()
print(f"   Task Builder方法: {dir(task_builder)}")