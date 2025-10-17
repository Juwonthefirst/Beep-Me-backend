from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import post_delete

User = get_user_model()


@receiver(post_delete, sender=[User])
def delete_avatar(sender, instance, **kwargs):
    if instance:
        instance.profile_picture.file.delete(save=False)
