from django.conf import settings
from rest_framework import serializers

from BeepMe.storage import public_storage
from group.queries import create_member
from group.models import Group, MemberDetail, Role, GroupPermission
from chat_room.models import ChatRoom
from django.db import transaction


class MembersSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField(source="member.id")
    username = serializers.ReadOnlyField(source="member.username")
    avatar = serializers.FileField(source="member.avatar", read_only=True)
    role = serializers.CharField(max_length=100, required=False)


class GroupSerializer(serializers.ModelSerializer):
    room_name = serializers.ReadOnlyField(source="chat.name")
    members = MembersSerializer(many=True, required=False)
    avatar_upload_link = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = [
            "id",
            "name",
            "description",
            "members",
            "room_name",
            "avatar",
            "avatar_upload_link",
            "base_role_permissions",
        ]

        extra_kwargs = {
            "created_at": {"read_only": True},
            "base_role_permissions": {"read_only": True},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")

        if data.get("avatar"):
            data["avatar"] = public_storage.generate_file_url(key=data["avatar"])
            if settings.DEBUG and request:
                data["avatar"] = request.build_absolute_uri(data["avatar"])

        return data

    def get_avatar_upload_link(self, instance: Group):
        if (
            upload_link := public_storage.generate_upload_url(key=instance.avatar)
        ) == "failed":
            return

        if settings.DEBUG and (request := self.context.get("request")):
            return request.build_absolute_uri(upload_link)
        return upload_link

    def create(self, validated_data):
        members = validated_data.pop("members", None)
        with transaction.atomic():
            group = Group.objects.create(**validated_data)
            owner_role = Role.objects.create(name="Owner", group=group)
            owner_role.permissions.add(*GroupPermission.objects.all())
            current_user = self.context.get("request").user
            create_member(group, current_user.id, owner_role)
            if members:
                members_id = [
                    member.get("id")
                    for member in members
                    if member.get("id") != current_user.id
                ]
                group.add_members(members_id)
            ChatRoom.objects.create(
                name=f"group-{group.id}", is_group=True, group=group
            )
        return group


class GroupMemberSerializer(serializers.ModelSerializer):
    member_username = serializers.ReadOnlyField(source="member.username")
    role_name = serializers.ReadOnlyField(source="role.name")

    class Meta:
        model = MemberDetail
        fields = ["role_id", "joined_at", "member_id", "member_username", "role_name"]
        extra_kwargs = {"joined_at": {"read_only": True}}


class GroupMemberChangeSerializer(serializers.Serializer):
    member_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1), allow_empty=False
    )


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupPermission
        fields = "__all__"


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True)

    class Meta:
        model = Role
        fields = "__all__"
        extra_kwargs = {"created_at": {"read_only": True}}

    def create(self, validated_data):
        permissions = validated_data.pop("permissions", [])
        role = Role.objects.create(**validated_data)
        for permission in permissions:
            if len(permission) == 0:
                continue
            role.permissions.add(permission["id"])

        return role

    def update(self, instance: Role, validated_data):
        instance.name = validated_data.get("name", instance.name)
        new_permissions = validated_data.get("permissions", None)
        if new_permissions or new_permissions == []:
            instance.permissions.clear()
            for permission in new_permissions:
                if not permission:
                    continue
                instance.permissions.add(permission["id"])

        instance.save(update_fields=["name"])
        return instance
