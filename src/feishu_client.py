"""
飞书API客户端
提供日历、任务、消息、文档等API的统一接口
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

import lark_oapi as lark
from lark_oapi.api.calendar.v4 import *
from lark_oapi.api.task.v2 import *
from lark_oapi.api.im.v1 import *
from lark_oapi.api.drive.v1 import *
from lark_oapi.api.contact.v3 import *

logger = logging.getLogger(__name__)


class FeishuClient:
    """飞书API客户端"""
    
    def __init__(self, app_id: str = None, app_secret: str = None):
        """
        初始化飞书客户端
        
        Args:
            app_id: 飞书应用ID
            app_secret: 飞书应用密钥
        """
        self.app_id = app_id or os.getenv("FEISHU_APP_ID")
        self.app_secret = app_secret or os.getenv("FEISHU_APP_SECRET")
        
        if not self.app_id or not self.app_secret:
            raise ValueError("飞书应用凭证未配置，请设置FEISHU_APP_ID和FEISHU_APP_SECRET环境变量")
        
        # 创建客户端配置
        self.client = lark.Client.builder() \
            .app_id(self.app_id) \
            .app_secret(self.app_secret) \
            .log_level(lark.LogLevel.INFO) \
            .build()
        
        logger.info(f"飞书客户端初始化完成，App ID: {self.app_id[:8]}...")
    
    # ==================== 日历API ====================
    
    def get_calendars(self) -> List[Dict]:
        """获取日历列表"""
        try:
            req = ListCalendarRequest.builder().build()
            resp = self.client.calendar.v4.calendar.list(req)
            
            if not resp.success():
                logger.error(f"获取日历列表失败: {resp.msg}, {resp.error}")
                return []
            
            calendars = []
            for calendar in resp.data.calendar_list:
                calendars.append({
                    "calendar_id": calendar.calendar_id,
                    "summary": calendar.summary,
                    "description": calendar.description,
                    "permissions": calendar.permissions,
                    "color": calendar.color,
                    "type": calendar.type,
                    "summary_alias": calendar.summary_alias,
                })
            
            logger.info(f"获取到 {len(calendars)} 个日历")
            return calendars
        
        except Exception as e:
            logger.error(f"获取日历列表异常: {e}")
            return []
    
    def get_events(self, calendar_id: str, start_time: str = None, end_time: str = None) -> List[Dict]:
        """
        获取日历事件
        
        Args:
            calendar_id: 日历ID
            start_time: 开始时间 (格式: 2026-02-22T00:00:00+08:00)
            end_time: 结束时间 (格式: 2026-02-23T00:00:00+08:00)
        """
        try:
            # 默认获取今天的事件
            if not start_time:
                start_time = datetime.now().strftime("%Y-%m-%dT00:00:00+08:00")
            if not end_time:
                end_time = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00+08:00")
            
            req = ListCalendarEventRequest.builder() \
                .calendar_id(calendar_id) \
                .start_time(start_time) \
                .end_time(end_time) \
                .page_size(500) \
                .build()
            
            resp = self.client.calendar.v4.calendar_event.list(req)
            
            if not resp.success():
                logger.error(f"获取日历事件失败: {resp.msg}, {resp.error}")
                return []
            
            events = []
            for event in resp.data.items:
                events.append({
                    "event_id": event.event_id,
                    "summary": event.summary,
                    "description": event.description,
                    "start_time": str(event.start_time) if event.start_time else None,
                    "end_time": str(event.end_time) if event.end_time else None,
                    "location": str(event.location) if event.location else None,
                    "attendees": [str(attendee) for attendee in event.attendees] if event.attendees else [],
                    "organizer": str(event.organizer) if event.organizer else None,
                    "status": event.status,
                    "visibility": event.visibility,
                    "recurrence": event.recurrence,
                })
            
            logger.info(f"获取到 {len(events)} 个日历事件")
            return events
        
        except Exception as e:
            logger.error(f"获取日历事件异常: {e}")
            return []
    
    def create_event(self, calendar_id: str, summary: str, start_time: Dict, 
                    end_time: Dict, description: str = None, location: str = None) -> Optional[Dict]:
        """
        创建日历事件
        
        Args:
            calendar_id: 日历ID
            summary: 事件标题
            start_time: 开始时间 {date: "2026-02-22", timestamp: "1708560000", timezone: "Asia/Shanghai"}
            end_time: 结束时间
            description: 事件描述
            location: 事件地点
        """
        try:
            # 构建事件数据
            event_data = {
                "summary": summary,
                "start_time": start_time,
                "end_time": end_time,
            }
            
            if description:
                event_data["description"] = description
            
            if location:
                event_data["location"] = {"name": location}
            
            # 创建日历事件请求体
            calendar_event = CalendarEvent.builder() \
                .summary(summary) \
                .start_time(start_time) \
                .end_time(end_time) \
                .build()
            
            if description:
                calendar_event.description = description
            
            if location:
                calendar_event.location = {"name": location}
            
            req = CreateCalendarEventRequest.builder() \
                .calendar_id(calendar_id) \
                .request_body(calendar_event) \
                .build()
            
            resp = self.client.calendar.v4.calendar_event.create(req)
            
            if not resp.success():
                logger.error(f"创建日历事件失败: {resp.msg}, {resp.error}")
                return None
            
            event = resp.data.event
            result = {
                "event_id": event.event_id,
                "summary": event.summary,
                "description": event.description,
                "start_time": str(event.start_time) if event.start_time else None,
                "end_time": str(event.end_time) if event.end_time else None,
                "location": str(event.location) if event.location else None,
                "status": "created",
            }
            
            logger.info(f"日历事件创建成功: {summary}")
            return result
        
        except Exception as e:
            logger.error(f"创建日历事件异常: {e}")
            return None
    
    # ==================== 任务API ====================
    
    def get_tasks(self, user_id: str = None) -> List[Dict]:
        """
        获取任务列表
        
        Args:
            user_id: 用户ID，为空则获取所有任务
        """
        try:
            req = ListTaskRequest.builder() \
                .page_size(100) \
                .user_id_type("user_id") \
                .build()
            
            if user_id:
                req.user_id = user_id
            
            resp = self.client.task.v2.task.list(req)
            
            if not resp.success():
                logger.error(f"获取任务列表失败: {resp.msg}, {resp.error}")
                return []
            
            tasks = []
            for task in resp.data.items:
                tasks.append({
                    "task_id": task.task_id,
                    "summary": task.summary,
                    "description": task.description,
                    "due_time": str(task.due) if task.due else None,
                    "creator": str(task.creator) if task.creator else None,
                    "assignee": str(task.assignee) if task.assignee else None,
                    "status": task.status,
                    "priority": task.priority,
                    "tags": task.tags,
                    "created_at": task.created_at,
                    "updated_at": task.updated_at,
                })
            
            logger.info(f"获取到 {len(tasks)} 个任务")
            return tasks
        
        except Exception as e:
            logger.error(f"获取任务列表异常: {e}")
            return []
    
    def create_task(self, summary: str, description: str = None, due_time: Dict = None,
                   assignee_id: str = None, priority: int = 1) -> Optional[Dict]:
        """
        创建任务
        
        Args:
            summary: 任务标题
            description: 任务描述
            due_time: 截止时间 {timestamp: "1708560000", timezone: "Asia/Shanghai"}
            assignee_id: 负责人ID
            priority: 优先级 (1-4, 1为最高)
        """
        try:
            task_data = {
                "summary": summary,
                "priority": priority,
            }
            
            if description:
                task_data["description"] = description
            
            if due_time:
                task_data["due"] = due_time
            
            if assignee_id:
                task_data["assignee"] = {"id": assignee_id, "type": "user"}
            
            # 创建任务对象
            task_builder = Task.builder() \
                .summary(summary)
            
            # 设置优先级
            task_builder.priority = priority
            
            if description:
                task_builder.description = description
            
            if due_time:
                task_builder.due = due_time
            
            if assignee_id:
                task_builder.assignee = {"id": assignee_id, "type": "user"}
            
            task = task_builder.build()
            
            req = CreateTaskRequest.builder() \
                .request_body(task) \
                .user_id_type("user_id") \
                .build()
            
            resp = self.client.task.v2.task.create(req)
            
            if not resp.success():
                logger.error(f"创建任务失败: {resp.msg}, {resp.error}")
                return None
            
            task = resp.data.task
            result = {
                "task_id": task.task_id,
                "summary": task.summary,
                "description": task.description,
                "due_time": str(task.due) if hasattr(task, 'due') and task.due else None,
                "status": task.status,
                "priority": task.priority if hasattr(task, 'priority') else None,
                "created_at": task.created_at if hasattr(task, 'created_at') else None,
            }
            
            # 可选字段
            if hasattr(task, 'assignee') and task.assignee:
                result["assignee"] = str(task.assignee)
            
            logger.info(f"任务创建成功: {summary}")
            return result
        
        except Exception as e:
            logger.error(f"创建任务异常: {e}")
            import traceback
            logger.error(f"详细堆栈: {traceback.format_exc()}")
            return None
    
    # ==================== 消息API ====================
    
    def send_message(self, receive_id: str, msg_type: str, content: Dict, 
                    receive_id_type: str = "open_id") -> Optional[Dict]:
        """
        发送消息
        
        Args:
            receive_id: 接收者ID
            msg_type: 消息类型 (text, post, image, interactive)
            content: 消息内容
            receive_id_type: ID类型 (open_id, user_id, email, chat_id)
        """
        try:
            # 创建消息请求体
            message_body = CreateMessageRequestBody.builder() \
                .receive_id(receive_id) \
                .msg_type(msg_type) \
                .content(json.dumps(content)) \
                .build()
            
            req = CreateMessageRequest.builder() \
                .receive_id_type(receive_id_type) \
                .request_body(message_body) \
                .build()
            
            resp = self.client.im.v1.message.create(req)
            
            if not resp.success():
                error_msg = getattr(resp, 'error', '未知错误')
                logger.error(f"发送消息失败: {resp.msg}, {error_msg}")
                return None
            
            result = {
                "message_id": resp.data.message_id,
                "root_id": resp.data.root_id,
                "parent_id": resp.data.parent_id,
                "msg_type": msg_type,
                "create_time": resp.data.create_time,
                "update_time": resp.data.update_time,
                "deleted": resp.data.deleted,
                "updated": resp.data.updated,
            }
            
            logger.info(f"消息发送成功: {msg_type}")
            return result
        
        except Exception as e:
            logger.error(f"发送消息异常: {e}")
            return None
    
    def send_text_message(self, receive_id: str, text: str, receive_id_type: str = "open_id") -> Optional[Dict]:
        """发送文本消息"""
        content = {"text": text}
        return self.send_message(receive_id, "text", content, receive_id_type)
    
    # ==================== 文档API ====================
    
    def get_documents(self, folder_token: str = None) -> List[Dict]:
        """
        获取文档列表
        
        Args:
            folder_token: 文件夹token，为空则获取根目录
        """
        try:
            if folder_token:
                req = ListFileRequest.builder() \
                    .folder_token(folder_token) \
                    .page_size(100) \
                    .build()
            else:
                req = ListFileRequest.builder() \
                    .page_size(100) \
                    .build()
            
            resp = self.client.drive.v1.file.list(req)
            
            if not resp.success():
                logger.error(f"获取文档列表失败: {resp.msg}, {resp.error}")
                return []
            
            documents = []
            for file in resp.data.files:
                documents.append({
                    "token": file.token,
                    "name": file.name,
                    "type": file.type,
                    "parent_token": file.parent_token,
                    "url": file.url,
                    "size": file.size,
                    "created_time": file.created_time,
                    "modified_time": file.modified_time,
                    "owner_id": file.owner_id,
                })
            
            logger.info(f"获取到 {len(documents)} 个文档")
            return documents
        
        except Exception as e:
            logger.error(f"获取文档列表异常: {e}")
            return []
    
    # ==================== 用户API ====================
    
    def get_users(self, department_id: str = None) -> List[Dict]:
        """
        获取用户列表
        
        Args:
            department_id: 部门ID，为空则获取所有用户
        """
        try:
            req = ListUserRequest.builder() \
                .page_size(100) \
                .user_id_type("user_id") \
                .department_id_type("department_id") \
                .build()
            
            if department_id:
                req.department_id = department_id
            
            resp = self.client.contact.v3.user.list(req)
            
            if not resp.success():
                logger.error(f"获取用户列表失败: {resp.msg}, {resp.error}")
                return []
            
            users = []
            for user in resp.data.items:
                users.append({
                    "user_id": user.user_id,
                    "name": user.name,
                    "email": user.email,
                    "mobile": user.mobile,
                    "avatar": str(user.avatar) if user.avatar else None,
                    "status": str(user.status) if user.status else None,
                    "department_ids": user.department_ids,
                })
            
            logger.info(f"获取到 {len(users)} 个用户")
            return users
        
        except Exception as e:
            logger.error(f"获取用户列表异常: {e}")
            return []
    
    # ==================== 工具方法 ====================
    
    def get_access_token(self) -> Optional[str]:
        """
        获取access_token
        
        Returns:
            access_token字符串，失败返回None
        """
        try:
            # 直接调用飞书API获取tenant_access_token
            import requests
            
            url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
            headers = {
                "Content-Type": "application/json; charset=utf-8"
            }
            data = {
                "app_id": self.app_id,
                "app_secret": self.app_secret
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    access_token = result.get("tenant_access_token")
                    logger.info("成功获取access_token")
                    return access_token
                else:
                    logger.error(f"获取access_token失败: {result.get('msg')}")
                    return None
            else:
                logger.error(f"获取access_token HTTP错误: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"获取access_token异常: {e}")
            return None
    
    def test_connection(self) -> bool:
        """测试API连接"""
        try:
            # 尝试获取用户列表来测试连接
            req = ListUserRequest.builder() \
                .page_size(1) \
                .user_id_type("user_id") \
                .department_id_type("department_id") \
                .build()
            
            resp = self.client.contact.v3.user.list(req)
            
            if resp.success():
                logger.info("飞书API连接测试成功")
                return True
            else:
                logger.error(f"飞书API连接测试失败: {resp.msg}, {resp.error}")
                return False
        
        except Exception as e:
            logger.error(f"飞书API连接测试异常: {e}")
            return False
    
    def get_system_info(self) -> Dict:
        """获取系统信息"""
        return {
            "app_id": self.app_id[:8] + "..." if self.app_id else None,
            "connected": self.test_connection(),
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
        }


# 全局客户端实例
_feishu_client = None

def get_feishu_client() -> FeishuClient:
    """获取飞书客户端单例"""
    global _feishu_client
    if _feishu_client is None:
        _feishu_client = FeishuClient()
    return _feishu_client