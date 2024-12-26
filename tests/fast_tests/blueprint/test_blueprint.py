import datetime as dt
from tempfile import TemporaryFile
from typing import List
from unittest.mock import MagicMock, patch
from urllib.parse import urlencode

import pytest
from fastapi.testclient import TestClient

from examples.config import (
    TEST_DEFAULT_PLATFORM_ID,
    TEST_DEFAULT_USER_ID,
    TEST_SECOND_PLATFORM_ID,
)
from examples.fastlib.models import Account, Card, File
from examples.fastlib.models.users import User

PLATFORM_ID_FILTER_REQUIRED = (
    'examples.fastlib.middlewares.AuthedMiddleware.required_platform_id'
)
USER_ID_FILTER_REQUIRED = (
    'examples.fastlib.middlewares.AuthedMiddleware.required_user_id'
)


def test_create_resource(client: TestClient) -> None:
    data = dict(name='Doroteo Arango')
    resp = client.post('/accounts', json=data)
    json_body = resp.json()
    model = Account.objects.get(id=json_body['id'])
    assert resp.status_code == 201
    assert model.to_dict() == json_body
    model.delete()


def test_create_resource_bad_request(client: TestClient) -> None:
    data = dict(invalid_field='some value')
    resp = client.post('/accounts', json=data)
    assert resp.status_code == 422


def test_retrieve_resource(client: TestClient, account: Account) -> None:
    resp = client.get(f'/accounts/{account.id}')
    assert resp.status_code == 200
    assert resp.json() == account.to_dict()


@patch(PLATFORM_ID_FILTER_REQUIRED, MagicMock(return_value=True))
def test_retrieve_resource_platform_id_filter_required(
    client: TestClient, other_account: Account
) -> None:
    resp = client.get(f'/accounts/{other_account.id}')
    assert resp.status_code == 404


@patch(USER_ID_FILTER_REQUIRED, MagicMock(return_value=True))
def test_retrieve_resource_user_id_filter_required(
    client: TestClient, other_account: Account
) -> None:
    resp = client.get(f'/accounts/{other_account.id}')
    assert resp.status_code == 404


@patch(PLATFORM_ID_FILTER_REQUIRED, MagicMock(return_value=True))
@patch(USER_ID_FILTER_REQUIRED, MagicMock(return_value=True))
def test_retrieve_resource_user_id_and_platform_id_filter_required(
    client: TestClient, other_account: Account
) -> None:
    resp = client.get(f'/accounts/{other_account.id}')
    assert resp.status_code == 404


def test_retrieve_resource_not_found(client: TestClient) -> None:
    resp = client.get('/accounts/unknown_id')
    assert resp.status_code == 404


def test_update_resource_with_invalid_params(client: TestClient) -> None:
    wrong_params = dict(wrong_param='wrong_value')
    response = client.patch(
        '/accounts/NOT_EXISTS',
        json=wrong_params,
    )
    assert response.status_code == 422


def test_retrieve_custom_method(client: TestClient, card: Card) -> None:
    resp = client.get(f'/cards/{card.id}')
    assert resp.status_code == 200
    assert resp.json()['number'] == '*' * 16


def test_update_resource_that_doesnt_exist(client: TestClient) -> None:
    resp = client.patch(
        '/accounts/5f9b4d0ff8d7255e3cc3c128',
        json=dict(name='Frida'),
    )
    assert resp.status_code == 404


def test_update_resource(client: TestClient, account: Account) -> None:
    resp = client.patch(
        f'/accounts/{account.id}',
        json=dict(name='Maria Felix'),
    )
    account.reload()
    assert resp.json()['name'] == 'Maria Felix'
    assert account.name == 'Maria Felix'
    assert resp.status_code == 200


def test_delete_resource(client: TestClient, account: Account) -> None:
    resp = client.delete(f'/accounts/{account.id}')
    account.reload()
    assert resp.status_code == 200
    assert resp.json()['deactivated_at'] is not None
    assert account.deactivated_at is not None


@pytest.mark.usefixtures('accounts')
def test_query_count_resource(client: TestClient) -> None:
    query_params = dict(count=1, name='Frida Kahlo')
    response = client.get(
        f'/accounts?{urlencode(query_params)}',
    )
    assert response.status_code == 200
    assert response.json()['count'] == 1


@pytest.mark.usefixtures('accounts')
def test_query_all_with_limit(client: TestClient) -> None:
    limit = 2
    query_params = dict(limit=limit)
    response = client.get(f'/accounts?{urlencode(query_params)}')
    json_body = response.json()
    assert response.status_code == 200
    assert len(json_body['items']) == limit
    assert json_body['next_page_uri'] is None


def test_query_all_resource(
    client: TestClient, accounts: List[Account]
) -> None:
    accounts = list(reversed(accounts))

    items = []
    page_uri = f'/accounts?{urlencode(dict(page_size=2))}'

    while page_uri:
        resp = client.get(page_uri)
        assert resp.status_code == 200
        json_body = resp.json()
        items.extend(json_body['items'])
        page_uri = json_body['next_page_uri']

    assert len(items) == len(accounts)
    assert all(a.to_dict() == b for a, b in zip(accounts, items))


def test_query_all_created_after(
    client: TestClient, accounts: List[Account]
) -> None:
    created_at = dt.datetime(2020, 2, 1)
    expected_length = len([a for a in accounts if a.created_at > created_at])

    query_params = dict(created_after=created_at.isoformat())
    resp = client.get(f'/accounts?{urlencode(query_params)}')
    json_body = resp.json()

    assert resp.status_code == 200
    assert len(json_body['items']) == expected_length


@patch(PLATFORM_ID_FILTER_REQUIRED, MagicMock(return_value=True))
def test_query_platform_id_filter_required(
    client: TestClient, accounts: List[Account]
) -> None:
    accounts = list(
        reversed(
            [a for a in accounts if a.platform_id == TEST_DEFAULT_PLATFORM_ID]
        )
    )

    items = []
    page_uri = f'/accounts?{urlencode(dict(page_size=2))}'

    while page_uri:
        resp = client.get(page_uri)
        assert resp.status_code == 200
        json_body = resp.json()
        items.extend(json_body['items'])
        page_uri = json_body['next_page_uri']

    assert len(items) == len(accounts)
    assert all(a.to_dict() == b for a, b in zip(accounts, items))


@patch(USER_ID_FILTER_REQUIRED, MagicMock(return_value=True))
def test_query_user_id_filter_required(
    client: TestClient, accounts: List[Account]
) -> None:
    accounts = list(
        reversed([a for a in accounts if a.user_id == TEST_DEFAULT_USER_ID])
    )
    items = []
    page_uri = f'/accounts?{urlencode(dict(page_size=2))}'

    while page_uri:
        resp = client.get(page_uri)
        assert resp.status_code == 200
        json_body = resp.json()
        items.extend(json_body['items'])
        page_uri = json_body['next_page_uri']

    assert len(items) == len(accounts)
    assert all(a.to_dict() == b for a, b in zip(accounts, items))


def test_query_resource_with_invalid_params(client: TestClient) -> None:
    wrong_params = dict(wrong_param='wrong_value')
    response = client.get(f'/accounts?{urlencode(wrong_params)}')
    assert response.status_code == 422


@pytest.mark.usefixtures('cards')
def test_query_custom_method(client: TestClient) -> None:
    query_params = dict(page_size=2)
    resp = client.get(f'/cards?{urlencode(query_params)}')
    json_body = resp.json()
    assert resp.status_code == 200
    assert len(json_body['items']) == 2
    assert all(card['number'] == '*' * 16 for card in json_body['items'])

    resp = client.get(json_body['next_page_uri'])
    json_body = resp.json()
    assert resp.status_code == 200
    assert len(json_body['items']) == 2
    assert all(card['number'] == '*' * 16 for card in json_body['items'])


def test_cannot_query_resource(client: TestClient) -> None:
    query_params = dict(count=1, name='Frida Kahlo')
    response = client.get(
        f'/transactions?{urlencode(query_params)}',
    )
    assert response.status_code == 405


def test_cannot_create_resource(client: TestClient) -> None:
    response = client.post('/billers', json=dict())
    assert response.status_code == 405
    assert response.json() == dict(error='Method Not Allowed')


def test_cannot_update_resource(client: TestClient) -> None:
    response = client.patch('/transactions/123', json=dict())
    assert response.status_code == 405
    assert response.json() == dict(error='Method Not Allowed')


def test_cannot_delete_resource(client: TestClient) -> None:
    resp = client.delete('/transactions/TR1234')
    assert resp.status_code == 405
    assert resp.json() == dict(error='Method Not Allowed')


def test_not_found(client: TestClient) -> None:
    resp = client.get('/non-registered-endpoint')
    assert resp.status_code == 404
    assert resp.json() == dict(error='Not Found')


def test_download_resource(client: TestClient, file: File) -> None:
    mimetype = 'application/pdf'
    resp = client.get(f'/files/{file.id}', headers={'Accept': mimetype})
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == mimetype


@pytest.mark.usefixtures('users')
def test_filter_no_user_id_query(client: TestClient) -> None:
    resp = client.get(f'/users?platform_id={TEST_DEFAULT_PLATFORM_ID}')
    resp_json = resp.json()
    assert resp.status_code == 200
    assert len(resp_json['items']) == 1
    user1 = resp_json['items'][0]
    resp = client.get(f'/users?platform_id={TEST_SECOND_PLATFORM_ID}')
    resp_json = resp.json()
    assert resp.status_code == 200
    assert len(resp_json['items']) == 1
    user2 = resp_json['items'][0]
    assert user1['id'] != user2['id']


def test_update_user_with_ip(client: TestClient, user: User) -> None:
    resp = client.patch(f'/users/{user.id}', json={'name': 'Pedrito Sola'})
    resp_json = resp.json()
    assert resp.status_code == 200
    assert resp_json['ip'] == 'testclient'
    assert resp_json['name'] == 'Pedrito Sola'


@pytest.mark.usefixtures('billers')
def test_filter_no_user_id_and_no_platform_id_query(
    client: TestClient,
) -> None:
    resp = client.get('/billers?name=ATT')
    resp_json = resp.json()
    assert resp.status_code == 200
    assert len(resp_json['items']) == 1


def test_upload_resource(client: TestClient) -> None:
    with TemporaryFile(mode='rb') as f:
        file_body = f.read()
    resp = client.post(
        '/files',
        files=dict(file=(None, file_body), file_name=(None, 'test_file.txt')),
    )
    assert resp.status_code == 201
    json = resp.json()
    assert json['name'] == 'test_file.txt'


def test_upload_resource_with_invalid_form(client: TestClient) -> None:
    wrong_form = dict(another_file=b'Whasaaaaap')
    resp = client.post('/files', files=wrong_form)
    assert resp.status_code == 400
