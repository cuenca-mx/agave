from typing import Any, Optional

from cuenca_validations.typing import DictStrAny
from mongoengine import Document, DoesNotExist, Q

from agave.exc import DoesNotExist as AgaveDoesNotExist
from agave.lib.mongoengine.model_helpers import mongo_to_dict
from agave.models.base import BaseModel


class MongoModel(BaseModel, Document):
    meta = {'allow_inheritance': True}

    def dict(self) -> DictStrAny:
        return self._dict(mongo_to_dict)

    @classmethod
    def retrieve(cls, id: str, *, user_id: Optional[str] = None):
        query = Q(id=id)
        if user_id:
            query = query & Q(user_id=user_id)
        try:
            id_obj = cls.objects.get(query)
        except DoesNotExist:
            raise AgaveDoesNotExist
        return id_obj

    @classmethod
    def count(cls, filters: Q) -> int:
        count = cls.objects.filter(filters).count()
        return count

    @classmethod
    def all(cls, filters: Q, *, limit: int):
        items = (
            cls.objects.order_by("-created_at").filter(filters).limit(limit)
        )
        return items

    @classmethod
    def has_more(cls, items: Q, limit: int):
        has_more = items.limit(limit + 1).count() > limit
        return has_more
