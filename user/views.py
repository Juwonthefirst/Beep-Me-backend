from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import UsersSerializer, RetrieveUsersSerializer
User = get_user_model()
bad_request = status.HTTP_400_BAD_REQUEST
not_found = status.HTTP_404_NOT_FOUND
class UsersView(ListAPIView):
	"""View to get all user in the database, this meant to be used with filtering and pagination"""
	queryset = User.objects.all()
	permission_classes = [IsAuthenticated]
	serializer_class = UsersSerializer
	
class RetrieveUserView(RetrieveAPIView): 
	"""View to get a particular user in the database """
	queryset = User.objects.all()
	permission_classes = [IsAuthenticated]
	serializer_class = RetrieveUsersSerializer
	
@api_view(["GET"])
def get_user_chat_rooms(request): 
	user_id = request.kwargs.get("pk")
	if not user_id: 
		return Response({"error": "user_id was not provided"}, status = bad_request)
		
	try: 
		user = User.objects.get(id = user_id)
		if not user.is_active: 
			raise User.DoesNotExist
			
	except User.DoesNotExist:
		return Response({"error": "user does not exist"}, status = not_found)
	
	
	