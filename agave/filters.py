import datetime as dt
from typing import Any, Dict

from cuenca_validations.types import QueryParams
from mongoengine import DoesNotExist, Q


def generic_query(query: QueryParams) -> Q:
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
    if 'count' in fields:
        del fields['count']
    return filters & Q(**fields)


def get_by_id(cls, id: str):
    try:
        id_obj = cls.model.objects.get(id=id)
    except Exception as exc:
        if isinstance(exc, DoesNotExist):
            raise
        id_obj = cls.model.get_by(id=id)
        if not id_obj:
            raise
    return id_obj


def get_by_id_and_user(cls, id: str):
    try:
        id_query = Q(id=id)
        id_query = id_query & Q(user_id=cls.current_user_id)
        id_obj = cls.model.objects.get(id_query)
    except Exception as exc:
        if isinstance(exc, DoesNotExist):
            raise
        id_obj = cls.model.query.filter(
            id=id,
            user=cls.current_user.o_id,  # It can only query the numeric index
        ).first()
        if not id_obj:
            raise
    return id_obj


def generic_query_redis(query: QueryParams, **kwargs) -> Dict[str, Any]:
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
    if len(filters) == 0:
        filters = fields
        return filters
    return filters
