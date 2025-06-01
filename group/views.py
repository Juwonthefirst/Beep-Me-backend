from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import (
	ListAPIView,
	CreateAPIView,
	RetrieveUpdateAPIView, 
	RetrieveUpdateDestroyAPIView
)
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Group, MemberDetails
from .permissions import IsAdmin
from .serializers import (
	UpdateGroupSerializer,
	GroupMembersSerializer,
	CreateGroupSerializer
)

class UpdateGroupView(RetrieveUpdateDestroyAPIView): 
	queryset = Group.objects.all()
	serializer_class =  UpdateGroupSerializer
	permission_classes = [IsAuthenticated, IsAdmin]
	
class GroupMembersView(ListAPIView): 
	serializer_class = GroupMembersSerializer
	permission_classes = [IsAuthenticated]
	def get_queryset(self): 
		group_id = self.kwargs["group_id"]
		try:
			Group.objects.get(id = group_id).members.all()
		except Group.DoesNotExist:
			Group.objects.none()

class CreateGroupView(CreateAPIView): 
	queryset = Group.objects.all()
	serializer_class = CreateGroupSerializer
	permission_classes = [IsAuthenticated]
	
class GroupMemberRoleView(RetrieveUpdateAPIView): 
	queryset = MemberDetails.objects.all()
	serializer_class = GroupMemberSerializer
	permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def deleteGroupMember(request, pk, user_id):
	try: 
		group = Group.objects.get(id = pk)
		#permission similar to IsAdminOrOwner
		if not group.user_is_admin(request.user) and request.user.id != user_id: 
			raise PermissionDenied
			
		group.members.remove(user_id)
		return Response({"status": "user removed"})
	except Group.DoesNotExist:
		return Response({"error": "This group does not exist"}, status = status.HTTP_400_BAD_REQUEST)
		