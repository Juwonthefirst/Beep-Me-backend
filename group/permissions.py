from rest_framework.permissions import BasePermission, SAFE_METHODS

from group.queries import has_group_permission
from .models import MemberDetail


class IsMember(BasePermission):
    """
    Allow access to only members
    """

    def has_permission(self, request, view):
        group_id = view.kwargs.get("pk")
        return MemberDetail.objects.filter(
            group_id=group_id, member=request.user
        ).exists()


def has_role_permission(action):
    """Checks if user role has permission"""

    class BaseGroupPermission(BasePermission):
        def has_permission(self, request, view):
            group_id = view.kwargs.get("pk")
            if not request.method in SAFE_METHODS:
                return has_group_permission(
                    group_id=group_id, member_id=request.user.id, permission=action
                )

            return IsMember().has_permission(request, view)

    return BaseGroupPermission
