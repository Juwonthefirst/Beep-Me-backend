from rest_framework import serializers
from upload.models import Attachment


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ["id", "url", "content_type"]
        extra_kwargs = {"content_type": {"read_only": True}}


class CreateAttachmentUploadURLSerializer(serializers.Serializer):
    filenames = serializers.ListField(child=serializers.CharField())


class GetUploadURLSerializer(serializers.Serializer):
    owner_id = serializers.IntegerField()
    upload_type = serializers.ChoiceField(choices=["profile_picture", "group_avatar"])
