import datetime as dt

from rom import DateTime

from agave.repositories import BaseModel, String, uuid_field


class AccountRedis(BaseModel):
    id = String(default=uuid_field('US'),
                required=True,
                unique=True,
                index=True)
    name = String(required=True)
    user_id = String(required=True)
    secret = String()
    created_at = DateTime(default=dt.datetime.utcnow)
    deactivated_at = DateTime(default=dt.datetime.utcnow)
