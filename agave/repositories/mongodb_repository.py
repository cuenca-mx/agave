from typing import Callable

from cuenca_validations.types import QueryParams
from mongoengine import Document
from mongoengine import DoesNotExist as DoesNotExist

from ..exc import ModelDoesNotExist
from .base_repository import BaseRepository
from .query_result import QueryResult


class MongoRepository(BaseRepository):
    def __init__(self, model: Document, query_builder: Callable):
        self.model = model
        self.query_builder = query_builder

    def get_by_id(self, resource_id: str):
        try:
            data = self.model.objects.get(id=resource_id)
        except DoesNotExist:
            raise ModelDoesNotExist
        return data

    def count(self, filters: QueryParams) -> int:
        query = self.query_builder(filters)
        return self.model.objects.filter(query).count()

    def all(self, query: QueryParams) -> QueryResult:
        filters = self.query_builder(query)
        if query.limit:
            limit = min(query.limit, query.page_size)
            query.limit = max(0, query.limit - limit)  # type: ignore
        else:
            limit = query.page_size
        items = (
            self.model.objects.order_by("-created_at")
            .filter(filters)
            .limit(limit)
        )

        results = list(items)
        last = results[-1]
        has_more = None
        wants_more = query.limit is None or query.limit > 0
        if wants_more:
            # only perform this query if it's necessary
            has_more = items.limit(limit + 1).count() > limit

        return QueryResult(
            items=list(items),
            has_more=has_more,
            wants_more=wants_more,
            last_created_at=last.created_at,
        )
