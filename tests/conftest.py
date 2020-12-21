import datetime as dt
from typing import Generator, List

import pytest
import rom
from _pytest.monkeypatch import MonkeyPatch
from chalice.test import Client
from redislite import Redis

from examples.chalicelib.models.mongo_models import Account

from .helpers import accept_json


@pytest.fixture
def user_id() -> str:
    return 'US123456789'


@pytest.fixture
def another_user_id() -> str:
    return 'US987654321'


@pytest.fixture(scope='session')
def monkeypatchsession(request):
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(autouse=True)
def setup_redis(monkeypatchsession) -> Generator[None, None, None]:
    # Usa un fake redis para no utilizar un servidor de Redis
    redis_connection = Redis('/tmp/redis.db')
    monkeypatchsession.setattr(
        rom.util, 'get_connection', lambda: redis_connection
    )
    yield


@pytest.fixture(autouse=True)
def flush_redis() -> Generator[None, None, None]:
    yield
    redis_connection = Redis('/tmp/redis.db')
    redis_connection.flushall()


@pytest.fixture()
def client() -> Generator[Client, None, None]:
    from examples import app

    with Client(app) as client:
        client.http.post = accept_json(  # type: ignore[assignment]
            client.http.post
        )
        client.http.patch = accept_json(  # type: ignore[assignment]
            client.http.patch
        )

        client.http.delete = accept_json(  # type: ignore[assignment]
            client.http.delete
        )
        yield client


@pytest.fixture
def accounts(
    user_id: str, another_user_id: str
) -> Generator[List[Account], None, None]:
    user_id = 'US123456789'
    accs = [
        Account(
            name='Frida Kahlo',
            user_id=user_id,
            created_at=dt.datetime(2020, 1, 1),
        ),
        Account(
            name='Sor Juana Inés',
            user_id=user_id,
            created_at=dt.datetime(2020, 2, 1),
        ),
        Account(
            name='Leona Vicario',
            user_id=user_id,
            created_at=dt.datetime(2020, 3, 1),
        ),
        Account(
            name='Remedios Varo',
            user_id=another_user_id,
            created_at=dt.datetime(2020, 4, 1),
        ),
    ]

    for acc in accs:
        acc.save()
    yield accs
    for acc in accs:
        acc.delete()


@pytest.fixture
def account(accounts: List[Account]) -> Generator[Account, None, None]:
    yield accounts[0]


@pytest.fixture
def other_account(accounts: List[Account]) -> Generator[Account, None, None]:
    yield accounts[-1]
