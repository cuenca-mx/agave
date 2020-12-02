import os
import datetime as dt
import time
from typing import Generator, List

import pytest
import rom
from _pytest.monkeypatch import MonkeyPatch
from chalice.test import Client
from redislite import Redis

from examples.chalicelib.models.models_redis import AccountRedis
from tests.helpers import accept_json


@pytest.fixture(scope='session')
def monkeypatchsession(request):
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope='session')
def client(monkeypatchsession) -> Generator[Client, None, None]:

    # Usa un fake redis para no utilizar un servidor de Redis
    redis_connection = Redis('/tmp/redis.db')
    monkeypatchsession.setattr(
        rom.util, 'get_connection', lambda: redis_connection
    )

    # Crea el cliente de Chalice
    from examples import app

    with Client(app) as client:
        client.http.get = accept_json(  # type: ignore[assignment]
            client.http.get
        )
        client.http.post = accept_json(  # type: ignore[assignment]
            client.http.post
        )
        client.http.put = accept_json(  # type: ignore[assignment]
            client.http.put
        )
        client.http.patch = accept_json(  # type: ignore[assignment]
            client.http.patch
        )
        client.http.delete = accept_json(  # type: ignore[assignment]
            client.http.delete
        )

        yield client


@pytest.fixture(autouse=True)
def flush_redis() -> Generator[None, None, None]:
    yield
    redis_connection = Redis('/tmp/redis.db')
    redis_connection.flushall()


@pytest.fixture
def accounts() -> Generator[List[AccountRedis], None, None]:
    user_id = 'US123456789'
    accs = [
        AccountRedis(
            name='Frida Kahlo',
            user_id=user_id,
            created_at=dt.datetime(2020, 1, 1),
            secret='I was born in Coyoacan, CDMX!',
        ),
        AccountRedis(
            name='Sor Juana Inés',
            user_id=user_id,
            created_at=dt.datetime(2020, 2, 1),
            secret='I speak Latin very well',
        ),
        AccountRedis(
            name='Leona Vicario',
            user_id=user_id,
            created_at=dt.datetime(2020, 3, 1),
            secret=(
                'my real name is María de la Soledad '
                'Leona Camila Vicario Fernández de San Salvador'
            ),
        ),
        AccountRedis(
            name='Remedios Varo',
            user_id='US987654321',
            created_at=dt.datetime(2020, 4, 1),
            secret='Octavio Paz was my friend!',
        ),
    ]

    for acc in accs:
        acc.save()
    yield accs


@pytest.fixture
def account(
    accounts: List[AccountRedis],
) -> Generator[AccountRedis, None, None]:
    yield accounts[0]


@pytest.fixture
def other_account(
    accounts: List[AccountRedis],
) -> Generator[AccountRedis, None, None]:
    yield accounts[-1]
