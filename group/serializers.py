from rest_framework import serializers
from .models import Group, MemberDetail, Role, Permission
from chat_room.models import ChatRoom


class MembersSerializer(serializers.Serializer):
    member_id = serializers.IntegerField()
    member_username = serializers.ReadOnlyField(source="member.username")
    member_avatar = serializers.FileField(source="member.profile_picture")
    role = serializers.CharField(max_length=100, required=False)


class GroupSerializer(serializers.ModelSerializer):
    members = MembersSerializer(many=True)

    class Meta:
        model = Group
        fields = "__all__"
        extra_kwargs = {"created_at": {"read_only": True}}

    def create(self, validated_data):
        members = validated_data.pop("members")
        avatar = validated_data.pop("avatar")
        group = Group.objects.create(**validated_data)
        group.avatar = avatar
        group.save(update_fields=["avatar"])
        ChatRoom.objects.create(name=f"group.{group.id}", is_group=True, group=group)
        owner_role = Role.objects.create(name="owner", group=group, is_master=True)
        owner_role.permissions.add(*Permission.objects.all())
        Role.objects.create(name="member", group=group, is_base_role=True)
        group.add_members(members)
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
        model = Permission
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

    def update(self, instance, validated_data):
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
