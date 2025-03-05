from dataclasses import dataclass
from typing import Iterable, Optional

from ..celery import build_celery_message
from .sqs_client import SqsClient


@dataclass
class SqsCeleryClient(SqsClient):
    def send_task(
        self,
        name: str,
        args: Optional[Iterable] = None,
        kwargs: Optional[dict] = None,
    ) -> None:
        celery_message = build_celery_message(name, args or (), kwargs or {})
        self.send_message(celery_message)
