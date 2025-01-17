from mongoengine import StringField
from mongoengine_plus.aio import AsyncDocument
from mongoengine_plus.models import BaseModel
from mongoengine_plus.models.helpers import uuid_field


class File(BaseModel, AsyncDocument):
    id = StringField(primary_key=True, default=uuid_field('TR'))
    user_id = StringField(required=True)
    name = StringField(required=True)
