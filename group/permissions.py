from rest_framework.permissions import BasePermission
from .models import MemberDetails
class IsAdmin(BasePermission): 
	"""
	permission to make sure any one editing the group is an admin
	"""
	def has_object_permission(self, request, view, obj, user_id):
		return obj.user_is_admin(request.user) or 