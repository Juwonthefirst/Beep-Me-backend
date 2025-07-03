from rest_framework.test import APITestCase
from group.serializers import (
	GroupSerializer, 
	GroupMemberSerializer, 
	GroupMemberChangeSerializer,
	RoleSerializer,
	PermissionSerializer,
)
from django.contrib.auth import get_user_model
from group.models import Group, MemberDetail, Role

User = get_user_model()

class TestGroupSerializer(APITestCase):
	def setUp(self): 
		self.user = User.objects.create_user(username = "test", email = "test@test.com", password = "testing123")
		self.user1 = User.objects.create_user(username = "test1", email = "test1@test.com", password = "testing123")
		self.group = Group.objects.create(name = "test")
		
	def test_create_method_with_valid_input(self):
		data = {
			"name": "test",
			"description": "I'm testing",
			"members": [{"member_id": self.user.id}, {"member_id": self.user1.id}],
		}
		serializer = GroupSerializer(data = data)
		self.assertTrue(serializer.is_valid())
		group = serializer.save()
		self.assertEqual(group.name, data["name"])
		self.assertIsNotNone(group.created_at)
		self.assertEqual(group.members.count(), 2)
		self.assertIsNotNone(group.chat_room)
		self.assertEqual(group.chat_room.name, "group." + str(group.id))
	
	def test_create_method_with_bad_input(self):
		data = {
			"description": "I'm testing",
			"members": [{"member_id": self.user.id, "role": "admin"}, {"member_id": self.user1.id, "role": "member"}],
		}
		serializer = GroupSerializer(data = data)
		self.assertFalse(serializer.is_valid())
			
	def test_serializer_description_field_blank_constraint(self):
		data = {
			"name": "juwon",
			"members": [{"member_id": self.user.id, "role": "admin"}, {"member_id": self.user1.id, "role": "member"}],
		}
		serializer = GroupSerializer(data = data)
		self.assertTrue(serializer.is_valid())
		
	def test_serializer_created_at_read_only(self):
		data = {
			"name": "TF, am i even doing",
			"description": "I'm testing",
			"members": [{"member_id": self.user.id, "role": "admin"}, {"member_id": self.user1.id, "role": "member"}],
			"created_at": "one day"
			
		}
		serializer = GroupSerializer(data = data)
		self.assertTrue(serializer.is_valid())
		self.assertNotIn("created_at", serializer.validated_data)
		
class TestGroupMemberSerializer(APITestCase): 
	def setUp(self): 
		self.user = User.objects.create_user(username = "test", email = "test@test.com", password = "testing123")
		self.group = Group.objects.create(name = "test")
		self.admim_role = Role.objects.create(name="admin", group = self. group)
		self.adminMember = MemberDetail.objects.create(group = self.group, member = self.user, role = self.admim_role)
	
	def test_read_only_fields_do_not_change_on_update(self):
		data = {
			"member_id": 3000,
			"member_username": "test",
			"joined_at": "today"
		}
		serializer = GroupMemberSerializer(self.adminMember, data = data, partial = True)
		self.assertTrue(serializer.is_valid())
		self.assertEqual(self.group.get_user_role(self.user).name, "admin")
		self.assertNotIn("member_id", serializer.validated_data)
		self.assertNotIn("member_username", serializer.validated_data)
		self.assertNotIn("joined_at", serializer.validated_data)
		
class TestGroupMemberChangeSerializer(APITestCase): 
	def test_validation_error_on_empty_list(self):
		serializer = GroupMemberChangeSerializer(data = {"member_ids": []})
		self.assertFalse(serializer.is_valid())
			
	def test_validation_error_on_wrong_data_type(self):
		serializer = GroupMemberChangeSerializer(data = {"member_ids": ""})
		self.assertFalse(serializer.is_valid())
		
class TestRoleSerializer(APITestCase):
	def setUp(self): 
		self.group = Group.objects.create(name = "test")
		self.mod_role = Role.objects.create(name = "mod", group = self.group)
		self.mod_role.permissions.add(1,2,3)
		
	def test_create_method_with_valid_data(self):
		data = {
			"name": "ninja",
			"group": 1,
			"permissions": [{"id": 1}, {"id": 2}]
		}
		serializer = RoleSerializer(data = data)
		self.assertTrue(serializer.is_valid())
		role = serializer.save()
		print(role)
		self.assertEqual(role.permissions.count(), 2)
		self.assertEqual(role.name, "ninja")
		self.assertEqual(role.group, self.group)
		self.assertIsNotNone(role.created_at)
		
	def test_create_method_with_invalid_data(self):
		data_1 = {
			"name": "",
			"group": 1,
			"permissions": [{"id": 1}, {"id": 2}]
		}
		
		serializer = RoleSerializer(data = data_1)
		self.assertFalse(serializer.is_valid())
		self.assertIn("name", serializer.errors)
		self.assertEqual(len(serializer.errors), 1)
		
		data_2 = {
			"name": "ninja",
			"permissions": [{"id": 1}, {"id": 2}]
		}
		
		serializer = RoleSerializer(data = data_2)
		self.assertFalse(serializer.is_valid())
		self.assertIn("group", serializer.errors)
		self.assertEqual(len(serializer.errors), 1)
		
		data_3 = {
			"name": "ninja",
			"group": 1
		}
		
		serializer = RoleSerializer(data = data_3)
		self.assertFalse(serializer.is_valid())
		self.assertIn("permissions", serializer.errors)
		self.assertEqual(len(serializer.errors), 1)
		
	def test_update_method_with_valid_input(self):
		data = {
			"name": "moderator"
		}
		
		serializer = RoleSerializer(instance = self.mod_role, data = data, partial = True)
		self.assertTrue(serializer.is_valid())
		self.new_mod_role = serializer.save()
		self.assertEqual(self.new_mod_role.name, "moderator")
		
		data = {
			"permissions": [{"id": 1}]
		}
		serializer = RoleSerializer(instance = self.mod_role, data = data, partial = True)
		self.assertTrue(serializer.is_valid())
		self.new_mod_role = serializer.save()
		self.assertEqual(new_mod_role.permissions.count(), 1)
		
	def test_update_method_with_empty_permissions(self):
		data = {
			"permissions": []
		}
		serializer = RoleSerializer(instance = self.mod_role, data = data, partial = True)
		self.assertTrue(serializer.is_valid())
		self.new_mod_role = serializer.save()
		self.assertEqual(new_mod_role.permissions.count(), 0)
		self.assertEqual(new_mod_role.name, "moderator")
		
	def test_update_method_with_invalid_input(self):
		data = {
			"name": ""
		}
		serializer = RoleSerializer(instance = self.mod_role, data = data, partial = True)
		self.assertFalse(serializer.is_valid())
		
		data = {
			"permissions": 1
		}
		serializer = RoleSerializer(instance = self.mod_role, data = data, partial = True)
		self.assertFalse(serializer.is_valid())
