try:
    from .rest_api import RestApiBlueprint
except ModuleNotFoundError:
    ...
else:
    __all__ = ['RestApiBlueprint']
