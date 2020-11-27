import datetime as dt
from typing import Tuple

from agave.filters import generic_query
from agave.repositories import MongoRepository

from ..models import Account as Model
from ..validators import AccountQuery, AccountRequest, AccountUpdateRequest
from .base import app_v2


@app_v2.resource('/accountsv2')
class AccountV2:
    repository = MongoRepository(Model, generic_query)
    query_validator = AccountQuery

    def create(self, request: AccountRequest) -> Tuple[Model, int]:
        account = Model(name=request.name, user_id=app_v2.current_user_id)
        account.save()
        return account, 201

    def update(self, account: Model, request: AccountUpdateRequest) -> Model:
        account.name = request.name
        account.save()
        return account

    def delete(self, account: Model) -> Model:
        account.deactivated_at = dt.datetime.utcnow().replace(microsecond=0)
        account.save()
        return account
