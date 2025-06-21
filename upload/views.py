from rest_framework.parser import MultiPartParser
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ProfilePicture
# Create your views here.

class UploadProfilePicture(APIView): 
	parser_classes = [MultiPartParser]
	
	def post(self, request):
		file = request.FILES.get("file")
		profile_picture = ProfilePicture(file = file, uploader = request.user)
		profile_picture.save()
		return Response({"status": "success"})
	