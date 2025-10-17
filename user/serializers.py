from rest_framework import serializers
from asgiref.sync import async_to_sync
from BeepMe.cache import cache
from django.contrib.auth import get_user_model

User = get_user_model()


class CurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class UsersSerializer(serializers.ModelSerializer):
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
            "last_online",
        ]


class RetrieveUsersSerializer(serializers.ModelSerializer):
    is_following_me = serializers.BooleanField(read_only=True)
    is_followed_by_me = serializers.BooleanField(read_only=True)
    is_online = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_followed_by_me",
            "is_following_me",
            "is_online",
            "last_online",
        ]
        extra_kwargs = {"id": {"read_only": True}}

    def get_is_online(self, obj):
        return async_to_sync(cache.is_user_online)(obj.id)


class FriendRequestSerializer(serializers.Serializer):
    friend_id = serializers.IntegerField(min_value=1)
    action = serializers.CharField(max_length=30)
