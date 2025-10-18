from celery import shared_task
from channels.layers import get_channel_layer
from BeepMe.cache import cache
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync

channel_layer = get_channel_layer()


@shared_task
def send_chat_notification(room_id, message, sender_username, sender_id):
    from chat_room.models import ChatRoom

    room = ChatRoom.objects.select_related("group").get(id=room_id)
    if room.is_group:
        members_id = room.group.members.values_list("id", flat=True)
    else:
        room_name = room.name
        members_id = room_name.split("_")[1:]

    online_inactive_members_id = async_to_sync(cache.get_online_inactive_members)(
        room.name, members_id
    ) - {sender_id}
    for member_id in online_inactive_members_id:
        async_to_sync(channel_layer.group_send)(
            f"user_{member_id}_notifications",
            {
                "type": "notification.chat",
                "notification_detail": {
                    "sender": sender_username,
                    "receiver": room.group.name,
                    "message": message,
                    "is_group": room.is_group,
                    "room_id": room.id,
                },
            },
        )


@shared_task
def send_group_notification(room_id, notification, sender_id):
    from chat_room.models import ChatRoom

    room = ChatRoom.objects.select_related("group").get(id=room_id)
    members_id = room.group.members.values_list("id", flat=True)
    online_inactive_members_id = async_to_sync(cache.get_online_inactive_members)(
        room.name, members_id
    ) - {sender_id}
    for member_id in online_inactive_members_id:

        async_to_sync(channel_layer.group_send)(
            f"user_{member_id}_notifications",
            {
                "type": "notification.group",
                "notification_detail": {
                    "group_id": room.group.id,
                    "notification": notification,
                },
            },
        )


@shared_task
def send_online_status_notification(user_id, status):
    User = get_user_model()

    user = User.objects.get(id=user_id)
    friends_id = user.get_friends().values_list("id", flat=True)
    online_friends_id = async_to_sync(cache.get_online_users)(friends_id)

    for friend_id in online_friends_id:
        async_to_sync(channel_layer.group_send)(
            f"user_{friend_id}_notifications",
            {
                "type": "notification.online",
                "notification_detail": {
                    "user": user.id,
                    "status": status,
                },
            },
        )


@shared_task
def send_friend_request_notification(username, friend_id, action):
    if async_to_sync(cache.is_user_online)(friend_id):
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


@shared_task
def send_call_notification(caller_id, caller_username, room_name, is_video=False):
    from chat_room.models import ChatRoom

    try:
        room = ChatRoom.objects.select_related("group").get(name=room_name)
        if room.is_group:
            members = room.group.members
        else:
            members = room.members

        members_id = list(members.exclude(id=caller_id).values_list("id", flat=True))

        online_members_id = async_to_sync(cache.get_online_users)(members_id)
        for member_id in online_members_id:

            async_to_sync(channel_layer.group_send)(
                f"user_{member_id}_notifications",
                {
                    "type": "notification.call",
                    "notification_detail": {
                        "caller": caller_username,
                        "room_name": room_name,
                        "is_video": is_video,
                        "is_group": room.is_group,
                        # "room_id": room.id,
                    },
                },
            )
    except ChatRoom.DoesNotExist:
        pass
