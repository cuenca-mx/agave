from typing import Generator

import pytest
from chalice.test import Client

from .helpers import accept_json

@pytest.fixture()
def client() -> Generator[Client, None, None]:
    from examples.chalice import app

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
