import datetime as dt

from mongoengine import DateTimeField, StringField
from mongoengine_plus.aio import AsyncDocument
from mongoengine_plus.models import BaseModel
from mongoengine_plus.models.helpers import uuid_field


class User(BaseModel, AsyncDocument):
    meta = {'db_alias': 'fast_connection'}
    id = StringField(primary_key=True, default=uuid_field('US'))
    created_at = DateTimeField(default=dt.datetime.utcnow)
    name = StringField(required=True)
    platform_id = StringField(required=True)
    ip = StringField()
