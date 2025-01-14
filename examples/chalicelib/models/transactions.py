from mongoengine import Document, FloatField, StringField
from mongoengine_plus.models.helpers import uuid_field

from agave.chalice.models import BaseModel


class Transaction(BaseModel, Document):
    id = StringField(primary_key=True, default=uuid_field('TR'))
    user_id = StringField(required=True)
    amount = FloatField(required=True)
