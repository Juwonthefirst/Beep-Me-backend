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
	    Group.objects.
		
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