from django.db import models
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied
from group.models import Group

User = get_user_model()
class ChatRoom(models.Model):
	name = models.CharField(max_length = 100, unique = True, db_index = True)
	is_group = models.BooleanField(default = False)
	members = models.ManyToManyField(User, related_name = "rooms", blank = True)
	group = models.OneToOneField(Group, related_name = "chat_room", on_delete = models.CASCADE, blank = True, null = True)
	
	
	@classmethod
	def create_with_members(cls, name):
		if not name.startswith("chat"): 
			raise ValueError("create_with_members should only be called for one to one messages")
			
		users = name.split("_")[1:]
		if not User.objects.get(id  = users[0]).is_friend(users[1]): 
			raise PermissionDenied
			
		room = ChatRoom.objects.create(name = name)
		room.members.add(*users)
		return room
	
	def get_last_message(self):
		return self.messages.filter().last()