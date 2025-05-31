from rest_framework import serializer
from .models import ChatRoom


class RoomMessagesSerializer(serializer.ModelSerializer):
	class Meta: 
		model = ChatRoom
		fields = ["__all__"]