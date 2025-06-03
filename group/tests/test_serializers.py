from rest_framework.test import APITestCase
from .serializers import GroupSerializer, GroupMemberSerializer, GroupMemberChangeSerializer
from rest_framework.serializers import ValidationError

class TestGroupSerializer(APITestCase):
	def setUp(self): 
		self.user = User.objects.create_user(username = "test", email = "test@test.com", password = "testing123")
		self.user1 = User.objects.create_user(username = "test1", email = "test1@test.com", password = "testing123")
		self.group = Group.objects.create(name = "test")
		self.adminMember = MemberDetails.objects.create(group = self.group, user = self.user, role = "admin")
		
	def test_create_method_with_valid_input(self):
		data = {
			"name": "test",
			"description": "I'm testing",
			"members": [self.user.id, self.user1.id]
		}
		serializer = GroupSerializer(data = data)
		self.assertTrue(serailizer.is_valid())
		group = serailizer.save()
		self.assertEqual(group.name, data["name"])
		self.assertIsNotNone(group.created_at)
		self.assertEqual(group.members.count(), 2)
		self.assertIsNotNone(group.chat_room)
		self.assertEqual(group.chat_room.name, "group." + group.id)
	
	def test_create_method_with_bad_input(self):
		data = {
			"description": "I'm testing",
			"members": [self.user.id, self.user1.id]
		}
		serializer = GroupSerializer(data = data)
		with self.assertRaises(ValidationError): 
			serializer.is_valid()
			
	def test_serializer_description_field_blank_constraint(self):
		data = {
			"name": "juwon",
			"members": [self.user.id, self.user1.id]
		}
		serializer = GroupSerializer(data = data)
		self.assertTrue(serializer.is_valid())
		
	def test_serializer_created_at_write_only(self):
		data = {
			"name": "TF, am i even doing"
			"description": "I'm testing",
			"members": [self.user.id, self.user1.id],
			"created_at": "one day"
			
		}
		serializer = GroupSerializer(data = data)
		self.assertTrue(serializer.is_valid())
		group = serailizer.save()
		self.assertNotEqual(group.created_at, "one day")
		
class TestGroupMemberSerializer(APITestCase): 
	def setUp(self): 
		self.user = User.objects.create_user(username = "test", email = "test@test.com", password = "testing123")
		self.group = Group.objects.create(name = "test")
		self.adminMember = MemberDetails.objects.create(group = self.group, user = self.user, role = "admin")
	def test_update_method_with_valid_input(self):
		data = {
			"role": "member"
		}
		self.assertTrue(self.Group.user_is_admin(self.user))
		serializer = GroupMemberSerializer(self.adminMember, data = data, partial = True)
		self.assertTrue(serailizer.is_valid())
		member = serailizer.save()
		self.assertEqual(member.role, "member")
		self.assertIsNotNone(member.joined_at)
	
	def test_read_only_fields_do_not_change_on_create(self):
		data = {
			"role": "admin",
			"member_id": 3000,
			"member_username": "test",
			"joined_at": "today"
		}
		serializer = GroupMemberSerializer(self.adminMember, data = data, partial = True)
		self.assertTrue(serailizer.is_valid())
		member = serailizer.save()
		self.assertTrue(Group.user_is_admin(self.user))
		self.assertEqual(member.member_id, 1)
		self.assertEqual(member.member_username, "test")
		self.assertNotEqual(member.joined_at, "today")
		
class TestGroupMemberChangeSerializer(APITestCase): 
	def test_validation_error_on_empty_list(self):
		serializer = GroupMemberChangeSerializer(data = [])
		with self.assertRaises(ValidationError): 
			serailizer.is_valid()
			
	def test_validation_error_on_wrong_data_type(self):
		serailizer = GroupMemberChangeSerializer(data = "")
		with self.assertRaises(ValidationError): 
			serailizer.is_valid()