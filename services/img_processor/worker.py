import logging
import sys
from tasks import process_messages
from aws_shared.aws_clients import QueueAlias

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def poll_and_process(max_empty_polls):
    from aws_shared.aws_clients import aws_client

    empty_polls = 0
    logger.info("Polling starts")

    while empty_polls < max_empty_polls:
        messages = aws_client.receive_message(
            QueueAlias.RAW_IMAGES, wait_time_seconds=10
        )

        if not messages:
            empty_polls += 1
            logger.info(f"No messages (empty poll {empty_polls}/{max_empty_polls})")
            continue

        empty_polls = 0
        logger.info(f"Processing {len(messages)} messages")

        process_messages(messages, aws_client)

    logger.info("No messages for a while, stopping worker")


def run():
    logger.info("Starting image lab worker")
    poll_and_process(5)


if __name__ == "__main__":
    run()
