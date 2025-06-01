from rest_framework.permissions import BasePermission

class IsAdminOrOwner(BasePermission): 
	"""
	permission to make sure any one editing the group is an admin
	"""
	def has_permission(self, request, view, obj): 
		