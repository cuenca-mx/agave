__all__ = ['AuthedBlueprint', 'AuthedRestApiBlueprint', 'RestApiBlueprint']

from .authed import AuthedBlueprint
from .rest_api import RestApiBlueprint


class AuthedRestApiBlueprint(AuthedBlueprint, RestApiBlueprint):
    ...
