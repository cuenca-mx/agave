import os
from functools import partial
from typing import Generator

import aiobotocore
import boto3
import pytest
from _pytest.monkeypatch import MonkeyPatch
from aiobotocore.session import AioSession

from agave.tasks import sqs_tasks


@pytest.fixture(scope='session')
def aws_credentials() -> None:
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    boto3.setup_default_session()


@pytest.fixture(scope='session')
def aws_endpoint_urls(
    aws_credentials,
) -> Generator[dict[str, str], None, None]:
    from moto.server import ThreadedMotoServer

    server = ThreadedMotoServer(port=4000)
    server.start()

    endpoints = dict(
        sqs='http://127.0.0.1:4000/',
    )
    yield endpoints

    server.stop()


@pytest.fixture(autouse=True)
def patch_tasks_count(monkeypatch: MonkeyPatch) -> None:
    def one_loop(*_, **__):
        # Para pruebas solo unos cuantos ciclos
        for i in range(5):
            yield i

    monkeypatch.setattr(sqs_tasks, 'count', one_loop)


@pytest.fixture(autouse=True)
def patch_create_client(aws_endpoint_urls, monkeypatch: MonkeyPatch) -> None:
    create_client = AioSession.create_client

    def mock_create_client(*args, **kwargs):
        service_name = next(a for a in args if type(a) is str)
        kwargs['endpoint_url'] = aws_endpoint_urls[service_name]

        return create_client(*args, **kwargs)

    monkeypatch.setattr(AioSession, 'create_client', mock_create_client)


@pytest.fixture
async def sqs_client():
    session = aiobotocore.session.get_session()
    async with session.create_client('sqs', 'us-east-1') as sqs:
        await sqs.create_queue(
            QueueName='core.fifo',
            Attributes={
                'FifoQueue': 'true',
                'ContentBasedDeduplication': 'true',
            },
        )
        resp = await sqs.get_queue_url(QueueName='core.fifo')
        sqs.send_message = partial(sqs.send_message, QueueUrl=resp['QueueUrl'])
        sqs.receive_message = partial(
            sqs.receive_message,
            QueueUrl=resp['QueueUrl'],
            AttributeNames=['ApproximateReceiveCount'],
        )
        sqs.queue_url = resp['QueueUrl']
        yield sqs
        await sqs.purge_queue(QueueUrl=resp['QueueUrl'])
