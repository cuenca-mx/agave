from agave.filters import generic_query

from ..models import Biller as BillerModel
from ..validators import BillerQuery
from .base import app


@app.resource('/billers')
class Biller:
    model = BillerModel
    query_validator = BillerQuery
    get_query_filter = generic_query
