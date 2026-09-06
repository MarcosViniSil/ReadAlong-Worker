from storage.bucket.bucketProvider import BucketProvider
import boto3
from botocore.client import Config

from storage.bucket.config import Settings


class BucketProviderImpl(BucketProvider):

    def __init__(self, settings: Settings):
        self.bucket = settings.s3_bucket

        self.client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
            config=Config(signature_version="s3v4"),
        )

    async def upload(self, key, file_path, content_type: str | None = None):
        extra_args = {}

        if content_type:
            extra_args["ContentType"] = content_type

        self.client.upload_file(
            Filename=str(file_path),
            Bucket=self.bucket,
            Key=key,
            ExtraArgs=extra_args or None,
        )

    async def download(self, key):
        response = self.client.get_object(Bucket=self.bucket, Key=key)

        return response["Body"].read()

    async def delete(self, key):
        self.client.delete_object(Bucket=self.bucket, Key=key)

    async def exists(self, key):
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except self.client.exceptions.ClientError:
            return False
