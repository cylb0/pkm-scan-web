import os
import logging
from aws_shared.schemas import ImageTask
from aws_shared.constants import FOLDER_MEDIA, get_s3_img_key
from aws_shared.aws_clients import AWSClientManager
from errors.processing import PokemonCardDetectionError
from processor import crop_card_border

logger = logging.getLogger(__name__)


def process_image(task: ImageTask, client: AWSClientManager):
    """
    Orchestrates the download, processing, and upload of a card image.

    This handler manages local temporary files and coordinates between S3 storage and the CV cropping logic.
    """
    local_raw_path = f"/tmp/{task.card_id}_raw.{task.s3_key.split('.')[-1]}"
    local_processed_path = f"/tmp/{task.card_id}_processed.webp"

    try:
        logger.info(f"Processing image for card {task.card_id}")
        client.download_file(task.s3_key, local_raw_path)

        crop_card_border(local_raw_path, local_processed_path)

        processed_key = get_s3_img_key(
            FOLDER_MEDIA,
            task.expansion,
            task.lang,
            task.card_id,
            "webp",
        )
        client.upload_file(local_processed_path, processed_key)

    except PokemonCardDetectionError as e:
        logger.warning(f"Detection failed for card {task.card_id}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error processing {task.card_id}: {e}")
    finally:
        for path in [local_raw_path, local_processed_path]:
            if os.path.exists(path):
                os.remove(path)


def process_messages(messages, client):
    for msg in messages:
        logger.info(f"Received message: {msg}")
        try:
            task = ImageTask.model_validate_json(msg["Body"])
            logger.info(f"Processing image for card {task.card_id}")
            process_image(task, client)
            client.delete_message(msg["ReceiptHandle"])
            logger.info(f"Image processed and deleted for card {task.card_id}")
        except Exception as e:
            logger.error(f"Failed to process {msg['MessageId']}: {e}")
