from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

from .feishu_client import get_feishu_client, FeishuClient
from .calendar_assistant import get_calendar_assistant, CalendarAssistant
from .task_assistant import get_task_assistant, TaskAssistant

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 创建FastAPI应用
app = FastAPI(
    title="飞书AI助手",
    description="基于FastAPI和飞书开放平台构建的智能助手系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 依赖注入
def get_feishu_client_dep() -> FeishuClient:
    return get_feishu_client()

def get_calendar_assistant_dep() -> CalendarAssistant:
    return get_calendar_assistant()

def get_task_assistant_dep() -> TaskAssistant:
    return get_task_assistant()

# ==================== 基础API ====================

@app.get("/")
async def root():
    return {"message": "欢迎使用飞书AI助手API", "timestamp": datetime.now().isoformat()}

@app.get("/health")
async def health_check(feishu_client: FeishuClient = Depends(get_feishu_client_dep)):
    """健康检查，包含飞书API连接状态"""
    try:
        # 测试飞书API连接
        feishu_connected = feishu_client.test_connection()
        
        return {
            "status": "healthy",
            "service": "feishu-ai-assistant",
            "feishu_connected": feishu_connected,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@app.get("/version")
async def get_version():
    return {
        "version": "1.0.0",
        "name": "Feishu AI Assistant",
        "description": "基于FastAPI和飞书开放平台构建的智能助手系统",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/system/info")
async def get_system_info(feishu_client: FeishuClient = Depends(get_feishu_client_dep)):
    """获取系统信息"""
    try:
        system_info = feishu_client.get_system_info()
        return {
            "success": True,
            "data": system_info,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取系统信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 日历API ====================

@app.get("/calendar/calendars")
async def get_calendars(feishu_client: FeishuClient = Depends(get_feishu_client_dep)):
    """获取日历列表"""
    try:
        calendars = feishu_client.get_calendars()
        return {
            "success": True,
            "data": calendars,
            "count": len(calendars),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取日历列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/calendar/events")
async def get_calendar_events(
    calendar_id: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    feishu_client: FeishuClient = Depends(get_feishu_client_dep),
    calendar_assistant: CalendarAssistant = Depends(get_calendar_assistant_dep)
):
    """获取日历事件"""
    try:
        if not calendar_id:
            calendar_id = calendar_assistant.default_calendar_id
        
        events = feishu_client.get_events(calendar_id, start_time, end_time)
        return {
            "success": True,
            "data": events,
            "count": len(events),
            "calendar_id": calendar_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取日历事件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/calendar/today")
async def get_today_events(calendar_assistant: CalendarAssistant = Depends(get_calendar_assistant_dep)):
    """获取今天的事件"""
    try:
        events = calendar_assistant.get_today_events()
        return {
            "success": True,
            "data": events,
            "count": len(events),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取今天事件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/calendar/upcoming")
async def get_upcoming_events(
    hours: int = 24,
    calendar_assistant: CalendarAssistant = Depends(get_calendar_assistant_dep)
):
    """获取即将发生的事件"""
    try:
        events = calendar_assistant.get_upcoming_events(hours)
        return {
            "success": True,
            "data": events,
            "count": len(events),
            "hours": hours,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取即将发生事件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/calendar/meeting")
async def create_meeting(
    title: str,
    start_time: str,
    duration_minutes: int = 60,
    description: Optional[str] = None,
    location: Optional[str] = None,
    calendar_assistant: CalendarAssistant = Depends(get_calendar_assistant_dep)
):
    """创建会议"""
    try:
        # 解析开始时间
        try:
            start_datetime = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        except ValueError:
            # 尝试其他格式
            start_datetime = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        
        result = calendar_assistant.create_meeting(
            title, start_datetime, duration_minutes, description, location
        )
        
        if result:
            return {
                "success": True,
                "data": result,
                "message": "会议创建成功",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="会议创建失败")
    
    except Exception as e:
        logger.error(f"创建会议失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/calendar/analysis")
async def analyze_schedule(calendar_assistant: CalendarAssistant = Depends(get_calendar_assistant_dep)):
    """分析日程安排"""
    try:
        analysis = calendar_assistant.analyze_schedule()
        return {
            "success": True,
            "data": analysis,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"分析日程失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/calendar/daily-summary")
async def get_daily_summary(calendar_assistant: CalendarAssistant = Depends(get_calendar_assistant_dep)):
    """获取每日日程摘要"""
    try:
        summary = calendar_assistant.get_daily_summary()
        return {
            "success": True,
            "data": summary,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取每日摘要失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 任务API ====================

@app.get("/tasks")
async def get_tasks(
    status: Optional[str] = None,
    priority: Optional[int] = None,
    task_assistant: TaskAssistant = Depends(get_task_assistant_dep)
):
    """获取任务列表"""
    try:
        if priority:
            tasks = task_assistant.get_tasks_by_priority(priority)
        elif status:
            tasks = task_assistant.get_my_tasks(status)
        else:
            tasks = task_assistant.get_my_tasks()
        
        return {
            "success": True,
            "data": tasks,
            "count": len(tasks),
            "filters": {"status": status, "priority": priority},
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取任务列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/overdue")
async def get_overdue_tasks(task_assistant: TaskAssistant = Depends(get_task_assistant_dep)):
    """获取过期任务"""
    try:
        tasks = task_assistant.get_overdue_tasks()
        return {
            "success": True,
            "data": tasks,
            "count": len(tasks),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取过期任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/due-today")
async def get_tasks_due_today(task_assistant: TaskAssistant = Depends(get_task_assistant_dep)):
    """获取今天到期的任务"""
    try:
        tasks = task_assistant.get_tasks_due_today()
        return {
            "success": True,
            "data": tasks,
            "count": len(tasks),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取今天到期任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tasks")
async def create_task(
    title: str,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: int = 3,
    task_assistant: TaskAssistant = Depends(get_task_assistant_dep)
):
    """创建任务"""
    try:
        due_datetime = None
        if due_date:
            try:
                due_datetime = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except ValueError:
                due_datetime = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
        
        result = task_assistant.create_task(title, description, due_datetime, priority)
        
        if result:
            return {
                "success": True,
                "data": result,
                "message": "任务创建成功",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="任务创建失败")
    
    except Exception as e:
        logger.error(f"创建任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/prioritize")
async def prioritize_tasks(task_assistant: TaskAssistant = Depends(get_task_assistant_dep)):
    """智能优先级排序"""
    try:
        tasks = task_assistant.prioritize_tasks()
        return {
            "success": True,
            "data": tasks,
            "count": len(tasks),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"智能排序任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/analysis")
async def analyze_workload(task_assistant: TaskAssistant = Depends(get_task_assistant_dep)):
    """分析工作负载"""
    try:
        analysis = task_assistant.analyze_workload()
        return {
            "success": True,
            "data": analysis,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"分析工作负载失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/daily-todo")
async def get_daily_todo_list(task_assistant: TaskAssistant = Depends(get_task_assistant_dep)):
    """获取每日待办清单"""
    try:
        todo_list = task_assistant.get_daily_todo_list()
        return {
            "success": True,
            "data": todo_list,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取每日待办清单失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 消息API ====================

@app.post("/messages/send")
async def send_message(
    receive_id: str,
    message: str,
    receive_id_type: str = "open_id",
    feishu_client: FeishuClient = Depends(get_feishu_client_dep)
):
    """发送消息"""
    try:
        result = feishu_client.send_text_message(receive_id, message, receive_id_type)
        
        if result:
            return {
                "success": True,
                "data": result,
                "message": "消息发送成功",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="消息发送失败")
    
    except Exception as e:
        logger.error(f"发送消息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 文档API ====================

@app.get("/documents")
async def get_documents(
    folder_token: Optional[str] = None,
    feishu_client: FeishuClient = Depends(get_feishu_client_dep)
):
    """获取文档列表"""
    try:
        documents = feishu_client.get_documents(folder_token)
        return {
            "success": True,
            "data": documents,
            "count": len(documents),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取文档列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 用户API ====================

@app.get("/users")
async def get_users(
    department_id: Optional[str] = None,
    feishu_client: FeishuClient = Depends(get_feishu_client_dep)
):
    """获取用户列表"""
    try:
        users = feishu_client.get_users(department_id)
        return {
            "success": True,
            "data": users,
            "count": len(users),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取用户列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 飞书消息处理API ====================

from pydantic import BaseModel
from typing import Dict, Any
try:
    from .webhook_handler import get_webhook_handler
except ImportError:
    # 开发环境可能需要的回退
    from webhook_handler import get_webhook_handler

class FeishuMessage(BaseModel):
    """飞书消息模型"""
    sender_id: str
    sender_name: str = ""
    message_type: str = "text"
    content: Dict[str, Any]
    chat_id: str = ""
    chat_type: str = "p2p"
    timestamp: str = ""

class FeishuResponse(BaseModel):
    """飞书响应模型"""
    success: bool
    reply: str
    data: Dict[str, Any] = {}
    timestamp: str = ""

@app.post("/feishu/process")
async def process_feishu_message(
    message: FeishuMessage,
    feishu_client: FeishuClient = Depends(get_feishu_client_dep),
    calendar_assistant: CalendarAssistant = Depends(get_calendar_assistant_dep),
    task_assistant: TaskAssistant = Depends(get_task_assistant_dep)
):
    """
    处理来自飞书机器人的转发消息
    支持：日历查询、任务管理、智能对话
    """
    try:
        logger.info(f"收到飞书消息: {message.sender_name} - {message.content}")
        
        # 提取消息内容
        if message.message_type == "text":
            text_content = message.content.get("text", "")
        else:
            text_content = str(message.content)
        
        # 智能路由处理
        response_text = ""
        
        # 1. 日历相关查询
        if any(keyword in text_content.lower() for keyword in ["日历", "会议", "日程", "安排", "今天有什么"]):
            if "今天" in text_content or "今日" in text_content:
                # 获取今日日历
                events = calendar_assistant.get_today_events()
                if events:
                    response_text = "📅 今日日程安排:\n"
                    for event in events:
                        response_text += f"• {event.get('summary', '未命名')} ({event.get('start_time', '')})\n"
                else:
                    response_text = "✅ 今天没有安排会议或日程。"
            elif "明天" in text_content:
                # 获取明日日历
                events = calendar_assistant.get_tomorrow_events()
                if events:
                    response_text = "📅 明日日程安排:\n"
                    for event in events:
                        response_text += f"• {event.get('summary', '未命名')} ({event.get('start_time', '')})\n"
                else:
                    response_text = "✅ 明天没有安排会议或日程。"
            else:
                # 通用日历查询
                calendars = feishu_client.get_calendars()
                response_text = f"📅 您有 {len(calendars)} 个日历。输入'今天日程'或'明天会议'查看具体安排。"
        
        # 2. 任务相关查询
        elif any(keyword in text_content.lower() for keyword in ["任务", "待办", "todo", "完成", "进度"]):
            if "今天" in text_content or "今日" in text_content:
                tasks = task_assistant.get_tasks_due_today()
                if tasks:
                    response_text = "✅ 今日待办任务:\n"
                    for task in tasks:
                        response_text += f"• {task.get('summary', '未命名')} (优先级: {task.get('priority', '普通')})\n"
                else:
                    response_text = "🎉 今天没有待办任务！"
            elif "过期" in text_content or "逾期" in text_content:
                tasks = task_assistant.get_overdue_tasks()
                if tasks:
                    response_text = "⚠️ 过期任务:\n"
                    for task in tasks:
                        response_text += f"• {task.get('summary', '未命名')} (过期时间: {task.get('due_time', '')})\n"
                else:
                    response_text = "✅ 没有过期任务。"
            else:
                tasks = task_assistant.get_my_tasks()
                response_text = f"📋 您有 {len(tasks)} 个任务。输入'今天任务'或'过期任务'查看具体内容。"
        
        # 3. 问候和帮助
        elif any(keyword in text_content.lower() for keyword in ["你好", "hi", "hello", "help", "帮助", "功能"]):
            response_text = """🤖 飞书AI助手已上线！
            
支持功能：
📅 日历管理：查询今天/明天日程、会议安排
✅ 任务管理：查看今日任务、过期任务、任务进度
📊 工作报告：生成每日综合报告
💬 智能对话：回答各种问题

试试这些命令：
• "今天有什么安排？"
• "查看今天任务"
• "生成每日报告"
• "帮助" 查看完整功能"""
        
        # 4. 工作报告
        elif "报告" in text_content or "summary" in text_content.lower():
            # 获取日历摘要
            calendar_summary = calendar_assistant.get_daily_summary()
            # 获取任务分析
            task_analysis = task_assistant.analyze_workload()
            
            response_text = f"""📊 每日工作报告：
            
📅 日历摘要：{calendar_summary.get('summary', '无数据')}
✅ 任务状态：{task_analysis.get('summary', '无数据')}
⏰ 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}"""
        
        # 5. 默认回复 - 智能对话
        else:
            # 这里可以集成更复杂的AI对话逻辑
            response_text = f"收到您的消息：'{text_content}'\n\n我是飞书AI助手，可以帮您管理日历、任务，或回答其他问题。需要什么帮助？"
        
        # 如果需要，自动回复给发送者
        auto_reply = True
        if auto_reply and message.sender_id:
            try:
                feishu_client.send_text_message(
                    receive_id=message.sender_id,
                    message=response_text,
                    receive_id_type="open_id"
                )
                logger.info(f"已自动回复消息给 {message.sender_name}")
            except Exception as e:
                logger.error(f"自动回复失败: {e}")
        
        return FeishuResponse(
            success=True,
            reply=response_text,
            data={
                "processed": True,
                "message_type": message.message_type,
                "sender": message.sender_name,
                "auto_replied": auto_reply
            },
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"处理飞书消息失败: {e}")
        return FeishuResponse(
            success=False,
            reply=f"处理消息时出错: {str(e)}",
            data={"error": str(e)},
            timestamp=datetime.now().isoformat()
        )

# ==================== 智能助手API ====================

@app.get("/assistant/daily-report")
async def get_daily_report(
    calendar_assistant: CalendarAssistant = Depends(get_calendar_assistant_dep),
    task_assistant: TaskAssistant = Depends(get_task_assistant_dep)
):
    """获取每日综合报告"""
    try:
        # 获取日历摘要
        calendar_summary = calendar_assistant.get_daily_summary()
        
        # 获取任务分析
        task_analysis = task_assistant.analyze_workload()
        
        # 获取每日待办
        daily_todo = task_assistant.get_daily_todo_list()
        
        # 生成综合报告
        report = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "calendar": calendar_summary,
            "tasks": task_analysis,
            "daily_todo": daily_todo,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "data": report,
            "message": "每日报告生成成功",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"生成每日报告失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Webhook API ====================

@app.post("/feishu/webhook")
async def feishu_webhook(
    request: Dict[str, Any],
    x_lark_timestamp: str = Header(None, alias="X-Lark-Request-Timestamp"),
    x_lark_nonce: str = Header(None, alias="X-Lark-Request-Nonce"),
    x_lark_signature: str = Header(None, alias="X-Lark-Signature")
):
    """
    飞书Webhook接收端点
    处理飞书开放平台的事件订阅
    """
    try:
        logger.info(f"收到Webhook请求: {request.get('type', 'unknown')}")
        
        # 直接从环境变量读取配置，完全绕过config.py
        import os
        verification_token = os.getenv("FEISHU_WEBHOOK_VERIFICATION_TOKEN", "")
        encrypt_key = os.getenv("FEISHU_WEBHOOK_ENCRYPT_KEY", "")
        
        # 验证签名（如果配置了验证令牌）
        if x_lark_timestamp and x_lark_nonce and x_lark_signature and verification_token:
            import hashlib
            # 拼接字符串
            content = f"{x_lark_timestamp}{x_lark_nonce}{verification_token}".encode('utf-8')
            # 计算SHA1哈希
            hash_obj = hashlib.sha1(content)
            calculated_signature = hash_obj.hexdigest()
            
            if calculated_signature != x_lark_signature:
                logger.warning(f"签名验证失败: {x_lark_signature}")
                raise HTTPException(status_code=403, detail="签名验证失败")
        
        # 处理加密数据（如果配置了加密密钥）
        encrypted_data = request.get("encrypt")
        if encrypted_data and encrypt_key:
            import base64
            import json
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.primitives import padding
            from cryptography.hazmat.backends import default_backend
            
            try:
                # Base64解码
                encrypted_bytes = base64.b64decode(encrypted_data)
                
                # 提取IV和密文
                iv = encrypted_bytes[:16]
                ciphertext = encrypted_bytes[16:]
                
                # AES解密
                cipher = Cipher(
                    algorithms.AES(encrypt_key.encode('utf-8')),
                    modes.CBC(iv),
                    backend=default_backend()
                )
                decryptor = cipher.decryptor()
                padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
                
                # 去除PKCS7填充
                unpadder = padding.PKCS7(128).unpadder()
                plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
                
                # 解析JSON
                request = json.loads(plaintext.decode('utf-8'))
                
            except Exception as e:
                logger.error(f"解密数据失败: {e}")
                # 不解密，继续处理原始数据
        
        # 处理事件 - 简化版本，专注于URL验证
        event_type = request.get("type")
        
        # URL验证事件
        if event_type == "url_verification":
            challenge = request.get("challenge", "")
            logger.info(f"URL验证成功: {challenge[:20]}...")
            return {"challenge": challenge}
        
        # 其他事件暂时返回成功
        logger.info(f"收到飞书事件: {event_type}")
        return {"success": True, "message": f"事件 {event_type} 已接收"}
        
    except Exception as e:
        logger.error(f"处理Webhook请求失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 独立Webhook API (绕过config.py) ====================

@app.post("/feishu/webhook/simple")
async def feishu_webhook_simple(request: Dict[str, Any]):
    """
    简化的飞书Webhook接收端点
    完全绕过config.py的验证问题
    """
    try:
        import os
        import json
        
        # 直接从环境变量读取，不经过config.py
        verification_token = os.getenv("FEISHU_WEBHOOK_VERIFICATION_TOKEN", "")
        
        # 只处理URL验证
        event_type = request.get("type")
        
        if event_type == "url_verification":
            challenge = request.get("challenge", "")
            logger.info(f"简单Webhook URL验证成功: {challenge[:20]}...")
            return {"challenge": challenge}
        
        # 其他事件返回成功
        logger.info(f"简单Webhook收到事件: {event_type}")
        return {"success": True, "message": f"事件 {event_type} 已接收"}
        
    except Exception as e:
        logger.error(f"简单Webhook处理失败: {e}")
        return {"success": False, "error": str(e)}


# ==================== 错误处理 ====================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    logger.error(f"全局异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
