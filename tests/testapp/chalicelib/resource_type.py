from ._generic_query import generic_query
from .base import app
from .model_type import Type as TypeModel
from .queries import USerQuery


@app.resource('/type')
class Type:
    model: TypeModel
    query_validator = USerQuery
    get_query_filter = generic_query
