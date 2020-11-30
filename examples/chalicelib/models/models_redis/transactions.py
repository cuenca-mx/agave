from rom import Float

from agave.models.helpers import uuid_field
from agave.repositories import BaseModel, String


class TransactionRedis(BaseModel):
    id = String(
        default=uuid_field('US'),
    )
    user_id = String(required=True)
    amount = Float(required=True)
