from urllib.parse import urlencode

from chalice.test import Client

from tests.testapp.chalicelib.models import Account


def test_create_resource(client: Client) -> None:
    data = dict(name='Doroteo Arango')
    resp = client.http.post('/accounts', json=data)
    model = Account.objects.get(id=resp.json_body['id'])
    assert resp.status_code == 201
    assert model.to_dict() == resp.json_body


def test_create_resource_bad_request(client: Client) -> None:
    data = dict(invalid_field='some value')
    resp = client.http.post('/accounts', json=data)
    assert resp.status_code == 400


def test_retrieve_resource(client: Client, account: Account) -> None:
    resp = client.http.get(f'/accounts/{account.id}')
    assert resp.status_code == 200
    assert resp.json_body == account.to_dict()


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


def test_update_resource_bad_request(client: Client) -> None:
    resp = client.http.patch(
        '/accounts/5f9b4d0ff8d7255e3cc3c128',
        json=dict(name='Frida'),
    )
    assert resp.status_code == 404


def test_update_resource(client: Client) -> None:
    model = Account.objects.get()
    assert model.name == 'Doroteo Arango'
    resp = client.http.patch(
        f'/accounts/{model.id}',
        json=dict(name='Frida'),
    )

    assert resp.json_body['name'] == 'Frida'
    assert resp.status_code == 200


def test_delete_resource(client: Client) -> None:
    data = dict(name='Doroteo Arango')
    resp = client.http.post('/accounts', json=data)
    model = Account.objects.get(id=resp.json_body['id'])
    resp = client.http.delete(f'/accounts/{model.id}')
    assert resp.json_body['deactivated_at'] is not None
    assert resp.status_code == 200


def test_query_count_resource(client: Client) -> None:
    query_params = dict(
        count=1,
    )
    response = client.http.get(
        f'/accounts?{urlencode(query_params)}',
    )
    assert response.status_code == 200


def test_query_all_with_limit(client: Client) -> None:
    query_params = dict(limit=3)
    response = client.http.get(f'/accounts?{urlencode(query_params)}')
    assert response.status_code == 200
    assert len(response.json_body['items']) == 2
    assert response.json_body['next_page_uri'] is None


def test_query_all_resource(client: Client) -> None:
    query_params = dict(page_size=1)
    resp = client.http.get(f'/accounts?{urlencode(query_params)}')
    assert resp.status_code == 200
    assert len(resp.json_body['items']) == 1


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
