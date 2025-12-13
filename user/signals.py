from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import post_delete, pre_save
from BeepMe.storage import public_storage

User = get_user_model()


@receiver(post_delete, sender=User)
def delete_avatar(sender, instance, **kwargs):
    if instance and instance.profile_picture:
        public_storage.delete_file(instance.profile_picture)


@receiver(pre_save, sender=User)
def delete_avatar_on_update(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    old_file = old_instance.profile_picture
    new_file = instance.profile_picture
    if old_file != new_file:
        public_storage.delete_file(old_file)
