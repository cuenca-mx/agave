from agave.models.mongo.filters import generic_mongo_query
from ..models.mongo_models import Transaction as TransactionModel
from ..validators import TransactionQuery
from .base import app


@app.resource('/transactions')
class Transaction:
    model = TransactionModel
    query_validator = TransactionQuery
    get_query_filter = generic_mongo_query
