from typing import Any, Dict, Optional, Tuple

from cuenca_validations.typing import DictStrAny
from mongoengine import Document, DoesNotExist, Q

from ..exc import ModelDoesNotExist
from ..lib.mongoengine.model_helpers import mongo_to_dict
from .base import BaseModel


class MongoModel(BaseModel, Document):
    meta = {'allow_inheritance': True}

    def dict(self) -> DictStrAny:
        return self._dict(mongo_to_dict)

    def retrieve(self, id: str, user_id: Optional[str] = None):
        try:
            id_query = Q(id=id)
            if user_id:
                id_query = id_query & Q(user_id=user_id)
            id_obj = self.model.objects.get(id_query)
        except DoesNotExist:
            raise ModelDoesNotExist
        return id_obj

    def count(self, filters: Any) -> Dict[str, Any]:
        count = self.model.objects.filter(filters).count()
        return count

    def filter_limit(self, filters: Any, limit: int) -> Tuple[any, bool]:
        items = (
            self.model.objects.order_by("-created_at")
            .filter(filters)
            .limit(limit)
        )
        has_more = items.limit(limit + 1).count() > limit
        return items, has_more
