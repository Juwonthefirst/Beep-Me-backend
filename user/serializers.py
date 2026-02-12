from django.conf import settings
from rest_framework import serializers
from asgiref.sync import async_to_sync
from BeepMe.cache import cache
from django.contrib.auth import get_user_model
from BeepMe.storage import public_storage
from BeepMe.utils import (
    build_absolute_uri,
    load_enviroment_variables,
    generate_chat_room_name,
)

load_enviroment_variables()
User = get_user_model()


class ProfilePictureUrlSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")

        if data.get("profile_picture"):
            data["profile_picture"] = public_storage.generate_file_url(
                key=data["profile_picture"]
            )
            if settings.DEBUG:
                data["profile_picture"] = build_absolute_uri(data["profile_picture"])

        return data


class CurrentUserSerializer(ProfilePictureUrlSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "profile_picture"]


class UsersSerializer(ProfilePictureUrlSerializer):
    is_following_me = serializers.BooleanField(read_only=True)
    is_followed_by_me = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "is_following_me",
            "is_followed_by_me",
            "profile_picture",
        ]


# class RetrieveUserSerializer(ProfilePictureUrlSerializer):
#     is_following_me = serializers.BooleanField(read_only=True)
#     is_followed_by_me = serializers.BooleanField(read_only=True)

#     class Meta:
#         model = User
#         fields = [
#             "id",
#             "username",
#             "is_followed_by_me",
#             "is_following_me",
#             "profile_picture",
#         ]


class FriendsSerializer(ProfilePictureUrlSerializer):
    room_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "profile_picture", "room_name"]

    def get_room_name(self, friend):
        request = self.context.get("request")
        if not request:
            return
        user_id = request.user.id
        return generate_chat_room_name(user_id, friend.id)


class RetrieveUserSerializer(ProfilePictureUrlSerializer):
    is_online = serializers.SerializerMethodField()
    is_following_me = serializers.BooleanField(read_only=True)
    is_followed_by_me = serializers.BooleanField(read_only=True)
    room_name = serializers.SerializerMethodField()
    is_friend = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "profile_picture",
            "is_followed_by_me",
            "is_following_me",
            "is_friend",
            "room_name",
            "is_online",
            "profile_picture",
            "last_online",
        ]

    def get_is_friend(self, obj):
        return obj.is_followed_by_me and obj.is_following_me

    def get_room_name(self, obj):
        if not (obj.is_followed_by_me and obj.is_following_me):
            return
        request = self.context.get("request")
        if not request:
            return
        user_id = request.user.id
        return generate_chat_room_name(user_id, obj.id)

    def get_is_online(self, obj):
        return (
            bool(async_to_sync(cache.is_user_online)(obj.id))
            if obj.is_followed_by_me and obj.is_following_me
            else None
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.is_followed_by_me and instance.is_following_me:
            return data

        data["last_online"] = None
        return data


class FriendRequestSerializer(serializers.Serializer):
    friend_id = serializers.IntegerField(min_value=1)
