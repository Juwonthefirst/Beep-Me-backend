from rest_framework.parser import MultiPartParser
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import FileResponse
from django.core.files.storage import default_storage
from .models import ProfilePicture

# Create your views here.

class UploadProfilePicture(APIView): 
	parser_classes = [MultiPartParser]
	
	def post(self, request):
		file = request.FILES.get("file")
		profile = ProfilePicture(file = file, uploader = request.user)
		profile.save()
		return Response({"status": "success"})

		
class GetProfilePicture(APIView): 
	permission_classes = [IsAuthenticated]
	
	def get(self, request, pk):
		file_path = "upload/profile/0" #default profile picture 
		try: 
			profile_picture = ProfilePicture.objects.get(uploader_id = pk)
			file = profile_picture.file
		except ProfilePicture.DoesNotExist: 
			file = default_storage.open(file_path)
		return FileResponse(
			file,
			as_attachment = False,
			filename = f"user_{pk}'s picture"
		)
	
class UploadAttachment(APIView): 
	parser_classes = [MultiPartParser]
	
	def post(self, request):
		