from rest_framework import serailizers
from .models import ChatRoom


class RoomMessagesSerializer(serailizers.ModelSerializer):
	class Meta: 
		model = ChatRoom
		fields = ["__all__"]