import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from BeepMe.cache import cache
from django.utils import timezone
from notification import tasks

@database_sync_to_async
def save_message(room, sender_id, message):
    from message.models import Message
    return Message.objects.create(room_id = room_id, body = message, sender_id = sender_id)
    
@database_sync_to_async
def get_or_create_room(room_name):
    from chat_room.models import ChatRoom
    try: 
        return ChatRoom.objects.get(name = room_name)
    except ChatRoom.DoesNotExist:
        return ChatRoom.create_with_members(room_name)

@database_sync_to_async
def create_notification(notification_type, notification, receiver, time, group_id = None): 
    from notification.models import Notification
    return Notification.objects.create(
        notification_type = notification_type, 
        notification = notification,
        receiver = receiver,
        timestamp = time,
        group_id = group_id,
    )
    
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        if not self.user:
            await self.close(code=4001)
        self.joined_rooms = {}
        await self.accept()
        await user.mark_last_online()
        tasks.send_online_status_notification.delay(self.user, True)
        
    async def disconnect(self, close_code):
        for room in self.joined_rooms:
            await self.channel_layer.group_discard(
                self.joined_rooms[room], self.channel_name
            )
            cache.remove_active_member(user_id, room)
        self.user.mark_last_online()
        self.joined_rooms.clear()
        cache.remove_user_online(self.user.id)
        tasks.send_online_status_notification.delay(self.user, False)
        
    async def group_join(self, room_name): 
        await self.channel_layer.group_add(
            room_name, self.channel_name
        )
        room = await get_or_create_room(room_name)
        self.joined_rooms[room_name] = room
        cache.add_active_members(user_id, room_name)
        
    async def group_leave(self, room_name):
        await self.channel_layer.group_discard(
            room_name, self.channel_name
        )
        del self.joined_rooms[room_name]
        self.remove_active_members(user_id, room)
        
    async def user_online(self): 
        user_id = self.user.id
        await cache.set_user_online(user_id)
        
    async def receive(self, text_data):
        data = json.loads(text_data)
        sender_id = data.get("sender_id")
        message = data.get("message")
        room_name = data.get("room")
        action = data.get("action")
        match(action): 
            case "group_join": 
                await self.group_join(room_name)
                
            case "group_leave": 
                await self.group_leave(room_name)
                
            case "typing": 
                await self.channel_layer.group_send(
                    room_name, {"type": "chat.typing", "room": room_name, "sender_id": sender_id}
                )
                
            case "is_online": 
                await self.user_online()
                
            case "chat": 
                await self.channel_layer.group_send(
                    room_name, {"type": "chat.message", "room": room_name, "message": message}
                )
        
    async def chat_message(self, event):
        room_name = event.get("room")
        message = event.get("message")
        sender_id = event.get("sender_id")
        room = self.joined_rooms[room_name]
        await self.send(text_data = json.dumps({"room": room_name,"message": message, "sender_id": sender_id}))
        tasks.send_chat_notification.delay(room, message, sender_id = sender_id)
        await save_message(room = room_name, message = message, sender_id = sender_id)
        
    async def chat_typing(self, event):
        room_name = event.get("room")
        sender_id = event.get("sender_id")
        await self.send(text_data = json.dumps({"room": room_name, "typing": True, "sender_id": sender_id }))
        
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
            "time": timezone.now(),
        }))
        
    async def notification_online(self, event):
        notification_detail = event.get("notification_detail")
        await self.send(text_data = json.dumps({
            "type": "online_status_notification",
            "user": notification_detail.get("user"),
            "status" notification_detail.get("status"),
            "time": timezone.now(),
        }))
        
    async def notification_friend(self, event):
        notification_detail = event.get("notification_detail")
        notification = notification_detail.get("notification"),
        time = timezone.now()
        await self.send(text_data = json.dumps({
            "type": "friend_notification",
            "notification": notification,
            "time": time,
        }))
        await create_notification("friend_notification", notification, self.user, time)
        
    async def notification_group(self, event):
        notification_detail = event.get("notification")
        notification = notification_detail.get("notification")
        group_id = notification_detail.get("group_id")
        time = timezone.now()
        await self.send(text_data = json.dumps({
            "type": "group_notification",
            "notification":  notification,
            "group_id": group_id,
            "time": time,
        }))
        await create_notification("group_notification", notification, self.user, time, group_id = group_id)