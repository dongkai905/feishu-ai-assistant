#!/usr/bin/env python3
"""
获取飞书应用所在的群列表
参考: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/chat/list
"""

import os
import sys
import json
import requests
from datetime import datetime

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from feishu_client import FeishuClient
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请确保在feishu-ai-assistant目录下运行此脚本")
    sys.exit(1)

def get_chat_list(feishu_client, page_size=20, sort_type="ByCreateTimeAsc"):
    """获取应用所在的群列表"""
    
    print("📋 获取飞书应用所在的群列表...")
    print(f"排序方式: {sort_type}")
    print(f"每页大小: {page_size}")
    print()
    
    # 获取access_token
    try:
        access_token = feishu_client.get_access_token()
        if not access_token:
            print("❌ 无法获取access_token")
            return None
    except Exception as e:
        print(f"❌ 获取access_token失败: {e}")
        return None
    
    # API端点
    url = "https://open.feishu.cn/open-apis/im/v1/chats"
    
    # 请求头
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # 查询参数
    params = {
        "page_size": page_size,
        "sort_type": sort_type,
        "user_id_type": "open_id"  # 使用open_id类型
    }
    
    try:
        print("🔄 调用飞书API获取群列表...")
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("code") == 0:
                print("✅ 获取群列表成功!")
                data = result.get("data", {})
                items = data.get("items", [])
                
                print(f"找到 {len(items)} 个群聊:")
                print("=" * 80)
                
                for i, chat in enumerate(items, 1):
                    print(f"\n{i}. 群聊信息:")
                    print(f"   🔷 群聊ID: {chat.get('chat_id')}")
                    print(f"   📛 群聊名称: {chat.get('name')}")
                    print(f"   📝 群聊描述: {chat.get('description', '无')}")
                    print(f"   👑 群主ID: {chat.get('owner_id', '未知')}")
                    print(f"   🏢 租户Key: {chat.get('tenant_key')}")
                    print(f"   📊 群状态: {chat.get('chat_status')}")
                    print(f"   🌐 外部群: {'是' if chat.get('external') else '否'}")
                    
                    # 检查是否是我们提供的chat_id
                    provided_chat_id = "oc_a0553eda9014c201e6969b478895c230"
                    if chat.get('chat_id') == provided_chat_id:
                        print(f"   ✅ 匹配: 这是您提供的chat_id!")
                
                print("\n" + "=" * 80)
                
                # 分页信息
                has_more = data.get("has_more", False)
                page_token = data.get("page_token")
                
                if has_more:
                    print(f"📄 还有更多群聊，page_token: {page_token[:30]}...")
                else:
                    print("📄 已获取所有群聊")
                
                return items
            else:
                print(f"❌ API返回错误: {result.get('msg')}")
                print(f"错误码: {result.get('code')}")
                return None
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            print(f"响应: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ 网络连接错误")
        return None
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def check_chat_id_in_list(chat_list, target_chat_id):
    """检查指定的chat_id是否在群列表中"""
    if not chat_list:
        return False, None
    
    for chat in chat_list:
        if chat.get('chat_id') == target_chat_id:
            return True, chat
    
    return False, None

def main():
    """主函数"""
    
    print("🚀 Feishu AI Assistant - 群列表查询工具")
    print("=" * 60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 检查环境变量
    app_id = os.getenv('FEISHU_APP_ID')
    app_secret = os.getenv('FEISHU_APP_SECRET')
    
    if not app_id or not app_secret:
        print("❌ 环境变量未设置")
        print("请先设置环境变量:")
        print("  export FEISHU_APP_ID=您的AppID")
        print("  export FEISHU_APP_SECRET=您的AppSecret")
        print("或者运行: source .env.local")
        return
    
    print(f"应用ID: {app_id[:10]}...")
    print()
    
    try:
        # 初始化飞书客户端
        print("🔄 初始化飞书客户端...")
        feishu = FeishuClient()
        print("✅ 飞书客户端初始化成功")
        print()
        
        # 获取群列表
        chat_list = get_chat_list(feishu)
        
        if chat_list:
            print()
            print("🔍 分析结果:")
            print("-" * 40)
            
            # 检查提供的chat_id
            target_chat_id = "oc_a0553eda9014c201e6969b478895c230"
            found, chat_info = check_chat_id_in_list(chat_list, target_chat_id)
            
            if found:
                print(f"✅ 找到匹配的群聊!")
                print(f"   群聊名称: {chat_info.get('name')}")
                print(f"   群聊描述: {chat_info.get('description', '无')}")
                print(f"   群状态: {chat_info.get('chat_status')}")
                print()
                print("💡 可能的问题:")
                print("   1. 应用没有发送消息的权限 (需要 im:message 权限)")
                print("   2. 群聊设置不允许机器人发送消息")
                print("   3. 应用被禁言或限制")
            else:
                print(f"❌ 未找到chat_id: {target_chat_id}")
                print()
                print("💡 可能的原因:")
                print("   1. chat_id不正确")
                print("   2. 应用不在该群聊中")
                print("   3. 需要将应用添加到群聊")
                print("   4. 群聊已解散或不存在")
            
            print()
            print("🎯 解决方案:")
            print("   1. 确认chat_id是否正确")
            print("   2. 将应用添加到群聊")
            print("   3. 检查应用权限 (需要 im:message 权限)")
            print("   4. 使用群列表中的其他chat_id测试")
        
        else:
            print("❌ 无法获取群列表")
            print()
            print("💡 可能的原因:")
            print("   1. 应用没有群聊权限 (需要 im:chat 或 im:chat:readonly 权限)")
            print("   2. 应用未启用机器人能力")
            print("   3. 应用未安装或未启用")
            print("   4. access_token无效")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        print(f"错误类型: {type(e).__name__}")

if __name__ == "__main__":
    main()