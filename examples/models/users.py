import datetime as dt

from cuenca_validations.types import uuid_field
from mongoengine import DateTimeField, StringField
from mongoengine_plus.aio import AsyncDocument
from mongoengine_plus.models import BaseModel


class User(BaseModel, AsyncDocument):
    id = StringField(primary_key=True, default=uuid_field('US'))
    created_at = DateTimeField(default=dt.datetime.utcnow)
    name = StringField(required=True)
    platform_id = StringField(required=True)
    ip = StringField()
