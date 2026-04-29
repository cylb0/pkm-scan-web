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
        self.s3 = self.session.client("s3")
        self.sqs = self.session.client("sqs")

    def upload_file(self, local_path, bucket, s3_key):
        return self.s3.upload_file(local_path, bucket, s3_key)

    def send_task(self, queue_url, task: ImageTask):
        return self.sqs.send_message(
            QueueUrl=queue_url, MessageBody=task.model_dump_json()
        )


aws_client = AWSClientManager()
