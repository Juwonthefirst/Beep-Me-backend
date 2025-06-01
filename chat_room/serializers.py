from rest_framework import serializers
from .models import ChatRoom
from django.contrib.auth import get_user_model
from message.models import Message

User = get_user_model()

class RoomMessagesSerializer(serializers.ModelSerializer):
	class Meta: 
		model = Messages
		fields = "__all__"
		
class RoomMembersSerializer(serializers.ModelSerializer): 
	class Meta: 
		model = User
		fields = ["id", "username", "email"]
		
class RoomDetailsSerializer(serializers.ModelSerializer): 
	class Meta: 
		model = ChatRoom
		fields = "__all__"