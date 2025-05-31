from django.db import models
import django.contrib.auth import get_user_model


class ChatRoom(models.Model):
	name = models.CharField(max_length = 100, unique = True, db_index = True)
	is_group = models.BooleanField(default = False)
	members = models.ManyToManyField(get_user_model(), related_name = "rooms", on_delete = models.CASCADE, blank = True)
	group = models.OneToOneField(group, related_name = "room", on_delete = models.CASCADE, blank = True)
	
	def create_with_members(name):
		users = name.split(".")[1:]
		room = ChatRoom.objects.create(name)
		room.members.add(**users)
		return room
		