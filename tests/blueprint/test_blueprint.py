import datetime as dt
from typing import List
from urllib.parse import urlencode

import pytest
from chalice.test import Client
from mock import MagicMock, patch

from examples.chalicelib.models import Account, Card, File
from examples.config import (
    TEST_DEFAULT_PLATFORM_ID,
    TEST_DEFAULT_USER_ID,
    TEST_SECOND_PLATFORM_ID,
)

PLATFORM_ID_FILTER_REQUIRED = (
    'examples.chalicelib.blueprints.authed.'
    'AuthedBlueprint.platform_id_filter_required'
)

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


@patch(PLATFORM_ID_FILTER_REQUIRED, MagicMock(return_value=True))
def test_retrieve_resource_platform_id_filter_required(
    client: Client, other_account: Account
) -> None:
    resp = client.http.get(f'/accounts/{other_account.id}')
    assert resp.status_code == 404


@patch(USER_ID_FILTER_REQUIRED, MagicMock(return_value=True))
def test_retrieve_resource_user_id_filter_required(
    client: Client, other_account: Account
) -> None:
    resp = client.http.get(f'/accounts/{other_account.id}')
    assert resp.status_code == 404


@patch(PLATFORM_ID_FILTER_REQUIRED, MagicMock(return_value=True))
@patch(USER_ID_FILTER_REQUIRED, MagicMock(return_value=True))
def test_retrieve_resource_user_id_and_platform_id_filter_required(
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


def test_retrieve_custom_method(client: Client, card: Card) -> None:
    resp = client.http.get(f'/cards/{card.id}')
    assert resp.status_code == 200
    assert resp.json_body['number'] == '*' * 16


def test_update_resource_that_doesnt_exist(client: Client) -> None:
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


def test_delete_resource_not_exists(client: Client) -> None:
    resp = client.http.delete('/accounts/1234')
    assert resp.status_code == 404


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
def test_query_all_resource(client: Client, accounts: List[Account]) -> None:
    accounts = list(reversed(accounts))

    items = []
    page_uri = f'/accounts?{urlencode(dict(page_size=2))}'

    while page_uri:
        resp = client.http.get(page_uri)
        assert resp.status_code == 200
        items.extend(resp.json_body['items'])
        page_uri = resp.json_body['next_page_uri']

    assert len(items) == len(accounts)
    assert all(a.to_dict() == b for a, b in zip(accounts, items))


def test_query_all_filter_active(
    client: Client, account: Account, accounts: List[Account]
) -> None:
    query_params = dict(active=True)
    # Query active items
    resp = client.http.get(f'/accounts?{urlencode(query_params)}')
    assert resp.status_code == 200
    items = resp.json_body['items']
    assert len(items) == len(accounts)
    assert all(item['deactivated_at'] is None for item in items)

    # Deactivate Item
    account.deactivated_at = dt.datetime.utcnow()
    account.save()
    resp = client.http.get(f'/accounts?{urlencode(query_params)}')
    assert resp.status_code == 200
    items = resp.json_body['items']
    assert len(items) == len(accounts) - 1

    # Query deactivated items
    query_params = dict(active=False)
    resp = client.http.get(f'/accounts?{urlencode(query_params)}')
    assert resp.status_code == 200
    items = resp.json_body['items']
    assert len(items) == 1
    assert items[0]['deactivated_at'] is not None


def test_query_all_created_after(
    client: Client, accounts: List[Account]
) -> None:
    created_at = dt.datetime(2020, 2, 1)
    expected_length = len([a for a in accounts if a.created_at > created_at])

    query_params = dict(created_after=created_at.isoformat())
    resp = client.http.get(f'/accounts?{urlencode(query_params)}')

    assert resp.status_code == 200
    assert len(resp.json_body['items']) == expected_length


@patch(PLATFORM_ID_FILTER_REQUIRED, MagicMock(return_value=True))
def test_query_platform_id_filter_required(
    client: Client, accounts: List[Account]
) -> None:
    accounts = list(
        reversed(
            [a for a in accounts if a.platform_id == TEST_DEFAULT_PLATFORM_ID]
        )
    )

    items = []
    page_uri = f'/accounts?{urlencode(dict(page_size=2))}'

    while page_uri:
        resp = client.http.get(page_uri)
        assert resp.status_code == 200
        json_body = resp.json_body
        items.extend(json_body['items'])
        page_uri = json_body['next_page_uri']

    assert len(items) == len(accounts)
    assert all(a.to_dict() == b for a, b in zip(accounts, items))


@patch(USER_ID_FILTER_REQUIRED, MagicMock(return_value=True))
def test_query_user_id_filter_required(
    client: Client, accounts: List[Account]
) -> None:
    accounts = list(
        reversed([a for a in accounts if a.user_id == TEST_DEFAULT_USER_ID])
    )
    items = []
    page_uri = f'/accounts?{urlencode(dict(page_size=2))}'

    while page_uri:
        resp = client.http.get(page_uri)
        assert resp.status_code == 200
        json_body = resp.json_body
        items.extend(json_body['items'])
        page_uri = json_body['next_page_uri']

    assert len(items) == len(accounts)
    assert all(a.to_dict() == b for a, b in zip(accounts, items))


def test_query_resource_with_invalid_params(client: Client) -> None:
    wrong_params = dict(wrong_param='wrong_value')
    response = client.http.get(f'/accounts?{urlencode(wrong_params)}')
    assert response.status_code == 400


@pytest.mark.usefixtures('cards')
def test_query_custom_method(client: Client) -> None:
    query_params = dict(page_size=2)
    resp = client.http.get(f'/cards?{urlencode(query_params)}')
    assert resp.status_code == 200
    assert len(resp.json_body['items']) == 2
    assert all(card['number'] == '*' * 16 for card in resp.json_body['items'])

    resp = client.http.get(resp.json_body['next_page_uri'])
    assert resp.status_code == 200
    assert len(resp.json_body['items']) == 2
    assert all(card['number'] == '*' * 16 for card in resp.json_body['items'])


def test_cannot_create_resource(client: Client) -> None:
    response = client.http.post('/transactions', json=dict())
    assert response.status_code == 405


def test_cannot_update_resource(client: Client) -> None:
    response = client.http.post('/transactions', json=dict())
    assert response.status_code == 405


def test_cannot_delete_resource(client: Client) -> None:
    resp = client.http.delete('/transactions/TR1234')
    assert resp.status_code == 405


def test_download_resource(client: Client, file: File) -> None:
    mimetype = 'application/pdf'
    resp = client.http.get(f'/files/{file.id}', headers={'Accept': mimetype})
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == mimetype


@pytest.mark.usefixtures('users')
def test_filter_no_user_id_query(client: Client) -> None:
    resp = client.http.get(f'/users?platform_id={TEST_DEFAULT_PLATFORM_ID}')
    resp_json = resp.json_body
    assert resp.status_code == 200
    assert len(resp_json['items']) == 1
    user1 = resp_json['items'][0]
    resp = client.http.get(f'/users?platform_id={TEST_SECOND_PLATFORM_ID}')
    resp_json = resp.json_body
    assert resp.status_code == 200
    assert len(resp_json['items']) == 1
    user2 = resp_json['items'][0]
    assert user1['id'] != user2['id']


@pytest.mark.usefixtures('billers')
def test_filter_no_user_id_and_no_platform_id_query(
    client: Client,
) -> None:
    resp = client.http.get('/billers?name=ATT')
    resp_json = resp.json_body
    assert resp.status_code == 200
    assert len(resp_json['items']) == 1
