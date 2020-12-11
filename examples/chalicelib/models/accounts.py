from mongoengine import DateTimeField, StringField

from agave.models.mongo import MongoModel
from agave.models.helpers import uuid_field


class Account(MongoModel):
    id = StringField(primary_key=True, default=uuid_field('AC'))
    name = StringField(required=True)
    user_id = StringField(required=True)
    created_at = DateTimeField()
    deactivated_at = DateTimeField()
