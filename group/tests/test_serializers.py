from rest_framework.test import APITestCase
from .serializers import GroupSerializer, GroupMemberSerializer

class TestGroupSerializer(APITestCase):
	def setUp(self): 
		self.user = User.objects.create_user(username = "test", email = "test@test.com", password = "testing123")
		self.user1 = User.objects.create_user(username = "test1", email = "test1@test.com", password = "testing123")
		self.user2 = User.objects.create_user(username = "test2", email = "test2@test.com", password = "testing123")
		self.user3 = User.objects.create_user(username = "test3", email = "test3@test.com", password = "testing123")
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
		with self.assertRaises(): 
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
	def test_update_method_with_valid_input(self):
		data = {
			"role": "member"
		}
		self.assertTrue(self.Group.user_is_admin(self.user))
		serializer = GroupMemberSerializer(self.adminMember, data = data, partial = True)
		self.assertTrue(serailizer.is_valid())
		member = serailizer.save()
		self.assertEqual(member.role, "member")
		self.assertIsNotNone(group.created_at)
		
	