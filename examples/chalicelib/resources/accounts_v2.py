import datetime as dt
from typing import Dict, Tuple

from agave.filters import generic_query
from agave.repositories import MongoRepository

from ..models import Account as Model
from ..validators import AccountQuery, AccountRequest, AccountUpdateRequest
from .base import AuthedRestApiBlueprintV2, app_v2


class AccountFormatter:
    def __init__(self, app: AuthedRestApiBlueprintV2):
        self.app = app

    def __call__(self, instance: Model) -> Dict:
        data = instance.to_dict()
        secret = data.get('secret')
        if secret:
            data['secret'] = secret[0:10] + ('*' * 10)
        return data


@app_v2.resource('/accountsv2')
class AccountV2:
    repository = MongoRepository(Model, generic_query)
    query_validator = AccountQuery
    #  it should be an instance so we can keep it compatible
    #  with a function
    formatter = AccountFormatter(app_v2)

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
