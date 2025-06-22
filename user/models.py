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
	last_online = models.DateTimeField()
	username = models.CharField(max_length = 60, unique = True, validators = [username_validator], error_messages = {"unique": "a user with this username already exists"}, db_index = True)
	friends = models.ManyToManyField("self", symmetrical = False, null = True)
		
	def mark_offline(self): 
		self.last_online = timezone.now()
		self.save(updated_fields = ["last_online"])