from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model
from group.utils import create_random_color_hex
from upload.utils import generate_group_avatar_url

User = get_user_model()


def create_member_rows(cls, group, new_member_id: int):

    return cls(group=group, member_id=new_member_id)


class GroupPermission(models.Model):
    action = models.CharField(max_length=200)
    code = models.IntegerField(unique=True)


class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True)
    members = models.ManyToManyField(
        User, related_name="chat_groups", through="MemberDetail", blank=True
    )
    avatar = models.CharField(max_length=300, default=generate_group_avatar_url)
    created_at = models.DateTimeField(auto_now_add=True)
    base_role_permissions = models.ManyToManyField(
        GroupPermission, related_name="base_roles"
    )

    def add_members(self, new_members):
        return MemberDetail.add(self, new_members)

    def update_members_role(self, role_id, member_ids):
        return MemberDetail.update_role(self, role_id, member_ids)

    def delete_members(self, member_ids):
        return MemberDetail.remove(self, member_ids)


class Role(models.Model):
    name = models.CharField(max_length=200)
    permissions = models.ManyToManyField(GroupPermission, related_name="roles")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="roles")
    created_at = models.DateTimeField(auto_now_add=True)
    hex_color = models.CharField(max_length=7, default=create_random_color_hex)


class MemberDetail(models.Model):
    member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    last_active_at = models.DateTimeField(default=timezone.now)
    hex_color = models.CharField(max_length=7, default=create_random_color_hex)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["member", "group"], name="unique-group-member"
            )
        ]

        indexes = [models.Index(fields=["member", "group"])]

    @classmethod
    def add(cls, group, new_members):
        if not isinstance(new_members, list):
            raise ValueError

        member_rows = map(
            lambda new_member: create_member_rows(cls, group, new_member), new_members
        )
        return cls.objects.bulk_create(member_rows, ignore_conflicts=False)

    @classmethod
    def update_role(cls, group, role_id, member_ids):
        if not isinstance(member_ids, list):
            raise ValueError
        return cls.objects.filter(group=group, member_id__in=member_ids).update(
            role_id=role_id
        )

    @classmethod
    def remove(cls, group: Group, member_ids: list[int]):
        if not isinstance(member_ids, list):
            raise ValueError
        return cls.objects.filter(group=group, member_id__in=member_ids).delete()
