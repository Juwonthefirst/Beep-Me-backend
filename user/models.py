from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.conf import settings

username_validator = RegexValidator(
	regex = settings.USERNAME_REGEX,
	message = "Your username should only have letters, number and non-repeating underscore and hyphen",
	code = "invalid_username"
)

class ActiveUserQueryset(models.QuerySet): 
	def active(self): 
		return self.filter(is_active = True)

class ActiveUserManager(UserManager): 
	def get_queryset(self):
		return ActiveUserQuerySet(self.model, using = self._db)



class CustomUser(AbstractUser): 
	last_online = models.DateTimeField(auto_now_add = True)
	username = models.CharField(max_length = 60, unique = True, validators = [username_validator], error_messages = {"unique": "a user with this username already exists"}, db_index = True)
	email = models.EmailField(unique = True, db_index = True)
	following = models.ManyToManyField("self", symmetrical = False, related_name = "followers")
	#objects = ActiveUserManager()
	
	def mark_last_online(self): 
		self.last_online = timezone.now()
		self.save(update_fields = ["last_online"])
		
	def is_friend(self, user_id): 
		return self.followers.filter(id = user_id).exists() and self.following.filter(id = user_id).exists()
		
	def get_friends(self): 
		return self.following.filter(id__in = self.followers.values_list("id", flat = True))
		
	def get_unmutual_following(self): 
		friends = self.get_friends().values_list("id", flat = True)
		return set(self.following.values_list("id", flat = True)) - set(friends)
	
	def get_unmutual_followers(self): 
		friends = self.get_friends().values_list("id", flat = True)
		return set(self.followers.values_list("id", flat = True)) - set(friends)
		
	def save(self, *args, **kwargs):
		self.username = self.username.capitalize()
		super().save(*args, **kwargs)