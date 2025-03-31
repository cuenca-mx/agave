from unittest.mock import AsyncMock

from _pytest.monkeypatch import MonkeyPatch
from fastapi.testclient import TestClient

from agave.core.exc import UnauthorizedError
from examples.fastapi.middlewares.authed import AuthedMiddleware


def test_iam_healthy(fastapi_client: TestClient) -> None:
    resp = fastapi_client.get('/')
    assert resp.status_code == 200
    assert resp.json() == dict(greeting="I'm healthy!!!")


def test_cuenca_error_handler(fastapi_client: TestClient) -> None:
    resp = fastapi_client.get('/raise_cuenca_errors')
    assert resp.status_code == 401
    assert resp.json() == dict(error='you are not lucky enough!', code=101)


def test_fast_agave_error_handler(fastapi_client: TestClient) -> None:
    resp = fastapi_client.get('/raise_fast_agave_errors')
    assert resp.status_code == 401
    assert resp.json() == dict(error='nice try!')


def test_fast_agave_error_handler_from_middleware(
    fastapi_client: TestClient, monkeypatch: MonkeyPatch
) -> None:
    monkeypatch.setattr(
        AuthedMiddleware,
        'authorize',
        AsyncMock(side_effect=UnauthorizedError('come back to the shadows!')),
    )
    resp = fastapi_client.get('/you_shall_not_pass')
    assert resp.status_code == 401
    assert resp.json() == dict(error='come back to the shadows!')


def test_get_ip(fastapi_client: TestClient) -> None:
    resp = fastapi_client.get('/get_ip')
    assert resp.status_code == 200
    assert resp.json() == 'testclient'


def test_get_ip_with_multiple_x_forwarded(fastapi_client: TestClient) -> None:
    resp = fastapi_client.get(
        '/get_ip',
        headers={'X-Forwarded-For': '192.168.1.1,10.0.0.1, 10.0.0.2'},
    )
    assert resp.status_code == 200
    assert resp.json() == '192.168.1.1'


def test_get_ip_with_empty_x_forwarded(fastapi_client: TestClient) -> None:
    resp = fastapi_client.get('/get_ip', headers={'X-Forwarded-For': ''})
    assert resp.status_code == 200
    assert resp.json() == 'testclient'
