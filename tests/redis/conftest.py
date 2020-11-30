from typing import Generator

import pytest
import rom
from _pytest.monkeypatch import MonkeyPatch
from chalice.test import Client
from redislite import Redis

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
