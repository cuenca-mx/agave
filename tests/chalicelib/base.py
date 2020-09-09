from typing import Dict

from agave.blueprints import RestApiBlueprint

app = RestApiBlueprint(__name__)


@app.get('/healthy_auth')
def health_auth_check() -> Dict:
    return dict(greeting="I'm authenticated and healthy !!!")
