import json
from typing import Dict

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
