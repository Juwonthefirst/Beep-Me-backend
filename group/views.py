from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from notification import services
from notification.serializers import NotificationSerializer
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    ListCreateAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Group, MemberDetail, Role, GroupPermission
from notification.models import Notification
from .permissions import has_role_permission, IsMember
from .serializers import (
    GroupMemberSerializer,
    GroupSerializer,
    GroupMemberChangeSerializer,
    PermissionSerializer,
    RoleSerializer,
)

User = get_user_model()
bad_request = status.HTTP_400_BAD_REQUEST


class RetrieveUpdateGroupView(RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [
        IsAuthenticated,
        has_role_permission("can update group details"),
    ]


class GroupMembersView(ListAPIView):
    serializer_class = GroupMemberSerializer
    permission_classes = [IsAuthenticated, IsMember]
    search_fields = ["member__username", "role__name"]

    def get_queryset(self):
        group_id = self.kwargs.get("pk")
        return MemberDetail.objects.select_related("role", "member").filter(
            group_id=group_id
        )


class CreateGroupView(CreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class RetrieveGroupMemberView(RetrieveUpdateAPIView):
    serializer_class = GroupMemberSerializer

    lookup_field = "member_id"

    def get_queryset(self):
        group_id = self.kwargs.get("pk")
        return MemberDetail.objects.select_related("role", "member").filter(
            group_id=group_id
        )


class GroupNotificationView(ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, IsMember]

    def get_queryset(self):
        group_id = self.kwargs.get("pk")
        return Notification.objects.filter(group_id=group_id)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated, has_role_permission("can delete member")])
def delete_group_members(request, pk):
    data = GroupMemberChangeSerializer(data=request.data)
    if not data.is_valid():
        return Response(data.errors, status=bad_request)
    try:
        member_ids = data.validated_data.get("member_ids")
        group = Group.objects.get(id=pk)

        group.delete_members(member_ids)
        no_of_people = (
            f"{len(member_ids)} people" if len(member_ids) == 1 else "one person"
        )

        services.send_group_notification(
            group.chat,
            f"{request.user.username} removed {no_of_people}",
            request.user.id,
        )
        return Response({"status": "success"})
    except Group.DoesNotExist:
        return Response({"error": "This group does not exist"}, status=bad_request)
    except ValueError:
        return Response({"error": "user ids should be in a list"}, status=bad_request)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated, has_role_permission("can add member")])
def add_group_members(request, pk):
    data = GroupMemberChangeSerializer(data=request.data)
    if not data.is_valid():
        return Response(data.errors, status=bad_request)
    try:
        member_ids = data.validated_data.get("member_ids")
        group = Group.objects.get(id=pk)

        group.add_members(member_ids)
        no_of_people = (
            f"{len(member_ids)} people" if len(member_ids) == 1 else "one person"
        )

        services.send_group_notification(
            group.chat,
            f"{request.user.username} added {no_of_people}",
            request.user.id,
        )
        return Response({"status": "success"})
    except Group.DoesNotExist:
        return Response({"error": "This group does not exist"}, status=bad_request)
    except ValueError:
        return Response({"error": "user ids should be in a list"}, status=bad_request)
    except IntegrityError:
        return Response(
            {"error": "user_id does not exist or user already a member"},
            status=bad_request,
        )


class RolesView(ListCreateAPIView):
    permission_classes = [
        IsAuthenticated,
        has_role_permission("can create group role"),
    ]
    serializer_class = RoleSerializer
    search_fields = ["name"]

    def get_queryset(self):
        group_id = self.kwargs.get("pk")
        return Role.objects.prefetch_related("permissions").filter(group_id=group_id)


class EditRolesView(RetrieveUpdateDestroyAPIView):
    permission_classes = [
        has_role_permission("can create group role"),
        IsAuthenticated,
    ]
    serializer_class = RoleSerializer
    queryset = Role.objects.prefetch_related("permissions")
    lookup_field = "role_id"

    def delete(self, request):
        return super().delete(request)


class PermissionsView(ListAPIView):
    queryset = GroupPermission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
