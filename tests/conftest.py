import pytest
from chalice import Chalice

from mezcal.resource.base import AuthedRestApiBlueprint


@pytest.fixture(scope='module')
def app():

    bp = AuthedRestApiBlueprint('testblueprint')

    @bp.route('/')
    def index():
        return {'hello': 'restapi'}

    app = Chalice('myapp')
    app.register_blueprint(bp)

    return app
