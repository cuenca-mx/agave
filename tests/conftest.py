import datetime as dt
import os
from typing import Dict, Generator, List

import pytest
from chalice import Chalice

from agave.models.helpers import uuid_field
from tests.app import app as demoapp
from tests.chalicelib.model_transfer import TransactionStatus, Transfer

from .helpers import auth_header, collection_fixture


@pytest.fixture()
def app() -> Chalice:
    return demoapp


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
@collection_fixture(Transfer)
def transfers(user_creds: Dict) -> List[Transfer]:
    return [
        Transfer(
            created_at=dt.datetime.utcnow() - dt.timedelta(days=1),
            account_number='123456789123456789',
            recipient_name='Frida Kahlo',
            amount=10000,
            descriptor='Transfer Test',
            idempotency_key='key_1',
            status=TransactionStatus.submitted,
        ),
        Transfer(
            created_at=dt.datetime.utcnow() - dt.timedelta(hours=2),
            account_number='123456789123456789',
            recipient_name='Frida Kahlo',
            amount=200000,
            descriptor='Transfer Test',
            idempotency_key='key_2',
            status=TransactionStatus.succeeded,
        ),
    ]


@pytest.fixture
def transfer(transfers: List[Transfer]) -> Generator[Transfer, None, None]:
    yield transfers[0]
