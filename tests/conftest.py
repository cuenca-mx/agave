from typing import Generator, List

import pytest
from chalice.test import Client

from tests.testapp.chalicelib.models import Account

from .helpers import accept_json


@pytest.fixture()
def client() -> Generator[Client, None, None]:
    from .testapp import app

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
def accounts() -> Generator[List[Account], None, None]:
    user_id = 'US123456789'
    accs = [
        Account(name='Frida Kahlo', user_id=user_id),
        Account(name='Sor Juana Inés', user_id=user_id),
        Account(name='Leona Vicario', user_id=user_id),
    ]

    for acc in accs:
        acc.save()
    yield accs
    for acc in accs:
        acc.delete()


@pytest.fixture
def account(accounts: List[Account]) -> Generator[Account, None, None]:
    yield accounts[0]
