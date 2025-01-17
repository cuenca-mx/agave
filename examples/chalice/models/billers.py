import datetime as dt

from mongoengine import DateTimeField, Document, StringField
from mongoengine_plus.models.helpers import uuid_field

from agave.chalice.models import BaseModel


class Biller(BaseModel, Document):
    id = StringField(primary_key=True, default=uuid_field('BL'))
    created_at = DateTimeField(default=dt.datetime.utcnow)
    name = StringField(required=True)
