from typing import Any, Callable, Dict
from agave.repositories.base_redis import BaseModel
from .base_repository import BaseRepository
from ..exc import ModelDoesNotExist


class RedisRepository(BaseRepository):
    def __int__(self, model: BaseModel, query_builder: Callable):
        self.model = model
        self.query_builder = query_builder

    def get_by_id(self, resource_id: str):
        data = self.model.query.filter(id=resource_id)
        if not data:
            raise ModelDoesNotExist
        return data

    def count(self, filters: Dict[str, Any]) -> int:
        return self.model.query.filter(**filters).count()
