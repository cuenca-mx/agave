from chalice import Response
from cuenca_validations.types import StrictTransferRequest, TransferQuery

from agave.resource.helpers import generic_query
from tests.chalicelib.base import app
from tests.chalicelib.model_transfer import Transfer as TransferModel


@app.resource('/mytest')
class Transfer:
    model = TransferModel
    query_validator = TransferQuery
    get_query_filter = generic_query
    update_validator = StrictTransferRequest

    @staticmethod
    @app.validate(StrictTransferRequest)
    def create(request: StrictTransferRequest) -> Response:
        transfer = TransferModel()
        transfer.create(request)
        transfer.save()
        status_code = 200
        return Response(transfer.to_dict(), status_code=status_code)

    @staticmethod
    def update(transfer: TransferModel, request: StrictTransferRequest):
        transfer.account_number = request
        transfer.save()
        return Response(transfer.to_dict(), status_code=200)

    @staticmethod
    def delete(id: str) -> Response:
        id_dummy = 'remove' + id
        return Response(body=id_dummy, status_code=200)
