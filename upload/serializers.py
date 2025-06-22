from rest_framework import serializers
from .models import Attachment

class UploadAttachmentSerializer(serializers.ModelSerializer): 
	class Meta: 
		model = Attachment
		fields = ["file", "source_message", "content_type", "sender", "uploaded_at"]
		extra_kwarga = {
			"uploaded_at": {
				"read_only": True
			}
		}
	