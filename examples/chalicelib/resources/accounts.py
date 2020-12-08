import datetime as dt
from typing import Any, Tuple, Union

from ..models import Account as MongoAccountModel
from ..models import AccountRedis as RedisAccountModel
from ..validators import AccountQuery, AccountRequest, AccountUpdateRequest
from .base import app
from .formatter import AccountFormatter, redis_formatter

DB_COLLECTION_ACCOUNTS = 'mongo'
collection: Any
formatter: Any
Model = Union[MongoAccountModel, RedisAccountModel]
ModelAccount: Any

if DB_COLLECTION_ACCOUNTS == 'mongo':
    from agave.collections.mongo import MongoCollection
    from agave.collections.mongo.filters import generic_query

    collection = MongoCollection(MongoAccountModel, generic_query)
    formatter = AccountFormatter(app)
    ModelAccount = MongoAccountModel
if DB_COLLECTION_ACCOUNTS == 'redis':
    from agave.collections.redis import RedisCollection
    from agave.collections.redis.filters import generic_query

    collection = RedisCollection(RedisAccountModel, generic_query)
    formatter = redis_formatter
    ModelAccount = RedisAccountModel


@app.resource('/accounts')
class Account:
    collection = collection
    query_validator = AccountQuery
    #  it should be an instance so we can keep it compatible
    #  with a function
    formatter = formatter

    def create(self, request: AccountRequest) -> Tuple[Model, int]:
        account = ModelAccount(name=request.name, user_id=app.current_user_id)
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
