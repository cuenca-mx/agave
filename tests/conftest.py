import datetime as dt
from typing import Generator, List

import pytest
from chalice.test import Client

from examples.chalicelib.models import Account

from .helpers import accept_json


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
def accounts() -> Generator[List[Account], None, None]:
    user_id = 'US123456789'
    accs = [
        Account(
            name='Frida Kahlo',
            user_id=user_id,
            created_at=dt.datetime(2020, 1, 1),
            secret='I was born in Coyoacan, CDMX!',
        ),
        Account(
            name='Sor Juana Inés',
            user_id=user_id,
            created_at=dt.datetime(2020, 2, 1),
            secret='I speak Latin very well',
        ),
        Account(
            name='Leona Vicario',
            user_id=user_id,
            created_at=dt.datetime(2020, 3, 1),
            secret=(
                'my real name is María de la Soledad '
                'Leona Camila Vicario Fernández de San Salvador'
            ),
        ),
        Account(
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
def account(accounts: List[Account]) -> Generator[Account, None, None]:
    yield accounts[0]


@pytest.fixture
def other_account(accounts: List[Account]) -> Generator[Account, None, None]:
    yield accounts[-1]
