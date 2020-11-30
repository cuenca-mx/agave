from abc import ABC, abstractmethod
from typing import Any

from cuenca_validations.types import QueryParams

from .query_result import QueryResult


class BaseRepository(ABC):
    @abstractmethod
    def get_by_id(self, resource_id: str) -> Any:
        ...

    @abstractmethod
    def count(self, filters: QueryParams) -> int:
        ...

    @abstractmethod
    def all(self, filters: QueryParams) -> QueryResult:
        ...
