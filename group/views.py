from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from notification.serializers import NotificationSerializer
from rest_framework.generics import (
	ListAPIView,
	CreateAPIView,
	RetrieveUpdateAPIView, 
	RetrieveUpdateDestroyAPIView
)
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Group, MemberDetails
from notification.models import Notification
from .permissions import IsAdminOrReadOnly
from .serializers import (
	GroupMemberSerializer,
	GroupSerializer,
	GroupMemberChangeSerializer
)

User = get_user_model()
bad_request = status.HTTP_400_BAD_REQUEST

class UpdateGroupView(RetrieveUpdateDestroyAPIView): 
	queryset = Group.objects.all()
	serializer_class =  GroupSerializer
	permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

class GroupMembersView(ListAPIView): 
	serializer_class = GroupMemberSerializer
	permission_classes = [IsAuthenticated]
	search_fields = ["member__username", "role"]
	def get_queryset(self): 
		group_id = self.kwargs["pk"]
		try:
			return Group.objects.get(id = group_id).memberdetails_set.all()
		except Group.DoesNotExist:
			return MemberDetails.objects.none()

class CreateGroupView(CreateAPIView): 
	queryset = Group.objects.all()
	serializer_class = GroupSerializer
	permission_classes = [IsAuthenticated]
	
class GroupMemberRoleView(RetrieveUpdateAPIView): 
	serializer_class = GroupMemberSerializer
	permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
	lookup_field = "member_id"
	
	def get_queryset(self): 
		group_id = self.kwargs["pk"]
		try:
			return Group.objects.get(id = group_id).memberdetails_set.all()
		except Group.DoesNotExist:
			return MemberDetails.objects.none()
			
class GroupNotificationView(ListAPIView): 
	serializer_class = NotificationSerializer
	permission_classes = [IsAuthenticated]
	
	def get_queryset(self): 
		group_id = self.kwargs.get("pk")
		try:
			return Group.objects.get(id = group_id).notifications.all()
		except Group.DoesNotExist:
			return Group.objects.none()
			
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def delete_group_members(request, pk):
	data = GroupMemberChangeSerializer(data = request.data)
	if not data.is_valid(): 
		return Response(data.errors, status = bad_request)
	try: 
		member_ids = data.validated_data.get("member_ids")
		group = Group.objects.get(id = pk)
		
		#permission similar to IsAdmin
		if not group.user_is_admin(request.user): 
			raise PermissionDenied
			
		group.delete_members(member_ids)
		return Response({"status": "success"})
	except Group.DoesNotExist:
		return Response({"error": "This group does not exist"}, status = bad_request)
	except ValueError: 
		return Response({"error": "user ids should be in a list"}, status = bad_request)
		
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def add_group_members(request, pk): 
	data = GroupMemberChangeSerializer(data = request.data)
	if not data.is_valid(): 
		return Response(data.errors, status = bad_request)
	try: 
		member_ids = data.validated_data.get("member_ids")
		group = Group.objects.get(id = pk)
		
		#permission similar to IsAdmin
		if not group.user_is_admin(request.user): 
			raise PermissionDenied
			
		group.add_members(member_ids)	
		return Response({"status": "success"})
	except Group.DoesNotExist:
		return Response({"error": "This group does not exist"}, status = bad_request)
	except ValueError: 
		return Response({"error": "user ids should be in a list"}, status = bad_request)
	except IntegrityError: 
		return Response({"error": "user_id does not exist or user already a member"}, status = bad_request)