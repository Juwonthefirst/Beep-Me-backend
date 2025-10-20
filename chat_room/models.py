from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied
from group.models import Group, MemberDetail as GroupMemberDetail

User = get_user_model()


class ChatRoom(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    is_group = models.BooleanField(default=False)
    members = models.ManyToManyField(
        User, through="MemberDetail", related_name="rooms", blank=True
    )
    group = models.OneToOneField(
        Group, related_name="chat", on_delete=models.CASCADE, blank=True, null=True
    )

    @classmethod
    def create_with_members(cls, name):
        if not name.startswith("chat"):
            raise ValueError(
                "create_with_members should only be called for one to one messages"
            )

        users = name.split("-")[1:]
        user1 = User.objects.get(id=users[0])
        if not user1.is_friend_of(users[1]):
            raise PermissionDenied

        room = ChatRoom.objects.create(name=name)
        MemberDetail.objects.create(member_id=users[0], room=room)
        MemberDetail.objects.create(member_id=users[1], room=room)
        return room

    def get_last_message(self):
        return self.messages.filter().last()

    def is_member(self, user_id):
        room = self
        if self.is_group:
            room = self.group

        return room.members.filter(id=user_id).exists()

    @classmethod
    def get_member_details(cls, member_id):
        if self.is_group:
            return GroupMemberDetail.objects.filter(
                member_id=member_id, group=self.group
            )
        return MemberDetail.objects.filter(id=member_id, room=self)


class MemberDetail(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    last_read_message_at = models.DateTimeField(default=timezone.now())

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["member", "room"], name="unique-group-member"
            )
        ]
