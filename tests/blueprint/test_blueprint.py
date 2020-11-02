from typing import Dict
from urllib.parse import urlencode

from chalice.test import Client


def test_create_user(client: Client, user_creds: Dict) -> None:
    name = dict(name='teodoro', key='key_1')
    response = client.http.post(
        '/users',
        headers=user_creds['auth'],
        json=name,
    )
    assert response.status_code == 201


def test_create_user_bad_request(client: Client, user_creds: Dict) -> None:
    user = dict(foobar='foobar')
    response = client.http.post(
        '/users', headers=user_creds['auth'], json=user
    )
    assert response.status_code == 400


def test_query_user_with_params(client: Client, user_creds: Dict) -> None:
    query_params = dict(key='key_1')
    response = client.http.get(
        f'/users?{urlencode(query_params)}',
        headers=user_creds['auth'],
    )
    assert response.status_code == 200
    items = response.json_body['items']
    assert len(items) == 1


def test_invalid_params(client: Client, user_creds: Dict) -> None:
    wrong_params = dict(wrong_param='wrong_value')
    response = client.http.get(
        f'/users?{urlencode(wrong_params)}', headers=user_creds['auth']
    )
    assert response.status_code == 400


def test_retrieve_user(client: Client, user_creds: Dict) -> None:
    name = dict(name='Juan', key='key_1')
    resp = client.http.post(
        '/users',
        headers=user_creds['auth'],
        json=name,
    )
    id = resp.json_body['id']
    response = client.http.get(f'/users/{id}', headers=user_creds['auth'])
    assert response.status_code == 200
    assert response.json_body['id'] == id


def test_retrieve_user_not_found(client: Client, user_creds: Dict) -> None:
    id = '53f466e60ffa5927709972e8'
    response = client.http.get(f'/users/{id}', headers=user_creds['auth'])
    assert response.status_code == 404


def test_delete_id(client: Client, user_creds: Dict) -> None:
    name = dict(name='teodoro', key='key_1')
    response = client.http.post(
        '/users',
        headers=user_creds['auth'],
        json=name,
    )
    id = response.json_body['id']
    resp = client.http.delete(
        f'/users/{id}',
        headers=user_creds['auth'],
        json=dict(code=0),
    )
    assert resp.status_code == 200


def test_update_name(client: Client, user_creds: Dict) -> None:
    name = dict(name='frida', key='key_2')
    response = client.http.post(
        '/users',
        headers=user_creds['auth'],
        json=name,
    )
    id = response.json_body['id']
    resp = client.http.patch(
        f'/users/{id}',
        headers=user_creds['auth'],
        json=dict(name='Frida'),
    )
    assert resp.status_code == 200


def test_name_not_exit(client: Client, user_creds: Dict) -> None:
    id = '5f9b4d0ff8d7255e3cc3c128'
    resp = client.http.patch(
        f'/users/{id}',
        headers=user_creds['auth'],
        json=dict(name='Frida'),
    )
    assert resp.status_code == 404


def test_invalid_value(client: Client, user_creds: Dict) -> None:
    wrong_params = dict(wrong_param='wrong_value')
    id = 'NOT_EXISTS'
    response = client.http.patch(
        f'/users/{id}',
        headers=user_creds['auth'],
        json=wrong_params,
    )
    assert response.status_code == 400


def test_query_count(client: Client, user_creds: Dict) -> None:
    query_params = dict(
        count=1,
    )
    response = client.http.get(
        f'/users?{urlencode(query_params)}',
        headers=user_creds['auth'],
    )
    assert response.status_code == 200


def test_query_all_user_with_page_size_and_limit(
    client: Client, user_creds: Dict
) -> None:
    query_params = dict(page_size=2, limit=5)
    response = client.http.get(
        f'/users?{urlencode(query_params)}', headers=user_creds['auth']
    )
    assert response.status_code == 200
    assert len(response.json_body['items']) == 2


def test_query_all_users_with_limit(client: Client, user_creds: Dict) -> None:
    query_params = dict(limit=3)
    response = client.http.get(
        f'/users?{urlencode(query_params)}', headers=user_creds['auth']
    )
    assert response.status_code == 200
    assert len(response.json_body['items']) == 3
    assert response.json_body['next_page_uri'] is None


def test_query_all_users(client: Client, user_creds: Dict) -> None:
    query_params = dict(page_size=1)
    response = client.http.get(
        f'/users?{urlencode(query_params)}', headers=user_creds['auth']
    )
    assert response.status_code == 200
