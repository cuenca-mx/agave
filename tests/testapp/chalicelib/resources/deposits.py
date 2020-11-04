from tests.testapp.chalicelib.models.deposits import Deposit as DepositModel
from tests.testapp.chalicelib.queries import USerQuery
from tests.testapp.chalicelib.resources._generic_query import generic_query
from tests.testapp.chalicelib.resources.base import app


@app.resource('/deposit')
class Deposit:
    model: DepositModel
    query_validator = USerQuery
    get_query_filter = generic_query
