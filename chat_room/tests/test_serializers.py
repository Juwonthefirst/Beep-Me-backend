from rest_framework.test import APITestCase
from chat_room.serializers import UserChatRoomSerializer
from chat_room.models import ChatRoom
from group.models import Group
from message.models import Message
from django.contrib.auth import get_user_model
User = get_user_model()

class TestUserChatRoomSerializer(APITestCase):
	def setUp(self): 
		self.user = User.objects.create_user(username = "test", email = "test@test.com", password = "testing123")
		self.user1 = User.objects.create_user(username = "test1", email = "test1@test.com", password = "testing123")
		self.group = Group.objects.create(name = "test_group")
		self.user.following.add(self.user1)
		self.user1.following.add(self.user)
		self.chat_room = ChatRoom.create_with_members("chat_1_2")
		self.group_chat_room = ChatRoom.objects.create(name = "group.12", is_group = True, group = self.group)
		self.message1 = Message.objects.create(sender = self.user, body = "This is a test for the UserChatRoomSerializer", room = self.chat_room)
		self.message2 = Message.objects.create(sender = self.user, body = "This is another test for the UserChatRoomSerializer", room = self.chat_room)
		self.chat_serializer_data = UserChatRoomSerializer(self.chat_room, context = {"user_id": self.user.id}).data
		self.group_chat_serializer_data = UserChatRoomSerializer(self.group_chat_room).data

	def test_parent_serializer_method_field_if_it_returns_the_right_parent(self):
		self.assertIn("parent", self.chat_serializer_data)
		self.assertEqual(self.chat_serializer_data["parent"]["id"], self.user1.id)
		
	def test_parent_serializer_method_field_if_it_returns_the_right_parent_with_a_group(self):
		self.assertTrue(self.group_chat_serializer_data["is_group"])
		self.assertIn("parent", self.group_chat_serializer_data)
		self.assertEqual(self.group_chat_serializer_data["parent"]["id"], self.group.id)
		
	def test_last_message_serializer_method_field_if_it_returns_the_last_message(self):
		self.assertIn("last_message", self.chat_serializer_data)
		self.assertEqual(self.chat_serializer_data["last_message"]["id"], self.message2.id)
		