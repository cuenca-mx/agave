__all__ = ['AuthedRestApiBlueprint']

from agave.chalice_support import RestApiBlueprint

from .authed import AuthedBlueprint


class AuthedRestApiBlueprint(AuthedBlueprint, RestApiBlueprint):
    ...
