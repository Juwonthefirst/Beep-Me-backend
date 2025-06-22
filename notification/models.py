from django.db import models
from django.contrib.auth import get_user_model
from group.models import Group
User = get_user_model()

# Create your models here.
class Notification(models.Model): 
	notification_type = models.CharField(max_length = 100)
	timestamp = models.DateTimeField()
	notification = models.CharField(max_length = 200)
	initiator = models.ForeignKey(User, on_delete = models.SET_NULL, null = True)
	receiver = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "notifications")
	group = models.ForeignKey(Group, on_delete = models.SET_NULL, related_name = "notifications", null = True)
	is_read = models.BooleanField(default = False)