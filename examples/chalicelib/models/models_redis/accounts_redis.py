import datetime as dt

from rom import DateTime, util

from agave.collections.redis.base_redis import BaseModel
from agave.collections.redis.helpers_redis import String
from agave.models.helpers import uuid_field

DEFAULT_MISSING_DATE = dt.datetime.utcfromtimestamp(0)


class AccountRedis(BaseModel):
    id = String(
        default=uuid_field('US'),
        required=True,
        unique=True,
        index=True,
        keygen=util.IDENTITY,
    )
    name = String(required=True, index=True, keygen=util.IDENTITY)
    user_id = String(required=True, index=True, keygen=util.IDENTITY)
    secret = String()
    created_at = DateTime(default=dt.datetime.utcnow, index=True)
    deactivated_at = DateTime(default=DEFAULT_MISSING_DATE, index=True)
