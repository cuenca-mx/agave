import datetime as dt
from typing import Dict, Tuple

from agave.collections.mongo import MongoCollection
from agave.filters import generic_query
from examples.chalicelib.blueprints import AuthedRestApiBlueprint

from ..models import Account as Model
from ..validators import AccountQuery, AccountRequest, AccountUpdateRequest
from .base import app


class AccountFormatter:
    def __init__(self, app: AuthedRestApiBlueprint):
        self.app = app

    def __call__(self, instance: Model) -> Dict:
        data = instance.to_dict()
        secret = data.get('secret')
        if secret:
            data['secret'] = secret[0:10] + ('*' * 10)
        return data


@app.resource('/accounts')
class Account:
    collection = MongoCollection(Model, generic_query)
    query_validator = AccountQuery
    #  it should be an instance so we can keep it compatible
    #  with a function
    formatter = AccountFormatter(app)

    def create(self, request: AccountRequest) -> Tuple[Model, int]:
        account = Model(name=request.name, user_id=app.current_user_id)
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
