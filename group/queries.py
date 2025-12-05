from chat_room.models import MemberDetail
from rest_framework.exceptions import PermissionDenied


def get_group_member(group_id: int, member_id: int):
    return (
        MemberDetail.objects.select_related("role")
        .filter(group_id=group_id, member_id=member_id)
        .first()
    )


def has_group_permission(group_id: int, member_id: int, permission: str):
    member = get_group_member(group_id, member_id)
    if not member:
        raise PermissionDenied

    return member.role.permissions.filters(action=permission).exists()
