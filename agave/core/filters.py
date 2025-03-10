from cuenca_validations.types import QueryParams
from mongoengine import Q


def generic_query(query: QueryParams, excluded: list[str] = []) -> Q:
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
        *excluded,
    }
    fields = query.model_dump(exclude=exclude_fields)
    if 'count' in fields:
        del fields['count']
    return filters & Q(**fields)
