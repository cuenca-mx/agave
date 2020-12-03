from typing import Callable

from cuenca_validations.types import QueryParams
from mongoengine import Document
from mongoengine import DoesNotExist as DoesNotExist

from agave.collections.base import BaseCollection
from agave.collections.query_result import QueryResult
from agave.exc import ModelDoesNotExist


class MongoCollection(BaseCollection):
    def __init__(self, model: Document, query_builder: Callable):
        self.model = model
        self.query_builder = query_builder

    def retrieve(self, resource_id: str, **delimiters):
        try:
            data = self.model.objects.get(id=resource_id, **delimiters)
        except DoesNotExist:
            raise ModelDoesNotExist
        return data

    def count(self, params: QueryParams, **delimiters) -> int:
        query = self.query_builder(params, **delimiters)
        return self.model.objects.filter(query).count()

    def all(self, params: QueryParams, **delimiters) -> QueryResult:
        query = self.query_builder(params, **delimiters)
        if params.limit:
            limit = min(params.limit, params.page_size)
            params.limit = max(0, params.limit - limit)  # type: ignore
        else:
            limit = params.page_size
        items = (
            self.model.objects.order_by("-created_at")
            .filter(query)
            .limit(limit)
        )

        results = list(items)
        last = results[-1]
        has_more = None
        wants_more = params.limit is None or params.limit > 0
        if wants_more:
            # only perform this query if it's necessary
            has_more = items.limit(limit + 1).count() > limit

        return QueryResult(
            items=list(items),
            has_more=has_more,
            wants_more=wants_more,
            last_created_at=last.created_at,
        )
