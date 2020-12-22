from typing import Any, Optional

from cuenca_validations.typing import DictStrAny
from mongoengine import Document, DoesNotExist, Q

from agave.exc import ObjectDoesNotExist
from agave.lib.mongoengine.model_helpers import mongo_to_dict
from agave.models.base import BaseModel


class MongoModel(BaseModel, Document):
    meta = {'allow_inheritance': True}

    def dict(self) -> DictStrAny:
        return self._dict(mongo_to_dict)

    @classmethod
    def retrieve(cls, id: str, user_id: Optional[str] = None):
        try:
            query = Q(id=id)
            if user_id:
                query = query & Q(user_id=user_id)
            id_obj = cls.objects.get(query)
        except DoesNotExist:
            raise ObjectDoesNotExist
        return id_obj

    @classmethod
    def count(cls, filters: Any) -> int:
        count = cls.objects.filter(filters).count()
        return count

    @classmethod
    def filter_limit(cls, filters: Any, limit: int):
        items = (
            cls.objects.order_by("-created_at").filter(filters).limit(limit)
        )
        return items

    @classmethod
    def has_more(cls, items: Any, limit: int):
        has_more = items.limit(limit + 1).count() > limit
        return has_more
