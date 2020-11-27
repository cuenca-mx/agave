from abc import ABC, abstractmethod

from cuenca_validations.types import QueryParams


class BaseRepository(ABC):
    @abstractmethod
    def get_by_id(self, resource_id: str):
        ...

    @abstractmethod
    def count(self, filters: QueryParams) -> int:
        ...

    @abstractmethod
    def all(self, filters: QueryParams):
        ...
