import asyncio
import json
from dataclasses import dataclass, field
from typing import Dict, Optional, Union
from uuid import uuid4

from aiobotocore.session import get_session
from types_aiobotocore_sqs import SQSClient


@dataclass
class SqsClient:
    queue_url: str
    region_name: str
    _sqs: SQSClient = field(init=False)
    _background_tasks: set = field(init=False)

    @property
    def background_tasks(self) -> set:
        return self._background_tasks

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def start(self):
        session = get_session()
        context = session.create_client('sqs', self.region_name)
        self._background_tasks = set()
        self._sqs = await context.__aenter__()

    async def close(self):
        await self._sqs.__aexit__(None, None, None)

    async def send_message(
        self,
        data: Union[str, Dict],
        message_group_id: Optional[str] = None,
    ) -> None:
        await self._sqs.send_message(
            QueueUrl=self.queue_url,
            MessageBody=data if type(data) is str else json.dumps(data),
            MessageGroupId=message_group_id or str(uuid4()),
        )

    def send_message_async(
        self,
        data: Union[str, Dict],
        message_group_id: Optional[str] = None,
    ) -> asyncio.Task:
        task = asyncio.create_task(self.send_message(data, message_group_id))
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)
        return task
