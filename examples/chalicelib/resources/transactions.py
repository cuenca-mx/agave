from agave.collections.mongo import MongoCollection
from agave.collections.mongo.filters import generic_query

from ..models.transactions import Transaction as TransactionModel
from ..validators import TransactionQuery
from .base import app


@app.resource('/transactions')
class Transaction:
    collection = MongoCollection(TransactionModel, generic_query)
    query_validator = TransactionQuery
    get_query_filter = generic_query
