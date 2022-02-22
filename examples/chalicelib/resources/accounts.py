import datetime as dt

from chalice import Response

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
            platform_id=app.current_platform_id,
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
    def delete(account: AccountModel) -> Response:
        account.deactivated_at = dt.datetime.utcnow().replace(microsecond=0)
        account.save()
        return Response(account.to_dict(), status_code=200)
