from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from BeepMe.storage import private_storage, public_storage
from django.core.files.storage import default_storage
from django.core.exceptions import SuspiciousFileOperation
from django.core.files.base import ContentFile
from upload.serializers import (
    CreateAttachmentUploadURLSerializer,
    GetUploadURLSerializer,
)
from upload.utils import (
    generate_attachment_path,
    generate_group_avatar_url,
    generate_profile_picture_url,
)
from django.contrib.auth import get_user_model

User = get_user_model()
bad_request = status.HTTP_400_BAD_REQUEST


class CreateUploadAttachmentURLView(APIView):
    def get(self, request):
        serializer = CreateAttachmentUploadURLSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=bad_request)

        filenames: list[str] = serializer.validated_data.get("filenames")

        filenameToUploadUrlMap: dict[str, str] = {}
        for filename in filenames:
            filenameToUploadUrlMap[filename] = private_storage.generate_upload_url(
                key=generate_attachment_path(filename),
            )

        return Response(filenameToUploadUrlMap)


class GetUploadURLView(APIView):
    def get(self, request):
        serializer = GetUploadURLSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=bad_request)

        upload_type = serializer.validated_data.get("upload_type")
        if upload_type == "profile_picture":
            key = generate_profile_picture_url()
        elif upload_type == "group_avatar":
            key = generate_group_avatar_url()

        upload_url = public_storage.generate_upload_url(key=key)
        if upload_url == "failed":
            return Response({"error": "file upload failed"}, status=bad_request)

        return Response({"key": key, "upload_url": upload_url})


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
