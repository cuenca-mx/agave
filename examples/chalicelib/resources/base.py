from typing import Dict

from ..blueprints import AuthedRestApiBlueprint, AuthedRestApiBlueprintV2

app = AuthedRestApiBlueprint(__name__)

app_v2 = AuthedRestApiBlueprintV2(__name__)


@app.get('/healthy_auth')
def health_auth_check() -> Dict:
    return dict(greeting="I'm authenticated and healthy !!!")
