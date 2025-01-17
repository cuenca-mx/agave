from agave.core.filters import generic_query

from ...validators import BillerQuery
from ..models import Biller as BillerModel
from .base import app


@app.resource('/billers')
class Biller:
    model = BillerModel
    query_validator = BillerQuery
    get_query_filter = generic_query
