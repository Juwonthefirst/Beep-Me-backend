from rest_framework import serializers
from .models import ChatRoom
from user.serializers import UsersSerializer
from message.serializers import MessagesSerializer
from group.serializers import GroupSerializer


class RoomDetailsSerializer(serializers.ModelSerializer): 
	class Meta: 
		model = ChatRoom
		fields = "__all__"
		
class UserChatRoomSerializer(serializers.ModelSerializer): 
	parent = serializers.SerializerMethodField()
	last_message = serializers.SerializerMethodField()
	class Meta: 
		model = ChatRoom
		fields = ["parent", "last_message", "id", "name", "is_group"]
		
	def get_last_message(self, obj): 
		last_message_object = obj.get_last_message()
		return MessagesSerializer(last_message_object).data
	
	def get_parent(self, obj): 
		if obj.is_group: 
			return GroupSerializer(obj.group).data
		user_id = self.context.get("user_id")
		other_member = obj.members.exclude(id = user_id)
		return UsersSerializer(other_member).data