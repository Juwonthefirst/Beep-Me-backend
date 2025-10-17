from django.db import models


class Attachment(models.Model):
    filename = models.CharField(max_length=200)
    file = models.FileField(upload_to="upload/attachment/")
    size = models.PositiveIntegerField(null=True, blank=True)
    content_type = models.CharField(max_length=200)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    """def save(self, *args, **kwargs): 
		if self.file: 
			self.file.name = source_message.id
		
		super().save{(*args, **kwargs)}"""
