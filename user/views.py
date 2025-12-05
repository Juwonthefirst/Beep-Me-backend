from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef
from BeepMe.utils import generate_chat_room_name
from chat_room.pagination import ChatRoomPagination
from notification.serializers import NotificationSerializer
from notification import services
from chat_room.serializers import UserChatRoomSerializer
from chat_room.models import ChatRoom
from drf_yasg.utils import swagger_auto_schema
from user.serializers import (
    FriendsSerializer,
    UsersSerializer,
    RetrieveUserSerializer,
    FriendRequestSerializer,
    CurrentUserSerializer,
)
from django.conf import settings
import re

from chat_room.queries import get_user_rooms
from user.queries import is_username_taken

User = get_user_model()
bad_request = status.HTTP_400_BAD_REQUEST
not_found = status.HTTP_404_NOT_FOUND


class CurrentUserView(APIView):
    def get(self, request):
        return Response(
            CurrentUserSerializer(
                self.request.user, context={"request": self.request}
            ).data
        )


class UsersView(ListAPIView):
    """View to get all user in the database, this meant to be used with filtering and pagination"""

    serializer_class = UsersSerializer
    search_fields = ["username"]

    def get_queryset(self):
        user = self.request.user
        return (
            User.objects.filter(is_active=True)
            .exclude(username=user.username)
            .annotate(
                is_followed_by_me=Exists(
                    User.following.through.objects.filter(
                        from_customuser_id=user.id, to_customuser_id=OuterRef("pk")
                    )
                ),
                is_following_me=Exists(
                    User.following.through.objects.filter(
                        from_customuser_id=OuterRef("pk"), to_customuser_id=user.id
                    )
                ),
            )
        )


class RetrieveUserView(RetrieveAPIView):
    """View to get a particular user in the database"""

    serializer_class = RetrieveUserSerializer

    def get_queryset(self):
        user = self.request.user
        return User.objects.annotate(
            is_followed_by_me=Exists(
                User.following.through.objects.filter(
                    from_customuser_id=user.id, to_customuser_id=OuterRef("pk")
                )
            ),
            is_following_me=Exists(
                User.following.through.objects.filter(
                    from_customuser_id=OuterRef("pk"), to_customuser_id=user.id
                )
            ),
        )


class RetrieveUserChatRoomView(RetrieveAPIView):
    serializer_class = UserChatRoomSerializer
    lookup_field = "name"

    def get_queryset(self):
        user = self.request.user
        return get_user_rooms(user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user_id"] = self.request.user.id
        return context


class UserChatRoomsView(ListAPIView):
    pagination_class = ChatRoomPagination
    serializer_class = UserChatRoomSerializer
    search_fields = ["members__username", "group__name"]

    def get_queryset(self):
        user = self.request.user
        return get_user_rooms(user)


class UserNotificationsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    search_fields = ["notification"]

    def get_queryset(self):
        user = self.request.user
        return user.notifications.all()


class DoesUsernameExistView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, username):
        requested_username = username.capitalize()
        username_taken = is_username_taken(requested_username)
        if not re.fullmatch(settings.USERNAME_REGEX, requested_username):
            return Response(
                {
                    "error": "username should only have numbers, letters, and non-repeating underscore and hyphen"
                },
                status=bad_request,
            )

        return Response({"exists": username_taken})


class FriendListView(ListAPIView):
    serializer_class = FriendsSerializer
    search_fields = ["username"]

    def get_queryset(self):
        user = self.request.user
        return user.get_friends()


class SentFriendRequestView(ListAPIView):
    serializer_class = UsersSerializer
    search_fields = ["username"]

    def get_queryset(self):
        user = self.request.user
        return user.get_unmutual_following()


class receivedFriendRequestView(ListAPIView):
    serializer_class = UsersSerializer
    search_fields = ["username"]

    def get_queryset(self):
        user = self.request.user
        return user.get_unmutual_followers()


@swagger_auto_schema(method="post", request_body=FriendRequestSerializer)
@api_view(["POST"])
def sendFriendRequest(request):
    serializer = FriendRequestSerializer(data=request.data)
    if serializer.is_valid():
        user_id = request.user.id
        friend_id = serializer.validated_data.get("friend_id")
        request.user.following.add(friend_id)
        is_following = request.user.is_friend_of(friend_id)
        action = "sent"
        if is_following:
            action = "accepted"

            room_name = generate_chat_room_name(user_id, friend_id)
            ChatRoom.create_with_members(room_name)
        services.send_friend_request_notification(request.user, friend_id, action)
        return Response({"status": "ok"})
    return Response({"error": serializer.errors}, status=bad_request)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_username(request):
    username = request.data.get("username")
    if not username:
        return Response({"error": "username not provided"}, status=bad_request)

    request.user.username = username
    request.user.save(update_fields=["username"])
    return Response(
        CurrentUserSerializer(request.user, context={"request": request}).data
    )
