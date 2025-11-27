import os
from rest_framework import serializers
from asgiref.sync import async_to_sync
from BeepMe.cache import cache
from django.contrib.auth import get_user_model
from BeepMe.utils import load_enviroment_variables

load_enviroment_variables()
User = get_user_model()


class ProfilePictureUrlSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        if not request or os.getenv("MODE") == "production":
            return data

        if data.get("profile_picture"):
            data["profile_picture"] = request.build_absolute_uri(
                data["profile_picture"]
            )

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
            "email",
            "is_following_me",
            "is_followed_by_me",
            "profile_picture",
        ]


class RetrieveUserSerializer(ProfilePictureUrlSerializer):
    is_following_me = serializers.BooleanField(read_only=True)
    is_followed_by_me = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "is_followed_by_me",
            "is_following_me",
            "profile_picture",
        ]

        extra_kwargs = {"id": {"read_only": True}}


class FriendsSerializer(ProfilePictureUrlSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "profile_picture",
        ]


class RetrieveFriendSerializer(ProfilePictureUrlSerializer):
    is_online = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "is_online",
            "profile_picture",
            "last_online",
        ]
        extra_kwargs = {"id": {"read_only": True}}

    def get_is_online(self, obj):
        return bool(async_to_sync(cache.is_user_online)(obj.id))


class FriendRequestSerializer(serializers.Serializer):
    friend_id = serializers.IntegerField(min_value=1)
