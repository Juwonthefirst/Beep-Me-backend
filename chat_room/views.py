from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from asigref.sync import async_to_sync
from .serializers import RoomMessagesSerializer, RoomMembersSerializer, RoomDetailsSerializer
from .models import ChatRoom
from BeepMe.cache import cache

class MessagePagination(PageNumberPagination): 
	page_size = 50
	
"""class RoomMessagesView(ListAPIView):
	serializer_class = RoomMessagesSerializer
	permission_classes = [IsAuthenticated]
	pagination_class = MessagePagination
	def get_queryset(self): 
		room_id = self.kwargs["room_id"]
		try: 
			#checks if the user is a member of the room before returning messages
			room = ChatRoom.objects.get(id = room_id)
			if not room.members.filter(id = self.request.user.id).exists(): 
				raise PermissionDenied
			cached_message = async_to_sync(cache.get_cached_messages)(room.name)
			if cached_message:
				return 
			return room.messages.all().order_by("timestamp")
		except ChatRoom.DoesNotExist: 
			return ChatRoom.objects.none()
"""

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_room_messages(request, room_id): 
	
	try:
		room = ChatRoom.objects.get(id = room_id)
		if not room.members.filter(id = request.user.id).exists(): 
			raise PermissionDenied
			
		cached_message = async_to_sync(cache.get_cached_messages)(room.name)
		if cached_message:
			return cached_message
		room_messages = room.messages.all().order_by("timestamp")[:50]
		if page == 1: 
			async_to_sync(cache.cache_message)(room.name, *room_messages)
			
		return RoomMessagesSerializer(room_messages).data
		
	except ChatRoom.DoesNotExist: 
		return ChatRoom.objects.none()

		
		
		
	
class RoomMembersView(ListAPIView): 
	serializer_class = RoomMembersSerializer
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
	
