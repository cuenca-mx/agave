import datetime as dt
from typing import Generator, List

import pytest
import rom
from _pytest.monkeypatch import MonkeyPatch
from chalice.test import Client
from redislite import Redis

from examples.chalicelib.models import Account

from examples.chalicelib.models.models_redis import AccountRedis

from .helpers import accept_json

collection_type = {
    'mongo': Account,
    'redis': AccountRedis,
}


@pytest.fixture
def collection(request):
    return collection_type[request.param]


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


@pytest.fixture(autouse=True)
def flush_redis() -> Generator[None, None, None]:
    yield
    redis_connection = Redis('/tmp/redis.db')
    redis_connection.flushall()


@pytest.fixture
@pytest.mark.parametrize(
    'collection',
    ['mongo', 'redis'],
    indirect=True,
)
def accounts(collection) -> Generator[List[collection], None, None]:
    user_id = 'US123456789'
    accs = [
        collection(
            name='Frida Kahlo',
            user_id=user_id,
            created_at=dt.datetime(2020, 1, 1),
            secret='I was born in Coyoacan, CDMX!',
        ),
        collection(
            name='Sor Juana Inés',
            user_id=user_id,
            created_at=dt.datetime(2020, 2, 1),
            secret='I speak Latin very well',
        ),
        collection(
            name='Leona Vicario',
            user_id=user_id,
            created_at=dt.datetime(2020, 3, 1),
            secret=(
                'my real name is María de la Soledad '
                'Leona Camila Vicario Fernández de San Salvador'
            ),
        ),
        collection(
            name='Remedios Varo',
            user_id='US987654321',
            created_at=dt.datetime(2020, 4, 1),
            secret='Octavio Paz was my friend!',
        ),
    ]

    for acc in accs:
        acc.save()
    yield accs
    for acc in accs:
        acc.delete()


@pytest.fixture
@pytest.mark.parametrize(
    'collection',
    ['mongo', 'redis'],
    indirect=True,
)
def account(accounts: List[collection]) -> Generator[collection, None, None]:
    yield accounts[0]


@pytest.fixture
@pytest.mark.parametrize(
    'collection',
    ['mongo', 'redis'],
    indirect=True,
)
def other_account(accounts: List[collection]) -> Generator[collection, None, None]:
    yield accounts[-1]
