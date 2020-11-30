from agave.filters import generic_query_redis
from agave.repositories import RedisRepository
from examples.chalicelib.models import TransactionRedis as TransactionModel
from examples.chalicelib.validators import TransactionQuery

from ..base import app_v2


@app_v2.resource('/transactionsredis')
class TransactionRedis:
    repository = RedisRepository(TransactionModel, generic_query_redis)
    query_validator = TransactionQuery
    get_query_filter = generic_query_redis
