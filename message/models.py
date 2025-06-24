from django.db import models
from chat_room.models import ChatRoom
from django.contrib.auth import get_user_model


class Message(models.Model): 
	
	body = models.TextField()
	timestamp = models.DateTimeField(auto_now_add = True)
	sender = models.ForeignKey(get_user_model(), related_name = "messages", on_delete = models.SET_NULL, null = True)
	reply_to = models.ForeignKey("self", on_delete = models.SET_NULL, related_name = "replies", null = True)
	room = models.ForeignKey(ChatRoom, related_name = "messages", on_delete = models.CASCADE, db_index = True)
	is_deleted = models.BooleanField(default = False)
	edited = models.BooleanField(default = False)
	sent = models.BooleanField(default = False)
	read = models.BooleanField(default = False)