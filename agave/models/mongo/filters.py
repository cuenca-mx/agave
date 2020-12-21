from cuenca_validations.types import QueryParams
from mongoengine import Q

from ...filters import exclude_fields


def generic_mongo_query(query: QueryParams) -> Q:
    filters = Q()
    if query.created_before:
        filters &= Q(created_at__lt=query.created_before)
    if query.created_after:
        filters &= Q(created_at__gt=query.created_after)
    fields = exclude_fields(query)
    return filters & Q(**fields)
