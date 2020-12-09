from cuenca_validations.typing import DictStrAny

from .base import BaseModel
from ..lib.mongoengine.model_helpers import mongo_to_dict


class MongoModel(BaseModel):

    def dict(self) -> DictStrAny:
        return self._dict(mongo_to_dict)
