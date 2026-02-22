#!/usr/bin/env python3
"""
发送测试消息到飞书群聊
"""

import requests
import json
import sys
from datetime import datetime

def send_test_message(chat_id, message=None):
    """发送测试消息到指定的chat_id"""
    
    base_url = "http://localhost:8000"
    
    if message is None:
        message = f"""🎉 测试消息来自Feishu AI Assistant系统

📅 发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📍 系统状态: 正常运行
🔧 功能验证: 消息发送测试

✅ 测试目的:
1. 验证飞书API连接
2. 测试消息发送功能
3. 确认群聊接收正常

💡 后续步骤:
- 如果收到此消息，说明系统正常工作
- 可以开始集成其他功能
- 准备生产环境部署

---
系统: Feishu AI Assistant v1.0
时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    print("📤 准备发送测试消息...")
    print(f"群聊ID: {chat_id}")
    print(f"消息长度: {len(message)} 字符")
    print(f"发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # 构建URL - 使用chat_id类型
        url = f"{base_url}/messages/send?receive_id={chat_id}&message={requests.utils.quote(message)}&receive_id_type=chat_id"
        
        print(f"请求URL: {url[:100]}...")
        print("正在发送...")
        
        # 发送请求
        response = requests.post(url, timeout=10)
        
        print(f"\n响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("🎉 消息发送成功!")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            print("\n✅ 发送详情:")
            print(f"   消息ID: {result.get('message_id', '未知')}")
            print(f"   消息类型: {result.get('msg_type', '未知')}")
            print(f"   创建时间: {result.get('create_time', '未知')}")
            print(f"   更新时间: {result.get('update_time', '未知')}")
            
            return True, result
            
        elif response.status_code == 500:
            print("❌ 服务器内部错误")
            print(f"错误详情: {response.text}")
            
            # 尝试获取更多错误信息
            try:
                error_data = response.json()
                if error_data.get('detail'):
                    print(f"详细错误: {error_data['detail']}")
            except:
                pass
                
            return False, {"error": "server_error", "details": response.text}
            
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应: {response.text}")
            return False, {"error": f"http_{response.status_code}", "details": response.text}
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时，请检查网络连接")
        return False, {"error": "timeout"}
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误，请检查应用是否运行")
        print(f"应用地址: {base_url}")
        return False, {"error": "connection_error"}
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        print(f"异常类型: {type(e).__name__}")
        return False, {"error": str(e)}

def main():
    """主函数"""
    
    print("🚀 Feishu AI Assistant - 消息发送测试")
    print("=" * 60)
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("❌ 用法: python send_test_message.py <chat_id> [message]")
        print()
        print("示例:")
        print("  python send_test_message.py oc_1234567890")
        print("  python send_test_message.py oc_1234567890 '自定义消息内容'")
        print()
        print("💡 chat_id格式: oc_xxxxxxxxxx")
        sys.exit(1)
    
    chat_id = sys.argv[1]
    
    # 检查chat_id格式
    if not chat_id.startswith('oc_'):
        print(f"⚠️ 警告: chat_id通常以'oc_'开头，您提供的是: {chat_id}")
        print("是否继续? (y/n): ", end='')
        choice = input().strip().lower()
        if choice != 'y':
            print("操作取消")
            sys.exit(0)
    
    # 获取自定义消息（如果有）
    custom_message = None
    if len(sys.argv) > 2:
        custom_message = ' '.join(sys.argv[2:])
        print(f"使用自定义消息: {custom_message[:50]}...")
    
    print()
    success, result = send_test_message(chat_id, custom_message)
    
    print()
    print("=" * 60)
    if success:
        print("✅ 测试完成! 请检查飞书群聊是否收到消息")
    else:
        print("❌ 测试失败，请检查:")
        print("   1. chat_id是否正确")
        print("   2. 应用是否正常运行")
        print("   3. 飞书API权限是否足够")
        print("   4. 网络连接是否正常")

if __name__ == "__main__":
    main()