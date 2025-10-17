from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from django.http import FileResponse
from django.core.files.storage import default_storage
from group.models import Group
from .models import Attachment
from django.contrib.auth import get_user_model

User = get_user_model()


class GetProfilePictureView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        file_path = "uploads/profile_picture/0"  # default profile picture
        try:
            user = User.objects.get(id=user_id)
            profile_picture = user.profile_picture
            if profile_picture:
                file = profile_picture.file
            else:
                raise User.DoesNotExist

        except User.DoesNotExist:
            file = default_storage.open(file_path)

        return FileResponse(
            file, as_attachment=False, filename=f"user_{user_id}'s picture"
        )


class GetGroupPictureView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        file_path = "uploads/profile_picture/0"  # default profile picture
        try:
            group = Group.objects.get(id=group_id)
            profile_picture = group.avatar
            if profile_picture:
                file = profile_picture.file
            else:
                raise Group.DoesNotExist

        except Group.DoesNotExist:
            file = default_storage.open(file_path)

        return FileResponse(
            file, as_attachment=False, filename=f"group_{group_id}'s picture"
        )


class GetAttachmentFileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, message_id):
        try:
            attachment = Attachment.objects.get(source_message_id=message_id)
            file = attachment.file
            return FileResponse(
                file, as_attachment=False, filename=f"message_{message_id}'s attachment"
            )
        except Attachment.DoesNotExist:
            return Response({"error": "File not found"}, status=HTTP_400_BAD_REQUEST)
