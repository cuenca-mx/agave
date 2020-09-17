import os
from typing import Dict, Generator, List

import pytest
from chalice import Chalice
from chalice.test import Client
from cuenca_validations.types import CardStatus

from agave.models.helpers import uuid_field
from tests.app import app as demoapp
from tests.chalicelib.model_card import Card

from .helpers import accept_json, auth_header, collection_fixture


@pytest.fixture()
def app() -> Chalice:
    return demoapp


@pytest.fixture()
def client(app) -> Generator[Client, None, None]:

    with Client(app) as client:
        client.http.patch = accept_json(  # type: ignore[assignment]
            client.http.patch
        )

        yield client


@pytest.fixture
def transfer_dict() -> Dict:
    return dict(
        account_number='646180157034181180',
        amount=10000,
        descriptor='mezcal, pulque y tequila',
        recipient_name='Doroteo Arango',
        idempotency_key='some unique key',
    )


@pytest.fixture()
def aws_credentials() -> None:
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'


@pytest.fixture
def user_creds() -> Generator[Dict, None, None]:
    sk = 'cuenca2020'
    user_id = uuid_field('US')()
    id = 'hjshEIEUw8820'
    yield dict(
        user_id=user_id, auth=auth_header(id, sk),
    )


@pytest.fixture
@collection_fixture(Card)
def virtual_cards() -> List[Card]:
    return [
        Card(status=CardStatus.created,),
        Card(status=CardStatus.created,),
    ]


@pytest.fixture
def virtual_card(virtual_cards: List[Card]) -> Card:
    return virtual_cards[0]
