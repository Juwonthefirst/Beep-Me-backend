from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse
from django.core.files.storage import default_storage
from BeepMe.storage_backend import PrivateStorage
from group.models import Group
from upload.serializers import CreateAttachmentUploadURLSerializer
from upload.utils import generate_attachment_path
from .models import Attachment
from django.contrib.auth import get_user_model

User = get_user_model()


class CreateUploadAttachmentURLView(APIView):
    def get(self, request):
        serializer = CreateAttachmentUploadURLSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        filenames: list[str] = serializer.validated_data.get("filenames")

        filenameToUploadUrlMap: dict[str, str] = {}
        privateStorage = PrivateStorage()
        for filename in filenames:
            filenameToUploadUrlMap[filename] = (
                privateStorage.connection.meta.client.generate_presigned_post(
                    Bucket=privateStorage.bucket_name,
                    Key=generate_attachment_path(filename),
                    ExpiresIn=3600,
                )
            )

        return Response(filenameToUploadUrlMap)
