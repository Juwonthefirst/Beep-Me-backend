from rest_framework import serializers
from message.models import Message


class MessagesSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source="sender.username")
    attachment = serializers.FileField(source="attachment.file")
    reply_to = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = "__all__"

    def get_reply_to(self, obj: Message):
        from .serializers import MessagesSerializer

        if obj.reply_to:
            return MessagesSerializer(obj.reply_to, context=self.context).data
