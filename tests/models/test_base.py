from mongoengine import Document, StringField
from rom import util

from agave.models.helpers import uuid_field
from agave.models.mongo import MongoModel
from agave.models.redis import RedisModel, String


class TestModel(MongoModel, Document):
    id = StringField()
    secret_field = StringField()
    __test__ = False
    _hidden = ['secret_field']


class TestModelRedis(RedisModel):
    id = String(
        default=uuid_field('US'),
        required=True,
        unique=True,
        index=True,
        keygen=util.IDENTITY,
    )
    secret_field = String(required=True, index=True, keygen=util.IDENTITY)

    _hidden = ['secret_field']
