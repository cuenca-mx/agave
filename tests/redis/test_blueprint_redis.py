from urllib.parse import urlencode
import pytest
from chalice.test import Client
from mock import MagicMock, patch

from examples.chalicelib.models.models_redis import AccountRedis

QUERY_DELIMITER = (
    'examples.chalicelib.blueprints.authed.AuthedBlueprint.query_delimiter'
)
pytestmark = pytest.mark.usefixtures('client')


def test_create_resource(client: Client) -> None:
    data = dict(name='Doroteo Arango')
    resp = client.http.post('/account_redis', json=data)
    model = AccountRedis.get_by(id=resp.json_body['id'])
    assert resp.status_code == 201
    assert model.dict() == resp.json_body
    model.delete()


def test_create_resource_bad_request(client: Client) -> None:
    data = dict(invalid_field='some value')
    resp = client.http.post('/account_redis', json=data)
    assert resp.status_code == 400


def test_retrieve_resource(client: Client, account: AccountRedis) -> None:
    resp = client.http.get(f'/account_redis/{account.id}')
    assert resp.status_code == 200


@patch(
    QUERY_DELIMITER,
    MagicMock(return_value=dict(user_id='US123456789')),
)
def test_retrieve_resource_user_id_filter_required(
    client: Client, other_account: AccountRedis
) -> None:
    resp = client.http.get(f'/account_redis/{other_account.id}')
    assert resp.status_code == 404


def test_retrieve_resource_not_found(client: Client) -> None:
    resp = client.http.get('/account_redis/unknown_id')
    assert resp.status_code == 404


def test_update_resource_with_invalid_params(client: Client) -> None:
    wrong_params = dict(wrong_param='wrong_value')
    response = client.http.patch(
        '/account_redis/NOT_EXISTS',
        json=wrong_params,
    )
    assert response.status_code == 400


def test_update_resource_that_doesnt_exit(client: Client) -> None:
    resp = client.http.patch(
        '/account_redis/5f9b4d0ff8d7255e3cc3c128',
        json=dict(name='Frida'),
    )
    assert resp.status_code == 404


def test_update_resource(client: Client, account: AccountRedis) -> None:
    resp = client.http.patch(
        f'/account_redis/{account.id}',
        json=dict(name='Maria Felix'),
    )
    account.update()
    assert resp.json_body['name'] == 'Maria Felix'
    assert account.name == 'Maria Felix'
    assert resp.status_code == 200


def test_delete_resource(client: Client, account: AccountRedis) -> None:
    resp = client.http.delete(f'/account_redis/{account.id}')
    account.update()
    assert resp.status_code == 200
    assert resp.json_body['deactivated_at'] is not None
    assert account.deactivated_at is not None


@pytest.mark.usefixtures('accounts')
def test_query_count_resource(client: Client) -> None:
    query_params = dict(count=1, name='Frida Kahlo')
    response = client.http.get(
        f'/account_redis?{urlencode(query_params)}',
    )
    assert response.status_code == 200
    assert response.json_body['count'] == 1
