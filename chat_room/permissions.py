from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission): 
	"""
	permission to make sure any one editing or viewing room details is a room member
	"""
	def has_object_permission(self, request, view, obj): 
		if obj.is_group: 
			return 
		
		return obj.members.filter(id = request.id).exists()
		