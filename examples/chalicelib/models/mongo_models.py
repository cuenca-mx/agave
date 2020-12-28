from mongoengine import DateTimeField, FloatField, StringField

from agave.models.mongo import MongoModel
from agave.models.helpers import uuid_field


class Account(MongoModel):
    id = StringField(primary_key=True, default=uuid_field('AC'))
    name = StringField(required=True)
    user_id = StringField(required=True)
    created_at = DateTimeField()
    deactivated_at = DateTimeField()
    secret_field = StringField()

    _hidden = ['secret_field']


class Transaction(MongoModel):
    id = StringField(primary_key=True, default=uuid_field('TR'))
    user_id = StringField(required=True)
    amount = FloatField(required=True)
