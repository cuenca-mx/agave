from typing import List, Optional, Tuple

import mongoengine as mongo
from cuenca_validations.typing import DictStrAny
from mongoengine import Document, Q

from agave import exc
from agave.lib.mongoengine.model_helpers import mongo_to_dict
from agave.models.base import BaseModel


class MongoModel(BaseModel, Document):
    meta = {'allow_inheritance': True}

    def dict(self) -> DictStrAny:
        return self._dict(mongo_to_dict)

    @classmethod
    def retrieve(
        cls, id: str, *, user_id: Optional[str] = None
    ) -> 'MongoModel':
        query = Q(id=id)
        if user_id:
            query = query & Q(user_id=user_id)
        try:
            obj = cls.objects.get(query)
        except mongo.DoesNotExist:
            raise exc.DoesNotExist
        return obj

    @classmethod
    def count(cls, filters: Q) -> int:
        return cls.objects.filter(filters).count()

    @classmethod
    def all(
        cls, filters: Q, *, limit: int, wants_more: bool
    ) -> Tuple[List['MongoModel'], bool]:
        items = (
            cls.objects.order_by("-created_at").filter(filters).limit(limit)
        )

        has_more = False
        if wants_more:
            has_more = items.limit(limit + 1).count() > limit

        return list(items), has_more
