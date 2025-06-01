from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .serializers import RoomMessagesSerializer, RoomMembersSerializer, RoomDetailsSerializer
from .models import ChatRoom

class RoomMessagesView(ListAPIView):
	serializer_class = RoomMessagesSerializer
	#permission_classes = [IsAuthenticated]
	def get_queryset(self): 
		room_id = self.kwargs["room_id"]
		try: 
			#checks if the user is a member of the room before returning messages
			room = ChatRoom.objects.get(id = room_id)
			#if not room.members.filter(id = self.request.user.id).exists(): 
			#	raise PermissionDenied
				
			return room.messages.all().order_by("timestamp")
		except ChatRoom.DoesNotExist: 
			return ChatRoom.objects.none()
	
class RoomMembersView(ListAPIView): 
	serializer_class = RoomMembersSerializer
	#permission_classes = [IsAuthenticated]
	def get_queryset(self): 
		room_id = self.kwargs["room_id"]
		try: 
			room = ChatRoom.objects.get(id = room_id)
			return room.members.all()
		except ChatRoom.DoesNotExist: 
			return ChatRoom.objects.none()
			
class RoomDetailsView(RetrieveUpdateDestroyAPIView): 
	queryset = ChatRoom.objects.all()
	serializer_class = RoomDetailsSerializer
	#permission_classes = [IsAuthenticated]
