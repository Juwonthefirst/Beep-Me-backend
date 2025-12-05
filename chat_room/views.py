from django.contrib.auth import get_user_model
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN
from rest_framework.decorators import permission_classes
from adrf.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from channels.db import database_sync_to_async
from BeepMe.utils import async_background_task
from chat_room.pagination import MessagePagination, create_next_cursor
from chat_room.permissions import block_non_members
from chat_room.serializers import RoomDetailsSerializer
from chat_room.models import ChatRoom
from group.queries import has_group_permission
from notification.services import send_call_notification
from message.serializers import MessagesSerializer
from BeepMe.cache import cache
import json, os
from livekit import api

User = get_user_model()
not_found = HTTP_404_NOT_FOUND
forbidden = HTTP_403_FORBIDDEN


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@block_non_members
async def get_room_messages(request: Request, room_name: str, roomObject: ChatRoom):
    paginator = MessagePagination()
    paginator.base_url = request.build_absolute_uri(request.path)
    cursor = request.query_params.get("cursor", None)

    if not cursor:
        cached_messages = await cache.get_cached_messages(roomObject.name)

        if cached_messages:
            messages = [json.loads(message) for message in cached_messages]
            messages_length = len(messages)
            return Response(
                {
                    "count": messages_length,
                    "next": (
                        None
                        if messages_length < MessagePagination.page_size
                        else create_next_cursor(
                            messages[-1].get("timestamp"), paginator
                        )
                    ),
                    "previous": None,
                    "results": messages,
                }
            )

    queryset = roomObject.messages.all()
    room_messages = await database_sync_to_async(paginator.paginate_queryset)(
        queryset, request
    )
    serialized_message = await database_sync_to_async(
        lambda: MessagesSerializer(room_messages, many=True).data
    )()

    if not cursor and serialized_message:
        jsonified_data = [
            json.dumps(message_object) for message_object in serialized_message
        ]

        async_background_task(cache.cache_message)(room_name, jsonified_data[::-1])

    return paginator.get_paginated_response(serialized_message)


# class RoomMembersView(ListAPIView):
#     serializer_class = UsersSerializer
#     permission_classes = [IsAuthenticated]
#     search_fields = ["username"]

#     def get_queryset(self):
#         room_id = self.kwargs.get("pk")
#         try:
#             room = ChatRoom.objects.get(id=room_id)
#             return room.members.all()
#         except ChatRoom.DoesNotExist:
#             return User.objects.none()


async def get_livekit_JWT_token(request: Request, room_object: ChatRoom):
    user = request.user
    is_video_admin = False

    if room_object.is_group:
        is_video_admin = await database_sync_to_async(has_group_permission)(
            room_object.group.id, user.id, "video admin"
        )

    token = (
        api.AccessToken(os.getenv("LIVEKIT_API_KEY"), os.getenv("LIVEKIT_API_SECRET"))
        .with_identity(str(user.id))
        .with_name(user.username)
        .with_grants(
            api.VideoGrants(
                room=room_object.name,
                room_join=True,
                room_create=False,
                room_admin=is_video_admin,
                can_publish=True,
                can_publish_data=True,
                can_subscribe=True,
            )
        )
        .to_jwt()
    )

    return {"token": token}


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@block_non_members
async def join_livekit_room(request, room_name, room_object):
    return Response(await get_livekit_JWT_token(request, room_object))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@block_non_members
async def create_livekit_room(request, room_name, room_object):
    async with api.LiveKitAPI() as client:
        await client.room.create_room(
            api.CreateRoomRequest(name=room_name, empty_timeout=300)
        )
    livekit_token = await get_livekit_JWT_token(request, room_object)
    async_background_task(send_call_notification)(
        caller_id=request.user.id,
        caller_username=request.user.username,
        room=room_object,
        is_video=request.data.get("is_video", False),
    )
    return Response({"room_url": os.getenv("LIVEKIT_URL"), **livekit_token})
