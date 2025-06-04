from rest_framework import serializers
from .models import Group, MemberDetails
from chat_room.models import ChatRoom

class MembersSerializer(serializers.Serializer): 
   member_id = serializers.IntegerField()
   role = serializers.CharField(max_length = 100)
       
class GroupSerializer(serializers.ModelSerializer): 
	members = MembersSerializer(many = True)
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
		
		#makes the first member an admin as the first member is always the creator
		group.add_members(members)
		ChatRoom.objects.create(name = f"group.{group.id}", is_group = True, group = group)
		return group
		
class GroupMemberSerializer(serializers.ModelSerializer): 
   member_id = serializers.ReadOnlyField(source = "member.id")
   member_username = serializers.ReadOnlyField(source = "member.username")
   
   class Meta: 
       model = MemberDetails
       fields = ["role", "joined_at", "member_id", "member_username"]
       extra_kwargs = {
           "joined_at": {
               "read_only": True
           }
       }
       
class GroupMemberChangeSerializer(serializers.Serializer): 
	member_ids = serializers.ListField(child = serializers.IntegerField(min_value = 0), allow_empty = False)