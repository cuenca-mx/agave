import datetime as dt
from typing import Dict, Tuple

from agave.filters import generic_query_redis
from agave.repositories import RedisRepository

from examples.chalicelib.models.models_redis import AccountRedis as Model
from examples.chalicelib.validators import (
    AccountQuery, AccountRequest, AccountUpdateRequest
)

from examples.chalicelib.resources.base import AuthedRestApiBlueprintV2, app_v2


class AccountFormatter:
    def __init__(self, app: AuthedRestApiBlueprintV2):
        self.app = app

    def __call__(self, instance: Model) -> Dict:
        data = instance.to_dict()
        secret = data.get('secret')
        if secret:
            data['secret'] = secret[0:10] + ('*' * 10)
        return data


@app_v2.resource('/accountredis')
class AccountV2:
    repository = RedisRepository(Model, generic_query_redis)
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