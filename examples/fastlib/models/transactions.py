from mongoengine import FloatField, StringField
from mongoengine_plus.aio import AsyncDocument
from mongoengine_plus.models import BaseModel
from mongoengine_plus.models.helpers import uuid_field


class Transaction(BaseModel, AsyncDocument):
    meta = {'db_alias': 'fast_connection'}
    id = StringField(primary_key=True, default=uuid_field('TR'))
    user_id = StringField(required=True)
    amount = FloatField(required=True)
