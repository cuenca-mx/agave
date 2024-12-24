from mongoengine import Document, StringField

from agave.chalice_support.models import BaseModel
from agave.chalice_support.models.helpers import uuid_field


class File(BaseModel, Document):
    id = StringField(primary_key=True, default=uuid_field('TR'))
    user_id = StringField(required=True)
    name = StringField(required=True)
