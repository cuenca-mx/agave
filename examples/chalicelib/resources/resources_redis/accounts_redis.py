import datetime as dt
from typing import Any, Dict, Tuple

from agave.collections.redis import RedisCollection
from agave.collections.redis.filters_redis import generic_query_redis
from examples.chalicelib.models.models_redis import AccountRedis as Model
from examples.chalicelib.validators import (
    AccountQuery,
    AccountRequest,
    AccountUpdateRequest,
)

from ..base import app


def redis_formatter(instance: Any) -> Dict:
    return instance.dict()


@app.resource('/account_redis')
class AccountRedis:
    collection = RedisCollection(Model, generic_query_redis)
    query_validator = AccountQuery
    formatter = redis_formatter

    def create(self, request: AccountRequest) -> Tuple[Model, int]:
        account = Model(name=request.name, user_id=app.current_user_id)
        account.save()
        return account, 201

    def update(self, account: Model, request: AccountUpdateRequest) -> Model:
        account.name = request.name  # type: ignore
        account.save()
        return account

    def delete(self, account: Model) -> Model:
        account.deactivated_at = dt.datetime.utcnow().replace(microsecond=0)
        account.save()
        return account
