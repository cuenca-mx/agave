from agave.core.filters import generic_query

from ...validators import UserQuery
from ..models import User as UserModel
from .base import app


@app.resource('/users')
class User:
    model = UserModel
    query_validator = UserQuery
    get_query_filter = generic_query
