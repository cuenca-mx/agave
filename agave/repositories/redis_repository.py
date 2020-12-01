from abc import ABC
from typing import Callable

from cuenca_validations.types import QueryParams

from agave.repositories.base_redis import BaseModel

from ..exc import ModelDoesNotExist
from .base_repository import BaseRepository
from .query_result import QueryResult


class RedisRepository(BaseRepository):
    def __init__(self, model: BaseModel, query_builder: Callable):
        self.model = model
        self.query_builder = query_builder

    def get_by_id(self, resource_id: str, **delimiters):
        data = self.model.query.filter(id=resource_id, **delimiters)
        if not data:
            raise ModelDoesNotExist
        return data

    def count(self, filters: QueryParams, **delimiters) -> int:
        query = self.query_builder(**filters, **delimiters)
        return self.model.query.filter(query).count()

    def all(self, params: QueryParams, **delimiters) -> QueryResult:
        query = self.query_builder(params, **delimiters)
        return QueryResult(items=query)
