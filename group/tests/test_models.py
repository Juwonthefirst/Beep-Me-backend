from rest_framework.test import APITestCase
from group.models import Group, MemberDetails
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

class TestGroupModel(APITestCase):
	def setUp(self): 
		self.user = User.objects.create_user(username = "test", email = "test@test.com", password = "testing123")
		self.group = Group.objects.create(name = "test")
		self.member = MemberDetails.objects.create(group = self.group, user = self.user, role = "admin")
		
	def test_model_undefined(self): 
		group = Group(name = "", description = "")
		with self.assertRaises(ValidationError): 
			group.full_clean()
		
	def test_model_maxlength(self): 
		group = Group(name = "3"*100, description = "3"*100)
		with self.assertRaises(ValidationError): 
			group.full_clean()
			
	def test_model_method_user_is_admin(self):
		self.assertTrue(self.group.user_is_admin(self.user))
	
	def test_model_method_add_members(self):
		self.group.add_members([1])
		self.assertEqual(self.group.members.count(), 1)
		self.group.add_members([1, 2, 3])
		self.assertEqual(self.group.members.count(), 3)
		with self.assertRaises(ValueError): 
			self.group.add_members(1)