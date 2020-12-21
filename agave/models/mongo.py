from typing import Any, Optional, Tuple

from cuenca_validations.typing import DictStrAny
from mongoengine import Document, DoesNotExist, Q

from ..exc import ObjectDoesNotExist
from ..lib.mongoengine.model_helpers import mongo_to_dict
from .base import BaseModel


class MongoModel(BaseModel, Document):
    meta = {'allow_inheritance': True}

    def dict(self) -> DictStrAny:
        return self._dict(mongo_to_dict)

    @classmethod
    def retrieve(cls, id: str, user_id: Optional[str] = None):
        try:
            id_query = Q(id=id)
            if user_id:
                id_query = id_query & Q(user_id=user_id)
            id_obj = cls.objects.get(id_query)
        except DoesNotExist:
            raise ObjectDoesNotExist
        return id_obj

    @classmethod
    def count(cls, filters: Any) -> int:
        count = cls.objects.filter(filters).count()
        return count

    @classmethod
    def filter_limit(cls, filters: Any, limit: int) -> Tuple[Any, bool]:
        items = (
            cls.objects.order_by("-created_at").filter(filters).limit(limit)
        )
        has_more = items.limit(limit + 1).count() > limit
        items = list(items)
        return items, has_more
