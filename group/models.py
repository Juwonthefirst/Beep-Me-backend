from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

def create_member_rows(cls, member): 
	if isinstance(member, dict): 
		return cls(group = group, **new_member)
	return cls(group = group, member_id = new_member)
	
	
class Group(models.Model): 
	name = models.CharField(max_length = 100)
	description = models.CharField(max_length = 200, blank = True)
	members = models.ManyToManyField(User, related_name = "chat_groups", through="MemberDetails", blank = True)
	avatar = models.CharField(max_length = 300, default = "default")
	created_at = models.DateTimeField(auto_now_add = True)
	
	def user_is_admin(self, user):
		try: 
			return self.memberdetails_set.get(member = user).role == "admin"
		except:
			return False
			
	def add_members(self, new_members): 
		return MemberDetails.add(self, new_members)
		
	def update_members_role(self, role, member_ids): 
		return MemberDetails.update_role(self, role, member_ids)
		
	def delete_members(self, member_ids): 
		return MemberDetails.delete(self, member_ids)
		
		
class MemberDetails(models.Model): 
	member = models.ForeignKey(User, on_delete = models.CASCADE)
	group = models.ForeignKey(Group, on_delete = models.CASCADE)
	role = models.CharField(max_length = 200, default = "member")
	joined_at = models.DateTimeField(auto_now_add = True)
	
	@classmethod
	def add(cls, group, new_members):
		if not isinstance(new_members, list): 
			raise ValueError
		
		member_rows = map(lambda member: create_member_rows(cls, member), members)
		return cls.objects.bulk_create(member_rows)
		
	@classmethod
	def update_role(cls, group, role, member_ids): 
		if not isinstance(member_ids, list): 
			raise ValueError
		return cls.objects.filter(group = group, member_id__in = member_ids).update(role = role)
		
	@classmethod
	def delete(cls, group, member_ids): 
		if not isinstance(member_ids, list): 
			raise ValueError
		return cls.objects.filter(group = group, member_id__in = member_ids).delete()
		
	class Meta: 
		constraints = [
			models.UniqueConstraint(fields = ["member", "group"], name = "unique-group-member")
		]
