from django.db import models

# Create your models here.
class Upload(models.Model): 
	filename = models.CharField(max_length = 200)
	file = models.FileField(upload_to = "upload/")
	size = models.PositiveIntegerField(null = True, blank = True)
	content_type = models.CharField(max_length = 200)
	uploaded_at = models.DateTimeField(auto_add_now = True)
	
	