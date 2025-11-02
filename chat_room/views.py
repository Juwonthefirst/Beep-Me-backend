import asyncio
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import (
    RetrieveAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from asgiref.sync import async_to_sync
from chat_room.permissions import block_non_members
from chat_room.serializers import RoomDetailsSerializer
from chat_room.models import ChatRoom
from chat_room.services import cache_messages
from notification.services import send_call_notification
from message.serializers import MessagesSerializer
from BeepMe.cache import cache
import json, os
from livekit import api

User = get_user_model()
not_found = HTTP_404_NOT_FOUND
forbidden = HTTP_403_FORBIDDEN


# use cursor pagination over page pagination
@api_view(["GET"])
@permission_classes([IsAuthenticated])
@block_non_members
def get_room_messages(request, room_name, roomObject):
    paginator = PageNumberPagination()
    paginator.page_size = 50
    page = request.query_params.get("page", "1")

    if page == "1":
        cached_message = async_to_sync(cache.get_cached_messages)(roomObject.name)
        if cached_message:
            paginated_cached_messages = paginator.paginate_queryset(
                [json.loads(message) for message in cached_message], request
            )
            return paginator.get_paginated_response(paginated_cached_messages)

    queryset = roomObject.messages.all().order_by("-timestamp")
    room_messages = paginator.paginate_queryset(queryset, request)

    serialized_data = MessagesSerializer(room_messages, many=True).data
    if page == "1":
        jsonified_data = [
            json.dumps(message_object) for message_object in serialized_data
        ]
        cache_messages(room_name, jsonified_data)

    return paginator.get_paginated_response(serialized_data)


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


@method_decorator(block_non_members, name="get")
class RoomDetailsView(RetrieveAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = RoomDetailsSerializer
    permission_classes = [IsAuthenticated]


def get_livekit_JWT_token(request, room_name, room_object):
    user = request.user
    is_video_admin = False

    if room_object.is_group:
        user_group_role = room_object.group.get_user_role(user.id)
        is_video_admin = user_group_role.permissions.filter(
            action="video admin"
        ).exists()

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
def join_livekit_room(request, room_name, room_object):
    return Response(get_livekit_JWT_token(request, room_name, room_object))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@block_non_members
def create_livekit_room(request, room_name, room_object):

    async def inner():
        async with api.LiveKitAPI() as client:
            await client.room.create_room(
                api.CreateRoomRequest(name=room_name, empty_timeout=300)
            )
        livekit_token = get_livekit_JWT_token(request, room_name, room_object)
        send_call_notification(
            caller_id=request.user.id,
            caller_username=request.user.username,
            room=room_object,
            is_video=request.data.get("is_video", False),
        )
        return Response({"room_url": os.getenv("LIVEKIT_URL"), **livekit_token})

    return asyncio.run(inner())
