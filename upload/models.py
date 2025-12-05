from django.db import models


class Attachment(models.Model):
    url = models.CharField(max_length=240)
    size = models.PositiveIntegerField(null=True, blank=True)
    content_type = models.CharField(max_length=200)
    uploaded_at = models.DateTimeField(auto_now_add=True)
