from datetime import timedelta
from channels.db import database_sync_to_async
from django.db import transaction
from django.utils import timezone
from asgiref.sync import sync_to_async
import json
from BeepMe.cache import cache


@database_sync_to_async
def save_message_to_db(
    room, sender_id, message, attachment_id, reply_to_message_id, uuid
):
    from message.models import Message
    from chat_room.queries import update_user_room_last_active_at

    with transaction.atomic():

        message = Message.objects.create(
            room_id=room.id,
            body=message,
            sender_id=sender_id,
            reply_to_id=reply_to_message_id,
            attachment_id=attachment_id,
            uuid=uuid,
        )

        room.last_message = message
        room.last_room_activity = message.created_at
        room.save(update_fields=["last_message", "last_room_activity"])
        update_user_room_last_active_at(room, sender_id)

    return message


async def save_message(
    room,
    sender_id: int,
    message: str,
    reply_to_message_id: int,
    attachment_id: int,
    uuid: str,
):
    from message.serializers import LastMessageSerializer

    message_model = await save_message_to_db(
        room, sender_id, message, attachment_id, reply_to_message_id, uuid
    )
    serialized_message = await sync_to_async(
        lambda: LastMessageSerializer(message_model).data
    )()
    jsonified_message = json.dumps(serialized_message)
    await cache.cache_message(room.name, jsonified_message)
    return serialized_message


@database_sync_to_async
def get_room(room_name):
    from chat_room.models import ChatRoom

    try:
        return (
            ChatRoom.objects.select_related("group")
            .prefetch_related("members", "messages")
            .get(name=room_name)
        )
    except ChatRoom.DoesNotExist:
        return None


@database_sync_to_async
def create_notification(
    notification_type, notification, receiver, time, group_id=None, sender=None
):
    from notification.models import Notification

    return Notification.objects.create(
        notification_type=notification_type,
        notification=notification,
        receiver=receiver,
        sender=sender,
        created_at=time,
        group_id=group_id,
    )


@database_sync_to_async
def is_group_member(group_id: int, user_id: int):
    from group.models import MemberDetail

    return MemberDetail.objects.filter(group_id=group_id, member_id=user_id).exists()


@database_sync_to_async
def update_message(message_uuid: str, new_body: str):
    from message.models import Message

    edit_grace_period = timezone.now() - timedelta(minutes=30)
    try:
        message = Message.objects.get(
            uuid=message_uuid, created_at__gte=edit_grace_period
        )
        message.body = new_body
        message.is_edited = True
        message.save(update_fields=["body", "is_edited"])
        return message
    except Message.DoesNotExist:
        return None


@database_sync_to_async
def delete_message(message_uuid: str):
    from message.models import Message

    try:
        delete_grace_period = timezone.now() - timedelta(minutes=30)
        return Message.objects.filter(
            uuid=message_uuid, created_at__gte=delete_grace_period
        ).delete()
    except Message.DoesNotExist:
        return None


# async def delete_message(room_name: str, message_uuid: str):
#     return_value = await delete_message_from_db(message_uuid)

#     if return_value != None and return_value[0] > 0:
#         await cache.delete_message(room_name, message_uuid)
#     return return_value
