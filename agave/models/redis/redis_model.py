from typing import Dict, List, Optional, Tuple

from cuenca_validations.typing import DictStrAny
from cuenca_validations.validators import sanitize_item
from rom import Column, Model, PrimaryKey

from agave.exc import DoesNotExist
from agave.models.base import BaseModel

EXCLUDED = ['o_id']


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


def redis_to_dict(obj, exclude_fields: List[str]) -> DictStrAny:
    excluded = EXCLUDED + exclude_fields
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
        return self._dict(redis_to_dict)

    @classmethod
    def retrieve(
        cls, id: str, *, user_id: Optional[str] = None
    ) -> 'RedisModel':
        params = dict(id=id)
        if user_id:
            params['user_id'] = user_id
        obj = cls.query.filter(**params).first()
        if not obj:
            raise DoesNotExist
        return obj

    @classmethod
    def count(cls, filters: Dict) -> int:
        return cls.query.filter(**filters).count()

    @classmethod
    def all(
        cls, filters: Dict, *, limit: int, wants_more: bool
    ) -> Tuple[List['RedisModel'], bool]:
        items = (
            cls.query.filter(**filters).order_by('-created_at').limit(0, limit)
        )

        has_more = False
        if wants_more:
            has_more = items.limit(0, limit + 1).count() > limit

        return list(items), has_more
