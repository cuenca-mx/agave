import json
from typing import Dict
from urllib.parse import urlencode

import pytest
from chalice.test import Client


@pytest.mark.usefixtures('aws_credentials')
def test_retrieve_transfer(app, user_creds: Dict, transfer_dict: Dict) -> None:
    with Client(app) as client:

        response = client.http.post(
            '/mytest',
            headers=user_creds['auth'],
            body=json.dumps(transfer_dict),
        )
        assert response.status_code == 200


def test_query_all_transfers(app, user_creds: Dict) -> None:
    with Client(app) as client:
        query_params = dict(page_size=4, user_id='limon')
        response = client.http.get(
            f'/mytest?{urlencode(query_params)}', headers=user_creds['auth']
        )
        assert response.status_code == 200
