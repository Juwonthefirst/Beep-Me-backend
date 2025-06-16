from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UsersSerializer(serializers.ModelSerializer): 
	class Meta: 
		model = User
		fields = ["id", "username", "profile_picture"]
		
class RetrieveUsersSerializer(serializers.ModelSerializer): 
	class Meta: 
		model = User
		fields = "__all__"
		