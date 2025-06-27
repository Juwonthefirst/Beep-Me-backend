from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import MemberDetail

class IsAdminOrReadOnly(BasePermission):
	"""
	permission to make sure any one editing the group is an admin or grant read only access
	"""
	def has_object_permission(self, request, view, obj): 
		return (obj.role == "admin") or (request.method in SAFE_METHODS)
		
		
class CanRemoveUser(BasePermission): 
	def has_object_permission(self, request, view, obj):
		group_id = request.kwargs.get("pk")
		member = MemberDetail.objects.filter(group_id = group_id, member = request.user)
		return member.role.permissions.filter(action = "can remove user").exists()
		
class CanAddUser(BasePermission): 
	def has_object_permission(self, request, view, obj):
		group_id = request.kwargs.get("pk")
		member = MemberDetail.objects.filter(group_id = group_id, member = request.user)
		return member.role.permissions.filter(action = "can add user").exists()
		
class CanChangeUserRole(BasePermission): 
	def has_object_permission(self, request, view, obj):
		group_id = request.kwargs.get("pk")
		member = MemberDetail.objects.filter(group_id = group_id, member = request.user)
		return member.role.permissions.filter(action = "can change role").exists()