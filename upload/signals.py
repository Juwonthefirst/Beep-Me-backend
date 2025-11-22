from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Attachment


@receiver(post_delete, sender=Attachment)
def delete_file_after_row_delete(sender, instance, **kwargs):
    if instance:
        instance.file.delete(save=False)
