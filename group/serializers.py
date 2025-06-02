from rest_framework import serializers
from .models import Group
class CreateGroupSerializer(serializers.Serializer): 
	class Meta: 
		model = Group
		fields = "__all__"