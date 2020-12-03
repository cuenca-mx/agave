from abc import ABC, abstractmethod
from typing import Any

from cuenca_validations.types import QueryParams

from agave.collections.query_result import QueryResult


class BaseCollection(ABC):
    @abstractmethod
    def retrieve(self, resource_id: str, **delimiters) -> Any:
        """

        :param resource_id:
        :param delimiters:
        :return:
        """

    @abstractmethod
    def count(self, params: QueryParams, **delimiters) -> int:
        """

        :param params:
        :param delimiters:
        :return:
        """

    @abstractmethod
    def all(self, params: QueryParams, **delimiters) -> QueryResult:
        """

        :param params:
        :param delimiters:
        :return:
        """