import os
from typing import Dict, Generator

import pytest
from chalice import Chalice, Response
from cuenca_validations.types import ApiKeyQuery

from agave.blueprints import RestApiBlueprint
from agave.resource.helpers import generic_query

bp = RestApiBlueprint(__name__)


@pytest.fixture
def app():
    app = Chalice('myapp')
    app.register_blueprint(bp)
    return app


@bp.resource('/mytest')
class DummyRestApi:
    query_validator = ApiKeyQuery

    @staticmethod
    def create() -> Response:
        user_id = 'shhausu'
        return Response(body=user_id, status_code=200)

    @staticmethod
    def delete(id: str) -> Response:
        id_dummy = 'remove' + id
        return Response(body=id_dummy, status_code=200)

    @staticmethod
    def query(query: ApiKeyQuery) -> Response:
        # params = TransactionQuery(user_id='user', status='pending')
        query = generic_query(query)
        return Response(body=query, status_code=200)


@pytest.fixture(scope='function')
def aws_credentials() -> None:
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'


@pytest.fixture
def user_creds() -> Generator[Dict, None, None]:
    yield dict(
        user_id='ghdgeueid',
        api_key='39wskq2',
        secret_key='72ysj373jssiq',
        auth='jsheyusghwjwkwkw',
    )
