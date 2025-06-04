from rest_framework.test import APITestCase
from group.models import Group, MemberDetails
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from psycopg2.errors import ForeignKeyViolation
User = get_user_model()

class TestGroupModel(APITestCase):
	def setUp(self): 
		self.user = User.objects.create_user(username = "test", email = "test@test.com", password = "testing123")
		self.user1 = User.objects.create_user(username = "test1", email = "test1@test.com", password = "testing123")
		self.user2 = User.objects.create_user(username = "test2", email = "test2@test.com", password = "testing123")
		self.user3 = User.objects.create_user(username = "test3", email = "test3@test.com", password = "testing123")
		self.group = Group.objects.create(name = "test")
		self.member = MemberDetails.objects.create(group = self.group, member = self.user, role = "admin")
		
	def test_model_undefined(self): 
		group = Group(name = "", description = "")
		with self.assertRaises(ValidationError): 
			group.full_clean()
		
	def test_model_maxlength(self): 
		group = Group(name = "3"*200, description = "3"*500)
		with self.assertRaises(ValidationError): 
			group.full_clean()
	
	def test_model_created_at(self):
		group = Group(name = "test")
		group.save()
		self.assertIsNotNone(group.created_at)
		
	def test_model_method_user_is_admin(self):
		self.assertTrue(self.group.user_is_admin(self.user))
		self.assertFalse(self.group.user_is_admin(self.user1))
		
	def test_model_method_add_members(self):
		self.assertEqual(self.group.members.count(), 1)
		self.group.add_members([self.user1.id, self.user2.id])
		self.assertEqual(self.group.members.count(), 3)
		
	def test_model_method_add_members_without_list(self):
		with self.assertRaises(ValueError): 
			self.group.add_members(self.user.id)
			
	def test_model_method_add_members_duplicate_users(self):
		with self.assertRaises(IntegrityError):	
			self.group.add_members([self.user.id])
			
	def test_model_method_add_members_uncreated_user(self):
		with self.assertRaises((ForeignKeyViolation, IntegrityError)):
			self.group.add_members([999])
			
	def test_model_method_update_members_role(self):
		self.assertTrue(self.group.user_is_admin(user = self.user))
		self.group.update_members_role("member", [self.user.id])
		self.assertFalse(self.group.user_is_admin(user = self.user))
		
	def test_model_method_update_members_role_without_list(self):
		with self.assertRaises(ValueError): 
			self.group.update_members_role("admin", self.user.id)
			
	def test_model_method_delete_members(self):
		self.group.add_members([self.user1.id, self.user2.id])
		self.assertEqual(self.group.members.count(), 3)
		self.group.delete_members([self.user.id, self.user1.id])
		self.assertEqual(self.group.members.count(), 1)
		
	def test_model_method_delete_members_without_list(self):
		with self.assertRaises(ValueError): 
			self.group.delete_members(self.user.id)