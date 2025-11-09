import boto3
from config.settings import settings

class ObjectStore:
    def __init__(self):
        if not settings.S3_ENDPOINT_URL:
            self.client = None
        else:
            self.client = boto3.client(
                "s3",
                endpoint_url=settings.S3_ENDPOINT_URL,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
            )
        self.bucket = settings.S3_BUCKET_RECORDINGS

    def put(self, key: str, data: bytes, content_type="audio/mpeg"):
        if self.client:
            self.client.put_object(Bucket=self.bucket, Key=key, Body=data, ContentType=content_type)
