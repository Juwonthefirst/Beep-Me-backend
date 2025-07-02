from .models import Permission
from django.dispatch import receiver
from django.db.models.signals import post_migrate

@receiver(post_migrate)
def create_permissions():
    permissions = [
        "can delete member",
        "can add member",
        "can delete group message",
        "can update group details",
        "can create group role",
        "is video admin"
    ]

    permission_count = Permission.objects.count()
    for permission in permissions[permission_count:]:
        Permission.objects.create(action = permission)
