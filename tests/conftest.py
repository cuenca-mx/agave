from typing import Dict, Generator

import pytest
from chalice.test import Client

from agave.models.helpers import uuid_field

from .helpers import accept_json, auth_header


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
def user_creds() -> Generator[Dict, None, None]:
    sk = 'cuenca2020'
    user_id = uuid_field('US')()
    id = 'hjshEIEUw8820'
    yield dict(
        user_id=user_id,
        auth=auth_header(id, sk),
    )
