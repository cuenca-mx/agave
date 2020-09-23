from chalice import BadRequestError, Response
from cuenca_validations.types import (
    StrictTransferRequest,
    TransactionStatus,
    TransferQuery,
)
from mongoengine import NotUniqueError

from tests.chalicelib._generic_query import generic_query
from tests.chalicelib.model_transfer import Transfer as TransferModel

from .base import app


@app.resource('/mytest')
class Transfer:
    model = TransferModel
    query_validator = TransferQuery
    get_query_filter = generic_query

    @staticmethod
    @app.validate(StrictTransferRequest)
    def create(request: StrictTransferRequest) -> Response:
        transfer = TransferModel()
        transfer.create(request)
        try:
            transfer.save()
        except NotUniqueError:
            previous = TransferModel.objects.get(
                recipient_name='Doroteo Arango',
                idempotency_key=transfer.idempotency_key,
            )
            if transfer == previous:
                transfer = previous
                status_code = 200
            else:
                raise BadRequestError('Duplicated idempotency key')
        else:
            transfer.status = TransactionStatus.submitted
            transfer.save()
            status_code = 201
        return Response(transfer.to_dict(), status_code=status_code)

    @staticmethod
    def delete(id: str) -> Response:
        id_dummy = 'remove' + id
        return Response(body=id_dummy, status_code=200)
