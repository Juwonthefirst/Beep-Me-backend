from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser): 
	username_validator = models.RegexValidator(
		re
	)
	email = models.EmailField(unique = True)
	friends = models.ManyToManyField("self", symmetrical = True)