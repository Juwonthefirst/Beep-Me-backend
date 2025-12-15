from rest_framework import serializers
from chat_room.models import ChatRoom
from user.serializers import RetrieveFriendSerializer
from message.serializers import LastMessageSerializer
from group.serializers import GroupSerializer


class RoomDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = "__all__"


class UserChatRoomSerializer(serializers.ModelSerializer):
    group = GroupSerializer()
    last_message = LastMessageSerializer()
    friend = serializers.SerializerMethodField()
    unread_message_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ChatRoom
        fields = [
            "friend",
            "last_message",
            "id",
            "name",
            "group",
            "is_group",
            "unread_message_count",
            "created_at",
        ]

    def get_friend(self, obj: ChatRoom):
        if obj.is_group:
            return None
        user_id = self.context.get("request").user.id
        other_member = obj.members.exclude(id=user_id).first()
        return RetrieveFriendSerializer(other_member, context=self.context).data
