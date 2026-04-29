import os
import boto3
from .schemas import ImageTask


class AWSClientManager:
    def __init__(self):
        profile = os.getenv("AWS_PROFILE")
        region = os.getenv("AWS_REGION_NAME")

        self.session = (
            boto3.Session(profile_name=profile, region_name=region)
            if profile
            else boto3.Session(region_name=region)
        )
        self.default_bucket = os.getenv("AWS_STORAGE_BUCKET")
        self.default_queue_url = os.getenv("AWS_QUEUE_URL")

        self.s3 = self.session.client("s3")
        self.sqs = self.session.client("sqs")

    def upload_file(self, local_path, s3_key, bucket_name=None):
        target_bucket = bucket_name or self.default_bucket
        if not target_bucket:
            raise ValueError("AWS_STORAGE_BUCKET environment variable not set")
        return self.s3.upload_file(local_path, target_bucket, s3_key)

    def download_file(self, s3_key, local_path, bucket_name=None):
        target_bucket = bucket_name or self.default_bucket
        if not target_bucket:
            raise ValueError("AWS_STORAGE_BUCKET environment variable not set")
        return self.s3.download_file(target_bucket, s3_key, local_path)

    def send_task(self, task: ImageTask, queue_url=None):
        target_queue_url = queue_url or self.default_queue_url
        if not target_queue_url:
            raise ValueError("AWS_QUEUE_URL environment variable not set")
        return self.sqs.send_message(
            QueueUrl=target_queue_url, MessageBody=task.model_dump_json()
        )


aws_client = AWSClientManager()
