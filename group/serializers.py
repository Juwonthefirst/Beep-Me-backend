from rest_framework import serializers
from .models import Group, MemberDetails
from chat_room.models import ChatRoom


class GroupSerializer(serializers.ModelSerializer): 
	class Meta: 
		model = Group
		fields = "__all__"
		extra_kwargs = {
		    "created_at": {
		        "read_only": True
		    }
		}
	
	def create(self, validated_data): 
		member_ids = validated_data.pop("members")
	    group = Group.objects.create(**validated_data)
	    
	    #makes the first member an admin as the first member is always the creator
	    member_rows = [MemberDetails(group = group, member_id = member_ids[0], role = "admin")]
	    
	    #the rest are regular members unless updated by the admin
		member_rows.extend([MemberDetails(group = group, member_id = member_id) for member_id in member_ids[1:]])
		
		MemberDetails.objects.bulk_create(member_rows)
		ChatRoom.objects.create(name = f"group.{group.id}", is_group = True, group = group)
		return group
		
class GroupMemberSerializer(serializers.ModelSerializer): 
   member_id = serializers.IntegerField(source = "member.username", read_only = True)
   member_username = serializers.CharField(source = "member.id", read_only = True)
   
   class Meta: 
       model = MemberDetails
       fields = ["role", "joined_at", "member_id", "member_username"]
       extra_kwargs = {
           "joined_at": {
               "read_only": True
           }
       }
       
class DeleteGroupMembers(serializers.Serializer): 
	member_ids = serializers.ListField(child = serailizer.IntegerField(min_value = 0), required = True)