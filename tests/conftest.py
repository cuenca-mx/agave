import datetime as dt
from typing import Generator, List

import pytest
from chalice.test import Client

from examples.chalicelib.models import Account, Card, File

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
            user_id='US987654321',
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


@pytest.fixture
def files() -> Generator[List[File], None, None]:
    user_id = 'US123456789'
    accs = [
        File(
            name='Frida Kahlo',
            user_id=user_id,
        ),
    ]

    for acc in accs:
        acc.save()
    yield accs
    for acc in accs:
        acc.delete()


@pytest.fixture
def file(files: List[File]) -> Generator[File, None, None]:
    yield files[0]


@pytest.fixture
def cards() -> Generator[List[Card], None, None]:
    user_id = 'US123456789'
    cards = [
        Card(
            number='5434000000000001',
            user_id=user_id,
            created_at=dt.datetime(2020, 1, 1),
        ),
        Card(
            number='5434000000000002',
            user_id=user_id,
            created_at=dt.datetime(2020, 2, 1),
        ),
        Card(
            number='5434000000000003',
            user_id=user_id,
            created_at=dt.datetime(2020, 3, 1),
        ),
        Card(
            number='5434000000000004',
            user_id='US987654321',
            created_at=dt.datetime(2020, 4, 1),
        ),
    ]

    for card in cards:
        card.save()
    yield cards
    for card in cards:
        card.delete()


@pytest.fixture
def card(cards: List[Card]) -> Generator[Card, None, None]:
    yield cards[0]
