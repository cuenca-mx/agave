from agave.filters import generic_query

from ..models.transactions import Transaction as TransactionModel
from ..validators import TransactionQuery
from .base import app


@app.resource('/transactions')
class Transaction:
    model = TransactionModel
    query_validator = TransactionQuery
    get_query_filter = generic_query
