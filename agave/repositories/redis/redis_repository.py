from typing import Callable

from cuenca_validations.types import QueryParams

from agave.repositories.redis.base_redis import BaseModel

from agave.exc import ModelDoesNotExist
from agave.repositories.base_repository import BaseRepository
from agave.repositories.query_result import QueryResult


class RedisRepository(BaseRepository):
    def __init__(self, model: BaseModel, query_builder: Callable):
        self.model = model
        self.query_builder = query_builder

    def get_by_id(self, resource_id: str, **delimiters):
        data = self.model.query.filter(id=resource_id, **delimiters).first()
        if not data:
            raise ModelDoesNotExist
        return data

    def count(self, params: QueryParams, **delimiters) -> int:
        query = self.query_builder(params, **delimiters)
        result = self.model.query.filter(**query).count()
        return result

    def all(self, params: QueryParams, **delimiters) -> QueryResult:
        query = self.query_builder(params, **delimiters)
        if params.limit:
            limit = min(params.limit, params.page_size)
            params.limit = max(0, params.limit - limit)  # type: ignore
        else:
            limit = params.page_size
        items = (
            self.model.query.filter(**query)
            .order_by('-created_at')
            .limit(0, limit)
        )
        results = list(items)
        last = results[-1]
        has_more = None
        wants_more = params.limit is None or params.limit > 0
        if wants_more:
            # only perform this query if it's necessary
            has_more = items.limit(0, limit + 1).count() > limit

        return QueryResult(
            items=list(items),
            has_more=has_more,
            wants_more=wants_more,
            last_created_at=last.created_at,
        )
