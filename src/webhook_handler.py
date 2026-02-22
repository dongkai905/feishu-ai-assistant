"""
飞书Webhook处理模块
处理来自飞书开放平台的事件订阅消息
"""

import hashlib
import base64
import json
import time
from typing import Dict, Any, Optional
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import logging

logger = logging.getLogger(__name__)


class FeishuWebhookHandler:
    """飞书Webhook处理器"""
    
    def __init__(self, verification_token: str, encrypt_key: str):
        """
        初始化Webhook处理器
        
        Args:
            verification_token: 飞书开放平台配置的Verification Token
            encrypt_key: 飞书开放平台配置的Encrypt Key
        """
        self.verification_token = verification_token
        self.encrypt_key = encrypt_key.encode('utf-8') if encrypt_key else None
        
    def verify_signature(self, timestamp: str, nonce: str, signature: str) -> bool:
        """
        验证飞书Webhook签名
        
        Args:
            timestamp: 时间戳
            nonce: 随机数
            signature: 签名
            
        Returns:
            bool: 验证是否通过
        """
        try:
            # 拼接字符串
            content = f"{timestamp}{nonce}{self.verification_token}".encode('utf-8')
            
            # 计算SHA1哈希
            hash_obj = hashlib.sha1(content)
            calculated_signature = hash_obj.hexdigest()
            
            # 比较签名
            return calculated_signature == signature
            
        except Exception as e:
            logger.error(f"验证签名失败: {e}")
            return False
    
    def decrypt_data(self, encrypted_data: str) -> Optional[Dict[str, Any]]:
        """
        解密飞书加密数据
        
        Args:
            encrypted_data: 加密的数据
            
        Returns:
            Optional[Dict]: 解密后的数据，失败返回None
        """
        if not self.encrypt_key:
            logger.warning("未配置加密密钥，跳过解密")
            return None
            
        try:
            # Base64解码
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # 提取IV和密文
            iv = encrypted_bytes[:16]
            ciphertext = encrypted_bytes[16:]
            
            # AES解密
            cipher = Cipher(
                algorithms.AES(self.encrypt_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            # 去除PKCS7填充
            unpadder = padding.PKCS7(128).unpadder()
            plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
            
            # 解析JSON
            return json.loads(plaintext.decode('utf-8'))
            
        except Exception as e:
            logger.error(f"解密数据失败: {e}")
            return None
    
    def process_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理飞书事件
        
        Args:
            event_data: 事件数据
            
        Returns:
            Dict: 处理结果
        """
        try:
            event_type = event_data.get("type")
            logger.info(f"收到飞书事件: {event_type}")
            
            # URL验证事件
            if event_type == "url_verification":
                challenge = event_data.get("challenge", "")
                return {"challenge": challenge}
            
            # 消息事件
            elif event_type == "im.message.receive_v1":
                return self._process_message_event(event_data)
            
            # 其他事件
            else:
                logger.info(f"忽略事件类型: {event_type}")
                return {"success": True, "message": f"事件 {event_type} 已接收"}
                
        except Exception as e:
            logger.error(f"处理事件失败: {e}")
            return {"success": False, "error": str(e)}
    
    def _process_message_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理消息事件
        
        Args:
            event_data: 消息事件数据
            
        Returns:
            Dict: 处理结果
        """
        try:
            # 提取消息信息
            event = event_data.get("event", {})
            message = event.get("message", {})
            sender = event.get("sender", {})
            
            message_id = message.get("message_id", "")
            message_type = message.get("message_type", "")
            chat_type = message.get("chat_type", "")
            chat_id = message.get("chat_id", "")
            content = message.get("content", "")
            
            sender_id = sender.get("sender_id", {})
            sender_user_id = sender_id.get("user_id", "")
            sender_open_id = sender_id.get("open_id", "")
            
            logger.info(f"收到消息: {message_id}, 类型: {message_type}, 发送者: {sender_user_id}")
            
            # 解析消息内容
            message_content = self._parse_message_content(content, message_type)
            
            # 返回处理结果
            return {
                "success": True,
                "message": "消息已接收",
                "data": {
                    "message_id": message_id,
                    "message_type": message_type,
                    "chat_type": chat_type,
                    "chat_id": chat_id,
                    "sender_user_id": sender_user_id,
                    "sender_open_id": sender_open_id,
                    "content": message_content,
                    "timestamp": int(time.time())
                }
            }
            
        except Exception as e:
            logger.error(f"处理消息事件失败: {e}")
            return {"success": False, "error": str(e)}
    
    def _parse_message_content(self, content: str, message_type: str) -> str:
        """
        解析消息内容
        
        Args:
            content: 原始内容
            message_type: 消息类型
            
        Returns:
            str: 解析后的文本内容
        """
        try:
            if message_type == "text":
                # 文本消息
                content_dict = json.loads(content)
                return content_dict.get("text", "")
            elif message_type == "post":
                # 富文本消息
                return "[富文本消息]"
            elif message_type == "image":
                return "[图片消息]"
            elif message_type == "file":
                return "[文件消息]"
            elif message_type == "audio":
                return "[语音消息]"
            elif message_type == "media":
                return "[媒体消息]"
            else:
                return f"[{message_type}类型消息]"
                
        except Exception as e:
            logger.error(f"解析消息内容失败: {e}")
            return content
    
    def generate_response(self, 
                         success: bool = True, 
                         message: str = "success", 
                         data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        生成标准响应
        
        Args:
            success: 是否成功
            message: 消息
            data: 数据
            
        Returns:
            Dict: 标准响应
        """
        response = {
            "code": 0 if success else 1,
            "msg": message,
            "data": data or {}
        }
        
        # 添加时间戳
        response["timestamp"] = int(time.time())
        
        return response


# 全局Webhook处理器实例
_webhook_handler = None

def get_webhook_handler() -> FeishuWebhookHandler:
    """获取Webhook处理器实例"""
    global _webhook_handler
    if _webhook_handler is None:
        import os
        # 直接从环境变量读取，避免config.py的验证问题
        verification_token = os.getenv("FEISHU_WEBHOOK_VERIFICATION_TOKEN", "")
        encrypt_key = os.getenv("FEISHU_WEBHOOK_ENCRYPT_KEY", "")
        _webhook_handler = FeishuWebhookHandler(
            verification_token=verification_token,
            encrypt_key=encrypt_key
        )
    return _webhook_handler

# 独立的Webhook处理函数，完全绕过config.py
def handle_webhook_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理Webhook请求的独立函数
    
    Args:
        data: 请求数据
        
    Returns:
        Dict: 响应数据
    """
    import os
    import json
    
    # 直接从环境变量读取配置
    verification_token = os.getenv("FEISHU_WEBHOOK_VERIFICATION_TOKEN", "")
    encrypt_key = os.getenv("FEISHU_WEBHOOK_ENCRYPT_KEY", "")
    
    # 创建处理器
    handler = FeishuWebhookHandler(
        verification_token=verification_token,
        encrypt_key=encrypt_key
    )
    
    # 处理事件
    return handler.process_event(data)