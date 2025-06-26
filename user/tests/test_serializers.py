from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from . import serializers
User = get_user_model()

class TestGroupSerializer(APITestCase):
	def setUp(self): 
		self.user = User.objects.create_user(username = "test", email = "test@test.com", password = "testing123")
		self.user1 = User.objects.create_user(username = "test1", email = "test1@test.com", password = "testing123")