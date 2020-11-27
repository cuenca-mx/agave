from agave.filters import generic_query
from agave.repositories import MongoRepository

from ..models.transactions import Transaction as TransactionModel
from ..validators import TransactionQuery
from .base import app_v2


@app_v2.resource('/transactionsv2')
class TransactionV2:
    repository = MongoRepository(TransactionModel, generic_query)
    query_validator = TransactionQuery
    get_query_filter = generic_query
