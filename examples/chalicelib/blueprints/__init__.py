__all__ = ['AuthedRestApiBlueprint']

from agave.blueprints import RestApiBlueprint, RestApiBlueprintV2

from .authed import AuthedBlueprint


class AuthedRestApiBlueprint(AuthedBlueprint, RestApiBlueprint):
    ...


class AuthedRestApiBlueprintV2(AuthedBlueprint, RestApiBlueprintV2):
    ...
