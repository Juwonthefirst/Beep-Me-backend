from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
# Create your models here.
class ProfilePicture(models.Model): 
	file = models.ImageField(upload_to = "upload/profile_picture/")
	uploader = models.OneToOneField(User, related_name = "profile_picture")
	uploaded_at = models.DateTimeField(auto_now_add = True)
	
	def save(self, *args, **kwargs): 
		if self.file: 
			self.file.name = self.uploader_id.id
		super().save(*args, **kwargs)
	
class Attachment(models.Model): 
	filename = models.CharField(max_length = 200)
	file = models.ImageField(upload_to = "upload/attachment/")
	size = models.PositiveIntegerField(null = True, blank = True)
	content_type = models.CharField(max_length = 200)
	uploaded_at = models.DateTimeField(auto_now_add = True)