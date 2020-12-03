from typing import Callable

from cuenca_validations.types import QueryParams

from agave.repositories.base_redis import BaseModel

from ..exc import ModelDoesNotExist
from .base_repository import BaseRepository


class RedisRepository(BaseRepository):
    def __int__(self, model: BaseModel, query_builder: Callable):
        self.model = model
        self.query_builder = query_builder

    def get_by_id(self, resource_id: str):
        data = self.model.query.filter(id=resource_id)
        if not data:
            raise ModelDoesNotExist
        return data

    def count(self, filters: QueryParams) -> int:
        return self.model.query.filter(**filters).count()
