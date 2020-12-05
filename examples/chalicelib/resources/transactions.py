from typing import Any
from ..validators import TransactionQuery
from .base import app

DB_COLLECTION_TRANSACTIONS = 'mongo'
collection: Any
get_query_filter: Any


if DB_COLLECTION_TRANSACTIONS == 'mongo':
    from agave.collections.mongo import MongoCollection
    from agave.collections.mongo.filters import generic_query

    from ..models import Transaction as TransactionModel
    collection = MongoCollection(TransactionModel, generic_query)
    get_query_filter = generic_query
else:
    from agave.collections.redis import RedisCollection
    from agave.collections.redis.filters import generic_query
    from examples.chalicelib.models import Transaction as Model
    collection = RedisCollection(Model, generic_query)
    get_query_filter = generic_query


@app.resource('/transactions')
class Transaction:
    collection = collection
    query_validator = TransactionQuery
    get_query_filter = get_query_filter
