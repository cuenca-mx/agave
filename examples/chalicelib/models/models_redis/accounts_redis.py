import datetime as dt

from rom import DateTime, util

from agave.models.helpers import uuid_field
from agave.repositories import BaseModel, String


class AccountRedis(BaseModel):
    id = String(
        default=uuid_field('US'),
        required=True,
        unique=True,
        index=True,
        keygen=util.IDENTITY,
    )
    name = String(required=True)
    user_id = String(required=True)
    secret = String()
    created_at = DateTime(default=dt.datetime.utcnow, index=True)
    deactivated_at = DateTime(index=True)
