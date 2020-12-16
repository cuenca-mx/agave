from typing import Any, Dict, Optional, Tuple

from cuenca_validations.typing import DictStrAny
from cuenca_validations.validators import sanitize_item
from rom import Column, Model, PrimaryKey

from .base import BaseModel
from ..exc import ModelDoesNotExist


class String(Column):
    """
    No utilizo la clase String de rom porque todo lo maneja en bytes
    codificado en latin-1.
    """

    _allowed = str

    def _to_redis(self, value):
        return value.encode('utf-8')

    def _from_redis(self, value):
        return value.decode('utf-8')


def redis_to_dit(obj, exclude_fields: list = None) -> dict:
    excluded = ['o_id']
    response = {
        key: sanitize_item(value)
        for key, value in obj._data.items()
        if key not in excluded
    }
    return response


class RedisModel(BaseModel, Model):
    meta = {'allow_inheritance': True}
    o_id = PrimaryKey()  # Para que podamos usar `id` en los modelos

    def dict(self) -> DictStrAny:
        return self._dict(redis_to_dit)

    def retrieve(self, id: str, user_id: Optional[str] = None):

        if user_id:
            id_obj = self.model.query.filter(
                id=id,
                user_id=user_id,
            ).first()
        else:
            id_obj = self.model.get_by(id=id)
        if not id_obj:
            raise ModelDoesNotExist
        return id_obj

    def count(self, filters: Any) -> Dict[str, Any]:
        count = self.model.query.filter(**filters).count()
        return count

    def filter_limit(self, filters: Any, limit: int) -> Tuple[any, bool]:
        items = (
            self.model.query.filter(**filters)
            .order_by('-created_at')
            .limit(0, limit)
        )
        has_more = items.limit(0, limit + 1).count() > limit
        return items, has_more
