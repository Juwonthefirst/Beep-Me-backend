from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.generics import CreateAPIView, DestroyAPIView
from django.core.files.storage import default_storage
from django.core.exceptions import SuspiciousFileOperation
from django.core.files.base import ContentFile
from BeepMe.storage import private_storage
from upload.models import Attachment
from upload.serializers import AttachmentSerializer, GetUploadURLSerializer
from upload.utils import (
    generate_group_avatar_url,
    generate_profile_picture_url,
)
from django.contrib.auth import get_user_model

User = get_user_model()
bad_request = status.HTTP_400_BAD_REQUEST


class CreateAttachmentView(CreateAPIView):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 201 and isinstance(response.data, dict):
            url = private_storage.generate_upload_url(response.data["path"])
            response.data["upload_url"] = (
                request.build_absolute_uri(url) if settings.DEBUG else url
            )
        return response


class DeleteAttachmentView(DestroyAPIView):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer


# class GetUploadURLView(APIView):
#     def get(self, request):
#         serializer = GetUploadURLSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=bad_request)

#         upload_type = serializer.validated_data.get("upload_type")
#         if upload_type == "profile_picture":
#             key = generate_profile_picture_url()
#         elif upload_type == "group_avatar":
#             key = generate_group_avatar_url()

#         upload_url = public_storage.generate_upload_url(key=key)
#         if upload_url == "failed":
#             return Response({"error": "file upload failed"}, status=bad_request)

#         return Response({"key": key, "upload_url": upload_url})


class DevelopmentUploadView(APIView):
    permission_classes = [AllowAny]

    def put(self, request, key: str):
        try:
            uploaded_file = ContentFile(b"")
            for chunk in request.stream:
                uploaded_file.write(chunk)
            uploaded_file.seek(0)
            default_storage.save(key, uploaded_file)
            return Response({"status": "success"})
        except SuspiciousFileOperation:
            return Response({"error": "Invalid file key"}, status=bad_request)
