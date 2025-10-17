from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Group, MemberDetail


class IsMember(BasePermission):
    """
    Allow access to only members
    """

    def has_permission(self, request, view):
        group_id = view.kwargs.get("pk")
        return Group.objects.filter(
            id=group_id, member_id__in=[request.user.id]
        ).exists()


def has_role_permission(action):
    """Checks if user role has permission"""

    class BaseGroupPermission(BasePermission):
        def has_permission(self, request, view):
            group_id = view.kwargs.get("pk")
            member = MemberDetail.objects.filter(group_id=group_id, member=request.user)
            if not request.method in SAFE_METHODS:
                return member.role.permissions.filter(action=action).exists()

            return IsMember().has_permission(request, view)

    return BaseGroupPermission
