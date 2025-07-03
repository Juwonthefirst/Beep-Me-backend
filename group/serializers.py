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
		member_role = Role.objects.create(name = "member", group = group)
		return group
		
class GroupMemberSerializer(serializers.ModelSerializer): 
   member_id = serializers.ReadOnlyField(source = "member.id")
   member_username = serializers.ReadOnlyField(source = "member.username")
   
   class Meta: 
       model = MemberDetail
       fields = ["role", "joined_at", "member_id", "member_username"]
       extra_kwargs = {
           "joined_at": {
               "read_only": True
           }
       }
       
class GroupMemberChangeSerializer(serializers.Serializer): 
	member_ids = serializers.ListField(child = serializers.IntegerField(min_value = 1), allow_empty = False)

class PermissionSerializer(serializers.ModelSerializer): 
	class Meta: 
		model = Permission
		fields = "__all__"	
		extra_kwargs = {
			"action": {
				"read_only": True
			}
		}
		
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
			role.permissions.add(permission["id"])
			
		return role
		
	def update(self, instance, validated_data): 
		instance.name = validated_data.get("name", instance.name)
		new_permissions = validated_data.get("permissions")
		if new_permissions: 
			instance.permissions.clear()
			for permission in new_permissions:
				instance.permissions.add(permission["id"])
			
		instance.save(updated_fields = ["name", "permissions"])
		return instance
		
class PermissionChangeSerializer(serializers.Serializer): 
	permission_ids = serializers.ListField(child = serializers.IntegerField(min_value = 1), allow_empty = False)
