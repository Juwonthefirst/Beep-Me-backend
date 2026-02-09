import re
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from BeepMe.cache import cache
from asgiref.sync import sync_to_async
from chatsocket.queries import (
    delete_message,
    get_room,
    is_group_member,
    save_message,
    update_message,
)
from message.serializers import MessagesSerializer


class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        from notification.services import send_online_status_notification

        self.user = self.scope.get("user")
        if not self.user:
            await self.close(code=4001)
            return
        self.currentRoom = None
        await self.accept()
        # remake into an hash to acccount for multiple login
        await cache.add_user_online(self.user.id)
        send_online_status_notification(self.user, True)

    async def disconnect(self, code):
        from notification.services import send_online_status_notification

        if hasattr(self, "currentRoom"):
            await self.group_leave()
        if not self.user:
            return

        await cache.remove_user_online(self.user.id)
        await database_sync_to_async(self.user.mark_last_online)()
        send_online_status_notification(self.user, False)

    async def group_join(self, room_name):
        if self.currentRoom:
            await self.group_leave()

        room = await get_room(room_name)
        if not room:
            return await self.respond_with_error("you aren't friends")

        if room_name.startswith("chat") and str(self.user.id) not in room_name.split(
            "-"
        ):
            return await self.respond_with_error("you aren't a member of this group")

        elif room.is_group and not await is_group_member(room.group.id, self.user.id):
            return await self.respond_with_error("you aren't a member of this group")

        await self.channel_layer.group_add(room_name, self.channel_name)

        self.currentRoom = room
        await cache.add_active_member(room_name, self.user.id)

    async def group_leave(self):
        from chat_room.queries import update_user_room_last_active_at

        if not self.currentRoom:
            return
        room_name = self.currentRoom.name
        await self.channel_layer.group_discard(room_name, self.channel_name)
        await database_sync_to_async(update_user_room_last_active_at)(
            self.currentRoom, self.user.id
        )
        self.currentRoom = None
        await cache.remove_active_member(self.user.id, room_name)

    async def ping_user_is_online(self):
        user_id = self.user.id
        await cache.ping(user_id)

    async def receive_json(self, content: dict):
        print(content)
        message: str = content.get("message")
        attachment_id: int = content.get("attachment")
        room_name: str = content.get("room_name")
        reply_to_message_id: int = content.get("reply_to")
        # sender_username: str = self.user.username
        action: str = content.get("action")
        uuid: str = content.get("uuid")
        call_id: int = content.get("call_id")

        if action == "ping":
            return await self.ping_user_is_online()

        if action == "call_decline":
            from chat_room.services import decline_call

            return await decline_call(self.user.id, call_id)

        if (
            room_name
            and action == "group_join"
            and not re.fullmatch(
                r"^(chat\-[1-9]+\-[1-9]+|group.[1-9]+){1,100}$", room_name
            )
        ):
            # prevent invalid room_name
            return await self.respond_with_error("Invalid room name")

        match (action):
            case "group_join":
                await self.group_join(room_name)

            case "group_leave":
                await self.group_leave()

            case "typing":
                if not self.currentRoom:
                    return await self.respond_with_error(
                        "you can't type in a room you haven't joined"
                    )

                await self.channel_layer.group_send(
                    self.currentRoom.name,
                    {
                        "type": "chat.typing",
                        "room_name": self.currentRoom.name,
                        "sender_username": self.user.username,
                    },
                )

            case "update":
                from notification.services import send_chat_notification

                room = self.currentRoom
                if not room:
                    return await self.respond_with_error("You aren't in any room")

                updated_message = await update_message(uuid, message)
                if not updated_message:
                    return
                serialized_message = await sync_to_async(
                    lambda: MessagesSerializer(updated_message).data
                )()

                await self.channel_layer.group_send(
                    room.name,
                    {
                        "type": "chat.message",
                        "room_name": room.name,
                        **serialized_message,
                    },
                )

                send_chat_notification(
                    room,
                    serialized_message,
                    self.user,
                )

            case "delete":
                room = self.currentRoom
                if not room:
                    return await self.respond_with_error("You aren't in any room")

                await delete_message(room.name, uuid)

                await self.channel_layer.group_send(
                    room.name,
                    {
                        "type": "chat.delete",
                        "room_name": room.name,
                        "uuid": uuid,
                    },
                )

            case "chat":
                from notification.services import send_chat_notification

                room = self.currentRoom
                if not room:
                    return await self.respond_with_error("You aren't in any room")
                # if room.name != room_name:
                #     return await self.respond_with_error("You aren't in this room")

                serialized_message = await save_message(
                    room=room,
                    attachment_id=attachment_id,
                    reply_to_message_id=reply_to_message_id,
                    message=message,
                    sender_id=self.user.id,
                    uuid=uuid,
                )

                await self.channel_layer.group_send(
                    room.name,
                    {
                        "type": "chat.message",
                        "room_name": room.name,
                        **serialized_message,
                    },
                )

                send_chat_notification(
                    room,
                    serialized_message,
                    self.user,
                )

    async def chat_message(self, event):
        await self.send_json(content={**event, "event": "chat"})

    async def chat_delete(self, event):
        await self.send_json(content={**event, "event": "delete"})

    async def chat_typing(self, event):

        room_name = event.get("room_name")
        sender_username = event.get("sender_username")
        if sender_username == self.user.username:
            return

        await self.send_json(
            content={
                "room_name": room_name,
                "typing": True,
                "sender_username": sender_username,
            }
        )

    async def chat_error(self, event):
        error_mesaage = event.get("error_mesaage")
        await self.send_json(content={"error": error_mesaage})

    async def respond_with_error(self, error_mesaage):
        await self.channel_layer.send(
            self.channel_name, {"error_mesaage": error_mesaage, "type": "chat.error"}
        )


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        if not self.user:
            await self.close(code=4001)
            return

        self.room_name = f"user_{self.user.id}_notifications"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, "room_name"):
            await self.channel_layer.group_discard(self.room_name, self.channel_name)

    # async def receive_json(self, content):

    #     action = content.get("action")
    #     notification_detail = content.get("notification_detail")
    #     await self.channel_layer.group_send(
    #         self.room_name,
    #         {
    #             "type": f"notification.{action}",
    #             "notification_detail": notification_detail,
    #         },
    #     )

    async def notification_chat(self, event):
        # notification for chat messages for user to user and group
        notification_detail = event.get("notification_detail")
        await self.send_json(
            content={
                "type": "chat_notification",
                **notification_detail,
            }
        )

    async def notification_online(self, event):
        # notification for online users
        notification_detail = event.get("notification_detail")
        await self.send_json(
            content={
                "type": "online_status_notification",
                **notification_detail,
            }
        )

    async def notification_friend(self, event):
        # notification for friend related things like unfriending
        notification_detail = event.get("notification_detail")
        action = notification_detail.get("action")
        sender = notification_detail.get("sender")
        await self.send_json(
            content={
                "type": "friend_notification",
                "sender": sender,
                "action": action,
            }
        )

    async def notification_group(self, event):
        # notification for group chat related events excluding chats
        notification_detail = event.get("notification_detail")
        group_id = notification_detail.get("group_id")
        notification = notification_detail.get("notification")
        await self.send_json(
            content={
                "type": "group_notification",
                "notification": notification,
                "group_id": group_id,
            }
        )

    async def notification_call(self, event):
        # notification for call events
        notification_detail = event.get("notification_detail")
        # is_video = notification_detail.get("is_video")
        # caller_username = notification_detail.get("caller")
        # room_name = notification_detail.get("room_name")
        # # room_id = notification_detail.get("room_id")
        # is_group = notification_detail.get("is_group")
        await self.send_json(
            content={
                "type": "call_notification",
                **notification_detail,
            }
        )
