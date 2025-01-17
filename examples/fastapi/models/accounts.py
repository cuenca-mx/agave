from mongoengine import DateTimeField, StringField
from mongoengine_plus.aio import AsyncDocument
from mongoengine_plus.models import BaseModel
from mongoengine_plus.models.helpers import uuid_field


class Account(BaseModel, AsyncDocument):
    meta = {'db_alias': 'fast_connection'}
    id = StringField(primary_key=True, default=uuid_field('AC'))
    name = StringField(required=True)
    user_id = StringField(required=True)
    platform_id = StringField(required=True)
    created_at = DateTimeField()
    deactivated_at = DateTimeField()
