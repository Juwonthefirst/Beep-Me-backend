import json, re
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from BeepMe.cache import cache
from django.utils import timezone
from notification import tasks

@database_sync_to_async
def save_message(room_id, sender_id, message, timestamp):
    from message.models import Message
    return Message.objects.create(room_id = room_id, body = message, sender_id = sender_id, timestamp = timestamp)
    
@database_sync_to_async
def get_room(room_name):
    from chat_room.models import ChatRoom
    try: 
        return ChatRoom.objects.get(name = room_name)
    except ChatRoom.DoesNotExist:
        return ChatRoom.create_with_members(room_name)

@database_sync_to_async
def create_notification(notification_type, notification, receiver, time, group_id = None, sender = None): 
    from notification.models import Notification
    return Notification.objects.create(
        notification_type = notification_type, 
        notification = notification,
        receiver = receiver,
        sender = sender,
        timestamp = time,
        group_id = group_id,
    )

@database_sync_to_async
def is_group_member(group_id, user_id): 
    from group.models import MemberDetail
    return MemberDetail.objects.filter(group_id = group_id, member_id = user_id).exists()
    
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        if not self.user:
            await self.close(code=4001)
        self.currentRoom = None
        await self.accept()
        await database_sync_to_async(self.user.mark_last_online)()
        tasks.send_online_status_notification.delay(self.user.id, True)
        
    async def disconnect(self, close_code):
        if self.currentRoom:
           await self.group_leave()
        await database_sync_to_async(self.user.mark_last_online)()
        cache.remove_user_online(self.user.id)
        tasks.send_online_status_notification.delay(self.user.id, False)
        
    async def group_join(self, room_name):
        if self.currentRoom:
           await self.group_leave()
           
        room = await get_room(room_name)
        if room_name.startswith("chat") and str(self.user.id) not in room_name.split("-"):
            return await self.respond_with_error("you aren't a member of this group")
        
        elif room.is_group and not await is_group_member(room.group.id, self.user.id):
            return await self.respond_with_error("you aren't a member of this group")
        await self.channel_layer.group_add(
            room_name, self.channel_name
        )
        
        self.currentRoom = room   
        await cache.add_active_member(self.user.id, room_name)
        
    async def group_leave(self):
        room_name = self.currentRoom.name
        await self.channel_layer.group_discard(
            room_name, self.channel_name
        )
        self.currentRoom = None
        await cache.remove_active_member(self.user.id, room_name)
        
    async def ping_user_is_online(self): 
        user_id = self.user.id
        await cache.ping(user_id)
        
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message")
        room_name = data.get("room")
        sender_username = self.user.username
        action = data.get("action")
        temporary_id = data.get("temporary_id")
        
        if action == "ping": 
            return await self.ping_user_is_online()
            
        if not re.match(r"^(chat\-[1-9]+\-[1-9]+|group.[1-9]+){1,100}$", room_name):
            #prevent invalid room_name
            await self.respond_with_error("Invalid room name")
            return
        
        match(action): 
            case "group_join": 
                await self.group_join(room_name)
                
            case "group_leave": 
                await self.group_leave()
                
            case "typing": 
                await self.channel_layer.group_send(
                    room_name, {"type": "chat.typing", "room": room_name, "sender_username": sender_username}
                )
                
            case "chat": 
                timestamp = timezone.now().isoformat()
                room = self.currentRoom
                if not room:
                    return
                if room.name != room_name:
                    return 
                await self.channel_layer.group_send(
                    room_name, {
                        "type": "chat.message", 
                        "room": room_name, 
                        "message": message, 
                        "temporary_id": temporary_id, 
                        "sender_username": sender_username,
                        "timestamp": timestamp
                    }
                )
                await save_message(room_id = room.id, message = message, sender_id = self.user.id, timestamp = timestamp)
                tasks.send_chat_notification.delay(room.id, message, self.user.username)
                
        
    async def chat_message(self, event):
        room_name = event.get("room")
        message = event.get("message")
        sender_username = event.get("sender_username")
        temporary_id = event.get("temporary_id")
        timestamp = event.get("timestamp")
        
        await self.send(text_data = json.dumps({
            "room": room_name,
            "message": message,
            "sender_username": sender_username,
            "timestamp": timestamp,
            "temporary_id": temporary_id
        }))
        
    async def chat_typing(self, event):
        room_name = event.get("room")
        sender_username = event.get("sender_username")
        if not self.currentRoom.name == room_name:
            return self.respond_with_error("join room before sending messages")
            
        await self.send(text_data = json.dumps({"room": room_name, "typing": True, "sender_username": sender_username }))
        
    async def chat_error(self, event): 
        error_mesaage = event.get("error_mesaage")
        await self.send(text_data = json.dumps({"error": error_mesaage}))
        
    async def respond_with_error(self, error_mesaage): 
        await self.channel_layer.send(
            self.channel_name, {
                "error_mesaage": error_mesaage,
                "type": "chat.error"
            }
        )
        
class NotificationConsumer(AsyncWebsocketConsumer): 
    async def connect(self):
        user = self.scope["user"]
        if not user:
            await self.close(code=4001)
        self.room_name = f"user_{user.id}_notifications"
        
        await self.channel_layer.group_add(
            self.room_name, self.channel_name
        )
        
        await self.accept()
        
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_name, self.channel_name
        )
        
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")
        notification_detail = data.get("notification_detail")
        await self.channel_layer.group_send(
            self.room_name, {"type": f"notification.{action}", "notification_detail": notification_detail}
        )
        
    async def notification_chat(self, event):
        notification_detail = event.get("notification_detail")
        await self.send(text_data = json.dumps({
            "type": "chat_notification",
            "sender": notification_detail.get("sender"),
            "receiver": notification_detail.get("receiver"),
            "message": notification_detail.get("message"),
            "is_group": notification_detail.get("is_group"),
            "timestamp": timezone.now().isoformat(),
        }))
        
    async def notification_online(self, event):
        notification_detail = event.get("notification_detail")
        await self.send(text_data = json.dumps({
            "type": "online_status_notification",
            "user": notification_detail.get("user"),
            "status":  notification_detail.get("status"),
            "timestamp": timezone.now().isoformat(),
        }))
        
    async def notification_friend(self, event):
        notification_detail = event.get("notification_detail")
        action = notification_detail.get("action"),
        sender = notification_detail.get("sender"),
        timestamp = timezone.now().isoformat()
        await self.send(text_data = json.dumps({
            "type": "friend_notification",
            "sender": sender,
            "action": action,
            "timestamp": timestamp,
        }))
        await create_notification("friend_notification", action, self.user, time, sender = sender)
        
    async def notification_group(self, event):
        notification_detail = event.get("notification")
        notification = notification_detail.get("notification")
        group_id = notification_detail.get("group_id")
        timestamp = timezone.now().isoformat()
        await self.send(text_data = json.dumps({
            "type": "group_notification",
            "notification":  notification,
            "group_id": group_id,
            "timestamp": timestamp,
        }))
        await create_notification("group_notification", notification, self.user, time, group_id = group_id)
        
    async def notification_call(self, event):
        notification_detail = event.get("notification")
        is_video = notification_detail.get("is_video")
        caller = notification_detail.get("caller")
        room_name = notification_detail.get("room_name")
        room_id = notification_detail.get("room_id")
        is_group = notification_detail.get("is_group")
        await self.send(text_data = json.dumps({
            "type": "call_notification",
            "caller": caller,
            "room_name": room_name,
            "room_id": room_id,
            "is_video": is_video,
            "is_group": is_group
        }))