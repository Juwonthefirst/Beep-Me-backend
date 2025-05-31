from rest_framework import serializers
from .models import ChatRoom


class RoomMessagesSerializer(serializers.ModelSerializer):
	class Meta: 
		model = ChatRoom
		fields = ["__all__"]