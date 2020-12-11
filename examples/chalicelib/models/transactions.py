from mongoengine import Document, FloatField, StringField

from agave.models.mongo import MongoModel
from agave.models.helpers import uuid_field


class Transaction(MongoModel):
    id = StringField(primary_key=True, default=uuid_field('TR'))
    user_id = StringField(required=True)
    amount = FloatField(required=True)
