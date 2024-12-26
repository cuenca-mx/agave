import datetime as dt

from fastapi import Request
from fastapi.responses import JSONResponse as Response

from agave.core.filters import generic_query

from ..models import Account as AccountModel
from ..validators import (
    AccountQuery,
    AccountRequest,
    AccountResponse,
    AccountUpdateRequest,
)
from .base import app


@app.resource('/accounts')
class Account:
    model = AccountModel
    query_validator = AccountQuery
    update_validator = AccountUpdateRequest
    get_query_filter = generic_query
    response_model = AccountResponse

    @staticmethod
    async def create(request: AccountRequest) -> Response:
        """This is the description for openapi"""
        account = AccountModel(
            name=request.name,
            user_id=app.current_user_id,
            platform_id=app.current_platform_id,
        )
        await account.async_save()
        return Response(content=account.to_dict(), status_code=201)

    @staticmethod
    async def update(
        account: AccountModel,
        request: AccountUpdateRequest,
    ) -> Response:
        account.name = request.name
        await account.async_save()
        return Response(content=account.to_dict(), status_code=200)

    @staticmethod
    async def delete(account: AccountModel, _: Request) -> Response:
        account.deactivated_at = dt.datetime.utcnow().replace(microsecond=0)
        await account.async_save()
        return Response(content=account.to_dict(), status_code=200)
