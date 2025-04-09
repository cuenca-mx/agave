import datetime as dt
from tempfile import TemporaryFile
from unittest.mock import MagicMock, patch
from urllib.parse import urlencode

import pytest
from fastapi.testclient import TestClient

from examples.config import (
    TEST_DEFAULT_API_KEY_ID,
    TEST_DEFAULT_PLATFORM_ID,
    TEST_DEFAULT_USER_ID,
    TEST_SECOND_PLATFORM_ID,
)
from examples.models import Account, Card, File, User

# Constants for both frameworks
FRAMEWORK_CONFIGS = {
    'chalice': {
        'platform_id_filter': (
            'examples.chalice.blueprints.authed.'
            'AuthedBlueprint.platform_id_filter_required'
        ),
        'user_id_filter': (
            'examples.chalice.blueprints.authed.'
            'AuthedBlueprint.user_id_filter_required'
        ),
        'bad_request_code': 400,
        'validation_error_code': 400,
        'method_not_allowed_code': 400,
        'not_found_code': 403,
    },
    'fastapi': {
        'platform_id_filter': (
            'examples.fastapi.middlewares.'
            'AuthedMiddleware.required_platform_id'
        ),
        'user_id_filter': (
            'examples.fastapi.middlewares.AuthedMiddleware.required_user_id'
        ),
        'bad_request_code': 422,
        'validation_error_code': 422,
        'method_not_allowed_code': 405,
        'not_found_code': 404,
    },
}


@pytest.mark.parametrize(
    "client_fixture", ["fastapi_client", "chalice_client"]
)
def test_create_resource(
    client_fixture: str, request: pytest.FixtureRequest
) -> None:
    client = request.getfixturevalue(client_fixture)
    data = dict(name='Doroteo Arango')
    resp = client.post("/accounts", json=data)
    json_body = resp.json()
    status_code = resp.status_code
    model = Account.objects.get(id=json_body['id'])
    assert status_code == 201
    assert model.to_dict() == json_body
    model.delete()


@pytest.mark.parametrize(
    "client_fixture, framework_config",
    [
        ("fastapi_client", FRAMEWORK_CONFIGS["fastapi"]),
        ("chalice_client", FRAMEWORK_CONFIGS["chalice"]),
    ],
)
def test_create_resource_bad_request(
    client_fixture: str, framework_config: dict, request: pytest.FixtureRequest
) -> None:
    client = request.getfixturevalue(client_fixture)
    data = dict(invalid_field='some value')
    resp = client.post('/accounts', json=data)
    assert resp.status_code == framework_config['validation_error_code']


@pytest.mark.parametrize(
    "client_fixture", ["fastapi_client", "chalice_client"]
)
def test_retrieve_resource(
    client_fixture: str, request: pytest.FixtureRequest, account: Account
) -> None:
    client = request.getfixturevalue(client_fixture)
    resp = client.get(f'/accounts/{account.id}')
    json_body = resp.json()
    status_code = resp.status_code
    assert status_code == 200
    assert json_body == account.to_dict()
    assert account.api_key_id == TEST_DEFAULT_API_KEY_ID


@pytest.mark.parametrize(
    "client_fixture, framework_config",
    [
        ("fastapi_client", FRAMEWORK_CONFIGS["fastapi"]),
        ("chalice_client", FRAMEWORK_CONFIGS["chalice"]),
    ],
)
def test_retrieve_resource_platform_id_filter_required(
    client_fixture: str,
    framework_config: dict,
    request: pytest.FixtureRequest,
    other_account: Account,
) -> None:
    patch_target = framework_config["platform_id_filter"]
    with patch(patch_target, MagicMock(return_value=True)):
        client = request.getfixturevalue(client_fixture)
        resp = client.get(f"/accounts/{other_account.id}")
        assert resp.status_code == 404


@pytest.mark.parametrize(
    "client_fixture, framework_config",
    [
        ("fastapi_client", FRAMEWORK_CONFIGS["fastapi"]),
        ("chalice_client", FRAMEWORK_CONFIGS["chalice"]),
    ],
)
def test_retrieve_resource_user_id_filter_required(
    client_fixture: str,
    framework_config: dict,
    request: pytest.FixtureRequest,
    other_account: Account,
) -> None:
    patch_target = framework_config["user_id_filter"]
    with patch(patch_target, MagicMock(return_value=True)):
        client = request.getfixturevalue(client_fixture)
        resp = client.get(f"/accounts/{other_account.id}")
        assert resp.status_code == 404


@pytest.mark.parametrize(
    "client_fixture, framework_config",
    [
        ("fastapi_client", FRAMEWORK_CONFIGS["fastapi"]),
        ("chalice_client", FRAMEWORK_CONFIGS["chalice"]),
    ],
)
def test_retrieve_resource_user_id_and_platform_id_filter_required(
    client_fixture: str,
    framework_config: dict,
    request: pytest.FixtureRequest,
    other_account: Account,
) -> None:
    platform_id_filter_target = framework_config["platform_id_filter"]
    user_id_filter_target = framework_config["user_id_filter"]

    with (
        patch(platform_id_filter_target, MagicMock(return_value=True)),
        patch(user_id_filter_target, MagicMock(return_value=True)),
    ):

        client = request.getfixturevalue(client_fixture)
        resp = client.get(f"/accounts/{other_account.id}")
        assert resp.status_code == 404


@pytest.mark.parametrize(
    "client_fixture", ["fastapi_client", "chalice_client"]
)
def test_retrieve_resource_not_found(
    client_fixture: str, request: pytest.FixtureRequest
) -> None:
    client = request.getfixturevalue(client_fixture)
    resp = client.get('/accounts/unknown_id')
    assert resp.status_code == 404


@pytest.mark.parametrize(
    "client_fixture, framework_config",
    [
        ("fastapi_client", FRAMEWORK_CONFIGS["fastapi"]),
        ("chalice_client", FRAMEWORK_CONFIGS["chalice"]),
    ],
)
def test_update_resource_with_invalid_params(
    client_fixture: str, framework_config: dict, request: pytest.FixtureRequest
) -> None:
    client = request.getfixturevalue(client_fixture)
    wrong_params = dict(wrong_param='wrong_value')
    response = client.patch(
        '/accounts/NOT_EXISTS',
        json=wrong_params,
    )
    assert response.status_code == framework_config['validation_error_code']


@pytest.mark.parametrize(
    "client_fixture", ["fastapi_client", "chalice_client"]
)
def test_retrieve_custom_method(
    client_fixture: str, request: pytest.FixtureRequest, card: Card
) -> None:
    client = request.getfixturevalue(client_fixture)
    resp = client.get(f'/cards/{card.id}')
    json_body = resp.json()
    status_code = resp.status_code
    assert status_code == 200
    assert json_body['number'] == '*' * 16


@pytest.mark.parametrize(
    "client_fixture", ["fastapi_client", "chalice_client"]
)
def test_update_resource_that_doesnt_exist(
    client_fixture: str, request: pytest.FixtureRequest
) -> None:
    client = request.getfixturevalue(client_fixture)
    resp = client.patch(
        '/accounts/5f9b4d0ff8d7255e3cc3c128',
        json=dict(name='Frida'),
    )
    assert resp.status_code == 404


@pytest.mark.parametrize(
    "client_fixture", ["fastapi_client", "chalice_client"]
)
def test_update_resource(
    client_fixture: str, request: pytest.FixtureRequest, account: Account
) -> None:
    client = request.getfixturevalue(client_fixture)
    resp = client.patch(
        f'/accounts/{account.id}',
        json=dict(name='Maria Felix'),
    )
    json_body = resp.json()
    status_code = resp.status_code
    account.reload()
    assert json_body['name'] == 'Maria Felix'
    assert account.name == 'Maria Felix'
    assert status_code == 200


@pytest.mark.parametrize(
    "client_fixture", ["fastapi_client", "chalice_client"]
)
def test_delete_resource(
    client_fixture: str, request: pytest.FixtureRequest, account: Account
) -> None:
    client = request.getfixturevalue(client_fixture)
    resp = client.delete(f'/accounts/{account.id}')
    json_body = resp.json()
    status_code = resp.status_code
    account.reload()
    assert status_code == 200
    assert json_body['deactivated_at'] is not None
    assert account.deactivated_at is not None


@pytest.mark.parametrize(
    "client_fixture", ["fastapi_client", "chalice_client"]
)
def test_delete_resource_not_exists(
    client_fixture: str, request: pytest.FixtureRequest
) -> None:
    client = request.getfixturevalue(client_fixture)
    resp = client.delete('/accounts/1234')
    assert resp.status_code == 404


@pytest.mark.parametrize(
    "client_fixture", ["fastapi_client", "chalice_client"]
)
@pytest.mark.usefixtures('accounts')
def test_query_count_resource(
    client_fixture: str, request: pytest.FixtureRequest
) -> None:
    client = request.getfixturevalue(client_fixture)
    query_params = dict(count=1, name='Frida Kahlo')
    resp = client.get(f'/accounts?{urlencode(query_params)}')
    json_body = resp.json()
    status_code = resp.status_code
    assert status_code == 200
    assert json_body['count'] == 1


@pytest.mark.parametrize(
    "client_fixture", ["fastapi_client", "chalice_client"]
)
@pytest.mark.usefixtures('accounts')
def test_query_all_with_limit(
    client_fixture: str, request: pytest.FixtureRequest
) -> None:
    client = request.getfixturevalue(client_fixture)
    limit = 2
    query_params = dict(limit=limit)
    resp = client.get(f'/accounts?{urlencode(query_params)}')
    json_body = resp.json()
    status_code = resp.status_code
    assert status_code == 200
    assert len(json_body['items']) == limit
    assert json_body['next_page_uri'] is None


@pytest.mark.parametrize(
    "client_fixture", ["fastapi_client", "chalice_client"]
)
@pytest.mark.usefixtures('accounts')
def test_query_all_resource(
    client_fixture: str,
    request: pytest.FixtureRequest,
    accounts: list[Account],
) -> None:
    client = request.getfixturevalue(client_fixture)
    accounts = list(reversed(accounts))

    items = []
    page_uri = f'/accounts?{urlencode(dict(page_size=2))}'

    while page_uri:
        resp = client.get(page_uri)
        json_body = resp.json()
        status_code = resp.status_code
        assert status_code == 200
        items.extend(json_body['items'])
        page_uri = json_body['next_page_uri']

    assert len(items) == len(accounts)
    assert all(a.to_dict() == b for a, b in zip(accounts, items))


@pytest.mark.parametrize("client_fixture", ["chalice_client"])
def test_query_all_filter_active(
    client_fixture: str,
    request: pytest.FixtureRequest,
    account: Account,
    accounts: list[Account],
) -> None:
    client = request.getfixturevalue(client_fixture)
    query_params = dict(active=True)
    # Query active items
    resp = client.get(f'/accounts?{urlencode(query_params)}')
    json_body = resp.json()
    status_code = resp.status_code
    assert status_code == 200
    items = json_body['items']
    assert len(items) == len(accounts)
    assert all(item['deactivated_at'] is None for item in items)

    # Deactivate Item
    account.deactivated_at = dt.datetime.utcnow()
    account.save()
    resp = client.get(f'/accounts?{urlencode(query_params)}')
    json_body = resp.json()
    status_code = resp.status_code
    assert status_code == 200
    items = json_body['items']
    assert len(items) == len(accounts) - 1

    # Query deactivated items
    query_params = dict(active=False)
    resp = client.get(f'/accounts?{urlencode(query_params)}')
    json_body = resp.json()
    status_code = resp.status_code
    assert status_code == 200
    items = json_body['items']
    assert len(items) == 1
    assert items[0]['deactivated_at'] is not None


@pytest.mark.parametrize(
    "client_fixture", ["fastapi_client", "chalice_client"]
)
def test_query_all_created_after(
    client_fixture: str,
    request: pytest.FixtureRequest,
    accounts: list[Account],
) -> None:
    client = request.getfixturevalue(client_fixture)
    created_at = dt.datetime(2020, 2, 1)
    expected_length = len([a for a in accounts if a.created_at > created_at])

    query_params = dict(created_after=created_at.isoformat())
    resp = client.get(f'/accounts?{urlencode(query_params)}')
    json_body = resp.json()
    status_code = resp.status_code
    assert status_code == 200
    assert len(json_body['items']) == expected_length


@pytest.mark.parametrize(
    "client_fixture, framework_config",
    [
        ("fastapi_client", FRAMEWORK_CONFIGS["fastapi"]),
        ("chalice_client", FRAMEWORK_CONFIGS["chalice"]),
    ],
)
def test_query_platform_id_filter_required(
    client_fixture: str,
    framework_config: dict,
    request: pytest.FixtureRequest,
    accounts: list[Account],
) -> None:
    client = request.getfixturevalue(client_fixture)
    patch_target = framework_config["platform_id_filter"]
    with patch(patch_target, MagicMock(return_value=True)):
        accounts = list(
            reversed(
                [
                    a
                    for a in accounts
                    if a.platform_id == TEST_DEFAULT_PLATFORM_ID
                ]
            )
        )

        items = []
        page_uri = f'/accounts?{urlencode(dict(page_size=2))}'

        while page_uri:
            resp = client.get(page_uri)
            json_body = resp.json()
            status_code = resp.status_code
            assert status_code == 200
            items.extend(json_body['items'])
            page_uri = json_body['next_page_uri']

        assert len(items) == len(accounts)
        assert all(a.to_dict() == b for a, b in zip(accounts, items))


@pytest.mark.parametrize(
    "client_fixture, framework_config",
    [
        ("fastapi_client", FRAMEWORK_CONFIGS["fastapi"]),
        ("chalice_client", FRAMEWORK_CONFIGS["chalice"]),
    ],
)
def test_query_user_id_filter_required(
    client_fixture: str,
    framework_config: dict,
    request: pytest.FixtureRequest,
    accounts: list[Account],
) -> None:
    client = request.getfixturevalue(client_fixture)
    patch_target = framework_config["user_id_filter"]
    with patch(patch_target, MagicMock(return_value=True)):
        accounts = list(
            reversed(
                [a for a in accounts if a.user_id == TEST_DEFAULT_USER_ID]
            )
        )
        items = []
        page_uri = f'/accounts?{urlencode(dict(page_size=2))}'

        while page_uri:
            resp = client.get(page_uri)
            json_body = resp.json()
            status_code = resp.status_code
            assert status_code == 200
            items.extend(json_body['items'])
            page_uri = json_body['next_page_uri']

        assert len(items) == len(accounts)
        assert all(a.to_dict() == b for a, b in zip(accounts, items))


@pytest.mark.parametrize(
    "client_fixture, framework_config",
    [
        ("fastapi_client", FRAMEWORK_CONFIGS["fastapi"]),
        ("chalice_client", FRAMEWORK_CONFIGS["chalice"]),
    ],
)
def test_query_resource_with_invalid_params(
    client_fixture: str, request: pytest.FixtureRequest, framework_config: dict
) -> None:
    client = request.getfixturevalue(client_fixture)
    wrong_params = dict(wrong_param='wrong_value')
    resp = client.get(f'/accounts?{urlencode(wrong_params)}')
    assert resp.status_code == framework_config['validation_error_code']


@pytest.mark.parametrize(
    "client_fixture", ["fastapi_client", "chalice_client"]
)
@pytest.mark.usefixtures('cards')
def test_query_custom_method(
    client_fixture: str, request: pytest.FixtureRequest
) -> None:
    client = request.getfixturevalue(client_fixture)
    query_params = dict(page_size=2)
    resp = client.get(f'/cards?{urlencode(query_params)}')
    json_body = resp.json()
    status_code = resp.status_code
    assert status_code == 200
    assert len(json_body['items']) == 2
    assert all(card['number'] == '*' * 16 for card in json_body['items'])

    resp = client.get(json_body['next_page_uri'])
    json_body = resp.json()
    status_code = resp.status_code
    assert status_code == 200
    assert len(json_body['items']) == 2
    assert all(card['number'] == '*' * 16 for card in json_body['items'])


@pytest.mark.parametrize(
    "client_fixture", ["fastapi_client", "chalice_client"]
)
def test_cannot_create_resource(
    client_fixture: str, request: pytest.FixtureRequest
) -> None:
    client = request.getfixturevalue(client_fixture)
    resp = client.post('/billers', json=dict())
    assert resp.status_code == 405


@pytest.mark.parametrize(
    "client_fixture, framework_config",
    [
        ("fastapi_client", FRAMEWORK_CONFIGS["fastapi"]),
        ("chalice_client", FRAMEWORK_CONFIGS["chalice"]),
    ],
)
def test_cannot_query_resource(
    client_fixture: str, request: pytest.FixtureRequest, framework_config: dict
) -> None:
    client = request.getfixturevalue(client_fixture)
    query_params = dict(count=1, name='Frida Kahlo')
    resp = client.get(f'/transactions?{urlencode(query_params)}')
    assert resp.status_code == framework_config['method_not_allowed_code']


@pytest.mark.parametrize(
    "client_fixture", ["fastapi_client", "chalice_client"]
)
def test_cannot_update_resource(
    client_fixture: str, request: pytest.FixtureRequest
) -> None:
    client = request.getfixturevalue(client_fixture)
    resp = client.patch('/transactions/123', json=dict())
    assert resp.status_code == 405


@pytest.mark.parametrize(
    "client_fixture", ["fastapi_client", "chalice_client"]
)
def test_cannot_delete_resource(
    client_fixture: str, request: pytest.FixtureRequest
) -> None:
    client = request.getfixturevalue(client_fixture)
    resp = client.delete('/transactions/TR1234')
    assert resp.status_code == 405


@pytest.mark.parametrize(
    "client_fixture, framework_config",
    [
        ("fastapi_client", FRAMEWORK_CONFIGS["fastapi"]),
        ("chalice_client", FRAMEWORK_CONFIGS["chalice"]),
    ],
)
def test_not_found(
    client_fixture: str, request: pytest.FixtureRequest, framework_config: dict
) -> None:
    client = request.getfixturevalue(client_fixture)
    resp = client.get('/non-registered-endpoint')
    assert resp.status_code == framework_config['not_found_code']


@pytest.mark.parametrize(
    "client_fixture", ["fastapi_client", "chalice_client"]
)
def test_download_resource(
    client_fixture: str, request: pytest.FixtureRequest, file: File
) -> None:
    client = request.getfixturevalue(client_fixture)
    mimetype = 'application/pdf'
    resp = client.get(f'/files/{file.id}', headers={'Accept': mimetype})
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == mimetype


@pytest.mark.parametrize(
    "client_fixture", ["fastapi_client", "chalice_client"]
)
@pytest.mark.usefixtures('users')
def test_filter_no_user_id_query(
    client_fixture: str, request: pytest.FixtureRequest
) -> None:
    client = request.getfixturevalue(client_fixture)
    resp = client.get(f'/users?platform_id={TEST_DEFAULT_PLATFORM_ID}')
    resp_json = resp.json()
    status_code = resp.status_code
    assert status_code == 200
    assert len(resp_json['items']) == 1
    user1 = resp_json['items'][0]

    resp = client.get(f'/users?platform_id={TEST_SECOND_PLATFORM_ID}')
    resp_json = resp.json()
    status_code = resp.status_code
    assert status_code == 200
    assert len(resp_json['items']) == 1
    user2 = resp_json['items'][0]
    assert user1['id'] != user2['id']


def test_update_user_with_ip(fastapi_client: TestClient, user: User) -> None:
    resp = fastapi_client.patch(
        f'/users/{user.id}', json={'name': 'Pedrito Sola'}
    )
    resp_json = resp.json()
    assert resp.status_code == 200
    assert resp_json['ip'] == 'testclient'
    assert resp_json['name'] == 'Pedrito Sola'


@pytest.mark.parametrize(
    "client_fixture", ["fastapi_client", "chalice_client"]
)
@pytest.mark.usefixtures('billers')
def test_filter_no_user_id_and_no_platform_id_query(
    client_fixture: str, request: pytest.FixtureRequest
) -> None:
    client = request.getfixturevalue(client_fixture)
    resp = client.get('/billers?name=ATT')
    resp_json = resp.json()
    status_code = resp.status_code
    assert status_code == 200
    assert len(resp_json['items']) == 1


def test_upload_resource(fastapi_client: TestClient) -> None:
    with TemporaryFile(mode='rb') as f:
        file_body = f.read()
    resp = fastapi_client.post(
        '/files',
        files=dict(file=(None, file_body), file_name=(None, 'test_file.txt')),
    )
    assert resp.status_code == 201
    json = resp.json()
    assert json['name'] == 'test_file.txt'


def test_upload_resource_with_invalid_form(fastapi_client: TestClient) -> None:
    wrong_form = dict(another_file=b'Whasaaaaap')
    resp = fastapi_client.post('/files', files=wrong_form)
    assert resp.status_code == 400
