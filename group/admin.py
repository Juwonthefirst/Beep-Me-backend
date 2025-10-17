from django.contrib import admin
from .models import Group, MemberDetail, Permission, Role

admin.site.register(Group)
admin.site.register(MemberDetail)
admin.site.register(Permission)
admin.site.register(Role)
