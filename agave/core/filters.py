from cuenca_validations.types import QueryParams
from mongoengine import Q


def _ids_filter_value(ids: str | list[str]) -> list[str]:
    if isinstance(ids, str):
        return [part.strip() for part in ids.split(',') if part.strip()]
    return list(ids)


def generic_query(query: QueryParams, excluded: list[str] = []) -> Q:
    filters = Q()
    if query.created_before:
        filters &= Q(created_at__lt=query.created_before)
    if query.created_after:
        filters &= Q(created_at__gt=query.created_after)
    ids = getattr(query, 'ids', None)
    if ids is not None:
        id_list = _ids_filter_value(ids)
        filters &= Q(id__in=id_list) if id_list else Q(id__in=[])
    exclude_fields = {
        'created_before',
        'created_after',
        'active',
        'limit',
        'page_size',
        'key',
        'ids',
        *excluded,
    }
    fields = query.model_dump(exclude=exclude_fields)
    if 'count' in fields:
        del fields['count']
    return filters & Q(**fields)
