from django.db import models
from django.contrib.auth import get_user_model
from message.models import Message
User = get_user_model()
# Create your models here.
class ProfilePicture(models.Model): 
	file = models.ImageField(upload_to = "upload/profile/")
	uploader = models.OneToOneField(User, related_name = "profile_picture", on_delete = models.CASCADE)
	uploaded_at = models.DateTimeField(auto_now_add = True)
	
	def save(self, *args, **kwargs): 
		if self.file: 
			self.file.name = self.uploader.id
		super().save(*args, **kwargs)
	
class Attachment(models.Model): 
	filename = models.CharField(max_length = 200)
	file = models.FileField(upload_to = "upload/attachment/")
	size = models.PositiveIntegerField(null = True, blank = True)
	source_message = models.OneToOneField(Message, related_name = "attachment", on_delete = models.CASCADE)
	content_type = models.CharField(max_length = 200)
	uploaded_at = models.DateTimeField(auto_now_add = True)
	sender = models.ForeignKey(User, )
	
	def save(self, *args, **kwargs): 
		if self.file: 
			self.file.name = source_message.id
			
		super().save(*args, **kwargs)