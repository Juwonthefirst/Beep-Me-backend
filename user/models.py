from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from datetime import timezone
# Create your models here.

username_validator = RegexValidator(
	regex = "^[a-zA-Z](?:[a-zA-Z0-9]*(?:[-_][a-zA-Z0-9])?)*[a-zA-Z0-9]+$",
	message = "Your username should only have letters, number and non-repeating underscore and hyphen",
	code = "invalid_username"
)


class CustomUser(AbstractUser): 
	is_online = models.BooleanField(default = False)
	last_online = models.DateTimeField()
	profile_picture = models.CharField(max_length = 200, default = "default")
	username = models.CharField(max_length = 60, unique = True, validators = [username_validator], error_messages = {"unique": "a user with this username already exists"}, db_index = True)
	friends = models.ManyToManyField("self", symmetrical = True, null = True)
	
	def mark_online( self ): 
		self.is_online = True
		self.save(updated_fields = ["is_online"])
		
	def mark_offline(self): 
		self.is_online = False
		self.last_online = timezone.now()
		self.save(updated_fields = ["is_online", "last_online"])