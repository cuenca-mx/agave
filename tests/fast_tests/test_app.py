from unittest.mock import AsyncMock

from _pytest.monkeypatch import MonkeyPatch
from fastapi.testclient import TestClient

from agave.fastapi_support.exc import UnauthorizedError
from examples.fastlib.middlewares.authed import AuthedMiddleware


def test_iam_healthy(client: TestClient) -> None:
    resp = client.get('/')
    assert resp.status_code == 200
    assert resp.json() == dict(greeting="I'm healthy!!!")


def test_cuenca_error_handler(client: TestClient) -> None:
    resp = client.get('/raise_cuenca_errors')
    assert resp.status_code == 401
    assert resp.json() == dict(error='you are not lucky enough!', code=101)


def test_fast_agave_error_handler(client: TestClient) -> None:
    resp = client.get('/raise_fast_agave_errors')
    assert resp.status_code == 401
    assert resp.json() == dict(error='nice try!')


def test_fast_agave_error_handler_from_middleware(
    client: TestClient, monkeypatch: MonkeyPatch
) -> None:
    monkeypatch.setattr(
        AuthedMiddleware,
        'authorize',
        AsyncMock(side_effect=UnauthorizedError('come back to the shadows!')),
    )
    resp = client.get('/you_shall_not_pass')
    assert resp.status_code == 401
    assert resp.json() == dict(error='come back to the shadows!')
