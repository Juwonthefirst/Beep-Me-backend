from chat_room.models import ChatRoom
from django.db.models import OuterRef, Count, Q, Subquery, Case, When, F
from django.utils import timezone
from group.models import MemberDetail as GroupMemberDetail
from chat_room.models import MemberDetail as ChatMemberDetail
from user.models import CustomUser
from message.models import Message


def get_user_rooms(user: CustomUser):
    last_message_time_subquery = Subquery(
        Message.objects.filter(room=OuterRef("pk"))
        .order_by("-timestamp", "-id")
        .values("timestamp")[:1]
    )
    return (
        ChatRoom.objects.select_related("group")
        .prefetch_related("members", "messages")
        .filter(members=user)
        .annotate(
            last_message_time=last_message_time_subquery,
            last_read_at=Case(
                When(
                    is_group=True,
                    then=Subquery(
                        GroupMemberDetail.objects.filter(
                            group=OuterRef("group"), member=user
                        ).values("last_active_at")[:1]
                    ),
                ),
                default=Subquery(
                    ChatMemberDetail.objects.filter(
                        room=OuterRef("pk"), member=user
                    ).values("last_active_at")[:1]
                ),
            ),
            unread_message_count=Count(
                "messages", filter=Q(messages__timestamp__gt=F("last_read_at"))
            ),
        )
        .order_by("-last_message_time", "-id")
    )


def get_room_members_id(room: ChatRoom):
    if room.is_group:
        return list(room.group.members.values_list("id", flat=True))
    else:
        room_name = room.name
        return room_name.split("_")[1:]


def update_user_room_last_active_at(is_group: bool, user_id: int, room_id: int):
    if is_group:
        GroupMemberDetail.objects.filter(member_id=user_id, room_id=room_id).update(
            last_active_at=timezone.now()
        )
    else:
        ChatMemberDetail.objects.filter(member_id=user_id, room_id=room_id).update(
            last_active_at=timezone.now()
        )
