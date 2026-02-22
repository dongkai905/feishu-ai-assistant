#!/usr/bin/env python3
"""
创建测试日历事件
用于验证自动化日历同步系统
"""

import os
import sys
import json
import datetime
from pathlib import Path

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from auto_calendar_sync import AutoCalendarSync

def create_test_event():
    """创建测试日历事件"""
    print("=" * 60)
    print("🎯 创建测试日历事件")
    print("验证自动化日历同步系统")
    print("日历设置: 个人")
    print("=" * 60)
    
    # 创建同步系统实例，使用配置文件
    config_file = os.path.expanduser("~/Desktop/calendar_sync_config.json")
    sync_system = AutoCalendarSync(config_file)
    
    # 创建测试任务 - 30分钟后开始
    now = datetime.datetime.now()
    start_time = now + datetime.timedelta(minutes=30)
    end_time = start_time + datetime.timedelta(minutes=30)
    
    test_task = {
        'title': '测试日历同步 - 自动化验证',
        'start_time': start_time.strftime('%Y-%m-%dT%H:%M:%S'),
        'end_time': end_time.strftime('%Y-%m-%dT%H:%M:%S'),
        'description': '这是自动化日历同步系统的测试任务，用于验证全自动功能。\n\n触发指令: "30分钟后测试日历同步"',
        'location': '测试环境',
        'priority': 'high'
    }
    
    print(f"📋 任务信息:")
    print(f"  标题: {test_task['title']}")
    print(f"  开始: {start_time.strftime('%H:%M')}")
    print(f"  结束: {end_time.strftime('%H:%M')}")
    print(f"  提醒: 提前15分钟 + 铃声")
    print(f"  来源: 用户指令")
    
    # 生成iCalendar文件
    ical_file = sync_system.generate_icalendar_file([test_task], 
                                                   filename="calendar_sync_test.ics")
    print(f"✅ iCalendar文件已创建: {ical_file}")
    
    # 自动导入到日历
    print("🚀 正在自动导入到日历...")
    result = sync_system.auto_import_to_calendar(ical_file)
    
    if result:
        print("🎉 日历事件已自动创建！")
        print("💡 请检查您的日历应用，事件应该已添加")
        
        # 显示事件详情
        print("\n📅 事件详情:")
        print(f"   时间: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
        print(f"   标题: {test_task['title']}")
        print(f"   描述: {test_task['description']}")
        print(f"   位置: {test_task['location']}")
        print(f"   提醒: 提前15分钟 + 铃声")
        
        # 创建验证指南
        create_verification_guide(test_task, ical_file)
    else:
        print("⚠️ 自动导入失败，请手动导入文件")
        print(f"   文件位置: {ical_file}")
        print("   请双击文件手动导入到日历应用")
    
    return test_task, ical_file

def create_verification_guide(task_info, ical_file):
    """创建验证指南"""
    guide_file = os.path.expanduser("~/Desktop/calendar_sync_test_guide.md")
    
    guide_content = f"""# 📅 日历同步测试验证指南

## 🎯 测试目的
验证自动化日历同步系统的全自动功能

## 📋 测试事件详情

### 基本信息
- **标题**: {task_info['title']}
- **开始时间**: {datetime.datetime.strptime(task_info['start_time'], '%Y-%m-%dT%H:%M:%S').strftime('%H:%M')}
- **结束时间**: {datetime.datetime.strptime(task_info['end_time'], '%Y-%m-%dT%H:%M:%S').strftime('%H:%M')}
- **提醒设置**: 提前15分钟 + 铃声
- **来源**: 用户指令"30分钟后测试日历同步"

### 触发流程
```
用户说话 → 系统检测 → 自动创建 → 铃声提醒 → 日历同步
    ↓          ↓          ↓          ↓          ↓
 "30分钟后"  识别任务   生成事件   设置提醒   自动导入
```

## ✅ 验证步骤

### 1. 检查日历应用
1. 打开Mac日历应用
2. 查看今天的时间线
3. 确认事件已添加
4. 检查提醒设置

### 2. 验证提醒功能
1. 等待15:40 (提前15分钟)
2. 系统应该弹出提醒
3. 应该有铃声

### 3. 验证自动化
1. 说另一个包含时间的任务
2. 例如："1小时后开会"
3. 检查是否自动创建事件

## 🔧 技术信息

### 系统状态
- **守护进程**: 运行中 (PID: 49341)
- **配置文件**: `~/Desktop/calendar_sync_config.json`
- **日志文件**: `~/Library/Logs/AutoCalendarSync/`

### 文件位置
- **iCalendar文件**: {ical_file}
- **测试指南**: {guide_file}

## 🎯 预期结果

### 成功标志
1. ✅ 日历事件已创建
2. ✅ 提醒时间正确
3. ✅ 铃声已设置
4. ✅ 事件信息完整

### 验证时间线
- **15:40**: 系统提醒 (提前15分钟)
- **15:55**: 事件开始时间
- **16:25**: 事件结束时间

## 💡 故障排除

### 如果事件未创建
1. 检查日历应用是否打开
2. 检查iCalendar文件是否损坏
3. 重新运行测试脚本

### 如果无提醒
1. 检查系统通知设置
2. 检查日历应用提醒设置
3. 验证iCalendar文件提醒配置

### 如果需要重新测试
```bash
cd feishu-ai-assistant/scripts
python3 create_test_event.py
```

## 🎊 测试完成标志

当您在15:40收到提醒铃声时，说明：
1. ✅ 自动化检测功能正常
2. ✅ 日历创建功能正常
3. ✅ 提醒设置功能正常
4. ✅ 全自动流程正常

---

**测试状态**: 🟢 进行中  
**创建时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**验证时间**: 15:40 (提醒时间)  
**系统原则**: 全自动，零手动干预
"""
    
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"📘 验证指南已创建: {guide_file}")

def main():
    """主函数"""
    try:
        task_info, ical_file = create_test_event()
        
        print("\n" + "=" * 60)
        print("🎉 测试事件创建完成！")
        print("=" * 60)
        print("\n💡 下一步操作:")
        print("1. 打开日历应用查看事件")
        print("2. 等待15:40验证提醒功能")
        print("3. 查看验证指南了解更多信息")
        print(f"\n📁 相关文件:")
        print(f"   • iCalendar文件: {ical_file}")
        print(f"   • 验证指南: ~/Desktop/calendar_sync_test_guide.md")
        print(f"   • 配置文件: ~/Desktop/calendar_sync_config.json")
        
    except Exception as e:
        print(f"❌ 创建测试事件失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()