from django.db import models


class Attachment(models.Model):
    path = models.CharField(max_length=240)
    upload_status = models.CharField(max_length=60, default="pending")
    size = models.PositiveIntegerField(null=True, blank=True)
    content_type = models.CharField(max_length=200)
    uploaded_at = models.DateTimeField(auto_now_add=True)
