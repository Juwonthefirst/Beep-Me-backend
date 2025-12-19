from uuid import uuid4
from django.db import models
from django.contrib.auth import get_user_model


class Message(models.Model):
    body = models.TextField()
    uuid = models.UUIDField(default=uuid4)
    attachment = models.OneToOneField(
        "upload.Attachment",
        related_name="message_parent",
        on_delete=models.CASCADE,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    sender = models.ForeignKey(
        get_user_model(),
        related_name="messages",
        on_delete=models.SET_NULL,
        null=True,
        db_index=True,
    )
    reply_to = models.ForeignKey(
        "self", on_delete=models.SET_NULL, related_name="replies", null=True
    )
    room = models.ForeignKey(
        "chat_room.ChatRoom",
        related_name="messages",
        on_delete=models.CASCADE,
        db_index=True,
    )
    is_deleted = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=["room", "created_at"])]
