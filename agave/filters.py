import datetime as dt
from typing import Any, Dict

from cuenca_validations.types import QueryParams
from mongoengine import Q


def generic_query(query: QueryParams, **kwargs) -> Q:
    filters = Q()
    if query.created_before:
        filters &= Q(created_at__lt=query.created_before)
    if query.created_after:
        filters &= Q(created_at__gt=query.created_after)
    exclude_fields = {
        'created_before',
        'created_after',
        'active',
        'limit',
        'page_size',
        'key',
    }
    fields = query.dict(exclude=exclude_fields)
    fields = {**fields, **kwargs}
    if 'count' in fields:
        del fields['count']
    return filters & Q(**fields)


def generic_query_redis(query: QueryParams) -> Dict[str, Any]:
    filters: Dict[str, Any] = dict()
    if query.created_before or query.created_after:
        # Restamos o sumamos un microsegundo porque la comparación
        # aquí es inclusiva
        created_at_lt = (
            query.created_before.replace(tzinfo=None)
            + dt.timedelta(microseconds=-1)
            if query.created_before
            else None
        )
        created_at_gt = (
            query.created_after.replace(tzinfo=None)
            + dt.timedelta(microseconds=1)
            if query.created_after
            else None
        )
        filters['created_at'] = (created_at_gt, created_at_lt)

    return filters
