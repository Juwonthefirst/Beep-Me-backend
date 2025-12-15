from django.contrib.auth import get_user_model
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import permission_classes
from adrf.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from channels.db import database_sync_to_async
from BeepMe.utils import async_background_task, load_enviroment_variables
from chat_room.pagination import MessagePagination, create_next_cursor
from chat_room.permissions import block_non_members
from chat_room.models import ChatRoom
from group.queries import get_group_member, get_group_member_role, has_group_permission
from notification.services import send_call_notification
from message.serializers import MessagesSerializer
from BeepMe.cache import cache
import json, os
from livekit import api

from user.serializers import FriendsSerializer

User = get_user_model()
not_found = status.HTTP_404_NOT_FOUND
forbidden = status.HTTP_403_FORBIDDEN

load_enviroment_variables()


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@block_non_members
async def get_room_messages(request: Request, room_name: str, room_object: ChatRoom):
    paginator = MessagePagination()
    paginator.base_url = request.build_absolute_uri(request.path)
    cursor = request.query_params.get("cursor", None)

    if not cursor:
        cached_messages = await cache.get_cached_messages(room_object.name)

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

    queryset = room_object.messages.all()
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
    user_role = None

    if room_object.is_group:
        user_role = await database_sync_to_async(get_group_member_role)(
            room_object.group.id,
            user.id,
        )

        is_video_admin = await database_sync_to_async(has_group_permission)(
            role=user_role, permission="video admin"
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
        .with_metadata(json.dumps({**FriendsSerializer(user).data, "role": user_role}))
        .to_jwt()
    )

    return {"token": token}


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@block_non_members
async def join_livekit_room(request, room_name, room_object):
    livekit_JWT_token = await get_livekit_JWT_token(request, room_object)

    return Response({"room_url": os.getenv("LIVEKIT_URL"), **livekit_JWT_token})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@block_non_members
async def create_livekit_room(request: Request, room_name: str, room_object: ChatRoom):
    is_video_call = request.data.get("is_video", False)
    try:
        async with api.LiveKitAPI() as client:
            await client.room.create_room(
                api.CreateRoomRequest(
                    name=room_name,
                    empty_timeout=60,
                    metadata=json.dumps(
                        {
                            "is_video_call": is_video_call,
                            "host_id": request.user.id,
                            "is_group": room_object.is_group,
                        }
                    ),
                )
            )
        livekit_token = await get_livekit_JWT_token(request, room_object)
        async_background_task(send_call_notification)(
            caller_id=request.user.id,
            caller_username=request.user.username,
            room=room_object,
            is_video=is_video_call,
        )
        return Response({"room_url": os.getenv("LIVEKIT_URL"), **livekit_token})
    except Exception as error:
        print(error)
        return Response(
            {"error": "Unable to connect to livekit"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
