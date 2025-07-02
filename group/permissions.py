from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import MemberDetail

class IsAdminOrReadOnly(BasePermission):
	"""
	permission to make sure any one editing the group is an admin or grant read only access
	"""
	def has_object_permission(self, request, view, obj): 
		return (obj.role == "admin") or (request.method in SAFE_METHODS)
		
		
def has_group_permission(action): 
	
	class BaseGroupPermission(BasePermission): 
		def has_object_permission(self, request, view, obj):
			group_id = request.kwargs.get("pk")
			member = MemberDetail.objects.filter(group_id = group_id, member = request.user)
			return member.role.permissions.filter(action = action).exists()
			
	return BaseGroupPermission