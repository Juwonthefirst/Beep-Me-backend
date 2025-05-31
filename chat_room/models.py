from django.db import models
from django.contrib.auth import get_user_model

class ChatRoom(models.Model):
	name = models.CharField(max_length = 100, unique = True, db_index = True)
	is_group = models.BooleanField(default = False)
	members = models.ManyToManyField(get_user_model(), related_name = "rooms", blank = True)
	#group = models.OneToOneField(Group, related_name = "room", on_delete = models.CASCADE, blank = True)
	
	def create_with_members(self, name):
		if not name.startswith("chat"): 
			raise ValueError("create_with_members should only be called for one to one messages")
			
		users = name.split("_")[1:]
		room = ChatRoom.objects.create(name)
		room.members.add(**users)
		return room
		