from functools import wraps
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from .models import ChatRoom


def block_non_members(f):
    @wraps(f)
    def wrapped_function(*args, **kwargs):
        request = args[0]
        room_name = args[1]
        try:
            chat_room = ChatRoom.objects.select_related("group").get(name=room_name)
            if not chat_room.is_member(request.user.id):
                raise PermissionDenied
            return f(*args, **kwargs, roomObject=chat_room)
        except ChatRoom.DoesNotExist:
            return Response(
                {"detail": "room not found"}, status=status.HTTP_404_NOT_FOUND
            )

    return wrapped_function
