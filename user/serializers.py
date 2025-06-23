from rest_framework import serializers
from django.contrib.auth import get_user_model
from chat_room.models import ChatRoom
from chat_room.serializers import RoomMessagesSerializer
from group.serializers import GroupSerializer
User = get_user_model()

class UsersSerializer(serializers.ModelSerializer): 
	class Meta: 
		model = User
		fields = ["id", "username"]
		
class RetrieveUsersSerializer(serializers.ModelSerializer): 
	class Meta: 
		model = User
		fields = "__all__"
		extra_kwargs = {
		    "password": {
		        "write_only": True
		    }
		}
		
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