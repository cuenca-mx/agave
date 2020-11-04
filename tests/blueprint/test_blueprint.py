from urllib.parse import urlencode

from chalice.test import Client


def test_create_user(client: Client) -> None:
    name = dict(name='teodoro', key='key_1')
    response = client.http.post(
        '/users',
        json=name,
    )
    assert response.status_code == 201


def test_create_user_bad_request(client: Client) -> None:
    user = dict(foobar='foobar')
    response = client.http.post('/users', json=user)
    assert response.status_code == 400


def test_query_user_with_params(client: Client) -> None:
    query_params = dict(key='key_1')
    response = client.http.get(f'/users?{urlencode(query_params)}')
    assert response.status_code == 200
    items = response.json_body['items']
    assert len(items) == 1


def test_invalid_params(client: Client) -> None:
    wrong_params = dict(wrong_param='wrong_value')
    response = client.http.get(f'/users?{urlencode(wrong_params)}')
    assert response.status_code == 400


def test_retrieve_user(client: Client) -> None:
    name = dict(name='Juan', key='key_1')
    resp = client.http.post(
        '/users',
        json=name,
    )
    id = resp.json_body['id']
    response = client.http.get(f'/users/{id}')
    assert response.status_code == 200
    assert response.json_body['id'] == id


def test_retrieve_user_not_found(client: Client) -> None:
    response = client.http.get('/users/53f466e60ffa5927709972e8')
    assert response.status_code == 404


def test_delete_id(client: Client) -> None:
    name = dict(name='teodoro', key='key_1')
    response = client.http.post(
        '/users',
        json=name,
    )
    id = response.json_body['id']
    resp = client.http.delete(
        f'/users/{id}',
        json=dict(code=0),
    )
    assert resp.status_code == 200


def test_update_name(client: Client) -> None:
    name = dict(name='frida', key='key_2')
    response = client.http.post(
        '/users',
        json=name,
    )
    id = response.json_body['id']
    resp = client.http.patch(
        f'/users/{id}',
        json=dict(name='Frida'),
    )
    assert resp.status_code == 200


def test_name_not_exit(client: Client) -> None:
    resp = client.http.patch(
        '/users/5f9b4d0ff8d7255e3cc3c128',
        json=dict(name='Frida'),
    )
    assert resp.status_code == 404


def test_invalid_value(client: Client) -> None:
    wrong_params = dict(wrong_param='wrong_value')
    response = client.http.patch(
        '/users/NOT_EXISTS',
        json=wrong_params,
    )
    assert response.status_code == 400


def test_query_count(client: Client) -> None:
    query_params = dict(
        count=1,
    )
    response = client.http.get(
        f'/users?{urlencode(query_params)}',
    )
    assert response.status_code == 200


def test_query_all_user_with_page_size_and_limit(client: Client) -> None:
    query_params = dict(page_size=2, limit=5)
    response = client.http.get(f'/users?{urlencode(query_params)}')
    assert response.status_code == 200
    assert len(response.json_body['items']) == 2


def test_query_all_users_with_limit(client: Client) -> None:
    query_params = dict(limit=3)
    response = client.http.get(f'/users?{urlencode(query_params)}')
    assert response.status_code == 200
    assert len(response.json_body['items']) == 3
    assert response.json_body['next_page_uri'] is None


def test_query_all_users(client: Client) -> None:
    query_params = dict(page_size=1)
    response = client.http.get(f'/users?{urlencode(query_params)}')
    assert response.status_code == 200


def test_deposit_cannot_create(client: Client) -> None:
    response = client.http.post(
        '/deposit',
        json=dict(name='Frida', key='key_2', type='deposit'),
    )
    assert response.status_code == 405


def test_deposit_cannot_delete(client: Client) -> None:
    response = client.http.delete('/deposit/foo')
    assert response.status_code == 405
