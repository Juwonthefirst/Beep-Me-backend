from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission): 
	"""
	permission to make sure any one editing the group is an admin
	"""
	def has_object_permission(self, request, view, obj): 
		pass
		