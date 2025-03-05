import datetime as dt
import functools
import json
import os
from functools import partial
from typing import Callable, Generator

import aiobotocore
import boto3
import pytest
from _pytest.monkeypatch import MonkeyPatch
from aiobotocore.session import AioSession
from chalice.test import Client as OriginalChaliceClient
from fastapi.testclient import TestClient as FastAPIClient
from mongoengine import Document
from typing_extensions import deprecated

from agave.tasks import sqs_tasks
from examples.config import (
    TEST_DEFAULT_PLATFORM_ID,
    TEST_DEFAULT_USER_ID,
    TEST_SECOND_PLATFORM_ID,
    TEST_SECOND_USER_ID,
)
from examples.models import Account, Biller, Card, File, User

FuncDecorator = Callable[..., Generator]


def collection_fixture(model: Document) -> Callable[..., FuncDecorator]:
    def collection_decorator(func: Callable) -> FuncDecorator:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Generator[list, None, None]:
            items = func(*args, **kwargs)
            for item in items:
                item.save()
            yield items
            model.objects.delete()

        return wrapper

    return collection_decorator


@pytest.fixture
@collection_fixture(Account)
def accounts() -> list[Account]:
    return [
        Account(
            name='Frida Kahlo',
            user_id=TEST_DEFAULT_USER_ID,
            platform_id=TEST_DEFAULT_PLATFORM_ID,
            created_at=dt.datetime(2020, 1, 1, 0),
        ),
        Account(
            name='Sor Juana Inés',
            user_id=TEST_DEFAULT_USER_ID,
            platform_id=TEST_DEFAULT_PLATFORM_ID,
            created_at=dt.datetime(2020, 2, 1, 0),
        ),
        Account(
            name='Eulalia Guzmán',
            user_id='US222222',
            platform_id=TEST_DEFAULT_PLATFORM_ID,
            created_at=dt.datetime(2020, 2, 1, 1),
        ),
        Account(
            name='Matilde Montoya',
            user_id='US222222',
            platform_id=TEST_DEFAULT_PLATFORM_ID,
            created_at=dt.datetime(2020, 2, 1, 2),
        ),
        Account(
            name='Leona Vicario',
            user_id=TEST_DEFAULT_USER_ID,
            platform_id=TEST_DEFAULT_PLATFORM_ID,
            created_at=dt.datetime(2020, 3, 1, 0),
        ),
        Account(
            name='Remedios Varo',
            user_id=TEST_SECOND_USER_ID,
            platform_id=TEST_SECOND_PLATFORM_ID,
            created_at=dt.datetime(2020, 4, 1, 0),
        ),
    ]


@pytest.fixture
def account(accounts: list[Account]) -> Generator[Account, None, None]:
    yield accounts[0]


@pytest.fixture
def user(users: list[User]) -> Generator[User, None, None]:
    yield users[0]


@pytest.fixture
def other_account(accounts: list[Account]) -> Generator[Account, None, None]:
    yield accounts[-1]


@pytest.fixture
@collection_fixture(File)
def files() -> list[File]:
    return [
        File(
            name='Frida Kahlo',
            user_id=TEST_DEFAULT_USER_ID,
        ),
    ]


@pytest.fixture
def file(files: list[File]) -> Generator[File, None, None]:
    yield files[0]


@pytest.fixture
@collection_fixture(Card)
def cards() -> list[Card]:
    return [
        Card(
            number='5434000000000001',
            user_id=TEST_DEFAULT_USER_ID,
            created_at=dt.datetime(2020, 1, 1),
        ),
        Card(
            number='5434000000000002',
            user_id=TEST_DEFAULT_USER_ID,
            created_at=dt.datetime(2020, 2, 1),
        ),
        Card(
            number='5434000000000003',
            user_id=TEST_DEFAULT_USER_ID,
            created_at=dt.datetime(2020, 3, 1),
        ),
        Card(
            number='5434000000000004',
            user_id=TEST_SECOND_USER_ID,
            created_at=dt.datetime(2020, 4, 1),
        ),
    ]


@pytest.fixture
def card(cards: list[Card]) -> Generator[Card, None, None]:
    yield cards[0]


@pytest.fixture
@collection_fixture(User)
def users() -> list[User]:
    return [
        User(name='User1', platform_id=TEST_DEFAULT_PLATFORM_ID),
        User(name='User2', platform_id=TEST_SECOND_PLATFORM_ID),
    ]


@pytest.fixture
@collection_fixture(Biller)
def billers() -> list[Biller]:
    return [
        Biller(name='Telcel'),
        Biller(name='ATT'),
    ]


@pytest.fixture
def fastapi_client() -> Generator[FastAPIClient, None, None]:
    from examples.fastapi.app import app

    client = FastAPIClient(app)
    yield client


class ChaliceResponse:
    def __init__(self, chalice_response):
        self._response = chalice_response
        self._json_body = chalice_response.json_body
        self._status_code = chalice_response.status_code
        self._headers = chalice_response.headers

    def json(self):
        return self._json_body

    @property
    def status_code(self):
        return self._status_code

    @property
    def headers(self):
        return self._headers


class ChaliceClient(OriginalChaliceClient):
    def _request_with_json(
        self, method: str, url: str, **kwargs
    ) -> ChaliceResponse:
        body = json.dumps(kwargs.pop('json')) if 'json' in kwargs else None
        headers = {'Content-Type': 'application/json'}
        response = getattr(self.http, method)(
            url, body=body, headers=headers, **kwargs
        )
        return ChaliceResponse(response)

    def post(self, url: str, **kwargs) -> ChaliceResponse:
        return self._request_with_json('post', url, **kwargs)

    def get(self, url: str, **kwargs) -> ChaliceResponse:
        response = self.http.get(url, **kwargs)
        return ChaliceResponse(response)

    def patch(self, url: str, **kwargs) -> ChaliceResponse:
        return self._request_with_json('patch', url, **kwargs)

    def delete(self, url: str, **kwargs) -> ChaliceResponse:
        return self._request_with_json('delete', url, **kwargs)


@pytest.fixture()
def chalice_client() -> Generator[ChaliceClient, None, None]:
    from examples.chalice import app

    client = ChaliceClient(app)
    yield client


@deprecated('Use fixtures from cuenca-test-fixtures')
@pytest.fixture(scope='session')
def aws_credentials() -> None:
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    boto3.setup_default_session()


@deprecated('Use fixtures from cuenca-test-fixtures')
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


@deprecated('Use fixtures from cuenca-test-fixtures')
@pytest.fixture(autouse=True)
def patch_aiobotocore_create_client(
    aws_endpoint_urls, monkeypatch: MonkeyPatch
) -> None:
    create_client = AioSession.create_client

    def mock_create_client(*args, **kwargs):
        service_name = next(a for a in args if type(a) is str)
        kwargs['endpoint_url'] = aws_endpoint_urls[service_name]

        return create_client(*args, **kwargs)

    monkeypatch.setattr(AioSession, 'create_client', mock_create_client)


@deprecated('Use fixtures from cuenca-test-fixtures')
@pytest.fixture(autouse=True)
def patch_boto3_create_client(
    aws_endpoint_urls, monkeypatch: MonkeyPatch
) -> None:
    create_client = boto3.Session.client

    def mock_client(*args, **kwargs):
        service_name = next(a for a in args if type(a) is str)
        if service_name in aws_endpoint_urls:
            kwargs['endpoint_url'] = aws_endpoint_urls[service_name]
        return create_client(*args, **kwargs)

    monkeypatch.setattr(boto3.Session, 'client', mock_client)


@deprecated('Use fixtures from cuenca-test-fixtures')
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
