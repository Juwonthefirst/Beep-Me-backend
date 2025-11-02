from channels.layers import get_channel_layer
from BeepMe.cache import cache
from asgiref.sync import async_to_sync
from BeepMe.utils import async_background_task, background_task


@async_background_task
async def send_chat_notification(room, message, sender):
    channel_layer = get_channel_layer()

    if room.is_group:
        members_id = list(room.group.members.values_list("id", flat=True))
    else:
        room_name = room.name
        members_id = room_name.split("_")[1:]

    online_inactive_members_id = await cache.get_online_inactive_members(
        room.name, members_id
    ) - {sender.id}

    for member_id in online_inactive_members_id:
        await channel_layer.group_send(
            f"user_{member_id}_notifications",
            {
                "type": "notification.chat",
                "notification_detail": {
                    "sender": sender.username,
                    "receiver": room.group.name,
                    "message": message,
                    "is_group": room.is_group,
                    "room_id": room.id,
                },
            },
        )


@background_task
async def send_group_notification(room, notification, sender_id):
    channel_layer = get_channel_layer()

    members_id = list(room.group.members.values_list("id", flat=True))
    online_inactive_members_id = await cache.get_online_inactive_members(
        room.name, members_id
    ) - {sender_id}
    for member_id in online_inactive_members_id:
        await channel_layer.group_send(
            f"user_{member_id}_notifications",
            {
                "type": "notification.group",
                "notification_detail": {
                    "group_id": room.group.id,
                    "notification": notification,
                },
            },
        )


@async_background_task
async def send_online_status_notification(user, status):
    channel_layer = get_channel_layer()

    friends_id = list(user.get_friends().values_list("id", flat=True))
    online_friends_id = await cache.get_online_users(friends_id)

    for friend_id in online_friends_id:
        await channel_layer.group_send(
            f"user_{friend_id}_notifications",
            {
                "type": "notification.online",
                "notification_detail": {
                    "user": user.id,
                    "status": status,
                },
            },
        )


@background_task
async def send_friend_request_notification(username, friend_id, action):
    channel_layer = get_channel_layer()

    if await cache.is_user_online(friend_id):
        async_to_sync(channel_layer.group_send)(
            f"user_{friend_id}_notifications",
            {
                "type": "notification.friend",
                "notification_detail": {
                    "sender": username,
                    "action": action,
                },
            },
        )


@background_task
async def send_call_notification(caller_id, caller_username, room, is_video=False):
    channel_layer = get_channel_layer()

    if room.is_group:
        members = room.group.members
    else:
        members = room.members

    members_id = list(members.exclude(id=caller_id).values_list("id", flat=True))

    online_members_id = await cache.get_online_users(members_id)
    for member_id in online_members_id:

        await channel_layer.group_send(
            f"user_{member_id}_notifications",
            {
                "type": "notification.call",
                "notification_detail": {
                    "caller": caller_username,
                    "room_name": room.name,
                    "is_video": is_video,
                    "is_group": room.is_group,
                    # "room_id": room.id,
                },
            },
        )
