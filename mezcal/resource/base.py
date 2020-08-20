from typing import Dict

from ..blueprints import AuthedRestApiBlueprint

app = AuthedRestApiBlueprint(__name__)


@app.get('/healthy_auth')
def health_auth_check() -> Dict:
    return dict(greeting="I'm authenticated and healthy !!!")
