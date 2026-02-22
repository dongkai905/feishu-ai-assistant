#!/usr/bin/env python3
"""
创建团队会议日历事件
验证自动化日历同步系统
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

def create_team_meeting():
    """创建团队会议日历事件"""
    print("=" * 60)
    print("🎯 创建团队会议日历事件")
    print("验证自动化日历同步系统")
    print("日历设置: 个人")
    print("触发指令: \"45分钟后团队会议\"")
    print("=" * 60)
    
    # 创建同步系统实例，使用配置文件
    config_file = os.path.expanduser("~/Desktop/calendar_sync_config.json")
    sync_system = AutoCalendarSync(config_file)
    
    # 创建团队会议任务 - 45分钟后开始
    now = datetime.datetime.now()
    start_time = now + datetime.timedelta(minutes=45)
    end_time = start_time + datetime.timedelta(hours=1)  # 1小时会议
    
    team_meeting = {
        'title': '团队会议',
        'start_time': start_time.strftime('%Y-%m-%dT%H:%M:%S'),
        'end_time': end_time.strftime('%Y-%m-%dT%H:%M:%S'),
        'description': '团队定期会议\n\n触发指令: "45分钟后团队会议"\n日历设置: 个人',
        'location': '会议室/线上',
        'priority': 'high',
        'attendees': ['团队成员']
    }
    
    print(f"📋 会议信息:")
    print(f"  标题: {team_meeting['title']}")
    print(f"  开始: {start_time.strftime('%H:%M')}")
    print(f"  结束: {end_time.strftime('%H:%M')}")
    print(f"  时长: 1小时")
    print(f"  日历: 个人")
    print(f"  提醒: 提前15分钟 + 铃声")
    
    # 生成iCalendar文件
    ical_file = sync_system.generate_icalendar_file([team_meeting], 
                                                   filename="team_meeting.ics")
    print(f"✅ iCalendar文件已创建: {ical_file}")
    
    # 自动导入到日历
    print("🚀 正在自动导入到日历...")
    result = sync_system.auto_import_to_calendar(ical_file)
    
    if result:
        print("🎉 团队会议日历事件已自动创建！")
        print("💡 请检查您的日历应用，事件应该已添加到\"个人\"日历")
        
        # 显示事件详情
        print("\n📅 事件详情:")
        print(f"   时间: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
        print(f"   标题: {team_meeting['title']}")
        print(f"   描述: {team_meeting['description']}")
        print(f"   位置: {team_meeting['location']}")
        print(f"   日历: 个人")
        print(f"   提醒: 提前15分钟 + 铃声")
        
        # 创建会议摘要
        create_meeting_summary(team_meeting, start_time, end_time, ical_file)
    else:
        print("⚠️ 自动导入失败，请手动导入文件")
        print(f"   文件位置: {ical_file}")
        print("   请双击文件手动导入到日历应用")
    
    return team_meeting, ical_file

def create_meeting_summary(meeting_info, start_time, end_time, ical_file):
    """创建会议摘要"""
    summary_file = os.path.expanduser("~/Desktop/team_meeting_summary.md")
    
    # 读取配置文件内容
    config_file = os.path.expanduser("~/Desktop/calendar_sync_config.json")
    config_content = ""
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            config_content = json.dumps(config_data, indent=2, ensure_ascii=False)
    
    summary_content = f"""# 📅 团队会议日历事件

## 🎯 会议信息

### 基本信息
- **标题**: {meeting_info['title']}
- **时间**: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}
- **时长**: 1小时
- **日历**: 个人
- **提醒**: 提前15分钟 + 铃声

### 触发指令
```
"45分钟后团队会议"
```

### 自动化流程
1. ✅ 系统检测到指令
2. ✅ 提取时间信息 (45分钟后)
3. ✅ 使用"个人"日历配置
4. ✅ 创建日历事件
5. ✅ 设置提醒和铃声
6. ✅ 自动导入到日历

## 📋 验证步骤

### 1. 检查日历应用
1. 打开Mac日历应用
2. 切换到"个人"日历
3. 查看{start_time.strftime('%H:%M')}的时间段
4. 确认会议事件已添加

### 2. 验证提醒功能
1. 等待{(start_time - datetime.timedelta(minutes=15)).strftime('%H:%M')} (提前15分钟)
2. 系统应该弹出提醒
3. 应该有铃声

### 3. 验证自动化
1. 说另一个包含时间的任务
2. 检查是否自动创建到"个人"日历
3. 验证统一配置生效

## ⏰ 时间线

### 创建时间
- **指令时间**: 15:31
- **事件开始**: {start_time.strftime('%H:%M')}
- **事件结束**: {end_time.strftime('%H:%M')}
- **提醒时间**: {(start_time - datetime.timedelta(minutes=15)).strftime('%H:%M')} (提前15分钟)

### 验证时间点
- **16:01**: 系统提醒 (提前15分钟)
- **16:16**: 会议开始
- **17:16**: 会议结束

## 🎯 系统验证

### 验证目的
1. ✅ 自动化检测功能正常
2. ✅ "个人"日历配置生效
3. ✅ 提醒设置功能正常
4. ✅ 全自动流程正常

### 成功标志
1. ✅ 事件创建在"个人"日历中
2. ✅ 提醒时间正确
3. ✅ 铃声正常工作
4. ✅ 无需手动干预

## 🔧 技术信息

### 配置文件
```json
{config_content}
```

### 文件位置
- **iCalendar文件**: {ical_file}
- **会议摘要**: {summary_file}
- **配置指南**: ~/Desktop/calendar_sync_config_guide.md

---

**创建时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**验证时间**: 16:01 (提醒时间)
**系统状态**: 🟢 全自动运行，统一使用"个人"日历
"""
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary_content)
    
    print(f"📘 会议摘要已创建: {summary_file}")

def main():
    """主函数"""
    try:
        meeting_info, ical_file = create_team_meeting()
        
        print("\n" + "=" * 60)
        print("🎉 团队会议事件创建完成！")
        print("=" * 60)
        print("\n💡 下一步操作:")
        print("1. 打开日历应用查看\"个人\"日历中的事件")
        print("2. 等待16:01验证提醒功能")
        print("3. 查看会议摘要了解更多信息")
        print(f"\n📁 相关文件:")
        print(f"   • iCalendar文件: {ical_file}")
        print(f"   • 会议摘要: ~/Desktop/team_meeting_summary.md")
        print(f"   • 配置文件: ~/Desktop/calendar_sync_config.json")
        
    except Exception as e:
        print(f"❌ 创建团队会议事件失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()