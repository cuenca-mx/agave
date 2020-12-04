from urllib.parse import urlencode

import pytest
from chalice.test import Client
from mock import MagicMock, patch

from examples.chalicelib.models import Account
from examples.chalicelib.models.models_redis import AccountRedis

QUERY_DELIMITER = (
    'examples.chalicelib.blueprints.authed.AuthedBlueprint.query_delimiter'
)

endpoints_url = {
    'mongo_account': '/accounts',
    'mongo_transactions': '/transactions',
    'redis_account': '/account_redis',
    'redis_transactions': '/transactions_redis',
}

query_get = {
    'mongo': Account.objects.get,
    'redis': AccountRedis.get_by,
}


@pytest.fixture
def endpoints(request):
    return endpoints_url[request.param]


@pytest.fixture
def query(request):
    return query_get[request.param]


@pytest.mark.parametrize(
    'endpoints, query',
    [('mongo_account', 'mongo'), ('redis_account', 'redis')],
    indirect=True,
)
def test_create_resource(client: Client, endpoints, query) -> None:
    data = dict(name='Doroteo Arango')
    resp = client.http.post(endpoints, json=data)
    model = query(id=resp.json_body['id'])
    assert resp.status_code == 201
    assert model.to_dict() or model.dict() == resp.json_body
    model.delete()


@pytest.mark.parametrize(
    'endpoints',
    ['mongo_account', 'redis_account'],
    indirect=True,
)
def test_create_resource_bad_request(client: Client, endpoints) -> None:
    data = dict(invalid_field='some value')
    resp = client.http.post(endpoints, json=data)
    assert resp.status_code == 400


@pytest.mark.parametrize(
    'endpoints, collection',
    [('mongo_account', 'mongo'), ('redis_account', 'redis')],
    indirect=True,
)
def test_retrieve_resource(client: Client, account, endpoints, collection) -> None:
    resp = client.http.get(f'{endpoints}/{account.id}')
    assert resp.status_code == 200


@patch(
    QUERY_DELIMITER,
    MagicMock(return_value=dict(user_id='US123456789')),
)
@pytest.mark.parametrize(
    'endpoints, collection',
    [('mongo_account', 'mongo'), ('redis_account', 'redis')],
    indirect=True,
)
def test_retrieve_resource_user_id_filter_required(
    client: Client, other_account, endpoints, collection
) -> None:
    resp = client.http.get(f'{endpoints}/{other_account.id}')
    assert resp.status_code == 404


@pytest.mark.parametrize(
    'endpoints',
    ['mongo_account', 'redis_account'],
    indirect=True,
)
def test_retrieve_resource_not_found(client: Client, endpoints) -> None:
    resp = client.http.get(f'{endpoints}/unknown_id')
    assert resp.status_code == 404


@pytest.mark.parametrize(
    'endpoints',
    ['mongo_account', 'redis_account'],
    indirect=True,
)
def test_update_resource_with_invalid_params(client: Client, endpoints) -> None:
    wrong_params = dict(wrong_param='wrong_value')
    response = client.http.patch(
        f'{endpoints}/NOT_EXISTS',
        json=wrong_params,
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'endpoints',
    ['mongo_account', 'redis_account'],
    indirect=True,
)
def test_update_resource_that_doesnt_exit(client: Client, endpoints) -> None:
    resp = client.http.patch(
        f'{endpoints}/5f9b4d0ff8d7255e3cc3c128',
        json=dict(name='Frida'),
    )
    assert resp.status_code == 404


@pytest.mark.parametrize(
    'endpoints, collection',
    [('mongo_account', 'mongo'), ('redis_account', 'redis')],
    indirect=True,
)
def test_update_resource(client: Client, account, endpoints, collection) -> None:
    resp = client.http.patch(
        f'{endpoints}/{account.id}',
        json=dict(name='Maria Felix'),
    )
    if isinstance(account, Account):
        account.reload()
    else:
        account.update()
    assert resp.json_body['name'] == 'Maria Felix'
    assert account.name == 'Maria Felix'
    assert resp.status_code == 200


@pytest.mark.parametrize(
    'endpoints, collection',
    [('mongo_account', 'mongo'), ('redis_account', 'redis')],
    indirect=True,
)
def test_delete_resource(client: Client, account, endpoints, collection) -> None:
    resp = client.http.delete(f'{endpoints}/{account.id}')
    if isinstance(account, Account):
        account.reload()
    else:
        account.update()
    assert resp.status_code == 200
    assert resp.json_body['deactivated_at'] is not None
    assert account.deactivated_at is not None


@pytest.mark.usefixtures('accounts')
@pytest.mark.parametrize(
    'endpoints, collection',
    [('mongo_account', 'mongo'), ('redis_account', 'redis')],
    indirect=True,
)
def test_query_count_resource(client: Client, endpoints, collection) -> None:
    query_params = dict(count=1, name='Frida Kahlo')
    response = client.http.get(
        f'{endpoints}?{urlencode(query_params)}',
    )
    assert response.status_code == 200
    assert response.json_body['count'] == 1


@pytest.mark.usefixtures('accounts')
@pytest.mark.parametrize(
    'endpoints, collection',
    [('mongo_account', 'mongo'), ('redis_account', 'redis')],
    indirect=True,
)
def test_query_all_with_limit(client: Client, endpoints, collection) -> None:
    limit = 2
    query_params = dict(limit=limit)
    response = client.http.get(f'{endpoints}?{urlencode(query_params)}')
    assert response.status_code == 200
    assert len(response.json_body['items']) == limit
    assert response.json_body['next_page_uri'] is None


@pytest.mark.usefixtures('accounts')
@pytest.mark.parametrize(
    'endpoints, collection',
    [('mongo_account', 'mongo'), ('redis_account', 'redis')],
    indirect=True,
)
def test_query_all_resource(client: Client, endpoints, collection) -> None:
    query_params = dict(page_size=2)
    resp = client.http.get(f'{endpoints}?{urlencode(query_params)}')
    assert resp.status_code == 200
    assert len(resp.json_body['items']) == 2

    resp = client.http.get(resp.json_body['next_page_uri'])
    assert resp.status_code == 200
    assert len(resp.json_body['items']) == 2


@pytest.mark.usefixtures('accounts')
@patch(QUERY_DELIMITER, MagicMock(return_value=dict(user_id='US123456789')))
@pytest.mark.parametrize(
    'endpoints, collection',
    [('mongo_account', 'mongo'), ('redis_account', 'redis')],
    indirect=True,
)
def test_query_user_id_filter_required(client: Client, endpoints, collection) -> None:
    query_params = dict(page_size=2)
    resp = client.http.get(f'{endpoints}?{urlencode(query_params)}')
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


@pytest.mark.parametrize(
    'endpoints',
    ['mongo_account', 'redis_account'],
    indirect=True,
)
def test_query_resource_with_invalid_params(client: Client, endpoints) -> None:
    wrong_params = dict(wrong_param='wrong_value')
    response = client.http.get(f'{endpoints}?{urlencode(wrong_params)}')
    assert response.status_code == 400


@pytest.mark.parametrize(
    'endpoints',
    ['mongo_transactions', 'redis_transactions'],
    indirect=True,
)
def test_cannot_create_resource(client: Client, endpoints) -> None:
    response = client.http.post(endpoints, json=dict())
    assert response.status_code == 405


@pytest.mark.parametrize(
    'endpoints',
    ['mongo_transactions', 'redis_transactions'],
    indirect=True,
)
def test_cannot_update_resource(client: Client, endpoints) -> None:
    response = client.http.post(endpoints, json=dict())
    assert response.status_code == 405


@pytest.mark.parametrize(
    'endpoints',
    ['mongo_transactions', 'redis_transactions'],
    indirect=True,
)
def test_cannot_delete_resource(client: Client, endpoints) -> None:
    resp = client.http.delete(f'{endpoints}/TR1234')
    assert resp.status_code == 405
