import datetime as dt

from cuenca_validations.types import QueryParams
from cuenca_validations.typing import DictStrAny

from ...filters import exclude_fields


def generic_redis_query(query: QueryParams, **kwargs) -> DictStrAny:
    filters = dict()
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
    if not filters:
        filters = fields
    return filters
