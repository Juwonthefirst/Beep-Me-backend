from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from time import sleep
User = get_user_model()

class TestUserModel(APITestCase):
	def setUp(self): 
		self.user = User.objects.create_user(username = "test", email = "test@test.com", password = "testing123")
		self.user1 = User.objects.create_user(username = "test1", email = "test1@test.com", password = "testing123")
		self.user2 = User.objects.create_user(username = "test2", email = "test2@test.com", password = "testing123")
		self.user3 = User.objects.create_user(username = "test3", email = "test3@test.com", password = "testing123")
		self.user.following.add(self.user1, self.user2)
		
	def test_adding_followers_match_following_in_the_opposite_user(self):
		self.assertEqual(self.user.following.count(), 2)
		self.assertEqual(self.user1.followers.count(), 1)

	def test_is_friend_method(self):
		self.user1.following.add(self.user)
		self.assertTrue(self.user.is_friend(self.user1.id))
		self.assertFalse(self.user.is_friend(self.user3.id))
		self.user1.following.clear()
		
	def test_get_friends_method(self):
		friends = self.user.get_friends()
		assertTrue(isinstance(friends, list))
		assertEqual(self.user.following.count(), 2)
		
	def test_get_unmutual_following_method(self):
		unmutual_following = self.user.get_unmutual_following()
		self.assertEqual(len(unmutual_following), 3)
		self.user1.following.add(self.user)
		self.assertEqual(len(unmutual_following), 2)
		self.user1.following.clear()
		
	def test_get_unmutual_followers_method(self):
		unmutual_followers = self.user1.get_unmutual_following()
		self.assertEqual(len(unmutual_followers), 1)
		self.user1.following.add(self.user)
		self.assertEqual(len(unmutual_followers), 0)
		self.user1.following.clear()
		
	def test_mark_last_online_method_is_updating(self):
		self.user.mark_last_online()
		old_last_online = self.user.last_online
		self.assertIsNotNone(old_last_online)
		sleep(1)
		self.user.mark_last_online()
		new_last_online = self.user.last_online
		
		assertTrue(new_last_online > old_last_online)
		
		
	def test_username_regex(self):
		user4 = User(username = "test__1", email = "test1@test.com", password = "testing123")
		with self.assertRaises(ValidationError): 
			user4.full_clean()