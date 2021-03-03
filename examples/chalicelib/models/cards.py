from mongoengine import DateTimeField, Document, StringField

from agave.models import BaseModel
from agave.models.helpers import uuid_field


class Card(BaseModel, Document):
    id = StringField(primary_key=True, default=uuid_field('CA'))
    number = StringField(required=True)
    user_id = StringField(required=True)
    created_at = DateTimeField()
