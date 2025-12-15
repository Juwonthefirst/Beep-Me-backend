from rest_framework import serializers
from message.models import Message
from upload.serializers import AttachmentSerializer


class ReplyToMessagesSerializer(serializers.ModelSerializer):
    attachment = AttachmentSerializer()
    sender = serializers.ReadOnlyField(source="sender.username")

    class Meta:
        model = Message
        fields = ["body", "attachment", "sender", "is_deleted"]

    def get_reply_to(self, obj: Message):
        from .serializers import MessagesSerializer

        if obj.reply_to:
            return MessagesSerializer(obj.reply_to, context=self.context).data


class MessagesSerializer(serializers.ModelSerializer):
    attachment = AttachmentSerializer()
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
