import json
from typing import Dict
from urllib.parse import urlencode

from chalice.test import Client
from mock import patch


def test_create_transfer(app, user_creds: Dict, transfer_dict: Dict) -> None:
    with Client(app) as client:
        response = client.http.post(
            '/mytest',
            headers=user_creds['auth'],
            body=json.dumps(transfer_dict),
        )
        assert response.status_code == 200


@patch('agave.blueprints.rest_api.AUTHORIZER', 'AWS_IAM')
def test_query_all_transfers(app, user_creds: Dict) -> None:
    with Client(app) as client:
        query_params = dict(page_size=4, count=1)
        response = client.http.get(
            f'/mytest?{urlencode(query_params)}', headers=user_creds['auth']
        )
        assert response.status_code == 200
        assert response.json_body['count'] == 1


@patch('agave.blueprints.rest_api.AUTHORIZER', 'AWS_IAM')
def test_query_all_transfers_with_limit(app, user_creds: Dict) -> None:
    with Client(app) as client:
        query_params = dict(limit=1)
        response = client.http.get(
            f'/mytest?{urlencode(query_params)}', headers=user_creds['auth']
        )
        assert response.status_code == 200
        assert len(response.json_body['items']) == 1


@patch('agave.blueprints.rest_api.AUTHORIZER', 'AWS_IAM')
def test_retrieve_transfer_not_found(app, user_creds: Dict) -> None:
    with Client(app) as client:
        transfer_id = 'abc123'
        response = client.http.get(
            f'/mytest/{transfer_id}', headers=user_creds['auth']
        )
        assert response.status_code == 404
