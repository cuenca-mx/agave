from agave.collections.redis import RedisCollection
from agave.collections.redis.filters_redis import generic_query_redis
from examples.chalicelib.models import TransactionRedis as Model
from examples.chalicelib.validators import TransactionQuery

from ..base import app


@app.resource('/transactions_redis')
class TransactionRedis:
    collection = RedisCollection(Model, generic_query_redis)
    query_validator = TransactionQuery
    get_query_filter = generic_query_redis
