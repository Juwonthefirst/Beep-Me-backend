from django.db import models


class Attachment(models.Model):
    path = models.CharField(max_length=240)
    filename = models.CharField(max_length=200)
    mime_type = models.CharField(max_length=160)
    kind = models.CharField(
        choices=[
            ("image", "image"),
            ("video", "video"),
            ("audio", "audio"),
            ("document", "document"),
        ]
    )
    size = models.PositiveIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
