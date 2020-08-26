import datetime as dt
import json

import pytest
from chalice import Chalice
from chalice.test import Client
from cuenca_validations.types import JSONEncoder

from tests.conftest import app as bp

today = dt.date.today()
now = dt.datetime.now()
utcnow = now.astimezone(dt.timezone.utc)


@pytest.fixture
def app():
    app = Chalice('myapp')
    app.register_blueprint(bp)

    @app.route('/')
    def health_check():
        return dict(greeting="I'm healthy!!!")

    @bp.post('/test')
    def test_post():
        return {'success': True}

    @bp.patch('/patch')
    def test_patch():
        return {'only': 'patch'}

    @bp.delete('/remove')
    def test_remove():
        return {'remove': 'all'}

    @bp.validate(JSONEncoder)
    def test_validate():
        to_encode = dict(
            status='succeeded', time=utcnow.isoformat(), hello='there'
        )
        encoded = json.dumps(to_encode, cls=JSONEncoder)
        decoded = json.loads(encoded)

        return decoded

    return app


def test_get_rest_api(app):
    with Client(app) as client:
        response = client.http.get('/')
        assert response.json_body == {'greeting': "I'm healthy!!!"}


def test_rest_api_blueprint(app) -> None:
    with Client(app) as client:
        response = client.http.get('/healthy_auth')

        assert response.status_code == 200


def test_rest_api_validations(app):
    @bp.resource('/proof')
    def test_patch():
        return {'only': 'resource'}

    with Client(app) as client:
        response = client.http.post('/proof')
        assert response.status_code == 403
