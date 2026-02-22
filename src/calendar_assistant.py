"""
日历智能助手
提供日程管理、会议安排、智能提醒等功能
"""
import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

from .feishu_client import get_feishu_client

logger = logging.getLogger(__name__)


class EventPriority(Enum):
    """事件优先级"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    URGENT = "urgent"


class CalendarAssistant:
    """日历智能助手"""
    
    def __init__(self, default_calendar_id: str = None):
        """
        初始化日历助手
        
        Args:
            default_calendar_id: 默认日历ID
        """
        self.client = get_feishu_client()
        self.default_calendar_id = default_calendar_id
        
        # 如果没有指定默认日历，使用第一个日历
        if not self.default_calendar_id:
            calendars = self.client.get_calendars()
            if calendars:
                self.default_calendar_id = calendars[0]["calendar_id"]
                logger.info(f"使用默认日历: {calendars[0]['summary']}")
        
        logger.info("日历智能助手初始化完成")
    
    def get_today_events(self) -> List[Dict]:
        """获取今天的所有事件"""
        try:
            today = datetime.now().strftime("%Y-%m-%dT00:00:00+08:00")
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00+08:00")
            
            events = self.client.get_events(self.default_calendar_id, today, tomorrow)
            
            # 按开始时间排序
            events.sort(key=lambda x: x.get("start_time", {}).get("timestamp", "0"))
            
            logger.info(f"获取到今天 {len(events)} 个事件")
            return events
        
        except Exception as e:
            logger.error(f"获取今天事件异常: {e}")
            return []
    
    def get_upcoming_events(self, hours: int = 24) -> List[Dict]:
        """获取即将发生的事件"""
        try:
            now = datetime.now()
            start_time = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
            end_time = (now + timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%S+08:00")
            
            events = self.client.get_events(self.default_calendar_id, start_time, end_time)
            
            # 过滤掉已结束的事件
            current_timestamp = int(now.timestamp())
            upcoming_events = []
            
            for event in events:
                event_start = event.get("start_time", {}).get("timestamp")
                if event_start and int(event_start) > current_timestamp:
                    upcoming_events.append(event)
            
            # 按开始时间排序
            upcoming_events.sort(key=lambda x: x.get("start_time", {}).get("timestamp", "0"))
            
            logger.info(f"获取到未来{hours}小时内 {len(upcoming_events)} 个即将发生的事件")
            return upcoming_events
        
        except Exception as e:
            logger.error(f"获取即将发生事件异常: {e}")
            return []
    
    def create_meeting(self, title: str, start_time: datetime, duration_minutes: int = 60,
                      description: str = None, location: str = None, attendees: List[str] = None) -> Optional[Dict]:
        """
        创建会议
        
        Args:
            title: 会议标题
            start_time: 开始时间
            duration_minutes: 持续时间（分钟）
            description: 会议描述
            location: 会议地点
            attendees: 参会者ID列表
        """
        try:
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            # 格式化时间
            start_time_dict = {
                "date": start_time.strftime("%Y-%m-%d"),
                "timestamp": str(int(start_time.timestamp())),
                "timezone": "Asia/Shanghai"
            }
            
            end_time_dict = {
                "date": end_time.strftime("%Y-%m-%d"),
                "timestamp": str(int(end_time.timestamp())),
                "timezone": "Asia/Shanghai"
            }
            
            # 创建事件
            event_data = {
                "summary": title,
                "start_time": start_time_dict,
                "end_time": end_time_dict,
            }
            
            if description:
                event_data["description"] = description
            
            if location:
                event_data["location"] = {"name": location}
            
            # TODO: 添加参会者功能需要进一步实现
            # if attendees:
            #     event_data["attendees"] = [{"type": "user", "id": uid} for uid in attendees]
            
            result = self.client.create_event(self.default_calendar_id, title, start_time_dict, 
                                            end_time_dict, description, location)
            
            if result:
                logger.info(f"会议创建成功: {title} ({start_time.strftime('%Y-%m-%d %H:%M')})")
                
                # 发送提醒消息
                self._send_meeting_reminder(title, start_time, result["event_id"])
                
                return result
            
            return None
        
        except Exception as e:
            logger.error(f"创建会议异常: {e}")
            return None
    
    def create_daily_standup(self, time_str: str = "09:30", duration_minutes: int = 30) -> Optional[Dict]:
        """
        创建每日站会
        
        Args:
            time_str: 时间字符串 (格式: "09:30")
            duration_minutes: 持续时间（分钟）
        """
        try:
            # 解析时间
            hour, minute = map(int, time_str.split(":"))
            
            # 设置开始时间为今天的指定时间
            today = datetime.now()
            start_time = today.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # 如果今天的时间已经过去，设置为明天
            if start_time < datetime.now():
                start_time += timedelta(days=1)
            
            title = "每日站会"
            description = "团队每日同步会议，同步进展、问题和计划"
            
            return self.create_meeting(title, start_time, duration_minutes, description)
        
        except Exception as e:
            logger.error(f"创建每日站会异常: {e}")
            return None
    
    def schedule_focus_time(self, duration_hours: int = 2, priority: str = "high") -> Optional[Dict]:
        """
        安排专注时间
        
        Args:
            duration_hours: 专注时间长度（小时）
            priority: 优先级 (high, medium, low)
        """
        try:
            # 找到下一个可用的时间段
            available_slot = self._find_available_slot(duration_hours * 60)
            
            if not available_slot:
                logger.warning("未找到可用的专注时间段")
                return None
            
            start_time, _ = available_slot
            title = f"专注时间 ({priority}优先级)"
            description = f"深度工作时段，请勿打扰。优先级: {priority}"
            
            return self.create_meeting(title, start_time, duration_hours * 60, description)
        
        except Exception as e:
            logger.error(f"安排专注时间异常: {e}")
            return None
    
    def analyze_schedule(self) -> Dict:
        """分析日程安排"""
        try:
            events = self.get_today_events()
            
            if not events:
                return {
                    "total_events": 0,
                    "total_hours": 0,
                    "busy_percentage": 0,
                    "recommendations": ["今天没有安排，可以自由安排工作"],
                }
            
            # 计算总时长
            total_minutes = 0
            for event in events:
                start_time = event.get("start_time", {}).get("timestamp")
                end_time = event.get("end_time", {}).get("timestamp")
                
                if start_time and end_time:
                    duration = (int(end_time) - int(start_time)) / 60  # 转换为分钟
                    total_minutes += duration
            
            total_hours = total_minutes / 60
            busy_percentage = min(100, (total_hours / 8) * 100)  # 假设8小时工作制
            
            # 生成建议
            recommendations = []
            
            if busy_percentage > 80:
                recommendations.append("日程非常繁忙，建议取消或推迟一些非紧急会议")
            elif busy_percentage > 60:
                recommendations.append("日程较满，注意安排休息时间")
            elif busy_percentage < 30:
                recommendations.append("日程较宽松，可以考虑安排一些深度工作或学习")
            
            # 检查会议间隙
            gaps = self._find_schedule_gaps(events)
            if gaps:
                recommendations.append(f"发现{gaps}个时间间隙，可用于处理零散任务")
            
            # 检查是否有背靠背会议
            back_to_back = self._check_back_to_back_meetings(events)
            if back_to_back:
                recommendations.append("有背靠背会议，建议安排休息时间")
            
            return {
                "total_events": len(events),
                "total_hours": round(total_hours, 1),
                "busy_percentage": round(busy_percentage, 1),
                "recommendations": recommendations,
                "events": events[:5],  # 只返回前5个事件
            }
        
        except Exception as e:
            logger.error(f"分析日程异常: {e}")
            return {"error": str(e)}
    
    def _find_available_slot(self, duration_minutes: int) -> Optional[Tuple[datetime, datetime]]:
        """找到可用的时间段"""
        try:
            events = self.get_today_events()
            
            if not events:
                # 如果没有事件，使用上午9点开始
                start_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
                if start_time < datetime.now():
                    start_time = datetime.now() + timedelta(minutes=30)  # 30分钟后
                
                end_time = start_time + timedelta(minutes=duration_minutes)
                return start_time, end_time
            
            # 按开始时间排序
            events.sort(key=lambda x: x.get("start_time", {}).get("timestamp", "0"))
            
            # 检查事件之间的间隙
            for i in range(len(events) - 1):
                current_end = self._get_event_end_time(events[i])
                next_start = self._get_event_start_time(events[i + 1])
                
                if current_end and next_start:
                    gap_minutes = (next_start - current_end).total_seconds() / 60
                    
                    if gap_minutes >= duration_minutes:
                        # 找到足够长的间隙
                        start_time = current_end + timedelta(minutes=5)  # 留5分钟缓冲
                        end_time = start_time + timedelta(minutes=duration_minutes)
                        return start_time, end_time
            
            # 如果没有找到间隙，放在最后一个事件之后
            last_event = events[-1]
            last_end = self._get_event_end_time(last_event)
            
            if last_end:
                start_time = last_end + timedelta(minutes=15)  # 留15分钟缓冲
                end_time = start_time + timedelta(minutes=duration_minutes)
                return start_time, end_time
            
            return None
        
        except Exception as e:
            logger.error(f"查找可用时间段异常: {e}")
            return None
    
    def _find_schedule_gaps(self, events: List[Dict], min_gap_minutes: int = 15) -> int:
        """查找日程间隙"""
        try:
            if len(events) < 2:
                return 0
            
            gaps = 0
            events.sort(key=lambda x: x.get("start_time", {}).get("timestamp", "0"))
            
            for i in range(len(events) - 1):
                current_end = self._get_event_end_time(events[i])
                next_start = self._get_event_start_time(events[i + 1])
                
                if current_end and next_start:
                    gap_minutes = (next_start - current_end).total_seconds() / 60
                    
                    if gap_minutes >= min_gap_minutes:
                        gaps += 1
            
            return gaps
        
        except Exception as e:
            logger.error(f"查找日程间隙异常: {e}")
            return 0
    
    def _check_back_to_back_meetings(self, events: List[Dict]) -> bool:
        """检查是否有背靠背会议"""
        try:
            if len(events) < 2:
                return False
            
            events.sort(key=lambda x: x.get("start_time", {}).get("timestamp", "0"))
            
            for i in range(len(events) - 1):
                current_end = self._get_event_end_time(events[i])
                next_start = self._get_event_start_time(events[i + 1])
                
                if current_end and next_start:
                    gap_minutes = (next_start - current_end).total_seconds() / 60
                    
                    if gap_minutes < 5:  # 小于5分钟视为背靠背
                        return True
            
            return False
        
        except Exception as e:
            logger.error(f"检查背靠背会议异常: {e}")
            return False
    
    def _get_event_start_time(self, event: Dict) -> Optional[datetime]:
        """获取事件的开始时间"""
        try:
            timestamp = event.get("start_time", {}).get("timestamp")
            if timestamp:
                return datetime.fromtimestamp(int(timestamp))
            return None
        except:
            return None
    
    def _get_event_end_time(self, event: Dict) -> Optional[datetime]:
        """获取事件的结束时间"""
        try:
            timestamp = event.get("end_time", {}).get("timestamp")
            if timestamp:
                return datetime.fromtimestamp(int(timestamp))
            return None
        except:
            return None
    
    def _send_meeting_reminder(self, title: str, start_time: datetime, event_id: str):
        """发送会议提醒"""
        try:
            # 这里可以集成消息发送功能
            # 暂时只记录日志
            time_str = start_time.strftime("%Y-%m-%d %H:%M")
            logger.info(f"会议提醒: {title} 将于 {time_str} 开始 (事件ID: {event_id})")
            
            # TODO: 实现实际的消息发送
            # self.client.send_text_message(user_id, f"提醒: {title} 将于 {time_str} 开始")
        
        except Exception as e:
            logger.error(f"发送会议提醒异常: {e}")
    
    def get_daily_summary(self) -> Dict:
        """获取每日日程摘要"""
        try:
            today_events = self.get_today_events()
            upcoming_events = self.get_upcoming_events(24)
            schedule_analysis = self.analyze_schedule()
            
            return {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "today_events_count": len(today_events),
                "upcoming_events_count": len(upcoming_events),
                "schedule_analysis": schedule_analysis,
                "next_event": upcoming_events[0] if upcoming_events else None,
                "recommendations": schedule_analysis.get("recommendations", []),
            }
        
        except Exception as e:
            logger.error(f"获取每日摘要异常: {e}")
            return {"error": str(e)}


# 全局助手实例
_calendar_assistant = None

def get_calendar_assistant() -> CalendarAssistant:
    """获取日历助手单例"""
    global _calendar_assistant
    if _calendar_assistant is None:
        _calendar_assistant = CalendarAssistant()
    return _calendar_assistant