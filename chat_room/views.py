from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from asigref.sync import async_to_sync
from .serializers import RoomMessagesSerializer, RoomMembersSerializer, RoomDetailsSerializer
from .models import ChatRoom
from user.serializers import UsersSerializer
from message.serializers import MessagesSerializer
from BeepMe.cache import cache
import json, os
from livekit import api


not_found = HTTP_404_NOT_FOUND

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_room_messages(request, room_id): 
	paginator = PageNumberPagination()
	paginator.page_size = 50
	page = request.query_params.get("page", "1")
	
	try:
		room = ChatRoom.objects.get(id = room_id)
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
@permission_classes(["IsAuthenticated"])
def get_livekit_JWT_token(request):
    user = request.user
    is_video_admin = False
    room_id = request.kwargs.get("pk")
    
    try:
        room = Room.objects.get(id = room_id)
        if room.is_group:
        	pass
            
    except Room.DoesNotExist:
        return Response({"error": "room not found"}, status = not_found)
        
    token = api.AccessToken(os.getenv("LIVEKIT_API_KEY"), os.getenv("LIVEKIT_API_SECRET")
	).with_identity(user.id).with_name(user.username).with_grants(api.VideoGrants(
		room_join = True,
		room_admin = is_video_admin,
		room = room.name,
		can_publish = True,
		can_publish_data = True,
		can_subscribe = True
	)).to_jwt()
	
	return Response({"token": token})