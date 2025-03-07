import json
from dataclasses import dataclass, field
from typing import Optional, Union
from uuid import uuid4

try:
    import boto3
    from types_boto3_sqs import SQSClient as Boto3SQSClient
except ImportError:
    raise ImportError(
        "You must install agave with [sync_aws_tools] option.\n"
        "You can install it with: pip install agave[sync_aws_tools]"
    )


@dataclass
class SqsClient:
    queue_url: str
    region_name: str
    _sqs: Optional[Boto3SQSClient] = field(init=False, default=None)

    def _get_client(self):
        if self._sqs is None:
            self._sqs = boto3.client('sqs', region_name=self.region_name)
        return self._sqs

    def send_message(
        self,
        data: Union[str, dict],
        message_group_id: Optional[str] = None,
        message_deduplication_id: Optional[str] = None,
    ) -> None:
        sqs = self._get_client()
        sqs.send_message(
            QueueUrl=self.queue_url,
            MessageBody=data if isinstance(data, str) else json.dumps(data),
            MessageGroupId=message_group_id or str(uuid4()),
            MessageDeduplicationId=message_deduplication_id or str(uuid4()),
        )
