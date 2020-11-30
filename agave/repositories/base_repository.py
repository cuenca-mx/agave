from abc import ABC, abstractmethod
from typing import Any

from cuenca_validations.types import QueryParams

from .query_result import QueryResult


class BaseRepository(ABC):
    @abstractmethod
    def get_by_id(self, resource_id: str, **delimiters) -> Any:
        ...

    @abstractmethod
    def count(self, params: QueryParams, **delimiters) -> int:
        ...

    @abstractmethod
    def all(self, params: QueryParams, **delimiters) -> QueryResult:
        ...
