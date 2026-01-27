import os
from typing import Literal
from django.conf import settings
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from BeepMe.utils import load_enviroment_variables
from django.core.files.storage import default_storage

load_enviroment_variables()


class DevelopmentStorage:
    def generate_upload_url(self, key: str):
        api_path = "/api/uploads/dev/"
        return os.path.join(api_path, key)

    def generate_file_url(self, key):
        return os.path.join(settings.MEDIA_URL, key)

    def delete_file(self, key):
        default_storage.delete(os.path.join(settings.MEDIA_ROOT, key))


class Storage:
    access_key: str | None = None
    secret_key: str | None = None
    bucket_name: str | None = None
    bucket_type: Literal["private", "public"] = "private"
    endpoint: str | None = None

    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version="s3v4"),
        )

    def generate_upload_url(self, key, expiration_time=1200):
        try:
            return self.client.generate_presigned_url(
                "put_object",
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=expiration_time,
            )
        except Exception as e:
            print(e)
            return "failed"

    def generate_file_url(self, key, expiration_time=300):
        try:
            if self.bucket_type == "private":
                return self.client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket_name, "Key": key},
                    ExpiresIn=expiration_time,
                )
            else:
                seperator = "" if self.endpoint.endswith("/") else "/"
                return self.endpoint + seperator + key
        except Exception as e:
            print(e)
            return "failed"

    def delete_file(self, key):
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=key)
            return "success"
        except ClientError as e:
            print(e.response["Error"]["Message"])
            return "failed"
        except Exception as e:
            print(e)
            return "failed"


class PrivateStorage(Storage):
    access_key = settings.PRIVATE_BUCKET_ACCESS_KEY
    secret_key = settings.PRIVATE_BUCKET_SECRET_KEY
    bucket_name = settings.PRIVATE_BUCKET_NAME
    endpoint = settings.PRIVATE_BUCKET_ENDPOINT_URL
    bucket_type = "private"


class PublicStorage(Storage):
    access_key = settings.PUBLIC_BUCKET_ACCESS_KEY
    secret_key = settings.PUBLIC_BUCKET_SECRET_KEY
    bucket_name = settings.PUBLIC_BUCKET_NAME
    endpoint = settings.PUBLIC_BUCKET_ENDPOINT_URL
    bucket_type = "public"


private_storage = (
    DevelopmentStorage()
    if os.getenv("ENVIROMENT") == "development"
    else PrivateStorage()
)
public_storage = (
    DevelopmentStorage()
    if os.getenv("ENVIROMENT") == "development"
    else PublicStorage()
)
