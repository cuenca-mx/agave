from agave.filters import generic_query
from agave.repositories import MongoRepository

from ..models.transactions import Transaction as TransactionModel
from ..validators import TransactionQuery
from .base import app


@app.resource('/transactions')
class Transaction:
    repository = MongoRepository(TransactionModel, generic_query)
    query_validator = TransactionQuery
    get_query_filter = generic_query
