import pytest
from chalice import Chalice, Response
from chalice.test import Client

from tests.conftest import app as app_demo

bp = Chalice('myapp')
bp.register_blueprint(app_demo)


@app_demo.resource('/mytest')
class DummyRestApi:
    @staticmethod
    def create() -> Response:
        user_id = 'USH827492'
        return Response(user_id, status_code=200)

    @staticmethod
    def delete(id: str) -> Response:
        id_dummy = id
        return Response(id_dummy, status_code=200)


@pytest.fixture(scope='class')
def app():
    app = Chalice('myapp')
    app.register_blueprint(app_demo)
    return app


def test_create_dummy(app) -> None:
    with Client(app) as client:
        response = client.http.post('/mytest')
        assert response.status_code == 200
