from rest_framework import serializers
from django.contrib.auth import get_user_model
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
		fields = ["id", "username", "email", "first_name", "last_name"]
		extra_kwargs = {
			"id": {
				"read_only": True
			}
		}
		
class UserIDSerializer(serializers.Serializer): 
	user_ids = serializers.ListField(child = serializers.IntegerField(min_value = 1), allow_empty = False)
