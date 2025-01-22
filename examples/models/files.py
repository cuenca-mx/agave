from cuenca_validations.types import uuid_field
from mongoengine import StringField
from mongoengine_plus.aio import AsyncDocument
from mongoengine_plus.models import BaseModel


class File(BaseModel, AsyncDocument):
    id = StringField(primary_key=True, default=uuid_field('TR'))
    user_id = StringField(required=True)
    name = StringField(required=True)
