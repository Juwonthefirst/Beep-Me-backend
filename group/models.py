from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied

User = get_user_model()


def create_member_rows(cls, group, new_member):
    if isinstance(new_member, dict):
        return cls(group=group, **new_member)
    return cls(group=group, member_id=new_member)


def generate_group_avatar_url(instance, filename: str):
    extension = filename.split(".")[-1]
    return f"uploads/group-avatar/{instance.pk}.{extension}"


class Permission(models.Model):
    action = models.CharField(max_length=200)


class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True)
    members = models.ManyToManyField(
        User, related_name="chat_groups", through="MemberDetail", blank=True
    )
    avatar = models.ImageField(upload_to=generate_group_avatar_url, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_user_role(self, member_id):
        member = (
            MemberDetail.objects.select_related("role")
            .filter(group_id=self.id, member_id=member_id)
            .first()
        )
        if not member:
            raise PermissionDenied
        return member.role

    def add_members(self, new_members):
        return MemberDetail.add(self, new_members)

    def update_members_role(self, role, member_ids):
        return MemberDetail.update_role(self, role, member_ids)

    def delete_members(self, member_ids):
        return MemberDetail.remove(self, member_ids)


class Role(models.Model):
    name = models.CharField(max_length=200)
    permissions = models.ManyToManyField(Permission)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="roles")
    is_master = models.BooleanField(default=False)
    is_base_role = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # class Meta:
    #     # make there to always be a role with is_master and is_base_role
    #     # there can only one base role
    #     constraints = [models]


class MemberDetail(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    last_active_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["member", "group"], name="unique-group-member"
            )
        ]

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
    def remove(cls, group, member_ids):
        if not isinstance(member_ids, list):
            raise ValueError
        return cls.objects.filter(group=group, member_id__in=member_ids).delete()
