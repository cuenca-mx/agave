from chalice.test import Client


def test_health_check(client: Client) -> None:
    response = client.http.get('/')
    assert response.status_code == 200
    assert response.json_body == dict(greeting="I'm testing app!!!")
