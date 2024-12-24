from mongoengine import Document, FloatField, StringField

from agave.chalice_support.models import BaseModel
from agave.chalice_support.models.helpers import uuid_field


class Transaction(BaseModel, Document):
    id = StringField(primary_key=True, default=uuid_field('TR'))
    user_id = StringField(required=True)
    amount = FloatField(required=True)
