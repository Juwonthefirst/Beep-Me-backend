from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()

class UsersSerializer(serializers.ModelSerializer): 
	is_following_me = serializers.BooleanField(read_only = True)
	is_followed_by_me = serializers.BooleanField(read_only = True)
	class Meta:
		model = User
		fields = ["id", "username", "email", "is_following_me", "is_followed_by_me"]
		
class RetrieveUsersSerializer(serializers.ModelSerializer): 
	is_following_me = serializers.BooleanField(read_only = True)
	is_followed_by_me = serializers.BooleanField(read_only = True)
	class Meta: 
		model = User
		fields = ["id", "username", "email", "first_name", "last_name", "is_followed_by_me", "is_following_me"]
		extra_kwargs = {
			"id": {
				"read_only": True
			}
		}
		
class UserIDSerializer(serializers.Serializer): 
	user_ids = serializers.ListField(child = serializers.IntegerField(min_value = 1), allow_empty = False)
