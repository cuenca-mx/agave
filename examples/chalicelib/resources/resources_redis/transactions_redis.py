from agave.filters import generic_query_redis
from agave.repositories import RedisRepository
from examples.chalicelib.models import TransactionRedis as Model
from examples.chalicelib.validators import TransactionQuery

from ..base import app


@app.resource('/transactions_redis')
class TransactionRedis:
    repository = RedisRepository(Model, generic_query_redis)
    query_validator = TransactionQuery
    get_query_filter = generic_query_redis
