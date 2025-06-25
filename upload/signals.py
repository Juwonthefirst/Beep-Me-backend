from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import ProfilePicture, Attachment


@receiver(post_delete, sender = [ProfilePicture, Attachment])
def delete_file_after_row_delete(sender, **kwargs): 
	if instance: 
		instance.file.delete()