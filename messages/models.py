from django.db import models
from django.contrib.auth import get_user_model
from chat_room.models import ChatRoom


class Message(models.Model):
	body = models.TextField()
	timestamp = models.DateTimeField(auto_add_now = True)
	sender = models.ForeignKey(get_user_model(), related_name = "messages", on_delete = models.CASCADE)
	reply_to = models.ForeignKey("self", related_name = "replies", on_delete = models.CASCADE, blank = True)
	room = models.ForeignKey(ChatRoom, related_name = "messages", on_delete = models.CASCADE, db_index = True)
	is_deleted = models.BooleanField(default = False)
	attachment = models.CharField(max_length = 100, blank = True)
	edited = models.BooleanField(default = False)
	sent = models.BooleanField(default = False)
	read = models.BooleanField(default = False)