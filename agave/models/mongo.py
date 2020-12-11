from cuenca_validations.typing import DictStrAny
from mongoengine import Document

from ..lib.mongoengine.model_helpers import mongo_to_dict
from .base import BaseModel


class MongoModel(BaseModel, Document):
    meta = {'allow_inheritance': True}

    def dict(self) -> DictStrAny:
        return self._dict(mongo_to_dict)
