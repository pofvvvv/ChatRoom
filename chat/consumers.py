import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer
from django.core.cache import cache
from channels.db import database_sync_to_async
from .models import ChatMessage

class ChatConsumer(AsyncWebsocketConsumer):
    """
    聊天室WebSocket消费者
    处理WebSocket连接、消息发送和接收等核心功能
    """
    
    async def connect(self):
        """
        处理WebSocket连接请求
        """
        try:
            # 检查用户是否已登录
            if not self.scope["user"].is_authenticated:
                await self.close()
                return

            # 获取用户信息
            user = self.scope["user"]
            self.user_id = user.id
            self.nickname = getattr(user, "nickname", user.username)
            
            # 从URL中获取房间名，并创建群组名
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = f'chat_{self.room_name}'

            # 将当前连接添加到聊天室群组
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            # 更新在线用户列表
            await self.update_online_users(add_user=True)
            
            # 接受WebSocket连接
            await self.accept()
            
            # 新增：发送历史消息
            history = await self.get_history_messages()
            await self.send(text_data=json.dumps({
                'type': 'history_messages',
                'messages': history
            }))
            
        except Exception as e:
            print(f"连接错误: {str(e)}")
            await self.close()

    async def receive(self, text_data):
        """
        处理接收到的WebSocket消息
        """
        try:
            # 解析JSON格式的消息
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            user = self.scope["user"]
            
            # 新增：保存消息到数据库
            await self.save_message_to_db(user, message)
            
            # 广播消息
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'nickname': getattr(user, "nickname", user.username),
                    'user_id': str(user.id),
                }
            )
        except Exception as e:
            print(f"接收消息错误: {str(e)}")

    async def disconnect(self, close_code):
        """
        处理WebSocket断开连接
        """
        try:
            # 更新在线用户列表
            await self.update_online_users(add_user=False)
            
            # 从群组中移除当前连接
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception:
            pass
        finally:
            raise StopConsumer()

    async def chat_message(self, event):
        """
        处理聊天消息事件
        """
        try:
            await self.send(text_data=json.dumps({
                'type': 'chat_message',
                'message': event['message'],
                'nickname': event['nickname'],
                'user_id': event['user_id'],
            }))
        except Exception as e:
            print(f"发送消息错误: {str(e)}")

    async def update_online_users(self, add_user):
        """
        更新在线用户列表
        """
        try:
            online_users = await self.get_online_users(add_user)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'online_users',
                    'users': online_users,
                }
            )
        except Exception as e:
            print(f"更新在线用户错误: {str(e)}")

    async def online_users(self, event):
        """
        处理在线用户列表更新事件
        """
        try:
            await self.send(text_data=json.dumps({
                'type': 'online_users',
                'users': event['users'],
            }))
        except Exception as e:
            print(f"发送在线用户列表错误: {str(e)}")

    async def get_online_users(self, add_user):
        """
        获取在线用户列表
        """
        try:
            online_users = list(await self.get_cache(self.room_group_name))
            user_info = {
                'id': self.user_id,
                'nickname': self.nickname
            }
            
            if add_user:
                if not any(u['id'] == self.user_id for u in online_users):
                    online_users.append(user_info)
            else:
                online_users = [u for u in online_users if u['id'] != self.user_id]

            await self.set_cache(self.room_group_name, online_users)
            return online_users
        except Exception as e:
            print(f"获取在线用户列表错误: {str(e)}")
            return []
        
    @database_sync_to_async
    def get_cache(self, key):
        return cache.get(key, [])
        
    @database_sync_to_async
    def set_cache(self, key, value):
        return cache.set(key, value, timeout=None)

    @database_sync_to_async
    def save_message_to_db(self, user, message):
        """同步方法：保存消息到数据库"""
        from .models import ChatMessage  # 添加模型导入
        ChatMessage.objects.create(
            sender=user,
            room=self.room_name,
            content=message
        )

    @database_sync_to_async
    def get_history_messages(self):
        messages = (ChatMessage.objects
                   .filter(room=self.room_name)
                   .select_related('sender')
                   .order_by('timestamp')[:50])  # 保持升序查询
        return [message.to_dict() for message in messages]  # 直接返回查询顺序
