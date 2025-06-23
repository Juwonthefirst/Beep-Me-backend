from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from notification.serializers import NotificationSerializer
from .serializers import (
	UsersSerializer, 
	RetrieveUsersSerializer,
	UserChatRoomSerializer
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
	
class RetrieveUserView(RetrieveAPIView): 
	"""View to get a particular user in the database """
	queryset = User.objects.all()
	permission_classes = [IsAuthenticated]
	serializer_class = RetrieveUsersSerializer
	
class UserChatRoomsView(ListAPIView): 
	permission_classes = [IsAuthenticated]
	serializer_class = UserChatRoomSerializer
	def get_queryset(self):
		user = self.request.user
		user_chat_rooms = user.rooms
		return user_chat_rooms.annotate(
			last_message_time = Max("messages_timestamp")
		).order_by("-last_message_time")

	def get_serializer_context(self): 
		context = super().get_serializer_context()
		context["user_id"] = self.request.user.id
		return context
	
class UserNotificationsView(ListAPIView): 
	permission_classes = [IsAuthenticated]
	serializer_class = NotificationSerializer
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