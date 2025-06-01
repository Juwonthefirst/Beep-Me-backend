from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Group(models.Model): 
	name = models.CharField(max_length = 100)
	description = models.CharField(max_length = 200, blank = True)
	members = models.ManyToManyField(User, related_name = "groups", through="MemberDetails", blank = True)
	avatar = models.CharField(max_length = 300, default = "default")
	created_at = models.DateTimeField(auto_now_add = True)
	
	def user_is_admin(self, user):
		try: 
			return self.memberdetails_set.get(user = user).role == "admin"
		except:
			return False
		
		
class MemberDetails(models.Model): 
	member = models.ForeignKey(User, on_delete = models.CASCADE)
	group = models.ForeignKey(Group, on_delete = models.CASCADE)
	role = models.CharField(max_length = 200, default = "member")
	joined_at = models.DateTimeField(auto_now_add = True)
		