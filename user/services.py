from chat_room.models import ChatRoom
from django.db.models import Max, OuterRef, Count, Q, Subquery, Case, When, F
from group.models import MemberDetail as GroupMemberDetail
from chat_room.models import MemberDetail as ChatMemberDetail


def get_user_rooms(user):
    return (
        ChatRoom.objects.select_related("group")
        .prefetch_related("members", "messages")
        .filter(members=user)
        .annotate(
            last_message_time=Max("messages__timestamp"),
            last_read_at=Case(
                When(
                    is_group=True,
                    then=Subquery(
                        GroupMemberDetail.objects.filter(
                            group=OuterRef("group"), member=user
                        ).values("last_read_message_at")[:1]
                    ),
                ),
                default=Subquery(
                    ChatMemberDetail.objects.filter(
                        room=OuterRef("pk"), member=user
                    ).values("last_read_message_at")[:1]
                ),
            ),
            unread_message_count=Count(
                "messages", filter=Q(messages__timestamp__gt=F("last_read_at"))
            ),
        )
        .order_by("-last_message_time")
    )
