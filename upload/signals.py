from django.db.models.signals import post_delete
from django.dispatch import receiver

from BeepMe.storage import private_storage
from .models import Attachment


@receiver(post_delete, sender=Attachment)
def delete_file_after_row_delete(sender, instance: Attachment, **kwargs):
    if instance:
        private_storage.delete_file(instance.path)
