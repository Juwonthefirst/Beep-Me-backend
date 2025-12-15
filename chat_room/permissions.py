from functools import wraps
from channels.db import database_sync_to_async
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from .models import ChatRoom


def block_non_members(f):
    @wraps(f)
    async def wrapped_function(*args, **kwargs):
        request = args[0]
        room_name = kwargs.get("room_name", "")
        try:
            chat_room = await database_sync_to_async(
                ChatRoom.objects.select_related("group").get
            )(name=room_name)

            if not await database_sync_to_async(chat_room.is_member)(request.user.id):
                raise PermissionDenied
            return await f(*args, **kwargs, room_object=chat_room)

        except ChatRoom.DoesNotExist:
            return Response(
                {"detail": "room not found"}, status=status.HTTP_404_NOT_FOUND
            )

    return wrapped_function
