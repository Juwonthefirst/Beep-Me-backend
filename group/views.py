from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Group, MemberDetails
from .permissions import IsAdmin

class UpdateGroupView(RetrieveUpdateDestroyAPIView): 
	queryset = Group.objects.all()
	serializer_class = UpdateGroupSerializer
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
			

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def createGroup(request): 
	data = request.data
	if data.name