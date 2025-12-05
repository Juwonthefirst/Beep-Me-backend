from chat_room.models import ChatRoom
from django.db.models import OuterRef, Count, Q, Subquery, Case, When, F
from django.utils import timezone
from group.models import MemberDetail as GroupMemberDetail
from chat_room.models import MemberDetail as ChatMemberDetail
from user.models import CustomUser


def get_user_rooms(user: CustomUser):

    return (
        ChatRoom.objects.select_related("group", "last_message")
        .filter(members=user)
        .annotate(
            last_active=Case(
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
                "messages",
                filter=Q(messages__timestamp__gt=F("last_active")),
            ),
        )
    )


def get_room_members_id(room: ChatRoom):
    if room.is_group:
        return list(room.group.members.values_list("id", flat=True))
    else:
        room_name = room.name
        return room_name.split("-")[1:]


def update_user_room_last_active_at(is_group: bool, user_id: int, room_id: int):
    if is_group:
        GroupMemberDetail.objects.filter(member_id=user_id, room_id=room_id).update(
            last_active_at=timezone.now()
        )
    else:
        ChatMemberDetail.objects.filter(member_id=user_id, room_id=room_id).update(
            last_active_at=timezone.now()
        )
