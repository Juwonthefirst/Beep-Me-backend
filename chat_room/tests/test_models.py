from rest_framework.test import APITestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from chat_room.models import ChatRoom
from message.models import Message
User = get_user_model()

class TestChatRoom(APITestCase):
	def setUp(self): 
		self.room = ChatRoom.objects.create(name = "testing")
		self.user = User.objects.create_user(username = "test", email = "test@test.com", password = "testing123")
		self.user1 = User.objects.create_user(username = "test1", email = "test1@test.com", password = "testing123")
		self.user.following.add(self.user1)
		self.user1.following.add(self.user)
		self.message1 = Message.objects.create(sender = self.user, body = "This is a test for the UserChatRoomSerializer", room = self.room)
		self.message2 = Message.objects.create(sender = self.user, body = "This is another test for the UserChatRoomSerializer", room = self.room)
		
	def test_name_field_length_constriction(self):
		chat_room = ChatRoom(name = "")
		with self.assertRaises(ValidationError): 
			chat_room.full_clean()
			
		chat_room1 = ChatRoom(name = "x"*101)
		with self.assertRaises(ValidationError): 
			chat_room1.full_clean()
		
	def test_name_field_unique_validation(self):
		chat_room1 = ChatRoom(name = "testing")
		with self.assertRaises(ValidationError): 
			chat_room1.save()
			
		chat_room1.delete()
		
	def test_members_many_to_many_relationship_methods(self):
		self.assertEqual(self.room.members.count(), 0)
		self.room.members.add(self.user, self.user1)
		self.assertEqual(self.room.members.count(), 2)
		self.room.members.remove(self.user)
		self.assertEqual(self.room.members.all(), [self.user1])
		self.room.members.add(self.user)
		self.room.members.clear()
		self.assertEqual(self.room.members.count(), 0)
		
	def test_create_with_members_model_method_with_group_prefix(self):
		with self.assertRaises(ValueError): 
			ChatRoom.create_with_members("group_1_2")
			
	def test_create_with_members_model_method_with_chat_prefix(self):
		chat_room = ChatRoom.create_with_members("chat_1_2")
		self.assertEqual(chat_room.members.count(), 2)
		
	def test_get_last_message(self):
		last_message = self.room.get_last_message()
		self.assertEqual(last_message.id, self.message2.id)
		