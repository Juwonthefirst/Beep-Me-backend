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
from chat_room.tasks import cache_messages
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
        cache_messages.delay(room_name, jsonified_data)

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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@block_non_members
def get_livekit_JWT_token(request, room_name, roomObject):
    user = request.user
    is_video_admin = False

    if roomObject.is_group:
        user_group_role = roomObject.group.get_user_role(user.id)
        is_video_admin = user_group_role.permissions.filter(
            action="video admin"
        ).exists()

    token = (
        api.AccessToken(os.getenv("LIVEKIT_API_KEY"), os.getenv("LIVEKIT_API_SECRET"))
        .with_identity(str(user.id))
        .with_name(user.username)
        .with_grants(
            api.VideoGrants(
                room=roomObject.name,
                room_join=True,
                room_admin=is_video_admin,
                can_publish=True,
                can_publish_data=True,
                can_subscribe=True,
            )
        )
        .to_jwt()
    )

    return Response({"token": token})
