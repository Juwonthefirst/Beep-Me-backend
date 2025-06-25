from rest_framework import serializers
from .models import ChatRoom
from django.contrib.auth import get_user_model
from message.models import Message

User = get_user_model()

class RoomMessagesSerializer(serializers.ModelSerializer):
	class Meta: 
		model = Message
		fields = "__all__"
		
class RoomMembersSerializer(serializers.ModelSerializer): 
	class Meta: 
		model = User
		fields = ["id", "username"]
		
class RoomDetailsSerializer(serializers.ModelSerializer): 
	class Meta: 
		model = ChatRoom
		fields = "__all__"
		
class UserChatRoomSerializer(serializers.ModelSerializer): 
	parent = serializers.SerializerMethodField()
	last_message = serializers.SerializerMethodField()
	class Meta: 
		model = ChatRoom
		fields = ["parent","last_message", "id", "name", "is_group"]
		
	def get_last_message(self, obj): 
		last_message_object = obj.get_last_message()
		return RoomMessagesSerializer(last_message_object).data
	
	def get_parent(self, obj): 
		if obj.is_group: 
			return GroupSerializer(obj.group).data
		user_id = self.context.get("user_id")
		other_member = obj.members.exclude(id = user_id)
		return UsersSerializer(other_member).data