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
        self.room_group_name = self.scope["url_route"]["kwargs"]["room_name"]
        if not self.scope["user"]:
            await self.close(code=4001)
            
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        await self.accept()
        self.room = await get_or_create_room(self.room_group_name)
        
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )
        
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        )
        await save_message(room = self.room, message = message, sender = self.scope["user"])
        
    async def chat_message(self, event):
        message = event["message"]
        await self.send(text_data = json.dumps({"message": message}))