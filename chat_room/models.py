from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from rest_framework.exceptions import PermissionDenied

User = get_user_model()


class ChatRoom(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    is_group = models.BooleanField(default=False)
    members = models.ManyToManyField(User, through="MemberDetail", related_name="rooms")
    group = models.OneToOneField(
        "group.Group",
        related_name="chat",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    last_message = models.ForeignKey(
        "message.Message",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_index=True,
    )

    last_room_activity = models.DateTimeField(default=timezone.now, db_index=True)

    @classmethod
    def create_with_members(cls, name):
        if not name.startswith("chat"):
            raise ValueError(
                "create_with_members should only be called for one to one chats"
            )

        users = name.split("-")[1:]
        user1 = User.objects.get(id=users[0])
        if not user1.is_friend_of(users[1]):
            raise PermissionDenied

        room = ChatRoom.objects.create(name=name)
        MemberDetail.objects.create(member_id=users[0], room=room)
        MemberDetail.objects.create(member_id=users[1], room=room)
        return room

    def is_member(self, user_id):
        room = self
        if self.is_group:
            room = self.group
        return room.members.filter(id=user_id).exists()


class MemberDetail(models.Model):
    member = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="room_roles", db_index=True
    )
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, db_index=True)
    last_active_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["member", "room"], name="unique-chat-member"
            )
        ]

        indexes = [
            models.Index(fields=["member", "room"]),
        ]


class CallHistory(models.Model):
    status = models.CharField(max_length=1, choices=[("S", "started"), ("E", "ended")])
    call_type = models.CharField(max_length=1, choices=[("A", "audio"), ("V", "video")])
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    sender = models.ForeignKey(
        User,
        related_name="started_calls",
        on_delete=models.SET_NULL,
        null=True,
        db_index=True,
    )
    joined_users = models.ManyToManyField(User, related_name="call_history")
    declined_users = models.ManyToManyField(User, related_name="declined_calls")

    room = models.ForeignKey(
        "chat_room.ChatRoom",
        related_name="call_history",
        on_delete=models.CASCADE,
        db_index=True,
    )

    class Meta:
        indexes = [models.Index(fields=["room", "created_at"])]

    @classmethod
    def create_call(cls, room: ChatRoom, is_video_call: bool, sender_id: int):
        return cls.objects.create(
            status="S",
            call_type="V" if is_video_call else "A",
            start_time=timezone.now() if room.is_group else None,
            sender_id=sender_id,
            room_id=room.id,
        )

    def start_call(self):
        if not self.start_time:
            self.start_time = timezone.now()
            self.save(update_fields=["start_time"])

    def end_call(self):
        updated_fields = []
        if not self.end_time:
            self.end_time = timezone.now()
            updated_fields.append("end_time")

        if self.status != "E":
            self.status = "E"
            updated_fields.append("status")

        if updated_fields:
            self.save(update_fields=updated_fields)

    def decline_call(self, user_id: int):
        self.declined_users.add(user_id)

    def accept_call(self, user_id: int):
        self.joined_users.add(user_id)
