from .models import Group, Permission
from django.dispatch import receiver
from django.db.models.signals import post_migrate, post_delete


@receiver(post_migrate)
def create_permissions(**kwargs):
    permissions = [
        "can delete member",
        "can add member",
        "can delete group message",
        "can update group details",
        "can create group role",
        "is video admin",
    ]

    permission_count = Permission.objects.count()
    for permission in permissions[permission_count:]:
        Permission.objects.create(action=permission)


@receiver(post_delete, sender=Group)
def delete_avatar(sender, instance, **kwargs):
    if instance:
        instance.avatar.file.delete(save=False)
