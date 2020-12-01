from urllib.parse import urlencode
import pytest
from chalice.test import Client
from examples.chalicelib.models.models_redis import AccountRedis

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
    assert model.to_dict() == resp.json_body
    model.delete()
