from urllib.parse import urlencode
import pytest
from chalice.test import Client
from examples.chalicelib.models.models_redis import AccountRedis
from examples.chalicelib.models import Account

USER_ID_FILTER_REQUIRED = (
    'examples.chalicelib.blueprints.authed.'
    'AuthedBlueprint.user_id_filter_required'
)
pytestmark = pytest.mark.usefixtures('client')


def test_create_resource(client: Client) -> None:
    data = dict(name='Doroteo Arango')
    resp = client.http.post('/account_redis', json=data)
    model = AccountRedis.get_by(id=resp.json_body['id'])
    assert resp.status_code == 201
    assert model.dict() == resp.json_body
    model.delete()


def test_create_resource_bad_request(client: Client) -> None:
    data = dict(invalid_field='some value')
    resp = client.http.post('/account_redis', json=data)
    assert resp.status_code == 400
