from .models import Group, GroupPermission
from django.dispatch import receiver
from django.db.models.signals import post_migrate, post_delete
from BeepMe.storage import public_storage


@receiver(post_migrate)
def create_permissions(**kwargs):
    permissions = [
        {"action": "can delete member", "code": 101},
        {"action": "can add member", "code": 102},
        {"action": "can delete group message", "code": 103},
        {"action": "can update group details", "code": 104},
        {"action": "can create group role", "code": 105},
        {"action": "video admin", "code": 106},
    ]

    permission_count = GroupPermission.objects.count()
    for permission in permissions[permission_count:]:
        GroupPermission.objects.create(**permission)


@receiver(post_delete, sender=Group)
def delete_avatar(sender, instance: Group, **kwargs):
    if instance and instance.avatar:
        public_storage.delete_file(instance.avatar)
