import asyncio
import json
from base64 import b64encode
from dataclasses import dataclass
from typing import Dict, Iterable, Optional
from uuid import uuid4

from agave.fastapi_support.tasks.sqs_client import SqsClient


def _build_celery_message(
    task_name: str, args_: Iterable, kwargs_: Dict
) -> str:
    task_id = str(uuid4())
    # la definición de esta plantila se encuentra en:
    # docs.celeryproject.org/en/stable/internals/protocol.html#definition
    message = dict(
        properties=dict(
            correlation_id=task_id,
            content_type='application/json',
            content_encoding='utf-8',
            body_encoding='base64',
            delivery_info=dict(exchange='', routing_key='celery'),
        ),
        headers=dict(
            lang='py',
            task=task_name,
            id=task_id,
            root_id=task_id,
            parent_id=None,
            group=None,
        ),
        body=_b64_encode(
            json.dumps(
                (
                    args_,
                    kwargs_,
                    dict(
                        callbacks=None, errbacks=None, chain=None, chord=None
                    ),
                )
            )
        ),
    )
    message['content-encoding'] = 'utf-8'
    message['content-type'] = 'application/json'

    encoded = _b64_encode(json.dumps(message))
    return encoded


def _b64_encode(value: str) -> str:
    encoded = b64encode(bytes(value, 'utf-8'))
    return encoded.decode('utf-8')


@dataclass
class SqsCeleryClient(SqsClient):
    async def send_task(
        self,
        name: str,
        args: Optional[Iterable] = None,
        kwargs: Optional[Dict] = None,
    ) -> None:
        celery_message = _build_celery_message(name, args or (), kwargs or {})
        await super().send_message(celery_message)

    def send_background_task(
        self,
        name: str,
        args: Optional[Iterable] = None,
        kwargs: Optional[Dict] = None,
    ) -> asyncio.Task:
        celery_message = _build_celery_message(name, args or (), kwargs or {})
        return super().send_message_async(celery_message)
