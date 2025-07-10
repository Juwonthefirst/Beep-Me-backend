from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import Max, Exists, OuterRef
from notification.serializers import NotificationSerializer
from chat_room.serializers import UserChatRoomSerializer
from chat_room.models import ChatRoom
from user.serializers import (
	UsersSerializer, 
	RetrieveUsersSerializer,
	UserIDSerializer
)

User = get_user_model()
bad_request = status.HTTP_400_BAD_REQUEST
not_found = status.HTTP_404_NOT_FOUND

class UsersView(ListAPIView):
	"""View to get all user in the database, this meant to be used with filtering and pagination"""
	queryset = User.objects.all()
	permission_classes = [IsAuthenticated]
	serializer_class = UsersSerializer
	search_fields = ["username"]
	def get_queryset(self): 
		user = self.request.user
		return User.objects.annotate(
			is_followed_by_me = Exists(
				User.following.through.objects.filter(
					from_user_id = user.id,
					to_user_id = OuterRef("pk")
				)
			),
			
			is_following_me = Exists(
				User.following.through.objects.filter(
					from_user_id = OuterRef("pk"),
					to_user_id = user.id
				)
			)
		)
	
class RetrieveUserView(RetrieveAPIView): 
	"""View to get a particular user in the database """
	queryset = User.objects.all()
	permission_classes = [IsAuthenticated]
	serializer_class = RetrieveUsersSerializer
	
class UserChatRoomsView(ListAPIView): 
	permission_classes = [IsAuthenticated]
	serializer_class = UserChatRoomSerializer
	search_fields = ["members__username", "group__name"]
	def get_queryset(self):
		user = self.request.user
		return ChatRoom.objects \
		.select_related("group") \
		.prefetch_related("members", "messages") \
		.filter(members = user) \
		.annotate(
			last_message_time = Max("messages__timestamp")
		) \
		.order_by("-last_message_time")

	def get_serializer_context(self): 
		context = super().get_serializer_context()
		context["user_id"] = self.request.user.id
		return context
	
class UserNotificationsView(ListAPIView): 
	permission_classes = [IsAuthenticated]
	serializer_class = NotificationSerializer
	search_fields = ["notification"]
	def get_queryset(self):
		user = self.request.user
		return user.notifications.all()
	
class DoesUsernameExistView(APIView): 
    permission_classes = [IsAuthenticated]
    def post(self, request): 
        requested_username = request.data.get("username")
        username_taken = User.objects.filter(username = requested_username).exists()
        if username_taken:
        	return Response({"exists": username_taken}, status = bad_request)
        return Response({"exists": username_taken})
        

class FriendListView(ListAPIView): 
	serializer_class = UsersSerializer
	permission_classes = [IsAuthenticated]
	search_fields = ["username"]
	def get_queryset(self): 
		user = self.request.user
		return user.get_friends()
		
class SentFriendRequestView(ListAPIView): 
	serializer_class = UsersSerializer
	permission_classes = [IsAuthenticated]
	search_fields = ["username"]
	def get_queryset(self): 
		user = self.request.user
		return user.get_unmutual_following()

class receivedFriendRequestView(ListAPIView): 
	serializer_class = UsersSerializer
	permission_classes = [IsAuthenticated]
	search_fields = ["username"]
	def get_queryset(self): 
		user = self.request.user
		return user.get_unmutual_followers()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def sendFriendRequest(request): 
	serializer = UserIDSerializer(data = request.data)
	if serializer.is_valid: 
		user_ids = serializer.validated_data.get("user_ids")
		request.user.following.add(*user_ids)
		return Response({"status": "ok"})
	return Response({"error": serializer.errors}, status = bad_request)