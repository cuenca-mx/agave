from typing import Dict
from urllib.parse import urlencode

from chalice.test import Client


def test_rst_api_dummy(app, user_creds: Dict) -> None:
    with Client(app) as client:
        id = 'Usyw23'
        status = True
        response = client.http.post('/mytest', headers=user_creds)
        responses = client.http.delete(f'/mytest/{id}')
        params = dict(active=status, count=1)
        responseses = client.http.get(
            f'/mytest?{urlencode(params)}', headers=user_creds
        )

        print(responseses)
        assert response.status_code == 200
        assert responses.status_code == 200
