__all__ = ['AuthedRestApiBlueprint']

from agave.chalice import RestApiBlueprint

from .authed import AuthedBlueprint


class AuthedRestApiBlueprint(AuthedBlueprint, RestApiBlueprint): ...
