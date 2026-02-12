from urllib import request
from rest_framework import serializers
from message.models import Message
from upload.serializers import AttachmentSerializer


class ReplyToMessagesSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True)
    sender = serializers.ReadOnlyField(source="sender.username")

    class Meta:
        model = Message
        fields = ["body", "attachments", "sender", "is_deleted"]


class MessagesSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(
        many=True,
    )
    reply_to = serializers.SerializerMethodField()
    sender_username = serializers.ReadOnlyField(source="sender.username")

    class Meta:
        model = Message
        fields = "__all__"

    def get_reply_to(self, obj: Message):
        if obj.reply_to:
            return ReplyToMessagesSerializer(obj.reply_to, context=self.context).data


class LastMessageSerializer(MessagesSerializer):
    sender_username = serializers.ReadOnlyField(source="sender.username")
