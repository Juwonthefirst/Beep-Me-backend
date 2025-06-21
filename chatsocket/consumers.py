import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

@database_sync_to_async
def save_message(room, sender, message):
    from message.models import Message
    return Message.objects.create(room = room, body = message, sender = sender)
    
@database_sync_to_async
def get_or_create_room(room_name):
    from chat_room.models import ChatRoom
    try: 
        return ChatRoom.objects.get(name = room_name)
    except:
        return ChatRoom.create_with_members(room_name)
        

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope["user"]:
            await self.close(code=4001)
            
        self.joined_rooms = set()
        await self.accept()
        
    async def disconnect(self, close_code):
        for room in rooms:
            await self.channel_layer.group_discard(
                room, self.channel_name
            )
        self.joined_rooms.clear()
        
    async def group_join(self, room_name): 
        await self.channel_layer.group_add(
            room_name, self.channel_name
        )
        self.joined_rooms.add(room_name)
        await get_or_create_room(room_name)
        
    async def group_leave(self, room_name):
        await self.channel_layer.group_discard(
            room_name, self.channel_name
        )
        self.joined_rooms.discard(room_name)
        
    async def receive(self, text_data):
        data = json.loads(text_data)
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
                    room_name, {"type": "chat.typing", "room": room_name}
                )
                
            case "chat": 
                await self.channel_layer.group_send(
                    room_name, {"type": "chat.message", "room": room_name, "message": message}
                )
                await save_message(room = room_name, message = message, sender = self.scope["user"])

        
    async def chat_message(self, event):
        room_name = event.get("room")
        message = event.get("message")
        await self.send(text_data = json.dumps({"room": room_name,"message": message}))
        
    async def chat_typing(self, event):
        room_name = event.get("room")
        await self.send(text_data = json.dumps({"room": room_name, "typing": True}))
        
        
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
        
    async def disconnect(self):
        await self.channel_layer.group_discard(
            self.room_name, self.channel_name
        )
        
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")
        
        await self.channel_layer.group_send(
            self.room_name, {"type": f"notification.{action}","notification": notification}
        )
        
    async def notification_chat(self, event):
        notification = event.get("notification")
        self.send(text_data = json.dumps({
            "sender": ,
            "to": ,
            "message" ,
            "time": ,
        }))
        
    async def notification_friend(self, event):
        pass
    