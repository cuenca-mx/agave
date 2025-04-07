from cuenca_validations.types import uuid_field
from mongoengine import DateTimeField, StringField
from mongoengine_plus.aio import AsyncDocument
from mongoengine_plus.models import BaseModel


class Account(BaseModel, AsyncDocument):
    id = StringField(primary_key=True, default=uuid_field('AC'))
    name = StringField(required=True)
    user_id = StringField(required=True)
    platform_id = StringField(required=True)
    api_key_id = StringField(required=True)
    created_at = DateTimeField()
    deactivated_at = DateTimeField()
