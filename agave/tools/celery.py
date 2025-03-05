import json
from base64 import b64encode
from typing import Iterable
from uuid import uuid4


def _b64_encode(value: str) -> str:
    encoded = b64encode(bytes(value, 'utf-8'))
    return encoded.decode('utf-8')


def build_celery_message(
    task_name: str, args_: Iterable, kwargs_: dict
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
