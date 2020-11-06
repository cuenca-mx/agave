from urllib.parse import urlencode

import pytest
from chalice.test import Client
from mock import MagicMock, patch

from examples.chalicelib.models import Account

USER_ID_FILTER_REQUIRED = (
    'examples.chalicelib.blueprints.authed.'
    'AuthedBlueprint.user_id_filter_required'
)


def test_create_resource(client: Client) -> None:
    data = dict(name='Doroteo Arango')
    resp = client.http.post('/accounts', json=data)
    model = Account.objects.get(id=resp.json_body['id'])
    assert resp.status_code == 201
    assert model.to_dict() == resp.json_body
    model.delete()


def test_create_resource_bad_request(client: Client) -> None:
    data = dict(invalid_field='some value')
    resp = client.http.post('/accounts', json=data)
    assert resp.status_code == 400


def test_retrieve_resource(client: Client, account: Account) -> None:
    resp = client.http.get(f'/accounts/{account.id}')
    assert resp.status_code == 200
    assert resp.json_body == account.to_dict()


@patch(USER_ID_FILTER_REQUIRED, MagicMock(return_value=True))
def test_retrieve_resource_user_id_filter_required(
    client: Client, other_account: Account
) -> None:
    resp = client.http.get(f'/accounts/{other_account.id}')
    assert resp.status_code == 404


def test_retrieve_resource_not_found(client: Client) -> None:
    resp = client.http.get('/accounts/unknown_id')
    assert resp.status_code == 404


def test_update_resource_with_invalid_params(client: Client) -> None:
    wrong_params = dict(wrong_param='wrong_value')
    response = client.http.patch(
        '/accounts/NOT_EXISTS',
        json=wrong_params,
    )
    assert response.status_code == 400


def test_update_resource_that_doesnt_exit(client: Client) -> None:
    resp = client.http.patch(
        '/accounts/5f9b4d0ff8d7255e3cc3c128',
        json=dict(name='Frida'),
    )
    assert resp.status_code == 404


def test_update_resource(client: Client, account: Account) -> None:
    resp = client.http.patch(
        f'/accounts/{account.id}',
        json=dict(name='Maria Felix'),
    )
    account.reload()
    assert resp.json_body['name'] == 'Maria Felix'
    assert account.name == 'Maria Felix'
    assert resp.status_code == 200


def test_delete_resource(client: Client, account: Account) -> None:
    resp = client.http.delete(f'/accounts/{account.id}')
    account.reload()
    assert resp.status_code == 200
    assert resp.json_body['deactivated_at'] is not None
    assert account.deactivated_at is not None


@pytest.mark.usefixtures('accounts')
def test_query_count_resource(client: Client) -> None:
    query_params = dict(count=1, name='Frida Kahlo')
    response = client.http.get(
        f'/accounts?{urlencode(query_params)}',
    )
    assert response.status_code == 200
    assert response.json_body['count'] == 1


@pytest.mark.usefixtures('accounts')
def test_query_all_with_limit(client: Client) -> None:
    limit = 2
    query_params = dict(limit=limit)
    response = client.http.get(f'/accounts?{urlencode(query_params)}')
    assert response.status_code == 200
    assert len(response.json_body['items']) == limit
    assert response.json_body['next_page_uri'] is None


@pytest.mark.usefixtures('accounts')
def test_query_all_resource(client: Client) -> None:
    query_params = dict(page_size=2)
    resp = client.http.get(f'/accounts?{urlencode(query_params)}')
    assert resp.status_code == 200
    assert len(resp.json_body['items']) == 2

    resp = client.http.get(resp.json_body['next_page_uri'])
    assert resp.status_code == 200
    assert len(resp.json_body['items']) == 2


@pytest.mark.usefixtures('accounts')
@patch(USER_ID_FILTER_REQUIRED, MagicMock(return_value=True))
def test_query_user_id_filter_required(client: Client) -> None:
    query_params = dict(page_size=2)
    resp = client.http.get(f'/accounts?{urlencode(query_params)}')
    assert resp.status_code == 200
    assert len(resp.json_body['items']) == 2
    assert all(
        item['user_id'] == 'US123456789' for item in resp.json_body['items']
    )

    resp = client.http.get(resp.json_body['next_page_uri'])
    assert resp.status_code == 200
    assert len(resp.json_body['items']) == 1
    assert all(
        item['user_id'] == 'US123456789' for item in resp.json_body['items']
    )


def test_query_resource_with_invalid_params(client: Client) -> None:
    wrong_params = dict(wrong_param='wrong_value')
    response = client.http.get(f'/accounts?{urlencode(wrong_params)}')
    assert response.status_code == 400


def test_cannot_create_resource(client: Client) -> None:
    response = client.http.post('/transactions', json=dict())
    assert response.status_code == 405


def test_cannot_update_resource(client: Client) -> None:
    response = client.http.post('/transactions', json=dict())
    assert response.status_code == 405


def test_cannot_delete_resource(client: Client) -> None:
    resp = client.http.delete('/transactions/TR1234')
    assert resp.status_code == 405
