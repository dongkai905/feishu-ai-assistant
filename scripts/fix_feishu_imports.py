#!/usr/bin/env python3
"""
修复飞书客户端导入问题
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 测试导入
try:
    from lark_oapi.api.calendar.v4 import CreateCalendarEventReq, CalendarEvent
    from lark_oapi.api.task.v2 import CreateTaskReq, Task
    from lark_oapi.api.im.v1 import CreateMessageReq
    from lark_oapi.api.calendar.v4 import ListCalendarEventReq
    from lark_oapi.api.task.v2 import ListTaskReq
    from lark_oapi.api.contact.v3 import ListUserReq
    
    print("✅ 所有必需的飞书API类都可以导入")
    print(f"  CreateCalendarEventReq: {CreateCalendarEventReq}")
    print(f"  CalendarEvent: {CalendarEvent}")
    print(f"  CreateTaskReq: {CreateTaskReq}")
    print(f"  Task: {Task}")
    print(f"  CreateMessageReq: {CreateMessageReq}")
    print(f"  ListCalendarEventReq: {ListCalendarEventReq}")
    print(f"  ListTaskReq: {ListTaskReq}")
    print(f"  ListUserReq: {ListUserReq}")
    
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("\n尝试安装lark-oapi:")
    print("  pip install lark-oapi")
    
except Exception as e:
    print(f"❌ 其他错误: {e}")