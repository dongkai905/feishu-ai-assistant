#!/usr/bin/env python3
"""
修复所有Req引用
"""

import re

# 读取文件
with open('src/feishu_client.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复所有Req引用
replacements = {
    'ListCalendarReq': 'ListCalendarRequest',
    'ListCalendarEventReq': 'ListCalendarEventRequest',
    'ListTaskReq': 'ListTaskRequest',
    'CreateTaskReq': 'CreateTaskRequest',
    'CreateMessageReq': 'CreateMessageRequest',
    'ListFileReq': 'ListFileRequest',
    'ListUserReq': 'ListUserRequest',
}

# 应用替换
for old, new in replacements.items():
    pattern = r'\b' + re.escape(old) + r'\b'
    content = re.sub(pattern, new, content)

# 写回文件
with open('src/feishu_client.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 已修复所有Req引用:")
for old, new in replacements.items():
    print(f"  {old} → {new}")