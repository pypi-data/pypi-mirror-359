from typing import Iterable
from itertools import islice

import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError, BotoCoreError

from petal.src.logger import logger
from petal.src.core.operators.Writer import Writer


class SqsWriter(Writer):
    def __init__(self, operator_id: str, queue_name: str, aws_region: str):
        super().__init__(operator_id)
        self.queue_name = queue_name
        self.sqs_client = self.create_boto_client(aws_region)
        self.queue_url = self.validate_queue_exists(queue_name)

    def create_boto_client(self, aws_region: str) -> BaseClient:
        return boto3.client("sqs", aws_region)

    def validate_queue_exists(self, queue_name: str) -> str:
        """
        Returns the specified SQS queue url if it exists.
        Throws error if not.

        :param sqs_client: boto3 client to access the AWS SDK
        :param queue_name Name of the SQS queue
        :return: True if the queue exists and is writable, False otherwise
        """
        try:
            # Get the queue URL (this checks that it exists)
            response = self.sqs_client.get_queue_url(QueueName=queue_name)
            queue_url = response['QueueUrl']
            if queue_url:
                return queue_url
            else:
                raise ValueError("No queue URL")
        except ClientError as e:
            logger.error(f"ClientError: {e.response['Error']['Message']}")
            raise e
        except BotoCoreError as e:
            logger.error(f"BotoCoreError: {str(e)}")
            raise e

    def send_messages_to_queue(self, messages: Iterable[str], batch_size: int = 10) -> None:
        """
        Sends a list of messages to the specified SQS queue in batches of 10.

        :param batch_size:
        :param messages: List of messages to send
        """
        try:
            # Use iterator to avoid loading everything into memory
            message_iter = iter(messages)
            while True:
                batch = list(islice(message_iter, batch_size))
                if not batch:
                    break

                entries = [
                    {
                        'Id': str(idx),
                        'MessageBody': msg
                    } for idx, msg in enumerate(batch)
                ]

                self.sqs_client.send_message_batch(
                    QueueUrl=self.queue_url,
                    Entries=entries
                )

        except ClientError as e:
            print(f"ClientError while sending messages: {e.response['Error']['Message']}")
        except BotoCoreError as e:
            print(f"BotoCoreError while sending messages: {str(e)}")

    def process(self, data: Iterable[str]) -> None:
        self.send_messages_to_queue(data)


class MockSqsWriter(Writer):
    def __init__(self, operator_id: str, queue_name: str, aws_region: str):
        super().__init__(operator_id)
        self.aws_region = aws_region
        self.queue_url = f"mock_url_for_{queue_name}"
        logger.info(f"Mocking get_queue_url for queue:{queue_name}")

    def process(self, data: Iterable[str]) -> None:
        logger.info(f"Mocking enqueue to {self.queue_url}:")
        for idx, item in enumerate(data):
            clean_itm = item.strip('\n')
            logger.info(f"{idx}) `{clean_itm}`")
