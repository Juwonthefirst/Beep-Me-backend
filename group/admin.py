from django.contrib import admin
from .models import Group, MemberDetail, GroupPermission, Role

admin.site.register(Group)
admin.site.register(MemberDetail)
admin.site.register(GroupPermission)
admin.site.register(Role)
