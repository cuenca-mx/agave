__all__ = ['AuthedRestApiBlueprint']

from agave.blueprints import RestApiBlueprint

from .authed import AuthedBlueprint


class AuthedRestApiBlueprint(AuthedBlueprint, RestApiBlueprint):
    ...
