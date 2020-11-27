from typing import Callable, Optional

from cuenca_validations.types import QueryParams
from mongoengine import Document
from mongoengine import DoesNotExist as DoesNotExist

from ..exc import ModelDoesNotExist
from .base_repository import BaseRepository


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
        return self.model.objects.filter(filters).count()

    def all(self, query: QueryParams):
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
        item_dicts = [i.to_dict() for i in items]

        has_more: Optional[bool] = None
        if wants_more := query.limit is None or query.limit > 0:
            # only perform this query if it's necessary
            has_more = items.limit(limit + 1).count() > limit

        next_page_uri: Optional[str] = None
        if wants_more and has_more:
            query.created_before = item_dicts[-1]['created_at']
            path = self.current_request.context['resourcePath']
            params = query.dict()
            if self.user_id_filter_required():
                params.pop('user_id')
            next_page_uri = f'{path}?{urlencode(params)}'
        return dict(items=item_dicts, next_page_uri=next_page_uri)
