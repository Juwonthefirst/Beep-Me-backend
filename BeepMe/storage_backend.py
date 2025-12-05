from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class PrivateStorage(S3Boto3Storage):
    access_key = settings.PRIVATE_BUCKET_ACCESS_KEY
    secret_key = settings.PRIVATE_BUCKET_SECRET_KEY
    bucket_name = settings.PRIVATE_BUCKET_NAME
    endpoint = settings.PRIVATE_BUCKET_ENDPOINT
    querystring_auth = True
    default_acl = "private"
