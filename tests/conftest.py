import datetime as dt
import functools
import json
from typing import Callable, Generator

import pytest
from chalice.test import Client as OriginalChaliceClient
from fastapi.testclient import TestClient as FastAPIClient
from mongoengine import Document

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
