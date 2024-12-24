import datetime as dt

from mongoengine import DateTimeField, Document, StringField

from agave.chalice_support.models import BaseModel
from agave.chalice_support.models.helpers import uuid_field


class User(BaseModel, Document):
    id = StringField(primary_key=True, default=uuid_field('US'))
    created_at = DateTimeField(default=dt.datetime.utcnow)
    name = StringField(required=True)
    platform_id = StringField(required=True)
