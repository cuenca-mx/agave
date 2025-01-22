from cuenca_validations.types import uuid_field
from mongoengine import DateTimeField, StringField
from mongoengine_plus.aio import AsyncDocument
from mongoengine_plus.models import BaseModel


class Card(BaseModel, AsyncDocument):
    id = StringField(primary_key=True, default=uuid_field('CA'))
    number = StringField(required=True)
    user_id = StringField(required=True)
    created_at = DateTimeField()
