import datetime as dt
from typing import Any, Dict, Optional, Tuple

from cuenca_validations.types import QueryParams
from mongoengine import DoesNotExist, Q


def exclude_fields(query: QueryParams) -> Dict[str, Any]:
    exclude_fields = {
        'created_before',
        'created_after',
        'active',
        'limit',
        'page_size',
        'key',
    }
    fields = query.dict(exclude=exclude_fields)
    if 'count' in fields:
        del fields['count']
    return fields


def generic_mongo_query(query: QueryParams) -> Q:
    filters = Q()
    if query.created_before:
        filters &= Q(created_at__lt=query.created_before)
    if query.created_after:
        filters &= Q(created_at__gt=query.created_after)
    fields = exclude_fields(query)
    return filters & Q(**fields)


def generic_redis_query(query: QueryParams, **kwargs) -> Dict[str, Any]:
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
    fields = exclude_fields(query)
    fields = {**fields, **kwargs}
    if len(filters) == 0:
        filters = fields
        return filters
    return filters


def get(cls, id: str, user_id: Optional[str] = None):
    try:
        id_query = Q(id=id)
        if user_id:
            id_query = id_query & Q(user_id=user_id)
        id_obj = cls.model.objects.get(id_query)
    except DoesNotExist:
        raise
    except Exception:
        if user_id:
            id_obj = cls.model.query.filter(
                id=id,
                user_id=user_id,
            ).first()
        else:
            id_obj = cls.model.get_by(id=id)
        if not id_obj:
            raise
    return id_obj


def filter_count(cls, filters: Any) -> Dict[str, Any]:
    try:
        count = cls.model.objects.filter(filters).count()
    except Exception:
        count = cls.model.query.filter(**filters).count()
    return count


def filter_limit(cls, filters: Any, limit: int) -> Tuple[any, bool]:
    try:
        items = (
            cls.model.objects.order_by("-created_at")
            .filter(filters)
            .limit(limit)
        )
        has_more = items.limit(limit + 1).count() > limit
    except Exception:
        items = (
            cls.model.query.filter(**filters)
            .order_by('-created_at')
            .limit(0, limit)
        )
        has_more = items.limit(0, limit + 1).count() > limit
    return items, has_more
