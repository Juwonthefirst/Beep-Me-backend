from rest_framework.exceptions import PermissionDenied

from group.models import Group, Role, MemberDetail


def get_group_member(group_id: int, member_id: int):
    return (
        MemberDetail.objects.select_related("role")
        .filter(group_id=group_id, member_id=member_id)
        .first()
    )


def get_group_member_role(group_id: int, member_id: int):
    member = get_group_member(group_id, member_id)
    if not member:
        raise PermissionDenied
    return member.role


def has_group_permission(
    *,
    group_id: int | None = None,
    member_id: int | None = None,
    role: Role | None = None,
    permission: str,
):
    if role:
        member_role = role

    elif group_id and member_id:
        member_role = get_group_member_role(group_id, member_id)
    else:
        return False

    return (
        bool(member_role) and member_role.permissions.filter(action=permission).exists()
    )


def create_member(group: Group, member_id: int, role: Role):
    return MemberDetail.objects.create(group=group, member_id=member_id, role=role)
