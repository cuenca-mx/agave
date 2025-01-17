from agave.core.filters import generic_query

from ...validators import TransactionQuery
from ...models.transactions import Transaction as TransactionModel
from .base import app


@app.resource('/transactions')
class Transaction:
    model = TransactionModel
    query_validator = TransactionQuery
    get_query_filter = generic_query
