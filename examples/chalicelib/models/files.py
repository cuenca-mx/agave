from mongoengine import Document, StringField

from agave.chalice.models import BaseModel
from agave.chalice.models.helpers import uuid_field


class File(BaseModel, Document):
    id = StringField(primary_key=True, default=uuid_field('TR'))
    user_id = StringField(required=True)
    name = StringField(required=True)
