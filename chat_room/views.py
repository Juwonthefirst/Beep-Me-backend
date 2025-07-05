from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from asgiref.sync import async_to_sync
from chat_room.serializers import RoomDetailsSerializer, ChatRoomAndMessagesSerializer
from chat_room.models import ChatRoom
from user.serializers import UsersSerializer
from message.serializers import MessagesSerializer
from BeepMe.cache import cache
import json, os
from livekit import api


not_found = HTTP_404_NOT_FOUND

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_room_messages(request, pk): 
	paginator = PageNumberPagination()
	paginator.page_size = 50
	page = request.query_params.get("page", "1")
	
	try:
		room = ChatRoom.objects.get(id = pk)
		if not room.members.filter(id = request.user.id).exists(): 
			raise PermissionDenied
			
		cached_message = async_to_sync(cache.get_cached_messages)(room.name)
		if cached_message and page == "1":
			paginated_cached_messages = paginator.paginate_queryset(cached_message, request)
			return paginator.get_paginated_response(paginated_cached_messages)
			
		queryset = room.messages.all().order_by("timestamp")
		room_messages = paginator.paginate_queryset(queryset, request)
					
		serializer = MessagesSerializer(room_messages, many = True).data
		if page == "1":
			jsonified_data = [json.dumps(message_object) for message_object in serializer]
			async_to_sync(cache.cache_message)(room.name, *jsonified_data)

		return paginator.get_paginated_response(serializer)
		
	except ChatRoom.DoesNotExist: 
		return Response({"error": "This chat room doesn't exist"}, status = not_found)

		
		
		
	
class RoomMembersView(ListAPIView): 
	serializer_class = UsersSerializer
	permission_classes = [IsAuthenticated]
	search_fields = ["username"]
	def get_queryset(self): 
		room_id = self.kwargs["pk"]
		try: 
			room = ChatRoom.objects.get(id = room_id)
			return room.members.all()
		except ChatRoom.DoesNotExist: 
			return ChatRoom.objects.none()
			
class RoomDetailsView(RetrieveUpdateDestroyAPIView): 
	queryset = ChatRoom.objects.all()
	serializer_class = RoomDetailsSerializer
	permission_classes = [IsAuthenticated]


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_livekit_JWT_token(request, pk): 
	user = request.user
	is_video_admin = False
	room_id = pk
	
	try:
		roomObject = ChatRoom.objects.get(pk = room_id)
	except ChatRoom.DoesNotExist:
		return Response({"error": "chat room not found"}, status = not_found)
	
	if roomObject.is_group: 
		user_group_role = roomObject.group.get_user_role(user)
		is_video_admin = user_group_role.permissions.filter(action = "video admin").exists()
	
	token = api.AccessToken(os.getenv("LIVEKIT_API_KEY"), os.getenv("LIVEKIT_API_SECRET")).with_identity(user.id).with_name(user.username).with_grants(api.VideoGrants(
		room = roomObject.name,
		room_join = True,
		room_admin = is_video_admin,
		can_publish = True,
		can_publish_data = True,
		can_subscribe = True
	)).to_jwt()
	
	return Response({"token": token})
	
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getChatRoomAndMessageByRoomName(request, room_name):
	
	
class GetChatRoomAndMessageByRoomName(RetrieveAPIView): 
	serializer_class = ChatRoomAndMessagesSerializer
	permission_classes = [IsAuthenticated]
	def get_queryset(self): 
		room_name = self.kwargs.get("room_name")
		try:
			return ChatRoom.objects.get(name = room_name)
		except ChatRoom.DoesNotExist:
			return ChatRoom.objects.none()
			