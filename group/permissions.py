from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
	"""
	permission to make sure any one editing the group is an admin or grant read only access
	"""
	def has_object_permission(self, request, view, obj): 
		return (obj.user_is_admin(request.user)) or (request.method in SAFE_METHODS)