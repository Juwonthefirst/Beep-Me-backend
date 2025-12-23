from django.contrib.auth import get_user_model
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from adrf.views import APIView
from rest_framework.decorators import permission_classes
from adrf.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from channels.db import database_sync_to_async
from BeepMe.utils import (
    async_background_task,
    background_task,
    load_enviroment_variables,
)
from chat_room.pagination import MessagePagination, create_next_cursor
from chat_room.parsers import LiveKitwebhookParser
from chat_room.permissions import block_non_members
from chat_room.models import CallHistory, ChatRoom
from chat_room.queries import does_room_exist
from group.queries import get_group_member_role, has_group_permission
from notification.services import send_call_notification
from message.serializers import MessagesSerializer
from BeepMe.cache import cache
import json, os
from livekit import api
from livekit.api.webhook import WebhookEvent

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
                            messages[-1].get("created_at"), paginator
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


async def get_livekit_JWT_token(request: Request, room_object: ChatRoom, call_id: str):
    user = request.user
    is_video_admin = False
    user_role = None

    async with api.LiveKitAPI() as client:
        if not await does_room_exist(client, call_id):
            return {"error": "Call doesn't exist"}

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
                room=call_id,
                room_join=True,
                room_create=False,
                room_admin=is_video_admin,
                can_publish=True,
                can_publish_data=True,
                can_subscribe=True,
            )
        )
        .with_metadata(
            json.dumps(
                {
                    **FriendsSerializer(user, context={"request": request}).data,
                    "role": getattr(user_role, "name", None),
                }
            )
        )
        .to_jwt()
    )

    return {"token": token}


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@block_non_members
async def join_livekit_room(request, room_name, call_id, room_object):
    livekit_JWT_token = await get_livekit_JWT_token(request, room_object, call_id)
    if "error" in livekit_JWT_token:
        return Response(livekit_JWT_token, status=status.HTTP_404_NOT_FOUND)

    return Response({"room_url": os.getenv("LIVEKIT_URL"), **livekit_JWT_token})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@block_non_members
async def create_livekit_room(request: Request, room_name: str, room_object: ChatRoom):
    is_video_call = request.data.get("is_video", False)
    try:
        async with api.LiveKitAPI() as client:
            if not (await does_room_exist(client, room_name)):
                callHistoryModel = await database_sync_to_async(
                    CallHistory.create_call
                )(room_object, is_video_call, request.user.id)
                call_id = str(callHistoryModel.id)
                await client.room.create_room(
                    api.CreateRoomRequest(
                        name=call_id,
                        empty_timeout=0,
                        max_participants=None if room_object.is_group else 2,
                        metadata=json.dumps(
                            {
                                "is_video_call": is_video_call,
                                "host_id": request.user.id,
                                "is_group": room_object.is_group,
                            }
                        ),
                    )
                )

                async_background_task(send_call_notification)(
                    caller=(
                        FriendsSerializer(
                            request.user, context={"request": request}
                        ).data
                    ),
                    room=room_object,
                    is_video=is_video_call,
                    call_id=call_id,
                )

        livekit_token = await get_livekit_JWT_token(request, room_object, call_id)

        if "error" in livekit_token:
            return Response(livekit_token, status=status.HTTP_404_NOT_FOUND)

        return Response({"room_url": os.getenv("LIVEKIT_URL"), **livekit_token})

    except Exception as error:
        print(error)
        return Response(
            {"error": "Unable to connect to livekit"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class ReceiveLivekitWebHookEvent(APIView):
    permission_classes = [AllowAny]
    parser_classes = [LiveKitwebhookParser]

    async def post(self, request):
        event: WebhookEvent = await request.data
        print("livekit webhook event received:", event.event)
        allowed_events = os.getenv("LIVEKIT_EVENTS")

        if event.event not in allowed_events.split(","):
            return Response(status=status.HTTP_204_NO_CONTENT)

        new_participant = event.participant
        livekitRoom = event.room
        call_history_id = int(livekitRoom.name)
        call_history_model = await database_sync_to_async(
            CallHistory.objects.select_related("room").filter(id=call_history_id).first
        )()

        if not call_history_model:
            return Response(status=status.HTTP_204_NO_CONTENT)

        match (event.event):
            case "participant_joined":
                if not call_history_model.room.is_group:
                    await database_sync_to_async(call_history_model.start_call)()

                await database_sync_to_async(call_history_model.accept_call)(
                    int(new_participant.identity)
                )

            case "participant_left":
                if not call_history_model.room.is_group:
                    try:
                        async with api.LiveKitAPI() as client:
                            await client.room.delete_room(
                                api.DeleteRoomRequest(room=livekitRoom.name)
                            )
                    except api.twirp_client.TwirpError as error:
                        print("Error deleting livekit room:", error)

                    except Exception as error:
                        print("Error deleting livekit room:", error)

            case "room_finished":
                await database_sync_to_async(call_history_model.end_call)()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
