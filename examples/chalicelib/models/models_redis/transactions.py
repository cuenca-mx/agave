from rom import Float, util

from agave.models.helpers import uuid_field
from agave.repositories import BaseModel, String


class TransactionRedis(BaseModel):
    id = String(
        default=uuid_field('TR'),
        required=True,
        unique=True,
        index=True,
        keygen=util.IDENTITY,
    )
    user_id = String(required=True, index=True, keygen=util.IDENTITY)
    amount = Float(required=True, index=True, keygen=util.IDENTITY)
