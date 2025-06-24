from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from django.http import FileResponse
from django.core.files.storage import default_storage
from .models import ProfilePicture, Attachment
from .tasks import resize_and_save
# Create your views here.

class UploadProfilePicture(APIView): 
	parser_classes = [MultiPartParser]
	permission_classes = [IsAuthenticated]
	
	def post(self, request):
		file = request.FILES.get("file")
		resize_and_save.delay(file, request.user)
		return Response({"status": "success"})

		
class GetProfilePicture(APIView): 
	permission_classes = [IsAuthenticated]
	
	def get(self, request, user_id):
		file_path = "upload/profile/0" #default profile picture 
		try: 
			profile_picture = ProfilePicture.objects.get(uploader_id = user_id)
			file = profile_picture.file
		except ProfilePicture.DoesNotExist: 
			file = default_storage.open(file_path)
			
		return FileResponse(
			file,
			as_attachment = False,
			filename = f"user_{pk}'s picture"
		)
	
class GetAttachmentFile(APIView): 
	permission_classes = [IsAuthenticated]
	
	def get(self, request, message_id):
		try: 
			attachment = Attachment.objects.get(message_id = message_id)
			file = attachment.file
			return FileResponse(
				file,
				as_attachment = False,
				filename = f"user_{pk}'s picture"
			)
		except Attachment.DoesNotExist: 
			return Response({"error": "File not found"}, status = HTTP_400_BAD_REQUEST)