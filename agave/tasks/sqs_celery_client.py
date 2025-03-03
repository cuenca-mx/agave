import asyncio
from dataclasses import dataclass
from typing import Iterable, Optional

from agave.tasks.sqs_client import SqsClient
from agave.tools.celery import build_celery_message


@dataclass
class SqsCeleryClient(SqsClient):
    async def send_task(
        self,
        name: str,
        args: Optional[Iterable] = None,
        kwargs: Optional[dict] = None,
    ) -> None:
        celery_message = build_celery_message(name, args or (), kwargs or {})
        await super().send_message(celery_message)

    def send_background_task(
        self,
        name: str,
        args: Optional[Iterable] = None,
        kwargs: Optional[dict] = None,
    ) -> asyncio.Task:
        celery_message = build_celery_message(name, args or (), kwargs or {})
        return super().send_message_async(celery_message)
