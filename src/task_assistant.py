"""
任务智能助手
提供任务管理、优先级排序、智能分配等功能
"""
import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

from .feishu_client import get_feishu_client

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """任务状态"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(Enum):
    """任务优先级"""
    URGENT = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class TaskAssistant:
    """任务智能助手"""
    
    def __init__(self, default_user_id: str = None):
        """
        初始化任务助手
        
        Args:
            default_user_id: 默认用户ID
        """
        self.client = get_feishu_client()
        self.default_user_id = default_user_id
        
        logger.info("任务智能助手初始化完成")
    
    def get_my_tasks(self, status: str = None) -> List[Dict]:
        """
        获取我的任务
        
        Args:
            status: 任务状态过滤 (todo, in_progress, done)
        """
        try:
            tasks = self.client.get_tasks(self.default_user_id)
            
            if status:
                tasks = [task for task in tasks if task.get("status") == status]
            
            # 按优先级和创建时间排序
            tasks.sort(key=lambda x: (x.get("priority", 4), x.get("created_at", "")))
            
            logger.info(f"获取到 {len(tasks)} 个任务 (状态: {status or 'all'})")
            return tasks
        
        except Exception as e:
            logger.error(f"获取任务异常: {e}")
            return []
    
    def get_tasks_by_priority(self, priority: int = None) -> List[Dict]:
        """
        按优先级获取任务
        
        Args:
            priority: 优先级 (1-4, 1为最高)
        """
        try:
            tasks = self.client.get_tasks(self.default_user_id)
            
            if priority:
                tasks = [task for task in tasks if task.get("priority") == priority]
            
            # 按截止时间排序
            tasks.sort(key=lambda x: x.get("due_time", {}).get("timestamp", "9999999999"))
            
            logger.info(f"获取到 {len(tasks)} 个优先级为 {priority} 的任务")
            return tasks
        
        except Exception as e:
            logger.error(f"按优先级获取任务异常: {e}")
            return []
    
    def get_overdue_tasks(self) -> List[Dict]:
        """获取过期任务"""
        try:
            tasks = self.client.get_tasks(self.default_user_id)
            
            current_timestamp = int(datetime.now().timestamp())
            overdue_tasks = []
            
            for task in tasks:
                if task.get("status") != "done":  # 只检查未完成的任务
                    due_time = task.get("due_time", {}).get("timestamp")
                    if due_time and int(due_time) < current_timestamp:
                        overdue_tasks.append(task)
            
            # 按过期时间排序（越早过期的排前面）
            overdue_tasks.sort(key=lambda x: x.get("due_time", {}).get("timestamp", "0"))
            
            logger.info(f"获取到 {len(overdue_tasks)} 个过期任务")
            return overdue_tasks
        
        except Exception as e:
            logger.error(f"获取过期任务异常: {e}")
            return []
    
    def get_tasks_due_today(self) -> List[Dict]:
        """获取今天到期的任务"""
        try:
            tasks = self.client.get_tasks(self.default_user_id)
            
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            today_start_ts = int(today_start.timestamp())
            today_end_ts = int(today_end.timestamp())
            
            due_today = []
            
            for task in tasks:
                if task.get("status") != "done":  # 只检查未完成的任务
                    due_time = task.get("due_time", {}).get("timestamp")
                    if due_time and today_start_ts <= int(due_time) < today_end_ts:
                        due_today.append(task)
            
            # 按优先级排序
            due_today.sort(key=lambda x: x.get("priority", 4))
            
            logger.info(f"获取到 {len(due_today)} 个今天到期的任务")
            return due_today
        
        except Exception as e:
            logger.error(f"获取今天到期任务异常: {e}")
            return []
    
    def create_task(self, title: str, description: str = None, due_date: datetime = None,
                   priority: int = 3, assignee_id: str = None) -> Optional[Dict]:
        """
        创建任务
        
        Args:
            title: 任务标题
            description: 任务描述
            due_date: 截止日期
            priority: 优先级 (1-4, 1为最高)
            assignee_id: 负责人ID
        """
        try:
            due_time_dict = None
            if due_date:
                due_time_dict = {
                    "timestamp": str(int(due_date.timestamp())),
                    "timezone": "Asia/Shanghai"
                }
            
            result = self.client.create_task(
                title, description, due_time_dict, 
                assignee_id or self.default_user_id, priority
            )
            
            if result:
                logger.info(f"任务创建成功: {title} (优先级: {priority})")
                
                # 发送任务创建通知
                self._send_task_notification(title, result["task_id"], "created")
                
                return result
            
            return None
        
        except Exception as e:
            logger.error(f"创建任务异常: {e}")
            return None
    
    def create_quick_task(self, title: str, due_in_hours: int = 24, priority: int = 3) -> Optional[Dict]:
        """
        创建快速任务
        
        Args:
            title: 任务标题
            due_in_hours: 多少小时后到期
            priority: 优先级 (1-4, 1为最高)
        """
        try:
            due_date = datetime.now() + timedelta(hours=due_in_hours)
            return self.create_task(title, None, due_date, priority)
        
        except Exception as e:
            logger.error(f"创建快速任务异常: {e}")
            return None
    
    def update_task_status(self, task_id: str, status: str) -> bool:
        """
        更新任务状态
        
        Args:
            task_id: 任务ID
            status: 新状态 (todo, in_progress, done)
        """
        try:
            # TODO: 实现任务状态更新
            # 飞书SDK目前没有直接的更新任务状态API
            # 这里先记录日志，后续实现
            
            logger.info(f"任务状态更新: {task_id} -> {status}")
            
            # 发送状态更新通知
            self._send_task_notification(f"任务状态更新为 {status}", task_id, "updated")
            
            return True
        
        except Exception as e:
            logger.error(f"更新任务状态异常: {e}")
            return False
    
    def complete_task(self, task_id: str) -> bool:
        """完成任务"""
        return self.update_task_status(task_id, "done")
    
    def prioritize_tasks(self) -> List[Dict]:
        """智能优先级排序"""
        try:
            tasks = self.get_my_tasks()
            
            if not tasks:
                return []
            
            # 计算每个任务的优先级分数
            prioritized_tasks = []
            current_time = datetime.now()
            
            for task in tasks:
                score = self._calculate_task_priority_score(task, current_time)
                task["priority_score"] = score
                prioritized_tasks.append(task)
            
            # 按优先级分数排序（分数越低优先级越高）
            prioritized_tasks.sort(key=lambda x: x.get("priority_score", 999))
            
            logger.info(f"完成 {len(prioritized_tasks)} 个任务的智能排序")
            return prioritized_tasks
        
        except Exception as e:
            logger.error(f"智能排序任务异常: {e}")
            return []
    
    def analyze_workload(self) -> Dict:
        """分析工作负载"""
        try:
            all_tasks = self.get_my_tasks()
            todo_tasks = self.get_my_tasks("todo")
            in_progress_tasks = self.get_my_tasks("in_progress")
            done_tasks = self.get_my_tasks("done")
            overdue_tasks = self.get_overdue_tasks()
            due_today_tasks = self.get_tasks_due_today()
            
            # 计算优先级分布
            priority_dist = {1: 0, 2: 0, 3: 0, 4: 0}
            for task in todo_tasks + in_progress_tasks:
                priority = task.get("priority", 4)
                priority_dist[priority] = priority_dist.get(priority, 0) + 1
            
            # 生成建议
            recommendations = []
            
            if len(overdue_tasks) > 0:
                recommendations.append(f"有 {len(overdue_tasks)} 个任务已过期，请优先处理")
            
            if len(due_today_tasks) > 5:
                recommendations.append(f"今天有 {len(due_today_tasks)} 个任务到期，建议重新安排优先级")
            
            if priority_dist[1] > 3:
                recommendations.append("紧急任务过多，建议重新评估优先级")
            
            if len(todo_tasks) > 10:
                recommendations.append("待办任务过多，建议分批处理或委派")
            
            if len(in_progress_tasks) > 3:
                recommendations.append("进行中任务过多，建议先完成部分任务")
            
            # 计算完成率
            total_tasks = len(all_tasks)
            done_count = len(done_tasks)
            completion_rate = (done_count / total_tasks * 100) if total_tasks > 0 else 0
            
            return {
                "total_tasks": total_tasks,
                "todo_tasks": len(todo_tasks),
                "in_progress_tasks": len(in_progress_tasks),
                "done_tasks": done_count,
                "overdue_tasks": len(overdue_tasks),
                "due_today_tasks": len(due_today_tasks),
                "priority_distribution": priority_dist,
                "completion_rate": round(completion_rate, 1),
                "recommendations": recommendations,
                "top_priority_tasks": self.get_tasks_by_priority(1)[:3],
            }
        
        except Exception as e:
            logger.error(f"分析工作负载异常: {e}")
            return {"error": str(e)}
    
    def get_daily_todo_list(self) -> Dict:
        """获取每日待办清单"""
        try:
            due_today = self.get_tasks_due_today()
            overdue_tasks = self.get_overdue_tasks()
            high_priority = self.get_tasks_by_priority(1)
            
            # 合并任务，去重
            all_tasks = {}
            for task in due_today + overdue_tasks + high_priority:
                task_id = task.get("task_id")
                if task_id:
                    all_tasks[task_id] = task
            
            task_list = list(all_tasks.values())
            
            # 智能排序
            prioritized_tasks = self.prioritize_tasks()
            
            # 创建今日待办清单
            todo_list = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "total_tasks": len(task_list),
                "overdue_count": len(overdue_tasks),
                "due_today_count": len(due_today),
                "high_priority_count": len(high_priority),
                "recommended_order": [task.get("task_id") for task in prioritized_tasks[:5]],
                "tasks": task_list[:10],  # 只返回前10个任务
            }
            
            logger.info(f"生成每日待办清单: {len(task_list)} 个任务")
            return todo_list
        
        except Exception as e:
            logger.error(f"获取每日待办清单异常: {e}")
            return {"error": str(e)}
    
    def _calculate_task_priority_score(self, task: Dict, current_time: datetime) -> float:
        """计算任务优先级分数"""
        try:
            score = 0.0
            
            # 基础优先级 (1-4, 1为最高)
            priority = task.get("priority", 4)
            score += (priority - 1) * 10  # 优先级越高，分数越低
            
            # 截止时间影响
            due_time = task.get("due_time", {}).get("timestamp")
            if due_time:
                due_date = datetime.fromtimestamp(int(due_time))
                hours_until_due = (due_date - current_time).total_seconds() / 3600
                
                if hours_until_due < 0:
                    # 已过期，分数大幅增加
                    score += 50
                elif hours_until_due < 24:
                    # 24小时内到期
                    score += 20
                elif hours_until_due < 72:
                    # 3天内到期
                    score += 10
            
            # 状态影响
            status = task.get("status", "todo")
            if status == "in_progress":
                score -= 5  # 进行中的任务优先级稍高
            elif status == "done":
                score += 100  # 已完成的任务优先级最低
            
            return score
        
        except Exception as e:
            logger.error(f"计算任务优先级分数异常: {e}")
            return 999.0
    
    def _send_task_notification(self, message: str, task_id: str, action: str):
        """发送任务通知"""
        try:
            # 这里可以集成消息发送功能
            # 暂时只记录日志
            logger.info(f"任务通知 [{action}]: {message} (任务ID: {task_id})")
            
            # TODO: 实现实际的消息发送
            # self.client.send_text_message(user_id, f"任务通知: {message}")
        
        except Exception as e:
            logger.error(f"发送任务通知异常: {e}")


# 全局助手实例
_task_assistant = None

def get_task_assistant() -> TaskAssistant:
    """获取任务助手单例"""
    global _task_assistant
    if _task_assistant is None:
        _task_assistant = TaskAssistant()
    return _task_assistant