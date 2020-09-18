import json
from typing import Dict
from urllib.parse import urlencode

from chalice.test import Client
from cuenca_validations.types import CardStatus
from cuenca_validations.types.requests import CardUpdateRequest
from mock import patch

from tests.chalicelib.model_card import Card


def test_create_transfer(app, user_creds: Dict, transfer_dict: Dict) -> None:
    with Client(app) as client:
        response = client.http.post(
            '/mytest',
            headers=user_creds['auth'],
            body=json.dumps(transfer_dict),
        )
        assert response.status_code == 200


def test_create_transfer_bad_request(app, user_creds: Dict) -> None:
    with Client(app) as client:
        transfer = dict(foobar='foobar')
        response = client.http.post(
            '/mytest', headers=user_creds['auth'], body=json.dumps(transfer)
        )
        assert response.status_code == 400


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
def test_invalid_params(app, user_creds: Dict) -> None:
    with Client(app) as client:
        wrong_params = dict(wrong_param='wrong_value')
        response = client.http.get(
            f'/mytest?{urlencode(wrong_params)}', headers=user_creds['auth']
        )
        assert response.status_code == 400


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
def test_query_all_transfers_with_page_size_and_limit(
    app, user_creds: Dict
) -> None:
    with Client(app) as client:
        query_params = dict(page_size=2, limit=5)
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


def test_delete_id(app, user_creds: Dict) -> None:
    with Client(app) as client:
        id = 'jejdiw'
        response = client.http.delete(
            f'/mytest/{id}',
            headers=user_creds['auth'],
            body=json.dumps(dict(minutes=0)),
        )
        assert response.status_code == 200


def test_update_card(client: Client, virtual_card: Card) -> None:
    card_update_req = CardUpdateRequest(status=CardStatus.blocked)
    resp = client.http.patch(
        f'/cards/{virtual_card.id}', json=card_update_req.dict(),
    )
    virtual_card.reload()
    assert resp.status_code == 200
    assert virtual_card.status == CardStatus.blocked


def test_update_card_bad_request(client: Client, virtual_card: Card) -> None:
    card_update_dict = dict(status='NOT_EXISTS')
    resp = client.http.patch(
        f'/cards/{virtual_card.id}', json=card_update_dict
    )
    virtual_card.reload()
    assert resp.status_code == 400
    assert virtual_card.status == CardStatus.created


def test_update_not_existing_card(client: Client) -> None:
    card_update_req = CardUpdateRequest(status=CardStatus.blocked)
    resp = client.http.patch('/cards/NOT_EXISTS', json=card_update_req.dict())
    resp.status_code == 404
