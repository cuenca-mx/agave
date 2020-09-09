import base64
import os
from typing import Dict, Generator

import pytest
from chalice import Chalice

from agave.models.helpers import uuid_field
from tests.app import app as demoapp


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


def auth_header(username: str, password: str) -> Dict:
    creds = base64.b64encode(f'{username}:{password}'.encode('ascii')).decode(
        'utf-8'
    )
    return {
        'Authorization': f'Basic {creds}',
        'Content-Type': 'application/json',
    }


@pytest.fixture
def user_creds() -> Generator[Dict, None, None]:
    sk = 'cuenca2020'
    user_id = uuid_field('US')()
    id = 'hjshEIEUw8820'
    yield dict(
        user_id=user_id, auth=auth_header(id, sk),
    )
