from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
# Create your models here.

username_validator = RegexValidator(
	regex = "^[a-zA-Z](?:[a-zA-Z0-9]*(?:[-_][a-zA-Z0-9])?)*[a-zA-Z0-9]+$",
	message = "Your username should only have letters, number and non-repeating undersore and hyphen",
	code = "invalid_username"
)


class CustomUser(AbstractUser): 
	username = models.CharField(max_length = 60, unique = True, validators = [username_validator], error_messages = {"unique": "a user with this username already exists"})
	friends = models.ManyToManyField("self", symmetrical = True)