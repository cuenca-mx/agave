import datetime as dt

from mongoengine import DateTimeField, Document, StringField

from agave.models.base import BaseModel
from agave.models.helpers import uuid_field


class Account(BaseModel, Document):
    id = StringField(primary_key=True, default=uuid_field('AC'))
    created_at = DateTimeField(
        default=dt.datetime.utcnow().replace(microsecond=0)
    )
    name = StringField(required=True)
    user_id = StringField(required=True)
    deactivated_at = DateTimeField()
