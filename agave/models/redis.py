from cuenca_validations.typing import DictStrAny
from cuenca_validations.validators import sanitize_dict

from .base import BaseModel


class RedisModel(BaseModel):

    def dict(self) -> DictStrAny:
        return self._dict(sanitize_dict)
