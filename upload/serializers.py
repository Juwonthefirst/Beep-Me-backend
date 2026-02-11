from django.conf import settings
from rest_framework import serializers
from upload.models import Attachment
from BeepMe.storage import private_storage
from upload.utils import generate_attachment_path


class AttachmentSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = [
            "id",
            "filename",
            "url",
            "path",
            "mime_type",
            "kind",
            "size",
            "uploaded_at",
        ]

        extra_kwargs = {
            "kind": {"read_only": True},
            "path": {"read_only": True},
            "uploaded_at": {"read_only": True},
        }

    def create(self, validated_data):
        mime_type: str = validated_data.get("mime_type")
        filename = validated_data.get("filename")
        path = generate_attachment_path(filename)
        if mime_type.startswith(("image", "video", "audio")):
            kind = mime_type.split("/")[0]
        else:
            kind = "document"

        return Attachment.objects.create(
            path=path,
            filename=filename,
            mime_type=mime_type,
            kind=kind,
            size=validated_data.get("size"),
        )

    def get_url(self, obj: Attachment):
        url = private_storage.generate_file_url(obj.path)
        request = self.context.get("request")
        return request.build_absolute_uri(url) if settings.DEBUG else url


class GetUploadURLSerializer(serializers.Serializer):
    owner_id = serializers.IntegerField()
    upload_type = serializers.ChoiceField(choices=["profile_picture", "group_avatar"])
