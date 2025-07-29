import boto3
import uuid
import json
from dramcash_lib.config import settings
from dramcash_lib.logger import logger


class AwsQueue:
    def __init__(self):
        self.sqs = boto3.client('sqs')
        self.queue_url = settings.queue_url

    def send_message(self, message: dict):
        
        try:
            # Validate message structure
            if not isinstance(message, dict):
                raise ValueError("Message must be a dictionary.")
            if 'user_id' not in message:
                raise ValueError("Message must contain a 'user_id' field.")
        

            # Send message to SQS queue
            response = self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageGroupId=str(message.get('user_id', str(uuid.uuid4()))),  # Use user_id or generate a UUID
                MessageBody=json.dumps(message),  # Convert message to JSON string
                MessageDeduplicationId=str(uuid.uuid4())  # Generate a unique deduplication ID
            )

            return response['MessageId']
        except Exception as e:
            logger.error(f"Failed to send message to SQS: {e}")
            raise e

Queue = AwsQueue()