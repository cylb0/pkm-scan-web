import os
import boto3
from enum import Enum
from typing import Dict, Optional
from .schemas import ImageTask


class ResourceType(str, Enum):
    BUCKETS = "buckets"
    QUEUES = "queues"


class BucketAlias(str, Enum):
    MEDIAS = "medias"


class QueueAlias(str, Enum):
    RAW_IMAGES = "raw_images"


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

        self._resources_map: Dict[ResourceType, Dict[str, Optional[str]]] = {
            ResourceType.BUCKETS: {
                BucketAlias.MEDIAS.value: os.getenv("AWS_STORAGE_BUCKET")
            },
            ResourceType.QUEUES: {
                QueueAlias.RAW_IMAGES.value: os.getenv("AWS_RAW_IMG_QUEUE_URL")
            },
        }

    def _get_resource(self, resource_type: ResourceType, alias: str) -> str:
        alias_str = alias.value if isinstance(alias, Enum) else alias
        value = self._resources_map.get(resource_type, {}).get(alias_str)
        if not value:
            raise ValueError(
                f"Resource configuration for {resource_type}: {alias} is missing."
            )
        return value

    def upload_file(
        self, local_path, s3_key, bucket_alias: BucketAlias = BucketAlias.MEDIAS
    ):
        target_bucket = self._get_resource(ResourceType.BUCKETS, bucket_alias)
        return self.s3.upload_file(local_path, target_bucket, s3_key)

    def download_file(
        self, s3_key, local_path, bucket_alias: BucketAlias = BucketAlias.MEDIAS
    ):
        target_bucket = self._get_resource(ResourceType.BUCKETS, bucket_alias)
        return self.s3.download_file(target_bucket, s3_key, local_path)

    def _send_to_sqs(self, queue_alias: QueueAlias, body: str):
        url = self._get_resource(ResourceType.QUEUES, queue_alias)
        return self.sqs.send_message(QueueUrl=url, MessageBody=body)

    def receive_message(
        self,
        queue_alias: QueueAlias,
        max_messages: int = 1,
        wait_time_seconds: int = 20,
    ):
        url = self._get_resource(ResourceType.QUEUES, queue_alias)
        response = self.sqs.receive_message(
            QueueUrl=url,
            MaxNumberOfMessages=max_messages,
            WaitTimeSeconds=wait_time_seconds,
        )
        return response.get("Messages", [])

    def delete_message(self, receipt_handle: str, queue_alias: QueueAlias):
        url = self._get_resource(ResourceType.QUEUES, queue_alias)
        return self.sqs.delete_message(QueueUrl=url, ReceiptHandle=receipt_handle)

    def trigger_image_processing(self, task: ImageTask):
        return self._send_to_sqs(QueueAlias.RAW_IMAGES, task.model_dump_json())


aws_client = AWSClientManager()
