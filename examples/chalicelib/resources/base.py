from ..blueprints import AuthedRestApiBlueprint

app = AuthedRestApiBlueprint(__name__)


@app.get('/healthy_auth')
def health_auth_check() -> dict:
    return dict(greeting="I'm authenticated and healthy !!!")
