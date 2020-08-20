from chalice.test import Client


def test_get(app):

    with Client(app) as client:
        response = client.http.get('/')
        assert response.json_body == {'hello': 'restapi'}
