from chalice import Response
from cuenca_validations.types import StrictTransferRequest, TransferQuery

from agave.resource.helpers import generic_query
from tests.chalicelib.base import app
from tests.chalicelib.model_dummy import DummyRest as DummyModel


@app.resource('/mytest')
class DummyRest:
    model = DummyModel
    query_validator = TransferQuery
    get_query_filter = generic_query

    @staticmethod
    @app.validate(StrictTransferRequest)
    def create(request: StrictTransferRequest) -> Response:
        transfer = DummyModel()
        transfer.create(request)
        status_code = 200
        return Response(transfer.to_dict(), status_code=status_code)
