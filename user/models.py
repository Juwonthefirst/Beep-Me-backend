from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone

username_validator = RegexValidator(
	regex = "^[a-zA-Z](?:[a-zA-Z0-9]*(?:[-_][a-zA-Z0-9])?)*[a-zA-Z0-9]+$",
	message = "Your username should only have letters, number and non-repeating underscore and hyphen",
	code = "invalid_username"
)


class CustomUser(AbstractUser): 
	last_online = models.DateTimeField()
	username = models.CharField(max_length = 60, unique = True, validators = [username_validator], error_messages = {"unique": "a user with this username already exists"}, db_index = True)
	following = models.ManyToManyField("self", symmetrical = False, related_name = "followers")
		
	def mark_offline(self): 
		self.last_online = timezone.now()
		self.save(updated_fields = ["last_online"])
		
	def is_friend(self, user_id): 
		return self.followers.filter(id = user_id).exists() and self.following.filter(id = user_id).exists()
		
	def get_friends(self): 
		followers_id = self.followers.related_name("id").all()
		friends = self.following.filter(id__in = followers_id)
		return friends