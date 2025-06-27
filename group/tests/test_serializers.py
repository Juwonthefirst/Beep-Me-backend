from rest_framework.test import APITestCase
from group.serializers import GroupSerializer, GroupMemberSerializer, GroupMemberChangeSerializer
from django.contrib.auth import get_user_model
from group.models import Group, MemberDetail

User = get_user_model()

class TestGroupSerializer(APITestCase):
	def setUp(self): 
		self.user = User.objects.create_user(username = "test", email = "test@test.com", password = "testing123")
		self.user1 = User.objects.create_user(username = "test1", email = "test1@test.com", password = "testing123")
		self.group = Group.objects.create(name = "test")
		self.adminMember = MemberDetail.objects.create(group = self.group, member = self.user, role = "admin")
		
	def test_create_method_with_valid_input(self):
		data = {
			"name": "test",
			"description": "I'm testing",
			"members": [{"member_id": self.user.id, "role": "admin"}, {"member_id": self.user1.id, "role": "member"}],
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
		self.adminMember = MemberDetail.objects.create(group = self.group, member = self.user, role = "admin")
		
	def test_update_method_with_valid_input(self):
		data = {
			"role": "member"
		}
		self.assertTrue(self.group.user_is_admin(self.user))
		serializer = GroupMemberSerializer(self.adminMember, data = data, partial = True)
		self.assertTrue(serializer.is_valid())
		member = serializer.save()
		self.assertEqual(member.role, "member")
		self.assertIsNotNone(member.joined_at)
	
	def test_read_only_fields_do_not_change_on_update(self):
		data = {
			"role": "admin",
			"member_id": 3000,
			"member_username": "test",
			"joined_at": "today"
		}
		serializer = GroupMemberSerializer(self.adminMember, data = data, partial = True)
		self.assertTrue(serializer.is_valid())
		self.assertTrue(self.group.user_is_admin(self.user))
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
	def test_description(self):
		