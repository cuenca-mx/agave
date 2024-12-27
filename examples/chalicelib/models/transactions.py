from mongoengine import Document, FloatField, StringField

from agave.chalice.models import BaseModel
from agave.chalice.models.helpers import uuid_field


class Transaction(BaseModel, Document):
    id = StringField(primary_key=True, default=uuid_field('TR'))
    user_id = StringField(required=True)
    amount = FloatField(required=True)
