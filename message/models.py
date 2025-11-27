from uuid import uuid4
from django.db import models
from chat_room.models import ChatRoom
from django.contrib.auth import get_user_model
from upload.models import Attachment


class Message(models.Model):
    body = models.TextField()
    uuid = models.UUIDField(default=uuid4)
    attachment = models.OneToOneField(
        Attachment, related_name="message_parent", on_delete=models.CASCADE, null=True
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(
        get_user_model(), related_name="messages", on_delete=models.SET_NULL, null=True
    )
    reply_to = models.ForeignKey(
        "self", on_delete=models.SET_NULL, related_name="replies", null=True
    )
    room = models.ForeignKey(
        ChatRoom, related_name="messages", on_delete=models.CASCADE, db_index=True
    )
    is_deleted = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
