from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from user.serializers import UsersSerializer, UserIDSerializer, RetrieveUsersSerializer
User = get_user_model()

class TestUserSerializer(APITestCase):
	def setUp(self): 
		self.user = User.objects.create_user(username = "test", email = "test@test.com", password = "testing123")
		self.user1 = User.objects.create_user(username = "test1", email = "test1@test.com", password = "testing123")
		self.user2 = User.objects.create_user(username = "test2", email = "test2@test.com", password = "testing123")
		self.user3 = User.objects.create_user(username = "test3", email = "test3@test.com", password = "testing123")
		self.user.following.add(self.user1, self.user2)
		
	def test_output_data(self):
		data = UsersSerializer(self.user).data
		self.assertIsNotNone(data.get("id"))
		self.assertIsNotNone(data.get("username"))
		self.assertEqual(self.user.id, data.get("id"))
		
		
class TestRetrieveUsersSerializer(APITestCase):
	def setUp(self): 
		self.user = User.objects.create_user(username = "test", email = "test@test.com", password = "testing123")
		self.user1 = User.objects.create_user(username = "test1", email = "test1@test.com", password = "testing123")
		self.user2 = User.objects.create_user(username = "test2", email = "test2@test.com", password = "testing123")
		self.user3 = User.objects.create_user(username = "test3", email = "test3@test.com", password = "testing123")
		self.user.following.add(self.user1, self.user2)

	def test_output_data(self):
		data = RetrieveUsersSerializer(self.user).data
		self.assertIn("id", data)
		self.assertEqual(self.user.username, data.get("username"))
		self.assertEqual(self.user.email, data.get("email"))
		
	def test_update_with_valid_data(self):
		data = {
			"username": "test40",
			"email": "test45@test.com",
			"first_name": "tester",
			"last_name": "mctester"
		}
		user4 = User.objects.create_user(username = "test4", email = "test4@test.com", password = "testing123")
		
		serializer = RetrieveUsersSerializer(user4, data = data, partial = True)
		self.assertTrue(serializer.is_valid())
		self.assertIn("username", serializer.validated_data)
		self.assertIn("email", serializer.validated_data)
		self.assertIn("first_name", serializer.validated_data)
		self.assertIn("last_name", serializer.validated_data)
		updated_user4 = serializer.save()
		self.assertEqual(updated_user4.id, user4.id)
		self.assertEqual(updated_user4.username, data.get("username"))
		user4.delete()
		
	def test_id_does_not_get_validated(self):
		data = {
			"id": 500000078,
			"username": "The_jay_man"
		}
		serializer = RetrieveUsersSerializer(data = data)
		self.assertTrue(serializer.is_valid())
		self.assertNotIn("id", serializer.validated_data)
		
		
class TestFriendRequestSerializer(APITestCase): 
	def test_validation_on_proper_data(self):
		serializer = FriendRequestSerializer(data = {"friend_id": 1, "action": "sent"})
		self.assertTrue(serializer.is_valid())
			
	def test_validation_error_on_empty_data(self):
		serializer = FriendRequestSerializer(data = {})
		self.assertFalse(serializer.is_valid())
		
	def test_validation_on_missing_data(self):
		serializer = FriendRequestSerializer(data = {"friend_id": 1})
		self.assertFalse(serializer.is_valid())
	    
	    serializer = FriendRequestSerializer(data = {"action": "sent"})
		self.assertFalse(serializer.is_valid())