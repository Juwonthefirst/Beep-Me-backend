from django.apps import AppConfig


class GroupConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'group'
    
    def ready(self): 
        from .models import Permission
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
