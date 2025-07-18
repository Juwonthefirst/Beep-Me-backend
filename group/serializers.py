from rest_framework import serializers
from .models import Group, MemberDetail, Role, Permission
from chat_room.models import ChatRoom

class MembersSerializer(serializers.Serializer): 
   member_id = serializers.IntegerField()
   role = serializers.CharField(max_length = 100, required = False)
       
class GroupSerializer(serializers.ModelSerializer): 
	members = MembersSerializer(many = True, write_only = True)
	class Meta: 
		model = Group
		fields = "__all__"
		extra_kwargs = {
		    "created_at": {
		        "read_only": True
		    }
		}
		
	def create(self, validated_data):
		members = validated_data.pop("members")
		group = Group.objects.create(**validated_data)
		group.add_members(members)
		ChatRoom.objects.create(name = f"group.{group.id}", is_group = True, group = group)
		owner_role = Role.objects.create(name = "owner", group = group)
		owner_role.permissions.add(*Permission.objects.all())
		member_role = Role.objects.create(name = "member", group = group)
		return group
		
class GroupMemberSerializer(serializers.ModelSerializer): 
   member_username = serializers.ReadOnlyField(source = "member.username")
   role_name = serializers.ReadOnlyField(source = "role.name")
   
   class Meta: 
       model = MemberDetail
       fields = ["role_id", "joined_at", "member_id", "member_username", "role_name"]
       extra_kwargs = {
           "joined_at": {
               "read_only": True
           }
       }
       
class GroupMemberChangeSerializer(serializers.Serializer): 
	member_ids = serializers.ListField(child = serializers.IntegerField(min_value = 1), allow_empty = False)

class PermissionSerializer(serializers.Serializer): 
	id = serializers.IntegerField()
	action = serializers.CharField(max_length = 100, read_only = True)
		
class RoleSerializer(serializers.ModelSerializer): 
	permissions = PermissionSerializer(many = True)
	class Meta: 
		model = Role
		fields = "__all__"
		extra_kwargs = {
		    "created_at": {
		        "read_only": True
		    }
		}
		
	def create(self, validated_data):
		permissions = validated_data.pop("permissions")
		if not isinstance(permissions, list):
			raise ValueError
		role = Role.objects.create(**validated_data)
		for permission in permissions:
			if len(permission) == 0:
				continue
			role.permissions.add(permission["id"])
			
		return role
		
	def update(self, instance, validated_data): 
		instance.name = validated_data.get("name", instance.name)
		new_permissions = validated_data.get("permissions")
		if new_permissions or new_permissions == []:
			instance.permissions.clear()
			for permission in new_permissions:
				if not permission:
					continue
				instance.permissions.add(permission["id"])
			
		instance.save(update_fields = ["name"])
		return instance
		
class PermissionChangeSerializer(serializers.Serializer): 
	permission_ids = serializers.ListField(child = serializers.IntegerField(min_value = 1), allow_empty = False)
