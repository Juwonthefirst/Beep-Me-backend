from rest_framework import serializers
from django.contrib.auth import get_user_model
from notification.models import Notification
from chat_room.models import ChatRoom
from chat_room.serializers import RoomMessagesSerializer
User = get_user_model()

class UsersSerializer(serializers.ModelSerializer): 
	class Meta: 
		model = User
		fields = ["id", "username", "profile_picture"]
		
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
	last_message = serializers.SerializerMethodField()
	class Meta: 
		model = ChatRoom
		fields = "__all__"
		
	def get_last_message(self, obj): 
		last_message_object = obj.get_last_message()
		return RoomMessagesSerializer(last_message_object).data
		
class UserNotificationsSerializer(serializers.ModelSerializer): 
	class Meta: 
		model = Notification
		fields = "__all__"