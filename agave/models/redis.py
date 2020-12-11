from cuenca_validations.typing import DictStrAny
from rom import Model, PrimaryKey

from agave.models.helpers import redis_to_dit

from .base import BaseModel


class RedisModel(BaseModel, Model):
    o_id = PrimaryKey()  # Para que podamos usar `id` en los modelos

    def dict(self) -> DictStrAny:
        return self._dict(redis_to_dit)
