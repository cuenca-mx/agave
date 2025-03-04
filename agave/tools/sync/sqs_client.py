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
    _sqs: Boto3SQSClient = field(init=False)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # allow this class to support context manager
        ...

    def start(self):
        session = boto3.Session()
        self._sqs = session.client('sqs', region_name=self.region_name)

    def send_message(
        self,
        data: Union[str, dict],
        message_group_id: Optional[str] = None,
    ) -> None:
        self._sqs.send_message(
            QueueUrl=self.queue_url,
            MessageBody=data if isinstance(data, str) else json.dumps(data),
            MessageGroupId=message_group_id or str(uuid4()),
        )
