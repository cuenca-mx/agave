import json
from typing import Dict
from urllib.parse import urlencode

import pytest
from chalice.test import Client
from cuenca_validations.types import TransactionStatus
from mock import patch

pytestmark = pytest.mark.usefixtures('transfers')


def test_create_transfer(app, user_creds: Dict, transfer_dict: Dict) -> None:
    with Client(app) as client:
        response = client.http.post(
            '/mytest',
            headers=user_creds['auth'],
            body=json.dumps(transfer_dict),
        )
        assert response.status_code == 201


def test_create_transfer_bad_request(app, user_creds: Dict) -> None:
    with Client(app) as client:
        transfer = dict(foobar='foobar')
        response = client.http.post(
            '/mytest', headers=user_creds['auth'], body=json.dumps(transfer)
        )
        assert response.status_code == 400


@patch('agave.blueprints.rest_api.AUTHORIZER', 'AWS_IAM')
def test_query_transfer_with_params(app, user_creds: Dict) -> None:
    with Client(app) as client:
        query_params = dict(idempotency_key='key_1')
        response = client.http.get(
            f'/mytest?{urlencode(query_params)}',
            headers=user_creds['auth'],
        )
        assert response.status_code == 200
        items = response.json_body['items']
        assert len(items) == 1
        assert items[0]['idempotency_key'] == 'key_1'


@patch('agave.blueprints.rest_api.AUTHORIZER', 'AWS_IAM')
def test_invalid_params(app, user_creds: Dict) -> None:
    with Client(app) as client:
        wrong_params = dict(wrong_param='wrong_value')
        response = client.http.get(
            f'/mytest?{urlencode(wrong_params)}', headers=user_creds['auth']
        )
        assert response.status_code == 400


@patch('agave.blueprints.rest_api.AUTHORIZER', 'AWS_IAM')
def test_retrieve_transfer_not_found(app, user_creds: Dict) -> None:
    with Client(app) as client:
        transfer_id = 'abc123'
        response = client.http.get(
            f'/mytest/{transfer_id}', headers=user_creds['auth']
        )
        assert response.status_code == 404


def test_delete_id(app, user_creds: Dict) -> None:
    with Client(app) as client:
        id = 'jejdiw'
        response = client.http.delete(
            f'/mytest/{id}',
            headers=user_creds['auth'],
            body=json.dumps(dict(minutes=0)),
        )
        assert response.status_code == 200


@patch('agave.blueprints.rest_api.AUTHORIZER', 'AWS_IAM')
def test_query_count(app, user_creds: Dict) -> None:
    with Client(app) as client:
        query_params = dict(
            status=TransactionStatus.succeeded.value,
            count=1,
        )
        response = client.http.get(
            f'/mytest?{urlencode(query_params)}',
            headers=user_creds['auth'],
        )
        assert response.status_code == 200


@patch('agave.blueprints.rest_api.AUTHORIZER', 'AWS_IAM')
def test_query_all_transfers_with_page_size_and_limit(
    app, user_creds: Dict
) -> None:
    with Client(app) as client:
        query_params = dict(page_size=2, limit=5)
        response = client.http.get(
            f'/mytest?{urlencode(query_params)}', headers=user_creds['auth']
        )
        assert response.status_code == 200
        assert len(response.json_body['items']) == 2


@patch('agave.blueprints.rest_api.AUTHORIZER', 'AWS_IAM')
def test_query_all_transfers_with_limit(app, user_creds: Dict) -> None:
    with Client(app) as client:
        query_params = dict(limit=3)
        response = client.http.get(
            f'/mytest?{urlencode(query_params)}', headers=user_creds['auth']
        )
        assert response.status_code == 200
        assert len(response.json_body['items']) == 2
        assert response.json_body['next_page_uri'] is None
