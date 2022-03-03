from agave.filters import generic_query

from ..models import User as UserModel
from ..validators import UserQuery
from .base import app


@app.resource('/users')
class User:
    model = UserModel
    query_validator = UserQuery
    get_query_filter = generic_query
