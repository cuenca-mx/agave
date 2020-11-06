import datetime as dt

from chalice import NotFoundError, Response
from mongoengine import DoesNotExist

from agave.filters import generic_query

from ..models import Account as AccountModel
from ..validators import AccountQuery, AccountRequest, AccountUpdateRequest
from .base import app


@app.resource('/accounts')
class Account:
    model = AccountModel
    query_validator = AccountQuery
    update_validator = AccountUpdateRequest
    get_query_filter = generic_query

    @staticmethod
    @app.validate(AccountRequest)
    def create(request: AccountRequest) -> Response:
        account = AccountModel(
            name=request.name,
            user_id=app.current_user_id,
        )
        account.save()
        return Response(account.to_dict(), status_code=201)

    @staticmethod
    def update(
        account: AccountModel, request: AccountUpdateRequest
    ) -> Response:
        account.name = request.name
        account.save()
        return Response(account.to_dict(), status_code=200)

    @staticmethod
    def delete(id: str) -> Response:
        try:
            account = AccountModel.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('Not valid id')

        account.deactivated_at = dt.datetime.utcnow().replace(microsecond=0)
        account.save()
        return Response(account.to_dict(), status_code=200)
