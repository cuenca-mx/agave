from mongoengine import DateTimeField, Document, StringField
from mongoengine_plus.models.helpers import uuid_field

from agave.chalice.models import BaseModel


class Card(BaseModel, Document):
    id = StringField(primary_key=True, default=uuid_field('CA'))
    number = StringField(required=True)
    user_id = StringField(required=True)
    created_at = DateTimeField()
