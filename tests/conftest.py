from typing import Dict

from agave.blueprints.rest_api import RestApiBlueprint

app = RestApiBlueprint(__name__)


@app.get('/healthy_auth')
def health_auth_check() -> Dict:
    return dict(greeting="only healthy !!!")
