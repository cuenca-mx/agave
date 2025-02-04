import datetime as dt

from mongoengine import DateTimeField, StringField
from mongoengine_plus.aio import AsyncDocument
from mongoengine_plus.models import BaseModel


class Jwt(BaseModel, AsyncDocument):
    token = StringField(primary_key=True)
    created_at = DateTimeField(default=dt.datetime.utcnow)
