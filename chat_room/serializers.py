from rest_framework import serializers
from chat_room.models import ChatRoom
from user.serializers import UsersSerializer
from message.serializers import MessagesSerializer
from group.serializers import GroupSerializer
from BeepMe.cache import cache
from asgiref.sync import async_to_sync
from chat_room.tasks import cache_messages
import json


class RoomDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = "__all__"


class UserChatRoomSerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            "parent",
            "last_message",
            "id",
            "name",
            "is_group",
            "unread_message_count",
        ]

    def get_last_message(self, obj):
        last_message_object = obj.get_last_message()
        return MessagesSerializer(last_message_object).data

    def get_parent(self, obj):
        if obj.is_group:
            return GroupSerializer(obj.group).data
        user_id = self.context.get("user_id")
        other_member = obj.members.exclude(id=user_id).first()
        return UsersSerializer(other_member).data


# class ChatRoomAndMessagesSerializer(serializers.ModelSerializer):
# 	parent = serializers.SerializerMethodField()
# 	messages = serializers.SerializerMethodField()
# 	class Meta:
# 		model = ChatRoom
# 		fields = ["parent", "messages", "id", "name", "is_group"]

# 	def get_messages(self, obj):
# 		cached_message = async_to_sync(cache.get_cached_messages)(obj.name)
# 		if cached_message:
# 			return cached_message

# 		queryset = obj.messages.all().order_by("-timestamp")[:50]
# 		serialized_data = MessagesSerializer(queryset, many = True).data
# 		jsonified_data = [json.dumps(message_object) for message_object in serialized_data]
# 		cache_messages.delay(jsonified_data)
# 		return serialized_data

# 	def get_parent(self, obj):
# 		if obj.is_group:
# 			number_of_active_members = len(async_to_sync(cache.get_active_members)(obj.name))
# 			return { **GroupSerializer(obj.group).data, "online_members_count": number_of_active_members }
# 		user_id = self.context.get("user_id")
# 		other_member = obj.members.exclude(id = user_id).first()
# 		is_other_member_online = async_to_sync(cache.is_user_online)(other_member.id)
# 		return { **UsersSerializer(other_member).data, "is_online": is_other_member_online}
