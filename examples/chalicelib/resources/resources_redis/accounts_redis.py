import datetime as dt
from typing import Any, Dict, Tuple

from agave.filters import generic_query_redis
from agave.repositories import RedisRepository
from examples.chalicelib.blueprints import AuthedRestApiBlueprint
from examples.chalicelib.models.models_redis import AccountRedis as Model
from examples.chalicelib.validators import (
    AccountQuery,
    AccountRequest,
    AccountUpdateRequest,
)

from ..base import app


class AccountFormatter:
    def __init__(self, app: AuthedRestApiBlueprint):
        self.app = app

    def __call__(self, instance: Model) -> Dict:
        data = instance.dict()
        secret = data.get('secret')
        if secret:
            data['secret'] = secret[0:10] + ('*' * 10)
        return data


def redis_formatter(instance: Any) -> Dict:
    return instance.dict()


@app.resource('/account_redis')
class AccountRedis:
    repository = RedisRepository(Model, generic_query_redis)
    query_validator = AccountQuery
    #  it should be an instance so we can keep it compatible
    #  with a function
    formatter = redis_formatter

    def create(self, request: AccountRequest) -> Tuple[Model, int]:
        account = Model(name=request.name, user_id=app.current_user_id)
        account.save()
        account.dict()
        return account, 201

    def update(self, account: Model, request: AccountUpdateRequest) -> Model:
        account.name = request.name
        account.save()
        return account

    def delete(self, account: Model) -> Model:
        account.deactivated_at = dt.datetime.utcnow().replace(microsecond=0)
        account.save()
        return account
