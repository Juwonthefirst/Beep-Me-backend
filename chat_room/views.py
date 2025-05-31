from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from chat_room.serializers import RoomMessagesSerializer
from chat_room.permissions import IsMember
from chat_room.models import ChatRoom

class RoomMessagesView(ListAPIView):
	serializer_class = RoomMessagesSerializer
	permission_classes = [IsMember]
	def get_queryset(self): 
		room_id = self.kwargs["room_id"]
		try: 
			return ChatRoom.objects.get(id = room_id).messages.all().order_by("timestamp")
		except ChatRoom.DoesNotExist: 
			return ChatRoom.objects.none()
	