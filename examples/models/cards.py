from mongoengine import DateTimeField, StringField
from mongoengine_plus.aio import AsyncDocument
from mongoengine_plus.models import BaseModel
from mongoengine_plus.models.helpers import uuid_field


class Card(BaseModel, AsyncDocument):
    meta = {'db_alias': 'fast_connection'}
    id = StringField(primary_key=True, default=uuid_field('CA'))
    number = StringField(required=True)
    user_id = StringField(required=True)
    created_at = DateTimeField()
