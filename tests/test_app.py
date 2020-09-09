from chalice.test import Client


def test_health_check(app) -> None:
    with Client(app) as client:
        response = client.http.get('/')
        assert response.status_code == 200
        assert response.json_body == dict(greeting="I'm testing app!!!")
