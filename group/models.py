from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

def create_member_rows(cls, group, new_member): 
	if isinstance(new_member, dict): 
		return cls(group = group, **new_member)
	return cls(group = group, member_id = new_member)
	
class Permission(models.Model): 
	action = models.CharField(max_length = 200)
	
	
class Group(models.Model): 
	name = models.CharField(max_length = 100)
	description = models.CharField(max_length = 200, blank = True)
	members = models.ManyToManyField(User, related_name = "chat_groups", through="MemberDetail", blank = True)
	avatar = models.CharField(max_length = 300, default = "default")
	created_at = models.DateTimeField(auto_now_add = True)
	
	def get_user_role(self, member):
		return self.memberdetail_set.get(member = member).role
			
	def add_members(self, new_members): 
		return MemberDetail.add(self, new_members)
		
	def update_members_role(self, role, member_ids): 
		return MemberDetail.update_role(self, role, member_ids)
		
	def delete_members(self, member_ids): 
		return MemberDetail.delete(self, member_ids)
		
class Role(models.Model): 
	name = models.CharField(max_length = 200)
	permissions = models.ManyToManyField(Permission)
	group = models.ForeignKey(Group, on_delete = models.CASCADE, related_name = "roles")
	created_at = models.DateTimeField(auto_now_add = True)
	
	
class MemberDetail(models.Model): 
	member = models.ForeignKey(User, on_delete = models.CASCADE)
	group = models.ForeignKey(Group, on_delete = models.CASCADE)
	role = models.ForeignKey(Role, on_delete = models.SET_NULL, null = True)
	joined_at = models.DateTimeField(auto_now_add = True)
	
	class Meta: 
		constraints = [
			models.UniqueConstraint(fields = ["member", "group"], name = "unique-group-member")
		]
		
	@classmethod
	def add(cls, group, new_members):
		if not isinstance(new_members, list): 
			raise ValueError
		
		member_rows = map(lambda new_member: create_member_rows(cls, group, new_member), new_members)
		return cls.objects.bulk_create(member_rows, ignore_conflicts = False)
		
	@classmethod
	def update_role(cls, group, role_id, member_ids): 
		if not isinstance(member_ids, list): 
			raise ValueError
		return cls.objects.filter(group = group, member_id__in = member_ids).update(role_id = role_id)
		
	@classmethod
	def delete(cls, group, member_ids): 
		if not isinstance(member_ids, list): 
			raise ValueError
		return cls.objects.filter(group = group, member_id__in = member_ids).delete()
		
	
